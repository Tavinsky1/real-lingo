# entries/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.conf import settings
from .models import Entry, Tag, UserFavorite, UserProgress
import random

# API Related Imports
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F
from .serializers import EntrySerializer, TagSerializer, UserFavoriteSerializer, UserProgressSerializer
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
        return Tag.objects.annotate(entries_count=Count('entry'))
    
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
            'most_used_tag': None
        }
        
        most_used = queryset.order_by('-entries_count').first()
        if most_used:
            stats['most_used_tag'] = {
                'name': most_used.name,
                'entries_count': most_used.entries_count
            }
        
        return Response(stats)

class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Enhanced API endpoint for Entries with advanced filtering and search.
    
    Features:
    - Advanced text search across multiple fields
    - Language, category, region, and tag filtering
    - Random sampling with 'random_count' parameter
    - Statistics endpoint
    - Search suggestions
    """
    serializer_class = EntrySerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EntryFilter
    search_fields = ['term', 'notes', 'translations__translation', 'examples__sentence']
    ordering_fields = ['term', 'language_code', 'category', 'created_at', 'updated_at']
    ordering = ['term']

    def get_queryset(self):
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
            'content_completeness': {
                'entries_with_translations': queryset.filter(translations_count__gt=0).count(),
                'entries_with_examples': queryset.filter(examples_count__gt=0).count(),
                'entries_with_tags': queryset.filter(tags_count__gt=0).count(),
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
        serializer = self.get_serializer(similar_entries, many=True)
        
        return Response({
            'similar_entries': serializer.data,
            'similarity_criteria': {
                'same_category': entry.category is not None,
                'common_tags': entry.tags.count() > 0
            }
        })

class UserFavoriteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user favorites.
    
    Features:
    - List user's favorite entries
    - Add/remove favorites
    - User-specific filtering (authenticated users only)
    """
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user).select_related('entry')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle favorite status for an entry."""
        entry_id = request.data.get('entry_id')
        if not entry_id:
            return Response({'error': 'entry_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return Response({'error': 'Entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        favorite, created = UserFavorite.objects.get_or_create(
            user=request.user,
            entry=entry
        )
        
        if not created:
            favorite.delete()
            return Response({'status': 'removed', 'is_favorite': False})
        else:
            return Response({'status': 'added', 'is_favorite': True})


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tracking user learning progress.
    
    Features:
    - Track learning progress per entry
    - Update difficulty ratings and notes
    - View statistics and progress over time
    """
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related('entry')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        # Increment view count when updating
        instance = serializer.save()
        UserProgress.objects.filter(id=instance.id).update(times_viewed=F('times_viewed') + 1)
    
    @action(detail=False, methods=['post'])
    def mark_viewed(self, request):
        """Mark an entry as viewed and increment counter."""
        entry_id = request.data.get('entry_id')
        if not entry_id:
            return Response({'error': 'entry_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return Response({'error': 'Entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            entry=entry,
            defaults={'times_viewed': 1}
        )
        
        if not created:
            progress.times_viewed += 1
            progress.save()
        
        return Response({
            'times_viewed': progress.times_viewed,
            'difficulty_rating': progress.difficulty_rating
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's learning statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total_entries_viewed': queryset.count(),
            'total_views': queryset.aggregate(total=models.Sum('times_viewed'))['total'] or 0,
            'difficulty_breakdown': {},
            'recent_activity': queryset.order_by('-last_viewed')[:10].values(
                'entry__term', 'times_viewed', 'difficulty_rating', 'last_viewed'
            )
        }
        
        # Calculate difficulty breakdown
        for choice in UserProgress.DIFFICULTY_CHOICES:
            count = queryset.filter(difficulty_rating=choice[0]).count()
            stats['difficulty_breakdown'][choice[1]] = count
        
        return Response(stats)

# --- FRONTEND WEB PAGE VIEWS ---

def entry_list_view(request):
    """Enhanced entry list view with language support and dynamic translation."""
    from .translations import TRANSLATIONS
    
    # Get user's language preference
    user_language = request.session.get('user_language', 'en')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_language = request.GET.get('language', '').strip()
    
    # Base queryset
    entries = Entry.objects.select_related().prefetch_related(
        'tags', 'translations', 'examples'
    ).annotate(
        translations_count=Count('translations', distinct=True),
        examples_count=Count('examples', distinct=True),
        tags_count=Count('tags', distinct=True)
    )
    
    # Apply filters
    if search_query:
        entries = entries.filter(
            Q(term__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(translations__translation__icontains=search_query) |
            Q(examples__sentence__icontains=search_query)
        ).distinct()
    
    if selected_category:
        entries = entries.filter(category=selected_category)
    
    if selected_language:
        entries = entries.filter(language_code=selected_language)
    
    # Get all defined categories for the filter dropdown
    all_defined_categories = Entry.objects.exclude(
        category__isnull=True
    ).values_list('category', flat=True).distinct().order_by('category')
    
    # Translate categories if user language is not English
    if user_language != 'en' and user_language in TRANSLATIONS:
        category_translations = TRANSLATIONS[user_language].get('categories', {})
        translated_categories = []
        for category in all_defined_categories:
            if category in category_translations:
                translated_categories.append((category, category_translations[category]))
            else:
                translated_categories.append((category, category))
        category_choices_for_template = translated_categories
    else:
        category_choices_for_template = [(cat, cat) for cat in all_defined_categories]
    
    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
        entries_for_cards = page_obj.object_list
        is_paginated = paginator.num_pages > 1
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)
        entries_for_cards = page_obj.object_list
        is_paginated = paginator.num_pages > 1
    
    # Translate entries for display
    for entry in entries_for_cards:
        entry = get_translated_entry(entry, user_language)
    
    # Available languages
    available_languages = [
        {'code': 'de', 'name': 'German'},
        {'code': 'es-AR', 'name': 'Argentinian Spanish'},
        {'code': 'en-AU', 'name': 'Australian English'},
    ]
    
    # Add user-specific data for authenticated users
    if request.user.is_authenticated:
        # Mark favorited entries
        favorite_ids = set(UserFavorite.objects.filter(user=request.user).values_list('entry_id', flat=True))
        for entry in entries_for_cards:
            entry.is_favorited = entry.id in favorite_ids
            
        # Get user progress data
        progress_data = {
            progress.entry_id: progress for progress in 
            UserProgress.objects.filter(user=request.user, entry__in=entries_for_cards)
        }
        for entry in entries_for_cards:
            progress = progress_data.get(entry.id)
            entry.user_progress = progress
            entry.view_count = progress.times_viewed if progress else 0

    context = {
        'all_categories': all_defined_categories,
        'selected_language': selected_language,
        'selected_category_code': selected_category,
        'current_category_name': selected_category,
        'entries_for_cards': entries_for_cards,
        'available_languages': available_languages,
        'category_choices_for_template': category_choices_for_template,
        'search_query': search_query,
        'is_paginated': is_paginated,
        'page_obj': page_obj,
        'user_language': user_language,
    }
    
    return render(request, 'entries/entry_list.html', context)

def get_translated_entry(entry, user_language='en'):
    """Get entry with translated content based on user language."""
    from .translations import TRANSLATIONS
    
    # Create a copy of the entry to avoid modifying the original
    translated_entry = entry
    
    # Translate category if it exists
    if entry.category and user_language in TRANSLATIONS:
        category_translations = TRANSLATIONS[user_language].get('categories', {})
        if entry.category in category_translations:
            translated_entry.category = category_translations[entry.category]
    
    # Get translations in user's language
    user_translations = entry.translations.filter(target_language_code=user_language)
    if user_translations.exists():
        translated_entry.user_translations = user_translations
    
    # Get examples in user's language
    user_examples = entry.examples.filter(language_code=user_language)
    if user_examples.exists():
        translated_entry.user_examples = user_examples
    
    return translated_entry

def entry_detail_view(request, entry_id):
    """Enhanced entry detail view with language support."""
    entry = get_object_or_404(Entry.objects.select_related().prefetch_related(
        'tags', 'translations', 'examples'
    ), id=entry_id)
    
    # Get user's language preference
    user_language = request.session.get('user_language', 'en')
    
    # Get translated entry
    translated_entry = get_translated_entry(entry, user_language)
    
    # Get user progress if authenticated
    user_progress = None
    if request.user.is_authenticated:
        user_progress = UserProgress.objects.filter(user=request.user, entry=entry).first()
    
    # Check if user has favorited this entry
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = UserFavorite.objects.filter(user=request.user, entry=entry).exists()
    
    # Get related entries
    related_entries = Entry.objects.filter(
        language_code=entry.language_code,
        category=entry.category
    ).exclude(id=entry.id)[:5]
    
    context = {
        'entry': translated_entry,
        'user_progress': user_progress,
        'is_favorited': is_favorited,
        'related_entries': related_entries,
        'user_language': user_language,
    }
    
    return render(request, 'entries/entry_detail.html', context)

def user_profile_view(request):
    """User profile view with achievements and settings."""
    if not request.user.is_authenticated:
        return redirect('admin:login')
    
    # Get user's recent favorites
    recent_favorites = UserFavorite.objects.filter(user=request.user).select_related('entry').order_by('-created_at')[:10]
    
    # Get user's recent activity
    recent_activity = UserProgress.objects.filter(user=request.user).select_related('entry').order_by('-last_viewed')[:15]
    
    # Calculate user statistics
    total_favorites = UserFavorite.objects.filter(user=request.user).count()
    total_entries_viewed = UserProgress.objects.filter(user=request.user).count()
    total_learned = UserProgress.objects.filter(user=request.user, difficulty_rating='MASTERED').count()
    
    context = {
        'recent_favorites': recent_favorites,
        'recent_activity': recent_activity,
        'total_favorites': total_favorites,
        'total_entries_viewed': total_entries_viewed,
        'total_learned': total_learned,
    }
    
    return render(request, 'entries/user_profile.html', context)

def advanced_search_view(request):
    """Advanced search view with filters and analytics."""
    search_query = request.GET.get('q', '').strip()
    language = request.GET.get('language', '').strip()
    category = request.GET.get('category', '').strip()
    tags = request.GET.getlist('tags')
    difficulty = request.GET.get('difficulty', '').strip()
    
    entries = Entry.objects.prefetch_related('tags', 'translations')
    
    # Apply filters
    if search_query:
        entries = entries.filter(
            Q(term__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(translations__translation__icontains=search_query)
        ).distinct()
    
    if language:
        entries = entries.filter(language_code=language)
    
    if category:
        entries = entries.filter(category=category)
    
    if tags:
        for tag in tags:
            entries = entries.filter(tags__name__icontains=tag)
    
    # Pagination
    paginator = Paginator(entries.order_by('term'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    available_languages = Entry.objects.values_list('language_code', flat=True).distinct()
    available_categories = Entry._meta.get_field('category').choices
    popular_tags = Tag.objects.annotate(usage_count=Count('entry')).order_by('-usage_count')[:20]
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_language': language,
        'selected_category': category,
        'selected_tags': tags,
        'available_languages': available_languages,
        'available_categories': available_categories,
        'popular_tags': popular_tags,
        'total_results': paginator.count,
    }
    
    return render(request, 'entries/advanced_search.html', context)

def user_dashboard_view(request):
    """Dashboard view for authenticated users showing their progress and favorites."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user's recent favorites
    recent_favorites = UserFavorite.objects.filter(user=request.user).select_related('entry').order_by('-created_at')[:6]
    
    # Get user's recent activity
    recent_activity = UserProgress.objects.filter(user=request.user).select_related('entry').order_by('-last_viewed')[:10]
    
    # Calculate user statistics
    total_favorites = UserFavorite.objects.filter(user=request.user).count()
    total_entries_viewed = UserProgress.objects.filter(user=request.user).count()
    total_learned = UserProgress.objects.filter(user=request.user, difficulty_rating='MASTERED').count()
    
    # Calculate streak (simplified - days with activity)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    streak_days = 0
    check_date = today
    
    while True:
        if UserProgress.objects.filter(user=request.user, last_viewed__date=check_date).exists():
            streak_days += 1
            check_date -= timedelta(days=1)
        else:
            break
    
    # Daily progress (simplified)
    daily_goal = 5
    daily_viewed = UserProgress.objects.filter(
        user=request.user, 
        last_viewed__date=today
    ).count()
    
    daily_progress = min(100, (daily_viewed / daily_goal) * 100) if daily_goal > 0 else 0
    daily_progress_offset = 339 - (339 * daily_progress / 100)
    
    # Weekly progress
    week_start = today - timedelta(days=today.weekday())
    weekly_viewed = UserProgress.objects.filter(
        user=request.user,
        last_viewed__date__gte=week_start
    ).count()
    weekly_goal = 50
    weekly_progress = min(100, (weekly_viewed / weekly_goal) * 100) if weekly_goal > 0 else 0
    
    # Monthly progress  
    month_start = today.replace(day=1)
    monthly_viewed = UserProgress.objects.filter(
        user=request.user,
        last_viewed__date__gte=month_start
    ).count()
    monthly_goal = 200
    monthly_progress = min(100, (monthly_viewed / monthly_goal) * 100) if monthly_goal > 0 else 0
    
    user_stats = {
        'favorites_count': total_favorites,
        'viewed_count': total_entries_viewed,
        'learned_count': total_learned,
        'streak_days': streak_days,
        'daily_goal': daily_goal,
        'daily_viewed': daily_viewed,
        'daily_completed': daily_viewed >= daily_goal,
        'daily_progress_offset': daily_progress_offset,
        'weekly_goal': weekly_goal,
        'weekly_viewed': weekly_viewed,
        'weekly_progress': weekly_progress,
        'monthly_goal': monthly_goal,
        'monthly_viewed': monthly_viewed,
        'monthly_progress': monthly_progress,
    }
    
    context = {
        'recent_favorites': recent_favorites,
        'recent_activity': recent_activity,
        'user_stats': user_stats,
    }
    
    return render(request, 'entries/user_dashboard_modern.html', context)

def home_view(request):
    """Modern home page with featured content and statistics."""
    # Get featured entries (random selection)
    featured_entries = Entry.objects.prefetch_related('tags', 'translations').order_by('?')[:6]
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(entries_count=Count('entry')).order_by('-entries_count')[:8]
    
    # Get statistics
    total_entries = Entry.objects.count()
    total_tags = Tag.objects.count()
    
    # User statistics if authenticated
    user_stats = {}
    if request.user.is_authenticated:
        user_stats = {
            'favorites_count': UserFavorite.objects.filter(user=request.user).count(),
            'viewed_count': UserProgress.objects.filter(user=request.user).count(),
        }
    
    context = {
        'featured_entries': featured_entries,
        'popular_tags': popular_tags,
        'total_entries': total_entries,
        'total_tags': total_tags,
        'user_stats': user_stats,
    }
    
    return render(request, 'entries/home_modern.html', context)

def country_selection_view(request):
    """Country selection page with enhanced UI and statistics."""
    from .translations import TRANSLATIONS
    
    # Get user's language preference
    user_language = request.session.get('user_language', 'en')
    
    # Get country descriptions in the user's language
    country_descriptions = TRANSLATIONS.get(user_language, {}).get('country_descriptions', {})
    
    # Get entry counts for each country
    argentina_count = Entry.objects.filter(language_code='es-AR').count()
    australia_count = Entry.objects.filter(language_code='en-AU').count()
    germany_count = Entry.objects.filter(language_code='de-DE').count()
    colombia_count = Entry.objects.filter(language_code='es-CO').count()
    belgium_count = Entry.objects.filter(language_code__in=['nl-BE', 'fr-BE']).count()
    
    context = {
        'argentina_count': argentina_count,
        'australia_count': australia_count,
        'germany_count': germany_count,
        'colombia_count': colombia_count,
        'belgium_count': belgium_count,
        'country_descriptions': country_descriptions,
        'user_language': user_language,
    }
    
    return render(request, 'entries/country_selection.html', context)

def country_home_view(request, country):
    """Country-specific home page."""
    # Map country codes to language codes
    country_mapping = {
        'argentina': {'language_code': 'es-AR', 'name': 'Argentina', 'flag': '🇦🇷'},
        'australia': {'language_code': 'en-AU', 'name': 'Australia', 'flag': '🇦🇺'},
        'germany': {'language_code': 'de-DE', 'name': 'Germany', 'flag': '🇩🇪'},
        'colombia': {'language_code': 'es-CO', 'name': 'Colombia', 'flag': '🇨🇴'},
        'belgium': {'language_codes': ['nl-BE', 'fr-BE'], 'name': 'Belgium', 'flag': '🇧🇪'},
    }
    
    if country not in country_mapping:
        return redirect('country-selection')
    
    country_info = country_mapping[country]
    
    # Handle Belgium's multiple languages
    if country == 'belgium':
        language_codes = country_info['language_codes']
        # Get country-specific statistics for Belgium (using region_code)
        total_entries = Entry.objects.filter(region_code='BE').count()
        total_tags = Tag.objects.filter(entry__region_code='BE').distinct().count()
        
        # Get featured entries (random selection)
        featured_entries = Entry.objects.filter(region_code='BE').order_by('?')[:6]
        
        # Get popular categories
        all_standard_categories = [
            'slang', 'colloquial_phrases', 'unique_concepts', 
            'insults', 'jokes', 'tongue_twisters'
        ]
        
        # Get counts for each category
        popular_categories = []
        for category in all_standard_categories:
            count = Entry.objects.filter(region_code='BE', category=category).count()
            popular_categories.append({
                'category': category,
                'count': count
            })
        
        # Sort by count descending, but keep all categories
        popular_categories.sort(key=lambda x: x['count'], reverse=True)
        
        # Get recent entries
        recent_entries = Entry.objects.filter(region_code='BE').order_by('-created_at')[:8]
    else:
        language_code = country_info['language_code']
        
        # Get user's interface language preference
        user_language = request.session.get('user_language', 'en')
        
        # Base queryset for entries
        entries_base_query = Entry.objects.filter(language_code=language_code)
        
        # LANGUAGE FILTERING: If user selected Spanish interface, filter out entries with English content
        if user_language == 'es' and language_code in ['es-AR', 'es-CO']:
            # Define common English words that shouldn't appear in Spanish content
            english_words = ['the ', 'and ', 'with ', 'this ', 'that ', 'person', 'people', 'from ', 'they ', 'have ', 'will ', 'would ', 'could ', 'should']
            
            # Create Q objects to exclude entries with English words
            exclude_conditions = Q()
            for word in english_words:
                exclude_conditions |= Q(notes__icontains=word)
            
            # Filter out entries with English content when Spanish interface is selected
            entries_base_query = entries_base_query.exclude(exclude_conditions)
        
        # Get country-specific statistics
        total_entries = entries_base_query.count()
        total_tags = Tag.objects.filter(entry__in=entries_base_query).distinct().count()
        
        # Get featured entries (random selection)
        featured_entries = entries_base_query.order_by('?')[:6]
        
        # Get popular categories - always show all 6 standardized categories
        all_standard_categories = [
            'slang', 'colloquial_phrases', 'unique_concepts', 
            'insults', 'jokes', 'tongue_twisters'
        ]
        
        # Get counts for each category using filtered queryset
        popular_categories = []
        for category in all_standard_categories:
            count = entries_base_query.filter(category=category).count()
            popular_categories.append({
                'category': category,
                'count': count
            })
        
        # Sort by count descending, but keep all categories
        popular_categories.sort(key=lambda x: x['count'], reverse=True)
        
        # Get recent entries using filtered queryset
        recent_entries = entries_base_query.order_by('-created_at')[:8]
    
    # Store selected country in session
    request.session['selected_country'] = country
    
    context = {
        'country': country,
        'country_info': country_info,
        'total_entries': total_entries,
        'total_tags': total_tags,
        'featured_entries': featured_entries,
        'popular_categories': popular_categories,
        'recent_entries': recent_entries,
    }
    
    return render(request, 'entries/country_home.html', context)

def country_entry_list_view(request, country):
    """Country-specific entry list view."""
    # Map country codes to language codes
    country_mapping = {
        'argentina': {'language_code': 'es-AR', 'name': 'Argentina', 'flag': '🇦🇷'},
        'australia': {'language_code': 'en-AU', 'name': 'Australia', 'flag': '🇦🇺'},
        'germany': {'language_code': 'de-DE', 'name': 'Germany', 'flag': '🇩🇪'},
        'colombia': {'language_code': 'es-CO', 'name': 'Colombia', 'flag': '🇨🇴'},
        'belgium': {'language_codes': ['nl-BE', 'fr-BE'], 'name': 'Belgium', 'flag': '🇧🇪'},
    }
    
    if country not in country_mapping:
        return redirect('country-selection')
    
    country_info = country_mapping[country]
    
    # Get user's interface language preference
    user_language = request.session.get('user_language', 'en')
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_tags = request.GET.getlist('tags')
    random_mode = request.GET.get('random', '').lower() == 'true'
    favorites_only = request.GET.get('favorites', '').lower() == 'true'
    
    # Base queryset filtered by country
    if country == 'belgium':
        entries_queryset = Entry.objects.filter(region_code='BE').prefetch_related('tags', 'translations')
    else:
        language_code = country_info['language_code']
        entries_queryset = Entry.objects.filter(language_code=language_code).prefetch_related('tags', 'translations')
        
        # LANGUAGE FILTERING: If user selected Spanish interface, filter out entries with English content
        if user_language == 'es' and language_code in ['es-AR', 'es-CO']:
            # Define common English words that shouldn't appear in Spanish content
            english_words = ['the ', 'and ', 'with ', 'this ', 'that ', 'person', 'people', 'from ', 'they ', 'have ', 'will ', 'would ', 'could ', 'should']
            
            # Create Q objects to exclude entries with English words
            exclude_conditions = Q()
            for word in english_words:
                exclude_conditions |= Q(notes__icontains=word)
            
            # Filter out entries with English content when Spanish interface is selected
            entries_queryset = entries_queryset.exclude(exclude_conditions)
    
    # Filter for favorites if requested and user is authenticated
    if favorites_only and request.user.is_authenticated:
        favorite_ids = UserFavorite.objects.filter(user=request.user).values_list('entry_id', flat=True)
        entries_queryset = entries_queryset.filter(id__in=favorite_ids)
    
    # Apply search filter
    if search_query:
        entries_queryset = entries_queryset.filter(
            Q(term__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(translations__translation__icontains=search_query)
        ).distinct()
    
    # Apply category filter
    if selected_category:
        entries_queryset = entries_queryset.filter(category=selected_category)
    
    # Apply tag filters
    if selected_tags:
        for tag in selected_tags:
            entries_queryset = entries_queryset.filter(tags__name__icontains=tag)
    
    # Handle random mode
    if random_mode:
        # Get random sample
        total_count = entries_queryset.count()
        if total_count > 0:
            sample_size = min(12, total_count)
            random_ids = random.sample(
                list(entries_queryset.values_list('id', flat=True)), 
                sample_size
            )
            entries = entries_queryset.filter(id__in=random_ids)
        else:
            entries = Entry.objects.none()
    else:
        # Apply ordering and pagination
        entries_queryset = entries_queryset.order_by('term')  # Order by term alphabetically
        paginator = Paginator(entries_queryset, 12)  # 12 entries per page
        page_number = request.GET.get('page')
        entries = paginator.get_page(page_number)
    
    # Get user statistics if authenticated
    user_stats = {}
    if request.user.is_authenticated:
        user_stats = {
            'favorites_count': UserFavorite.objects.filter(user=request.user).count(),
            'viewed_count': UserProgress.objects.filter(user=request.user).count(),
        }
    
    # Get country-specific statistics
    if country == 'belgium':
        total_entries = Entry.objects.filter(region_code='BE').count()
        total_tags = Tag.objects.filter(entry__region_code='BE').distinct().count()
    else:
        total_entries = Entry.objects.filter(language_code=language_code).count()
        total_tags = Tag.objects.filter(entry__language_code=language_code).distinct().count()
    
    # Store selected country in session
    request.session['selected_country'] = country
    
    context = {
        'entries': entries,
        'country': country,
        'country_info': country_info,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_tags': selected_tags,
        'random_mode': random_mode,
        'favorites_only': favorites_only,
        'total_entries': total_entries,
        'total_tags': total_tags,
        'user_stats': user_stats,
        'is_paginated': hasattr(entries, 'has_other_pages') and entries.has_other_pages(),
        'page_obj': entries if hasattr(entries, 'has_other_pages') else None,
    }
    
    return render(request, 'entries/country_entry_list.html', context)

# Language selection views
from django.http import JsonResponse
from django.utils import translation
from django.conf import settings
import json

def language_selection_view(request):
    """Language selection landing page."""
    return render(request, 'entries/language_selection.html')

def set_language_view(request):
    """Set user's preferred language using Django's i18n system."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            language = data.get('language', 'en')
            
            if language in ['en', 'es']:
                # Activate the language for the current request
                translation.activate(language)
                # Use the correct session key constant
                request.session[settings.LANGUAGE_COOKIE_NAME] = language
                request.session['user_language'] = language
                
                # Set the language cookie
                response = JsonResponse({'status': 'success', 'language': language})
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
                return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid language'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def quiz_test_view(request):
    """Test view for debugging quiz functionality."""
    return render(request, 'entries/quiz_test.html')

# Node.js Backend Integration Views
def signup_nodejs_view(request):
    """Signup page that connects to Node.js backend."""
    return render(request, 'registration/signup_nodejs.html')

def login_nodejs_view(request):
    """Login page that connects to Node.js backend."""
    return render(request, 'registration/login_nodejs.html')

def verify_email_view(request):
    """Email verification page that connects to Node.js backend."""
    return render(request, 'registration/verify_email.html')
