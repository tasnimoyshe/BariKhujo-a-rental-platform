from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator # পেজিনেশন ইম্পোর্ট করা হলো
from .models import Property, PropertyImage, UserProfile
from .forms import PropertyForm, SignUpForm

def home(request):
    all_properties = Property.objects.all().order_by('-id')

    query = request.GET.get('q')
    if query:
        all_properties = all_properties.filter(
            Q(location__icontains=query) | Q(title__icontains=query)
        )

    tenant = request.GET.get('tenant')
    if tenant and tenant != 'Any':
        all_properties = all_properties.filter(tenant_type=tenant)

    beds = request.GET.get('beds')
    if beds:
        all_properties = all_properties.filter(bedrooms__gte=beds)

    baths = request.GET.get('baths')
    if baths:
        all_properties = all_properties.filter(bathrooms__gte=baths)

    pet = request.GET.get('pet')
    if pet == 'true':
        all_properties = all_properties.filter(pet_allowed=True)
        
    min_rent = request.GET.get('min_rent')
    max_rent = request.GET.get('max_rent')
    
    if min_rent:
        all_properties = all_properties.filter(rent__gte=min_rent)
    if max_rent:
        all_properties = all_properties.filter(rent__lte=max_rent)

    all_properties = all_properties.filter(is_available=True)

    # পেজিনেশন লজিক: এক পেজে ৫টি করে প্রপার্টি দেখাবে (আপনি চাইলে বাড়াতে পারেন)
    paginator = Paginator(all_properties, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # টেমপ্লেটে page_obj কে properties নামে পাঠানো হচ্ছে
    return render(request, 'index.html', {'properties': page_obj})

def property_details(request, id):
    property = get_object_or_404(Property, id=id) 
    return render(request, 'details.html', {'property': property})

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

@login_required(login_url='login')
def post_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            images = request.FILES.getlist('images')
            if images:
                property_obj.image = images[0] 
            property_obj.save()
            if len(images) > 1:
                for img in images[1:10]:
                    PropertyImage.objects.create(property=property_obj, image=img)
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'post_property.html', {'form': form})

@login_required(login_url='login')
def dashboard(request):
    user_properties = Property.objects.filter(owner=request.user).order_by('-id')
    now = timezone.now()
    for prop in user_properties:
        if prop.is_available and prop.updated_at:
            days_passed = (now - prop.updated_at).days
            prop.needs_status_update = days_passed >= 0 
        else:
            prop.needs_status_update = False
    return render(request, 'dashboard.html', {'properties': user_properties})

@login_required(login_url='login')
def update_status(request, id, status):
    prop = get_object_or_404(Property, id=id, owner=request.user)
    if status == 'available':
        prop.is_available = True 
    elif status == 'rented':
        prop.is_available = False 
    prop.save() 
    return redirect('dashboard')

@login_required(login_url='login')
def edit_property(request, id):
    property_obj = get_object_or_404(Property, id=id, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, 'edit_property.html', {'form': form, 'property': property_obj})

@login_required(login_url='login')
def delete_property(request, id):
    property_to_delete = get_object_or_404(Property, id=id, owner=request.user)
    property_to_delete.delete()
    return redirect('dashboard')