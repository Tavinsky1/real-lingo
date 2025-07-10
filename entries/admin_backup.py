from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin # Import the special admin class
from .models import Tag, Entry, Translation, Example # Your models
from .resources import EntryResource # Your resource class

# Enhanced Tag admin with color support
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color_preview', 'entries_count', 'view_entries_link')
    search_fields = ('name', 'description')
    list_filter = ('color',)
    list_per_page = 25
    ordering = ('name',)
    
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;background-color:{};border:1px solid #ccc;border-radius:3px;"></span> {}',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'
    
    def entries_count(self, obj):
        return obj.entry_set.count()
    entries_count.short_description = 'Entries'
    entries_count.admin_order_field = 'entries_count'
    
    def view_entries_link(self, obj):
        url = reverse('admin:entries_entry_changelist') + f'?tags__id__exact={obj.id}'
        return format_html('<a href="{}">View Entries</a>', url)
    view_entries_link.short_description = 'View Entries'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(entries_count=Count('entry'))
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Display', {
            'fields': ('color',),
            'classes': ('collapse',)
        })
    )

class TranslationInline(admin.TabularInline):
    model = Translation
    extra = 1
    fields = ('target_language_code', 'translation', 'literal_translation')
    classes = ('collapse',)

class ExampleInline(admin.TabularInline):
    model = Example
    extra = 1
    fields = ('sentence', 'language_code', 'translation')
    classes = ('collapse',)

@admin.register(Entry)
class EntryAdmin(ImportExportModelAdmin):
    resource_classes = [EntryResource]
    list_display = ('term', 'language_code', 'category', 'region_code', 'tags_display', 'translations_count', 'examples_count', 'created_at')
    list_filter = ('language_code', 'category', 'region_code', 'tags', 'created_at')
    search_fields = ('term', 'notes', 'translations__translation', 'examples__sentence')
    filter_horizontal = ('tags',)
    inlines = [TranslationInline, ExampleInline]
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('term', 'language_code', 'region_code', 'category', 'part_of_speech')
        }),
        ('Content', {
            'fields': ('notes', 'tags'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tags_display(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()[:3]]) + ("..." if obj.tags.count() > 3 else "")
    tags_display.short_description = 'Tags'
    
    def translations_count(self, obj):
        return obj.translations.count()
    translations_count.short_description = 'Translations'
    
    def examples_count(self, obj):
        return obj.examples.count()
    examples_count.short_description = 'Examples'

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('entry', 'target_language_code', 'translation')
    list_filter = ('target_language_code',)
    search_fields = ('translation', 'literal_translation', 'entry__term')

@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ('entry', 'sentence', 'language_code')
    list_filter = ('language_code',)
    search_fields = ('sentence', 'translation', 'entry__term')