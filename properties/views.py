import base64
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Property, PropertyImage, UserProfile, PropertyReport, PropertyComment
from .forms import PropertyForm, SignUpForm

# ===============================
# Public Views (Home & Details)
# ===============================

def home(request):
    # শুধু অ্যাক্টিভ প্রপার্টিগুলো দেখানো হবে এবং নতুনগুলো আগে আসবে
    all_properties = Property.objects.filter(is_available=True).order_by('-created_at')

    # ১. Keyword & Location Search
    q = request.GET.get('q')
    if q:
        all_properties = all_properties.filter(
            Q(title__icontains=q) | 
            Q(location__icontains=q) | 
            Q(district__icontains=q) |
            Q(street_address__icontains=q)
        )

    # ২. Primary Filters
    listing_type = request.GET.get('listing_type')
    if listing_type:
        all_properties = all_properties.filter(listing_type=listing_type)

    property_type = request.GET.get('property_type')
    if property_type:
        all_properties = all_properties.filter(property_type=property_type)

    # ৩. Advanced Filters (Price, Tenant, Rooms)
    min_price = request.GET.get('min_price')
    if min_price and min_price.isdigit():
        all_properties = all_properties.filter(rent_or_price__gte=int(min_price))

    max_price = request.GET.get('max_price')
    if max_price and max_price.isdigit():
        all_properties = all_properties.filter(rent_or_price__lte=int(max_price))

    tenant = request.GET.get('tenant')
    if tenant:
        all_properties = all_properties.filter(tenant_type=tenant)

    beds = request.GET.get('beds')
    if beds:
        all_properties = all_properties.filter(bedrooms=beds)

    baths = request.GET.get('baths')
    if baths:
        all_properties = all_properties.filter(bathrooms=baths)

    # ৪. Amenities (Checkboxes)
    if request.GET.get('gas_line') == 'on':
        all_properties = all_properties.filter(gas_type__icontains='Line Gas')
        
    if request.GET.get('lift') == 'on':
        all_properties = all_properties.filter(has_lift=True)
        
    if request.GET.get('generator') == 'on':
        all_properties = all_properties.filter(has_generator=True)
        
    if request.GET.get('parking') == 'on':
        all_properties = all_properties.exclude(parking_facility='None')

    # ** নতুন কোড: পেজিনেশনের জন্য ফিল্টার প্যারামিটারগুলো সেভ করে রাখা **
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    filter_string = query_dict.urlencode()

    # পেজিনেশন: এক পেজে ৮টি করে কার্ড দেখাবে
    paginator = Paginator(all_properties, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'index.html', {
        'properties': page_obj,
        'filter_string': filter_string  # এটি টেমপ্লেটে পাঠানো হলো
    })

def property_details(request, id):
    property = get_object_or_404(Property, id=id) 
    
    # সরাসরি PropertyImage মডেল থেকে এই প্রপার্টির সব এক্সট্রা ছবিগুলো নিয়ে আসছি
    extra_images = PropertyImage.objects.filter(property=property)
    
    return render(request, 'details.html', {
        'property': property, 
        'extra_images': extra_images
    })

# ===============================
# Authentication Views
# ===============================

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('home')

# ===============================
# Dashboard & Property Management
# ===============================

