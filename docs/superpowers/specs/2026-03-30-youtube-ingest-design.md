# Design: YouTube Niche Ingest — Phase 1

**Date:** 2026-03-30
**Scope:** `tools/ingest_youtube.py` + `tools/channels.json`

## Goal

Pull the last 90 days of uploads from 10 seed AI/automation channels and write them to `.tmp/ingest_YYYYMMDD.jsonl` for downstream metrics and chart tools.

## Files

| File | Purpose |
|------|---------|
| `tools/channels.json` | Seed channel list — `[{id, name}]` |
| `tools/ingest_youtube.py` | Ingestion script |
| `.tmp/ingest_YYYYMMDD.jsonl` | Output — one video per line |

## Seed Channels

| Name | Category |
|------|---------|
| Matt Wolfe | AI news & tools |
| AI Explained | AI news & tools |
| The AI Advantage | AI news & tools |
| Skill Leap AI | AI news & tools |
| Liam Ottley | AI automation |
| Nick Saraev | AI automation |
| David Ondrej | AI automation |
| Corbin Brown | AI automation |
| Andrej Karpathy | Technical/research |
| Yannic Kilcher | Technical/research |

## Script Design

Four functions in `ingest_youtube.py`:

1. **`get_uploads_playlist(channel_id)`** — calls `channels.list` with `contentDetails` part, returns the uploads playlist ID. Cost: 1 unit per channel.

2. **`fetch_video_ids(playlist_id, cutoff_date)`** — paginates `playlistItems.list` (snippet part), collects video IDs while `publishedAt >= cutoff_date`, stops early when the cutoff is crossed. Cost: ~1 unit per page (50 items/page).

3. **`fetch_video_details(video_ids)`** — batches `videos.list` in chunks of 50 (API max), requests `snippet,statistics,contentDetails` parts. Returns per-video: `video_id`, `channel_id`, `published_at`, `title`, `description`, `view_count`, `like_count`, `comment_count`, `duration`. Cost: 1 unit per batch.

4. **`main()`** — loads `channels.json`, computes 90-day cutoff, loops channels, writes results to `.tmp/ingest_YYYYMMDD.jsonl`, prints total video count and estimated quota used.

## Output Schema

Each line of the JSONL file:
```
video_id, channel_id, channel_name, published_at, title, description,
view_count, like_count, comment_count, duration
```

## Error Handling

- On API error for a channel: log the error, skip the channel, continue.
- No retries in v1. If quota is exhausted, the script exits with a clear message.

## Quota Estimate

~30 units for a full 10-channel run (well within the 10k daily limit). Script prints actual estimate at the end of each run.

## Verification

Run passes when:
1. `.tmp/ingest_YYYYMMDD.jsonl` exists with at least one row per channel
2. Spot-check 3 videos against the YouTube UI — view counts and titles match
3. No videos older than 90 days appear in the output
