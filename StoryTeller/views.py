import io
import os
import re
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from twilio.rest import Client

from StoryTeller.models import (
    FAQ,
    Activity,
    BlogPost,
    Certification,
    Donation,
    EducationLevel,
    Event,
    EventCategory,
    EventLocation,
    Experience,
    ImageGallery,
    Job,
    JobApplication,
    MyUser,
    NewsletterSubscriber,
    Notification,
    PortfolioItem,
    Project,
    Sibling,
    SiblingImage,
    Skill,
    Support,
    Task,
    Testimonial,
    Volunteer,
    contact,
)

from .forms import (
    ActivityForm,
    BlogForm,
    CertificationForm,
    ContactusForm,
    DonationAdminForm,
    DonationForm,
    EducationLevelForm,
    EventCategoryForm,
    FAQForm,
    ImageGalleryForm,
    JobApplicationForm,
    JobForm,
    MessageForm,
    MyUserCreationForm,
    NewsletterForm,
    NotificationForm,
    OurSiblingsForm,
    PortfolioForm,
    ProjectForm,
    SiblingForm,
    SkillForm,
    SupportForm,
    TaskForm,
    TestimonialForm,
    VolunteerForm,
    eventlocationForm,
    eventsForm,
)

# Create your views here.

def owner_required(view_func):
    """Only the site owner (a superuser) may change shared content."""
    @login_required(login_url='login')
    @user_passes_test(lambda user: user.is_superuser, login_url='login')
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    wrapper.__name__ = getattr(view_func, '__name__', 'owner_required')
    wrapper.__doc__ = view_func.__doc__
    return wrapper


def _split_list(value):
    """Split a comma separated field into a clean list."""
    return [part.strip() for part in (value or '').split(',') if part.strip()]


