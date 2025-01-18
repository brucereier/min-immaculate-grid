import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import time
import random

teams = [
    "crd", "atl", "rav", "buf", "car", "chi", "cin", "dal", "den", "det",
    "gnb", "htx", "clt", "jax", "kan", "rai", "sdg", "ram", "mia", "min",
    "nwe", "nor", "nyg", "cle", "nyj", "phi", "pit", "sfo", "sea", "tam",
    "oti", "was"
]

players = defaultdict(set)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Loop through all pairs of teams
for i in range(len(teams) - 1):
    for j in range(i + 1, len(teams)):
        url = (
            "https://www.pro-football-reference.com/friv/"
            f"players-who-played-for-multiple-teams-franchises.fcgi?"
            f"level=franch&t1={teams[i]}&t2={teams[j]}&t3=--&t4=--"
        )
        connection = f"{teams[i]}-{teams[j]}"
        print(f"Scraping {connection} from {url}")

        # Add a random pause before each request
        time.sleep(random.uniform(7, 10))

        try:
            # Make the GET request
            resp = requests.get(url, headers=headers)

            # Check if the request was successful
            if resp.status_code == 429:
                print("Rate limit hit. Sleeping for a longer period...")
                time.sleep(random.uniform(20, 30))  # Sleep longer and retry
                continue  # Retry the current URL after sleeping
            elif resp.status_code != 200:
                print(f"Failed to fetch {
                      url}, status code: {resp.status_code}")
                continue

            # Parse the page using BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract player data
            ct = 0
            for tr in soup.find_all("tr"):
                th = tr.find("th")
                if th:
                    a = th.find("a")
                    if a and a.has_attr("href"):
                        # Store the player's URL (href) and the connection
                        ct += 1
                        players[a["href"]].add(connection)

            print(f"Connections for {connection}: {
                  ct} players found. Total players: {len(players)}")

        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            continue

# Write results to a text file
with open("players.txt", "w", encoding="utf-8") as f:
    for player_href, connections in players.items():
        connections_str = ",".join(sorted(connections))
        f.write(f"{player_href}: {connections_str}\n")
