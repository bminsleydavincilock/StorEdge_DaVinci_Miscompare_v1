#!/usr/bin/env python3
"""
Standalone Excel Export Script for StorEdge DaVinci Unit Status Analysis

This script allows you to export analysis results to a professionally formatted Excel file.
It can work with existing analysis results or run a new analysis.

Usage:
    python export_to_excel.py --units units.csv --rentroll rentroll.csv --locks locks.csv --output report.xlsx
    python export_to_excel.py --input complete_analysis_results.csv --output report.xlsx
"""

import argparse
import sys
import logging
from pathlib import Path
import pandas as pd

# Import our custom modules
from src.unit_status_analyzer import UnitStatusAnalyzer
from src.enhanced_excel_exporter import EnhancedExcelExporter

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def export_from_csv(input_csv: str, output_excel: str):
    """
    Export analysis results from existing CSV file to Excel.
    
    Args:
        input_csv (str): Path to existing analysis results CSV
        output_excel (str): Path to output Excel file
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Loading analysis results from {input_csv}")
        df = pd.read_csv(input_csv)
        
        logger.info("Creating enhanced Excel report...")
        exporter = EnhancedExcelExporter()
        exporter.create_enhanced_report(df, output_excel)
        
        logger.info(f"Enhanced Excel report saved to {output_excel}")
        print(f"[SUCCESS] Excel report successfully created: {output_excel}")
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        print(f"[ERROR] {str(e)}")
        sys.exit(1)

def export_from_analysis(units_file: str, rentroll_file: str, locks_file: str, output_excel: str):
    """
    Run analysis and export results to Excel.
    
    Args:
        units_file (str): Path to units.csv
        rentroll_file (str): Path to rentroll.csv
        locks_file (str): Path to locks.csv
        output_excel (str): Path to output Excel file
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Running unit status analysis...")
        analyzer = UnitStatusAnalyzer()
        results_df = analyzer.run_analysis(units_file, rentroll_file, locks_file)
        
        logger.info("Creating enhanced Excel report...")
        exporter = EnhancedExcelExporter()
        exporter.create_enhanced_report(results_df, output_excel)
        
        # Print summary
        summary = analyzer.generate_summary_report(results_df)
        print(f"\nAnalysis Summary:")
        print(f"   Total Units: {summary['total_units']}")
        print(f"   Miscompares: {summary['miscompare_count']} ({summary['miscompare_rate']:.1f}%)")
        print(f"   High Severity: {summary['severity_breakdown'].get('HIGH - Vacant unit with tenant lock', 0)}")
        
        logger.info(f"Enhanced Excel report saved to {output_excel}")
        print(f"[SUCCESS] Excel report successfully created: {output_excel}")
        
    except Exception as e:
        logger.error(f"Error during analysis or export: {str(e)}")
        print(f"[ERROR] {str(e)}")
        sys.exit(1)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Export StorEdge DaVinci analysis results to Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Export from existing analysis results
    python export_to_excel.py --input complete_analysis_results.csv --output report.xlsx
    
    # Run new analysis and export
    python export_to_excel.py --units units.csv --rentroll rentroll.csv --locks locks.csv --output report.xlsx
    
    # Export with custom filename
    python export_to_excel.py --input results.csv --output "StorEdge_Analysis_$(date +%Y%m%d).xlsx"
        """
    )
    
    # Create mutually exclusive group for input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', help='Path to existing analysis results CSV file')
    input_group.add_argument('--units', help='Path to units.csv file (requires --rentroll and --locks)')
    
    parser.add_argument('--rentroll', help='Path to rentroll.csv file')
    parser.add_argument('--locks', help='Path to locks.csv file')
    parser.add_argument('--output', required=True, help='Path to output Excel file')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Validate arguments
    if args.units and (not args.rentroll or not args.locks):
        print("[ERROR] --units requires both --rentroll and --locks arguments")
        sys.exit(1)
    
    if args.input and (args.rentroll or args.locks):
        print("[ERROR] --input cannot be used with --rentroll or --locks")
        sys.exit(1)
    
    # Validate input files exist
    if args.input:
        if not Path(args.input).exists():
            print(f"[ERROR] Input file not found: {args.input}")
            sys.exit(1)
    else:
        for file_path in [args.units, args.rentroll, args.locks]:
            if not Path(file_path).exists():
                print(f"[ERROR] File not found: {file_path}")
                sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("StorEdge DaVinci Excel Export Tool")
    print("=" * 50)
    
    # Run appropriate export function
    if args.input:
        print(f"[INFO] Loading analysis results from: {args.input}")
        export_from_csv(args.input, args.output)
    else:
        print(f"[INFO] Running analysis with:")
        print(f"   Units: {args.units}")
        print(f"   Rentroll: {args.rentroll}")
        print(f"   Locks: {args.locks}")
        export_from_analysis(args.units, args.rentroll, args.locks, args.output)
    
    print("\nExcel Report Features:")
    print("   - Executive Summary with key metrics")
    print("   - Complete analysis with conditional formatting")
    print("   - Priority-sorted miscompares")
    print("   - High severity issues highlighted")
    print("   - Status breakdowns with charts")
    print("   - Detailed cross-tabulation")
    print("   - Actionable recommendations")
    print("   - Professional formatting and colors")

if __name__ == "__main__":
    main()
