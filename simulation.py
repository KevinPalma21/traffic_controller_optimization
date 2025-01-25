import random
import time
import threading
import pygame
import sys
import tkinter as tk

# Function to get dynamic screen size
def get_screen_size():
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height

# Function to calculate scaling percentages
def calculate_scaling_percentages(screen_width, screen_height):
    original_width, original_height = 2360, 1640
    width_adjustment_percent = screen_width / original_width
    height_adjustment_percent = screen_height / original_height
    return width_adjustment_percent, height_adjustment_percent


def initialize_pygame():
    pygame.init()
    screen_width, screen_height = get_screen_size()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Traffic Simulation")
    return screen

def load_images():
    images = {
        "car_north": pygame.image.load("images/car_northside.png"),
        "car_south": pygame.image.load("images/car_southside.png"),
        "car_east": pygame.image.load("images/car_eastside.png"),
        "car_west": pygame.image.load("images/car_westside.png"),
        "motorcycle_north": pygame.image.load("images/motorcycle_northside.png"),
        "motorcycle_south": pygame.image.load("images/motorcycle_southside.png"),
        "motorcycle_east": pygame.image.load("images/motorcycle_eastside.png"),
        "motorcycle_west": pygame.image.load("images/motorcycle_westside.png"),
        "truck_north": pygame.image.load("images/truck_northside.png"),
        "truck_south": pygame.image.load("images/truck_southside.png"),
        "truck_east": pygame.image.load("images/truck_eastside.png"),
        "truck_west": pygame.image.load("images/truck_westside.png"),

        "background": pygame.image.load("images/Grid_background.png")
    }
    return images

def generate_cars(screen_width, screen_height):
    # Calculate scaling percentages using the function
    width_adjustment_percent, height_adjustment_percent = calculate_scaling_percentages(screen_width, screen_height)

    # Adjusted car positions after scaling
    car_positions = {
        "east": [
            [(int(4 * width_adjustment_percent), int(552 * height_adjustment_percent)), 
             (int(1191 * width_adjustment_percent), int(552 * height_adjustment_percent))],
            [(int(4 * width_adjustment_percent), int(591 * height_adjustment_percent)), 
             (int(1191 * width_adjustment_percent), int(591 * height_adjustment_percent))],
            [(int(4 * width_adjustment_percent), int(1092 * height_adjustment_percent)), 
             (int(1191 * width_adjustment_percent), int(1092 * height_adjustment_percent))],
            [(int(4 * width_adjustment_percent), int(1131 * height_adjustment_percent)), 
             (int(1191 * width_adjustment_percent), int(1131 * height_adjustment_percent))]
        ],
        "south": [
            [(int(309 * width_adjustment_percent), int(4 * height_adjustment_percent)), 
             (int(1490 * width_adjustment_percent), int(4 * height_adjustment_percent))],
            [(int(350 * width_adjustment_percent), int(4 * height_adjustment_percent)), 
             (int(1530 * width_adjustment_percent), int(4 * height_adjustment_percent))],
            [(int(730 * width_adjustment_percent), int(4 * height_adjustment_percent)), 
             (int(1910 * width_adjustment_percent), int(4 * height_adjustment_percent))],
            [(int(770 * width_adjustment_percent), int(4 * height_adjustment_percent)), 
             (int(1953 * width_adjustment_percent), int(4 * height_adjustment_percent))]
        ],
        "west": [
            [(int(1127 * width_adjustment_percent), int(472 * height_adjustment_percent)), 
             (int(2317 * width_adjustment_percent), int(472 * height_adjustment_percent))],
            [(int(1127 * width_adjustment_percent), int(510 * height_adjustment_percent)), 
             (int(2317 * width_adjustment_percent), int(510 * height_adjustment_percent))],
            [(int(1127 * width_adjustment_percent), int(1011 * height_adjustment_percent)), 
             (int(2317 * width_adjustment_percent), int(1011 * height_adjustment_percent))],
            [(int(1127 * width_adjustment_percent), int(1050 * height_adjustment_percent)), 
             (int(2317 * width_adjustment_percent), int(1050 * height_adjustment_percent))]
        ],
        "north": [
            [(int(389 * width_adjustment_percent), int(1600 * height_adjustment_percent)), 
             (int(1570 * width_adjustment_percent), int(1600 * height_adjustment_percent))],
            [(int(430 * width_adjustment_percent), int(1600 * height_adjustment_percent)), 
             (int(1608 * width_adjustment_percent), int(1600 * height_adjustment_percent))],
            [(int(809 * width_adjustment_percent), int(1600 * height_adjustment_percent)), 
             (int(1990 * width_adjustment_percent), int(1600 * height_adjustment_percent))],
            [(int(851 * width_adjustment_percent), int(1600 * height_adjustment_percent)), 
             (int(2032 * width_adjustment_percent), int(1600 * height_adjustment_percent))]
        ]
    }

    cars = []
    for direction, points in car_positions.items():
        for static, ml in points:
            cars.append(Car(static[0], static[1], direction, width_adjustment_percent, height_adjustment_percent))
            cars.append(Car(ml[0], ml[1], direction, width_adjustment_percent, height_adjustment_percent))

    return cars


