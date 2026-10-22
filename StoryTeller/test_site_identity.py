"""Tests for the site identity, the search page and the private screens."""

from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    BlogPost,
    Experience,
    Job,
    JobApplication,
    MyUser,
    Project,
    SiteSettings,
    Task,
)


class SiteIdentityTests(TestCase):
    """The public identity comes from the database, never from a template."""

    def setUp(self):
        self.owner = MyUser.objects.create_user(
            username='owner', email='owner@example.com', password='test-password-123'
        )
        self.owner.is_superuser = True
        self.owner.name = 'Ada Lovelace'
        self.owner.headline = 'Software Developer & Tech Enthusiast'
        self.owner.location = 'Nairobi, Kenya'
        self.owner.bio = 'I build web applications.'
        self.owner.github_url = 'https://github.com/example'
        self.owner.linkedin_url = 'https://linkedin.com/in/example'
        self.owner.save()

    def test_context_processor_exposes_the_owner(self):
        response = self.client.get(reverse('me'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['owner_name'], 'Ada Lovelace')
        self.assertEqual(response.context['owner_location'], 'Nairobi, Kenya')
        self.assertIn('github', [item['network'] for item in response.context['social_links']])

    def test_pages_render_the_stored_identity(self):
        for url in (reverse('me'), reverse('about')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'Ada Lovelace')
                self.assertContains(response, 'Nairobi, Kenya')

    def test_social_links_only_list_the_configured_networks(self):
        response = self.client.get(reverse('me'))
        networks = [item['network'] for item in response.context['social_links']]

        self.assertIn('github', networks)
        self.assertIn('linkedin', networks)
        self.assertNotIn('twitter', networks)

    def test_site_settings_singleton_is_seeded(self):
        settings_row = SiteSettings.current()

        self.assertEqual(settings_row.pk, 1)
        self.assertEqual(settings_row.site_name, 'FelloMarley Foundation')

    def test_site_settings_row_is_used_when_it_exists(self):
        row = SiteSettings.current()
        row.site_name = 'FelloMarley'
        row.tagline = 'Build things'
        row.owner = self.owner
        row.save()

        response = self.client.get(reverse('me'))

        self.assertEqual(response.context['site_name'], 'FelloMarley')
        self.assertEqual(response.context['site_tagline'], 'Build things')

    def test_public_pages_are_indexed_and_private_ones_are_not(self):
        self.assertEqual(self.client.get(reverse('me')).context['meta_robots'], 'index, follow')

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('index')).context['meta_robots'], 'noindex, follow')

    def test_meta_robots_reaches_the_rendered_page(self):
        response = self.client.get(reverse('about'))
        self.assertContains(response, 'index, follow')


