# ----------------------------------------------------------------------------------------------------------------------
# Libraries and dependencies
import imageio.v2 as imageio
import numpy
import cv2
from PIL import Image
import pygame
import sys


# Functions
def blitlines(surf, text, renderer, color, x, y):
    h = renderer.get_height()
    lines = text.split('\n')
    for i, ll in enumerate(lines):
        txt_surface = renderer.render(ll, True, color)
        surf.blit(txt_surface, (x, y + (i * h)))


# ----------------------------------------------------------------------------------------------------------------------
# Importing source image.
source_image = imageio.imread("test.png")

# Storing dimensions of source image.
source_dimy = len(source_image)
source_dimx = len(source_image[0])

# ----------------------------------------------------------------------------------------------------------------------
# Storing dimensions of downsampled image.
resolution = 10
dimy = int(source_dimy / resolution)
dimx = int(source_dimx / resolution)

# Rescaling source image to a downsampled version.
downsampled_image = cv2.resize(source_image, (dimx, dimy))

# For testing purposes :
ds = Image.fromarray(downsampled_image)
ds.save("ds.png")

# ----------------------------------------------------------------------------------------------------------------------
# Creating the filtering matrix (for the moment a blank array).
filtering_matrix = numpy.empty([dimy, dimx, 4], dtype="uint8")

# Creating the final dithered matrix (for the moment a blank array).
dithered_matrix = numpy.empty([dimy, dimx], dtype="str")

# ----------------------------------------------------------------------------------------------------------------------
# Filling each pixel of the dithering matrix and of the grayscale image with the pixels of the downsampled image.
for y in range(dimy):
    for x in range(dimx):
        filtering_matrix[y, x, 0] = downsampled_image[y, x, 0]
        filtering_matrix[y, x, 1] = downsampled_image[y, x, 1]
        filtering_matrix[y, x, 2] = downsampled_image[y, x, 2]
        filtering_matrix[y, x, 3] = (
                                            int(downsampled_image[y, x, 0])
                                            + int(downsampled_image[y, x, 1])
                                            + int(downsampled_image[y, x, 2])
                                    ) / 3
# ----------------------------------------------------------------------------------------------------------------------
# Dithering algorithm :
# 0 : Blank space
# 1-64 : .
# 65-128 : -
# 129-192 : *
# 193-256 : #

for y in range(dimy):
    for x in range(dimx):
        if int(filtering_matrix[y, x, 3]) == 0:
            dithered_matrix[y, x] = " "

        elif 0 < int(filtering_matrix[y, x, 3]) < 65:
            dithered_matrix[y, x] = "·"

        elif 64 < int(filtering_matrix[y, x, 3]) < 129:
            dithered_matrix[y, x] = "-"

        elif 128 < int(filtering_matrix[y, x, 3]) < 193:
            dithered_matrix[y, x] = "+"

        elif 192 < int(filtering_matrix[y, x, 3]):
            dithered_matrix[y, x] = "#"

with open("test.txt", "w") as txt_file:
    for line in dithered_matrix:
        txt_file.write(" ".join(line) + "\n")

# ----------------------------------------------------------------------------------------------------------------------
# Creating a grayscale downsampled image for testing purposes.
image_grayscale = numpy.empty([dimy, dimx, 3], dtype="uint8")
for y in range(dimy):
    for x in range(dimx):
        image_grayscale[y, x, 0] = filtering_matrix[y, x, 3]
        image_grayscale[y, x, 1] = filtering_matrix[y, x, 3]
        image_grayscale[y, x, 2] = filtering_matrix[y, x, 3]

gs = Image.fromarray(image_grayscale)
gs.save("gs.png")

# ----------------------------------------------------------------------------------------------------------------------
# Color constants for pygame.
background_colour = (0, 0, 0)

# Initialising pygame, creating a screen and setting up a font.
pygame.init()
screen = pygame.display.set_mode((source_dimx, source_dimy))
font = pygame.font.Font('Consolas.ttf', 15)

# Fill the screen with black.
screen.fill(background_colour)

# Display "dithering text" on screen.
for x in range(dimx):
    for y in range(dimy):
        text = font.render(str(dithered_matrix[y, x]), True, (
            int(filtering_matrix[y, x, 0]),
            int(filtering_matrix[y, x, 1]),
            int(filtering_matrix[y, x, 2])
        ))
        textRect = text.get_rect()
        textRect.center = (x*resolution+10, y*resolution+5)
        screen.blit(text, textRect)

# Update the full display Surface to the screen.
pygame.display.flip()

# Saving pygame output as png.
pygame.image.save(screen, 'pygame.png')

# Exiting pygame.
sys.exit()
