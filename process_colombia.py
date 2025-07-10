#!/usr/bin/env python3
"""
Script to process Colombian slang data and add it to LingoWorld.
"""

import os
import sys
import django
import csv
import re

# Set up Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry, Tag

# Category mapping to standardized categories
CATEGORY_MAPPING = {
    'Slang': 'slang',
    'Insult': 'insults',
    'Idiom': 'colloquial_phrases',
    'Proverb': 'colloquial_phrases',
    'Joke': 'jokes',
    'Tongue Twister': 'tongue_twisters',
    'Cultural Reference': 'unique_concepts',
    'Expression': 'colloquial_phrases',
    'Interjection': 'colloquial_phrases',
    'Filler Word': 'colloquial_phrases',
    'Phrase': 'colloquial_phrases',
    'Saying': 'colloquial_phrases',
    'Colloquial': 'colloquial_phrases',
    'Common Expression': 'colloquial_phrases',
}

def clean_text(text):
    """Clean and normalize text data."""
    if not text or text == '-' or text.lower() == 'n/a':
        return ''
    return text.strip()

def process_colombia_data():
    """Process the Colombia data file and add entries to the database."""
    
    print("🇨🇴 Processing Colombian slang data...")
    
    # Read the Colombia data
    colombia_file = '/Users/tavinsky/lingo_project/colombia.txt'
    
    if not os.path.exists(colombia_file):
        print(f"❌ File not found: {colombia_file}")
        return
    
    entries_added = 0
    entries_skipped = 0
    
    with open(colombia_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Extract data from the CSV row
                category = clean_text(row.get('Category', ''))
                term = clean_text(row.get('Term (Spanish)', ''))
                literal_meaning = clean_text(row.get('Literal Meaning', ''))
                slang_meaning = clean_text(row.get('Slang Meaning (English)', ''))
                usage_example_es = clean_text(row.get('Usage Example (Spanish)', ''))
                usage_example_en = clean_text(row.get('Usage Example (English)', ''))
                regional_notes = clean_text(row.get('Regional/Contextual Notes', ''))
                severity = clean_text(row.get('Severity (for insults)', ''))
                gender_notes = clean_text(row.get('Gender/Age Notes', ''))
                
                # More inclusive term detection - try to extract term from different sources
                final_term = term
                if not final_term and usage_example_es:
                    # Try to extract a phrase from the example if no term is provided
                    # This might capture colloquial phrases
                    example_words = usage_example_es.split()
                    if len(example_words) <= 5:  # Short phrases might be the actual terms
                        final_term = usage_example_es
                
                if not final_term and slang_meaning:
                    # If still no term but we have meaning, create a descriptive term
                    final_term = f"[Expression: {slang_meaning[:30]}]"
                
                # Skip only if absolutely no useful data
                if not final_term and not slang_meaning and not usage_example_es:
                    entries_skipped += 1
                    print(f"⏭️  Skipping row with no usable data")
                    continue
                
                # Map category to standardized format
                standardized_category = CATEGORY_MAPPING.get(category, 'slang')
                
                # Build the notes field
                notes_parts = []
                if slang_meaning:
                    notes_parts.append(f"Meaning: {slang_meaning}")
                if literal_meaning:
                    notes_parts.append(f"Literal: {literal_meaning}")
                if regional_notes:
                    notes_parts.append(f"Notes: {regional_notes}")
                if severity and severity.lower() != 'n/a':
                    notes_parts.append(f"Severity: {severity}")
                if gender_notes and gender_notes.lower() != 'n/a':
                    notes_parts.append(f"Gender: {gender_notes}")
                
                notes = ' | '.join(notes_parts)
                
                # Check if entry already exists
                existing_entry = Entry.objects.filter(
                    term=final_term, 
                    language_code='es-CO'
                ).first()
                
                if existing_entry:
                    print(f"⏭️  Skipping existing entry: {final_term}")
                    entries_skipped += 1
                    continue
                
                # Create the entry
                entry = Entry.objects.create(
                    term=final_term,
                    language_code='es-CO',  # Colombian Spanish
                    region_code='CO',
                    category=standardized_category,
                    notes=notes,
                    part_of_speech=''  # Not provided in the data
                )
                
                # Add translation if available
                if slang_meaning:
                    from entries.models import Translation
                    Translation.objects.create(
                        entry=entry,
                        target_language_code='en',
                        translation=slang_meaning
                    )
                
                # Add example if available
                if usage_example_es and usage_example_en:
                    from entries.models import Example
                    Example.objects.create(
                        entry=entry,
                        sentence=usage_example_es,
                        language_code='es-CO',
                        translation=usage_example_en
                    )
                
                # Add tags based on category and notes
                tags_to_add = []
                if 'Bogota' in regional_notes or 'Medellín' in regional_notes:
                    tags_to_add.append('Regional')
                if 'party' in slang_meaning.lower() or 'rumba' in term.lower():
                    tags_to_add.append('Party')
                if 'vulgar' in regional_notes.lower() or severity:
                    tags_to_add.append('Vulgar')
                if gender_notes and 'gendered' in gender_notes.lower():
                    tags_to_add.append('Gendered')
                
                # Add general Colombian tag
                tags_to_add.append('Colombian')
                
                for tag_name in tags_to_add:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    entry.tags.add(tag)
                
                entries_added += 1
                print(f"✅ Added: {final_term} ({standardized_category})")
                
            except Exception as e:
                print(f"❌ Error processing row: {e}")
                entries_skipped += 1
                continue
    
    print(f"\n🎉 Processing complete!")
    print(f"   ✅ Entries added: {entries_added}")
    print(f"   ⏭️  Entries skipped: {entries_skipped}")
    
    return entries_added

def get_colombia_stats():
    """Get statistics about Colombian entries."""
    total_entries = Entry.objects.filter(language_code='es-CO').count()
    
    if total_entries == 0:
        print("No Colombian entries found in database.")
        return
    
    print(f"\n📊 Colombian entries statistics:")
    print(f"   Total entries: {total_entries}")
    
    # Category breakdown
    categories = Entry.objects.filter(language_code='es-CO').exclude(
        category__isnull=True
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    print(f"   Categories:")
    for cat in categories:
        print(f"     {cat['category']}: {cat['count']} entries")

if __name__ == '__main__':
    from django.db.models import Count
    
    print("🌎 LingoWorld - Adding Colombia 🇨🇴")
    print("=" * 40)
    
    # Check current state
    get_colombia_stats()
    
    # Process the data
    entries_added = process_colombia_data()
    
    if entries_added > 0:
        print("\n" + "=" * 40)
        get_colombia_stats()
    
    print("\n🎯 Colombia has been added to LingoWorld! 🇨🇴✨")
