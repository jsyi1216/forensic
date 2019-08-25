"""forensic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
from apps.tool.views import ModelViewSet, PredictViewSet

router = routers.DefaultRouter()
router.register(r'predict', PredictViewSet, r"predict")
router.register(r'models', ModelViewSet, r"models")

urlpatterns = [
    url(r'^forensic/', include(router.urls))
]
