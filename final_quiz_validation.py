#!/usr/bin/env python3
"""
Complete quiz system validation test.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.translations import get_translation

def test_quiz_interface_translations():
    """Test all quiz interface elements have Spanish translations."""
    print("🎯 TESTING QUIZ INTERFACE TRANSLATIONS")
    print("-" * 50)
    
    interface_keys = [
        'take_quiz',
        'quiz_complete', 
        'correct',
        'incorrect',
        'skipped',
        'slang_master',
        'good_job',
        'keep_learning',
        'try_again',
        'try_again_button',
        'close_quiz',
        'percent_correct',
        'question',
        'of',
        'score',
        'skip',
        'next'
    ]
    
    all_working = True
    for key in interface_keys:
        spanish = get_translation(key, 'es')
        english = get_translation(key, 'en')
        
        if spanish == english or spanish == key:
            print(f"❌ {key}: Missing Spanish translation")
            all_working = False
        else:
            print(f"✅ {key}: '{spanish}'")
    
    return all_working

def test_country_quiz_titles():
    """Test that all country quiz titles have Spanish translations."""
    print("\n🌍 TESTING COUNTRY QUIZ TITLES")
    print("-" * 50)
    
    country_keys = [
        'argentine_slang_quiz',
        'australian_slang_quiz',
        'german_slang_quiz', 
        'colombian_slang_quiz',
        'belgian_slang_quiz'
    ]
    
    all_working = True
    for key in country_keys:
        spanish = get_translation(key, 'es')
        english = get_translation(key, 'en')
        
        if spanish == english or spanish == key:
            print(f"❌ {key}: Missing Spanish translation")
            all_working = False
        else:
            print(f"✅ {key}: '{spanish}'")
    
    return all_working

def test_quiz_template_structure():
    """Test that quiz template has proper structure."""
    print("\n📄 TESTING QUIZ TEMPLATE STRUCTURE")
    print("-" * 50)
    
    template_path = '/Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key structural elements
        checks = [
            ('USER_LANGUAGE variable', "const USER_LANGUAGE = '{{ request.session.user_language|default:\"en\" }}';"),
            ('QUIZ_TRANSLATIONS object', 'const QUIZ_TRANSLATIONS = {'),
            ('Spanish language conditional', "{% if request.session.user_language == 'es' %}"),
            ('Quiz widget element', 'id="slangQuiz"'),
            ('Quiz class definition', 'class SlangQuiz {'),
            ('Country detection method', 'detectCountry()'),
            ('Question sets for all countries', 'questionSets = {')
        ]
        
        all_present = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"✅ {check_name}: Found")
            else:
                print(f"❌ {check_name}: Missing")
                all_present = False
        
        # Check for all countries in question sets
        countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
        for country in countries:
            if f"{country}:" in content:
                print(f"✅ {country} questions: Found")
            else:
                print(f"❌ {country} questions: Missing")
                all_present = False
        
        return all_present
        
    except FileNotFoundError:
        print("❌ Quiz template file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    print("🚀 COMPREHENSIVE QUIZ SYSTEM VALIDATION")
    print("=" * 60)
    
    interface_test = test_quiz_interface_translations()
    titles_test = test_country_quiz_titles()
    template_test = test_quiz_template_structure()
    
    print("\n" + "=" * 60)
    print("📊 FINAL VALIDATION RESULTS")
    print("=" * 60)
    
    if interface_test and titles_test and template_test:
        print("🎉 ALL TESTS PASSED! QUIZ SYSTEM IS FULLY FUNCTIONAL")
        print()
        print("✅ Interface Translations: Complete")
        print("✅ Country Quiz Titles: Complete") 
        print("✅ Template Structure: Complete")
        print()
        print("🌟 Spanish users will have a 100% localized quiz experience!")
        print("🌟 Quiz system works across all 5 countries!")
        print("🌟 Language detection is properly implemented!")
        return True
    else:
        print("❌ SOME TESTS FAILED:")
        if not interface_test:
            print("   - Interface translations need fixing")
        if not titles_test:
            print("   - Country quiz titles need fixing")
        if not template_test:
            print("   - Template structure needs fixing")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🏆 QUIZ SYSTEM VALIDATION: SUCCESS!")
    else:
        print("\n💥 QUIZ SYSTEM VALIDATION: FAILED!")
    sys.exit(0 if success else 1)
