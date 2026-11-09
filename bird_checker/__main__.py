import argparse
import datetime as dt
import json
from pathlib import Path

from bird_checker import api, db

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
RECENT_DAYS = 14
REPORT_DAYS = 7
RARITY = {1: "algemeen", 2: "vrij algemeen", 3: "zeldzaam", 4: "zeer zeldzaam"}


def days_ago(days):
    return (dt.date.today() - dt.timedelta(days=days)).isoformat()


def get_my_species(conn, config):
    fetched_at = db.my_species_fetched_at(conn)
    if fetched_at is None or fetched_at < dt.datetime.now() - dt.timedelta(days=1):
        db.replace_my_species(conn, api.fetch_my_species_ids(config["user_id"]))
    return db.get_my_species(conn)


def check(conn, config):
    first_run = db.is_empty(conn)
    recent_species = db.species_observed_since(conn, days_ago(RECENT_DAYS))
    new_observations = []
    for location in config["locations"]:
        new_observations += db.insert_new(conn, api.fetch_recent_observations(location))
    if first_run:
        return

    my_species = get_my_species(conn, config)
    alerted = set()
    for obs in new_observations:
        species = obs["species_detail"]
        if species["id"] in my_species | recent_species | alerted:
            continue
        alerted.add(species["id"])
        print(
            f"Nieuwe waarneming: {species['name']}, {RARITY.get(obs['rarity'])}\n"
            f"   {obs['date']} bij {obs['location_detail']['name']}\n"
            f"   {obs['permalink']}"
        )


def weekly(conn, config):
    my_species = get_my_species(conn, config)
    rows = [r for r in db.species_summary_since(conn, days_ago(REPORT_DAYS)) if r["species_id"] not in my_species]
    if not rows:
        return
    print(f"Afgelopen {REPORT_DAYS} dagen gespot, nog niet op je lijst:")
    for r in rows:
        print(f"- {r['name']}, {RARITY.get(r['rarity'])}, {r['num_obs']}x, laatst {r['last_seen']}")


def main():
    parser = argparse.ArgumentParser(prog="bird_checker")
    parser.add_argument("command", choices=["check", "weekly"])
    command = parser.parse_args().command
    config = json.loads(CONFIG_PATH.read_text())
    with db.connect() as conn:
        {"check": check, "weekly": weekly}[command](conn, config)


if __name__ == "__main__":
    main()
