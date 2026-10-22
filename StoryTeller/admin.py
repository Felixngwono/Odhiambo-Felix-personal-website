from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .forms import MyUserCreationForm
from .models import (
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
    SiteSettings,
    Skill,
    Support,
    Task,
    Testimonial,
    Volunteer,
    contact,
)


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = MyUser
        fields = "__all__"


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    list_display = ("email", "name", "is_staff", "is_superuser", "date_joined")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_enduser")
    search_fields = ("email", "name", "username")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "name", "username", "password")}),
        ("Profile", {"fields": ("bio", "profilepic", "birthdate", "gender")}),
        (
            "Public identity",
            {
                "fields": (
                    "headline",
                    "location",
                    "phone",
                    "website",
                    "github_url",
                    "linkedin_url",
                    "twitter_url",
                    "instagram_url",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "date_created")
    list_filter = ("date_created",)
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("date_created",)
    date_hierarchy = "date_created"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "content")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = ("publish_posts",)

    @admin.action(description="Publish selected posts")
    def publish_posts(self, request, queryset):
        updated = queryset.update(status="published")
        self.message_user(request, f"{updated} post(s) published.")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "technologies_used", "featured")
    list_filter = ("featured", "category", "status")
    search_fields = ("title", "description", "technologies_used")


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "date_created")
    list_filter = ("category", "date_created")
    search_fields = ("title", "description", "technology")
    readonly_fields = ("date_created",)


@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "caption")
    readonly_fields = ("created_at",)


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    search_fields = ("name", "address")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "location", "host", "start_date")
    list_filter = ("category", "location", "start_date")
    search_fields = ("title", "description", "guests")
    date_hierarchy = "start_date"
    autocomplete_fields = ("host",)


@admin.register(Sibling)
class SiblingAdmin(admin.ModelAdmin):
    list_display = ("name", "occupation", "birthdate")
    search_fields = ("name", "occupation")


@admin.register(SiblingImage)
class SiblingImageAdmin(admin.ModelAdmin):
    list_display = ("sibling", "description", "uploaded_at")
    list_filter = ("sibling",)
    readonly_fields = ("uploaded_at",)


@admin.register(EducationLevel)
class EducationLevelAdmin(admin.ModelAdmin):
    list_display = ("level", "school", "Year", "date")
    list_filter = ("level",)
    search_fields = ("level", "school", "description")
    readonly_fields = ("date",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "assigned_to", "due_date", "completed")
    list_filter = ("priority", "completed", "due_date")
    search_fields = ("title", "description")
    date_hierarchy = "due_date"
    actions = ("mark_completed",)

    @admin.action(description="Mark selected tasks as completed")
    def mark_completed(self, request, queryset):
        updated = queryset.update(completed=True)
        self.message_user(request, f"{updated} task(s) marked as completed.")


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "category", "user", "created_at")
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "job_type", "posted_at", "due_at")
    list_filter = ("job_type", "posted_at")
    search_fields = ("title", "company", "location", "description")
    readonly_fields = ("posted_at",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant_name", "job", "status", "applied_at")
    list_filter = ("status", "applied_at")
    search_fields = ("applicant_name", "job__title")
    readonly_fields = ("applied_at", "updated_at")
    autocomplete_fields = ("job", "applicant")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at",)
    actions = ("mark_read",)

    @admin.action(description="Mark selected notifications as read")
    def mark_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("title", "description")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "proficiency")
    search_fields = ("name",)
    ordering = ("-proficiency",)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "issuing_organization", "date_issued")
    search_fields = ("title", "issuing_organization")
    ordering = ("-date_issued",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "designation", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "designation", "message")
    readonly_fields = ("created_at",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "created_at")
    search_fields = ("question", "answer")
    readonly_fields = ("created_at",)


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "availability", "joined_at")
    list_filter = ("availability", "joined_at")
    search_fields = ("full_name", "email", "skills")
    readonly_fields = ("joined_at",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "subscribed_at")
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "amount", "payment_method", "date_donated")
    list_filter = ("payment_method", "date_donated")
    search_fields = ("name", "email", "transaction_id")
    readonly_fields = ("date_donated",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("title", "organisation", "period", "order")
    list_editable = ("order",)
    search_fields = ("title", "organisation")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "owner", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        """There is only one settings row, so adding a second one is not allowed."""
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
