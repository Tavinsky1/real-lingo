#!/usr/bin/env python3
"""
Belgium Data Processing Script for LingoWorld
Process belgium.csv and import Belgian slang, phrases, and linguistic expressions
"""

import os
import sys
import django
import csv
from collections import defaultdict

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry, Tag, Translation, Example

def categorize_entry(category, sub_category, term, notes):
    """
    Categorize entries based on the Category and Sub-Category columns
    """
    category_lower = category.lower()
    sub_category_lower = sub_category.lower() if sub_category else ""
    
    # Map categories
    if category_lower == "colloquial phrases":
        return "colloquial_phrases"
    elif category_lower == "insults":
        return "insults"
    elif category_lower == "slang":
        return "slang"
    elif category_lower == "tongue twisters":
        return "tongue_twisters"
    elif category_lower == "unique concepts":
        return "unique_concepts"
    else:
        # Default to slang for any unmapped categories
        return "slang"

def process_belgium_data():
    """Process the Belgium CSV file and import into database"""
    
    file_path = '/Users/tavinsky/lingo_project/belgium.csv'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return
    
    print(f"Found Belgium data file: {file_path}")
    
    # Get or create Belgian tag
    belgian_tag, created = Tag.objects.get_or_create(name='Belgian')
    if created:
        print("Created 'Belgian' tag")
    else:
        print("Using existing 'Belgian' tag")
    
    # Statistics
    stats = defaultdict(int)
    imported_count = 0
    skipped_count = 0
    
    print("Processing Belgium data...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"CSV headers: {reader.fieldnames}")
            
            for row_num, row in enumerate(reader, 1):
                if row_num <= 5:  # Show first 5 rows for debugging
                    print(f"Row {row_num}: {row}")
                
                try:
                    # Extract data
                    category = row.get('Category', '').strip()
                    sub_category = row.get('Sub-Category', '').strip()
                    term = row.get('Term/Phrase', '').strip()
                    translation = row.get('Translation/Meaning', '').strip()
                    language = row.get('Language', '').strip()
                    region = row.get('Region', '').strip()
                    notes = row.get('Notes', '').strip()
                    
                    if not term or not translation:
                        print(f"Row {row_num}: Skipping - missing term or translation")
                        skipped_count += 1
                        continue
                    
                    # Determine language code based on the Language column
                    if 'flemish' in language.lower() or 'dutch' in language.lower():
                        language_code = 'nl-BE'  # Dutch (Belgium)
                    elif 'french' in language.lower():
                        language_code = 'fr-BE'  # French (Belgium)
                    elif 'brusseleir' in language.lower():
                        language_code = 'nl-BE'  # Brussels dialect (Dutch-based)
                    elif 'walloon' in language.lower():
                        language_code = 'fr-BE'  # Walloon (French-based)
                    else:
                        # Default to Dutch Belgian for mixed or unclear cases
                        language_code = 'nl-BE'
                    
                    # Categorize the entry
                    entry_category = categorize_entry(category, sub_category, term, notes)
                    stats[entry_category] += 1
                    
                    # Create example sentence
                    example = f"Example: {term}"
                    if region and region != "Belgium":
                        example += f" (Used in {region})"
                    
                    # Create comprehensive description
                    description = translation
                    if language and language != "Both":
                        description += f" [Language: {language}]"
                    if region and region != "Belgium":
                        description += f" [Region: {region}]"
                    if notes:
                        description += f" Note: {notes}"
                    
                    # Check if entry already exists
                    existing = Entry.objects.filter(
                        term=term,
                        language_code=language_code,
                        region_code='BE'
                    ).first()
                    
                    if existing:
                        print(f"Row {row_num}: Entry '{term}' already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    # Create the entry
                    entry = Entry.objects.create(
                        term=term,
                        language_code=language_code,
                        region_code='BE',
                        category=entry_category,
                        notes=notes
                    )
                    
                    # Add Belgian tag
                    entry.tags.add(belgian_tag)
                    
                    # Create translation
                    Translation.objects.create(
                        entry=entry,
                        target_language_code='en',  # English translation
                        translation=description
                    )
                    
                    # Create example
                    Example.objects.create(
                        entry=entry,
                        sentence=example,
                        language_code=language_code
                    )
                    
                    imported_count += 1
                    
                    if imported_count % 50 == 0:
                        print(f"Processed {imported_count} entries...")
                        
                except Exception as e:
                    print(f"Row {row_num}: Error processing entry - {e}")
                    skipped_count += 1
                    continue
                    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Print final statistics
    print(f"\n{'='*50}")
    print("BELGIUM IMPORT COMPLETE")
    print(f"{'='*50}")
    print(f"Total entries imported: {imported_count}")
    print(f"Total entries skipped: {skipped_count}")
    print(f"\nEntries by category:")
    for category, count in sorted(stats.items()):
        print(f"  {category}: {count}")
    
    # Verify the import
    total_belgian = Entry.objects.filter(region_code='BE').count()
    print(f"\nTotal Belgian entries in database: {total_belgian}")
    
    # Language breakdown
    dutch_count = Entry.objects.filter(language_code='nl-BE').count()
    french_count = Entry.objects.filter(language_code='fr-BE').count()
    print(f"Dutch/Flemish entries: {dutch_count}")
    print(f"French/Walloon entries: {french_count}")

if __name__ == '__main__':
    process_belgium_data()
