import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_public_servant_data(n=100):
    # List of possible education locations
    education_locations = ['USA', 'UK', 'Canada', 'Australia', 'India', 'Germany', 'France']
    departments = ['IAS', 'IPS', 'IFS', 'IRS', 'Railway Services', 'Defense Services']
    universities = {
        'USA': ['Harvard University', 'MIT', 'Stanford University', 'Yale University'],
        'UK': ['Oxford University', 'Cambridge University', 'LSE', 'Imperial College'],
        'Canada': ['University of Toronto', 'McGill University', 'UBC'],
        'Australia': ['University of Melbourne', 'Australian National University'],
        'India': ['IIT Delhi', 'IIT Bombay', 'Delhi University', 'JNU'],
        'Germany': ['TU Munich', 'Heidelberg University'],
        'France': ['Sciences Po', 'Sorbonne University']
    }

    # Generate public servant data
    servant_data = {
        'name': [f'Officer {i}' for i in range(1, n+1)],
        'department': np.random.choice(departments, n),
        'joining_year': np.random.randint(2000, 2024, n),
        'education_location': np.random.choice(education_locations, n, p=[0.2, 0.15, 0.1, 0.05, 0.35, 0.1, 0.05]),
        'degree_level': np.random.choice(['Bachelors', 'Masters', 'PhD'], n),
    }
    servant_data['university'] = [
        np.random.choice(universities[loc])
        for loc in servant_data['education_location']
    ]
    return pd.DataFrame(servant_data)

def generate_politician_data(n=50):
    parties = ['Party A', 'Party B', 'Party C', 'Party D']
    positions = ['MP', 'MLA', 'Minister', 'Chief Minister', 'Party President']
    education_locations = ['USA', 'UK', 'Canada', 'Australia', 'India']
    universities = {
        'USA': ['Harvard University', 'Stanford University', 'Yale University'],
        'UK': ['Oxford University', 'Cambridge University', 'LSE'],
        'Canada': ['University of Toronto', 'McGill University'],
        'Australia': ['University of Melbourne', 'Australian National University'],
        'India': ['Delhi University', 'JNU', 'Allahabad University']
    }

    politician_data = {
        'name': [f'Politician {i}' for i in range(1, n+1)],
        'party': np.random.choice(parties, n),
        'position': np.random.choice(positions, n),
        'education_location': np.random.choice(education_locations, n),
        'degree_level': np.random.choice(['Bachelors', 'Masters', 'PhD', 'High School'], n),
    }
    politician_data['university'] = [
        np.random.choice(universities[loc]) if loc in universities else 'Other'
        for loc in politician_data['education_location']
    ]
    return pd.DataFrame(politician_data)

def generate_family_data(politician_ids, n_per_politician=2):
    relations = ['Son', 'Daughter']  
    education_locations = ['USA', 'UK', 'Canada', 'Australia', 'India']
    universities = {
        'USA': ['Harvard University', 'Stanford University', 'Yale University', 'Columbia University'],
        'UK': ['Oxford University', 'Cambridge University', 'LSE', 'UCL'],
        'Canada': ['University of Toronto', 'McGill University', 'UBC'],
        'Australia': ['University of Melbourne', 'Australian National University'],
        'India': ['Delhi University', 'JNU', 'St. Stephens', 'SRCC']
    }

    family_data = []
    for pid in politician_ids:
        for _ in range(np.random.randint(0, n_per_politician + 1)):
            location = np.random.choice(education_locations)
            family_data.append({
                'politician_id': pid,
                'name': f'Family Member {pid}-{_}',
                'relation_type': np.random.choice(relations),  
                'education_location': location,
                'university': np.random.choice(universities[location]) if location in universities else 'Other',
                'degree_level': np.random.choice(['Bachelors', 'Masters', 'PhD', 'Studying'])
            })
    return pd.DataFrame(family_data)