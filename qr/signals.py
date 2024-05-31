from django.dispatch import receiver
from django.db.models.signals import pre_save
from qr.models import Card
from qr.tasks import compress_media_file_task


@receiver(pre_save, sender=Card)
def compress_media_signal(sender, instance, **kwargs):
    if instance.media_file:
        compress_media_file_task.delay(instance.uuid)