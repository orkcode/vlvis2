from django.urls import path
from qr.views import CardDetailView, GenerateQRCodeImageView, AddMediaFileView, SetPasswordView, ChangePasswordView

urlpatterns = [
    path('loveyou/<uuid:uuid>/', CardDetailView.as_view(), name='card_detail'),
    path('qr-code/<uuid:uuid>/', GenerateQRCodeImageView.as_view(), name='generate_qr_code'),
]