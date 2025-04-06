import pandas as pd

# Mapping dictionary from the legend
TEST_TYPE_MAPPING = {
    'A': 'Ability & Aptitude',
    'B': 'Biodata & Situational Judgement',
    'C': 'Competencies',
    'D': 'Development & 360',
    'E': 'Assessment Exercises',
    'K': 'Knowledge & Skills',
    'P': 'Personality & Behavior',
    'S': 'Simulations'
}

def expand_test_type(code_str):
    """Convert letter codes to full names using the mapping"""
    if pd.isna(code_str):
        return ''
    return ', '.join([TEST_TYPE_MAPPING.get(char, '') for char in str(code_str)])

# Read CSV file
df = pd.read_csv('data/shl_product_details.csv')

# Apply transformation to 'Test Type' column
df['Test Type'] = df['Test Type'].apply(expand_test_type)

# Save modified dataframe
df.to_csv('data/updated_shl_product_details.csv', index=False)
