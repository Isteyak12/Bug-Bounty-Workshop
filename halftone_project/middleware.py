from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta

from processor.models import ActivityLog


class ActivityLogMiddleware:
    """Log all authenticated user activity."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            ActivityLog.objects.create(
                user=request.user,
                path=request.path,
                method=request.method,
                status_code=response.status_code,
            )

        return response


class RateLimitMiddleware:
    """Rate-limit uploads to prevent abuse."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == "POST"
            and request.user.is_authenticated
            and request.path == "/"
        ):
            window = timezone.now() - timedelta(
                minutes=getattr(settings, "RATE_LIMIT_WINDOW", 5)
            )
            # Count this user's recent uploads
            user_upload_count = ActivityLog.objects.filter(
                user=request.user,
                path="/",
                method="POST",
                timestamp__gte=window,
            ).count()

            max_uploads = getattr(settings, "RATE_LIMIT_UPLOADS", 10)
            profile = getattr(request.user, "profile", None)
            if profile is not None and profile.max_uploads > 0:
                max_uploads = profile.max_uploads
            if user_upload_count >= max_uploads:
                return HttpResponse(
                    "Rate limit exceeded. Try again later.", status=429
                )

        return self.get_response(request)
