import pygame
import time
import sys
import threading
import random

print("Hello World")  # For testing
# Please work

# Initialize pygame
pygame.init()

# Load the background image
background_image = pygame.image.load("images\Grid_background.png")

# Set screen dimensions
screenWidth = 2360
screenHeight = 1640
screenSize = (screenWidth, screenHeight)

# Rotate the background image
background_Rotated = pygame.transform.rotate(background_image, 90)
background_new_size = pygame.transform.smoothscale(background_Rotated,(2360,1640))
# Create the screen and set the caption
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption("SIMULATION")

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Handle quit event
            running = False
    
    # Draw the rotated background image
    screen.blit(background_new_size, (0, 0))

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
