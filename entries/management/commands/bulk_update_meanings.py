"""
Django management command for bulk updating curated meanings.
Usage: 
    python manage.py bulk_update_meanings --csv-file curated_meanings.csv
    python manage.py bulk_update_meanings --json-file curated_meanings.json
    python manage.py bulk_update_meanings --export-template
"""

import csv
import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from entries.models import Entry

class Command(BaseCommand):
    help = 'Bulk update curated meanings from CSV or JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            help='CSV file with curated meanings to import'
        )
        parser.add_argument(
            '--json-file',
            type=str,
            help='JSON file with curated meanings to import'
        )
        parser.add_argument(
            '--export-template',
            action='store_true',
            help='Export template files for bulk editing'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        parser.add_argument(
            '--filter-language',
            type=str,
            help='Only process entries for specific language (e.g., es-AR)'
        )
        parser.add_argument(
            '--filter-category',
            type=str,
            help='Only process entries for specific category (e.g., slang)'
        )

    def handle(self, *args, **options):
        if options['export_template']:
            self.export_templates()
        elif options['csv_file']:
            self.import_from_csv(options)
        elif options['json_file']:
            self.import_from_json(options)
        else:
            raise CommandError('Please specify --csv-file, --json-file, or --export-template')

    def export_templates(self):
        """Export template files for bulk editing."""
        # Create templates directory
        os.makedirs('curation_templates', exist_ok=True)
        
        # Export CSV template
        csv_filename = 'curation_templates/meanings_template.csv'
        self._export_csv_template(csv_filename)
        
        # Export JSON template
        json_filename = 'curation_templates/meanings_template.json'
        self._export_json_template(json_filename)
        
        # Export current entries for editing
        current_csv = 'curation_templates/current_entries_for_editing.csv'
        self._export_current_entries(current_csv)
        
        self.stdout.write(
            self.style.SUCCESS(f'Template files exported to curation_templates/')
        )
        self.stdout.write(f'  - {csv_filename}: CSV template with examples')
        self.stdout.write(f'  - {json_filename}: JSON template with examples')
        self.stdout.write(f'  - {current_csv}: Current entries ready for editing')

    def _export_csv_template(self, filename):
        """Export CSV template with examples."""
        template_data = [
            {
                'id': 'EXAMPLE',
                'term': 'che',
                'language_code': 'es-AR',
                'category': 'slang',
                'meaning_es': 'Interjección para llamar la atención, como "oye".',
                'meaning_en': 'Hey, dude (common interjection).',
                'notes': 'Very common in Argentina, used between friends',
                'action': 'UPDATE'
            },
            {
                'id': 'EXAMPLE2',
                'term': 'boludo',
                'language_code': 'es-AR',
                'category': 'slang',
                'meaning_es': 'Persona tonta o amigo, según el contexto.',
                'meaning_en': 'Dude or idiot, depending on context.',
                'notes': 'Can be friendly or insulting based on tone',
                'action': 'UPDATE'
            }
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=template_data[0].keys())
            writer.writeheader()
            writer.writerows(template_data)

    def _export_json_template(self, filename):
        """Export JSON template with examples."""
        template_data = {
            "instructions": {
                "format": "Each entry should have these fields",
                "required_fields": ["id", "action"],
                "optional_fields": ["meaning_es", "meaning_en", "notes"],
                "actions": ["UPDATE", "SKIP"],
                "notes": "Leave meaning fields empty to not update them"
            },
            "entries": [
                {
                    "id": 123,
                    "term": "che",
                    "current_meaning_es": "",
                    "current_meaning_en": "",
                    "meaning_es": "Interjección para llamar la atención, como 'oye'.",
                    "meaning_en": "Hey, dude (common interjection).",
                    "notes": "Very common in Argentina",
                    "action": "UPDATE"
                }
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)

    def _export_current_entries(self, filename):
        """Export current entries that need curation."""
        # Get entries that need meanings
        entries_to_export = []
        
        # Prioritize entries without curated meanings
        priority_entries = Entry.objects.filter(
            category__in=['slang', 'colloquial_phrases', 'insults']
        ).order_by('language_code', 'term')
        
        for entry in priority_entries[:500]:  # Limit to manageable number
            current_meaning_es = getattr(entry, 'meaning_es', '') or ''
            current_meaning_en = getattr(entry, 'meaning_en', '') or ''
            
            # Only include if missing curated meanings
            if not current_meaning_es and not current_meaning_en:
                entries_to_export.append({
                    'id': entry.id,
                    'term': entry.term,
                    'language_code': entry.language_code,
                    'category': entry.category,
                    'current_notes': (getattr(entry, 'notes', '') or '')[:200],
                    'current_meaning_es': current_meaning_es,
                    'current_meaning_en': current_meaning_en,
                    'meaning_es': '',  # To be filled
                    'meaning_en': '',  # To be filled
                    'notes': '',  # To be filled
                    'action': 'UPDATE'
                })
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if entries_to_export:
                writer = csv.DictWriter(f, fieldnames=entries_to_export[0].keys())
                writer.writeheader()
                writer.writerows(entries_to_export)
        
        self.stdout.write(f'Exported {len(entries_to_export)} entries needing curation')

    def import_from_csv(self, options):
        """Import curated meanings from CSV file."""
        csv_file = options['csv_file']
        dry_run = options['dry_run']
        
        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')
        
        updates = []
        errors = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                try:
                    entry_id = row.get('id')
                    action = row.get('action', '').upper()
                    
                    if action != 'UPDATE':
                        continue
                    
                    if not entry_id or entry_id == 'EXAMPLE':
                        continue
                    
                    entry = Entry.objects.get(id=int(entry_id))
                    
                    # Apply filters if specified
                    if options['filter_language'] and entry.language_code != options['filter_language']:
                        continue
                    if options['filter_category'] and entry.category != options['filter_category']:
                        continue
                    
                    update_data = {}
                    
                    # Check for meaning updates
                    if 'meaning_es' in row and row['meaning_es'].strip():
                        update_data['meaning_es'] = row['meaning_es'].strip()
                    
                    if 'meaning_en' in row and row['meaning_en'].strip():
                        update_data['meaning_en'] = row['meaning_en'].strip()
                    
                    if 'notes' in row and row['notes'].strip():
                        update_data['notes'] = row['notes'].strip()
                    
                    if update_data:
                        updates.append({
                            'entry': entry,
                            'data': update_data,
                            'row': row_num
                        })
                    
                except Entry.DoesNotExist:
                    errors.append(f'Row {row_num}: Entry ID {entry_id} not found')
                except ValueError:
                    errors.append(f'Row {row_num}: Invalid entry ID {entry_id}')
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
        
        # Show summary
        self.stdout.write(f'Found {len(updates)} entries to update')
        if errors:
            self.stdout.write(self.style.WARNING(f'Found {len(errors)} errors:'))
            for error in errors[:10]:  # Show first 10 errors
                self.stdout.write(f'  {error}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
            for update in updates[:5]:  # Show first 5 updates
                entry = update['entry']
                data = update['data']
                self.stdout.write(f'  Would update {entry.term} ({entry.id}):')
                for field, value in data.items():
                    self.stdout.write(f'    {field}: {value[:50]}...')
            return
        
        # Perform updates
        if updates:
            with transaction.atomic():
                updated_count = 0
                for update in updates:
                    entry = update['entry']
                    data = update['data']
                    
                    for field, value in data.items():
                        setattr(entry, field, value)
                    
                    entry.save(update_fields=list(data.keys()))
                    updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated {updated_count} entries')
                )

    def import_from_json(self, options):
        """Import curated meanings from JSON file."""
        json_file = options['json_file']
        dry_run = options['dry_run']
        
        if not os.path.exists(json_file):
            raise CommandError(f'JSON file not found: {json_file}')
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries_data = data.get('entries', [])
        updates = []
        errors = []
        
        for i, entry_data in enumerate(entries_data):
            try:
                entry_id = entry_data.get('id')
                action = entry_data.get('action', '').upper()
                
                if action != 'UPDATE':
                    continue
                
                entry = Entry.objects.get(id=int(entry_id))
                
                # Apply filters if specified
                if options['filter_language'] and entry.language_code != options['filter_language']:
                    continue
                if options['filter_category'] and entry.category != options['filter_category']:
                    continue
                
                update_data = {}
                
                # Check for meaning updates
                if entry_data.get('meaning_es', '').strip():
                    update_data['meaning_es'] = entry_data['meaning_es'].strip()
                
                if entry_data.get('meaning_en', '').strip():
                    update_data['meaning_en'] = entry_data['meaning_en'].strip()
                
                if entry_data.get('notes', '').strip():
                    update_data['notes'] = entry_data['notes'].strip()
                
                if update_data:
                    updates.append({
                        'entry': entry,
                        'data': update_data,
                        'index': i
                    })
                
            except Entry.DoesNotExist:
                errors.append(f'Entry {i}: Entry ID {entry_id} not found')
            except Exception as e:
                errors.append(f'Entry {i}: {str(e)}')
        
        # Show summary and perform updates (similar to CSV logic)
        self.stdout.write(f'Found {len(updates)} entries to update from JSON')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
            return
        
        if updates:
            with transaction.atomic():
                updated_count = 0
                for update in updates:
                    entry = update['entry']
                    data = update['data']
                    
                    for field, value in data.items():
                        setattr(entry, field, value)
                    
                    entry.save(update_fields=list(data.keys()))
                    updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated {updated_count} entries from JSON')
                )