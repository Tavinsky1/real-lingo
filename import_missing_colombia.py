#!/usr/bin/env python3
"""
Script to import the missing Colombian colloquial phrases and unique concepts.
"""

import os
import sys
import django

# Set up Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry, Tag, Translation, Example

def import_missing_entries():
    """Import the specific missing entries."""
    
    print("🇨🇴 Importing missing Colombian colloquial phrases and unique concepts...")
    
    # The missing entries data
    missing_entries = [
        # Colloquial Phrases
        ("Colloquial Phrase", "No saber ni papa de algo", "Not knowing a potato about something", "Having zero knowledge about something", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "Tirar / Botar la casa por la ventana", "To throw the house out of the window", "To go all out (for a celebration)", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "Ponerse las pilas", "To put on the batteries", "To get to work, to get serious, to become alert", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "Ser pan comido", "To be eaten bread", "To be a piece of cake (easy)", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "Hacer su agosto", "To make one's August", "To make hay while the sun shines; to take advantage of a good situation", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "Estar vivito y coleando", "To be alive and wagging", "To be alive and kicking", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "Creerse la última Coca-Cola del desierto", "To think of oneself as the last Coca-Cola in the desert", "To be arrogant, cocky, think highly of oneself", "Ella es tan mandona y arrogante, se cree la ultima Coca-Cola del desierto.", "She is so bossy and cocky, she thinks she's the shit.", "", "", ""),
        ("Colloquial Phrase", "Feliz como una lombriz", "Happy as a worm", "Happy as a clam", "Mi hermana estaba feliz como una lombriz cuando compró su nuevo apartamento.", "My sister was happy as a clam when she bought her new flat.", "", "", ""),
        ("Colloquial Phrase", "Aunque la mona se vista de seda, mona se queda", "Though the monkey dresses in silk, it remains a monkey", "Superficial changes don't alter true nature; all show and no go", "", "", "[30]", "", ""),
        ("Colloquial Phrase", "El burro hablando de orejas", "The donkey talking about ears", "The pot calling the kettle black", "¡No me digas que hacer! Qué gracioso, el burro hablando de orejas.", "Don't tell me what to do! How funny, the pot calling the kettle black.", "", "", ""),
        ("Colloquial Phrase", "Tener mala leche", "To have bad milk", "To have bad luck", "Después del divorcio, Andrés perdió su trabajo. ¡Que mala leche tiene!", "After the divorce, Andrés lost his job. What bad luck the poor guy has!", "", "", ""),
        ("Colloquial Phrase", "Estar loco como una cabra", "To be crazy as a goat", "To be nuts, crazy, out of one's mind", "Él está pensando en subir El Monte Everest... está loco como una cabra.", "He's thinking about climbing Mount Everest... he's nuts!", "", "", ""),
        ("Colloquial Phrase", "Dar lata", "To give can", "To bother, to annoy", "La hermana de Jessica siempre le da lata.", "Jessica's sister always drones on.", "", "", ""),
        ("Colloquial Phrase", "No le cabe ni un tinto", "Not even a tinto fits", "A place is so crowded that not even a cup of coffee can make it in", "", "", "", "", ""),
        ("Colloquial Phrase", "Como Pedro por su casa", "Like Peter in his own house", "Someone acts as if they own the place", "", "", "", "", ""),
        ("Colloquial Phrase", "Lo que no mata, engorda", "What doesn't kill, fattens", "Even if your food falls to the ground, the worst that can happen after eating it is getting fat", "", "", "", "", ""),
        ("Colloquial Phrase", "¿Durmió conmigo anoche o qué?", "Did you sleep with me last night or what?", "Used when someone enters a place without greeting", "", "", "", "", ""),
        ("Colloquial Phrase", "Tengo un filo, que si me agacho me corto", "I have a blade, if I bend over I cut myself", "You are very hungry", "", "", "", "", ""),
        ("Colloquial Phrase", "Uyy, ¿quién pidió pollo?", "Uyy, who ordered chicken?", "Used to joke around or flirt with friends when someone handsome/pretty approaches or passes by", "", "", "", "", ""),
        ("Colloquial Phrase", "No me abra los ojos que no le voy a echar gotas", "Don't open your eyes like that I am not going to put eyedrops on them", "Used when someone doesn't like you -or doesn't like something you said-", "", "", "", "", ""),
        ("Colloquial Phrase", "¿Qué come que adivina?", "What do you eat that you guess?", "Used when someone guesses what you are thinking or about to say", "", "", "", "", ""),
        ("Colloquial Phrase", "El que tiene tienda que la atienda", "He who has a shop should attend to it", "If you have something, take care of it", "", "", "", "", ""),
        ("Colloquial Phrase", "Le cuento el milagro pero no el santo", "I tell you the miracle but not the saint", "They would tell you the 'secret' or 'gossip' but not who told them", "", "", "", "", ""),
        ("Colloquial Phrase", "Colgó los guayos", "(He or she) hung the soccer shoes", "Someone died", "", "", "", "", ""),
        ("Colloquial Phrase", "¡Que entre el diablo y escoja!", "Let the devil come and choose!", "You have two options but you don't like any, basically, you are screwed either way", "", "", "", "", ""),
        ("Colloquial Phrase", "Es pan comido", "It's an eaten bread", "It's a piece of cake", "", "", "", "", ""),
        ("Colloquial Phrase", "Virgen del agarradero (agárrame a mi primero)", "Virgin of the handgrip (grab me first)", "A funny way of saying \"oh my God\" or \"God, save me!\" when afraid", "", "", "", "", ""),
        ("Colloquial Phrase", "Lo que le diga es mentira", "Whatever I tell you is a lie", "Used to indicate uncertainty or inability to provide a definitive answer", "", "", "", "", ""),
        
        # Unique Concepts
        ("Unique Concept", "Tinto", "Black coffee", "Small cup of black coffee (not red wine)", "", "", "Ubiquitous beverage, reflects coffee culture. [3, 15, 17, 18, 22, 23, 41]", "", ""),
        ("Unique Concept", "Arepa", "Circular corn cake", "A staple food in Colombia with regional variations", "", "", "Eaten any time of day; e.g., plain white, cheese-filled, \"Arepa de Huevo\". [22]", "", ""),
        ("Unique Concept", "Ñapa", "-", "A little \"extra\" given for free by a vendor, as a kind gesture", "", "", "Common practice, reflects generosity and informal bargaining. [18, 22]", "", ""),
        ("Unique Concept", "Rumba", "Cuban music and dance style", "Party or fiesta", "", "", "Lively celebrations with dancing, music, aguardiente. Verb \"rumbear\" means to party. [3, 15, 20, 22]", "", ""),
        ("Unique Concept", "Tejo", "-", "Colombia's national sport: throwing a metal puck at a gunpowder target for an explosion", "", "", "Often accompanied by drinking beer; losing team pays. [41, 42]", "", ""),
        ("Unique Concept", "Día de las Velitas", "-", "Day of the Little Candles (Christmas tradition)", "", "", "December 7th. [22, 41]", "", ""),
        ("Unique Concept", "La Novena de Aguinaldos", "-", "Nine days of carols and prayers before Christmas", "", "", "December 16th to Christmas Eve. Families gather. [22, 41]", "", ""),
        ("Unique Concept", "Buñuelos", "-", "Fried dough balls (Christmas food)", "", "", "Traditional Christmas food. [22, 41]", "", ""),
        ("Unique Concept", "Natilla", "-", "Type of custard (Christmas food)", "", "", "Traditional Christmas food. [22, 41]", "", ""),
        ("Unique Concept", "New Year's Traditions", "-", "Eating 12 grapes, yellow underwear, lentils in pockets, suitcase around the block", "", "", "For wishes, luck, abundance, travel. [41, 43]", "", ""),
        ("Unique Concept", "Quemar el Año Viejo", "-", "Burning a scarecrow-like doll at midnight on New Year's Eve", "", "", "To ward off negativity. [41, 43]", "", ""),
        ("Unique Concept", "Cheese Consumption", "-", "Combination of cheese with sweet dishes (e.g., in hot chocolate or fruit salads)", "", "", "Peculiar but widespread practice. [22, 41]", "", ""),
        ("Unique Concept", "Menú del Día", "-", "Common, budget-friendly lunch menu (soup, main course, juice, dessert)", "", "", "Found throughout the country. [41]", "", ""),
        ("Unique Concept", "Voseo", "-", "Use of \"vos\" instead of \"tú\" for \"you\"", "", "", "Characteristic of Paisa Region and Valle del Cauca. [7]", "", ""),
        ("Unique Concept", "Su merced", "Your mercy", "Formal second-person singular pronoun, often pronounced \"su mercé\"", "Y su merced, ¿qué dice?", "And you, what do you say?", "Used in Cundinamarca and Boyacá, replaces \"usted\". [7, 28]", "", ""),
        ("Unique Concept", "Accent Features (Rolo/Cachaco)", "-", "Clarity and prestige; preserves syllable-final /s/, 'll'/'y' distinction", "", "", "Bogotá dialect. [1, 2, 7]", "", ""),
        ("Unique Concept", "Accent Features (Costeño)", "-", "Faster speech; aspiration/deletion of syllable-final /s/; velar word-final /n/", "", "", "Caribbean/Coastal dialects. [5, 7]", "", ""),
        ("Unique Concept", "Accent Features (Chocó)", "-", "African influences in rhythm and intonation", "", "", "Pacific dialect. [1, 7]", "", ""),
        ("Unique Concept", "Diminutives and Augmentatives", "-", "Suffixes altering size, tone (affection, anger, politeness); usage varies by region", "", "", "", "", ""),
        ("Unique Concept", "Indirect Communication", "-", "More information conveyed through body language and context; protects relationships/face", "", "", "\"I will have to see\" might implicitly mean \"no\". [11, 12]", "", ""),
        ("Unique Concept", "The \"Pues\" Particle", "Well", "Filler word, casual conversational tag, or intensifier", "", "", "Frequently added to end of sentences, especially in Medellín. [2, 28]", "", ""),
    ]
    
    entries_added = 0
    entries_skipped = 0
    
    for entry_data in missing_entries:
        try:
            category, term, literal_meaning, slang_meaning, usage_example_es, usage_example_en, regional_notes, severity, gender_notes = entry_data
            
            # Clean the data
            def clean_text(text):
                if not text or text == '-' or text.lower() == 'n/a':
                    return ''
                return text.strip()
            
            term = clean_text(term)
            literal_meaning = clean_text(literal_meaning)
            slang_meaning = clean_text(slang_meaning)
            usage_example_es = clean_text(usage_example_es)
            usage_example_en = clean_text(usage_example_en)
            regional_notes = clean_text(regional_notes)
            severity = clean_text(severity)
            gender_notes = clean_text(gender_notes)
            
            # Map category to standardized format
            if category == "Colloquial Phrase":
                standardized_category = 'colloquial_phrases'
            elif category == "Unique Concept":
                standardized_category = 'unique_concepts'
            else:
                standardized_category = 'slang'
            
            # Check if entry already exists
            existing_entry = Entry.objects.filter(
                term=term, 
                language_code='es-CO'
            ).first()
            
            if existing_entry:
                print(f"⏭️  Skipping existing entry: {term}")
                entries_skipped += 1
                continue
            
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
            
            # Create the entry
            entry = Entry.objects.create(
                term=term,
                language_code='es-CO',
                region_code='CO',
                category=standardized_category,
                notes=notes,
                part_of_speech=''
            )
            
            # Add translation if available
            if slang_meaning:
                Translation.objects.create(
                    entry=entry,
                    target_language_code='en',
                    translation=slang_meaning
                )
            
            # Add example if available
            if usage_example_es and usage_example_en:
                Example.objects.create(
                    entry=entry,
                    sentence=usage_example_es,
                    language_code='es-CO',
                    translation=usage_example_en
                )
            
            # Add tags
            tags_to_add = ['Colombian']
            if category == "Colloquial Phrase":
                tags_to_add.append('Phrase')
            elif category == "Unique Concept":
                tags_to_add.append('Cultural')
            
            # Add specific tags based on content
            if 'Christmas' in slang_meaning or 'Christmas' in regional_notes:
                tags_to_add.append('Holiday')
            if 'food' in slang_meaning.lower() or 'coffee' in slang_meaning.lower():
                tags_to_add.append('Food')
            if 'sport' in slang_meaning.lower():
                tags_to_add.append('Sports')
            if 'dialect' in regional_notes.lower() or 'accent' in term.lower():
                tags_to_add.append('Regional')
            
            for tag_name in tags_to_add:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                entry.tags.add(tag)
            
            entries_added += 1
            print(f"✅ Added: {term} ({standardized_category})")
            
        except Exception as e:
            print(f"❌ Error processing entry {term}: {e}")
            entries_skipped += 1
            continue
    
    print(f"\n🎉 Import complete!")
    print(f"   ✅ Entries added: {entries_added}")
    print(f"   ⏭️  Entries skipped: {entries_skipped}")
    
    return entries_added

def get_updated_stats():
    """Get updated statistics about Colombian entries."""
    from django.db.models import Count
    
    total_entries = Entry.objects.filter(language_code='es-CO').count()
    
    print(f"\n📊 Updated Colombian entries statistics:")
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
    print("🇨🇴 Adding Missing Colombian Entries")
    print("=" * 40)
    
    # Import the missing entries
    entries_added = import_missing_entries()
    
    if entries_added > 0:
        print("\n" + "=" * 40)
        get_updated_stats()
    
    print("\n🎯 Missing Colombian entries have been added! 🇨🇴✨")
