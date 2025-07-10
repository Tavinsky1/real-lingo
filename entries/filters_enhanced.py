import django_filters
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Entry, Tag


class EntryFilter(django_filters.FilterSet):
    """Advanced filtering for Entry model with enhanced capabilities."""
    
    # Text search across multiple fields
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Language filtering with multiple options
    language = django_filters.CharFilter(field_name='language_code', lookup_expr='icontains')
    languages = django_filters.BaseInFilter(field_name='language_code', lookup_expr='in')
    
    # Category filtering with multiple choice
    category = django_filters.MultipleChoiceFilter(
        field_name='category',
        choices=Entry._meta.get_field('category').choices
    )
    
    # Region filtering
    region = django_filters.CharFilter(field_name='region_code', lookup_expr='icontains')
    regions = django_filters.BaseInFilter(field_name='region_code', lookup_expr='in')
    
    # Tag filtering - can filter by tag names or IDs
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        queryset=Tag.objects.all(),
        to_field_name='name',
        conjoined=False  # OR behavior instead of AND
    )
    
    # Tag filtering by IDs
    tag_ids = django_filters.BaseInFilter(field_name='tags__id', lookup_expr='in')
    
    # Exclude tags
    exclude_tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        queryset=Tag.objects.all(),
        to_field_name='name',
        exclude=True
    )
    
    # Date range filtering
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    
    # Convenience date filters
    created_today = django_filters.BooleanFilter(method='filter_created_today')
    created_this_week = django_filters.BooleanFilter(method='filter_created_this_week')
    created_this_month = django_filters.BooleanFilter(method='filter_created_this_month')
    
    # Content presence filters
    has_translations = django_filters.BooleanFilter(method='filter_has_translations')
    has_examples = django_filters.BooleanFilter(method='filter_has_examples')
    has_notes = django_filters.BooleanFilter(method='filter_has_notes')
    has_tags = django_filters.BooleanFilter(method='filter_has_tags')
    
    # Content count filters
    min_translations = django_filters.NumberFilter(method='filter_min_translations')
    max_translations = django_filters.NumberFilter(method='filter_max_translations')
    min_examples = django_filters.NumberFilter(method='filter_min_examples')
    max_examples = django_filters.NumberFilter(method='filter_max_examples')
    min_tags = django_filters.NumberFilter(method='filter_min_tags')
    max_tags = django_filters.NumberFilter(method='filter_max_tags')
    
    # Completion score filter
    min_completion_score = django_filters.NumberFilter(method='filter_min_completion_score')
    completion_level = django_filters.ChoiceFilter(
        method='filter_completion_level',
        choices=[
            ('incomplete', 'Incomplete (< 50%)'),
            ('partial', 'Partial (50-79%)'),
            ('complete', 'Complete (80%+)'),
        ]
    )
    
    # Term length filters
    min_term_length = django_filters.NumberFilter(field_name='term', lookup_expr='length__gte')
    max_term_length = django_filters.NumberFilter(field_name='term', lookup_expr='length__lte')
    
    class Meta:
        model = Entry
        fields = {
            'term': ['exact', 'icontains', 'istartswith', 'iendswith'],
            'language_code': ['exact', 'icontains'],
            'region_code': ['exact', 'icontains'],
            'category': ['exact'],
            'part_of_speech': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Enhanced search across term, notes, translations, examples, and tags."""
        if not value:
            return queryset
        
        # Split search terms for better matching
        search_terms = value.split()
        query = Q()
        
        for term in search_terms:
            term_query = (
                Q(term__icontains=term) |
                Q(notes__icontains=term) |
                Q(translations__translation__icontains=term) |
                Q(translations__literal_translation__icontains=term) |
                Q(examples__sentence__icontains=term) |
                Q(examples__translation__icontains=term) |
                Q(tags__name__icontains=term)
            )
            query &= term_query
        
        return queryset.filter(query).distinct()
    
    def filter_created_today(self, queryset, name, value):
        """Filter entries created today."""
        if value is True:
            today = timezone.now().date()
            return queryset.filter(created_at__date=today)
        return queryset
    
    def filter_created_this_week(self, queryset, name, value):
        """Filter entries created this week."""
        if value is True:
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)
        return queryset
    
    def filter_created_this_month(self, queryset, name, value):
        """Filter entries created this month."""
        if value is True:
            month_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=month_ago)
        return queryset
    
    def filter_has_translations(self, queryset, name, value):
        """Filter entries that have or don't have translations."""
        if value is True:
            return queryset.filter(translations__isnull=False).distinct()
        elif value is False:
            return queryset.filter(translations__isnull=True)
        return queryset
    
    def filter_has_examples(self, queryset, name, value):
        """Filter entries that have or don't have examples."""
        if value is True:
            return queryset.filter(examples__isnull=False).distinct()
        elif value is False:
            return queryset.filter(examples__isnull=True)
        return queryset
    
    def filter_has_notes(self, queryset, name, value):
        """Filter entries that have or don't have notes."""
        if value is True:
            return queryset.exclude(notes__isnull=True).exclude(notes='')
        elif value is False:
            return queryset.filter(Q(notes__isnull=True) | Q(notes=''))
        return queryset
    
    def filter_has_tags(self, queryset, name, value):
        """Filter entries that have or don't have tags."""
        if value is True:
            return queryset.filter(tags__isnull=False).distinct()
        elif value is False:
            return queryset.filter(tags__isnull=True)
        return queryset
    
    def filter_min_translations(self, queryset, name, value):
        """Filter entries with minimum number of translations."""
        return queryset.annotate(
            trans_count=Count('translations')
        ).filter(trans_count__gte=value)
    
    def filter_max_translations(self, queryset, name, value):
        """Filter entries with maximum number of translations."""
        return queryset.annotate(
            trans_count=Count('translations')
        ).filter(trans_count__lte=value)
    
    def filter_min_examples(self, queryset, name, value):
        """Filter entries with minimum number of examples."""
        return queryset.annotate(
            ex_count=Count('examples')
        ).filter(ex_count__gte=value)
    
    def filter_max_examples(self, queryset, name, value):
        """Filter entries with maximum number of examples."""
        return queryset.annotate(
            ex_count=Count('examples')
        ).filter(ex_count__lte=value)
    
    def filter_min_tags(self, queryset, name, value):
        """Filter entries with minimum number of tags."""
        return queryset.annotate(
            tag_count=Count('tags')
        ).filter(tag_count__gte=value)
    
    def filter_max_tags(self, queryset, name, value):
        """Filter entries with maximum number of tags."""
        return queryset.annotate(
            tag_count=Count('tags')
        ).filter(tag_count__lte=value)
    
    def filter_min_completion_score(self, queryset, name, value):
        """Filter entries by minimum completion score."""
        # This is a simplified version - ideally you'd calculate this in the database
        filtered_ids = []
        for entry in queryset:
            score = self._calculate_completion_score(entry)
            if score >= value:
                filtered_ids.append(entry.id)
        return queryset.filter(id__in=filtered_ids)
    
    def filter_completion_level(self, queryset, name, value):
        """Filter entries by completion level."""
        if value == 'incomplete':
            return self.filter_min_completion_score(queryset, name, 0).exclude(
                id__in=self.filter_min_completion_score(queryset, name, 50).values_list('id', flat=True)
            )
        elif value == 'partial':
            partial_ids = set(self.filter_min_completion_score(queryset, name, 50).values_list('id', flat=True))
            complete_ids = set(self.filter_min_completion_score(queryset, name, 80).values_list('id', flat=True))
            return queryset.filter(id__in=partial_ids - complete_ids)
        elif value == 'complete':
            return self.filter_min_completion_score(queryset, name, 80)
        return queryset
    
    def _calculate_completion_score(self, entry):
        """Calculate completion score for an entry."""
        score = 20  # Base score for having a term
        
        if entry.notes:
            score += 20
        if entry.translations.exists():
            score += 25
        if entry.examples.exists():
            score += 25
        if entry.tags.exists():
            score += 10
            
        return score


class TagFilter(django_filters.FilterSet):
    """Advanced filtering for Tag model."""
    
    # Basic text search
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Color filtering
    color = django_filters.CharFilter(field_name='color', lookup_expr='exact')
    
    # Usage-based filtering
    has_entries = django_filters.BooleanFilter(method='filter_has_entries')
    min_entries = django_filters.NumberFilter(method='filter_min_entries')
    max_entries = django_filters.NumberFilter(method='filter_max_entries')
    
    # Popular tags (top N most used)
    popular = django_filters.BooleanFilter(method='filter_popular')
    
    class Meta:
        model = Tag
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'description': ['icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search in tag name and description."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_has_entries(self, queryset, name, value):
        """Filter tags that have or don't have entries."""
        if value is True:
            return queryset.filter(entry__isnull=False).distinct()
        elif value is False:
            return queryset.filter(entry__isnull=True)
        return queryset
    
    def filter_min_entries(self, queryset, name, value):
        """Filter tags with minimum number of entries."""
        return queryset.annotate(
            entry_count=Count('entry')
        ).filter(entry_count__gte=value)
    
    def filter_max_entries(self, queryset, name, value):
        """Filter tags with maximum number of entries."""
        return queryset.annotate(
            entry_count=Count('entry')
        ).filter(entry_count__lte=value)
    
    def filter_popular(self, queryset, name, value):
        """Filter to show only popular tags (top 20 most used)."""
        if value is True:
            return queryset.annotate(
                entry_count=Count('entry')
            ).filter(entry_count__gt=0).order_by('-entry_count')[:20]
        return queryset
