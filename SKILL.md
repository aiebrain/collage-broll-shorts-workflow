---
name: collage-broll-shorts
description: "Standardize a cross-platform, versioned workflow for turning a source video, transcript, goal, and channel tone into a vertical collage B-roll YouTube Short with approved metaphor stills, replaceable voice and rendering adapters, rights checks, and machine QA. Use when planning, generating, revising, or preparing a collage B-roll Short for external distribution without automatic upload or publication."
---

# Collage B-roll Shorts

## Objective

Create a repeatable 9:16 Short from the source's real screen activity and spoken words. Preserve the source evidence, isolate one core message, build a hook → process → conclusion timeline, and make every visual, audio, version, and publication decision auditable.

Keep this skill provider-neutral. Put brand tone, creative choices, renderer, voice provider, image provider, and caption method in project configuration and approval records rather than in this skill.

## Non-negotiable boundaries

- Treat existing source files and prior outputs (`v1`, `v2`, `v3`, and later) as read-only. Never overwrite, rename, delete, or render over them.
- Create a new slug and version directory for every output. Stop on a name collision.
- Do not upload, publish, schedule, connect an account, or send a file to an external service unless the user explicitly approves that exact action after QA.
- Allow only local-generated BGM or assets with clear permission for the intended public use. Record source, license or permission, and verification date without recording tokens, account data, or private voice identifiers.
- Use a personal/user voice only when the user has explicitly granted permission for this project and an authenticated user session is already available. Do not create an account, store credentials, register a voice, or infer consent from a prior task.
- Keep provider names, brand claims, creative hypotheses, and unverified facts in configuration or review notes. Mark unknowns as pending approval.

## Project contract

Set a project root through `COLLAGE_BROLL_ROOT` or `--root`. Use this layout for new work; do not retrofit an existing production folder by moving or replacing files.

```text
<root>/
├─ config/project.json                 # declared specs, adapters, tone, approval state
├─ input/
│  ├─ source/                          # original video and screen captures
│  ├─ transcript/                      # transcript, SRT, or VTT
│  ├─ brief/                           # goal and channel-tone notes
│  └─ references/                      # optional, rights-cleared references
├─ work/<slug>/
│  ├─ analysis/                        # source evidence and timeline
│  ├─ metaphors/                       # proposal cards and approval records
│  ├─ stills/                          # generated stills and visual review
│  ├─ broll/                           # assembled short B-roll clips
│  ├─ audio/                           # voice and local/permitted BGM
│  └─ captions/                        # SRT/VTT or caption source
└─ output/<slug>/
   ├─ v1/                              # immutable deliverable package
   ├─ v2/                              # later approved revision
   └─ ...
```

Use relative paths inside manifests. Hash source and predecessor files when they are in a mixed workspace. Keep secrets and session data out of `config`, manifests, QA reports, and notes.

Declare at least these `config/project.json` values before rendering:

```json
{
  "schema": "collage-broll-shorts/1",
  "slug": "short-slug",
  "renderer": "ffmpeg",
  "width": 1080,
  "height": 1920,
  "fps": 30,
  "max_duration_seconds": 60,
  "voice_mode": "default_tts",
  "caption_mode": "burned_in",
  "publish_approval": false
}
```

Keep `renderer`, `voice_mode`, and `caption_mode` replaceable. A `user_voice` mode requires a separate consent record with only a boolean status and non-identifying provider label.

## Cross-platform preflight

Run the bundled read-only preflight before inspecting or rendering. It detects Windows versus macOS, checks Python, `ffmpeg`, `ffprobe`, and the selected Node/Remotion path, and validates the declared folder layout. It uses only the standard Python library.

PowerShell:

```powershell
$env:COLLAGE_BROLL_ROOT = 'C:\path\to\collage-work'
python '<skill-dir>\scripts\preflight.py' --root $env:COLLAGE_BROLL_ROOT --renderer ffmpeg --require-layout --json
```

macOS Terminal (zsh/bash):

```sh
export COLLAGE_BROLL_ROOT="$PWD/collage-work"
python3 "<skill-dir>/scripts/preflight.py" --root "$COLLAGE_BROLL_ROOT" --renderer ffmpeg --require-layout --json
```

Use `--renderer remotion` when the project selects Remotion. Override tool locations without editing the skill:

