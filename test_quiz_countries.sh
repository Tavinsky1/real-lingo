#!/bin/bash

echo "Testing quiz functionality for all countries..."

# Check if the quiz template has our latest changes
echo "=== Checking template version ==="
grep -n "VERSION 2024-06-19" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html

echo "=== Checking quiz initialization ==="
grep -n "console.log.*SlangQuiz" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html

echo "=== Checking country data availability ==="
grep -A 10 -B 2 "this.quizData = {" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html | head -15

echo "=== All countries should have quiz data ==="
grep -n "argentina:\|australia:\|germany:\|colombia:\|belgium:" /Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html

echo "=== Template inclusion check ==="
grep -n "slang_quiz.html" /Users/tavinsky/lingo_project/entries/templates/entries/country_home.html

echo "Done! If you see VERSION 2024-06-19 above, the template is updated."
echo "Now test Germany quiz in browser and check console for debug messages."
