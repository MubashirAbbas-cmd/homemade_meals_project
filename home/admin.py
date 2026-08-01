from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem, PageSectionImage


class PageSectionImageForm(forms.ModelForm):
    class Meta:
        model = PageSectionImage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_sections = set(
            PageSectionImage.objects.exclude(pk=self.instance.pk if self.instance.pk else None)
            .filter(section__in=PageSectionImage.SINGLE_IMAGE_SECTIONS)
            .values_list('section', flat=True)
        )
        allowed_choices = []
        for value, label in self.fields['section'].choices:
            if value in PageSectionImage.SINGLE_IMAGE_SECTIONS and value in existing_sections:
                continue
            allowed_choices.append((value, label))
        self.fields['section'].choices = allowed_choices
        self.fields['section'].help_text = (
            'Choose a section for this image. Hero, About, and Showcase sections each allow only one image. '
            'Gallery images can have many uploads.'
        )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'quantity', 'food')


@admin.register(PageSectionImage)
class PageSectionImageAdmin(admin.ModelAdmin):
    form = PageSectionImageForm
    list_display = ('section', 'caption', 'sort_order', 'section_note', 'image_preview')
    list_filter = ('section',)
    search_fields = ('caption',)
    readonly_fields = ('image_preview',)
    ordering = ('section', 'sort_order')
    fieldsets = (
        (None, {
            'fields': ('section', 'image', 'caption', 'sort_order', 'image_preview'),
            'description': 'Use one image for hero, about, and showcase sections. Gallery allows many images.'
        }),
    )

    def section_note(self, obj):
        if obj.section == PageSectionImage.SECTION_GALLERY:
            return 'Gallery uploads are unlimited.'
        return 'Single image only for this section.'
    section_note.short_description = 'Section note'

    def image_preview(self, obj):
        if not obj.pk or not obj.image:
            return '-'
        return format_html(
            '<img src="{}" style="max-height: 120px; max-width: 240px; object-fit: contain;" />',
            obj.image.url
        )
    image_preview.short_description = 'Preview'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'customer_name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'user__username')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
