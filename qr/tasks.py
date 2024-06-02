from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import get_valid_filename
from django.conf import settings
from qr.models import Card
from moviepy.editor import VideoFileClip
import os
import tempfile
import mimetypes
from celery import shared_task


@shared_task(bind=True)
def compress_media_file_task(self, instance_uuid):
    try:
        instance = Card.objects.get(uuid=instance_uuid)
        original_media_name = os.path.basename(instance.media_file.name)
        valid_media_name = get_valid_filename(original_media_name)

        if instance.media_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            image = Image.open(instance.media_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            img_io = BytesIO()
            image.save(img_io, format='JPEG', quality=85, optimize=True)
            img_io.seek(0)
            new_media = ContentFile(img_io.getvalue(), name=valid_media_name)
            instance.media_file.delete(save=False)

        elif instance.media_file.name.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_video_path = os.path.join(temp_dir, 'temp_video.mp4')
                video = VideoFileClip(instance.media_file.path)
                video.write_videofile(temp_video_path, codec="libx264", audio_codec="aac",
                                      temp_audiofile="temp-audio.m4a", remove_temp=True, audio_bitrate="65k",
                                      bitrate="500k", preset="ultrafast")
                with open(temp_video_path, "rb") as temp_video_file:
                    temp_video_data = temp_video_file.read()
                new_media = ContentFile(temp_video_data, name=valid_media_name)
                instance.media_file.delete(save=False)

        else:
            pass

        instance.media_file.save(new_media.name, new_media, save=False)

    except Exception as e:
        print(f"Ошибка при сжатии файла: {e}")


def get_card_files():
    card_files = set()
    for card in Card.objects.all():
        if card.media_file:
            card_files.add(card.media_file.path)
    return card_files

@shared_task(bind=True)
def delete_unused_files_task(self):
    try:
        upload_dir = settings.MEDIA_ROOT
        card_files = get_card_files()

        if not os.path.exists(upload_dir):
            return

        for root, dirs, files in os.walk(upload_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path not in card_files:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Ошибка при удалении {file_path}: {e}")
    except Exception as e:
        print(f"Ошибка при удалении неиспользуемых файлов: {e}")