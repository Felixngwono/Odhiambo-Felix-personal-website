"""Template context shared by every page.

``dashboard_globals`` feeds the header, sidebar and admin pages, while
``site`` exposes the editable identity of the site (name, headline, location,
social links) so no page has to hardcode it.
"""

from django.conf import settings

from .models import MyUser, Notification, SiteSettings

# Only these pages belong in a search engine index. Everything else is either
# the private dashboard or an owner only screen.
PUBLIC_URL_NAMES = {
    'me',
    'about',
    'blog',
    'blog_details',
    'portfolio',
    'portfolio_details',
    'projects_list',
    'project_detail',
    'certification_list',
    'certification_detail',
    'skills',
    'skill_detail',
    'gallery',
    'events',
    'event_detail',
    'event_details',
    'testimonials_list',
    'job_list',
    'job_posting',
    'faq_list',
    'education_journey',
    'siblings_list',
    'sibling_detail',
    'volunteer_list',
    'contactus',
    'donate',
}


def dashboard_globals(request):
    """Values the header, the sidebar and the admin pages always need."""
    user = getattr(request, 'user', None)

    avatar_url = ''
    notifications_unread = 0

    if user is not None and user.is_authenticated:
        profile_pic = getattr(user, 'profilepic', None)
        if profile_pic:
            avatar_url = profile_pic.url
        notifications_unread = Notification.objects.filter(user=user, read=False).count()

    return {
        'avatar_url': avatar_url,
        'notifications_unread': notifications_unread,
    }


def _owner_user():
    """The account that owns the site: the first superuser, else the oldest user."""
    owner = MyUser.objects.filter(is_superuser=True).order_by('id').first()
    if owner is None:
        owner = MyUser.objects.order_by('id').first()
    return owner


def site(request):
    """Expose the site settings, the owner profile and shared links."""
    site_settings = SiteSettings.current()
    owner = site_settings.owner or _owner_user()

    resolver = getattr(request, 'resolver_match', None)
    url_name = getattr(resolver, 'url_name', None)

    return {
        'site_settings': site_settings,
        'site_owner': owner,
        'site_name': site_settings.site_name or 'FelloMarley Foundation',
        'site_tagline': site_settings.tagline or '',
        'owner_name': owner.display_name if owner else 'FelloMarley',
        'owner_headline': (owner.headline if owner else '') or 'Software Developer & Tech Enthusiast',
        'owner_location': (owner.location if owner else '') or 'Nairobi, Kenya',
        'owner_bio': (owner.bio if owner else '') or '',
        'owner_socials': owner.social_links if owner else [],
        'owner_avatar': owner.profilepic if owner else None,
        'social_links': owner.social_links if owner else [],
        'site_description': site_settings.site_description or (
            'Portfolio of FelloMarley, a software developer building modern web '
            'applications with Django, Python, JavaScript and Tailwind CSS.'
        ),
        'meta_robots': 'index, follow' if url_name in PUBLIC_URL_NAMES else 'noindex, follow',
        'media_url': settings.MEDIA_URL,
    }
