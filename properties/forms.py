from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Property, UserProfile

# নতুন ইউজার রেজিস্ট্রেশন ফর্ম (ফোন নাম্বার সহ)
class SignUpForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True, help_text="Required for verification (e.g. 017xxxxxxxx)")
    whatsapp_number = forms.CharField(max_length=15, required=False, help_text="Optional")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('username',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # UserProfile তৈরি করে ফোন নাম্বার সেভ করা হচ্ছে
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number'),
                whatsapp_number=self.cleaned_data.get('whatsapp_number')
            )
        return user

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PropertyForm(forms.ModelForm):
    images = MultipleFileField(
        label="Property Images (Max 10)",
        help_text="Select up to 10 images. The first image will be used as the cover.",
        required=False
    )

    class Meta:
        model = Property
        exclude = ['owner', 'image']
        widgets = {
            'rent': forms.NumberInput(attrs={'min': '2000', 'step': '500', 'placeholder': 'e.g. 15000'}),
            'bedrooms': forms.NumberInput(attrs={'min': '1', 'max': '10', 'placeholder': 'e.g. 2'}),
            'bathrooms': forms.NumberInput(attrs={'min': '1', 'max': '10', 'placeholder': 'e.g. 1'}),
            'video': forms.FileInput(attrs={'accept': 'video/*'}),
        }
        labels = {
            'tenant_type': 'Tenant Preference (Family/Bachelor)',
            'pet_allowed': 'Are Pets Allowed?',
            'is_available': 'Is Available Right Now?',
        }
        help_texts = {
            'video': 'Upload a short property tour (Max size: 10 MB. Only 1 video).',
        }

    def clean_images(self):
        images = self.files.getlist('images')
        if len(images) > 10:
            raise ValidationError("You can upload a maximum of 10 images only.")
        return images

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            max_size = 10 * 1024 * 1024  # 10 MB
            if video.size > max_size:
                raise ValidationError("Video size must be under 10MB.")
        return video