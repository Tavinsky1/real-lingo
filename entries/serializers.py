"""
Enhanced serializers for the Lingo Dictionary API with comprehensive user analytics.
"""

from rest_framework import serializers
from django.db.models import Count, Avg, Max
from django.contrib.auth.models import User
from .models import Tag, Entry, Translation, Example, UserFavorite, UserProgress

class TagSerializer(serializers.ModelSerializer):
    """Enhanced Tag serializer with usage statistics."""
    entries_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'color', 'entries_count']

class TranslationSerializer(serializers.ModelSerializer):
    """Translation serializer for nested entry data."""
    class Meta:
        model = Translation
        fields = ['id', 'target_language_code', 'translation', 'literal_translation']

class ExampleSerializer(serializers.ModelSerializer):
    """Example serializer for nested entry data."""
    class Meta:
        model = Example
        fields = ['id', 'sentence', 'language_code', 'translation']

class EntrySerializer(serializers.ModelSerializer):
    """Enhanced Entry serializer with comprehensive data."""
    tags = TagSerializer(many=True, read_only=True)
    translations = TranslationSerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)
    
    # Computed fields
    translations_count = serializers.IntegerField(read_only=True)
    examples_count = serializers.IntegerField(read_only=True)
    tags_count = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Entry
        fields = [
            'id', 'term', 'language_code', 'region_code', 'category', 
            'part_of_speech', 'notes', 'created_at', 'updated_at',
            'tags', 'translations', 'examples',
            'translations_count', 'examples_count', 'tags_count',
            'is_favorited', 'user_progress'
        ]
    
    def get_is_favorited(self, obj):
        """Check if current user has favorited this entry."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(user=request.user, entry=obj).exists()
        return False
    
    def get_user_progress(self, obj):
        """Get current user's progress on this entry."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserProgress.objects.get(user=request.user, entry=obj)
                return {
                    'difficulty_rating': progress.difficulty_rating,
                    'times_viewed': progress.times_viewed,
                    'last_viewed': progress.last_viewed,
                    'notes': progress.notes
                }
            except UserProgress.DoesNotExist:
                return None
        return None


class UserFavoriteSerializer(serializers.ModelSerializer):
    """User favorite serializer with entry details."""
    entry = EntrySerializer(read_only=True)
    entry_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserFavorite
        fields = ['id', 'entry', 'entry_id', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserProgressSerializer(serializers.ModelSerializer):
    """User progress serializer with entry details."""
    entry = EntrySerializer(read_only=True)
    entry_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'entry', 'entry_id', 'difficulty_rating', 
            'times_viewed', 'last_viewed', 'notes'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Increment times_viewed when updating
        instance.times_viewed += 1
        return super().update(instance, validated_data)

class UserStatsSerializer(serializers.Serializer):
    """Comprehensive user statistics serializer."""
    total_favorites = serializers.IntegerField()
    total_entries_viewed = serializers.IntegerField()
    total_learned = serializers.IntegerField()
    streak_days = serializers.IntegerField()
    daily_progress = serializers.FloatField()
    weekly_progress = serializers.FloatField()
    monthly_progress = serializers.FloatField()
    
    # Language statistics
    favorite_languages = serializers.ListField()
    language_progress = serializers.DictField()
    
    # Category statistics
    favorite_categories = serializers.ListField()
    category_progress = serializers.DictField()
    
    # Achievement data
    achievements = serializers.ListField()
    recent_activity = serializers.ListField()

class AchievementSerializer(serializers.Serializer):
    """Achievement system serializer."""
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    category = serializers.CharField()
    progress = serializers.IntegerField()
    max_progress = serializers.IntegerField()
    completed = serializers.BooleanField()
    completed_at = serializers.DateTimeField(required=False)
    rarity = serializers.CharField()
    points = serializers.IntegerField()