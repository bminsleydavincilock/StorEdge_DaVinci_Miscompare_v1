"""
StorEdge DaVinci Unit Status Analyzer - Web Application

A Streamlit web application for analyzing self-storage unit status and lock assignments.
Users can upload CSV files and receive comprehensive analysis reports.
"""

import streamlit as st
import pandas as pd
import io
import base64
from datetime import datetime
import logging
from pathlib import Path
import tempfile
import os

# Import our custom modules
from src.unit_status_analyzer import UnitStatusAnalyzer
from src.report_generator import ReportGenerator
from src.enhanced_excel_exporter import EnhancedExcelExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="StorEdge DaVinci Analyzer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def create_download_link(data, filename, file_type="text/csv"):
    """Create a download link for data."""
    href = ""  # Initialize href variable
    
    if file_type == "text/csv":
        csv = data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download {filename}</a>'
    elif file_type == "text/html":
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}">Download {filename}</a>'
    elif file_type == "application/zip":
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="{filename}">Download {filename}</a>'
    else:
        # Fallback for unknown file types
        href = f'<span style="color: red;">Unsupported file type: {file_type}</span>'
    
    return href

def validate_csv_file(file, expected_columns, file_name):
    """Validate uploaded CSV or Excel file."""
    try:
        # Check file extension to determine how to read it
        if file.name.lower().endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            # Try different encodings for CSV files
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    file.seek(0)  # Reset file pointer
                    df = pd.read_csv(file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file with any supported encoding")
        
        available_cols = [col.strip().strip('"') for col in df.columns]
        
        missing_cols = []
        for expected_col in expected_columns:
            if not any(expected_col.lower() in col.lower() for col in available_cols):
                missing_cols.append(expected_col)
        
        if missing_cols:
            return False, f"Missing required columns in {file_name}: {missing_cols}"
        
        file_type = "Excel" if file.name.lower().endswith('.xlsx') else "CSV"
        return True, f"✅ {file_name} ({file_type}) validated successfully ({len(df)} rows)"
    
    except Exception as e:
        return False, f"Error reading {file_name}: {str(e)}"

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🏢 StorEdge DaVinci Unit Status Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Analyze self-storage unit status and lock assignments to identify miscompares
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 File Upload")
        st.markdown("Upload your CSV files to begin analysis:")
        
        # File uploaders
        units_file = st.file_uploader(
            "Upload Units CSV",
            type=['csv'],
            help="Master record of all units (Column C: Unit, Column G: Status)"
        )
        
        rentroll_file = st.file_uploader(
            "Upload Rentroll CSV", 
            type=['csv'],
            help="Payment status for occupied units (Column A: Unit, Column S: Days Past Due)"
        )
        
        locks_file = st.file_uploader(
            "Upload Locks File (CSV or Excel)",
            type=['csv', 'xlsx'], 
            help="Lock assignments (Column C: Unit Number, Column E: Status). Supports both CSV and Excel formats."
        )
        
        st.markdown("---")
        st.header("⚙️ Analysis Options")
        
        # Analysis options
        include_dashboard = st.checkbox("Generate Interactive Dashboard", value=True)
        include_visualizations = st.checkbox("Generate Individual Visualizations", value=True)
        include_enhanced_excel = st.checkbox("Generate Enhanced Excel Report", value=True)
        
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This tool analyzes self-storage unit status and lock assignments to identify miscompares between expected and actual lock statuses.
        
        **Input Requirements:**
        - Units CSV: Master unit records
        - Rentroll CSV: Payment status data
        - Locks CSV: Lock assignment data
        
        **Output:**
        - Comprehensive analysis reports
        - Excel files with formatting
        - Interactive dashboards
        - Priority alerts
        """)
    
    # Main content area
    if units_file and rentroll_file and locks_file:
        
        # Validate files
        st.markdown('<h2 class="sub-header">📋 File Validation</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valid_units, msg_units = validate_csv_file(units_file, ['Unit', 'Status'], 'units.csv')
            if valid_units:
                st.success(msg_units)
            else:
                st.error(msg_units)
        
        with col2:
            valid_rentroll, msg_rentroll = validate_csv_file(rentroll_file, ['Unit', 'Days Past Due'], 'rentroll.csv')
            if valid_rentroll:
                st.success(msg_rentroll)
            else:
                st.error(msg_rentroll)
        
        with col3:
            valid_locks, msg_locks = validate_csv_file(locks_file, ['Unit Number', 'Status'], 'locks.csv')
            if valid_locks:
                st.success(msg_locks)
            else:
                st.error(msg_locks)
        
        # Proceed with analysis if all files are valid
        if valid_units and valid_rentroll and valid_locks:
            
            if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Initialize analyzer
                    status_text.text("Initializing analyzer...")
                    progress_bar.progress(10)
                    
                    analyzer = UnitStatusAnalyzer()
                    
                    # Save uploaded files temporarily
                    status_text.text("Processing uploaded files...")
                    progress_bar.progress(20)
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_units = os.path.join(temp_dir, 'units.csv')
                        temp_rentroll = os.path.join(temp_dir, 'rentroll.csv')
                        temp_locks = os.path.join(temp_dir, 'locks.csv')
                        
                        # Save files
                        units_file.seek(0)
                        with open(temp_units, 'wb') as f:
                            f.write(units_file.getbuffer())
                        
                        rentroll_file.seek(0)
                        with open(temp_rentroll, 'wb') as f:
                            f.write(rentroll_file.getbuffer())
                        
                        locks_file.seek(0)
                        # Handle Excel files for locks
                        if locks_file.name.lower().endswith('.xlsx'):
                            temp_locks = os.path.join(temp_dir, 'locks.xlsx')
                        with open(temp_locks, 'wb') as f:
                            f.write(locks_file.getbuffer())
                        
                        # Run analysis
                        status_text.text("Running unit status analysis...")
                        progress_bar.progress(40)
                        
                        results_df = analyzer.run_analysis(temp_units, temp_rentroll, temp_locks)
                        
                        # Generate summary
                        status_text.text("Generating summary report...")
                        progress_bar.progress(60)
                        
                        summary = analyzer.generate_summary_report(results_df)
                        
                        # Generate reports
                        status_text.text("Generating reports...")
                        progress_bar.progress(80)
                        
                        report_gen = ReportGenerator(results_df)
                        
                        # Create temporary files for downloads
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        # Generate Excel reports
                        if include_enhanced_excel:
                            enhanced_excel_path = os.path.join(temp_dir, f'enhanced_analysis_{timestamp}.xlsx')
                            enhanced_exporter = EnhancedExcelExporter()
                            enhanced_exporter.create_enhanced_report(results_df, enhanced_excel_path)
                            
                            with open(enhanced_excel_path, 'rb') as f:
                                enhanced_excel_data = f.read()
                        
                        standard_excel_path = os.path.join(temp_dir, f'standard_analysis_{timestamp}.xlsx')
                        report_gen.create_detailed_report(standard_excel_path)
                        
                        with open(standard_excel_path, 'rb') as f:
                            standard_excel_data = f.read()
                        
                        # Generate CSV
                        csv_data = results_df.to_csv(index=False)
                        
                        # Generate priority alerts
                        alert_report = report_gen.generate_alert_report()
                        alert_csv = alert_report.to_csv(index=False) if not alert_report.empty else ""
                        
                        # Generate dashboard
                        if include_dashboard:
                            dashboard_path = os.path.join(temp_dir, f'dashboard_{timestamp}.html')
                            report_gen.create_summary_dashboard(dashboard_path)
                            
                            with open(dashboard_path, 'rb') as f:
                                dashboard_data = f.read()
                        
                        # Generate visualizations
                        if include_visualizations:
                            viz_dir = os.path.join(temp_dir, 'visualizations')
                            os.makedirs(viz_dir, exist_ok=True)
                            report_gen.create_visualizations(viz_dir)
                            
                            # Create zip file of visualizations
                            import zipfile
                            viz_zip_path = os.path.join(temp_dir, f'visualizations_{timestamp}.zip')
                            with zipfile.ZipFile(viz_zip_path, 'w') as zipf:
                                for root, dirs, files in os.walk(viz_dir):
                                    for file in files:
                                        zipf.write(os.path.join(root, file), file)
                            
                            with open(viz_zip_path, 'rb') as f:
                                viz_zip_data = f.read()
                        
                        progress_bar.progress(100)
                        status_text.text("Analysis complete!")
                        
                        # Display results
                        st.markdown('<h2 class="sub-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
                        
                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Units", summary['total_units'])
                        
                        with col2:
                            st.metric("Miscompares", f"{summary['miscompare_count']} ({summary['miscompare_rate']:.1f}%)")
                        
                        with col3:
                            high_severity = summary['severity_breakdown'].get('HIGH - Vacant unit with tenant lock', 0)
                            st.metric("High Severity", high_severity)
                        
                        with col4:
                            medium_severity = summary['severity_breakdown'].get('MEDIUM - Lock status mismatch', 0)
                            st.metric("Medium Severity", medium_severity)
                        
                        # Status breakdown
                        st.markdown('<h3 class="sub-header">📈 Unit Status Breakdown</h3>', unsafe_allow_html=True)
                        
                        status_breakdown = results_df['Final_Status'].value_counts()
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.dataframe(status_breakdown.reset_index().rename(columns={'index': 'Status', 'Final_Status': 'Count'}))
                        
                        with col2:
                            st.bar_chart(status_breakdown)
                        
                        # Miscompares table
                        if not results_df[results_df['Is_Miscompare'] == True].empty:
                            st.markdown('<h3 class="sub-header">⚠️ Miscompares Found</h3>', unsafe_allow_html=True)
                            
                            miscompares = results_df[results_df['Is_Miscompare'] == True].copy()
                            miscompares_display = miscompares[['Unit', 'Final_Status', 'Actual_Lock_Status', 'Expected_Lock_Status', 'Miscompare_Severity']]
                            
                            st.dataframe(miscompares_display, use_container_width=True)
                        
                        # Download section
                        st.markdown('<h3 class="sub-header">📥 Download Reports</h3>', unsafe_allow_html=True)
                        
                        download_col1, download_col2 = st.columns(2)
                        
                        with download_col1:
                            st.markdown("**Excel Reports:**")
                            if include_enhanced_excel:
                                st.markdown(create_download_link(
                                    enhanced_excel_data, 
                                    f'enhanced_analysis_{timestamp}.xlsx',
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                ), unsafe_allow_html=True)
                            
                            st.markdown(create_download_link(
                                standard_excel_data,
                                f'standard_analysis_{timestamp}.xlsx', 
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            ), unsafe_allow_html=True)
                            
                            st.markdown(create_download_link(
                                results_df,
                                f'complete_results_{timestamp}.csv'
                            ), unsafe_allow_html=True)
                        
                        with download_col2:
                            st.markdown("**Additional Reports:**")
                            
                            if not alert_report.empty:
                                st.markdown(create_download_link(
                                    alert_report,
                                    f'priority_alerts_{timestamp}.csv'
                                ), unsafe_allow_html=True)
                            
                            if include_dashboard:
                                st.markdown(create_download_link(
                                    dashboard_data,
                                    f'dashboard_{timestamp}.html',
                                    "text/html"
                                ), unsafe_allow_html=True)
                            
                            if include_visualizations:
                                st.markdown(create_download_link(
                                    viz_zip_data,
                                    f'visualizations_{timestamp}.zip',
                                    "application/zip"
                                ), unsafe_allow_html=True)
                        
                        # Success message
                        st.markdown("""
                        <div class="success-message">
                            <h4>✅ Analysis Complete!</h4>
                            <p>Your analysis has been completed successfully. Download the reports above to view detailed results, charts, and recommendations.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                except Exception as e:
                    st.markdown(f"""
                    <div class="error-message">
                        <h4>❌ Analysis Failed</h4>
                        <p>Error: {str(e)}</p>
                        <p>Please check your file formats and try again.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    logger.error(f"Analysis failed: {str(e)}")
    
    else:
        # Instructions when files are not uploaded
        st.markdown('<h2 class="sub-header">📋 Instructions</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        ### How to Use This Tool
        
        1. **Upload Required Files** (use the sidebar):
           - **Units CSV**: Master record of all units
           - **Rentroll CSV**: Payment status for occupied units  
           - **Locks CSV**: Lock assignments for each unit
        
        2. **Configure Options** (optional):
           - Choose which reports to generate
           - Select analysis preferences
        
        3. **Run Analysis**:
           - Click the "Run Analysis" button
           - Wait for processing to complete
        
        4. **Download Results**:
           - Excel reports with formatting
           - Interactive dashboards
           - Priority alerts
           - Visualization files
        
        ### File Format Requirements
        
        **Units CSV:**
        - Column C: `Unit` (unit identifier)
        - Column G: `Status` (unit status)
        
        **Rentroll CSV:**
        - Column A: `Unit` (unit identifier)
        - Column S: `Days Past Due` (payment status)
        
        **Locks File (CSV or Excel):**
        - Column C: `Unit Number` (unit identifier)
        - Column E: `Status` (lock status)
        - Supports both CSV and Excel (.xlsx) formats
        """)
        
        # Sample data section
        with st.expander("📊 View Sample Data Structure"):
            st.markdown("**Sample Units CSV:**")
            sample_units = pd.DataFrame({
                'Unit': ['A001', 'A002', 'A003'],
                'Status': ['Occupied - Current', 'Vacant - Available', 'Occupied - Delinquent']
            })
            st.dataframe(sample_units)
            
            st.markdown("**Sample Rentroll CSV:**")
            sample_rentroll = pd.DataFrame({
                'Unit': ['A001', 'A003'],
                'Days Past Due': [0, 15]
            })
            st.dataframe(sample_rentroll)
            
            st.markdown("**Sample Locks File (CSV or Excel):**")
            sample_locks = pd.DataFrame({
                'Unit Number': ['A001', 'A002', 'A003'],
                'Status': ['Tenant Using Lock', 'Assigned Vacant', 'Assigned Overlock']
            })
            st.dataframe(sample_locks)
            st.markdown("*Note: This file can be uploaded as either CSV or Excel (.xlsx) format*")

if __name__ == "__main__":
    main()
