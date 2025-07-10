# LingoWorld - Enhanced Argentinian Slang Dictionary

## Project Overview
LingoWorld is a comprehensive Django-based web application for exploring and learning Argentinian slang. The project now includes advanced features for language learning, user interaction, and comprehensive data management.

## Key Features Implemented

### 🎨 Enhanced Frontend Interface
- **Modern Design**: Beautiful, responsive interface with Bootstrap 5 and custom CSS
- **Interactive Search**: Real-time search suggestions with autocomplete
- **User Dashboard**: Personalized dashboard for authenticated users
- **Smart Navigation**: Context-aware navigation with breadcrumbs
- **Progressive Enhancement**: Works without JavaScript, enhanced with it

### 🔐 User Authentication & Personalization
- **User Accounts**: Full authentication system with login/logout
- **Favorites System**: Users can save and manage favorite entries
- **Learning Progress**: Track difficulty ratings, view counts, and personal notes
- **User Dashboard**: Comprehensive overview of learning progress and favorites
- **Responsive Design**: Works seamlessly on all devices

### 🚀 Advanced API Features
- **RESTful API**: Comprehensive API with multiple endpoints
- **Advanced Filtering**: Filter by category, tags, difficulty, date ranges
- **Search Suggestions**: Intelligent search suggestions for terms and tags
- **Random Sampling**: Get random entries for learning
- **Statistics**: Detailed analytics for entries, tags, and user progress
- **Similar Entries**: Find related content based on tags and categories

### 📊 Data Management & Analytics
- **Enhanced Admin Interface**: Powerful admin tools with bulk actions
- **Import/Export**: Flexible data import with CSV support
- **Tag Management**: Color-coded tags with usage analytics
- **Progress Tracking**: Monitor user engagement and learning patterns
- **Data Quality**: Tools for analyzing and improving data quality

### 🔧 API Endpoints

#### Core Endpoints
- `GET /api/entries/` - List entries with filtering and search
- `GET /api/entries/{id}/` - Get detailed entry information
- `GET /api/entries/random/` - Get random entries for learning
- `GET /api/entries/search_suggestions/` - Get search suggestions
- `GET /api/entries/{id}/similar/` - Find similar entries
- `GET /api/entries/statistics/` - Get comprehensive statistics

#### Tag Management
- `GET /api/tags/` - List all tags with usage counts
- `GET /api/tags/popular/` - Get most popular tags
- `GET /api/tags/statistics/` - Get tag usage statistics

#### User Features (Authentication Required)
- `GET /api/favorites/` - List user's favorite entries
- `POST /api/favorites/toggle/` - Add/remove favorites
- `GET /api/progress/` - View learning progress
- `POST /api/progress/mark_viewed/` - Mark entry as viewed
- `GET /api/progress/statistics/` - Get learning statistics

#### Utility Endpoints
- `GET /api/health/` - System health check
- `GET /api/docs/` - API documentation
- `GET /api/categories/` - Available categories
- `GET /api/languages/` - Available languages
- `GET /api/frontend-stats/` - Statistics for frontend

### 📱 Frontend Views
- **Home Page**: `/entries/` - Enhanced entry browser with categories
- **Entry Detail**: `/entries/{id}/` - Detailed entry view with similar entries
- **User Dashboard**: `/dashboard/` - Personal learning dashboard
- **Admin Interface**: `/admin/` - Enhanced administration panel

### 🗃️ Database Models

#### Core Models
- **Entry**: Main slang entries with term, definitions, categories
- **Tag**: Categorization system with colors and descriptions
- **Translation**: Multiple translations per entry
- **Example**: Usage examples with context

#### User Interaction Models
- **UserFavorite**: User's saved favorite entries
- **UserProgress**: Learning progress tracking with difficulty ratings

### 🎯 Advanced Features

#### Smart Filtering
- Filter by category, language, region, and tags
- Date range filtering for entry creation
- Content completeness filtering
- User-specific filtering for authenticated users

#### Learning Enhancement
- **Random Learning**: Discover new content randomly
- **Difficulty Tracking**: Rate entries by personal difficulty
- **Progress Analytics**: Track learning over time
- **Similar Content**: Discover related entries automatically

#### Data Quality
- **Import Validation**: Robust CSV import with error handling
- **Data Analysis**: Management commands for data quality assessment
- **Tag Optimization**: Merge duplicate tags, assign colors
- **Content Completeness**: Track missing translations and examples

## Technical Stack
- **Backend**: Django 4.2 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Bootstrap 5, vanilla JavaScript with progressive enhancement
- **Authentication**: Django's built-in authentication system
- **API**: RESTful API with comprehensive filtering and pagination
- **Admin**: Enhanced Django admin with custom actions and analytics

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip and virtualenv

### Quick Start
```bash
# Clone and navigate to project
cd lingo_project

# Activate virtual environment
source lingo_env/bin/activate

# Install dependencies (already installed)
pip install django djangorestframework django-import-export django-filter python-dotenv dj-database-url

# Run migrations (already applied)
python manage.py migrate

# Create superuser (already created: admin/admin123)
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Import data (already imported)
python manage.py import_lingo argentina_structured.csv
```

### Environment Configuration
The project uses a `.env` file for configuration:
```
# DATABASE_URL=postgresql://user:pass@localhost/dbname  # Commented out for SQLite
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Usage Examples

### API Usage
```bash
# Get random entries
curl "http://localhost:8000/api/entries/random/?count=5"

# Search for entries
curl "http://localhost:8000/api/entries/?search=che"

# Get popular tags
curl "http://localhost:8000/api/tags/popular/?limit=10"

# Get system statistics
curl "http://localhost:8000/api/health/"
```

### Management Commands
```bash
# Analyze data quality
python manage.py analyze_dictionary

# Import new data
python manage.py import_lingo new_data.csv

# Django admin commands
python manage.py collectstatic
python manage.py test
```

## Future Enhancements

### Planned Features
- **Audio Pronunciation**: Upload and play pronunciation files
- **User Comments**: Allow users to add comments and corrections
- **Learning Games**: Interactive games for vocabulary learning
- **Social Features**: Share favorites and progress with friends
- **Mobile App**: React Native or Flutter mobile application
- **Advanced Analytics**: Machine learning insights on usage patterns

### Technical Improvements
- **Caching**: Redis caching for improved performance
- **Search**: Elasticsearch for advanced full-text search
- **Real-time**: WebSocket support for real-time features
- **Internationalization**: Multi-language interface support
- **Performance**: Database optimization and query profiling

## Project Structure
```
lingo_project/
├── lingo_project/          # Django project settings
├── entries/                # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API and web views
│   ├── serializers.py     # API serializers
│   ├── admin.py           # Enhanced admin interface
│   ├── filters.py         # Advanced filtering
│   ├── urls.py            # URL configuration
│   ├── templates/         # Frontend templates
│   └── management/        # Custom management commands
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── README.md            # This documentation
```

## Development Team Notes
- **Code Style**: Follow PEP 8 and Django best practices
- **Testing**: Write tests for new features
- **Documentation**: Update API docs for new endpoints
- **Security**: Always validate user input and use CSRF protection
- **Performance**: Monitor query counts and optimize N+1 queries

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Update documentation
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

**LingoWorld** - Making Argentinian slang accessible to everyone! 🇦🇷✨
