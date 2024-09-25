import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Module, Enrollment, UserProgress
from django.contrib.auth.decorators import login_required
from taggit.models import Tag
from .models import UserProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

def homepage(request):
    # Fetch some popular or recent courses to display
    courses = Course.objects.all()[:3]  # Example: display first 3 courses
    return render(request, 'courses/homepage.html', {'courses': courses})


@login_required
def checkout(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if course.is_free:
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': course.title,
                        },
                        'unit_amount': int(course.price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri(
                    f'/courses/{course_id}/success/'
                ),
                cancel_url=request.build_absolute_uri(
                    f'/courses/{course_id}/'
                ),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return render(request, 'courses/checkout.html', {
                'course': course,
                'error': str(e)
            })

    return render(request, 'courses/checkout.html', {'course': course})


@login_required
def payment_success(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Enroll the user in the course after successful payment
    Enrollment.objects.get_or_create(user=request.user, course=course)

    return render(request, 'courses/payment_success.html', {'course': course})

# courses/views.py
@login_required
def dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    courses = [enrollment.course for enrollment in enrollments]
    
    return render(request, 'courses/dashboard.html', {'courses': courses})

@login_required
def profile_view(request):
    # Render a profile page or redirect to the dashboard if you don't have a profile page.
    return redirect('dashboard')  # Assuming 'dashboard' is your view name

def author_detail(request, author_id):
    # Get the author's profile based on the user ID
    author_profile = get_object_or_404(UserProfile, user__id=author_id)

    return render(request, 'courses/author_detail.html', {
        'author_profile': author_profile,
    })

def course_list_by_tag(request, tag_slug):
    # Get the tag object
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    # Get courses associated with this tag
    courses = Course.objects.filter(tags__in=[tag], status='published')  # Only show published courses

    return render(request, 'courses/course_list_by_tag.html', {'courses': courses, 'tag': tag})



def course_list(request):
    if request.user.is_staff:
        # Show all courses to staff members (draft and published)
        courses = Course.objects.all()
    else:
        # Show only published courses to general users
        courses = Course.objects.filter(status='published')

    return render(request, 'courses/course_list.html', {'courses': courses})


def course_detail(request, course_id):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    
    if request.user.is_staff:
        # Staff can view both draft and published courses
        course = get_object_or_404(Course, id=course_id)
    else:
        # General users can only view published courses
        course = get_object_or_404(Course, id=course_id, status='published')

    modules = course.modules.all()
    tags = course.tags.all()

    # Fetch the course author's bio and social links
    author = course.creator
    author_profile = author.userprofile
    bio = author_profile.bio
    linkedin = author_profile.linkedin
    twitter = author_profile.twitter
    website = author_profile.website
    instagram = author_profile.instagram

    # Check if the course is free or paid
    if course.is_free:
        # Free courses are available to everyone
        return render(request, 'courses/course_detail.html', {
            'course': course,
            'modules': modules,
            'tags': tags,
            'author': author,
            'bio': bio,
            'linkedin': linkedin,
            'twitter': twitter,
            'website': website,
            'instagram': instagram,
        })
    else:
        # Paid courses require enrollment or staff access
        if request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
            if enrollment or request.user.is_staff:
                return render(request, 'courses/course_detail.html', {
                    'course': course,
                    'modules': modules,
                    'tags': tags,
                    'author': author,
                    'bio': bio,
                    'linkedin': linkedin,
                    'twitter': twitter,
                    'website': website,
                    'instagram': instagram,
                })
            else:
                # Redirect to Stripe Checkout
                if request.method == 'POST':
                    try:
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{
                                'price_data': {
                                    'currency': 'usd',
                                    'product_data': {
                                        'name': course.title,
                                    },
                                    'unit_amount': int(course.price * 100),  # Price in cents
                                },
                                'quantity': 1,
                            }],
                            mode='payment',
                            success_url=request.build_absolute_uri(f'/courses/{course.id}/enroll/'),
                            cancel_url=request.build_absolute_uri(f'/courses/{course.id}/'),
                        )
                        return JsonResponse({'id': checkout_session.id})
                    except Exception as e:
                        return JsonResponse({'error': str(e)})

                # Render the course detail page with the Buy Now button
                return render(request, 'courses/course_detail.html', {
                    'course': course,
                    'modules': modules,
                    'tags': tags,
                    'author': author,
                    'bio': bio,
                    'linkedin': linkedin,
                    'twitter': twitter,
                    'website': website,
                    'instagram': instagram,
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,  # Pass the public key
                })
        else:
            return redirect('login')  # Redirect to login if not authenticated




@login_required
def enroll_in_course(request, course_id):
    # Enroll in the course only if it is published or the user is a staff member
    course = get_object_or_404(Course, id=course_id)
    
    # Allow enrollment only for published courses or if the user is staff
    if course.status == 'published' or request.user.is_staff:
        if not course.is_free:
            # For paid courses, check for enrollment
            enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
            return redirect('course_detail', course_id=course.id)
        else:
            # Free courses don't require enrollment, just redirect to course detail
            return redirect('course_detail', course_id=course.id)
    else:
        return redirect('course_list')  # Redirect if the course is not published

@login_required
def module_detail(request, course_id, module_id):
    # Access modules only if the course is published or the user is a staff member
    course = get_object_or_404(Course, id=course_id)
    
    if course.status == 'published' or request.user.is_staff:
        module = get_object_or_404(Module, id=module_id, course=course)
        progress, created = UserProgress.objects.get_or_create(user=request.user, module=module)
        
        if request.method == "POST":
            progress.completed = True
            progress.save()
            return redirect('course_detail', course_id=course.id)
        
        return render(request, 'courses/module_detail.html', {'module': module, 'progress': progress})
    else:
        return redirect('course_list')  # Redirect if the course is not published

@csrf_exempt
def create_checkout_session(request, course_id):
    if request.method == 'POST':
        try:
            course = Course.objects.get(id=course_id)
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': course.title,
                        },
                        'unit_amount': int(course.price * 100),  # Stripe expects amounts in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',  # Update with your actual success URL
                cancel_url='http://127.0.0.1:8000/cancel/',  # Update with your actual cancel URL
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
