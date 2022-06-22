# ----------------------------------------------------------------------------------------------------------------------
# Libraries and dependencies
import os
import imageio.v2 as imageio
import numpy
import cv2
import skimage.exposure
# from PIL import Image
import pygame
# import sys
import subprocess
import time

# Importing source video
source_video = cv2.VideoCapture("D:\VIDEO#onTheFence_HBFS\source_mp4\input.mp4")

# Creating a frame counter
frame_counter = 0

while True:
    # Counting frames
    frame_counter += 1
    print("-----------------------------------------------------------------------------------------------------------")
    print("Currently processing frame N°", frame_counter)

    # Global timer
    global_timer_start = time.perf_counter()

    ret, source_image = source_video.read()
    if ret:
        # -------------------------------------------------------------------------------------------------------------
        # Creating a timer for image downscaling
        timer_start = time.perf_counter()

        # Storing dimensions of source image.
        source_dimy = len(source_image)
        source_dimx = len(source_image[0])

        # Storing dimensions of downsampled image.
        resolution = 10
        dimy = int(source_dimy / resolution)
        dimx = int(source_dimx / resolution)

        # Rescaling source image to a downsampled version.
        downsampled_image = cv2.resize(source_image, (dimx, dimy))

        # Timer output for image downscaling
        print("Downscaled frame in", time.perf_counter() - timer_start, "seconds.")

        # -------------------------------------------------------------------------------------------------------------
        # Creating a timer for image filtering
        timer_start = time.perf_counter()

        # Increasing its contrast.
        downsampled_image = skimage.exposure.rescale_intensity(downsampled_image, in_range=(20, 190), out_range=(0, 255))

        # Creating the filtering matrix (for the moment a blank array).
        filtering_matrix = numpy.empty([dimy, dimx, 4], dtype="uint8")

        # Creating the final dithered matrix (for the moment a blank array).
        dithered_matrix = numpy.empty([dimy, dimx], dtype="str")

        # Filling each pixel of the dithering matrix and of the grayscale image with the pixels of the downsampled image.
        for y in range(dimy):
            for x in range(dimx):
                filtering_matrix[y, x, 0] = downsampled_image[y, x, 2]
                filtering_matrix[y, x, 1] = downsampled_image[y, x, 1]
                filtering_matrix[y, x, 2] = downsampled_image[y, x, 0]
                filtering_matrix[y, x, 3] = (
                                                    int(downsampled_image[y, x, 0])
                                                    + int(downsampled_image[y, x, 1])
                                                    + int(downsampled_image[y, x, 2])
                                            ) / 3

        # Timer output for filtering matrix
        print("Filtered frame in", (time.perf_counter() - timer_start) * 1000, "ms.")

        # -------------------------------------------------------------------------------------------------------------
        # Creating a timer for image dithering
        timer_start = time.perf_counter()

        # Dithering algorithm :
            # 0 : Blank space
            # 1-64 : .
            # 65-128 : -
            # 129-192 : *
            # 193-256 : #

        for y in range(dimy):
            for x in range(dimx):
                if int(filtering_matrix[y, x, 3]) < 51:
                    dithered_matrix[y, x] = " "

                elif 50 < int(filtering_matrix[y, x, 3]) < 102:
                    dithered_matrix[y, x] = "·"

                elif 101 < int(filtering_matrix[y, x, 3]) < 153:
                    dithered_matrix[y, x] = "+"

                elif 152 < int(filtering_matrix[y, x, 3]) < 204:
                    dithered_matrix[y, x] = "#"

                elif 203 < int(filtering_matrix[y, x, 3]):
                    dithered_matrix[y, x] = "@"

        # Timer output for dithering matrix
        print("Dithered frame in", (time.perf_counter() - timer_start)*1000, "ms.")

        # -------------------------------------------------------------------------------------------------------------
        # Creating a timer for image displaying
        timer_start = time.perf_counter()

        # Color constants for pygame.
        background_colour = (0, 0, 0)

        # Initialising pygame, creating a screen and setting up a font.
        pygame.init()
        screen = pygame.display.set_mode((source_dimx, source_dimy))
        font = pygame.font.Font('C:/Users/falco/PycharmProjects/ASCII_Video_Dither/Consolas.ttf', 16)

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
                textRect.center = (x * resolution + 10, y * resolution + 5)
                screen.blit(text, textRect)

        # Update the full display Surface to the screen.
        pygame.display.flip()

        # Timer output for image displaying
        print("Displayed frame in", (time.perf_counter() - timer_start)*1000, "ms.")

        # -------------------------------------------------------------------------------------------------------------
        # Creating a timer for image storing
        timer_start = time.perf_counter()

        # Saving pygame output as png.
        os.chdir('D:/VIDEO#onTheFence_HBFS/dither_gen')
        pygame.image.save(screen, str(frame_counter).zfill(5)+'.png')

        # Timer output for image storing
        print("Stored frame in", (time.perf_counter() - timer_start)*1000, "ms.")

        # Output for global timer
        print()
        print("Total processing time :", (time.perf_counter() - global_timer_start)*1000, "ms.")
        print("Average framerate:", 1/(time.perf_counter() - global_timer_start), "FPS.")
        print()

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
