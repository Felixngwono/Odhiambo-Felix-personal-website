from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


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
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username


   


class contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.IntegerField()
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
    title= models.CharField(max_length=100)
    content=models.TextField()
    author=models.ForeignKey(MyUser, on_delete=models.CASCADE,null=True)
    status=models.CharField(max_length=100,choices=statuschoice, null=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    image=models.ImageField(upload_to='blog_images/', blank=True, null=True)
    video = models.FileField(upload_to='blog_videos/', blank=True, null=True)  # Optional

    class Meta:
        ordering= ['-updated_at']

    def __str__(self):
        return self.title
    
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
    date_created=models.DateTimeField(auto_now_add=True, blank=True, null=True)
    #url=models.URLField()
    
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
    age=models.IntegerField()
    occupation = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField()
    full_description = models.TextField()
    profile_picture = models.ImageField(upload_to='siblings/', blank=True, null=True)
    video = models.FileField(upload_to='galery_videos/', blank=True, null=True)  # Optional

    def __str__(self):
        return self.name
    
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
    
class Task(models.Model):
    mypriority=(
        ('low','low'),
        ('medium','medium'),
        ('high','high'),
        ('urgent', 'Urgent'),)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True, blank=True, related_name="assigned_tasks")
    created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="created_tasks")
    priority=models.CharField(max_length=100,choices=mypriority,null=True)
    progress_percentage=models.IntegerField(default=50)

    class Meta:
        ordering=['-created_at']


    def __str__(self):
        return self.title

class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="notifications")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    

class Activity(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="activities")
    class Meta:
        ordering= ['-created_at']

    def __str__(self):
        return self.title
    

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
    image = models.ImageField(upload_to='gallery_images/')
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    video=models.FileField(upload_to='gallery_videos/', blank=True, null=True)  # Optional
    class Meta:
        ordering= ['-created_at']

    def __str__(self):
        return self.title

class message(models.Model):
    name=models.CharField(max_length=100)
    messaging=models.TextField(null=True)
   
    def __str__(self):
        return self.name
 
class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)  # Optional GitHub link
    live_demo = models.URLField(blank=True, null=True)  # Optional demo link
    technologies_used = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Django, React, Tailwind"
    video = models.FileField(upload_to='project_videos/', blank=True, null=True)  # Optional

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

class Certification(models.Model):
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    date_issued = models.DateField()
    credential_url = models.URLField(blank=True, null=True)
    certificate_pdf = models.FileField(upload_to='certificates/', blank=True, null=True)
    certificate_image=models.FileField(upload_to='certificate_images', blank=True, null=True)
    
    class Meta:
        ordering = ['-date_issued']

    def __str__(self):
        return f"{self.title} - {self.issuing_organization}"



class Skill(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Python", "Django", "Public Speaking"
    proficiency = models.IntegerField(default=50)  # Represented as a percentage (0-100)

    def __str__(self):
        return f"{self.name} ({self.proficiency}%)"

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
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="volunteers")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Weekends only"
    skills = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-joined_at']

    def __str__(self):
        return self.full_name

class Job(models.Model):
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

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

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
    cover_letter = models.FileField(upload_to="Applicant's cover letter",null=True)  # Applicant's cover letter
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_review')  # Current status of the application
    applied_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the application was made
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update on the application
    
    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.name}"


class Donation(models.Model):
    PAYMENT_METHODS = [
        ('mpesa', 'M-PESA'),
        ('paypal', 'PayPal'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
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

    class Meta:
        ordering = ['-date_donated']

    def __str__(self):
        return f"Donation of {self.amount} by {self.donor.username if self.donor else 'Anonymous'} via {self.payment_method}"

