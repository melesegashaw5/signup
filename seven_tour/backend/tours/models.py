from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
# from users.models import CustomUser # If we need to link packages to users (e.g. created_by)

def tour_package_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/tours/package_images/<package_id>/<filename>
    return f'tours/package_images/{instance.id}/{filename}'

class Country(models.Model):
    name = models.CharField(_("country name"), max_length=100, unique=True)
    country_code = models.CharField(_("country code"), max_length=3, blank=True, null=True, help_text=_("Optional ISO 3166-1 alpha-2 code"))
    # Add other relevant fields like continent, flag image, etc. later if needed

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ['name']

    def __str__(self):
        return self.name

class Destination(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='destinations')
    name = models.CharField(_("destination name"), max_length=200)
    description = models.TextField(_("description"), blank=True, null=True)
    # image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    # Add other fields like latitude, longitude, etc. later if needed

    class Meta:
        verbose_name = _("Destination")
        verbose_name_plural = _("Destinations")
        unique_together = ('country', 'name') # A destination name should be unique within a country
        ordering = ['country__name', 'name']


    def __str__(self):
        return f"{self.name}, {self.country.name}"

class TourPackage(models.Model):
    class VisaTypeChoices(models.TextChoices):
        VISA_FREE = 'VISA_FREE', _('Visa Free')
        E_VISA = 'E_VISA', _('E-Visa')
        ON_ARRIVAL = 'ON_ARRIVAL', _('On Arrival')
        STICKER_VISA = 'STICKER_VISA', _('Sticker Visa')
        # Add more if needed, or make this a ForeignKey to a separate VisaType model
        # if visa types need more attributes or admin management.

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))

    # Relationships
    # A tour package is typically for one primary country, but might cover multiple destinations.
    # If a package can span multiple countries, this might need to be ManyToManyField.
    # For simplicity now, one primary country.
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL, # Or PROTECT if a country shouldn't be deleted if it has packages
        null=True, blank=True, # Package might be general or country not yet set
        related_name='tour_packages'
    )
    # A package can have multiple destinations.
    destinations = models.ManyToManyField(
        Destination,
        related_name='tour_packages',
        blank=True # A package might not have specific destinations initially, or be country-wide
    )

    visa_type = models.CharField(
        _("visa type"),
        max_length=20,
        choices=VisaTypeChoices.choices,
        default=VisaTypeChoices.STICKER_VISA # Or some other sensible default
    )

    price = models.DecimalField(_("price"), max_digits=10, decimal_places=2, help_text=_("Price in ETB or a common currency"))

    highlights = models.TextField(_("highlights"), help_text=_("Short bullet points or key features, one per line."), blank=True)
    inclusions = models.TextField(_("inclusions"), help_text=_("What is included in the package, one per line."), blank=True)
    exclusions = models.TextField(_("exclusions"), help_text=_("What is NOT included in the package, one per line."), blank=True) # Added exclusions

    # Duration (e.g., "7 Days / 6 Nights")
    duration_days = models.PositiveIntegerField(_("duration in days"), null=True, blank=True)

    # Main image for the package
    main_image = models.ImageField(
        _("main image"),
        upload_to=tour_package_image_path,
        null=True,
        blank=True
    )

    # Capacity, availability, etc. can be added later
    is_active = models.BooleanField(_("is active"), default=True, help_text=_("Is this package currently available for booking?"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_packages')

    class Meta:
        verbose_name = _("Tour Package")
        verbose_name_plural = _("Tour Packages")
        ordering = ['-created_at', 'title']

    def __str__(self):
        return self.title

class Review(models.Model):
    tour_package = models.ForeignKey(
        TourPackage,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        # Use settings.AUTH_USER_MODEL to avoid circular import if Review was in users app
        # Since it's in tours app, direct import is fine if users app is loaded first or use string
        'users.CustomUser',
        on_delete=models.CASCADE, # Or SET_NULL if reviews should persist if user is deleted
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        _("rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("Rating from 1 to 5 stars")
    )
    comment = models.TextField(_("comment"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = ('tour_package', 'user') # User can only review a package once
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.email} for {self.tour_package.title} ({self.rating} stars)"
