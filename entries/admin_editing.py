# entries/admin_editing.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Entry, Tag, Translation, Example
import json

@staff_member_required
@require_http_methods(["GET"])
def admin_check(request):
    """Check if user has admin permissions"""
    return JsonResponse({
        'is_admin': request.user.is_staff,
        'is_superuser': request.user.is_superuser,
        'username': request.user.username
    })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def quick_edit_entry(request, entry_id):
    """Quick edit an entry's content via AJAX."""
    try:
        entry = get_object_or_404(Entry, id=entry_id)
        data = json.loads(request.body)
        
        with transaction.atomic():
            # Update the entry fields
            if 'term' in data:
                entry.term = data['term'].strip()
            if 'notes' in data:
                entry.notes = data['notes'].strip()
            if 'category' in data:
                entry.category = data['category']
            if 'part_of_speech' in data:
                entry.part_of_speech = data['part_of_speech']
                
            # Update tags
            if 'tags' in data:
                tag_names = [name.strip() for name in data['tags'] if name.strip()]
                tags = []
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'description': f'Tag for {tag_name}', 'color': '#6c757d'}
                    )
                    tags.append(tag)
                entry.tags.set(tags)
            
            entry.full_clean()
            entry.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Entry "{entry.term}" updated successfully',
            'entry': {
                'id': entry.id,
                'term': entry.term,
                'notes': entry.notes,
                'category': entry.category,
                'part_of_speech': entry.part_of_speech,
                'tags': [tag.name for tag in entry.tags.all()],
                'updated_at': entry.updated_at.isoformat()
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Validation error: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def delete_entry(request, entry_id):
    """Delete an entry via AJAX."""
    try:
        entry = get_object_or_404(Entry, id=entry_id)
        term_name = entry.term
        entry.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Entry "{term_name}" deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def flag_entry_problematic(request, entry_id):
    """Flag an entry as problematic for later review."""
    try:
        entry = get_object_or_404(Entry, id=entry_id)
        
        # Create or get problematic tag
        from .models import Tag
        problem_tag, created = Tag.objects.get_or_create(
            name='needs-review',
            defaults={'description': 'Entry flagged for admin review', 'color': '#ff6b6b'}
        )
        
        entry.tags.add(problem_tag)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Entry "{entry.term}" flagged for review'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@staff_member_required
@require_http_methods(["GET"])
def get_entry_data(request, entry_id):
    """Get detailed entry data for editing"""
    try:
        entry = get_object_or_404(Entry, id=entry_id)
        
        return JsonResponse({
            'status': 'success',
            'entry': {
                'id': entry.id,
                'term': entry.term,
                'language_code': entry.language_code,
                'region_code': entry.region_code,
                'category': entry.category,
                'part_of_speech': entry.part_of_speech,
                'notes': entry.notes,
                'tags': [{'id': tag.id, 'name': tag.name} for tag in entry.tags.all()],
                'translations': [
                    {
                        'id': t.id,
                        'target_language_code': t.target_language_code,
                        'translation': t.translation,
                        'literal_translation': t.literal_translation
                    }
                    for t in entry.translations.all()
                ],
                'examples': [
                    {
                        'id': e.id,
                        'sentence': e.sentence,
                        'language_code': e.language_code,
                        'translation': e.translation
                    }
                    for e in entry.examples.all()
                ],
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting entry data: {str(e)}'
        }, status=500)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_translation(request, entry_id):
    """Add a translation to an entry"""
    try:
        entry = get_object_or_404(Entry, id=entry_id)
        data = json.loads(request.body)
        
        translation = Translation.objects.create(
            entry=entry,
            target_language_code=data['target_language_code'],
            translation=data['translation'],
            literal_translation=data.get('literal_translation', '')
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Translation added to "{entry.term}"',
            'translation': {
                'id': translation.id,
                'target_language_code': translation.target_language_code,
                'translation': translation.translation,
                'literal_translation': translation.literal_translation
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error adding translation: {str(e)}'
        }, status=500)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_example(request, entry_id):
    """Add an example to an entry"""
    try:
        entry = get_object_or_404(Entry, id=entry_id)
        data = json.loads(request.body)
        
        example = Example.objects.create(
            entry=entry,
            sentence=data['sentence'],
            language_code=data['language_code'],
            translation=data.get('translation', '')
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Example added to "{entry.term}"',
            'example': {
                'id': example.id,
                'sentence': example.sentence,
                'language_code': example.language_code,
                'translation': example.translation
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error adding example: {str(e)}'
        }, status=500)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def bulk_action(request):
    """Perform bulk actions on multiple entries"""
    try:
        data = json.loads(request.body)
        entry_ids = data.get('entry_ids', [])
        action = data.get('action')
        
        if not entry_ids or not action:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing entry_ids or action'
            }, status=400)
        
        entries = Entry.objects.filter(id__in=entry_ids)
        count = entries.count()
        
        if action == 'flag_english_in_spanish':
            # Flag entries with English in Spanish
            flag_tag, created = Tag.objects.get_or_create(
                name='english-in-spanish',
                defaults={'description': 'Contains English text', 'color': '#dc3545'}
            )
            for entry in entries:
                entry.tags.add(flag_tag)
            message = f'Flagged {count} entries with english-in-spanish tag'
            
        elif action == 'mark_reviewed':
            # Mark as reviewed
            reviewed_tag, created = Tag.objects.get_or_create(
                name='reviewed',
                defaults={'description': 'Reviewed by admin', 'color': '#28a745'}
            )
            for entry in entries:
                entry.tags.add(reviewed_tag)
            message = f'Marked {count} entries as reviewed'
            
        elif action == 'remove_tag':
            tag_name = data.get('tag_name')
            if tag_name:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    for entry in entries:
                        entry.tags.remove(tag)
                    message = f'Removed "{tag_name}" tag from {count} entries'
                except Tag.DoesNotExist:
                    message = f'Tag "{tag_name}" not found'
            else:
                message = 'Tag name required for remove_tag action'
                
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Unknown action: {action}'
            }, status=400)
        
        return JsonResponse({
            'status': 'success',
            'message': message,
            'count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error performing bulk action: {str(e)}'
        }, status=500)
