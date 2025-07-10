"""
Automated tests for quiz content quality and API functionality.
Run with: python manage.py test tests.test_quiz_quality
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from entries.models import Entry, Translation, Tag
from entries.analytics_views import _is_generic, _is_valid_quiz_option, _get_meaning_for_term


class QuizQualityTestCase(TestCase):
    """Test quiz content quality and generation."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test entries
        self.good_entry = Entry.objects.create(
            term='test_term',
            language_code='es-AR',
            category='slang',
            notes='This is a good quality definition with sufficient detail.'
        )
        
        self.poor_entry = Entry.objects.create(
            term='poor_term',
            language_code='es-AR',
            category='slang',
            notes='The provided entry lacks a detailed definition and is generic.'
        )
        
        # Create translations
        Translation.objects.create(
            entry=self.good_entry,
            target_language_code='en',
            translation='A well-written translation with proper context'
        )
        
        Translation.objects.create(
            entry=self.poor_entry,
            target_language_code='en',
            translation='slang term'
        )

    def test_generic_content_detection(self):
        """Test that generic content is properly detected."""
        # Test generic phrases
        self.assertTrue(_is_generic('slang term'))
        self.assertTrue(_is_generic('The provided entry lacks a detailed definition'))
        self.assertTrue(_is_generic('colloquial phrase'))
        self.assertTrue(_is_generic('translation needed'))
        
        # Test good content
        self.assertFalse(_is_generic('A friendly greeting used between friends'))
        self.assertFalse(_is_generic('Sweet talk or flattery to persuade someone'))
        
        # Test edge cases
        self.assertTrue(_is_generic(''))
        self.assertTrue(_is_generic('a'))
        self.assertTrue(_is_generic(None))

    def test_valid_quiz_option_detection(self):
        """Test that quiz options are properly validated."""
        # Test valid options
        self.assertTrue(_is_valid_quiz_option('A friendly greeting'))
        self.assertTrue(_is_valid_quiz_option('Sweet talk or flattery'))
        
        # Test invalid options
        self.assertFalse(_is_valid_quiz_option('The provided entry lacks'))
        self.assertFalse(_is_valid_quiz_option('slang term'))
        self.assertFalse(_is_valid_quiz_option(''))
        self.assertFalse(_is_valid_quiz_option('a' * 150))  # Too long
        
        # Test with term in definition (should be invalid)
        self.assertFalse(_is_valid_quiz_option('Che is a greeting', 'che'))

    def test_meaning_extraction(self):
        """Test meaning extraction for different entry types."""
        # Test good entry
        meaning = _get_meaning_for_term(
            self.good_entry.term,
            self.good_entry.category,
            self.good_entry,
            'en'
        )
        self.assertIsNotNone(meaning)
        self.assertNotEqual(meaning.strip(), '')
        
        # Test poor entry should return None or be filtered
        poor_meaning = _get_meaning_for_term(
            self.poor_entry.term,
            self.poor_entry.category,
            self.poor_entry,
            'en'
        )
        # Should either be None or the fallback translation should be valid
        if poor_meaning:
            self.assertFalse(_is_generic(poor_meaning))

    def test_quiz_api_endpoint(self):
        """Test the quiz questions API endpoint."""
        url = reverse('quiz_questions')  # Adjust URL name as needed
        
        # Test basic request
        response = self.client.get(url, {
            'language': 'es-AR',
            'user_language': 'en',
            'count': 2
        })
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertIn('questions', data)
            
            # Test question structure
            if data['questions']:
                question = data['questions'][0]
                required_fields = ['id', 'question', 'choices', 'correct_answer']
                for field in required_fields:
                    self.assertIn(field, question)
                
                # Test that choices are not generic
                for choice in question['choices']:
                    self.assertFalse(_is_generic(choice), f"Generic choice found: {choice}")
                    self.assertTrue(_is_valid_quiz_option(choice), f"Invalid choice: {choice}")

    def test_content_quality_scores(self):
        """Test content quality scoring."""
        # Good entry should have higher score
        good_score = self._calculate_quality_score(self.good_entry)
        poor_score = self._calculate_quality_score(self.poor_entry)
        
        self.assertGreater(good_score, poor_score)
        self.assertGreaterEqual(good_score, 3)  # Should have reasonable score
        self.assertLessEqual(poor_score, 5)  # Should be flagged as poor

    def _calculate_quality_score(self, entry):
        """Calculate quality score for an entry (simplified version)."""
        score = 0
        
        # Check notes quality
        if entry.notes and len(entry.notes) > 20 and not _is_generic(entry.notes):
            score += 3
        
        # Check translations
        for trans in entry.translations.all():
            if len(trans.translation) > 10 and not _is_generic(trans.translation):
                score += 2
                break
        
        # Check examples
        if entry.examples.exists():
            score += 1
        
        return score


