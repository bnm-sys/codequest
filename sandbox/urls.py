# sandbox/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SandboxSessionViewSet

router = DefaultRouter()
router.register(r'sessions', SandboxSessionViewSet, basename='sandbox-session')

urlpatterns = [
    path('api/', include(router.urls)),
]

