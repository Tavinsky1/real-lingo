"""
Enhanced API views for user analytics, achievements, and advanced features.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg, Max, F
from django.utils import timezone
from datetime import datetime, timedelta
import random
import re

from .models import Entry, Tag, UserFavorite, UserProgress
from .serializers import (
    UserStatsSerializer, AchievementSerializer, EntrySerializer,
    UserFavoriteSerializer, UserProgressSerializer
)
from .achievements import AchievementManager

SPANISH_MEANINGS = {
    "chamuyo": "Charla persuasiva, piropo o intento de convencer con palabras bonitas.",
    "chamuyar": "Hablar con intención de convencer, adular o seducir.",
    "ya fue": "No importa, olvídalo, ya pasó.",
    "talle": "Tamaño de ropa.",
    "pandulce": "Pan dulce típico de Navidad.",
    "chocar la ferrari": "Arruinar algo valioso o desperdiciar una gran oportunidad.",
    "che": "Interjección para llamar la atención, como 'oye'.",
    "boludo": "Persona tonta o amigo, según el contexto.",
    "pibe": "Niño o joven.",
    "laburo": "Trabajo o empleo.",
    "parcero": "Amigo o compañero (Colombia).",
    "chimba": "Genial o excelente (Colombia).",
    "bacano": "Bueno o agradable (Colombia).",
    "tinto": "Café negro (Colombia)",
}


class UserAnalyticsViewSet(viewsets.ViewSet):
    """
    Advanced user analytics and statistics API.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get comprehensive dashboard statistics for the user."""
        user = request.user
        
        # Basic counts
        total_favorites = UserFavorite.objects.filter(user=user).count()
        total_entries_viewed = UserProgress.objects.filter(user=user).count()
        total_learned = UserProgress.objects.filter(
            user=user, 
            difficulty_rating='MASTERED'
        ).count()
        
        # Calculate streak
        today = datetime.now().date()
        streak_days = 0
        check_date = today
        
        while True:
            if UserProgress.objects.filter(user=user, last_viewed__date=check_date).exists():
                streak_days += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        # Daily/Weekly/Monthly progress
        daily_goal = 5
        weekly_goal = 50
        monthly_goal = 200
        
        daily_viewed = UserProgress.objects.filter(
            user=user, 
            last_viewed__date=today
        ).count()
        
        week_start = today - timedelta(days=today.weekday())
        weekly_viewed = UserProgress.objects.filter(
            user=user,
            last_viewed__date__gte=week_start
        ).count()
        
        month_start = today.replace(day=1)
        monthly_viewed = UserProgress.objects.filter(
            user=user,
            last_viewed__date__gte=month_start
        ).count()
        
        # Language statistics
        favorite_languages = list(
            UserFavorite.objects.filter(user=user)
            .values('entry__language_code')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        language_progress = {}
        for lang_stat in favorite_languages:
            lang_code = lang_stat['entry__language_code']
            language_progress[lang_code] = {
                'favorites': lang_stat['count'],
                'learned': UserProgress.objects.filter(
                    user=user,
                    entry__language_code=lang_code,
                    difficulty_rating='MASTERED'
                ).count()
            }
        
        # Category statistics
        favorite_categories = list(
            UserFavorite.objects.filter(user=user)
            .exclude(entry__category__isnull=True)
            .values('entry__category')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        category_progress = {}
        for cat_stat in favorite_categories:
            category = cat_stat['entry__category']
            category_progress[category] = {
                'favorites': cat_stat['count'],
                'learned': UserProgress.objects.filter(
                    user=user,
                    entry__category=category,
                    difficulty_rating='MASTERED'
                ).count()
            }
        
        # Recent activity
        recent_activity = []
        recent_progress = UserProgress.objects.filter(
            user=user
        ).select_related('entry').order_by('-last_viewed')[:10]
        
        for progress in recent_progress:
            recent_activity.append({
                'type': 'viewed',
                'entry_id': progress.entry.id,
                'entry_term': progress.entry.term,
                'entry_language': progress.entry.language_code,
                'timestamp': progress.last_viewed,
                'difficulty': progress.difficulty_rating
            })
        
        # Achievement data
        achievements = AchievementManager.get_user_achievements(user)
        completed_achievements = [a for a in achievements if a['completed']]
        next_achievements = AchievementManager.get_next_achievements(user, 3)
        
        data = {
            'total_favorites': total_favorites,
            'total_entries_viewed': total_entries_viewed,
            'total_learned': total_learned,
            'streak_days': streak_days,
            'daily_progress': min(100, (daily_viewed / daily_goal) * 100) if daily_goal > 0 else 0,
            'weekly_progress': min(100, (weekly_viewed / weekly_goal) * 100) if weekly_goal > 0 else 0,
            'monthly_progress': min(100, (monthly_viewed / monthly_goal) * 100) if monthly_goal > 0 else 0,
            'favorite_languages': favorite_languages,
            'language_progress': language_progress,
            'favorite_categories': favorite_categories,
            'category_progress': category_progress,
            'achievements': completed_achievements,
            'next_achievements': next_achievements,
            'recent_activity': recent_activity,
            'achievement_points': AchievementManager.get_achievement_points(user)
        }
        
        serializer = UserStatsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def achievements(self, request):
        """Get all user achievements with progress."""
        user = request.user
        achievements = AchievementManager.get_user_achievements(user)
        
        # Filter by category if requested
        category = request.query_params.get('category')
        if category:
            achievements = [a for a in achievements if a['category'].lower() == category.lower()]
        
        # Filter by completion status
        completed_only = request.query_params.get('completed_only') == 'true'
        if completed_only:
            achievements = [a for a in achievements if a['completed']]
        
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get user leaderboard data."""
        # Top learners by mastered entries
        top_learners = []
        users_with_progress = User.objects.annotate(
            mastered_count=Count(
                'progress__id',
                filter=Q(progress__difficulty_rating='MASTERED')
            )
        ).filter(mastered_count__gt=0).order_by('-mastered_count')[:10]
        
        for user in users_with_progress:
            achievement_points = AchievementManager.get_achievement_points(user)
            top_learners.append({
                'username': user.username,
                'mastered_count': user.mastered_count,
                'achievement_points': achievement_points
            })
        
        # Current user's rank
        current_user_rank = None
        if request.user.is_authenticated:
            user_mastered = UserProgress.objects.filter(
                user=request.user,
                difficulty_rating='MASTERED'
            ).count()
            
            better_users = User.objects.annotate(
                mastered_count=Count(
                    'progress__id',
                    filter=Q(progress__difficulty_rating='MASTERED')
                )
            ).filter(mastered_count__gt=user_mastered).count()
            
            current_user_rank = better_users + 1
        
        return Response({
            'top_learners': top_learners,
            'current_user_rank': current_user_rank,
            'current_user_mastered': user_mastered if request.user.is_authenticated else 0
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def search_autocomplete(request):
    """Advanced search autocomplete with suggestions."""
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return Response({'suggestions': []})
    
    # Term suggestions
    term_suggestions = list(
        Entry.objects.filter(term__icontains=query)
        .values_list('term', flat=True)
        .distinct()[:8]
    )
    
    # Translation suggestions
    translation_suggestions = list(
        Entry.objects.filter(translations__translation__icontains=query)
        .values_list('translations__translation', flat=True)
        .distinct()[:5]
    )
    
    # Tag suggestions
    tag_suggestions = list(
        Tag.objects.filter(name__icontains=query)
        .values_list('name', flat=True)
        .distinct()[:3]
    )
    
    # Language suggestions
    language_suggestions = list(
        Entry.objects.filter(language_code__icontains=query)
        .values('language_code')
        .annotate(count=Count('id'))
        .order_by('-count')[:3]
    )
    
    return Response({
        'suggestions': {
            'terms': term_suggestions,
            'translations': translation_suggestions,
            'tags': tag_suggestions,
            'languages': [ls['language_code'] for ls in language_suggestions]
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def word_of_the_day(request):
    """Get word of the day with rotation logic."""
    # Use current date as seed for consistent daily rotation
    today = datetime.now().date()
    seed = int(today.strftime('%Y%m%d'))
    random.seed(seed)
    
    # Get a random featured entry
    total_entries = Entry.objects.count()
    if total_entries == 0:
        return Response({'error': 'No entries available'}, status=404)
    
    random_index = random.randint(0, total_entries - 1)
    word_of_day = Entry.objects.select_related().prefetch_related(
        'tags', 'translations', 'examples'
    )[random_index]
    
    serializer = EntrySerializer(word_of_day, context={'request': request})
    
    return Response({
        'word_of_the_day': serializer.data,
        'date': today.isoformat(),
        'fun_fact': _get_language_fun_fact(word_of_day.language_code)
    })

def _get_language_fun_fact(language_code):
    """Get a fun fact about the language."""
    facts = {
        'en': 'English has borrowed words from over 350 languages!',
        'es': 'Spanish is spoken by over 500 million people worldwide.',
        'fr': 'French was the official language of England for about 300 years.',
        'de': 'German has the longest compound words in the world.',
        'it': 'Italian is closest to Latin among all Romance languages.',
        'pt': 'Portuguese is the 6th most spoken language globally.',
        'ru': 'Russian has 6 grammatical cases for nouns.',
        'ja': 'Japanese has 3 writing systems used simultaneously.',
        'ko': 'Korean has 7 speech levels based on formality.',
        'zh': 'Chinese characters can represent both meaning and sound.',
    }
    return facts.get(language_code, 'Every language has its own unique beauty!')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_entry_view(request):
    """Track when a user views an entry for analytics."""
    entry_id = request.data.get('entry_id')
    if not entry_id:
        return Response({'error': 'entry_id required'}, status=400)
    
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        return Response({'error': 'Entry not found'}, status=404)
    
    # Create or update user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        entry=entry,
        defaults={'times_viewed': 1}
    )
    
    if not created:
        progress.times_viewed = F('times_viewed') + 1
        progress.save(update_fields=['times_viewed', 'last_viewed'])
        progress.refresh_from_db()
    
    # Check for new achievements
    achievements_before = len([a for a in AchievementManager.get_user_achievements(request.user) if a['completed']])
    achievements_after = len([a for a in AchievementManager.get_user_achievements(request.user) if a['completed']])
    
    new_achievements = []
    if achievements_after > achievements_before:
        all_achievements = AchievementManager.get_user_achievements(request.user)
        # This is simplified - in a real implementation you'd track exactly which achievements were just completed
        new_achievements = AchievementManager.get_recent_achievements(request.user, 1)
    
    return Response({
        'success': True,
        'times_viewed': progress.times_viewed,
        'new_achievements': new_achievements
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def quiz_questions(request):
    """Generate quiz questions based on available entries with enhanced quality control."""
    count = min(int(request.GET.get('count', 5)), 10)  # Max 10 questions
    language = request.GET.get('language')
    category = request.GET.get('category')
    user_language = request.GET.get('user_language', 'en')  # User's interface language

    # Filter entries and prioritize high-quality ones
    entries_query = Entry.objects.select_related().prefetch_related('translations')
    if language:
        entries_query = entries_query.filter(language_code=language)
    if category:
        entries_query = entries_query.filter(category=category)

    # First try to get entries with curated meanings
    curated_entries = []
    if user_language == 'es':
        curated_entries = [e for e in entries_query if hasattr(e, 'meaning_es') and e.meaning_es and not _is_generic(e.meaning_es)]
    elif user_language == 'en':
        curated_entries = [e for e in entries_query if hasattr(e, 'meaning_en') and e.meaning_en and not _is_generic(e.meaning_en)]
    
    # If not enough curated entries, supplement with dictionary entries
    dictionary_terms = list(SPANISH_MEANINGS.keys()) if user_language == 'es' else list(ENGLISH_MEANINGS.keys())
    dictionary_entries = list(entries_query.filter(term__iregex=r'^(' + '|'.join(dictionary_terms) + ')$'))
    
    # Combine and prioritize curated content
    available_entries = list(set(curated_entries + dictionary_entries))
    
    # If still not enough, add other high-quality entries
    if len(available_entries) < count * 3:
        other_entries = []
        for entry in entries_query.exclude(id__in=[e.id for e in available_entries]):
            meaning = _get_meaning_for_term(entry.term, entry.category, entry, user_language)
            if meaning and _is_valid_quiz_option(meaning, entry.term):
                other_entries.append(entry)
                if len(other_entries) >= count * 2:
                    break
        available_entries.extend(other_entries)

    if len(available_entries) < count:
        return Response({
            'error': f'Not enough high-quality entries for quiz. Found {len(available_entries)}, need {count}',
            'available_count': len(available_entries)
        }, status=400)

    # Randomly sample entries, ensuring we have enough for filtering
    sample_size = min(count * 5, len(available_entries))
    sampled_entries = random.sample(available_entries, sample_size)

    questions = []
    used_correct_answers = set()  # Track used answers to prevent repetition
    used_terms = set()  # Track used terms to prevent duplicate questions
    attempts = 0
    max_attempts = len(sampled_entries)
    
    for entry in sampled_entries:
        attempts += 1
        if len(questions) >= count:
            break
            
        # Skip if we've already used this term
        if entry.term.lower() in used_terms:
            continue
            
        correct_answer = _get_meaning_for_term(entry.term, entry.category, entry, user_language)
        if not correct_answer or not _is_valid_quiz_option(correct_answer, entry.term):
            continue
            
        # Skip if we've already used this answer to prevent repetition
        correct_answer_normalized = correct_answer.lower().strip()
        if correct_answer_normalized in used_correct_answers:
            continue
            
        # Generate high-quality distractors
        distractors = []
        distractor_pool = Entry.objects.filter(language_code=entry.language_code).exclude(id=entry.id)
        
        # Prefer distractors from same category for more challenging questions
        same_category_distractors = list(distractor_pool.filter(category=entry.category).order_by('?')[:20])
        other_distractors = list(distractor_pool.exclude(category=entry.category).order_by('?')[:30])
        
        # Combine and shuffle distractor candidates
        all_distractor_candidates = same_category_distractors + other_distractors
        random.shuffle(all_distractor_candidates)
        
        for d_entry in all_distractor_candidates:
            if len(distractors) >= 3:
                break
                
            d_meaning = _get_meaning_for_term(d_entry.term, d_entry.category, d_entry, user_language)
            if (d_meaning and 
                _is_valid_quiz_option(d_meaning, d_entry.term) and 
                d_meaning.lower().strip() != correct_answer_normalized and  # Ensure different from correct answer
                d_meaning.lower().strip() not in [d.lower().strip() for d in distractors] and  # Ensure unique distractors
                d_meaning.lower().strip() not in used_correct_answers and  # Don't use previous correct answers as distractors
                not _meanings_too_similar(correct_answer, d_meaning)):
                distractors.append(d_meaning)
        
        # Only create question if we have enough quality distractors
        if len(distractors) < 3:
            continue
            
        choices = [correct_answer] + distractors[:3]
        random.shuffle(choices)
        
        # Update correct answer index after shuffling
        correct_answer_index = choices.index(correct_answer)
        
        # Determine question format based on category
        question_text = _get_question_text(entry.term, entry.category, user_language)
        
        questions.append({
            'id': entry.id,
            'question': question_text,
            'choices': choices,
            'correct_answer': correct_answer,
            'correct_index': correct_answer_index,
            'language_code': entry.language_code,
            'category': entry.category,
            'translation': correct_answer,
            'answer_lang': user_language,
            'explanation': _get_explanation(entry, user_language)
        })
        
        # Track used answers and terms to prevent repetition
        used_correct_answers.add(correct_answer_normalized)
        used_terms.add(entry.term.lower())

    if len(questions) == 0:
        return Response({
            'error': 'Could not generate any high-quality questions with the current content',
            'suggestions': 'Consider adding more curated meanings or improving content quality'
        }, status=400)

    return Response({'questions': questions})


GENERIC_PHRASES = [
    'slang term', 'colloquial phrase', 'tongue twister', 
    'street language', 'local expression', 'insult', 'compliment', 'greeting', 'farewell',
    'idiomatic expression', 'common phrase', 'regional saying',
    'a phrase used', 'a term for', 'a word for', 'a way to',
    'in lunfardo', 'argentine slang', 'argentinian slang', 'german slang', 'australian slang',
    'used to address', 'used to refer', 'used to describe', 'used to express',
    'my precious daughter',
    'well',
    'no translation', 'no definite translation', 'no clear translation',
    'chapter:', 'page:', 'section:',
    'see notes', 'see above', 'see below', 'see entry',
    'placeholder', 'todo', 'tbd', 'to be determined',
    'translation needed', 'needs translation', 'requires translation',
    '[traducción', 'traduccion', '[translation]',
    'ai generated', 'automatically generated', 'auto-generated',
    'this term', 'this word', 'this phrase', 'this expression',
    'the term appears', 'the word appears', 'appears to be',
    'might be', 'could be', 'possibly', 'perhaps',
    'without context', 'context needed', 'more context required',
]

def _is_generic(text):
    """Check if a text string is generic or a placeholder."""
    if not text or not isinstance(text, str):
        return True
    
    text_lower = text.lower().strip()
    
    # Check for empty or very short content
    if len(text_lower) < 3:
        return True
    
    # Check for generic phrases
    if any(p in text_lower for p in GENERIC_PHRASES):
        return True
    
    # Check for AI-generated uncertainty markers
    uncertainty_markers = [
        'the provided entry', 'the given entry', 'this entry',
        'lacks', 'lacks a', 'doesn\'t offer', 'doesn\'t provide',
        'insufficient information', 'limited information',
        'cannot be determined', 'unclear from', 'ambiguous',
        'requires more', 'needs more', 'without further',
    ]
    if any(marker in text_lower for marker in uncertainty_markers):
        return True
    
    # Check for meta-commentary about definitions
    meta_patterns = [
        'definition', 'meaning', 'explanation', 'translation',
        'entry', 'text', 'content', 'information'
    ]
    if any(f'the {pattern}' in text_lower or f'this {pattern}' in text_lower 
           for pattern in meta_patterns):
        return True
    
    return False

ENGLISH_MEANINGS = {
    "chamuyo": "Sweet talk, flattery, or deceptive talk to persuade someone.",
    "chamuyar": "To sweet-talk, flatter, or try to persuade with smooth or deceptive talk.",
    "ya fue": "Forget it, it's over, it doesn't matter anymore.",
    "talle": "Clothing size.",
    "pandulce": "A sweet bread eaten at Christmas.",
    "chocar la ferrari": "To ruin something valuable or waste a great opportunity.",
    "che": "Hey, dude (common interjection).",
    "boludo": "Dude or idiot, depending on context.",
    "pibe": "Young person or kid.",
    "laburo": "Work or job.",
    "parcero": "Friend or buddy (Colombia).",
    "chimba": "Cool or awesome (Colombia).",
    "bacano": "Cool or nice (Colombia).",
    "tinto": "Black coffee (Colombia)",
    # German terms
    "alter": "Informal way to say 'dude' or 'man'.",
    "krass": "Means 'awesome' or 'intense'.",
    "geil": "Originally vulgar, now commonly used to mean 'cool' or 'awesome'.",
    "digger": "North German slang for 'buddy' or 'mate'.",
    "servus": "Bavarian/Austrian greeting meaning 'hello' or 'goodbye'.",
    "bock": "Means 'desire' or 'motivation'.",
    "abfahrt": "Means 'awesome' or 'wicked'.",
    "chillen": "To relax or chill out.",
    "checken": "To understand or get something.",
    "hammer": "Means 'awesome' or 'amazing'.",
    "kumpel": "Informal word for friend or buddy.",
    "mucke": "Slang for music.",
    "pennen": "To sleep.",
    "knorke": "Berlin slang meaning 'great' or 'fantastic'.",
    "icke": "Berlin dialect for 'I' or 'me'.",
    "zoff": "Means trouble or conflict.",
    "quatsch": "Nonsense or rubbish.",
    "schweinerei": "Something outrageous or a mess.",
    "fetzig": "Cool or awesome.",
}


def _get_meaning_for_term(term, category, entry=None, lang='en'):
    """
    Generate a plausible, non-generic meaning for a term in the requested language.
    Returns None if no suitable meaning can be found.
    """
    term_lower = term.lower()
    # 1. Check for a curated meaning in the requested language
    if lang == 'es' and hasattr(entry, 'meaning_es') and entry.meaning_es:
        if not _is_generic(entry.meaning_es):
            return entry.meaning_es.strip()
    if lang == 'en' and hasattr(entry, 'meaning_en') and entry.meaning_en:
        if not _is_generic(entry.meaning_en):
            return entry.meaning_en.strip()
    # 2. Fallback to notes if in the right language
    if entry and hasattr(entry, 'notes') and entry.notes:
        notes = entry.notes.strip()
        if lang == 'en' and re.search(r'[a-zA-Z]', notes) and not _is_generic(notes) and not '[traducción' in notes:
            return notes
        if lang == 'es' and re.search(r'[áéíóúñü]', notes) and not _is_generic(notes):
            return notes
    # 3. Fallback to translation if it matches the language
    if entry and hasattr(entry, 'translations') and entry.translations.exists():
        for tr in entry.translations.all():
            if lang == 'en' and re.match(r'^[a-zA-Z0-9 ,.!?\'\"]+$', tr.translation) and not _is_generic(tr.translation):
                return tr.translation.strip()
            if lang == 'es' and re.search(r'[áéíóúñü]', tr.translation) and not _is_generic(tr.translation):
                return tr.translation.strip()
    # 4. Curated dictionary fallback (for Spanish)
    if lang == 'es' and term_lower in SPANISH_MEANINGS:
        return SPANISH_MEANINGS[term_lower]
    # 5. Curated dictionary fallback (for English)
    if lang == 'en' and term_lower in ENGLISH_MEANINGS:
        return ENGLISH_MEANINGS[term_lower]
    return None


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_results(request):
    """
    Submit quiz results and update user progress.
    """
    results = request.data.get('results', [])
    user = request.user

    if not results:
        return Response({'error': 'No results provided'}, status=status.HTTP_400_BAD_REQUEST)

    correct_answers = 0
    for result in results:
        entry_id = result.get('id')
        is_correct = result.get('correct')

        if entry_id is None or is_correct is None:
            continue

        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            continue

        progress, created = UserProgress.objects.get_or_create(
            user=user,
            entry=entry,
        )

        if is_correct:
            correct_answers += 1
            # Logic to advance difficulty rating
            if progress.difficulty_rating == 'NEW':
                progress.difficulty_rating = 'LEARNING'
            elif progress.difficulty_rating == 'LEARNING':
                progress.difficulty_rating = 'INTERMEDIATE'
            elif progress.difficulty_rating == 'INTERMEDIATE':
                progress.difficulty_rating = 'ADVANCED'
            elif progress.difficulty_rating == 'ADVANCED':
                progress.difficulty_rating = 'MASTERED'
        else:
            # Logic to regress difficulty rating
            if progress.difficulty_rating == 'MASTERED':
                progress.difficulty_rating = 'ADVANCED'
            elif progress.difficulty_rating == 'ADVANCED':
                progress.difficulty_rating = 'INTERMEDIATE'
            elif progress.difficulty_rating == 'INTERMEDIATE':
                progress.difficulty_rating = 'LEARNING'

        progress.save()

    # TODO: Check for quiz-related achievements
    # AchievementManager.check_quiz_achievements(user, score, total_questions)

    return Response({
        'success': True,
        'message': f'Quiz results submitted. You got {correct_answers}/{len(results)} correct.',
    }, status=status.HTTP_200_OK)

def _is_valid_quiz_option(text, term=None):
    """Return True if the text is a concise, valid quiz option."""
    if not text or not isinstance(text, str):
        return False
    
    text_stripped = text.strip()
    text_lower = text_stripped.lower()
    
    # Check for reasonable length (not too short, not too long)
    if len(text_stripped) < 3 or len(text_stripped) > 120:
        return False
    
    # Check if it's generic content
    if _is_generic(text_stripped):
        return False
    
    # Check for forbidden patterns specific to quiz options
    forbidden = [
        'the provided entry', 'example', 'context', 'ambiguous', 'without further information',
        'missing', 'insufficient', 'no further', 'cannot be determined', 'no specific', 'requires more',
        'see notes', 'see above', 'see below', 'typo', 'abbreviation', 'truncated', 'unclear', 'unknown',
        'not enough', 'no translation', 'not specified', 'not available', 'not given', 'not provided',
        'definition is', 'entry only', 'entry does not', 'entry indicates', 'entry shows', 'entry lists', 
        'entry includes', 'entry describes', 'entry highlights', 'entry notes', 'entry mentions', 
        'entry refers', 'entry suggests', 'entry states', 'entry uses', 'entry provides',
        'context-dependent', 'context dependent', 'contextual', 'contextually', 'context',
        'ambiguous', 'uncertain', 'unclear', 'unknown', 'unspecified', 'multi-meaning', 'contradictory',
        'further information', 'more information', 'more context', 'not enough context',
        'cannot determine', 'cannot be determined', 'not determinable', 'not possible', 'not clear',
        'not found', 'not listed', 'not defined', 'not described', 'not explained', 'not elaborated',
        'not detailed', 'not explicit', 'not explicitely', 'not explicitely stated',
        'based on the', 'according to', 'it appears', 'it seems', 'likely', 'probably',
        'chapter', 'page', 'section', 'document', 'source',
        'variant of', 'variation of', 'similar to', 'related to', 'type of',
    ]
    
    # Check if the term appears in the definition (would make it too obvious)
    if term and term.lower() in text_lower:
        return False
    
    # Check for forbidden patterns
    if any(f in text_lower for f in forbidden):
        return False
    
    # Check for repetitive words (poor quality indicator)
    words = text_lower.split()
    if len(words) > 3:
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only check meaningful words
                word_counts[word] = word_counts.get(word, 0) + 1
        # If any significant word appears more than twice, it's likely repetitive/poor quality
        if any(count > 2 for count in word_counts.values()):
            return False
    
    # Check for minimum content quality (should have some meaningful words)
    meaningful_words = [w for w in words if len(w) > 3 and w not in ['the', 'and', 'that', 'with', 'for']]
    if len(meaningful_words) < 1:
        return False
    
    return True


def _meanings_too_similar(meaning1, meaning2):
    """Check if two meanings are too similar to be good distractors."""
    if not meaning1 or not meaning2:
        return True
    
    # Convert to lowercase and split into words
    words1 = set(meaning1.lower().split())
    words2 = set(meaning2.lower().split())
    
    # Remove common words that don't matter for similarity
    common_words = {'a', 'an', 'the', 'of', 'to', 'and', 'or', 'in', 'on', 'at', 'for', 'with', 'by'}
    words1 = words1 - common_words
    words2 = words2 - common_words
    
    if len(words1) == 0 or len(words2) == 0:
        return True
    
    # Calculate similarity based on word overlap
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if len(union) == 0:
        return True
    
    similarity = len(intersection) / len(union)
    
    # If more than 50% of words overlap, they're too similar
    return similarity > 0.5


def _get_question_text(term, category, user_language):
    """Generate appropriate question text based on category and language."""
    if user_language == 'es':
        if category == 'unique_concepts':
            return f'¿Qué significa "{term}"?'
        elif category == 'insults':
            return f'¿Qué significa el insulto "{term}"?'
        elif category == 'jokes':
            return f'¿Qué significa "{term}" en este contexto?'
        elif category == 'tongue_twisters':
            return f'¿Qué significa "{term}"?'
        else:
            return f'¿Qué significa "{term}"?'
    else:  # English
        if category == 'unique_concepts':
            return f'What does "{term}" mean?'
        elif category == 'insults':
            return f'What does the insult "{term}" mean?'
        elif category == 'jokes':
            return f'What does "{term}" mean in this context?'
        elif category == 'tongue_twisters':
            return f'What does "{term}" mean?'
        else:
            return f'What does "{term}" mean?'


def _get_explanation(entry, user_language):
    """Generate a helpful explanation for the quiz answer."""
    if not entry:
        return None
    
    explanation_parts = []
    
    # Add category context
    if entry.category:
        if user_language == 'es':
            category_names = {
                'slang': 'jerga',
                'insults': 'insulto',
                'jokes': 'broma',
                'tongue_twisters': 'trabalenguas',
                'colloquial_phrases': 'frase coloquial',
                'unique_concepts': 'concepto único'
            }
            cat_name = category_names.get(entry.category, entry.category)
            explanation_parts.append(f"Esta es una {cat_name}")
        else:
            explanation_parts.append(f"This is a {entry.get_category_display()}")
    
    # Add regional context
    if entry.region_code:
        if user_language == 'es':
            explanation_parts.append(f"típica de {entry.region_code}")
        else:
            explanation_parts.append(f"typical of {entry.region_code}")
    
    # Add notes if available and appropriate
    if entry.notes and len(entry.notes) < 200 and not _is_generic(entry.notes):
        explanation_parts.append(entry.notes)
    
    return '. '.join(explanation_parts) if explanation_parts else None
