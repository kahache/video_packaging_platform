# End-to-end tests

Two complementary E2E tests for the video packaging pipeline.

| Test | What it exercises | Needs MySQL/Docker? |
|------|-------------------|---------------------|
| `pipeline_e2e.py` | The real `app/video_ops.py` code: ingest → fragment → encrypt → dash | **No** — `video_ops` is DB-free; only needs the Bento4 binaries in `bin/` |
| `http_e2e.py` | The live REST API: `POST /success` → `POST /packaged_content` → `GET /packaged_content_id/<id>` | **Yes** — run the full stack with `docker compose up` |

## 0. Get a sample video

```bash
bash tests/e2e/get_sample_video.sh
```

Downloads a small (~2 MB) public clip into `tests/TEST_VIDEOS/`. You can also
point either test at your own file via an argument or `$E2E_VIDEO`.

## 1. Pipeline test (no Docker required)

Runs the production media code directly against the binaries. Great for a fast
local sanity check and for CI without a database.

```bash
# deps the binaries' wrapper + app need:
pip install -r app/requirements.txt

cd tests
python3 e2e/pipeline_e2e.py                      # auto-finds a sample in TEST_VIDEOS/
python3 e2e/pipeline_e2e.py /path/to/your.mp4    # or pass one explicitly
```

It asserts each stage returns success **and** that the real output files exist:
the stored input, the fragmented mp4, the `_enc.mp4`, and the
`dash/stream.mpd` manifest. Exit code `0` = pass, `1` = fail, `2` = skipped
(no sample video).

## 2. HTTP test (full stack)

```bash
docker compose up --build          # app on :5000, MySQL gated by healthcheck

# in another shell:
pip install requests
python3 tests/e2e/http_e2e.py      # uses http://localhost:5000 by default
```

Env knobs: `E2E_BASE_URL` (default `http://localhost:5000`),
`E2E_KEY` / `E2E_KID`, `E2E_VIDEO`, `E2E_PACKAGE_TIMEOUT` (default 900s, since
packaging runs synchronously inside the request).

## Notes

- Key/KID default to the same 22-char base64 values used by the repo's unit
  tests; the video track id is **auto-detected** during ingest, so any standard
  H.264 mp4 works.
- `pipeline_e2e.py` copies the sample before ingesting (ingest *moves* the file
  into `storage/`), so re-runs are safe.
