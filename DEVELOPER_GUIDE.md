# Real Lingo Developer Guide

## Overview

Real Lingo is a Django-based web application for learning authentic slang, idioms, and colloquial expressions from various countries. This guide covers the technical architecture, development workflows, and maintenance procedures.

## Architecture

### Backend (Django)

- **Framework**: Django 4.x with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Key Apps**: `entries` (main application)
- **Authentication**: Django's built-in user system with email verification

### Frontend

- **Templates**: Django templates with Bootstrap 5
- **JavaScript**: Vanilla JS for quiz functionality
- **CSS**: Custom CSS with responsive design
- **Icons**: Bootstrap Icons

### API

- **Quiz API**: `/api/quiz/questions/` and `/api/quiz/submit/`
- **Content API**: `/api/entries/` with advanced filtering
- **Documentation**: Available at `/api/` endpoint

## Core Models

### Entry
```python
class Entry(models.Model):
    term = models.CharField(max_length=255)
    language_code = models.CharField(max_length=15)
    region_code = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    notes = models.TextField(blank=True)
    meaning_es = models.TextField(blank=True)  # Curated Spanish meaning
    meaning_en = models.TextField(blank=True)  # Curated English meaning
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
```

### Translation
```python
class Translation(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    target_language_code = models.CharField(max_length=15)
    translation = models.TextField()
    literal_translation = models.TextField(blank=True)
```

### UserProgress
```python
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    difficulty_rating = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    times_viewed = models.PositiveIntegerField(default=0)
    last_viewed = models.DateTimeField(auto_now=True)
```

## Quiz System Architecture

### Question Generation Process

1. **Entry Selection**: Prioritizes entries with curated meanings (`meaning_es`, `meaning_en`)
2. **Quality Filtering**: Uses `_is_valid_quiz_option()` to ensure high-quality content
3. **Distractor Generation**: Creates plausible wrong answers from similar entries
4. **Language Adaptation**: Serves content in user's preferred language

### Content Quality Control

```python
# Key quality control functions
def _is_generic(text):
    """Detects generic/placeholder content"""
    
def _is_valid_quiz_option(text, term=None):
    """Validates quiz option quality"""
    
def _get_meaning_for_term(term, category, entry, lang):
    """Extracts best available meaning for term"""
```

### Quiz API Endpoints

#### GET `/api/quiz/questions/`
**Parameters:**
- `language`: Entry language (e.g., 'es-AR')
- `category`: Entry category (optional)
- `user_language`: UI language ('en' or 'es')
- `count`: Number of questions (1-10)

**Response:**
```json
{
  "questions": [
    {
      "id": 123,
      "question": "What does \"che\" mean?",
      "choices": ["Hey, dude", "Thank you", "Goodbye", "Please"],
      "correct_answer": "Hey, dude",
      "category": "slang",
      "explanation": "Common interjection in Argentina"
    }
  ]
}
```

#### POST `/api/quiz/submit/`
**Authentication**: Required
**Payload:**
```json
{
  "results": [
    {"id": 123, "correct": true}
  ]
}
```

## Development Setup

### Prerequisites
- Python 3.8+
- Django 4.x
- Virtual environment

### Installation
```bash
# Clone repository
git clone <repository-url>
cd real-lingo

# Create virtual environment
python -m venv lingo_env
source lingo_env/bin/activate  # On Windows: lingo_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Load sample data (if available)
python manage.py loaddata sample_data.json

# Run development server
python manage.py runserver
```

### Environment Variables
```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Content Management

### Admin Interface

Access the admin at `/admin/` with superuser credentials.

**Key admin features:**
- Entry management with quality scoring
- Bulk editing actions
- Content export for curation
- Quality reports generation

**Useful admin actions:**
- `generate_quality_report`: Export quality analysis
- `export_for_curation`: Export entries for manual curation
- `mark_needs_curation`: Flag entries needing attention

### Management Commands

#### Content Quality Reports
```bash
python manage.py content_quality_report --output-dir reports/
```
Generates comprehensive quality reports:
- `missing_meanings_{timestamp}.csv`: Entries needing curation
- `generic_content_{timestamp}.csv`: AI-generated content detection
- `quality_scores_{timestamp}.csv`: Quality scoring for all entries
- `translation_gaps_{timestamp}.csv`: Language coverage analysis
- `curation_priorities_{timestamp}.csv`: High-impact curation targets

#### Bulk Content Updates
```bash
# Export template for editing
python manage.py bulk_update_meanings --export-template

