import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import sobel

input_folder = ''
# Set the input folder that contains the target images

def detect_inner_image_boundary(image_path):
    try:
        img = Image.open(image_path)
        # Open the image

        img_cropped = img.crop((0, 0, img.width, img.height - 50))
        # Crop the bottom of the image

        img_array = np.array(img_cropped)
        #Convert the cropped image into a Numpy array

        gray_img_array = np.mean(img_array, axis=2)
        #Convert the 3D Numpy array to 2D by taking the mean of the color channel dimension.
        #This has the effect of converting the image data to greyscale, for easier processing.

        edges = sobel(gray_img_array, axis=0)
        #Compute the intensity of gradients row to row.  axis=0 indicates that the measure should be row to row, rather
        #than column-to-column

        edge_intensity = np.sum(edges, axis=1)
        #Collapse the 2D edge-detection result into a 1D array, by summing the edge intensities row by row.

        smoothed_intensity = np.convolve(edge_intensity, np.ones(10) / 10, mode='same')
        #Smooth the edge intensity data to reduce noise

        derivative = np.diff(smoothed_intensity)
        #Calculate the rate of change of the intensity data

        jump_threshold = 15000
        significant_jumps = np.where(np.abs(derivative) > jump_threshold)[0]
        #Determine a value that represents the threshold of significane

        num_jumps = len(significant_jumps)
        print(f"Number of significant jumps detected: {num_jumps}")
        if num_jumps < 2:
            print(f"Not enough significant jumps found in {image_path} for second last jump")
            return None
        #Handle any instances where the image doesn't contain enough jumps that meet the threshold

        second_last_jump = significant_jumps[-2]
        #We're not actually looking for the last jump, but the second last jump

        #******PLOT THE RESULTS******

        plt.figure(figsize=(10, 5))

        plt.subplot(1, 2, 1)
        plt.imshow(img_cropped)
        plt.axhline(y=second_last_jump, color='red', linestyle='--', linewidth=2, label='Second Last Significant Jump')
        plt.title("Original Image with Detected Boundary (After Cropping)")
        plt.legend()

        plt.subplot(1, 2, 2)
        plt.plot(smoothed_intensity, label="Smoothed Intensity")
        plt.plot(np.arange(len(derivative)), derivative, label="Derivative", color='orange')
        plt.axvline(x=second_last_jump, color='red', linestyle='--', label="Second Last Significant Jump")

        for jump_index in significant_jumps:
            if np.abs(derivative[jump_index]) > jump_threshold:
                plt.text(jump_index, derivative[jump_index], f'{derivative[jump_index]:.0f}', color='green', fontsize=10,
                         verticalalignment='bottom', horizontalalignment='center')

        plt.title("Edge Intensity and Derivative with Jump Labels")
        plt.legend()
        plt.show()

        return second_last_jump
        #******FINISHED PLOTTING THE RESULTS******

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    #******FINISHED IMAGE PROCESSING******

image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('webp', 'png', 'jpg', 'jpeg'))]

if not image_files:
    print("No valid image files found in the folder.")
else:
    for filename in image_files[:5]:
        image_path = os.path.join(input_folder, filename)
        print(f"Analyzing {filename}")
        detected_row = detect_inner_image_boundary(image_path)
        if detected_row is not None:
            print(f"Detected second last significant jump at row {detected_row}")
        else:
            print("No significant boundary detected.")
