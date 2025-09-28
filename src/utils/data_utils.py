"""
Data utility functions
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_data(file_path, **kwargs):
    """
    Load data from various file formats
    
    Parameters:
    -----------
    file_path : str or Path
        Path to the data file
    **kwargs : dict
        Additional arguments to pass to pandas read function
        
    Returns:
    --------
    pd.DataFrame
        Loaded data
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, **kwargs)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, **kwargs)
        elif file_path.suffix.lower() == '.json':
            df = pd.read_json(file_path, **kwargs)
        elif file_path.suffix.lower() == '.parquet':
            df = pd.read_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Successfully loaded data from {file_path}")
        logger.info(f"Data shape: {df.shape}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {str(e)}")
        raise

def save_data(df, file_path, **kwargs):
    """
    Save DataFrame to various file formats
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save
    file_path : str or Path
        Path to save the file
    **kwargs : dict
        Additional arguments to pass to pandas save function
    """
    file_path = Path(file_path)
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if file_path.suffix.lower() == '.csv':
            df.to_csv(file_path, index=False, **kwargs)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            df.to_excel(file_path, index=False, **kwargs)
        elif file_path.suffix.lower() == '.json':
            df.to_json(file_path, **kwargs)
        elif file_path.suffix.lower() == '.parquet':
            df.to_parquet(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        logger.info(f"Successfully saved data to {file_path}")
        
    except Exception as e:
        logger.error(f"Error saving data to {file_path}: {str(e)}")
        raise

def clean_data(df, missing_strategy='drop', outlier_method='iqr'):
    """
    Clean the dataset by handling missing values and outliers
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    missing_strategy : str
        Strategy for handling missing values ('drop', 'mean', 'median', 'mode')
    outlier_method : str
        Method for handling outliers ('iqr', 'zscore', 'none')
        
    Returns:
    --------
    pd.DataFrame
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Handle missing values
    if missing_strategy == 'drop':
        df_clean = df_clean.dropna()
    elif missing_strategy == 'mean':
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
    elif missing_strategy == 'median':
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
    elif missing_strategy == 'mode':
        for col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0] if not df_clean[col].mode().empty else df_clean[col].iloc[0])
    
    # Handle outliers
    if outlier_method == 'iqr':
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
    elif outlier_method == 'zscore':
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
            df_clean = df_clean[z_scores < 3]
    
    logger.info(f"Data cleaning completed. Shape changed from {df.shape} to {df_clean.shape}")
    
    return df_clean
