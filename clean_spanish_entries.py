#!/usr/bin/env python
"""
Comprehensive script to clean English text from Spanish entries in LingoWorld database.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry, Tag
import re

def clean_english_from_spanish():
    """Clean English text from Spanish entries and replace with Spanish equivalents."""
    
    # Comprehensive translation mapping
    translations_map = {
        # Common phrases
        'familiar address': 'tratamiento familiar',
        'familiar form': 'forma familiar',
        'informal address': 'tratamiento informal',
        'used to address': 'usado para dirigirse a',
        'term of endearment': 'término cariñoso',
        'affectionate term': 'término afectivo',
        'slang term': 'término de jerga',
        'colloquial expression': 'expresión coloquial',
        'informal way': 'manera informal',
        'casual expression': 'expresión casual',
        'friendly term': 'término amistoso',
        'intimate form': 'forma íntima',
        
        # Relationships
        'close friend': 'amigo cercano',
        'family member': 'miembro de la familia',
        'loved one': 'ser querido',
        'romantic partner': 'pareja romántica',
        'significant other': 'pareja',
        'boyfriend': 'novio',
        'girlfriend': 'novia',
        'husband': 'esposo',
        'wife': 'esposa',
        'child': 'niño/niña',
        'baby': 'bebé',
        'little one': 'pequeño/pequeña',
        'buddy': 'amigo',
        'pal': 'compañero',
        'mate': 'amigo',
        'dude': 'tipo',
        'guy': 'tipo',
        
        # Common words
        'person': 'persona',
        'individual': 'individuo',
        'someone': 'alguien',
        'anybody': 'cualquiera',
        'everyone': 'todos',
        'people': 'gente',
        
        # Verbs and actions
        'to steal': 'robar',
        'to rob': 'robar',
        'to sleep': 'dormir',
        'to nap': 'tomar una siesta',
        'to suggest': 'sugerir',
        'to indicate': 'indicar',
        'to describe': 'describir',
        'to mean': 'significar',
        'to imply': 'implicar',
        'to refer': 'referirse',
        'to use': 'usar',
        'to call': 'llamar',
        'to say': 'decir',
        'to speak': 'hablar',
        
        # Descriptive phrases
        'widely used': 'ampliamente usado',
        'commonly used': 'comúnmente usado',
        'frequently used': 'frecuentemente usado',
        'originates from': 'proviene de',
        'comes from': 'proviene de',
        'derives from': 'deriva de',
        'old Spanish': 'español antiguo',
        'popular language': 'lenguaje popular',
        'related to': 'relacionado con',
        'similar to': 'similar a',
        'similar in meaning': 'similar en significado',
        'same as': 'lo mismo que',
        'equivalent to': 'equivalente a',
        'at full speed': 'a toda velocidad',
        'at maximum intensity': 'a máxima intensidad',
        'very active': 'muy activo',
        'very excited': 'muy emocionado',
        'describes a state': 'describe un estado',
        'refers to a state': 'se refiere a un estado',
        'indicates a condition': 'indica una condición',
        
        # Structural phrases
        'this term': 'este término',
        'this word': 'esta palabra',
        'this expression': 'esta expresión',
        'this phrase': 'esta frase',
        'the term': 'el término',
        'the word': 'la palabra',
        'the expression': 'la expresión',
        'the phrase': 'la frase',
        'suggesting': 'sugiriendo',
        'indicating': 'indicando',
        'meaning': 'significando',
        'implying': 'implicando',
        
        # Simple words that often appear
        'word': 'palabra',
        'language': 'idioma',
        'dialect': 'dialecto',
        'slang': 'jerga',
        'term': 'término',
        'expression': 'expresión',
        'phrase': 'frase',
        'meaning': 'significado',
        'translation': 'traducción',
        'definition': 'definición',
    }
    
    # Get all Spanish entries
    spanish_entries = Entry.objects.filter(language_code='es-AR')
    total_entries = spanish_entries.count()
    fixed_count = 0
    
    print(f"Processing {total_entries} Spanish entries...")
    
    # Create or get tag for tracking cleaned entries
    cleaned_tag, created = Tag.objects.get_or_create(
        name='auto-translated',
        defaults={'description': 'Entry had English text automatically translated to Spanish', 'color': '#28a745'}
    )
    
    for i, entry in enumerate(spanish_entries, 1):
        if entry.notes:
            original_notes = entry.notes
            updated_notes = entry.notes
            
            # Apply translations
            for english, spanish in translations_map.items():
                if english.lower() in updated_notes.lower():
                    # Case-insensitive replacement
                    pattern = re.compile(re.escape(english), re.IGNORECASE)
                    updated_notes = pattern.sub(spanish, updated_notes)
            
            # If changes were made, save and tag the entry
            if updated_notes != original_notes:
                entry.notes = updated_notes
                entry.save()
                entry.tags.add(cleaned_tag)
                fixed_count += 1
                
                if fixed_count <= 5:  # Show first 5 examples
                    print(f"\nFixed '{entry.term}':")
                    print(f"  Before: {original_notes[:150]}...")
                    print(f"  After:  {updated_notes[:150]}...")
        
        # Progress indicator
        if i % 500 == 0:
            print(f"Processed {i}/{total_entries} entries... ({fixed_count} fixed)")
    
    print(f"\n✅ Cleaning complete!")
    print(f"📊 Results:")
    print(f"  - Total Spanish entries: {total_entries}")
    print(f"  - Entries fixed: {fixed_count}")
    print(f"  - Percentage fixed: {(fixed_count/total_entries)*100:.1f}%")
    print(f"  - Entries tagged as 'auto-translated': {fixed_count}")

if __name__ == '__main__':
    clean_english_from_spanish()
