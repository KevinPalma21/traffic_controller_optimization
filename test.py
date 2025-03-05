import pygame
import sys
import csv
import random
import time
import threading

simulation_running = True

###############################################################################
# LOADING THE GRAPH
###############################################################################
def load_graph_from_csv(csv_filename):
    graph = {}
    entry_nodes = []
    exit_nodes = []
    try:
        with open(csv_filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # skip header row if present

            for row in reader:
                if len(row) < 8:
                    continue

                node_name = row[1].strip()
                node_type_raw = row[2].strip().lower()
                direction = row[3].strip().lower()
                x = float(row[4])
                y = float(row[5])

                neighbors = []
                if row[6].strip():
                    neighbors.append(row[6].strip())
                if row[7].strip():
                    neighbors.append(row[7].strip())

                graph[node_name] = {
                    "x": x,
                    "y": y,
                    "neighbors": neighbors,
                    "direction": direction,
                    "type": node_type_raw
                }

                if node_type_raw == "entry":
                    entry_nodes.append(node_name)
                elif node_type_raw == "exit":
                    exit_nodes.append(node_name)

        print(f"Loaded {len(graph)} nodes from {csv_filename}")
        print(f"Entry nodes: {entry_nodes}")
        print(f"Exit nodes:  {exit_nodes}")

    except Exception as e:
        print(f"Error loading CSV {csv_filename}: {e}")

    return graph, entry_nodes, exit_nodes

def select_random_entry(entry_nodes):
    if not entry_nodes:
        return None
    return random.choice(entry_nodes)

###############################################################################
# OCCUPANCY CHECK
###############################################################################
def is_node_occupied(node_name, all_vehicles, this_vehicle):
    """
    Returns True if any other vehicle has node_name == their current_node.
    'this_vehicle' is excluded so a vehicle doesn't block itself.
    """
    for v in all_vehicles:
        if v is not this_vehicle and v.current_node == node_name:
            return True
    return False

###############################################################################
# VEHICLE CLASSES
###############################################################################
class BaseVehicle:
    """
    Common base class for vehicles. 
    """
    def __init__(self, graph, start_node, side, speed=2):
        self.graph = graph
        self.current_node = start_node
        self.x = graph[start_node]["x"]
        self.y = graph[start_node]["y"]
        self.base_speed = speed  # <-- ADDED: store original speed separately
        self.image = None
        self.target_node = None
        self.side = side
        self.spawn_time = time.time()

    def choose_next_node(self):
        neighbors = self.graph[self.current_node]["neighbors"]
        if not neighbors:
            return None
        return random.choice(neighbors)

    def move(self, all_vehicles):
        """
        Now takes 'all_vehicles' to check occupancy.
        Returns False if despawned; True otherwise.
        """
        # 1) If we are at an exit, despawn
        if self.graph[self.current_node]["type"] == "exit":
            return False

        # 2) If no target node chosen, pick one
        if self.target_node is None:
            self.target_node = self.choose_next_node()
        if self.target_node is None:
            return False

        # 3) Check if the target node is occupied
        #    If yes, we set speed to 0 to stop.
        if is_node_occupied(self.target_node, all_vehicles, self):
            current_speed = 0
        else:
            current_speed = self.base_speed

        # 4) Normal movement logic with 'current_speed'
        target_x = self.graph[self.target_node]["x"]
        target_y = self.graph[self.target_node]["y"]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2)**0.5

        if dist < current_speed:
            # Snap to node
            self.current_node = self.target_node
            self.x = target_x
            self.y = target_y
            self.target_node = self.choose_next_node()

            # Check if new node is exit => despawn
            if self.graph[self.current_node]["type"] == "exit":
                return False

            self.set_image_by_direction(self.graph[self.current_node]["direction"])
        else:
            # Move fractionally
            if current_speed > 0:
                self.x += current_speed * (dx / dist)
                self.y += current_speed * (dy / dist)
            # else speed=0 => do not move

        return True

    def draw(self, screen):
        if self.image:
            rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, rect)

    def set_image_by_direction(self, direction):
        pass

class Car(BaseVehicle):
    def __init__(self, images, graph, start_node, side, speed=1.5):
        super().__init__(graph, start_node, side, speed)
        self.images = images
        self.set_image_by_direction(graph[start_node]["direction"])

    def set_image_by_direction(self, direction):
        if direction in self.images:
            self.image = self.images[direction]

class Truck(BaseVehicle):
    def __init__(self, images, graph, start_node, side, speed=1):
        super().__init__(graph, start_node, side, speed)
        self.images = images
        self.set_image_by_direction(graph[start_node]["direction"])

    def set_image_by_direction(self, direction):
        if direction in self.images:
            self.image = self.images[direction]

class Motorcycle(BaseVehicle):
    def __init__(self, images, graph, start_node, side, speed=2):
        super().__init__(graph, start_node, side, speed)
        self.images = images
        self.set_image_by_direction(graph[start_node]["direction"])

    def set_image_by_direction(self, direction):
        if direction in self.images:
            self.image = self.images[direction]

