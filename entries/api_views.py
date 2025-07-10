from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Entry, Tag
from django.db.models import Count
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """
    Comprehensive API documentation for the Lingo Dictionary API.
    """
    documentation = {
        "title": "Lingo Dictionary API Documentation",
        "version": "2.0",
        "description": "Enhanced API for accessing Argentinian slang dictionary data",
        "base_url": "/api/",
        "endpoints": {
            "entries": {
                "url": "/api/entries/",
                "methods": ["GET"],
                "description": "Access dictionary entries with advanced filtering and search",
                "features": [
                    "Advanced text search across multiple fields",
                    "Language, category, region, and tag filtering",
                    "Random sampling",
                    "Statistics",
                    "Completion scoring",
                    "Similar entries"
                ],
                "parameters": {
                    "search": "Text search across term, notes, translations, examples, and tags",
                    "language": "Filter by language code (partial match)",
                    "languages": "Filter by multiple language codes (comma-separated)",
                    "category": "Filter by category (multiple allowed)",
                    "region": "Filter by region code (partial match)",
                    "regions": "Filter by multiple region codes (comma-separated)",
                    "tags": "Filter by tag names (multiple allowed)",
                    "tag_ids": "Filter by tag IDs (comma-separated)",
                    "exclude_tags": "Exclude entries with these tags",
                    "has_translations": "Filter entries with/without translations (true/false)",
                    "has_examples": "Filter entries with/without examples (true/false)",
                    "has_notes": "Filter entries with/without notes (true/false)",
                    "has_tags": "Filter entries with/without tags (true/false)",
                    "min_translations": "Minimum number of translations",
                    "max_translations": "Maximum number of translations",
                    "min_examples": "Minimum number of examples",
                    "max_examples": "Maximum number of examples",
                    "min_tags": "Minimum number of tags",
                    "max_tags": "Maximum number of tags",
                    "completion_level": "Filter by completion level (incomplete/partial/complete)",
                    "created_today": "Filter entries created today (true/false)",
                    "created_this_week": "Filter entries created this week (true/false)",
                    "created_this_month": "Filter entries created this month (true/false)",
                    "created_after": "Filter entries created after date (YYYY-MM-DD)",
                    "created_before": "Filter entries created before date (YYYY-MM-DD)",
                    "random_count": "Return random sample of N entries",
                    "ordering": "Order results by field (term, created_at, etc.)",
                    "page": "Page number for pagination",
                    "page_size": "Number of results per page"
                },
                "actions": {
                    "/api/entries/statistics/": "Get comprehensive statistics about entries",
                    "/api/entries/random/": "Get random entries (use 'count' parameter)",
                    "/api/entries/search_suggestions/": "Get search suggestions (use 'q' parameter)",
                    "/api/entries/{id}/similar/": "Get similar entries based on tags and category"
                }
            },
            "tags": {
                "url": "/api/tags/",
                "methods": ["GET"],
                "description": "Access tags with usage statistics and filtering",
                "features": [
                    "Tag usage statistics",
                    "Popular tags",
                    "Tag-based analytics",
                    "Filter by usage count"
                ],
                "parameters": {
                    "search": "Text search in tag name and description",
                    "color": "Filter by exact color code",
                    "has_entries": "Filter tags with/without entries (true/false)",
                    "min_entries": "Minimum number of entries using this tag",
                    "max_entries": "Maximum number of entries using this tag",
                    "popular": "Show only popular tags (true)",
                    "ordering": "Order results by field (name, entries_count)",
                    "page": "Page number for pagination"
                },
                "actions": {
                    "/api/tags/popular/": "Get most popular tags (use 'limit' parameter)",
                    "/api/tags/statistics/": "Get tag usage statistics",
                    "/api/tags/{id}/entries/": "Get entries for a specific tag"
                }
            }
        },
        "examples": {
            "search_for_slang": "/api/entries/?search=che&category=SLANG",
            "get_german_entries": "/api/entries/?language=de",
            "random_5_entries": "/api/entries/random/?count=5",
            "entries_with_translations": "/api/entries/?has_translations=true",
            "popular_tags": "/api/tags/popular/?limit=10",
            "incomplete_entries": "/api/entries/?completion_level=incomplete",
            "recent_entries": "/api/entries/?created_this_week=true",
            "search_suggestions": "/api/entries/search_suggestions/?q=che"
        },
        "response_format": {
            "entries_list": {
                "count": "Total number of results",
                "next": "URL for next page",
                "previous": "URL for previous page", 
                "results": [
                    {
                        "id": "Entry ID",
                        "term": "The slang term",
                        "language_code": "Language code",
                        "region_code": "Region code",
                        "category": "Entry category",
                        "part_of_speech": "Part of speech",
                        "tags": "Array of tag objects",
                        "translations_count": "Number of translations",
                        "examples_count": "Number of examples",
                        "created_at": "Creation timestamp",
                        "updated_at": "Last update timestamp"
                    }
                ]
            },
            "entry_detail": {
                "id": "Entry ID",
                "term": "The slang term",
                "language_code": "Language code",
                "region_code": "Region code", 
                "category": "Entry category",
                "part_of_speech": "Part of speech",
                "notes": "Additional notes",
                "tags": "Array of tag objects with details",
                "translations": "Array of translation objects",
                "examples": "Array of example objects",
                "completion_score": "Completion percentage (0-100)",
                "created_at": "Creation timestamp",
                "updated_at": "Last update timestamp"
            }
        },
        "statistics": {
            "entries_endpoint": "/api/entries/statistics/",
            "tags_endpoint": "/api/tags/statistics/",
            "description": "Get comprehensive statistics about the dictionary data"
        }
    }
    
    return Response(documentation)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_health(request):
    """
    API health check endpoint.
    """
    # Basic database connectivity check
    try:
        entry_count = Entry.objects.count()
        tag_count = Tag.objects.count()
        status = "healthy"
    except Exception as e:
        entry_count = 0
        tag_count = 0
        status = "unhealthy"
    
    return Response({
        "status": status,
        "timestamp": request.META.get('HTTP_DATE', 'unknown'),
        "database": {
            "entries": entry_count,
            "tags": tag_count
        },
        "version": "2.0"
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_categories(request):
    """
    Get all available categories with their display names.
    """
    categories = []
    for code, display_name in Entry._meta.get_field('category').choices:
        categories.append({
            "code": code,
            "display_name": display_name,
            "count": Entry.objects.filter(category=code).count()
        })
    
    return Response({
        "categories": categories,
        "total_categories": len(categories)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_languages(request):
    """
    Get all available languages with entry counts.
    """
    languages = list(Entry.objects.values('language_code').annotate(
        count=Count('id')
    ).order_by('-count'))
    
    return Response({
        "languages": languages,
        "total_languages": len(languages)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_frontend_stats(request):
    """Get statistics for the frontend homepage."""
    total_entries = Entry.objects.count()
    total_tags = Tag.objects.count()
    total_categories = Entry.objects.exclude(category__isnull=True).values('category').distinct().count()
    
    # Get popular categories
    popular_categories = list(Entry.objects.exclude(category__isnull=True).values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:5])
    
    # Get latest entries
    latest_entries = Entry.objects.select_related().prefetch_related('tags').order_by('-created_at')[:5]
    latest_data = []
    for entry in latest_entries:
        latest_data.append({
            'id': entry.id,
            'term': entry.term,
            'language_code': entry.language_code,
            'category': entry.get_category_display() if entry.category else None,
            'tags': [tag.name for tag in entry.tags.all()[:3]]
        })
    
    return JsonResponse({
        'statistics': {
            'total_entries': total_entries,
            'total_tags': total_tags,
            'total_categories': total_categories,
        },
        'popular_categories': popular_categories,
        'latest_entries': latest_data,
        'timestamp': timezone.now().isoformat()
    })
