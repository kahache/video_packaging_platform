#!/usr/bin/env python3
"""
End-to-end test of the REAL video pipeline (app/video_ops.py).

It drives the production `Video_ops` code through the same four stages the
application uses, in order:

    ingest  ->  fragment  ->  encrypt  ->  dash

`video_ops.py` is intentionally database-free ("It's a dumb module, it doesn't
work with databases"), so this test needs NO MySQL and NO Docker: just the
Bento4 binaries in ../bin and a sample .mp4 file.

Usage:
    python3 pipeline_e2e.py [path/to/video.mp4]

Video resolution order:
    1. argv[1]
    2. $E2E_VIDEO
    3. first *.mp4 found in tests/TEST_VIDEOS/

Exit codes:
    0  pipeline completed and all output files exist
    1  a stage failed / an output file is missing
    2  no sample video available (skipped) -> see get_sample_video.sh
"""
import os
import sys
import glob
import time
import shutil

# --- locate the project layout and import the real Video_ops -----------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
APP = os.path.join(REPO, "app")

# video_ops computes bin_dir/storage_dir/output_dir from the CWD at import time,
# exactly as it does when launched from app/. So we chdir into app/ first.
os.chdir(APP)
sys.path.insert(0, APP)

# These dirs are created by the Dockerfile; create them locally too.
os.makedirs(os.path.join(REPO, "storage"), exist_ok=True)
os.makedirs(os.path.join(REPO, "output"), exist_ok=True)

from video_ops import Video_ops, storage_dir  # noqa: E402

# Same test key/kid used by the repo's unit tests (22-char base64, no padding).
KEY = os.environ.get("E2E_KEY", "hyN9IKGfWKdAwFaE5pm0qg")
KID = os.environ.get("E2E_KID", "oW5AK5BW43HzbTSKpiu3SQ")


def resolve_video():
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return os.path.abspath(sys.argv[1])
    if os.environ.get("E2E_VIDEO"):
        return os.path.abspath(os.environ["E2E_VIDEO"])
    candidates = sorted(glob.glob(os.path.join(REPO, "tests", "TEST_VIDEOS", "*.mp4")))
    return candidates[0] if candidates else None


def ok(result):
    """video_ops methods put a 1 as the last tuple element on success."""
    return isinstance(result, tuple) and result and result[-1] == 1


def stage(name, fn):
    print("\n--- %s ---" % name, flush=True)
    t0 = time.time()
    result = fn()
    dt = time.time() - t0
    if not ok(result):
        print("FAIL  %s (%.1fs) -> %r" % (name, dt, result))
        sys.exit(1)
    print("PASS  %s (%.1fs)" % (name, dt))
    return result


def must_exist(label, path):
    if not (path and os.path.isfile(path)):
        print("FAIL  expected %s not found: %r" % (label, path))
        sys.exit(1)
    size = os.path.getsize(path)
    print("      %s -> %s (%d bytes)" % (label, path, size))
    if size == 0:
        print("FAIL  %s is empty" % label)
        sys.exit(1)


def main():
    video = resolve_video()
    if not video or not os.path.isfile(video):
        print("SKIP - no sample video found.")
        print("       Run: bash tests/e2e/get_sample_video.sh")
        print("       or:  python3 pipeline_e2e.py /path/to/video.mp4")
        sys.exit(2)

    print("=" * 64)
    print("E2E VIDEO PIPELINE TEST")
    print("  sample : %s (%d bytes)" % (video, os.path.getsize(video)))
    print("  key/kid: %s / %s" % (KEY, KID))
    print("=" * 64)

    # Mimic the app: the uploaded file is first saved next to app.py, then
    # ingest moves it into storage/. Copy so the sample survives re-runs.
    basename = os.path.basename(video)
    ingest_src = os.path.join(APP, basename)
    shutil.copy(video, ingest_src)

    # 1) INGEST: detects the video track id and moves the file to storage/.
    ingest = stage("ingest", lambda: Video_ops.video_ingest(ingest_src))
    video_track_number = ingest[1]
    print("      detected video_track_number = %s" % video_track_number)
    stored = os.path.join(storage_dir, basename)
    must_exist("stored input", stored)

    # 2) FRAGMENT: produces output/<CODE>/<CODE>.mp4
    fragment = stage("fragment", lambda: Video_ops.video_fragment(stored))
    fragmented = fragment[1]
    must_exist("fragmented mp4", fragmented)

    # 3) ENCRYPT: produces <fragmented>_enc.mp4
    encrypt = stage("encrypt",
                    lambda: Video_ops.video_encrypt(video_track_number, KEY, KID, fragmented))
    encrypted = encrypt[1]
    must_exist("encrypted mp4", encrypted)

    # 4) DASH: produces <dir>/dash/stream.mpd  (+ a playback URL)
    dash = stage("dash", lambda: Video_ops.video_dash(encrypted))
    mpd, url = dash[1], dash[2]
    must_exist("MPEG-DASH manifest", mpd)
    print("      playback url = %s" % url)

    print("\n" + "=" * 64)
    print("RESULT: ALL STAGES PASSED  (ingest -> fragment -> encrypt -> dash)")
    print("=" * 64)
    sys.exit(0)


if __name__ == "__main__":
    main()
