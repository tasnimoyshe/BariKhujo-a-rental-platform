from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True, help_text="Optional")
    is_verified = models.BooleanField(default=False, help_text="Admin will verify NID/Bills for Blue Tick")
    
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    occupation = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Businessman, Software Engineer")
    facebook_link = models.URLField(max_length=255, blank=True, null=True, help_text="Optional Facebook profile link")

    def __str__(self):
        return f"{self.user.username}'s Profile"

# 2. Main Property Model
class Property(models.Model):
    LISTING_CHOICES = (('Rent', 'For Rent'), ('Sale', 'For Sale'))
    CATEGORY_CHOICES = (('Residential', 'Residential'), ('Commercial', 'Commercial'))
    
    PROPERTY_TYPES = (
        ('Apartment', 'Apartment'), ('House', 'House'), ('Sublet Room', 'Sublet Room'), 
        ('Single Room', 'Single Room'), ('Hostel', 'Hostel'),
        ('Offices', 'Offices'), ('Building', 'Building'), ('Restaurant', 'Restaurant'), 
        ('Factory / Mill', 'Factory / Mill'), ('Commercial', 'Commercial'), 
        ('Warehouse', 'Warehouse'), ('Shop', 'Shop'), ('Garage', 'Garage'), ('Hotel', 'Hotel'),
        ('Other', 'Other')
    )
    
    ROOM_COUNTS = (('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5+', '5+'))
    
    TENANT_CHOICES = (
        ('Family', 'Family'), ('Bachelor - Male', 'Bachelor - Male'),
        ('Bachelor - Female', 'Bachelor - Female'), ('Bachelor - Any', 'Bachelor - Any'),
        ('Small Family / Couple', 'Small Family / Couple'),
        ('Office / Commercial', 'Office / Commercial'), ('Any (family/bachelor)', 'Any (family/bachelor)')
    )
    
    FACING_CHOICES = (
        ('East', 'East'), ('West', 'West'), ('North', 'North'), ('South', 'South'),
        ('North-East', 'North-East'), ('North-West', 'North-West'), 
        ('South-East', 'South-East'), ('South-West', 'South-West')
    )
    
    FLOOR_CHOICES = [(str(i), str(i)) for i in range(1, 21)]
    FLOOR_CHOICES.insert(0, ('Ground', 'Ground Floor'))

    PARKING_CHOICES = (
        ('Car Parking', 'Car Parking'), ('Bike Parking', 'Bike Parking'),
        ('Both', 'Both (Car & Bike)'), ('None', 'None')
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    
    district = models.CharField(max_length=50, default='Dhaka')
    location = models.CharField(max_length=200, help_text="Area name, e.g. ECB Chattar, Mirpur")
    street_address = models.CharField(max_length=255, blank=True, null=True, help_text="Building Name, Road No, Block/Sector")
    
    # ==========================================
    # ** NEW FIELD: Landmark for precise Google Map **
    # ==========================================
    landmark = models.CharField(max_length=255, blank=True, null=True, help_text="Nearby famous place, e.g. Mirpur College")
    
    listing_type = models.CharField(max_length=10, choices=LISTING_CHOICES, default='Rent')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Residential')
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default='Apartment')
    
    rent_or_price = models.PositiveIntegerField(help_text="Monthly Rent or Total Price")
    service_charge = models.PositiveIntegerField(default=0, help_text="Monthly Service Charge (if any)")
    
    bedrooms = models.CharField(max_length=10, choices=ROOM_COUNTS, default='1')
    bathrooms = models.CharField(max_length=10, choices=ROOM_COUNTS, default='1')
    balconies = models.CharField(max_length=10, choices=ROOM_COUNTS, default='0')
    drawing_room = models.CharField(max_length=10, choices=ROOM_COUNTS, default='0')
    dining_room = models.CharField(max_length=10, choices=ROOM_COUNTS, default='0')
    
    floor = models.CharField(max_length=50, choices=FLOOR_CHOICES, default='1', help_text="Select Floor Level")
    facing = models.CharField(max_length=20, choices=FACING_CHOICES, blank=True, null=True)
    available_from = models.DateField(blank=True, null=True, help_text="When can tenant move in?")
    
    tenant_type = models.CharField(max_length=50, choices=TENANT_CHOICES, default='Family')
    
    gas_type = models.CharField(max_length=50, choices=(('Line Gas', 'Line Gas'), ('Cylinder Gas', 'Cylinder Gas'), ('None', 'None')), default='None')
    electricity_meter = models.CharField(max_length=50, choices=(('Prepaid Meter', 'Prepaid Meter'), ('Sub-Meter', 'Sub-Meter')), default='Prepaid Meter')
    
    water_supply = models.CharField(max_length=50, choices=(('WASA Line', 'WASA Line'), ('Deep Tube-well', 'Deep Tube-well'), ('Both', 'Both')), default='WASA Line')
    has_washing_machine_point = models.BooleanField(default=False, verbose_name="Washing Machine Point")
    has_ac_point = models.BooleanField(default=False, verbose_name="AC Point")
    has_geyser_point = models.BooleanField(default=False, verbose_name="Geyser Point")
    
    has_lift = models.BooleanField(default=False, verbose_name="Lift")
    has_generator = models.BooleanField(default=False, verbose_name="Generator Backup")
    has_cctv = models.BooleanField(default=False, verbose_name="CCTV Camera")
    has_security_guard = models.BooleanField(default=False, verbose_name="Security Guard")
    
    parking_facility = models.CharField(max_length=50, choices=PARKING_CHOICES, default='None')
    
    has_attached_bath = models.BooleanField(default=False, verbose_name="Attached Bath")
    has_balcony = models.BooleanField(default=False, verbose_name="Balcony")
    floor_type = models.CharField(max_length=50, choices=(('Tiled', 'Tiled'), ('Normal Floor', 'Normal Floor / Mosaic')), default='Tiled')
    
    description = models.TextField(blank=True, null=True, help_text="Optional message from owner")
    
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    video = models.FileField(upload_to='property_videos/', null=True, blank=True)

    favorites = models.ManyToManyField(User, related_name='favorite_properties', blank=True)

    def __str__(self):
        return f"{self.property_type} in {self.location} by {self.owner.username if self.owner else 'Unknown'}"

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_gallery/')


