import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    FLEXPRICE_API_KEY = os.getenv('FLEXPRICE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    PATHWAY_API_KEY = os.getenv('PATHWAY_API_KEY')
    UPLOAD_FOLDER = 'uploads'
    REPORTS_FOLDER = 'reports'
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
