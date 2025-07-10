from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from import_export.admin import ImportExportModelAdmin
from .models import Tag, Entry, Translation, Example
from .resources import EntryResource

# Enhanced Tag admin with color support and analytics
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color_preview', 'entries_count', 'view_entries_link')
    search_fields = ('name', 'description')
    list_filter = ('color',)
    list_per_page = 25
    ordering = ('name',)
    actions = ['merge_tags', 'assign_random_colors']
    
    def color_preview(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;background-color:{};border:1px solid #ccc;border-radius:3px;margin-right:5px;"></span>{}',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'
    
    def entries_count(self, obj):
        count = getattr(obj, 'entries_count', None)
        if count is None:
            count = obj.entry_set.count()
        return count
    entries_count.short_description = 'Entries'
    entries_count.admin_order_field = 'entries_count'
    
    def view_entries_link(self, obj):
        url = reverse('admin:entries_entry_changelist') + f'?tags__id__exact={obj.id}'
        return format_html('<a href="{}">View {} Entries</a>', url, self.entries_count(obj))
    view_entries_link.short_description = 'View Entries'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(entries_count=Count('entry'))
    
    def merge_tags(self, request, queryset):
        """Merge selected tags into the first one."""
        if queryset.count() < 2:
            self.message_user(request, "Please select at least 2 tags to merge.", level='warning')
            return
        
        primary_tag = queryset.first()
        tags_to_merge = queryset.exclude(pk=primary_tag.pk)
        
        # Move all entries from other tags to primary tag
        for tag in tags_to_merge:
            for entry in tag.entry_set.all():
                entry.tags.add(primary_tag)
                entry.tags.remove(tag)
        
        # Delete the merged tags
        merged_count = tags_to_merge.count()
        tags_to_merge.delete()
        
        self.message_user(
            request, 
            f'Successfully merged {merged_count} tags into "{primary_tag.name}".'
        )
    merge_tags.short_description = "Merge selected tags into the first one"
    
    def assign_random_colors(self, request, queryset):
        """Assign random colors to selected tags."""
        import random
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#F38BA8', '#A8DADC']
        
        for tag in queryset:
            tag.color = random.choice(colors)
            tag.save()
        
        self.message_user(request, f'Assigned random colors to {queryset.count()} tags.')
    assign_random_colors.short_description = "Assign random colors to selected tags"
    
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
    list_display = ('term', 'language_code', 'category', 'region_code', 'tags_display', 'translations_count', 'examples_count', 'completion_status', 'created_at')
    list_filter = ('language_code', 'category', 'region_code', 'tags', 'created_at', 'updated_at')
    search_fields = ('term', 'notes', 'translations__translation', 'examples__sentence', 'tags__name')
    filter_horizontal = ('tags',)
    inlines = [TranslationInline, ExampleInline]
    readonly_fields = ('created_at', 'updated_at', 'completion_score')
    date_hierarchy = 'created_at'
    list_per_page = 50
    actions = ['mark_as_reviewed', 'bulk_add_tag', 'export_to_csv']
    
    fieldsets = (
        (None, {
            'fields': ('term', 'language_code', 'region_code', 'category', 'part_of_speech')
        }),
        ('Content', {
            'fields': ('notes', 'tags'),
            'classes': ('wide',)
        }),
        ('Analytics', {
            'fields': ('completion_score',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related().prefetch_related('tags', 'translations', 'examples').annotate(
            translations_count=Count('translations', distinct=True),
            examples_count=Count('examples', distinct=True),
            tags_count=Count('tags', distinct=True)
        )
    
    def tags_display(self, obj):
        tags = obj.tags.all()[:3]
        if not tags:
            return "No tags"
        
        display = ", ".join([
            format_html('<span style="background-color:{};color:white;padding:2px 5px;border-radius:3px;font-size:11px;">{}</span>', 
                       tag.color, tag.name) for tag in tags
        ])
        
        if obj.tags.count() > 3:
            display += f" <small>(+{obj.tags.count() - 3} more)</small>"
        
        return format_html(display)
    tags_display.short_description = 'Tags'
    
    def translations_count(self, obj):
        count = getattr(obj, 'translations_count', None)
        if count is None:
            count = obj.translations.count()
        return count
    translations_count.short_description = 'Translations'
    translations_count.admin_order_field = 'translations_count'
    
    def examples_count(self, obj):
        count = getattr(obj, 'examples_count', None)
        if count is None:
            count = obj.examples.count()
        return count
    examples_count.short_description = 'Examples'
    examples_count.admin_order_field = 'examples_count'
    
    def completion_status(self, obj):
        score = self.completion_score(obj)
        if score >= 80:
            color = '#28a745'  # Green
            status = 'Complete'
        elif score >= 50:
            color = '#ffc107'  # Yellow
            status = 'Partial'
        else:
            color = '#dc3545'  # Red
            status = 'Incomplete'
        
        return format_html(
            '<span style="color:{};font-weight:bold;">{} ({}%)</span>',
            color, status, score
        )
    completion_status.short_description = 'Completion'
    
    def completion_score(self, obj):
        """Calculate completion score based on available data."""
        score = 20  # Base score for having a term
        
        if obj.notes:
            score += 20
        if hasattr(obj, 'translations_count') and obj.translations_count > 0:
            score += 25
        elif obj.translations.exists():
            score += 25
        if hasattr(obj, 'examples_count') and obj.examples_count > 0:
            score += 25
        elif obj.examples.exists():
            score += 25
        if hasattr(obj, 'tags_count') and obj.tags_count > 0:
            score += 10
        elif obj.tags.exists():
            score += 10
            
        return score
    completion_score.short_description = 'Completion Score (%)'
    
    def mark_as_reviewed(self, request, queryset):
        """Mark selected entries as reviewed by adding a 'reviewed' tag."""
        reviewed_tag, created = Tag.objects.get_or_create(
            name='reviewed',
            defaults={'description': 'Entry has been reviewed', 'color': '#28a745'}
        )
        
        count = 0
        for entry in queryset:
            entry.tags.add(reviewed_tag)
            count += 1
        
        self.message_user(request, f'Marked {count} entries as reviewed.')
    mark_as_reviewed.short_description = "Mark selected entries as reviewed"
    
    def bulk_add_tag(self, request, queryset):
        """Add a tag to all selected entries."""
        # This would typically show a form, but for simplicity, we'll add a 'bulk-processed' tag
        bulk_tag, created = Tag.objects.get_or_create(
            name='bulk-processed',
            defaults={'description': 'Processed in bulk', 'color': '#6c757d'}
        )
        
        count = 0
        for entry in queryset:
            entry.tags.add(bulk_tag)
            count += 1
        
        self.message_user(request, f'Added "bulk-processed" tag to {count} entries.')
    bulk_add_tag.short_description = "Add bulk-processed tag to selected entries"

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ('entry_term', 'target_language_code', 'translation', 'has_literal')
    list_filter = ('target_language_code', 'entry__language_code', 'entry__category')
    search_fields = ('translation', 'literal_translation', 'entry__term')
    autocomplete_fields = ['entry']
    list_per_page = 50
    
    def entry_term(self, obj):
        return obj.entry.term
    entry_term.short_description = 'Entry Term'
    entry_term.admin_order_field = 'entry__term'
    
    def has_literal(self, obj):
        return bool(obj.literal_translation)
    has_literal.boolean = True
    has_literal.short_description = 'Has Literal'

@admin.register(Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ('entry_term', 'sentence_preview', 'language_code', 'has_translation')
    list_filter = ('language_code', 'entry__language_code', 'entry__category')
    search_fields = ('sentence', 'translation', 'entry__term')
    autocomplete_fields = ['entry']
    list_per_page = 50
    
    def entry_term(self, obj):
        return obj.entry.term
    entry_term.short_description = 'Entry Term'
    entry_term.admin_order_field = 'entry__term'
    
    def sentence_preview(self, obj):
        return obj.sentence[:50] + '...' if len(obj.sentence) > 50 else obj.sentence
    sentence_preview.short_description = 'Sentence'
    
    def has_translation(self, obj):
        return bool(obj.translation)
    has_translation.boolean = True
    has_translation.short_description = 'Has Translation'

# Customize admin site headers
admin.site.site_header = "Lingo Dictionary Administration"
admin.site.site_title = "Lingo Dictionary Admin"
admin.site.index_title = "Welcome to Lingo Dictionary Administration"
