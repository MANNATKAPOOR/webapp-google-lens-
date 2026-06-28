// DOM Elements
const pages = {
    landing: document.getElementById('landingPage'),
    dashboard: document.getElementById('dashboardPage')
};

const btns = {
    theme: document.getElementById('themeToggleBtn'),
    tryNow: document.getElementById('tryNowBtn'),
    backToHome: document.getElementById('backToHomeBtn'),
    browse: document.getElementById('browseBtn'),
    analyze: document.getElementById('analyzeBtn'),
    copy: document.getElementById('copyBtn'),
    downloadJson: document.getElementById('downloadJsonBtn')
};

const upload = {
    dropZone: document.getElementById('dropZone'),
    fileInput: document.getElementById('fileInput'),
    imagePreview: document.getElementById('imagePreview'),
    placeholderText: document.querySelector('.placeholder-text')
};

const ui = {
    moonIcon: document.getElementById('moonIcon'),
    sunIcon: document.getElementById('sunIcon'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    resultsContent: document.getElementById('resultsContent'),
    resultActions: document.getElementById('resultActions'),
    toast: document.getElementById('toast')
};

let currentFile = null;
let currentResultData = null;

// API Configuration
const API_BASE_URL = window.location.origin; // Auto-detect: works locally, via ngrok, or in production

// --- Theme Management ---
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    if (theme === 'dark') {
        ui.moonIcon.style.display = 'block';
        ui.sunIcon.style.display = 'none';
    } else {
        ui.moonIcon.style.display = 'none';
        ui.sunIcon.style.display = 'block';
    }
}

// --- Navigation ---
function navigateTo(pageName) {
    Object.values(pages).forEach(page => page.classList.remove('active'));
    pages[pageName].classList.add('active');
}

// --- File Handling ---
function handleFileSelect(file) {
    if (!file) return;
    
    if (!file.type.startsWith('image/')) {
        showToast('Please upload an image file.', 'error');
        return;
    }

    // Check size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showToast('File is too large. Maximum size is 10MB.', 'error');
        return;
    }

    currentFile = file;
    btns.analyze.disabled = false;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        upload.imagePreview.src = e.target.result;
        upload.imagePreview.style.display = 'block';
        upload.placeholderText.style.display = 'none';
    };
    reader.readAsDataURL(file);
    
    // Clear previous results
    clearResults();
}

// --- Drag & Drop ---
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    upload.dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    upload.dropZone.addEventListener(eventName, () => {
        upload.dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    upload.dropZone.addEventListener(eventName, () => {
        upload.dropZone.classList.remove('dragover');
    }, false);
});

upload.dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) handleFileSelect(files[0]);
}, false);

// --- API Interaction ---
async function analyzeImage() {
    if (!currentFile) return;

    // UI State
    btns.analyze.disabled = true;
    ui.loadingOverlay.classList.add('active');
    
    const formData = new FormData();
    formData.append('file', currentFile);

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const data = await response.json();
        currentResultData = data;
        renderResults(data);
        showToast('Analysis complete', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
        clearResults();
    } finally {
        ui.loadingOverlay.classList.remove('active');
        btns.analyze.disabled = false;
    }
}

// --- Render Results ---
function renderResults(data) {
    ui.resultActions.style.display = 'flex';
    
    // Build tags HTML
    const tagsHtml = data.objects.map(obj => `<span class="tag">${obj}</span>`).join('');
    
    const html = `
        <div class="result-section" style="animation-delay: 0.1s">
            <h4>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                Extracted Text
            </h4>
            <div class="result-text">${escapeHTML(data.text)}</div>
        </div>

        <div class="result-section" style="animation-delay: 0.2s">
            <h4>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                AI Image Understanding
            </h4>
            <div class="result-text">${escapeHTML(data.description)}</div>
            ${tagsHtml ? `<div class="tags-container" style="margin-top: 12px;">${tagsHtml}</div>` : ''}
        </div>

        <div class="metrics-row" style="animation-delay: 0.3s">
            <div class="result-section metric">
                <h4>Language</h4>
                <div class="value" style="color: var(--text-primary)">${escapeHTML(data.language)}</div>
            </div>
            
            <div class="result-section metric">
                <h4>Confidence</h4>
                <div class="value">${data.confidence}%</div>
            </div>

            <div class="result-section metric">
                <h4>Time</h4>
                <div class="value" style="color: var(--text-secondary)">${escapeHTML(data.processing_time)}</div>
            </div>
        </div>
    `;
    
    ui.resultsContent.innerHTML = html;
}

function clearResults() {
    currentResultData = null;
    ui.resultActions.style.display = 'none';
    ui.resultsContent.innerHTML = `
        <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            <p>Results will appear here</p>
        </div>
    `;
}

// --- Utils ---
function escapeHTML(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
}

let toastTimeout;
function showToast(message, type = 'info') {
    ui.toast.textContent = message;
    ui.toast.className = `toast show ${type}`;
    
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        ui.toast.classList.remove('show');
    }, 3000);
}

function downloadDataAsJSON() {
    if (!currentResultData) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentResultData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "ocr_results.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

async function copyTextToClipboard() {
    if (!currentResultData || !currentResultData.text) return;
    try {
        await navigator.clipboard.writeText(currentResultData.text);
        showToast('Text copied to clipboard', 'success');
    } catch (err) {
        showToast('Failed to copy text', 'error');
    }
}

// --- Event Listeners ---
btns.theme.addEventListener('click', toggleTheme);
btns.tryNow.addEventListener('click', () => navigateTo('dashboard'));
btns.backToHome.addEventListener('click', () => navigateTo('landing'));

btns.browse.addEventListener('click', (e) => {
    e.preventDefault();
    upload.fileInput.click();
});

upload.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFileSelect(e.target.files[0]);
});

btns.analyze.addEventListener('click', analyzeImage);
btns.copy.addEventListener('click', copyTextToClipboard);
btns.downloadJson.addEventListener('click', downloadDataAsJSON);

// Init
initTheme();
