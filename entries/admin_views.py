# entries/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Entry, Tag, UserAnalytics, Feedback
from datetime import datetime, timedelta
import re
import json

@staff_member_required
def data_cleaning_dashboard(request):
    """Admin dashboard for data cleaning operations."""
    
    # Get statistics
    total_entries = Entry.objects.count()
    spanish_entries = Entry.objects.filter(language_code='es-AR').count()
    
    # Find problematic entries
    english_words = [
        'familiar address', 'the ', 'and ', 'or ', 'with ', 'this ', 'that ',
        'for ', 'from ', 'they ', 'have ', 'been ', 'will ', 'would ', 'could ',
        'should ', 'about ', 'after ', 'before ', 'during ', 'through ',
        'without ', 'within ', 'person ', 'people ', 'woman ', 'man ', 'child ',
        'family ', 'friend ', 'house ', 'home ', 'work ', 'school ', 'place ',
        'time ', 'year ', 'day '
    ]
    
    # Build query to find Spanish entries with English words
    q_objects = Q()
    for word in english_words:
        q_objects |= Q(notes__icontains=word)
    
    problematic_entries = Entry.objects.filter(
        language_code='es-AR'
    ).filter(q_objects)
    
    # Get entries already tagged as problematic
    tagged_problematic = Entry.objects.filter(tags__name='english-in-spanish').count()
    
    # Recent problematic entries for preview
    recent_problematic = problematic_entries[:10]
    
    context = {
        'total_entries': total_entries,
        'spanish_entries': spanish_entries,
        'problematic_count': problematic_entries.count(),
        'tagged_problematic': tagged_problematic,
        'recent_problematic': recent_problematic,
        'english_words': english_words[:10],  # Show first 10 for reference
    }
    
    return render(request, 'admin/entries/data_cleaning_dashboard.html', context)

