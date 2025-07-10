// Enhanced Admin Inline Editing System
class AdminInlineEditor {
    constructor() {
        this.isEnabled = false;
        this.currentUser = null;
        this.init();
    }

    async init() {
        try {
            const response = await fetch('/admin/entries/admin-check/', {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.is_admin) {
                    this.currentUser = data;
                    this.createAdminInterface();
                }
            }
        } catch (error) {
            console.log('Admin check failed:', error);
        }
    }

    createAdminInterface() {
        this.createToggleButton();
        this.createNotificationArea();
        this.attachEventListeners();
        this.addAdminStyles();
    }

    createToggleButton() {
        const toggle = document.createElement('div');
        toggle.id = 'admin-editing-toggle';
        toggle.innerHTML = '<button id="admin-toggle-btn" class="admin-toggle-btn" title="Toggle Admin Editing"><span>🔧 Admin Edit</span></button>';
        document.body.appendChild(toggle);
    }

    createNotificationArea() {
        const notifications = document.createElement('div');
        notifications.id = 'admin-notifications';
        notifications.className = 'admin-notification';
        document.body.appendChild(notifications);
    }

    addAdminStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #admin-editing-toggle { position: fixed; top: 20px; right: 20px; z-index: 10000; }
            .admin-toggle-btn { background: #007bff; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; font-size: 12px; }
            .admin-toggle-btn:hover { background: #0056b3; }
            .admin-toggle-btn.active { background: #28a745; }
            .admin-edit-controls { background: rgba(0, 0, 0, 0.9); color: white; padding: 10px; border-radius: 5px; margin: 10px 0; display: none; }
            .admin-edit-controls.active { display: block; }
            .admin-edit-btn { background: #17a2b8; color: white; border: none; padding: 5px 10px; margin: 2px; border-radius: 3px; cursor: pointer; font-size: 11px; }
            .admin-edit-btn:hover { background: #138496; }
            .admin-edit-btn.danger { background: #dc3545; }
            .admin-edit-btn.warning { background: #ffc107; color: #000; }
            .admin-notification { position: fixed; top: 80px; right: 20px; max-width: 300px; z-index: 10001; opacity: 0; transform: translateX(100%); transition: all 0.3s ease; }
            .admin-notification.show { opacity: 1; transform: translateX(0); }
            .admin-notification .alert { padding: 10px 15px; border-radius: 5px; margin-bottom: 10px; border: 1px solid; }
            .admin-notification .alert-success { background: #d4edda; border-color: #c3e6cb; color: #155724; }
            .admin-notification .alert-error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
            .admin-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); z-index: 10002; display: none; align-items: center; justify-content: center; }
            .admin-modal.show { display: flex; }
            .admin-modal-content { background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%; max-height: 80%; overflow-y: auto; }
            .admin-form-group { margin-bottom: 15px; }
            .admin-form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
            .admin-form-group input, .admin-form-group textarea, .admin-form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            .admin-form-group textarea { height: 100px; resize: vertical; }
            .admin-form-actions { text-align: right; margin-top: 20px; }
            .admin-form-actions button { margin-left: 10px; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
            .admin-btn-primary { background: #007bff; color: white; }
            .admin-btn-secondary { background: #6c757d; color: white; }
        `;
        document.head.appendChild(style);
    }

    attachEventListeners() {
        const btn = document.getElementById('admin-toggle-btn');
        if (btn) {
            btn.addEventListener('click', () => this.toggleAdminMode());
        }
        this.addEntryListeners();
    }

    toggleAdminMode() {
        this.isEnabled = !this.isEnabled;
        const toggleBtn = document.getElementById('admin-toggle-btn');
        
        if (this.isEnabled) {
            toggleBtn.classList.add('active');
            this.showAdminControls();
            this.showNotification('Admin editing mode enabled', 'success');
        } else {
            toggleBtn.classList.remove('active');
            this.hideAdminControls();
            this.showNotification('Admin editing mode disabled', 'success');
        }
    }

    showAdminControls() {
        const entries = this.findEntryElements();
        entries.forEach(entry => this.addControlsToEntry(entry));
    }

    hideAdminControls() {
        document.querySelectorAll('.admin-edit-controls').forEach(el => el.remove());
    }

    findEntryElements() {
        const selectors = ['[data-entry-id]', '.entry-detail', '.entry-item', '.word-entry', 'article[id*="entry"]', '.entry-container'];
        let entries = [];
        selectors.forEach(selector => {
            entries = entries.concat(Array.from(document.querySelectorAll(selector)));
        });

        const urlMatch = window.location.pathname.match(/\/(\d+)\//);
        if (urlMatch && entries.length === 0) {
            const mainContent = document.querySelector('main, .content, .entry-content, .container');
            if (mainContent) {
                mainContent.dataset.entryId = urlMatch[1];
                entries.push(mainContent);
            }
        }
        return entries;
    }

    addControlsToEntry(entryElement) {
        const entryId = this.getEntryId(entryElement);
        if (!entryId) return;

        const controls = document.createElement('div');
        controls.className = 'admin-edit-controls active';
        controls.innerHTML = `
            <div style="font-size: 11px; margin-bottom: 5px; opacity: 0.8;">Admin Controls for Entry #${entryId}</div>
            <button class="admin-edit-btn" onclick="adminEditor.editEntry(${entryId})">Edit</button>
            <button class="admin-edit-btn warning" onclick="adminEditor.flagEntry(${entryId})">Flag</button>
            <button class="admin-edit-btn danger" onclick="adminEditor.deleteEntry(${entryId})">Delete</button>
        `;
        entryElement.insertBefore(controls, entryElement.firstChild);
    }

    getEntryId(element) {
        if (element.dataset.entryId) return element.dataset.entryId;
        const urlMatch = window.location.pathname.match(/\/(\d+)\//);
        if (urlMatch) return urlMatch[1];
        const idMatch = element.id && element.id.match(/entry.*?(\d+)/);
        if (idMatch) return idMatch[1];
        return null;
    }

    async editEntry(entryId) {
        try {
            const response = await fetch(`/admin/entries/get-entry/${entryId}/`, { credentials: 'same-origin' });
            if (!response.ok) throw new Error('Failed to fetch entry data');
            const data = await response.json();
            if (data.status === 'success') {
                this.showEditModal(data.entry);
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error loading entry data: ' + error.message, 'error');
        }
    }

    showEditModal(entry) {
        const modal = document.createElement('div');
        modal.className = 'admin-modal show';
        modal.innerHTML = `
            <div class="admin-modal-content">
                <h3>Edit Entry: ${entry.term}</h3>
                <form id="edit-entry-form">
                    <div class="admin-form-group">
                        <label>Term:</label>
                        <input type="text" name="term" value="${entry.term}" required>
                    </div>
                    <div class="admin-form-group">
                        <label>Category:</label>
                        <select name="category">
                            <option value="expression"${entry.category === 'expression' ? ' selected' : ''}>Expression</option>
                            <option value="word"${entry.category === 'word' ? ' selected' : ''}>Word</option>
                            <option value="phrase"${entry.category === 'phrase' ? ' selected' : ''}>Phrase</option>
                            <option value="saying"${entry.category === 'saying' ? ' selected' : ''}>Saying</option>
                        </select>
                    </div>
                    <div class="admin-form-group">
                        <label>Notes:</label>
                        <textarea name="notes">${entry.notes || ''}</textarea>
                    </div>
                    <div class="admin-form-group">
                        <label>Tags (comma-separated):</label>
                        <input type="text" name="tags" value="${entry.tags.map(t => t.name).join(', ')}">
                    </div>
                    <div class="admin-form-actions">
                        <button type="button" class="admin-btn-secondary" onclick="this.closest('.admin-modal').remove()">Cancel</button>
                        <button type="submit" class="admin-btn-primary">Save Changes</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        modal.querySelector('#edit-entry-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveEntryChanges(entry.id, new FormData(e.target));
            modal.remove();
        });
    }

    async saveEntryChanges(entryId, formData) {
        try {
            const data = {
                term: formData.get('term'),
                category: formData.get('category'),
                notes: formData.get('notes'),
                tags: formData.get('tags').split(',').map(t => t.trim()).filter(t => t)
            };
            const response = await fetch(`/admin/entries/quick-edit/${entryId}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });
            const result = await response.json();
            if (result.status === 'success') {
                this.showNotification(result.message, 'success');
                window.location.reload();
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error saving changes: ' + error.message, 'error');
        }
    }

    async flagEntry(entryId) {
        try {
            const response = await fetch(`/admin/entries/flag/${entryId}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flag_type: 'needs-review' }),
                credentials: 'same-origin'
            });
            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error flagging entry: ' + error.message, 'error');
        }
    }

    async deleteEntry(entryId) {
        if (!confirm('Are you sure you want to delete this entry? This action cannot be undone.')) return;
        try {
            const response = await fetch(`/admin/entries/delete/${entryId}/`, {
                method: 'POST',
                credentials: 'same-origin'
            });
            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                setTimeout(() => { window.location.href = '/countries/'; }, 2000);
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error deleting entry: ' + error.message, 'error');
        }
    }

    showNotification(message, type = 'success') {
        const notifications = document.getElementById('admin-notifications');
        const notification = document.createElement('div');
        notification.className = `alert alert-${type}`;
        notification.textContent = message;
        notifications.appendChild(notification);
        notifications.classList.add('show');
        setTimeout(() => {
            notification.remove();
            if (notifications.children.length === 0) {
                notifications.classList.remove('show');
            }
        }, 5000);
    }

    addEntryListeners() {
        const observer = new MutationObserver(() => {
            if (this.isEnabled) {
                this.hideAdminControls();
                this.showAdminControls();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.adminEditor = new AdminInlineEditor();
});
