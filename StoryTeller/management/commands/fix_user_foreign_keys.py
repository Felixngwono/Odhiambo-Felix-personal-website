"""Repoint legacy ``auth_user`` foreign keys at the custom user model.

The project switched to ``StoryTeller.MyUser`` (AUTH_USER_MODEL) long after the
database was created, so an older MySQL server can still hold foreign keys that
point at the abandoned ``auth_user`` table. Every insert that references a user
whose id is missing from ``auth_user`` then dies with:

    IntegrityError: ... FOREIGN KEY CONSTRAINT ... REFERENCES `auth_user` (`id`)

This command finds those constraints, moves the affected rows onto real
``StoryTeller.MyUser`` accounts (creating an account from the legacy row when
needed, keeping the old password hash so the login still works) and rebuilds the
constraints so they point at the right table.

Run it with ``--dry-run`` first to see exactly what it would change.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.transaction import atomic

from StoryTeller.models import MyUser

# table, column, ON DELETE rule, may a missing account be created?
TARGETS = [
    ('storyteller_volunteer', 'user_id', 'CASCADE', True),
    ('storyteller_jobapplication', 'applicant_id', 'CASCADE', True),
    ('storyteller_donation', 'donor_id', 'CASCADE', True),
    ('storyteller_support', 'user_id', 'CASCADE', True),
    ('storyteller_support', 'assignee_id', 'SET NULL', True),
    ('storyteller_testimonial', 'user_id', 'CASCADE', True),
    # Admin log rows are history, not a reason to create an account.
    ('django_admin_log', 'user_id', 'CASCADE', False),
]

LEGACY_TABLE = 'auth_user'
TARGET_TABLE = MyUser._meta.db_table


class Command(BaseCommand):
    help = 'Repoint legacy auth_user foreign keys at StoryTeller.MyUser.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without writing anything.',
        )
        parser.add_argument(
            '--backup',
            default='',
            help='Path for a JSON snapshot of the affected rows.',
        )

    # -- helpers -------------------------------------------------------------

    def _foreign_keys(self):
        """Every foreign key in the database that points at auth_user."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT kcu.TABLE_NAME, kcu.COLUMN_NAME, kcu.CONSTRAINT_NAME, kcu.REFERENCED_TABLE_NAME
                FROM information_schema.KEY_COLUMN_USAGE kcu
                WHERE kcu.TABLE_SCHEMA = DATABASE()
                  AND kcu.REFERENCED_TABLE_NAME = %s
                """,
                [LEGACY_TABLE],
            )
            return [
                {
                    'table': row[0],
                    'column': row[1],
                    'constraint': row[2],
                    'referenced': row[3],
                }
                for row in cursor.fetchall()
            ]

    def _constraint_on(self, table, column):
        """The foreign key that currently sits on a column, if any."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT CONSTRAINT_NAME, REFERENCED_TABLE_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s AND COLUMN_NAME = %s
                  AND REFERENCED_TABLE_NAME IS NOT NULL
                LIMIT 1
                """,
                [table, column],
            )
            row = cursor.fetchone()
        return row

    def _target_table(self):
        """The physical name of the user table, the way the server stores it."""
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = LOWER(%s)
                """,
                [TARGET_TABLE],
            )
            row = cursor.fetchone()
        return row[0] if row else TARGET_TABLE

    def _column_nullable(self, table, column):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT IS_NULLABLE FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table, column],
            )
            row = cursor.fetchone()
        return bool(row and row[0] == 'YES')

    def _column_type(self, table, column):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COLUMN_TYPE FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
                """,
                [table, column],
            )
            row = cursor.fetchone()
        return row[0] if row else ''

    def _referenced_ids(self, table, column):
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL')
            return [row[0] for row in cursor.fetchall()]

    def _legacy_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, password, first_name, last_name,
                       is_staff, is_superuser, is_active, date_joined, last_login
                FROM auth_user WHERE id = %s
                """,
                [user_id],
            )
            return cursor.fetchone()

    def _match_myuser(self, legacy):
        """Find the real account for a legacy row: email first, then username."""
        _id, username, email = legacy[0], legacy[1], legacy[2]

        if email:
            match = MyUser.objects.filter(email__iexact=email).order_by('id').first()
            if match:
                return match, 'email'

        if username:
            match = MyUser.objects.filter(username__iexact=username).order_by('id').first()
            if match:
                return match, 'username'

        return None, None

    def _create_myuser(self, legacy):
        """Recreate a legacy account on the custom user model, password and all."""
        (
            _id, username, email, password, first_name, last_name,
            is_staff, is_superuser, is_active, date_joined, last_login,
        ) = legacy

        new_username = username or f'legacy{_id}'
        candidate = new_username
        suffix = 1
        while MyUser.objects.filter(username__iexact=candidate).exists():
            suffix += 1
            candidate = f'{new_username}{suffix}'

        name = ' '.join(part for part in (first_name, last_name) if part).strip() or candidate

        user = MyUser(
            username=candidate,
            email=email,
            password=password,
            first_name=first_name or '',
            last_name=last_name or '',
            name=name,
            is_staff=bool(is_staff),
            is_superuser=bool(is_superuser),
            is_active=bool(is_active),
            date_joined=date_joined,
            last_login=last_login,
        )
        user.save()
        return user

    def _snapshot(self, path):
        payload = {}
        with connection.cursor() as cursor:
            for table, column, _rule, _create in TARGETS:
                cursor.execute(f'SELECT id, {column} FROM {table}')
                payload.setdefault(table, {})[column] = cursor.fetchall()
        Path(path).write_text(json.dumps(payload, indent=2, default=str), encoding='utf-8')
        self.stdout.write(self.style.WARNING(f'Snapshot written to {path}'))

    # -- main ----------------------------------------------------------------

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        backup = options['backup']

        rules = {(table, column): rule for table, column, rule, _create in TARGETS}
        may_create = {(table, column): create for table, column, _rule, create in TARGETS}

        pending = []
        target_table = self._target_table()

        for table, column, _rule, _create in TARGETS:
            constraint = self._constraint_on(table, column)

            if constraint and constraint[1].lower() == target_table.lower():
                self.stdout.write(f'  {table}.{column} already points at {target_table}')
                continue

            if constraint:
                self.stdout.write(
                    f'  {table}.{column} points at {constraint[1]} ({constraint[0]}), needs repointing'
                )
            else:
                self.stdout.write(f'  {table}.{column} has no foreign key, needs one')

            pending.append((table, column))

        legacy_left = [key for key in self._foreign_keys() if (key['table'], key['column']) not in rules]
        for key in legacy_left:
            self.stdout.write(
                f"  - {key['table']}.{key['column']} ({key['constraint']}) left alone: "
                f"belongs to Django's own auth_user table"
            )

        if not pending:
            self.stdout.write(self.style.SUCCESS('Every user foreign key already points at StoryTeller.MyUser.'))
            return

        if backup and not dry_run:
            self._snapshot(backup)

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run, nothing was written.'))
            self._report(rules, dry_run=True)
            return

        with atomic():
            self._repoint(pending, rules, may_create)

        self._report(rules, dry_run=False)

    def _repoint(self, pending, rules, may_create):
        target_table = self._target_table()

        for table, column in pending:
            nullable = self._column_nullable(table, column)
            can_create = may_create.get((table, column), False)
            target_type = self._column_type(target_table, 'id')

            # 1. Let go of the old constraint.
            constraint = self._constraint_on(table, column)
            if constraint:
                with connection.cursor() as cursor:
                    cursor.execute(f'ALTER TABLE {table} DROP FOREIGN KEY `{constraint[0]}`')

            # 2. The column has to match the type of the user table (bigint).
            current_type = self._column_type(table, column)
            if current_type != target_type:
                null_clause = 'NULL' if nullable else 'NOT NULL'
                with connection.cursor() as cursor:
                    cursor.execute(
                        f'ALTER TABLE {table} MODIFY `{column}` {target_type} {null_clause}'
                    )
                self.stdout.write(f'  {table}.{column}: {current_type} -> {target_type}')

            # 3. Move the rows onto real accounts.
            for value in self._referenced_ids(table, column):
                if MyUser.objects.filter(pk=value).exists():
                    # The row already points at a real account, keep it.
                    continue

                legacy = self._legacy_user(value)

                if legacy is None:
                    if nullable:
                        with connection.cursor() as cursor:
                            cursor.execute(f'UPDATE {table} SET {column} = NULL WHERE {column} = %s', [value])
                        self.stdout.write(f'  {table}.{column}={value} cleared (no account on either table)')
                    continue

                user, matched_by = self._match_myuser(legacy)

                if user is None and can_create:
                    user = self._create_myuser(legacy)
                    matched_by = 'created'
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  created MyUser "{user.username}" from legacy "{legacy[1]}" '
                            f'(email {legacy[2]})'
                        )
                    )

                if user is None:
                    if nullable:
                        with connection.cursor() as cursor:
                            cursor.execute(f'UPDATE {table} SET {column} = NULL WHERE {column} = %s', [value])
                        self.stdout.write(
                            f'  {table}.{column}={value} cleared '
                            f'(legacy "{legacy[1]}" has no account on the custom user model)'
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  {table}.{column}={value} has no matching account and cannot be nulled'
                            )
                        )
                    continue

                with connection.cursor() as cursor:
                    cursor.execute(f'UPDATE {table} SET {column} = %s WHERE {column} = %s', [user.pk, value])

                self.stdout.write(
                    f'  {table}.{column}: legacy {value} ({legacy[1]}) -> MyUser {user.pk} ({user.username}) [{matched_by}]'
                )

            # 4. Point the column at the custom user table.
            rule = rules.get((table, column), 'CASCADE')
            new_name = f'fk_{table}_{column}_myuser'[:64]

            with connection.cursor() as cursor:
                cursor.execute(
                    f'ALTER TABLE {table} ADD CONSTRAINT `{new_name}` '
                    f'FOREIGN KEY (`{column}`) REFERENCES `{target_table}` (`id`) ON DELETE {rule}'
                )

            self.stdout.write(self.style.SUCCESS(f'  {table}.{column} now points at {target_table}'))

    def _report(self, rules, dry_run):
        managed_tables = {table for table, _column, _rule, _create in TARGETS}
        target_table = self._target_table()
        missing = []

        for table, column, _rule, _create in TARGETS:
            constraint = self._constraint_on(table, column)
            if not constraint or constraint[1].lower() != target_table.lower():
                missing.append(f'{table}.{column}')

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = DATABASE()
                  AND REFERENCED_TABLE_NAME = %s
                  AND TABLE_NAME IN %s
                """,
                [LEGACY_TABLE, list(managed_tables)],
            )
            remaining = cursor.fetchone()[0]

        if remaining or missing:
            self.stdout.write(
                self.style.ERROR(
                    f'{remaining} foreign key(s) still point at {LEGACY_TABLE}'
                    + (f', missing constraint on: {", ".join(missing)}' if missing else '')
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('All user foreign keys now point at StoryTeller.MyUser.'))
