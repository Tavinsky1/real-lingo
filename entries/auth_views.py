# entries/auth_views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import CustomUserCreationForm, CustomAuthenticationForm, EntryForm
from .models import Entry, UserFavorite, UserProgress, EmailVerification
from .translations import get_translation, get_user_language
from .email_verification import create_verification_for_user, send_verification_email, send_welcome_email


@csrf_protect
@never_cache
def signup_view(request):
    """User registration view."""
    language = get_user_language(request)
    
    if request.user.is_authenticated:
        return redirect('country-selection')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, language=language)
        if form.is_valid():
            user = form.save()  # User is created but inactive
            username = form.cleaned_data.get('username')
            
            # Send verification email
            email_sent = create_verification_for_user(user, request, language)
            
            if email_sent:
                # Add success message with email verification instruction
                messages.success(
                    request, 
                    get_translation('signup_success_verify_email', language).format(email=user.email)
                )
                # Redirect to verification pending page
                return redirect('verification-pending')
            else:
                # Email sending failed
                messages.error(
                    request, 
                    get_translation('email_sending_failed', language)
                )
        else:
            # Add error message
            messages.error(
                request, 
                get_translation('invalid_form_data', language)
            )
    else:
        # Clear any existing messages on GET request to avoid showing 
        # logout/login messages from previous sessions
        list(messages.get_messages(request))  # Consume all messages by converting to list
        
        form = CustomUserCreationForm(language=language)
    
    context = {
        'form': form,
        'language': language,
        'title': get_translation('sign_up', language),
    }
    return render(request, 'registration/signup.html', context)


@csrf_protect
@never_cache
def login_view(request):
    """Enhanced login view with language support."""
    language = get_user_language(request)
    
    if request.user.is_authenticated:
        return redirect('country-selection')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST, language=language)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(
                    request, 
                    get_translation('login_success', language)
                )
                
                # Redirect to next page or country selection
                next_url = request.GET.get('next', 'country-selection')
                return redirect(next_url)
        else:
            messages.error(
                request, 
                get_translation('invalid_credentials', language)
            )
    else:
        # Clear any existing messages on GET request to avoid showing 
        # logout/signup messages from previous sessions
        list(messages.get_messages(request))  # Consume all messages by converting to list
        
        form = CustomAuthenticationForm(language=language)
    
    context = {
        'form': form,
        'language': language,
        'title': get_translation('login', language),
    }
    return render(request, 'registration/login.html', context)


@csrf_protect
def logout_view(request):
    """Enhanced logout view with complete session clearing and proper POST handling."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        # Store language preference before logout
        user_language = request.session.get('user_language', 'en')
        
        # Use Django's logout which properly clears all session data including admin
        logout(request)
        
        # Set language preference in the fresh session
        request.session['user_language'] = user_language
        
        messages.success(
            request, 
            get_translation('logout_success', language)
        )
        return redirect('language-selection')
    elif request.method == 'GET':
        # Handle GET requests for backward compatibility, but prefer POST
        user_language = request.session.get('user_language', 'en')
        
        # Use Django's logout which properly clears all session data including admin
        logout(request)
        
        # Set language preference in the fresh session
        request.session['user_language'] = user_language
        
        messages.info(
            request,
            get_translation('logout_success', language)
        )
        return redirect('language-selection')
    else:
        # Handle other HTTP methods
        return redirect('language-selection')


@login_required
def user_profile_view(request):
    """Enhanced user profile view showing contributions and statistics."""
    language = get_user_language(request)
    user = request.user
    
    # Get user's contributed entries
    contributed_entries = Entry.objects.filter(author=user).order_by('-created_at')
    
    # Pagination for contributed entries
    paginator = Paginator(contributed_entries, 10)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    
    # Get user's favorites
    recent_favorites = UserFavorite.objects.filter(user=user).select_related('entry').order_by('-created_at')[:10]
    
    # Get user's recent activity
    recent_activity = UserProgress.objects.filter(user=user).select_related('entry').order_by('-last_viewed')[:15]
    
    # Calculate user statistics
    total_contributions = contributed_entries.count()
    total_favorites = UserFavorite.objects.filter(user=user).count()
    total_entries_viewed = UserProgress.objects.filter(user=user).count()
    total_learned = UserProgress.objects.filter(user=user, difficulty_rating='MASTERED').count()
    
    context = {
        'language': language,
        'contributed_entries': entries,
        'recent_favorites': recent_favorites,
        'recent_activity': recent_activity,
        'total_contributions': total_contributions,
        'total_favorites': total_favorites,
        'total_entries_viewed': total_entries_viewed,
        'total_learned': total_learned,
        'title': get_translation('profile', language),
    }
    
    return render(request, 'entries/user_profile.html', context)


@login_required
def add_entry_view(request):
    """View for users to add new entries."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, language=language)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user  # Set the current user as author
            entry.save()
            form.save_m2m()  # Save many-to-many relationships (tags)
            
            messages.success(
                request,
                f"Entry '{entry.term}' has been added successfully!"
            )
            return redirect('entry-detail', entry_id=entry.id)
    else:
        form = EntryForm(language=language)
    
    context = {
        'form': form,
        'language': language,
        'title': get_translation('add_entry', language),
    }
    return render(request, 'entries/add_entry.html', context)


