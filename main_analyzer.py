#!/usr/bin/env python3
"""
StorEdge DaVinci Unit Status Analyzer - Main Application

This is the main application script for analyzing self-storage unit status and lock assignments.
It processes three CSV files (units.csv, rentroll.csv, locks.csv) and generates comprehensive
reports identifying miscompares between expected and actual lock statuses.

Usage:
    python main_analyzer.py --units units.csv --rentroll rentroll.csv --locks locks.csv --output results/

Author: StorEdge DaVinci Miscompare v1
"""

import argparse
import sys
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

# Import our custom modules
from src.unit_status_analyzer import UnitStatusAnalyzer
from src.report_generator import ReportGenerator
from src.enhanced_excel_exporter import EnhancedExcelExporter

def setup_logging(log_level: str = 'INFO'):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('unit_analysis.log')
        ]
    )

def validate_input_files(units_file: str, rentroll_file: str, locks_file: str):
    """Validate that input files exist and are readable."""
    files_to_check = [
        (units_file, 'units.csv'),
        (rentroll_file, 'rentroll.csv'),
        (locks_file, 'locks.csv')
    ]
    
    for file_path, file_type in files_to_check:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"{file_type} file not found: {file_path}")
        
        try:
            # Try to read the file to ensure it's valid CSV
            pd.read_csv(file_path, nrows=1)
        except Exception as e:
            raise ValueError(f"Error reading {file_type} file {file_path}: {str(e)}")

def create_output_directory(output_dir: str) -> Path:
    """Create output directory with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"analysis_{timestamp}"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path

def main():
    """Main application function."""
    parser = argparse.ArgumentParser(
        description="StorEdge DaVinci Unit Status Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage
    python main_analyzer.py --units units.csv --rentroll rentroll.csv --locks locks.csv
    
    # With custom output directory
    python main_analyzer.py --units units.csv --rentroll rentroll.csv --locks locks.csv --output ./results/
    
    # With verbose logging
    python main_analyzer.py --units units.csv --rentroll rentroll.csv --locks locks.csv --log-level DEBUG
        """
    )
    
    parser.add_argument('--units', required=True, help='Path to units.csv file')
    parser.add_argument('--rentroll', required=True, help='Path to rentroll.csv file')
    parser.add_argument('--locks', required=True, help='Path to locks.csv file')
    parser.add_argument('--output', default='./output', help='Output directory (default: ./output)')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--no-dashboard', action='store_true', 
                       help='Skip generating interactive dashboard')
    parser.add_argument('--no-visualizations', action='store_true',
                       help='Skip generating individual visualization files')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting StorEdge DaVinci Unit Status Analysis")
        logger.info(f"Units file: {args.units}")
        logger.info(f"Rentroll file: {args.rentroll}")
        logger.info(f"Locks file: {args.locks}")
        logger.info(f"Output directory: {args.output}")
        
        # Validate input files
        logger.info("Validating input files...")
        validate_input_files(args.units, args.rentroll, args.locks)
        logger.info("Input files validated successfully")
        
        # Create output directory
        output_path = create_output_directory(args.output)
        logger.info(f"Output directory created: {output_path}")
        
        # Initialize analyzer
        analyzer = UnitStatusAnalyzer()
        
        # Run analysis
        logger.info("Running unit status analysis...")
        results_df = analyzer.run_analysis(args.units, args.rentroll, args.locks)
        
        # Generate summary statistics
        summary = analyzer.generate_summary_report(results_df)
        logger.info("Analysis Summary:")
        for key, value in summary.items():
            logger.info(f"  {key}: {value}")
        
        # Initialize report generator
        report_gen = ReportGenerator(results_df)
        
        # Generate enhanced Excel report
        excel_report_path = output_path / "detailed_analysis_report.xlsx"
        logger.info("Generating enhanced Excel report...")
        
        # Create both standard and enhanced reports
        report_gen.create_detailed_report(str(excel_report_path))
        
        # Create enhanced Excel report with formatting and charts
        enhanced_excel_path = output_path / "enhanced_analysis_report.xlsx"
        enhanced_exporter = EnhancedExcelExporter()
        enhanced_exporter.create_enhanced_report(results_df, str(enhanced_excel_path))
        
        # Generate alert report
        alert_report = report_gen.generate_alert_report()
        if not alert_report.empty:
            alert_path = output_path / "priority_alerts.csv"
            alert_report.to_csv(alert_path, index=False)
            logger.info(f"Priority alerts saved to: {alert_path}")
            logger.warning(f"Found {len(alert_report)} units requiring immediate attention!")
        else:
            logger.info("No miscompares found - all units are properly configured!")
        
        # Generate interactive dashboard
        if not args.no_dashboard:
            logger.info("Generating interactive dashboard...")
            dashboard_path = output_path / "analysis_dashboard.html"
            report_gen.create_summary_dashboard(str(dashboard_path))
        
        # Generate individual visualizations
        if not args.no_visualizations:
            logger.info("Generating visualization suite...")
            viz_dir = output_path / "visualizations"
            report_gen.create_visualization_suite(str(viz_dir))
        
        # Save raw results
        results_path = output_path / "complete_analysis_results.csv"
        results_df.to_csv(results_path, index=False)
        logger.info(f"Complete results saved to: {results_path}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("STOREDGE DAVINCI UNIT STATUS ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total Units Analyzed: {summary['total_units']}")
        print(f"Miscompares Found: {summary['miscompare_count']}")
        print(f"Miscompare Rate: {summary['miscompare_rate']:.2f}%")
        print(f"\nUnit Status Breakdown:")
        for status, count in summary['unit_status_breakdown'].items():
            print(f"  {status}: {count}")
        print(f"\nHigh Severity Issues: {summary['severity_breakdown'].get('HIGH - Vacant unit with tenant lock', 0) + summary['severity_breakdown'].get('HIGH - Current tenant without proper lock', 0) + summary['severity_breakdown'].get('HIGH - Delinquent unit without lock', 0)}")
        print(f"\nOutput Directory: {output_path}")
        print("="*60)
        
        if summary['miscompare_count'] > 0:
            print(f"\n⚠️  ATTENTION: {summary['miscompare_count']} miscompares found!")
            print("Please review the priority_alerts.csv file for immediate action items.")
        else:
            print("\n✅ All units are properly configured - no miscompares found!")
        
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        print(f"\n[ERROR] Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
