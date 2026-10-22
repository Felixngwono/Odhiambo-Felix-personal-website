from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    BlogPost,
    Certification,
    Event,
    EventCategory,
    EventLocation,
    ImageGallery,
    Job,
    MyUser,
    PortfolioItem,
    Project,
    Skill,
    Testimonial,
)


class PublicSiteTests(TestCase):
    """A visitor must be able to read the site without an account."""

    def setUp(self):
        self.today = timezone.now().date()
        self.owner = MyUser.objects.create_user(
            username='owner', email='owner@example.com', password='test-password-123'
        )
        self.owner.is_superuser = True
        self.owner.name = 'Site Owner'
        self.owner.save()

        self.post = BlogPost.objects.create(
            title='Hello world', content='A first post.', author=self.owner,
            status='published', category='story', tags='intro, django',
        )
        self.portfolio_item = PortfolioItem.objects.create(
            title='Portfolio piece', description='A project.', author=self.owner, category='web',
        )
        self.project = Project.objects.create(
            title='Public project', description='Something I built.', status='live',
        )
        self.category = EventCategory.objects.create(name='Workshops')
        self.location = EventLocation.objects.create(name='Nairobi', address='Nairobi, Kenya')
        self.event = Event.objects.create(
            title='Public event', description='An open event.', category=self.category,
            location=self.location, start_date=timezone.now() + timedelta(days=3),
        )
        self.media = ImageGallery.objects.create(title='A photo', caption='Caption.')
        self.skill = Skill.objects.create(name='Django', category='technical', proficiency=90)
        self.certification = Certification.objects.create(
            title='Public certificate', issuing_organization='Issuer',
            date_issued=self.today, level='advanced',
        )
        self.job = Job.objects.create(
            title='Public role', company='Company', status='open',
            description='A role.', job_type='full-time', category='engineering',
        )
        self.testimonial = Testimonial.objects.create(
            user=self.owner, name='Reviewer', designation='Engineer', message='Great work.',
        )

    def test_public_pages_render_for_a_visitor(self):
        pages = [
            reverse('me'),
            reverse('about'),
            reverse('blog'),
            reverse('blog_details', args=[self.post.pk]),
            reverse('portfolio'),
            reverse('portfolio_details', args=[self.portfolio_item.pk]),
            reverse('projects_list'),
            reverse('project_detail', args=[self.project.pk]),
            reverse('events'),
            reverse('event_detail', args=[self.event.pk]),
            reverse('event_category_list'),
            reverse('event_category_detail', args=[self.category.pk]),
            reverse('event_location_list'),
            reverse('event_location_detail', args=[self.location.pk]),
            reverse('gallery'),
            reverse('skills'),
            reverse('skill_detail', args=[self.skill.pk]),
            reverse('certification_list'),
            reverse('certification_detail', args=[self.certification.pk]),
            reverse('job_list'),
            reverse('job_posting', args=[self.job.pk]),
            reverse('testimonials_list'),
            reverse('faq_list'),
            reverse('search'),
            reverse('donate'),
            reverse('education_journey'),
        ]

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200, f'{url} returned {response.status_code}')

    def test_search_finds_public_content(self):
        response = self.client.get(reverse('search'), {'searched': 'public'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public project')

    def test_owner_only_pages_send_visitors_to_the_login_page(self):
        pages = [
            reverse('add_project'),
            reverse('edit_project', args=[self.project.pk]),
            reverse('delete_project', args=[self.project.pk]),
            reverse('add_portfolio'),
            reverse('add_image'),
            reverse('update_image', args=[self.media.pk]),
            reverse('delete_image', args=[self.media.pk]),
            reverse('add_event'),
            reverse('skill_create'),
            reverse('certification_add'),
            reverse('certification_update', args=[self.certification.pk]),
            reverse('certification_delete', args=[self.certification.pk]),
            reverse('post_job'),
            reverse('update_job', args=[self.job.pk]),
            reverse('delete_job', args=[self.job.pk]),
            reverse('job_application_list'),
            reverse('add_testimonial'),
            reverse('add_faq'),
        ]

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302, f'{url} was reachable by a visitor')
                self.assertIn('/login/', response.url)

    def test_draft_posts_stay_hidden_from_visitors(self):
        draft = BlogPost.objects.create(
            title='Secret draft', content='Not ready yet.', author=self.owner, status='drafted',
        )

        response = self.client.get(reverse('blog'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Secret draft')

        response = self.client.get(reverse('blog_details', args=[draft.pk]))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_reach_everything(self):
        self.client.force_login(self.owner)

        pages = [
            reverse('add_project'),
            reverse('add_portfolio'),
            reverse('add_image'),
            reverse('add_event'),
            reverse('skill_create'),
            reverse('certification_add'),
            reverse('post_job'),
            reverse('job_application_list'),
            reverse('add_testimonial'),
            reverse('add_faq'),
        ]

        for url in pages:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
