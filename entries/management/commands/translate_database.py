from django.core.management.base import BaseCommand
from django.utils import translation
from entries.models import Entry, Translation, Example
from entries.translations import TRANSLATIONS
import json

class Command(BaseCommand):
    help = 'Translate database content based on user language preference'

    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            default='es',
            help='Target language for translation (default: es)'
        )

    def handle(self, *args, **options):
        target_language = options['language']
        
        if target_language not in TRANSLATIONS:
            self.stdout.write(
                self.style.ERROR(f'Language {target_language} not supported')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Starting translation to {target_language}')
        )

        # Translate categories
        category_translations = TRANSLATIONS[target_language].get('categories', {})
        
        # Update entries with translated categories
        for entry in Entry.objects.all():
            if entry.category and entry.category in category_translations:
                entry.category = category_translations[entry.category]
                entry.save()
                self.stdout.write(f'Translated category for entry: {entry.term}')

        # Create Spanish translations for entries that don't have them
        spanish_translations_created = 0
        for entry in Entry.objects.all():
            # Check if Spanish translation already exists
            if not entry.translations.filter(target_language_code='es').exists():
                # Create a basic translation (you might want to use a translation API here)
                Translation.objects.create(
                    entry=entry,
                    target_language_code='es',
                    translation=f'[Traducción al español de: {entry.term}]',
                    literal_translation=f'[Traducción literal de: {entry.term}]'
                )
                spanish_translations_created += 1

        self.stdout.write(
            self.style.SUCCESS(f'Created {spanish_translations_created} Spanish translations')
        )

        # Translate examples
        examples_translated = 0
        for example in Example.objects.all():
            if not example.translation and example.language_code != 'es':
                # Create Spanish translation for example
                example.translation = f'[Traducción al español del ejemplo: {example.sentence[:50]}...]'
                example.save()
                examples_translated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Translated {examples_translated} examples')
        )

        self.stdout.write(
            self.style.SUCCESS('Database translation completed!')
        ) 