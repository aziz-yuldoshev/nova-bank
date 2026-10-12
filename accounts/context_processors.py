from .models import Notification


def notifications_context(request):
    if request.user.is_authenticated:

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        return {
            "unread_notifications": notifications.filter(
                is_read=False
            ).count(),

            "recent_notifications": notifications[:5],
        }

    return {
        "unread_notifications": 0,
        "recent_notifications": [],
    }