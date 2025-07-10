# Real Lingo Content Curation Guidelines

## Overview

Real Lingo aims to provide authentic, high-quality slang, idioms, and colloquial expressions from various countries. This guide outlines standards and best practices for content curation to ensure engaging, accurate, and culturally appropriate quiz questions.

## Content Quality Standards

### Excellent Content (Score: 8-10)
**Characteristics:**
- Clear, concise definitions (20-80 words)
- Cultural context and usage notes
- Appropriate examples when helpful
- Accurate translations in multiple languages
- Proper categorization and tagging

**Example:**
```
Term: "che" (Argentina)
Category: slang
Meaning (ES): "Interjección muy común para llamar la atención o dirigirse a alguien, similar a 'oye' o 'eh'. Se usa entre amigos y en situaciones informales."
Meaning (EN): "Common interjection used to get attention or address someone, similar to 'hey' or 'dude'. Used among friends in informal situations."
Notes: "Iconic expression from Argentina, popularized internationally by Che Guevara's nickname."
```

### Good Content (Score: 6-7)
**Characteristics:**
- Clear definition with minor room for improvement
- Good cultural accuracy
- May lack some context or examples
- Translations available but could be enhanced

### Fair Content (Score: 4-5)
**Characteristics:**
- Basic definition present but lacks detail
- Limited cultural context
- Some translation gaps
- Needs enhancement for quiz use

### Poor Content (Score: 2-3)
**Characteristics:**
- Generic or vague definitions
- Limited cultural accuracy
- Missing key information
- Not suitable for quiz questions

### Critical Content (Score: 0-1)
**Characteristics:**
- Placeholder text or AI-generated uncertainty
- Factually incorrect information
- Offensive or inappropriate content
- Must be completely rewritten

## Content Categories

### Slang
**Definition:** Informal words or phrases used in casual conversation
**Examples:** "boludo" (Argentina), "mate" (Australia), "digga" (Germany)
**Guidelines:**
- Include usage context (friendly vs. offensive)
- Note regional variations
- Explain cultural significance

### Insults
**Definition:** Derogatory terms or expressions
**Guidelines:**
- Handle with cultural sensitivity
- Explain severity and context
- Note when terms can be friendly vs. offensive
- Avoid extremely offensive content

### Tongue Twisters
**Definition:** Phrases designed to be difficult to pronounce
**Examples:** "Trabalenguas" in Spanish
**Guidelines:**
- Include pronunciation guidance
- Explain linguistic challenges
- Provide cultural context

### Colloquial Phrases
**Definition:** Informal expressions used in everyday speech
**Guidelines:**
- Explain literal vs. figurative meanings
- Provide usage contexts
- Include regional variations

### Jokes
**Definition:** Humorous expressions or wordplay
**Guidelines:**
- Explain the humor mechanism
- Note cultural context for understanding
- Ensure appropriateness

### Unique Concepts
**Definition:** Culture-specific concepts without direct translations
**Examples:** "Saudade" (Portuguese), "Hygge" (Danish)
**Guidelines:**
- Provide extensive cultural explanation
- Compare to similar concepts in other cultures
- Explain why translation is difficult

## Writing Guidelines

### Definitions (meaning_es, meaning_en)

**Do:**
- Use 20-80 words for optimal quiz readability
- Start with the most common usage
- Include cultural context when relevant
- Use active voice and clear language
- Provide literal translations when helpful

**Don't:**
- Use the term itself in the definition
- Include generic phrases like "slang term" or "expression used to"
- Write overly academic or complex explanations
- Include offensive examples unnecessarily
- Use uncertain language ("might be", "could mean")

**Template Structure:**
```
[Primary meaning]. [Usage context]. [Cultural note if relevant].

Examples:
✅ "Friendly greeting between friends, similar to 'hey' or 'what's up'. Commonly used in informal settings."
❌ "This slang term is used to greet people and might mean hello or similar expressions."
```

### Notes Field

**Purpose:** Additional context that doesn't fit in definitions
**Include:**
- Etymology or word origins
- Regional usage variations
- Historical or cultural significance
- Pronunciation guidance
- Related terms

**Example:**
```
Notes: "Originally from lunfardo (Buenos Aires slang). Can be friendly or insulting depending on tone and relationship. Widely known throughout Latin America due to Argentine media."
```

### Examples and Translations

**Best Practices:**
- Provide realistic usage examples
- Include both formal and informal contexts
- Show regional variations when significant
- Translate examples to aid understanding

## Quality Control Process

### Initial Review Checklist
- [ ] Definition is clear and concise (20-80 words)
- [ ] Cultural context is accurate
- [ ] No generic or placeholder language
- [ ] Appropriate for target audience
- [ ] Translations are accurate
- [ ] Category is correct
- [ ] Regional codes are specified

