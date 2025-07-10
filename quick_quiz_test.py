#!/usr/bin/env python3
"""
Quick quiz template test.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

def test_quiz_template():
    """Test quiz template rendering."""
    from django.template.loader import get_template
    from django.template import Context
    from django.http import HttpRequest
    
    print("🧪 Testing Quiz Template Rendering")
    print("=" * 40)
    
    try:
        # Create a mock request with session
        request = HttpRequest()
        request.session = {'user_language': 'es'}
        
        # Load the quiz template
        template = get_template('entries/slang_quiz.html')
        
        # Try to render it
        rendered = template.render({}, request=request)
        
        print("✅ Template renders successfully")
        
        # Check for key content
        if 'Hacer Quiz' in rendered:
            print("✅ Spanish button text found")
        
        if 'class SlangQuiz' in rendered:
            print("✅ Quiz class definition found")
            
        if 'const QUIZ_TRANSLATIONS' in rendered:
            print("✅ Quiz translations found")
            
        # Check for common JS errors
        if 'SyntaxError' in rendered:
            print("❌ JavaScript syntax error detected")
            
        print(f"✅ Template size: {len(rendered)} characters")
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_quiz_template()
