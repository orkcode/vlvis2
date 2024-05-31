import os
import tempfile
from moviepy.editor import VideoFileClip
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_video_duration(file):
    # Проверка, является ли загруженный файл видео
    if file.name.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
        # Использование tempfile для создания временного файла
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name

        video = VideoFileClip(temp_path)
        duration = video.duration
        if duration > 150:  # 2.5 минут = 150 секунд
            raise ValidationError(
                _('Видео должно быть не более 2.5 минут'),
                code='invalid'
            )
        video.reader.close()
        video.audio.reader.close_proc()
        os.remove(temp_path)
