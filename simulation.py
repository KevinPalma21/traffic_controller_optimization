import pygame
import sys
import csv
import random
import time
import threading

simulation_running = True
###################################################################################################
def load_graph_from_csv(csv_filename):#This function get the directed graph from the csv, the infomation of each node, and returns the graph, entry nodes, and exit nodes
    graph = {}
    entry_nodes = []
    exit_nodes = []

    try:
        with open(csv_filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)

            for row in reader:
                if len(row) < 8:#Should only be a max of 8 feilds of info for each node 
                    continue
                node_name = row[1].strip()
                node_type = row[2].strip().lower()
                vehicle_direction = row[3].strip().lower()
                node_x = float(row[4])
                node_y = float(row[5])

                neighbors = []
                if row[6].strip():
                    neighbors.append(row[6].strip())
                if row[7].strip():
                    neighbors.append(row[7].strip())

                graph[node_name] = {
                    "x": node_x,
                    "y": node_y,
                    "neighbors": neighbors,
                    "direction": vehicle_direction,
                    "node_type": node_type
                }

                if node_type == "entry":
                    entry_nodes.append(node_name)
                elif node_type == "exit":
                    exit_nodes.append(node_name)

    
    except Exception as e:
        print(f"Error loading CSV {csv_filename}: {e}")
    
    return graph, entry_nodes, exit_nodes,
#########################################################################################################

def select_random_entry(entry_nodes):#Randomly picks an entry node, will be called later to generate a vehicle at that node
    if not entry_nodes:
        return None
    return random.choice(entry_nodes)

def is_node_occupied(node_name, all_vehicles, this_vehicle):# This function checks if there is a vehicle is on a node, will return true if another vehicle has their currnt node name
    for v in all_vehicles:
        if v is not this_vehicle and v.current_node == node_name:
            return True
    return False
############################################################################################################

class TrafficLight:
    def __init__(self, node_name, x, y, orientation, images):
        """
        :param node_name: the identifier from your CSV (e.g., "V1.9")
        :param x, y: coordinates for this node
        :param orientation: either "horizontal" or "vertical"
        :param images: a dict of images for that orientation with keys "red", "yellow", "green"
        """
        self.node_name = node_name
        self.x = x
        self.y = y
        self.orientation = orientation  # "horizontal" or "vertical"
        self.images = images
        self.state = "red"  # initial state
        self.cycle_period = 12.0  # total cycle time in seconds

    def update(self):
        # Use the current time mod cycle_period for a synchronized cycle.
        t = time.time() % self.cycle_period
        if self.orientation == "horizontal":
            # Horizontal cycle: green (0-5 sec), yellow (5-7 sec), red (7-12 sec)
            if t < 5:
                self.state = "green"
            elif t < 7:
                self.state = "yellow"
            else:
                self.state = "red"
        else:  # vertical
            # Vertical cycle: red (0-7 sec), green (7-10 sec), yellow (10-12 sec)
            if t < 7:
                self.state = "red"
            elif t < 10:
                self.state = "green"
            else:
                self.state = "yellow"

    def draw(self, screen):
        # Draw the image centered at the node's (x, y)
        img = self.images[self.state]
        rect = img.get_rect(center=(self.x, self.y))
        screen.blit(img, rect)

def create_traffic_lights(graph, horizontal_images, vertical_images):
    traffic_lights = []
    for node_name, node_data in graph.items():
        if node_data["node_type"].lower() == "traffic_controller":
            direction = node_data["direction"]
            # Determine orientation based on the direction.
            # Assume "eastside" and "westside" are horizontal, others vertical.
            if direction in ("eastside", "westside"):
                orientation = "horizontal"
                images = horizontal_images
            else:
                orientation = "vertical"
                images = vertical_images
            tl = TrafficLight(node_name, node_data["x"], node_data["y"], orientation, images)
            traffic_lights.append(tl)
    return traffic_lights


class BaseVehicle:

    def __init__(self, graph, start_node, side, speed=2, light_state=None):
        self.graph = graph
        self.current_node = start_node
        self.x = graph[start_node]["x"]
        self.y = graph[start_node]["y"]
        self.base_speed = speed   #This is temparay, actual speed will be in each vehicle type class
        self.image = None
        self.target_node = None
        self.side = side
        self.spawn_time = time.time() #Starts timer when vehicle is generated, this is the metric which we will use to conclude weather or not traffic signals controlled by machine learning are better then what we have today
        self.light_state = light_state  # dictionary of node_name -> TrafficLight object

    def choose_next_node(self):#Cannot use a shortest path traversal algo like Dijkstra or Greedy because if I randomly choose a entry and exit node, there might never be a path between these two becasue of the layout of the streets
        neighbors = self.graph[self.current_node]["neighbors"]
        if not neighbors:
            return None
        return random.choice(neighbors)
        
    def move(self, all_vehicles):
        #1) If we are at an exit, despawn
        if self.graph[self.current_node]["node_type"] == "exit":
            return False

        #2) If no target node chosen, pick one
        if self.target_node is None:
            self.target_node = self.choose_next_node()
        if self.target_node is None:
            return False

        #3) Check if the target node is occupied, If yes, we set speed to 0 to stop.
        if is_node_occupied(self.target_node, all_vehicles, self):
            current_speed = 0
        else:
            current_speed = self.base_speed               
        
        # If next node is a traffic_controller node, check the light
        if self.graph[self.target_node]["node_type"] == "traffic_controller":
            #check the traffic light
            # self.lights_dict may be None if not provided, so check that first
            if self.light_state and self.target_node in self.light_state:
                light_state = self.light_state[self.target_node].state
                if light_state != "green":
                    current_speed = 0


        #Normal movement logic with 'current_speed'
        target_x = self.graph[self.target_node]["x"]
        target_y = self.graph[self.target_node]["y"]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx**2 + dy**2)**0.5

        if dist < current_speed:
            self.current_node = self.target_node
            self.x = target_x
            self.y = target_y
            self.target_node = self.choose_next_node()
            if self.graph[self.current_node]["node_type"] == "exit":
                return False
            self.set_image_by_direction(self.graph[self.current_node]["direction"])
        else:
            if current_speed > 0:
                self.x += current_speed * (dx / dist)
                self.y += current_speed * (dy / dist)
        return True
    
    def draw(self, screen):
        if self.image:
            rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, rect)

    def set_image_by_direction(self, direction):
        pass

