#!/usr/bin/env python
import os, django
import sys
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from entries.views import country_home_view
from django.test import RequestFactory

def test_country_categories(country):
    factory = RequestFactory()
    request = factory.get(f'/{country}/')
    request.session = {}
    
    response = country_home_view(request, country)
    print(f'\n{country.title()} page status: {response.status_code}')
    
    # Extract context from response
    if hasattr(response, 'context_data'):
        categories = response.context_data.get('popular_categories', [])
    else:
        # For rendered response, we need to render to get context
        from django.template.response import TemplateResponse
        if isinstance(response, TemplateResponse):
            categories = response.context_data.get('popular_categories', [])
        else:
            print("Cannot access context data")
            return
    
    print(f'Categories for {country}:')
    for cat in categories:
        print(f'  {cat["category"]}: {cat["count"]} entries')

# Test all countries
for country in ['argentina', 'australia', 'germany']:
    test_country_categories(country)
