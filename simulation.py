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
        "north": pygame.image.load("images/car_northside.png"),
        "south": pygame.image.load("images/car_southside.png"),
        "east": pygame.image.load("images/car_eastside.png"),
        "west": pygame.image.load("images/car_westside.png"),
        "background": pygame.image.load("images/Grid_background.png")
    }
    return images

def generate_cars(screen_width, screen_height):
    # Calculate scaling percentages using the function
    width_adjustment_percent, height_adjustment_percent = calculate_scaling_percentages(screen_width, screen_height)

    # Adjusted car positions after scaling
    car_positions = {
        "east": [
            [(int(7 * width_adjustment_percent), int(560 * height_adjustment_percent)), 
             (int(1195 * width_adjustment_percent), int(560 * height_adjustment_percent))],
            [(int(7 * width_adjustment_percent), int(599 * height_adjustment_percent)), 
             (int(1195 * width_adjustment_percent), int(599 * height_adjustment_percent))],
            [(int(7 * width_adjustment_percent), int(1100 * height_adjustment_percent)), 
             (int(1195 * width_adjustment_percent), int(1100 * height_adjustment_percent))],
            [(int(7 * width_adjustment_percent), int(1139 * height_adjustment_percent)), 
             (int(1195 * width_adjustment_percent), int(1139 * height_adjustment_percent))]
        ],
        "south": [
            [(int(319 * width_adjustment_percent), int(6 * height_adjustment_percent)), 
             (int(1500 * width_adjustment_percent), int(6 * height_adjustment_percent))],
            [(int(355 * width_adjustment_percent), int(6 * height_adjustment_percent)), 
             (int(1537 * width_adjustment_percent), int(6 * height_adjustment_percent))],
            [(int(740 * width_adjustment_percent), int(6 * height_adjustment_percent)), 
             (int(1920 * width_adjustment_percent), int(6 * height_adjustment_percent))],
            [(int(777 * width_adjustment_percent), int(6 * height_adjustment_percent)), 
             (int(1958 * width_adjustment_percent), int(6 * height_adjustment_percent))]
        ],
        "west": [
            [(int(1157 * width_adjustment_percent), int(482 * height_adjustment_percent)), 
             (int(2350 * width_adjustment_percent), int(482 * height_adjustment_percent))],
            [(int(1157 * width_adjustment_percent), int(520 * height_adjustment_percent)), 
             (int(2350 * width_adjustment_percent), int(520 * height_adjustment_percent))],
            [(int(1157 * width_adjustment_percent), int(1021 * height_adjustment_percent)), 
             (int(2350 * width_adjustment_percent), int(1021 * height_adjustment_percent))],
            [(int(1157 * width_adjustment_percent), int(1060 * height_adjustment_percent)), 
             (int(2350 * width_adjustment_percent), int(1060 * height_adjustment_percent))]
        ],
        "north": [
            [(int(399 * width_adjustment_percent), int(1625 * height_adjustment_percent)), 
             (int(1580 * width_adjustment_percent), int(1625 * height_adjustment_percent))],
            [(int(437 * width_adjustment_percent), int(1625 * height_adjustment_percent)), 
             (int(1618 * width_adjustment_percent), int(1625 * height_adjustment_percent))],
            [(int(819 * width_adjustment_percent), int(1625 * height_adjustment_percent)), 
             (int(2000 * width_adjustment_percent), int(1625 * height_adjustment_percent))],
            [(int(858 * width_adjustment_percent), int(1625 * height_adjustment_percent)), 
             (int(2039 * width_adjustment_percent), int(1625 * height_adjustment_percent))]
        ]
    }

    cars = []
    for direction, points in car_positions.items():
        for static, ml in points:
            cars.append(Car(static[0], static[1], direction))
            cars.append(Car(ml[0], ml[1], direction))

    return cars


def process_background(background, screen_size):
    rotated_background = pygame.transform.rotate(background, 90)
    scaled_background = pygame.transform.smoothscale(rotated_background, screen_size)
    return scaled_background

class Car:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.image = pygame.image.load(f"images/car_{direction}side.png")

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

def main():
    screen = initialize_pygame()
    images = load_images()

    screen_width, screen_height = screen.get_size()
    background = process_background(images["background"], (screen_width, screen_height))

    # Dynamically calculate scaling percentages
    width_adjustment_percent, height_adjustment_percent = calculate_scaling_percentages(screen_width, screen_height)

    cars = generate_cars(screen_width, screen_height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background, (0, 0))

        for car in cars:
            car.render(screen)

        pygame.display.flip()
        time.sleep(0.02)  # Add a short delay for smooth rendering

    pygame.quit()


if __name__ == "__main__":
    main()