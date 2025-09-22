from supabase import create_client, Client
from config.config import Config
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    def create_tables(self):
        """Create necessary tables in Supabase"""
        # Documents table
        documents_schema = """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(255) NOT NULL,
            upload_time TIMESTAMP DEFAULT NOW(),
            file_size INTEGER,
            document_type VARCHAR(50)
        );
        """
        
        # Analysis reports table
        reports_schema = """
        CREATE TABLE IF NOT EXISTS analysis_reports (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(100) NOT NULL,
            document_ids INTEGER[],
            contradictions JSONB,
            total_contradictions INTEGER DEFAULT 0,
            report_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            analysis_time_seconds DECIMAL
        );
        """
        
        # Usage tracking table
        usage_schema = """
        CREATE TABLE IF NOT EXISTS usage_tracking (
            id SERIAL PRIMARY KEY,
            user_session VARCHAR(100),
            documents_analyzed INTEGER DEFAULT 0,
            reports_generated INTEGER DEFAULT 0,
            billing_amount DECIMAL DEFAULT 0.00,
            timestamp TIMESTAMP DEFAULT NOW()
        );
        """
    
    def save_document(self, filename, file_path, file_size, doc_type):
        """Save document metadata to database"""
        try:
            result = self.supabase.table('documents').insert({
                'filename': filename,
                'file_path': file_path,
                'file_size': file_size,
                'document_type': doc_type
            }).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def save_analysis_report(self, session_id, doc_ids, contradictions, report_path, analysis_time):
        """Save analysis report to database"""
        try:
            result = self.supabase.table('analysis_reports').insert({
                'session_id': session_id,
                'document_ids': doc_ids,
                'contradictions': json.dumps(contradictions),
                'total_contradictions': len(contradictions),
                'report_path': report_path,
                'analysis_time_seconds': analysis_time
            }).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def update_usage(self, session_id, docs_analyzed=0, reports_generated=0, billing_amount=0.0):
        """Update usage statistics"""
        try:
            # Check if session exists
            existing = self.supabase.table('usage_tracking').select('*').eq('user_session', session_id).execute()
            
            if existing.data:
                # Update existing record
                current = existing.data[0]
                self.supabase.table('usage_tracking').update({
                    'documents_analyzed': current['documents_analyzed'] + docs_analyzed,
                    'reports_generated': current['reports_generated'] + reports_generated,
                    'billing_amount': current['billing_amount'] + billing_amount,
                    'timestamp': datetime.now().isoformat()
                }).eq('user_session', session_id).execute()
            else:
                # Create new record
                self.supabase.table('usage_tracking').insert({
                    'user_session': session_id,
                    'documents_analyzed': docs_analyzed,
                    'reports_generated': reports_generated,
                    'billing_amount': billing_amount
                }).execute()
        except Exception as e:
            print(f"Usage tracking error: {e}")
    
    def get_usage_stats(self, session_id):
        """Get usage statistics for session"""
        try:
            result = self.supabase.table('usage_tracking').select('*').eq('user_session', session_id).execute()
            return result.data[0] if result.data else {
                'documents_analyzed': 0,
                'reports_generated': 0,
                'billing_amount': 0.0
            }
        except Exception as e:
            print(f"Error getting usage stats: {e}")
            return {'documents_analyzed': 0, 'reports_generated': 0, 'billing_amount': 0.0}