class QuizFunctionalTestCase(TestCase):
    """Functional tests for quiz behavior."""
    
    def setUp(self):
        """Set up test data with more comprehensive entries."""
        # Create multiple quality entries for testing
        self.entries = []
        for i in range(10):
            entry = Entry.objects.create(
                term=f'test_term_{i}',
                language_code='es-AR',
                category='slang',
                notes=f'High quality definition number {i} with proper context and meaning.'
            )
            
            Translation.objects.create(
                entry=entry,
                target_language_code='en',
                translation=f'Well written English translation for term {i}'
            )
            
            self.entries.append(entry)

    def test_quiz_generation_with_sufficient_content(self):
        """Test that quiz generates successfully with quality content."""
        url = reverse('quiz_questions')
        
        response = self.client.get(url, {
            'language': 'es-AR',
            'user_language': 'en',
            'count': 5
        })
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertEqual(len(data['questions']), 5)
            
            # Verify all questions have 4 choices
            for question in data['questions']:
                self.assertEqual(len(question['choices']), 4)
                self.assertIn(question['correct_answer'], question['choices'])

    def test_quiz_handles_insufficient_content(self):
        """Test quiz behavior when there's insufficient quality content."""
        # Delete most entries to simulate insufficient content
        Entry.objects.filter(id__in=[e.id for e in self.entries[2:]]).delete()
        
        url = reverse('quiz_questions')
        response = self.client.get(url, {
            'language': 'es-AR',
            'user_language': 'en',
            'count': 5
        })
        
        # Should either return fewer questions or an error with helpful message
        if response.status_code == 400:
            data = json.loads(response.content)
            self.assertIn('error', data)
            self.assertIn('high-quality', data['error'].lower())


class ContentCurationTestCase(TestCase):
    """Test content curation tools and admin functionality."""
    
    def setUp(self):
        """Set up admin user and test content."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')
        
        # Create test entries with various quality levels
        self.high_quality = Entry.objects.create(
            term='excellent_term',
            language_code='es-AR',
            category='slang',
            notes='Comprehensive definition with cultural context and usage examples.'
        )
        
        self.low_quality = Entry.objects.create(
            term='poor_term',
            language_code='es-AR',
            category='slang',
            notes='slang term used to address someone'
        )

    def test_quality_report_generation(self):
        """Test that quality reports can be generated."""
        # This would test the admin action for generating quality reports
        # Implementation depends on your admin setup
        pass

    def test_content_export_for_curation(self):
        """Test content export functionality."""
        # This would test the admin action for exporting content for curation
        # Implementation depends on your admin setup
        pass


class PerformanceTestCase(TestCase):
    """Test performance of quiz generation and content quality checks."""
    
    def setUp(self):
        """Create large dataset for performance testing."""
        # Create 100 entries for performance testing
        entries = []
        for i in range(100):
            entries.append(Entry(
                term=f'performance_term_{i}',
                language_code='es-AR',
                category='slang',
                notes=f'Performance test definition {i} with adequate content length.'
            ))
        Entry.objects.bulk_create(entries)

    def test_quiz_generation_performance(self):
        """Test that quiz generation completes within reasonable time."""
        import time
        
        url = reverse('quiz_questions')
        start_time = time.time()
        
        response = self.client.get(url, {
            'language': 'es-AR',
            'user_language': 'en',
            'count': 5
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Quiz should generate within 2 seconds
        self.assertLess(duration, 2.0, f"Quiz generation took {duration:.2f} seconds")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.assertLessEqual(len(data['questions']), 5)


# Test runner command
if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests.test_quiz_quality"])