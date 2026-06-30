#!/usr/bin/env python3
"""
End-to-end test of the running REST API (the full Docker stack).

Drives the real HTTP endpoints exposed by app/app.py against a live server:

    POST /success            (multipart upload)  -> ingest + DB insert
    POST /packaged_content   (JSON)              -> fragment + encrypt + dash + DB
    GET  /packaged_content_id/<id>               -> final status + manifest URL

Prerequisites:
    docker compose up --build      (app on :5000, MySQL ready via healthcheck)

Usage:
    python3 http_e2e.py [path/to/video.mp4]

Env:
    E2E_BASE_URL   default http://localhost:5000
    E2E_KEY/E2E_KID  encryption key/kid (defaults match the repo's unit tests)
    E2E_VIDEO      sample path (alternative to argv[1])

Exit codes:
    0  full HTTP flow succeeded
    1  a step failed
    2  no sample video available (skipped)
"""
import os
import re
import sys
import glob
import json

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

BASE = os.environ.get("E2E_BASE_URL", "http://localhost:5000").rstrip("/")
KEY = os.environ.get("E2E_KEY", "hyN9IKGfWKdAwFaE5pm0qg")
KID = os.environ.get("E2E_KID", "oW5AK5BW43HzbTSKpiu3SQ")

# Packaging (fragment+encrypt+dash) runs synchronously inside the request.
PACKAGE_TIMEOUT = int(os.environ.get("E2E_PACKAGE_TIMEOUT", "900"))


def resolve_video():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return os.path.abspath(sys.argv[1])
    if os.environ.get("E2E_VIDEO"):
        return os.path.abspath(os.environ["E2E_VIDEO"])
    candidates = sorted(glob.glob(os.path.join(REPO, "tests", "TEST_VIDEOS", "*.mp4")))
    return candidates[0] if candidates else None


def fail(msg):
    print("FAIL  " + msg)
    sys.exit(1)


def main():
    video = resolve_video()
    if not video or not os.path.isfile(video):
        print("SKIP - no sample video found. Run get_sample_video.sh first.")
        sys.exit(2)

    print("=" * 64)
    print("E2E HTTP TEST against %s" % BASE)
    print("  sample : %s" % video)
    print("=" * 64)

    # 0) Server reachable?
    try:
        r = requests.get(BASE + "/", allow_redirects=False, timeout=15)
    except requests.RequestException as e:
        fail("server not reachable at %s (%s). Is 'docker compose up' running?" % (BASE, e))
    print("PASS  GET / -> %s" % r.status_code)

    # 1) Upload -> /success  (returns success.html containing input_content_id)
    print("\n--- POST /success (upload) ---", flush=True)
    with open(video, "rb") as fh:
        r = requests.post(BASE + "/success",
                          files={"file": (os.path.basename(video), fh, "video/mp4")},
                          timeout=PACKAGE_TIMEOUT)
    if r.status_code != 200:
        fail("/success returned %s: %s" % (r.status_code, r.text[:200]))
    m = re.search(r"input_content_id:\s*(\d+)", r.text)
    if not m:
        fail("could not parse input_content_id from /success response:\n" + r.text[:300])
    input_content_id = int(m.group(1))
    print("PASS  uploaded, input_content_id = %s" % input_content_id)

    # 2) Package -> /packaged_content  (JSON in, JSON out)
    print("\n--- POST /packaged_content (fragment+encrypt+dash) ---", flush=True)
    payload = {"input_content_id": input_content_id, "key": KEY, "kid": KID}
    r = requests.post(BASE + "/packaged_content", json=payload, timeout=PACKAGE_TIMEOUT)
    if r.status_code != 200:
        fail("/packaged_content returned %s: %s" % (r.status_code, r.text[:300]))
    try:
        data = r.json()
    except json.JSONDecodeError:
        fail("/packaged_content did not return JSON:\n" + r.text[:300])
    pcid = (data.get("packaged_content_id") or [None])[0]
    url = (data.get("url") or [None])[0]
    if pcid is None or not url:
        fail("unexpected /packaged_content body: %r" % data)
    print("PASS  packaged, packaged_content_id = %s" % pcid)
    print("      url = %s" % url)

    # 3) Status -> /packaged_content_id/<id>  (should be Ready with a manifest)
    print("\n--- GET /packaged_content_id/%s ---" % pcid, flush=True)
    r = requests.get("%s/packaged_content_id/%s" % (BASE, pcid), timeout=60)
    if r.status_code != 200:
        fail("status endpoint returned %s: %s" % (r.status_code, r.text[:200]))
    try:
        status = r.json()
    except json.JSONDecodeError:
        fail("status not Ready yet (no JSON returned): %s" % r.text[:200])
    if "url" not in status:
        fail("status JSON missing url: %r" % status)
    print("PASS  status Ready -> %r" % status)

    print("\n" + "=" * 64)
    print("RESULT: FULL HTTP E2E PASSED")
    print("=" * 64)
    sys.exit(0)


if __name__ == "__main__":
    main()