# Import curated content
python manage.py bulk_update_meanings --csv-file curated_meanings.csv
python manage.py bulk_update_meanings --json-file curated_meanings.json

# Dry run to preview changes
python manage.py bulk_update_meanings --csv-file data.csv --dry-run
```

## Testing

### Backend Tests
```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test tests.test_quiz_quality

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Tests
Open `tests/test_frontend_quiz.html` in browser to run:
- Quiz functionality tests
- Accessibility compliance tests
- Responsive design tests
- Performance monitoring

### Test Categories

**Quiz Quality Tests:**
- Generic content detection
- Valid quiz option validation
- Meaning extraction quality
- API endpoint functionality

**Functional Tests:**
- Quiz generation with sufficient content
- Graceful handling of insufficient content
- User progress tracking

**Performance Tests:**
- Quiz generation speed (< 2 seconds)
- Large dataset handling

## Deployment

### Production Setup
```bash
# Install production dependencies
pip install gunicorn psycopg2

# Collect static files
python manage.py collectstatic

# Configure database (PostgreSQL recommended)
# Update DATABASE_URL in environment

# Run migrations
python manage.py migrate

# Start with Gunicorn
gunicorn lingo_project.wsgi:application
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ {
        alias /path/to/real-lingo/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring & Maintenance

### Performance Monitoring
- Quiz generation response times
- Database query optimization
- Memory usage tracking
- User engagement metrics

### Content Quality Monitoring
```bash
# Generate weekly quality reports
python manage.py content_quality_report

# Check for entries needing curation
python manage.py shell -c "
from entries.models import Entry
from entries.analytics_views import _is_generic
poor_entries = [e for e in Entry.objects.all() if _is_generic(e.notes)]
print(f'Found {len(poor_entries)} entries needing curation')
"
```

### Database Maintenance
```bash
# Backup database
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Clean up old user sessions
python manage.py clearsessions

# Update search indexes (if using search)
python manage.py rebuild_index
```

## API Integration

### External Quiz Integration
```javascript
// Fetch quiz questions
const response = await fetch('/api/quiz/questions/?language=es-AR&count=5');
const data = await response.json();

// Submit quiz results (requires authentication)
const results = [
    {id: 123, correct: true},
    {id: 124, correct: false}
];

await fetch('/api/quiz/submit/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({results})
});
```

### Content API Usage
```javascript
// Search entries
const entries = await fetch('/api/entries/?search=greeting&language=es-AR');

// Get statistics
const stats = await fetch('/api/entries/statistics/');

// Random entries
const random = await fetch('/api/entries/random/?count=10');
```

## Troubleshooting

### Common Issues

**Quiz not generating questions:**
- Check content quality with reports
- Verify sufficient entries for language
- Review error logs for API issues

**Poor quiz quality:**
- Run content quality audit
- Update curated meanings
- Improve distractor generation

**Performance issues:**
- Check database query efficiency
- Monitor memory usage
- Optimize content filtering

### Debug Tools
```python
# Django shell debugging
python manage.py shell

# Check quiz generation
from entries.analytics_views import quiz_questions
from django.test import RequestFactory
factory = RequestFactory()
request = factory.get('/api/quiz/questions/?language=es-AR')
response = quiz_questions(request)
print(response.data)
```

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Keep functions focused and small

### Content Guidelines
- Prioritize cultural accuracy
- Avoid offensive content
- Provide context and examples
- Use clear, concise definitions

### Commit Messages
```
feat: add new quiz difficulty levels
fix: resolve distractor generation bug
docs: update API documentation
test: add quiz quality tests
refactor: improve content filtering logic
```

## Support

For technical issues:
1. Check this documentation
2. Review existing GitHub issues
3. Run diagnostic tests
4. Create detailed bug report

For content questions:
1. Review content curation guidelines
2. Use admin quality reports
3. Check existing entries for examples
4. Contact content team