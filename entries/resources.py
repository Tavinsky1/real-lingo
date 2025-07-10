from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from .models import Entry, Tag

class EntryResource(resources.ModelResource):
    # Custom field for handling tags as comma-separated names
    tags = fields.Field(
        attribute='tags',
        widget=ManyToManyWidget(Tag, field='name', separator=',')
    )

    class Meta:
        model = Entry
        fields = ('id', 'term', 'language_code', 'region_code', 'category', 'part_of_speech', 'notes', 'tags', 'created_at', 'updated_at')
        skip_unchanged = True
        report_skipped = True

    # If you need to create Tags on the fly during import if they don't exist based on a comma-separated string in a 'tags' column:
    def before_import_row(self, row, **kwargs):
        tag_names_str = row.get('tags')
        if tag_names_str:
            tag_names = [name.strip().lower() for name in tag_names_str.split(',') if name.strip()]
            tags_for_row = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tags_for_row.append(tag.pk) # django-import-export expects pks for M2M by default
            row['tags'] = ','.join(map(str, tags_for_row)) # Convert back to comma-separated PKs for the widget