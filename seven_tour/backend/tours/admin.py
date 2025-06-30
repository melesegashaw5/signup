from django.contrib import admin
from .models import Country, Destination, TourPackage, Review

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'country_code')
    search_fields = ('name', 'country_code')

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'get_country_name')
    search_fields = ('name', 'country__name')
    list_filter = ('country',)
    autocomplete_fields = ['country'] # For easier selection if many countries

    @admin.display(description='Country Name', ordering='country__name')
    def get_country_name(self, obj):
        return obj.country.name

@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'visa_type', 'price', 'duration_days', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'country__name', 'destinations__name')
    list_filter = ('is_active', 'visa_type', 'country', 'created_at')
    filter_horizontal = ('destinations',) # Better UI for ManyToMany
    autocomplete_fields = ['country'] # For easier selection

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'main_image', 'is_active')
        }),
        ('Location & Visa', {
            'fields': ('country', 'destinations', 'visa_type')
        }),
        ('Details', {
            'fields': ('price', 'duration_days', 'highlights', 'inclusions', 'exclusions')
        }),
        # ('Admin', {
        #     'fields': ('created_by',), # If created_by is added
        #     'classes': ('collapse',), # Keep admin-specific fields less prominent
        # })
    )
    # readonly_fields = ('created_at', 'updated_at') # If you want to show them but not edit

    # If you have many destinations, you might want to use raw_id_fields for 'destinations'
    # raw_id_fields = ('destinations',)

    def save_model(self, request, obj, form, change):
        # if not obj.pk and hasattr(request, 'user') and request.user.is_authenticated:
        #     obj.created_by = request.user # Set created_by if field exists and user is logged in
        super().save_model(request, obj, form, change)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('tour_package_title', 'user_email', 'rating', 'created_at', 'comment_snippet')
    list_filter = ('rating', 'created_at', 'tour_package__title')
    search_fields = ('user__email', 'tour_package__title', 'comment')
    autocomplete_fields = ['tour_package', 'user'] # Makes selection easier

    @admin.display(description='Package Title', ordering='tour_package__title')
    def tour_package_title(self, obj):
        return obj.tour_package.title

    @admin.display(description='User Email', ordering='user__email')
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description='Comment (Snippet)')
    def comment_snippet(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment

    # To make user and tour_package fields read-only during edit, if desired
    # def get_readonly_fields(self, request, obj=None):
    #     if obj: # when editing an object
    #         return ['user', 'tour_package', 'created_at', 'updated_at']
    #     return ['created_at', 'updated_at']