@login_required(login_url='login')
def dashboard(request):
    # লগইন করা ইউজারের নিজের প্রপার্টি
    user_properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    # ইউজারের সেভ করা (Favorite) প্রপার্টিগুলো
    saved_properties = request.user.favorite_properties.all()
    
    # স্ট্যাটাস কাউন্ট
    total_properties = user_properties.count()
    active_listings = user_properties.filter(is_available=True).count()
    draft_properties = user_properties.filter(is_available=False).count()
    saved_count = saved_properties.count()

    context = {
        'properties': user_properties,
        'saved_properties': saved_properties, # এটি নতুন যুক্ত হলো
        'total_properties': total_properties,
        'active_listings': active_listings,
        'draft_properties': draft_properties,
        'saved_count': saved_count, # এটি নতুন যুক্ত হলো
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def post_property(request):
    if request.method == 'POST':
        property_obj = Property(owner=request.user)
        
        property_obj.title = request.POST.get('title')
        property_obj.district = request.POST.get('district')
        property_obj.location = request.POST.get('location')
        property_obj.street_address = request.POST.get('street_address')
        property_obj.listing_type = request.POST.get('listing_type')
        property_obj.category = request.POST.get('category')
        property_obj.property_type = request.POST.get('property_type')
        property_obj.rent_or_price = request.POST.get('rent_or_price')
        
        service_charge = request.POST.get('service_charge')
        property_obj.service_charge = service_charge if service_charge else 0
        
        property_obj.floor = request.POST.get('floor')
        property_obj.facing = request.POST.get('facing')
        
        avail_date = request.POST.get('available_from')
        if avail_date:
            property_obj.available_from = avail_date
            
        property_obj.tenant_type = request.POST.get('tenant_type')
        
        property_obj.bedrooms = request.POST.get('bedrooms')
        property_obj.bathrooms = request.POST.get('bathrooms')
        property_obj.balconies = request.POST.get('balconies')
        property_obj.drawing_room = request.POST.get('drawing_room')
        property_obj.dining_room = request.POST.get('dining_room')
        
        property_obj.gas_type = request.POST.get('gas_type')
        property_obj.electricity_meter = request.POST.get('electricity_meter')
        property_obj.water_supply = request.POST.get('water_supply')
        property_obj.parking_facility = request.POST.get('parking_facility')
        property_obj.floor_type = request.POST.get('floor_type')

        property_obj.has_attached_bath = request.POST.get('has_attached_bath') == 'on'
        property_obj.has_balcony = request.POST.get('has_balcony') == 'on'
        property_obj.has_ac_point = request.POST.get('has_ac_point') == 'on'
        property_obj.has_geyser_point = request.POST.get('has_geyser_point') == 'on'
        property_obj.has_washing_machine_point = request.POST.get('has_washing_machine_point') == 'on'
        property_obj.has_lift = request.POST.get('has_lift') == 'on'
        property_obj.has_generator = request.POST.get('has_generator') == 'on'
        property_obj.has_cctv = request.POST.get('has_cctv') == 'on'
        property_obj.has_security_guard = request.POST.get('has_security_guard') == 'on'

        property_obj.description = request.POST.get('description')
        
        images = request.FILES.getlist('image')
        if images:
            property_obj.image = images[0]
            
        if request.FILES.get('video'):
            property_obj.video = request.FILES.get('video')

        action = request.POST.get('action')
        property_obj.is_available = (action == 'published')
        
        property_obj.save()

        if len(images) > 1:
            for img in images[1:]:
                PropertyImage.objects.create(property=property_obj, image=img)
                
        return redirect('dashboard')
        
    return render(request, 'post_property.html')

@login_required(login_url='login')
def edit_property(request, id):
    property_obj = get_object_or_404(Property, id=id, owner=request.user)

    if request.method == "POST":
        property_obj.title = request.POST.get('title')
        property_obj.district = request.POST.get('district')
        
        location = request.POST.get('location')
        if location:
            property_obj.location = location
            
        property_obj.street_address = request.POST.get('street_address')
        property_obj.listing_type = request.POST.get('listing_type')
        property_obj.category = request.POST.get('category')
        property_obj.property_type = request.POST.get('property_type')
        
        rent_price = request.POST.get('rent_or_price')
        if rent_price:
            property_obj.rent_or_price = rent_price
            
        service_charge = request.POST.get('service_charge')
        property_obj.service_charge = service_charge if service_charge else 0
        
        property_obj.floor = request.POST.get('floor')
        property_obj.facing = request.POST.get('facing')
        
        avail_date = request.POST.get('available_from')
        if avail_date:
            property_obj.available_from = avail_date
            
        property_obj.tenant_type = request.POST.get('tenant_type')
        
        property_obj.bedrooms = request.POST.get('bedrooms')
        property_obj.bathrooms = request.POST.get('bathrooms')
        property_obj.balconies = request.POST.get('balconies')
        property_obj.drawing_room = request.POST.get('drawing_room')
        property_obj.dining_room = request.POST.get('dining_room')
        
        property_obj.gas_type = request.POST.get('gas_type')
        property_obj.electricity_meter = request.POST.get('electricity_meter')
        property_obj.water_supply = request.POST.get('water_supply')
        property_obj.parking_facility = request.POST.get('parking_facility')
        property_obj.floor_type = request.POST.get('floor_type')

        property_obj.has_attached_bath = request.POST.get('has_attached_bath') == 'on'
        property_obj.has_balcony = request.POST.get('has_balcony') == 'on'
        property_obj.has_ac_point = request.POST.get('has_ac_point') == 'on'
        property_obj.has_geyser_point = request.POST.get('has_geyser_point') == 'on'
        property_obj.has_washing_machine_point = request.POST.get('has_washing_machine_point') == 'on'
        property_obj.has_lift = request.POST.get('has_lift') == 'on'
        property_obj.has_generator = request.POST.get('has_generator') == 'on'
        property_obj.has_cctv = request.POST.get('has_cctv') == 'on'
        property_obj.has_security_guard = request.POST.get('has_security_guard') == 'on'

        property_obj.description = request.POST.get('description')
        
        images = request.FILES.getlist('image')
        if images:
            property_obj.image = images[0]
            
        if request.FILES.get('video'):
            property_obj.video = request.FILES.get('video')

        action = request.POST.get('action')
        property_obj.is_available = (action == 'published')
        
        property_obj.save()
        
        if len(images) > 1:
            for img in images[1:]:
                PropertyImage.objects.create(property=property_obj, image=img)
                
        return redirect('dashboard')

    return render(request, 'post_property.html', {'property': property_obj})

@login_required(login_url='login')
def delete_property(request, id):
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, id=id, owner=request.user)
        property_obj.delete()
    return redirect('dashboard')

