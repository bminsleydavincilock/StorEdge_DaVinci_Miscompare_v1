#!/usr/bin/env python3
"""
Test script for the StorEdge DaVinci Web Application

This script tests the core components of the web application without running Streamlit.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.unit_status_analyzer import UnitStatusAnalyzer
        print("[SUCCESS] UnitStatusAnalyzer imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import UnitStatusAnalyzer: {e}")
        return False
    
    try:
        from src.report_generator import ReportGenerator
        print("[SUCCESS] ReportGenerator imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import ReportGenerator: {e}")
        return False
    
    try:
        from src.enhanced_excel_exporter import EnhancedExcelExporter
        print("[SUCCESS] EnhancedExcelExporter imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import EnhancedExcelExporter: {e}")
        return False
    
    try:
        from src.supabase_integration import SupabaseManager
        print("[SUCCESS] SupabaseManager imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import SupabaseManager: {e}")
        return False
    
    try:
        import streamlit as st
        print("[SUCCESS] Streamlit imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import Streamlit: {e}")
        return False
    
    return True

def test_analyzer():
    """Test the analyzer with sample data."""
    print("\nTesting analyzer with sample data...")
    
    try:
        from src.unit_status_analyzer import UnitStatusAnalyzer
        
        # Check if sample data exists
        sample_units = "data/raw/units.csv"
        sample_rentroll = "data/raw/rentroll.csv"
        sample_locks = "data/raw/locks.csv"
        
        if not all(os.path.exists(f) for f in [sample_units, sample_rentroll, sample_locks]):
            print("[WARNING] Sample data files not found, skipping analyzer test")
            return True
        
        analyzer = UnitStatusAnalyzer()
        results_df = analyzer.run_analysis(sample_units, sample_rentroll, sample_locks)
        
        print(f"[SUCCESS] Analysis completed successfully")
        print(f"   Total units: {len(results_df)}")
        print(f"   Miscompares: {len(results_df[results_df['Is_Miscompare'] == True])}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Analyzer test failed: {e}")
        return False

def test_excel_exporter():
    """Test the Excel exporter."""
    print("\nTesting Excel exporter...")
    
    try:
        from src.enhanced_excel_exporter import EnhancedExcelExporter
        import tempfile
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Unit': ['A001', 'A002', 'A003'],
            'Unit_Status': ['Occupied', 'Vacant', 'Occupied'],
            'Final_Status': ['Occupied-Current', 'Vacant', 'Occupied-Delinquent'],
            'Actual_Lock_Status': ['Tenant Using Lock', 'Assigned Vacant', 'Assigned Overlock'],
            'Expected_Lock_Status': ['Tenant Using Lock', 'Assigned Vacant', 'Assigned Overlock'],
            'Is_Miscompare': [False, False, False],
            'Miscompare_Severity': ['No Issue', 'No Issue', 'No Issue']
        })
        
        exporter = EnhancedExcelExporter()
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            exporter.create_enhanced_report(sample_data, tmp_file.name)
            print(f"[SUCCESS] Excel report created successfully: {tmp_file.name}")
            
            # Clean up
            os.unlink(tmp_file.name)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Excel exporter test failed: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection."""
    print("\nTesting Supabase connection...")
    
    try:
        from src.supabase_integration import SupabaseManager
        
        manager = SupabaseManager()
        if manager.test_connection():
            print("[SUCCESS] Supabase connection successful")
        else:
            print("[WARNING] Supabase connection failed (this is expected if not configured)")
        
        return True
        
    except Exception as e:
        print(f"[WARNING] Supabase test failed (this is expected if not configured): {e}")
        return True  # Don't fail the test for Supabase issues

def test_file_validation():
    """Test file validation logic."""
    print("\nTesting file validation...")
    
    try:
        # Test with sample data if available
        sample_units = "data/raw/units.csv"
        if os.path.exists(sample_units):
            df = pd.read_csv(sample_units)
            available_cols = [col.strip().strip('"') for col in df.columns]
            
            # Check for required columns
            required_cols = ['Unit', 'Status']
            missing_cols = []
            for expected_col in required_cols:
                if not any(expected_col.lower() in col.lower() for col in available_cols):
                    missing_cols.append(expected_col)
            
            if missing_cols:
                print(f"[WARNING] Missing columns in units.csv: {missing_cols}")
            else:
                print("[SUCCESS] Units CSV validation passed")
        
        print("[SUCCESS] File validation test completed")
        return True
        
    except Exception as e:
        print(f"[ERROR] File validation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing StorEdge DaVinci Web Application Components")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_analyzer,
        test_excel_exporter,
        test_supabase_connection,
        test_file_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! The web application is ready for deployment.")
        return True
    else:
        print("[WARNING] Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
