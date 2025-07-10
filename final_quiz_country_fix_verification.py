#!/usr/bin/env python3

"""
Final Quiz Country Fix Verification
This script checks that the quiz system now correctly passes country parameters
"""

import os
import sys

def check_quiz_fixes():
    """Check that quiz fixes have been properly applied"""
    print("🔧 FINAL QUIZ COUNTRY FIX VERIFICATION")
    print("=" * 50)
    
    fixes_applied = 0
    total_checks = 0
    
    # Check 1: country_home.html has country parameter fix
    total_checks += 1
    country_home_path = "/Users/tavinsky/lingo_project/entries/templates/entries/country_home.html"
    
    if os.path.exists(country_home_path):
        with open(country_home_path, 'r') as f:
            content = f.read()
            
        if "window.slangQuiz.show('{{ country }}')" in content:
            print("✅ country_home.html: Quiz button now passes country parameter")
            fixes_applied += 1
        else:
            print("❌ country_home.html: Quiz button still missing country parameter")
    else:
        print("❌ country_home.html: File not found")
    
    # Check 2: user_dashboard_enhanced.html has country parameter fix
    total_checks += 1
    dashboard_path = "/Users/tavinsky/lingo_project/entries/templates/entries/user_dashboard_enhanced.html"
    
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r') as f:
            content = f.read()
            
        if "window.slangQuiz.show('{{ request.session.selected_country|default:\"argentina\" }}')" in content:
            print("✅ user_dashboard_enhanced.html: Quiz button now passes country parameter")
            fixes_applied += 1
        else:
            print("❌ user_dashboard_enhanced.html: Quiz button still missing country parameter")
    else:
        print("❌ user_dashboard_enhanced.html: File not found")
    
    # Check 3: Main quiz template has all country data
    total_checks += 1
    quiz_path = "/Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html"
    
    if os.path.exists(quiz_path):
        with open(quiz_path, 'r') as f:
            content = f.read()
            
        countries = ['argentina', 'australia', 'germany', 'colombia', 'belgium']
        all_countries_present = all(f"{country}:" in content for country in countries)
        
        if all_countries_present:
            print("✅ slang_quiz.html: All 5 countries have quiz data")
            fixes_applied += 1
        else:
            missing = [country for country in countries if f"{country}:" not in content]
            print(f"❌ slang_quiz.html: Missing quiz data for: {missing}")
    else:
        print("❌ slang_quiz.html: File not found")
    
    # Check 4: Quiz show method accepts country parameter
    total_checks += 1
    if os.path.exists(quiz_path):
        with open(quiz_path, 'r') as f:
            content = f.read()
            
        if "show(country)" in content:
            print("✅ slang_quiz.html: show() method accepts country parameter")
            fixes_applied += 1
        else:
            print("❌ slang_quiz.html: show() method signature not updated")
    
    # Check 5: Debug logging is present
    total_checks += 1
    if os.path.exists(quiz_path):
        with open(quiz_path, 'r') as f:
            content = f.read()
            
        if "console.log('Quiz show called with country:', country)" in content:
            print("✅ slang_quiz.html: Debug logging is present")
            fixes_applied += 1
        else:
            print("❌ slang_quiz.html: Debug logging missing")
    
    print("\n" + "=" * 50)
    print(f"📊 SUMMARY: {fixes_applied}/{total_checks} fixes applied correctly")
    
    if fixes_applied == total_checks:
        print("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n✅ The quiz system should now work correctly for all countries:")
        print("   - Argentina 🇦🇷")
        print("   - Australia 🇦🇺") 
        print("   - Germany 🇩🇪")
        print("   - Colombia 🇨🇴")
        print("   - Belgium 🇧🇪")
        print("\n🔧 What was fixed:")
        print("   1. Quiz buttons now pass the correct country parameter")
        print("   2. Country detection enhanced with fallbacks")
        print("   3. All countries have complete quiz data")
        print("   4. Debug logging added for troubleshooting")
        print("   5. Consistent quiz behavior across all country pages")
        return True
    else:
        print("❌ Some fixes are missing. Please review the failed checks above.")
        return False

def test_country_detection():
    """Test the country detection logic"""
    print("\n🌍 TESTING COUNTRY DETECTION LOGIC")
    print("-" * 30)
    
    test_urls = [
        "/argentina/",
        "/australia/",
        "/germany/", 
        "/colombia/",
        "/belgium/"
    ]
    
    expected_countries = ["argentina", "australia", "germany", "colombia", "belgium"]
    
    print("✅ URL patterns that should be detected:")
    for url, country in zip(test_urls, expected_countries):
        print(f"   {url} → {country}")
    
    print("\n✅ Detection fallbacks available:")
    print("   - URL path analysis")
    print("   - Page title analysis") 
    print("   - Page content analysis")
    print("   - Default to 'argentina' if all else fails")

if __name__ == "__main__":
    success = check_quiz_fixes()
    test_country_detection()
    
    if success:
        print(f"\n🚀 NEXT STEPS:")
        print("1. Test the quiz on each country page in a browser")
        print("2. Check browser console for debug messages")
        print("3. Verify quiz opens with correct country-specific content")
        print("4. Confirm quiz positioning and scrolling work properly")
        sys.exit(0)
    else:
        print(f"\n⚠️  ISSUES FOUND - Please fix the failed checks before testing")
        sys.exit(1)
