"""
URL configuration for lingo_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin # Keep this if it's there
from django.urls import path, include # Make sure 'include' is added here!
from entries import views as entry_views # Import views from your entries app
from entries import auth_views  # Import authentication views
from entries import admin_views  # Import admin views for feedback


urlpatterns = [
    # Admin site URL
    path('admin/', admin.site.urls),
    
    # Custom admin views
    path('admin/entries/', include('entries.admin_urls')),

    # API URLs (keep this as it is for your API)
    path('api/', include('entries.urls')), # This points to entries/urls.py for /api/ paths

    # --- NEW: Frontend Web Page URLs ---
    # Language selection landing page
    path('', entry_views.language_selection_view, name='language-selection'),
    
    # Language setting endpoint
    path('set-language/', entry_views.set_language_view, name='set-language'),
    
    # Authentication URLs - MUST come before country patterns to avoid conflicts
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('signup/', auth_views.signup_view, name='signup'),
    path('profile/', auth_views.user_profile_view, name='user-profile'),
    path('add-entry/', auth_views.add_entry_view, name='add-entry'),
    path('edit-entry/<int:entry_id>/', auth_views.edit_entry_view, name='edit-entry'),
    path('my-contributions/', auth_views.my_contributions_view, name='my-contributions'),
    
    # Email verification URLs
    path('verification-pending/', auth_views.verification_pending_view, name='verification-pending'),
    path('verify-email/<uuid:token>/', auth_views.verify_email_view, name='verify-email'),
    path('resend-verification/', auth_views.resend_verification_view, name='resend-verification'),
    path('resend-verification/<int:user_id>/', auth_views.resend_verification_view, name='resend-verification'),
    
    # Country selection page
    path('countries/', entry_views.country_selection_view, name='country-selection'),
    
    # Country-specific home pages
    path('<str:country>/', entry_views.country_home_view, name='country-home'),
    path('<str:country>/entries/', entry_views.country_entry_list_view, name='country-entries'),
    
    # Legacy home page (now redirects to country selection)
    path('home/', entry_views.home_view, name='home'),
    
    # Map the base '/entries/' URL to the entry_list_view function
    path('entries/', entry_views.entry_list_view, name='entry-list'),

    # Map URLs like '/entries/1/' or '/entries/42/' to the entry_detail_view function
    # <int:entry_id> captures the number from the URL and passes it as 'entry_id' argument to the view
    path('entries/<int:entry_id>/', entry_views.entry_detail_view, name='entry-detail'),
    
    # User dashboard
    path('dashboard/', entry_views.user_dashboard_view, name='user-dashboard'),
    
    # Advanced Features
    path('search/', entry_views.advanced_search_view, name='advanced-search'),
    
    # Feedback System
    path('feedback/', admin_views.feedback_form_view, name='feedback_form'),
    path('feedback/success/', admin_views.feedback_success_view, name='feedback_success'),
    
    # Node.js Backend Authentication (New System)
    path('signup-nodejs/', entry_views.signup_nodejs_view, name='signup-nodejs'),
    path('login-nodejs/', entry_views.login_nodejs_view, name='login-nodejs'),
    path('verify-email/', entry_views.verify_email_view, name='verify-email'),
    
    # Test pages
    path('quiz-test/', entry_views.quiz_test_view, name='quiz-test'),
]