```text
COLLAGE_BROLL_ROOT   project root
COLLAGE_BROLL_INPUT  input directory override
COLLAGE_BROLL_OUTPUT output directory override
FFMPEG_BIN           ffmpeg executable or absolute path
FFPROBE_BIN          ffprobe executable or absolute path
NODE_BIN             node executable or absolute path
REMOTION_BIN         remotion executable or local .bin path
```

Prefer a project-local Remotion binary. On Windows invoke `node_modules\.bin\remotion.cmd`; on macOS invoke `node_modules/.bin/remotion`. Prefer `python` on Windows and `python3` on macOS, but honor an explicit interpreter path. Do not install dependencies or change global configuration as part of this skill.

## Workflow and approval gates

Complete each gate before the next one and record the result in the project package.

| Gate | Required action | Pass evidence |
|---|---|---|
| 0. Scope | Capture source, transcript, goal, tone, output slug, declared specs, and the no-publish boundary. | `manifest.json` with `publish_approval: false` |
| 1. Narrative | Inspect the actual source screen and spoken delivery. Select one core message and map hook → process → conclusion with time ranges. | `work/<slug>/analysis/timeline.json` |
| 2. Metaphor | Propose a small set of B-roll metaphors and obtain user approval for the chosen concept. | Approved metaphor card |
| 3. Still | Generate or obtain text-free, logo-free, UI-free stills. Visually inspect every still before motion. | Still review with pass/reject per asset |
| 4. B-roll | Assemble approved stills into short clips with declared duration and motion. | Clip paths, hashes, and source ledger |
| 5. Audio/captions | Select default TTS, permitted user voice, or silence; prepare captions and permitted/local BGM. | Voice consent status, caption source, rights ledger |
| 6. Compose | Combine source video, B-roll, captions, voice, and BGM into a new version directory. | New `output/<slug>/vN/final.mp4` |
| 7. Final QA | Run technical, decode, sync, loudness, rights, and sample-frame checks. | `qa-report.json` with pass/fail and evidence |
| 8. Publish | Treat upload or publication as a separate user-approved handoff. | Exact approval; otherwise remain unpublished |

### Analyze the source

Read the transcript for wording, but also watch the real screen and listen to pacing, pauses, emphasis, and transitions. Do not invent product facts or claim that a visual result was shown if it was not shown.

Write a compact timeline with:

```json
{
  "core_message": "one sentence",
  "hook": {"start": 0.0, "end": 3.0, "claim": "observable opening promise"},
  "process": [
    {"start": 3.0, "end": 22.0, "purpose": "step or proof", "screen_evidence": "..."}
  ],
  "conclusion": {"start": 22.0, "end": 30.0, "claim": "observable outcome"},
  "open_questions": []
}
```

Keep the hook concrete, make the process legible, and let the conclusion resolve the opening promise. Ask for approval when the core message or timeline changes the meaning of the source.

### Gate the collage B-roll

Use the sequence `metaphor approval → still inspection → short-video assembly`.

For each metaphor card, state what it represents, why it matches the source, and what could be misread. After approval, require each still to pass all of these checks:

- no readable text, logo, brand mark, watermark, or recognizable UI;
- no accidental product/identity substitution;
- composition works in the declared 9:16 crop and leaves room for captions;
- asset source and public-use permission are recorded.

Reject and regenerate a still that fails any check. Assemble motion only from passed stills. Do not silently replace an approved metaphor with a different concept.

### Choose audio and captions

Support three voice modes:

1. `default_tts`: use a configured local or external adapter and record only provider label, voice mode, duration, and file hash.
2. `user_voice`: require explicit project permission and a logged-in user session. Do not save session cookies, tokens, voice IDs, personal names, or provider account data. If either condition is missing, stop or ask for an approved fallback.
3. `silent`: render captions and BGM only when that is the approved creative choice.

Use captions from the approved transcript/timeline. When captions are burned into the video, sample the rendered frames for readable size, contrast, safe margins, and correct timing. When captions are sidecar files, keep the file beside the matching version and validate its encoding.

Allow BGM only when it is generated locally or its license explicitly permits the intended public use. Record `asset_id`, kind, source class, license/permission, checked date, and allowed-for-public-use status in `rights.json`; never record credentials.

## Replaceable adapter contract

Keep adapters behind these inputs and outputs so providers can be changed without changing the narrative or approval gates:

