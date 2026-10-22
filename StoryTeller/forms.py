from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

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
    message,
)


class  MyUserCreationForm(UserCreationForm):

    class Meta:
        model = MyUser
        fields = ['name','username','email','gender','profilepic']

        def clean_email(self):

         email = self.cleaned_data.get("email")
         if MyUser.objects.filter(email=email).exclude(username=self.instance.username).exists():
            raise forms.ValidationError("This email is already taken.")
         return email


class BlogPostForm(ModelForm):
    class Meta:
        model=BlogPost
        fields='__all__'


class PortfolioForm(ModelForm):
    class Meta:
        model=PortfolioItem
        fields='__all__'

class  ContactusForm(ModelForm):

    class Meta:
        model = contact
        fields = '__all__'


class eventsForm(ModelForm):
    class Meta:
        model=Event
        fields='__all__'

class EventCategoryForm(ModelForm):

    class Meta:
        model = EventCategory
        fields = '__all__'

class eventlocationForm(ModelForm):

    class Meta:
        model=EventLocation
        fields='__all__'


class SiblingForm(ModelForm):

    class Meta:
        model = Sibling
        fields = ['name', 'birthdate',  'occupation','short_description', 'full_description', 'profile_picture']

class EducationLevelForm(ModelForm):
    class Meta:
        model = EducationLevel
        fields = ['level', 'school', 'description', 'pdf_proof']

class EducationLevelForm(ModelForm):  # noqa: F811

    class Meta:
        model = EducationLevel
        fields = "__all__"

class ImageGalleryForm(ModelForm):
    class Meta:
        model = ImageGallery
        fields = ['title', 'image', 'caption','video']



class BlogForm(ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'author', 'status', 'category', 'tags', 'image', 'video']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Give the post a clear, memorable title'}),
            'content': forms.Textarea(attrs={'rows': 12, 'placeholder': 'Write the full story here...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Community, Mentorship, Youth'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['author'].required = False
        if not self.instance.pk and not self.initial.get('status'):
            self.initial['status'] = 'drafted'
        if not self.instance.pk and not self.initial.get('category'):
            self.initial['category'] = 'story'

class MessageForm(ModelForm):

    class Meta:
        model = message
        fields = '__all__'

class TaskForm(ModelForm):
    priority = forms.ChoiceField(
        required=False,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        label='Priority',
    )
    progress_percentage = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 5}),
        label='Progress (%)',
    )
    estimated_hours = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=6,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'min': 0, 'step': '0.25'}),
        label='Estimated hours',
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'due_date', 'status', 'category', 'priority',
            'progress_percentage', 'estimated_hours', 'tags', 'notes',
            'assigned_to', 'created_by', 'completed',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'What needs doing?'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the work and what done looks like'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Community, Mentorship'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Internal notes, blockers, links'}),
        }
        labels = {
            'assigned_to': 'Assignee',
            'created_by': 'Created by',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].required = False
        self.fields['created_by'].required = False
        self.fields['notes'].required = False
        self.fields['tags'].required = False

    def clean_progress_percentage(self):
        value = self.cleaned_data.get('progress_percentage')
        if value is None:
            return 0
        return max(0, min(100, value))


class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = "__all__"

class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'kind', 'link', 'read', 'user']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'What happened?'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Add the detail behind the alert'}),
            'link': forms.TextInput(attrs={'placeholder': '/tasks/ or https://...'}),
        }



class NewsletterForm(ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']



class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'



class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = [
            'title', 'issuing_organization', 'level', 'date_issued', 'expiry_date',
            'credential_id', 'skills', 'description', 'credential_url',
            'certificate_pdf', 'certificate_image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Certificate title'}),
            'issuing_organization': forms.TextInput(attrs={'placeholder': 'Issuing body'}),
            'credential_id': forms.TextInput(attrs={'placeholder': 'Reference or licence number'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Cloud, Data Analysis'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What the certificate covered'}),
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'certificate_pdf': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
            'certificate_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('expiry_date', 'credential_id', 'skills', 'description', 'credential_url'):
            self.fields[name].required = False


