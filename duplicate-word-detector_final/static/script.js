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
        this.setupRecManagerEvents();
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
        let dragCounter = 0;

        uploadArea.addEventListener('click', (e) => {
            if (!e.target.closest('button')) fileInput.click();
        });

        uploadArea.addEventListener('dragenter', (e) => {
            e.preventDefault();
            dragCounter++;
            uploadArea.classList.add('border-blue-500', 'bg-blue-50', 'scale-[1.01]');
            uploadArea.querySelector('i.fa-cloud-upload-alt')?.classList.add('text-blue-500');
        });

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        uploadArea.addEventListener('dragleave', (e) => {
            dragCounter--;
            if (dragCounter === 0) {
                uploadArea.classList.remove('border-blue-500', 'bg-blue-50', 'scale-[1.01]');
                uploadArea.querySelector('i.fa-cloud-upload-alt')?.classList.remove('text-blue-500');
            }
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dragCounter = 0;
            uploadArea.classList.remove('border-blue-500', 'bg-blue-50', 'scale-[1.01]');
            uploadArea.querySelector('i.fa-cloud-upload-alt')?.classList.remove('text-blue-500');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload({ target: { files } });
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
                    formData.append('files', file);
                });
                
                this.updateProgress(30, 'กำลังแปลงไฟล์...');
                
                const response = await fetch('/api/upload-multiple', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // ตรวจสอบไฟล์ที่แปลงไม่สำเร็จ
                    const failedFiles = result.data.filter(item => !item.success);
                    const successFiles = result.data.filter(item => item.success);
                    
                    // รวมข้อความจากไฟล์ที่แปลงสำเร็จเท่านั้น
                    const uploadedTexts = successFiles.map(item => item.content || '').join('\n\n');
                    allTextContent += uploadedTexts;
                    
                    // เก็บข้อมูลไฟล์ (ใช้ไฟล์แรกที่สำเร็จ)
                    const firstFile = successFiles[0];
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
                        
                        if (failedFiles.length > 0) {
                            const failedNames = failedFiles.map(f => f.filename).join(', ');
                            console.warn(`ไฟล์ที่แปลงไม่สำเร็จ: ${failedNames}`);
                        }
                        
                        await this.analyzeTextContent(allTextContent, fileInfo);
                    } else {
                        // ไม่พบข้อความ - สร้าง error message ที่ละเอียด
                        let errorMsg = 'ไม่พบข้อความในไฟล์ที่อัปโหลด\n\n';
                        if (failedFiles.length > 0) {
                            errorMsg += 'ไฟล์ที่ไม่สามารถแปลงได้:\n';
                            failedFiles.forEach(f => {
                                errorMsg += `• ${f.filename}: ${f.error || 'ไม่ทราบสาเหตุ'}\n`;
                            });
                            errorMsg += '\nหมายเหตุ: ไฟล์ PDF ที่เป็นภาพ (Scanned PDF) จำเป็นต้องมีระบบ OCR ที่พร้อมใช้งาน';
                        }
                        throw new Error(errorMsg);
                    }
                } else {
                    throw new Error(result.error || 'ไม่สามารถแปลงไฟล์ได้');
                }
            } catch (error) {
                this.hideProgress();
                document.getElementById('inputSection').classList.remove('hidden');
                this.updateStepIndicator(1);
                const msg = error.message;
                setTimeout(() => alert('เกิดข้อผิดพลาด: ' + msg), 100);
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
                    this.currentAnalysisId = result.analysis_id;
                    this.displayResults(result.data);
                }, 500);
            } else {
                throw new Error(result.error || 'ไม่สามารถวิเคราะห์ได้');
            }
        } catch (error) {
            this.hideProgress();
            document.getElementById('inputSection').classList.remove('hidden');
            this.updateStepIndicator(1);
            const msg = error.message;
            setTimeout(() => alert('เกิดข้อผิดพลาดในการวิเคราะห์: ' + msg), 100);
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
                    this.currentAnalysisId = result.analysis_id;
                    this.displayResults(result.data);
                }, 500);
            } else {
                this.hideProgress();
                document.getElementById('inputSection').classList.remove('hidden');
                this.updateStepIndicator(1);
                const msg = result.error || 'ไม่สามารถวิเคราะห์ได้';
                setTimeout(() => alert('เกิดข้อผิดพลาด: ' + msg), 100);
            }
        } catch (error) {
            this.hideProgress();
            document.getElementById('inputSection').classList.remove('hidden');
            this.updateStepIndicator(1);
            const msg = error.message;
            setTimeout(() => alert('เกิดข้อผิดพลาด: ' + msg), 100);
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
        this.loadRecommendations(this.currentAnalysisId);
        this.loadTrendData();
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
        
        // Reset recommendation shortcut button
        const jumpBtn = document.getElementById('jumpToRecBtn');
        if (jumpBtn) jumpBtn.classList.add('hidden');
        
        // Reset recommendation panel highlight
        const panel = document.getElementById('recommendationPanel');
        if (panel) panel.classList.remove('ring-2', 'ring-indigo-400', 'ring-offset-2');
        
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
    
    async loadRecommendations(analysisId) {
        const container = document.getElementById('recommendationContainer');
        const badge = document.getElementById('matchedCategoryBadge');
        const badgeName = document.getElementById('matchedCategoryName');

        if (!this.currentAnalysisData || !this.currentAnalysisData.category_summary) {
            container.innerHTML = '<p class="text-gray-500">ไม่พบข้อมูลหมวดหมู่</p>';
            return;
        }

        const categorySummary = this.currentAnalysisData.category_summary;
        if (!categorySummary || categorySummary.length === 0) {
            container.innerHTML = '<p class="text-gray-500">ไม่พบข้อมูลหมวดหมู่จากการวิเคราะห์</p>';
            return;
        }

        try {
            container.innerHTML = '<div class="flex items-center justify-center py-8"><div class="animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-indigo-600"></div><span class="ml-3 text-gray-500">กำลังค้นหาเอกสารที่เกี่ยวข้อง...</span></div>';

            const response = await fetch('/api/recommendations/match', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    category_summary: categorySummary
                })
            });

            const result = await response.json();
            console.log("RECOMMENDATION MATCH RESPONSE:", result);

            if (result.matched_category) {
                badge.classList.remove('hidden');
                badgeName.textContent = result.matched_category;
            } else {
                badge.classList.add('hidden');
            }

            if (result.data && result.data.length > 0) {
                const topCatInfo = result.top_category_info;
                container.innerHTML = `
                    ${topCatInfo ? `
                        <div class="mb-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                            <p class="text-sm text-indigo-900">
                                <i class="fas fa-chart-pie mr-1"></i>
                                หมวดหมู่ <strong>"${result.matched_category}"</strong>
                                มีคำที่พบ ${topCatInfo.unique_words} คำ (ความถี่รวม ${topCatInfo.total_frequency})
                                — แสดงเอกสารที่เกี่ยวข้องจากหมวดหมู่นี้
                            </p>
                        </div>
                    ` : ''}
                    <div class="space-y-3">
                        ${result.data.map(rec => `
                            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-indigo-300 transition-all cursor-pointer rec-card" data-rec-id="${rec.id}">
                                <div class="flex items-start justify-between gap-3">
                                    <div class="flex items-start gap-3 flex-1 min-w-0">
                                        <div class="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${rec.pdf_stored_name ? 'bg-red-50' : 'bg-gray-100'}">
                                            <i class="fas ${rec.pdf_stored_name ? 'fa-file-pdf text-red-500' : 'fa-file-alt text-gray-400'} text-lg"></i>
                                        </div>
                                        <div class="flex-1 min-w-0">
                                            <h4 class="font-semibold text-gray-900 truncate">${rec.title}</h4>
                                            <div class="flex items-center gap-2 mt-1 flex-wrap">
                                                <span class="inline-flex items-center px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded text-xs font-medium">
                                                    <i class="fas fa-tag mr-1"></i>${rec.category}
                                                </span>
                                                ${rec.pdf_filename ? `<span class="text-xs text-gray-500"><i class="fas fa-paperclip mr-1"></i>${rec.pdf_filename}</span>` : ''}
                                            </div>
                                            ${rec.description ? `<p class="text-sm text-gray-600 mt-1 line-clamp-2">${rec.description}</p>` : ''}
                                        </div>
                                    </div>
                                    <button class="flex-shrink-0 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-lg text-sm font-medium transition-colors" onclick="event.stopPropagation(); analyzer.viewRecDetail(${rec.id})">
                                        <i class="fas fa-eye mr-1"></i>ดู
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <p class="text-xs text-gray-400 mt-3 text-center">พบ ${result.data.length} เอกสารในหมวดหมู่ "${result.matched_category}"</p>
                `;

                container.querySelectorAll('.rec-card').forEach(card => {
                    card.addEventListener('click', () => {
                        const recId = card.dataset.recId;
                        this.viewRecDetail(parseInt(recId));
                    });
                });

                // แสดงปุ่ม shortcut ที่ results header
                const jumpBtn = document.getElementById('jumpToRecBtn');
                const jumpLabel = document.getElementById('jumpToRecLabel');
                if (jumpBtn) {
                    jumpBtn.classList.remove('hidden');
                    if (jumpLabel) jumpLabel.textContent = `ดูเอกสาร (${result.data.length})`;
                    setTimeout(() => jumpBtn.classList.remove('animate-pulse'), 3000);
                }

                // Highlight recommendation panel แล้ว scroll ไป
                const panel = document.getElementById('recommendationPanel');
                if (panel) {
                    panel.classList.add('ring-2', 'ring-indigo-400', 'ring-offset-2');
                    setTimeout(() => {
                        panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        setTimeout(() => panel.classList.remove('ring-2', 'ring-indigo-400', 'ring-offset-2'), 3000);
                    }, 1800);
                }
            } else {
                const sorted = [...categorySummary]
                    .filter(c => c.category !== 'อื่นๆ')
                    .sort((a, b) => b.total_frequency - a.total_frequency);
                const topCats = sorted.slice(0, 3).map(c => `"${c.category}" (${c.total_frequency})`).join(', ');

                // ซ่อนปุ่ม shortcut
                const jumpBtn = document.getElementById('jumpToRecBtn');
                if (jumpBtn) jumpBtn.classList.add('hidden');

                container.innerHTML = `
                    <div class="text-center py-8">
                        <i class="fas fa-inbox text-4xl text-gray-300 mb-3"></i>
                        <p class="text-gray-500">ไม่พบเอกสารในหมวดหมู่ "${result.matched_category || '-'}"</p>
                        <p class="text-sm text-gray-400 mt-1">หมวดหมู่ที่พบมากที่สุด: ${topCats}</p>
                        <p class="text-sm text-gray-400 mt-1">กรุณาเพิ่มเอกสารในฐานข้อมูล Recommendation เพื่อให้ระบบแนะนำได้</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Recommendation match error:', error);
            container.innerHTML = '<p class="text-red-500">เกิดข้อผิดพลาดในการค้นหาเอกสาร</p>';
        }
    }

    // ============ Recommendation Manager Functions ============

    setupRecManagerEvents() {
        const openBtn = document.getElementById('openRecManagerBtn');
        const modal = document.getElementById('recManagerModal');
        const closeBtn = document.getElementById('closeRecManager');
        const form = document.getElementById('addRecForm');
        const resetBtn = document.getElementById('resetRecDbBtn');

        if (openBtn) {
            openBtn.addEventListener('click', () => this.openRecManager());
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) modal.classList.add('hidden');
            });
        }

        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addRecommendation();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetRecDb());
        }

        // PDF viewer
        const pdfModal = document.getElementById('pdfViewerModal');
        const closePdf = document.getElementById('closePdfViewer');

        if (closePdf) {
            closePdf.addEventListener('click', () => pdfModal.classList.add('hidden'));
        }

        if (pdfModal) {
            pdfModal.addEventListener('click', (e) => {
                if (e.target === pdfModal) pdfModal.classList.add('hidden');
            });
        }
    }

    openRecManager() {
        document.getElementById('recManagerModal').classList.remove('hidden');
        this.loadRecList();
    }

    async loadRecList() {
        const container = document.getElementById('recListContainer');
        const countEl = document.getElementById('recTotalCount');

        try {
            const response = await fetch('/api/recommendations');
            const result = await response.json();

            if (!result.success) {
                container.innerHTML = '<p class="text-red-500 text-center py-4">โหลดข้อมูลไม่สำเร็จ</p>';
                return;
            }

            const recs = result.data;
            countEl.textContent = recs.length;

            if (recs.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-center py-8">ยังไม่มีข้อมูล กรุณาเพิ่มวาระการประชุม</p>';
                return;
            }

            container.innerHTML = recs.map(rec => {
                const date = rec.created_at ? new Date(rec.created_at).toLocaleDateString('th-TH', { year: 'numeric', month: 'short', day: 'numeric' }) : '-';
                const size = rec.pdf_size ? `${(rec.pdf_size / (1024 * 1024)).toFixed(2)} MB` : '';
                return `
                    <div class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        <div class="flex items-center gap-3 flex-1 min-w-0">
                            <div class="w-9 h-9 rounded-lg flex items-center justify-center ${rec.pdf_stored_name ? 'bg-red-50' : 'bg-gray-100'} flex-shrink-0">
                                <i class="fas ${rec.pdf_stored_name ? 'fa-file-pdf text-red-500' : 'fa-file text-gray-400'}"></i>
                            </div>
                            <div class="flex-1 min-w-0">
                                <p class="font-medium text-gray-900 text-sm truncate">${rec.title}</p>
                                <div class="flex items-center gap-2 text-xs text-gray-500">
                                    <span class="px-1.5 py-0.5 bg-indigo-50 text-indigo-700 rounded font-medium">${rec.category}</span>
                                    <span>${date}</span>
                                    ${size ? `<span>${size}</span>` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center gap-1 flex-shrink-0">
                            <button onclick="analyzer.openEditRec(${rec.id})" class="p-2 text-amber-600 hover:bg-amber-50 rounded-lg transition-colors" title="แก้ไข">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${rec.pdf_stored_name ? `
                                <button onclick="analyzer.viewRecDetail(${rec.id})" class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="ดูเอกสาร">
                                    <i class="fas fa-eye"></i>
                                </button>
                            ` : ''}
                            <button onclick="analyzer.deleteRec(${rec.id})" class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="ลบ">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Load rec list error:', error);
            container.innerHTML = '<p class="text-red-500 text-center py-4">เกิดข้อผิดพลาด</p>';
        }
    }

    async addRecommendation() {
        const title = document.getElementById('recTitle').value.trim();
        const category = document.getElementById('recCategory').value;
        const description = document.getElementById('recDescription').value.trim();
        const pdfFile = document.getElementById('recPdfFile').files[0];

        if (!title || !category) {
            alert('กรุณากรอกชื่อวาระและเลือกหมวดหมู่');
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('category', category);
        formData.append('description', description);
        if (pdfFile) {
            formData.append('pdf_file', pdfFile);
        }

        try {
            const response = await fetch('/api/recommendation', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                document.getElementById('addRecForm').reset();
                this.loadRecList();
                alert('บันทึกสำเร็จ!');
            } else {
                alert('เกิดข้อผิดพลาด: ' + (result.error || 'ไม่สามารถบันทึกได้'));
            }
        } catch (error) {
            console.error('Add rec error:', error);
            alert('เกิดข้อผิดพลาดในการบันทึก');
        }
    }

    async deleteRec(recId) {
        if (!confirm('ต้องการลบวาระนี้ใช่หรือไม่?')) return;

        try {
            const response = await fetch(`/api/recommendation/${recId}`, { method: 'DELETE' });
            const result = await response.json();

            if (result.success) {
                this.loadRecList();
            } else {
                alert('ไม่สามารถลบได้: ' + (result.error || ''));
            }
        } catch (error) {
            console.error('Delete rec error:', error);
        }
    }

    async openEditRec(recId) {
        try {
            const response = await fetch(`/api/recommendation/${recId}`);
            const result = await response.json();
            if (!result.success) {
                alert('ไม่พบข้อมูล');
                return;
            }
            const rec = result.data;

            let modal = document.getElementById('editRecModal');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'editRecModal';
                modal.className = 'hidden fixed inset-0 bg-black bg-opacity-50 z-[60] flex items-center justify-center p-4';
                modal.style.backdropFilter = 'blur(4px)';
                modal.innerHTML = `
                    <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
                        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
                            <h3 class="text-lg font-bold text-gray-900 flex items-center gap-2">
                                <i class="fas fa-edit text-amber-600"></i>
                                แก้ไขวาระการประชุม
                            </h3>
                            <button onclick="document.getElementById('editRecModal').classList.add('hidden')" class="text-gray-400 hover:text-gray-600">
                                <i class="fas fa-times text-xl"></i>
                            </button>
                        </div>
                        <div class="p-6">
                            <form id="editRecForm" class="space-y-4">
                                <input type="hidden" id="editRecId">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">ชื่อวาระ <span class="text-red-500">*</span></label>
                                    <input type="text" id="editRecTitle" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">หมวดหมู่ <span class="text-red-500">*</span></label>
                                    <select id="editRecCategory" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500">
                                        <option value="">-- เลือกหมวดหมู่ --</option>
                                        <option value="การศึกษา">การศึกษา</option>
                                        <option value="เศรษฐกิจ">เศรษฐกิจ</option>
                                        <option value="การเมือง">การเมือง</option>
                                        <option value="สังคม">สังคม</option>
                                        <option value="สาธารณสุข">สาธารณสุข</option>
                                        <option value="เกษตรกรรม">เกษตรกรรม</option>
                                        <option value="กฎหมาย">กฎหมาย</option>
                                        <option value="คมนาคม">คมนาคม</option>
                                        <option value="พลังงาน">พลังงาน</option>
                                        <option value="สื่อสารและเทคโนโลยี">สื่อสารและเทคโนโลยี</option>
                                        <option value="สิ่งแวดล้อม">สิ่งแวดล้อม</option>
                                        <option value="การต่างประเทศ">การต่างประเทศ</option>
                                        <option value="ท่องเที่ยว">ท่องเที่ยว</option>
                                        <option value="กีฬา">กีฬา</option>
                                        <option value="แรงงาน">แรงงาน</option>
                                        <option value="มหาดไทย">มหาดไทย</option>
                                        <option value="การเงิน/งบประมาณ">การเงิน/งบประมาณ</option>
                                        <option value="โครงการ/แผนงาน">โครงการ/แผนงาน</option>
                                        <option value="เทคโนโลยี/ระบบ/ข้อมูล">เทคโนโลยี/ระบบ/ข้อมูล</option>
                                        <option value="นโยบาย/กฎระเบียบ/กฎหมาย">นโยบาย/กฎระเบียบ/กฎหมาย</option>
                                        <option value="สถานที่/โครงสร้างพื้นฐาน">สถานที่/โครงสร้างพื้นฐาน</option>
                                        <option value="วิจัย/นวัตกรรม">วิจัย/นวัตกรรม</option>
                                        <option value="ความร่วมมือ/ภายนอก">ความร่วมมือ/ภายนอก</option>
                                        <option value="ปัญหา/ความเสี่ยง/การแก้ไข">ปัญหา/ความเสี่ยง/การแก้ไข</option>
                                        <option value="อื่นๆ">อื่นๆ</option>
                                    </select>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">รายละเอียด</label>
                                    <textarea id="editRecDescription" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500" placeholder="คำอธิบายเพิ่มเติม"></textarea>
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700 mb-1">เปลี่ยนไฟล์ PDF (ไม่บังคับ)</label>
                                    <p id="editRecCurrentFile" class="text-xs text-gray-500 mb-1"></p>
                                    <input type="file" id="editRecPdfFile" accept=".pdf" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-amber-50 file:text-amber-700 hover:file:bg-amber-100">
                                </div>
                                <div class="flex gap-3 justify-end pt-2">
                                    <button type="button" onclick="document.getElementById('editRecModal').classList.add('hidden')" class="px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors">ยกเลิก</button>
                                    <button type="submit" class="px-5 py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2">
                                        <i class="fas fa-save"></i> บันทึก
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);

                modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.add('hidden'); });
                document.getElementById('editRecForm').addEventListener('submit', (e) => { e.preventDefault(); analyzer.saveEditRec(); });
            }

            document.getElementById('editRecId').value = rec.id;
            document.getElementById('editRecTitle').value = rec.title || '';
            document.getElementById('editRecCategory').value = rec.category || '';
            document.getElementById('editRecDescription').value = rec.description || '';
            document.getElementById('editRecPdfFile').value = '';
            document.getElementById('editRecCurrentFile').textContent = rec.pdf_filename ? `ไฟล์ปัจจุบัน: ${rec.pdf_filename}` : 'ยังไม่มีไฟล์ PDF';

            modal.classList.remove('hidden');
        } catch (error) {
            console.error('Open edit rec error:', error);
            alert('เกิดข้อผิดพลาดในการโหลดข้อมูล');
        }
    }

    async saveEditRec() {
        const recId = document.getElementById('editRecId').value;
        const title = document.getElementById('editRecTitle').value.trim();
        const category = document.getElementById('editRecCategory').value;
        const description = document.getElementById('editRecDescription').value.trim();
        const pdfFile = document.getElementById('editRecPdfFile').files[0];

        if (!title || !category) {
            alert('กรุณากรอกชื่อวาระและเลือกหมวดหมู่');
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('category', category);
        formData.append('description', description);
        if (pdfFile) {
            formData.append('pdf_file', pdfFile);
        }

        try {
            const response = await fetch(`/api/recommendation/${recId}`, {
                method: 'PUT',
                body: formData
            });
            const result = await response.json();

            if (result.success) {
                document.getElementById('editRecModal').classList.add('hidden');
                this.loadRecList();
                alert('อัปเดตสำเร็จ!');
            } else {
                alert('เกิดข้อผิดพลาด: ' + (result.error || 'ไม่สามารถอัปเดตได้'));
            }
        } catch (error) {
            console.error('Save edit rec error:', error);
            alert('เกิดข้อผิดพลาดในการบันทึก');
        }
    }

    async resetRecDb() {
        if (!confirm('⚠️ ต้องการรีเซ็ตฐานข้อมูล Recommendation ทั้งหมดใช่หรือไม่?\n\nข้อมูลและไฟล์ PDF ทั้งหมดจะถูกลบ!')) return;

        try {
            const response = await fetch('/api/recommendations/reset', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.loadRecList();
                alert('รีเซ็ตฐานข้อมูล Recommendation สำเร็จ');
            } else {
                alert('เกิดข้อผิดพลาด: ' + (result.error || ''));
            }
        } catch (error) {
            console.error('Reset rec error:', error);
        }
    }

    async viewRecDetail(recId) {
        const modal = document.getElementById('pdfViewerModal');
        const titleEl = document.getElementById('pdfViewerTitle');
        const metaEl = document.getElementById('pdfViewerMeta');
        const contentEl = document.getElementById('pdfViewerContent');
        const downloadLink = document.getElementById('pdfDownloadLink');

        modal.classList.remove('hidden');
        contentEl.innerHTML = '<div class="flex items-center justify-center h-full"><div class="animate-spin rounded-full h-10 w-10 border-2 border-gray-200 border-t-indigo-600"></div></div>';

        try {
            const response = await fetch(`/api/recommendation/${recId}`);
            const result = await response.json();

            if (!result.success) {
                contentEl.innerHTML = '<p class="text-red-500 text-center">ไม่พบข้อมูล</p>';
                return;
            }

            const rec = result.data;
            titleEl.textContent = rec.title;

            const date = rec.created_at ? new Date(rec.created_at).toLocaleDateString('th-TH', { year: 'numeric', month: 'long', day: 'numeric' }) : '-';
            metaEl.textContent = `หมวดหมู่: ${rec.category} | วันที่: ${date}`;

            if (rec.pdf_stored_name) {
                const pdfUrl = `/uploads/recommendations/${rec.pdf_stored_name}`;
                downloadLink.href = pdfUrl;
                downloadLink.classList.remove('hidden');
                downloadLink.style.display = 'flex';

                contentEl.innerHTML = `
                    <div class="w-full h-full flex flex-col">
                        <div class="bg-gray-50 rounded-lg p-4 mb-3">
                            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                <div><span class="text-gray-500">ชื่อวาระ:</span><br><strong>${rec.title}</strong></div>
                                <div><span class="text-gray-500">หมวดหมู่:</span><br><span class="inline-flex px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded text-xs font-medium">${rec.category}</span></div>
                                <div><span class="text-gray-500">ไฟล์:</span><br><strong>${rec.pdf_filename || '-'}</strong></div>
                                <div><span class="text-gray-500">ขนาด:</span><br><strong>${rec.pdf_size ? (rec.pdf_size / (1024*1024)).toFixed(2) + ' MB' : '-'}</strong></div>
                            </div>
                            ${rec.description ? `<div class="mt-3 pt-3 border-t border-gray-200"><span class="text-gray-500 text-sm">รายละเอียด:</span><p class="text-gray-900 mt-1">${rec.description}</p></div>` : ''}
                        </div>
                        <iframe src="${pdfUrl}" class="flex-1 w-full rounded-lg border border-gray-200" style="min-height: 500px;" title="PDF Viewer"></iframe>
                    </div>
                `;
            } else {
                downloadLink.classList.add('hidden');
                contentEl.innerHTML = `
                    <div class="bg-gray-50 rounded-lg p-6">
                        <div class="grid grid-cols-2 gap-4 text-sm mb-4">
                            <div><span class="text-gray-500">ชื่อวาระ:</span><br><strong class="text-lg">${rec.title}</strong></div>
                            <div><span class="text-gray-500">หมวดหมู่:</span><br><span class="inline-flex px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded font-medium">${rec.category}</span></div>
                        </div>
                        ${rec.description ? `<div class="mt-3 pt-3 border-t border-gray-200"><span class="text-gray-500">รายละเอียด:</span><p class="text-gray-900 mt-2">${rec.description}</p></div>` : ''}
                        <div class="mt-4 text-center text-gray-400"><i class="fas fa-file-circle-xmark text-3xl mb-2"></i><p>ไม่มีไฟล์ PDF แนบ</p></div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('View rec detail error:', error);
            contentEl.innerHTML = '<p class="text-red-500 text-center">เกิดข้อผิดพลาดในการโหลดข้อมูล</p>';
        }
    }

    async loadTrendData() {
    try {
        const response = await fetch('/api/trend/category');
        const result = await response.json();
        console.log("TREND RESPONSE:", result);

        if (!result.trend) return;

        const ctx = document.getElementById('trendChart');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: result.trend.map(item => item.date),
                datasets: [{
                    label: 'จำนวนการวิเคราะห์',
                    data: result.trend.map(item => item.count),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59,130,246,0.1)',
                    fill: true,
                    tension: 0.3
                }]
            }
        });

    } catch (error) {
        console.error(error);
    }
    }
}

// Initialize the analyzer when the page loads
let analyzer;
document.addEventListener('DOMContentLoaded', function() {
    analyzer = new WordFrequencyAnalyzer();
    // ทำให้ analyzer ใช้งานได้จาก global scope (สำหรับ onclick ใน HTML)
    window.analyzer = analyzer;
});
