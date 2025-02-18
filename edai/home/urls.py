from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_pdf, name='upload_pdf'),
    path('add-dictionary/', views.add_dictionary, name='add_dictionary'),
    path('download/<str:filename>/', views.download_pdf, name='download_pdf'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)