// Enhanced Admin Inline Editing System
// This script adds comprehensive inline editing capabilities for admin users

class AdminInlineEditor {
    constructor() {
        this.isEnabled = false;
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Check if user has admin permissions
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
        toggle.innerHTML = '<button id="admin-toggle-btn" class="admin-toggle-btn" title="Toggle Admin Editing"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg><span>Admin Edit</span></button>';
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
        style.textContent = '#admin-editing-toggle { position: fixed; top: 20px; right: 20px; z-index: 10000; background: rgba(0, 0, 0, 0.8); border-radius: 8px; padding: 5px; } .admin-toggle-btn { background: #007bff; color: white; border: none; padding: 8px 12px; border-radius: 5px; cursor: pointer; display: flex; align-items: center; gap: 5px; font-size: 12px; transition: background 0.3s; } .admin-toggle-btn:hover { background: #0056b3; } .admin-toggle-btn.active { background: #28a745; } .admin-edit-controls { background: rgba(0, 0, 0, 0.9); color: white; padding: 10px; border-radius: 5px; margin: 10px 0; display: none; position: relative; z-index: 1000; } .admin-edit-controls.active { display: block; } .admin-edit-btn { background: #17a2b8; color: white; border: none; padding: 5px 10px; margin: 2px; border-radius: 3px; cursor: pointer; font-size: 11px; } .admin-edit-btn:hover { background: #138496; } .admin-edit-btn.danger { background: #dc3545; } .admin-edit-btn.danger:hover { background: #c82333; } .admin-edit-btn.warning { background: #ffc107; color: #000; } .admin-edit-btn.warning:hover { background: #e0a800; } .admin-notification { position: fixed; top: 80px; right: 20px; max-width: 300px; z-index: 10001; opacity: 0; transform: translateX(100%); transition: all 0.3s ease; } .admin-notification.show { opacity: 1; transform: translateX(0); } .admin-notification .alert { padding: 10px 15px; border-radius: 5px; margin-bottom: 10px; border: 1px solid; } .admin-notification .alert-success { background: #d4edda; border-color: #c3e6cb; color: #155724; } .admin-notification .alert-error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; } .admin-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); z-index: 10002; display: none; align-items: center; justify-content: center; } .admin-modal.show { display: flex; } .admin-modal-content { background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%; max-height: 80%; overflow-y: auto; } .admin-form-group { margin-bottom: 15px; } .admin-form-group label { display: block; margin-bottom: 5px; font-weight: bold; } .admin-form-group input, .admin-form-group textarea, .admin-form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; } .admin-form-group textarea { height: 100px; resize: vertical; } .admin-form-actions { text-align: right; margin-top: 20px; } .admin-form-actions button { margin-left: 10px; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; } .admin-btn-primary { background: #007bff; color: white; } .admin-btn-secondary { background: #6c757d; color: white; }';
        document.head.appendChild(style);
    }

    attachEventListeners() {
        document.getElementById('admin-toggle-btn').addEventListener('click', () => {
            this.toggleAdminMode();
        });
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
        entries.forEach(entry => {
            this.addControlsToEntry(entry);
        });
    }

    hideAdminControls() {
        document.querySelectorAll('.admin-edit-controls').forEach(el => {
            el.remove();
        });
    }

    findEntryElements() {
        const selectors = [
            '[data-entry-id]',
            '.entry-detail',
            '.entry-item',
            '.word-entry',
            'article[id*="entry"]',
            '.entry-container'
        ];

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
        controls.innerHTML = '<div style="font-size: 11px; margin-bottom: 5px; opacity: 0.8;">Admin Controls for Entry #' + entryId + '</div><button class="admin-edit-btn" onclick="adminEditor.editEntry(' + entryId + ')">Edit Entry</button><button class="admin-edit-btn warning" onclick="adminEditor.flagEntry(' + entryId + ')">Flag Issue</button><button class="admin-edit-btn" onclick="adminEditor.addTranslation(' + entryId + ')">Add Translation</button><button class="admin-edit-btn" onclick="adminEditor.addExample(' + entryId + ')">Add Example</button><button class="admin-edit-btn danger" onclick="adminEditor.deleteEntry(' + entryId + ')" style="margin-left: 10px;">Delete</button>';

        entryElement.insertBefore(controls, entryElement.firstChild);
    }

