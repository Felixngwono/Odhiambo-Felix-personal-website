from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Certification, ImageGallery, Job, JobApplication, MyUser


def make_admin(username='hiring_admin'):
    user = MyUser.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='test-password-123',
    )
    user.is_staff = True
    user.is_superuser = True
    user.name = 'Hiring Admin'
    user.save()
    return user


class JobPageTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)

        self.today = timezone.now().date()
        self.job = Job.objects.create(
            title='Backend Engineer',
            company='FelloMarley Foundation',
            location='Nairobi, Kenya',
            job_type='full-time',
            category='engineering',
            status='open',
            description='Build and maintain the foundation services.',
            requirements='Django and Python.',
            skills='Django, Python, PostgreSQL',
            benefits='Learning budget',
            salary_range='KSh 80,000 - 120,000',
            slots=2,
            due_at=self.today + timedelta(days=30),
            is_featured=True,
        )
        self.application = JobApplication.objects.create(
            job=self.job,
            applicant=self.admin,
            applicant_name='Hiring Admin',
        )

    def test_board_pages_render(self):
        pages = [
            reverse('job_list'),
            reverse('job_posting', args=[self.job.pk]),
            reverse('post_job'),
            reverse('update_job', args=[self.job.pk]),
            reverse('delete_job', args=[self.job.pk]),
            reverse('jobdetails', args=[self.application.pk]),
            reverse('job_application_list'),
        ]

        for url in pages:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_job_filters_render(self):
        response = self.client.get(reverse('job_list'), {
            'q': 'backend',
            'type': 'full-time',
            'category': 'engineering',
            'status': 'open',
            'sort': 'popular',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend Engineer')

    def test_pipeline_filters_render(self):
        response = self.client.get(reverse('job_application_list'), {
            'q': 'hiring',
            'stage': 'under_review',
            'job': str(self.job.pk),
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hiring Admin')

    def test_apply_flow(self):
        applicant = MyUser.objects.create_user(
            username='applicant',
            email='applicant@example.com',
            password='test-password-123',
        )
        applicant.name = 'Job Applicant'
        applicant.save()

        self.client.force_login(applicant)

        response = self.client.get(reverse('apply_for_job', args=[self.job.pk]))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('apply_for_job', args=[self.job.pk]), {
            'job': self.job.pk,
            'applicant_name': 'Job Applicant',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(JobApplication.objects.filter(job=self.job, applicant=applicant).exists())

        # A second application from the same person is turned away.
        response = self.client.get(reverse('apply_for_job', args=[self.job.pk]))
        self.assertRedirects(response, reverse('already_applied', args=[self.job.pk]))

    def test_status_update_returns_to_the_application(self):
        destination = reverse('jobdetails', args=[self.application.pk])

        response = self.client.post(
            reverse('update_application_status', args=[self.application.pk]),
            {'status': 'interview', 'next': destination},
        )

        self.assertRedirects(response, destination)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'interview')
        self.assertTrue(self.application.reviewed)

    def test_status_update_without_next_falls_back_to_the_pipeline(self):
        response = self.client.post(
            reverse('update_application_status', args=[self.application.pk]),
            {'status': 'hired'},
        )

        self.assertRedirects(response, reverse('job_application_list'))

    def test_response_is_recorded_on_the_application(self):
        destination = reverse('jobdetails', args=[self.application.pk])

        response = self.client.post(
            reverse('respond_to_application', args=[self.application.pk]),
            {'response_message': 'We would like to call you.', 'next': destination},
        )

        self.assertRedirects(response, destination)
        self.application.refresh_from_db()
        self.assertIn('We would like to call you.', self.application.notes)
        self.assertTrue(self.application.reviewed)

    def test_empty_response_is_rejected(self):
        response = self.client.post(
            reverse('respond_to_application', args=[self.application.pk]),
            {'response_message': '   '},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.application.refresh_from_db()
        self.assertNotIn('Write a response', self.application.notes or '')
        self.assertIn('Write a response before sending it.', [str(message) for message in response.context['messages']])

    def test_post_update_and_delete_a_role(self):
        response = self.client.post(reverse('post_job'), {
            'title': 'Community Officer',
            'company': 'FelloMarley Foundation',
            'location': 'Kisumu',
            'job_type': 'contract',
            'category': 'community',
            'status': 'open',
            'description': 'Work with the community teams.',
            'requirements': 'Facilitation',
            'skills': 'Facilitation, Reporting',
            'benefits': 'Transport',
            'salary_range': 'KSh 40,000',
            'due_at': str(self.today + timedelta(days=14)),
            'slots': 1,
        })
        self.assertEqual(response.status_code, 302)

        posted = Job.objects.get(title='Community Officer')

        response = self.client.post(reverse('update_job', args=[posted.pk]), {
            'title': 'Community Officer (Revised)',
            'company': 'FelloMarley Foundation',
            'job_type': 'contract',
            'category': 'community',
            'status': 'open',
            'description': 'Work with the community teams.',
            'slots': 1,
        })
        self.assertRedirects(response, reverse('job_posting', args=[posted.pk]))
        posted.refresh_from_db()
        self.assertEqual(posted.title, 'Community Officer (Revised)')

        response = self.client.post(reverse('delete_job', args=[posted.pk]))
        self.assertRedirects(response, reverse('job_list'))
        self.assertFalse(Job.objects.filter(pk=posted.pk).exists())


class GalleryPageTests(TestCase):
    def setUp(self):
        self.admin = make_admin('gallery_admin')
        self.client.force_login(self.admin)

        self.image = ImageGallery.objects.create(
            title='Team photo',
            caption='The crew after the community drive.',
        )
        self.video = ImageGallery.objects.create(
            title='Launch clip',
            caption='Short clip from the launch.',
        )

    def test_gallery_pages_render(self):
        pages = [
            reverse('gallery'),
            reverse('add_image'),
            reverse('update_image', args=[self.image.pk]),
            reverse('delete_image', args=[self.image.pk]),
        ]

        for url in pages:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_gallery_shows_counts(self):
        response = self.client.get(reverse('gallery'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Team photo')
        self.assertContains(response, 'Launch clip')
        self.assertEqual(response.context['total_media'], 2)
        self.assertEqual(response.context['total_images'], 2)
        self.assertEqual(response.context['total_videos'], 0)

    def test_gallery_filters(self):
        response = self.client.get(reverse('gallery'), {'q': 'launch'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Launch clip')
        self.assertNotContains(response, 'Team photo')

        response = self.client.get(reverse('gallery'), {'type': 'video'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['images']), 0)

        response = self.client.get(reverse('gallery'), {'sort': 'title'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.title for item in response.context['images']],
            ['Launch clip', 'Team photo'],
        )

    def test_upload_edit_and_delete_media(self):
        response = self.client.post(reverse('add_image'), {
            'title': 'New picture',
            'caption': 'Fresh upload.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ImageGallery.objects.filter(title='New picture').exists())

        created = ImageGallery.objects.get(title='New picture')

        response = self.client.post(reverse('update_image', args=[created.pk]), {
            'title': 'New picture v2',
            'caption': 'Updated caption.',
        })
        self.assertRedirects(response, reverse('gallery'))
        created.refresh_from_db()
        self.assertEqual(created.title, 'New picture v2')
        self.assertEqual(created.caption, 'Updated caption.')

        response = self.client.post(reverse('delete_image', args=[created.pk]))
        self.assertRedirects(response, reverse('gallery'))
        self.assertFalse(ImageGallery.objects.filter(pk=created.pk).exists())


class CertificationPageTests(TestCase):
    def setUp(self):
        self.admin = make_admin('wallet_admin')
        self.client.force_login(self.admin)

        self.today = timezone.now().date()
        self.certification = Certification.objects.create(
            title='Cloud Architecture',
            issuing_organization='Cloud Academy',
            date_issued=self.today - timedelta(days=60),
            level='advanced',
            skills='Cloud, Networking',
            description='Architecture and operations.',
            credential_id='CA-1234',
            credential_url='https://example.com/credential',
        )

    def test_wallet_pages_render(self):
        pages = [
            reverse('certification_list'),
            reverse('certification_detail', args=[self.certification.pk]),
            reverse('certification_add'),
            reverse('certification_update', args=[self.certification.pk]),
            reverse('certification_delete', args=[self.certification.pk]),
        ]

        for url in pages:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_wallet_filters_render(self):
        response = self.client.get(reverse('certification_list'), {
            'q': 'cloud',
            'level': 'advanced',
            'org': 'Cloud Academy',
            'year': str(self.certification.year),
            'sort': 'level',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cloud Architecture')

    def test_create_update_and_delete_a_credential(self):
        response = self.client.post(reverse('certification_add'), {
            'title': 'Data Analytics',
            'issuing_organization': 'Data Academy',
            'level': 'expert',
            'date_issued': str(self.today),
            'expiry_date': str(self.today + timedelta(days=365)),
            'credential_id': 'DA-1',
            'skills': 'Data Analysis, Excel',
            'description': 'Analytics for decision making.',
        })
        self.assertEqual(response.status_code, 302)

        created = Certification.objects.get(title='Data Analytics')

        response = self.client.post(reverse('certification_update', args=[created.pk]), {
            'title': 'Data Analytics Pro',
            'issuing_organization': 'Data Academy',
            'level': 'expert',
            'date_issued': str(self.today),
            'credential_id': 'DA-1',
            'skills': 'Data Analysis, Excel',
            'description': 'Analytics for decision making.',
        })
        self.assertRedirects(response, reverse('certification_detail', args=[created.pk]))
        created.refresh_from_db()
        self.assertEqual(created.title, 'Data Analytics Pro')

        response = self.client.post(reverse('certification_delete', args=[created.pk]))
        self.assertRedirects(response, reverse('certification_list'))
        self.assertFalse(Certification.objects.filter(pk=created.pk).exists())