class ExperienceTimelineTests(TestCase):
    """The work history on the about page is driven by the database."""

    def setUp(self):
        self.owner = MyUser.objects.create_user(
            username='owner', email='owner@example.com', password='test-password-123'
        )
        self.owner.is_superuser = True
        self.owner.save()

    def test_timeline_entries_are_shown_on_the_about_page(self):
        Experience.objects.create(
            title='ICT Consultant', organisation='IEBC Kenya',
            start_date=date(2025, 1, 1), is_current=True, order=1,
            description='Supporting ICT systems.',
        )
        Experience.objects.create(
            title='Developer', organisation='Agency', start_date=date(2020, 6, 1),
            end_date=date(2023, 12, 1), order=2,
        )

        response = self.client.get(reverse('about'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ICT Consultant')
        self.assertContains(response, 'IEBC Kenya')
        self.assertContains(response, '2025 - Present')
        self.assertContains(response, '2020 - 2023')

    def test_period_handles_a_missing_year(self):
        entry = Experience.objects.create(title='Freelancer', organisation='Self employed')

        self.assertEqual(entry.period, 'Present')
        self.assertTrue(entry.is_ongoing)

    def test_empty_timeline_shows_a_placeholder(self):
        Experience.objects.all().delete()

        response = self.client.get(reverse('about'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'work history is being updated')


class SearchPageTests(TestCase):
    """The search page lists the public content of every type."""

    def setUp(self):
        self.owner = MyUser.objects.create_user(
            username='owner', email='owner@example.com', password='test-password-123'
        )
        self.owner.is_superuser = True
        self.owner.save()

        self.project = Project.objects.create(
            title='Django search project', description='A project.', status='live',
        )
        self.post = BlogPost.objects.create(
            title='Django search notes', content='A post.', author=self.owner, status='published',
        )
        self.job = Job.objects.create(
            title='Django search role', company='Company', status='open',
            description='A role.', job_type='full-time', category='engineering',
        )
        self.task = Task.objects.create(
            title='Django search task', description='A task.',
            due_date=timezone.now() + timedelta(days=365), created_by=self.owner,
        )

    def test_search_lists_public_content(self):
        response = self.client.get(reverse('search'), {'searched': 'Django'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django search project')
        self.assertContains(response, 'Django search notes')
        self.assertContains(response, 'Django search role')

    def test_search_keeps_private_records_away_from_visitors(self):
        response = self.client.get(reverse('search'), {'searched': 'Django'})

        self.assertNotContains(response, 'Django search task')

    def test_the_owner_sees_the_private_records(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse('search'), {'searched': 'Django'})

        self.assertContains(response, 'Django search task')

    def test_search_without_a_query_shows_the_prompt(self):
        response = self.client.get(reverse('search'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'What are you looking for?')


class PrivateScreenTests(TestCase):
    """Account actions stay with the account holder and the site owner."""

    def setUp(self):
        self.owner = MyUser.objects.create_user(
            username='owner', email='owner@example.com', password='test-password-123'
        )
        self.owner.is_superuser = True
        self.owner.save()

        self.member = MyUser.objects.create_user(
            username='member', email='member@example.com', password='test-password-123',
        )

    def test_visitor_cannot_open_the_member_directory(self):
        response = self.client.get(reverse('myuser'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_owner_can_open_the_member_directory(self):
        self.client.force_login(self.owner)

        self.assertEqual(self.client.get(reverse('myuser')).status_code, 200)

    def test_member_cannot_edit_another_profile(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse('update_user', args=[self.owner.pk]))

        self.assertEqual(response.status_code, 403)

    def test_member_can_edit_their_own_profile(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse('update_user', args=[self.member.pk]))

        self.assertEqual(response.status_code, 200)

    def test_member_cannot_delete_another_profile(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse('delete_profile', args=[self.owner.pk]))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(MyUser.objects.filter(pk=self.owner.pk).exists())

    def test_other_members_do_not_see_a_private_email(self):
        self.client.force_login(self.member)

        response = self.client.get(reverse('user_detail', args=[self.owner.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'owner@example.com')

    def test_applicant_names_stay_hidden_on_a_public_job_page(self):
        job = Job.objects.create(
            title='Public role', company='Company', status='open', description='A role.',
            job_type='full-time', category='engineering',
        )
        JobApplication.objects.create(
            job=job, applicant=self.member, applicant_name='member',
            cover_letter='Please hire me.',
        )

        response = self.client.get(reverse('job_posting', args=[job.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'member')
        self.assertContains(response, '1')

    def test_the_owner_sees_the_applicants(self):
        job = Job.objects.create(
            title='Public role', company='Company', status='open', description='A role.',
            job_type='full-time', category='engineering',
        )
        JobApplication.objects.create(
            job=job, applicant=self.member, applicant_name='member',
            cover_letter='Please hire me.',
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse('job_posting', args=[job.pk]))

        self.assertContains(response, 'member')


class SearchEngineFilesTests(TestCase):
    """The crawler helpers are served from the site root."""

    def test_robots_points_at_the_sitemap(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, 200)
        self.assertIn('text/plain', response['Content-Type'])
        self.assertIn('Sitemap:', response.content.decode())

    def test_sitemap_lists_the_public_pages(self):
        response = self.client.get('/sitemap.xml')

        self.assertEqual(response.status_code, 200)
        self.assertIn('application/xml', response['Content-Type'])
        self.assertIn(b'<urlset', response.content)

    def test_missing_page_returns_the_custom_error_page(self):
        response = self.client.get('/this-page-does-not-exist/')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'could not find that page', status_code=404)
