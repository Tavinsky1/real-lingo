#!/usr/bin/env python
"""
Script to standardize categories across all languages in the lingo_project.

This script maps the current 19 different category types to 6 standardized categories:
1. slang - General slang terms (including youth, urban, internet, regional slang)
2. insults - Offensive/insulting terms and banter
3. tongue_twisters - Pronunciation challenges
4. colloquial_phrases - Idioms, sayings, proverbs, expressions
5. jokes - Humorous content and wordplay
6. unique_concepts - Culture-specific words/concepts

Mapping Strategy:
- SLANG, YOUTH_SLANG, URBAN_SLANG, REGIONAL_SLANG, INTERNET_SLANG -> slang
- INSULT -> insults
- TONGUE_TWISTER -> tongue_twisters
- IDIOM, PROVERB, GREETING_FAREWELL, FILLER_WORD -> colloquial_phrases
- JOKE, WORDPLAY -> jokes
- UNIQUE_CONCEPT, CULTURAL_REFERENCE, ENDEARMENT, JARGON, SHORTCUT, OTHER -> unique_concepts
"""

import os
import sys
import django

# Set up Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry
from django.db import transaction
from django.db.models import Count

# Define the standardized categories
STANDARD_CATEGORIES = [
    ('slang', 'Slang'),
    ('insults', 'Insults'),
    ('tongue_twisters', 'Tongue Twisters'),
    ('colloquial_phrases', 'Colloquial Phrases'),
    ('jokes', 'Jokes'),
    ('unique_concepts', 'Unique Concepts'),
]

# Category mapping from old to new
CATEGORY_MAPPING = {
    # Map to 'slang'
    'SLANG': 'slang',
    'YOUTH_SLANG': 'slang',
    'URBAN_SLANG': 'slang',
    'REGIONAL_SLANG': 'slang',
    'INTERNET_SLANG': 'slang',
    
    # Map to 'insults'
    'INSULT': 'insults',
    
    # Map to 'tongue_twisters'
    'TONGUE_TWISTER': 'tongue_twisters',
    
    # Map to 'colloquial_phrases'
    'IDIOM': 'colloquial_phrases',
    'PROVERB': 'colloquial_phrases',
    'GREETING_FAREWELL': 'colloquial_phrases',
    'FILLER_WORD': 'colloquial_phrases',
    
    # Map to 'jokes'
    'JOKE': 'jokes',
    'WORDPLAY': 'jokes',
    
    # Map to 'unique_concepts'
    'UNIQUE_CONCEPT': 'unique_concepts',
    'CULTURAL_REFERENCE': 'unique_concepts',
    'ENDEARMENT': 'unique_concepts',
    'JARGON': 'unique_concepts',
    'SHORTCUT': 'unique_concepts',
    'OTHER': 'unique_concepts',
}

def analyze_current_categories():
    """Analyze current category distribution."""
    print("Current Category Analysis:")
    print("=" * 60)
    
    # Get all current categories with counts
    categories = Entry.objects.exclude(category__isnull=True).values('category').annotate(count=Count('id')).order_by('-count')
    
    for cat in categories:
        current_cat = cat['category']
        new_cat = CATEGORY_MAPPING.get(current_cat, 'unknown')
        print(f"{current_cat:20} -> {new_cat:20} ({cat['count']:4} entries)")
    
    print("\n" + "=" * 60)
    
    # Show what the new distribution will look like
    print("\nPredicted New Category Distribution:")
    print("-" * 40)
    
    new_distribution = {}
    for cat in categories:
        current_cat = cat['category']
        new_cat = CATEGORY_MAPPING.get(current_cat, 'unknown')
        new_distribution[new_cat] = new_distribution.get(new_cat, 0) + cat['count']
    
    for new_cat, count in sorted(new_distribution.items(), key=lambda x: x[1], reverse=True):
        print(f"{new_cat:20}: {count:4} entries")
    
    return new_distribution

def standardize_categories(dry_run=True):
    """Standardize all categories according to the mapping."""
    print(f"\n{'DRY RUN - ' if dry_run else ''}Standardizing Categories:")
    print("=" * 60)
    
    if dry_run:
        print("This is a DRY RUN - no changes will be made to the database.")
        print("Set dry_run=False to actually perform the updates.\n")
    
    updates_made = 0
    
    with transaction.atomic():
        for old_category, new_category in CATEGORY_MAPPING.items():
            entries_to_update = Entry.objects.filter(category=old_category)
            count = entries_to_update.count()
            
            if count > 0:
                print(f"Updating {count:4} entries: {old_category} -> {new_category}")
                
                if not dry_run:
                    entries_to_update.update(category=new_category)
                
                updates_made += count
    
    print(f"\nTotal entries {'would be' if dry_run else ''} updated: {updates_made}")
    
    if not dry_run:
        print("\nCategory standardization completed successfully!")
    
    return updates_made

def verify_standardization():
    """Verify the standardization was successful."""
    print("\nVerifying Standardization:")
    print("=" * 40)
    
    # Check final category distribution
    categories = Entry.objects.exclude(category__isnull=True).values('category').annotate(count=Count('id')).order_by('-count')
    
    standard_category_codes = [code for code, name in STANDARD_CATEGORIES]
    
    for cat in categories:
        current_cat = cat['category']
        status = "✓ STANDARD" if current_cat in standard_category_codes else "✗ NON-STANDARD"
        print(f"{current_cat:20}: {cat['count']:4} entries {status}")
    
    # Check for any non-standard categories
    non_standard = [cat['category'] for cat in categories if cat['category'] not in standard_category_codes]
    
    if non_standard:
        print(f"\nWARNING: Found {len(non_standard)} non-standard categories:")
        for cat in non_standard:
            print(f"  - {cat}")
    else:
        print("\n✓ All categories are now standardized!")
    
    return len(non_standard) == 0

def show_language_distribution():
    """Show category distribution by language after standardization."""
    print("\nStandardized Category Distribution by Language:")
    print("=" * 60)
    
    for lang in ['de-DE', 'es-AR', 'en-AU']:
        lang_name = {'de-DE': 'German', 'es-AR': 'Argentinian Spanish', 'en-AU': 'Australian English'}[lang]
        print(f"\n{lang_name} ({lang}):")
        print("-" * 30)
        
        categories = Entry.objects.filter(language_code=lang).exclude(category__isnull=True).values('category').annotate(count=Count('id')).order_by('-count')
        
        for cat in categories:
            print(f"  {cat['category']:20}: {cat['count']:3} entries")
        
        total_lang = Entry.objects.filter(language_code=lang).count()
        print(f"  {'Total':20}: {total_lang:3} entries")

if __name__ == "__main__":
    print("LingoWorld Category Standardization Tool")
    print("========================================")
    
    # Step 1: Analyze current categories
    analyze_current_categories()
    
    # Step 2: Perform dry run
    print("\n" + "=" * 60)
    standardize_categories(dry_run=True)
    
    # Step 3: Ask for confirmation
    print("\n" + "=" * 60)
    response = input("Do you want to proceed with the actual standardization? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print("\nProceeding with standardization...")
        standardize_categories(dry_run=False)
        
        # Step 4: Verify results
        verify_standardization()
        
        # Step 5: Show final distribution
        show_language_distribution()
    else:
        print("Standardization cancelled.")
