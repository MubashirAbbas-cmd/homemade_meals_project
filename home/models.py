from django.conf import settings
from django.db import models

from food.models import Food


class PageSectionImage(models.Model):
    SECTION_HERO_BACKGROUND = 'hero_background'
    SECTION_HERO_FEATURE = 'hero_feature'
    SECTION_ABOUT_STORY = 'about_story'
    SECTION_SHOWCASE = 'showcase'
    SECTION_GALLERY = 'gallery'

    SECTION_CHOICES = [
        (SECTION_HERO_BACKGROUND, 'Hero background'),
        (SECTION_HERO_FEATURE, 'Hero featured image'),
        (SECTION_ABOUT_STORY, 'About section image'),
        (SECTION_SHOWCASE, 'Showcase image'),
        (SECTION_GALLERY, 'Gallery image'),
    ]

    SINGLE_IMAGE_SECTIONS = {
        SECTION_HERO_BACKGROUND,
        SECTION_HERO_FEATURE,
        SECTION_ABOUT_STORY,
        SECTION_SHOWCASE,
    }

    section = models.CharField(max_length=32, choices=SECTION_CHOICES)
    image = models.ImageField(
        upload_to='section_images/',
        help_text='Upload the image for this page section.'
    )
    caption = models.CharField(
        max_length=128,
        blank=True,
        help_text='Optional caption or alt text for the image.'
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text='Lower values appear before higher values when multiple items are allowed.'
    )

    class Meta:
        ordering = ['section', 'sort_order']
        verbose_name = 'Section image'
        verbose_name_plural = 'Section images'
        constraints = [
            models.UniqueConstraint(
                fields=['section'],
                condition=models.Q(
                    section__in=[
                        'hero_background',
                        'hero_feature',
                        'about_story',
                        'showcase',
                    ]
                ),
                name='unique_single_image_section'
            )
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.section in self.SINGLE_IMAGE_SECTIONS:
            existing = PageSectionImage.objects.filter(section=self.section)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError(
                    { 'section': 'Only one image is allowed for this section. Remove the previous image or choose a different section.' }
                )

    def __str__(self):
        return f'{self.get_section_display()} ({self.sort_order})'


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PREPARING = 'preparing'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=128)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.customer_name} ({self.status})'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.food.name if self.food else "Deleted item"} × {self.quantity}'
