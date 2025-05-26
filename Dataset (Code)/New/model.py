import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.visualization.scatter import Scatter

# Step 1: Load the dataset
file_path = 'farmer_panchayat_haryana_updated.xlsx'
farmer_data = pd.read_excel(file_path)

# Step 2: Data Preparation
# Extract relevant columns
villages = farmer_data[['Gram Panchayat & Equivalent', 'Latitude', 'Longitude', 'Total Harvested Waste (tons)', 'District']]
num_villages = len(villages)

# Define the company location in Panipat
company_panipat = {
    'Latitude': 29.3901,
    'Longitude': 76.9635
}

# Truck transport parameters
average_speed = 50  # average speed in km/h
cost_per_km = 10  # cost per km in currency unit

# Function to calculate distance between two lat-long points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c  # Distance in km
    return distance

# Calculate distances from each village to the company
villages.loc[:, 'Distance_to_Company'] = villages.apply(lambda row: haversine(row['Latitude'], row['Longitude'], company_panipat['Latitude'], company_panipat['Longitude']), axis=1)
villages.loc[:, 'Delivery_Time'] = villages['Distance_to_Company'] / average_speed  # in hours
villages.loc[:, 'Delivery_Cost'] = villages['Distance_to_Company'] * cost_per_km  # in currency unit

# Step 3: Define the optimization problem
class HarvestWasteOptimization(Problem):
    def __init__(self):
        super().__init__(n_var=num_villages, n_obj=2, n_constr=len(villages['District'].unique()), xl=0, xu=1)
    
    def _evaluate(self, x, out, *args, **kwargs):
        total_waste_collected = np.sum(x * villages['Total Harvested Waste (tons)'].values, axis=1)
        total_delivery_cost = np.sum(x * villages['Delivery_Cost'].values, axis=1)
        
        out["F"] = np.column_stack([-total_waste_collected, total_delivery_cost])
        
        # Constraint to ensure at least one stockholder per district
        district_constraint = []
        for district in villages['District'].unique():
            district_constraint.append(np.sum(x * (villages['District'].values == district), axis=1))
        
        out["G"] = -np.array(district_constraint).T

problem = HarvestWasteOptimization()

# Step 4: Run the optimization algorithm (NSGA-II)
algorithm = NSGA2(pop_size=100)
res = minimize(problem, algorithm, ('n_gen', 200), verbose=True)

# Step 5: Visualize the results (Pareto Front)
fig, ax = plt.subplots()
sc = ax.scatter(-res.F[:, 0], res.F[:, 1], c='red', edgecolors='black', s=50)
ax.set_title("Pareto Front")
ax.set_xlabel("Total Waste Collected (tons)")
ax.set_ylabel("Total Delivery Cost (currency unit)")
plt.show()

# Step 6: Print the best solution
best_solution = res.X[np.argmax(-res.F[:, 0])]
best_villages = villages[best_solution > 0.5]
print("Best Villages to Collect Waste From:")
print(best_villages)

# Visualize the optimal solution
fig, ax = plt.subplots()
ax.scatter(villages['Longitude'], villages['Latitude'], c='blue', label='All Villages')
ax.scatter(best_villages['Longitude'], best_villages['Latitude'], c='red', label='Selected Villages')
ax.scatter(company_panipat['Longitude'], company_panipat['Latitude'], c='green', marker='x', s=100, label='Company (Panipat)')
ax.set_title("Optimal Villages for Waste Collection")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend()
plt.show()
