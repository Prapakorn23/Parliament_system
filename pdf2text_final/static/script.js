// ===================================================
// PDF to Text Converter - JavaScript
// Adapted to match Duplicate UI structure
// ===================================================

// ===================================================
// Initialization
// ===================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('PDF to Text Converter initialized');
    
    initializeEventListeners();
    initializeHelpModal();
    initializeSearchBar();
    
    // Load first page if in page-by-page mode
    if (window.pageView && window.pageView.pagesData && window.pageView.pagesData.length > 0) {
        loadPage(1);
    }
});

// ===================================================
// Event Listeners Setup
// ===================================================

function initializeEventListeners() {
    // File Upload - Drag and Drop
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const resetBtn = document.getElementById('resetBtn');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-blue-500', 'bg-blue-50');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-blue-500', 'bg-blue-50');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });
        
        fileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                handleFileSelect(this.files[0]);
            }
        });
    }
    
    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            if (fileInput && fileInput.files.length > 0) {
                updateStepIndicator(2);
                showProgress();
            }
        });
    }
    
    // Reset button
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            resetAll();
        });
    }
}

function initializeHelpModal() {
    const helpBtn = document.getElementById('helpBtn');
    const helpModal = document.getElementById('helpModal');
    const closeHelp = document.getElementById('closeHelp');
    
    if (helpBtn && helpModal) {
        helpBtn.addEventListener('click', () => {
            helpModal.classList.remove('hidden');
        });
    }
    
    if (closeHelp) {
        closeHelp.addEventListener('click', () => {
            helpModal.classList.add('hidden');
        });
    }
    
    if (helpModal) {
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                helpModal.classList.add('hidden');
            }
        });
    }
}

// ===================================================
// Step Indicator
// ===================================================

function updateStepIndicator(stepNum) {
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    
    if (!step1 || !step2 || !step3) return;
    
    [step1, step2, step3].forEach((step, index) => {
        const circle = step.querySelector('div');
        const text = step.querySelector('span');
        
        if (index < stepNum - 1) {
            // Completed step
            circle.classList.remove('bg-gray-300', 'bg-blue-600');
            circle.classList.add('bg-green-500');
            circle.innerHTML = '<i class="fas fa-check text-white text-sm"></i>';
            if (text) {
                text.classList.remove('text-gray-400');
                text.classList.add('text-green-600');
            }
        } else if (index === stepNum - 1) {
            // Current step
            circle.classList.remove('bg-gray-300', 'bg-green-500');
            circle.classList.add('bg-blue-600');
            circle.textContent = stepNum;
            if (text) {
                text.classList.remove('text-gray-400');
                text.classList.add('text-gray-900');
            }
        } else {
            // Future step
            circle.classList.remove('bg-blue-600', 'bg-green-500');
            circle.classList.add('bg-gray-300');
            circle.textContent = index + 1;
            if (text) {
                text.classList.remove('text-gray-900');
                text.classList.add('text-gray-400');
            }
        }
    });
}

// ===================================================
// File Upload & Selection
// ===================================================

function handleFileSelect(file) {
    const selectedFileContainer = document.getElementById('selectedFileContainer');
    const selectedFileName = document.getElementById('selectedFileName');
    
    if (selectedFileContainer && selectedFileName) {
        selectedFileContainer.classList.remove('hidden');
        selectedFileName.textContent = file.name;
    }
}

function showProgress() {
    const uploadProgress = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (uploadProgress) {
        uploadProgress.classList.remove('hidden');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            if (progressFill) progressFill.style.width = progress + '%';
        }, 200);
        
        // Clear interval on page unload
        window.addEventListener('beforeunload', () => clearInterval(interval));
    }
}

// ===================================================
// Page Navigation (for multi-page PDFs)
// ===================================================

