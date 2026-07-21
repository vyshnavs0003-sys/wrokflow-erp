from django.contrib import admin
from .models import Announcement, Notification

# Register your models here.

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "created_by",
        "target_department",
        "priority",
        "publish_date",
        "expiry_date",
        "is_active",
    )

    search_fields = (
        "title",
        "message",
        "created_by__employee_id",
    )

    list_filter = (
        "priority",
        "target_department",
        "is_active",
    )

    ordering = (
        "-publish_date",
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "recipient",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )

    search_fields = (
        "recipient__employee_id",
        "title",
        "message",
    )

    list_filter = (
        "notification_type",
        "is_read",
    )

    ordering = (
        "-created_at",
    )