# 3. Roommate Finder Model
class RoommateAd(models.Model):
    GENDER_CHOICES = (('Male', 'Male'), ('Female', 'Female'), ('Any', 'Any'))
    PROFESSION_CHOICES = (('Student', 'Student'), ('Job Holder', 'Job Holder'), ('Any', 'Any'))
    ROOM_CHOICES = (('Single Room', 'Single Room'), ('Shared (2 Seats)', 'Shared (2 Seats)'), ('Shared (3+ Seats)', 'Shared (3+ Seats)'))
    FOOD_CHOICES = (('Khala Cooks', 'Khala Cooks'), ('Mess System', 'Mess System'), ('Self Cooking', 'Self Cooking'), ('No Food', 'No Food Facility'))

    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roommate_ads')
    title = models.CharField(max_length=200, help_text="e.g. 1 Seat Available for Male Student")
    location = models.CharField(max_length=200)
    rent_per_seat = models.PositiveIntegerField()
    utility_included = models.BooleanField(default=False, help_text="Is gas/electricity included in rent?")
    available_from = models.DateField()
    pref_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Any')
    pref_profession = models.CharField(max_length=20, choices=PROFESSION_CHOICES, default='Any')
    room_type = models.CharField(max_length=20, choices=ROOM_CHOICES, default='Shared (2 Seats)')
    food_system = models.CharField(max_length=20, choices=FOOD_CHOICES, default='Khala Cooks')
    is_smoking_allowed = models.BooleanField(default=False)
    late_entry_allowed = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image1 = models.ImageField(upload_to='roommate_images/', null=True, blank=True)
    image2 = models.ImageField(upload_to='roommate_images/', null=True, blank=True)
    image3 = models.ImageField(upload_to='roommate_images/', null=True, blank=True)

    def __str__(self):
        return self.title

    # 4. Property Report Model
class PropertyReport(models.Model):
    REPORT_REASONS = (
        ('Already Rented', 'Property Already Rented'),
        ('Not Responding', 'Owner Not Responding'),
        ('Fake Info', 'Fake Pictures or Info'),
        ('Broker', 'Broker / Agency (Not Owner)'),
        ('Advance Money Scam', 'Asking for Advance Money'),
        ('Other', 'Other Issue'),
    )
    
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=50, choices=REPORT_REASONS)
    details = models.TextField(blank=True, null=True, help_text="Extra details from user")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, help_text="Admin checked this report")

    def __str__(self):
        return f"Report on {self.property.title} - {self.reason}"

    # 5. Property Comment Model (FB Style)
class PropertyComment(models.Model):
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # নতুন কমেন্ট আগে দেখাবে

    def __str__(self):
        return f"Comment by {self.user.username}"