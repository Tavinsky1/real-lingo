#!/usr/bin/env python
"""
Test script to verify category standardization is working correctly across all system components.
"""

import os
import sys
import django

# Set up Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry
from django.db.models import Count
from django.test import RequestFactory
from entries.views import country_home_view, entry_list_view
from entries.serializers import EntrySerializer
from rest_framework.test import APIRequestFactory
import json

def test_category_standardization():
    """Test that all categories are now standardized."""
    print("Testing Category Standardization")
    print("=" * 50)
    
    # Test 1: Verify all categories are standardized
    categories = Entry.objects.exclude(category__isnull=True).values('category').distinct()
    standard_categories = ['slang', 'insults', 'tongue_twisters', 'colloquial_phrases', 'jokes', 'unique_concepts']
    
    all_categories = [cat['category'] for cat in categories]
    non_standard = [cat for cat in all_categories if cat not in standard_categories]
    
    if non_standard:
        print(f"❌ FAILED: Found non-standard categories: {non_standard}")
        return False
    else:
        print("✅ PASSED: All categories are standardized")
    
    # Test 2: Verify category distribution
    print("\nCategory Distribution:")
    print("-" * 30)
    for category in standard_categories:
        count = Entry.objects.filter(category=category).count()
        print(f"  {category:20}: {count:4} entries")
    
    total_categorized = Entry.objects.exclude(category__isnull=True).count()
    total_entries = Entry.objects.count()
    print(f"  {'Total categorized':20}: {total_categorized:4} entries")
    print(f"  {'Total entries':20}: {total_entries:4} entries")
    
    if total_categorized != total_entries:
        print(f"❌ WARNING: {total_entries - total_categorized} entries without categories")
    else:
        print("✅ PASSED: All entries have categories")
    
    return True

def test_model_choices():
    """Test that the model choices are updated correctly."""
    print("\nTesting Model Category Choices")
    print("=" * 40)
    
    # Get the category field choices from the model
    category_field = Entry._meta.get_field('category')
    model_choices = [choice[0] for choice in category_field.choices]
    expected_choices = ['slang', 'insults', 'tongue_twisters', 'colloquial_phrases', 'jokes', 'unique_concepts']
    
    if set(model_choices) == set(expected_choices):
        print("✅ PASSED: Model category choices are updated correctly")
        for choice in category_field.choices:
            print(f"  {choice[0]:20} -> {choice[1]}")
        return True
    else:
        print(f"❌ FAILED: Model choices mismatch")
        print(f"  Expected: {expected_choices}")
        print(f"  Actual: {model_choices}")
        return False

def test_api_serialization():
    """Test that API serialization works with new categories."""
    print("\nTesting API Serialization")
    print("=" * 30)
    
    try:
        # Get a sample entry from each category
        for category in ['slang', 'insults', 'tongue_twisters', 'colloquial_phrases', 'jokes', 'unique_concepts']:
            entry = Entry.objects.filter(category=category).first()
            if entry:
                serializer = EntrySerializer(entry)
                data = serializer.data
                if data['category'] == category:
                    print(f"✅ {category:20}: Serialization working")
                else:
                    print(f"❌ {category:20}: Serialization failed")
                    return False
            else:
                print(f"⚠️  {category:20}: No entries found")
        
        print("✅ PASSED: API serialization working correctly")
        return True
    except Exception as e:
        print(f"❌ FAILED: API serialization error: {e}")
        return False

def test_language_distribution():
    """Test category distribution across languages."""
    print("\nTesting Language Distribution")
    print("=" * 35)
    
    languages = [
        ('de-DE', 'German'),
        ('es-AR', 'Argentinian Spanish'),
        ('en-AU', 'Australian English')
    ]
    
    for lang_code, lang_name in languages:
        print(f"\n{lang_name} ({lang_code}):")
        print("-" * 25)
        
        categories = Entry.objects.filter(language_code=lang_code).exclude(
            category__isnull=True
        ).values('category').annotate(count=Count('id')).order_by('-count')
        
        for cat in categories:
            print(f"  {cat['category']:20}: {cat['count']:3} entries")
        
        total = Entry.objects.filter(language_code=lang_code).count()
        print(f"  {'Total':20}: {total:3} entries")
    
    print("\n✅ PASSED: Language distribution analyzed")
    return True

def test_frontend_view_context():
    """Test that frontend views work with new categories."""
    print("\nTesting Frontend View Context")
    print("=" * 35)
    
    try:
        # Test country home view
        factory = RequestFactory()
        request = factory.get('/germany/')
        
        # Mock a simple request
        request.session = {}
        response = country_home_view(request, 'germany')
        
        if response.status_code == 200:
            print("✅ PASSED: Country home view working")
        else:
            print(f"❌ FAILED: Country home view returned {response.status_code}")
            return False
        
        # Test entry list view
        request = factory.get('/?language=de-DE&category=slang')
        response = entry_list_view(request)
        
        if response.status_code == 200:
            print("✅ PASSED: Entry list view working")
        else:
            print(f"❌ FAILED: Entry list view returned {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ FAILED: Frontend view error: {e}")
        return False

def test_category_display_names():
    """Test that category display names are working correctly."""
    print("\nTesting Category Display Names")
    print("=" * 35)
    
    category_field = Entry._meta.get_field('category')
    display_names = dict(category_field.choices)
    
    expected_display_names = {
        'slang': 'Slang',
        'insults': 'Insults',
        'tongue_twisters': 'Tongue Twisters',
        'colloquial_phrases': 'Colloquial Phrases',
        'jokes': 'Jokes',
        'unique_concepts': 'Unique Concepts'
    }
    
    for code, expected_name in expected_display_names.items():
        actual_name = display_names.get(code)
        if actual_name == expected_name:
            print(f"✅ {code:20}: '{actual_name}'")
        else:
            print(f"❌ {code:20}: Expected '{expected_name}', got '{actual_name}'")
            return False
    
    print("✅ PASSED: All category display names correct")
    return True

def main():
    """Run all tests."""
    print("LingoWorld Category Standardization Test Suite")
    print("=" * 60)
    
    tests = [
        test_category_standardization,
        test_model_choices,
        test_api_serialization,
        test_language_distribution,
        test_frontend_view_context,
        test_category_display_names
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test.__name__} threw exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Category standardization is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
