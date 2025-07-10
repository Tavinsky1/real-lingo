#!/usr/bin/env python
import os, django
import sys
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.models import Entry
from django.db.models import Count

try:
    print('Australia categories:')
    aus_categories = Entry.objects.filter(language_code='en-AU').exclude(category__isnull=True).values('category').annotate(count=Count('id')).order_by('-count')
    for cat in aus_categories:
        print(f"  {cat['category']}: {cat['count']} entries")

    print('\nAll standardized categories:')
    all_categories = ['slang', 'colloquial_phrases', 'unique_concepts', 'insults', 'jokes', 'tongue_twisters']
    for category in all_categories:
        count = Entry.objects.filter(language_code='en-AU', category=category).count()
        print(f"  {category}: {count} entries")
        
    print('\nTotal Australia entries:', Entry.objects.filter(language_code='en-AU').count())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
