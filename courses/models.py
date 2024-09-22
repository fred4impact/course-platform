from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from taggit.managers import TaggableManager

class Course(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    summary = models.TextField(blank=True, null=True)  # Course summary for listing
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)  # Optional image for course
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')  # Draft or Published status
    is_free = models.BooleanField(default=False)  # New field to mark if a course is free
    
    published_at = models.DateTimeField(null=True, blank=True)  # When the course was published
    
    tags = TaggableManager()  # Add the TaggableManager for course tags

    def publish(self):
        """Set the course status to published and record the time."""
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    # Extend the User model to include bio and social links
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.username




class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def progress(self):
        total_modules = self.course.modules.count()
        completed_modules = self.userprogress_set.filter(completed=True).count()
        if total_modules > 0:
            return (completed_modules / total_modules) * 100
        return 0

    def __str__(self):
        return f'{self.user.username} enrolled in {self.course.title}'

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} progress in {self.module.title}'
