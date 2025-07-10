from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Avg
from entries.models import Entry, Tag, Translation, Example
from collections import defaultdict, Counter
import json

class Command(BaseCommand):
    help = 'Analyze the lingo dictionary data and provide comprehensive insights'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['json', 'text'],
            default='text',
            help='Output format (default: text)'
        )
        parser.add_argument(
            '--save-to-file',
            type=str,
            help='Save analysis to a file'
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Include detailed analysis'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Analyzing Lingo Dictionary Data...'))
        
        analysis = self.perform_analysis(detailed=options['detailed'])
        
        if options['format'] == 'json':
            output = json.dumps(analysis, indent=2, default=str)
        else:
            output = self.format_text_output(analysis)
        
        if options['save_to_file']:
            with open(options['save_to_file'], 'w', encoding='utf-8') as f:
                f.write(output)
            self.stdout.write(
                self.style.SUCCESS(f'Analysis saved to {options["save_to_file"]}')
            )
        else:
            self.stdout.write(output)

    def perform_analysis(self, detailed=False):
        """Perform comprehensive analysis of the dictionary data."""
        
        # Basic counts
        total_entries = Entry.objects.count()
        total_tags = Tag.objects.count()
        total_translations = Translation.objects.count()
        total_examples = Example.objects.count()
        
        # Language analysis
        language_stats = list(Entry.objects.values('language_code').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        # Category analysis
        category_stats = list(Entry.objects.exclude(category__isnull=True).values('category').annotate(
            count=Count('id')
        ).order_by('-count'))
        
        # Tag analysis
        tag_stats = list(Tag.objects.annotate(
            entry_count=Count('entry')
        ).order_by('-entry_count')[:20])  # Top 20 tags
        
        # Content completeness
        entries_with_translations = Entry.objects.filter(translations__isnull=False).distinct().count()
        entries_with_examples = Entry.objects.filter(examples__isnull=False).distinct().count()
        entries_with_notes = Entry.objects.exclude(notes__isnull=True).exclude(notes='').count()
        entries_with_tags = Entry.objects.filter(tags__isnull=False).distinct().count()
        
        # Quality metrics
        avg_translations_per_entry = Translation.objects.count() / max(total_entries, 1)
        avg_examples_per_entry = Example.objects.count() / max(total_entries, 1)
        avg_tags_per_entry = Entry.objects.annotate(
            tag_count=Count('tags')
        ).aggregate(avg=Avg('tag_count'))['avg'] or 0
        
        # Completion score analysis
        completion_scores = []
        for entry in Entry.objects.all()[:1000]:  # Sample for performance
            score = self.calculate_completion_score(entry)
            completion_scores.append(score)
        
        # Data quality issues
        issues = self.identify_data_issues()
        
        analysis = {
            'timestamp': str(Entry.objects.order_by('-created_at').first().created_at if total_entries > 0 else 'N/A'),
            'overview': {
                'total_entries': total_entries,
                'total_tags': total_tags,
                'total_translations': total_translations,
                'total_examples': total_examples
            },
            'languages': {
                'total_languages': len(language_stats),
                'distribution': language_stats,
                'most_common': language_stats[0] if language_stats else None
            },
            'categories': {
                'total_categories': len(category_stats),
                'distribution': category_stats,
                'most_common': category_stats[0] if category_stats else None
            },
            'tags': {
                'total_tags': total_tags,
                'tags_with_entries': len([t for t in tag_stats if t['entry_count'] > 0]),
                'unused_tags': total_tags - len([t for t in tag_stats if t['entry_count'] > 0]),
                'top_20_tags': tag_stats
            },
            'content_completeness': {
                'entries_with_translations': {
                    'count': entries_with_translations,
                    'percentage': round((entries_with_translations / max(total_entries, 1)) * 100, 1)
                },
                'entries_with_examples': {
                    'count': entries_with_examples,
                    'percentage': round((entries_with_examples / max(total_entries, 1)) * 100, 1)
                },
                'entries_with_notes': {
                    'count': entries_with_notes,
                    'percentage': round((entries_with_notes / max(total_entries, 1)) * 100, 1)
                },
                'entries_with_tags': {
                    'count': entries_with_tags,
                    'percentage': round((entries_with_tags / max(total_entries, 1)) * 100, 1)
                }
            },
            'quality_metrics': {
                'avg_translations_per_entry': round(avg_translations_per_entry, 2),
                'avg_examples_per_entry': round(avg_examples_per_entry, 2),
                'avg_tags_per_entry': round(avg_tags_per_entry, 2)
            },
            'completion_analysis': {
                'sample_size': len(completion_scores),
                'avg_completion_score': round(sum(completion_scores) / max(len(completion_scores), 1), 1),
                'completion_distribution': self.analyze_completion_distribution(completion_scores)
            },
            'data_quality_issues': issues
        }
        
        if detailed:
            analysis['detailed_analysis'] = self.get_detailed_analysis()
        
        return analysis

    def calculate_completion_score(self, entry):
        """Calculate completion score for an entry."""
        score = 20  # Base score for having a term
        
        if entry.notes:
            score += 20
        if entry.translations.exists():
            score += 25
        if entry.examples.exists():
            score += 25
        if entry.tags.exists():
            score += 10
            
        return score

    def analyze_completion_distribution(self, scores):
        """Analyze the distribution of completion scores."""
        if not scores:
            return {}
        
        incomplete = len([s for s in scores if s < 50])
        partial = len([s for s in scores if 50 <= s < 80])
        complete = len([s for s in scores if s >= 80])
        total = len(scores)
        
        return {
            'incomplete': {'count': incomplete, 'percentage': round((incomplete / total) * 100, 1)},
            'partial': {'count': partial, 'percentage': round((partial / total) * 100, 1)},
            'complete': {'count': complete, 'percentage': round((complete / total) * 100, 1)}
        }

    def identify_data_issues(self):
        """Identify potential data quality issues."""
        issues = []
        
        # Entries without translations
        no_translations = Entry.objects.filter(translations__isnull=True).count()
        if no_translations > 0:
            issues.append({
                'type': 'missing_translations',
                'count': no_translations,
                'description': f'{no_translations} entries have no translations'
            })
        
        # Entries without examples
        no_examples = Entry.objects.filter(examples__isnull=True).count()
        if no_examples > 0:
            issues.append({
                'type': 'missing_examples',
                'count': no_examples,
                'description': f'{no_examples} entries have no examples'
            })
        
        # Entries without tags
        no_tags = Entry.objects.filter(tags__isnull=True).count()
        if no_tags > 0:
            issues.append({
                'type': 'missing_tags',
                'count': no_tags,
                'description': f'{no_tags} entries have no tags'
            })
        
        # Very short terms (potential data issues)
        short_terms = Entry.objects.filter(term__length__lt=2).count()
        if short_terms > 0:
            issues.append({
                'type': 'short_terms',
                'count': short_terms,
                'description': f'{short_terms} entries have very short terms (< 2 characters)'
            })
        
        # Unused tags
        unused_tags = Tag.objects.filter(entry__isnull=True).count()
        if unused_tags > 0:
            issues.append({
                'type': 'unused_tags',
                'count': unused_tags,
                'description': f'{unused_tags} tags are not used by any entries'
            })
        
        # Duplicate terms (same language)
        duplicates = Entry.objects.values('term', 'language_code').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        if duplicates:
            issues.append({
                'type': 'duplicate_terms',
                'count': len(duplicates),
                'description': f'{len(duplicates)} term-language combinations have duplicates'
            })
        
        return issues

    def get_detailed_analysis(self):
        """Get detailed analysis for advanced insights."""
        # Most prolific tags
        prolific_tags = list(Tag.objects.annotate(
            entry_count=Count('entry')
        ).filter(entry_count__gt=0).order_by('-entry_count')[:10])
        
        # Recent activity
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        recent_entries = Entry.objects.filter(created_at__gte=week_ago).count()
        
        # Language-category combinations
        lang_cat_combos = list(Entry.objects.exclude(category__isnull=True).values(
            'language_code', 'category'
        ).annotate(count=Count('id')).order_by('-count')[:20])
        
        return {
            'most_prolific_tags': [
                {'name': tag.name, 'entries': tag.entry_count} 
                for tag in prolific_tags
            ],
            'recent_activity': {
                'entries_added_last_week': recent_entries
            },
            'popular_language_category_combinations': lang_cat_combos
        }

    def format_text_output(self, analysis):
        """Format analysis as readable text."""
        output = []
        output.append("="*60)
        output.append("LINGO DICTIONARY DATA ANALYSIS")
        output.append("="*60)
        output.append(f"Analysis Date: {analysis['timestamp']}")
        output.append("")
        
        # Overview
        output.append("OVERVIEW:")
        output.append("-" * 20)
        overview = analysis['overview']
        output.append(f"Total Entries: {overview['total_entries']:,}")
        output.append(f"Total Tags: {overview['total_tags']:,}")
        output.append(f"Total Translations: {overview['total_translations']:,}")
        output.append(f"Total Examples: {overview['total_examples']:,}")
        output.append("")
        
        # Languages
        output.append("LANGUAGES:")
        output.append("-" * 20)
        lang_data = analysis['languages']
        output.append(f"Total Languages: {lang_data['total_languages']}")
        if lang_data['most_common']:
            output.append(f"Most Common: {lang_data['most_common']['language_code']} ({lang_data['most_common']['count']} entries)")
        output.append("Distribution:")
        for lang in lang_data['distribution'][:5]:
            output.append(f"  - {lang['language_code']}: {lang['count']} entries")
        output.append("")
        
        # Categories
        output.append("CATEGORIES:")
        output.append("-" * 20)
        cat_data = analysis['categories']
        output.append(f"Total Categories: {cat_data['total_categories']}")
        if cat_data['most_common']:
            output.append(f"Most Common: {cat_data['most_common']['category']} ({cat_data['most_common']['count']} entries)")
        output.append("Top Categories:")
        for cat in cat_data['distribution'][:5]:
            output.append(f"  - {cat['category']}: {cat['count']} entries")
        output.append("")
        
        # Content Completeness
        output.append("CONTENT COMPLETENESS:")
        output.append("-" * 20)
        completeness = analysis['content_completeness']
        output.append(f"Entries with Translations: {completeness['entries_with_translations']['count']} ({completeness['entries_with_translations']['percentage']}%)")
        output.append(f"Entries with Examples: {completeness['entries_with_examples']['count']} ({completeness['entries_with_examples']['percentage']}%)")
        output.append(f"Entries with Notes: {completeness['entries_with_notes']['count']} ({completeness['entries_with_notes']['percentage']}%)")
        output.append(f"Entries with Tags: {completeness['entries_with_tags']['count']} ({completeness['entries_with_tags']['percentage']}%)")
        output.append("")
        
        # Quality Metrics
        output.append("QUALITY METRICS:")
        output.append("-" * 20)
        quality = analysis['quality_metrics']
        output.append(f"Average Translations per Entry: {quality['avg_translations_per_entry']}")
        output.append(f"Average Examples per Entry: {quality['avg_examples_per_entry']}")
        output.append(f"Average Tags per Entry: {quality['avg_tags_per_entry']}")
        output.append("")
        
        # Data Quality Issues
        if analysis['data_quality_issues']:
            output.append("DATA QUALITY ISSUES:")
            output.append("-" * 20)
            for issue in analysis['data_quality_issues']:
                output.append(f"⚠️  {issue['description']}")
            output.append("")
        
        # Completion Analysis
        completion = analysis['completion_analysis']
        output.append("COMPLETION ANALYSIS:")
        output.append("-" * 20)
        output.append(f"Sample Size: {completion['sample_size']} entries")
        output.append(f"Average Completion Score: {completion['avg_completion_score']}%")
        dist = completion['completion_distribution']
        output.append(f"Incomplete Entries (< 50%): {dist['incomplete']['count']} ({dist['incomplete']['percentage']}%)")
        output.append(f"Partial Entries (50-79%): {dist['partial']['count']} ({dist['partial']['percentage']}%)")
        output.append(f"Complete Entries (80%+): {dist['complete']['count']} ({dist['complete']['percentage']}%)")
        output.append("")
        
        output.append("="*60)
        
        return "\n".join(output)
