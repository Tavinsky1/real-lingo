#!/usr/bin/env python3
"""
Authentication Integration Test for LingoWorld
Tests the complete user authentication system including login, signup, and user attribution.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Setup Django environment
sys.path.insert(0, '/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry, Tag
from entries.auth_views import *


class AuthenticationIntegrationTest(TestCase):
    """Test suite for the authentication system integration."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='slang', color='#FF5733')
        self.tag2 = Tag.objects.create(name='informal', color='#33FF57')
        
        # Create test entries with authors
        self.entry1 = Entry.objects.create(
            term='che',
            definition='Argentine expression',
            language_code='es-AR',
            region_code='AR',
            category='GREETING',
            notes='Common greeting in Argentina',
            author=self.user1
        )
        
        self.entry2 = Entry.objects.create(
            term='mate',
            definition='Traditional South American drink',
            language_code='es-AR',
            region_code='AR',
            category='FOOD',
            notes='Traditional drink shared among friends',
            author=self.user2
        )
    
    def test_user_signup(self):
        """Test user registration functionality."""
        print("Testing user signup...")
        
        signup_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        
        response = self.client.post(reverse('signup'), signup_data)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        print("✓ User signup successful")
    
    def test_user_login(self):
        """Test user login functionality."""
        print("Testing user login...")
        
        login_data = {
            'username': 'testuser1',
            'password': 'testpass123',
        }
        
        response = self.client.post(reverse('login'), login_data)
        
        # Check if user is logged in
        user = User.objects.get(username='testuser1')
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        print("✓ User login successful")
    
    def test_entry_author_attribution(self):
        """Test that entries show proper author attribution."""
        print("Testing entry author attribution...")
        
        # Check that entries have authors
        self.assertEqual(self.entry1.author, self.user1)
        self.assertEqual(self.entry2.author, self.user2)
        
        # Test entry detail page shows author
        response = self.client.get(reverse('entry-detail', kwargs={'entry_id': self.entry1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.username)
        
        print("✓ Entry author attribution working")
    
    def test_authenticated_entry_creation(self):
        """Test that authenticated users can create entries."""
        print("Testing authenticated entry creation...")
        
        # Login user
        self.client.login(username='testuser1', password='testpass123')
        
        entry_data = {
            'term': 'boludo',
            'definition': 'Argentine slang term',
            'language_code': 'es-AR',
            'region_code': 'AR',
            'category': 'EXPRESSION',
            'notes': 'Commonly used expression in Argentina',
        }
        
        response = self.client.post(reverse('add-entry'), entry_data)
        
        # Check if entry was created
        created_entry = Entry.objects.filter(term='boludo').first()
        self.assertIsNotNone(created_entry)
        self.assertEqual(created_entry.author, self.user1)
        
        print("✓ Authenticated entry creation successful")
    
    def test_unauthenticated_entry_creation_redirect(self):
        """Test that unauthenticated users are redirected when trying to create entries."""
        print("Testing unauthenticated entry creation redirect...")
        
        # Try to access add-entry without login
        response = self.client.get(reverse('add-entry'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        print("✓ Unauthenticated users properly redirected")
    
    def test_user_profile_view(self):
        """Test user profile view shows contributions."""
        print("Testing user profile view...")
        
        # Login user
        self.client.login(username='testuser1', password='testpass123')
        
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, 200)
        
        # Check that user's entries are shown
        self.assertContains(response, self.entry1.term)
        print("✓ User profile view working")
    
    def test_entry_edit_permissions(self):
        """Test that only entry authors can edit their entries."""
        print("Testing entry edit permissions...")
        
        # Login as user1
        self.client.login(username='testuser1', password='testpass123')
        
        # Try to edit own entry (should work)
        response = self.client.get(reverse('edit-entry', kwargs={'entry_id': self.entry1.id}))
        self.assertEqual(response.status_code, 200)
        
        # Try to edit other user's entry (should redirect)
        response = self.client.get(reverse('edit-entry', kwargs={'entry_id': self.entry2.id}))
        self.assertEqual(response.status_code, 302)  # Redirect due to no permission
        
        print("✓ Entry edit permissions working correctly")
    
    def test_navbar_authentication_integration(self):
        """Test that navbar shows appropriate content based on authentication status."""
        print("Testing navbar authentication integration...")
        
        # Test unauthenticated navbar
        response = self.client.get(reverse('entry-list'))
        self.assertContains(response, 'login')
        self.assertContains(response, 'signup')
        
        # Test authenticated navbar
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('entry-list'))
        self.assertContains(response, self.user1.username)
        self.assertContains(response, 'add_entry')
        
        print("✓ Navbar authentication integration working")
    
    def test_language_support_in_authentication(self):
        """Test that authentication forms support multiple languages."""
        print("Testing language support in authentication...")
        
        # Test Spanish language setting
        session = self.client.session
        session['user_language'] = 'es'
        session.save()
        
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Test English language setting
        session['user_language'] = 'en'
        session.save()
        
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        print("✓ Language support in authentication working")


def run_authentication_tests():
    """Run all authentication integration tests."""
    print("🧪 Running LingoWorld Authentication Integration Tests")
    print("=" * 60)
    
    # Import Django test runner
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run the tests
    failures = test_runner.run_tests(['__main__.AuthenticationIntegrationTest'])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed")
        return False
    else:
        print("\n✅ All authentication integration tests passed!")
        print("\n🎉 LingoWorld authentication system is fully integrated and working!")
        return True


if __name__ == '__main__':
    success = run_authentication_tests()
    sys.exit(0 if success else 1)