### Content Validation
1. **Accuracy Check:** Verify with native speakers
2. **Cultural Sensitivity:** Ensure appropriate representation
3. **Quiz Suitability:** Can generate good distractors
4. **Language Quality:** Clear, engaging writing

### Rejection Criteria
**Automatic rejection for:**
- Placeholder text ("slang term", "expression used to")
- AI-generated uncertainty markers ("might be", "appears to")
- Factually incorrect information
- Extremely offensive content without educational value
- Copyright violations

## Curation Workflow

### 1. Content Import
- Import raw data from reliable sources
- Tag entries needing curation
- Generate quality reports

### 2. Prioritization
**High Priority:**
- Popular terms (che, boludo, mate, etc.)
- Terms with existing but poor definitions
- Frequently used categories (slang, colloquial phrases)

**Medium Priority:**
- Regional variations
- Less common but culturally significant terms
- Terms missing translations

**Low Priority:**
- Very specialized or rare terms
- Duplicate entries
- Low-impact regional variations

### 3. Research Process
**Sources to consult:**
- Native speaker verification
- Regional dictionaries and glossaries
- Cultural context resources
- Academic linguistic sources
- Popular culture references

### 4. Writing and Review
- Draft definitions following guidelines
- Review for accuracy and clarity
- Test in quiz format
- Get native speaker validation
- Implement feedback

### 5. Quality Assurance
- Run through automated quality checks
- Test quiz generation
- Verify translations
- Final editorial review

## Tools and Resources

### Admin Interface Actions
- **Generate Quality Report:** Identify entries needing curation
- **Export for Curation:** Download entries in editable format
- **Mark Needs Curation:** Flag entries for review
- **Bulk Update:** Import curated content

### Management Commands
```bash
# Generate comprehensive quality reports
python manage.py content_quality_report

# Export curation templates
python manage.py bulk_update_meanings --export-template

# Import curated content
python manage.py bulk_update_meanings --csv-file curated_meanings.csv
```

### Quality Indicators
**Green flags (good content):**
- Concise, clear definitions
- Cultural context included
- Multiple language support
- Proper categorization
- Realistic examples

**Red flags (needs work):**
- Generic phrases ("slang term")
- Uncertainty markers ("might be")
- Overly long or short definitions
- Missing cultural context
- Poor translations

## Regional Considerations

### Argentina (es-AR)
- Focus on lunfardo and porteño expressions
- Include tango culture references
- Note formal vs. informal usage (vos vs. tú)

### Australia (en-AU)
- Emphasize unique Australian humor
- Include cultural context for international users
- Note regional variations (states/territories)

### Germany (de-DE)
- Distinguish between standard German and regional dialects
- Include youth slang vs. traditional expressions
- Note formality levels (du vs. Sie contexts)

### Colombia (es-CO)
- Include regional variations (coastal vs. Andean)
- Note differences from other Latin American Spanish
- Include cultural context for expressions

### Belgium
- Handle multilingual complexity (Dutch/French)
- Note regional usage patterns
- Include cultural context for each language community

## Best Practices for Quiz Generation

### Creating Good Distractors
**Strategies:**
- Use definitions from similar categories
- Include related but incorrect meanings
- Avoid obviously wrong answers
- Ensure all options are plausible

**Example:**
```
Question: What does "chamuyo" mean?
A) Sweet talk or flattery (correct)
B) A type of dance
C) Traditional food
D) Afternoon nap

All options are noun phrases of similar length and plausibility.
```

### Avoiding Common Pitfalls
- Don't include the term in the definition
- Avoid overly technical language
- Don't make correct answers obviously longer/shorter
- Ensure cultural appropriateness of all options

## Continuous Improvement

### Feedback Integration
- Monitor quiz performance metrics
- Collect user feedback on question quality
- Track which entries generate poor quizzes
- Update based on educational effectiveness

### Content Updates
- Regular review of trending expressions
- Seasonal updates for cultural events
- Incorporation of new slang as it emerges
- Removal of outdated expressions

### Quality Metrics
**Track:**
- Quiz completion rates by content quality score
- User engagement with different categories
- Accuracy of user responses by content type
- Time spent on questions by quality level

## Support and Resources

### Getting Help
1. **Content Questions:** Consult native speakers and cultural experts
2. **Technical Issues:** Use developer documentation and admin tools
3. **Style Questions:** Reference this guide and existing high-quality examples
4. **Cultural Sensitivity:** Consult cultural advisors for appropriate representation

### Reference Materials
- Regional slang dictionaries
- Cultural context resources
- Linguistic academic papers
- Native speaker communities
- Popular culture references

### Quality Assurance Tools
- Automated content quality scoring
- Quiz generation testing
- Native speaker validation workflows
- Editorial review processes

---

**Remember:** The goal is to create authentic, engaging, and educational content that helps users genuinely understand and appreciate the rich diversity of language and culture represented in Real Lingo.