function toggleView() {
    const allPagesView = document.getElementById('allPagesView');
    const pageByPageView = document.getElementById('pageByPageView');
    const viewModeText = document.getElementById('viewModeText');
    
    if (!window.pageView) return;
    
    window.pageView.isPageByPage = !window.pageView.isPageByPage;
    
    if (window.pageView.isPageByPage) {
        if (allPagesView) allPagesView.classList.add('hidden');
        if (pageByPageView) pageByPageView.classList.remove('hidden');
        if (viewModeText) viewModeText.textContent = 'ดูทุกหน้า';
        loadPage(1);
    } else {
        if (allPagesView) allPagesView.classList.remove('hidden');
        if (pageByPageView) pageByPageView.classList.add('hidden');
        if (viewModeText) viewModeText.textContent = 'ดูทีละหน้า';
    }
}

function loadPage(pageNumber) {
    if (!window.pageView || !window.pageView.pagesData) return;
    
    const { pagesData, totalPages } = window.pageView;
    
    if (pageNumber < 1 || pageNumber > totalPages) return;
    
    window.pageView.currentPage = pageNumber;
    const pageData = pagesData[pageNumber - 1];
    
    // Update page text
    const pageText = document.getElementById('pageText');
    if (pageText) {
        pageText.value = pageData.text || '';
    }
    
    // Update page input
    const pageInput = document.getElementById('pageInput');
    if (pageInput) {
        pageInput.value = pageNumber;
    }
    
    // Update OCR status
    const pageOcrStatus = document.getElementById('pageOcrStatus');
    if (pageOcrStatus) {
        if (pageData.ocr_used) {
            pageOcrStatus.classList.remove('hidden');
        } else {
            pageOcrStatus.classList.add('hidden');
        }
    }
    
    // Update navigation buttons
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    
    if (prevBtn) prevBtn.disabled = pageNumber <= 1;
    if (nextBtn) nextBtn.disabled = pageNumber >= totalPages;
}

function prevPage() {
    if (window.pageView && window.pageView.currentPage > 1) {
        loadPage(window.pageView.currentPage - 1);
    }
}

function nextPage() {
    if (window.pageView && window.pageView.currentPage < window.pageView.totalPages) {
        loadPage(window.pageView.currentPage + 1);
    }
}

function goToPage(pageNumber) {
    const page = parseInt(pageNumber);
    if (!isNaN(page) && window.pageView) {
        const { totalPages } = window.pageView;
        if (page >= 1 && page <= totalPages) {
            loadPage(page);
        }
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (!window.pageView || !window.pageView.isPageByPage) return;
    
    if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevPage();
    } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        nextPage();
    }
});

// ===================================================
// Text Summarization
// ===================================================

async function summarizeText() {
    const resultText = document.getElementById('resultText');
    const summarySection = document.getElementById('summarySection');
    const summaryText = document.getElementById('summaryText');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const processingStats = document.getElementById('processingStats');
    
    if (!resultText || !resultText.value) {
        alert('ไม่พบข้อความที่จะสรุป');
        return;
    }
    
    // Show summary section
    if (summarySection) {
        summarySection.classList.remove('hidden');
        summarySection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Update button state
    if (summarizeBtn) {
        summarizeBtn.disabled = true;
        summarizeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span class="hidden sm:inline">กำลังสรุป...</span>';
    }
    
    // Show loading
    if (summaryText) {
        summaryText.value = 'กำลังประมวลผล กรุณารอสักครู่...';
    }
    
    // ตรวจสอบว่ามาจาก search หรือไม่
    const fromSearch = window.documentData?.from_search || false;
    const extractionId = window.documentData?.extraction_id || null;
    
    try {
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: resultText.value,
                lang: 'auto',
                provider: 'auto',
                filename: window.documentData?.filename || 'unknown',
                from_search: fromSearch,
                extraction_id: extractionId
            })
        });
        
        if (!response.ok) {
            throw new Error('เกิดข้อผิดพลาดในการสรุป');
        }
        
        const data = await response.json();
        
        // Display summary
        if (summaryText) {
            summaryText.value = data.summary;
        }
        
        // Display stats
        if (processingStats) {
            processingStats.classList.remove('hidden');
            const processingTimeEl = document.getElementById('processingTime');
            const textLengthEl = document.getElementById('textLength');
            const summaryLengthEl = document.getElementById('summaryLength');
            
            if (processingTimeEl) processingTimeEl.textContent = data.processing_time || '-';
            if (textLengthEl) textLengthEl.textContent = (data.text_length || 0).toLocaleString() + ' ตัวอักษร';
            if (summaryLengthEl) summaryLengthEl.textContent = (data.summary_length || 0).toLocaleString() + ' ตัวอักษร';
        }
        
        // Update step indicator
        updateStepIndicator(3);
        
    } catch (error) {
        if (summaryText) {
            summaryText.value = 'เกิดข้อผิดพลาด: ' + error.message;
        }
        console.error('Summarization error:', error);
    } finally {
        // Reset button
        if (summarizeBtn) {
            summarizeBtn.disabled = false;
            summarizeBtn.innerHTML = '<i class="fas fa-robot"></i><span class="hidden sm:inline">สรุปข้อความ</span>';
        }
    }
}