    getEntryId(element) {
        if (element.dataset.entryId) {
            return element.dataset.entryId;
        }

        const urlMatch = window.location.pathname.match(/\/(\d+)\//);
        if (urlMatch) {
            return urlMatch[1];
        }

        const idMatch = element.id && element.id.match(/entry.*?(\d+)/);
        if (idMatch) {
            return idMatch[1];
        }

        return null;
    }

    async editEntry(entryId) {
        try {
            const response = await fetch('/admin/entries/get-entry/' + entryId + '/', {
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch entry data');
            }

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
        modal.innerHTML = '<div class="admin-modal-content"><h3>Edit Entry: ' + entry.term + '</h3><form id="edit-entry-form"><div class="admin-form-group"><label>Term:</label><input type="text" name="term" value="' + entry.term + '" required></div><div class="admin-form-group"><label>Category:</label><select name="category"><option value="expression"' + (entry.category === 'expression' ? ' selected' : '') + '>Expression</option><option value="word"' + (entry.category === 'word' ? ' selected' : '') + '>Word</option><option value="phrase"' + (entry.category === 'phrase' ? ' selected' : '') + '>Phrase</option><option value="saying"' + (entry.category === 'saying' ? ' selected' : '') + '>Saying</option></select></div><div class="admin-form-group"><label>Part of Speech:</label><input type="text" name="part_of_speech" value="' + (entry.part_of_speech || '') + '"></div><div class="admin-form-group"><label>Notes:</label><textarea name="notes">' + (entry.notes || '') + '</textarea></div><div class="admin-form-group"><label>Tags (comma-separated):</label><input type="text" name="tags" value="' + entry.tags.map(t => t.name).join(', ') + '"></div><div class="admin-form-actions"><button type="button" class="admin-btn-secondary" onclick="this.closest(\'.admin-modal\').remove()">Cancel</button><button type="submit" class="admin-btn-primary">Save Changes</button></div></form></div>';

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
                part_of_speech: formData.get('part_of_speech'),
                notes: formData.get('notes'),
                tags: formData.get('tags').split(',').map(t => t.trim()).filter(t => t)
            };

            const response = await fetch('/admin/entries/quick-edit/' + entryId + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
            const response = await fetch('/admin/entries/flag/' + entryId + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
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
        if (!confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/admin/entries/delete/' + entryId + '/', {
                method: 'POST',
                credentials: 'same-origin'
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                setTimeout(() => {
                    window.location.href = '/countries/';
                }, 2000);
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error deleting entry: ' + error.message, 'error');
        }
    }

    async addTranslation(entryId) {
        const translation = prompt('Enter translation:');
        const languageCode = prompt('Enter target language code (e.g., en, es):', 'en');
        
        if (!translation || !languageCode) return;

        try {
            const response = await fetch('/admin/entries/add-translation/' + entryId + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    translation: translation,
                    target_language_code: languageCode,
                    literal_translation: ''
                }),
                credentials: 'same-origin'
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                window.location.reload();
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error adding translation: ' + error.message, 'error');
        }
    }

    async addExample(entryId) {
        const sentence = prompt('Enter example sentence:');
        const languageCode = prompt('Enter language code (e.g., es-AR):', 'es-AR');
        
        if (!sentence || !languageCode) return;

        try {
            const response = await fetch('/admin/entries/add-example/' + entryId + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sentence: sentence,
                    language_code: languageCode,
                    translation: ''
                }),
                credentials: 'same-origin'
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification(data.message, 'success');
                window.location.reload();
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('Error adding example: ' + error.message, 'error');
        }
    }

    showNotification(message, type = 'success') {
        const notifications = document.getElementById('admin-notifications');
        const notification = document.createElement('div');
        notification.className = 'alert alert-' + type;
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

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.adminEditor = new AdminInlineEditor();
});
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .admin-toolbar.visible {
                    transform: translateY(0);
                }
                
                .admin-toolbar.hidden {
                    display: none;
                }
                
                .admin-toggle {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: #ff6b6b;
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    font-size: 18px;
                    cursor: pointer;
                    z-index: 10001;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                }
                
                .admin-toggle:hover {
                    background: #ee5a24;
                    transform: scale(1.1);
                }
                
                .entry-admin-controls {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 8px;
                    padding: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    display: none;
                    gap: 5px;
                }
                
                .entry-admin-controls.visible {
                    display: flex;
                }
                
                .admin-btn {
                    background: #007cba;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    cursor: pointer;
                    transition: background 0.2s ease;
                }
                
                .admin-btn:hover {
                    background: #005a87;
                }
                
                .admin-btn.danger {
                    background: #dc3545;
                }
                
                .admin-btn.danger:hover {
                    background: #c82333;
                }
                
                .admin-btn.warning {
                    background: #ffc107;
                    color: #212529;
                }
                
                .admin-btn.warning:hover {
                    background: #e0a800;
                }
                
                .entry-card {
                    position: relative;
                }
                
                .entry-card:hover .entry-admin-controls {
                    display: flex;
                }
                
                .admin-edit-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    z-index: 10002;
                    display: none;
                    justify-content: center;
                    align-items: center;
                }
                
