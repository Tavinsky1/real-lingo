from rest_framework import serializers
from .models import Tag, Entry, Translation, Example # Import your models

class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model."""
    class Meta:
        model = Tag
        fields = ['id', 'name'] # Fields to include in the API output


class TranslationSerializer(serializers.ModelSerializer):
    """Serializer for the Translation model."""
    class Meta:
        model = Translation
        fields = ['id', 'target_language_code', 'translation', 'literal_translation']
        # We don't include 'entry' here by default to avoid nesting loops,
        # unless specifically needed for a nested API structure later.


class ExampleSerializer(serializers.ModelSerializer):
    """Serializer for the Example model."""
    class Meta:
        model = Example
        fields = ['id', 'sentence', 'language_code', 'translation']


class EntrySerializer(serializers.ModelSerializer):
    """Serializer for the main Entry model."""
    # To show tag names instead of just tag IDs in the API:
    tags = TagSerializer(many=True, read_only=True)
    # To show related translations and examples directly nested in the Entry API response:
    translations = TranslationSerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)

    class Meta:
        model = Entry
        # List all fields from the Entry model you want exposed in the API
        fields = [
            'id',
            'term',
            'language_code',
            'region_code',
            'category',
            'part_of_speech',
            'notes',
            'tags', # Include the nested tags
            'translations', # Include the nested translations
            'examples', # Include the nested examples
            'created_at',
            'updated_at',
        ]
        # read_only_fields = ['created_at', 'updated_at'] # Often good practice