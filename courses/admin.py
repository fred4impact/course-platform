from django.contrib import admin
from .models import Course, Module, Enrollment, UserProgress, UserProfile
from taggit.models import Tag  # For tagging

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'creator', 'created_at', 'published_at')  # Display creator
    list_filter = ('status', 'created_at', 'tags')  # Filter by tags
    search_fields = ('title', 'tags__name', 'creator__username')  # Search by tags and creator
    inlines = [ModuleInline]

    # Custom admin actions
    actions = ['make_published']

    def make_published(self, request, queryset):
        queryset.update(status='published', published_at=timezone.now())
    make_published.short_description = "Mark selected courses as published"

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'linkedin', 'twitter', 'website', 'instagram')
    search_fields = ('user__username', 'bio')

# Register the models with the updated admin functionality
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment)
admin.site.register(UserProgress)
admin.site.register(UserProfile, UserProfileAdmin)  # Register UserProfile for bio and social links
 # Ensure tags can be managed via the admin panel
