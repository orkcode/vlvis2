import os
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from qr.validators import validate_video_duration


class Card(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    media_file = models.FileField(_("Медиафайл"), upload_to='media/',
                                  validators=[
                                      FileExtensionValidator(allowed_extensions=[
                                          'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',  # Изображение
                                          'mp4', 'avi', 'mkv', 'mov'  # Видео
                                      ]),
                                      validate_video_duration
                                  ],
                                  help_text=_('Загрузите файл изображения или видео (не более 2,5 минут)'),
                                  blank=True, null=True)
    password = models.CharField(_("Пароль"), max_length=128, blank=True, null=True)

    class Meta:
        verbose_name = _("Карточка")
        verbose_name_plural  =  _("Карточки")

    def __str__(self):
        return str(self.uuid)

    def is_video(self):
        _, ext = os.path.splitext(self.media_file.name)
        return ext.lower() in ['.mp4', '.mov', '.avi', '.wmv']

    def is_image(self):
        _, ext = os.path.splitext(self.media_file.name)
        return ext.lower() in ['.jpg', '.jpeg', '.png', '.gif']
