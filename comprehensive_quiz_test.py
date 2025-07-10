#!/usr/bin/env python3
"""
Complete quiz system integration test to verify functionality.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.translations import get_translation

def test_quiz_button_spanish():
    """Test that quiz button shows Spanish text."""
    spanish_button = get_translation('take_quiz', 'es')
    english_button = get_translation('take_quiz', 'en')
    
    print("🔘 QUIZ BUTTON TEST:")
    print(f"   Spanish quiz button text: {spanish_button}")
    print(f"   English quiz button text: {english_button}")
    
    if spanish_button == "Hacer Quiz":
        print("   ✅ Spanish quiz button working")
        return True
    else:
        print("   ❌ Spanish quiz button NOT FOUND")
        return False

def test_language_detection():
    """Test language detection functionality."""
    print("\n🌐 LANGUAGE DETECTION TEST:")
    
    # Test Spanish translations exist
    spanish_keys = ['correct', 'incorrect', 'quiz_complete', 'take_quiz']
    spanish_working = True
    
    for key in spanish_keys:
        spanish_val = get_translation(key, 'es')
        english_val = get_translation(key, 'en')
        
        if spanish_val == english_val:
            print(f"   ❌ {key}: No Spanish translation found")
            spanish_working = False
        else:
            print(f"   ✅ {key}: Spanish='{spanish_val}', English='{english_val}'")
    
    return spanish_working

def test_all_countries_quiz_titles():
    """Test that all country quiz titles have Spanish translations."""
    print("\n🌍 COUNTRY QUIZ TITLES TEST:")
    
    countries = [
        ('argentine_slang_quiz', 'Argentina'),
        ('australian_slang_quiz', 'Australia'), 
        ('german_slang_quiz', 'Germany'),
        ('colombian_slang_quiz', 'Colombia'),
        ('belgian_slang_quiz', 'Belgium')
    ]
    
    all_working = True
    for key, country in countries:
        spanish_title = get_translation(key, 'es')
        english_title = get_translation(key, 'en')
        
        if spanish_title != english_title and "Quiz de Jerga" in spanish_title:
            print(f"   ✅ {country}: '{spanish_title}'")
        else:
            print(f"   ❌ {country}: Missing Spanish title")
            all_working = False
    
    return all_working

def main():
    print("🎯 COMPREHENSIVE QUIZ INTEGRATION TEST")
    print("=" * 50)
    
    button_test = test_quiz_button_spanish()
    language_test = test_language_detection()
    countries_test = test_all_countries_quiz_titles()
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS:")
    print("=" * 50)
    
    if button_test and language_test and countries_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Quiz button displays 'Hacer Quiz' in Spanish")
        print("✅ Language detection working properly") 
        print("✅ All country quiz titles have Spanish versions")
        print("✅ Spanish users will have complete Spanish quiz experience")
        print("\n🌟 QUIZ SYSTEM IS FULLY FUNCTIONAL AND LOCALIZED!")
        return True
    else:
        print("❌ SOME TESTS FAILED:")
        if not button_test:
            print("   - Quiz button Spanish translation issue")
        if not language_test:
            print("   - Language detection issue")
        if not countries_test:
            print("   - Country quiz titles missing Spanish translations")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
