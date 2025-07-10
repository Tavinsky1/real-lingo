#!/usr/bin/env python3
"""
Fix JavaScript quote escaping in quiz template.
"""

import re

def fix_quiz_quotes():
    """Fix single quotes in JavaScript strings in the quiz template."""
    
    template_path = '/Users/tavinsky/lingo_project/entries/templates/entries/slang_quiz.html'
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix quotes inside JavaScript strings for questions and explanations
    # Pattern to find JavaScript object properties with single quotes
    def escape_quotes_in_js_strings(match):
        full_match = match.group(0)
        # Replace single quotes with escaped single quotes, but not the surrounding quotes
        fixed = re.sub(r"(?<!\\)'(?!')", "\\'", full_match)
        return fixed
    
    # Find patterns like: question: "text with 'quotes' inside",
    # and explanation: "text with 'quotes' inside"
    patterns = [
        r'question:\s*"[^"]*\'[^"]*"',
        r'explanation:\s*"[^"]*\'[^"]*"'
    ]
    
    for pattern in patterns:
        content = re.sub(pattern, escape_quotes_in_js_strings, content)
    
    # Manual fix for known problematic strings
    replacements = [
        ("'che'", "\\'che\\'"),
        ("'boludo'", "\\'boludo\\'"),
        ("'pibe'", "\\'pibe\\'"),
        ("'mate'", "\\'mate\\'"),
        ("'laburo'", "\\'laburo\\'"),
        ("'arvo'", "\\'arvo\\'"),
        ("'barbie'", "\\'barbie\\'"),
        ("'bogan'", "\\'bogan\\'"),
        ("'fair dinkum'", "\\'fair dinkum\\'"),
        ("'sheila'", "\\'sheila\\'"),
        ("'geil'", "\\'geil\\'"),
        ("'krass'", "\\'krass\\'"),
        ("'digga'", "\\'digga\\'"),
        ("'parcero'", "\\'parcero\\'"),
        ("'chimba'", "\\'chimba\\'"),
        ("'bacano'", "\\'bacano\\'"),
        ("'man'", "\\'man\\'"),
        ("'tinto'", "\\'tinto\\'"),
        ("'allee'", "\\'allee\\'"),
        ("'goesting'", "\\'goesting\\'"),
        ("'ambetant'", "\\'ambetant\\'"),
        ("'zwanze'", "\\'zwanze\\'"),
        ("'kot'", "\\'kot\\'")
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write back the fixed content
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed JavaScript quote escaping in quiz template")

if __name__ == "__main__":
    fix_quiz_quotes()
