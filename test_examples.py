#!/usr/bin/env python3
"""
Test script to verify country-specific example generation
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.translations import get_translation

def test_example_generation():
    """Test the example generation for different countries"""
    
    countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
    languages = ['en', 'es']
    example_types = ['conversation', 'context']
    test_term = "mate"
    
    print("=== Testing Country-Specific Example Generation ===\n")
    
    for lang in languages:
        print(f"Language: {lang.upper()}")
        print("-" * 40)
        
        for country in countries:
            print(f"\nCountry: {country.title()}")
            
            for example_type in example_types:
                try:
                    template = get_translation(
                        f'example_templates.{country}.{example_type}', 
                        language=lang
                    )
                    example = template.format(test_term)
                    print(f"  {example_type.title()}: {example}")
                except Exception as e:
                    print(f"  {example_type.title()}: ERROR - {e}")
        
        print("\n" + "="*60 + "\n")

def test_navigation_translations():
    """Test navigation translations"""
    
    print("=== Testing Navigation Translations ===\n")
    
    nav_terms = ['home', 'explore', 'random', 'change_country', 'in_conversation', 'in_context', 'related_terms']
    
    for lang in ['en', 'es']:
        print(f"Language: {lang.upper()}")
        print("-" * 30)
        
        for term in nav_terms:
            translation = get_translation(term, language=lang)
            print(f"  {term}: {translation}")
        
        print()

if __name__ == '__main__':
    test_example_generation()
    test_navigation_translations()
