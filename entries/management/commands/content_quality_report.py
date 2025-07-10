"""
Django management command to generate comprehensive content quality reports.
Usage: python manage.py content_quality_report [--output-dir reports/]
"""

import csv
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from entries.models import Entry, Translation, Example

class Command(BaseCommand):
    help = 'Generate comprehensive content quality reports for curation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='reports',
            help='Directory to save reports (default: reports/)'
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json', 'html'],
            default='csv',
            help='Output format (default: csv)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        output_format = options['format']
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate various reports
        self.generate_missing_meanings_report(output_dir, timestamp, output_format)
        self.generate_generic_content_report(output_dir, timestamp, output_format)
        self.generate_quality_scores_report(output_dir, timestamp, output_format)
        self.generate_translation_gaps_report(output_dir, timestamp, output_format)
        self.generate_curation_priorities_report(output_dir, timestamp, output_format)
        
        self.stdout.write(
            self.style.SUCCESS(f'Content quality reports generated in {output_dir}/')
        )

    def generate_missing_meanings_report(self, output_dir, timestamp, format):
        """Generate report of entries with missing or poor quality meanings."""
        filename = f'{output_dir}/missing_meanings_{timestamp}.{format}'
        
        # Patterns that indicate missing or poor content
        generic_patterns = [
            r'slang term', r'colloquial phrase', r'idiomatic expression',
            r'the provided entry', r'lacks a detailed', r'doesn\'t offer',
            r'translation needed', r'\[traducción', r'see notes',
            r'chapter:', r'page:', r'placeholder', r'todo', r'tbd'
        ]
        
        missing_entries = []
        
        for entry in Entry.objects.all():
            issues = []
            
            # Check notes field
            notes = getattr(entry, 'notes', '') or ''
            if not notes:
                issues.append('NO_NOTES')
            else:
                for pattern in generic_patterns:
                    if re.search(pattern, notes, re.IGNORECASE):
                        issues.append(f'GENERIC_NOTES: {pattern}')
                        break
            
            # Check if has any high-quality meanings
            has_good_meaning = False
            
            # Check curated meaning fields
            if hasattr(entry, 'meaning_es') and entry.meaning_es:
                if not any(re.search(p, entry.meaning_es, re.IGNORECASE) for p in generic_patterns):
                    has_good_meaning = True
            
            if hasattr(entry, 'meaning_en') and entry.meaning_en:
                if not any(re.search(p, entry.meaning_en, re.IGNORECASE) for p in generic_patterns):
                    has_good_meaning = True
            
            # Check translations
            good_translations = 0
            for trans in entry.translations.all():
                if not any(re.search(p, trans.translation, re.IGNORECASE) for p in generic_patterns):
                    good_translations += 1
            
            if good_translations == 0 and not has_good_meaning:
                issues.append('NO_GOOD_TRANSLATIONS')
            
            # Check examples
            if not entry.examples.exists():
                issues.append('NO_EXAMPLES')
            
            if issues:
                missing_entries.append({
                    'id': entry.id,
                    'term': entry.term,
                    'language_code': entry.language_code,
                    'category': entry.category,
                    'issues': '; '.join(issues),
                    'notes_preview': (notes[:100] + '...') if len(notes) > 100 else notes,
                    'translations_count': entry.translations.count(),
                    'examples_count': entry.examples.count(),
                    'priority': self._calculate_priority(entry, issues)
                })
        
        # Sort by priority (high priority first)
        missing_entries.sort(key=lambda x: x['priority'], reverse=True)
        
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if missing_entries:
                    writer = csv.DictWriter(f, fieldnames=missing_entries[0].keys())
                    writer.writeheader()
                    writer.writerows(missing_entries)
        
        self.stdout.write(f'Missing meanings report: {len(missing_entries)} entries need attention')

    def generate_generic_content_report(self, output_dir, timestamp, format):
        """Generate report of entries with generic or AI-generated content."""
        filename = f'{output_dir}/generic_content_{timestamp}.{format}'
        
        ai_indicators = [
            r'the provided entry', r'based on the context', r'appears to be',
            r'seems to be', r'likely', r'probably', r'might be',
            r'without further context', r'ambiguous', r'unclear',
            r'insufficient information', r'requires more context'
        ]
        
        generic_entries = []
        
        for entry in Entry.objects.all():
            notes = getattr(entry, 'notes', '') or ''
            generic_score = 0
            detected_patterns = []
            
            for pattern in ai_indicators:
                if re.search(pattern, notes, re.IGNORECASE):
                    generic_score += 1
                    detected_patterns.append(pattern)
            
            if generic_score > 0:
                generic_entries.append({
                    'id': entry.id,
                    'term': entry.term,
                    'language_code': entry.language_code,
                    'generic_score': generic_score,
                    'detected_patterns': '; '.join(detected_patterns),
                    'notes': notes[:200] + '...' if len(notes) > 200 else notes
                })
        
        # Sort by generic score (highest first)
        generic_entries.sort(key=lambda x: x['generic_score'], reverse=True)
        
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if generic_entries:
                    writer = csv.DictWriter(f, fieldnames=generic_entries[0].keys())
                    writer.writeheader()
                    writer.writerows(generic_entries)
        
        self.stdout.write(f'Generic content report: {len(generic_entries)} entries with AI-generated content')

    def generate_quality_scores_report(self, output_dir, timestamp, format):
        """Generate report with quality scores for all entries."""
        filename = f'{output_dir}/quality_scores_{timestamp}.{format}'
        
        scored_entries = []
        
        for entry in Entry.objects.all():
            score = self._calculate_quality_score(entry)
            scored_entries.append({
                'id': entry.id,
                'term': entry.term,
                'language_code': entry.language_code,
                'category': entry.category,
                'quality_score': score,
                'has_curated_meaning': self._has_curated_meaning(entry),
                'translations_count': entry.translations.count(),
                'examples_count': entry.examples.count(),
                'tags_count': entry.tags.count(),
                'notes_length': len(getattr(entry, 'notes', '') or ''),
                'recommendation': self._get_quality_recommendation(score)
            })
        
        # Sort by quality score (lowest first - needs most attention)
        scored_entries.sort(key=lambda x: x['quality_score'])
        
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if scored_entries:
                    writer = csv.DictWriter(f, fieldnames=scored_entries[0].keys())
                    writer.writeheader()
                    writer.writerows(scored_entries)
        
        self.stdout.write(f'Quality scores report: {len(scored_entries)} entries scored')

    def generate_translation_gaps_report(self, output_dir, timestamp, format):
        """Generate report of translation gaps by language."""
        filename = f'{output_dir}/translation_gaps_{timestamp}.{format}'
        
        # Get language statistics
        language_stats = Entry.objects.values('language_code').annotate(
            total_entries=Count('id'),
            has_translations=Count('translations'),
            has_examples=Count('examples'),
            has_notes=Count('id', filter=Q(notes__isnull=False) & ~Q(notes=''))
        )
        
        gap_report = []
        for stat in language_stats:
            lang_code = stat['language_code']
            total = stat['total_entries']
            
            # Calculate gap percentages
            translation_gap = ((total - stat['has_translations']) / total * 100) if total > 0 else 0
            examples_gap = ((total - stat['has_examples']) / total * 100) if total > 0 else 0
            notes_gap = ((total - stat['has_notes']) / total * 100) if total > 0 else 0
            
            gap_report.append({
                'language_code': lang_code,
                'total_entries': total,
                'translation_gap_percent': round(translation_gap, 1),
                'examples_gap_percent': round(examples_gap, 1),
                'notes_gap_percent': round(notes_gap, 1),
                'priority_level': self._get_gap_priority(translation_gap, examples_gap, notes_gap)
            })
        
        # Sort by overall gap priority
        gap_report.sort(key=lambda x: (x['priority_level'], -x['total_entries']))
        
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if gap_report:
                    writer = csv.DictWriter(f, fieldnames=gap_report[0].keys())
                    writer.writeheader()
                    writer.writerows(gap_report)
        
        self.stdout.write(f'Translation gaps report: {len(gap_report)} languages analyzed')

    def generate_curation_priorities_report(self, output_dir, timestamp, format):
        """Generate prioritized list for manual curation efforts."""
        filename = f'{output_dir}/curation_priorities_{timestamp}.{format}'
        
        # Get entries that would have biggest impact if improved
        priority_entries = []
        
        # High-impact criteria: popular terms that lack good definitions
        for entry in Entry.objects.all():
            impact_score = 0
            
            # Popular terms (appeared in curated dictionaries)
            if entry.term.lower() in ['che', 'boludo', 'chamuyo', 'pibe', 'laburo', 'parcero', 'chimba']:
                impact_score += 50
            
            # High-frequency categories
            if entry.category in ['slang', 'colloquial_phrases']:
                impact_score += 20
            
            # Languages with many entries
            lang_count = Entry.objects.filter(language_code=entry.language_code).count()
            if lang_count > 100:
                impact_score += 10
            
            # Subtract points for existing quality
            quality_score = self._calculate_quality_score(entry)
            impact_score += (10 - quality_score)  # Lower quality = higher impact potential
            
            priority_entries.append({
                'id': entry.id,
                'term': entry.term,
                'language_code': entry.language_code,
                'category': entry.category,
                'impact_score': impact_score,
                'current_quality': quality_score,
                'improvement_potential': 10 - quality_score,
                'curation_action': self._suggest_curation_action(entry),
                'notes_preview': (getattr(entry, 'notes', '') or '')[:100]
            })
        
        # Sort by impact score (highest first)
        priority_entries.sort(key=lambda x: x['impact_score'], reverse=True)
        
        # Take top 500 for manageable curation
        priority_entries = priority_entries[:500]
        
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if priority_entries:
                    writer = csv.DictWriter(f, fieldnames=priority_entries[0].keys())
                    writer.writeheader()
                    writer.writerows(priority_entries)
        
        self.stdout.write(f'Curation priorities report: Top {len(priority_entries)} entries identified')

    def _calculate_priority(self, entry, issues):
        """Calculate priority level for missing content."""
        priority = 0
        
        # High priority for popular terms
        if entry.term.lower() in ['che', 'boludo', 'chamuyo', 'pibe', 'laburo']:
            priority += 10
        
        # Priority for frequently used categories
        if entry.category in ['slang', 'colloquial_phrases']:
            priority += 5
        
        # Priority based on number of issues
        priority += len(issues)
        
        return priority

    def _calculate_quality_score(self, entry):
        """Calculate quality score (0-10) for an entry."""
        score = 0
        
        # Check for curated meanings
        if self._has_curated_meaning(entry):
            score += 4
        
        # Check translations quality
        good_translations = 0
        for trans in entry.translations.all():
            if len(trans.translation) > 10 and not self._is_generic_text(trans.translation):
                good_translations += 1
        score += min(good_translations, 2)  # Max 2 points for translations
        
        # Check examples
        if entry.examples.exists():
            score += 1
        
        # Check notes quality
        notes = getattr(entry, 'notes', '') or ''
        if notes and len(notes) > 20 and not self._is_generic_text(notes):
            score += 2
        
        # Check tags
        if entry.tags.exists():
            score += 1
        
        return min(score, 10)

    def _has_curated_meaning(self, entry):
        """Check if entry has curated meaning fields."""
        if hasattr(entry, 'meaning_es') and entry.meaning_es:
            if not self._is_generic_text(entry.meaning_es):
                return True
        if hasattr(entry, 'meaning_en') and entry.meaning_en:
            if not self._is_generic_text(entry.meaning_en):
                return True
        return False

    def _is_generic_text(self, text):
        """Check if text is generic or placeholder."""
        if not text or len(text.strip()) < 3:
            return True
        
        generic_patterns = [
            r'slang term', r'colloquial phrase', r'the provided entry',
            r'lacks a detailed', r'translation needed', r'see notes',
            r'placeholder', r'todo', r'tbd'
        ]
        
        return any(re.search(p, text, re.IGNORECASE) for p in generic_patterns)

    def _get_quality_recommendation(self, score):
        """Get recommendation based on quality score."""
        if score >= 8:
            return 'EXCELLENT - Use as template'
        elif score >= 6:
            return 'GOOD - Minor improvements needed'
        elif score >= 4:
            return 'FAIR - Needs content enhancement'
        elif score >= 2:
            return 'POOR - Requires major curation'
        else:
            return 'CRITICAL - Complete rewrite needed'

    def _get_gap_priority(self, trans_gap, examples_gap, notes_gap):
        """Calculate priority level for translation gaps."""
        avg_gap = (trans_gap + examples_gap + notes_gap) / 3
        if avg_gap > 70:
            return 'HIGH'
        elif avg_gap > 40:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _suggest_curation_action(self, entry):
        """Suggest specific curation action for entry."""
        actions = []
        
        if not self._has_curated_meaning(entry):
            actions.append('ADD_MEANING')
        
        if not entry.translations.exists():
            actions.append('ADD_TRANSLATION')
        
        if not entry.examples.exists():
            actions.append('ADD_EXAMPLE')
        
        notes = getattr(entry, 'notes', '') or ''
        if self._is_generic_text(notes):
            actions.append('IMPROVE_NOTES')
        
        return '; '.join(actions) if actions else 'REVIEW_ONLY'