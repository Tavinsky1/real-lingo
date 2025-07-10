from rest_framework import serializers
from django.db.models import Count
from .models import Tag, Entry, Translation, Example

class TagSerializer(serializers.ModelSerializer):
    """Enhanced serializer for the Tag model with usage statistics."""
    entries_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'color', 'entries_count']
    
    def get_entries_count(self, obj):
        # Use annotated count if available, otherwise query
        if hasattr(obj, 'entries_count'):
            return obj.entries_count
        return obj.entry_set.count()

class TranslationSerializer(serializers.ModelSerializer):
    """Enhanced serializer for the Translation model."""
    entry_term = serializers.CharField(source='entry.term', read_only=True)
    
    class Meta:
        model = Translation
        fields = ['id', 'target_language_code', 'translation', 'literal_translation', 'entry_term']

class ExampleSerializer(serializers.ModelSerializer):
    """Enhanced serializer for the Example model."""
    entry_term = serializers.CharField(source='entry.term', read_only=True)
    
    class Meta:
        model = Example
        fields = ['id', 'sentence', 'language_code', 'translation', 'entry_term']

class EntryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Entry lists."""
    tags = TagSerializer(many=True, read_only=True)
    translations_count = serializers.IntegerField(read_only=True)
    examples_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Entry
        fields = [
            'id', 'term', 'language_code', 'region_code', 'category', 
            'part_of_speech', 'tags', 'translations_count', 'examples_count', 
            'created_at', 'updated_at'
        ]

class EntryDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual Entry objects."""
    tags = TagSerializer(many=True, read_only=True)
    translations = TranslationSerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)
    completion_score = serializers.SerializerMethodField()
    
    class Meta:
        model = Entry
        fields = [
            'id', 'term', 'language_code', 'region_code', 'category',
            'part_of_speech', 'notes', 'tags', 'translations', 'examples',
            'completion_score', 'created_at', 'updated_at'
        ]
    
    def get_completion_score(self, obj):
        """Calculate completion score."""
        score = 20  # Base score for having a term
        
        if obj.notes:
            score += 20
        if obj.translations.exists():
            score += 25
        if obj.examples.exists():
            score += 25
        if obj.tags.exists():
            score += 10
            
        return score

# Keep the original EntrySerializer for backward compatibility
class EntrySerializer(EntryDetailSerializer):
    """Main Entry serializer - uses detailed version."""
    pass
