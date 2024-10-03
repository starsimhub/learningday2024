

import matplotlib.pyplot as plt
import networkx as nx
import random
import time

class HouseholdSetup:
    def __init__(self, ages, household_sizes):
        self.ages = ages
        self.household_sizes = household_sizes
        self.total_adults = 2

    def setup_households(self, num_adults=2):
        households = []
        ages = list(self.ages)         # Age Bins
        
        # Sort ages in reverse to get adults first and then shuffle adults
        ages.sort(reverse=True)
        adults = ages[:len(self.household_sizes)*num_adults]
        adults = adults[0:]
        if len(adults) < len(self.household_sizes)*num_adults:
            raise Exception('Not enough adults to fill houses')

        random.shuffle(adults)
        
        # Remaining people after adults
        remainder = ages[len(self.household_sizes):]
        random.shuffle(remainder)

        # Create households
        for size in self.household_sizes:
            household = []
            for i in range(num_adults):
                household += [adults.pop(0)]
                size -= 1
            household += remainder[:size]
            remainder = remainder[size:]
            """ add the household to the list of households only with unique values"""
            
            households.append(list(set(household))) # Remove twins
            print ("Household: ", household)
        print ("households: ", households)

        return households

def vectors_generators_generic(age_distribution={'1-18': 0.5, '19-100': 0.5}, household_sizes=[2, 6], num_households=2000, head_of_household=2):
    """
    Generates random ages and household sizes based on given age distribution with age ranges as keys.
    """
    
    # Ensure the age distribution is valid
    total_percentage = sum(age_distribution.values())
    if total_percentage > 1:
        raise Exception('The total percentage of the age distribution cannot exceed 1')

    for age_range, percentage in age_distribution.items():
        if percentage < 0 or percentage > 1:
            raise Exception(f'Invalid percentage for age range {age_range}')
    
    ages = []
    people = []
    
    total_percentage = sum(age_distribution.values())
    max_hh = max(household_sizes)
    
    # Calculate the number of individuals for each age range
    for age_range, percentage in age_distribution.items():
        
        # Parse the age range from the key (e.g., '1-12' -> (1, 12))
        age_min, age_max = map(int, age_range.split('-'))
        num_people=int(num_households*(percentage/total_percentage)*max_hh) # Calculate the number of people for this age range
        ages += [random.randint(age_min, age_max) for _ in range(num_people)]
    
    household_sizes_vector = [random.randint(household_sizes[0], household_sizes[1]) for _ in range(num_households)]
    
    return ages, household_sizes_vector

def plot_network(households):
    # Create a graph object
    G = nx.Graph()

    # Add households to the graph
    for i, household in enumerate(households):
        # For each household, create nodes and edges between them
        for person in household:
            G.add_node(person)  # Add node for each person
            
        for j in range(len(household)):
            for k in range(j + 1, len(household)):
                G.add_edge(household[j], household[k])  # Add edge between every two people in the household

    # Draw the graph
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G)  # Layout for a visually pleasing network
    nx.draw(G, pos, with_labels=True, node_size=400, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")
    plt.title("Household Network")
    plt.show()
    
def plot_household_network(households):
    # Create a graph object
    G = nx.Graph()

    # Add households to the graph
    for household in households:
        # for person in household:
        #     G.add_node(person)  # Add node for each person
        for i in range(len(household)):
            for j in range(i + 1, len(household)):
                G.add_edge(household[i], household[j])  # Connect each pair of people in the household

    # Draw the graph
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G)  # Layout for a visually pleasing network
    nx.draw(G, pos, with_labels=True, node_size=300, node_color="skyblue", font_size=7, font_color="black", edge_color="gray")
    plt.title("Household Network")
    plt.show()
# Example usage

def plot_household_network_clusters(households):
    # Create a graph object
    G = nx.Graph()
    # Add households to the graph
    for idx, household in enumerate(households):
        # for person in household:
        #     G.add_node(f"{idx}-{person}")  # Add node for each person, prefixed with household ID
        for i in range(len(household)):
            for j in range(i + 1, len(household)):
                G.add_edge(f"{idx}-{household[i]}", f"{idx}-{household[j]}", weight=household[i])  # Connect each pair of people in the household

    # Define positions for nodes to randomly spread households
    pos = {}
    for idx, household in enumerate(households):
        
        # Use a circular layout for each household
        sub_pos = nx.circular_layout([f"{idx}-{person}" for person in household])
        
        # Apply a random offset to each household's cluster to spread them out
        x_offset = random.uniform(-10, 10)  # Random x position
        y_offset = random.uniform(-10, 10)  # Random y position
        
        for key in sub_pos:
            sub_pos[key][0] += x_offset  # Shift in the x direction
            sub_pos[key][1] += y_offset  # Shift in the y direction
        pos.update(sub_pos)
    
    # Draw the graph
    plt.figure(figsize=(10, 10))
    nx.draw(G, pos, with_labels=True, node_size=200, node_color="skyblue", font_size=6, font_color="black", edge_color="gray")
    plt.title("Household Network (Randomly Spread Clusters)")
    plt.show()


if __name__ == '__main__':
    
    agebins = {'1-12': 0.15, '13-18': 0.15, '19-40': 0.3, '41-70': 0.3, '71-100': 0.01}
    
    ages, household_sizes = vectors_generators_generic(agebins, household_sizes=[2,6], num_households=10)
    
    hh = HouseholdSetup(ages, household_sizes)
    
    households = hh.setup_households()
    
    plot_household_network_clusters(households)

    plot_network(households)