#!/usr/bin/env python3
"""
Test script to verify quiz translations are working correctly.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.translations import get_translation

def test_quiz_translations():
    """Test quiz-related translations in both languages."""
    
    print("=== TESTING QUIZ TRANSLATIONS ===\n")
    
    # Test basic quiz terms
    quiz_keys = [
        'slang_quiz_challenge',
        'question', 
        'of',
        'score',
        'skip',
        'next',
        'take_quiz',
        'correct',
        'incorrect',
        'skipped',
        'quiz_complete',
        'slang_master',
        'good_job',
        'keep_learning',
        'try_again',
        'try_again_button',
        'close_quiz',
        'loading_question',
        'percent_correct',
        'argentine_slang_quiz',
        'australian_slang_quiz',
        'german_slang_quiz',
        'colombian_slang_quiz',
        'belgian_slang_quiz'
    ]
    
    print("English translations:")
    for key in quiz_keys:
        en_translation = get_translation(key, 'en')
        print(f"  {key}: {en_translation}")
    
    print("\nSpanish translations:")
    for key in quiz_keys:
        es_translation = get_translation(key, 'es')
        print(f"  {key}: {es_translation}")
    
    print("\n=== TESTING COMPLETE ===")
    
    # Verify that Spanish translations are different from English
    differences_found = 0
    for key in quiz_keys:
        en_val = get_translation(key, 'en')
        es_val = get_translation(key, 'es')
        if en_val != es_val:
            differences_found += 1
    
    print(f"\nFound {differences_found}/{len(quiz_keys)} translations with language differences")
    
    if differences_found > 0:
        print("✅ Quiz translations are working correctly!")
        return True
    else:
        print("❌ Quiz translations are not working - no differences found")
        return False

if __name__ == "__main__":
    test_quiz_translations()
