#!/usr/bin/env python3
"""
Quiz functionality diagnostic script.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/tavinsky/lingo_project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

from django.test import Client
from django.contrib.sessions.models import Session

def test_quiz_on_page():
    """Test quiz functionality on country pages."""
    
    print("🔧 DIAGNOSING QUIZ FUNCTIONALITY ISSUE")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Test Argentina page (most likely to work)
    print("\n1. Testing Argentina page response:")
    try:
        response = client.get('/argentina/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check for key quiz elements
            quiz_checks = [
                ('Quiz widget included', 'slang_quiz.html' in content),
                ('Quiz element present', 'id="slangQuiz"' in content),
                ('Quiz translations present', 'QUIZ_TRANSLATIONS' in content),
                ('SlangQuiz class present', 'class SlangQuiz' in content),
                ('USER_LANGUAGE variable', 'const USER_LANGUAGE' in content),
                ('Quiz trigger button code', 'quiz-trigger' in content),
                ('Argentina questions', 'argentina:' in content),
                ('Quiz initialization', 'new SlangQuiz()' in content)
            ]
            
            print("\n2. Quiz Component Analysis:")
            for check_name, result in quiz_checks:
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
            
            # Check for JavaScript errors or issues
            print("\n3. Potential Issues:")
            if 'syntax error' in content.lower():
                print("   ❌ JavaScript syntax errors detected")
            
            if 'slang_quiz.html' not in content:
                print("   ❌ Quiz template not included in country home")
            
            if 'QUIZ_TRANSLATIONS' not in content:
                print("   ❌ Quiz translations not loaded")
                
        else:
            print(f"   ❌ Page failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing page: {e}")
    
    # Test template rendering directly
    print("\n4. Testing Template Rendering:")
    try:
        from django.template.loader import render_to_string
        from django.http import HttpRequest
        
        # Create mock request with Spanish session
        request = HttpRequest()
        request.session = {'user_language': 'es', 'selected_country': 'argentina'}
        
        quiz_content = render_to_string('entries/slang_quiz.html', {}, request=request)
        
        if 'Hacer Quiz' in quiz_content:
            print("   ✅ Spanish quiz button text rendered correctly")
        else:
            print("   ❌ Spanish quiz button text not found")
            
        if 'class SlangQuiz' in quiz_content:
            print("   ✅ Quiz class definition present")
        else:
            print("   ❌ Quiz class definition missing")
            
    except Exception as e:
        print(f"   ❌ Template rendering error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_quiz_on_page()
