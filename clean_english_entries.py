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

def clean_english_from_argentinian_entries():
    """Clean English words from Argentinian entries and replace with Spanish"""
    
    # Translation mappings for common English words to Spanish
    translations = {
        # Basic words
        'dude': 'tipo/chabón',
        'mate': 'amigo/compañero', 
        'pal': 'amigo/compadre',
        'guy': 'tipo/chabón',
        'girl': 'chica/piba',
        'hot dog': 'pancho/salchicha',
        
        # Descriptive words
        'clueless': 'despistado/sin idea',
        'silly': 'tonto/bobo',
        'stupid': 'estúpido/tonto',
        'foolish': 'tonto/necio',
        'relaxed': 'relajado/tranquilo',
        'calm': 'tranquilo/calmado',
        'versatility': 'versatilidad',
        'unique': 'único',
        
        # Phrases
        'familiar address': 'forma familiar de dirigirse',
        'term of endearment': 'término cariñoso',
        'big-balled': 'valentón/corajudo',
        'multiple meanings': 'múltiples significados',
        'dual meaning': 'doble significado',
        'highlights': 'destaca',
        'refers to': 'se refiere a',
        'similar to': 'similar a',
        'meaning': 'significado',
        'context': 'contexto',
        'literally': 'literalmente',
        'translates to': 'se traduce como',
    }
    
    # Find problematic entries
    problematic_entries = []
    
    # First, handle the specific "familiar address" entries
    familiar_entries = Entry.objects.filter(
        language_code='es-AR', 
        term__in=['familiar address', '(familiar address)']
    )
    
    print(f"Found {familiar_entries.count()} entries with 'familiar address' as term")
    
    for entry in familiar_entries:
        print(f"Deleting problematic entry: ID {entry.id}, Term: '{entry.term}'")
        entry.delete()
    
    # Now fix entries with English in notes
    argentina_entries = Entry.objects.filter(language_code='es-AR')
    fixed_count = 0
    
    print(f"\nChecking {argentina_entries.count()} Argentinian entries for English text...")
    
    for entry in argentina_entries:
        if not entry.notes:
            continue
            
        original_notes = entry.notes
        updated_notes = original_notes
        changed = False
        
        # Apply translations
        for english, spanish in translations.items():
            if english.lower() in updated_notes.lower():
                # Use regex for word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(english) + r'\b'
                if re.search(pattern, updated_notes, re.IGNORECASE):
                    updated_notes = re.sub(pattern, spanish, updated_notes, flags=re.IGNORECASE)
                    changed = True
        
        # Additional specific fixes
        if 'similar to "dude," "mate," or "pal."' in updated_notes:
            updated_notes = updated_notes.replace(
                'similar to "dude," "mate," or "pal."',
                'similar a "chabón," "amigo," o "compadre."'
            )
            changed = True
        
        if 'The etymology is given as "big-balled,"' in updated_notes:
            updated_notes = updated_notes.replace(
                'The etymology is given as "big-balled,"',
                'La etimología se da como "valentón,"'
            )
            changed = True
            
        if changed:
            entry.notes = updated_notes
            entry.save()
            fixed_count += 1
            print(f"Fixed entry {entry.id}: '{entry.term}'")
            print(f"  Before: {original_notes[:100]}...")
            print(f"  After:  {updated_notes[:100]}...")
            print()
    
    print(f"\nFixed {fixed_count} entries with English text")

if __name__ == '__main__':
    clean_english_from_argentinian_entries()
