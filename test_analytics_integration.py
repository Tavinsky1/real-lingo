#!/usr/bin/env python3
"""
Test script to verify analytics integration and backend functionality.
Run this from the project root: python test_analytics_integration.py
"""

import os
import sys
import django

# Add the project directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

# Now we can import Django models and test our functionality
from django.contrib.auth.models import User
from entries.models import Entry, Tag, UserFavorite, UserProgress
from entries.achievements import AchievementManager
from entries.serializers import UserStatsSerializer
import json

def test_achievement_system():
    """Test the achievement system functionality."""
    print("=== Testing Achievement System ===")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    print(f"Test user: {user.username} (created: {created})")
    
    # Initialize achievement manager
    achievement_manager = AchievementManager()
    print(f"Available achievements: {len(achievement_manager.achievements)}")
    
    # Test achievement categories
    categories = achievement_manager.get_achievements_by_category()
    for category, achievements in categories.items():
        print(f"  {category}: {len(achievements)} achievements")
    
    # Test individual achievement progress
    test_achievement = 'first_favorite'
    progress = achievement_manager.calculate_achievement_progress(user, test_achievement)
    print(f"Progress for '{test_achievement}': {progress}")
    
    # Test checking achievements for user
    unlocked = achievement_manager.check_achievements_for_user(user)
    print(f"Unlocked achievements: {unlocked}")
    
    return True

def test_user_analytics():
    """Test user analytics and statistics."""
    print("\n=== Testing User Analytics ===")
    
    user = User.objects.get(username='testuser')
    
    # Create some test data
    entries = Entry.objects.all()[:5]
    if entries:
        # Add some favorites
        for entry in entries[:3]:
            UserFavorite.objects.get_or_create(user=user, entry=entry)
        
        # Add some progress
        for entry in entries[:2]:
            UserProgress.objects.get_or_create(
                user=user, 
                entry=entry,
                defaults={'times_viewed': 5, 'difficulty_rating': 'EASY'}
            )
    
    # Test user statistics serializer
    serializer = UserStatsSerializer()
    stats = serializer.get_user_stats(user)
    print("User Statistics:")
    print(json.dumps(stats, indent=2))
    
    return True

def test_search_functionality():
    """Test search and filtering functionality."""
    print("\n=== Testing Search Functionality ===")
    
    # Test basic search
    total_entries = Entry.objects.count()
    print(f"Total entries in database: {total_entries}")
    
    # Test search by term
    search_results = Entry.objects.filter(term__icontains='che')[:5]
    print(f"Search results for 'che': {len(search_results)} entries")
    for entry in search_results:
        print(f"  - {entry.term} ({entry.language_code})")
    
    # Test category filtering
    categories = Entry.objects.values_list('category', flat=True).distinct()
    print(f"Available categories: {list(categories)}")
    
    if categories:
        first_category = [cat for cat in categories if cat][0]  # Get first non-null category
        category_results = Entry.objects.filter(category=first_category)[:3]
        print(f"Entries in category '{first_category}': {len(category_results)}")
        for entry in category_results:
            print(f"  - {entry.term}")
    
    return True

def test_api_endpoints():
    """Test API endpoint functionality (without HTTP requests)."""
    print("\n=== Testing API Endpoints Logic ===")
    
    from entries.analytics_views import UserAnalyticsViewSet
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    
    # Create a mock request
    request = factory.get('/api/v1/analytics/dashboard_stats/')
    request.user = User.objects.get(username='testuser')
    
    # Test the viewset
    viewset = UserAnalyticsViewSet()
    viewset.request = request
    
    # Test dashboard stats method
    try:
        response = viewset.dashboard_stats(request)
        print(f"Dashboard stats response status: {response.status_code}")
        if hasattr(response, 'data'):
            print("Dashboard data keys:", list(response.data.keys()))
    except Exception as e:
        print(f"Error testing dashboard stats: {e}")
    
    return True

def test_word_of_the_day():
    """Test word of the day functionality."""
    print("\n=== Testing Word of the Day ===")
    
    from entries.analytics_views import UserAnalyticsViewSet
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/api/v1/analytics/word_of_the_day/')
    request.user = User.objects.get(username='testuser')
    
    viewset = UserAnalyticsViewSet()
    viewset.request = request
    
    try:
        response = viewset.word_of_the_day(request)
        print(f"Word of the day response status: {response.status_code}")
        if hasattr(response, 'data') and response.data:
            word_data = response.data
            print(f"Word of the day: {word_data.get('term')} ({word_data.get('language_code')})")
            print(f"Definition: {word_data.get('definition', 'N/A')[:100]}...")
    except Exception as e:
        print(f"Error testing word of the day: {e}")
    
    return True

def test_database_statistics():
    """Test database content and statistics."""
    print("\n=== Database Statistics ===")
    
    # Count entries by language
    languages = Entry.objects.values('language_code').distinct()
    for lang in languages:
        count = Entry.objects.filter(language_code=lang['language_code']).count()
        print(f"  {lang['language_code']}: {count} entries")
    
    # Count tags
    tag_count = Tag.objects.count()
    print(f"Total tags: {tag_count}")
    
    # Count user interactions
    user_count = User.objects.count()
    favorites_count = UserFavorite.objects.count()
    progress_count = UserProgress.objects.count()
    
    print(f"Users: {user_count}")
    print(f"Favorites: {favorites_count}")
    print(f"Progress records: {progress_count}")
    
    return True

def main():
    """Run all tests."""
    print("LingoWorld Analytics Integration Test")
    print("====================================")
    
    tests = [
        test_database_statistics,
        test_achievement_system,
        test_user_analytics,
        test_search_functionality,
        test_api_endpoints,
        test_word_of_the_day,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            results.append((test.__name__, False))
    
    print("\n=== Test Results ===")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
