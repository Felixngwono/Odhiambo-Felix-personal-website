from django.test import TestCase
from django.urls import reverse

from .models import MyUser


class SiteSmokeTests(TestCase):
    def setUp(self):
        user = MyUser.objects.create_user(
            username='smoke_admin', email='smoke_admin@example.com', password='pw-12345678'
        )
        user.is_staff = True
        user.is_superuser = True
        user.name = 'Smoke Admin'
        user.save()
        self.client.force_login(user)

    def test_main_pages_render(self):
        names = [
            'me', 'index', 'blog', 'portfolio', 'contactus', 'events', 'about',
            'gallery', 'admins', 'myuser', 'dashboard', 'tasks', 'support', 'analytics',
            'notifications', 'activity_list', 'education_journey', 'messaging', 'skills',
            'certification_list', 'projects_list', 'testimonials_list', 'volunteer_list',
            'job_list', 'donations', 'faq_list', 'search',
        ]

        broken = []
        unknown = []

        for name in names:
            try:
                url = reverse(name)
            except Exception:
                unknown.append(name)
                continue
            try:
                response = self.client.get(url)
            except Exception as exc:
                broken.append(f'{name}: {type(exc).__name__}: {exc}')
                continue
            if response.status_code != 200:
                broken.append(f'{name}: status {response.status_code}')

        self.assertEqual(broken, [], '\n'.join(broken))
        self.assertEqual(unknown, [], 'unresolved url names: ' + ', '.join(unknown))
