from django.contrib import admin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from import_export.admin import ImportExportModelAdmin
from .models import Tag, Entry, Translation, Example, UserFavorite, UserProgress, UserAnalytics, Feedback
from .resources import EntryResource
import re

# Custom admin filters
class EnglishInSpanishFilter(admin.SimpleListFilter):
    title = 'Language Issues'
    parameter_name = 'language_issues'
    
    def lookups(self, request, model_admin):
        return (
            ('english_in_spanish', 'Has English text (Spanish entries)'),
            ('needs_review', 'Needs Review'),
            ('clean', 'Clean entries'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'english_in_spanish':
            # Find entries tagged with english-in-spanish
            return queryset.filter(tags__name='english-in-spanish')
        elif self.value() == 'needs_review':
            # Entries with problematic patterns
            english_words = ['familiar address', 'the ', 'and ', 'or ', 'with ', 'this ', 'that ']
            q_objects = Q()
            for word in english_words:
                q_objects |= Q(notes__icontains=word)
            return queryset.filter(q_objects, language_code='es-AR')
        elif self.value() == 'clean':
            # Entries without English words in Spanish
            return queryset.filter(language_code='es-AR').exclude(tags__name='english-in-spanish')
        return queryset

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
    list_filter = ('language_code', 'category', 'region_code', 'tags', 'created_at', 'updated_at', EnglishInSpanishFilter)
    search_fields = ('term', 'notes', 'translations__translation', 'examples__sentence', 'tags__name')
    filter_horizontal = ('tags',)
    inlines = [TranslationInline, ExampleInline]
    readonly_fields = ('created_at', 'updated_at', 'completion_score')
    date_hierarchy = 'created_at'
    list_per_page = 50
    actions = ['mark_as_reviewed', 'bulk_add_tag', 'export_to_csv', 'find_english_in_spanish', 'translate_to_spanish', 'clean_notes_bulk', 'generate_quality_report', 'export_for_curation', 'mark_needs_curation']
    
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
        
        self.message_user(request, f'Added bulk-processed tag to {count} entries.')
    bulk_add_tag.short_description = "Add bulk-processed tag to selected entries"
    
    def find_english_in_spanish(self, request, queryset=None):
        """Find and flag entries with English text in Spanish entries."""
        english_words = [
            'familiar address', 'the', 'and', 'or', 'with', 'this', 'that', 'for', 
            'from', 'they', 'have', 'been', 'will', 'would', 'could', 'should',
            'about', 'after', 'before', 'during', 'through', 'without', 'within',
            'person', 'people', 'woman', 'man', 'child', 'family', 'friend',
            'house', 'home', 'work', 'school', 'place', 'time', 'year', 'day'
        ]
        
        # Find Spanish entries with English words
        spanish_entries = Entry.objects.filter(language_code='es-AR')
        problematic_entries = []
        
        for entry in spanish_entries:
            if entry.notes:
                notes_lower = entry.notes.lower()
                for word in english_words:
                    if word in notes_lower:
                        problematic_entries.append(entry.id)
                        break
        
        if problematic_entries:
            # Create or get a tag for problematic entries
            problem_tag, created = Tag.objects.get_or_create(
                name='english-in-spanish',
                defaults={'description': 'Spanish entry contains English text', 'color': '#dc3545'}
            )
            
            # Add tag to problematic entries
            entries_to_tag = Entry.objects.filter(id__in=problematic_entries)
            for entry in entries_to_tag:
                entry.tags.add(problem_tag)
            
            count = len(problematic_entries)
            self.message_user(request, f'Found and tagged {count} Spanish entries with English text. Look for entries tagged "english-in-spanish".')
        else:
            self.message_user(request, 'No Spanish entries with English text found.')
    
    find_english_in_spanish.short_description = "Find English text in Spanish entries"
    
    def translate_to_spanish(self, request, queryset):
        """Fix mixed-language explanations by standardizing to English."""
        # Fix common Spanish words that appear in English explanations
        spanish_to_english_fixes = {
            'The palabra': 'The word',
            'La palabra': 'The word', 
            'este término': 'this term',
            'este termino': 'this term',
            'Este término': 'This term',
            'Este termino': 'This term',
            'el término': 'the term',
            'el termino': 'the term',
            'alguien': 'someone',
            'Alguien': 'Someone',
            'algo': 'something',
            'Algo': 'Something',
            'persona': 'person',
            'Persona': 'Person',
            'una persona': 'a person',
            'Un persona': 'A person',
            'significa': 'means',
            'Significa': 'Means',
            'se usa': 'is used',
            'Se usa': 'Is used',
            'muy': 'very',
            'Muy': 'Very',
            'también': 'also',
            'También': 'Also',
            'pero': 'but',
            'Pero': 'But',
            'con': 'with',
            'Con': 'With',
            'para': 'for',
            'Para': 'For',
            'en': 'in',
            'En': 'In',
            'de': 'of',
            'De': 'Of',
            'que': 'that',
            'Que': 'That',
            'como': 'like/as',
            'Como': 'Like/As',
        }
        
        count = 0
        for entry in queryset:
            if entry.notes and entry.language_code == 'es-AR':
                original_notes = entry.notes
                updated_notes = entry.notes
                
                # Fix mixed language issues
                for spanish, english in spanish_to_english_fixes.items():
                    # Replace Spanish words in English text
                    updated_notes = updated_notes.replace(spanish, english)
                
                # Additional cleanup for common patterns
                updated_notes = updated_notes.replace(' término ', ' term ')
                updated_notes = updated_notes.replace(' termino ', ' term ')
                updated_notes = updated_notes.replace(' palabra ', ' word ')
                
                if updated_notes != original_notes:
                    entry.notes = updated_notes
                    entry.save()
                    count += 1
        
        if count > 0:
            self.message_user(request, f'Fixed mixed language issues in {count} entries.')
        else:
            self.message_user(request, 'No mixed language issues found to fix.')
    
    translate_to_spanish.short_description = "Fix mixed-language explanations"
    
    def clean_notes_bulk(self, request, queryset):
        """Clean and standardize notes for selected entries."""
        count = 0
        for entry in queryset:
            if entry.notes:
                # Remove extra whitespace and standardize formatting
                cleaned_notes = ' '.join(entry.notes.split())
                
                # Fix common issues
                cleaned_notes = cleaned_notes.replace('  ', ' ')  # Remove double spaces
                cleaned_notes = cleaned_notes.replace(' ,', ',')  # Fix space before comma
                cleaned_notes = cleaned_notes.replace(' .', '.')  # Fix space before period
                cleaned_notes = cleaned_notes.replace('..', '.')  # Fix double periods
                
                if cleaned_notes != entry.notes:
                    entry.notes = cleaned_notes
                    entry.save()
                    count += 1
        
        if count > 0:
            self.message_user(request, f'Cleaned notes for {count} entries.')
        else:
            self.message_user(request, 'No entries needed cleaning.')
    
    clean_notes_bulk.short_description = "Clean and standardize notes"
    
    def generate_quality_report(self, request, queryset):
        """Generate a quality report for selected entries."""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Term', 'Language', 'Category', 'Quality Score', 
            'Issues', 'Has Curated Meaning', 'Translations Count', 
            'Examples Count', 'Notes Length', 'Recommendation'
        ])
        
        for entry in queryset:
            quality_score = self._calculate_entry_quality_score(entry)
            issues = self._identify_entry_issues(entry)
            has_curated = self._has_curated_meaning(entry)
            
            writer.writerow([
                entry.id, entry.term, entry.language_code, entry.category or '',
                quality_score, '; '.join(issues), has_curated,
                entry.translations.count(), entry.examples.count(),
                len(getattr(entry, 'notes', '') or ''),
                self._get_quality_recommendation(quality_score)
            ])
        
        return response
    generate_quality_report.short_description = "Export quality report for selected entries"
    
    def export_for_curation(self, request, queryset):
        """Export selected entries in curation-friendly format."""
        import csv
        from django.http import HttpResponse
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="curation_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'id', 'term', 'language_code', 'category', 'current_notes',
            'current_meaning_es', 'current_meaning_en', 'meaning_es',
            'meaning_en', 'notes', 'action'
        ])
        
        for entry in queryset:
            current_meaning_es = getattr(entry, 'meaning_es', '') or ''
            current_meaning_en = getattr(entry, 'meaning_en', '') or ''
            
            writer.writerow([
                entry.id, entry.term, entry.language_code, entry.category or '',
                (getattr(entry, 'notes', '') or '')[:200],
                current_meaning_es, current_meaning_en,
                '',  # To be filled by curator
                '',  # To be filled by curator  
                '',  # To be filled by curator
                'UPDATE'
            ])
        
        return response
    export_for_curation.short_description = "Export selected entries for curation"
    
    def mark_needs_curation(self, request, queryset):
        """Mark selected entries as needing curation."""
        curation_tag, created = Tag.objects.get_or_create(
            name='needs-curation',
            defaults={'description': 'Entry needs manual curation', 'color': '#ffc107'}
        )
        
        count = 0
        for entry in queryset:
            entry.tags.add(curation_tag)
            count += 1
        
        self.message_user(request, f'Marked {count} entries as needing curation.')
    mark_needs_curation.short_description = "Mark selected entries as needing curation"
    
    def _calculate_entry_quality_score(self, entry):
        """Calculate quality score (0-10) for an entry."""
        score = 0
        
        # Check for curated meanings
        if self._has_curated_meaning(entry):
            score += 4
        
        # Check translations quality
        good_translations = 0
        for trans in entry.translations.all():
            if len(trans.translation) > 10 and not self._is_generic_text(trans.translation):
                good_translations += 1
        score += min(good_translations, 2)
        
        # Check examples
        if entry.examples.exists():
            score += 1
        
        # Check notes quality
        notes = getattr(entry, 'notes', '') or ''
        if notes and len(notes) > 20 and not self._is_generic_text(notes):
            score += 2
        
        # Check tags
        if entry.tags.exists():
            score += 1
        
        return min(score, 10)
    
    def _identify_entry_issues(self, entry):
        """Identify specific issues with an entry."""
        issues = []
        
        if not self._has_curated_meaning(entry):
            issues.append('NO_CURATED_MEANING')
        
        if not entry.translations.exists():
            issues.append('NO_TRANSLATIONS')
        
        if not entry.examples.exists():
            issues.append('NO_EXAMPLES')
        
        notes = getattr(entry, 'notes', '') or ''
        if self._is_generic_text(notes):
            issues.append('GENERIC_NOTES')
        
        if not entry.category:
            issues.append('NO_CATEGORY')
        
        return issues
    
    def _has_curated_meaning(self, entry):
        """Check if entry has curated meaning fields."""
        if hasattr(entry, 'meaning_es') and entry.meaning_es:
            if not self._is_generic_text(entry.meaning_es):
                return True
        if hasattr(entry, 'meaning_en') and entry.meaning_en:
            if not self._is_generic_text(entry.meaning_en):
                return True
        return False
    
    def _is_generic_text(self, text):
        """Check if text is generic or placeholder."""
        if not text or len(text.strip()) < 3:
            return True
        
        generic_patterns = [
            r'slang term', r'colloquial phrase', r'the provided entry',
            r'lacks a detailed', r'translation needed', r'see notes',
            r'placeholder', r'todo', r'tbd'
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in generic_patterns)
    
    def _get_quality_recommendation(self, score):
        """Get recommendation based on quality score."""
        if score >= 8:
            return 'EXCELLENT - Use as template'
        elif score >= 6:
            return 'GOOD - Minor improvements needed'
        elif score >= 4:
            return 'FAIR - Needs content enhancement'
        elif score >= 2:
            return 'POOR - Requires major curation'
        else:
            return 'CRITICAL - Complete rewrite needed'

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

