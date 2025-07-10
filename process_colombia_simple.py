#!/usr/bin/env python3
"""
Simple script to process Colombian slang data and add it to LingoWorld.
"""

import os
import sys
import django
import csv

# Set up Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry, Tag, Translation, Example

def process_colombia_data():
    """Process the Colombia data file and add entries to the database."""
    
    print("🇨🇴 Processing Colombian slang data...")
    
    colombia_file = '/Users/tavinsky/lingo_project/colombia.txt'
    
    entries_added = 0
    entries_processed = 0
    
    try:
        with open(colombia_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            print(f"Column headers: {reader.fieldnames}")
            
            for row in reader:
                entries_processed += 1
                
                # Get basic data
                term = row.get('Term (Spanish)', '').strip()
                category = row.get('Category', '').strip()
                slang_meaning = row.get('Slang Meaning (English)', '').strip()
                
                print(f"Processing entry {entries_processed}: {term}")
                
                if not term or term == '-':
                    print(f"  Skipping - no term")
                    continue
                
                # Map category to standardized format
                if category.lower() == 'slang':
                    standardized_category = 'slang'
                else:
                    standardized_category = 'slang'  # Default for now
                
                # Build notes
                notes_parts = []
                if slang_meaning and slang_meaning != '-':
                    notes_parts.append(f"Meaning: {slang_meaning}")
                
                literal = row.get('Literal Meaning', '').strip()
                if literal and literal != '-':
                    notes_parts.append(f"Literal: {literal}")
                
                regional = row.get('Regional/Contextual Notes', '').strip()
                if regional and regional != 'N/A' and regional != '-':
                    notes_parts.append(f"Notes: {regional}")
                
                notes = ' | '.join(notes_parts)
                
                # Check if entry exists
                existing = Entry.objects.filter(term=term, language_code='es-CO').first()
                if existing:
                    print(f"  Skipping - entry exists")
                    continue
                
                # Create entry
                entry = Entry.objects.create(
                    term=term,
                    language_code='es-CO',
                    region_code='CO',
                    category=standardized_category,
                    notes=notes
                )
                
                # Add translation
                if slang_meaning and slang_meaning != '-':
                    Translation.objects.create(
                        entry=entry,
                        language_code='en',
                        translation=slang_meaning
                    )
                
                # Add example
                example_es = row.get('Usage Example (Spanish)', '').strip()
                example_en = row.get('Usage Example (English)', '').strip()
                if example_es and example_en and example_es != 'N/A':
                    Example.objects.create(
                        entry=entry,
                        example_text=example_es,
                        translation=example_en
                    )
                
                # Add Colombian tag
                tag, created = Tag.objects.get_or_create(name='Colombian')
                entry.tags.add(tag)
                
                entries_added += 1
                print(f"  ✅ Added successfully")
                
                # Limit for testing
                if entries_added >= 10:
                    print(f"  Stopping at 10 entries for testing...")
                    break
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nProcessing complete:")
    print(f"  Processed: {entries_processed}")
    print(f"  Added: {entries_added}")
    
    return entries_added

if __name__ == '__main__':
    process_colombia_data()