| Adapter | Input | Required output |
|---|---|---|
| Analysis | source video, transcript, goal, tone | timeline JSON plus evidence paths and open questions |
| Still generator | approved metaphor card, aspect ratio, caption-safe area | still files plus hashes and rights metadata |
| B-roll assembler | passed stills, duration/motion config | short clips plus hashes and source map |
| Voice | approved script, `voice_mode` | audio file, duration, mode, consent status; no identity data |
| Caption | approved transcript and timeline | SRT/VTT or burned-in caption layer with encoding status |
| Composer | source, clips, voice, captions, BGM, project config | new version package; never overwrite |
| QA | final media, version manifest, rights ledger | machine-readable QA report and visual sample list |

Treat a provider failure as an adapter failure. Preserve approved inputs, report the failure, and switch providers only through configuration and a new version; do not bypass a gate.

## Compose and render

Use the declared `width`, `height`, `fps`, and `max_duration_seconds`. Default to 1080×1920, 30 fps, and a 60-second target, but keep them configurable and recheck the platform's current limit only when publication is explicitly requested.

Preserve the source's meaning while fitting 9:16. Choose crop, pad, or reframing explicitly. Keep captions inside safe margins. Mix narration and BGM with a declared target, duck BGM under speech, and measure the result; do not call a level acceptable merely because it sounds acceptable in one preview.

Use an atomic output rule:

1. Reserve `output/<slug>/vN/` only if it does not exist.
2. Render to a new temporary file inside that version directory.
3. Verify the temporary file, then rename it to `final.mp4` once.
4. Write `manifest.json`, `rights.json`, `qa-report.json`, and `samples/` in the same version directory.
5. If any check fails, retain the failed version for diagnosis or mark it rejected; never overwrite a prior version.

## Machine QA contract

Write `qa-report.json` using this minimum shape:

```json
{
  "schema": "collage-broll-shorts/qa-1",
  "version": "v1",
  "pass": false,
  "media": {
    "path": "final.mp4",
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration_seconds": 0,
    "video_codec": "",
    "audio_codec": "",
    "decode": {"video": "pending", "audio": "pending"}
  },
  "sync": {"caption_voice": "pending", "evidence": []},
  "audio": {"bgm_rights": "pending", "measured_level": {}, "pass": false},
  "visual_samples": [],
  "predecessors": [],
  "publication": {"uploaded": false, "published": false, "approval": null}
}
```

Run `ffprobe` and retain its JSON evidence. Then run a full decode check with `ffmpeg -v error -i <final> -f null -`. On PowerShell, quote the path and invoke an explicit executable with `&`; on POSIX shells, quote the path normally. Check the declared dimensions, frame rate, duration, codecs, pixel format, sample rate, channel count, and absence of decode errors. Allow no audio only when `voice_mode: silent` and record that exception.

Check voice/caption sync by proving that each voice clip fits its timeline slot and that the caption intervals match the retimed video. Measure BGM and final mix levels with `volumedetect` or `ebur128`; record the measured values and the configured acceptance target. Do not invent a measurement.

Extract four to six sample frames covering the opening screen, a collage, a middle transition, and the conclusion. Inspect vertical framing, text/logo/UI absence in B-roll, caption readability, and any accidental crop or flash. Put sample paths in `visual_samples`.

Before declaring a revision complete, compare predecessor hashes and report `unchanged: true` for every preserved version. A final pass requires technical checks, decode checks, sync checks, rights checks, and sample-frame QA; otherwise set `pass: false` and state the blocking item.

## Versioning and feedback

Use `v1` for the first complete candidate and increment monotonically for every later candidate. Store each candidate as:

```text
output/<slug>/vN/
├─ final.mp4
├─ manifest.json
├─ rights.json
├─ qa-report.json
└─ samples/
```

For feedback that says “make it faster,” “lower the BGM,” or “change the voice,” adjust only the declared tempo, BGM, or voice axis and create the next version. Preserve the prior version and record the changed fields. If the feedback changes the message, metaphor, source, or captions, treat it as a new approval decision rather than a minor mix revision.

## Publication handoff

Stop after local QA by default. A publication request must name the exact platform, destination/account, asset, and submission action. Obtain final approval after the QA report is complete, then hand off to a separate publishing workflow. Do not log in, connect accounts, upload, schedule, or publish while preparing or validating this skill.

## Bundled resource

Run `scripts/preflight.py` for dependency and layout checks. It is intentionally read-only and has no third-party Python dependency. Keep any future renderer or provider implementation behind the adapter contract above; add a resource only when it is deterministic, cross-platform, and necessary.
