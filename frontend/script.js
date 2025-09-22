// SmartDoc AI - Working Version
console.log("🚀 SmartDoc AI Loading...");

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM Ready - Initializing SmartDoc AI...");
    
    // Configuration
    const API_URL = 'http://localhost:5001/api';
    let uploadedFiles = [];
    let lastReport = null;
    
    // Get all elements
    const elements = {
        startBtn: document.getElementById('startAnalysisBtn'),
        uploadBtn: document.getElementById('uploadFilesBtn'),
        uploadZone: document.getElementById('uploadZone'),
        fileInput: document.getElementById('fileInput'),
        filesList: document.getElementById('filesList'),
        resultsSection: document.getElementById('resultsSection'),
        loadingOverlay: document.getElementById('loadingOverlay'),
        toastContainer: document.getElementById('toastContainer'),
        totalDocs: document.getElementById('totalDocs'),
        totalIssues: document.getElementById('totalIssues'),
        totalContradictions: document.getElementById('totalContradictions'),
        avgSeverity: document.getElementById('avgSeverity'),
        analysisTime: document.getElementById('analysisTime'),
        contradictionsContainer: document.getElementById('contradictionsContainer'),
        exportBtn: document.getElementById('exportBtn'),
        newAnalysisBtn: document.getElementById('newAnalysisBtn')
    };
    
    // Log element availability
    console.log("📋 Elements Check:", {
        startBtn: !!elements.startBtn,
        uploadBtn: !!elements.uploadBtn,
        uploadZone: !!elements.uploadZone,
        fileInput: !!elements.fileInput
    });
    
    // Initialize Event Listeners
    initializeEventListeners();
    checkBackendConnection();
    
    function initializeEventListeners() {
        console.log("🔧 Setting up event listeners...");
        
        // Start Analysis Button
        if (elements.startBtn) {
            elements.startBtn.addEventListener('click', function() {
                console.log('🚀 Start Analysis clicked!');
                startAnalysis();
            });
        }
        
        // Upload Button
        if (elements.uploadBtn) {
            elements.uploadBtn.addEventListener('click', function() {
                console.log('📁 Upload button clicked!');
                if (elements.fileInput) elements.fileInput.click();
            });
        }
        
        // Upload Zone
        if (elements.uploadZone) {
            elements.uploadZone.addEventListener('click', function() {
                console.log('📂 Upload zone clicked!');
                if (elements.fileInput) elements.fileInput.click();
            });
            
            // Drag and drop
            elements.uploadZone.addEventListener('dragover', handleDragOver);
            elements.uploadZone.addEventListener('dragleave', handleDragLeave);
            elements.uploadZone.addEventListener('drop', handleDrop);
        }
        
        // File Input
        if (elements.fileInput) {
            elements.fileInput.addEventListener('change', function(e) {
                console.log('📄 Files selected:', e.target.files.length);
                handleFiles(Array.from(e.target.files));
            });
        }
        
        // Export Button
        if (elements.exportBtn) {
            elements.exportBtn.addEventListener('click', function() {
                console.log('💾 Export clicked!');
                exportReport();
            });
        }
        
        // New Analysis Button
        if (elements.newAnalysisBtn) {
            elements.newAnalysisBtn.addEventListener('click', function() {
                console.log('🔄 New Analysis clicked!');
                newAnalysis();
            });
        }
        
        console.log("✅ Event listeners initialized!");
    }
    
    function handleDragOver(e) {
        e.preventDefault();
        elements.uploadZone.classList.add('dragover');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        elements.uploadZone.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        e.preventDefault();
        elements.uploadZone.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    }
    
    function handleFiles(files) {
        console.log('🔍 Processing files:', files.length);
        
        const validFiles = files.filter(file => {
            return file.name.match(/\.(pdf|docx|txt)$/i);
        });
        
        if (validFiles.length === 0) {
            showToast('❌ Please select valid files (PDF, DOCX, TXT)', 'error');
            return;
        }
        
        validFiles.forEach(file => {
            uploadedFiles.push({
                id: Date.now() + Math.random(),
                name: file.name,
                size: file.size,
                file: file
            });
        });
        
        updateFilesList();
        updateStats();
        showToast(`✅ Added ${validFiles.length} files successfully!`, 'success');
        
        console.log('📋 Total files:', uploadedFiles.length);
    }
    
    function updateFilesList() {
        if (!elements.filesList) return;
        
        if (uploadedFiles.length === 0) {
            elements.filesList.innerHTML = '';
            return;
        }
        
        elements.filesList.innerHTML = uploadedFiles.map(file => `
            <div class="file-item">
                <div class="file-info">
                    <div class="file-icon">
                        <i class="fas fa-file-${getFileIcon(file.name)}"></i>
                    </div>
                    <div class="file-details">
                        <h5>${file.name}</h5>
                        <small>${formatFileSize(file.size)}</small>
                    </div>
                </div>
                <button class="file-remove" onclick="removeFile('${file.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
    }
    
    // Make removeFile global so onclick can access it
    window.removeFile = function(fileId) {
        console.log('🗑️ Removing file:', fileId);
        uploadedFiles = uploadedFiles.filter(file => file.id != fileId);
        updateFilesList();
        updateStats();
        showToast('🗑️ File removed successfully!', 'success');
    };
    
    function getFileIcon(filename) {
        if (filename.toLowerCase().endsWith('.pdf')) return 'pdf';
        if (filename.toLowerCase().endsWith('.docx')) return 'word';
        return 'alt';
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function updateStats() {
        if (elements.totalDocs) {
            elements.totalDocs.textContent = uploadedFiles.length;
        }
    }
    
    async function startAnalysis() {
        console.log('🔍 Starting analysis...');
        
        if (uploadedFiles.length < 2) {
            showToast('❌ Please upload at least 2 documents for comparison', 'error');
            return;
        }
        
        showLoading('AI Analysis in Progress', 'Scanning documents for contradictions...');
        
        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: 'session_' + Date.now(),
                    files: uploadedFiles.map(f => f.name)
                })
            });
            
            const result = await response.json();
            console.log('📊 Analysis result:', result);
            
            if (response.ok) {
                lastReport = result.report;
                displayResults(result.report);
                showToast('✅ Analysis completed successfully!', 'success');
            } else {
                throw new Error(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('❌ Analysis error:', error);
            showToast(`❌ Analysis failed: ${error.message}`, 'error');
        } finally {
            hideLoading();
        }
    }
    
    function displayResults(report) {
        console.log('📋 Displaying results:', report);
        
        // Update summary cards
        if (elements.totalContradictions) {
            elements.totalContradictions.textContent = report.total_contradictions || 0;
        }
        if (elements.totalIssues) {
            elements.totalIssues.textContent = report.total_contradictions || 0;
        }
        if (elements.analysisTime) {
            elements.analysisTime.textContent = `${report.analysis_time_seconds || 2.3}s`;
        }
        
        // Calculate average severity
        const avgSev = report.contradictions && report.contradictions.length > 0 
            ? Math.round(report.contradictions.reduce((sum, c) => sum + (c.severity_score || 0), 0) / report.contradictions.length * 100)
            : 0;
        
        if (elements.avgSeverity) {
            elements.avgSeverity.textContent = `${avgSev}%`;
        }
        
        // Display contradictions
        if (elements.contradictionsContainer) {
            if (!report.contradictions || report.contradictions.length === 0) {
                elements.contradictionsContainer.innerHTML = `
                    <div style="text-align: center; padding: 50px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 20px; color: #10b981;">
                        <div style="font-size: 4rem; margin-bottom: 20px;">✅</div>
                        <h3 style="font-size: 1.8rem; margin-bottom: 15px; color: #10b981;">Perfect Alignment!</h3>
                        <p style="font-size: 1.1rem; color: #94a3b8;">All documents are consistent with each other. No contradictions detected.</p>
                    </div>
                `;
            } else {
                elements.contradictionsContainer.innerHTML = report.contradictions.map((contradiction, index) => `
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 30px; margin-bottom: 25px; transition: all 0.3s ease;" 
                         onmouseover="this.style.background='rgba(255, 255, 255, 0.08)'; this.style.transform='translateY(-3px)'"
                         onmouseout="this.style.background='rgba(255, 255, 255, 0.05)'; this.style.transform='translateY(0)'">
                        
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                            <h4 style="color: #ef4444; font-size: 1.3rem; font-weight: 700;">
                                🔍 ${(contradiction.type || 'CONFLICT').toUpperCase()} Conflict
                            </h4>
                            <div style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem; font-weight: 600;">
                                ${Math.round((contradiction.severity_score || 0.5) * 100)}% Severity
                            </div>
                        </div>
                        
                        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 15px; padding: 20px; margin-bottom: 25px;">
                            <h5 style="color: #ef4444; margin-bottom: 10px; font-size: 1.1rem;">⚠️ Issue Detected</h5>
                            <p style="color: #f8fafc; font-size: 1rem; line-height: 1.6;">${contradiction.description || 'Contradiction found between documents'}</p>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 20px; align-items: center; margin-bottom: 25px;">
                            <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 15px; padding: 20px;">
                                <h5 style="color: #0ea5e9; margin-bottom: 12px; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
                                    <i class="fas fa-file-alt"></i> ${contradiction.document1 || 'Document 1'}
                                </h5>
                                <p style="color: #e2e8f0; font-style: italic; line-height: 1.5;">"${contradiction.sentence1 || 'No content available'}"</p>
                            </div>
                            
                            <div style="background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 12px 18px; border-radius: 50%; font-weight: 800; text-align: center; font-size: 0.9rem; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);">
                                VS
                            </div>
                            
                            <div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 15px; padding: 20px;">
                                <h5 style="color: #0ea5e9; margin-bottom: 12px; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
                                    <i class="fas fa-file-alt"></i> ${contradiction.document2 || 'Document 2'}
                                </h5>
                                <p style="color: #e2e8f0; font-style: italic; line-height: 1.5;">"${contradiction.sentence2 || 'No content available'}"</p>
                            </div>
                        </div>
                        
                        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 15px; padding: 20px;">
                            <h5 style="color: #10b981; margin-bottom: 12px; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-lightbulb"></i> Recommended Solution
                            </h5>
                            <p style="color: #f8fafc; line-height: 1.6;">${contradiction.suggestion || 'Review and align the conflicting information between documents'}</p>
                        </div>
                    </div>
                `).join('');
            }
        }
        
        // Show results section
        if (elements.resultsSection) {
            elements.resultsSection.style.display = 'block';
            elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    function exportReport() {
        if (!lastReport) {
            showToast('❌ No report available to export', 'error');
            return;
        }
        
        // Create a beautiful HTML report
        const htmlReport = generateHTMLReport(lastReport);
        
        // Create and download the file
        const blob = new Blob([htmlReport], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `smartdoc_report_${Date.now()}.html`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showToast('📄 Report exported successfully!', 'success');
    }
    
    function generateHTMLReport(report) {
        return `
        <!DOCTYPE html>
        <html>
        <head>
            <title>SmartDoc AI - Analysis Report</title>
            <style>
                body { font-family: Inter, sans-serif; background: #0f172a; color: white; margin: 0; padding: 40px; }
                .header { text-align: center; margin-bottom: 40px; padding: 40px; background: linear-gradient(135deg, #6366f1, #0ea5e9); border-radius: 20px; }
                .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }
                .card { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; }
                .contradiction { background: rgba(255,255,255,0.05); padding: 30px; margin: 20px 0; border-radius: 15px; border-left: 5px solid #ef4444; }
                .vs { background: #ef4444; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>SmartDoc AI Analysis Report</h1>
                <p>Generated on ${new Date().toLocaleString()}</p>
            </div>
            
            <div class="summary">
                <div class="card">
                    <h2>${report.total_contradictions || 0}</h2>
                    <p>Total Contradictions</p>
                </div>
                <div class="card">
                    <h2>${uploadedFiles.length}</h2>
                    <p>Documents Analyzed</p>
                </div>
                <div class="card">
                    <h2>${report.analysis_time_seconds || 2.3}s</h2>
                    <p>Processing Time</p>
                </div>
            </div>
            
            ${(report.contradictions || []).map(c => `
                <div class="contradiction">
                    <h3>${(c.type || 'CONFLICT').toUpperCase()} - ${Math.round((c.severity_score || 0.5) * 100)}% Severity</h3>
                    <p><strong>${c.description || 'Contradiction detected'}</strong></p>
                    <p><strong>Document 1:</strong> "${c.sentence1 || 'N/A'}"</p>
                    <span class="vs">VS</span>
                    <p><strong>Document 2:</strong> "${c.sentence2 || 'N/A'}"</p>
                    <p><strong>Recommendation:</strong> ${c.suggestion || 'Review and align the information'}</p>
                </div>
            `).join('')}
            
            <footer style="text-align: center; margin-top: 40px; color: #94a3b8;">
                <p>Generated by SmartDoc AI - Enterprise Document Intelligence Platform</p>
            </footer>
        </body>
        </html>`;
    }
    
    function newAnalysis() {
        uploadedFiles = [];
        lastReport = null;
        updateFilesList();
        updateStats();
        
        if (elements.resultsSection) {
            elements.resultsSection.style.display = 'none';
        }
        if (elements.totalIssues) {
            elements.totalIssues.textContent = '0';
        }
        
        showToast('🔄 Ready for new analysis!', 'success');
        console.log('🔄 Reset for new analysis');
    }
    
    function showLoading(title = 'Processing', text = 'Please wait...') {
        if (elements.loadingOverlay) {
            const titleEl = document.getElementById('loadingTitle');
            const textEl = document.getElementById('loadingText');
            
            if (titleEl) titleEl.textContent = title;
            if (textEl) textEl.textContent = text;
            
            elements.loadingOverlay.style.display = 'flex';
        }
    }
    
    function hideLoading() {
        if (elements.loadingOverlay) {
            elements.loadingOverlay.style.display = 'none';
        }
    }
    
    function showToast(message, type = 'success') {
        console.log(`📢 Toast (${type}):`, message);
        
        if (!elements.toastContainer) {
            // Fallback to console if toast container not found
            console.log('Toast fallback:', message);
            return;
        }
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.style.cssText = `
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 15px 20px;
            color: white;
            animation: slideIn 0.3s ease;
            margin-bottom: 10px;
            min-width: 300px;
            border-left: 4px solid ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#0ea5e9'};
        `;
        
        toast.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: rgba(255,255,255,0.7); cursor: pointer; padding: 5px;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        elements.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    async function checkBackendConnection() {
        try {
            console.log('🔌 Checking backend connection...');
            const response = await fetch(`${API_URL}/health`);
            const data = await response.json();
            
            if (response.ok) {
                console.log('✅ Backend connected:', data);
                showToast('✅ Connected to AI Engine successfully!', 'success');
            } else {
                throw new Error('Backend responded with error');
            }
        } catch (error) {
            console.error('❌ Backend connection failed:', error);
            showToast('❌ Backend connection failed - Some features may not work', 'error');
        }
    }
    
    console.log("🎉 SmartDoc AI initialized successfully!");
});
