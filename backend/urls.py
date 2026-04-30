from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("Playto KYC API Running 🚀")

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/v1/', include('kyc.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)