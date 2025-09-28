"""
Configuration file for StorEdge DaVinci Miscompare v1 project
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
MODELS_DIR = PROJECT_ROOT / "src" / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Data file paths
RAW_DATA_FILE = RAW_DATA_DIR / "storedge_davinci_miscompare_raw.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "storedge_davinci_miscompare_processed.csv"

# Model configuration
MODEL_CONFIG = {
    "random_state": 42,
    "test_size": 0.2,
    "validation_size": 0.2,
    "cv_folds": 5
}

# Visualization settings
PLOT_CONFIG = {
    "figure_size": (12, 8),
    "dpi": 300,
    "style": "seaborn-v0_8",
    "color_palette": "husl"
}

# Database configuration (if needed)
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "your_database",
    "username": "your_username",
    "password": "your_password"
}

# API configuration (if needed)
API_CONFIG = {
    "base_url": "https://api.example.com",
    "timeout": 30,
    "retries": 3
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": PROJECT_ROOT / "logs" / "project.log"
}

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