function clearSummary() {
    const summarySection = document.getElementById('summarySection');
    if (summarySection) {
        summarySection.classList.add('hidden');
    }
}

// ===================================================
// Copy & Download Functions
// ===================================================

async function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    try {
        await navigator.clipboard.writeText(element.value);
        showToast('คัดลอกไปยังคลิปบอร์ดแล้ว! ✓');
    } catch (err) {
        // Fallback for older browsers
        element.select();
        document.execCommand('copy');
        showToast('คัดลอกไปยังคลิปบอร์ดแล้ว! ✓');
    }
}

function downloadExtractedText() {
    const resultText = document.getElementById('resultText');
    const filename = window.documentData ? window.documentData.filename : 'extracted_text.txt';
    
    if (!resultText || !resultText.value) {
        alert('ไม่พบข้อความที่จะดาวน์โหลด');
        return;
    }
    
    const blob = new Blob([resultText.value], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename.replace(/\.[^/.]+$/, '') + '.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showToast('ดาวน์โหลดเรียบร้อย! ✓');
}

async function downloadSummary() {
    const summaryText = document.getElementById('summaryText');
    const filename = window.documentData ? window.documentData.filename : 'document';
    
    if (!summaryText || !summaryText.value) {
        alert('ไม่พบข้อความสรุปที่จะดาวน์โหลด');
        return;
    }
    
    const blob = new Blob([summaryText.value], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename.replace(/\.[^/.]+$/, '') + '_summary.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showToast('ดาวน์โหลดสรุปเรียบร้อย! ✓');
}

// ===================================================
// Reset All Function - รีเซ็ตทุกอย่างในหน้าเว็บ
// ===================================================

function resetAll() {
    if (confirm('ต้องการล้างข้อมูลทั้งหมดและเริ่มต้นใหม่หรือไม่?\n\n- ข้อความที่แปลง\n- สรุปข้อความ\n- ผลการค้นหา\n- ตัวกรอง\n- ไฟล์ที่เลือก')) {
        // Show loading
        showToast('🔄 กำลังรีเซ็ตและเริ่มต้นใหม่...', 1000);
        
        // Redirect to home page to reset everything
        setTimeout(() => {
            window.location.href = '/';
        }, 800);
    }
}

// Legacy function - เรียกใช้ resetAll() แทน
function resetResults() {
    resetAll();
}

// ===================================================
// Toast Notifications
// ===================================================

function showToast(message, duration = 3000) {
    // Remove existing toasts
    const existingToast = document.querySelector('.toast');
    if (existingToast) existingToast.remove();
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ===================================================
// Utility Functions
// ===================================================

// Auto-resize textarea
document.querySelectorAll('textarea').forEach(textarea => {
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});

// Handle errors globally
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// ===================================================
// Search Bar Functionality
// ===================================================

let searchTimeout;
let autocompleteTimeout;
let currentPage = 1;
const resultsPerPage = 10;
let selectedSuggestionIndex = -1;
let currentSuggestions = [];

function initializeSearchBar() {
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    const closeResultsBtn = document.getElementById('closeResultsBtn');
    
    if (searchInput) {
        // Autocomplete suggestions (triggered on every input)
        searchInput.addEventListener('input', function() {
            clearTimeout(autocompleteTimeout);
            const query = this.value.trim();
            
            // Show autocomplete for single character or more
            if (query.length >= 1) {
                autocompleteTimeout = setTimeout(() => {
                    loadAutocompleteSuggestions(query);
                }, 300); // Faster response for autocomplete
            } else {
                hideAutocompleteDropdown();
                hideSearchResults(); // ซ่อน search results เมื่อลบข้อความ
            }
            
            // ไม่เรียก performSearch อัตโนมัติ - รอให้ผู้ใช้เลือก suggestion หรือกด Enter/ปุ่มค้นหา
        });
        
        // Handle keyboard navigation in autocomplete
        searchInput.addEventListener('keydown', function(e) {
            const dropdown = document.getElementById('autocompleteDropdown');
            if (!dropdown || dropdown.classList.contains('hidden')) {
                // If dropdown is hidden and user presses Enter, perform search
                if (e.key === 'Enter') {
                    e.preventDefault();
                    hideAutocompleteDropdown();
                    performSearch(this.value.trim(), 1);
                }
                return;
            }
            
            const suggestions = dropdown.querySelectorAll('.suggestion-item');
            if (suggestions.length === 0) return;
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedSuggestionIndex = Math.min(selectedSuggestionIndex + 1, suggestions.length - 1);
                updateSuggestionSelection(suggestions);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedSuggestionIndex = Math.max(selectedSuggestionIndex - 1, -1);
                updateSuggestionSelection(suggestions);
            } else if (e.key === 'Enter' && selectedSuggestionIndex >= 0) {
                e.preventDefault();
                const selected = suggestions[selectedSuggestionIndex];
                if (selected) {
                    selectSuggestion(selected);
                }
            } else if (e.key === 'Enter' && selectedSuggestionIndex < 0) {
                // กด Enter โดยไม่ได้เลือก suggestion - ให้ค้นหา
                e.preventDefault();
                hideAutocompleteDropdown();
                performSearch(this.value.trim(), 1);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                hideAutocompleteDropdown();
            }
        });
        
        // Hide autocomplete when clicking outside
        document.addEventListener('click', function(e) {
            const searchContainer = document.getElementById('searchContainer');
            const dropdown = document.getElementById('autocompleteDropdown');
            if (searchContainer && dropdown && !searchContainer.contains(e.target)) {
                hideAutocompleteDropdown();
            }
        });
    }
    
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const query = document.getElementById('searchInput').value.trim();
            if (query && query.length >= 1) {
                hideAutocompleteDropdown(); // ซ่อน dropdown เมื่อกดปุ่มค้นหา
                performSearch(query, 1);
            }
        });
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            clearFilters();
        });
    }
    
    if (closeResultsBtn) {
        closeResultsBtn.addEventListener('click', function() {
            hideSearchResults();
        });
    }
    
    // Load popular tags for suggestions
    loadPopularTags();
}