@staff_member_required
def bulk_fix_english_in_spanish(request):
    """Bulk fix English text in Spanish entries."""
    if request.method == 'POST':
        # Translation mapping
        translations_map = {
            'familiar address': 'tratamiento familiar',
            'familiar form': 'forma familiar',
            'informal address': 'tratamiento informal',
            'used to address': 'usado para dirigirse a',
            'term of endearment': 'término cariñoso',
            'affectionate term': 'término afectivo',
            'slang term': 'término de jerga',
            'colloquial expression': 'expresión coloquial',
            'informal way': 'manera informal',
            'casual expression': 'expresión casual',
            'friendly term': 'término amistoso',
            'intimate form': 'forma íntima',
            'close friend': 'amigo cercano',
            'family member': 'miembro de la familia',
            'loved one': 'ser querido',
            'romantic partner': 'pareja romántica',
            'significant other': 'pareja',
            'boyfriend': 'novio',
            'girlfriend': 'novia',
            'husband': 'esposo',
            'wife': 'esposa',
            'child': 'niño/niña',
            'baby': 'bebé',
            'little one': 'pequeño/pequeña',
            'buddy': 'amigo',
            'pal': 'compañero',
            'mate': 'amigo',
            'dude': 'tipo',
            'guy': 'tipo',
            'person': 'persona',
            'individual': 'individuo',
            'someone': 'alguien',
            'anybody': 'cualquiera',
            'everyone': 'todos',
            'people': 'gente'
        }
        
        # Get entries with English text
        english_words = list(translations_map.keys())
        q_objects = Q()
        for word in english_words:
            q_objects |= Q(notes__icontains=word)
        
        spanish_entries = Entry.objects.filter(
            language_code='es-AR'
        ).filter(q_objects)
        
        fixed_count = 0
        for entry in spanish_entries:
            if entry.notes:
                original_notes = entry.notes
                updated_notes = entry.notes
                
                for english, spanish in translations_map.items():
                    if english.lower() in updated_notes.lower():
                        # Case-insensitive replacement
                        pattern = re.compile(re.escape(english), re.IGNORECASE)
                        updated_notes = pattern.sub(spanish, updated_notes)
                
                if updated_notes != original_notes:
                    entry.notes = updated_notes
                    entry.save()
                    fixed_count += 1
        
        messages.success(request, f'Fixed English text in {fixed_count} Spanish entries.')
        
        return JsonResponse({
            'status': 'success',
            'message': f'Fixed {fixed_count} entries',
            'fixed_count': fixed_count
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@staff_member_required
def preview_problematic_entries(request):
    """Get a preview of problematic entries for the dashboard."""
    
    english_words = ['familiar address', 'the ', 'and ', 'or ', 'with ']
    q_objects = Q()
    for word in english_words:
        q_objects |= Q(notes__icontains=word)
    
    problematic_entries = Entry.objects.filter(
        language_code='es-AR'
    ).filter(q_objects)[:20]  # Get first 20
    
    entries_data = []
    for entry in problematic_entries:
        entries_data.append({
            'id': entry.id,
            'term': entry.term,
            'notes': entry.notes[:100] + '...' if len(entry.notes) > 100 else entry.notes,
            'admin_url': f'/admin/entries/entry/{entry.id}/change/'
        })
    
    return JsonResponse({
        'entries': entries_data,
        'total_count': problematic_entries.count()
    })


# Analytics and Feedback Views

@staff_member_required
def admin_analytics_dashboard(request):
    """Admin analytics dashboard showing app traffic and usage statistics"""
    
    # Date filtering
    days = int(request.GET.get('days', 7))
    start_date = datetime.now() - timedelta(days=days)
    
    # Basic metrics
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=start_date).count()
    total_entries = Entry.objects.count()
    
    # Analytics data
    analytics_qs = UserAnalytics.objects.filter(timestamp__gte=start_date)
    
    # Page views
    page_views = analytics_qs.filter(action='page_view').count()
    unique_sessions = analytics_qs.values('session_id').distinct().count()
    
    # Quiz statistics
    quiz_data = analytics_qs.filter(action='quiz_completed')
    total_quizzes = quiz_data.count()
    avg_quiz_score = quiz_data.aggregate(avg_score=Avg('quiz_score'))['avg_score'] or 0
    
    # Most popular countries
    popular_countries = (analytics_qs.filter(country__isnull=False)
                        .values('country')
                        .annotate(views=Count('id'))
                        .order_by('-views')[:5])
    
    # Most viewed entries
    popular_entries = (analytics_qs.filter(entry_id__isnull=False)
                      .values('entry_id__term', 'entry_id__language_code')
                      .annotate(views=Count('id'))
                      .order_by('-views')[:10])
    
    # Daily activity for charts
    daily_activity = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        day_views = analytics_qs.filter(
            timestamp__date=date.date()
        ).count()
        daily_activity.append({
            'date': date.strftime('%Y-%m-%d'),
            'views': day_views
        })
    
    # Recent activity
    recent_activity = analytics_qs.order_by('-timestamp')[:20]
    
    # Feedback summary
    feedback_summary = {
        'total': Feedback.objects.count(),
        'open': Feedback.objects.filter(status='open').count(),
        'critical': Feedback.objects.filter(priority='critical', status__in=['open', 'in_progress']).count(),
    }
    
    context = {
        'days': days,
        'total_users': total_users,
        'active_users': active_users,
        'total_entries': total_entries,
        'page_views': page_views,
        'unique_sessions': unique_sessions,
        'total_quizzes': total_quizzes,
        'avg_quiz_score': round(avg_quiz_score, 1),
        'popular_countries': popular_countries,
        'popular_entries': popular_entries,
        'daily_activity': json.dumps(daily_activity),
        'recent_activity': recent_activity,
        'feedback_summary': feedback_summary,
    }
    
    return render(request, 'admin/analytics_dashboard.html', context)


@staff_member_required
def admin_feedback_list(request):
    """Admin view to manage user feedback"""
    
    # Filtering
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    priority_filter = request.GET.get('priority', '')
    
    feedback_qs = Feedback.objects.all()
    
    if status_filter:
        feedback_qs = feedback_qs.filter(status=status_filter)
    if type_filter:
        feedback_qs = feedback_qs.filter(feedback_type=type_filter)
    if priority_filter:
        feedback_qs = feedback_qs.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(feedback_qs, 20)
    page_number = request.GET.get('page')
    feedback_list = paginator.get_page(page_number)
    
    context = {
        'feedback_list': feedback_list,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'feedback_types': Feedback.FEEDBACK_TYPES,
        'status_choices': Feedback.STATUS_CHOICES,
        'priority_levels': Feedback.PRIORITY_LEVELS,
    }
    
    return render(request, 'admin/feedback_list.html', context)


@staff_member_required
def admin_feedback_detail(request, feedback_id):
    """Admin view to manage individual feedback"""
    feedback = get_object_or_404(Feedback, id=feedback_id)
    
    if request.method == 'POST':
        # Update feedback status, priority, and admin notes
        feedback.status = request.POST.get('status', feedback.status)
        feedback.priority = request.POST.get('priority', feedback.priority)
        feedback.admin_notes = request.POST.get('admin_notes', feedback.admin_notes)
        feedback.save()
        
        messages.success(request, 'Feedback updated successfully!')
        return redirect('admin_feedback_detail', feedback_id=feedback.id)
    
    context = {
        'feedback': feedback,
        'status_choices': Feedback.STATUS_CHOICES,
        'priority_levels': Feedback.PRIORITY_LEVELS,
    }
    
    return render(request, 'admin/feedback_detail.html', context)


@login_required
def feedback_form_view(request):
    """User feedback submission form"""
    from .forms import FeedbackForm
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.page_url = request.META.get('HTTP_REFERER', '')
            feedback.save()
            
            messages.success(request, 'Thank you for your feedback! We appreciate your input.')
            return redirect('feedback_success')
    else:
        form = FeedbackForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'entries/feedback_form.html', context)


def feedback_success_view(request):
    """Feedback submission success page"""
    return render(request, 'entries/feedback_success.html')


# Analytics tracking helper function
def track_user_action(request, action, **kwargs):
    """Helper function to track user actions"""
    try:
        # Get or create session ID for anonymous users
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Create analytics record
        UserAnalytics.objects.create(
            user=user,
            session_id=session_id,
            action=action,
            page_url=request.build_absolute_uri(),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            ip_address=get_client_ip(request),
            **kwargs
        )
    except Exception as e:
        # Don't let analytics tracking break the app
        print(f"Analytics tracking error: {e}")


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
