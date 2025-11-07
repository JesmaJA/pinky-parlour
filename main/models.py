from django.db import models
from django.contrib.auth.models import User

# Services offered
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to='services/')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Appointments
class Appointment(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('Pending','Pending'), ('Approved','Approved'), ('Rejected','Rejected')], default='Pending')

    def __str__(self):
        return f"{self.name} - {self.service.name}"

# Offers / Packages
class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# Gallery Images
class Gallery(models.Model):
    category = models.CharField(max_length=50, choices=[('Hair','Hair'),('Makeup','Makeup'),('Nails','Nails')])
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category} Image"
from django.db import models

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    profile = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    content = models.TextField()
    stars = models.IntegerField(default=5)
    status = models.CharField(max_length=10, choices=[('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"
