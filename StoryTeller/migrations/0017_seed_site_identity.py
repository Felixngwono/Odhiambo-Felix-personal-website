"""Seed the site settings, the owner profile and the work history.

The identity of the site used to be hardcoded in the templates. The data now
lives in the database so the owner can edit it from the admin, and this
migration moves the old hardcoded values over.
"""

from django.db import migrations


SEED_EXPERIENCE = [
    {
        'title': 'ICT Consultant',
        'organisation': 'IEBC Kenya',
        'start_date': '2025-01-01',
        'is_current': True,
        'description': (
            'Supporting ICT systems, troubleshooting technical issues and '
            'contributing to digital solutions for election operations.'
        ),
        'order': 1,
    },
    {
        'title': 'Freelance Software Developer',
        'organisation': 'Self Employed',
        'start_date': '2023-01-01',
        'is_current': True,
        'description': (
            'Designing and building web applications, databases and custom '
            'software solutions for clients and small businesses.'
        ),
        'order': 2,
    },
    {
        'title': 'Software Developer',
        'organisation': 'FelloMarley Foundation',
        'start_date': '2022-01-01',
        'is_current': True,
        'description': (
            'Building community focused platforms, internal tools and digital '
            'resources for the foundation and the people it serves.'
        ),
        'order': 3,
    },
]


def seed(apps, schema_editor):
    MyUser = apps.get_model('StoryTeller', 'MyUser')
    SiteSettings = apps.get_model('StoryTeller', 'SiteSettings')
    Experience = apps.get_model('StoryTeller', 'Experience')

    owner = MyUser.objects.filter(is_superuser=True).order_by('id').first()
    if owner is None:
        owner = MyUser.objects.order_by('id').first()

    if owner is not None:
        if not owner.name:
            owner.name = 'Felix Odhiambo'
        if not owner.headline:
            owner.headline = 'Software Developer & Tech Enthusiast'
        if not owner.location:
            owner.location = 'Nairobi, Kenya'
        if not owner.bio:
            owner.bio = (
                "I'm Felix Odhiambo, a software developer passionate about "
                'building modern web applications, database systems and '
                'digital solutions that solve real-world problems.'
            )
        if not owner.github_url:
            owner.github_url = 'https://github.com/Felixngwono'
        if not owner.linkedin_url:
            owner.linkedin_url = 'https://linkedin.com/in/felixngwono'
        owner.save()

    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={
            'site_name': 'FelloMarley Foundation',
            'tagline': 'Software Developer & Tech Enthusiast',
            'site_description': (
                'Portfolio of Felix Odhiambo, a software developer building '
                'modern web applications with Django, Python, JavaScript and '
                'Tailwind CSS.'
            ),
            'keywords': 'Felix Odhiambo, software developer, Django, Python, Kenya',
            'owner': owner,
        },
    )

    for entry in SEED_EXPERIENCE:
        Experience.objects.get_or_create(
            title=entry['title'],
            organisation=entry['organisation'],
            defaults=entry,
        )


def unseed(apps, schema_editor):
    Experience = apps.get_model('StoryTeller', 'Experience')
    SiteSettings = apps.get_model('StoryTeller', 'SiteSettings')

    Experience.objects.filter(
        title__in=[entry['title'] for entry in SEED_EXPERIENCE]
    ).delete()
    SiteSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('StoryTeller', '0016_experience_myuser_github_url_myuser_headline_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
