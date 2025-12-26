# views.py
from django.http import JsonResponse
from django.conf import settings
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from .models import Meetings
from tasks.models import Contact
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated



# Helper function to send email notifications
def send_meeting_notification(meeting, action, old_datetime=None):
    try:
        participants = meeting.participants.all()
        recipient_emails = [contact.email for contact in participants if contact.email]
        
        if not recipient_emails:
            print(f"No email recipients for meeting {meeting.id}")
            return
        
        meeting_datetime = timezone.localtime(meeting.date_time).strftime("%d %b %Y, %I:%M %p")
        
    
        if action == 'created':
            subject = f"Meeting Created: {meeting.title}"
            if old_datetime:  
                if timezone.is_aware(old_datetime):
                    old_time = timezone.localtime(old_datetime).strftime("%d %b %Y, %I:%M %p")
                else:
                    old_time = old_datetime.strftime("%d %b %Y, %I:%M %p")
                message = f"Meeting '{meeting.title}' rescheduled from {old_time} to {meeting_datetime}."
            else:
                message = f"Meeting '{meeting.title}' scheduled for {meeting_datetime}."
                
        elif action == 'updated':
            subject = f"Meeting Updated: {meeting.title}"
            message = f"Meeting '{meeting.title}' updated. New time: {meeting_datetime}."
            
        elif action == 'cancelled':
            subject = f"Meeting Cancelled: {meeting.title}"
            message = f"Meeting '{meeting.title}' scheduled for {meeting_datetime} has been cancelled."
        
        if meeting.location:
            message += f" Location: {meeting.location}."
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER, 
            recipient_list=recipient_emails,
            fail_silently=True  
        )
        
        print(f"Email sent to {len(recipient_emails)} participants for meeting {meeting.id}")
        
    except Exception as e:
        print(f"Failed to send email notification: {e}")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_meetings(request):
    try:
        meetings = Meetings.objects.all().order_by('date_time')
        
        meetings_data = []
        for meeting in meetings:
            participant_ids = list(meeting.participants.values_list('id', flat=True))
            
            user_contact = Contact.objects.filter(email=request.user.email).first()
            if user_contact and user_contact.id not in participant_ids:
                participant_ids.append('current_user')
            
            meetings_data.append({
                'id': meeting.id,
                'title': meeting.title,
                'description': meeting.description,
                'date_time': meeting.date_time.isoformat(),
                'duration': meeting.duration,
                'location': meeting.location,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'deal': meeting.deal_id,
                'deal_title': meeting.deal.title if meeting.deal else None,
                'company': meeting.company_id,
                'company_name': meeting.company.name if meeting.company else None,
                'participants': participant_ids,
                'created_at': meeting.created_at,
                'updated_at': meeting.updated_at,
                'is_upcoming': meeting.is_upcoming
            })
        
        print(f"Returning {len(meetings_data)} meetings")
        return JsonResponse(meetings_data, safe=False)
        
    except Exception as e:
        print(f"Error getting meetings: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_meeting(request, id):
    try:
        meeting = Meetings.objects.get(id=id)
    
        participant_ids = list(meeting.participants.values_list('id', flat=True))
        
        meeting_data = {
            'id': meeting.id,
            'title': meeting.title,
            'description': meeting.description,
            'date_time': meeting.date_time.isoformat(),
            'duration': meeting.duration,
            'location': meeting.location,
            'meeting_type': meeting.meeting_type,
            'status': meeting.status,
            'deal': meeting.deal_id,
            'deal_title': meeting.deal.title if meeting.deal else None,
            'company': meeting.company_id,
            'company_name': meeting.company.name if meeting.company else None,
            'participants': participant_ids,
            'created_at': meeting.created_at,
            'updated_at': meeting.updated_at,
            'is_upcoming': meeting.is_upcoming
        }
        
        print(f"Returning meeting: {meeting.id}")
        return JsonResponse(meeting_data)
        
    except Meetings.DoesNotExist:
        print(f"Meeting {id} not found")
        return JsonResponse({"success": False, "error": "Meeting not found"}, status=404)
    except Exception as e:
        print(f"Error getting meeting: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create(request):
    try:
        user = request.user
        data = json.loads(request.body)
        
        print(f"User: {user.email}")
        print(f"Data: {data}")
        
        date_time_str = data['date_time']
        
        naive_datetime = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
        
        aware_datetime = timezone.make_aware(naive_datetime)
        
        meeting = Meetings.objects.create(
            title=data['title'],
            description=data.get('description', ''),
            date_time=aware_datetime,
            duration=data['duration'],
            location=data.get('location', ''),
            meeting_type=data['meeting_type'],
            status=data['status'],
            deal_id=data.get('deal'),
            company_id=data.get('company')
        )
        
        print(f"Meeting created: {meeting.id}")
        
        user_contact = Contact.objects.filter(email=user.email).first()
        
        participant_ids = data.get('participants', [])
        
        if user_contact and user_contact.id not in participant_ids:
            participant_ids.append(user_contact.id)
            print(f"Added user: {user_contact.id}")
       
        valid_ids = [pid for pid in participant_ids if isinstance(pid, int)]
       
        if valid_ids:
            meeting.participants.set(valid_ids)
            print(f"Participants set: {valid_ids}")
       
        send_meeting_notification(meeting, 'created')
        
        print(f"Success!")
        
        return JsonResponse({
            "success": True, 
            "message": "Meeting created",
            "meeting_id": meeting.id
        })
        
    except KeyError as e:
        print(f"Missing field: {e}")
        return JsonResponse({"success": False, "error": f"Missing {e}"}, status=400)
        
    except json.JSONDecodeError:
        print("Invalid JSON")
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update(request, id):
    try:
        user = request.user
        data = json.loads(request.body)
        
        print(f"UPDATE - User: {user.email}")
        print(f"Meeting ID: {id}")
        print(f"Data: {data}")
        
        meeting = Meetings.objects.get(id=id)
      
        old_datetime = meeting.date_time if 'date_time' in data else None
        
        if 'title' in data:
            meeting.title = data['title']
        if 'description' in data:
            meeting.description = data.get('description', '')
        if 'date_time' in data:
            # Convert string date_time to timezone-aware datetime
            date_time_str = data['date_time']
            naive_datetime = datetime.fromisoformat(date_time_str.replace('Z', '+00:00'))
            aware_datetime = timezone.make_aware(naive_datetime)
            meeting.date_time = aware_datetime
        if 'duration' in data:
            meeting.duration = data['duration']
        if 'location' in data:
            meeting.location = data.get('location', '')
        if 'meeting_type' in data:
            meeting.meeting_type = data['meeting_type']
        if 'status' in data:
            meeting.status = data['status']
        if 'deal' in data:
            meeting.deal_id = data['deal']
        if 'company' in data:
            meeting.company_id = data['company']
        
        meeting.save()
        print(f"Meeting updated: {meeting.id}")
        
        
        if 'participants' in data:
            participant_ids = data['participants']
            
            user_contact = Contact.objects.filter(email=user.email).first()
            
            if user_contact and user_contact.id not in participant_ids:
                participant_ids.append(user_contact.id)
                print(f"Added user to participants: {user_contact.id}")
            
            valid_ids = [pid for pid in participant_ids if isinstance(pid, int)]
            
            meeting.participants.set(valid_ids)
            print(f"Updated participants: {valid_ids}")
        
        if old_datetime and 'date_time' in data:
            send_meeting_notification(meeting, 'created', old_datetime)
        else:
            send_meeting_notification(meeting, 'updated')
        
        print(f"Update successful!")
        
        return JsonResponse({
            "success": True, 
            "message": "Meeting updated",
            "meeting_id": meeting.id
        })
        
    except Meetings.DoesNotExist:
        print(f"Meeting {id} not found")
        return JsonResponse({"success": False, "error": "Meeting not found"}, status=404)
    except Exception as e:
        print(f"Update error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete(request, id):
    try:
        meeting = Meetings.objects.get(id=id)
        
        print(f"DELETE - Meeting: {meeting.id} - {meeting.title}")
        
        send_meeting_notification(meeting, 'cancelled')
        meeting.status = 'cancelled'
        meeting.save()
        
        print(f"Meeting cancelled: {meeting.id}")
        
        return JsonResponse({
            "success": True, 
            "message": "Meeting cancelled"
        })
        
    except Meetings.DoesNotExist:
        print(f"Meeting {id} not found")
        return JsonResponse({"success": False, "error": "Meeting not found"}, status=404)
    except Exception as e:
        print(f"Delete error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def today_count(request):
    try:
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        count = Meetings.objects.filter(
            date_time__gte=today_start,
            date_time__lt=today_end,
            status='scheduled'
        ).count()
        
        print(f"Today's meetings count: {count}")
        
        return JsonResponse({
            "success": True,
            "count": count,
            "date": today_start.date().isoformat()
        })
        
    except Exception as e:
        print(f"Today count error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_meetings(request):
    try:
        deal_id = request.GET.get('deal')
        company_id = request.GET.get('company')
        status = request.GET.get('status')
    
        meetings_qs = Meetings.objects.all()
      
        if deal_id:
            meetings_qs = meetings_qs.filter(deal_id=deal_id)
        if company_id:
            meetings_qs = meetings_qs.filter(company_id=company_id)
        if status:
            meetings_qs = meetings_qs.filter(status=status)
       
        meetings_qs = meetings_qs.order_by('date_time')
        
        meetings_data = []
        for meeting in meetings_qs:
            participant_ids = list(meeting.participants.values_list('id', flat=True))
            
            meetings_data.append({
                'id': meeting.id,
                'title': meeting.title,
                'date_time': meeting.date_time.isoformat(),
                'duration': meeting.duration,
                'meeting_type': meeting.meeting_type,
                'status': meeting.status,
                'deal': meeting.deal_id,
                'company': meeting.company_id,
                'participants': participant_ids
            })
        
        print(f"Filtered meetings: {len(meetings_data)} results")
        return JsonResponse(meetings_data, safe=False)
        
    except Exception as e:
        print(f"Filter error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)