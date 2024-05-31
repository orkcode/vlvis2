from django.views.generic import DetailView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
from .models import Card
from .forms import CardForm, SetPasswordForm, ChangePasswordForm
import qrcode
from io import BytesIO


class GenerateQRCodeImageView(View):
    def get(self, request, *args, **kwargs):
        card = get_object_or_404(Card, uuid=self.kwargs['uuid'])
        url = request.build_absolute_uri(reverse('card_detail', args=[card.uuid]))

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer, content_type='image/png')


class CardDetailView(View):
    def get(self, request, *args, **kwargs):
        card = get_object_or_404(Card, uuid=self.kwargs['uuid'])
        context = {
            'card': card,
            'media_file_form': CardForm(instance=card),
            'set_password_form': SetPasswordForm(),
            'change_password_form': ChangePasswordForm(),
            'form_type': ''
        }
        return render(request, 'card_detail.html', context)

    def post(self, request, *args, **kwargs):
        card = get_object_or_404(Card, uuid=self.kwargs['uuid'])
        form_type = request.POST.get('form_type', '')
        if form_type == 'add_media':
            media_file_form = CardForm(request.POST, request.FILES, instance=card)
            if media_file_form.is_valid():
                card.media_file = media_file_form.cleaned_data['media_file']
                card.save()
                return redirect('card_detail', uuid=card.uuid)
            set_password_form = SetPasswordForm()
            change_password_form = ChangePasswordForm()
        elif form_type == 'set_password':
            set_password_form = SetPasswordForm(request.POST)
            if set_password_form.is_valid():
                card.password = set_password_form.cleaned_data['password']
                card.save()
                return redirect('card_detail', uuid=card.uuid)
            media_file_form = CardForm()
            change_password_form = ChangePasswordForm()
        elif form_type == 'change_password':
            change_password_form = ChangePasswordForm(request.POST, instance=card)
            if change_password_form.is_valid():
                card.password = change_password_form.cleaned_data['new_password']
                card.save()
                return redirect('card_detail', uuid=card.uuid)
            media_file_form = CardForm()
            set_password_form = SetPasswordForm()
        else:
            media_file_form = CardForm()
            set_password_form = SetPasswordForm()
            change_password_form = ChangePasswordForm()

        context = {
            'card': card,
            'media_file_form': media_file_form,
            'set_password_form': set_password_form,
            'change_password_form': change_password_form,
            'form_type': form_type
        }
        return render(request, 'card_detail.html', context)


class AddMediaFileView(View):
    def post(self, request, *args, **kwargs):
        card = get_object_or_404(Card, uuid=self.kwargs['uuid'])
        form = CardForm(request.POST, request.FILES)
        if form.is_valid():
            card.media_file = form.cleaned_data['media_file']
            card.save()
        return redirect('card_detail', uuid=card.uuid)


class SetPasswordView(View):
    def get(self, request, *args, **kwargs):
        return redirect('card_detail', uuid=self.kwargs['uuid'])

    def post(self, request, *args, **kwargs):
        card = get_object_or_404(Card, uuid=self.kwargs['uuid'])
        form = SetPasswordForm(request.POST)
        if form.is_valid() and form.cleaned_data['password'] == form.cleaned_data['confirm_password']:
            card.password = form.cleaned_data['password']
            card.save()
            return redirect('card_detail', uuid=card.uuid)
        else:
            context = {
                'card': card,
                'media_file_form': CardForm(),
                'set_password_form': form,
                'change_password_form': ChangePasswordForm()
            }
            return render(request, 'card_detail.html', context)


class ChangePasswordView(View):
    def get(self, request, *args, **kwargs):
        return redirect('card_detail', uuid=self.kwargs['uuid'])
    def post(self, request, *args, **kwargs):
        card = get_object_or_404(Card, uuid=self.kwargs['uuid'])
        form = ChangePasswordForm(request.POST, instance=card)
        if form.is_valid() and card.password == form.cleaned_data['password'] and form.cleaned_data['new_password'] == form.cleaned_data['confirm_password']:
            card.password = form.cleaned_data['new_password']
            card.save()
            return redirect('card_detail', uuid=card.uuid)
        else:
            context = {
                'card': card,
                'media_file_form': CardForm(),
                'set_password_form': SetPasswordForm(),
                'change_password_form': form
            }
            return render(request, 'card_detail.html', context)