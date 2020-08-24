from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('index/', include('SongFound.urls')),
    path('index/results/', include('SongFound.urls')),
    path('admin/', admin.site.urls),
]
