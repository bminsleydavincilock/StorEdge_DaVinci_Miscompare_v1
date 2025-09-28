"""
StorEdge DaVinci Unit Status Analyzer

This module analyzes self-storage unit status and lock assignments to identify miscompares.
It processes three CSV files: units.csv, rentroll.csv, and locks.csv to determine:
- Unit status: Vacant, Occupied-Current, or Occupied-Delinquent
- Lock status: Assigned Vacant, Tenant Using Lock, Assigned Auction, Assigned Overlock
- Miscompares: When actual lock status doesn't match expected lock status

Author: StorEdge DaVinci Miscompare v1
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnitStatusAnalyzer:
    """
    Analyzes self-storage unit status and lock assignments for miscompare detection.
    """
    
    def __init__(self):
        """Initialize the analyzer with default settings."""
        self.units_df = None
        self.rentroll_df = None
        self.locks_df = None
        self.master_df = None
        
        # Expected lock status mappings
        self.expected_lock_status = {
            'Vacant': 'Assigned Vacant',
            'Occupied-Current': 'Tenant Using Lock',
            'Occupied-Delinquent': ['Assigned Overlock', 'Assigned Auction']
        }
        
        # Valid lock statuses
        self.valid_lock_statuses = [
            'Assigned Vacant',
            'Tenant Using Lock', 
            'Assigned Auction',
            'Assigned Overlock'
        ]
    
    def load_units_file(self, file_path: str) -> pd.DataFrame:
        """
        Load and process the units.csv file.
        
        Args:
            file_path (str): Path to the units.csv file
            
        Returns:
            pd.DataFrame: Processed units data
        """
        try:
            logger.info(f"Loading units file: {file_path}")
            
            # Try different encodings for CSV files
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Successfully read units file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read units file with any supported encoding")
            
            # Validate required columns
            required_cols = ['Unit', 'Status']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in units.csv: {missing_cols}")
            
            # Clean and process the data
            df = df.copy()
            df['Unit'] = df['Unit'].astype(str).str.strip()
            
            # Extract unit status from first 3 characters
            df['Status_Clean'] = df['Status'].astype(str).str[:3].str.upper()
            
            # Map to standard status
            status_mapping = {
                'OCC': 'Occupied',
                'VAC': 'Vacant'
            }
            df['Unit_Status'] = df['Status_Clean'].map(status_mapping)
            
            # Handle unmapped statuses
            unmapped = df[df['Unit_Status'].isna()]
            if not unmapped.empty:
                logger.warning(f"Found unmapped statuses: {unmapped['Status_Clean'].unique()}")
                df['Unit_Status'] = df['Unit_Status'].fillna('Unknown')
            
            logger.info(f"Loaded {len(df)} units from units.csv")
            return df
            
        except Exception as e:
            logger.error(f"Error loading units file: {str(e)}")
            raise
    
    def load_rentroll_file(self, file_path: str) -> pd.DataFrame:
        """
        Load and process the rentroll.csv file.
        
        Args:
            file_path (str): Path to the rentroll.csv file
            
        Returns:
            pd.DataFrame: Processed rentroll data
        """
        try:
            logger.info(f"Loading rentroll file: {file_path}")
            
            # Try different encodings for CSV files
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Successfully read rentroll file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read rentroll file with any supported encoding")
            
            # Validate required columns (handle different column name formats)
            required_cols = ['Unit', 'Days Past Due']
            # Check for various column name formats
            available_cols = list(df.columns)
            missing_cols = []
            
            # Map possible column names
            unit_col_candidates = ['Unit', 'UNIT', '"Unit"', '"UNIT"']
            days_col_candidates = ['Days Past Due', 'DAYS PAST DUE', '"Days Past Due"', '"DAYS PAST DUE"']
            
            unit_col_found = any(col in available_cols for col in unit_col_candidates)
            days_col_found = any(col in available_cols for col in days_col_candidates)
            
            if not unit_col_found:
                missing_cols.append('Unit')
            if not days_col_found:
                missing_cols.append('Days Past Due')
            
            if missing_cols:
                raise ValueError(f"Missing required columns in rentroll.csv: {missing_cols}")
            
            # Clean and process the data
            df = df.copy()
            
            # Handle different column name formats
            unit_col = None
            days_col = None
            
            for col in ['Unit', 'UNIT', '"Unit"', '"UNIT"']:
                if col in df.columns:
                    unit_col = col
                    break
            
            for col in ['Days Past Due', 'DAYS PAST DUE', '"Days Past Due"', '"DAYS PAST DUE"']:
                if col in df.columns:
                    days_col = col
                    break
            
            df['Unit'] = df[unit_col].astype(str).str.strip()
            
            # Convert Days Past Due to numeric, handling empty values
            df['Days_Past_Due_Clean'] = pd.to_numeric(df[days_col], errors='coerce').fillna(0)
            
            # Determine payment status
            df['Payment_Status'] = df['Days_Past_Due_Clean'].apply(
                lambda x: 'Delinquent' if x > 0 else 'Current'
            )
            
            logger.info(f"Loaded {len(df)} occupied units from rentroll.csv")
            return df
            
        except Exception as e:
            logger.error(f"Error loading rentroll file: {str(e)}")
            raise
    
    def load_locks_file(self, file_path: str) -> pd.DataFrame:
        """
        Load and process the locks file (CSV or Excel).
        
        Args:
            file_path (str): Path to the locks file (CSV or Excel)
            
        Returns:
            pd.DataFrame: Processed locks data
        """
        try:
            logger.info(f"Loading locks file: {file_path}")
            
            # Check file extension to determine how to read it
            if file_path.lower().endswith('.xlsx'):
                df = pd.read_excel(file_path)
                logger.info("Reading locks file as Excel format")
            else:
                # Try different encodings for CSV files
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                df = None
                
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        logger.info(f"Successfully read locks file with {encoding} encoding")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    raise ValueError("Could not read locks file with any supported encoding")
            
            # Validate required columns
            required_cols = ['Unit Number', 'Status']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns in locks.csv: {missing_cols}")
            
            # Clean and process the data
            df = df.copy()
            df['Unit'] = df['Unit Number'].astype(str).str.strip()
            df['Lock_Status'] = df['Status'].astype(str).str.strip()
            
            # Validate lock statuses
            invalid_statuses = df[~df['Lock_Status'].isin(self.valid_lock_statuses)]
            if not invalid_statuses.empty:
                logger.warning(f"Found invalid lock statuses: {invalid_statuses['Lock_Status'].unique()}")
            
            file_type = "Excel" if file_path.lower().endswith('.xlsx') else "CSV"
            logger.info(f"Loaded {len(df)} lock assignments from locks.{file_type.lower()}")
            return df[['Unit', 'Lock_Status']]
            
        except Exception as e:
            logger.error(f"Error loading locks file: {str(e)}")
            raise
    
    def determine_unit_status(self, units_df: pd.DataFrame, rentroll_df: pd.DataFrame) -> pd.DataFrame:
        """
        Determine the final status of each unit based on units and rentroll data.
        
        Args:
            units_df (pd.DataFrame): Units data
            rentroll_df (pd.DataFrame): Rentroll data
            
        Returns:
            pd.DataFrame: Units with final status determined
        """
        logger.info("Determining unit status...")
        
        # Start with all units
        result_df = units_df[['Unit', 'Unit_Status']].copy()
        
        # Create a mapping of units to payment status from rentroll
        rentroll_mapping = rentroll_df.set_index('Unit')['Payment_Status'].to_dict()
        
        def get_final_status(row):
            unit = row['Unit']
            unit_status = row['Unit_Status']
            
            if unit_status == 'Vacant':
                return 'Vacant'
            elif unit_status == 'Occupied':
                if unit in rentroll_mapping:
                    payment_status = rentroll_mapping[unit]
                    return f'Occupied-{payment_status}'
                else:
                    # Unit marked as occupied in units.csv but not in rentroll.csv
                    # This could be a data inconsistency, but we'll treat as vacant
                    logger.warning(f"Unit {unit} marked as occupied but not found in rentroll - treating as vacant")
                    return 'Vacant'
            else:
                return 'Unknown'
        
        result_df['Final_Status'] = result_df.apply(get_final_status, axis=1)
        
        # Handle units in rentroll but not in units.csv (shouldn't happen but just in case)
        units_in_rentroll_not_units = set(rentroll_df['Unit']) - set(units_df['Unit'])
        if units_in_rentroll_not_units:
            logger.warning(f"Units in rentroll but not in units.csv: {units_in_rentroll_not_units}")
        
        logger.info("Unit status determination completed")
        return result_df
    
    def add_lock_status(self, units_df: pd.DataFrame, locks_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add lock status information to the units dataframe.
        
        Args:
            units_df (pd.DataFrame): Units with status information
            locks_df (pd.DataFrame): Locks data
            
        Returns:
            pd.DataFrame: Units with lock status added
        """
        logger.info("Adding lock status information...")
        
        result_df = units_df.copy()
        
        # Create a mapping of units to lock status
        locks_mapping = locks_df.set_index('Unit')['Lock_Status'].to_dict()
        
        # Add actual lock status
        result_df['Actual_Lock_Status'] = result_df['Unit'].map(locks_mapping).fillna('No Lock Assigned')
        
        # Determine expected lock status
        def get_expected_lock_status(final_status):
            if final_status == 'Vacant':
                return 'Assigned Vacant'
            elif final_status == 'Occupied-Current':
                return 'Tenant Using Lock'
            elif final_status == 'Occupied-Delinquent':
                return 'Assigned Overlock or Assigned Auction'  # Either is acceptable
            else:
                return 'Unknown'
        
        result_df['Expected_Lock_Status'] = result_df['Final_Status'].apply(get_expected_lock_status)
        
        logger.info("Lock status information added")
        return result_df
    
    def detect_miscompares(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect miscompares between actual and expected lock status.
        
        Args:
            df (pd.DataFrame): Units with status and lock information
            
        Returns:
            pd.DataFrame: Units with miscompare flags
        """
        logger.info("Detecting miscompares...")
        
        result_df = df.copy()
        
        def is_miscompare(row):
            actual = row['Actual_Lock_Status']
            expected = row['Expected_Lock_Status']
            final_status = row['Final_Status']
            
            # Handle special case for delinquent units
            if final_status == 'Occupied-Delinquent':
                return actual not in ['Assigned Overlock', 'Assigned Auction']
            
            # Handle other cases
            if final_status == 'Vacant':
                return actual != 'Assigned Vacant'
            elif final_status == 'Occupied-Current':
                return actual != 'Tenant Using Lock'
            else:
                return False
        
        result_df['Is_Miscompare'] = result_df.apply(is_miscompare, axis=1)
        
        # Add miscompare severity
        def get_miscompare_severity(row):
            if not row['Is_Miscompare']:
                return 'No Issue'
            
            actual = row['Actual_Lock_Status']
            final_status = row['Final_Status']
            
            # High severity miscompares
            if final_status == 'Vacant' and actual in ['Tenant Using Lock', 'Assigned Overlock']:
                return 'HIGH - Vacant unit with tenant lock'
            elif final_status == 'Occupied-Current' and actual in ['Assigned Vacant', 'Assigned Overlock']:
                return 'HIGH - Current tenant without proper lock'
            elif final_status == 'Occupied-Delinquent' and actual == 'Assigned Vacant':
                return 'HIGH - Delinquent unit without lock'
            else:
                return 'MEDIUM - Lock status mismatch'
        
        result_df['Miscompare_Severity'] = result_df.apply(get_miscompare_severity, axis=1)
        
        miscompare_count = result_df['Is_Miscompare'].sum()
        logger.info(f"Detected {miscompare_count} miscompares out of {len(result_df)} units")
        
        return result_df
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a summary report of the analysis.
        
        Args:
            df (pd.DataFrame): Complete analysis results
            
        Returns:
            Dict: Summary statistics
        """
        logger.info("Generating summary report...")
        
        summary = {
            'total_units': len(df),
            'unit_status_breakdown': df['Final_Status'].value_counts().to_dict(),
            'lock_status_breakdown': df['Actual_Lock_Status'].value_counts().to_dict(),
            'miscompare_count': df['Is_Miscompare'].sum(),
            'miscompare_rate': (df['Is_Miscompare'].sum() / len(df)) * 100,
            'severity_breakdown': df['Miscompare_Severity'].value_counts().to_dict()
        }
        
        return summary
    
    def run_analysis(self, units_file: str, rentroll_file: str, locks_file: str) -> pd.DataFrame:
        """
        Run the complete unit status analysis.
        
        Args:
            units_file (str): Path to units.csv
            rentroll_file (str): Path to rentroll.csv  
            locks_file (str): Path to locks.csv
            
        Returns:
            pd.DataFrame: Complete analysis results
        """
        logger.info("Starting unit status analysis...")
        
        try:
            # Load all files
            self.units_df = self.load_units_file(units_file)
            self.rentroll_df = self.load_rentroll_file(rentroll_file)
            self.locks_df = self.load_locks_file(locks_file)
            
            # Determine unit status
            units_with_status = self.determine_unit_status(self.units_df, self.rentroll_df)
            
            # Add lock status
            units_with_locks = self.add_lock_status(units_with_status, self.locks_df)
            
            # Detect miscompares
            self.master_df = self.detect_miscompares(units_with_locks)
            
            # Generate summary
            summary = self.generate_summary_report(self.master_df)
            logger.info(f"Analysis completed. Found {summary['miscompare_count']} miscompares.")
            
            return self.master_df
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    def save_results(self, output_file: str, include_summary: bool = True):
        """
        Save analysis results to Excel file with formatting.
        
        Args:
            output_file (str): Path to output Excel file
            include_summary (bool): Whether to include summary sheet
        """
        if self.master_df is None:
            raise ValueError("No analysis results to save. Run analysis first.")
        
        logger.info(f"Saving results to {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main results
            self.master_df.to_excel(writer, sheet_name='Unit_Analysis', index=False)
            
            if include_summary:
                # Summary statistics
                summary = self.generate_summary_report(self.master_df)
                summary_df = pd.DataFrame(list(summary.items()), columns=['Metric', 'Value'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Miscompares only
                miscompares = self.master_df[self.master_df['Is_Miscompare'] == True]
                if not miscompares.empty:
                    miscompares.to_excel(writer, sheet_name='Miscompares', index=False)
        
        logger.info("Results saved successfully")
    
    def get_miscompares(self) -> pd.DataFrame:
        """
        Get only the units with miscompares.
        
        Returns:
            pd.DataFrame: Units with miscompares
        """
        if self.master_df is None:
            raise ValueError("No analysis results available. Run analysis first.")
        
        return self.master_df[self.master_df['Is_Miscompare'] == True].copy()