// Load autocomplete suggestions
async function loadAutocompleteSuggestions(query) {
    if (!query || query.length < 1) {
        hideAutocompleteDropdown();
        return;
    }
    
    try {
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success && data.suggestions && data.suggestions.length > 0) {
            displayAutocompleteSuggestions(data.suggestions, query);
        } else {
            hideAutocompleteDropdown();
        }
    } catch (error) {
        console.error('Autocomplete error:', error);
        hideAutocompleteDropdown();
    }
}

// Display autocomplete suggestions
function displayAutocompleteSuggestions(suggestions, query) {
    const dropdown = document.getElementById('autocompleteDropdown');
    if (!dropdown) return;
    
    currentSuggestions = suggestions;
    selectedSuggestionIndex = -1;
    
    dropdown.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item px-4 py-2 hover:bg-blue-50 cursor-pointer flex items-center gap-3';
        item.dataset.index = index;
        
        // Highlight matching text
        const highlightedFilename = highlightSuggestionText(suggestion.filename, query);
        
        item.innerHTML = `
            <i class="fas ${getFileIcon(suggestion.file_type)} text-gray-400"></i>
            <span class="flex-1">${highlightedFilename}</span>
            <span class="text-xs text-gray-500">${(suggestion.file_type || '').toUpperCase()}</span>
        `;
        
        item.addEventListener('click', () => {
            selectSuggestion(item);
        });
        
        item.addEventListener('mouseenter', () => {
            selectedSuggestionIndex = index;
            updateSuggestionSelection(dropdown.querySelectorAll('.suggestion-item'));
        });
        
        dropdown.appendChild(item);
    });
    
    dropdown.classList.remove('hidden');
}

