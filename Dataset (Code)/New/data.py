import pandas as pd
import numpy as np

# Ensure you have the correct file path
file_path = 'farmer_panchayat-try.xlsx'  # Update with the correct path

# Load the existing Excel file
try:
    data = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"File not found: {file_path}")
    raise

# Function to generate random latitude and longitude within Haryana's bounds
def generate_haryana_coordinates(num_entries):
    data = {
        'Latitude': np.random.uniform(27.6, 30.9, num_entries),
        'Longitude': np.random.uniform(74.3, 77.5, num_entries)
    }
    return pd.DataFrame(data)

# Function to generate random agricultural data
def generate_agricultural_data(num_entries):
    data = {
        'Cultivable Area (ha)': np.random.uniform(1, 500, num_entries),
        'Avg Yield per ha (Rice)': np.random.uniform(1, 10, num_entries),
        'Avg Yield per ha (Wheat)': np.random.uniform(1, 10, num_entries)
    }
    
    # Rice and Wheat Cultivation Area should be less than or equal to Cultivable Area
    data['Rice Cultivation Area (ha)'] = np.random.uniform(0, data['Cultivable Area (ha)'])
    data['Wheat Cultivation Area (ha)'] = np.random.uniform(0, data['Cultivable Area (ha)'])
    
    # Calculate total harvested waste based on average yield and cultivation area
    data['Total Harvested Waste (Rice) (tons)'] = data['Rice Cultivation Area (ha)'] * data['Avg Yield per ha (Rice)'] * 0.15  # Assuming 15% of yield is waste
    data['Total Harvested Waste (Wheat) (tons)'] = data['Wheat Cultivation Area (ha)'] * data['Avg Yield per ha (Wheat)'] * 0.15  # Assuming 15% of yield is waste
    data['Total Harvested Waste (tons)'] = data['Total Harvested Waste (Rice) (tons)'] + data['Total Harvested Waste (Wheat) (tons)']
    
    return pd.DataFrame(data)

# Generate the Haryana-specific latitude and longitude
num_entries = len(data)
haryana_coordinates = generate_haryana_coordinates(num_entries)

# Update the DataFrame with these coordinates
data['Latitude'] = haryana_coordinates['Latitude']
data['Longitude'] = haryana_coordinates['Longitude']

# Generate the agricultural data
agricultural_data = generate_agricultural_data(num_entries)

# Add the new columns to the original DataFrame
for column in agricultural_data.columns:
    data[column] = agricultural_data[column]

# Define the output file path
output_file_path_haryana = 'farmer_panchayat_haryana_updated.xlsx'  # Update with the correct path

# Save the updated DataFrame to an Excel file
data.to_excel(output_file_path_haryana, index=False)

print(f"Updated file saved to: {output_file_path_haryana}")
