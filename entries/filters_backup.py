import django_filters
from django.db.models import Q
from .models import Entry, Tag


class EntryFilter(django_filters.FilterSet):
    """Advanced filtering for Entry model."""
    
    # Text search across multiple fields
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Language filtering
    language = django_filters.CharFilter(field_name='language_code', lookup_expr='icontains')
    
    # Category filtering with multiple choice
    category = django_filters.MultipleChoiceFilter(
        field_name='category',
        choices=Entry._meta.get_field('category').choices
    )
    
    # Region filtering
    region = django_filters.CharFilter(field_name='region_code', lookup_expr='icontains')
    
    # Tag filtering - can filter by tag names
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__name',
        queryset=Tag.objects.all(),
        to_field_name='name',
        conjoined=False  # OR behavior instead of AND
    )
    
    # Date range filtering
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Has translations/examples
    has_translations = django_filters.BooleanFilter(method='filter_has_translations')
    has_examples = django_filters.BooleanFilter(method='filter_has_examples')
    
    class Meta:
        model = Entry
        fields = {
            'term': ['exact', 'icontains', 'istartswith'],
            'language_code': ['exact', 'icontains'],
            'region_code': ['exact', 'icontains'],
            'category': ['exact'],
            'part_of_speech': ['exact', 'icontains'],
        }
    
    def filter_search(self, queryset, name, value):
        """Search across term, notes, translations, and examples."""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(term__icontains=value) |
            Q(notes__icontains=value) |
            Q(translations__translation__icontains=value) |
            Q(translations__literal_translation__icontains=value) |
            Q(examples__sentence__icontains=value) |
            Q(examples__translation__icontains=value) |
            Q(tags__name__icontains=value)
        ).distinct()
    
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