def process_background(background, screen_size):
    rotated_background = pygame.transform.rotate(background, 90)
    scaled_background = pygame.transform.smoothscale(rotated_background, screen_size)
    return scaled_background

class Car:
    def __init__(self, x, y, direction, width_percent, height_percent):
        self.x = x
        self.y = y
        self.direction = direction
        self.image = pygame.image.load(f"images/car_{direction}side.png")
        original_width , original_height = self.image.get_size()
        scaled_width = int(original_width * width_percent)
        scaled_height = int(original_height * height_percent)
        self.image = pygame.transform.smoothscale(self.image, (scaled_width, scaled_height))

    def move(self):
        if self.direction == "east":
            self.x += 2
        elif self.direction == "south":
            self.y += 2
        elif self.direction == "west":
            self.x -= 2
        elif self.direction == "north":
            self.y -= 2

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

def vehicle_vanishing(vehicle,x,y, screen_width, screen_height):
    width_adjustment_percent, height_adjustment_percent = calculate_scaling_percentages(screen_width, screen_height)
    vanishing_points = [
        (int(389 * width_adjustment_percent), int(4 * height_adjustment_percent)) , (int(809 * width_adjustment_percent), int(4 * height_adjustment_percent)) ,
        (int(1570 * width_adjustment_percent), int(4 * height_adjustment_percent)) , (int(1990 * width_adjustment_percent), int(4 * height_adjustment_percent)) ,
        (int(430 * width_adjustment_percent), int(4 * height_adjustment_percent)) , (int(851 * width_adjustment_percent), int(4 * height_adjustment_percent)) ,
        (int(1608 * width_adjustment_percent), int(4 * height_adjustment_percent)) , (int(2032 * width_adjustment_percent), int(4 * height_adjustment_percent)) ,
        (int(309 * width_adjustment_percent), int(1600 * height_adjustment_percent)) , (int(730 * width_adjustment_percent), int(1600 * height_adjustment_percent)) ,
        (int(1490 * width_adjustment_percent), int(1600 * height_adjustment_percent)) , (int(1910 * width_adjustment_percent), int(1600 * height_adjustment_percent)) ,
        (int(350 * width_adjustment_percent), int(1600 * height_adjustment_percent)) , (int(770 * width_adjustment_percent), int(1600 * height_adjustment_percent)) ,
        (int(1530 * width_adjustment_percent), int(1600 * height_adjustment_percent)) , (int(1953 * width_adjustment_percent), int(1600 * height_adjustment_percent)) ,
        (int(1127 * width_adjustment_percent), int(552 * height_adjustment_percent)) , (int(1127 * width_adjustment_percent), int(1092 * height_adjustment_percent)) ,
        (int(2317 * width_adjustment_percent), int(552 * height_adjustment_percent)) , (int(2317 * width_adjustment_percent), int(1092 * height_adjustment_percent)) ,
        (int(1127 * width_adjustment_percent), int(591 * height_adjustment_percent)) , (int(1127 * width_adjustment_percent), int(1131 * height_adjustment_percent)) ,
        (int(2317 * width_adjustment_percent), int(591 * height_adjustment_percent)) , (int(2317 * width_adjustment_percent), int(1131 * height_adjustment_percent)) ,
        (int(4 * width_adjustment_percent), int(472 * height_adjustment_percent)) , (int(4 * width_adjustment_percent), int(1011 * height_adjustment_percent)) ,
        (int(1191 * width_adjustment_percent), int(472 * height_adjustment_percent)) , (int(1191 * width_adjustment_percent), int(1011 * height_adjustment_percent)) ,
        (int(4 * width_adjustment_percent), int(510 * height_adjustment_percent)) , (int(4 * width_adjustment_percent), int(1050 * height_adjustment_percent)) ,
        (int(1191 * width_adjustment_percent), int(510 * height_adjustment_percent)) , (int(1191 * width_adjustment_percent), int(1050 * height_adjustment_percent))
    ]

    for vx , vy in vanishing_points:
        if abs(x-vx) <=1 and abs (y - vy) <= 1:
            return True
    return False
def main():
    screen = initialize_pygame()
    images = load_images()

    screen_width, screen_height = screen.get_size()
    background = process_background(images["background"], (screen_width, screen_height))

    width_adjustment_percent, height_adjustment_percent = calculate_scaling_percentages(screen_width, screen_height)

    cars = generate_cars(screen_width, screen_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background, (0, 0))

        for car in cars[:]:
            if vehicle_vanishing(car, car.x, car.y, screen_width, screen_height):
                cars.remove(car)
            else:
                car.move()
                car.render(screen)

        pygame.display.flip()
        time.sleep(0.02)

    pygame.quit()



if __name__ == "__main__":
    main()