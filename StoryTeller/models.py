from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


def _initials_for(name):
    """Two letter initials for an avatar fallback."""
    parts = [part for part in (name or '').split() if part]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()



class MyUser(AbstractUser):
    mygender = (
        ('male', 'male'),
        ('female', 'female'),
        ('others', 'others')
    )
    email=models.EmailField(unique=True,null=True)
    name = models.CharField(unique=True, max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profilepic=models.FileField(null=True, blank=True, upload_to='profiles/', default="avatar.png")
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=mygender, blank=True, null=True, default='male')
    is_enduser = models.BooleanField(default=False, null=True)
    # Public profile shown across the site, editable from the admin.
    headline = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=120, blank=True, null=True)
    phone = models.CharField(max_length=40, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username

    @property
    def display_name(self):
        """Name shown publicly, falling back to the account username."""
        return (self.name or self.get_full_name() or self.username or '').strip()

    @property
    def initials(self):
        return _initials_for(self.display_name)

    @property
    def social_links(self):
        """Social profiles that actually have a URL, ready for the templates."""
        pairs = (
            ('github', self.github_url, 'fa-github'),
            ('linkedin', self.linkedin_url, 'fa-linkedin'),
            ('twitter', self.twitter_url, 'fa-x-twitter'),
            ('instagram', self.instagram_url, 'fa-instagram'),
            ('website', self.website, 'fa-globe'),
        )
        links = [
            {'network': network, 'url': url, 'icon': icon}
            for network, url, icon in pairs
            if url
        ]
        if self.email:
            links.append({
                'network': 'email',
                'url': f'mailto:{self.email}',
                'icon': 'fa-envelope',
            })
        return links


class SiteSettings(models.Model):
    """Singleton row holding the editable settings of the whole site."""

    site_name = models.CharField(max_length=120, default='FelloMarley Foundation')
    tagline = models.CharField(max_length=200, blank=True, null=True)
    site_description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(
        MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='site_settings'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'

    def __str__(self):
        return self.site_name or 'Site settings'

    @classmethod
    def current(cls):
        """Return the settings row, or an unsaved default row when none exists."""
        try:
            return cls.objects.select_related('owner').get(pk=1)
        except cls.DoesNotExist:
            return cls(pk=1)

    @property
    def social_links(self):
        return self.owner.social_links if self.owner else []

class contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.CharField(max_length=20)
    date_created=models.DateTimeField(auto_now_add=True, blank=True, null=True)
    message=models.TextField()

    class Meta:
        ordering= ['-date_created']
    def __str__(self):
            return self.name


class BlogPost(models.Model):
    statuschoice=(
        ('drafted','drafted'),
        ('published','published'),
        )
    categorychoice=(
        ('story','Personal Story'),
        ('tutorial','Tutorial'),
        ('insight','Creative Insight'),
        ('community','Community Update'),
        ('news','Foundation News'),
        )
    title= models.CharField(max_length=100)
    content=models.TextField()
    author=models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True)
    status=models.CharField(max_length=100,choices=statuschoice, null=True)
    category=models.CharField(max_length=20,choices=categorychoice, null=True, blank=True, default='story')
    tags=models.CharField(max_length=200, null=True, blank=True)
    views=models.PositiveIntegerField(default=0)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    image=models.ImageField(upload_to='blog_images/', blank=True, null=True)
    video = models.FileField(upload_to='blog_videos/', blank=True, null=True)  # Optional

    class Meta:
        ordering= ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        """Tags stored as a comma separated string, normalised to a clean list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    @property
    def reading_time(self):
        """Rough reading time in whole minutes, rounded up, with a one minute floor."""
        words = len((self.content or '').split())
        return max(1, (words + 199) // 200)

    @property
    def excerpt(self):
        """Short plain text preview of the post body."""
        text = ' '.join((self.content or '').split())
        if len(text) <= 180:
            return text
        return text[:180].rsplit(' ', 1)[0] + '...'

class PortfolioItem(models.Model):
    CATEGORY_CHOICES = (
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('ai', 'Artificial Intelligence'),
        ('graphic', 'Graphic Design'),
        ('other', 'Other'),
    )
    title=models.CharField(max_length=100)
    description=models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    technology = models.CharField(max_length=2445, help_text="Comma-separated (e.g., Python, Django, React)" ,null=True)
    video = models.FileField(upload_to='portfolio_videos/', blank=True, null=True)  # Optional
    image=models.ImageField(upload_to='portfolio_images/', blank=True, null=True)
    live_url = models.URLField(blank=True, null=True, help_text="Link to the live work, for example the hosted site.")
    date_created=models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering= ['-date_created']

    def __str__(self):
        return self.title

class EventCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EventLocation(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.address


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='events_images/', blank=True, null=True)
    start_date=models.DateTimeField(null=True)
    end_date=models.DateTimeField(null=True)
    host = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name="hosted_events", help_text="User who created the event.")
    guests = models.CharField(max_length=255, blank=True, help_text="Guests attending this event.")
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, related_name="events")
    location = models.ForeignKey(EventLocation, on_delete=models.SET_NULL, null=True, related_name="events")
    video = models.FileField(upload_to='events_videos/', blank=True, null=True)  # Optional

    class Meta:
        ordering= ['-start_date']
    def __str__(self):
        return self.title


class Sibling(models.Model):
    name = models.CharField(max_length=100)
    birthdate = models.DateField()
    occupation = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField()
    full_description = models.TextField()
    profile_picture = models.ImageField(upload_to='siblings/', blank=True, null=True)
    video = models.FileField(upload_to='galery_videos/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def age(self):
        today = date.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

class SiblingImage(models.Model):
    sibling = models.ForeignKey(Sibling, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='sibling_images/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    video = models.FileField(upload_to='my_videos/', blank=True, null=True)  # Optional

    def __str__(self):
        return f"Image for {self.sibling.name}"



class EducationLevel(models.Model):
    level = models.CharField(max_length=100)  # e.g., "Bachelor's", "High School"
    school = models.CharField(max_length=100)  # Name of the school or university
    description = models.TextField()  # Description of the education level
    Year=models.CharField(max_length=10, blank=True, null=True)
    Grade=models.CharField(max_length=20, blank=True, null=True)
    pdf_proof = models.FileField(upload_to='education_proofs/', null=True, blank=True)  # The PDF proof file
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering=['-date']

    def __str__(self):
        return f"{self.level} - {self.school}"


class Experience(models.Model):
    """One entry of the work history timeline shown on the about page."""

    title = models.CharField(max_length=150)
    organisation = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['order', '-start_date']

    def __str__(self):
        return f"{self.title} - {self.organisation}"

    @property
    def start_year(self):
        return self.start_date.year if self.start_date else None

    @property
    def end_year(self):
        return self.end_date.year if self.end_date else None

    @property
    def period(self):
        """Human readable date range, for example "2025 - Present"."""
        start = self.start_year or ''
        if self.is_current or not self.end_date:
            end = 'Present'
        else:
            end = self.end_year or ''
        if start and end:
            return f"{start} - {end}"
        return start or end

    @property
    def is_ongoing(self):
        """True while the role is still running, that is without an end date."""
        return bool(self.is_current or not self.end_date)


class Task(models.Model):
    mypriority=(
        ('low','low'),
        ('medium','medium'),
        ('high','high'),
        ('urgent', 'Urgent'),)
    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('development', 'Development'),
        ('design', 'Design'),
        ('content', 'Content & Writing'),
        ('community', 'Community'),
        ('admin', 'Admin & Ops'),
        ('research', 'Research'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True, blank=True, related_name="assigned_tasks")
    created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="created_tasks")
    priority=models.CharField(max_length=100,choices=mypriority,null=True)
    progress_percentage=models.IntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='to_do')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    tags = models.CharField(max_length=200, blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering=['-created_at']
        verbose_name_plural = 'Tasks'


    def __str__(self):
        return self.title

    # --- Display helpers -----------------------------------------------------

    @property
    def priority_label(self):
        """A clean label for the stored priority value."""
        if not self.priority:
            return 'Unset'
        return str(self.priority).capitalize()

    @property
    def priority_slug(self):
        return self.priority or 'low'

    @property
    def status_label(self):
        if self.completed:
            return 'Done'
        return dict(self.STATUS_CHOICES).get(self.status, 'To Do')

    @property
    def status_slug(self):
        if self.completed:
            return 'done'
        return self.status or 'to_do'

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, 'General')

    @property
    def category_slug(self):
        return self.category or 'general'

    @property
    def tag_list(self):
        return [tag.strip() for tag in (self.tags or '').split(',') if tag.strip()]

    @property
    def progress(self):
        """Progress clamped to the 0-100 range the UI expects."""
        try:
            value = int(self.progress_percentage or 0)
        except (TypeError, ValueError):
            value = 0
        return max(0, min(100, value))

    @property
    def is_overdue(self):
        if self.completed or not self.due_date:
            return False
        from django.utils import timezone as _timezone
        return self.due_date < _timezone.now()

    @property
    def days_left(self):
        """Whole days until the due date. Negative when it has passed."""
        if not self.due_date:
            return None
        from django.utils import timezone as _timezone
        now = _timezone.now()
        target = self.due_date
        if target.tzinfo is None:
            target = _timezone.make_aware(target)
        return (target.date() - now.date()).days

    @property
    def is_due_soon(self):
        days = self.days_left
        return days is not None and 0 <= days <= 2 and not self.completed

    @property
    def assignee_name(self):
        if not self.assigned_to:
            return 'Unassigned'
        return getattr(self.assigned_to, 'name', None) or self.assigned_to.username

    @property
    def assignee_initials(self):
        if not self.assigned_to:
            return '—'
        return _initials_for(self.assignee_name)

    @property
    def creator_name(self):
        if not self.created_by:
            return 'Unknown'
        return getattr(self.created_by, 'name', None) or self.created_by.username

    @property
    def creator_initials(self):
        return _initials_for(self.creator_name)

    @property
    def word_count(self):
        return len((self.description or '').split())

class Notification(models.Model):
    KIND_CHOICES = (
        ('task', 'Task'),
        ('event', 'Event'),
        ('blog', 'Publishing'),
        ('message', 'Message'),
        ('support', 'Support'),
        ('system', 'System'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='system')
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="notifications")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def kind_label(self):
        return dict(self.KIND_CHOICES).get(self.kind, 'System')

    @property
    def kind_slug(self):
        return self.kind or 'system'

    @property
    def is_fresh(self):
        """True when the notification landed in the last three days."""
        if not self.created_at:
            return False
        return (timezone.now() - self.created_at).days < 3



class Activity(models.Model):
    TYPE_CHOICES = (
        ('community', 'Community Outreach'),
        ('workshop', 'Workshop'),
        ('training', 'Training'),
        ('meeting', 'Meeting'),
        ('fundraising', 'Fundraising'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    activity_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='community')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    location = models.CharField(max_length=150, blank=True, null=True)
    participants = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="activities")

    class Meta:
        ordering= ['-created_at']

    def __str__(self):
        return self.title

    @property
    def type_label(self):
        return dict(self.TYPE_CHOICES).get(self.activity_type, 'Other')

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Planned')

    @property
    def excerpt(self):
        text = ' '.join((self.description or '').split())
        if len(text) <= 170:
            return text
        return text[:170].rsplit(' ', 1)[0] + '...'



MyUser = get_user_model()

class Support(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('account', 'Account'),
        ('billing', 'Billing'),
        ('other', 'Other'),
    ]
    note=[('pending', 'pending'),
        ('resolved', 'resolved'),
        ('drafted','drafted')]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="supports")
    assignee = models.ForeignKey(MyUser, on_delete=models.SET_NULL, related_name="assigned_supports", null=True, blank=True)
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)
    resolution_notes=models.CharField(max_length=100,choices=note,null=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

    class Meta:
        ordering= ['-created_at']




class ImageGallery(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gallery_images/', blank=True, null=True)
    video = models.FileField(upload_to='gallery_videos/', blank=True, null=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def media_type(self):
        if self.video:
            return "video"
        if self.image:
            return "image"
        return "none"

class message(models.Model):
    name=models.CharField(max_length=100)
    messaging=models.TextField(null=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    CATEGORY_CHOICES = (
        ('web', 'Web Application'),
        ('mobile', 'Mobile Application'),
        ('api', 'API & Backend'),
        ('data', 'Data & Automation'),
        ('design', 'Design'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('idea', 'Concept'),
        ('building', 'In Build'),
        ('live', 'Live'),
        ('archived', 'Archived'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)  # Optional GitHub link
    live_demo = models.URLField(blank=True, null=True)  # Optional demo link
    technologies_used = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Django, React, Tailwind"
    video = models.FileField(upload_to='project_videos/', blank=True, null=True)  # Optional
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='web')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='building')
    role = models.CharField(max_length=150, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    featured = models.BooleanField(default=False, help_text="Show this project in the featured sections of the site.")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    @property
    def tech_list(self):
        """Technologies stored as a comma separated string, normalised to a list."""
        if not self.technologies_used:
            return []
        return [tech.strip() for tech in self.technologies_used.split(',') if tech.strip()]

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, 'Other')

    @property
    def category_slug(self):
        return self.category or 'other'

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'In Build')

    @property
    def status_slug(self):
        return self.status or 'building'

    @property
    def excerpt(self):
        """Short plain text preview of the project description."""
        text = ' '.join((self.description or '').split())
        if len(text) <= 170:
            return text
        return text[:170].rsplit(' ', 1)[0] + '...'

class Certification(models.Model):
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    date_issued = models.DateField()
    credential_url = models.URLField(blank=True, null=True)
    certificate_pdf = models.FileField(upload_to='certificates/', blank=True, null=True)
    certificate_image=models.FileField(upload_to='certificate_images', blank=True, null=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True)
    level = models.CharField(max_length=20, choices=[
        ('foundation', 'Foundation'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='intermediate')
    skills = models.CharField(max_length=255, blank=True, null=True)
    expiry_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_issued']

    def __str__(self):
        return f"{self.title} - {self.issuing_organization}"

    # --- Display helpers -----------------------------------------------------

    @property
    def level_label(self):
        return {
            'foundation': 'Foundation',
            'intermediate': 'Intermediate',
            'advanced': 'Advanced',
            'expert': 'Expert',
        }.get(self.level, 'Intermediate')

    @property
    def level_slug(self):
        return self.level or 'intermediate'

    @property
    def skill_list(self):
        return [skill.strip() for skill in (self.skills or '').split(',') if skill.strip()]

    @property
    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expired(self):
        days = self.days_to_expiry
        return days is not None and days < 0

    @property
    def is_expiring(self):
        days = self.days_to_expiry
        return days is not None and 0 <= days <= 60

    @property
    def status_label(self):
        if self.is_expired:
            return 'Expired'
        if self.is_expiring:
            return 'Expiring soon'
        return 'Active'

    @property
    def status_slug(self):
        if self.is_expired:
            return 'expired'
        if self.is_expiring:
            return 'expiring'
        return 'active'

    @property
    def year(self):
        return self.date_issued.year if self.date_issued else None



class Skill(models.Model):
    CATEGORY_CHOICES = (
        ('technical', 'Technical'),
        ('tool', 'Tools & Platforms'),
        ('soft', 'Soft Skills'),
        ('leadership', 'Leadership'),
        ('language', 'Languages'),
    )

    name = models.CharField(max_length=100)  # e.g., "Python", "Django", "Public Speaking"
    proficiency = models.IntegerField(default=50)  # Represented as a percentage (0-100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=80, blank=True, null=True)  # Font Awesome class, e.g. "fa-brands fa-python"
    years_experience = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-proficiency', 'name']

    def __str__(self):
        return f"{self.name} ({self.proficiency}%)"

    @property
    def level(self):
        """Readable band for a proficiency score."""
        score = self.proficiency or 0
        if score >= 90:
            return 'Expert'
        if score >= 75:
            return 'Advanced'
        if score >= 60:
            return 'Proficient'
        if score >= 40:
            return 'Intermediate'
        return 'Beginner'

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, 'Other')

    @property
    def category_slug(self):
        return self.category or 'technical'

    @property
    def level_slug(self):
        """Key used to pick a colour for the level badge."""
        return {
            'Expert': 'expert',
            'Advanced': 'advanced',
            'Proficient': 'proficient',
            'Intermediate': 'intermediate',
            'Beginner': 'beginner',
        }[self.level]

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
class Testimonial(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="testimonials")
    name = models.CharField(max_length=100)  # Reviewer name
    designation = models.CharField(max_length=100, blank=True, null=True)  # e.g., CEO, Software Engineer
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.designation}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question

class Volunteer(models.Model):
    AREA_CHOICES = [
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('content', 'Content & Writing'),
        ('community', 'Community Outreach'),
        ('mentorship', 'Mentorship'),
        ('operations', 'Operations'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="volunteers")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Weekends only"
    skills = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    area = models.CharField(max_length=20, choices=AREA_CHOICES, default='community')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    hours_per_week = models.PositiveSmallIntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-joined_at']

    def __str__(self):
        return self.full_name

    # --- Display helpers -----------------------------------------------------

    @property
    def area_label(self):
        return dict(self.AREA_CHOICES).get(self.area, 'Other')

    @property
    def area_slug(self):
        return self.area or 'community'

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Applied')

    @property
    def status_slug(self):
        return self.status or 'applied'

    @property
    def skill_list(self):
        raw = self.skills or ''
        parts = [part.strip() for part in raw.split(',') if part.strip()]
        if len(parts) == 1 and len(raw.split()) > 1:
            parts = [part for part in raw.split() if part]
        return parts

    @property
    def initials(self):
        return _initials_for(self.full_name)

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def has_resume(self):
        return bool(self.resume)

class Job(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('filled', 'Filled'),
    ]
    CATEGORY_CHOICES = [
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('content', 'Content & Writing'),
        ('community', 'Community'),
        ('operations', 'Operations'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=[('full-time', 'Full-Time'), ('part-time', 'Part-Time'), ('contract', 'Contract')])
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    application_link = models.URLField(blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    due_at=models.DateField(null=True)
    salary_range=models.CharField(max_length=50,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='engineering')
    skills = models.CharField(max_length=255, blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    slots = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

    # --- Display helpers -----------------------------------------------------

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Open')

    @property
    def status_slug(self):
        return self.status or 'open'

    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, 'Other')

    @property
    def category_slug(self):
        return self.category or 'engineering'

    @property
    def job_type_label(self):
        return dict(self._meta.get_field('job_type').choices).get(self.job_type, 'Full-Time')

    @property
    def skill_list(self):
        return [skill.strip() for skill in (self.skills or '').split(',') if skill.strip()]

    @property
    def is_open(self):
        return self.status == 'open'

    @property
    def applications_count(self):
        return self.applications.count()

    @property
    def days_open(self):
        if not self.posted_at:
            return 0
        return (timezone.now().date() - self.posted_at.date()).days

    @property
    def is_expired(self):
        return bool(self.due_at and self.due_at < timezone.now().date())


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('under_review', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('offer_made', 'Offer Made'),
    ]
    applicant_name=models.CharField(max_length=100,null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")  # The job the user applied for
    applicant = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="applications",null=True)  # The applicant applying for the job
    resume = models.FileField(upload_to='job_applications/resumes/', null=True, blank=True)  # Applicant's resume
    cover_letter = models.FileField(upload_to="Applicant's cover letter",null=True, blank=True)  # Applicant's cover letter
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_review')  # Current status of the application
    applied_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the application was made
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update on the application
    rating = models.IntegerField(null=True, blank=True)
    reviewed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.name}"

    # --- Display helpers -----------------------------------------------------

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Under Review')

    @property
    def status_slug(self):
        return self.status or 'under_review'

    @property
    def applicant_display(self):
        if self.applicant:
            return getattr(self.applicant, 'name', None) or self.applicant.username
        return self.applicant_name or 'Applicant'

    @property
    def applicant_initials(self):
        return _initials_for(self.applicant_display)



class Donation(models.Model):
    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('paypal', 'PayPal'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ]
    PURPOSES = [
        ('general', 'General Fund'),
        ('education', 'Education & Scholarships'),
        ('technology', 'Technology & Tools'),
        ('community', 'Community Outreach'),
        ('emergency', 'Emergency Relief'),
        ('other', 'Other Cause'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    name=models.CharField(max_length=100)
    email=models.EmailField()
    donor = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="donations", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    anonymous = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # To track payments
    date_donated = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=30, choices=PURPOSES, default='general')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True, null=True)
    receipt_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_donated']
        verbose_name_plural = 'Donations'

    def __str__(self):
        return f"Donation of {self.amount} by {self.donor.username if self.donor else 'Anonymous'} via {self.payment_method}"

    # --- Display helpers -----------------------------------------------------

    @property
    def payment_method_label(self):
        return dict(self.PAYMENT_METHODS).get(self.payment_method, 'Other')

    @property
    def purpose_label(self):
        return dict(self.PURPOSES).get(self.purpose, 'General Fund')

    @property
    def purpose_slug(self):
        return self.purpose or 'general'

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, 'Pending')

    @property
    def status_slug(self):
        return self.status or 'pending'

    @property
    def donor_display(self):
        """How the donor is shown publicly: anonymous gifts hide the name."""
        if self.anonymous:
            return 'Anonymous Donor'
        if self.donor:
            return getattr(self.donor, 'name', None) or self.donor.username
        return self.name or 'Anonymous Donor'

    @property
    def initials(self):
        source = 'Anonymous Donor' if self.anonymous else (self.name or 'DN')
        parts = [part for part in (source or '').split() if part]
        if not parts:
            return 'DN'
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def reference(self):
        """A stable public reference derived from the primary key."""
        return f"DN-{self.pk:05d}"

    @property
    def is_completed(self):
        return self.status == 'completed'