###############################################################################
# THREADING FOR SPAWNING VEHICLES
###############################################################################
def spawn_vehicles_thread(
    vehicles_static, vehicles_ml, lock,
    entry_static, entry_ml,
    graph_static, graph_ml,
    cars_img, trucks_img, motos_img
):
    global simulation_running

    while simulation_running:
        time.sleep(random.uniform(0.5, 1.5))
        if simulation_running:
            # --- 1) Choose entries
            entry_s = select_random_entry(entry_static)
            entry_m = select_random_entry(entry_ml)
            if entry_s and entry_m:
                vehicle_type_s = random.choice(["car", "truck", "motorcycle"])
                vehicle_type_m = random.choice(["car", "truck", "motorcycle"])

                with lock:
                    if vehicle_type_s == "car":
                        new_vehicle_s = Car(cars_img, graph_static, entry_s, side="static")
                    elif vehicle_type_s == "truck":
                        new_vehicle_s = Truck(trucks_img, graph_static, entry_s, side="static")
                    else:
                        new_vehicle_s = Motorcycle(motos_img, graph_static, entry_s, side="static")

                    if vehicle_type_m == "car":
                        new_vehicle_m = Car(cars_img, graph_ml, entry_m, side="ml")
                    elif vehicle_type_m == "truck":
                        new_vehicle_m = Truck(trucks_img, graph_ml, entry_m, side="ml")
                    else:
                        new_vehicle_m = Motorcycle(motos_img, graph_ml, entry_m, side="ml")

                    vehicles_static.append(new_vehicle_s)
                    vehicles_ml.append(new_vehicle_m)

                    print(f"[Spawner] Spawned {vehicle_type_s} at '{entry_s}' (static)")
                    print(f"[Spawner] Spawned {vehicle_type_m} at '{entry_m}' (ML)")

###############################################################################
# MAIN LOOP
###############################################################################
def main():
    global simulation_running
    pygame.init()

    # Load both graphs
    graph_static, entry_static, exit_static = load_graph_from_csv("Directed_Graph - Static.csv")
    graph_ml, entry_ml, exit_ml = load_graph_from_csv("Directed_Graph - Machine_Learning.csv")

    # Create a window
    screen = pygame.display.set_mode((1300, 1000))
    pygame.display.set_caption("Dual-Side Simulation")

    # Load background
    background_img = pygame.image.load("images/Grid_Sim_Background.jpg").convert()
    bg_width, bg_height = background_img.get_size()
    screen = pygame.display.set_mode((bg_width, bg_height))

    # Load images
    car_images = {
        "southside": pygame.image.load("images/car_southside.png").convert_alpha(),
        "northside": pygame.image.load("images/car_northside.png").convert_alpha(),
        "eastside":  pygame.image.load("images/car_eastside.png").convert_alpha(),
        "westside":  pygame.image.load("images/car_westside.png").convert_alpha()
    }
    truck_images = {
        "southside": pygame.image.load("images/truck_southside.png").convert_alpha(),
        "northside": pygame.image.load("images/truck_northside.png").convert_alpha(),
        "eastside":  pygame.image.load("images/truck_eastside.png").convert_alpha(),
        "westside":  pygame.image.load("images/truck_westside.png").convert_alpha()
    }
    moto_images = {
        "southside": pygame.image.load("images/motorcycle_southside.png").convert_alpha(),
        "northside": pygame.image.load("images/motorcycle_northside.png").convert_alpha(),
        "eastside":  pygame.image.load("images/motorcycle_eastside.png").convert_alpha(),
        "westside":  pygame.image.load("images/motorcycle_westside.png").convert_alpha()
    }

    clock = pygame.time.Clock()
    vehicles_static = []
    vehicles_ml = []
    vehicles_lock = threading.Lock()

    # Start spawner thread
    spawner_thread = threading.Thread(
        target=spawn_vehicles_thread,
        args=(
            vehicles_static, vehicles_ml, vehicles_lock,
            entry_static, entry_ml,
            graph_static, graph_ml,
            car_images, truck_images, moto_images
        ),
        daemon=True
    )
    spawner_thread.start()

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        with vehicles_lock:
            # Build a combined list for occupancy checks
            all_vehicles = vehicles_static + vehicles_ml

            # Update static side
            for v in vehicles_static[:]:
                if not v.move(all_vehicles):
                    # Vehicle is despawning => record time
                    elapsed = time.time() - v.spawn_time
                    with open("static_result_metrics.txt", "a") as f:
                        f.write(f"{elapsed:.3f}\n")
                    vehicles_static.remove(v)

            # Update ML side
            for v in vehicles_ml[:]:
                if not v.move(all_vehicles):
                    # Vehicle is despawning => record time
                    elapsed = time.time() - v.spawn_time
                    with open("ml_result_metrics.txt", "a") as f:
                        f.write(f"{elapsed:.3f}\n")
                    vehicles_ml.remove(v)

        # Render
        screen.blit(background_img, (0, 0))
        with vehicles_lock:
            for v in vehicles_static:
                v.draw(screen)
            for v in vehicles_ml:
                v.draw(screen)

        pygame.display.flip()

    # Clean up
    simulation_running = False
    spawner_thread.join()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
