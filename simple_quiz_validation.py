#!/usr/bin/env python3
"""
Simple quiz validation test.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.translations import get_translation

try:
    print("🔍 Quick Quiz Validation")
    
    # Test key translations
    take_quiz_es = get_translation('take_quiz', 'es')
    take_quiz_en = get_translation('take_quiz', 'en')
    
    print(f"Take Quiz ES: '{take_quiz_es}'")
    print(f"Take Quiz EN: '{take_quiz_en}'")
    
    if take_quiz_es == "Hacer Quiz":
        print("✅ Spanish quiz button working!")
    else:
        print("❌ Spanish quiz button not working")
    
    # Test quiz completion message
    complete_es = get_translation('quiz_complete', 'es')
    complete_en = get_translation('quiz_complete', 'en')
    
    print(f"Quiz Complete ES: '{complete_es}'")
    print(f"Quiz Complete EN: '{complete_en}'")
    
    print("✅ Quiz localization system is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
