#!/usr/bin/env python3
import os
import sys
import django
import re

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry

def find_english_entries():
    """Find entries with English words that shouldn't be there"""
    
    # English patterns to look for
    english_patterns = [
        r'\bfamiliar address\b',
        r'\bdude\b',
        r'\bmate\b', 
        r'\bpal\b',
        r'\bhot dog\b',
        r'\bcalm/relaxed person\b',
        r'\bsomeone clueless\b',
        r'\bversatility\b',
        r'\bmultiple meanings\b',
        r'\bunique\b',
        r'\bsilly\b',
        r'\bclueless\b',
        r'\brelaxed person\b'
    ]
    
    problematic_entries = []
    argentina_entries = Entry.objects.filter(language_code='es-AR')
    
    print(f"Checking {argentina_entries.count()} Argentinian entries...")
    
    for entry in argentina_entries:
        notes_text = entry.notes or ""
        text_to_check = f"{entry.term} {notes_text}"
        
        for pattern in english_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                problematic_entries.append({
                    'id': entry.id,
                    'term': entry.term,
                    'notes': entry.notes,
                    'pattern': pattern
                })
                break
    
    print(f"\nFound {len(problematic_entries)} entries with English text:")
    print("=" * 60)
    
    for i, entry in enumerate(problematic_entries[:15], 1):  # Show first 15
        print(f"{i}. ID: {entry['id']}, Term: '{entry['term']}'")
        print(f"   Pattern matched: {entry['pattern']}")
        if entry['notes']:
            notes_preview = entry['notes'][:150] + "..." if len(entry['notes']) > 150 else entry['notes']
            print(f"   Notes: {notes_preview}")
        print()
    
    if len(problematic_entries) > 15:
        print(f"... and {len(problematic_entries) - 15} more entries")
    
    return problematic_entries

if __name__ == '__main__':
    find_english_entries()
