import os

from django.conf import settings

from .models import BatchJob, ImageUpload
from .halftone import apply_halftone


def process_batch(batch_id):
    """Process all images in a batch job."""
    batch = BatchJob.objects.get(pk=batch_id)
    batch.status = "processing"
    batch.processed_count = 0
    batch.save(update_fields=["status", "processed_count"])

    images = ImageUpload.objects.filter(batch=batch)
    image_count = images.count()
    if batch.total_images != image_count:
        batch.total_images = image_count
        batch.save(update_fields=["total_images"])

    if image_count == 0:
        batch.status = "failed"
        batch.save(update_fields=["status"])
        return

    success_count = 0
    for upload in images:
        try:
            original_path = upload.original.path
            filename = f"halftone_{upload.pk}.png"
            output_path = os.path.join(settings.MEDIA_ROOT, "processed", filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            apply_halftone(original_path, output_path)

            upload.processed = f"processed/{filename}"
            upload.save()

            success_count += 1
            batch.processed_count = success_count
            batch.save(update_fields=["processed_count"])
        except Exception:
            continue

    batch.status = "completed" if success_count == batch.total_images else "failed"
    batch.save(update_fields=["status"])