@login_required(login_url='login')
def update_status(request, id, status):
    prop = get_object_or_404(Property, id=id, owner=request.user)
    if status == 'available':
        prop.is_available = True 
    elif status == 'rented':
        prop.is_available = False 
    prop.save() 
    return redirect('dashboard')

# ===============================
# User Settings & Profile
# ===============================

@login_required(login_url='login')
def settings_page(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # 1. Update Default User Model
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()

        # 2. Update Custom UserProfile Model
        profile.phone_number = request.POST.get('phone_number', '')
        profile.whatsapp_number = request.POST.get('whatsapp_number', '')
        
        # ** নতুন ফিল্ডগুলো সেভ করার লজিক **
        profile.occupation = request.POST.get('occupation', '')
        profile.facebook_link = request.POST.get('facebook_link', '')
        
        # 3. Handle Cropped Profile Picture (Base64)
        cropped_data = request.POST.get('cropped_image_data')
        
        if cropped_data:
            format, imgstr = cropped_data.split(';base64,') 
            ext = format.split('/')[-1] 
            image_name = f"{request.user.username}_profile.{ext}"
            data = ContentFile(base64.b64decode(imgstr), name=image_name)
            profile.profile_picture = data
            
        elif 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        return redirect('settings')

    return render(request, 'settings.html', {'profile': profile})

# Public Profile Page
def public_profile(request, username):
    # ইউজারকে ডেটাবেস থেকে খুঁজে বের করা
    host = get_object_or_404(User, username=username)
    
    # এই ইউজারের শুধুমাত্র "Published" বা Active প্রপার্টিগুলো নেওয়া
    host_properties = Property.objects.filter(owner=host, is_available=True).order_by('-created_at')
    
    return render(request, 'public_profile.html', {
        'host': host,
        'host_properties': host_properties,
        'total_listings': host_properties.count()
    })

# ===============================
# Saved / Favorites Feature
# ===============================
@login_required(login_url='login')
def toggle_favorite(request, id):
    property_obj = get_object_or_404(Property, id=id)
    
    # যদি ইউজারের লিস্টে আগে থেকেই প্রপার্টিটা সেভ করা থাকে, তবে রিমুভ করে দেবে
    if property_obj.favorites.filter(id=request.user.id).exists():
        property_obj.favorites.remove(request.user)
    # আর যদি সেভ করা না থাকে, তবে নতুন করে সেভ করে নেবে
    else:
        property_obj.favorites.add(request.user)
        
    # ইউজার যে পেজে ছিল, তাকে আবার সেই পেজেই ফেরত পাঠাবে
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Property, PropertyReport # PropertyReport মডেলটি ইমপোর্ট করতে ভুলবেন না

def report_property(request, id):
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, id=id)
        reason = request.POST.get('reason')
        details = request.POST.get('details', '')

        # Create the report
        report = PropertyReport(
            property=property_obj,
            reason=reason,
            details=details
        )
        
        # If user is logged in, save their ID
        if request.user.is_authenticated:
            report.user = request.user
            
        report.save()

        # Show success message
        messages.success(request, "Thank you! Your report has been submitted successfully. We will review it shortly.")
        return redirect('property_details', id=id) 

    return redirect('home')

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def add_comment(request, id):
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, id=id)
        body = request.POST.get('body')
        parent_id = request.POST.get('parent_id') # রিপ্লাইয়ের ক্ষেত্রে প্যারেন্ট আইডি নিবে
        
        if body and body.strip():
            parent_obj = None
            if parent_id:
                parent_obj = PropertyComment.objects.filter(id=parent_id).first()
                
            PropertyComment.objects.create(
                property=property_obj,
                user=request.user,
                body=body.strip(),
                parent=parent_obj # ডাটাবেসে রিপ্লাই সেভ করবে
            )
            messages.success(request, "Comment added successfully!")
            
    return redirect('property_details', id=id)

@login_required(login_url='login')
def edit_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(PropertyComment, id=comment_id)
        # Shudhumatro comment er lekhok (author) edit korte parbe
        if request.user == comment.user:
            body = request.POST.get('body')
            if body and body.strip():
                comment.body = body.strip()
                comment.save()
                messages.success(request, "Comment updated successfully!")
    return redirect('property_details', id=comment.property.id)

@login_required(login_url='login')
def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(PropertyComment, id=comment_id)
        # Comment er lekhok othoba property owner delete korte parbe
        if request.user == comment.user or request.user == comment.property.owner:
            property_id = comment.property.id
            comment.delete()
            messages.success(request, "Comment deleted successfully!")
            return redirect('property_details', id=property_id)
    return redirect('home')