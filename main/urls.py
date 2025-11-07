from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # User Side URLs
    # =========================
    path('', views.home, name='home'),
    path('services/', views.services_page, name='services_page'),
        path('about/', views.about_page, name='about'),
                path('contact/', views.contact_page, name='contact'),


    path('gallery/', views.gallery_page, name='gallery_page'),
    path('offers/', views.offers_page, name='offers_page'),
    path('book/', views.book_appointment, name='book_appointment'),

    # =========================
    # Admin Authentication & Dashboard
    # =========================
    path('admin/', views.admin_login_view, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),

    # Approve/Reject Appointments
    path('approve/<int:id>/', views.approve_appointment, name='approve_appointment'),
    path('reject/<int:id>/', views.reject_appointment, name='reject_appointment'),
        path('delete/<int:appt_id>/', views.delete_appointment, name='delete_appointment'),


    # =========================
    # Service Management
    # =========================
    path('add-service/', views.add_service, name='add_service'),
    path('edit-service/<int:id>/', views.edit_service, name='edit_service'),
    path('delete-service/<int:id>/', views.delete_service, name='delete_service'),

    # =========================
    # Offer Management
    # =========================
    path('add-offer/', views.add_offer, name='add_offer'),
    path('edit-offer/<int:id>/', views.edit_offer, name='edit_offer'),
    path('delete-offer/<int:id>/', views.delete_offer, name='delete_offer'),

    # =========================
    # Gallery Management
    # =========================
    path('add-gallery/', views.add_gallery, name='add_gallery'),
    path('edit-gallery/<int:id>/', views.edit_gallery, name='edit_gallery'),
    path('delete-gallery/<int:id>/', views.delete_gallery, name='delete_gallery'),

    
    
    # Admin Pages for Sidebar
path('admin-services/', views.services_page_admin, name='services_page_admin'),
path('admin-offers/', views.offers_page_admin, name='offers_page_admin'),
path('admin-gallery/', views.gallery_page_admin, name='gallery_page_admin'),
path('admin-appointments/', views.appointments_page_admin, name='appointments_page_admin'),

path("testimonials/", views.testimonials_page, name="testimonials_page"),
    path("submit-feedback/", views.submit_feedback, name="submit_feedback"),

    # Admin testimonial control
    path("admin/testimonials/", views.testimonials_page_admin, name="testimonials_page_admin"),
    path("admin/testimonials/approve/<int:id>/", views.approve_testimonial, name="approve_testimonial"),
    path("admin/testimonials/reject/<int:id>/", views.reject_testimonial, name="reject_testimonial"),

]
