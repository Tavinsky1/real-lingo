# In entries/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views, analytics_views # Import all view modules

# Create a router and register our API viewsets with it.
router = DefaultRouter()
router.register(r'entries', views.EntryViewSet, basename='entry')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'favorites', views.UserFavoriteViewSet, basename='favorite')
router.register(r'progress', views.UserProgressViewSet, basename='progress')
router.register(r'analytics', analytics_views.UserAnalyticsViewSet, basename='analytics')

# The API URLs are now determined automatically by the router.
# These URLs will be included under the '/api/' path in the main urls.py
urlpatterns = [
    path('', include(router.urls)), # Include only the router URLs for the API
    
    # Additional API endpoints
    path('docs/', api_views.api_documentation, name='api-docs'),
    path('health/', api_views.api_health, name='api-health'),
    path('categories/', api_views.api_categories, name='api-categories'),
    path('languages/', api_views.api_languages, name='api-languages'),
    path('frontend-stats/', api_views.api_frontend_stats, name='api-frontend-stats'),
    
    # Enhanced Analytics & Features
    path('search/autocomplete/', analytics_views.search_autocomplete, name='search-autocomplete'),
    path('word-of-the-day/', analytics_views.word_of_the_day, name='word-of-the-day'),
    path('track-view/', analytics_views.track_entry_view, name='track-view'),
    path('quiz/questions/', analytics_views.quiz_questions, name='quiz-questions'),
    path('quiz/submit/', analytics_views.submit_quiz_results, name='quiz-submit'),
]