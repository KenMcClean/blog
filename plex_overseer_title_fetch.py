#Fetches the names of the TV shows stored on a Plex server
#Requires the plex_auth.py script

from plexapi.myplex import MyPlexAccount
import json
import requests
import credentials

plex_url = "<plex_url>"
plex_resource_name = "<sever name>"

session_obj = requests.Session()
#Define session object to be used with HTTPS requests
page_size = 20
ski_val = 0

session_obj.get(f"{plex_url}/login")
#Fetch the Overseerr login

payload = {"authToken": credentials.overseerr_authtoken}
resp = session_obj.post("f{plex_url}/api/v1/auth/plex", json=payload)
#Authenticate against Overseerr with a Plex token

account = MyPlexAccount(credentials.plex_username, credentials.plex_password)
plex = account.resource("f{plex_resource_name}").connect()  # returns a PlexServer instance


fetch_requests_info = session_obj.get(f"{plex_url}/api/v1/request?take=20&skip=0")

fetch_requests_json = json.loads(fetch_requests_info.text)

for result in fetch_requests_json["results"]:
     if result['media']['mediaType'] == "tv":
         fetch_tv_req = session_obj.get({f"plex_url}/api/v1/tv/{result['media']['tmdbId']}")
         tv_json = json.loads(fetch_tv_req.text)
         print(tv_json["name"])
