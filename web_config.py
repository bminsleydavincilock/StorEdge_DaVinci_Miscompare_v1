"""
Configuration file for the StorEdge DaVinci Web Application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_CONFIG = {
    "url": os.getenv("SUPABASE_URL", "https://yyrwwxgfbeisquzwixuk.supabase.co"),
    "key": os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cnd3eGdmYmVpc3F1endpeHVrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg5OTU5NTIsImV4cCI6MjA3NDU3MTk1Mn0.3VqefG5756l8cmodw8dqxEto4U-q6DSOgwITtp2NR94"),
    "email": os.getenv("SUPABASE_EMAIL", "DaVinciLock-Brad"),
    "password": os.getenv("SUPABASE_PASSWORD", "pled0!Naples"),
}

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db.yyrwwxgfbeisquzwixuk.supabase.co"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "postgres"),
    "username": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "pled0!Naples"),
    "schema": os.getenv("DB_SCHEMA", "public")
}

# Application Configuration
APP_CONFIG = {
    "title": "StorEdge DaVinci Unit Status Analyzer",
    "description": "Analyze self-storage unit status and lock assignments",
    "version": "1.0.0",
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_file_types": ["csv"],
    "session_timeout": 3600,  # 1 hour
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "default_include_dashboard": True,
    "default_include_visualizations": True,
    "default_include_enhanced_excel": True,
    "max_units_per_analysis": 10000,
    "analysis_timeout": 300,  # 5 minutes
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.getenv("LOG_FILE", "storedge_analyzer.log"),
}
