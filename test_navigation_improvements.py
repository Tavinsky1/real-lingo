#!/usr/bin/env python
"""
Test script for navigation improvements: logout functionality and language selection
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from entries.translations import get_translation

def test_navigation_improvements():
    """Test the new navigation features"""
    print("=== Testing Navigation Improvements ===\n")
    
    # Create test client
    client = Client()
    
    # Test 1: Check home/language selection access
    print("1. Testing Home/Language Selection Access...")
    response = client.get(reverse('language-selection'))
    print(f"   Language selection page status: {response.status_code}")
    assert response.status_code == 200, "Language selection page should be accessible"
    
    # Test 2: Test logout functionality (requires authentication)
    print("\n2. Testing Authentication Flow...")
    
    # Create test user
    test_user = User.objects.create_user(
        username='nav_test_user',
        email='navtest@example.com',
        password='testpass123',
        is_active=True  # Active user for testing
    )
    
    # Login the user
    login_success = client.login(username='nav_test_user', password='testpass123')
    print(f"   User login successful: {login_success}")
    
    if login_success:
        # Test authenticated access to profile
        profile_response = client.get(reverse('user-profile'))
        print(f"   Profile page status: {profile_response.status_code}")
        
        # Test logout functionality (GET request to logout URL should work)
        logout_response = client.get(reverse('logout'))
        print(f"   Logout response status: {logout_response.status_code}")
        print(f"   Logout redirects to: {logout_response.url if hasattr(logout_response, 'url') else 'No redirect'}")
    
    # Test 3: Check translations for new navigation items
    print("\n3. Testing Navigation Translations...")
    
    nav_translations = {
        'home': ['Home', 'Inicio'],
        'change_language': ['Change Language', 'Cambiar Idioma'],
        'logout': ['Logout', 'Cerrar Sesión'],
        'change_country': ['Change Country', 'Cambiar País']
    }
    
    for key, expected_values in nav_translations.items():
        en_translation = get_translation(key, 'en')
        es_translation = get_translation(key, 'es')
        
        print(f"   {key}:")
        print(f"     EN: {en_translation} (expected: {expected_values[0]})")
        print(f"     ES: {es_translation} (expected: {expected_values[1]})")
        
        # Verify translations exist and are not the key itself
        assert en_translation != key, f"English translation missing for {key}"
        assert es_translation != key, f"Spanish translation missing for {key}"
    
    # Test 4: Test URL patterns
    print("\n4. Testing URL Patterns...")
    
    urls_to_test = [
        ('language-selection', 'Language Selection'),
        ('logout', 'Logout'),
        ('login', 'Login'), 
        ('signup', 'Signup'),
        ('user-profile', 'User Profile')
    ]
    
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"   {description}: {url} ✅")
        except Exception as e:
            print(f"   {description}: ERROR - {e} ❌")
    
    # Test 5: Test country navigation
    print("\n5. Testing Country Navigation...")
    
    countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
    for country in countries:
        try:
            country_home_url = reverse('country-home', kwargs={'country': country})
            country_entries_url = reverse('country-entries', kwargs={'country': country})
            print(f"   {country.title()}: Home={country_home_url}, Entries={country_entries_url} ✅")
        except Exception as e:
            print(f"   {country.title()}: ERROR - {e} ❌")
    
    print("\n✅ Navigation improvements test completed!")
    
    # Cleanup
    test_user.delete()
    print("\n🧹 Test data cleaned up")

if __name__ == '__main__':
    test_navigation_improvements()
