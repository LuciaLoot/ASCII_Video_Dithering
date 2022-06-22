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


# ----------------------------------------------------------------------------------------------------------------------
# Function to split frames using cv2
def extractImages(pathIn, pathOut, frameRate):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success, image = vidcap.read()
    success = True
    while success:
        print('Currently exporting frame :', count)
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count*1000/frameRate))    # added this line
        success, image = vidcap.read()
        cv2.imwrite(pathOut + "\\%05d.png" % count, image)     # save frame as PNG file
        count = count + 1


# ----------------------------------------------------------------------------------------------------------------------
# Algorithm to split the frames of input video in 'D:/VIDEO#onTheFence_HBFS/source_mp4' to '/source_png'
# It first checks whether or not some PNGs have already been generated (if that's the case, it skips to the next part)
if len(os.listdir('D:/VIDEO#onTheFence_HBFS/source_png')) == 0:
    print("'Source_png' folder is empty : extracting frames.")
    extractImages('D:/VIDEO#onTheFence_HBFS/source_mp4/input.mp4', 'D:/VIDEO#onTheFence_HBFS/source_png', 15)
else:
    print("'Source_png' folder is not empty : moving on.")

# ----------------------------------------------------------------------------------------------------------------------
# Main loop running for each frame exported in 'D:/VIDEO#onTheFence_HBFS/source_png'
for file in os.listdir('D:/VIDEO#onTheFence_HBFS/source_png'):
    print('Currently dithering :', file)
    os.chdir('D:/VIDEO#onTheFence_HBFS/source_png')
    # ------------------------------------------------------------------------------------------------------------------
    # Importing source image.
    source_image = imageio.imread(str(file))

    # Storing dimensions of source image.
    source_dimy = len(source_image)
    source_dimx = len(source_image[0])

    # ------------------------------------------------------------------------------------------------------------------
    # Storing dimensions of downsampled image.
    resolution = 10
    dimy = int(source_dimy / resolution)
    dimx = int(source_dimx / resolution)

    # Rescaling source image to a downsampled version.
    downsampled_image = cv2.resize(source_image, (dimx, dimy))

    # Increasing its contrast.
    downsampled_image = skimage.exposure.rescale_intensity(downsampled_image, in_range=(20, 190), out_range=(0, 255))

    # For testing purposes :
    # ds = Image.fromarray(downsampled_image)
    # ds.save("ds.png")

    # ------------------------------------------------------------------------------------------------------------------
    # Creating the filtering matrix (for the moment a blank array).
    filtering_matrix = numpy.empty([dimy, dimx, 4], dtype="uint8")

    # Creating the final dithered matrix (for the moment a blank array).
    dithered_matrix = numpy.empty([dimy, dimx], dtype="str")

    # ------------------------------------------------------------------------------------------------------------------
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
    # ------------------------------------------------------------------------------------------------------------------
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

    # with open("test.txt", "w") as txt_file:
    #     for line in dithered_matrix:
    #         txt_file.write(" ".join(line) + "\n")

    # ------------------------------------------------------------------------------------------------------------------
    # Creating a grayscale downsampled image for testing purposes.
    # image_grayscale = numpy.empty([dimy, dimx, 3], dtype="uint8")
    # for y in range(dimy):
    #     for x in range(dimx):
    #         image_grayscale[y, x, 0] = filtering_matrix[y, x, 3]
    #         image_grayscale[y, x, 1] = filtering_matrix[y, x, 3]
    #         image_grayscale[y, x, 2] = filtering_matrix[y, x, 3]
    #
    # gs = Image.fromarray(image_grayscale)
    # gs.save("gs.png")
    #
    # ------------------------------------------------------------------------------------------------------------------
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

    # Saving pygame output as png.
    os.chdir('D:/VIDEO#onTheFence_HBFS/dither_gen')
    pygame.image.save(screen, file)

# Exiting pygame.
pygame.quit()

# ----------------------------------------------------------------------------------------------------------------------
# Dithered PNGs to lossless .avi (for testing purposes, better to build it in Premiere Pro / After Effects).
print("Launching ffmpeg to export test.avi.")
subprocess.call(['ffmpeg',
                 '-r', '15',
                 '-f', 'image2',
                 '-s', '1920x1080',
                 '-i', '%05d.png',
                 '-vcodec', 'libx264',
                 '-lossless', '1',
                 '-crf', '0',
                 'test.avi'])