class NewsletterForm(forms.ModelForm):  # noqa: F811
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']


class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ['title', 'description', 'category','user','assignee','status', 'priority', 'attachment']



class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency', 'years_experience', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Python, Public Speaking, Figma...'}),
            'proficiency': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
            'years_experience': forms.NumberInput(attrs={'min': 0, 'max': 60, 'step': 1}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What do you do with it, and where have you used it?'}),
            'icon': forms.TextInput(attrs={'placeholder': 'fa-brands fa-python'}),
        }

    def clean_proficiency(self):
        value = self.cleaned_data.get('proficiency') or 0
        return max(0, min(100, value))

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'designation', 'message', 'image']


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = [
            'full_name', 'email', 'phone', 'area', 'status', 'availability',
            'skills', 'hours_per_week', 'start_date', 'linkedin', 'reason',
            'notes', 'resume',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+254 700 000 000'}),
            'availability': forms.TextInput(attrs={'placeholder': 'Weekends, evenings'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Facilitation'}),
            'hours_per_week': forms.NumberInput(attrs={'min': 0, 'max': 40}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Why do you want to join?'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Internal notes about this volunteer'}),
            'resume': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False
        self.fields['linkedin'].required = False
        self.fields['resume'].required = False


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location', 'job_type', 'category', 'status',
            'description', 'requirements', 'skills', 'benefits', 'salary_range',
            'application_link', 'due_at', 'slots', 'is_featured',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Role title'}),
            'company': forms.TextInput(attrs={'placeholder': 'Company or team'}),
            'location': forms.TextInput(attrs={'placeholder': 'Nairobi, Kenya'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Django, Figma, Facilitation'}),
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'What the role involves'}),
            'requirements': forms.Textarea(attrs={'rows': 5, 'placeholder': 'What you bring'}),
            'benefits': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What the role offers'}),
            'due_at': forms.DateInput(attrs={'type': 'date'}),
            'slots': forms.NumberInput(attrs={'min': 1, 'max': 50}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ('location', 'application_link', 'salary_range', 'skills', 'benefits', 'requirements', 'due_at'):
            self.fields[name].required = False


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['job', 'applicant_name', 'resume', 'cover_letter']
        widgets = {
            'applicant_name': forms.TextInput(attrs={'placeholder': 'Your full name'}),
            'resume': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
            'cover_letter': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applicant_name'].required = False


class DonationForm(forms.ModelForm):
    amount = forms.DecimalField(
        min_value=1,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '1', 'class': 'w-full p-3 border rounded-lg'}),
    )

    class Meta:
        model = Donation
        fields = ['name', 'email', 'amount', 'payment_method', 'purpose', 'message', 'anonymous']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 border rounded-lg', 'placeholder': 'you@example.com'}),
            'payment_method': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'purpose': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'rows': 4, 'placeholder': 'Add a note or dedicate this gift'}),
        }
        labels = {
            'anonymous': 'Keep my name private (list as Anonymous)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].required = False
        self.fields['anonymous'].required = False


class DonationAdminForm(ModelForm):
    """Full admin form: it can also record who made the gift and how it was settled."""

    donated_on = forms.DateField(
        required=False,
        label='Donation date',
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Optional: backdate a gift that was made offline.',
    )

    class Meta:
        model = Donation
        fields = [
            'name', 'email', 'donor', 'amount', 'payment_method', 'purpose',
            'status', 'transaction_id', 'message', 'notes',
            'anonymous', 'receipt_sent',
        ]
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['donor'].required = False
        self.fields['transaction_id'].required = False
        self.fields['message'].required = False
        self.fields['notes'].required = False
        self.fields['anonymous'].required = False
        self.fields['receipt_sent'].required = False
        if self.instance and self.instance.pk and self.instance.date_donated:
            self.fields['donated_on'].initial = self.instance.date_donated.date()


class FAQForm(forms.ModelForm):

    class Meta:
        model = FAQ
        fields = '__all__'


class OurSiblingsForm(forms.ModelForm):

    class Meta:
        model = SiblingImage
        fields = ['image', 'description']
