"""
Generate Sample Mental Health Service Data
Creates anonymized, realistic sample data for demonstration
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)


class SampleDataGenerator:
    """Generate realistic sample mental health service data"""
    
    def __init__(self, num_students=20000, start_date='2023-01-01', end_date='2024-12-31'):
        self.num_students = num_students
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        
        # Define reference data
        self.service_types = [
            'Individual Counseling', 'Crisis Support', 'Group Therapy',
            'Therapy Session', 'Workshop', 'Assessment', 'Follow-up'
        ]
        
        self.colleges = [
            'College of Business', 'College of Engineering', 'College of Arts and Sciences',
            'College of Education', 'College of Health', 'College of Liberal Arts',
            'College of Music', 'College of Visual Arts'
        ]
        
        self.student_years = ['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']
        
        self.referral_sources = [
            'Self-referral', 'Faculty', 'Advisor', 'Peer', 'Health Services',
            'Residence Life', 'Athletics', 'Online', 'Emergency'
        ]
    
    def generate_student_ids(self):
        """Generate anonymized student IDs"""
        return [f"STU{str(i).zfill(6)}" for i in range(1, self.num_students + 1)]
    
    def generate_counselor_ids(self, num_counselors=50):
        """Generate counselor IDs"""
        return [f"CNS{str(i).zfill(3)}" for i in range(1, num_counselors + 1)]
    
    def generate_appointments(self):
        """Generate appointment records"""
        records = []
        student_ids = self.generate_student_ids()
        counselor_ids = self.generate_counselor_ids()
        
        # Each student has a probability of using services
        service_utilization_prob = 0.15  # ~15% of students use services
        
        for student_id in student_ids:
            if random.random() > service_utilization_prob:
                continue
            
            # Student characteristics (remain constant)
            student_year = random.choice(self.student_years)
            student_college = random.choice(self.colleges)
            student_status = random.choices(
                ['Full-time', 'Part-time'],
                weights=[0.85, 0.15]
            )[0]
            international_student = random.choices([True, False], weights=[0.12, 0.88])[0]
            first_generation = random.choices([True, False], weights=[0.20, 0.80])[0]
            
            # Number of visits for this student (follows realistic distribution)
            num_visits = int(np.random.gamma(2, 2)) + 1  # Most students: 1-5 visits
            num_visits = min(num_visits, 20)  # Cap at 20 visits
            
            # Generate visits for this student
            visit_dates = sorted(random.sample(list(self.date_range), min(num_visits, len(self.date_range))))
            
            for i, appointment_date in enumerate(visit_dates):
                # Service type selection (crisis more likely for first visit)
                if i == 0 and random.random() < 0.15:
                    service_type = 'Crisis Support'
                else:
                    service_type = random.choices(
                        self.service_types,
                        weights=[35, 10, 15, 25, 8, 5, 2]
                    )[0]
                
                # Counselor assignment (some consistency)
                if i == 0:
                    assigned_counselor = random.choice(counselor_ids)
                else:
                    # 70% chance of same counselor for continuity
                    assigned_counselor = records[-1]['counselor_id'] if random.random() < 0.7 else random.choice(counselor_ids)
                
                # Duration varies by service type
                if service_type == 'Workshop':
                    duration = random.randint(90, 120)
                elif service_type == 'Group Therapy':
                    duration = random.randint(60, 90)
                elif service_type == 'Crisis Support':
                    duration = random.randint(45, 90)
                else:
                    duration = random.randint(30, 60)
                
                # Wait time (varies by time of year and service type)
                month = appointment_date.month
                # Higher wait times during academic stress periods (Oct, Nov, Apr, May)
                if month in [10, 11, 4, 5]:
                    base_wait = random.randint(7, 21)
                else:
                    base_wait = random.randint(2, 10)
                
                # Crisis support has shorter wait
                if service_type == 'Crisis Support':
                    wait_days = random.randint(0, 3)
                else:
                    wait_days = base_wait
                
                # No-show probability (higher for longer waits)
                no_show_prob = 0.05 + (wait_days * 0.01)
                no_show = random.random() < no_show_prob
                
                # Referral source (first visit)
                if i == 0:
                    if service_type == 'Crisis Support':
                        referral_source = random.choices(
                            self.referral_sources,
                            weights=[20, 10, 5, 5, 15, 10, 5, 5, 25]
                        )[0]
                    else:
                        referral_source = random.choices(
                            self.referral_sources,
                            weights=[40, 15, 10, 10, 10, 5, 3, 5, 2]
                        )[0]
                else:
                    referral_source = 'Follow-up'
                
                # Follow-up scheduling (more likely if not last visit)
                follow_up_scheduled = i < len(visit_dates) - 1 or random.random() < 0.4
                
                record = {
                    'student_id': student_id,
                    'appointment_date': appointment_date.strftime('%Y-%m-%d'),
                    'service_type': service_type,
                    'counselor_id': assigned_counselor,
                    'duration_minutes': duration,
                    'student_year': student_year,
                    'student_college': student_college,
                    'student_status': student_status,
                    'international_student': international_student,
                    'first_generation': first_generation,
                    'referral_source': referral_source,
                    'wait_days': wait_days,
                    'no_show': no_show,
                    'follow_up_scheduled': follow_up_scheduled
                }
                
                records.append(record)
        
        return pd.DataFrame(records)
    
    def add_data_quality_issues(self, df, missing_rate=0.02):
        """Add realistic data quality issues"""
        # Randomly set some values to NaN
        for col in ['duration_minutes', 'wait_days']:
            mask = np.random.random(len(df)) < missing_rate
            df.loc[mask, col] = np.nan
        
        return df
    
    def generate_dataset(self, output_path='data/raw/mental_health_data.csv'):
        """Generate complete dataset"""
        print("Generating sample mental health service data...")
        print(f"Target students: {self.num_students}")
        print(f"Date range: {self.start_date.date()} to {self.end_date.date()}")
        
        # Generate appointments
        df = self.generate_appointments()
        
        # Add minor data quality issues
        df = self.add_data_quality_issues(df)
        
        # Sort by date
        df = df.sort_values('appointment_date').reset_index(drop=True)
        
        print(f"\nGenerated {len(df):,} appointment records")
        print(f"Unique students served: {df['student_id'].nunique():,}")
        print(f"Date range: {df['appointment_date'].min()} to {df['appointment_date'].max()}")
        
        # Print summary statistics
        print("\n=== Summary Statistics ===")
        print(f"Service Type Distribution:")
        print(df['service_type'].value_counts())
        print(f"\nCollege Distribution:")
        print(df['student_college'].value_counts())
        print(f"\nAverage wait time: {df['wait_days'].mean():.1f} days")
        print(f"No-show rate: {df['no_show'].mean()*100:.1f}%")
        
        # Save to CSV
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\nData saved to: {output_path}")
        
        return df


def main():
    """Generate sample data"""
    generator = SampleDataGenerator(
        num_students=20000,
        start_date='2023-01-01',
        end_date='2024-12-31'
    )
    
    df = generator.generate_dataset(
        output_path='/home/claude/unt-mental-health-analysis/data/raw/mental_health_data.csv'
    )
    
    print("\nSample data generation complete!")


if __name__ == "__main__":
    main()
