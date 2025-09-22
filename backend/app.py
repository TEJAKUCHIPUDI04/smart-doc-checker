from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '../uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Smart Doc Checker is running!",
        "timestamp": datetime.now().isoformat(),
        "port": 5001,
        "endpoints": [
            "GET /api/health",
            "POST /api/upload",
            "POST /api/analyze",
            "GET /api/usage/<session_id>"
        ]
    })

@app.route("/api/upload", methods=["POST"])
def upload_documents():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        session_id = request.form.get('session_id', str(uuid.uuid4()))
        
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = str(int(time.time()))
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                
                uploaded_files.append({
                    'id': len(uploaded_files) + 1,
                    'filename': filename,
                    'path': file_path,
                    'size': file_size
                })
        
        return jsonify({
            'message': f'Successfully uploaded {len(uploaded_files)} files!',
            'session_id': session_id,
            'uploaded_files': uploaded_files,
            'count': len(uploaded_files)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/analyze", methods=["POST"])
def analyze_documents():
    try:
        data = request.get_json()
        session_id = data.get('session_id', 'demo-session')
        
        # Demo contradictions
        demo_contradictions = [
            {
                'type': 'numerical',
                'document1': 'policy1.txt',
                'document2': 'policy2.txt',
                'sentence1': 'Students must maintain minimum 75% attendance',
                'sentence2': 'Students with 65% attendance are eligible',
                'description': 'Conflicting attendance requirements: 75% vs 65%',
                'severity_score': 0.9,
                'suggestion': 'Clarify the correct attendance percentage'
            },
            {
                'type': 'time',
                'document1': 'policy1.txt',
                'document2': 'policy2.txt',
                'sentence1': 'Deadline is 11:59 PM',
                'sentence2': 'Submit before 10:00 PM',
                'description': 'Conflicting deadlines: 11:59 PM vs 10:00 PM',
                'severity_score': 0.8,
                'suggestion': 'Standardize submission deadline'
            }
        ]
        
        return jsonify({
            'message': 'Analysis completed successfully!',
            'report': {
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'total_contradictions': len(demo_contradictions),
                'contradictions': demo_contradictions,
                'summary': {
                    'numerical_conflicts': 1,
                    'time_conflicts': 1,
                    'policy_conflicts': 0
                },
                'status': 'Demo analysis - working perfectly!'
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/usage/<session_id>", methods=["GET"])
def get_usage_stats(session_id):
    return jsonify({
        'session_id': session_id,
        'documents_analyzed': 2,
        'reports_generated': 1,
        'total_cost': 9.00,
        'pricing': {'per_document': '$2.00', 'per_report': '$5.00'},
        'note': 'Demo billing - Flexprice integration ready'
    })

if __name__ == "__main__":
    print("🚀 Smart Doc Checker Starting on Port 5001...")
    print("📊 All endpoints ready!")
    print("🔍 Health: http://localhost:5001/api/health")
    print("📤 Upload: POST http://localhost:5001/api/upload")
    print("🔍 Analyze: POST http://localhost:5001/api/analyze")
    app.run(debug=True, host="0.0.0.0", port=5001)