// Highlight suggestion text
function highlightSuggestionText(text, query) {
    if (!text || !query) return text;
    
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<span class="font-semibold text-blue-600">$1</span>');
}

// Update suggestion selection
function updateSuggestionSelection(suggestions) {
    suggestions.forEach((item, index) => {
        if (index === selectedSuggestionIndex) {
            item.classList.add('bg-blue-100');
            item.classList.remove('hover:bg-blue-50');
            // Scroll into view if needed
            item.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        } else {
            item.classList.remove('bg-blue-100');
            item.classList.add('hover:bg-blue-50');
        }
    });
}

// Select a suggestion
function selectSuggestion(item) {
    const index = parseInt(item.dataset.index);
    const suggestion = currentSuggestions[index];
    
    if (suggestion) {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = suggestion.filename;
            hideAutocompleteDropdown();
            performSearch(suggestion.filename, 1);
        }
    }
}

// Hide autocomplete dropdown
function hideAutocompleteDropdown() {
    const dropdown = document.getElementById('autocompleteDropdown');
    if (dropdown) {
        dropdown.classList.add('hidden');
    }
    selectedSuggestionIndex = -1;
    currentSuggestions = [];
}

// Perform search
async function performSearch(query, page = 1) {
    if (!query || query.length < 1) {
        return;
    }
    
    currentPage = page;
    
    // Show loading
    const loadingEl = document.getElementById('searchLoading');
    const resultsEl = document.getElementById('searchResults');
    if (loadingEl) loadingEl.classList.remove('hidden');
    if (resultsEl) resultsEl.classList.add('hidden');
    
    // Get filter values
    const fileType = document.getElementById('fileTypeFilter')?.value || '';
    const dateFrom = document.getElementById('dateFromFilter')?.value || '';
    const dateTo = document.getElementById('dateToFilter')?.value || '';
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                file_type: fileType,
                date_from: dateFrom,
                date_to: dateTo,
                page: page,
                per_page: resultsPerPage
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displaySearchResults(data.results, data.total, data.page, data.pages);
        } else {
            showSearchError(data.error || 'เกิดข้อผิดพลาดในการค้นหา');
        }
    } catch (error) {
        console.error('Search error:', error);
        showSearchError('เกิดข้อผิดพลาดในการเชื่อมต่อ');
    } finally {
        if (loadingEl) loadingEl.classList.add('hidden');
    }
}

