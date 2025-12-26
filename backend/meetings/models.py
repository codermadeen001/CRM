from django.db import models
from tasks.models import Deal, Company, Contact

class Meetings(models.Model):
    MEETING_TYPE_CHOICES = [
        ('in_person', 'In Person'),
        ('virtual', 'Virtual'),
        ('phone', 'Phone'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_time = models.DateTimeField()
    duration = models.IntegerField(default=60, help_text='Duration in minutes')
    location = models.TextField(blank=True, default="", null=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='in_person')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    deal = models.ForeignKey(Deal, on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings_meetings')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='meetings_meetings')
    participants = models.ManyToManyField(Contact, related_name='meetings_meetings', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_time']
    
    def __str__(self):
        return f"{self.title} - {self.date_time}"
    
    @property
    def is_upcoming(self):
        from django.utils import timezone
        return self.date_time > timezone.now() and self.status not in ['completed', 'cancelled']
    
    @property
    def end_time(self):
        from django.utils import timezone
        return self.date_time + timezone.timedelta(minutes=self.duration)







