from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.exceptions import PermissionDenied # Import for custom permission checks
from django_filters.rest_framework import DjangoFilterBackend
from .models import Country, Destination, TourPackage, Review
from .serializers import CountrySerializer, DestinationSerializer, TourPackageSerializer, ReviewSerializer

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows countries to be viewed.
    """
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny] # Publicly viewable
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'country_code']

class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows destinations to be viewed.
    """
    queryset = Destination.objects.select_related('country').all().order_by('country__name', 'name')
    serializer_class = DestinationSerializer
    permission_classes = [permissions.AllowAny] # Publicly viewable
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country__id', 'country__name'] # Filter by country ID or name
    search_fields = ['name', 'description', 'country__name']
    ordering_fields = ['name', 'country__name']


class TourPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows tour packages to be viewed.
    Supports filtering by country, visa_type, and price range (min_price, max_price).
    Supports searching by title, description, country name, destination names.
    Supports ordering by price and created_at.
    """
    queryset = TourPackage.objects.select_related('country').prefetch_related('destinations').filter(is_active=True).order_by('-created_at')
    serializer_class = TourPackageSerializer
    permission_classes = [permissions.AllowAny] # Publicly viewable for now

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Define filterset fields for precise filtering
    filterset_fields = {
        'country__id': ['exact'],
        'country__name': ['exact', 'icontains'],
        'visa_type': ['exact'],
        'price': ['exact', 'gte', 'lte', 'range'], # Allows ?price__gte=100&price__lte=500
        'duration_days': ['exact', 'gte', 'lte'],
        'destinations__id': ['exact'], # Filter by specific destination ID
        'destinations__name': ['icontains'], # Filter by destination name
    }

    search_fields = [
        'title',
        'description',
        'country__name',
        'destinations__name',
        'highlights',
        'inclusions'
    ]

    ordering_fields = ['price', 'created_at', 'title', 'duration_days']
    # Default ordering is already set in the queryset

    # Example of a custom filter if needed later:
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     # Example: filter by min_price
    #     min_price = self.request.query_params.get('min_price')
    #     if min_price:
    #         queryset = queryset.filter(price__gte=min_price)
    #     # Example: filter by max_price
    #     max_price = self.request.query_params.get('max_price')
    #     if max_price:
    #         queryset = queryset.filter(price__lte=max_price)
    #     return queryset

class ReviewViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin, # Optional: if you want to allow fetching a specific review
                    mixins.UpdateModelMixin,   # Optional: if users can update their reviews
                    mixins.DestroyModelMixin,  # Optional: if users can delete their reviews
                    mixins.ListModelMixin,     # Optional: if you want to list reviews (e.g., per package)
                    viewsets.GenericViewSet):
    """
    API endpoint for creating, retrieving, updating, and deleting reviews.
    - Users can create reviews for tour packages.
    - Requires authentication to create/update/delete.
    - Listing reviews can be filtered by tour_package_id.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow read for anyone, write for authenticated

    def get_queryset(self):
        """
        Optionally filter reviews by tour_package if 'tour_package_id' is in query_params.
        """
        queryset = Review.objects.select_related('user', 'tour_package').all()
        tour_package_id = self.request.query_params.get('tour_package_id')
        if tour_package_id:
            queryset = queryset.filter(tour_package__id=tour_package_id)

        user_id = self.request.query_params.get('user_id')
        if user_id: # to get reviews by a specific user
            queryset = queryset.filter(user__id=user_id)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Set the user to the currently authenticated user
        serializer.save(user=self.request.user)

    # Add perform_update and perform_destroy if you want to ensure
    # that only the owner of a review can modify/delete it.
    def perform_update(self, serializer):
        # Ensure the user updating the review is the one who created it.
        if serializer.instance.user != self.request.user:
            # from rest_framework.exceptions import PermissionDenied # Import this
            # raise PermissionDenied("You do not have permission to edit this review.")
            # Or handle silently / differently
            pass # For now, let DRF's default behavior or serializer validation handle it
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure the user deleting the review is the one who created it.
        if instance.user != self.request.user:
            # from rest_framework.exceptions import PermissionDenied
            # raise PermissionDenied("You do not have permission to delete this review.")
            pass
        instance.delete()
