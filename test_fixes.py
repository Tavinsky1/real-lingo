#!/usr/bin/env python3
"""
Test script to verify logout and navigation fixes.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

def test_logout_functionality():
    """Test that logout works with both GET and POST requests."""
    print("🔐 Testing logout functionality...")
    
    client = Client()
    
    # Create a test user
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    
    # Login the user
    login_success = client.login(username='testuser', password='testpass123')
    print(f"   ✓ User login: {'SUCCESS' if login_success else 'FAILED'}")
    
    # Test POST logout (preferred method)
    print("   Testing POST logout...")
    response = client.post(reverse('logout'))
    print(f"   ✓ POST logout status: {response.status_code}")
    print(f"   ✓ POST logout redirect: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    # Login again for GET test
    client.login(username='testuser', password='testpass123')
    
    # Test GET logout (backward compatibility)
    print("   Testing GET logout...")
    response = client.get(reverse('logout'))
    print(f"   ✓ GET logout status: {response.status_code}")
    print(f"   ✓ GET logout redirect: {response.url if hasattr(response, 'url') else 'No redirect'}")
    
    # Cleanup
    user.delete()
    print("   ✓ Test user cleaned up")

def test_navigation_context_awareness():
    """Test that navigation is context-aware to selected country."""
    print("🧭 Testing navigation context awareness...")
    
    client = Client()
    
    # Test navigation without selected country
    print("   Testing navigation without selected country...")
    response = client.get(reverse('language-selection'))
    print(f"   ✓ Language selection page status: {response.status_code}")
    
    # Test setting a country session
    print("   Testing navigation with selected country...")
    session = client.session
    session['selected_country'] = 'argentina'
    session.save()
    
    # Now test a page that should show the navigation
    try:
        response = client.get(reverse('country-entries', args=['argentina']))
        print(f"   ✓ Argentina entries page status: {response.status_code}")
        
        # Check if the response contains the correct navigation structure
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'country-entries' in content:
                print("   ✓ Context-aware navigation detected in template")
            else:
                print("   ⚠ Context-aware navigation not found in template")
    except Exception as e:
        print(f"   ⚠ Could not test country-specific navigation: {e}")

def test_url_patterns():
    """Test that all relevant URL patterns are working."""
    print("🔗 Testing URL patterns...")
    
    client = Client()
    
    # Test main URLs
    urls_to_test = [
        ('language-selection', []),
        ('country-selection', []),
        ('entry-list', []),
    ]
    
    for url_name, args in urls_to_test:
        try:
            url = reverse(url_name, args=args)
            response = client.get(url)
            print(f"   ✓ {url_name}: {response.status_code} - {url}")
        except Exception as e:
            print(f"   ✗ {url_name}: ERROR - {e}")

if __name__ == '__main__':
    print("🚀 Starting LingoWorld fixes testing...\n")
    
    try:
        test_logout_functionality()
        print()
        test_navigation_context_awareness()
        print()
        test_url_patterns()
        print()
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
