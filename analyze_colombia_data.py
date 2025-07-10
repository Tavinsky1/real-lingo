#!/usr/bin/env python3
"""
Script to analyze what data is being skipped in Colombia dataset.
"""

import csv

def analyze_colombia_data():
    """Analyze the Colombia data to see what's being skipped."""
    
    colombia_file = '/Users/tavinsky/lingo_project/colombia.txt'
    
    total_rows = 0
    empty_terms = 0
    valid_terms = 0
    colloquial_phrases = 0
    skipped_details = []
    
    with open(colombia_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print(f"Column headers: {reader.fieldnames}")
        print("=" * 50)
        
        for i, row in enumerate(reader, 1):
            total_rows += 1
            
            category = row.get('Category', '').strip()
            term = row.get('Term (Spanish)', '').strip()
            slang_meaning = row.get('Slang Meaning (English)', '').strip()
            literal_meaning = row.get('Literal Meaning', '').strip()
            usage_example_es = row.get('Usage Example (Spanish)', '').strip()
            
            # Check for colloquial phrases
            if category.lower() in ['expression', 'idiom', 'proverb', 'interjection', 'filler word']:
                colloquial_phrases += 1
            
            if not term or term == '-' or term.lower() == 'n/a':
                empty_terms += 1
                # Check if there's still valuable data
                if slang_meaning or usage_example_es or literal_meaning:
                    skipped_details.append({
                        'row': i,
                        'category': category,
                        'term': term,
                        'slang_meaning': slang_meaning,
                        'literal_meaning': literal_meaning,
                        'usage_example': usage_example_es[:50] + '...' if len(usage_example_es) > 50 else usage_example_es
                    })
            else:
                valid_terms += 1
    
    print(f"Total rows: {total_rows}")
    print(f"Valid terms: {valid_terms}")
    print(f"Empty/missing terms: {empty_terms}")
    print(f"Potential colloquial phrases: {colloquial_phrases}")
    print()
    
    if skipped_details:
        print("SKIPPED ROWS WITH VALUABLE DATA:")
        print("=" * 50)
        for detail in skipped_details[:10]:  # Show first 10
            print(f"Row {detail['row']}: Category='{detail['category']}'")
            print(f"  Term: '{detail['term']}'")
            print(f"  Meaning: '{detail['slang_meaning']}'")
            print(f"  Literal: '{detail['literal_meaning']}'")
            print(f"  Example: '{detail['usage_example']}'")
            print()
    
    # Check for specific patterns that might be colloquial phrases
    print("ANALYZING FOR COLLOQUIAL PHRASES:")
    print("=" * 50)
    
    with open(colombia_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i, row in enumerate(reader, 1):
            category = row.get('Category', '').strip()
            term = row.get('Term (Spanish)', '').strip()
            slang_meaning = row.get('Slang Meaning (English)', '').strip()
            
            # Look for multi-word terms or phrases
            if term and (' ' in term or len(term.split()) > 1):
                if 'phrase' in category.lower() or 'expression' in category.lower() or len(term.split()) > 2:
                    print(f"Row {i}: '{term}' ({category}) -> '{slang_meaning}'")
                    if i > 15:  # Limit output
                        break

if __name__ == '__main__':
    analyze_colombia_data()
