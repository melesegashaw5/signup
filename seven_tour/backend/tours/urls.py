from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, DestinationViewSet, TourPackageViewSet, ReviewViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'destinations', DestinationViewSet, basename='destination')
router.register(r'packages', TourPackageViewSet, basename='tourpackage')
router.register(r'reviews', ReviewViewSet, basename='review')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