def _initials(name):
    """Two letter initials for an avatar fallback."""
    parts = [p for p in (name or '').split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()


def _author_profile(user):
    """Display details for a post author, with a safe fallback for missing users."""
    if not user:
        return {
            'name': 'FelloMarley Foundation',
            'initials': 'FM',
            'avatar': None,
            'bio': 'Part of the FelloMarley Foundation team, sharing what we learn as we go.',
        }

    name = user.name or user.username
    avatar = None
    try:
        profile_pic = user.profilepic.name
    except ValueError:
        profile_pic = ''
    if profile_pic and default_storage.exists(profile_pic):
        avatar = user.profilepic.url

    return {
        'name': name,
        'initials': _initials(name),
        'avatar': avatar,
        'bio': user.bio or 'Part of the FelloMarley Foundation team, sharing what we learn as we go.',
    }


def portfolio_context():
    """Everything the portfolio pages need: enriched items, filters and stats."""
    portfolios = list(PortfolioItem.objects.select_related('author').all())

    category_labels = dict(PortfolioItem.CATEGORY_CHOICES)
    category_counts = {}
    technology_counts = {}
    total_technologies = 0

    for item in portfolios:
        item.tech_list = _split_list(item.technology)
        item.category_label = category_labels.get(item.category, 'Other')
        item.category_slug = (item.category or 'other')
        item.author_name = item.author.name if item.author else None
        item.excerpt = (item.description or '')[:220]
        item.has_media = bool(item.image or item.video)

        category_counts[item.category_slug] = category_counts.get(item.category_slug, 0) + 1
        for tech in item.tech_list:
            key = tech.lower()
            technology_counts[key] = technology_counts.get(key, 0) + 1
            total_technologies += 1

    portfolio_categories = [
        {
            'slug': slug,
            'label': category_labels.get(slug, 'Other'),
            'count': count,
            'percent': round(count * 100 / len(portfolios)) if portfolios else 0,
        }
        for slug, count in sorted(category_counts.items(), key=lambda kv: -kv[1])
    ]

    portfolio_technologies = [
        {'name': name, 'count': count}
        for name, count in sorted(technology_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:18]
    ]

    with_media = sum(1 for item in portfolios if item.has_media)

    return {
        'portfolios': portfolios,
        'portfolio_categories': portfolio_categories,
        'portfolio_technologies': portfolio_technologies,
        'portfolio_stats': {
            'total': len(portfolios),
            'categories': len(portfolio_categories),
            'technologies': len(technology_counts),
            'technology_mentions': total_technologies,
            'with_media': with_media,
            'featured': portfolios[0] if portfolios else None,
        },
    }


def events_context():
    """Everything the events pages need: schedule, filters and stats."""
    now = timezone.now()
    events = list(Event.objects.select_related('category', 'location', 'host').all())

    category_counts = {}
    location_counts = {}

    for event in events:
        event.is_upcoming = bool(event.start_date and event.start_date >= now)
        event.days_until = (event.start_date - now).days if event.is_upcoming else None
        event.guest_list = _split_list(event.guests)
        event.guest_count = len(event.guest_list)
        event.duration_label = _duration_label(event.start_date, event.end_date)
        event.schedule_label = _schedule_label(event.start_date, event.end_date)
        event.category_slug = (event.category.name if event.category else 'Uncategorised')
        event.location_name = event.location.name if event.location else 'To be announced'
        event.host_name = event.host.name if event.host else None
        event.excerpt = (event.description or '')[:200]

        if event.is_upcoming:
            key = event.category_slug
            category_counts[key] = category_counts.get(key, 0) + 1

        location_key = event.location_name
        location_counts[location_key] = location_counts.get(location_key, 0) + 1

    upcoming = [event for event in events if event.is_upcoming]
    past = [event for event in events if not event.is_upcoming]
    upcoming.sort(key=lambda e: (e.start_date is None, e.start_date))
    past.sort(key=lambda e: (e.start_date is None, e.start_date), reverse=True)

    event_categories = [
        {'name': name, 'count': count}
        for name, count in sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    event_locations = [
        {'name': name, 'count': count}
        for name, count in sorted(location_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    total_guests = sum(event.guest_count for event in events)

    return {
        'events': events,
        'upcoming_events': upcoming,
        'past_events': past,
        'event_categories': event_categories,
        'event_locations': event_locations,
        'event_stats': {
            'total': len(events),
            'upcoming': len(upcoming),
            'past': len(past),
            'categories': len(event_categories),
            'locations': len(event_locations),
            'guests': total_guests,
            'next_event': upcoming[0] if upcoming else None,
            'with_video': sum(1 for event in events if event.video),
        },
    }


def testimonials_context():
    """Everything the testimonials page needs: highlights, themes and stats."""
    testimonials = list(Testimonial.objects.select_related('user').all())

    designation_counts = {}
    word_total = 0

    for item in testimonials:
        item.initials = _initials(item.name)
        item.words = len((item.message or '').split())
        word_total += item.words
        item.excerpt = (item.message or '')[:260]
        key = item.designation or 'Community member'
        designation_counts[key] = designation_counts.get(key, 0) + 1

    testimonial_themes = [
        {'name': name, 'count': count}
        for name, count in sorted(designation_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    longest = max(testimonials, key=lambda t: t.words, default=None)
    most_recent = max(
        (t for t in testimonials if t.created_at),
        key=lambda t: t.created_at,
        default=None,
    )

    return {
        'testimonials': testimonials,
        'testimonial_themes': testimonial_themes,
        'featured_testimonial': longest,
        'recent_testimonial': most_recent,
        'testimonial_stats': {
            'total': len(testimonials),
            'people': len({t.name for t in testimonials if t.name}),
            'themes': len(testimonial_themes),
            'words': word_total,
            'average_words': round(word_total / len(testimonials)) if testimonials else 0,
            'longest': longest.words if longest else 0,
            'with_photo': sum(1 for t in testimonials if t.image),
        },
    }


def family_context():
    """Everything the family pages need: profiles, galleries and stats."""
    siblings = list(Sibling.objects.all())

    gallery_counts = dict(
        SiblingImage.objects.values_list('sibling_id').annotate(count=Count('id'))
    )

    occupation_counts = {}
    for sibling in siblings:
        sibling.initials = _initials(sibling.name)
        sibling.image_count = gallery_counts.get(sibling.id, 0)
        sibling.excerpt = (sibling.short_description or '')[:180]
        age = sibling.age if sibling.birthdate else None
        sibling.age_display = age if age is not None and 0 <= age <= 120 else None
        key = sibling.occupation or 'Unlisted'
        occupation_counts[key] = occupation_counts.get(key, 0) + 1

    ages = [sibling.age_display for sibling in siblings if sibling.age_display is not None]

    family_occupations = [
        {'name': name, 'count': count}
        for name, count in sorted(occupation_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    return {
        'siblings': siblings,
        'family_occupations': family_occupations,
        'family_stats': {
            'total': len(siblings),
            'photos': sum(sibling.image_count for sibling in siblings),
            'with_photo': sum(1 for sibling in siblings if sibling.profile_picture),
            'with_video': sum(1 for sibling in siblings if sibling.video),
            'youngest': min(ages) if ages else None,
            'oldest': max(ages) if ages else None,
            'occupations': len(family_occupations),
        },
    }


def blog_context(request=None):
    """Everything the blog pages need: posts, taxonomy, filters and stats."""
    posts = list(BlogPost.objects.select_related('author').all())

    category_labels = dict(BlogPost.categorychoice)
    editor = bool(
        request
        and getattr(request, 'user', None)
        and request.user.is_authenticated
        and request.user.is_superuser
    )

    for post in posts:
        profile = _author_profile(post.author)
        post.author_name = profile['name']
        post.author_initials = profile['initials']
        post.author_avatar = profile['avatar']
        post.category_label = category_labels.get(post.category, 'Uncategorised')
        post.category_slug = post.category or 'uncategorised'
        post.is_published = post.status == 'published'
        post.status_label = 'Published' if post.is_published else 'Draft'
        post.word_count = len((post.content or '').split())
        post.has_media = bool(post.image or post.video)
        post.has_video = bool(post.video)

    # --- Taxonomy -----------------------------------------------------------
    category_counts = {}
    tag_counts = {}
    archive_counts = {}

    for post in posts:
        category_counts[post.category_slug] = category_counts.get(post.category_slug, 0) + 1
        for tag in post.tag_list:
            key = tag.lower()
            tag_counts[key] = tag_counts.get(key, 0) + 1
        if post.created_at:
            archive_key = post.created_at.strftime('%Y-%m')
            archive_counts[archive_key] = archive_counts.get(archive_key, 0) + 1

    total_posts = len(posts)

    blog_categories = [
        {
            'slug': slug,
            'label': category_labels.get(slug, 'Uncategorised'),
            'count': count,
            'percent': round(count * 100 / total_posts) if total_posts else 0,
        }
        for slug, count in sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    blog_tags = [
        {'name': name, 'count': count}
        for name, count in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:24]
    ]

    blog_archives = [
        {
            'key': key,
            'label': datetime.strptime(key, '%Y-%m').strftime('%B %Y'),
            'count': count,
        }
        for key, count in sorted(archive_counts.items(), key=lambda kv: kv[0], reverse=True)
    ]

    # --- Highlights ---------------------------------------------------------
    published = [post for post in posts if post.is_published]
    featured_post = None
    for candidate in published:
        if candidate.image:
            featured_post = candidate
            break
    if featured_post is None and published:
        featured_post = published[0]

    popular_posts = sorted(published, key=lambda p: (-p.views, -p.word_count))[:5]
    recent_posts = sorted(published, key=lambda p: p.created_at or timezone.now(), reverse=True)[:5]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    category_filter = (request.GET.get('category') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = posts if editor else published

    if query:
        needle = query.lower()

        def matches(post):
            haystacks = (post.title, post.content, post.tags, post.author_name)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [post for post in visible if matches(post)]

    if category_filter:
        visible = [post for post in visible if post.category_slug == category_filter]

    if status_filter in ('published', 'drafted'):
        visible = [post for post in visible if (post.status or 'drafted') == status_filter]

    if sort == 'oldest':
        visible.sort(key=lambda p: p.created_at or timezone.now())
    elif sort == 'popular':
        visible.sort(key=lambda p: (-p.views, -p.word_count))
    elif sort == 'title':
        visible.sort(key=lambda p: p.title.lower())
    elif sort == 'reading':
        visible.sort(key=lambda p: -p.reading_time)
    else:
        visible.sort(key=lambda p: p.created_at or timezone.now(), reverse=True)

    # The featured story gets its own spotlight, so keep it out of the grid.
    filters_active = bool(query or category_filter or status_filter)
    if not filters_active and featured_post is not None:
        visible = [post for post in visible if post.pk != featured_post.pk]

    page_obj = Paginator(visible, 9).get_page(request.GET.get('page') if request else 1)

    return {
        'blogs': page_obj,
        'blog_posts': visible,
        'featured_post': featured_post,
        'popular_posts': popular_posts,
        'recent_posts': recent_posts,
        'blog_categories': blog_categories,
        'blog_tags': blog_tags,
        'blog_archives': blog_archives,
        'blog_stats': {
            'total': total_posts,
            'published': len(published),
            'drafts': total_posts - len(published),
            'categories': len(blog_categories),
            'tags': len(tag_counts),
            'views': sum(post.views for post in posts),
            'words': sum(post.word_count for post in posts),
            'authors': len({post.author_id for post in posts if post.author_id}),
            'with_media': sum(1 for post in posts if post.has_media),
            'longest': max(posts, key=lambda p: p.word_count, default=None),
        },
        'blog_query': query,
        'blog_category': category_filter,
        'blog_status': status_filter,
        'blog_sort': sort,
        'blog_filters_active': filters_active,
        'blog_is_editor': editor,
        'blog_sort_options': [
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('popular', 'Most read'),
            ('reading', 'Longest read'),
            ('title', 'A - Z'),
        ],
        'blog_status_options': [('published', 'Published'), ('drafted', 'Draft')],
    }


def _duration_label(start, end):
    """Human readable event duration."""
    if not start or not end:
        return None
    total = int((end - start).total_seconds() // 60)
    if total <= 0:
        return None
    days, hours = divmod(total // 60, 24)
    minutes = total % 60
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes and not days:
        parts.append(f"{minutes} min")
    return " · ".join(parts) if parts else None


def _schedule_label(start, end):
    """Human readable event schedule."""
    if not start:
        return "To be scheduled"
    if end:
        return f"{start.strftime('%b %d, %Y · %H:%M')} – {end.strftime('%H:%M')}"
    return start.strftime('%b %d, %Y · %H:%M')


def _month_span(oldest, today=None, max_buckets=24):
    """Month buckets from the oldest activity month up to the current month."""
    today = today or timezone.now()
    tz = timezone.get_current_timezone()
    if oldest is None:
        oldest = today

    start_index = oldest.year * 12 + (oldest.month - 1)
    end_index = today.year * 12 + (today.month - 1)
    total = end_index - start_index + 1

    if total > max_buckets:
        start_index = end_index - max_buckets + 1

    buckets = []
    for index in range(start_index, end_index + 1):
        year, month = divmod(index, 12)
        month += 1
        start = datetime(year, month, 1, tzinfo=tz)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=tz)
        else:
            end = datetime(year, month + 1, 1, tzinfo=tz)
        buckets.append((start, end))
    return buckets


def _count_by_month(queryset, field, buckets):
    """Count queryset rows per month bucket for a datetime field."""
    counts = []
    for start, end in buckets:
        counts.append(queryset.filter(**{f"{field}__gte": start, f"{field}__lt": end}).count())
    return counts


def _label(value, fallback="Unspecified"):
    """Readable label for a possibly empty aggregate value."""
    if value is None or value == '':
        return fallback
    return str(value).replace('_', ' ').title()


def analytics_context():
    """Aggregated metrics, trends and chart payloads for the analytics page."""
    now = timezone.now()

    users = MyUser.objects.all()
    posts = BlogPost.objects.all()
    portfolio_items = PortfolioItem.objects.all()
    projects = Project.objects.all()
    events = Event.objects.all()
    inbox = contact.objects.all()
    supports = Support.objects.all()
    tasks = Task.objects.all()
    applications = JobApplication.objects.all()
    notifications = Notification.objects.all()
    media = ImageGallery.objects.all()

    # --- Window: start at the oldest tracked activity so trends are never blank ---
    oldest_candidates = []
    for queryset, field in (
        (users, 'date_joined'),
        (posts, 'created_at'),
        (portfolio_items, 'date_created'),
        (inbox, 'date_created'),
    ):
        earliest = queryset.order_by(field).values_list(field, flat=True).first()
        if earliest:
            oldest_candidates.append(earliest)
    oldest = min(oldest_candidates) if oldest_candidates else None

    buckets = _month_span(oldest, now)
    labels = [start.strftime('%b %Y') for start, _ in buckets]

    # --- Member metrics ---
    total_users = users.count()
    new_users = users.filter(date_joined__gte=now - timedelta(days=30)).count()
    active_users = users.filter(last_login__gte=now - timedelta(days=30)).count()
    staff_users = users.filter(is_staff=True).count()

    gender_rows = list(
        users.exclude(gender=None)
        .values('gender')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    gender_distribution = [
        {'gender': _label(row['gender'], 'Not specified'), 'count': row['count']}
        for row in gender_rows
    ]

    # --- Content metrics ---
    published_posts = posts.filter(status='published').count()
    draft_posts = posts.exclude(status='published').count()

    post_status_rows = list(posts.values('status').annotate(count=Count('id')).order_by('-count'))
    post_status = [
        {'label': _label(row['status'], 'Unspecified'), 'count': row['count']}
        for row in post_status_rows
    ]

    # --- Event metrics ---
    event_category_rows = list(
        events.values('category__name')
        .annotate(
            count=Count('id'),
            male_count=Count('id', filter=Q(host__gender='male')),
            female_count=Count('id', filter=Q(host__gender='female')),
        )
        .order_by('-count')
    )
    events_by_category = [
        {
            'category__name': _label(row['category__name'], 'Uncategorised'),
            'count': row['count'],
            'male_count': row['male_count'],
            'female_count': row['female_count'],
        }
        for row in event_category_rows
    ]

    event_location_rows = list(
        events.values('location__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    events_by_location = [
        {'location__name': _label(row['location__name'], 'TBA'), 'count': row['count']}
        for row in event_location_rows
    ]

    upcoming_events = events.filter(start_date__gte=now).count()

    # --- Support, tasks and applications ---
    support_status_rows = list(supports.values('status').annotate(count=Count('id')).order_by('-count'))
    support_by_status = [
        {'label': _label(row['status'], 'Unknown'), 'count': row['count']}
        for row in support_status_rows
    ]

    support_priority_rows = list(supports.values('priority').annotate(count=Count('id')).order_by('-count'))
    support_by_priority = [
        {'label': _label(row['priority'], 'Unassigned'), 'count': row['count']}
        for row in support_priority_rows
    ]

    task_buckets = []
    for priority in ['urgent', 'high', 'medium', 'low', None]:
        open_count = tasks.filter(priority=priority, completed=False).count()
        done_count = tasks.filter(priority=priority, completed=True).count()
        if open_count or done_count:
            task_buckets.append({
                'label': priority.title() if priority else 'Unassigned',
                'open': open_count,
                'done': done_count,
            })

    application_rows = list(applications.values('status').annotate(count=Count('id')).order_by('-count'))
    application_by_status = [
        {'label': _label(row['status'], 'Unknown'), 'count': row['count']}
        for row in application_rows
    ]

    # --- Education ---
    education_rows = list(
        EducationLevel.objects.values('level').annotate(count=Count('id')).order_by('-count')
    )
    education_levels = [
        {'level': _label(row['level'], 'Unspecified'), 'count': row['count']}
        for row in education_rows
    ]

    # --- Time series ---
    member_series = _count_by_month(users, 'date_joined', buckets)
    post_series = _count_by_month(posts, 'created_at', buckets)
    portfolio_series = _count_by_month(portfolio_items, 'date_created', buckets)
    message_series = _count_by_month(inbox, 'date_created', buckets)
    event_series = _count_by_month(events, 'start_date', buckets)

    # --- Portfolio discipline split ---
    portfolio_rows = list(
        portfolio_items.values('category').annotate(count=Count('id')).order_by('-count')
    )
    portfolio_by_category = [
        {'label': _label(row['category'], 'Other'), 'count': row['count']}
        for row in portfolio_rows
    ]

    # --- Latest activity ---
    recent_posts = list(posts.select_related('author').order_by('-created_at')[:6])
    recent_events = list(events.select_related('category', 'location').order_by('-start_date')[:6])

    headline = [
        {
            'label': 'Members',
            'value': total_users,
            'detail': f"{new_users} joined in the last 30 days",
            'icon': 'fa-users',
            'tone': 'blue',
        },
        {
            'label': 'Active members',
            'value': active_users,
            'detail': 'Signed in within 30 days',
            'icon': 'fa-user-check',
            'tone': 'emerald',
        },
        {
            'label': 'Published posts',
            'value': published_posts,
            'detail': f"{draft_posts} still in draft",
            'icon': 'fa-newspaper',
            'tone': 'violet',
        },
        {
            'label': 'Portfolio pieces',
            'value': portfolio_items.count(),
            'detail': f"{projects.count()} source projects",
            'icon': 'fa-briefcase',
            'tone': 'amber',
        },
        {
            'label': 'Events',
            'value': events.count(),
            'detail': f"{upcoming_events} still upcoming",
            'icon': 'fa-calendar-day',
            'tone': 'rose',
        },
        {
            'label': 'Open tickets',
            'value': supports.exclude(status__in=['resolved', 'closed']).count(),
            'detail': f"{supports.count()} raised in total",
            'icon': 'fa-life-ring',
            'tone': 'cyan',
        },
        {
            'label': 'Applications',
            'value': applications.count(),
            'detail': f"{applications.filter(status='under_review').count()} under review",
            'icon': 'fa-file-lines',
            'tone': 'indigo',
        },
        {
            'label': 'Media assets',
            'value': media.count(),
            'detail': f"{notifications.count()} notifications tracked",
            'icon': 'fa-images',
            'tone': 'teal',
        },
    ]

    return {
        # Headline numbers
        'total_users': total_users,
        'new_users': new_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'analytics_headline': headline,

        # Chart payloads
        'chart_growth': {
            'labels': labels,
            'members': member_series,
            'posts': post_series,
            'portfolio': portfolio_series,
            'messages': message_series,
            'events': event_series,
        },
        'chart_gender': {
            'labels': [row['gender'] for row in gender_distribution],
            'data': [row['count'] for row in gender_distribution],
        },
        'chart_events_category': {
            'labels': [row['category__name'] for row in events_by_category],
            'data': [row['count'] for row in events_by_category],
        },
        'chart_events_location': {
            'labels': [row['location__name'] for row in events_by_location],
            'data': [row['count'] for row in events_by_location],
        },
        'chart_comparative': {
            'labels': [row['category__name'] for row in events_by_category],
            'male': [row['male_count'] for row in events_by_category],
            'female': [row['female_count'] for row in events_by_category],
        },
        'chart_posts_over_time': {
            'labels': labels,
            'data': post_series,
        },
        'chart_portfolio_over_time': {
            'labels': labels,
            'data': portfolio_series,
        },
        'chart_education': {
            'labels': [row['level'] for row in education_levels],
            'data': [row['count'] for row in education_levels],
        },
        'chart_post_status': {
            'labels': [row['label'] for row in post_status],
            'data': [row['count'] for row in post_status],
        },
        'chart_support': {
            'labels': [row['label'] for row in support_by_status],
            'data': [row['count'] for row in support_by_status],
        },
        'chart_support_priority': {
            'labels': [row['label'] for row in support_by_priority],
            'data': [row['count'] for row in support_by_priority],
        },
        'chart_tasks': {
            'labels': [row['label'] for row in task_buckets],
            'open': [row['open'] for row in task_buckets],
            'done': [row['done'] for row in task_buckets],
        },
        'chart_applications': {
            'labels': [row['label'] for row in application_by_status],
            'data': [row['count'] for row in application_by_status],
        },
        'chart_portfolio_category': {
            'labels': [row['label'] for row in portfolio_by_category],
            'data': [row['count'] for row in portfolio_by_category],
        },

        # Tables
        'gender_distribution': gender_distribution,
        'events_by_category': events_by_category,
        'events_by_location': events_by_location,
        'blog_posts_over_time': [{'month': label, 'count': value} for label, value in zip(labels, post_series)],
        'portfolio_items_over_time': [{'month': label, 'count': value} for label, value in zip(labels, portfolio_series)],
        'education_levels': education_levels,
        'post_status': post_status,
        'support_by_status': support_by_status,
        'support_by_priority': support_by_priority,
        'task_buckets': task_buckets,
        'application_by_status': application_by_status,
        'portfolio_by_category': portfolio_by_category,
        'recent_posts': recent_posts,
        'recent_events': recent_events,
        'analytics_labels': labels,
    }


def home_context():
    """Shared context for the public landing page."""
    published = BlogPost.objects.exclude(status='drafted').order_by('-created_at')
    blogs = published[:3] if published.exists() else BlogPost.objects.all()[:3]

    projects = list(Project.objects.all())

    featured = list(Project.objects.filter(featured=True))
    home_projects = featured or projects[:8]

    return {
        'skill': Skill.objects.all(),
        'skills': Skill.objects.all(),
        'testimonials': Testimonial.objects.all()[:5],
        'projects': projects,
        'featured_projects': featured,
        'home_projects': home_projects,
        'portfolio_items': PortfolioItem.objects.all()[:6],
        'blogs': blogs,
        'education_levels': EducationLevel.objects.all(),
        'certifications': Certification.objects.all(),
        'events': Event.objects.all()[:4],
        'activities': Activity.objects.all()[:4],
        'images': ImageGallery.objects.all(),
        'faqs': FAQ.objects.all()[:6],
        'experiences': Experience.objects.all(),
        'current_year': timezone.now().year,
        'media_url': settings.MEDIA_URL,
        'cv_url': f"{settings.MEDIA_URL}resumes/Felixs_CV.pdf",
    }


def me(request):
    return render(request, 'home.html', home_context())


def public_contact(request):
    """Contact form on the landing page (public, no login required)."""
    if request.method == 'POST':
        data = request.POST.copy()
        data['phone'] = re.sub(r'[\s\-()]', '', data.get('phone', '').strip())
        form = ContactusForm(data)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thanks for reaching out! Your message has been received.')
            return redirect('me')
        messages.error(request, 'Please correct the highlighted fields and try again.')
        context = home_context()
        context['contact_form'] = form
        return render(request, 'home.html', context)

    return redirect('me')


def newsletter_subscribe(request):
    """Newsletter signup from the landing page."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email address.')
        elif NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            messages.info(request, 'You are already subscribed to the newsletter.')
        else:
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Subscribed! Thanks for joining the newsletter.')
            else:
                messages.error(request, 'Please enter a valid email address.')
        return redirect('me')

    return redirect('me')

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html', dashboard_context(request))


def _month_windows(now, months=6):
    """Ordered (year, month) windows ending with the current month."""
    windows = []
    for offset in range(months - 1, -1, -1):
        year = now.year
        month = now.month - offset
        while month <= 0:
            month += 12
            year -= 1
        windows.append((year, month))
    return windows


def _series_by_month(queryset, date_field):
    """{ (year, month): count } for a queryset."""
    rows = queryset.annotate(month=TruncMonth(date_field)).values('month').annotate(count=Count('id'))
    return {(row['month'].year, row['month'].month): row['count'] for row in rows if row['month']}


def _timeline(bucket_maps, now, max_months=12):
    """Months to plot: from the first month that has data up to the current month."""
    months = set()
    for buckets in bucket_maps:
        months.update(key for key, value in buckets.items() if value)

    current = (now.year, now.month)
    if not months:
        return list(_month_windows(now, 6))

    ordered = sorted(months)
    if ordered[-1] != current:
        ordered.append(current)
    return ordered[-max_months:]


def _values(buckets, timeline):
    """Bucket counts aligned to a timeline."""
    return [buckets.get(key, 0) for key in timeline]


def _trend(queryset, date_field, now):
    """Percentage change between the last 30 days and the 30 days before."""
    current = queryset.filter(**{f'{date_field}__gte': now - timedelta(days=30)}).count()
    previous = queryset.filter(**{f'{date_field}__gte': now - timedelta(days=60),
                                  f'{date_field}__lt': now - timedelta(days=30)}).count()
    if previous == 0:
        return 100.0 if current else 0.0
    return round(((current - previous) / previous) * 100, 1)


def dashboard_context(request):
    """Everything the dashboard needs: KPIs, trends, chart series and activity."""
    now = timezone.now()

    users = MyUser.objects.all()
    posts = BlogPost.objects.all()
    portfolio = PortfolioItem.objects.all()
    events = Event.objects.all()
    media = ImageGallery.objects.all()
    messages = contact.objects.all()
    tasks = Task.objects.all()
    supports = Support.objects.all()
    applications = JobApplication.objects.all()
    skills = Skill.objects.all()

    # Time series ------------------------------------------------------------
    user_buckets = _series_by_month(users, 'date_joined')
    post_buckets = _series_by_month(posts, 'created_at')
    portfolio_buckets = _series_by_month(portfolio, 'date_created')
    media_buckets = _series_by_month(media, 'created_at')
    message_buckets = _series_by_month(messages, 'date_created')

    timeline = _timeline([user_buckets, post_buckets, portfolio_buckets, media_buckets, message_buckets], now)
    labels = [datetime(year, month, 1).strftime('%b %Y') for year, month in timeline]

    # Distributions ----------------------------------------------------------
    gender_rows = list(users.values('gender').annotate(count=Count('id')))
    category_rows = list(events.values('category__name').annotate(count=Count('id')).order_by('-count'))
    location_rows = list(events.values('location__name').annotate(count=Count('id')).order_by('-count'))
    support_rows = list(supports.values('status').annotate(count=Count('id')))
    application_rows = list(applications.values('status').annotate(count=Count('id')))

    top_skills = list(skills.order_by('-proficiency')[:8])

    # Task buckets by priority (including tasks saved without a priority)
    task_buckets = []
    for priority in ['urgent', 'high', 'medium', 'low', None]:
        open_count = tasks.filter(priority=priority, completed=False).count()
        done_count = tasks.filter(priority=priority, completed=True).count()
        if open_count or done_count:
            task_buckets.append((priority.title() if priority else 'Unassigned', open_count, done_count))
    if not task_buckets:
        task_buckets = [(priority.title(), 0, 0) for priority in ['low', 'medium', 'high', 'urgent']]

    context = {
        # Headline numbers
        'user_count': users.count(),
        'users_new': users.filter(date_joined__gte=now - timedelta(days=30)).count(),
        'project_count': Project.objects.count(),
        'Portfolio_count': portfolio.count(),
        'blog_count': posts.count(),
        'posts_published': posts.filter(status='published').count(),
        'posts_drafted': posts.exclude(status='published').count(),
        'event_count': events.count(),
        'events_upcoming': events.filter(start_date__gte=now).count(),
        'media_count': media.count(),
        'message_count': messages.count(),
        'task_count': tasks.count(),
        'tasks_open': tasks.filter(completed=False).count(),
        'tasks_done': tasks.filter(completed=True).count(),
        'tasks_overdue': tasks.filter(completed=False, due_date__lt=now).count(),
        'notification_count': Notification.objects.count(),
        'notifications_unread': Notification.objects.filter(read=False).count(),
        'donation_count': Donation.objects.filter(status='completed').count(),
        'donation_total': sum(
            (donation.amount for donation in Donation.objects.filter(status='completed')),
            Decimal('0'),
        ),
        'donation_pending': sum(
            (donation.amount for donation in Donation.objects.filter(status='pending')),
            Decimal('0'),
        ),
        'support_count': supports.count(),
        'support_open': supports.exclude(status__in=['resolved', 'closed']).count(),
        'jobs_count': Job.objects.count(),
        'applications_count': applications.count(),
        'skill_count': skills.count(),
        'certification_count': Certification.objects.count(),
        'sibling_count': Sibling.objects.count(),
        'volunteer_count': Volunteer.objects.count(),
        'subscriber_count': NewsletterSubscriber.objects.count(),
        'testimonial_count': Testimonial.objects.count(),
        'education_count': EducationLevel.objects.count(),

        # Trends (percent change over the last 30 days)
        'trend_users': _trend(users, 'date_joined', now),
        'trend_portfolio': _trend(portfolio, 'date_created', now),
        'trend_posts': _trend(posts, 'created_at', now),
        'trend_media': _trend(media, 'created_at', now),
        'trend_messages': _trend(messages, 'date_created', now),

        # Chart payloads
        'chart_users_growth': {
            'labels': labels,
            'data': _values(user_buckets, timeline),
        },
        'chart_posts_over_time': {
            'labels': labels,
            'blog': _values(post_buckets, timeline),
            'portfolio': _values(portfolio_buckets, timeline),
            'media': _values(media_buckets, timeline),
            'messages': _values(message_buckets, timeline),
        },
        'chart_content_mix': {
            'labels': ['Portfolio', 'Projects', 'Blog Posts', 'Events', 'Media', 'Skills'],
            'data': [
                portfolio.count(),
                Project.objects.count(),
                posts.count(),
                events.count(),
                media.count(),
                skills.count(),
            ],
        },
        'chart_gender': {
            'labels': [(row['gender'] or 'unspecified').title() for row in gender_rows],
            'data': [row['count'] for row in gender_rows],
        },
        'chart_events_category': {
            'labels': [row['category__name'] or 'Uncategorised' for row in category_rows],
            'data': [row['count'] for row in category_rows],
        },
        'chart_events_location': {
            'labels': [row['location__name'] or 'Unspecified' for row in location_rows],
            'data': [row['count'] for row in location_rows],
        },
        'chart_skills': {
            'labels': [skill.name for skill in top_skills],
            'data': [skill.proficiency for skill in top_skills],
        },
        'chart_tasks': {
            'labels': [bucket[0] for bucket in task_buckets],
            'open': [bucket[1] for bucket in task_buckets],
            'done': [bucket[2] for bucket in task_buckets],
        },
        'chart_support': {
            'labels': [row['status'].replace('_', ' ').title() for row in support_rows],
            'data': [row['count'] for row in support_rows],
        },
        'chart_applications': {
            'labels': [row['status'].replace('_', ' ').title() for row in application_rows],
            'data': [row['count'] for row in application_rows],
        },

        # Recent activity feeds
        'recent_activities': Activity.objects.select_related('user').all()[:8],
        'recent_messages': messages.all()[:6],
        'recent_posts': posts.all()[:5],
        'recent_users': users.order_by('-date_joined')[:6],
        'recent_applications': applications.select_related('job').all()[:5],
        'recent_media': media.all()[:8],
        'upcoming_events': events.filter(start_date__gte=now).order_by('start_date')[:5],
        'past_events': events.filter(start_date__lt=now).order_by('-start_date')[:5],
        'open_tasks': tasks.filter(completed=False).order_by('due_date')[:6],
        'recent_notifications': Notification.objects.all()[:6],
    }

    if not context['upcoming_events']:
        context['upcoming_events'] = events.order_by('-start_date')[:5]

    return context

def _member_context(member):
    """Profile details, activity and stats for a single member."""
    profile = _author_profile(member)

    return {
        'user': member,
        'member': member,
        'member_profile': profile,
        'member_posts': BlogPost.objects.filter(author=member).order_by('-created_at')[:6],
        'member_events': Event.objects.filter(host=member).order_by('-start_date')[:6],
        'member_stats': {
            'posts': BlogPost.objects.filter(author=member).count(),
            'events': Event.objects.filter(host=member).count(),
            'tasks': Task.objects.filter(created_by=member).count(),
            'joined': member.date_joined,
            'last_login': member.last_login,
            'is_staff': member.is_staff,
            'is_superuser': member.is_superuser,
        },
    }


@owner_required
def user(request):
    """The member directory. It lists contact addresses, so it stays private."""
    m_user=MyUser.objects.all().order_by('-date_joined')
    return render(request,'user.html',{'m_user':m_user})

@login_required(login_url='login')
def user_details(request, user_id):
    member = get_object_or_404(MyUser, pk=user_id)
    return render(request, 'user_detail.html', _member_context(member))


@login_required(login_url='login')
def update_user(request, pk):
    """Edit a member profile. Only the account holder or the site owner may do it."""
    myuser = get_object_or_404(MyUser, id=pk)

    if request.user.pk != myuser.pk and not request.user.is_superuser:
        raise PermissionDenied('You can only edit your own profile.')

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES, instance=myuser)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully updated')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MyUserCreationForm(instance=myuser)

    context = {
        'myuser': myuser,
        'form': form,
    }
    return render(request, 'update_profile.html', context)


@login_required(login_url='login')
def delete_profile(request,pk):
    """Delete a member profile. Only the account holder or the site owner may do it."""
    delete_profile=get_object_or_404(MyUser,id=pk)

    if request.user.pk != delete_profile.pk and not request.user.is_superuser:
        raise PermissionDenied('You can only delete your own profile.')

    form=MyUserCreationForm(instance=delete_profile)
    if request.method=='POST':
        form=MyUserCreationForm(request.POST,instance=delete_profile)
        delete_profile.delete()
        messages.success(request,'Profile deleted successfully')
        return redirect('login')


    context={'delete_profile':delete_profile,
             'form':form}
    return render(request,'delete_profile.html',context)

def loginpage(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = MyUser.objects.get(email=email)
        except MyUser.DoesNotExist:
            return HttpResponse('User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.info(request, 'Login successful')
            if next_url:
                return redirect(next_url)
            return redirect('index')
        else:
            messages.warning(request, 'Wrong username or password')
    return render(request, 'login.html', {'next': next_url})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.html'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login')

def logoutuser(request):
    logout(request)
    messages.info(request,"Its sad to see you leave, welcome again " )
    return redirect('login')



def signup(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])  # This hashes the password
            user.save()  # Save the user
            messages.info(request, 'Registration successful, login to continue to main page')
            return redirect('login')  # Redirect to login page
        else:
            messages.warning(request, 'An error occurred during registration')

    return render(request, 'signup.html', {'form': form})

def blog(request):
    """The editorial hub: browse, search, filter and manage every post."""
    context = blog_context(request)
    return render(request, 'blogpost.html', context)


def blog_details(request, pk):
    """A single post with its reading meta, related stories and share tools."""
    detailedblog = get_object_or_404(BlogPost, id=pk)

    if not request.user.is_authenticated or not request.user.is_superuser:
        if detailedblog.status != 'published':
            messages.info(request, 'That post is still a draft and is not public yet.')
            return redirect('blog')

    BlogPost.objects.filter(pk=detailedblog.pk).update(views=detailedblog.views + 1)
    detailedblog.views += 1

    related = [
        post for post in BlogPost.objects.select_related('author')
        .filter(category=detailedblog.category)
        .exclude(pk=detailedblog.pk)
        if post.status == 'published'
    ][:3]

    if len(related) < 3:
        extra = BlogPost.objects.select_related('author').filter(status='published').exclude(
            pk__in=[detailedblog.pk] + [post.pk for post in related]
        )
        related.extend(list(extra)[:3 - len(related)])

    context = {
        'detailedblog': detailedblog,
        'related_posts': related,
        'author': _author_profile(detailedblog.author),
        'blog_stats': {
            'total': BlogPost.objects.count(),
            'published': BlogPost.objects.filter(status='published').count(),
            'views': detailedblog.views,
        },
    }
    return render(request, 'blog_details.html', context)


@login_required(login_url='login')
def add_blog(request):
    form = BlogForm()
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if not post.author_id:
                post.author = request.user
            if not post.status:
                post.status = 'drafted'
            post.save()
            messages.success(request, f'“{post.title}” was saved as a {post.status} post.')
            return redirect('blog')
    context = {'form': form, 'post': None}
    return render(request, 'add_blog.html', context)

@login_required(login_url='login')
def update_blog(request, pk):
    blog =get_object_or_404(BlogPost,id=pk)

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog post updated successfully!")
            return redirect('blog')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'update_blog.html', {'form': form, 'blog': blog, 'post': blog})

@login_required(login_url='login')
def delete_blog(request, pk):
    b = get_object_or_404(BlogPost, pk=pk)
    form = BlogForm(instance=b)
    if request.method == 'POST':
        b.delete()
        messages.success(request, 'BlogPost Deleted successfully')
        return redirect('blog')
    context = {'b': b, 'form': form}
    return render(request, 'deleteblog.html', context)

def Portfolio(request):
    context = portfolio_context()
    return render(request, 'portfoliopost.html', context)

def portfolio_details(request,pk):
    detailedportfolio=get_object_or_404(PortfolioItem, id=pk)
    context = portfolio_context()
    enriched = next(
        (item for item in context['portfolios'] if item.pk == detailedportfolio.pk),
        detailedportfolio,
    )
    context['detailedportfolio'] = enriched
    related = [
        item for item in context['portfolios']
        if item.pk != detailedportfolio.pk and item.category_slug == enriched.category_slug
    ]
    if not related:
        related = [item for item in context['portfolios'] if item.pk != detailedportfolio.pk]
    context['related_portfolios'] = related[:3]
    return render(request,'detailed_portfolio.html',context)

@owner_required
def add_portfolio(request):
    form=PortfolioForm()
    if request.method=='POST':
        form=PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('portfolio')
    context={'form':form}
    return render(request, 'add_portfolio.html',context)

@owner_required
def update_portfolio(request, pk):
    portfolio_item = get_object_or_404(PortfolioItem, pk=pk)

    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES, instance=portfolio_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Portfolio item updated successfully!")  # Show success message

            return redirect('portfolio')  # Redirect to the portfolio detail page
    else:
        form = PortfolioForm(instance=portfolio_item)

    return render(request, 'update_portfolio.html', {'form': form, 'portfolio_item': portfolio_item})

@owner_required
def delete_portfolio(request, pk):
    portfolio = PortfolioItem.objects.get(id=pk)
    form=PortfolioForm()

    if request.method == "POST":
        portfolio.delete()
        messages.success(request, "Portfolio deleted successfully!")
        return redirect('portfolio')  # Redirect back to the projects list
    context={'form':form,'portfolio': portfolio}
    return render(request,'delete_portfolio_confirm.html', context)  # Ensure user lands on confirm page

@login_required(login_url='login')
def ContactusPage(request):
    form = ContactusForm()

    if request.method == 'POST':
            form = ContactusForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')
    context={'form':form}
    return render(request, 'contact_us.html',context)

def eventsItem(request):
    context = events_context()
    return render(request, 'events.html', context)

def event_details(request,pk):
    """Legacy route: renders the same rich event page as ``event_detail``."""
    return event_detail(request, pk)

@owner_required
def add_event(request):
    form = eventsForm()
    if request.method=='POST':
            form=eventsForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('events')
    context={'form':form}

    return render(request, 'event_upload.html', context)

def event_category_list(request):

    form = EventCategoryForm()
    if request.method=='POST':
            form=EventCategoryForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('add_event')
    context={'form':form}
    return render(request, 'event_category_list.html', context)

def event_category_detail(request, category_id):
    category = get_object_or_404(EventCategory, id=category_id)

    return render(request, 'event_category_detail.html', {'category': category})

def event_location_list(request):
    form = eventlocationForm()
    if request.method=='POST':
            form=eventlocationForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect('add_event')
    context={'form':form}
    return render(request, 'event_location_list.html', context)

def event_location_detail(request, location_id):
    location = get_object_or_404(EventLocation, id=location_id)
    return render(request, 'event_location_detail.html', {'location': location})

@owner_required
def update_event(request, pk):
    event = get_object_or_404(Event, pk=pk)  # Get the event with the given primary key (pk)

    if request.method == 'POST':  # If the form is submitted
        form = eventsForm(request.POST, request.FILES, instance=event)  # Bind the form with the data and existing event instance
        if form.is_valid():  # If the form is valid
            form.save()  # Save the updated event
            messages.success(request, "Event updated successfully!")  # Show success message
            return redirect('events')  # Redirect to the event list page (change to your desired redirect location)
    else:
        form = eventsForm(instance=event)  # If it's a GET request, pre-populate the form with the existing event data

    return render(request, 'update_event.html', {'form': form, 'event': event})

@owner_required
def delete_event(request,pk):
    e=Event.objects.get(id=pk)
    form=eventsForm()
    if request.method=='POST':
        form=eventsForm(request.POST,instance=e)
        e.delete()
        messages.success(request,'Event deleted Successfully')
        return redirect('events')
    context={'form':form}
    return render(request, 'delete_event.html', context)

def about(request):
    """Full biography page, fed from the database wherever possible."""
    now = timezone.now()

    projects = list(Project.objects.all())

    context = {
        'skills': Skill.objects.all().order_by('-proficiency'),
        'education_levels': EducationLevel.objects.all(),
        'certifications': Certification.objects.all(),
        'projects': projects,
        'portfolio_items': PortfolioItem.objects.all()[:6],
        'events': Event.objects.all()[:6],
        'testimonials': Testimonial.objects.all()[:3],
        'media': ImageGallery.objects.all()[:8],
        'faqs': FAQ.objects.all()[:6],
        'experiences': Experience.objects.all(),
        'blog_count': BlogPost.objects.count(),
        'sibling_count': Sibling.objects.count(),
        'volunteer_count': Volunteer.objects.count(),
        'member_count': MyUser.objects.count(),
        'media_url': settings.MEDIA_URL,
        'cv_url': f"{settings.MEDIA_URL}resumes/Felixs_CV.pdf",
        'current_year': now.year,
    }

    return render(request, 'about.html', context)

def gallery_stats():
    """Counts shown beside the gallery, the upload form and the edit form."""
    media = ImageGallery.objects.all()

    return {
        'total_media': media.count(),
        'total_images': media.filter(video__isnull=True).count(),
        'total_videos': media.filter(video__isnull=False).count(),
    }


def gallery_view(request):
    """The media library: every image and video, with search and filters."""
    media_items = list(ImageGallery.objects.all())

    query = (request.GET.get('q') or '').strip()
    type_filter = (request.GET.get('type') or '').strip()
    sort = (request.GET.get('sort') or 'newest').strip()

    visible = list(media_items)

    if query:
        needle = query.lower()

        def matches(item):
            haystacks = (item.title, item.caption)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [item for item in visible if matches(item)]

    if type_filter == 'image':
        visible = [item for item in visible if not item.video]
    elif type_filter == 'video':
        visible = [item for item in visible if item.video]

    if sort == 'oldest':
        visible.sort(key=lambda item: item.created_at or timezone.now())
    elif sort == 'title':
        visible.sort(key=lambda item: (item.title or '').lower())
    else:
        visible.sort(key=lambda item: item.created_at or timezone.now(), reverse=True)

    context = {
        "images": visible,
        "media_items": visible,
        "all_media": media_items,
        "total_media": len(media_items),
        "total_images": len([item for item in media_items if not item.video]),
        "total_videos": len([item for item in media_items if item.video]),
        "gallery_query": query,
        "gallery_type": type_filter,
        "gallery_sort": sort,
        "gallery_filters_active": bool(query or type_filter),
        "gallery_sort_options": [
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('title', 'A - Z'),
        ],
    }

    return render(request, "gallery.html", context)


@owner_required
def add_image(request):

    form = ImageGalleryForm(request.POST or None, request.FILES or None)

    if request.method == "POST":

        if form.is_valid():

            form.save()

            messages.success(request, "Media uploaded successfully.")

            return redirect("gallery")

    return render(request, "add_image.html", {"form": form, **gallery_stats()})


@owner_required
def delete_image(request, pk):

    media = get_object_or_404(ImageGallery, pk=pk)

    if request.method == "POST":

        media.delete()

        messages.success(request, "Media deleted successfully.")

        return redirect("gallery")

    return render(
        request,
        "delete_image.html",
        {"media": media},
    )
def admin_required(view_func):
    """Restrict a view to superusers, sending everyone else to the login page."""
    @login_required(login_url='login')
    @user_passes_test(lambda u: u.is_superuser, login_url='login')
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = getattr(view_func, '__name__', 'admin_required')
    wrapper.__doc__ = view_func.__doc__
    return wrapper


@admin_required
def AdminsDashboard(request):
    """Administration console: KPIs, attention queue, analytics and moderation tables."""
    context = admin_context(request)
    return render(request, 'admins.html', context)


def admin_context(request):
    now = timezone.now()

    users = MyUser.objects.all()
    posts = BlogPost.objects.all()
    projects = Project.objects.all()
    portfolio_items = PortfolioItem.objects.all()
    media = ImageGallery.objects.all()
    events = Event.objects.all()
    messages = contact.objects.all()
    supports = Support.objects.all()
    tasks = Task.objects.all()
    applications = JobApplication.objects.all()
    notifications = Notification.objects.all()
    activities = Activity.objects.all()

    # Time series ------------------------------------------------------------
    member_buckets = _series_by_month(users, 'date_joined')
    post_buckets = _series_by_month(posts, 'created_at')
    portfolio_buckets = _series_by_month(portfolio_items, 'date_created')
    media_buckets = _series_by_month(media, 'created_at')
    message_buckets = _series_by_month(messages, 'date_created')

    timeline = _timeline([member_buckets, post_buckets, portfolio_buckets, media_buckets, message_buckets], now)
    labels = [datetime(year, month, 1).strftime('%b %Y') for year, month in timeline]

    category_rows = list(events.values('category__name').annotate(count=Count('id')).order_by('-count'))
    support_rows = list(supports.values('status').annotate(count=Count('id')))
    application_rows = list(applications.values('status').annotate(count=Count('id')))

    # Events carry an explicit upcoming/past flag so the template never has to
    # compare against a hardcoded calendar boundary.
    event_rows = []
    for event in events:
        event.is_upcoming = bool(event.start_date and event.start_date >= now)
        event_rows.append(event)

    task_buckets = []
    for priority in ['urgent', 'high', 'medium', 'low', None]:
        open_count = tasks.filter(priority=priority, completed=False).count()
        done_count = tasks.filter(priority=priority, completed=True).count()
        if open_count or done_count:
            task_buckets.append((priority.title() if priority else 'Unassigned', open_count, done_count))

    # Tasks carry an explicit overdue flag so the template never compares dates.
    task_rows = []
    for task in tasks:
        task_rows.append(task)

    return {
        'admin_now': now,
        # Headline numbers
        'members_total': users.count(),
        'members_new': users.filter(date_joined__gte=now - timedelta(days=30)).count(),
        'messages_total': messages.count(),
        'messages_recent': messages.filter(date_created__gte=now - timedelta(days=7)).count(),
        'posts_total': posts.count(),
        'posts_published': posts.filter(status='published').count(),
        'posts_draft': posts.exclude(status='published').count(),
        'projects_total': projects.count(),
        'portfolio_total': portfolio_items.count(),
        'media_total': media.count(),
        'events_total': events.count(),
        'events_upcoming': events.filter(start_date__gte=now).count(),
        'events_past': events.filter(start_date__lt=now).count(),
        'support_total': supports.count(),
        'support_open': supports.exclude(status__in=['resolved', 'closed']).count(),
        'tasks_total': tasks.count(),
        'tasks_open': tasks.filter(completed=False).count(),
        'tasks_overdue': tasks.filter(completed=False, due_date__lt=now).count(),
        'applications_total': applications.count(),
        'applications_pending': applications.filter(status='under_review').count(),
        'notifications_unread': notifications.filter(read=False).count(),
        'volunteers_total': Volunteer.objects.count(),
        'subscribers_total': NewsletterSubscriber.objects.count(),
        'certifications_total': Certification.objects.count(),
        'skills_total': Skill.objects.count(),
        'siblings_total': Sibling.objects.count(),
        'testimonials_total': Testimonial.objects.count(),
        'faqs_total': FAQ.objects.count(),

        # Trends
        'trend_members': _trend(users, 'date_joined', now),
        'trend_messages': _trend(messages, 'date_created', now),
        'trend_posts': _trend(posts, 'created_at', now),
        'trend_media': _trend(media, 'created_at', now),

        # Moderation tables
        'contactinfo': messages[:60],
        'userinfo': users.order_by('-date_joined')[:60],
        'eventinfo': event_rows,
        'jobapplicants': applications.select_related('job'),
        'posts_list': posts,
        'projects_list': projects,
        'portfolio_list': portfolio_items,
        'media_list': media[:40],
        'support_list': supports,
        'tasks_list': task_rows,
        'notification_list': notifications[:40],
        'activity_list': activities.select_related('user')[:40],
        'skill_list': Skill.objects.all().order_by('-proficiency'),
        'certification_list': Certification.objects.all(),
        'sibling_list': Sibling.objects.all(),
        'testimonial_list': Testimonial.objects.all(),
        'faq_list': FAQ.objects.all(),
        'volunteer_list': Volunteer.objects.all(),
        'subscriber_list': NewsletterSubscriber.objects.all(),

        # Charts
        'chart_admin_growth': {
            'labels': labels,
            'posts': _values(post_buckets, timeline),
            'portfolio': _values(portfolio_buckets, timeline),
            'media': _values(media_buckets, timeline),
            'messages': _values(message_buckets, timeline),
        },
        'chart_admin_members': {
            'labels': labels,
            'data': _values(member_buckets, timeline),
        },
        'chart_admin_inventory': {
            'labels': ['Posts', 'Projects', 'Portfolio', 'Media', 'Events', 'Members'],
            'data': [posts.count(), projects.count(), portfolio_items.count(),
                     media.count(), events.count(), users.count()],
        },
        'chart_admin_support': {
            'labels': [row['status'].replace('_', ' ').title() for row in support_rows],
            'data': [row['count'] for row in support_rows],
        },
        'chart_admin_applications': {
            'labels': [row['status'].replace('_', ' ').title() for row in application_rows],
            'data': [row['count'] for row in application_rows],
        },
        'chart_admin_categories': {
            'labels': [row['category__name'] or 'Uncategorised' for row in category_rows],
            'data': [row['count'] for row in category_rows],
        },
        'chart_admin_tasks': {
            'labels': [bucket[0] for bucket in task_buckets],
            'open': [bucket[1] for bucket in task_buckets],
            'done': [bucket[2] for bucket in task_buckets],
        },
    }

@owner_required
def jobdetails(request, pk):
    """Review one application: the posting, the applicant and the rest of the pipeline."""
    application = get_object_or_404(JobApplication, id=pk)
    context = applications_context(request)
    context['jobdet'] = application
    context['application'] = application
    context['job'] = application.job
    context['job_applications'] = [
        item for item in context['all_applications']
        if item.job_id == application.job_id and item.pk != application.pk
    ]
    return render(request, 'jobdetails.html', context)

@login_required(login_url='login')
def user_detail(request, pk):
    member = get_object_or_404(MyUser, id=pk)
    return render(request, 'user_detail.html', _member_context(member))

@login_required(login_url='login')
def siblings_list(request):
    context = family_context()
    return render(request, 'siblings_list.html', context)

@login_required(login_url='login')
def sibling_detail(request, sibling_id):
    sibling = get_object_or_404(Sibling, id=sibling_id)  # Only use get_object_or_404
    images = SiblingImage.objects.filter(sibling=sibling)  # Fixed typo here, using the correct variable
    context = family_context()
    enriched = next(
        (member for member in context['siblings'] if member.pk == sibling.pk),
        sibling,
    )
    context['sibling'] = enriched
    context['images'] = images
    context['related_siblings'] = [
        member for member in context['siblings'] if member.pk != sibling.pk
    ][:3]
    return render(request, 'sibling_detail.html', context)

@login_required(login_url='login')
def add_picture(request, sibling_id):
    sibling = get_object_or_404(Sibling, id=sibling_id)
    # Fetch existing images for the sibling
    images = SiblingImage.objects.filter(sibling=sibling)

    if request.method == 'POST':
        form = OurSiblingsForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)  # Save form but don't commit yet
            new_image.sibling = sibling  # Associate the image with the sibling
            new_image.save()  # Now save the image

            return redirect('sibling_detail', sibling_id=sibling.id)  # Redirect back to the sibling detail page
    else:
        form = OurSiblingsForm()  # If not POST, just show the empty form
    context={'sibling': sibling,
        'form': form,
        'images': images,}
    return render(request, 'ours.html',context)


def education_journey(request):
    # Fetch all education levels
    education_levels = EducationLevel.objects.all()
    return render(request, 'education_journey.html', {'education_levels': education_levels})

@login_required(login_url='login')
def education_level(request):
    form=EducationLevelForm()
    if request.method=='POST':
        form=EducationLevelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"You've successfully added your Education details")
            return redirect('education_journey')
    context={'form':form}
    return render(request,'education_level.html',context)


@login_required(login_url='login')
def update_education(request, education_id):
    # Get the education object by ID or return 404 if not found
    education = get_object_or_404(EducationLevel, pk=education_id)

    # If the form is submitted
    if request.method == 'POST':
        form = EducationLevelForm(request.POST, request.FILES, instance=education)
        if form.is_valid():
            form.save()
            # Redirect to a page that shows updated information
            return redirect('education_journey')
    else:
        # If it's a GET request, pre-fill the form with the existing data
        form = EducationLevelForm(instance=education)

    return render(request, 'update_education.html', {'form': form, 'education': education})

@login_required(login_url='login')
def dashboard(request):
    return render(request,'index.html')

@login_required(login_url='login')
def add_family(request):
    form = SiblingForm()
    if request.method == 'POST':
        form = SiblingForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('siblings_list')
    context={'form':form}
    return render(request, 'add_family.html',context)



@login_required(login_url='login')
def update_member(request, member_id):
    sibling = get_object_or_404(Sibling, id=member_id)
    form = SiblingForm(instance=sibling)

    if request.method == "POST":
        form = SiblingForm(request.POST, request.FILES, instance=sibling)
        if form.is_valid():
            form.save()
            messages.success(request, f"{sibling.name}'s details updated successfully!")
            return redirect('siblings_list')  # Redirect to the list after update

    return render(request, 'update_member.html', {'form': form, 'sibling': sibling})

def tasks_context(request=None):
    """Everything the task pages need: the board, taxonomy, filters and stats."""
    now = timezone.now()
    tasks = list(Task.objects.select_related('assigned_to', 'created_by').all())

    status_labels = dict(Task.STATUS_CHOICES)
    category_labels = dict(Task.CATEGORY_CHOICES)
    priority_order = ['urgent', 'high', 'medium', 'low']

    for task in tasks:
        task.due_soon = task.is_due_soon

    status_counts = {}
    priority_counts = {}
    category_counts = {}
    workload = {}
    tag_counts = {}

    for task in tasks:
        status_counts[task.status_slug] = status_counts.get(task.status_slug, 0) + 1
        priority_counts[task.priority_slug] = priority_counts.get(task.priority_slug, 0) + 1
        category_counts[task.category_slug] = category_counts.get(task.category_slug, 0) + 1

        name = task.assignee_name
        workload[name] = workload.get(name, 0) + 1

        for tag in task.tag_list:
            key = tag.lower()
            tag_counts[key] = tag_counts.get(key, 0) + 1

    total = len(tasks)
    completed = [task for task in tasks if task.completed]
    open_tasks = [task for task in tasks if not task.completed]
    overdue = [task for task in open_tasks if task.is_overdue]
    due_soon = [task for task in open_tasks if task.is_due_soon]
    week_ahead = now + timedelta(days=7)

    # --- Columns for the board ---------------------------------------------
    columns = []
    for slug in ('to_do', 'in_progress', 'blocked', 'done'):
        column_tasks = [task for task in tasks if task.status_slug == slug]
        column_tasks.sort(key=lambda t: (t.due_date is None, t.due_date or timezone.now()))
        columns.append({
            'slug': slug,
            'label': status_labels.get(slug, 'To Do'),
            'count': len(column_tasks),
            'items': column_tasks,
            'accent': {
                'to_do': 'slate',
                'in_progress': 'indigo',
                'blocked': 'rose',
                'done': 'emerald',
            }[slug],
        })

    task_statuses = [
        {'slug': slug, 'label': status_labels.get(slug, 'To Do'), 'count': status_counts.get(slug, 0)}
        for slug in ('to_do', 'in_progress', 'blocked', 'done')
    ]

    task_priorities = [
        {
            'slug': slug,
            'label': slug.capitalize(),
            'count': priority_counts.get(slug, 0),
        }
        for slug in priority_order
    ]

    task_categories = []
    for slug, label in category_labels.items():
        count = category_counts.get(slug, 0)
        task_categories.append({
            'slug': slug,
            'label': label,
            'count': count,
            'percent': round(count * 100 / total) if total else 0,
        })

    task_tags = [
        {'name': name, 'count': count}
        for name, count in sorted(tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
    ]

    assignees = [
        {'name': name, 'count': count}
        for name, count in sorted(workload.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    priority_filter = (request.GET.get('priority') or '').strip() if request else ''
    category_filter = (request.GET.get('category') or '').strip() if request else ''
    assignee_filter = (request.GET.get('assignee') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'due').strip() if request else 'due'

    visible = list(tasks)

    if query:
        needle = query.lower()

        def matches(task):
            haystacks = (task.title, task.description, task.assignee_name, task.notes)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [task for task in visible if matches(task)]

    if status_filter:
        visible = [task for task in visible if task.status_slug == status_filter]

    if priority_filter:
        visible = [task for task in visible if task.priority_slug == priority_filter]

    if category_filter:
        visible = [task for task in visible if task.category_slug == category_filter]

    if assignee_filter:
        visible = [task for task in visible if task.assignee_name == assignee_filter]

    if sort == 'newest':
        visible.sort(key=lambda t: t.created_at or timezone.now(), reverse=True)
    elif sort == 'oldest':
        visible.sort(key=lambda t: t.created_at or timezone.now())
    elif sort == 'priority':
        visible.sort(key=lambda t: (
            priority_order.index(t.priority_slug) if t.priority_slug in priority_order else 99,
            t.due_date or timezone.now(),
        ))
    elif sort == 'progress':
        visible.sort(key=lambda t: t.progress, reverse=True)
    elif sort == 'title':
        visible.sort(key=lambda t: (t.title or '').lower())
    else:  # due
        visible.sort(key=lambda t: (t.completed, t.due_date is None, t.due_date or timezone.now()))

    # The board always mirrors the filters that are applied.
    board_columns = []
    for column in columns:
        board_columns.append({
            **column,
            'items': [task for task in visible if task.status_slug == column['slug']],
            'count': sum(1 for task in visible if task.status_slug == column['slug']),
        })

    upcoming = sorted(
        [task for task in visible if not task.completed and task.due_date and task.due_date <= week_ahead],
        key=lambda t: t.due_date,
    )[:5]

    return {
        'tasks': visible,
        'all_tasks': tasks,
        'tasking': visible,
        'task_columns': board_columns,
        'task_statuses': task_statuses,
        'task_priorities': task_priorities,
        'task_categories': task_categories,
        'task_tags': task_tags,
        'task_assignees': assignees,
        'task_upcoming': upcoming,
        'task_stats': {
            'total': total,
            'open': len(open_tasks),
            'completed': len(completed),
            'overdue': len(overdue),
            'due_soon': len(due_soon),
            'unassigned': sum(1 for task in open_tasks if not task.assigned_to),
            'blocked': status_counts.get('blocked', 0),
            'in_progress': status_counts.get('in_progress', 0),
            'completion_rate': round(len(completed) * 100 / total) if total else 0,
            'hours': sum(float(task.estimated_hours or 0) for task in tasks),
            'hours_open': sum(float(task.estimated_hours or 0) for task in open_tasks),
            'assignees': len(assignees),
            'tags': len(task_tags),
        },
        'task_query': query,
        'task_status': status_filter,
        'task_priority': priority_filter,
        'task_category': category_filter,
        'task_assignee': assignee_filter,
        'task_sort': sort,
        'task_filters_active': bool(query or status_filter or priority_filter or category_filter or assignee_filter),
        'task_sort_options': [
            ('due', 'Due date'),
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('priority', 'Priority'),
            ('progress', 'Progress'),
            ('title', 'A - Z'),
        ],
    }


@login_required(login_url='login')
def tasks(request):
    context = tasks_context(request)
    return render(request, 'tasks.html', context)


@login_required(login_url='login')
def task_details(request, pk):
    task = get_object_or_404(Task, pk=pk)
    context = tasks_context(request)
    context['task'] = task
    context['taskdetails'] = task
    context['related_tasks'] = [
        item for item in context['all_tasks']
        if item.pk != task.pk and item.category_slug == task.category_slug
    ][:4]
    if len(context['related_tasks']) < 3:
        extra = [
            item for item in context['all_tasks']
            if item.pk != task.pk and item not in context['related_tasks']
        ][:3 - len(context['related_tasks'])]
        context['related_tasks'].extend(extra)
    return render(request, 'task_details.html', context)


@login_required(login_url='login')
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if not task.created_by_id:
                task.created_by = request.user
            if task.completed and not task.completed_at:
                task.completed_at = timezone.now()
            if task.completed:
                task.status = 'done'
                task.progress_percentage = 100
            task.save()
            messages.success(request, f"Task '{task.title}' added successfully!")
            return redirect('task_details', pk=task.pk)
    else:
        form = TaskForm()
        form.fields['created_by'].initial = request.user

    context = tasks_context(request)
    context['form'] = form
    return render(request, 'add_task.html', context)


@login_required(login_url='login')
def update_task(request, pk):
    task = get_object_or_404(Task, id=pk)
    original_creator_id = task.created_by_id

    if request.method == "POST":
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.created_by_id:
                updated.created_by_id = original_creator_id
            if updated.completed and not updated.completed_at:
                updated.completed_at = timezone.now()
            if not updated.completed:
                updated.completed_at = None
                if updated.status == 'done':
                    updated.status = 'in_progress'
            elif updated.status != 'blocked':
                updated.status = 'done'
                updated.progress_percentage = 100
            updated.save()
            messages.success(request, f"{task.title}'s details updated successfully!")
            return redirect('task_details', pk=task.pk)
    else:
        form = TaskForm(instance=task)

    context = tasks_context(request)
    context['form'] = form
    context['task'] = task
    return render(request, 'update_task.html', context)


@login_required(login_url='login')
def delete_task(request, pk):
    task = get_object_or_404(Task, id=pk)

    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f"Task '{title}' deleted successfully")
        return redirect('tasks')

    context = tasks_context(request)
    context['dele'] = task
    context['task'] = task
    context['form'] = TaskForm(instance=task)
    return render(request, 'delete_task.html', context)


@login_required(login_url='login')
def toggle_task(request, pk):
    """Mark a task done or reopen it, and let the assignee know."""
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        if task.completed:
            task.completed = False
            task.completed_at = None
            task.status = 'in_progress'
            task.progress_percentage = min(task.progress_percentage or 0, 90)
            messages.info(request, f"'{task.title}' is back on the board.")
        else:
            task.completed = True
            task.completed_at = timezone.now()
            task.status = 'done'
            task.progress_percentage = 100
            messages.success(request, f"'{task.title}' marked as done.")

        task.save()

        if task.assigned_to and task.assigned_to_id != request.user.id:
            Notification.objects.create(
                title=f"Task {'completed' if task.completed else 'reopened'}: {task.title}",
                description=(
                    f"{request.user.get_username()} marked '{task.title}' as "
                    f"{'done' if task.completed else 'open again'}."
                ),
                kind='task',
                link=f"/task_details/details/{task.pk}/",
                user=task.assigned_to,
            )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'completed': task.completed,
                'status': task.status_slug,
                'progress': task.progress,
            })

        return redirect('task_details', pk=task.pk)

    return redirect('tasks')


# Analytics view
@login_required(login_url='login')
def analytics(request):
    context = analytics_context()
    return render(request, 'analytics.html', context)

def notifications_context(request=None):
    """Everything the notification pages need: the feed, filters, taxonomy and stats."""
    notifications = list(Notification.objects.select_related('user').all())

    for item in notifications:
        item.excerpt = ' '.join((item.description or '').split())[:140]

    kind_counts = {}
    for item in notifications:
        kind_counts[item.kind_slug] = kind_counts.get(item.kind_slug, 0) + 1

    kind_labels = dict(Notification.KIND_CHOICES)
    notification_kinds = [
        {
            'slug': slug,
            'label': kind_labels.get(slug, 'System'),
            'count': count,
        }
        for slug, count in sorted(kind_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    total = len(notifications)
    unread = [item for item in notifications if not item.read]

    now = timezone.now()
    this_week = [
        item for item in notifications
        if item.created_at and (now - item.created_at).days < 7
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    state_filter = (request.GET.get('state') or 'all').strip() if request else 'all'
    kind_filter = (request.GET.get('kind') or '').strip() if request else ''

    visible = notifications

    if query:
        needle = query.lower()
        visible = [
            item for item in visible
            if needle in (item.title or '').lower()
            or needle in (item.description or '').lower()
        ]

    if state_filter == 'unread':
        visible = [item for item in visible if not item.read]
    elif state_filter == 'read':
        visible = [item for item in visible if item.read]

    if kind_filter:
        visible = [item for item in visible if item.kind_slug == kind_filter]

    return {
        'notify': visible,
        'all_notifications': notifications,
        'notification_kinds': notification_kinds,
        'notification_stats': {
            'total': total,
            'unread': len(unread),
            'read': total - len(unread),
            'this_week': len(this_week),
            'kinds': len(notification_kinds),
            'latest': notifications[0] if notifications else None,
        },
        'notification_query': query,
        'notification_state': state_filter,
        'notification_kind': kind_filter,
        'notification_filters_active': bool(query or kind_filter or state_filter != 'all'),
    }


# Notifications view
@login_required(login_url='login')
def notifications(request):
    context = notifications_context(request)
    return render(request, 'notifications.html', context)


@login_required(login_url='login')
def mark_notifications_read(request):
    """Mark every unread notification for the signed in user as read."""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect(request.POST.get('next') or 'notifications')
    return redirect('notifications')


@login_required(login_url='login')
def mark_notification_read(request, pk):
    """Mark a single notification as read and optionally follow its link."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == 'POST':
        notification.read = True
        notification.save(update_fields=['read'])

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications')


@login_required(login_url='login')
def add_notification(request):
    form = NotificationForm()
    form.fields['user'].required = False
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        form.fields['user'].required = False
        if form.is_valid():
            notification = form.save(commit=False)
            if not notification.user_id:
                notification.user = request.user
            notification.save()
            messages.success(request, 'Notifications added successfully.')
            return redirect('notifications')
    context = {'form': form}
    return render(request, 'add_notification.html', context)


@login_required(login_url='login')
def update_notification(request, pk):
    notification = get_object_or_404(Notification, id=pk)
    original_user_id = notification.user_id
    form = NotificationForm(instance=notification)
    form.fields['user'].required = False

    if request.method == "POST":
        form = NotificationForm(request.POST, request.FILES, instance=notification)
        form.fields['user'].required = False
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.user_id:
                updated.user_id = original_user_id
            updated.save()
            messages.success(request, f"{notification.title}'s details updated successfully!")
            return redirect('notifications')

    return render(request, 'update_notification.html', {'form': form, 'notifications': notification})


@login_required(login_url='login')
def delete_notifications(request, pk):
    notification = get_object_or_404(Notification, id=pk)

    if request.method == 'POST':
        title = notification.title
        notification.delete()
        messages.success(request, f'“{title}” was removed from the notification feed.')
        return redirect('notifications')

    context = {'notify': notification}
    return render(request, 'delete_notification.html', context)
# Activities view


@login_required(login_url='login')
def analytics_view(request):
    # 1. **Total Users**
    total_users = MyUser.objects.count()

    # 2. **Gender Distribution**
    gender_distribution = MyUser.objects.values('gender').annotate(count=Count('id'))

    # 3. **Events Stats**
    events_by_category = Event.objects.values('category__name').annotate(count=Count('id'))
    events_by_location = Event.objects.values('location__name').annotate(count=Count('id'))

    # 4. **Blog Posts Over Time**
    blog_posts_over_time = BlogPost.objects.annotate(month=TruncMonth('created_at')) \
                                           .values('month') \
                                           .annotate(count=Count('id')) \
                                           .order_by('month')

    # 5. **Portfolio Items Over Time**
    portfolio_items_over_time = PortfolioItem.objects.annotate(month=TruncMonth('date_created')) \
                                                     .values('month') \
                                                     .annotate(count=Count('id')) \
                                                     .order_by('month')

    # 6. **Education Levels Stats**
    education_levels = EducationLevel.objects.values('level').annotate(count=Count('id'))

    # 7. **Newsletter Subscribers**

    # **Context to pass to template**
    context = {
        'total_users': total_users,
        'gender_distribution': gender_distribution,
        'events_by_category': events_by_category,
        'events_by_location': events_by_location,
        'blog_posts_over_time': blog_posts_over_time,
        'portfolio_items_over_time': portfolio_items_over_time,
        'education_levels': education_levels
    }

    return render(request, 'analytics.html', context)



@owner_required
def update_image(request, image_id):
    # Get the image object to update
    image = get_object_or_404(ImageGallery, id=image_id)

    if request.method == 'POST':
        # If the form has been submitted
        form = ImageGalleryForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            # Save the form and redirect to the gallery page
            form.save()
            messages.success(request, f"'{image.title}' has been updated.")
            return redirect('gallery')  # Assuming 'gallery' is the name of the gallery page URL
    else:
        # Create a form instance with the image object
        form = ImageGalleryForm(instance=image)

    return render(request, 'update_image.html', {'form': form, 'image': image, **gallery_stats()})

@login_required(login_url='login')
def messaging(request):

    form=MessageForm()
    if request.method=='POST':
        form=MessageForm(request.POST)
        if form.is_valid():
         form.save()
         return redirect('admins')
    context={'form':form}
    return render(request,'messaging.html',context)

def activities_context(request=None):
    """Everything the activity pages need: the log, taxonomy, filters and stats."""
    activities = list(Activity.objects.select_related('user').all())

    type_labels = dict(Activity.TYPE_CHOICES)
    status_labels = dict(Activity.STATUS_CHOICES)

    for activity in activities:
        profile = _author_profile(activity.user)
        activity.author_name = profile['name']
        activity.author_initials = profile['initials']
        activity.author_avatar = profile['avatar']
        activity.type_slug = activity.activity_type or 'other'
        activity.status_slug = activity.status or 'planned'
        activity.word_count = len((activity.description or '').split())

    type_counts = {}
    status_counts = {}
    contributor_counts = {}
    location_counts = {}
    month_counts = {}

    for activity in activities:
        type_counts[activity.type_slug] = type_counts.get(activity.type_slug, 0) + 1
        status_counts[activity.status_slug] = status_counts.get(activity.status_slug, 0) + 1
        contributor_counts[activity.author_name] = contributor_counts.get(activity.author_name, 0) + 1
        if activity.location:
            location_counts[activity.location] = location_counts.get(activity.location, 0) + 1
        if activity.created_at:
            key = activity.created_at.strftime('%Y-%m')
            month_counts[key] = month_counts.get(key, 0) + 1

    total = len(activities)

    activity_types = [
        {
            'slug': slug,
            'label': type_labels.get(slug, 'Other'),
            'count': count,
            'percent': round(count * 100 / total) if total else 0,
        }
        for slug, count in sorted(type_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    activity_statuses = [
        {
            'slug': slug,
            'label': status_labels.get(slug, 'Planned'),
            'count': status_counts.get(slug, 0),
        }
        for slug in ('completed', 'ongoing', 'planned')
        if status_counts.get(slug, 0)
    ]

    contributors = [
        {'name': name, 'count': count}
        for name, count in sorted(contributor_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    venues = [
        {'name': name, 'count': count}
        for name, count in sorted(location_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    ]

    months = [
        {
            'key': key,
            'label': datetime.strptime(key, '%Y-%m').strftime('%B %Y'),
            'count': count,
        }
        for key, count in sorted(month_counts.items(), key=lambda kv: kv[0], reverse=True)[:12]
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    type_filter = (request.GET.get('type') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = activities

    if query:
        needle = query.lower()

        def matches(activity):
            haystacks = (activity.title, activity.description, activity.location, activity.author_name)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [activity for activity in visible if matches(activity)]

    if type_filter:
        visible = [activity for activity in visible if activity.type_slug == type_filter]

    if status_filter:
        visible = [activity for activity in visible if activity.status_slug == status_filter]

    if sort == 'oldest':
        visible.sort(key=lambda a: a.created_at or timezone.now())
    elif sort == 'participants':
        visible.sort(key=lambda a: -(a.participants or 0))
    elif sort == 'title':
        visible.sort(key=lambda a: (a.title or '').lower())
    else:
        visible.sort(key=lambda a: a.created_at or timezone.now(), reverse=True)

    # Group the visible activities into a month by month timeline.
    timeline = []
    for activity in visible:
        key = activity.created_at.strftime('%Y-%m') if activity.created_at else 'undated'
        if not timeline or timeline[-1]['key'] != key:
            timeline.append({
                'key': key,
                'label': datetime.strptime(key, '%Y-%m').strftime('%B %Y') if key != 'undated' else 'Undated',
                'count': 0,
                'items': [],
            })
        timeline[-1]['items'].append(activity)
        timeline[-1]['count'] += 1

    now = timezone.now()
    this_month = [
        activity for activity in activities
        if activity.created_at
        and activity.created_at.year == now.year
        and activity.created_at.month == now.month
    ]

    return {
        'activities': visible,
        'all_activities': activities,
        'activity_timeline': timeline,
        'activity_types': activity_types,
        'activity_statuses': activity_statuses,
        'activity_contributors': contributors,
        'activity_venues': venues,
        'activity_months': months,
        'activity_stats': {
            'total': total,
            'this_month': len(this_month),
            'participants': sum(activity.participants or 0 for activity in activities),
            'locations': len(location_counts),
            'types': len(activity_types),
            'contributors': len(contributors),
            'completed': status_counts.get('completed', 0),
            'ongoing': status_counts.get('ongoing', 0),
            'planned': status_counts.get('planned', 0),
            'words': sum(activity.word_count for activity in activities),
        },
        'activity_query': query,
        'activity_type': type_filter,
        'activity_status': status_filter,
        'activity_sort': sort,
        'activity_filters_active': bool(query or type_filter or status_filter),
        'activity_sort_options': [
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('participants', 'Most participants'),
            ('title', 'A - Z'),
        ],
    }


@login_required(login_url='login')
def activity_list(request):
    context = activities_context(request)
    return render(request, 'activity_list.html', context)

@login_required(login_url='login')
def add_activity(request):
    form = ActivityForm()
    form.fields['user'].required = False
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        form.fields['user'].required = False
        if form.is_valid():
            activity = form.save(commit=False)
            if not activity.user_id:
                activity.user = request.user
            activity.save()
            messages.success(request, "You've successfully added your Activity details")
            return redirect('activity_list')
    context = {'form': form}
    return render(request, 'add_activity.html', context)

@login_required(login_url='login')
def update_activity(request, pk):
    activity = get_object_or_404(Activity, id=pk)

    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        form.fields['user'].required = False
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.user_id:
                updated.user = request.user
            updated.save()
            messages.success(request, "Activity updated successfully.")
            return redirect('activity_list')  # Redirect to the list of activities
    else:
        form = ActivityForm(instance=activity)
        form.fields['user'].required = False

    return render(request, 'update_activity.html', {'form': form, 'activity': activity})

# Delete activity view
@login_required(login_url='login')
def delete_activity(request, pk):
    # Fetch the activity by its ID
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        # Handle the deletion logic
        activity.delete()
        messages.success(request, "Activity deleted successfully.")
        return redirect('activity_list')  # Redirect to the activity list after deletion

    # If it's a GET request, show the confirmation page
    return render(request, 'activity_confirm_delete.html', {'activity': activity})

@login_required(login_url='login')
def activity_detail(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)

    context = activities_context(request)

    enriched = next(
        (item for item in context['all_activities'] if item.pk == activity.pk),
        activity,
    )
    context['activity'] = enriched
    context['related_activities'] = [
        item for item in context['all_activities']
        if item.pk != activity.pk and item.type_slug == enriched.type_slug
    ][:4]
    if len(context['related_activities']) < 4:
        extra = [
            item for item in context['all_activities']
            if item.pk != activity.pk and item not in context['related_activities']
        ]
        context['related_activities'].extend(extra[:4 - len(context['related_activities'])])

    return render(request, 'activity_detail.html', context)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = events_context()
    enriched = next(
        (item for item in context['events'] if item.pk == event.pk),
        event,
    )
    context['event'] = enriched
    context['related_events'] = [
        item for item in context['events']
        if item.pk != event.pk and item.category_slug == enriched.category_slug
    ][:3]
    if not context['related_events']:
        context['related_events'] = [
            item for item in context['events'] if item.pk != event.pk
        ][:3]
    return render(request, 'event_detail.html', context)

@login_required(login_url='login')
def contact_details(request, contact_id):
    contdetail = get_object_or_404(contact, id=contact_id)
    return render(request, 'contact_details.html', {'contdetail': contdetail})


@login_required(login_url='login')
@csrf_exempt  # Allow AJAX requests without CSRF token
def subscribe_newsletter(request):
    form=NewsletterForm()
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Subscription successful!"}, status=200)
    return JsonResponse({"message": "Invalid email."}, status=400)

def skills_context(request=None):
    """Everything the skills pages need: the skill set, taxonomy, filters and stats."""
    skills = list(Skill.objects.all())

    category_labels = dict(Skill.CATEGORY_CHOICES)

    for skill in skills:
        skill.badge = skill.level_slug

    category_counts = {}
    level_counts = {}
    for skill in skills:
        category_counts[skill.category_slug] = category_counts.get(skill.category_slug, 0) + 1
        level_counts[skill.level] = level_counts.get(skill.level, 0) + 1

    total = len(skills)
    average = round(sum(skill.proficiency or 0 for skill in skills) / total) if total else 0

    skill_categories = [
        {
            'slug': slug,
            'label': category_labels.get(slug, 'Other'),
            'count': count,
            'percent': round(count * 100 / total) if total else 0,
        }
        for slug, count in sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    level_order = ['Expert', 'Advanced', 'Proficient', 'Intermediate', 'Beginner']
    skill_levels = [
        {'name': name, 'count': level_counts.get(name, 0)}
        for name in level_order
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    category_filter = (request.GET.get('category') or '').strip() if request else ''
    level_filter = (request.GET.get('level') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'proficiency').strip() if request else 'proficiency'

    visible = skills

    if query:
        needle = query.lower()
        visible = [
            skill for skill in visible
            if needle in (skill.name or '').lower()
            or needle in (skill.description or '').lower()
        ]

    if category_filter:
        visible = [skill for skill in visible if skill.category_slug == category_filter]

    if level_filter:
        visible = [skill for skill in visible if skill.level == level_filter]

    if sort == 'name':
        visible.sort(key=lambda s: (s.name or '').lower())
    elif sort == 'experience':
        visible.sort(key=lambda s: -(s.years_experience or 0))
    elif sort == 'oldest':
        visible.sort(key=lambda s: s.created_at or timezone.now())
    else:
        visible.sort(key=lambda s: -(s.proficiency or 0))

    top_skills = sorted(skills, key=lambda s: -(s.proficiency or 0))[:5]

    return {
        'skills': visible,
        'all_skills': skills,
        'skill_categories': skill_categories,
        'skill_levels': skill_levels,
        'top_skills': top_skills,
        'skill_stats': {
            'total': total,
            'average': average,
            'expert': level_counts.get('Expert', 0),
            'categories': len(skill_categories),
            'years': sum(skill.years_experience or 0 for skill in skills),
            'documented': sum(1 for skill in skills if skill.description),
            'strongest': top_skills[0] if top_skills else None,
        },
        'skill_query': query,
        'skill_category': category_filter,
        'skill_level': level_filter,
        'skill_sort': sort,
        'skill_filters_active': bool(query or category_filter or level_filter),
        'skill_sort_options': [
            ('proficiency', 'Most proficient'),
            ('experience', 'Most experienced'),
            ('name', 'A - Z'),
            ('oldest', 'Oldest first'),
        ],
    }


def skills_view(request):
    context = skills_context(request)
    return render(request, 'skills.html', context)

def certifications_context(request=None):
    """Everything the certification pages need: the wallet, taxonomy, filters and stats."""
    certifications = list(Certification.objects.all())

    level_labels = {
        'foundation': 'Foundation',
        'intermediate': 'Intermediate',
        'advanced': 'Advanced',
        'expert': 'Expert',
    }

    level_counts = {}
    org_counts = {}
    year_counts = {}
    skill_counts = {}
    status_counts = {'active': 0, 'expiring': 0, 'expired': 0}

    for certification in certifications:
        level_counts[certification.level_slug] = level_counts.get(certification.level_slug, 0) + 1
        org_counts[certification.issuing_organization] = org_counts.get(certification.issuing_organization, 0) + 1
        status_counts[certification.status_slug] = status_counts.get(certification.status_slug, 0) + 1
        if certification.year:
            year_counts[certification.year] = year_counts.get(certification.year, 0) + 1
        for skill in certification.skill_list:
            key = skill.lower()
            skill_counts[key] = skill_counts.get(key, 0) + 1

    total = len(certifications)

    certification_levels = [
        {
            'slug': slug,
            'label': label,
            'count': level_counts.get(slug, 0),
            'percent': round(level_counts.get(slug, 0) * 100 / total) if total else 0,
        }
        for slug, label in level_labels.items()
    ]

    organizations = [
        {'name': name, 'count': count}
        for name, count in sorted(org_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    years = [
        {'year': year, 'count': count}
        for year, count in sorted(year_counts.items(), key=lambda kv: -kv[0])
    ]

    certification_skills = [
        {'name': name, 'count': count}
        for name, count in sorted(skill_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    level_filter = (request.GET.get('level') or '').strip() if request else ''
    org_filter = (request.GET.get('org') or '').strip() if request else ''
    year_filter = (request.GET.get('year') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = list(certifications)

    if query:
        needle = query.lower()

        def matches(certification):
            haystacks = (certification.title, certification.issuing_organization, certification.skills)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [certification for certification in visible if matches(certification)]

    if level_filter:
        visible = [certification for certification in visible if certification.level_slug == level_filter]

    if org_filter:
        visible = [certification for certification in visible if certification.issuing_organization == org_filter]

    if year_filter:
        visible = [certification for certification in visible if str(certification.year) == year_filter]

    if sort == 'oldest':
        visible.sort(key=lambda c: c.date_issued or timezone.now().date())
    elif sort == 'level':
        order = ['expert', 'advanced', 'intermediate', 'foundation']
        visible.sort(key=lambda c: order.index(c.level_slug) if c.level_slug in order else 99)
    elif sort == 'organization':
        visible.sort(key=lambda c: (c.issuing_organization or '').lower())
    else:
        visible.sort(key=lambda c: c.date_issued or timezone.now().date(), reverse=True)

    return {
        'certifications': visible,
        'all_certifications': certifications,
        'certification_levels': certification_levels,
        'certification_organizations': organizations,
        'certification_years': years,
        'certification_skills': certification_skills,
        'certification_stats': {
            'total': total,
            'active': status_counts.get('active', 0),
            'expiring': status_counts.get('expiring', 0),
            'expired': status_counts.get('expired', 0),
            'organizations': len(organizations),
            'this_year': len([c for c in certifications if c.year == timezone.now().year]),
            'expert': level_counts.get('expert', 0),
            'advanced': level_counts.get('advanced', 0),
            'skills': len(certification_skills),
        },
        'certification_query': query,
        'certification_level': level_filter,
        'certification_org': org_filter,
        'certification_year': year_filter,
        'certification_sort': sort,
        'certification_filters_active': bool(query or level_filter or org_filter or year_filter),
        'certification_sort_options': [
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('level', 'Highest level'),
            ('organization', 'By organization'),
        ],
    }


def certification_list(request):
    context = certifications_context(request)
    return render(request, 'certification_list.html', context)


def certification_detail(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    context = certifications_context(request)
    context['certification'] = certification
    context['related_certifications'] = [
        item for item in context['all_certifications']
        if item.pk != certification.pk
        and (item.issuing_organization == certification.issuing_organization
             or item.level_slug == certification.level_slug)
    ][:4]
    return render(request, 'certification_detail.html', context)


@owner_required
def certification_add(request):
    if request.method == "POST":
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save()
            messages.success(request, f"'{certification.title}' has been added to the wallet.")
            return redirect('certification_detail', pk=certification.pk)

    else:
        form = CertificationForm()

    context = certifications_context(request)
    context['form'] = form
    return render(request, 'certification_form.html', context)


@owner_required
def certification_update(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == "POST":
        form = CertificationForm(request.POST, request.FILES, instance=certification)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{certification.title}' has been updated.")
            return redirect('certification_detail', pk=certification.pk)
    else:
        form = CertificationForm(instance=certification)

    context = certifications_context(request)
    context['form'] = form
    context['certification'] = certification
    return render(request, 'certificate_updation.html', context)


@owner_required
def certification_delete(request, pk):
    certification = get_object_or_404(Certification, pk=pk)
    if request.method == "POST":
        title = certification.title
        certification.delete()
        messages.success(request, f"'{title}' was removed from the wallet.")
        return redirect('certification_list')

    context = certifications_context(request)
    context['certification'] = certification
    return render(request, 'certification_confirm_delete.html', context)


def projects_context(request=None):
    """Everything the project pages need: the catalogue, taxonomy, filters and stats."""
    projects = list(Project.objects.all())

    category_labels = dict(Project.CATEGORY_CHOICES)
    status_labels = dict(Project.STATUS_CHOICES)

    for project in projects:
        project.has_links = bool(project.github_link or project.live_demo)
        project.word_count = len((project.description or '').split())

    category_counts = {}
    status_counts = {}
    tech_counts = {}
    year_counts = {}

    for project in projects:
        category_counts[project.category_slug] = category_counts.get(project.category_slug, 0) + 1
        status_counts[project.status_slug] = status_counts.get(project.status_slug, 0) + 1
        for tech in project.tech_list:
            key = tech.lower()
            tech_counts[key] = tech_counts.get(key, 0) + 1
        if project.year:
            year_counts[project.year] = year_counts.get(project.year, 0) + 1

    total = len(projects)

    project_categories = [
        {
            'slug': slug,
            'label': category_labels.get(slug, 'Other'),
            'count': count,
            'percent': round(count * 100 / total) if total else 0,
        }
        for slug, count in sorted(category_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    project_statuses = [
        {
            'slug': slug,
            'label': status_labels.get(slug, 'In Build'),
            'count': status_counts.get(slug, 0),
        }
        for slug in ('live', 'building', 'idea', 'archived')
        if status_counts.get(slug, 0)
    ]

    project_techs = [
        {'name': name, 'count': count}
        for name, count in sorted(tech_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:20]
    ]

    project_years = [
        {'year': year, 'count': count}
        for year, count in sorted(year_counts.items(), key=lambda kv: -kv[0])
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    category_filter = (request.GET.get('category') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    tech_filter = (request.GET.get('tech') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = projects

    if query:
        needle = query.lower()

        def matches(project):
            haystacks = (project.title, project.description, project.technologies_used, project.role)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [project for project in visible if matches(project)]

    if category_filter:
        visible = [project for project in visible if project.category_slug == category_filter]

    if status_filter:
        visible = [project for project in visible if project.status_slug == status_filter]

    if tech_filter:
        visible = [
            project for project in visible
            if any(tech.lower() == tech_filter.lower() for tech in project.tech_list)
        ]

    if sort == 'oldest':
        visible.sort(key=lambda p: p.created_at or timezone.now())
    elif sort == 'title':
        visible.sort(key=lambda p: (p.title or '').lower())
    elif sort == 'size':
        visible.sort(key=lambda p: -p.word_count)
    else:
        visible.sort(key=lambda p: p.created_at or timezone.now(), reverse=True)

    live_projects = [project for project in projects if project.status_slug == 'live']

    return {
        'projects': visible,
        'all_projects': projects,
        'project_categories': project_categories,
        'project_statuses': project_statuses,
        'project_techs': project_techs,
        'project_years': project_years,
        'project_stats': {
            'total': total,
            'live': len(live_projects),
            'building': status_counts.get('building', 0),
            'categories': len(project_categories),
            'technologies': len(tech_counts),
            'with_links': sum(1 for project in projects if project.has_links),
            'with_media': sum(1 for project in projects if project.image or project.video),
            'years': len(year_counts),
            'latest_year': project_years[0]['year'] if project_years else None,
        },
        'project_query': query,
        'project_category': category_filter,
        'project_status': status_filter,
        'project_tech': tech_filter,
        'project_sort': sort,
        'project_filters_active': bool(query or category_filter or status_filter or tech_filter),
        'project_sort_options': [
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('title', 'A - Z'),
            ('size', 'Most detailed'),
        ],
    }


# Display all projects
def projects_list(request):
    context = projects_context(request)
    return render(request, 'projects_list.html', context)


# View project details
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    context = projects_context(request)

    enriched = next(
        (item for item in context['all_projects'] if item.pk == project.pk),
        project,
    )
    context['project'] = enriched
    context['related_projects'] = [
        item for item in context['all_projects']
        if item.pk != project.pk and item.category_slug == enriched.category_slug
    ][:3]
    if len(context['related_projects']) < 3:
        extra = [
            item for item in context['all_projects']
            if item.pk != project.pk and item not in context['related_projects']
        ]
        context['related_projects'].extend(extra[:3 - len(context['related_projects'])])

    return render(request, 'project_detail.html', context)
# Add a new project
@owner_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Project added successfully.")
            return redirect('projects_list')
    else:
        form = ProjectForm()
    return render(request, 'project_form.html', {'form': form, 'project': None})


# Edit an existing project
@owner_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully.")
            return redirect('projects_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_form.html', {'form': form, 'project': project})


# Delete a project
@owner_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        title = project.title
        project.delete()
        messages.success(request, f'“{title}” was removed from the project catalogue.')
        return redirect('projects_list')
    return render(request, 'project_confirm_delete.html', {'project': project})


@login_required(login_url='login')
def download_report(request):
    # Create a PDF response with inline display
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="siblings_report.pdf"'  # 'inline' displays in browser

    # Create the PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    y = height - 40  # Start from the top

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Siblings Report")
    y -= 30

    # Table Headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Name")
    p.drawString(200, y, "Age")
    p.drawString(300, y, "Occupation")
    y -= 20

    # Fetch data
    siblings = Sibling.objects.all()

    # Add Data
    p.setFont("Helvetica", 10)
    for sibling in siblings:
        p.drawString(50, y, sibling.name)
        p.drawString(200, y, str(sibling.age) if sibling.age else "N/A")
        p.drawString(300, y, sibling.occupation if sibling.occupation else "N/A")
        y -= 20

    # Save the PDF
    p.showPage()
    p.save()

    return response


@login_required(login_url='login')
def generate_full_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    styles['Normal']

    elements = []

    # Title
    elements.append(Paragraph("FelloMarley Foundation", title_style))
    elements.append(Spacer(1, 10))

    # ========== 1. Portfolio Items ==========
    elements.append(Paragraph("📌 Portfolio Items", heading_style))
    portfolio_data = [["Title", "Description", "Image"]]

    for port in PortfolioItem.objects.all():
        img_path = port.image.path if port.image else None
        img = Image(img_path, width=60, height=60) if img_path and os.path.exists(img_path) else "No Image"
        portfolio_data.append([port.title, port.description, img])

    table = Table(portfolio_data, colWidths=[150, 300, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # ========== 2. Sibling Information ==========
    elements.append(Paragraph("👨‍👩‍👧‍👦 Siblings", heading_style))
    sibling_data = [["Name", "Occupation", "Age", "Profile Picture"]]

    for sib in Sibling.objects.all():
        img_path = sib.profile_picture.path if sib.profile_picture else None
        img = Image(img_path, width=60, height=60) if img_path and os.path.exists(img_path) else "No Image"
        sibling_data.append([sib.name, sib.occupation, sib.age, img])

    table = Table(sibling_data, colWidths=[120, 220, 50, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # ========== 3. Projects ==========
    elements.append(Paragraph("🚀 Projects", heading_style))
    project_data = [["Title", "Technologies Used", "GitHub", "Live Demo"]]

    for proj in Project.objects.all():
        project_data.append([proj.title, proj.technologies_used, proj.github_link or "N/A", proj.live_demo or "N/A"])

    table = Table(project_data, colWidths=[150, 350, 200, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # ========== 4. Skills ==========
    elements.append(Paragraph("🛠️ Skills", heading_style))
    skill_data = [["Skill Name", "Proficiency (%)"]]

    for skill in Skill.objects.all():
        skill_data.append([skill.name, f"{skill.proficiency}%"])

    table = Table(skill_data, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # ========== 5. Certifications ==========
    elements.append(Paragraph("📜 Certifications", heading_style))
    cert_data = [["Title", "Issuer", "Date Issued", "Credential URL"]]

    for cert in Certification.objects.all():
        cert_data.append([cert.title, cert.issuing_organization, cert.date_issued, cert.credential_url or "N/A"])

    table = Table(cert_data, colWidths=[150, 150, 100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # ========== 6. Tasks ==========
    elements.append(Paragraph("✅ Tasks", heading_style))
    task_data = [["Title", "Due Date", "Completed"]]

    for task in Task.objects.all():
        task_data.append([task.title, task.due_date.strftime("%Y-%m-%d"), "Yes" if task.completed else "No"])

    table = Table(task_data, colWidths=[200, 100, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # ========== 7. Notifications ==========
    elements.append(Paragraph("🔔 Notifications", heading_style))
    notification_data = [["Title", "Description", "Date"]]

    for note in Notification.objects.all():
        notification_data.append([note.title, note.description, note.created_at.strftime("%Y-%m-%d")])

    table = Table(notification_data, colWidths=[150, 250, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Build and return PDF
    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Full_Report.pdf")




# List all support tickets for the logged-in user
@login_required(login_url='login')
def support(request):
    supports=Support.objects.all()
    return render(request, 'support.html',{'supports':supports})  # Adjust the template as needed

# View support ticket details
@login_required(login_url='login')
def support_detail(request, pk):
    support = Support.objects.get(id=pk)
    return render(request, 'support_detail.html', {'support': support})

# Create a new support ticket
@login_required(login_url='login')
def support_create(request):
    if request.method == "POST":
        form = SupportForm(request.POST, request.FILES)
        if form.is_valid():
            support = form.save(commit=False)
            support.user = request.user
            support.save()
            return redirect('support')
    else:
        form = SupportForm()
    return render(request, 'support_form.html', {'form': form})

# Update an existing support ticket
@login_required(login_url='login')
def support_update(request, pk):
    support = get_object_or_404(Support, pk=pk, user=request.user)
    if request.method == "POST":
        form = SupportForm(request.POST, request.FILES, instance=support)
        if form.is_valid():
            form.save()
            return redirect('support')
    else:
        form = SupportForm(instance=support)
    return render(request, 'support_form.html', {'form': form})

# Delete a support ticket
@login_required(login_url='login')
def support_delete(request, pk):
    support = get_object_or_404(Support, pk=pk, user=request.user)
    if request.method == "POST":
        support.delete()
        return redirect('support_list')
    return render(request, 'support_confirm_delete.html', {'support': support})



def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)

    context = skills_context(request)
    context['skill'] = skill

    related = [item for item in context['all_skills']
               if item.pk != skill.pk and item.category_slug == skill.category_slug][:4]
    if len(related) < 4:
        extra = [item for item in context['all_skills']
                 if item.pk != skill.pk and item not in related]
        related.extend(extra[:4 - len(related)])
    context['related_skills'] = related

    return render(request, 'skill_detail.html', context)

# Create & Update View
@owner_required
def skill_form(request, pk=None):
    if pk:
        skill = get_object_or_404(Skill, pk=pk)
    else:
        skill = None

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            saved = form.save()
            messages.success(request, f'“{saved.name}” was saved to the skill set.')
            return redirect('skills')
    else:
        form = SkillForm(instance=skill)

    return render(request, 'skill_form.html', {'form': form, 'skill': skill})

# Delete View
@owner_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        name = skill.name
        skill.delete()
        messages.success(request, f'“{name}” was removed from the skill set.')
        return redirect('skills')
    return render(request, 'skill_confirm_delete.html', {'skill': skill})




def _twilio_client():
    """Authenticated Twilio client, or None when the credentials are not configured."""
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    if not account_sid or not auth_token:
        return None
    return Client(account_sid, auth_token)


@admin_required
def send_response(request, contact_id):
    contdetail = get_object_or_404(contact, id=contact_id)

    if request.method == "POST":
        response_message = (request.POST.get("response_message") or "").strip()

        if response_message:
            client = _twilio_client()

            if client is None:
                messages.error(request, "SMS is not configured on this server, so the reply was not sent.")
            else:
                try:
                    client.messages.create(
                        body=f"Admin Response: {response_message}",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=contdetail.phone,
                    )
                    messages.success(request, "Response sent successfully via SMS!")
                except Exception as e:
                    messages.error(request, f"Error sending message: {str(e)}")

        return redirect("admins")  # Redirect back to the admin page

    return render(request, "contact_details.html", {"contdetail": contdetail})



@admin_required
def admin_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    return render(request, "admin_event_view.html", {"event": event})


@admin_required
def send_event_response(request, event_id):
    eventing = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        response_message = (request.POST.get("response_message") or "").strip()

        if response_message:
            recipient = getattr(eventing.host, "phone", None)
            client = _twilio_client()

            if client is not None and recipient:
                try:
                    client.messages.create(
                        body=f"Admin Response: {response_message}",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=recipient,
                    )
                    messages.success(request, "Response sent successfully via SMS!")
                except Exception as e:
                    messages.error(request, f"Error sending message: {str(e)}")
            else:
                # No phone number on file for the host, so the response is recorded in-app.
                if eventing.host_id:
                    Notification.objects.create(
                        user=eventing.host,
                        title=f"Event response for {eventing.title}",
                        description=response_message,
                    )
                messages.success(request, "Response recorded and delivered to the host as an in-app notification.")

        return redirect("admins")

    return render(request, "admin_event_view.html", {"event": eventing})

def testimonials_list(request):
    context = testimonials_context()
    return render(request, 'testimonials_list.html', context)

@owner_required
def update_testimonial(request,pk):
    testimony=get_object_or_404(Testimonial,id=pk)
    form=TestimonialForm(instance=testimony)
    if request.method=='POST':
        form=TestimonialForm(request.POST,request.FILES,instance=testimony)
        if form.is_valid():
            form.save()
            messages.success(request,'Testimonial has been updated successfully')
            return redirect('testimonials_list')

    context={'testimony':testimony,
             'form':form}
    return render(request,'update_testimonial.html',context)

@owner_required
def delete_testimonial(request,pk):
    delit=get_object_or_404(Testimonial,id=pk)
    form=TestimonialForm(instance=delit)
    if request.method=='POST':
        form=TestimonialForm(request.POST,request.FILES,instance=delit)
        delit.delete()
        messages.success(request,"Youve successfully deleted the testimonial")
        return redirect('testimonials_list')
    context={'delit':delit,
             'form':form
             }
    return render(request,'delete_testimonial.html',context)

@owner_required
def add_testimonial(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.save()
            return redirect('testimonials_list')
    else:
        form = TestimonialForm()
    return render(request, 'add_testimonial.html', {'form': form})

def volunteers_context(request=None):
    """Everything the volunteer pages need: the roster, taxonomy, filters and stats."""
    volunteers = list(Volunteer.objects.select_related('user').all())

    area_labels = dict(Volunteer.AREA_CHOICES)
    status_labels = dict(Volunteer.STATUS_CHOICES)

    area_counts = {}
    status_counts = {}
    skill_counts = {}
    total_hours = 0
    active_hours = 0

    for volunteer in volunteers:
        area_counts[volunteer.area_slug] = area_counts.get(volunteer.area_slug, 0) + 1
        status_counts[volunteer.status_slug] = status_counts.get(volunteer.status_slug, 0) + 1
        hours = volunteer.hours_per_week or 0
        total_hours += hours
        if volunteer.status == 'active':
            active_hours += hours
        for skill in volunteer.skill_list:
            key = skill.lower()
            skill_counts[key] = skill_counts.get(key, 0) + 1

    total = len(volunteers)

    volunteer_areas = [
        {
            'slug': slug,
            'label': label,
            'count': area_counts.get(slug, 0),
            'percent': round(area_counts.get(slug, 0) * 100 / total) if total else 0,
        }
        for slug, label in area_labels.items()
    ]

    volunteer_statuses = [
        {
            'slug': slug,
            'label': status_labels.get(slug, 'Applied'),
            'count': status_counts.get(slug, 0),
        }
        for slug in ('applied', 'shortlisted', 'active', 'paused', 'completed')
    ]

    volunteer_skills = [
        {'name': name, 'count': count}
        for name, count in sorted(skill_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    area_filter = (request.GET.get('area') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = list(volunteers)

    if query:
        needle = query.lower()

        def matches(volunteer):
            haystacks = (volunteer.full_name, volunteer.email, volunteer.skills, volunteer.availability)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [volunteer for volunteer in visible if matches(volunteer)]

    if area_filter:
        visible = [volunteer for volunteer in visible if volunteer.area_slug == area_filter]

    if status_filter:
        visible = [volunteer for volunteer in visible if volunteer.status_slug == status_filter]

    if sort == 'name':
        visible.sort(key=lambda v: (v.full_name or '').lower())
    elif sort == 'area':
        visible.sort(key=lambda v: (v.area_label, (v.full_name or '').lower()))
    elif sort == 'hours':
        visible.sort(key=lambda v: -(v.hours_per_week or 0))
    else:
        visible.sort(key=lambda v: v.joined_at or timezone.now(), reverse=True)

    # Group the roster by the area people give their time to.
    groups = []
    for area in volunteer_areas:
        items = [volunteer for volunteer in visible if volunteer.area_slug == area['slug']]
        if items:
            groups.append({**area, 'items': items})

    this_month = [
        volunteer for volunteer in volunteers
        if volunteer.joined_at
        and volunteer.joined_at.year == timezone.now().year
        and volunteer.joined_at.month == timezone.now().month
    ]

    return {
        'volunteers': visible,
        'all_volunteers': volunteers,
        'volunteer_groups': groups,
        'volunteer_areas': volunteer_areas,
        'volunteer_statuses': volunteer_statuses,
        'volunteer_status_choices': Volunteer.STATUS_CHOICES,
        'volunteer_skills': volunteer_skills,
        'volunteer_stats': {
            'total': total,
            'active': status_counts.get('active', 0),
            'applicants': status_counts.get('applied', 0),
            'shortlisted': status_counts.get('shortlisted', 0),
            'paused': status_counts.get('paused', 0),
            'completed': status_counts.get('completed', 0),
            'this_month': len(this_month),
            'hours': total_hours,
            'active_hours': active_hours,
            'areas': len([area for area in volunteer_areas if area['count']]),
            'with_resume': sum(1 for volunteer in volunteers if volunteer.has_resume),
        },
        'volunteer_query': query,
        'volunteer_area': area_filter,
        'volunteer_status': status_filter,
        'volunteer_sort': sort,
        'volunteer_filters_active': bool(query or area_filter or status_filter),
        'volunteer_sort_options': [
            ('newest', 'Newest first'),
            ('name', 'A - Z'),
            ('area', 'By area'),
            ('hours', 'Most hours'),
        ],
    }


@login_required(login_url='login')
def volunteer_list(request):
    context = volunteers_context(request)
    return render(request, 'volunteer_list.html', context)


@login_required(login_url='login')
def volunteer_detail(request, pk):
    volunteer = get_object_or_404(Volunteer, pk=pk)
    context = volunteers_context(request)
    context['volunteer'] = volunteer
    context['volunteer_fellows'] = [
        item for item in context['all_volunteers']
        if item.pk != volunteer.pk and item.area_slug == volunteer.area_slug
    ][:4]
    return render(request, 'volunteer_detail.html', context)


@login_required(login_url='login')
def volunteer_signup(request):
    if request.method == "POST":
        form = VolunteerForm(request.POST, request.FILES)
        if form.is_valid():
            volunteer = form.save(commit=False)
            volunteer.user = request.user
            volunteer.save()
            messages.success(request, f"Thanks {volunteer.full_name}! Your volunteer application is in.")
            return redirect('volunteer_detail', pk=volunteer.pk)
    else:
        form = VolunteerForm(initial={'status': 'applied'})

    context = volunteers_context(request)
    context['form'] = form
    return render(request, 'volunteer_signup.html', context)


@owner_required
def update_volunteer(request, pk):
    volunteer = get_object_or_404(Volunteer, pk=pk)

    if request.method == 'POST':
        form = VolunteerForm(request.POST, request.FILES, instance=volunteer)
        if form.is_valid():
            form.save()
            messages.success(request, f"{volunteer.full_name}'s details updated successfully!")
            return redirect('volunteer_detail', pk=volunteer.pk)
    else:
        form = VolunteerForm(instance=volunteer)

    context = volunteers_context(request)
    context['form'] = form
    context['volunteer'] = volunteer
    return render(request, 'update_volunteer.html', context)


@owner_required
def delete_volunteer(request, pk):
    volunteer = get_object_or_404(Volunteer, pk=pk)

    if request.method == 'POST':
        name = volunteer.full_name
        volunteer.delete()
        messages.success(request, f"{name} was removed from the volunteer roster.")
        return redirect('volunteer_list')

    context = volunteers_context(request)
    context['volunteer'] = volunteer
    return render(request, 'delete_volunteer.html', context)


@owner_required
def update_volunteer_status(request, pk):
    """Move a volunteer along the pipeline and let them know."""
    volunteer = get_object_or_404(Volunteer, pk=pk)

    if request.method == 'POST':
        new_status = (request.POST.get('status') or '').strip()
        valid = {slug for slug, _ in Volunteer.STATUS_CHOICES}

        if new_status in valid:
            volunteer.status = new_status
            volunteer.save(update_fields=['status'])
            messages.success(request, f"{volunteer.full_name} is now marked as {volunteer.status_label.lower()}.")

            if volunteer.user_id and volunteer.user_id != request.user.id:
                Notification.objects.create(
                    title=f"Volunteer application: {volunteer.status_label}",
                    description=f"Your volunteer application '{volunteer.full_name}' moved to {volunteer.status_label.lower()}.",
                    kind='task',
                    link=f"/volunteers/{volunteer.pk}/",
                    user=volunteer.user,
                )

    return redirect('volunteer_detail', pk=volunteer.pk)


def jobs_context(request=None):
    """Everything the jobs pages need: the board, taxonomy, filters and stats."""
    now = timezone.now()
    jobs = list(Job.objects.prefetch_related('applications').all())

    type_labels = dict(Job._meta.get_field('job_type').choices)
    category_labels = dict(Job.CATEGORY_CHOICES)
    status_labels = dict(Job.STATUS_CHOICES)

    type_counts = {}
    category_counts = {}
    status_counts = {}
    skill_counts = {}
    applicants = 0

    for job in jobs:
        type_counts[job.job_type] = type_counts.get(job.job_type, 0) + 1
        category_counts[job.category_slug] = category_counts.get(job.category_slug, 0) + 1
        status_counts[job.status_slug] = status_counts.get(job.status_slug, 0) + 1
        applicants += job.applications_count
        for skill in job.skill_list:
            key = skill.lower()
            skill_counts[key] = skill_counts.get(key, 0) + 1

    total = len(jobs)

    job_types = [
        {
            'slug': slug,
            'label': label,
            'count': type_counts.get(slug, 0),
            'percent': round(type_counts.get(slug, 0) * 100 / total) if total else 0,
        }
        for slug, label in type_labels.items()
    ]

    job_categories = [
        {
            'slug': slug,
            'label': label,
            'count': category_counts.get(slug, 0),
            'percent': round(category_counts.get(slug, 0) * 100 / total) if total else 0,
        }
        for slug, label in category_labels.items()
    ]

    job_statuses = [
        {
            'slug': slug,
            'label': status_labels.get(slug, 'Open'),
            'count': status_counts.get(slug, 0),
        }
        for slug in ('open', 'closed', 'filled')
    ]

    job_skills = [
        {'name': name, 'count': count}
        for name, count in sorted(skill_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
    ]

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    type_filter = (request.GET.get('type') or '').strip() if request else ''
    category_filter = (request.GET.get('category') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = list(jobs)

    if query:
        needle = query.lower()

        def matches(job):
            haystacks = (job.title, job.company, job.description, job.location, job.skills)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [job for job in visible if matches(job)]

    if type_filter:
        visible = [job for job in visible if job.job_type == type_filter]

    if category_filter:
        visible = [job for job in visible if job.category_slug == category_filter]

    if status_filter:
        visible = [job for job in visible if job.status_slug == status_filter]

    if sort == 'oldest':
        visible.sort(key=lambda j: j.posted_at or timezone.now())
    elif sort == 'title':
        visible.sort(key=lambda j: (j.title or '').lower())
    elif sort == 'popular':
        visible.sort(key=lambda j: j.applications_count, reverse=True)
    elif sort == 'closing':
        visible.sort(key=lambda j: (j.due_at is None, j.due_at or timezone.now().date()))
    else:
        visible.sort(key=lambda j: j.posted_at or timezone.now(), reverse=True)

    this_month = [
        job for job in jobs
        if job.posted_at
        and job.posted_at.year == now.year
        and job.posted_at.month == now.month
    ]

    featured = [job for job in visible if job.is_featured]

    return {
        'jobs': visible,
        'all_jobs': jobs,
        'job_types': job_types,
        'job_categories': job_categories,
        'job_statuses': job_statuses,
        'job_skills': job_skills,
        'job_featured': featured,
        'job_stats': {
            'total': total,
            'open': status_counts.get('open', 0),
            'closed': status_counts.get('closed', 0),
            'filled': status_counts.get('filled', 0),
            'featured': len([job for job in jobs if job.is_featured]),
            'applicants': applicants,
            'this_month': len(this_month),
            'slots': sum(job.slots or 1 for job in jobs if job.is_open),
            'expired': sum(1 for job in jobs if job.is_expired),
            'categories': len([category for category in job_categories if category['count']]),
        },
        'job_query': query,
        'job_type': type_filter,
        'job_category': category_filter,
        'job_status': status_filter,
        'job_sort': sort,
        'job_filters_active': bool(query or type_filter or category_filter or status_filter),
        'job_sort_options': [
            ('newest', 'Newest first'),
            ('oldest', 'Oldest first'),
            ('title', 'A - Z'),
            ('popular', 'Most applied'),
            ('closing', 'Closing soon'),
        ],
    }


def applications_context(request=None):
    """The hiring pipeline: every application, with filters and stage counts."""
    applications = list(JobApplication.objects.select_related('job', 'applicant').all())

    status_labels = dict(JobApplication.STATUS_CHOICES)
    stage_counts = {}

    for application in applications:
        stage_counts[application.status_slug] = stage_counts.get(application.status_slug, 0) + 1

    pipeline = [
        {'slug': slug, 'label': status_labels.get(slug, 'Under Review'), 'count': stage_counts.get(slug, 0)}
        for slug in ('under_review', 'interview', 'offer_made', 'hired', 'rejected')
    ]

    query = (request.GET.get('q') or '').strip() if request else ''
    stage_filter = (request.GET.get('stage') or '').strip() if request else ''
    job_filter = (request.GET.get('job') or '').strip() if request else ''

    visible = list(applications)

    if query:
        needle = query.lower()

        def matches(application):
            haystacks = (application.applicant_display, application.job.title, application.applicant_name)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [application for application in visible if matches(application)]

    if stage_filter:
        visible = [application for application in visible if application.status_slug == stage_filter]

    if job_filter:
        visible = [application for application in visible if str(application.job_id) == job_filter]

    return {
        'applications': visible,
        'all_applications': applications,
        'application_pipeline': pipeline,
        'application_query': query,
        'application_stage': stage_filter,
        'application_job': job_filter,
        'application_stats': {
            'total': len(applications),
            'under_review': stage_counts.get('under_review', 0),
            'interview': stage_counts.get('interview', 0),
            'offer_made': stage_counts.get('offer_made', 0),
            'hired': stage_counts.get('hired', 0),
            'rejected': stage_counts.get('rejected', 0),
            'reviewed': sum(1 for application in applications if application.reviewed),
            'rated': sum(1 for application in applications if application.rating),
        },
    }


def job_list(request):
    context = jobs_context(request)
    return render(request, 'job_list.html', context)


def job_posting(request, pk):
    """A single posting: what the role is, who applied and how to apply."""
    job = get_object_or_404(Job, pk=pk)
    is_owner = request.user.is_authenticated and request.user.is_superuser

    context = jobs_context(request)
    context['job'] = job
    # Applicants are other people's records, so only the owner sees who applied.
    context['job_applications'] = list(job.applications.select_related('applicant').all()) if is_owner else []
    context['application_count'] = job.applications.count()
    context['related_jobs'] = [
        item for item in context['all_jobs']
        if item.pk != job.pk and item.category_slug == job.category_slug
    ][:3]
    context['already_applied'] = bool(
        request.user.is_authenticated
        and JobApplication.objects.filter(job=job, applicant=request.user).exists()
    )
    return render(request, 'job_posting.html', context)


@owner_required
def post_job(request):
    if request.method == "POST":
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'The job posting has been published.')
            return redirect('job_list')
    else:
        form = JobForm()
    context = jobs_context(request)
    context['form'] = form
    return render(request, 'post_job.html', context)


@login_required(login_url='login')
def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        return redirect('already_applied', job_id=job.id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            if not application.applicant_name:
                application.applicant_name = getattr(request.user, 'name', None) or request.user.username
            application.save()
            messages.success(request, f"Application sent for {job.title}.")
            return redirect('job_application_success')
    else:
        form = JobApplicationForm(initial={'job': job, 'applicant_name': getattr(request.user, 'name', None) or request.user.username})

    context = jobs_context(request)
    context['form'] = form
    context['job'] = job
    return render(request, 'apply_for_job.html', context)


@login_required(login_url='login')
def already_applied(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    return render(request, 'already_applied.html', {'job': job})


@login_required(login_url='login')
def job_application_success(request):
    return render(request, 'job_application_success.html')


@owner_required
def job_application_list(request):
    """Every application across every posting, for the hiring pipeline."""
    context = applications_context(request)
    context['jobs_list'] = Job.objects.all()
    return render(request, 'job_application_list.html', context)


@owner_required
def update_application_status(request, pk):
    """Move an application along the pipeline."""
    application = get_object_or_404(JobApplication, pk=pk)
    destination = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        new_status = (request.POST.get('status') or '').strip()
        valid = {slug for slug, _ in JobApplication.STATUS_CHOICES}

        if new_status in valid:
            application.status = new_status
            application.reviewed = True
            application.save(update_fields=['status', 'reviewed', 'updated_at'])
            messages.success(request, f"{application.applicant_display} moved to {application.status_label.lower()}.")

            if application.applicant_id and application.applicant_id != request.user.id:
                Notification.objects.create(
                    title=f"Application update: {application.job.title}",
                    description=f"Your application for {application.job.title} moved to {application.status_label.lower()}.",
                    kind='support',
                    link=f"/jobdetails/{application.pk}/",
                    user=application.applicant,
                )

    if destination:
        return redirect(destination)

    return redirect('job_application_list')


@owner_required
def respond_to_application(request, pk):
    """Reply to an applicant and keep the reply on the application record."""
    application = get_object_or_404(JobApplication, pk=pk)
    destination = request.POST.get('next') or request.GET.get('next') or ''

    if request.method == 'POST':
        response_message = (request.POST.get('response_message') or '').strip()

        if not response_message:
            messages.error(request, 'Write a response before sending it.')
        else:
            stamp = timezone.now().strftime('%d %b %Y, %H:%M')
            existing = (application.notes or '').strip()
            entry = f"[{stamp}] {response_message}"
            application.notes = f"{existing}\n\n{entry}".strip()
            application.reviewed = True
            application.save(update_fields=['notes', 'reviewed', 'updated_at'])

            if application.applicant_id and application.applicant_id != request.user.id:
                Notification.objects.create(
                    title=f"Update on your application: {application.job.title}",
                    description=response_message,
                    kind='support',
                    link=f"/jobdetails/{application.pk}/",
                    user=application.applicant,
                )

            messages.success(request, f"Response sent to {application.applicant_display}.")

    if destination:
        return redirect(destination)

    return redirect('jobdetails', pk=application.pk)


@owner_required
def update_job(request, pk):
    job = get_object_or_404(Job, id=pk)

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{job.title}' has been updated.")
            return redirect('job_posting', pk=job.pk)
    else:
        form = JobForm(instance=job)

    context = jobs_context(request)
    context['form'] = form
    context['updatejob'] = job
    context['job'] = job
    return render(request, 'updatejobapplication.html', context)


@owner_required
def delete_job(request, pk):
    job = get_object_or_404(Job, id=pk)

    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f"'{title}' has been deleted.")
        return redirect('job_list')

    context = jobs_context(request)
    context['deletejob'] = job
    context['job'] = job
    context['form'] = JobForm(instance=job)
    return render(request, 'deletejob.html', context)

def donation_context(request=None):
    """Everything the donation pages need: totals, causes, filters and stats."""
    now = timezone.now()
    donations = list(Donation.objects.select_related('donor').all())

    method_labels = dict(Donation.PAYMENT_METHODS)
    purpose_labels = dict(Donation.PURPOSES)
    status_labels = dict(Donation.STATUS_CHOICES)

    for donation in donations:
        donation.gift_label = f"{donation.payment_method_label} gift"

    completed = [donation for donation in donations if donation.status == 'completed']
    total_raised = sum((donation.amount for donation in completed), Decimal('0'))
    lifetime_pending = sum((donation.amount for donation in donations if donation.status == 'pending'), Decimal('0'))

    month_key = now.strftime('%Y-%m')
    month_total = sum(
        (donation.amount for donation in completed
         if donation.date_donated and donation.date_donated.strftime('%Y-%m') == month_key),
        Decimal('0'),
    )

    amounts = [donation.amount for donation in completed]
    average_gift = (total_raised / len(completed)) if completed else Decimal('0')
    largest_gift = max(amounts) if amounts else Decimal('0')

    # --- Causes -------------------------------------------------------------
    cause_totals = {}
    method_totals = {}
    status_counts = {}
    monthly_totals = {}

    for donation in donations:
        status_counts[donation.status_slug] = status_counts.get(donation.status_slug, 0) + 1
        if donation.status != 'completed':
            continue
        cause_totals[donation.purpose_slug] = cause_totals.get(donation.purpose_slug, Decimal('0')) + donation.amount
        method_totals[donation.payment_method] = method_totals.get(donation.payment_method, Decimal('0')) + donation.amount
        if donation.date_donated:
            key = donation.date_donated.strftime('%Y-%m')
            monthly_totals[key] = monthly_totals.get(key, Decimal('0')) + donation.amount

    causes = []
    for slug, label in purpose_labels.items():
        amount = cause_totals.get(slug, Decimal('0'))
        causes.append({
            'slug': slug,
            'label': label,
            'amount': amount,
            'percent': round(float(amount) * 100 / float(total_raised)) if total_raised else 0,
        })

    methods = []
    for slug, label in method_labels.items():
        amount = method_totals.get(slug, Decimal('0'))
        methods.append({
            'slug': slug,
            'label': label,
            'amount': amount,
            'count': sum(1 for donation in completed if donation.payment_method == slug),
        })

    months = []
    for offset in range(5, -1, -1):
        year = now.year
        month = now.month - offset
        while month <= 0:
            month += 12
            year -= 1
        key = f"{year:04d}-{month:02d}"
        amount = monthly_totals.get(key, Decimal('0'))
        months.append({
            'key': key,
            'label': datetime(year, month, 1).strftime('%b'),
            'amount': amount,
        })

    peak = max((entry['amount'] for entry in months), default=Decimal('0'))
    for entry in months:
        entry['percent'] = round(float(entry['amount']) * 100 / float(peak)) if peak else 0

    # --- Filters ------------------------------------------------------------
    query = (request.GET.get('q') or '').strip() if request else ''
    method_filter = (request.GET.get('method') or '').strip() if request else ''
    status_filter = (request.GET.get('status') or '').strip() if request else ''
    purpose_filter = (request.GET.get('purpose') or '').strip() if request else ''
    sort = (request.GET.get('sort') or 'newest').strip() if request else 'newest'

    visible = list(donations)

    if query:
        needle = query.lower()

        def matches(donation):
            haystacks = (donation.name, donation.email, donation.message, donation.transaction_id)
            return any(needle in (text or '').lower() for text in haystacks)

        visible = [donation for donation in visible if matches(donation)]

    if method_filter:
        visible = [donation for donation in visible if donation.payment_method == method_filter]

    if status_filter:
        visible = [donation for donation in visible if donation.status_slug == status_filter]

    if purpose_filter:
        visible = [donation for donation in visible if donation.purpose_slug == purpose_filter]

    if sort == 'oldest':
        visible.sort(key=lambda donation: donation.date_donated or timezone.now(), reverse=False)
    elif sort == 'highest':
        visible.sort(key=lambda donation: donation.amount, reverse=True)
    elif sort == 'lowest':
        visible.sort(key=lambda donation: donation.amount, reverse=False)
    elif sort == 'name':
        visible.sort(key=lambda donation: (donation.name or '').lower())
    else:
        visible.sort(key=lambda donation: donation.date_donated or timezone.now(), reverse=True)

    return {
        'donations': visible,
        'causes': causes,
        'payment_methods': methods,
        'months': months,
        'status_labels': status_labels,
        'method_labels': method_labels,
        'purpose_labels': purpose_labels,
        'donation_query': query,
        'donation_method_filter': method_filter,
        'donation_status_filter': status_filter,
        'donation_purpose_filter': purpose_filter,
        'donation_sort': sort,
        'donation_stats': {
            'total': total_raised,
            'count': len(completed),
            'average': average_gift,
            'largest': largest_gift,
            'month': month_total,
            'pending': lifetime_pending,
            'donors': len({(donation.email or '').lower() for donation in completed}),
            'anonymous': sum(1 for donation in completed if donation.anonymous),
            'receipts': sum(1 for donation in completed if donation.receipt_sent),
        },
    }


def _apply_donation_date(donation, donated_on):
    """Backdate a gift: date_donated is auto-set, so it needs a direct update."""
    if not donated_on:
        return
    stamp = timezone.make_aware(datetime.combine(donated_on, datetime.min.time()))
    Donation.objects.filter(pk=donation.pk).update(date_donated=stamp)
    donation.date_donated = stamp


def donate(request):
    """Public donation page: live totals, the causes we fund and a working gift form."""
    context = donation_context(request)

    signed_in = getattr(request, 'user', None) and request.user.is_authenticated

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.status = 'completed'
            if signed_in:
                donation.donor = request.user
            donation.save()
            messages.success(
                request,
                f"Thank you {donation.name}! Your donation of {donation.amount} towards "
                f"{donation.purpose_label} has been received.",
            )
            return redirect('donate')
    else:
        form = DonationForm()
        if signed_in:
            form.fields['name'].initial = getattr(request.user, 'name', None) or request.user.username
            form.fields['email'].initial = request.user.email

    context['form'] = form
    context['recent_donations'] = [
        donation for donation in Donation.objects.select_related('donor').filter(status='completed')
    ][:6]
    return render(request, 'donation.html', context)


@login_required(login_url='login')
def donations(request):
    """Admin view of every donation, with filters and live totals."""
    context = donation_context(request)
    return render(request, 'donations.html', context)


@login_required(login_url='login')
def donation_detail(request, pk):
    """A single donation with its full paper trail."""
    donation = get_object_or_404(Donation, pk=pk)
    context = donation_context(request)
    context['donation'] = donation
    return render(request, 'donation_detail.html', context)


@login_required(login_url='login')
def add_donation(request):
    """Record a donation that was made outside the site (cash, offline transfer)."""
    if request.method == 'POST':
        form = DonationAdminForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.save()
            _apply_donation_date(donation, form.cleaned_data.get('donated_on'))
            messages.success(request, f"Donation of {donation.amount} from {donation.name} recorded successfully!")
            return redirect('donations')
    else:
        form = DonationAdminForm()

    context = donation_context(request)
    context['form'] = form
    return render(request, 'add_donation.html', context)


@login_required(login_url='login')
def update_donation(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    original_user_id = donation.donor_id

    if request.method == 'POST':
        form = DonationAdminForm(request.POST, instance=donation)
        if form.is_valid():
            updated = form.save(commit=False)
            if not updated.donor_id:
                updated.donor_id = original_user_id
            updated.save()
            _apply_donation_date(updated, form.cleaned_data.get('donated_on'))
            messages.success(request, f"Donation from {updated.name} updated successfully!")
            return redirect('donation_detail', pk=updated.pk)
    else:
        form = DonationAdminForm(instance=donation)

    context = donation_context(request)
    context['form'] = form
    context['donation'] = donation
    return render(request, 'update_donation.html', context)


@login_required(login_url='login')
def delete_donation(request, pk):
    donation = get_object_or_404(Donation, pk=pk)

    if request.method == 'POST':
        donor_name = donation.donor_display
        donation.delete()
        messages.success(request, f"The donation from {donor_name} has been deleted.")
        return redirect('donations')

    context = donation_context(request)
    context['donation'] = donation
    return render(request, 'delete_donation.html', context)


@login_required(login_url='login')
def toggle_donation_receipt(request, pk):
    """Flag a donation receipt as sent (or not yet sent)."""
    donation = get_object_or_404(Donation, pk=pk)

    if request.method == 'POST':
        donation.receipt_sent = not donation.receipt_sent
        donation.save(update_fields=['receipt_sent'])
        state = 'marked as sent' if donation.receipt_sent else 'flagged as pending'
        messages.success(request, f"Receipt for {donation.reference} {state}.")

    return redirect('donation_detail', pk=donation.pk)



def faq_list(request):
    """The public question and answer page."""
    query = request.GET.get('q', '').strip()

    faqs = FAQ.objects.all()
    if query:
        faqs = faqs.filter(Q(question__icontains=query) | Q(answer__icontains=query))

    return render(
        request,
        'faq_list.html',
        {
            'faqs': faqs,
            'faq_query': query,
            'faq_total': FAQ.objects.count(),
        },
    )

@owner_required
def add_faq(request):
    form= FAQForm()
    if request.method=='POST':
       form=FAQForm(request.POST,request.FILES)
       if form.is_valid():
           form.save()
           return redirect('faq_list')
    return render (request,'add_faq.html',{'form':form})



def search(request):
    """Search the site. Visitors only see public content, the owner sees everything."""
    query = request.GET.get('searched', '').strip()
    results = {}

    is_owner = request.user.is_authenticated and request.user.is_superuser

    if query:
        results = {
            'projects': Project.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'blogs': BlogPost.objects.filter(Q(title__icontains=query) | Q(content__icontains=query)),
            'events': Event.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'testimonials': Testimonial.objects.filter(Q(name__icontains=query) | Q(message__icontains=query)),
            'portfolios': PortfolioItem.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'education_levels': EducationLevel.objects.filter(Q(level__icontains=query) | Q(school__icontains=query) | Q(description__icontains=query)),
            'skills': Skill.objects.filter(Q(name__icontains=query)),
            'certifications': Certification.objects.filter(Q(title__icontains=query) | Q(issuing_organization__icontains=query)),
            'jobs': Job.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(company__icontains=query)),
            'faqs': FAQ.objects.filter(Q(question__icontains=query) | Q(answer__icontains=query)),
            'gallery_images': ImageGallery.objects.filter(Q(title__icontains=query) | Q(caption__icontains=query)),
        }

        if not is_owner:
            # Draft posts stay out of the results for everyone but the owner.
            results['blogs'] = results['blogs'].filter(status='published')

    if is_owner:
        # The private corners of the site: tasks, messages, people, records.
        results.update({
            'tasks': Task.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'siblings': Sibling.objects.filter(Q(name__icontains=query) | Q(short_description__icontains=query) | Q(full_description__icontains=query)),
            'sibling_images': SiblingImage.objects.filter(Q(description__icontains=query)),
            'activities': Activity.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'notifications': Notification.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'job_applications': JobApplication.objects.filter(Q(applicant_name__icontains=query) | Q(status__icontains=query)),
            'supports': Support.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)),
            'volunteers': Volunteer.objects.filter(Q(full_name__icontains=query) | Q(skills__icontains=query) | Q(reason__icontains=query)),
            'contacts': contact.objects.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(message__icontains=query)),
        })

    context = {
        'query': query,
        'results': results,
        'search_is_owner': is_owner,
    }
    return render(request, 'search_item.html', context)
