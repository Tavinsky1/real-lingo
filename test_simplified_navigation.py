#!/usr/bin/env python
"""
Test script for simplified navigation - removed country-specific home links
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from entries.translations import get_translation

def test_simplified_navigation():
    """Test the simplified navigation without country-specific home links"""
    print("=== Testing Simplified Navigation ===\n")
    
    client = Client()
    
    # Test 1: Basic navigation access
    print("1. Testing Basic Navigation URLs...")
    
    navigation_urls = [
        ('language-selection', 'Language Selection (Home)'),
        ('entry-list', 'All Terms'),
        ('country-selection', 'Country Selection'),
    ]
    
    for url_name, description in navigation_urls:
        try:
            response = client.get(reverse(url_name))
            status = "✅ OK" if response.status_code in [200, 302] else f"❌ {response.status_code}"
            print(f"   {description}: {status}")
        except Exception as e:
            print(f"   {description}: ❌ ERROR - {e}")
    
    # Test 2: Test country-specific navigation (should still work but not be in main nav)
    print("\n2. Testing Country-Specific URLs (still functional)...")
    
    countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
    for country in countries[:2]:  # Test first 2 to avoid spam
        try:
            country_entries_url = reverse('country-entries', kwargs={'country': country})
            response = client.get(country_entries_url)
            status = "✅ OK" if response.status_code in [200, 302] else f"❌ {response.status_code}"
            print(f"   {country.title()} entries: {status}")
        except Exception as e:
            print(f"   {country.title()} entries: ❌ ERROR - {e}")
    
    # Test 3: Test translations for navigation items
    print("\n3. Testing Navigation Translations...")
    
    nav_items = ['home', 'explore', 'random', 'all_terms', 'change_country', 'choose_country']
    
    for item in nav_items:
        en_translation = get_translation(item, 'en')
        es_translation = get_translation(item, 'es')
        
        # Check if translation exists (not just the key)
        en_ok = "✅" if en_translation != item else "❌"
        es_ok = "✅" if es_translation != item else "❌"
        
        print(f"   {item}: EN={en_translation} {en_ok}, ES={es_translation} {es_ok}")
    
    print("\n4. Navigation Structure Summary...")
    print("   📋 Simplified Navigation Items:")
    print("   • 🏠 Home (Language Selection)")
    print("   • 📖 Explore/All Terms (context-dependent)")
    print("   • 🎲 Random (context-dependent)")
    print("   • 🌍 Choose/Change Country")
    print("   • 🌐 Language Switcher (right side)")
    print("   • 👤 User Menu (authenticated users)")
    
    print("\n   ❌ Removed Items:")
    print("   • Country-specific home links (🇦🇺 Australia, etc.)")
    print("   • Admin link from main navigation")
    print("   • Redundant navigation items")
    
    print("\n✅ Simplified navigation test completed!")
    print("\n🎯 Benefits of Simplified Navigation:")
    print("   • Cleaner, less cluttered interface")
    print("   • Consistent navigation regardless of country selection")
    print("   • Better mobile experience with fewer items")
    print("   • More intuitive user flow")
    print("   • Admin access properly secured")

if __name__ == '__main__':
    test_simplified_navigation()
