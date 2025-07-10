from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
from django.conf import settings
import uuid
from datetime import datetime, timedelta

# Create your models here.

class Tag(models.Model):
    name = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Tag name (e.g., 'slang', 'formal', 'offensive')"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Optional description of what this tag represents"
    )
    color = models.CharField(
        max_length=7,
        default="#6c757d",
        help_text="Hex color code for tag display (e.g., #ff5733)"
    )

    def __str__(self):
        return self.name

class Entry(models.Model):
    """Represents a single lingo entry (slang, idiom, tongue twister, etc.)."""
    term = models.CharField(
        max_length=255,
        null=False, blank=False,
        help_text="The original term or phrase in its native language."
    )
    language_code = models.CharField(
        max_length=15,
        null=False, blank=False,
        help_text="Language code (e.g., 'en', 'es', 'de-BE' for regional German)."
    )
    region_code = models.CharField(
        max_length=50,
        blank=True, null=True,
        help_text="Specific region if applicable (e.g., 'US-NY', 'Berlin', 'AU-NSW')."
    )
    # User who contributed/added this entry
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='contributed_entries',
        help_text="User who contributed this entry"
    )
    # Standardized category for the type of entry
    category = models.CharField(
        max_length=50,
        blank=True, null=True,
        choices=[
            ('slang', 'Slang'),
            ('insults', 'Insults'),
            ('tongue_twisters', 'Tongue Twisters'),
            ('colloquial_phrases', 'Colloquial Phrases'),
            ('jokes', 'Jokes'),
            ('unique_concepts', 'Unique Concepts'),
        ],
        help_text="Standardized category type: slang, insults, tongue twisters, colloquial phrases, jokes, or unique concepts."
    )
    part_of_speech = models.CharField(
        max_length=50,
        blank=True, null=True,
        help_text="Grammatical part of speech if applicable (e.g., 'noun', 'verb')."
    )
    notes = models.TextField(
        blank=True, null=True,
        help_text="General cultural notes, etymology, or usage context."
    )
    # We'll handle audio later, let's get the text structure first.
    # audio_file = models.FileField(upload_to='audio_pronunciations/', blank=True, null=True)
    created_at = models.DateTimeField(
        auto_now_add=True, # Automatically set when object is first created
        help_text="Timestamp when the entry was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, # Automatically set every time the object is saved
        help_text="Timestamp when the entry was last updated."
    )
    tags = models.ManyToManyField(Tag, blank=True)

    # This tells Django how to represent an Entry object as a string
    def __str__(self):
        return f"{self.term} ({self.language_code})"

    class Meta:
        verbose_name_plural = "Entries" # Makes the admin interface look nicer

class Translation(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='translations')
    target_language_code = models.CharField(
        max_length=15,
        help_text="Language code for the translation (e.g., 'en', 'es')."
    )
    translation = models.TextField(
        help_text="Main translation of the entry."
    )
    literal_translation = models.TextField(
        blank=True, null=True,
        help_text="Optional literal translation."
    )

    def __str__(self):
        return f"{self.translation} ({self.target_language_code})"

class Example(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='examples')
    sentence = models.TextField(
        help_text="Example sentence using the entry."
    )
    language_code = models.CharField(
        max_length=15,
        help_text="Language code of the example sentence."
    )
    translation = models.TextField(
        blank=True, null=True,
        help_text="Optional translation of the example sentence."
    )

    def __str__(self):
        return self.sentence

class UserFavorite(models.Model):
    """Represents a user's favorite entry."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'entry')  # Prevent duplicate favorites
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.entry.term}"

class UserProgress(models.Model):
    """Track user's learning progress with entries."""
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('MASTERED', 'Mastered'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='user_progress')
    difficulty_rating = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, null=True, blank=True)
    times_viewed = models.PositiveIntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Personal notes about this entry")
    
    class Meta:
        unique_together = ('user', 'entry')
        ordering = ['-last_viewed']
    
    def __str__(self):
        return f"{self.user.username} - {self.entry.term} ({self.difficulty_rating or 'Unrated'})"


class EmailVerification(models.Model):
    """Model to store email verification tokens."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Email Verification"
        verbose_name_plural = "Email Verifications"
    
    def __str__(self):
        return f"Email verification for {self.user.username}"
    
    def is_expired(self):
        """Check if the verification token has expired."""
        expiry_date = self.created_at + timedelta(days=getattr(settings, 'ACCOUNT_ACTIVATION_DAYS', 7))
        return datetime.now() > expiry_date.replace(tzinfo=None)
    
    def verify(self):
        """Mark the email as verified."""
        self.is_verified = True
        self.verified_at = datetime.now()
        self.save()
        
        # Activate the user account
        self.user.is_active = True
        self.user.save()


class UserAnalytics(models.Model):
    """Track user analytics and app usage"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True, blank=True,  # Allow anonymous users
        help_text="User performing the action (null for anonymous)"
    )
    session_id = models.CharField(
        max_length=100,
        help_text="Session identifier for anonymous users"
    )
    action = models.CharField(
        max_length=100,
        help_text="Action performed (e.g., 'page_view', 'quiz_taken', 'entry_viewed')"
    )
    page_url = models.CharField(
        max_length=500,
        help_text="URL of the page where action occurred"
    )
    country = models.CharField(
        max_length=50,
        blank=True, null=True,
        help_text="Country context (e.g., 'germany', 'argentina')"
    )
    entry_id = models.ForeignKey(
        Entry,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        help_text="Related entry if applicable"
    )
    quiz_score = models.IntegerField(
        blank=True, null=True,
        help_text="Quiz score if action is quiz-related"
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text="Browser user agent string"
    )
    ip_address = models.GenericIPAddressField(
        blank=True, null=True,
        help_text="User IP address (anonymized for privacy)"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "entries_user_analytics"
        verbose_name = "User Analytics"
        verbose_name_plural = "User Analytics"
        ordering = ['-timestamp']
    
    def __str__(self):
        user_display = self.user.username if self.user else f"Anonymous ({self.session_id[:8]})"
        return f"{user_display} - {self.action} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Feedback(models.Model):
    """User feedback and suggestions"""
    FEEDBACK_TYPES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('content', 'Content Suggestion'),
        ('other', 'Other'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="User who submitted the feedback"
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        default='other',
        help_text="Type of feedback"
    )
    title = models.CharField(
        max_length=200,
        help_text="Brief title describing the feedback"
    )
    description = models.TextField(
        help_text="Detailed description of the feedback"
    )
    country_context = models.CharField(
        max_length=50,
        blank=True, null=True,
        help_text="Country context if relevant"
    )
    page_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL where the issue/suggestion was noticed"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text="Priority level (set by admin)"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Current status of the feedback"
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes from admin team"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "entries_feedback"
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()}: {self.title} by {self.user.username}"