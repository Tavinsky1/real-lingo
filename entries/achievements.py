"""
Achievement system for the Lingo Dictionary.
Tracks user progress and awards achievements based on various criteria.
"""

from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.contrib.auth.models import User
from .models import Entry, UserFavorite, UserProgress

class AchievementManager:
    """Manages user achievements and progress tracking."""
    
    ACHIEVEMENTS = {
        # Explorer Achievements
        'first_favorite': {
            'name': 'First Love',
            'description': 'Add your first favorite term',
            'icon': '💖',
            'category': 'Explorer',
            'points': 10,
            'rarity': 'common'
        },
        'polyglot_10': {
            'name': 'Mini Polyglot',
            'description': 'Learn terms from 10 different languages',
            'icon': '🌍',
            'category': 'Explorer',
            'points': 50,
            'rarity': 'uncommon'
        },
        'polyglot_25': {
            'name': 'Global Explorer',
            'description': 'Learn terms from 25 different languages',
            'icon': '🌏',
            'category': 'Explorer',
            'points': 100,
            'rarity': 'rare'
        },
        'category_master': {
            'name': 'Category Master',
            'description': 'Master terms from all available categories',
            'icon': '🎯',
            'category': 'Explorer',
            'points': 200,
            'rarity': 'epic'
        },
        
        # Collector Achievements
        'favorite_10': {
            'name': 'Collector',
            'description': 'Favorite 10 terms',
            'icon': '⭐',
            'category': 'Collector',
            'points': 25,
            'rarity': 'common'
        },
        'favorite_50': {
            'name': 'Enthusiast',
            'description': 'Favorite 50 terms',
            'icon': '🌟',
            'category': 'Collector',
            'points': 75,
            'rarity': 'uncommon'
        },
        'favorite_100': {
            'name': 'Curator',
            'description': 'Favorite 100 terms',
            'icon': '✨',
            'category': 'Collector',
            'points': 150,
            'rarity': 'rare'
        },
        'favorite_500': {
            'name': 'Archive Master',
            'description': 'Favorite 500 terms',
            'icon': '💎',
            'category': 'Collector',
            'points': 500,
            'rarity': 'legendary'
        },
        
        # Scholar Achievements
        'learned_10': {
            'name': 'Quick Learner',
            'description': 'Master 10 terms',
            'icon': '📚',
            'category': 'Scholar',
            'points': 30,
            'rarity': 'common'
        },
        'learned_50': {
            'name': 'Scholar',
            'description': 'Master 50 terms',
            'icon': '🎓',
            'category': 'Scholar',
            'points': 100,
            'rarity': 'uncommon'
        },
        'learned_100': {
            'name': 'Expert',
            'description': 'Master 100 terms',
            'icon': '🏆',
            'category': 'Scholar',
            'points': 200,
            'rarity': 'rare'
        },
        'learned_500': {
            'name': 'Grandmaster',
            'description': 'Master 500 terms',
            'icon': '👑',
            'category': 'Scholar',
            'points': 1000,
            'rarity': 'legendary'
        },
        
        # Streak Achievements
        'streak_7': {
            'name': 'Week Warrior',
            'description': 'Maintain a 7-day learning streak',
            'icon': '🔥',
            'category': 'Dedication',
            'points': 50,
            'rarity': 'uncommon'
        },
        'streak_30': {
            'name': 'Monthly Devotee',
            'description': 'Maintain a 30-day learning streak',
            'icon': '🌟',
            'category': 'Dedication',
            'points': 150,
            'rarity': 'rare'
        },
        'streak_100': {
            'name': 'Centurion',
            'description': 'Maintain a 100-day learning streak',
            'icon': '💯',
            'category': 'Dedication',
            'points': 500,
            'rarity': 'epic'
        },
        'streak_365': {
            'name': 'Year Master',
            'description': 'Maintain a 365-day learning streak',
            'icon': '🏅',
            'category': 'Dedication',
            'points': 2000,
            'rarity': 'legendary'
        },
        
        # Special Achievements
        'early_bird': {
            'name': 'Early Bird',
            'description': 'Log in before 8 AM on 5 different days',
            'icon': '🐦',
            'category': 'Special',
            'points': 40,
            'rarity': 'uncommon'
        },
        'night_owl': {
            'name': 'Night Owl',
            'description': 'Log in after 10 PM on 5 different days',
            'icon': '🦉',
            'category': 'Special',
            'points': 40,
            'rarity': 'uncommon'
        },
        'weekend_warrior': {
            'name': 'Weekend Warrior',
            'description': 'Learn on 10 weekends',
            'icon': '⚔️',
            'category': 'Special',
            'points': 60,
            'rarity': 'rare'
        },
        'slang_master': {
            'name': 'Slang Master',
            'description': 'Master 50 slang terms',
            'icon': '😎',
            'category': 'Special',
            'points': 100,
            'rarity': 'rare'
        },
        'culture_explorer': {
            'name': 'Culture Explorer',
            'description': 'Learn 25 cultural reference terms',
            'icon': '🎭',
            'category': 'Special',
            'points': 80,
            'rarity': 'rare'
        }
    }
    
    @classmethod
    def get_user_achievements(cls, user):
        """Get all achievements for a user with progress."""
        if not user.is_authenticated:
            return []
        
        achievements = []
        
        # Get user stats
        stats = cls._get_user_stats(user)
        
        for achievement_id, achievement_data in cls.ACHIEVEMENTS.items():
            progress, max_progress, completed = cls._calculate_achievement_progress(
                user, achievement_id, stats
            )
            
            achievement = {
                'id': achievement_id,
                'name': achievement_data['name'],
                'description': achievement_data['description'],
                'icon': achievement_data['icon'],
                'category': achievement_data['category'],
                'points': achievement_data['points'],
                'rarity': achievement_data['rarity'],
                'progress': progress,
                'max_progress': max_progress,
                'completed': completed,
                'completed_at': None  # TODO: Track completion dates
            }
            
            achievements.append(achievement)
        
        return achievements
    
    @classmethod
    def _get_user_stats(cls, user):
        """Get comprehensive user statistics."""
        favorites_count = UserFavorite.objects.filter(user=user).count()
        learned_count = UserProgress.objects.filter(
            user=user, 
            difficulty_rating='MASTERED'
        ).count()
        
        # Language diversity
        unique_languages = UserProgress.objects.filter(
            user=user
        ).values('entry__language_code').distinct().count()
        
        # Category diversity
        unique_categories = UserProgress.objects.filter(
            user=user
        ).exclude(entry__category__isnull=True).values('entry__category').distinct().count()
        
        # Slang mastery
        slang_mastered = UserProgress.objects.filter(
            user=user,
            difficulty_rating='MASTERED',
            entry__category__in=['SLANG', 'YOUTH_SLANG', 'URBAN_SLANG', 'REGIONAL_SLANG', 'INTERNET_SLANG']
        ).count()
        
        # Cultural references
        culture_mastered = UserProgress.objects.filter(
            user=user,
            difficulty_rating='MASTERED',
            entry__category='CULTURAL_REFERENCE'
        ).count()
        
        # Calculate streak
        streak_days = cls._calculate_streak(user)
        
        return {
            'favorites_count': favorites_count,
            'learned_count': learned_count,
            'unique_languages': unique_languages,
            'unique_categories': unique_categories,
            'slang_mastered': slang_mastered,
            'culture_mastered': culture_mastered,
            'streak_days': streak_days,
            'total_categories': 18  # Based on model choices
        }
    
    @classmethod
    def _calculate_achievement_progress(cls, user, achievement_id, stats):
        """Calculate progress for a specific achievement."""
        achievement = cls.ACHIEVEMENTS[achievement_id]
        
        # Favorite-based achievements
        if achievement_id == 'first_favorite':
            return min(stats['favorites_count'], 1), 1, stats['favorites_count'] >= 1
        elif achievement_id == 'favorite_10':
            return min(stats['favorites_count'], 10), 10, stats['favorites_count'] >= 10
        elif achievement_id == 'favorite_50':
            return min(stats['favorites_count'], 50), 50, stats['favorites_count'] >= 50
        elif achievement_id == 'favorite_100':
            return min(stats['favorites_count'], 100), 100, stats['favorites_count'] >= 100
        elif achievement_id == 'favorite_500':
            return min(stats['favorites_count'], 500), 500, stats['favorites_count'] >= 500
        
        # Learning-based achievements
        elif achievement_id == 'learned_10':
            return min(stats['learned_count'], 10), 10, stats['learned_count'] >= 10
        elif achievement_id == 'learned_50':
            return min(stats['learned_count'], 50), 50, stats['learned_count'] >= 50
        elif achievement_id == 'learned_100':
            return min(stats['learned_count'], 100), 100, stats['learned_count'] >= 100
        elif achievement_id == 'learned_500':
            return min(stats['learned_count'], 500), 500, stats['learned_count'] >= 500
        
        # Language diversity achievements
        elif achievement_id == 'polyglot_10':
            return min(stats['unique_languages'], 10), 10, stats['unique_languages'] >= 10
        elif achievement_id == 'polyglot_25':
            return min(stats['unique_languages'], 25), 25, stats['unique_languages'] >= 25
        
        # Category mastery
        elif achievement_id == 'category_master':
            return min(stats['unique_categories'], stats['total_categories']), stats['total_categories'], stats['unique_categories'] >= stats['total_categories']
        
        # Streak achievements
        elif achievement_id == 'streak_7':
            return min(stats['streak_days'], 7), 7, stats['streak_days'] >= 7
        elif achievement_id == 'streak_30':
            return min(stats['streak_days'], 30), 30, stats['streak_days'] >= 30
        elif achievement_id == 'streak_100':
            return min(stats['streak_days'], 100), 100, stats['streak_days'] >= 100
        elif achievement_id == 'streak_365':
            return min(stats['streak_days'], 365), 365, stats['streak_days'] >= 365
        
        # Special achievements
        elif achievement_id == 'slang_master':
            return min(stats['slang_mastered'], 50), 50, stats['slang_mastered'] >= 50
        elif achievement_id == 'culture_explorer':
            return min(stats['culture_mastered'], 25), 25, stats['culture_mastered'] >= 25
        
        # Placeholder for special achievements that need more complex logic
        elif achievement_id in ['early_bird', 'night_owl', 'weekend_warrior']:
            return 0, 5, False  # TODO: Implement time-based tracking
        
        return 0, 1, False
    
    @classmethod
    def _calculate_streak(cls, user):
        """Calculate user's current learning streak."""
        today = datetime.now().date()
        streak_days = 0
        check_date = today
        
        while True:
            if UserProgress.objects.filter(
                user=user, 
                last_viewed__date=check_date
            ).exists():
                streak_days += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        return streak_days
    
    @classmethod
    def get_recent_achievements(cls, user, limit=5):
        """Get recently completed achievements."""
        achievements = cls.get_user_achievements(user)
        completed = [a for a in achievements if a['completed']]
        # Sort by completion date when we implement it, for now just return first few
        return completed[:limit]
    
    @classmethod
    def get_achievement_points(cls, user):
        """Calculate total achievement points for user."""
        achievements = cls.get_user_achievements(user)
        return sum(a['points'] for a in achievements if a['completed'])
    
    @classmethod
    def get_next_achievements(cls, user, limit=3):
        """Get next achievements user is closest to completing."""
        achievements = cls.get_user_achievements(user)
        incomplete = [a for a in achievements if not a['completed']]
        
        # Sort by progress percentage
        incomplete.sort(key=lambda x: x['progress'] / x['max_progress'], reverse=True)
        
        return incomplete[:limit]