                .admin-edit-modal.visible {
                    display: flex;
                }
                
                .admin-edit-content {
                    background: white;
                    border-radius: 12px;
                    padding: 25px;
                    max-width: 600px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                }
                
                .admin-edit-field {
                    margin-bottom: 15px;
                }
                
                .admin-edit-field label {
                    display: block;
                    font-weight: bold;
                    margin-bottom: 5px;
                    color: #333;
                }
                
                .admin-edit-field input,
                .admin-edit-field textarea,
                .admin-edit-field select {
                    width: 100%;
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    font-size: 14px;
                }
                
                .admin-edit-field textarea {
                    min-height: 100px;
                    resize: vertical;
                }
                
                .admin-edit-buttons {
                    display: flex;
                    gap: 10px;
                    justify-content: flex-end;
                    margin-top: 20px;
                }
                
                .admin-notification {
                    position: fixed;
                    top: 70px;
                    right: 20px;
                    background: #28a745;
                    color: white;
                    padding: 12px 20px;
                    border-radius: 6px;
                    z-index: 10003;
                    transform: translateX(100%);
                    transition: transform 0.3s ease;
                }
                
                .admin-notification.error {
                    background: #dc3545;
                }
                
                .admin-notification.visible {
                    transform: translateX(0);
                }
                
