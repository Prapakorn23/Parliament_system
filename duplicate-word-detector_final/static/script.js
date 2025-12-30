// Word Frequency Analyzer - Updated for Laravel-style UI
class WordFrequencyAnalyzer {
    constructor() {
        this.currentAnalysisData = null;
        this.wordFrequencyChart = null;
        this.currentFiles = []; // เปลี่ยนเป็น array สำหรับหลายไฟล์
        this.currentPage = 1;
        this.wordsPerPage = 15;
        this.totalWords = 0;
        this.maxFileSize = 200 * 1024 * 1024; // Default 200MB (จะถูกอัปเดตจาก API)
        this.maxFileSizeMB = 200; // Default 200MB
        this.init();
    }

    async init() {
        await this.loadUploadConfig();
        this.setupEventListeners();
    }

    async loadUploadConfig() {
        try {
            const response = await fetch('/api/upload-config');
            if (response.ok) {
                const config = await response.json();
                this.maxFileSize = config.max_file_size;
                this.maxFileSizeMB = config.max_file_size_mb;
                // อัปเดตข้อความใน UI
                const fileSizeText = document.querySelector('[data-file-size-text]');
                if (fileSizeText) {
                    fileSizeText.textContent = `รองรับไฟล์: PDF, DOC, DOCX, TXT (สูงสุด ${Math.round(this.maxFileSizeMB)}MB)`;
                }
            }
        } catch (error) {
            console.warn('ไม่สามารถโหลดการตั้งค่าการอัปโหลดได้ ใช้ค่า default:', error);
        }
    }

