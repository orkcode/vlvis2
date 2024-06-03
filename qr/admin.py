from django.contrib import admin
from .models import Card
import qrcode
from django.http import HttpResponse
from zipfile import ZipFile
from io import BytesIO
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from qr.tasks import create_cards_task

@admin.action(description='Скачать QR коды')
def create_cards(modeladmin, request, queryset):
    buffer = BytesIO()
    with ZipFile(buffer, 'w') as zip_file:
        for card in queryset:
            card.is_active = True
            card.save()
            url = request.build_absolute_uri(reverse('card_detail', args=[card.uuid]))
            qr = qrcode.make(url)
            qr_io = BytesIO()
            qr.save(qr_io, 'PNG')
            qr_io.seek(0)
            zip_file.writestr(f"QR_{card.id}.png", qr_io.read())
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.zip"'
    return response

class CardCreationForm(forms.Form):
    number_of_cards = forms.IntegerField(label="Кол-во новых открыток", min_value=1)

@admin.action(description='Сделать активными')
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
    modeladmin.message_user(request, "Выбранные карты были успешно активированы.")

@admin.action(description='Сделать неактивными')
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
    modeladmin.message_user(request, "Выбранные карты были успешно деактивированы.")

class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'is_active')
    actions = [create_cards, 'create_multiple_cards', make_active, make_inactive]

    def create_multiple_cards(self, request, queryset):
        if not queryset:
            self.message_user(request, "No cards selected.", level='error')
            return HttpResponseRedirect(request.get_full_path())

        if request.POST.get('apply'):
            form = CardCreationForm(request.POST)
            if form.is_valid():
                number_of_cards = form.cleaned_data['number_of_cards']
                task = create_cards_task.delay(number_of_cards)
                self.message_user(request, f"Task {task.id} to create {number_of_cards} cards has been started.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        self.message_user(request, f"{form[field].label}: {error}", level='error')
        else:
            form = CardCreationForm(initial={'_create_multiple_cards': 'yes'})

        context = {
            'form': form,
            'title': 'Массовое создание открыток',
            'queryset': queryset,
            'opts': self.model._meta,
            'media': self.media,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return render(request, 'admin/create_multiple_cards.html', context)

    create_multiple_cards.short_description = "Массовое создание открыток"

admin.site.register(Card, CardAdmin)