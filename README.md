## Edge Detection
*edge_detection.py*
Here’s the challenge: there’s an image that consists of a white background, black text, and an inner image underneath.   You want to crop the text off the top, leaving just the inner image.

To complicate matters, you have several thousand of these images, and they’re all different sizes.  This precludes scripting a solution that just chops X number of pixels off the top of each image.

So how do we detect the transition between text and image, using Python?

Please note that I absolutely used ChatGPT to work out the edge detection math on this script.  I’ll fully admit to that.  It was an area in which I had zero experience, and I learned quite a lot.

The Approach

Essentially we need to quantify the difference in edge intensity between each row, and look for major “jumps” in the value that represents edge intensity.  In other words, the white gap between the text and the image will change drastically as soon as the first row of the inner image is detected.

This is accomplished over several steps. 

    The image is converted to a grayscale array of data.  Grayscale gradients are much easier to work with.
    The Sobel operator is used to create a version of the image that highlights the edges
    The intensity of each edge is summed along the row, to create a single value that represents the entire edge
    The edge intensity data is smoothed to reduce noise
    The data in the array of smoothed intensity data is diffed, in order to quantify the difference between the edges
    Significant changes in edge intensity are determined, by establishing a threshold that represents the minimum “amount” of intensity
    The resulting values are plotted over the image, in order to visually display the results that the script has found for each image.

So, in short, we convert the image to grayscale, determine how drastic the difference between each row of pixels is, and pick a row that represents our needs.

