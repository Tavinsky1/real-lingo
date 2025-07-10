#!/bin/bash

echo "🎯 FINAL QUIZ VERIFICATION FOR ALL COUNTRIES"
echo "============================================="

# Check the main template file
echo "✅ Checking main quiz template..."
if grep -q "VERSION 2024-06-19" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html; then
    echo "   ✓ Template is updated with latest version"
else
    echo "   ❌ Template version not found"
fi

# Check console logging
if grep -q "console.log.*Quiz show called" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html; then
    echo "   ✓ Debug logging is enabled"
else
    echo "   ❌ Debug logging not found"
fi

# Check all countries have quiz data
echo ""
echo "✅ Verifying quiz data for all countries..."
for country in argentina australia germany colombia belgium; do
    if grep -q "$country:" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html; then
        echo "   ✓ $country quiz data found"
    else
        echo "   ❌ $country quiz data missing"
    fi
done

# Check CSS for proper scrolling
echo ""
echo "✅ Checking CSS for proper scrolling..."
if grep -q "overflow-y: auto" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html; then
    echo "   ✓ Overlay scrolling enabled"
else
    echo "   ❌ Overlay scrolling not enabled"
fi

if grep -q "align-items: flex-start" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html; then
    echo "   ✓ Proper alignment for scrolling"
else
    echo "   ❌ Alignment not set for scrolling"
fi

# Check template inclusion
echo ""
echo "✅ Checking template inclusion..."
if grep -q "slang_quiz.html" /Users/tavinsky/lingo_project/entries/templates/entries/country_home.html; then
    echo "   ✓ Quiz template is included in country pages"
else
    echo "   ❌ Quiz template not included"
fi

echo ""
echo "🚀 NEXT STEPS:"
echo "1. Open your browser and go to localhost:8000/germany/"
echo "2. Open Developer Tools (F12) and go to Console tab"
echo "3. Click 'Take Quiz' button"
echo "4. Look for these console messages:"
echo "   - 'SlangQuiz initialized successfully'"
echo "   - 'Quiz show called with country: germany'"
echo "   - 'Final country for quiz: germany'"
echo "   - 'Quiz data found for country: germany'"
echo "5. Verify the quiz opens and is fully scrollable"
echo ""
echo "If you see all the console messages and the quiz works, then it's fixed!"
echo "If not, check the browser console for any error messages."
echo ""
echo "📁 Test files created:"
echo "   - germany_quiz_test.html (Direct test page)"
echo "   - quiz_full_scrolling_test.html (Scrolling test)"
echo ""
echo "✅ All checks completed!"