class Car(BaseVehicle):
    def __init__(self, images, graph, start_node, side, speed=1.5, light_state=None): #Actual Speed of Car
        super().__init__(graph, start_node, side, speed, light_state)
        self.images = images
        self.set_image_by_direction(graph[start_node]["direction"])

    def set_image_by_direction(self, direction):
        if direction in self.images:
            self.image = self.images[direction]

class Truck(BaseVehicle):
    def __init__(self, images, graph, start_node, side, speed=1, light_state=None): #Actual Speed of Truck
        super().__init__(graph, start_node, side, speed, light_state)
        self.images = images
        self.set_image_by_direction(graph[start_node]["direction"])

    def set_image_by_direction(self, direction):
        if direction in self.images:
            self.image = self.images[direction]

class Motorcycle(BaseVehicle):
    def __init__(self, images, graph, start_node, side, speed=1.75, light_state=None): #Actual Speed of Motorcycle
        super().__init__(graph, start_node, side, speed, light_state)
        self.images = images
        self.set_image_by_direction(graph[start_node]["direction"])

    def set_image_by_direction(self, direction):
        if direction in self.images:
            self.image = self.images[direction]

####################################################################################################################

def spawn_vehicles_thread(
    vehicles_static, vehicles_ml, lock,
    entry_static, entry_ml,
    graph_static, graph_ml,
    cars_img, trucks_img, motos_img,
    lights_state_static, lights_state_ml,
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
                        new_vehicle_s = Car(cars_img, graph_static, entry_s, side="static", light_state=lights_state_static)
                    elif vehicle_type_s == "truck":
                        new_vehicle_s = Truck(trucks_img, graph_static, entry_s, side="static", light_state=lights_state_static)
                    else:
                        new_vehicle_s = Motorcycle(motos_img, graph_static, entry_s, side="static", light_state=lights_state_static)

                    if vehicle_type_m == "car":
                        new_vehicle_m = Car(cars_img, graph_ml, entry_m, side="ml", light_state=lights_state_ml)
                    elif vehicle_type_m == "truck":
                        new_vehicle_m = Truck(trucks_img, graph_ml, entry_m, side="ml", light_state=lights_state_ml)
                    else:
                        new_vehicle_m = Motorcycle(motos_img, graph_ml, entry_m, side="ml", light_state=lights_state_ml)

                    vehicles_static.append(new_vehicle_s)
                    vehicles_ml.append(new_vehicle_m)
######################################################################################################################
def main():
    global simulation_running
    pygame.init()

    # Load both graphs
    graph_static, entry_static, exit_static = load_graph_from_csv("Directed_Graph - Static.csv")
    graph_ml, entry_ml, exit_ml = load_graph_from_csv("Directed_Graph - Machine_Learning.csv")

    # Create a window
    screen = pygame.display.set_mode((1300, 1000))
    pygame.display.set_caption("Traffic Simulation: Static vs. Machine Learning Controlled Traffic Signals")

    # Load background
    background_img = pygame.image.load("images\Grid_Sim_Background.png").convert()
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
    motorcycle_images = {
        "southside": pygame.image.load("images/motorcycle_southside.png").convert_alpha(),
        "northside": pygame.image.load("images/motorcycle_northside.png").convert_alpha(),
        "eastside":  pygame.image.load("images/motorcycle_eastside.png").convert_alpha(),
        "westside":  pygame.image.load("images/motorcycle_westside.png").convert_alpha()
    }

    
    # Load traffic light images for horizontal and vertical nodes.
    horizontal_images = {
        "red": pygame.image.load("images/traffic_light_right_red.png").convert_alpha(),
        "yellow": pygame.image.load("images/traffic_light_right_yellow.png").convert_alpha(),
        "green": pygame.image.load("images/traffic_light_right_green.png").convert_alpha()
    }
    vertical_images = {
        "red": pygame.image.load("images/traffic_light_left_red.png").convert_alpha(),
        "yellow": pygame.image.load("images/traffic_light_left_yellow.png").convert_alpha(),
        "green": pygame.image.load("images/traffic_light_left_green.png").convert_alpha()
    }

    # Create traffic lights for each graph.
    static_traffic_lights = create_traffic_lights(graph_static, horizontal_images, vertical_images)
    ml_traffic_lights = create_traffic_lights(graph_ml, horizontal_images, vertical_images)

    lights_state_static = {tl.node_name: tl for tl in static_traffic_lights}
    lights_state_ml = {tl.node_name: tl for tl in ml_traffic_lights}

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
            car_images, truck_images, motorcycle_images,
            lights_state_static,
            lights_state_ml,
        ),
        daemon=True
    )
    spawner_thread.start()

    running = True
    while running:
        dt = clock.tick(120)

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
        
        # Update and draw static side traffic lights.
        for tl in static_traffic_lights:
            tl.update()
            tl.draw(screen)
        for tl in ml_traffic_lights:
            tl.update()
            tl.draw(screen)

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