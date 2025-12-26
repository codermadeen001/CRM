# tasks/tasks.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from django.apps import AppConfig

def update_past_meetings():
    try:
        from .models import Meetings
        
        now = timezone.now()
        print(f"[{now}] Checking for past meetings...")
        

        past_meetings = Meetings.objects.filter(
            status__in=['scheduled', 'in_progress'],
            date_time__lt=now
        )
        
        updated_count = 0
        for meeting in past_meetings:
            meeting_end_time = meeting.date_time + timezone.timedelta(minutes=meeting.duration)
            if meeting_end_time < now:
                meeting.status = 'completed'
                meeting.save()
                updated_count += 1
                print(f"   Meeting '{meeting.title}' marked as completed")
        
        if updated_count > 0:
            print(f"   Updated {updated_count} meetings to 'completed' status")
        else:
            print("   No meetings to update")
            
    except Exception as e:
        print(f"   Error updating past meetings: {e}")

# Start the scheduler when Django starts
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_past_meetings,
        trigger=IntervalTrigger(minutes=1),  # Run every 1 second
        id='update_past_meetings',
        replace_existing=True
    )
    scheduler.start()
   