@login_required
def edit_entry_view(request, entry_id):
    """View for users to edit their own entries."""
    language = get_user_language(request)
    
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        messages.error(request, "Entry not found.")
        return redirect('entry-list')
    
    # Check if user is the author or has permission to edit
    if entry.author != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to edit this entry.")
        return redirect('entry-detail', entry_id=entry.id)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry, language=language)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Entry '{entry.term}' has been updated successfully!"
            )
            return redirect('entry-detail', entry_id=entry.id)
    else:
        form = EntryForm(instance=entry, language=language)
    
    context = {
        'form': form,
        'entry': entry,
        'language': language,
        'title': get_translation('edit_entry', language),
    }
    return render(request, 'entries/edit_entry.html', context)


@login_required
def my_contributions_view(request):
    """View showing user's contributed entries."""
    language = get_user_language(request)
    
    # Get user's contributed entries
    contributed_entries = Entry.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(contributed_entries, 20)
    page = request.GET.get('page')
    try:
        entries = paginator.page(page)
    except PageNotAnInteger:
        entries = paginator.page(1)
    except EmptyPage:
        entries = paginator.page(paginator.num_pages)
    
    context = {
        'entries': entries,
        'language': language,
        'total_contributions': contributed_entries.count(),
        'title': get_translation('my_contributions', language),
    }
    return render(request, 'entries/my_contributions.html', context)


def verification_pending_view(request):
    """View shown after user signs up, informing them to check email."""
    language = get_user_language(request)
    
    context = {
        'language': language,
        'title': get_translation('email_verification_pending', language),
    }
    return render(request, 'registration/verification_pending.html', context)


def verify_email_view(request, token):
    """View to verify email using the token from email."""
    language = get_user_language(request)
    
    try:
        verification = EmailVerification.objects.get(token=token)
    except EmailVerification.DoesNotExist:
        messages.error(
            request,
            get_translation('invalid_verification_token', language)
        )
        return redirect('login')
    
    if verification.is_expired():
        messages.error(
            request,
            get_translation('verification_token_expired', language)
        )
        return redirect('resend-verification', user_id=verification.user.id)
    
    if verification.is_verified:
        messages.info(
            request,
            get_translation('email_already_verified', language)
        )
        return redirect('login')
    
    # Verify the email
    verification.verify()

    # Send welcome email
    send_welcome_email(verification.user)
    
    messages.success(
        request,
        get_translation('email_verification_success', language)
    )
    
    # Log the user in automatically after verification
    login(request, verification.user)
    return redirect('country-selection')


def resend_verification_view(request, user_id=None):
    """View to resend verification email."""
    language = get_user_language(request)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)
            email_sent = create_verification_for_user(user, request, language)
            
            if email_sent:
                messages.success(
                    request,
                    get_translation('verification_email_resent', language)
                )
            else:
                messages.error(
                    request,
                    get_translation('email_sending_failed', language)
                )
        except User.DoesNotExist:
            messages.error(
                request,
                get_translation('user_not_found', language)
            )
        
        return redirect('verification-pending')
    
    # If user_id is provided, prefill the email
    user_email = ''
    if user_id:
        try:
            user = User.objects.get(id=user_id, is_active=False)
            user_email = user.email
        except User.DoesNotExist:
            pass
    
    context = {
        'language': language,
        'user_email': user_email,
        'title': get_translation('resend_verification', language),
    }
    return render(request, 'registration/resend_verification.html', context)
