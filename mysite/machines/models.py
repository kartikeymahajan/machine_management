from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Machine(models.Model):
    name = models.CharField(max_length=100)
    discription = models.TextField(null=True, max_length=500)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)  # True for free, False for occupied
    purpose = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.TextField()  # Purpose field, can be blank

