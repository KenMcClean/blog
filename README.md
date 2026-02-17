## Edge Detection
*edge_detection.py*
Here’s the challenge: there’s an image that consists of a white background, black text, and an inner image underneath.   You want to crop the text off the top, leaving just the inner image.

To complicate matters, you have several thousand of these images, and they’re all different sizes.  This precludes scripting a solution that just chops X number of pixels off the top of each image.

So how do we detect the transition between text and image, using Python?

## Reddit History Wiper
### Please note that this script no longer works, after Reddit made some changes to their API
This script utilizes the undocumented Reddit "Shreddit" API to first overwrite, then delete the history of a Reddit account.
