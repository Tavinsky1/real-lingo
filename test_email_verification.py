#!/usr/bin/env python
"""
Test script for email verification functionality
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from entries.models import EmailVerification
from entries.email_verification import create_verification_for_user
from entries.translations import get_translation

def test_email_verification():
    """Test the complete email verification flow"""
    print("=== Testing Email Verification System ===\n")
    
    # Create a test user
    test_user, created = User.objects.get_or_create(
        username='testuser_verification',
        defaults={
            'email': 'test@example.com',
            'is_active': False  # Inactive until verified
        }
    )
    
    print(f"1. Test user created: {test_user.username}")
    print(f"   Email: {test_user.email}")
    print(f"   Active: {test_user.is_active}")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.post('/signup/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Test creating verification for English
    print("\n2. Testing verification creation (English)...")
    email_sent = create_verification_for_user(test_user, request, 'en')
    print(f"   Email sent: {email_sent}")
    
    # Check if verification was created
    verification = EmailVerification.objects.get(user=test_user)
    print(f"   Verification token: {verification.token}")
    print(f"   Is verified: {verification.is_verified}")
    print(f"   Is expired: {verification.is_expired()}")
    
    # Test creating verification for Spanish
    print("\n3. Testing verification creation (Spanish)...")
    email_sent_es = create_verification_for_user(test_user, request, 'es')
    print(f"   Email sent: {email_sent_es}")
    
    # Test translations
    print("\n4. Testing translations...")
    for lang in ['en', 'es']:
        print(f"\n   Language: {lang}")
        print(f"   - Subject: {get_translation('email_verification_subject', lang)}")
        print(f"   - Button: {get_translation('verify_email_button', lang)}")
        print(f"   - Success: {get_translation('email_verification_success', lang)}")
        print(f"   - Pending: {get_translation('email_verification_pending', lang)}")
    
    # Test verification process
    print("\n5. Testing email verification...")
    verification.verify()
    test_user.refresh_from_db()
    
    print(f"   After verification:")
    print(f"   - Is verified: {verification.is_verified}")
    print(f"   - User active: {test_user.is_active}")
    print(f"   - Verified at: {verification.verified_at}")
    
    print("\n✅ Email verification system test completed successfully!")
    
    # Cleanup
    test_user.delete()
    print("\n🧹 Test user cleaned up")

if __name__ == '__main__':
    test_email_verification()
