# The Bitly API and Python

I’ve started working on a QR-code based inventory management and pricing system.   One of the foundational elements of this system is the ability to print a price tag with a QR code on it, and to be able to update the link associated with that QR code without replacing the sticker.

This is possible if the QR code links to bit.ly instead of directly to the link in question.   So long as the shortened URL is generated under a Bitly account, it can be edited and modified after the fact.

The Bitly API is at the same time well documented, and a bit frustrating.  It’s frustrating because all of the example Python code on the internet uses the bitly_api package, which is apparently either abandoned or complete trash.   For example, all of the examples on the internet result in an error like this:
```
bitly api.bitly _api.Bitly Error: "PERMANENTLY REMOVED"
```
I assume this means that the method has been removed from the class or package, but I couldn’t find a way to fix it.

Instead, let’s use the https requests library to connect to the Bitly API and generate a shortened link.

## The Setup

First things first, you should go check out the Bitly API documentation.  Like any API, life is easier if you read the documentation first.

Second, install the *http requests* package in your Python environment if you haven’t already done so.

Third, generate a Bitly access token.  Documentation on this can be found here: https://dev.bitly.com/docs/getting-started/authentication/

Fourth, grab the *group ID* of your Bitly account.   If you go into your Bitly account settings and then groups, the URL will look something like this:

https://app.bitly.com/settings/organization/Ox1nx1X1pxX/groups/Bo1ntGXNMqT

The bit at the end that looks like Bo1ntGXNMqT is the group ID you’re after. Yours will be different.

## The Code

The code isn’t terribly complicated. We’re making a POST request to the API url, and feeding it the bare minimum JSON.    From the content that is returned, we’re selecting the link parameter.

**The long_url value is the one that needs to change, each time you want to shorten a new URL.**

You also need to supply the bearer token (access token) and the group ID.  Remove the squiggly brackets.

```python
import requests
import json

bitlyAPIDomain = "https://api-ssl.bitly.com/v4/shorten"

headers = {
    'Authorization': 'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

payload = {
    "group_guid": "{group ID}",
    "domain": "bit.ly",
    "long_url": "https://dev.bitly.com"
}

json_payload = json.dumps(payload)
post = json.loads(requests.post(bitlyAPIDomain, headers=headers, data=json_payload).content)

link = post.get("link")

print(link)
```