                body.admin-mode {
                    padding-top: 40px;
                }
            </style>
        `;
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    addAdminToolbar() {
        const toolbar = `
            <div id="admin-toolbar" class="admin-toolbar">
                <div>
                    <strong>🛠️ Admin Mode</strong> - Click on any entry to edit
                </div>
                <div>
                    <button class="admin-btn" onclick="adminEditor.showProblematicEntries()">
                        Find Issues (${this.countProblematicEntries()})
                    </button>
                    <button class="admin-btn" onclick="adminEditor.showAdminDashboard()">
                        Dashboard
                    </button>
                    <button class="admin-btn danger" onclick="adminEditor.toggleAdminMode()">
                        Exit Admin
                    </button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('afterbegin', toolbar);
    }

    addAdminToggle() {
        const toggle = `
            <button id="admin-toggle" class="admin-toggle" onclick="adminEditor.toggleAdminMode()" title="Toggle Admin Mode">
                ⚙️
            </button>
        `;
        document.body.insertAdjacentHTML('beforeend', toggle);
    }

    addEntryEditButtons() {
        // Add edit buttons to entry cards
        const entryCards = document.querySelectorAll('.entry-card, .card, [data-entry-id]');
        
        entryCards.forEach(card => {
            const entryId = card.getAttribute('data-entry-id') || this.extractEntryId(card);
            if (entryId) {
                const controls = `
                    <div class="entry-admin-controls">
                        <button class="admin-btn" onclick="adminEditor.editEntry(${entryId})" title="Edit Entry">
                            ✏️
                        </button>
                        <button class="admin-btn warning" onclick="adminEditor.flagEntry(${entryId})" title="Flag for Review">
                            🚩
                        </button>
                        <button class="admin-btn danger" onclick="adminEditor.deleteEntry(${entryId})" title="Delete Entry">
                            🗑️
                        </button>
                    </div>
                `;
                card.style.position = 'relative';
                card.insertAdjacentHTML('beforeend', controls);
            }
        });
    }

    extractEntryId(element) {
        // Try to extract entry ID from various possible sources
        const idFromData = element.getAttribute('data-entry-id');
        if (idFromData) return idFromData;

        // Look for links that might contain entry IDs
        const links = element.querySelectorAll('a[href*="/entry/"], a[href*="/entries/"]');
        for (let link of links) {
            const href = link.getAttribute('href');
            const match = href.match(/\/(\d+)\//);
            if (match) return match[1];
        }

        return null;
    }

    toggleAdminMode() {
        const toolbar = document.getElementById('admin-toolbar');
        const toggle = document.getElementById('admin-toggle');
        
        if (toolbar.classList.contains('visible')) {
            // Exit admin mode
            toolbar.classList.remove('visible');
            document.body.classList.remove('admin-mode');
            document.querySelectorAll('.entry-admin-controls').forEach(el => el.style.display = 'none');
        } else {
            // Enter admin mode
            toolbar.classList.add('visible');
            document.body.classList.add('admin-mode');
            document.querySelectorAll('.entry-admin-controls').forEach(el => el.style.display = 'flex');
        }
    }

    async editEntry(entryId) {
        try {
            // Get entry data
            const response = await fetch(`/api/entries/${entryId}/`);
            const entry = await response.json();
            
            this.showEditModal(entry);
        } catch (error) {
            this.showNotification('Failed to load entry data', 'error');
        }
    }

    showEditModal(entry) {
        const modal = `
            <div id="admin-edit-modal" class="admin-edit-modal visible">
                <div class="admin-edit-content">
                    <h3>Edit Entry: ${entry.term}</h3>
                    <form id="admin-edit-form">
                        <div class="admin-edit-field">
                            <label for="edit-term">Term:</label>
                            <input type="text" id="edit-term" value="${entry.term || ''}" required>
                        </div>
                        
                        <div class="admin-edit-field">
                            <label for="edit-notes">Notes/Description:</label>
                            <textarea id="edit-notes">${entry.notes || ''}</textarea>
                        </div>
                        
                        <div class="admin-edit-field">
                            <label for="edit-category">Category:</label>
                            <select id="edit-category">
                                <option value="slang" ${entry.category === 'slang' ? 'selected' : ''}>Slang</option>
                                <option value="insults" ${entry.category === 'insults' ? 'selected' : ''}>Insults</option>
                                <option value="tongue_twisters" ${entry.category === 'tongue_twisters' ? 'selected' : ''}>Tongue Twisters</option>
                                <option value="terms_of_endearment" ${entry.category === 'terms_of_endearment' ? 'selected' : ''}>Terms of Endearment</option>
                                <option value="idioms" ${entry.category === 'idioms' ? 'selected' : ''}>Idioms</option>
                                <option value="expressions" ${entry.category === 'expressions' ? 'selected' : ''}>Expressions</option>
                                <option value="other" ${entry.category === 'other' ? 'selected' : ''}>Other</option>
                            </select>
                        </div>
                        
                        <div class="admin-edit-buttons">
                            <button type="button" class="admin-btn" onclick="adminEditor.closeEditModal()">Cancel</button>
                            <button type="submit" class="admin-btn" style="background: #28a745;">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modal);
        
        // Handle form submission
        document.getElementById('admin-edit-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveEntry(entry.id);
        });
    }

    async saveEntry(entryId) {
        const formData = {
            term: document.getElementById('edit-term').value,
            notes: document.getElementById('edit-notes').value,
            category: document.getElementById('edit-category').value
        };

        try {
            const response = await fetch(`/admin/entries/quick-edit/${entryId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(result.message);
                this.closeEditModal();
                // Refresh the page to show changes
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to save changes', 'error');
        }
    }

    async deleteEntry(entryId) {
        if (!confirm('Are you sure you want to delete this entry? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/admin/entries/delete/${entryId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(result.message);
                // Remove the entry from the page
                const entryElement = document.querySelector(`[data-entry-id="${entryId}"]`);
                if (entryElement) {
                    entryElement.style.transition = 'opacity 0.3s ease';
                    entryElement.style.opacity = '0';
                    setTimeout(() => entryElement.remove(), 300);
                }
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to delete entry', 'error');
        }
    }

    async flagEntry(entryId) {
        try {
            const response = await fetch(`/admin/entries/flag/${entryId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(result.message);
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            this.showNotification('Failed to flag entry', 'error');
        }
    }

    closeEditModal() {
        const modal = document.getElementById('admin-edit-modal');
        if (modal) {
            modal.remove();
        }
    }

    showNotification(message, type = 'success') {
        const notification = `
            <div class="admin-notification ${type} visible">
                ${message}
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', notification);
        
        setTimeout(() => {
            const notif = document.querySelector('.admin-notification');
            if (notif) {
                notif.classList.remove('visible');
                setTimeout(() => notif.remove(), 300);
            }
        }, 3000);
    }

    countProblematicEntries() {
        // Count entries that might need review
        const entries = document.querySelectorAll('.entry-card, .card');
        let count = 0;
        
        entries.forEach(entry => {
            const text = entry.textContent.toLowerCase();
            if (text.includes('familiar address') || 
                text.includes('(talk)') || 
                text.includes('(clumsy') ||
                text.includes('(in the sense')) {
                count++;
            }
        });
        
        return count;
    }

    showProblematicEntries() {
        window.open('/admin/entries/data-cleaning/', '_blank');
    }

    showAdminDashboard() {
        window.open('/admin/', '_blank');
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token) return token.value;
        
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }
}

// Initialize admin editor when page loads
let adminEditor;
document.addEventListener('DOMContentLoaded', () => {
    adminEditor = new AdminInlineEditor();
});

// Make it globally available
window.adminEditor = adminEditor;
