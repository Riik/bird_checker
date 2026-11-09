import re

import requests

BASE_URL = "https://waarneming.nl"
BIRDS = 1
HEADERS = {"Accept-Language": "nl"}


def get(url, params=None):
    response = requests.get(url, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response


def fetch_recent_observations(location, days=2):
    url = f"{BASE_URL}/api/v1/observations/around-point/"
    params = {
        "lat": location["lat"],
        "lng": location["lng"],
        "radius": location["radius_meters"],
        "days": days,
        "species_group": BIRDS,
    }
    observations = []
    while url:
        page = get(url, params).json()
        observations += page["results"]
        url, params = page["next"], None
    return observations


def fetch_my_species_ids(user_id):
    params = {"species_group_id": BIRDS, "include_exotic_and_extinct": "on", "include_escapes": "on"}
    html = get(f"{BASE_URL}/users/{user_id}/species/", params).text
    species_ids = {int(i) for i in re.findall(r"/species/(\d+)/statistics/", html)}
    if not species_ids:
        raise RuntimeError("Found no species on my species page, did the page layout change?")
    return species_ids