// Display search results
function displaySearchResults(results, total, page, totalPages) {
    const resultsEl = document.getElementById('searchResults');
    const containerEl = document.getElementById('resultsContainer');
    const countEl = document.getElementById('resultCount');
    
    if (!resultsEl || !containerEl) return;
    
    // Update count
    if (countEl) {
        countEl.textContent = total.toLocaleString();
    }
    
    // Clear previous results
    containerEl.innerHTML = '';
    
    if (results.length === 0) {
        containerEl.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-search text-gray-300 text-6xl mb-4"></i>
                <p class="text-gray-600 text-lg">ไม่พบผลการค้นหา</p>
                <p class="text-gray-500 text-sm mt-2">ลองใช้คำค้นหาอื่นหรือล้างตัวกรอง</p>
            </div>
        `;
    } else {
        // Display results
        results.forEach(result => {
            const card = createResultCard(result);
            containerEl.appendChild(card);
        });
        
        // Display pagination
        if (totalPages > 1) {
            displayPagination(page, totalPages);
        }
    }
    
    // Show results section
    resultsEl.classList.remove('hidden');
    
    // Scroll to results
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create result card
function createResultCard(result) {
    const card = document.createElement('div');
    card.className = 'search-result-card';
    
    // Get file icon class
    const fileIconClass = getFileIconClass(result.file_type);
    
    // Format date
    const date = result.created_at ? new Date(result.created_at) : new Date();
    const formattedDate = date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Highlight search terms
    const query = document.getElementById('searchInput').value.trim();
    const highlightedFilename = highlightText(result.filename || '', query);
    const highlightedPreview = highlightText(result.extracted_text_preview || '', query);
    
    // Tags HTML
    let tagsHtml = '';
    if (result.tags && result.tags.length > 0) {
        tagsHtml = result.tags.map(tag => `
            <span class="tag-badge" style="background-color: ${tag.color || '#3B82F6'}20; color: ${tag.color || '#3B82F6'};">
                <i class="fas fa-tag mr-1"></i>
                ${tag.name}
            </span>
        `).join('');
    }
    
    card.innerHTML = `
        <div class="flex gap-4">
            <!-- File Icon -->
            <div class="file-icon ${fileIconClass}">
                <i class="fas ${getFileIcon(result.file_type)}"></i>
            </div>
            
            <!-- Content -->
            <div class="flex-1">
                <div class="flex items-start justify-between mb-2">
                    <h4 class="text-lg font-semibold text-gray-900">
                        ${highlightedFilename}
                    </h4>
                    <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        ${(result.file_type || 'unknown').toUpperCase()}
                    </span>
                </div>
                
                <!-- Preview -->
                ${result.extracted_text_preview ? `
                    <p class="text-sm text-gray-600 mb-2 line-clamp-2">
                        ${highlightedPreview}
                    </p>
                ` : ''}
                
                <!-- Tags -->
                ${tagsHtml ? `<div class="mb-2">${tagsHtml}</div>` : ''}
                
                <!-- Metadata -->
                <div class="flex items-center gap-4 text-xs text-gray-500 mt-2 flex-wrap">
                    <span>
                        <i class="fas fa-file-alt mr-1"></i>
                        ${formatFileSize(result.file_size || 0)}
                    </span>
                    <span>
                        <i class="fas fa-font mr-1"></i>
                        ${(result.extracted_text_length || 0).toLocaleString()} ตัวอักษร
                    </span>
                    ${result.total_pages > 0 ? `
                        <span>
                            <i class="fas fa-file-pdf mr-1"></i>
                            ${result.total_pages} หน้า
                        </span>
                    ` : ''}
                    <span>
                        <i class="fas fa-calendar mr-1"></i>
                        ${formattedDate}
                    </span>
                    ${result.summary_count > 0 ? `
                        <span>
                            <i class="fas fa-robot mr-1"></i>
                            ${result.summary_count} สรุป
                        </span>
                    ` : ''}
                </div>
                
                <!-- Actions -->
                <div class="flex gap-2 mt-3">
                    <button 
                        onclick="viewExtraction(${result.id})" 
                        class="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                    >
                        <i class="fas fa-file-upload mr-1"></i>
                        โหลดไฟล์
                    </button>
                    <button 
                        onclick="downloadExtraction(${result.id})" 
                        class="px-3 py-1.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg text-sm font-medium transition-colors"
                    >
                        <i class="fas fa-download mr-1"></i>
                        ดาวน์โหลด
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

// Highlight search terms in text
function highlightText(text, query) {
    if (!text || !query) return text;
    
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<span class="highlight">$1</span>');
}

// Escape regex special characters
function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Display pagination
function displayPagination(currentPage, totalPages) {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;
    
    paginationEl.innerHTML = '';
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.className = 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed';
    prevBtn.disabled = currentPage === 1;
    prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevBtn.onclick = () => {
        const query = document.getElementById('searchInput').value.trim();
        performSearch(query, currentPage - 1);
    };
    paginationEl.appendChild(prevBtn);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 ${
                i === currentPage ? 'bg-blue-600 text-white border-blue-600' : ''
            }`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => {
                const query = document.getElementById('searchInput').value.trim();
                performSearch(query, i);
            };
            paginationEl.appendChild(pageBtn);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const ellipsis = document.createElement('span');
            ellipsis.className = 'px-2';
            ellipsis.textContent = '...';
            paginationEl.appendChild(ellipsis);
        }
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.className = 'px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextBtn.onclick = () => {
        const query = document.getElementById('searchInput').value.trim();
        performSearch(query, currentPage + 1);
    };
    paginationEl.appendChild(nextBtn);
}

// Load popular tags for suggestions
async function loadPopularTags() {
    try {
        const response = await fetch('/api/tags/popular?limit=10');
        const data = await response.json();
        
        if (data.success && data.tags && data.tags.length > 0) {
            const suggestionsEl = document.getElementById('tagSuggestions');
            if (suggestionsEl) {
                suggestionsEl.classList.remove('hidden');
                
                data.tags.forEach(tag => {
                    const tagBtn = document.createElement('button');
                    tagBtn.className = 'tag-badge';
                    tagBtn.style.backgroundColor = (tag.color || '#3B82F6') + '20';
                    tagBtn.style.color = tag.color || '#3B82F6';
                    tagBtn.innerHTML = `<i class="fas fa-tag mr-1"></i>${tag.name}`;
                    tagBtn.onclick = () => {
                        document.getElementById('searchInput').value = tag.name;
                        performSearch(tag.name, 1);
                    };
                    suggestionsEl.appendChild(tagBtn);
                });
            }
        }
    } catch (error) {
        // Silently fail - tags are optional
        console.log('Tags not available:', error);
    }
}

// Clear filters
function clearFilters() {
    const fileTypeFilter = document.getElementById('fileTypeFilter');
    const dateFromFilter = document.getElementById('dateFromFilter');
    const dateToFilter = document.getElementById('dateToFilter');
    
    if (fileTypeFilter) fileTypeFilter.value = '';
    if (dateFromFilter) dateFromFilter.value = '';
    if (dateToFilter) dateToFilter.value = '';
    
    const query = document.getElementById('searchInput')?.value.trim();
    if (query) {
        performSearch(query, 1);
    }
}

// Hide search results
function hideSearchResults() {
    const resultsEl = document.getElementById('searchResults');
    if (resultsEl) {
        resultsEl.classList.add('hidden');
    }
}

// Helper functions for search
function getFileIcon(fileType) {
    const icons = {
        'pdf': 'fa-file-pdf',
        'docx': 'fa-file-word',
        'txt': 'fa-file-alt',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
        'gif': 'fa-file-image',
        'bmp': 'fa-file-image',
        'tiff': 'fa-file-image'
    };
    return icons[fileType?.toLowerCase()] || 'fa-file';
}

function getFileIconClass(fileType) {
    const classes = {
        'pdf': 'pdf',
        'docx': 'docx',
        'txt': 'txt',
        'jpg': 'jpg',
        'jpeg': 'jpg',
        'png': 'png',
        'gif': 'gif'
    };
    return classes[fileType?.toLowerCase()] || 'txt';
}

function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// View extraction details
function viewExtraction(id) {
    // Navigate to extraction detail page or show modal
    window.location.href = `/extraction/${id}`;
}

// Download extraction
async function downloadExtraction(id) {
    try {
        const response = await fetch(`/api/extractions/${id}/download`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `extraction_${id}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            alert('ไม่สามารถดาวน์โหลดไฟล์ได้');
        }
    } catch (error) {
        console.error('Download error:', error);
        alert('เกิดข้อผิดพลาดในการดาวน์โหลด');
    }
}

function showSearchError(message) {
    const containerEl = document.getElementById('resultsContainer');
    if (containerEl) {
        containerEl.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                <p class="text-red-600">${message}</p>
            </div>
        `;
    }
    
    const resultsEl = document.getElementById('searchResults');
    if (resultsEl) {
        resultsEl.classList.remove('hidden');
    }
}

console.log('🚀 PDF to Text Converter - Ready!');
