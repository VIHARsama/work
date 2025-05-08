from django.db import models

# Create your models here.

class EventList(models.Model):
    eventID = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.eventID

class SantaPair(models.Model):
    event = models.ForeignKey(EventList, on_delete=models.CASCADE)
    santaPair = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['event']),
        ]

    def __str__(self):
        return f"Santa Pair: {self.santaPair} for Event: {self.event.eventID}"