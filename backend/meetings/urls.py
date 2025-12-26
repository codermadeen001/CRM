# urls.py
from django.urls import path
from .views import (
    create, get_all_meetings, get_meeting, 
    update, delete, today_count, filter_meetings
)

urlpatterns = [
    path("create/", create, name="meeting_create"),
    path("", get_all_meetings, name="meetings_list"),
    path("<int:id>/", get_meeting, name="meeting_detail"),
    path("update/<int:id>/", update, name="meeting_update"),
    path("delete/<int:id>/", delete, name="meeting_delete"),
    path("today/count/", today_count, name="today_meetings_count"),
    path("filter/", filter_meetings, name="meetings_filter"),
]