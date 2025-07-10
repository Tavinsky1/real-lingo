# entries/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.http import JsonResponse
from .models import Entry, Tag, Translation, Example
import random # For random sampling

# API Related Imports
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from .serializers import EntrySerializer, TagSerializer, EntryListSerializer, EntryDetailSerializer
from .filters import EntryFilter

# --- API VIEWSETS ---

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Tags with statistics and filtering.
    
    Features:
    - List all tags with usage statistics
    - Filter tags by usage count
    - Get popular/trending tags
    - Tag-based analytics
    """
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'entries_count']
    ordering = ['name']
    
    def get_queryset(self):
        """Get tags with usage statistics."""
        return Tag.objects.annotate(
            entries_count=Count('entry')
        ).prefetch_related('entry_set')
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular tags."""
        limit = int(request.query_params.get('limit', 10))
        tags = self.get_queryset().order_by('-entries_count')[:limit]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get tag usage statistics."""
        queryset = self.get_queryset()
        stats = {
            'total_tags': queryset.count(),
            'tags_with_entries': queryset.filter(entries_count__gt=0).count(),
            'unused_tags': queryset.filter(entries_count=0).count(),
            'avg_entries_per_tag': queryset.aggregate(avg=Avg('entries_count'))['avg'] or 0,
            'most_used_tag': None,
            'tag_distribution': []
        }
        
        # Most used tag
        most_used = queryset.order_by('-entries_count').first()
        if most_used:
            stats['most_used_tag'] = {
                'name': most_used.name,
                'entries_count': most_used.entries_count
            }
        
        # Tag distribution (buckets)
        stats['tag_distribution'] = [
            {'range': '0 entries', 'count': queryset.filter(entries_count=0).count()},
            {'range': '1-5 entries', 'count': queryset.filter(entries_count__range=(1, 5)).count()},
            {'range': '6-20 entries', 'count': queryset.filter(entries_count__range=(6, 20)).count()},
            {'range': '21+ entries', 'count': queryset.filter(entries_count__gt=20).count()},
        ]
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def entries(self, request, pk=None):
        """Get entries for a specific tag."""
        tag = self.get_object()
        entries = tag.entry_set.all().select_related().prefetch_related('tags', 'translations', 'examples')
        
        # Apply pagination
        page = self.paginate_queryset(entries)
        if page is not None:
            serializer = EntryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EntryListSerializer(entries, many=True)
        return Response(serializer.data)

class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Enhanced API endpoint for Entries with advanced filtering and search.
    
    Features:
    - Advanced text search across multiple fields
    - Language, category, region, and tag filtering
    - Random sampling with 'random_count' parameter
    - Statistics endpoint
    - Bulk operations for favorites
    - Different serializers for list vs detail views
    """
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EntryFilter
    search_fields = ['term', 'notes', 'translations__translation', 'examples__sentence']
    ordering_fields = ['term', 'language_code', 'category', 'created_at', 'updated_at']
    ordering = ['term']

    def get_serializer_class(self):
        """Use different serializers for list vs detail views."""
        if self.action == 'list':
            return EntryListSerializer
        return EntryDetailSerializer

    def get_queryset(self):
        """Enhanced queryset with better performance and random sampling."""
        base_queryset = Entry.objects.select_related().prefetch_related(
            'tags', 'translations', 'examples'
        ).annotate(
            translations_count=Count('translations', distinct=True),
            examples_count=Count('examples', distinct=True),
            tags_count=Count('tags', distinct=True)
        )

        # Handle random sampling
        random_count_str = self.request.query_params.get('random_count', None)
        if random_count_str:
            try:
                random_count = int(random_count_str)
                if random_count > 0:
                    # Apply filters first, then sample
                    filtered_queryset = self.filter_queryset(base_queryset)
                    ids = list(filtered_queryset.values_list('id', flat=True))
                    
                    if len(ids) > random_count:
                        sampled_ids = random.sample(ids, random_count)
                        return base_queryset.filter(pk__in=sampled_ids)
                    return filtered_queryset
            except ValueError:
                pass
        
        return base_queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive statistics about the entries."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Basic counts
        total_entries = queryset.count()
        
        # Language statistics
        language_stats = list(queryset.values('language_code').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        # Category statistics
        category_stats = list(queryset.exclude(category__isnull=True).values('category').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        # Region statistics
        region_stats = list(queryset.exclude(region_code__isnull=True).values('region_code').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        stats = {
            'total_entries': total_entries,
            'languages': {
                'total_languages': len(language_stats),
                'distribution': language_stats
            },
            'categories': {
                'total_categories': len(category_stats),
                'distribution': category_stats
            },
            'regions': {
                'total_regions': len(region_stats),
                'distribution': region_stats
            },
            'content_completeness': {
                'entries_with_translations': queryset.filter(translations_count__gt=0).count(),
                'entries_with_examples': queryset.filter(examples_count__gt=0).count(),
                'entries_with_tags': queryset.filter(tags_count__gt=0).count(),
                'entries_with_notes': queryset.exclude(notes__isnull=True).exclude(notes='').count(),
            },
            'averages': {
                'avg_translations_per_entry': queryset.aggregate(avg=models.Avg('translations_count'))['avg'] or 0,
                'avg_examples_per_entry': queryset.aggregate(avg=models.Avg('examples_count'))['avg'] or 0,
                'avg_tags_per_entry': queryset.aggregate(avg=models.Avg('tags_count'))['avg'] or 0,
            }
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get random entries - shortcut for ?random_count=X"""
        count = request.query_params.get('count', 5)
        try:
            count = int(count)
            count = min(max(count, 1), 50)  # Limit between 1 and 50
        except ValueError:
            count = 5
            
        # Apply the random_count parameter and use existing logic
        modified_params = request.query_params.copy()
        modified_params['random_count'] = count
        request._request.GET = modified_params
        
        return self.list(request)
    
    @action(detail=False, methods=['get'])
    def search_suggestions(self, request):
        """Get search suggestions based on partial input."""
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response({'suggestions': []})
        
        # Get term suggestions
        term_suggestions = list(
            Entry.objects.filter(term__icontains=query)
            .values_list('term', flat=True)
            .distinct()[:10]
        )
        
        # Get tag suggestions
        tag_suggestions = list(
            Tag.objects.filter(name__icontains=query)
            .values_list('name', flat=True)
            .distinct()[:5]
        )
        
        return Response({
            'suggestions': {
                'terms': term_suggestions,
                'tags': tag_suggestions
            }
        })
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar entries based on tags and category."""
        entry = self.get_object()
        
        # Find entries with similar tags or same category
        similar_queryset = Entry.objects.exclude(pk=entry.pk).annotate(
            translations_count=Count('translations', distinct=True),
            examples_count=Count('examples', distinct=True),
            tags_count=Count('tags', distinct=True)
        ).prefetch_related('tags', 'translations', 'examples')
        
        # Same category entries
        same_category = similar_queryset.filter(
            category=entry.category
        ) if entry.category else Entry.objects.none()
        
        # Entries with common tags
        if entry.tags.exists():
            common_tags = similar_queryset.filter(
                tags__in=entry.tags.all()
            ).annotate(
                common_tags_count=Count('tags')
            ).order_by('-common_tags_count')
        else:
            common_tags = Entry.objects.none()
        
        # Combine and limit results
        similar_ids = set()
        
        # Add same category entries (up to 3)
        for e in same_category[:3]:
            similar_ids.add(e.id)
        
        # Add common tag entries (up to 5 total)
        for e in common_tags:
            if len(similar_ids) >= 5:
                break
            similar_ids.add(e.id)
        
        # Get final queryset
        similar_entries = similar_queryset.filter(id__in=similar_ids)
        serializer = EntryListSerializer(similar_entries, many=True)
        
        return Response({
            'similar_entries': serializer.data,
            'similarity_criteria': {
                'same_category': entry.category is not None,
                'common_tags': entry.tags.count() > 0
            }
        })

    # --- ACTIONS FOR FAVORITES (Keep if you plan to use them soon) ---
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        entry = self.get_object()
        if request.user.is_authenticated: # Should be guaranteed by permission_classes
            entry.favorited_by.add(request.user)
            return Response({'status': 'entry favorited'}, status=status.HTTP_200_OK)
        # This part might be redundant if IsAuthenticated permission is effective
        return Response({'status': 'authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        entry = self.get_object()
        if request.user.is_authenticated: # Should be guaranteed by permission_classes
            entry.favorited_by.remove(request.user)
            return Response({'status': 'entry unfavorited'}, status=status.HTTP_200_OK)
        # This part might be redundant if IsAuthenticated permission is effective
        return Response({'status': 'authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

# Optional: ViewSet for listing a user's favorites (keep if you plan to use it)
class FavoriteEntriesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.favorite_entries.all().prefetch_related(
            'tags', 'translations', 'examples', 'favorited_by' # Add prefetch here too
        ).order_by('term')


# --- FRONTEND WEB PAGE VIEWS ---

def entry_list_view(request):
    default_language = 'de'
    selected_language = request.GET.get('language', default_language).strip()
    selected_category_code = request.GET.get('category', None)
    if selected_category_code:
        selected_category_code = selected_category_code.strip().upper()

    all_defined_categories = Entry._meta.get_field('category').choices
    
    entries_for_cards = []
    current_category_name = None

    # Initial query based on language, further filtered by category if selected
    base_query = Entry.objects.filter(language_code=selected_language)

    if selected_category_code:
        base_query = base_query.filter(category=selected_category_code)
        all_matching_entries = list(base_query.order_by('?')) # Order randomly for sampling
        
        num_cards_to_show = 5
        if len(all_matching_entries) > num_cards_to_show:
            entries_for_cards = random.sample(all_matching_entries, num_cards_to_show)
        else:
            entries_for_cards = all_matching_entries # Show all if fewer than num_cards_to_show
        
        current_category_name = dict(all_defined_categories).get(selected_category_code, selected_category_code)
    
    # For the category filter dropdown - show categories available for the selected language
    available_categories_qs = Entry.objects.filter(language_code=selected_language).values_list('category', flat=True).distinct()
    entry_category_choices_dict = dict(all_defined_categories)
    category_choices_for_template = []
    for code in available_categories_qs:
        if code:
            display_name = entry_category_choices_dict.get(code, code)
            category_choices_for_template.append((code, display_name))
    category_choices_for_template.sort()

    # For the language selector dropdown
    # Consider making this more robust later (e.g., predefined list or based on actual distinct languages in DB)
    available_languages = [
        {'code': 'de', 'name': 'German'},
        {'code': 'es-AR', 'name': 'Argentinian Spanish'},
        # Add more as you import data for them
    ]


    context = {
        'all_categories': all_defined_categories, # For displaying category buttons
        'selected_language': selected_language,
        'selected_category_code': selected_category_code,
        'current_category_name': current_category_name,
        'entries_for_cards': entries_for_cards, # The few random cards to display
        'available_languages': available_languages, # For the language dropdown
        'category_choices_for_template': category_choices_for_template, # For the category filter (if still used)
    }
    return render(request, 'entries/entry_list.html', context)


def entry_detail_view(request, entry_id):
    entry = get_object_or_404(Entry.objects.prefetch_related('tags', 'translations', 'examples'), pk=entry_id)
    context = {
        'entry': entry,
    }
    return render(request, 'entries/entry_detail.html', context)