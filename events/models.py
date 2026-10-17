from django.db import models

# Create your models here.
class Event(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data']

    def __str__(self):
        return f"{self.title} at {self.venue}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reservations')
    attendee_name = models.CharField(max_length=200)
    attendee_email = models.EmailField()
    seats_reserved = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.attendee_name} - {self.event.title} ({self.seats_reserved} seats)"
