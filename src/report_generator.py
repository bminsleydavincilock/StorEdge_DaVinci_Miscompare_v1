"""
Report Generator for StorEdge DaVinci Unit Status Analysis

This module generates comprehensive reports and visualizations for unit status analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates comprehensive reports and visualizations for unit status analysis."""
    
    def __init__(self, analyzer_results: pd.DataFrame):
        """
        Initialize the report generator.
        
        Args:
            analyzer_results (pd.DataFrame): Results from UnitStatusAnalyzer
        """
        self.df = analyzer_results.copy()
        self.setup_plotting_style()
    
    def setup_plotting_style(self):
        """Set up consistent plotting styles."""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Define colors for different statuses
        self.colors = {
            'Vacant': '#2E8B57',  # Sea Green
            'Occupied-Current': '#4169E1',  # Royal Blue
            'Occupied-Delinquent': '#DC143C',  # Crimson
            'Assigned Vacant': '#90EE90',  # Light Green
            'Tenant Using Lock': '#87CEEB',  # Sky Blue
            'Assigned Overlock': '#FFB6C1',  # Light Pink
            'Assigned Auction': '#FF6347',  # Tomato
            'No Lock Assigned': '#D3D3D3'  # Light Gray
        }
    
    def create_summary_dashboard(self, output_path: str = None):
        """
        Create a comprehensive summary dashboard.
        
        Args:
            output_path (str): Path to save the dashboard HTML file
        """
        logger.info("Creating summary dashboard...")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Unit Status Distribution',
                'Lock Status Distribution', 
                'Miscompare Severity',
                'Unit Status vs Lock Status',
                'Miscompares by Unit Status',
                'Daily Miscompare Trend'
            ],
            specs=[
                [{"type": "pie"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "bar"}]
            ]
        )
        
        # 1. Unit Status Distribution (Pie Chart)
        unit_status_counts = self.df['Final_Status'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=unit_status_counts.index,
                values=unit_status_counts.values,
                name="Unit Status",
                marker_colors=[self.colors.get(status, '#808080') for status in unit_status_counts.index]
            ),
            row=1, col=1
        )
        
        # 2. Lock Status Distribution (Pie Chart)
        lock_status_counts = self.df['Actual_Lock_Status'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=lock_status_counts.index,
                values=lock_status_counts.values,
                name="Lock Status",
                marker_colors=[self.colors.get(status, '#808080') for status in lock_status_counts.index]
            ),
            row=1, col=2
        )
        
        # 3. Miscompare Severity (Bar Chart)
        severity_counts = self.df['Miscompare_Severity'].value_counts()
        fig.add_trace(
            go.Bar(
                x=severity_counts.index,
                y=severity_counts.values,
                name="Miscompare Severity",
                marker_color=['#DC143C' if 'HIGH' in str(x) else '#FF6347' if 'MEDIUM' in str(x) else '#2E8B57' 
                             for x in severity_counts.index]
            ),
            row=2, col=1
        )
        
        # 4. Unit Status vs Lock Status (Bar Chart)
        cross_tab = pd.crosstab(self.df['Final_Status'], self.df['Actual_Lock_Status'])
        for lock_status in cross_tab.columns:
            fig.add_trace(
                go.Bar(
                    x=cross_tab.index,
                    y=cross_tab[lock_status],
                    name=lock_status,
                    marker_color=self.colors.get(lock_status, '#808080')
                ),
                row=2, col=2
            )
        
        # 5. Miscompares by Unit Status (Scatter Plot)
        miscompares = self.df[self.df['Is_Miscompare'] == True]
        if not miscompares.empty:
            fig.add_trace(
                go.Scatter(
                    x=miscompares['Final_Status'],
                    y=miscompares['Actual_Lock_Status'],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color='#DC143C',
                        symbol='x'
                    ),
                    name="Miscompares",
                    text=miscompares['Unit'],
                    hovertemplate="Unit: %{text}<br>Status: %{x}<br>Lock: %{y}<extra></extra>"
                ),
                row=3, col=1
            )
        
        # 6. Miscompare Rate by Status (Bar Chart)
        miscompare_rate = self.df.groupby('Final_Status')['Is_Miscompare'].mean() * 100
        fig.add_trace(
            go.Bar(
                x=miscompare_rate.index,
                y=miscompare_rate.values,
                name="Miscompare Rate %",
                marker_color=['#DC143C' if x > 10 else '#FF6347' if x > 5 else '#2E8B57' 
                             for x in miscompare_rate.values]
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="StorEdge DaVinci Unit Status Analysis Dashboard",
            title_x=0.5,
            height=1200,
            showlegend=True
        )
        
        # Save dashboard
        if output_path:
            fig.write_html(output_path)
            logger.info(f"Dashboard saved to {output_path}")
        
        return fig
    
    def create_detailed_report(self, output_path: str):
        """
        Create a detailed Excel report with multiple sheets.
        
        Args:
            output_path (str): Path to save the Excel report
        """
        logger.info("Creating detailed Excel report...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main analysis results
            self.df.to_excel(writer, sheet_name='Complete_Analysis', index=False)
            
            # Summary statistics
            summary_data = self._create_summary_data()
            summary_df = pd.DataFrame(list(summary_data.items()), columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Miscompares only
            miscompares = self.df[self.df['Is_Miscompare'] == True]
            if not miscompares.empty:
                miscompares.to_excel(writer, sheet_name='Miscompares', index=False)
            
            # High severity miscompares
            high_severity = miscompares[miscompares['Miscompare_Severity'].str.contains('HIGH', na=False)]
            if not high_severity.empty:
                high_severity.to_excel(writer, sheet_name='High_Severity', index=False)
            
            # Unit status breakdown
            status_breakdown = self.df['Final_Status'].value_counts().reset_index()
            status_breakdown.columns = ['Status', 'Count']
            status_breakdown.to_excel(writer, sheet_name='Status_Breakdown', index=False)
            
            # Lock status breakdown
            lock_breakdown = self.df['Actual_Lock_Status'].value_counts().reset_index()
            lock_breakdown.columns = ['Lock_Status', 'Count']
            lock_breakdown.to_excel(writer, sheet_name='Lock_Breakdown', index=False)
        
        logger.info(f"Detailed report saved to {output_path}")
    
    def _create_summary_data(self) -> dict:
        """Create summary statistics for the report."""
        total_units = len(self.df)
        miscompare_count = self.df['Is_Miscompare'].sum()
        miscompare_rate = (miscompare_count / total_units) * 100
        
        summary = {
            'Total Units': total_units,
            'Total Miscompares': miscompare_count,
            'Miscompare Rate (%)': round(miscompare_rate, 2),
            'Vacant Units': len(self.df[self.df['Final_Status'] == 'Vacant']),
            'Occupied-Current Units': len(self.df[self.df['Final_Status'] == 'Occupied-Current']),
            'Occupied-Delinquent Units': len(self.df[self.df['Final_Status'] == 'Occupied-Delinquent']),
            'High Severity Miscompares': len(self.df[self.df['Miscompare_Severity'].str.contains('HIGH', na=False)]),
            'Medium Severity Miscompares': len(self.df[self.df['Miscompare_Severity'].str.contains('MEDIUM', na=False)])
        }
        
        return summary
    
    def create_visualization_suite(self, output_dir: str):
        """
        Create a suite of individual visualizations.
        
        Args:
            output_dir (str): Directory to save visualization files
        """
        logger.info("Creating visualization suite...")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Unit Status Distribution
        self._create_unit_status_chart(output_path / 'unit_status_distribution.png')
        
        # 2. Lock Status Distribution
        self._create_lock_status_chart(output_path / 'lock_status_distribution.png')
        
        # 3. Miscompare Analysis
        self._create_miscompare_chart(output_path / 'miscompare_analysis.png')
        
        # 4. Cross-tabulation Heatmap
        self._create_heatmap(output_path / 'status_cross_tabulation.png')
        
        logger.info(f"Visualization suite saved to {output_dir}")
    
    def _create_unit_status_chart(self, output_path: Path):
        """Create unit status distribution chart."""
        plt.figure(figsize=(10, 6))
        status_counts = self.df['Final_Status'].value_counts()
        colors = [self.colors.get(status, '#808080') for status in status_counts.index]
        
        plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title('Unit Status Distribution', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_lock_status_chart(self, output_path: Path):
        """Create lock status distribution chart."""
        plt.figure(figsize=(12, 6))
        lock_counts = self.df['Actual_Lock_Status'].value_counts()
        colors = [self.colors.get(status, '#808080') for status in lock_counts.index]
        
        bars = plt.bar(lock_counts.index, lock_counts.values, color=colors)
        plt.title('Lock Status Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Lock Status')
        plt.ylabel('Number of Units')
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_miscompare_chart(self, output_path: Path):
        """Create miscompare analysis chart."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Miscompare count by status
        miscompare_by_status = self.df.groupby('Final_Status')['Is_Miscompare'].sum()
        colors = [self.colors.get(status, '#808080') for status in miscompare_by_status.index]
        
        bars1 = ax1.bar(miscompare_by_status.index, miscompare_by_status.values, color=colors)
        ax1.set_title('Miscompares by Unit Status', fontweight='bold')
        ax1.set_ylabel('Number of Miscompares')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        # Miscompare rate by status
        miscompare_rate = self.df.groupby('Final_Status')['Is_Miscompare'].mean() * 100
        colors = ['#DC143C' if x > 10 else '#FF6347' if x > 5 else '#2E8B57' 
                 for x in miscompare_rate.values]
        
        bars2 = ax2.bar(miscompare_rate.index, miscompare_rate.values, color=colors)
        ax2.set_title('Miscompare Rate by Unit Status', fontweight='bold')
        ax2.set_ylabel('Miscompare Rate (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_heatmap(self, output_path: Path):
        """Create cross-tabulation heatmap."""
        plt.figure(figsize=(12, 8))
        
        # Create cross-tabulation
        cross_tab = pd.crosstab(self.df['Final_Status'], self.df['Actual_Lock_Status'])
        
        # Create heatmap
        sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Number of Units'})
        plt.title('Unit Status vs Lock Status Cross-Tabulation', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Lock Status')
        plt.ylabel('Unit Status')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_alert_report(self) -> pd.DataFrame:
        """
        Generate a prioritized alert report for immediate action.
        
        Returns:
            pd.DataFrame: Prioritized alerts
        """
        logger.info("Generating alert report...")
        
        miscompares = self.df[self.df['Is_Miscompare'] == True].copy()
        
        if miscompares.empty:
            logger.info("No miscompares found - no alerts to generate")
            return pd.DataFrame()
        
        # Prioritize alerts
        priority_order = {
            'HIGH - Vacant unit with tenant lock': 1,
            'HIGH - Current tenant without proper lock': 2,
            'HIGH - Delinquent unit without lock': 3,
            'MEDIUM - Lock status mismatch': 4
        }
        
        miscompares['Priority'] = miscompares['Miscompare_Severity'].map(priority_order)
        miscompares = miscompares.sort_values('Priority')
        
        # Add recommended actions
        def get_recommended_action(row):
            severity = row['Miscompare_Severity']
            if 'Vacant unit with tenant lock' in severity:
                return 'Remove tenant lock and verify unit is truly vacant'
            elif 'Current tenant without proper lock' in severity:
                return 'Install proper tenant lock immediately'
            elif 'Delinquent unit without lock' in severity:
                return 'Install overlock or proceed to auction'
            else:
                return 'Review lock assignment and correct as needed'
        
        miscompares['Recommended_Action'] = miscompares.apply(get_recommended_action, axis=1)
        
        # Select relevant columns for alert report
        alert_columns = [
            'Unit', 'Final_Status', 'Actual_Lock_Status', 'Expected_Lock_Status',
            'Miscompare_Severity', 'Priority', 'Recommended_Action'
        ]
        
        return miscompares[alert_columns]
