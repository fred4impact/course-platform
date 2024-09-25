# courses/urls.py
from django.urls import path
from . import views
from .views import create_checkout_session

urlpatterns = [
   # Home page with the list of courses
    path('', views.course_list, name='course_list'),
    
    # Course detail page (displays course details, modules, etc.)
    path('<int:course_id>/', views.course_detail, name='course_detail'),

    # Enroll in a course (either free or paid)
    path('<int:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'),

    # Module details for a specific course
    path('<int:course_id>/modules/<int:module_id>/', views.module_detail, name='module_detail'),

    # Display courses by tag
    path('tag/<slug:tag_slug>/', views.course_list_by_tag, name='course_list_by_tag'),

    # Author detail view (for course creators, displaying bio and social links)
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),

    path('<int:course_id>/checkout/', views.checkout, name='checkout'),

    
    
    path('<int:course_id>/success/', views.payment_success, name='payment_success'),

    # path('courses/<int:course_id>/checkout/', views.create_checkout_session, name='create_checkout_session'),

    path('create-checkout-session/<int:course_id>/', create_checkout_session, name='create_checkout_session'),


]
