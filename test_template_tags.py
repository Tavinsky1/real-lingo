#!/usr/bin/env python3
"""
Test the template tags functionality
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from django.template import Context, Template
from django.http import HttpRequest

# Test the template tags
def test_template_tags():
    print("=== Testing Template Tags ===\n")
    
    # Create a mock request with language session
    request = HttpRequest()
    request.session = {'user_language': 'en'}
    
    # Test template with translate tag
    template_str = """
    {% load lingo_tags %}
    Home: {% translate 'home' %}
    Explore: {% translate 'explore' %}
    """
    
    template = Template(template_str)
    context = Context({'request': request})
    result = template.render(context)
    print("English translations:")
    print(result)
    
    # Test Spanish
    request.session = {'user_language': 'es'}
    context = Context({'request': request})
    result = template.render(context)
    print("Spanish translations:")
    print(result)
    
    # Test example sentence tag
    example_template_str = """
    {% load lingo_tags %}
    Argentina conversation: {% example_sentence 'argentina' 'conversation' 'mate' %}
    Australia context: {% example_sentence 'australia' 'context' 'bloody' %}
    """
    
    template = Template(example_template_str)
    context = Context({'request': request})
    result = template.render(context)
    print("Example sentences:")
    print(result)

if __name__ == '__main__':
    test_template_tags()
