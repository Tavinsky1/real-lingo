# entries/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Entry, Feedback
from .translations import get_translation


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user creation form with additional fields and validation."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)',
            'autocomplete': 'family-name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language', 'en')
        super().__init__(*args, **kwargs)
        
        # Customize form field widgets and labels based on language
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': get_translation('username', self.language),
            'autocomplete': 'username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': get_translation('password', self.language),
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': get_translation('confirm_password', self.language),
            'autocomplete': 'new-password'
        })
        
        # Update labels
        self.fields['username'].label = get_translation('username', self.language)
        self.fields['email'].label = get_translation('email', self.language)
        self.fields['first_name'].label = get_translation('first_name', self.language)
        self.fields['last_name'].label = get_translation('last_name', self.language)
        self.fields['password1'].label = get_translation('password', self.language)
        self.fields['password2'].label = get_translation('confirm_password', self.language)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(get_translation('email_taken', self.language))
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Keep inactive until email verification
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced authentication form with better styling and translations."""
    
    def __init__(self, request=None, *args, **kwargs):
        self.language = kwargs.pop('language', 'en')
        super().__init__(request, *args, **kwargs)
        
        # Customize form field widgets and labels based on language
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': get_translation('username', self.language),
            'autocomplete': 'username',
            'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': get_translation('password', self.language),
            'autocomplete': 'current-password'
        })
        
        # Update labels
        self.fields['username'].label = get_translation('username', self.language)
        self.fields['password'].label = get_translation('password', self.language)


class EntryForm(forms.ModelForm):
    """Form for creating and editing entries."""
    
    class Meta:
        model = Entry
        fields = ['term', 'language_code', 'region_code', 'category', 'part_of_speech', 'notes', 'tags']
        widgets = {
            'term': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the term or phrase'
            }),
            'language_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., en, es, de'
            }),
            'region_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., US-NY, Berlin (optional)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'part_of_speech': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., noun, verb (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cultural notes, etymology, or usage context (optional)'
            }),
            'tags': forms.CheckboxSelectMultiple()
        }
    
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language', 'en')
        super().__init__(*args, **kwargs)
        
        # Update labels based on language
        self.fields['term'].label = get_translation('term', self.language) if hasattr(self, 'language') else 'Term'
        self.fields['language_code'].label = 'Language Code'
        self.fields['region_code'].label = 'Region Code'
        self.fields['category'].label = get_translation('categories', self.language)
        self.fields['part_of_speech'].label = 'Part of Speech'
        self.fields['notes'].label = 'Notes'
        self.fields['tags'].label = 'Tags'


class FeedbackForm(forms.ModelForm):
    """Form for user feedback submission."""
    
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'title', 'description', 'country_context']
        widgets = {
            'feedback_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title describing your feedback',
                'maxlength': '200',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Please provide detailed information about your feedback, suggestion, or issue...',
                'required': True
            }),
            'country_context': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Related country (optional, e.g., Germany, Argentina)',
                'maxlength': '50'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set field labels
        self.fields['feedback_type'].label = 'Feedback Type'
        self.fields['title'].label = 'Title'
        self.fields['description'].label = 'Description'
        self.fields['country_context'].label = 'Related Country (Optional)'
        
        # Set help texts
        self.fields['feedback_type'].help_text = 'Select the type that best describes your feedback'
        self.fields['title'].help_text = 'A concise summary of your feedback'
        self.fields['description'].help_text = 'Provide as much detail as possible to help us understand and address your feedback'
        self.fields['country_context'].help_text = 'If your feedback relates to a specific country\'s content, please specify'
