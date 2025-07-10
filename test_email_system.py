#!/usr/bin/env python
"""
Test Email Verification System
Run this script to test the complete email verification flow.
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from entries.models import User, EmailVerification
from entries.email_verification import create_verification_for_user
from django.test import RequestFactory

def test_email_configuration():
    """Test basic email configuration."""
    print("🔧 Testing Email Configuration")
    print(f"   Email Backend: {settings.EMAIL_BACKEND}")
    print(f"   Email Host: {settings.EMAIL_HOST}")
    print(f"   Email User: {settings.EMAIL_HOST_USER}")
    print(f"   Default From: {settings.DEFAULT_FROM_EMAIL}")
    print()

def test_simple_email():
    """Test sending a simple email."""
    print("📧 Testing Simple Email Send")
    
    try:
        result = send_mail(
            subject='[LingoWorld] SMTP Test',
            message='This is a test email to verify Gmail SMTP configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['lingoworldapp@gmail.com'],  # Send to self
            fail_silently=False,
        )
        print(f"   ✅ Email sent successfully! Messages sent: {result}")
        return True
    except Exception as e:
        print(f"   ❌ Email sending failed: {e}")
        if "Username and Password not accepted" in str(e):
            print("   💡 Gmail App Password required - see GMAIL_SMTP_SETUP.md")
        return False

def test_verification_email():
    """Test the complete email verification system."""
    print("🔐 Testing Email Verification System")
    
    # Create a test user (if doesn't exist)
    test_email = "test@lingoworld.com"
    test_username = "testuser_verification"
    
    try:
        # Remove existing test user if exists
        User.objects.filter(username=test_username).delete()
        User.objects.filter(email=test_email).delete()
        
        # Create new test user
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password='testpass123',
            is_active=False  # Inactive until verified
        )
        
        print(f"   ✅ Test user created: {user.username} ({user.email})")
        
        # Test verification email creation
        factory = RequestFactory()
        request = factory.get('/')
        
        # Create verification
        email_sent = create_verification_for_user(user, request, 'en')
        
        if email_sent:
            print("   ✅ Verification email sent successfully")
            
            # Check verification record
            verification = EmailVerification.objects.filter(user=user).first()
            if verification:
                print(f"   ✅ Verification token created: {verification.token[:10]}...")
                print(f"   ✅ Token expires: {verification.expires_at}")
            else:
                print("   ❌ No verification record found")
        else:
            print("   ❌ Verification email failed to send")
            
        # Clean up test user
        user.delete()
        print("   🧹 Test user cleaned up")
        
        return email_sent
        
    except Exception as e:
        print(f"   ❌ Verification test failed: {e}")
        return False

def main():
    """Run all email tests."""
    print("🌍 LingoWorld Email System Test Suite")
    print("=" * 50)
    print()
    
    # Test 1: Configuration
    test_email_configuration()
    
    # Test 2: Simple email
    simple_email_ok = test_simple_email()
    print()
    
    # Test 3: Verification system
    verification_ok = test_verification_email()
    print()
    
    # Summary
    print("📊 Test Summary")
    print(f"   Simple Email: {'✅ PASS' if simple_email_ok else '❌ FAIL'}")
    print(f"   Verification: {'✅ PASS' if verification_ok else '❌ FAIL'}")
    print()
    
    if simple_email_ok and verification_ok:
        print("🎉 All email tests passed! Email system is ready.")
    elif verification_ok:
        print("⚠️  Email system working, but Gmail SMTP needs App Password.")
        print("   Check GMAIL_SMTP_SETUP.md for setup instructions.")
    else:
        print("❌ Email system needs configuration. Check GMAIL_SMTP_SETUP.md")

if __name__ == "__main__":
    main()
