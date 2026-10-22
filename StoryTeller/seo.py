"""Public search engine helpers: robots.txt and the XML sitemap."""

from django.contrib.sitemaps import Sitemap
from django.http import HttpResponse
from django.urls import reverse

from .models import (
    BlogPost,
    Certification,
    Event,
    PortfolioItem,
    Project,
)


def robots_txt(request):
    """Tell the crawlers what to index and where the sitemap lives."""
    sitemap_url = request.build_absolute_uri(reverse('sitemap'))

    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /index/",
            "Disallow: /myuser/",
            "Disallow: /update_user/",
            "Disallow: /delete_profile/",
            "Disallow: /add/",
            "Disallow: /update/",
            "Disallow: /delete",
            "Disallow: /tasks/",
            "Disallow: /notifications/",
            "Disallow: /analytics/",
            "Disallow: /support/",
            "Disallow: /dashboard/",
            "Disallow: /login/",
            "Disallow: /signup/",
            "Disallow: /logoutuser/",
            "Disallow: /password-reset/",
            "Disallow: /search/",
            "",
            f"Sitemap: {sitemap_url}",
            "",
        ]
    )

    return HttpResponse(body, content_type="text/plain; charset=utf-8")


class StaticViewSitemap(Sitemap):
    """The pages that always exist."""

    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return ['me', 'about', 'blog', 'portfolio', 'projects_list', 'events',
                'certification_list', 'skills', 'gallery', 'testimonials_list',
                'job_list', 'faq_list', 'education_journey', 'siblings_list']

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return BlogPost.objects.exclude(status='drafted').order_by('-updated_at')

    def lastmod(self, obj):
        return obj.updated_at or obj.created_at

    def location(self, obj):
        return reverse('blog_details', args=[obj.pk])


class PortfolioSitemap(Sitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return PortfolioItem.objects.all()

    def lastmod(self, obj):
        return obj.date_created

    def location(self, obj):
        return reverse('portfolio_details', args=[obj.pk])


class ProjectSitemap(Sitemap):
    priority = 0.7
    changefreq = 'monthly'

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('project_detail', args=[obj.pk])


class CertificationSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return Certification.objects.all()

    def lastmod(self, obj):
        return obj.date_issued

    def location(self, obj):
        return reverse('certification_detail', args=[obj.pk])


class EventSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return Event.objects.all()

    def lastmod(self, obj):
        return obj.start_date

    def location(self, obj):
        return reverse('event_detail', args=[obj.pk])


SITEMAPS = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
    'portfolio': PortfolioSitemap,
    'projects': ProjectSitemap,
    'certifications': CertificationSitemap,
    'events': EventSitemap,
}
