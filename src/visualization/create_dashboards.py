"""
Visualization Module for Mental Health Service Analysis
Creates comprehensive visualizations and dashboards
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8-darkgrid')


class MentalHealthVisualizer:
    """Create visualizations for mental health service analysis"""
    
    def __init__(self, data_path=None):
        """
        Initialize visualizer
        
        Args:
            data_path: Path to data file (optional)
        """
        self.df = None
        if data_path:
            self.load_data(data_path)
        
        # Color palettes
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8'
        }
    
    def load_data(self, file_path):
        """Load data from CSV"""
        self.df = pd.read_csv(file_path)
        self.df['appointment_date'] = pd.to_datetime(self.df['appointment_date'])
        print(f"Loaded {len(self.df)} records")
    
    def plot_service_utilization_trends(self, save_path=None):
        """Plot service utilization trends over time"""
        # Aggregate by month and service category
        monthly_data = self.df.copy()
        monthly_data['year_month'] = monthly_data['appointment_date'].dt.to_period('M')
        
        trend_data = monthly_data.groupby(['year_month', 'service_type']).size().reset_index(name='count')
        trend_data['year_month'] = trend_data['year_month'].astype(str)
        
        # Create interactive plot
        fig = px.line(
            trend_data, 
            x='year_month', 
            y='count', 
            color='service_type',
            title='Mental Health Service Utilization Trends',
            labels={'year_month': 'Month', 'count': 'Number of Appointments', 'service_type': 'Service Type'}
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500,
            hovermode='x unified'
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def plot_demographic_distribution(self, save_path=None):
        """Plot service usage by demographics"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('By Student Year', 'By College', 
                          'International Students', 'First Generation'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'pie'}]]
        )
        
        # By student year
        year_counts = self.df['student_year'].value_counts()
        fig.add_trace(
            go.Bar(x=year_counts.index, y=year_counts.values, name='Student Year',
                  marker_color=self.colors['primary']),
            row=1, col=1
        )
        
        # By college
        college_counts = self.df['student_college'].value_counts()
        fig.add_trace(
            go.Bar(x=college_counts.index, y=college_counts.values, name='College',
                  marker_color=self.colors['secondary']),
            row=1, col=2
        )
        
        # International students
        intl_counts = self.df['international_student'].value_counts()
        fig.add_trace(
            go.Pie(labels=['Domestic', 'International'], values=intl_counts.values,
                  marker=dict(colors=[self.colors['info'], self.colors['warning']])),
            row=2, col=1
        )
        
        # First generation
        first_gen_counts = self.df['first_generation'].value_counts()
        fig.add_trace(
            go.Pie(labels=['Not First Gen', 'First Gen'], values=first_gen_counts.values,
                  marker=dict(colors=[self.colors['success'], self.colors['danger']])),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Service Usage by Demographics", showlegend=False)
        fig.update_xaxes(tickangle=-45, row=1, col=2)
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def plot_wait_time_analysis(self, save_path=None):
        """Analyze and visualize wait times"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Wait Time Distribution', 'Wait Times by Service Type',
                          'Wait Times Over Time', 'Wait Time vs No-Show Rate'),
            specs=[[{'type': 'histogram'}, {'type': 'box'}],
                   [{'type': 'scatter'}, {'type': 'scatter'}]]
        )
        
        # Wait time distribution
        fig.add_trace(
            go.Histogram(x=self.df['wait_days'], nbinsx=30, name='Wait Days',
                        marker_color=self.colors['primary']),
            row=1, col=1
        )
        
        # Wait times by service type
        for service in self.df['service_type'].unique():
            service_data = self.df[self.df['service_type'] == service]['wait_days']
            fig.add_trace(
                go.Box(y=service_data, name=service),
                row=1, col=2
            )
        
        # Wait times over time
        monthly_wait = self.df.copy()
        monthly_wait['year_month'] = monthly_wait['appointment_date'].dt.to_period('M').astype(str)
        wait_trend = monthly_wait.groupby('year_month')['wait_days'].mean().reset_index()
        
        fig.add_trace(
            go.Scatter(x=wait_trend['year_month'], y=wait_trend['wait_days'],
                      mode='lines+markers', name='Avg Wait Time',
                      line=dict(color=self.colors['danger'])),
            row=2, col=1
        )
        
        # Wait time vs no-show rate
        wait_bins = pd.cut(self.df['wait_days'], bins=[0, 3, 7, 14, 30])
        no_show_rate = self.df.groupby(wait_bins)['no_show'].mean() * 100
        
        fig.add_trace(
            go.Scatter(x=[str(x) for x in no_show_rate.index], y=no_show_rate.values,
                      mode='lines+markers', name='No-Show Rate',
                      line=dict(color=self.colors['warning'])),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Wait Time Analysis", showlegend=False)
        fig.update_xaxes(title_text="Days", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Days", row=1, col=2)
        fig.update_xaxes(title_text="Month", row=2, col=1, tickangle=-45)
        fig.update_yaxes(title_text="Avg Wait (days)", row=2, col=1)
        fig.update_xaxes(title_text="Wait Time Range", row=2, col=2)
        fig.update_yaxes(title_text="No-Show Rate (%)", row=2, col=2)
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def plot_service_gaps_heatmap(self, save_path=None):
        """Create heatmap showing service gaps by college and service type"""
        # Calculate average wait time by college and service type
        gap_matrix = self.df.groupby(['student_college', 'service_type'])['wait_days'].mean().reset_index()
        gap_pivot = gap_matrix.pivot(index='student_college', columns='service_type', values='wait_days')
        
        fig = go.Figure(data=go.Heatmap(
            z=gap_pivot.values,
            x=gap_pivot.columns,
            y=gap_pivot.index,
            colorscale='RdYlGn_r',
            text=gap_pivot.values.round(1),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Avg Wait<br>(days)")
        ))
        
        fig.update_layout(
            title='Service Gaps: Average Wait Time by College and Service Type',
            xaxis_title='Service Type',
            yaxis_title='College',
            height=600,
            xaxis_tickangle=-45
        )
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def plot_counselor_workload(self, save_path=None):
        """Visualize counselor workload distribution"""
        # Aggregate counselor data
        counselor_stats = self.df.groupby('counselor_id').agg({
            'student_id': 'count',
            'duration_minutes': 'sum'
        }).reset_index()
        counselor_stats.columns = ['counselor_id', 'appointments', 'total_minutes']
        counselor_stats['total_hours'] = counselor_stats['total_minutes'] / 60
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Appointments per Counselor', 'Hours per Counselor')
        )
        
        # Appointments distribution
        fig.add_trace(
            go.Histogram(x=counselor_stats['appointments'], nbinsx=20,
                        marker_color=self.colors['primary'], name='Appointments'),
            row=1, col=1
        )
        
        # Hours distribution
        fig.add_trace(
            go.Histogram(x=counselor_stats['total_hours'], nbinsx=20,
                        marker_color=self.colors['secondary'], name='Hours'),
            row=1, col=2
        )
        
        fig.update_layout(height=400, title_text="Counselor Workload Distribution", showlegend=False)
        fig.update_xaxes(title_text="Number of Appointments", row=1, col=1)
        fig.update_xaxes(title_text="Total Hours", row=1, col=2)
        
        if save_path:
            fig.write_html(save_path)
        
        return fig
    
    def create_executive_dashboard(self, save_path='outputs/executive_dashboard.html'):
        """Create comprehensive executive dashboard"""
        # Calculate KPIs
        total_students = self.df['student_id'].nunique()
        total_appointments = len(self.df)
        avg_wait = self.df['wait_days'].mean()
        no_show_rate = self.df['no_show'].mean() * 100
        
        # Create dashboard
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Key Performance Indicators',
                'Service Utilization Trend',
                'Wait Time by Service Type',
                'Demographics Overview',
                'Service Gaps Heatmap',
                'Counselor Workload'
            ),
            specs=[
                [{'type': 'indicator'}, {'type': 'scatter'}],
                [{'type': 'box'}, {'type': 'bar'}],
                [{'type': 'heatmap', 'colspan': 2}, None]
            ],
            row_heights=[0.25, 0.35, 0.4]
        )
        
        # KPIs
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=total_students,
                title={'text': f"Unique Students<br>Avg Wait: {avg_wait:.1f} days<br>No-Show: {no_show_rate:.1f}%"},
                domain={'x': [0, 1], 'y': [0, 1]}
            ),
            row=1, col=1
        )
        
        # Trend
        monthly = self.df.copy()
        monthly['month'] = monthly['appointment_date'].dt.to_period('M').astype(str)
        trend = monthly.groupby('month').size().reset_index(name='count')
        
        fig.add_trace(
            go.Scatter(x=trend['month'], y=trend['count'], mode='lines+markers',
                      line=dict(color=self.colors['primary'])),
            row=1, col=2
        )
        
        # Wait times by service
        for service in self.df['service_type'].unique()[:5]:  # Top 5
            data = self.df[self.df['service_type'] == service]['wait_days']
            fig.add_trace(go.Box(y=data, name=service), row=2, col=1)
        
        # Demographics
        year_counts = self.df['student_year'].value_counts()
        fig.add_trace(
            go.Bar(x=year_counts.index, y=year_counts.values,
                  marker_color=self.colors['secondary']),
            row=2, col=2
        )
        
        # Heatmap
        gap_matrix = self.df.groupby(['student_college', 'service_type'])['wait_days'].mean().reset_index()
        gap_pivot = gap_matrix.pivot(index='student_college', columns='service_type', values='wait_days')
        
        fig.add_trace(
            go.Heatmap(
                z=gap_pivot.values,
                x=gap_pivot.columns,
                y=gap_pivot.index,
                colorscale='RdYlGn_r'
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            height=1200,
            title_text="Mental Health Services - Executive Dashboard",
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
            print(f"Dashboard saved to {save_path}")
        
        return fig
    
    def generate_all_visualizations(self, output_dir='outputs/visualizations'):
        """Generate all visualizations"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print("Generating visualizations...")
        
        self.plot_service_utilization_trends(f"{output_dir}/utilization_trends.html")
        print("✓ Utilization trends")
        
        self.plot_demographic_distribution(f"{output_dir}/demographics.html")
        print("✓ Demographics")
        
        self.plot_wait_time_analysis(f"{output_dir}/wait_times.html")
        print("✓ Wait time analysis")
        
        self.plot_service_gaps_heatmap(f"{output_dir}/service_gaps.html")
        print("✓ Service gaps heatmap")
        
        self.plot_counselor_workload(f"{output_dir}/counselor_workload.html")
        print("✓ Counselor workload")
        
        self.create_executive_dashboard(f"{output_dir}/executive_dashboard.html")
        print("✓ Executive dashboard")
        
        print(f"\nAll visualizations saved to {output_dir}/")


def main():
    """Generate visualizations"""
    viz = MentalHealthVisualizer('/home/claude/unt-mental-health-analysis/data/raw/mental_health_data.csv')
    viz.generate_all_visualizations('/home/claude/unt-mental-health-analysis/outputs/visualizations')


if __name__ == "__main__":
    main()
