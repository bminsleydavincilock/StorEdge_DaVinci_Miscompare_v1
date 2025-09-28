# 🚀 StorEdge DaVinci Unit Status Analyzer v1

A comprehensive Python application for analyzing self-storage unit status and lock assignments to identify miscompares between expected and actual lock statuses.

## 🎯 Overview

This tool processes three CSV files to determine unit status and validate lock assignments:
- **units.csv**: Master record of all units with status information
- **rentroll.csv**: Payment status for occupied units  
- **locks.csv**: Lock assignments and status for each unit

The analyzer identifies miscompares where the actual lock status doesn't match the expected status based on unit occupancy and payment status.

## 🏗️ Project Structure

```
StorEdge_DaVinci_Miscompare_v1/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── main_analyzer.py            # Main application script
├── create_sample_data.py       # Sample data generator
├── src/                        # Source code
│   ├── unit_status_analyzer.py # Core analysis logic
│   └── report_generator.py     # Report and visualization generation
├── notebooks/                  # Jupyter notebooks
│   └── 01_data_exploration.ipynb
├── data/                       # Data files
│   ├── raw/                    # Raw CSV files
│   ├── processed/              # Processed data
│   └── external/               # External datasets
├── config/                     # Configuration files
└── tests/                      # Test files
```

## 🚀 Quick Start

### Option 1: Web Application (Recommended)

