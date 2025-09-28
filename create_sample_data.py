"""
Sample Data Generator for StorEdge DaVinci Unit Status Analyzer

This script creates sample CSV files to demonstrate the analyzer functionality.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import random

def create_sample_units_data(num_units: int = 100) -> pd.DataFrame:
    """Create sample units.csv data."""
    
    # Generate unit numbers (mix of different formats)
    units = []
    for i in range(1, num_units + 1):
        if i <= 30:
            units.append(f"A{i:03d}")  # A001, A002, etc.
        elif i <= 60:
            units.append(f"B{i-30:03d}")  # B001, B002, etc.
        else:
            units.append(f"C{i-60:03d}")  # C001, C002, etc.
    
    # Generate statuses (70% occupied, 30% vacant)
    statuses = []
    for i in range(num_units):
        if random.random() < 0.7:  # 70% occupied
            occupied_types = [
                "Occupied - Tenant Active",
                "Occupied - Month to Month",
                "Occupied - Annual Lease",
                "Occupied - Commercial Tenant"
            ]
            statuses.append(random.choice(occupied_types))
        else:  # 30% vacant
            vacant_types = [
                "Vacant - Ready for Rent",
                "Vacant - Needs Cleaning",
                "Vacant - Under Maintenance",
                "Vacant - Reserved"
            ]
            statuses.append(random.choice(vacant_types))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Unit': units,
        'Status': statuses,
        'Size': np.random.choice(['5x5', '5x10', '10x10', '10x15', '10x20'], num_units),
        'Floor': np.random.choice(['Ground', 'Second', 'Third'], num_units),
        'Type': np.random.choice(['Standard', 'Climate', 'Drive-Up'], num_units),
        'Rate': np.random.uniform(50, 300, num_units).round(2)
    })
    
    return df

def create_sample_rentroll_data(units_df: pd.DataFrame) -> pd.DataFrame:
    """Create sample rentroll.csv data based on units data."""
    
    # Only include occupied units
    occupied_units = units_df[units_df['Status'].str.startswith('Occupied')].copy()
    
    # Generate payment status (80% current, 20% delinquent)
    payment_status = []
    days_past_due = []
    
    for i in range(len(occupied_units)):
        if random.random() < 0.8:  # 80% current
            payment_status.append('Current')
            days_past_due.append(0)
        else:  # 20% delinquent
            payment_status.append('Delinquent')
            days_past_due.append(random.randint(1, 90))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Unit': occupied_units['Unit'].values,
        'Tenant_Name': [f"Tenant_{i+1}" for i in range(len(occupied_units))],
        'Email': [f"tenant{i+1}@email.com" for i in range(len(occupied_units))],
        'Phone': [f"555-{random.randint(1000, 9999)}" for _ in range(len(occupied_units))],
        'Move_In_Date': pd.date_range('2020-01-01', periods=len(occupied_units), freq='D').strftime('%Y-%m-%d'),
        'Monthly_Rate': occupied_units['Rate'].values,
        'Last_Payment_Date': pd.date_range('2024-01-01', periods=len(occupied_units), freq='D').strftime('%Y-%m-%d'),
        'Payment_Status': payment_status,
        'Days Past Due': days_past_due,
        'Balance': [max(0, days * rate / 30) for days, rate in zip(days_past_due, occupied_units['Rate'])],
        'Auto_Pay': np.random.choice(['Yes', 'No'], len(occupied_units)),
        'Insurance': np.random.choice(['Required', 'Waived'], len(occupied_units)),
        'Notes': [''] * len(occupied_units)
    })
    
    return df

def create_sample_locks_data(units_df: pd.DataFrame) -> pd.DataFrame:
    """Create sample locks.csv data based on units data."""
    
    # Generate lock assignments for all units
    lock_data = []
    
    for _, unit_row in units_df.iterrows():
        unit = unit_row['Unit']
        status = unit_row['Status']
        
        # Determine lock status based on unit status
        if status.startswith('Vacant'):
            lock_status = 'Assigned Vacant'
        elif status.startswith('Occupied'):
            # Check if this unit is in rentroll (delinquent)
            # For demo purposes, we'll randomly assign some as delinquent
            if random.random() < 0.2:  # 20% chance of being delinquent
                lock_status = random.choice(['Assigned Overlock', 'Assigned Auction'])
            else:
                lock_status = 'Tenant Using Lock'
        else:
            lock_status = 'Assigned Vacant'
        
        # Add some intentional miscompares for demonstration
        if random.random() < 0.1:  # 10% miscompare rate
            if status.startswith('Vacant'):
                lock_status = random.choice(['Tenant Using Lock', 'Assigned Overlock'])
            elif status.startswith('Occupied'):
                lock_status = random.choice(['Assigned Vacant', 'Assigned Overlock'])
        
        lock_data.append({
            'Lock_ID': f"LOCK_{unit}_{random.randint(1000, 9999)}",
            'Unit Number': unit,
            'Lock_Type': random.choice(['Standard', 'High Security', 'Electronic']),
            'Install_Date': pd.date_range('2020-01-01', periods=1, freq='D')[0].strftime('%Y-%m-%d'),
            'Status': lock_status,
            'Last_Service': pd.date_range('2023-01-01', periods=1, freq='D')[0].strftime('%Y-%m-%d'),
            'Notes': ''
        })
    
    df = pd.DataFrame(lock_data)
    return df

def main():
    """Generate sample data files."""
    print("Creating sample data files for StorEdge DaVinci Unit Status Analyzer...")
    
    # Create sample directory
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # Set random seed for reproducible results
    random.seed(42)
    np.random.seed(42)
    
    # Generate sample data
    print("Generating units.csv...")
    units_df = create_sample_units_data(100)
    units_df.to_csv(sample_dir / "units.csv", index=False)
    
    print("Generating rentroll.csv...")
    rentroll_df = create_sample_rentroll_data(units_df)
    rentroll_df.to_csv(sample_dir / "rentroll.csv", index=False)
    
    print("Generating locks.csv...")
    locks_df = create_sample_locks_data(units_df)
    locks_df.to_csv(sample_dir / "locks.csv", index=False)
    
    print(f"\nSample data files created in '{sample_dir}' directory:")
    print(f"  - units.csv: {len(units_df)} units")
    print(f"  - rentroll.csv: {len(rentroll_df)} occupied units")
    print(f"  - locks.csv: {len(locks_df)} lock assignments")
    
    print(f"\nTo run the analyzer with this sample data:")
    print(f"python main_analyzer.py --units {sample_dir}/units.csv --rentroll {sample_dir}/rentroll.csv --locks {sample_dir}/locks.csv")
    
    # Show some sample data
    print(f"\nSample units.csv data:")
    print(units_df.head())
    
    print(f"\nSample rentroll.csv data:")
    print(rentroll_df.head())
    
    print(f"\nSample locks.csv data:")
    print(locks_df.head())

if __name__ == "__main__":
    main()
