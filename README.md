
# ARS GRATIA ARTIS
Little or no justfication is provided for many of these scripts.  I wrote them simply to see if I could. 



## Banana Bread
*banana_bread.txt*

It's a recipe for banana bread.  It's also my love letter to the importance of being precise.

## Edge Detection
*edge_detection.py*

Here’s the challenge: there’s an image that consists of a white background, black text, and an inner image underneath.   You want to crop the text off the top, leaving just the inner image.

To complicate matters, you have several thousand of these images, and they’re all different sizes.  This precludes scripting a solution that just chops X number of pixels off the top of each image.

So how do we detect the transition between text and image, using Python?

## Plex scripts
*plex_overseer_title_fetch.py*

Fetches the title of the TV shows on a Plex server setup.
*plex_auth.py*

Used to authenticate against the Plex server, required by all other Plex scripts in this repository.

## Reddit History Wiper
_Please note that this script no longer works, after Reddit made some changes to their API_

*reddit_account_wiper.py*

This script utilizes the undocumented Reddit "Shreddit" API to first overwrite, then delete the history of a Reddit account.

## YouTube Comment Wiper
*youtube_comment_wiper.js*

This is a script that runs in the browser console, and deletes all of the comments that the logged-in YouTube account has made.
