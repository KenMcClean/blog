from plexapi.myplex import MyPlexAccount

plex_username = ""
plex_password = ""
plex_servername = ""
account = MyPlexAccount(f'plex_username', f'{plex_password')
plex = account.resource(f'{plex_servername').connect()  # returns a PlexServer instance

print(plex._token)
