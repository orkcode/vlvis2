from django.urls import path
from .views import CardDetailView, GenerateQRCodeImageView, AddMediaFileView, SetPasswordView, ChangePasswordView, PrivacyPolicyView, AgreementPolicyView

urlpatterns = [
    path('loveyou/<uuid:uuid>/', CardDetailView.as_view(), name='card_detail'),
    path('qr-code/<uuid:uuid>/', GenerateQRCodeImageView.as_view(), name='generate_qr_code'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
    path('agreement/', AgreementPolicyView.as_view(), name='agreement'),
]
