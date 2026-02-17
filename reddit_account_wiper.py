'''
This script no longer works.  When it did work, it used the undocumented Reddit "Shreddit" API, and cookies from an already-logged in account, to wipe the history of a Reddit account.

Here's the original blurb that went with the script:



There’s no easy way to bulk delete the content of a Reddit account. It’s possible to delete the account itself, but posts and comments are persistent.   By default, the only option is to delete this content one click at a time.

This is by design. Reddit’s business model is predicated on having both a current and historical body of content, with which they can continue to draw in new users.  Allowing users to delete content in bulk would be antithetical to that.

The motivations of Reddit and the desire of some of its customers can be assumed to be in contrast, in this case.

In addition to not allowing bulk deletion of data, Reddit has a tendency to un-delete content that has been deleted.  This is not a paranoid statement, but rather is the simple truth: I have seen content re-appear on my account, months after I deleted it.

For that reason, we need a tool that does two things. First, it should overwrite the content of all posts and comments.  Second, it should delete that overwritten content.   In this way, even content that is undeleted can be assumed to be of little concern.
The Solution

In the interest of privacy and safety, it is not sufficient to simply overwrite comments with the same string. This provides a vector by which the contents of a deleted account can be associated and collated. Instead, the content with which the comments are overwritten is a random string of numbers and letters, and is itself a random length. 

The script uses existing cookies within the browser to perform these actions. In this way, we sidestep Reddit’s refusal to provide sanctioned API access to the “Shreddit” system.    It first overwrites each comment, and then deletes it.

Because this approach takes a roundabout path to get to where we’re going, it typically must be run several times in a row in order to delete all content.   This is one of the areas in which the script could definitely be improved.



'''



import requests
from bs4 import BeautifulSoup
import browser_cookie3
import time
import random
import string

# Fetch cookies from Firefox
firefox_cookies = browser_cookie3.firefox()

# Define the domain for which you need cookies
domain = ".reddit.com"

# Define the target Reddit username
reddit_username = "<>"

reddit_session_cookie = ""
csrf_token_cookie = ""

for cookie in firefox_cookies:
    if cookie.domain.__contains__("reddit"):
        if cookie.name == "reddit_session":
            reddit_session_cookie = cookie.value
    if cookie.name == "csrf_token":
        csrf_token_cookie = cookie.value

exp_cookie = f'reddit_session="{reddit_session_cookie}"; csrf_token={csrf_token_cookie};'

url = f'https://www.reddit.com/svc/shreddit/profiles/profile_overview-more-posts/new/?t=ALL&name={reddit_username}&feedLength=10000'
headers = {
    'Accept': 'text/vnd.reddit.hybrid+html, text/html;q=0.9',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Cookie': exp_cookie,
}

# Send an HTTP GET request to return the list of posts and comments
response = requests.get(url, headers=headers)

# Parse the HTML response with BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find all elements with the thing-id attribute
elements = soup.find_all(attrs={'thing-id': True})

if elements:
    comment_ids = [element['thing-id'] for element in elements]

    while comment_ids:
        print(f"{len(comment_ids)} remaining.")

        comment_ids = set(comment_ids)
        comment_ids = list(comment_ids)

        url = 'https://www.reddit.com/svc/shreddit/graphql'
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json',
            'Cookie': exp_cookie,
        }

        for comment in comment_ids:

            length = random.randint(5, 25)  # Random length between 5 and 25
            characters = string.ascii_letters + string.digits  # All letters and digits
            random_string = ''.join(random.choice(characters) for _ in range(length))


            if comment.startswith("t1"):  # Comment
                # Step 1: Overwrite the comment
                overwrite_data = {
                    "operation": "UpdateComment",
                    "variables": {
                        "input": {
                            "commentId": comment,
                            "content": {"markdown": f"{random_string}"}
                        }
                    },
                    "csrf_token": csrf_token_cookie
                }
                overwrite_response = requests.post(url, headers=headers, json=overwrite_data)
                print(f"Overwrite response for {comment}: {overwrite_response.json()}")

                time.sleep(1)  # Delay between overwrite and delete

                # Step 2: Delete the comment
                delete_data = {
                    "operation": "DeleteComment",
                    "variables": {
                        "input": {
                            "commentId": comment
                        }
                    },
                    "csrf_token": csrf_token_cookie
                }
                delete_response = requests.post(url, headers=headers, json=delete_data)
                print(f"Delete response for {comment}: {delete_response.json()}")
                comment_ids.remove(comment)

            elif comment.startswith("t3"):  # Post
                delete_data = {
                    "operation": "DeletePost",
                    "variables": {
                        "input": {
                            "postId": comment
                        }
                    },
                    "csrf_token": csrf_token_cookie
                }
                delete_response = requests.post(url, headers=headers, json=delete_data)
                print(f"Delete response for {comment}: {delete_response.json()}")
                comment_ids.remove(comment)
else:
    print("Reached the end of the content.")
