#!/usr/bin/env python3

from pyaml import yaml
import os
from mastodon import Mastodon
import argparse
import datetime
from tqdm import tqdm
import time
import pytz

def datetype(s):
    return pytz.utc.localize(datetime.datetime.strptime(s, '%Y-%m-%d'))

parser = argparse.ArgumentParser(description="Mass-delete fedi posts")
parser.add_argument("--from-date", type=datetype, default=pytz.utc.localize(datetime.datetime.min))
parser.add_argument("--to-date", type=datetype, default=pytz.utc.localize(datetime.datetime.max))
parser.add_argument("--public-only", action="store_true")

with open("fedi.login", "r") as f:
    login = yaml.load(f.read(), Loader=yaml.FullLoader)

if not os.path.exists(".oauth.secret"):
    Mastodon.create_app(
        "purger", api_base_url=login["instance"], to_file=".oauth.secret"
    )
if not os.path.exists(".user.secret"):
    mastodon = Mastodon(client_id=".oauth.secret", api_base_url=login["instance"])
    mastodon.log_in(login["username"], login["password"], to_file=".user.secret")

mastodon = Mastodon(access_token=".user.secret", api_base_url=login["instance"])

def matches(post, from_date, to_date, public_only):
    date_match = from_date <= post["created_at"] <= to_date
    v_match = True if public_only is False else post["visibility"] in ["public", "unlisted"]
    return date_match and v_match
    

if __name__ == "__main__":
    args = parser.parse_args()
    my_id = mastodon.me()["id"]
    max_id = None

    print("Planning to delete all statuses posted between {} and {}".format(
        args.from_date, args.to_date))
    to_delete = []
    print("Collating posts...")
    while 1:
        time.sleep(0.1)
        print("-- Grabbing posts from {}".format(max_id))
        posts = mastodon.account_statuses(my_id, max_id=max_id, limit=100)
        max_id = posts[-1]["id"]
        print("--- {}".format(posts[-1]["created_at"]))
        if len(posts) == 0:
            break
        if posts[0]["created_at"] > args.to_date:
            continue
        if posts[-1]["created_at"] < args.from_date:
            break
        to_delete += [x["id"] for x in posts if matches(x, args.from_date, args.to_date, args.public_only)]
    print("Planning to delete {} posts".format(len(to_delete)))
    if input("Continue? (y/n) ").lower() == "y":
        for post in tqdm(to_delete):
            mastodon.status_delete(post)
            time.sleep(0.1)
        pass
    else:
        print("Aborting!")
