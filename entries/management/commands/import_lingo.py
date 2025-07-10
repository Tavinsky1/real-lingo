import csv
from django.core.management.base import BaseCommand, CommandError
from entries.models import Entry, Tag # Assuming your app is named 'entries'

class Command(BaseCommand):
    help = 'Imports lingo entries from a specified CSV file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The path to the CSV file to import.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file_path']
        self.stdout.write(self.style.SUCCESS(f'Starting import from "{csv_file_path}"...'))

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                if not reader.fieldnames:
                    raise CommandError(f"CSV file '{csv_file_path}' is empty or has no headers.")

                # Check available headers and map them
                available_headers = set(reader.fieldnames)
                
                # Map CSV headers to our expected field names
                header_mapping = {
                    'Term_Phrase_Item': 'term',  # Handle the actual CSV header
                    'term': 'term',              # Also handle if it's already correct
                }
                
                # Required headers that must exist in some form
                required_mapping = {
                    'language_code': 'language_code',
                    'category': 'category',
                    'notes': 'notes',
                    'tags': 'tags'
                }
                
                # Check that we can map all required fields
                for csv_field, model_field in required_mapping.items():
                    if csv_field not in available_headers:
                        raise CommandError(
                            f"Missing required header '{csv_field}' in CSV file. "
                            f"Found headers: {', '.join(reader.fieldnames)}"
                        )
                
                # Check for term field
                term_field = None
                for possible_term in ['Term_Phrase_Item', 'term']:
                    if possible_term in available_headers:
                        term_field = possible_term
                        break
                
                if not term_field:
                    raise CommandError(
                        f"No term field found. Expected 'term' or 'Term_Phrase_Item'. "
                        f"Found headers: {', '.join(reader.fieldnames)}"
                    )

                entries_created_count = 0
                entries_updated_count = 0
                tags_created_count = 0

                for row_num, row in enumerate(reader, 1):
                    term = row.get(term_field, '').strip()  # Use the dynamic term field
                    language_code = row.get('language_code', '').strip()

                    if not term or not language_code:
                        self.stdout.write(self.style.WARNING(f"Skipping row {row_num}: 'term' and 'language_code' are required. Found term='{term}', lang='{language_code}'"))
                        continue

                    # Prepare data for Entry model
                    entry_data = {
                        'language_code': language_code,
                        'category': row.get('category', 'OTHER').upper() or 'OTHER', # Ensure category is not empty
                        'region_code': row.get('region_code', '').strip() or None, # Use None for blank
                        'part_of_speech': row.get('part_of_speech', '').strip() or None,
                        'notes': row.get('notes', '').strip() or None,
                    }

                    # Update or create Entry
                    # Using term and language_code as unique identifiers for an entry
                    entry, created = Entry.objects.update_or_create(
                        term=term,
                        language_code=language_code, # Assuming term + language_code is unique
                        defaults=entry_data
                    )

                    if created:
                        entries_created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Created new entry: '{entry.term}' ({entry.language_code})"))
                    else:
                        entries_updated_count += 1
                        self.stdout.write(self.style.NOTICE(f"Updated existing entry: '{entry.term}' ({entry.language_code})"))

                    # Handle Tags
                    tag_names_str = row.get('tags', '').strip()
                    if tag_names_str:
                        tag_names = [name.strip() for name in tag_names_str.split(',') if name.strip()]
                        current_tags = []
                        for tag_name in tag_names:
                            tag, tag_created = Tag.objects.get_or_create(name=tag_name.lower()) # Store tags in lowercase for consistency
                            if tag_created:
                                tags_created_count += 1
                                self.stdout.write(f"  Created new tag: '{tag.name}'")
                            current_tags.append(tag)
                        entry.tags.set(current_tags) # Use set() to manage ManyToMany relationships

        except FileNotFoundError:
            raise CommandError(f"CSV file not found at '{csv_file_path}'")
        except Exception as e:
            raise CommandError(f"An error occurred during import: {e}")

        self.stdout.write(self.style.SUCCESS(f"\nImport completed."))
        self.stdout.write(f"Entries created: {entries_created_count}")
        self.stdout.write(f"Entries updated: {entries_updated_count}")
        self.stdout.write(f"Tags created: {tags_created_count}")