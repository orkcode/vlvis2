from io import BytesIO
from PIL import Image
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from moviepy.editor import VideoFileClip
import os
import tempfile
import mimetypes


def compress_media_file(media_file):
    try:
        if media_file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            # Сжатие изображения
            image = Image.open(media_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            media_file.file = output

        elif media_file.name.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(media_file.file.read())
                temp_file_path = temp_file.name

            # Сжатие видео
            video = VideoFileClip(temp_file_path)
            if video.duration > 150:  # Ограничение длительности видео 2,5 минутами
                video = video.subclip(0, 150)

            output_file_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as output_file:
                    output_file_path = output_file.name
                    video.write_videofile(output_file_path, codec='libx264', audio_codec='aac',
                                          temp_audiofile='temp-audio.m4a', remove_temp=True)

                with open(output_file_path, 'rb') as output_file:
                    media_file.file = BytesIO(output_file.read())
            finally:
                if temp_file_path:
                    os.remove(temp_file_path)
                if output_file_path:
                    os.remove(output_file_path)

    except Exception as e:
        # Обработка ошибок
        print(f"Ошибка при сжатии файла {media_file.name}: {e}")