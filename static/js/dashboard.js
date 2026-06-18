// Dashboard Modal Handlers
const addModal = document.getElementById('add-modal');
const editModal = document.getElementById('edit-modal');

// Selectors for Add
const addCategory = document.getElementById('add-category');
const addQuestion = document.getElementById('add-question');
const addAnswer = document.getElementById('add-answer');

// Selectors for Edit
const editId = document.getElementById('edit-id');
const editCategory = document.getElementById('edit-category');
const editQuestion = document.getElementById('edit-question');
const editAnswer = document.getElementById('edit-answer');

/**
 * Open Add FAQ Modal
 */
function openAddModal() {
    addQuestion.value = '';
    addAnswer.value = '';
    addCategory.selectedIndex = 0;
    addModal.classList.remove('hidden');
    addQuestion.focus();
}

function closeAddModal() {
    addModal.classList.add('hidden');
}

/**
 * Open Edit FAQ Modal
 */
function openEditModal(id, question, answer, category) {
    editId.value = id;
    editQuestion.value = question;
    editAnswer.value = answer;
    editCategory.value = category;
    
    editModal.classList.remove('hidden');
    editQuestion.focus();
}

function closeEditModal() {
    editModal.classList.add('hidden');
}

/**
 * Show notification toast helpers
 */
function showToast(message, category = 'success') {
    // We use the base.html toast container
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast-item pointer-events-auto flex items-center p-4 rounded-xl shadow-lg border backdrop-blur-glass transition-all duration-300 transform translate-x-0 bg-white/95 dark:bg-[#0c1220]/95
        ${category === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' : ''}
        ${category === 'danger' ? 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400' : ''}`;
        
    toast.innerHTML = `
        <div class="mr-3 text-lg">
            <i class="fa-solid ${category === 'success' ? 'fa-circle-check' : 'fa-circle-xmark'}"></i>
        </div>
        <div class="flex-1 text-sm font-medium">${message}</div>
        <button onclick="this.parentElement.remove()" class="ml-4 text-slate-400 hover:text-slate-650 transition-colors">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Submit Create FAQ via API
 */
async function submitAddFaq() {
    const question = addQuestion.value.trim();
    const answer = addAnswer.value.trim();
    const category = addCategory.value;

    if (!question || !answer) {
        showToast("Please fill in both Question and Answer fields.", "danger");
        return;
    }

    try {
        const response = await fetch('/api/faq', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question, answer, category })
        });

        const data = await response.json();
        
        if (response.ok) {
            closeAddModal();
            showToast("FAQ entry successfully added.");
            // Reload page to show updated table
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(data.error || "Failed to create FAQ.", "danger");
        }
    } catch (err) {
        console.error(err);
        showToast("Network error: Unable to contact FAQ API.", "danger");
    }
}

/**
 * Submit Update FAQ via API
 */
async function submitEditFaq() {
    const id = editId.value;
    const question = editQuestion.value.trim();
    const answer = editAnswer.value.trim();
    const category = editCategory.value;

    if (!question || !answer) {
        showToast("Question and Answer cannot be empty.", "danger");
        return;
    }

    try {
        const response = await fetch(`/api/faq/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question, answer, category })
        });

        const data = await response.json();

        if (response.ok) {
            closeEditModal();
            showToast("FAQ entry successfully updated.");
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(data.error || "Failed to update FAQ.", "danger");
        }
    } catch (err) {
        console.error(err);
        showToast("Network error: Unable to contact FAQ API.", "danger");
    }
}

/**
 * Delete FAQ via API
 */
async function deleteFaq(id) {
    if (!confirm("Are you sure you want to permanently delete this FAQ entry? This will also remove it from the chatbot matching corpus.")) {
        return;
    }

    try {
        const response = await fetch(`/api/faq/${id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showToast("FAQ entry successfully deleted.");
            setTimeout(() => window.location.reload(), 1000);
        } else {
            showToast(data.error || "Failed to delete FAQ.", "danger");
        }
    } catch (err) {
        console.error(err);
        showToast("Network error: Unable to contact FAQ API.", "danger");
    }
}