# User Interaction Admin
@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry', 'created_at')
    list_filter = ('created_at', 'entry__category', 'entry__language_code')
    search_fields = ('user__username', 'entry__term')
    raw_id_fields = ('user', 'entry')
    readonly_fields = ('created_at',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry', 'difficulty_rating', 'times_viewed', 'last_viewed')
    list_filter = ('difficulty_rating', 'last_viewed', 'entry__category', 'entry__language_code')
    search_fields = ('user__username', 'entry__term')
    raw_id_fields = ('user', 'entry')
    readonly_fields = ('times_viewed', 'last_viewed')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'entry')

# Customize admin site headers
admin.site.site_header = "LingoWorld Administration"
admin.site.site_title = "LingoWorld Admin"
admin.site.index_title = "Welcome to LingoWorld Administration"

# Analytics and Feedback Admin
@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'action', 'country', 'timestamp', 'ip_address']
    list_filter = ['action', 'country', 'timestamp', 'user']
    search_fields = ['user__username', 'action', 'page_url', 'session_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def user_display(self, obj):
        if obj.user:
            return obj.user.username
        else:
            return f"Anonymous ({obj.session_id[:8]})"
    user_display.short_description = 'User'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'feedback_type', 'status', 'priority', 'created_at']
    list_filter = ['feedback_type', 'status', 'priority', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'country_context']
    readonly_fields = ['created_at', 'updated_at', 'page_url']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'feedback_type', 'title', 'description', 'country_context', 'page_url')
        }),
        ('Management', {
            'fields': ('status', 'priority', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Add custom admin dashboard links
from django.urls import reverse
from django.utils.html import format_html

# Custom admin site with additional features
class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_links'] = [
            {
                'title': '📊 Analytics Dashboard',
                'description': 'View app traffic and usage statistics',
                'url': reverse('admin_analytics_dashboard'),
                'icon': '📊'
            },
            {
                'title': '📝 Feedback Management',
                'description': 'Manage user feedback and suggestions',
                'url': reverse('admin_feedback_list'),
                'icon': '📝'
            },
            {
                'title': '🧹 Data Cleaning Dashboard',
                'description': 'Clean and fix problematic entries',
                'url': reverse('admin_data_cleaning'),
                'icon': '🧹'
            }
        ]
        return super().index(request, extra_context)

# Replace the default admin site
admin.site.__class__ = CustomAdminSite
