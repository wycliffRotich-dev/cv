"""Fetch live AetherGrid stats and write stats/stats.json (+ stats/adrs.json for the README badge).

Rules:
  * Each stat is fetched independently. If one fetch fails, the previous value is kept.
  * A value is only accepted if it is a sane positive integer.
  * Never raises on network failure, so a flaky API cannot break a push.
"""
import json
import os
import re
import sys
import urllib.request

OWNER = "wycliffRotich-dev"
REPO = "aethergrid"
GIST_BADGE = ("https://gist.githubusercontent.com/wycliffRotich-dev/"
              "4b35dff5cea5aa68433713c36c3108bb/raw/aethergrid-test-badge.json")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATS = os.path.join(ROOT, "stats", "stats.json")
ADRS_BADGE = os.path.join(ROOT, "stats", "adrs.json")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cv-live-stats"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", "Bearer " + TOKEN)
        req.add_header("Accept", "application/vnd.github+json")
    return urllib.request.urlopen(req, timeout=20)


def sane(n):
    return isinstance(n, int) and 0 < n < 1_000_000


def fetch_tests():
    # Published by AetherGrid's own CI after a full run against Postgres: "696 passed"
    data = json.load(get(GIST_BADGE))
    m = re.search(r"\d+", str(data.get("message", "")))
    return int(m.group()) if m else None


def fetch_adrs():
    items = json.load(get(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/docs/adr"))
    return len([i for i in items if re.match(r"^\d{4}-.*\.md$", i["name"])])


def fetch_commits():
    resp = get(f"https://api.github.com/repos/{OWNER}/{REPO}/commits?per_page=1")
    link = resp.headers.get("Link", "")
    m = re.search(r'[?&]page=(\d+)>; rel="last"', link)
    return int(m.group(1)) if m else None


def main():
    old = {}
    if os.path.exists(STATS):
        old = json.load(open(STATS))
    new = dict(old)
    for key, fn in (("tests", fetch_tests), ("adrs", fetch_adrs), ("commits", fetch_commits)):
        try:
            val = fn()
            if sane(val):
                new[key] = val
            else:
                print(f"warn: {key} returned an unusable value ({val!r}); keeping {old.get(key)}", file=sys.stderr)
        except Exception as exc:  # noqa: BLE001 - never fail the build on a network error
            print(f"warn: could not fetch {key} ({exc}); keeping {old.get(key)}", file=sys.stderr)
    os.makedirs(os.path.dirname(STATS), exist_ok=True)
    with open(STATS, "w") as f:
        json.dump(new, f, indent=2)
        f.write("\n")
    if "adrs" in new:
        with open(ADRS_BADGE, "w") as f:
            f.write('{"schemaVersion":1,"label":"ADRs","message":"%d","color":"blueviolet"}\n' % new["adrs"])
    print("stats:", new)


if __name__ == "__main__":
    main()
