from django import forms
from .models import Card

class CardForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Card
        fields = ['media_file', 'password']
        widgets = {
            'media_file': forms.ClearableFileInput(attrs={'enctype': 'multipart/form-data'}),
        }

    def __init__(self, *args, **kwargs):
        super(CardForm, self).__init__(*args, **kwargs)
        if self.instance and not self.instance.password:
            self.fields.pop('password')

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.instance and self.instance.password and password != self.instance.password:
            self.add_error('password', "Неверный пароль.")
        return password

    def clean_media_file(self):
        media_file = self.cleaned_data.get('media_file')
        if not media_file and not self.instance._state.adding:
            return None
        return media_file


class SetPasswordForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Card
        fields = ['password', 'confirm_password']

    def clean(self):
        cleaned_data = super(SetPasswordForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Пароли не совпадают.")
        return cleaned_data


class ChangePasswordForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Card
        fields = ['password', 'new_password', 'confirm_password']

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        old_password = cleaned_data.get("password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            self.add_error('confirm_password', "Новые пароли не совпадают.")

        if old_password != self.instance.password:
            self.add_error('password', "Старый пароль неверен.")
        return cleaned_data