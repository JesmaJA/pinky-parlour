from django.shortcuts import render, redirect, get_object_or_404
from .models import Service, Appointment, Offer, Gallery, Testimonial
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

# =========================
# User Side Views
# =========================
def home(request):
    services = Service.objects.filter(available=True)
    offers = Offer.objects.filter(active=True)
    gallery = Gallery.objects.filter(active=True)
    testimonials = Testimonial.objects.filter(status="approved")

    return render(request, 'home.html', {
        'services': services,
        'offers': offers,
        'gallery': gallery,
        'testimonials': testimonials
    })

def services_page(request):
    services = Service.objects.filter(available=True)
    return render(request, 'services.html', {'services': services})

def about_page(request):
    return render(request, 'about.html')
def contact_page(request):
    return render(request, 'contact.html')

def gallery_page(request):
    gallery = Gallery.objects.filter(active=True)
    return render(request, 'gallery.html', {'gallery': gallery})

def offers_page(request):
    offers = Offer.objects.filter(active=True)
    return render(request, 'offers.html', {'offers': offers})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Testimonial

def testimonials_page(request):
    testimonials = Testimonial.objects.filter(status="Approved")
    return render(request, "testimonials.html", {"testimonials": testimonials})

def submit_feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        content = request.POST.get("content")
        stars = request.POST.get("stars")
        profile = request.FILES.get("profile")

        Testimonial.objects.create(
            name=name,
            content=content,
            stars=stars,
            profile=profile,
            status="Pending"
        )
        messages.success(request, "Thank you! Your feedback has been submitted and is waiting for admin approval.")
        return redirect("testimonials_page")


def testimonials_page_admin(request):
    testimonials = Testimonial.objects.all()
    return render(request, "admin_testimonials.html", {"testimonials": testimonials})

def approve_testimonial(request, id):
    t = get_object_or_404(Testimonial, id=id)
    t.status = "Approved"
    t.save()
    return redirect("testimonials_page_admin")

def reject_testimonial(request, id):
    t = get_object_or_404(Testimonial, id=id)
    t.status = "Rejected"
    t.save()
    return redirect("testimonials_page_admin")

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def book_appointment(request):
    if request.method == "POST":
        service_id = request.POST.get('service')
        service = Service.objects.get(id=service_id)
        
        appointment = Appointment.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            service=service,
            date=request.POST['date'],
            time=request.POST['time'],
            status='Pending'  # Default status
        )

        # Success message for user
        messages.success(request, f"Your appointment for {service.name} on {appointment.date} at {appointment.time} has been successfully booked!")

        # Notify Admin via email
        admin_email = settings.DEFAULT_ADMIN_EMAIL
        send_mail(
            subject="New Appointment Booked",
            message=f"A new appointment has been booked by {appointment.name}.\n"
                    f"Service: {service.name}\nDate: {appointment.date}\nTime: {appointment.time}\n"
                    f"Phone: {appointment.phone}\nEmail: {appointment.email}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=True,
        )

        return redirect('book_appointment')

    services = Service.objects.filter(available=True)
    return render(request, 'book.html', {'services': services})


# =========================
# Admin Authentication
# =========================
def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin_login.html', {'error': 'Invalid credentials'})
    return render(request, 'admin_login.html')