    setupEventListeners() {
        // Tab Elements
        const fileTab = document.getElementById('fileTab');
        const textTab = document.getElementById('textTab');
        const fileTabContent = document.getElementById('fileTabContent');
        const textTabContent = document.getElementById('textTabContent');
        
        // Tab Switching
        fileTab.addEventListener('click', () => {
            fileTab.classList.add('border-blue-600', 'text-blue-600');
            fileTab.classList.remove('border-transparent', 'text-gray-500');
            textTab.classList.remove('border-blue-600', 'text-blue-600');
            textTab.classList.add('border-transparent', 'text-gray-500');
            fileTabContent.classList.remove('hidden');
            textTabContent.classList.add('hidden');
        });
        
        textTab.addEventListener('click', () => {
            textTab.classList.add('border-blue-600', 'text-blue-600');
            textTab.classList.remove('border-transparent', 'text-gray-500');
            fileTab.classList.remove('border-blue-600', 'text-blue-600');
            fileTab.classList.add('border-transparent', 'text-gray-500');
            textTabContent.classList.remove('hidden');
            fileTabContent.classList.add('hidden');
        });

        // Help Modal
        const helpBtn = document.getElementById('helpBtn');
        const helpModal = document.getElementById('helpModal');
        const closeHelp = document.getElementById('closeHelp');
        
        helpBtn.addEventListener('click', () => {
            helpModal.classList.remove('hidden');
        });
        
        closeHelp.addEventListener('click', () => {
            helpModal.classList.add('hidden');
        });
        
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                helpModal.classList.add('hidden');
            }
        });

        // Character Counter
        const textInput = document.getElementById('textInput');
        const charCount = document.getElementById('charCount');
        
        textInput.addEventListener('input', (e) => {
            const count = e.target.value.length;
            charCount.textContent = count.toLocaleString();
        });

        // File Upload - Drag and Drop
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
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
                this.handleFileUpload({ target: fileInput });
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e);
            }
        });

        // Remove all files button
        const removeAllFiles = document.getElementById('removeAllFiles');
        if (removeAllFiles) {
            removeAllFiles.addEventListener('click', (e) => {
                e.stopPropagation();
                this.clearSelectedFiles();
            });
        }

        // Analyze Button
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.addEventListener('click', () => {
            this.analyzeText();
        });

        // Reset Button
        const resetBtn = document.getElementById('resetBtn');
        resetBtn.addEventListener('click', () => {
            this.resetAnalysis();
        });
        
        // Reset button in results section
        const resetResultsBtn = document.getElementById('resetResultsBtn');
        if (resetResultsBtn) {
            resetResultsBtn.addEventListener('click', () => {
                this.resetAnalysis();
            });
        }

        // Export Button
        const exportBtn = document.getElementById('exportBtn');
        exportBtn.addEventListener('click', () => {
            this.exportResults();
        });

        // Pagination
        const prevPage = document.getElementById('prevPage');
        const nextPage = document.getElementById('nextPage');
        
        if (prevPage) {
            prevPage.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.displayWordTable(this.currentAnalysisData.word_frequency, this.currentPage - 1);
            }
        });
    }

        if (nextPage) {
            nextPage.addEventListener('click', () => {
                const totalPages = Math.ceil(this.totalWords / this.wordsPerPage);
                if (this.currentPage < totalPages) {
                    this.displayWordTable(this.currentAnalysisData.word_frequency, this.currentPage + 1);
                }
            });
        }
    }

    updateStepIndicator(stepNum) {
        const step1 = document.getElementById('step1');
        const step2 = document.getElementById('step2');
        const step3 = document.getElementById('step3');
        
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

    clearSelectedFiles() {
        const fileInput = document.getElementById('fileInput');
        fileInput.value = '';
        this.currentFiles = [];
        document.getElementById('selectedFilesContainer').classList.add('hidden');
    }

    removeFile(index) {
        this.currentFiles.splice(index, 1);
        this.displaySelectedFiles();
        // อัปเดต file input
        const fileInput = document.getElementById('fileInput');
        const dt = new DataTransfer();
        this.currentFiles.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
    }

    displaySelectedFiles() {
        const container = document.getElementById('selectedFilesContainer');
        const list = document.getElementById('selectedFilesList');
        const count = document.getElementById('fileCount');
        
        if (this.currentFiles.length === 0) {
            container.classList.add('hidden');
            return;
        }
        
        container.classList.remove('hidden');
        count.textContent = this.currentFiles.length;
        
        // สร้างรายการไฟล์
        list.innerHTML = this.currentFiles.map((file, index) => {
            const fileName = file.name.toLowerCase();
            const isPDF = fileName.endsWith('.pdf');
            const isTXT = fileName.endsWith('.txt') || fileName.endsWith('.text');
            const isDOC = fileName.endsWith('.doc') || fileName.endsWith('.docx');
            
            let icon = 'fa-file';
            let color = 'text-blue-600';
            if (isPDF) { icon = 'fa-file-pdf'; color = 'text-red-600'; }
            else if (isDOC) { icon = 'fa-file-word'; color = 'text-blue-600'; }
            else if (isTXT) { icon = 'fa-file-alt'; color = 'text-green-600'; }
            
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            
            return `
                <div class="p-2 bg-white border border-gray-200 rounded-lg flex items-center justify-between">
                    <div class="flex items-center gap-2 flex-1 min-w-0">
                        <i class="fas ${icon} ${color}"></i>
                        <span class="text-sm font-medium text-gray-800 truncate" title="${file.name}">${file.name}</span>
                        <span class="text-xs text-gray-500">(${sizeMB} MB)</span>
                    </div>
                    <button onclick="analyzer.removeFile(${index})" class="ml-2 text-red-600 hover:text-red-800">
                        <i class="fas fa-times"></i>
                        </button>
                </div>
            `;
        }).join('');
    }

    async handleFileUpload(event) {
        const files = Array.from(event.target.files);
        if (files.length === 0) return;

        // ตรวจสอบไฟล์ทั้งหมด
        const validFiles = [];
        const invalidFiles = [];
        
        for (const file of files) {
            const fileName = file.name.toLowerCase();
            const isPDF = fileName.endsWith('.pdf');
            const isTXT = fileName.endsWith('.txt') || fileName.endsWith('.text');
            const isDOC = fileName.endsWith('.doc') || fileName.endsWith('.docx');
            
            // ตรวจสอบประเภทไฟล์
            if (!isPDF && !isTXT && !isDOC) {
                invalidFiles.push(file.name);
                continue;
            }

            // ตรวจสอบขนาดไฟล์
            if (file.size > this.maxFileSize) {
                invalidFiles.push(`${file.name} (เกิน ${Math.round(this.maxFileSizeMB)}MB)`);
                continue;
            }
            
            validFiles.push(file);
        }
        
        // แสดงข้อผิดพลาดถ้ามี
        if (invalidFiles.length > 0) {
            alert(`ไฟล์ต่อไปนี้ไม่สามารถใช้งานได้:\n${invalidFiles.join('\n')}`);
        }
        
        if (validFiles.length === 0) {
            event.target.value = '';
            return;
        }
        
        // เพิ่มไฟล์ที่ถูกต้องเข้ารายการ
        this.currentFiles = this.currentFiles.concat(validFiles);
        this.displaySelectedFiles();
        
        // อัปโหลดและประมวลผลไฟล์ทั้งหมด
        await this.uploadAndProcessFiles(this.currentFiles);
    }

    async uploadAndProcessFiles(files) {
        if (files.length === 0) return;
        
        this.updateStepIndicator(2);
        
        // แยกไฟล์ตามประเภท
        const pdfFiles = [];
        const docFiles = [];
        const txtFiles = [];
        
        files.forEach(file => {
            const fileName = file.name.toLowerCase();
            if (fileName.endsWith('.pdf')) {
                pdfFiles.push(file);
            } else if (fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
                docFiles.push(file);
            } else if (fileName.endsWith('.txt') || fileName.endsWith('.text')) {
                txtFiles.push(file);
            }
        });
        
        // อ่านไฟล์ TXT ภายใน browser
        let allTextContent = '';
        for (const txtFile of txtFiles) {
            try {
                const text = await this.readTextFile(txtFile);
                allTextContent += text + '\n\n';
            } catch (error) {
                console.error(`ไม่สามารถอ่านไฟล์ ${txtFile.name}:`, error);
            }
        }
        
        // อัปโหลดไฟล์ PDF และ DOC ไปที่ server
        const filesToUpload = [...pdfFiles, ...docFiles];
        
        if (filesToUpload.length > 0) {
            this.showProgress(`กำลังอัปโหลด ${filesToUpload.length} ไฟล์...`, 10);
            
            try {
                const formData = new FormData();
                filesToUpload.forEach((file, index) => {
                    formData.append('files', file); // ใช้ 'files' (plural) และ append หลายไฟล์
                });
                
                this.updateProgress(30, 'กำลังแปลงไฟล์...');
                
                const response = await fetch('/api/upload-multiple', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // รวมข้อความจากไฟล์ที่อัปโหลด
                    const uploadedTexts = result.data.map(item => item.content || '').join('\n\n');
                    allTextContent += uploadedTexts;
                    
                    // เก็บข้อมูลไฟล์ (ใช้ไฟล์แรกถ้ามีหลายไฟล์)
                    const firstFile = result.data.find(item => item.success);
                    const fileInfo = firstFile ? {
                        file_name: firstFile.filename,
                        file_type: firstFile.file_type,
                        original_file_path: firstFile.original_file_path,
                        file_size: firstFile.file_size
                    } : null;
                    
                    this.updateProgress(70, 'กำลังวิเคราะห์...');
                    
                    // วิเคราะห์ข้อความรวม
                    if (allTextContent.trim()) {
                        document.getElementById('textInput').value = allTextContent;
                        // วิเคราะห์ข้อความรวมพร้อมข้อมูลไฟล์
                        await this.analyzeTextContent(allTextContent, fileInfo);
                    } else {
                        throw new Error('ไม่พบข้อความในไฟล์ที่อัปโหลด');
                    }
                } else {
                    throw new Error(result.error || 'ไม่สามารถแปลงไฟล์ได้');
                }
            } catch (error) {
                this.hideProgress();
                this.updateStepIndicator(1);
                alert('เกิดข้อผิดพลาด: ' + error.message);
            }
        } else if (allTextContent.trim()) {
            // มีเฉพาะไฟล์ TXT
            document.getElementById('textInput').value = allTextContent;
            this.updateProgress(50, 'กำลังวิเคราะห์...');
            await this.analyzeTextContent(allTextContent);
        }
    }
    
    readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsText(file, 'UTF-8');
        });
    }
    
    async analyzeTextContent(content, fileInfo = null) {
        // เรียก API analyze เพื่อวิเคราะห์ข้อความ
        try {
            const requestData = {
                text: content,
                filter_pos: true
            };
            
            // เพิ่มข้อมูลไฟล์ถ้ามี
            if (fileInfo) {
                requestData.file_name = fileInfo.file_name;
                requestData.file_type = fileInfo.file_type;
                requestData.original_file_path = fileInfo.original_file_path;
                requestData.file_size = fileInfo.file_size;
            }
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateProgress(100, 'เสร็จสิ้น!');
                setTimeout(() => {
                    this.currentAnalysisData = result.data;
                    this.displayResults(result.data);
                }, 500);
            } else {
                throw new Error(result.error || 'ไม่สามารถวิเคราะห์ได้');
            }
        } catch (error) {
            this.hideProgress();
            this.updateStepIndicator(1);
            alert('เกิดข้อผิดพลาดในการวิเคราะห์: ' + error.message);
        }
    }

    async analyzeText() {
        const fileTabContent = document.getElementById('fileTabContent');
        const text = document.getElementById('textInput').value.trim();

        if (!text) {
            alert('กรุณาพิมพ์ข้อความหรืออัปโหลดไฟล์');
            return;
        }

        this.updateStepIndicator(2);
        this.showProgress('กำลังวิเคราะห์ข้อความ...', 20);

        try {
            this.updateProgress(50, 'กำลังประมวลผล...');
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    filter_pos: true
                })
            });

            const result = await response.json();

            if (result.success) {
                this.updateProgress(100, 'เสร็จสิ้น!');
                setTimeout(() => {
                    this.currentAnalysisData = result.data;
                    this.displayResults(result.data);
                }, 500);
            } else {
                this.hideProgress();
                this.updateStepIndicator(1);
                alert('เกิดข้อผิดพลาด: ' + (result.error || 'ไม่สามารถวิเคราะห์ได้'));
            }
        } catch (error) {
            this.hideProgress();
            this.updateStepIndicator(1);
            alert('เกิดข้อผิดพลาด: ' + error.message);
        }
    }

    displayResults(data) {
        console.log('Display results called with data:', data);
        
        this.hideProgress();
        this.updateStepIndicator(3);
        
        // Hide input, show results
        document.getElementById('inputSection').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');
        
        // Update statistics
        this.animateNumber('totalWords', 0, data.total_words, 1000);
        this.animateNumber('uniqueWords', 0, data.unique_words, 1000);
        
        // Calculate and display categories count
        const categoriesCount = Object.keys(data.categorized_words || {}).length;
        this.animateNumber('totalCategories', 0, categoriesCount, 1000);
        
        // Calculate average frequency
        const avgFreq = data.total_words > 0 ? (data.total_words / data.unique_words).toFixed(1) : 0;
        this.animateNumber('avgFrequency', 0, avgFreq, 1000);
        
        // Create chart - รอให้ DOM พร้อมก่อน
        setTimeout(() => {
            console.log('About to create chart with top_words:', data.top_words);
            if (data.top_words) {
                this.createWordFrequencyChart(data.top_words);
        } else {
                console.error('top_words is missing from data');
            }
        }, 300);
        
        // Display categories
        setTimeout(() => {
            this.displayCategories(data.categorized_words, data.top_words_by_category);
        }, 500);
        
        // Display word table
        setTimeout(() => {
            this.displayWordTable(data.word_frequency);
        }, 700);
        
        // Scroll to results
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 200);
    }

    animateNumber(elementId, start, end, duration) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                current = end;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString();
        }, 16);
    }

    createWordFrequencyChart(topWords) {
        const ctx = document.getElementById('wordFrequencyChart');
        if (!ctx) {
            console.error('❌ Canvas element #wordFrequencyChart not found');
            return;
        }

        console.log('📊 Creating chart with data:', topWords);
        console.log('📊 Data type:', typeof topWords, 'Is Array?', Array.isArray(topWords));
        
        if (!topWords || Object.keys(topWords).length === 0) {
            console.error('❌ No data to display in chart');
            // แสดงข้อความว่าไม่มีข้อมูล
            const parent = ctx.parentElement;
            parent.innerHTML = '<div class="flex items-center justify-center h-full"><p class="text-gray-500">ไม่มีข้อมูลแสดงกราฟ</p></div>';
            return;
        }

        if (this.wordFrequencyChart) {
            console.log('🔄 Destroying old chart');
            this.wordFrequencyChart.destroy();
        }
        
        // เรียงลำดับข้อมูลจากมากไปน้อย
        const sortedEntries = Object.entries(topWords).sort((a, b) => b[1] - a[1]);
        const words = sortedEntries.map(entry => entry[0]);
        const frequencies = sortedEntries.map(entry => entry[1]);
        
        console.log('✅ Words (sorted):', words);
        console.log('✅ Frequencies (sorted):', frequencies);
        
        // Create vibrant gradient colors for bars - สีสดใสและแตกต่างกันชัดเจน
        const colors = [
            '#FF6B6B', '#4ECDC4', '#FFD93D', '#6BCF7F', '#A8E6CF',
            '#FF8B94', '#95E1D3', '#FDCB6E', '#74B9FF', '#A29BFE',
            '#FD79A8', '#FDCB6E', '#55EFC4', '#81ECEC', '#FAB1A0'
        ];
        
        const backgroundColors = words.map((_, index) => colors[index % colors.length]);
        const borderColors = backgroundColors.map(color => color);
        
        this.wordFrequencyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: words,
                datasets: [{
                    label: 'ความถี่',
                    data: frequencies,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1,
                    borderRadius: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 800
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            font: { size: 12 },
                            color: '#6b7280'
                        },
                        grid: { color: '#e5e7eb' }
                    },
                    x: {
                        ticks: {
                            font: { size: 12, weight: '600' },
                            color: '#374151'
                        },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 },
                        padding: 10,
                        cornerRadius: 6,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'ความถี่: ' + context.parsed.y + ' ครั้ง';
                            }
                        }
                    }
                }
            }
        });
    }

    displayCategories(categorizedWords, topWordsByCategory) {
        const container = document.getElementById('categoriesContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (!categorizedWords || Object.keys(categorizedWords).length === 0) {
            container.innerHTML = '<p class="text-gray-500">ไม่พบหมวดหมู่</p>';
            return;
        }

        const colors = [
            { bg: 'bg-blue-50', text: 'text-blue-900', badge: 'bg-blue-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-green-50', text: 'text-green-900', badge: 'bg-green-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-purple-50', text: 'text-purple-900', badge: 'bg-purple-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-orange-50', text: 'text-orange-900', badge: 'bg-orange-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-pink-50', text: 'text-pink-900', badge: 'bg-pink-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-red-50', text: 'text-red-900', badge: 'bg-red-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-yellow-50', text: 'text-yellow-900', badge: 'bg-yellow-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-indigo-50', text: 'text-indigo-900', badge: 'bg-indigo-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-teal-50', text: 'text-teal-900', badge: 'bg-teal-600 text-white', icon: 'fa-folder' },
            { bg: 'bg-cyan-50', text: 'text-cyan-900', badge: 'bg-cyan-600 text-white', icon: 'fa-folder' },
        ];
        
        Object.keys(categorizedWords).forEach((category, index) => {
            const words = categorizedWords[category];
            const wordCount = Object.keys(words).length;
            const totalFreq = Object.values(words).reduce((a, b) => a + b, 0);
            const color = colors[index % colors.length];
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow';
            
            categoryDiv.innerHTML = `
                <button class="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between transition-colors category-button" data-category="${index}">
                    <div class="flex items-center gap-3">
                        <i class="fas ${color.icon} ${color.text}"></i>
                        <div class="text-left">
                            <h4 class="font-bold text-gray-900">${category}</h4>
                            <p class="text-sm text-gray-600">${wordCount} คำ • ความถี่รวม ${totalFreq}</p>
                        </div>
                    </div>
                    <i class="fas fa-chevron-down text-gray-400 transition-transform category-chevron"></i>
                </button>
                <div class="category-content hidden p-4 ${color.bg}">
                    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                        ${Object.entries(topWordsByCategory[category] || {}).map(([word, freq]) => `
                            <div class="flex items-center justify-between px-3 py-2 bg-white rounded border border-gray-200 text-sm">
                                <span class="font-medium text-gray-900">${word}</span>
                                <span class="ml-2 px-2 py-1 ${color.badge} rounded text-xs font-bold">${freq}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            
            // Add toggle functionality
            const button = categoryDiv.querySelector('.category-button');
            const content = categoryDiv.querySelector('.category-content');
            const chevron = categoryDiv.querySelector('.category-chevron');
            
            button.addEventListener('click', () => {
                content.classList.toggle('hidden');
                chevron.classList.toggle('rotate-180');
            });
            
            container.appendChild(categoryDiv);
        });
    }

    displayWordTable(wordFrequency, page = 1) {
        const allWords = Object.entries(wordFrequency).sort((a, b) => b[1] - a[1]);
        this.totalWords = allWords.length;
        this.currentPage = page;
        
        const totalPages = Math.ceil(this.totalWords / this.wordsPerPage);
        const startIndex = (this.currentPage - 1) * this.wordsPerPage;
        const endIndex = Math.min(startIndex + this.wordsPerPage, this.totalWords);
        const wordsToDisplay = allWords.slice(startIndex, endIndex);
        const maxFreq = allWords[0][1];
        
        // Update UI
        const wordCount = document.getElementById('wordCount');
        const currentPageDisplay = document.getElementById('currentPageDisplay');
        const totalPagesDisplay = document.getElementById('totalPages');
        
        if (wordCount) wordCount.textContent = this.totalWords.toLocaleString();
        if (currentPageDisplay) currentPageDisplay.textContent = this.currentPage;
        if (totalPagesDisplay) totalPagesDisplay.textContent = totalPages;
        
        // Display table
        const tbody = document.getElementById('wordTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        wordsToDisplay.forEach(([word, frequency], index) => {
            const actualRank = startIndex + index + 1;
            const percentage = (frequency / maxFreq * 100).toFixed(1);
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            
            // Medal icons for top 3
            let rankDisplay = actualRank;
            let rankClass = 'text-gray-700';
            if (actualRank === 1) {
                rankDisplay = '<i class="fas fa-trophy"></i>';
                rankClass = 'text-yellow-500';
            } else if (actualRank === 2) {
                rankDisplay = '<i class="fas fa-medal"></i>';
                rankClass = 'text-gray-400';
            } else if (actualRank === 3) {
                rankDisplay = '<i class="fas fa-award"></i>';
                rankClass = 'text-orange-500';
            }
            
            row.innerHTML = `
                <td class="px-4 py-3 text-center font-semibold ${rankClass}">
                    ${rankDisplay}
                </td>
                <td class="px-4 py-3">
                    <span class="font-medium text-gray-900">${word}</span>
                </td>
                <td class="px-4 py-3">
                    <span class="inline-block px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-bold">
                        ${frequency}
                    </span>
                </td>
                <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                        <div class="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                            <div class="bg-blue-600 h-full rounded-full transition-all" style="width: ${percentage}%"></div>
                        </div>
                        <span class="text-sm text-gray-600 font-medium w-12">${percentage}%</span>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Update pagination controls
        this.updatePaginationControls(totalPages);
    }

    updatePaginationControls(totalPages) {
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        const pageNumbers = document.getElementById('pageNumbers');
        
        if (!prevBtn || !nextBtn || !pageNumbers) return;
        
        // Enable/Disable buttons
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === totalPages;
        
        // Generate page numbers
        pageNumbers.innerHTML = '';
        
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(totalPages, this.currentPage + 2);
        
        if (endPage - startPage < 4) {
            if (startPage === 1) {
                endPage = Math.min(totalPages, startPage + 4);
            } else {
                startPage = Math.max(1, endPage - 4);
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.textContent = i;
            pageBtn.className = i === this.currentPage
                ? 'px-4 py-2 bg-blue-600 text-white rounded-lg font-medium'
                : 'px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors';
            pageBtn.onclick = () => this.displayWordTable(this.currentAnalysisData.word_frequency, i);
            pageNumbers.appendChild(pageBtn);
        }
    }

    exportResults() {
        if (!this.currentAnalysisData) {
            alert('ไม่มีข้อมูลให้ดาวน์โหลด กรุณาวิเคราะห์ข้อความก่อน');
            return;
        }

        try {
            let csv = '\ufeff'; // UTF-8 BOM
            
            // Header summary
            csv += '=== สรุปผลการวิเคราะห์ ===\n';
            csv += `วันที่วิเคราะห์,${new Date().toLocaleDateString('th-TH')}\n`;
            csv += `จำนวนคำทั้งหมด,${this.currentAnalysisData.total_words}\n`;
            csv += `จำนวนคำไม่ซ้ำ,${this.currentAnalysisData.unique_words}\n`;
            csv += `จำนวนหมวดหมู่,${Object.keys(this.currentAnalysisData.categorized_words || {}).length}\n`;
            csv += '\n';
            
            // Word frequency table
            csv += '=== รายการคำทั้งหมด ===\n';
            csv += 'อันดับ,คำ,ความถี่,สัดส่วน (%)\n';
            
            const sortedWords = Object.entries(this.currentAnalysisData.word_frequency)
                .sort((a, b) => b[1] - a[1]);
            
            const maxFreq = sortedWords[0][1];
            
            sortedWords.forEach(([word, freq], index) => {
                const percentage = ((freq / maxFreq) * 100).toFixed(2);
                csv += `${index + 1},"${word}",${freq},${percentage}\n`;
            });
            
            csv += '\n';
            
            // Categories
            if (this.currentAnalysisData.categorized_words) {
                csv += '=== คำแยกตามหมวดหมู่ ===\n';
                Object.entries(this.currentAnalysisData.categorized_words).forEach(([category, words]) => {
                    csv += `\n${category}\n`;
                    csv += 'คำ,ความถี่\n';
                    Object.entries(words)
                        .sort((a, b) => b[1] - a[1])
                        .forEach(([word, freq]) => {
                            csv += `"${word}",${freq}\n`;
                        });
                });
            }
            
            // Create and download file
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            link.download = `การวิเคราะห์คำ_${timestamp}.csv`;
            link.click();
            
            alert('ดาวน์โหลดไฟล์สำเร็จ! 🎉');
            
        } catch (error) {
            console.error('Export error:', error);
            alert('เกิดข้อผิดพลาดในการดาวน์โหลด: ' + error.message);
        }
    }

    resetAnalysis() {
        // Reset state
        this.currentAnalysisData = null;
        this.currentFiles = [];
        document.getElementById('fileInput').value = '';
        document.getElementById('textInput').value = '';
        document.getElementById('charCount').textContent = '0';
        
        // Reset file selection display
        const selectedFilesContainer = document.getElementById('selectedFilesContainer');
        const selectedFilesList = document.getElementById('selectedFilesList');
        const fileCount = document.getElementById('fileCount');
        if (selectedFilesContainer) selectedFilesContainer.classList.add('hidden');
        if (selectedFilesList) selectedFilesList.innerHTML = '';
        if (fileCount) fileCount.textContent = '0';
        
        // Reset pagination
        this.currentPage = 1;
        this.totalWords = 0;
        
        // Hide results and show input
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('inputSection').classList.remove('hidden');
        document.getElementById('progressContainer').classList.add('hidden');
        
        // Reset step indicator
        this.updateStepIndicator(1);
        
        // Destroy chart
        if (this.wordFrequencyChart) {
            this.wordFrequencyChart.destroy();
            this.wordFrequencyChart = null;
        }
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showProgress(message, percent) {
        document.getElementById('inputSection').classList.add('hidden');
        document.getElementById('progressContainer').classList.remove('hidden');
        this.updateProgress(percent, message);
    }

    updateProgress(percent, message) {
        const progressBar = document.getElementById('progressBar');
        const progressMessage = document.getElementById('progressMessage');
        const progressPercent = document.getElementById('progressPercent');
        
        if (progressBar) progressBar.style.width = percent + '%';
        if (progressMessage) progressMessage.textContent = message;
        if (progressPercent) progressPercent.textContent = percent;
    }

    hideProgress() {
        document.getElementById('progressContainer').classList.add('hidden');
    }
}

// Initialize the analyzer when the page loads
let analyzer;
document.addEventListener('DOMContentLoaded', function() {
    analyzer = new WordFrequencyAnalyzer();
    // ทำให้ analyzer ใช้งานได้จาก global scope (สำหรับ onclick ใน HTML)
    window.analyzer = analyzer;
});
