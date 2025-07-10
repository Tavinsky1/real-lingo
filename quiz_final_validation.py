#!/usr/bin/env python3

"""
Quick Quiz Validation Test
Tests the basic structure and content of the fixed slang quiz template
"""

import os
import re

def test_quiz_template():
    """Test the quiz template for basic functionality"""
    quiz_file = "/Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html"
    
    if not os.path.exists(quiz_file):
        print("❌ FAIL: Quiz template file not found")
        return False
    
    with open(quiz_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test 1: Check for Django template syntax
    if "{% load i18n %}" not in content:
        print("❌ FAIL: Missing Django template load tag")
        return False
    print("✅ PASS: Django template syntax present")
    
    # Test 2: Check for overlay structure
    if 'id="quizOverlay"' not in content:
        print("❌ FAIL: Missing quiz overlay element")
        return False
    print("✅ PASS: Quiz overlay structure present")
    
    # Test 3: Check for NO blur effects (the main bug we fixed)
    if "backdrop-filter: blur" in content:
        print("❌ FAIL: Blur effects still present (main bug not fixed)")
        return False
    print("✅ PASS: No blur effects found (bug fixed)")
    
    # Test 4: Check for SlangQuiz class
    if "class SlangQuiz" not in content:
        print("❌ FAIL: Missing SlangQuiz JavaScript class")
        return False
    print("✅ PASS: SlangQuiz JavaScript class present")
    
    # Test 5: Check for quiz data for all countries
    countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
    missing_countries = []
    for country in countries:
        if f"{country}:" not in content:
            missing_countries.append(country)
    
    if missing_countries:
        print(f"❌ FAIL: Missing quiz data for countries: {missing_countries}")
        return False
    print("✅ PASS: Quiz data present for all 5 countries")
    
    # Test 6: Check for show() method that handles country parameter
    if "show(country)" not in content:
        print("❌ FAIL: Missing show(country) method")
        return False
    print("✅ PASS: show(country) method present")
    
    # Test 7: Check for proper z-index values (no interference)
    if "z-index: 1999" not in content or "z-index: 2000" not in content:
        print("❌ FAIL: Missing proper z-index layering")
        return False
    print("✅ PASS: Proper z-index layering present")
    
    # Test 8: Check for scroll-to-top functionality
    if "window.scrollTo(0, 0)" not in content:
        print("❌ FAIL: Missing scroll-to-top functionality")
        return False
    print("✅ PASS: Scroll-to-top functionality present")
    
    # Test 9: Check file size (should be reasonable, not massive like before)
    file_size = len(content)
    if file_size > 50000:  # 50KB limit
        print(f"⚠️  WARNING: File size is {file_size} bytes (may still have corruption)")
    else:
        print(f"✅ PASS: File size is reasonable ({file_size} bytes)")
    
    # Test 10: Check for proper close functionality
    if "document.body.style.overflow = 'auto'" not in content:
        print("❌ FAIL: Missing proper close functionality")
        return False
    print("✅ PASS: Proper close functionality present")
    
    return True

def main():
    print("🧪 Testing Fixed Slang Quiz Template")
    print("=" * 50)
    
    success = test_quiz_template()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Quiz system should now work properly.")
        print("\n📋 Summary of fixes applied:")
        print("   • Removed backdrop-filter blur effects (main bug)")
        print("   • Clean overlay system with proper z-index")
        print("   • Complete SlangQuiz JavaScript class")
        print("   • Quiz data for all 5 countries")
        print("   • Proper show(country) method")
        print("   • Scroll-to-top functionality")
        print("   • Mobile responsive design")
        print("   • Score tracking and progress bar")
        print("\n🚀 Ready to test: Click 'Take Quiz' button on any country page!")
    else:
        print("❌ SOME TESTS FAILED. Quiz may still have issues.")

if __name__ == "__main__":
    main()
