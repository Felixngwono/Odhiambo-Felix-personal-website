from django.forms import ModelForm
from django import forms
from .models import FAQ, Donation, Job, NewsletterSubscriber,Activity, BlogPost, Certification, EducationLevel, ImageGallery, JobApplication, Notification, PortfolioItem, Project, Sibling, SiblingImage, Skill, Support, Task, MyUser, Testimonial, Volunteer, contact, Event,EventCategory,EventLocation, message
from django.contrib.auth.forms import UserCreationForm

class  MyUserCreationForm(UserCreationForm):
    
    class Meta:
        model = MyUser
        fields = ['name','username','email','is_enduser','gender','profilepic']

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
        fields = ['name', 'birthdate', 'age', 'occupation', 'full_description', 'profile_picture']

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
        fields = ['title', 'image', 'caption']
       


class BlogForm(ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title','content','author','image','video']

class MessageForm(ModelForm):
    
    class Meta:
        model = message
        fields = '__all__'

class TaskForm(ModelForm):
    
    class Meta:
        model = Task
        fields = '__all__'

class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = "__all__"

class NotificationForm(ModelForm):
    class Meta:
        model = Notification
        fields = "__all__"



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
        fields = ['title', 'issuing_organization', 'date_issued', 'credential_url', 'certificate_pdf','certificate_image']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
        }



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
        fields = ['name', 'proficiency']
        widgets = {
            'proficiency': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 1}),
        }

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'designation', 'message', 'image']


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields ='__all__'



class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'job_type', 'description', 'requirements', 'application_link','salary_range','due_at']

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['job','applicant_name','resume', 'cover_letter']


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['name', 'email', 'amount', 'payment_method']

class FAQForm(forms.ModelForm):
    
    class Meta:
        model = FAQ
        fields = '__all__'


class OurSiblingsForm(forms.ModelForm):
    
    class Meta:
        model = SiblingImage
        fields = ['image', 'description']