**Deploy to Streamlit Cloud:**
1. Push your code to GitHub
2. Connect to [Streamlit Cloud](https://share.streamlit.io)
3. Deploy with your repository
4. Share the web app URL with users

**Run Locally:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the web application
streamlit run streamlit_app.py
```

### Option 2: Command Line Interface

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run analysis
python main_analyzer.py --units units.csv --rentroll rentroll.csv --locks locks.csv

# With custom output directory
python main_analyzer.py --units units.csv --rentroll rentroll.csv --locks locks.csv --output ./results/
```

### Option 3: Generate Sample Data (Optional)

```bash
python create_sample_data.py
```

## 📊 Input File Requirements

### units.csv
- **Column C**: `Unit` - Unit identifier (e.g., "A001", "B123")
- **Column G**: `Status` - Unit status (evaluates first 3 characters: "Occ" = Occupied, "Vac" = Vacant)

### rentroll.csv  
- **Column A**: `Unit` - Unit identifier (matches units.csv)
- **Column S**: `Days Past Due` - Payment status (positive value = delinquent, empty/0 = current)

### locks.csv or locks.xlsx
- **Column C**: `Unit Number` - Unit identifier (matches units.csv)
- **Column E**: `Status` - Lock status (Assigned Vacant, Tenant Using Lock, Assigned Overlock, Assigned Auction)
- **Format**: Supports both CSV and Excel (.xlsx) formats

## 🎯 Analysis Logic

### Unit Status Determination
1. **Vacant**: Unit status starts with "Vac" OR unit not found in rentroll.csv
2. **Occupied-Current**: Unit status starts with "Occ" AND Days Past Due = 0/empty
3. **Occupied-Delinquent**: Unit status starts with "Occ" AND Days Past Due > 0

### Expected Lock Status
- **Vacant Units**: Should have "Assigned Vacant" lock
- **Occupied-Current Units**: Should have "Tenant Using Lock" 
- **Occupied-Delinquent Units**: Should have "Assigned Overlock" OR "Assigned Auction"

### Miscompare Detection
The tool flags units where actual lock status doesn't match expected status, with severity levels:
- **HIGH**: Critical mismatches requiring immediate attention
- **MEDIUM**: Status mismatches that need review

## 📈 Output Reports

The analyzer generates comprehensive reports including:

1. **Enhanced Excel Report** (`enhanced_analysis_report.xlsx`)
   - **Executive Summary**: Key metrics and overview
   - **Complete Analysis**: All data with conditional formatting
   - **Miscompares**: Priority-sorted issues with recommended actions
   - **High Severity Issues**: Critical problems highlighted in red
   - **Unit Status Breakdown**: Distribution with pie charts
   - **Lock Status Breakdown**: Distribution with bar charts
   - **Detailed Analysis**: Cross-tabulation tables
   - **Recommendations**: Actionable items with priority levels
   - **Professional Formatting**: Colors, borders, and charts

2. **Standard Excel Report** (`detailed_analysis_report.xlsx`)
   - Complete analysis results
   - Summary statistics
   - Miscompares breakdown
   - High severity issues

3. **Interactive Dashboard** (`analysis_dashboard.html`)
   - Unit status distribution
   - Lock status analysis
   - Miscompare visualizations
   - Cross-tabulation charts

4. **Priority Alerts** (`priority_alerts.csv`)
   - Units requiring immediate attention
   - Recommended actions
   - Severity prioritization

5. **Visualization Suite** (`visualizations/` folder)
   - Individual charts and graphs
   - High-resolution images for presentations

## 🛠️ Advanced Usage

### Command Line Options

```bash
python main_analyzer.py --help

Options:
  --units UNITS           Path to units.csv file
  --rentroll RENTROLL     Path to rentroll.csv file  
  --locks LOCKS          Path to locks.csv file
  --output OUTPUT        Output directory (default: ./output)
  --log-level LEVEL      Logging level (DEBUG, INFO, WARNING, ERROR)
  --no-dashboard         Skip generating interactive dashboard
  --no-visualizations    Skip generating individual visualization files
```

### Excel Export Tool

```bash
# Export from existing analysis results
python export_to_excel.py --input complete_analysis_results.csv --output report.xlsx

# Run new analysis and export to Excel
python export_to_excel.py --units units.csv --rentroll rentroll.csv --locks locks.csv --output report.xlsx
```

### Programmatic Usage

```python
from src.unit_status_analyzer import UnitStatusAnalyzer
from src.report_generator import ReportGenerator
from src.enhanced_excel_exporter import EnhancedExcelExporter

# Initialize analyzer
analyzer = UnitStatusAnalyzer()

# Run analysis
results = analyzer.run_analysis('units.csv', 'rentroll.csv', 'locks.csv')

# Generate standard reports
report_gen = ReportGenerator(results)
report_gen.create_detailed_report('analysis_report.xlsx')
report_gen.create_summary_dashboard('dashboard.html')

# Generate enhanced Excel report
excel_exporter = EnhancedExcelExporter()
excel_exporter.create_enhanced_report(results, 'enhanced_report.xlsx')
```

## 📊 Key Features

### Core Analysis
- ✅ **Automated Status Detection**: Intelligently parses unit status from various formats
- ✅ **Payment Status Analysis**: Determines current vs delinquent status from rentroll data
- ✅ **Lock Assignment Validation**: Validates lock status against expected assignments
- ✅ **Miscompare Detection**: Identifies discrepancies with severity classification

### Web Application
- ✅ **User-Friendly Interface**: Drag-and-drop file upload with validation
- ✅ **Real-Time Analysis**: Instant processing with progress indicators
- ✅ **Interactive Results**: Live charts and data tables
- ✅ **Download Reports**: Multiple formats (Excel, HTML, CSV, Images)
- ✅ **Cloud Deployment**: Ready for Streamlit Cloud deployment

### Reporting & Visualization
- ✅ **Enhanced Excel Reports**: Professional formatting with charts and conditional formatting
- ✅ **Interactive Dashboards**: Plotly-based visualizations for data exploration
- ✅ **Priority Alerts**: Actionable recommendations for immediate issues
- ✅ **Multiple Output Formats**: Excel, HTML, CSV, PNG images

### Technical Features
- ✅ **Error Handling**: Robust validation and error reporting
- ✅ **Logging**: Detailed logging for troubleshooting and audit trails
- ✅ **Database Integration**: Supabase integration for data storage
- ✅ **Scalable Architecture**: Modular design for easy maintenance

## 🔧 Troubleshooting

### Common Issues

1. **File Not Found**: Ensure CSV files exist and paths are correct
2. **Column Mismatch**: Verify column headers match requirements exactly
3. **Data Format Issues**: Check for special characters or encoding problems
4. **Memory Issues**: For large datasets, consider processing in chunks

### Log Files

Check `unit_analysis.log` for detailed execution logs and error messages.

## 📚 Dependencies

- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- seaborn >= 0.12.0
- plotly >= 5.15.0
- openpyxl >= 3.1.0

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
