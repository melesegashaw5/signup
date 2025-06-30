from rest_framework import serializers
from .models import Country, Destination, TourPackage, Review
from users.models import CustomUser # For user context in ReviewSerializer

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'country_code']

class DestinationSerializer(serializers.ModelSerializer):
    # Optionally include country details if needed, or just the ID
    # country = CountrySerializer(read_only=True) # If you want nested details
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source='country')
    country_name = serializers.CharField(source='country.name', read_only=True)


    class Meta:
        model = Destination
        fields = ['id', 'name', 'description', 'country_id', 'country_name']

class TourPackageSerializer(serializers.ModelSerializer):
    # To show names instead of IDs for ForeignKey and ManyToMany fields in responses
    country = CountrySerializer(read_only=True)
    destinations = DestinationSerializer(many=True, read_only=True)

    # For writing, allow IDs to be passed
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source='country', write_only=True, allow_null=True, required=False
    )
    destination_ids = serializers.PrimaryKeyRelatedField(
        queryset=Destination.objects.all(), source='destinations', write_only=True, many=True, required=False
    )

    # Make visa_type human-readable in GET requests
    visa_type_display = serializers.CharField(source='get_visa_type_display', read_only=True)

    class Meta:
        model = TourPackage
        fields = [
            'id', 'title', 'description', 'country', 'destinations',
            'visa_type', 'visa_type_display', 'price', 'highlights', 'inclusions', 'exclusions',
            'duration_days', 'main_image', 'is_active',
            'created_at', 'updated_at',
            # Write-only fields for linking by ID
            'country_id', 'destination_ids'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # DRF handles ManyToMany relationships with PrimaryKeyRelatedField correctly
        # if 'destinations' (the source of destination_ids) is in validated_data.
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    # Alternatively, to show user email (read-only):
    # user_email = serializers.EmailField(source='user.email', read_only=True)

    tour_package_id = serializers.PrimaryKeyRelatedField(
        queryset=TourPackage.objects.all(), source='tour_package', write_only=True
    )
    # To show package title (read-only) if listing reviews:
    # tour_package_title = serializers.CharField(source='tour_package.title', read_only=True)


    class Meta:
        model = Review
        fields = [
            'id', 'user', 'tour_package_id', # 'tour_package_title', 'user_email',
            'rating', 'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Check that the user has not already reviewed this package.
        DRF's UniqueTogetherValidator handles this if 'user' is part of validated_data.
        If user is set via CurrentUserDefault, it's not in 'data' initially.
        So, we might need to do this check manually if user is not part of the unique_together check
        at the serializer level because it's being defaulted.
        However, the model's unique_together constraint should catch this at DB level.
        For a cleaner API error, we can check here.
        """
        request_user = self.context['request'].user
        tour_package = data.get('tour_package') # This is the TourPackage instance after PKRelatedField

        if tour_package and request_user.is_authenticated:
            if Review.objects.filter(tour_package=tour_package, user=request_user).exists():
                # This check is for creating new reviews. For updates, it might be different.
                # Since this is a "stub" and likely create-only for now, this is fine.
                if not self.instance: # If creating new
                     raise serializers.ValidationError(
                        _("You have already reviewed this tour package.")
                    )
                # If updating, and the user or package hasn't changed, allow.
                # This logic might get complex if user/package can be changed on update.
                elif self.instance and (self.instance.user != request_user or self.instance.tour_package != tour_package) :
                     raise serializers.ValidationError(
                        _("You have already reviewed this tour package (on update attempt with different user/package).")
                    )

        # Validate rating is within 1-5 (already handled by model validators, but good for early feedback)
        rating = data.get('rating')
        if rating is not None and not (1 <= rating <= 5):
            raise serializers.ValidationError(_("Rating must be between 1 and 5."))

        return data
