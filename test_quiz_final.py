#!/usr/bin/env python3
"""
Final Quiz Functionality Test
Tests that the quiz system works properly after the template literal fixes.
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingo_project.settings')
django.setup()

def test_quiz_javascript_syntax():
    """Test that the quiz template renders without JavaScript syntax errors"""
    client = Client()
    
    print("🧪 Testing quiz JavaScript syntax...")
    
    # Test all country pages to ensure quiz renders properly
    countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
    
    for country in countries:
        print(f"\n📍 Testing {country.title()} quiz...")
        
        # Test in English
        session = client.session
        session['user_language'] = 'en'
        session.save()
        
        try:
            response = client.get(f'/{country}/')
            
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                
                # Check for JavaScript syntax errors that would prevent quiz from working
                if "question: '" in content and country != 'argentina':
                    print(f"❌ {country}: Still has single quotes in questions (JavaScript syntax error)")
                elif "question: `" in content:
                    print(f"✅ {country}: Using template literals (syntax safe)")
                else:
                    print(f"⚠️  {country}: Question format unclear")
                
                # Check for quiz button
                if 'take_quiz' in content or 'Take Quiz' in content:
                    print(f"✅ {country}: Quiz button found")
                else:
                    print(f"❌ {country}: Quiz button missing")
                    
            else:
                print(f"❌ {country}: Page error (status {response.status_code})")
                
        except Exception as e:
            print(f"❌ {country}: Exception - {e}")
    
    # Test in Spanish
    print(f"\n🇪🇸 Testing Spanish quiz syntax...")
    session = client.session
    session['user_language'] = 'es'
    session.save()
    
    try:
        response = client.get('/argentina/')
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Count quote types in Spanish quiz
            single_quote_questions = content.count("question: '")
            template_literal_questions = content.count("question: `")
            
            print(f"Spanish quiz syntax analysis:")
            print(f"  - Single quote questions: {single_quote_questions}")
            print(f"  - Template literal questions: {template_literal_questions}")
            
            if single_quote_questions == 0 and template_literal_questions > 0:
                print("✅ Spanish quiz: All questions use template literals (syntax safe)")
            elif single_quote_questions > 0:
                print("❌ Spanish quiz: Still has single quote syntax errors")
            else:
                print("⚠️  Spanish quiz: Question format unclear")
        else:
            print(f"❌ Spanish test: Page error (status {response.status_code})")
            
    except Exception as e:
        print(f"❌ Spanish test: Exception - {e}")

if __name__ == '__main__':
    test_quiz_javascript_syntax()
    print("\n🎯 Test completed! Check results above.")