# =========================
# Admin Dashboard
# =========================
@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    context = {
        'appointments': Appointment.objects.all(),
        'services': Service.objects.all(),
        'offers': Offer.objects.all(),
        'gallery': Gallery.objects.all(),
        'testimonials': Testimonial.objects.all()
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def approve_appointment(request, id):
    appt = get_object_or_404(Appointment, id=id)
    appt.status = 'Approved'
    appt.save()

    # Notify user
    send_mail(
        subject="Your Appointment is Confirmed",
        message=f"Hello {appt.name},\n\nYour appointment for {appt.service.name} on {appt.date} at {appt.time} has been APPROVED by our admin.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appt.email],
        fail_silently=True,
    )

    messages.success(request, f"Appointment {appt.id} approved and user notified.")
    return redirect('admin_dashboard')


@login_required
def reject_appointment(request, id):
    appt = get_object_or_404(Appointment, id=id)
    appt.status = 'Rejected'
    appt.save()

    # Notify user
    send_mail(
        subject="Your Appointment is Rejected",
        message=f"Hello {appt.name},\n\nWe are sorry to inform you that your appointment for {appt.service.name} on {appt.date} at {appt.time} has been REJECTED.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appt.email],
        fail_silently=True,
    )

    messages.warning(request, f"Appointment {appt.id} rejected and user notified.")
    return redirect('admin_dashboard')



# =========================
# Reusable Admin Form Helper
# =========================
def admin_form_view(request, model_class, fields, obj=None, form_type=None, back_url='admin_dashboard'):
    """
    Generic add/edit form view for admin.
    model_class: Django model class (Service, Offer, Gallery, Testimonial)
    fields: list of dicts defining each field (label, name, type)
    obj: object to edit (None for add)
    form_type: string name of the model ('Service', 'Offer', etc.)
    back_url: redirect url on cancel
    """
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == "POST":
        data = {}
        for f in fields:
            name = f['name']
            if f['type'] == 'checkbox':
                data[name] = request.POST.get(name) == 'on'
            elif f['type'] == 'file':
                data[name] = request.FILES.get(name)
            else:
                data[name] = request.POST.get(name)
        
        if obj:  # Edit
            for k, v in data.items():
                if v is not None:
                    setattr(obj, k, v)
            obj.save()
        else:  # Add
            model_class.objects.create(**data)
        return redirect(back_url)
    
    # Set initial values for edit form
    for f in fields:
        f['value'] = getattr(obj, f['name'], None) if obj else None
    
    return render(request, 'admin_form.html', {
        'form_type': form_type,
        'action': 'Edit' if obj else 'Add',
        'fields': fields,
        'back_url': f'/{back_url}/'
    })


# =========================
# Service Views
# =========================
@login_required
def add_service(request):
    fields = [
        {'label': 'Name', 'name': 'name', 'type': 'text'},
        {'label': 'Description', 'name': 'description', 'type': 'textarea'},
        {'label': 'Price', 'name': 'price', 'type': 'number'},
        {'label': 'Available', 'name': 'available', 'type': 'checkbox'},
        {'label': 'Image', 'name': 'image', 'type': 'file'},
    ]
    return admin_form_view(request, Service, fields, form_type='Service')

@login_required
def edit_service(request, id):
    service = get_object_or_404(Service, id=id)
    fields = [
        {'label': 'Name', 'name': 'name', 'type': 'text'},
        {'label': 'Description', 'name': 'description', 'type': 'textarea'},
        {'label': 'Price', 'name': 'price', 'type': 'number'},
        {'label': 'Available', 'name': 'available', 'type': 'checkbox'},
        {'label': 'Image', 'name': 'image', 'type': 'file'},
    ]
    return admin_form_view(request, Service, fields, obj=service, form_type='Service')

@login_required
def delete_service(request, id):
    service = get_object_or_404(Service, id=id)
    service.delete()
    return redirect('admin_dashboard')


# =========================
# Offer Views
# =========================
@login_required
def add_offer(request):
    fields = [
        {'label': 'Title', 'name': 'title', 'type': 'text'},
        {'label': 'Description', 'name': 'description', 'type': 'textarea'},
        {'label': 'Start Date', 'name': 'start_date', 'type': 'date'},
        {'label': 'End Date', 'name': 'end_date', 'type': 'date'},
        {'label': 'Active', 'name': 'active', 'type': 'checkbox'},
    ]
    return admin_form_view(request, Offer, fields, form_type='Offer')

@login_required
def edit_offer(request, id):
    offer = get_object_or_404(Offer, id=id)
    fields = [
        {'label': 'Title', 'name': 'title', 'type': 'text'},
        {'label': 'Description', 'name': 'description', 'type': 'textarea'},
        {'label': 'Start Date', 'name': 'start_date', 'type': 'date'},
        {'label': 'End Date', 'name': 'end_date', 'type': 'date'},
        {'label': 'Active', 'name': 'active', 'type': 'checkbox'},
    ]
    return admin_form_view(request, Offer, fields, obj=offer, form_type='Offer')

@login_required
def delete_offer(request, id):
    offer = get_object_or_404(Offer, id=id)
    offer.delete()
    return redirect('admin_dashboard')


# =========================
# Gallery Views
# =========================
@login_required
def add_gallery(request):
    fields = [
        {'label': 'Category', 'name': 'category', 'type': 'text'},
        {'label': 'Description', 'name': 'description', 'type': 'textarea'},
        {'label': 'Active', 'name': 'active', 'type': 'checkbox'},
        {'label': 'Image', 'name': 'image', 'type': 'file'},
    ]
    return admin_form_view(request, Gallery, fields, form_type='Gallery')

@login_required
def edit_gallery(request, id):
    gallery = get_object_or_404(Gallery, id=id)
    fields = [
        {'label': 'Category', 'name': 'category', 'type': 'text'},
        {'label': 'Description', 'name': 'description', 'type': 'textarea'},
        {'label': 'Active', 'name': 'active', 'type': 'checkbox'},
        {'label': 'Image', 'name': 'image', 'type': 'file'},
    ]
    return admin_form_view(request, Gallery, fields, obj=gallery, form_type='Gallery')

@login_required
def delete_gallery(request, id):
    gallery = get_object_or_404(Gallery, id=id)
    gallery.delete()
    return redirect('admin_dashboard')



# Admin Pages for Sidebar
@login_required
def services_page_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    services = Service.objects.all()
    return render(request, 'admin_services.html', {'services': services})

@login_required
def offers_page_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    offers = Offer.objects.all()
    return render(request, 'admin_offers.html', {'offers': offers})

@login_required
def gallery_page_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    gallery = Gallery.objects.all()
    return render(request, 'admin_gallery.html', {'gallery': gallery})

@login_required
def testimonials_page_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    testimonials = Testimonial.objects.all()
    return render(request, 'admin_testimonials.html', {'testimonials': testimonials})

@login_required
def appointments_page_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    appointments = Appointment.objects.all()
    return render(request, 'admin_appointments.html', {'appointments': appointments})

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Appointment

def delete_appointment(request, appt_id):
    appointment = get_object_or_404(Appointment, id=appt_id)
    appointment.delete()
    return redirect('appointments_page_admin')  # change to your actual manage page URL name
