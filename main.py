import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as TK
from tkinter import ttk
import numpy as np
import random

# Parameters
population_size = 500
num_generations = 1000
num_waypoints = 1  # Number of waypoints between start and end
start_point = (0, 0)
end_point = (100, 100)
mutation_rate = 0.1

# Randomly generated environmental data (for simplicity)
danger_zones = [(50, 50, 10), (70, 30, 15)]  # (x, y, radius) for each dangerous area
wind_direction = np.random.uniform(0, 2*np.pi)  # Random wind direction
wind_speed = np.random.uniform(5, 15)  # Random wind speed in knots

# Helper functions
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def generate_random_route():
    return [start_point] + [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(num_waypoints)] + [end_point]

def fitness(route):
    total_distance = sum(distance(route[i], route[i+1]) for i in range(len(route) - 1))
    time_penalty = total_distance / (10 + wind_speed * np.cos(wind_direction))
    danger_penalty = sum(1 for x, y, r in danger_zones if any(distance(wp, (x, y)) < r for wp in route))
    return total_distance + time_penalty + danger_penalty * 100

def crossover(parent1, parent2):
    crossover_point = random.randint(1, num_waypoints)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutate(route):
    if random.random() < mutation_rate:
        mutate_point = random.randint(1, num_waypoints)
        route[mutate_point] = (random.uniform(0, 100), random.uniform(0, 100))
    return route

def evolve_population(population):
    population = sorted(population, key=lambda route: fitness(route))
    new_population = population[:10]  # Elitism: carry forward the top 10 routes
    while len(new_population) < population_size:
        parent1, parent2 = random.choices(population[:25], k=2)
        child1, child2 = crossover(parent1, parent2)
        new_population += [mutate(child1), mutate(child2)]
    return new_population

def update_graph():
    ax.clear()
    for route in population:
        route_np = np.array(route)
        ax.plot(route_np[:, 0], route_np[:, 1], color='grey', alpha=0.5)

    best_route_np = np.array(best_route)
    ax.plot(best_route_np[:, 0], best_route_np[:, 1], color='blue', marker='o', label='Best Route')

    # Mark start and end points
    ax.plot(start_point[0], start_point[1], 'go', markersize=10)  # Start
    ax.plot(end_point[0], end_point[1], 'ro', markersize=10)  # End

    # Mark dangerous areas
    for x, y, r in danger_zones:
        ax.add_patch(plt.Circle((x, y), r, color='red', alpha=0.3))

    ax.set_title('Genetic Algorithm for Ship Navigation')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend()
    ax.grid(True)
    canvas.draw()

def add_danger_zone():
    try:
        x = float(x_entry.get())
        y = float(y_entry.get())
        radius = float(radius_entry.get())
        danger_zones.append((x, y, radius))
        update_graph()
    except ValueError:
        print("Invalid input! Please enter numeric values.")

def undo_danger_zone():
    if danger_zones:
        danger_zones.pop()  # Remove the last added danger zone
        update_graph()
    else:
        print("No danger zones to undo.")

# Initialize Population
population = [generate_random_route() for _ in range(population_size)]

# Evolve Population over Generations
for generation in range(num_generations):
    population = evolve_population(population)

# Get the best route
best_route = min(population, key=lambda route: fitness(route))

# Tkinter setup
root = TK.Tk()
root.title("Genetic Algorithm Visualization")

# Create Notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Create a frame for the graph tab
graph_frame = TK.Frame(notebook)
notebook.add(graph_frame, text='Graph')

# Create Matplotlib figure and axis
fig, ax = plt.subplots(figsize=(10, 8))

# Embed the Matplotlib figure into the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill='both', expand=True)

# Create a frame for the danger zone input tab
input_frame = TK.Frame(notebook)
notebook.add(input_frame, text='Add Danger Zone')

# Input fields for danger zone coordinates and radius
TK.Label(input_frame, text="X Coordinate:").grid(row=0, column=0, padx=5, pady=5)
x_entry = TK.Entry(input_frame)
x_entry.grid(row=0, column=1, padx=5, pady=5)

TK.Label(input_frame, text="Y Coordinate:").grid(row=1, column=0, padx=5, pady=5)
y_entry = TK.Entry(input_frame)
y_entry.grid(row=1, column=1, padx=5, pady=5)

TK.Label(input_frame, text="Radius:").grid(row=2, column=0, padx=5, pady=5)
radius_entry = TK.Entry(input_frame)
radius_entry.grid(row=2, column=1, padx=5, pady=5)

# Buttons to add and undo danger zones
add_button = TK.Button(input_frame, text="Add Danger Zone", command=add_danger_zone)
add_button.grid(row=3, columnspan=2, pady=10)

undo_button = TK.Button(input_frame, text="Undo Last Danger Zone", command=undo_danger_zone)
undo_button.grid(row=4, columnspan=2, pady=10)

#exit
exit_button = TK.Button(root, text="Exit", command=root.destroy) 
exit_button.pack(pady=20)

# Initialize graph
update_graph()

# Run the Tkinter main loop
root.mainloop()
