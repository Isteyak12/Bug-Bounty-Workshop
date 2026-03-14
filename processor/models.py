import secrets

from django.db import models
from django.contrib.auth.models import User


class ImageUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original = models.ImageField(upload_to="uploads/")
    processed = models.ImageField(upload_to="processed/", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, blank=True, default="Untitled")
    is_public = models.BooleanField(default=False)
    share_token = models.CharField(max_length=12, blank=True, null=True, unique=True)
    view_count = models.IntegerField(default=0)
    batch = models.ForeignKey(
        "BatchJob", on_delete=models.SET_NULL, null=True, blank=True, related_name="images"
    )

    def save(self, *args, **kwargs):
        if self.is_public and not self.share_token:
            self.share_token = self._generate_unique_token()
        super().save(*args, **kwargs)

    def _generate_unique_token(self):
        while True:
            token = secrets.token_hex(6)
            if not ImageUpload.objects.filter(share_token=token).exists():
                return token

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.uploaded_at})"


class Preset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="presets")
    name = models.CharField(max_length=100)
    config = models.JSONField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class BatchJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="batch_jobs")
    total_images = models.IntegerField(default=0)
    processed_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batch {self.pk} - {self.user.username} ({self.status})"


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_logs")
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} {self.method} {self.path} @ {self.timestamp}"
