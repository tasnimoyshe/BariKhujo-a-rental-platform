from django.contrib import admin
from .models import Property, PropertyImage

# অ্যাডমিন প্যানেলে প্রপার্টির নিচেই যেন ছবি আপলোডের এক্সট্রা ঘর থাকে
class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3  # ডিফল্টভাবে ৩টি ছবি আপলোড করার খালি ঘর দেখাবে

class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]

admin.site.register(Property, PropertyAdmin)