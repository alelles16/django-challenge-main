from django.urls import path, include
from rest_framework.routers import DefaultRouter

from booking import views


router = DefaultRouter()
router.register('bookings', views.BookingViewSet)

app_name = 'booking'

urlpatterns = [
    path('', include(router.urls)),
]
