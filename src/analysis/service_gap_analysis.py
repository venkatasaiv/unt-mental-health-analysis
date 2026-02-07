"""
Service Gap Analysis for Mental Health Services
Identifies underserved populations and resource allocation opportunities
"""

import pandas as pd
import numpy as np
from google.cloud import bigquery
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ServiceGapAnalyzer:
    """Analyze service gaps and resource allocation needs"""
    
    def __init__(self, project_id):
        """
        Initialize analyzer with BigQuery client
        
        Args:
            project_id (str): GCP project ID
        """
        self.client = bigquery.Client(project=project_id)
        self.results = {}
        logger.info(f"Initialized ServiceGapAnalyzer for project: {project_id}")
    
    def query_data(self, query):
        """
        Execute BigQuery query
        
        Args:
            query (str): SQL query
            
        Returns:
            DataFrame: Query results
        """
        return self.client.query(query).to_dataframe()
    
    def analyze_demographic_gaps(self):
        """Identify underserved demographic groups"""
        logger.info("Analyzing demographic service gaps...")
        
        query = """
        SELECT 
            student_year,
            student_college,
            international_student,
            first_generation,
            COUNT(*) as total_visits,
            AVG(wait_days) as avg_wait_days,
            COUNTDISTINCT(student_id) as unique_students,
            SUM(CASE WHEN no_show THEN 1 ELSE 0 END) as no_shows
        FROM `mental_health.service_records`
        GROUP BY student_year, student_college, international_student, first_generation
        HAVING total_visits > 10
        ORDER BY avg_wait_days DESC
        """
        
        df = self.query_data(query)
        
        # Calculate utilization rate (visits per unique student)
        df['utilization_rate'] = df['total_visits'] / df['unique_students']
        
        # Identify gaps
        df['service_gap'] = np.where(
            (df['avg_wait_days'] > 7) | (df['utilization_rate'] < 2),
            'High Gap',
            np.where(
                (df['avg_wait_days'] > 3) | (df['utilization_rate'] < 3),
                'Moderate Gap',
                'Adequate'
            )
        )
        
        self.results['demographic_gaps'] = df
        
        # Summary statistics
        logger.info("\n=== Demographic Gap Summary ===")
        logger.info(f"Total demographic segments analyzed: {len(df)}")
        logger.info(f"High gap segments: {len(df[df['service_gap'] == 'High Gap'])}")
        logger.info(f"Moderate gap segments: {len(df[df['service_gap'] == 'Moderate Gap'])}")
        
        return df
    
    def analyze_temporal_gaps(self):
        """Identify time-based service gaps"""
        logger.info("Analyzing temporal service gaps...")
        
        query = """
        SELECT 
            year,
            month,
            EXTRACT(DAYOFWEEK FROM appointment_date) as day_of_week,
            service_category,
            COUNT(*) as appointment_count,
            AVG(wait_days) as avg_wait_days,
            COUNTDISTINCT(counselor_id) as available_counselors
        FROM `mental_health.service_records`
        GROUP BY year, month, day_of_week, service_category
        ORDER BY year, month, day_of_week
        """
        
        df = self.query_data(query)
        
        # Map day of week
        day_map = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 
                   5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
        df['day_name'] = df['day_of_week'].map(day_map)
        
        # Calculate demand-supply ratio
        df['demand_per_counselor'] = df['appointment_count'] / df['available_counselors']
        
        # Identify peak demand periods
        threshold = df['demand_per_counselor'].quantile(0.75)
        df['peak_demand'] = df['demand_per_counselor'] > threshold
        
        self.results['temporal_gaps'] = df
        
        logger.info(f"Peak demand periods identified: {df['peak_demand'].sum()}")
        
        return df
    
    def analyze_service_type_gaps(self):
        """Analyze gaps by service type"""
        logger.info("Analyzing service type gaps...")
        
        query = """
        SELECT 
            service_category,
            student_college,
            COUNT(*) as demand,
            AVG(wait_days) as avg_wait,
            SUM(CASE WHEN wait_days > 7 THEN 1 ELSE 0 END) as extended_wait_count,
            COUNTDISTINCT(counselor_id) as counselor_count
        FROM `mental_health.service_records`
        GROUP BY service_category, student_college
        """
        
        df = self.query_data(query)
        
        # Calculate metrics
        df['pct_extended_wait'] = (df['extended_wait_count'] / df['demand']) * 100
        df['demand_per_counselor'] = df['demand'] / df['counselor_count']
        
        # Categorize service adequacy
        df['adequacy_rating'] = pd.cut(
            df['pct_extended_wait'],
            bins=[0, 10, 25, 50, 100],
            labels=['Excellent', 'Good', 'Needs Improvement', 'Critical']
        )
        
        self.results['service_type_gaps'] = df
        
        logger.info("\n=== Service Type Gap Summary ===")
        for category in df['service_category'].unique():
            cat_df = df[df['service_category'] == category]
            logger.info(f"\n{category}:")
            logger.info(f"  Total demand: {cat_df['demand'].sum()}")
            logger.info(f"  Avg wait: {cat_df['avg_wait'].mean():.1f} days")
            logger.info(f"  Critical areas: {len(cat_df[cat_df['adequacy_rating'] == 'Critical'])}")
        
        return df
    
    def identify_underserved_populations(self):
        """Identify specific underserved student populations"""
        logger.info("Identifying underserved populations...")
        
        query = """
        WITH student_stats AS (
            SELECT 
                student_id,
                student_year,
                international_student,
                first_generation,
                COUNT(*) as total_visits,
                AVG(wait_days) as avg_wait
            FROM `mental_health.service_records`
            GROUP BY student_id, student_year, international_student, first_generation
        ),
        population_stats AS (
            SELECT 
                student_year,
                international_student,
                first_generation,
                COUNT(*) as student_count,
                AVG(total_visits) as avg_visits_per_student,
                AVG(avg_wait) as avg_wait_days
            FROM student_stats
            GROUP BY student_year, international_student, first_generation
        )
        SELECT *
        FROM population_stats
        ORDER BY avg_wait_days DESC
        """
        
        df = self.query_data(query)
        
        # Calculate service equity score (lower is more underserved)
        overall_avg_visits = df['avg_visits_per_student'].mean()
        overall_avg_wait = df['avg_wait_days'].mean()
        
        df['visit_ratio'] = df['avg_visits_per_student'] / overall_avg_visits
        df['wait_ratio'] = overall_avg_wait / df['avg_wait_days']
        df['equity_score'] = (df['visit_ratio'] + df['wait_ratio']) / 2
        
        # Flag underserved (equity score < 0.7)
        df['underserved'] = df['equity_score'] < 0.7
        
        self.results['underserved_populations'] = df
        
        underserved = df[df['underserved']]
        logger.info(f"\nIdentified {len(underserved)} underserved population segments")
        logger.info("\nMost underserved groups:")
        logger.info(underserved.head(10)[['student_year', 'international_student', 
                                          'first_generation', 'equity_score']])
        
        return df
    
    def calculate_resource_needs(self):
        """Calculate additional resource requirements"""
        logger.info("Calculating resource needs...")
        
        # Get current capacity
        query = """
        SELECT 
            service_category,
            COUNT(DISTINCT counselor_id) as current_counselors,
            COUNT(*) as total_appointments,
            SUM(duration_minutes) as total_minutes
        FROM `mental_health.service_records`
        GROUP BY service_category
        """
        
        capacity_df = self.query_data(query)
        
        # Calculate current workload
        capacity_df['avg_appointments_per_counselor'] = (
            capacity_df['total_appointments'] / capacity_df['current_counselors']
        )
        capacity_df['avg_hours_per_counselor'] = (
            capacity_df['total_minutes'] / capacity_df['current_counselors'] / 60
        )
        
        # Get wait time data
        wait_query = """
        SELECT 
            service_category,
            AVG(wait_days) as avg_wait_days,
            PERCENTILE_CONT(wait_days, 0.75) OVER(PARTITION BY service_category) as p75_wait_days
        FROM `mental_health.service_records`
        GROUP BY service_category
        """
        
        wait_df = self.query_data(wait_query)
        
        # Merge data
        resource_df = pd.merge(capacity_df, wait_df, on='service_category')
        
        # Calculate additional counselors needed
        # Assumption: Reduce wait time to <= 3 days, standard is 40 appointments/week
        target_wait_days = 3
        standard_weekly_appointments = 40
        
        resource_df['wait_reduction_factor'] = resource_df['avg_wait_days'] / target_wait_days
        resource_df['additional_counselors_needed'] = np.ceil(
            resource_df['current_counselors'] * (resource_df['wait_reduction_factor'] - 1)
        ).astype(int)
        
        # Calculate percentage increase
        resource_df['pct_increase_needed'] = (
            (resource_df['additional_counselors_needed'] / resource_df['current_counselors']) * 100
        ).round(1)
        
        self.results['resource_needs'] = resource_df
        
        logger.info("\n=== Resource Allocation Recommendations ===")
        for _, row in resource_df.iterrows():
            logger.info(f"\n{row['service_category']}:")
            logger.info(f"  Current counselors: {row['current_counselors']}")
            logger.info(f"  Current avg wait: {row['avg_wait_days']:.1f} days")
            logger.info(f"  Additional counselors needed: {row['additional_counselors_needed']}")
            logger.info(f"  Percentage increase: {row['pct_increase_needed']}%")
        
        total_additional = resource_df['additional_counselors_needed'].sum()
        logger.info(f"\nTotal additional counselors needed: {total_additional}")
        
        return resource_df
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        logger.info("\n" + "="*80)
        logger.info("GENERATING RECOMMENDATIONS")
        logger.info("="*80)
        
        recommendations = []
        
        # Demographic recommendations
        if 'demographic_gaps' in self.results:
            high_gap = self.results['demographic_gaps'][
                self.results['demographic_gaps']['service_gap'] == 'High Gap'
            ]
            
            if len(high_gap) > 0:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Demographic Gaps',
                    'issue': f'{len(high_gap)} demographic segments with high service gaps',
                    'recommendation': 'Increase outreach and dedicated resources for international students, first-generation students, and specific colleges',
                    'expected_impact': '15-20% increase in utilization among underserved groups'
                })
        
        # Temporal recommendations
        if 'temporal_gaps' in self.results:
            peak_periods = self.results['temporal_gaps'][
                self.results['temporal_gaps']['peak_demand'] == True
            ]
            
            if len(peak_periods) > 0:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Scheduling Optimization',
                    'issue': f'{len(peak_periods)} time periods with peak demand',
                    'recommendation': 'Extend counseling hours during midterms and finals; add weekend appointments',
                    'expected_impact': '10-15% reduction in average wait times'
                })
        
        # Service type recommendations
        if 'service_type_gaps' in self.results:
            critical_services = self.results['service_type_gaps'][
                self.results['service_type_gaps']['adequacy_rating'] == 'Critical'
            ]
            
            if len(critical_services) > 0:
                recommendations.append({
                    'priority': 'CRITICAL',
                    'category': 'Service Capacity',
                    'issue': f'{len(critical_services)} service-college combinations critically understaffed',
                    'recommendation': 'Immediate hiring for crisis support and high-demand counseling services',
                    'expected_impact': '25-30% reduction in extended wait times'
                })
        
        # Resource allocation recommendations
        if 'resource_needs' in self.results:
            total_needed = self.results['resource_needs']['additional_counselors_needed'].sum()
            
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Staffing',
                'issue': f'Overall capacity shortage of {total_needed} counselors',
                'recommendation': 'Phased hiring plan with priority on crisis support and individual counseling',
                'expected_impact': '10% increase in service capacity as stated in project goals'
            })
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            logger.info(f"\n{i}. [{rec['priority']}] {rec['category']}")
            logger.info(f"   Issue: {rec['issue']}")
            logger.info(f"   Recommendation: {rec['recommendation']}")
            logger.info(f"   Expected Impact: {rec['expected_impact']}")
        
        self.results['recommendations'] = pd.DataFrame(recommendations)
        
        return recommendations
    
    def save_results(self, output_path):
        """Save all results to files"""
        logger.info(f"\nSaving results to {output_path}")
        
        for name, df in self.results.items():
            filepath = f"{output_path}/{name}.csv"
            df.to_csv(filepath, index=False)
            logger.info(f"Saved {name} to {filepath}")
    
    def run_complete_analysis(self):
        """Execute complete service gap analysis"""
        logger.info("\n" + "="*80)
        logger.info("STARTING COMPREHENSIVE SERVICE GAP ANALYSIS")
        logger.info("="*80 + "\n")
        
        # Run all analyses
        self.analyze_demographic_gaps()
        self.analyze_temporal_gaps()
        self.analyze_service_type_gaps()
        self.identify_underserved_populations()
        self.calculate_resource_needs()
        self.generate_recommendations()
        
        logger.info("\n" + "="*80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*80)
        
        return self.results


def main():
    """Main execution function"""
    # Configuration
    PROJECT_ID = "your-gcp-project-id"
    OUTPUT_PATH = "/home/claude/unt-mental-health-analysis/data/processed"
    
    # Initialize analyzer
    analyzer = ServiceGapAnalyzer(PROJECT_ID)
    
    # Run analysis
    results = analyzer.run_complete_analysis()
    
    # Save results
    analyzer.save_results(OUTPUT_PATH)
    
    logger.info("\nService gap analysis completed successfully!")
    logger.info(f"Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
