# entries/admin_urls.py
from django.urls import path
from . import admin_views, admin_editing

urlpatterns = [
    # Data cleaning dashboard
    path('data-cleaning/', admin_views.data_cleaning_dashboard, name='admin_data_cleaning'),
    path('bulk-fix-english/', admin_views.bulk_fix_english_in_spanish, name='admin_bulk_fix_english'),
    path('preview-problematic/', admin_views.preview_problematic_entries, name='admin_preview_problematic'),
    
    # Analytics and Feedback Management
    path('analytics/', admin_views.admin_analytics_dashboard, name='admin_analytics_dashboard'),
    path('feedback/', admin_views.admin_feedback_list, name='admin_feedback_list'),
    path('feedback/<int:feedback_id>/', admin_views.admin_feedback_detail, name='admin_feedback_detail'),
    
    # Real-time admin editing
    path('admin-check/', admin_editing.admin_check, name='admin_check'),
    path('quick-edit/<int:entry_id>/', admin_editing.quick_edit_entry, name='quick_edit_entry'),
    path('delete/<int:entry_id>/', admin_editing.delete_entry, name='delete_entry'),
    path('flag/<int:entry_id>/', admin_editing.flag_entry_problematic, name='flag_entry'),
    path('get-entry/<int:entry_id>/', admin_editing.get_entry_data, name='get_entry_data'),
    path('add-translation/<int:entry_id>/', admin_editing.add_translation, name='add_translation'),
    path('add-example/<int:entry_id>/', admin_editing.add_example, name='add_example'),
    path('bulk-action/', admin_editing.bulk_action, name='bulk_action'),
]
