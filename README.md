# Collage B-roll Shorts Workflow

`collage-broll-shorts` is a cross-platform Codex skill for turning a source video, transcript, goal, and channel tone into a versioned vertical collage B-roll YouTube Short.

It standardizes source analysis, metaphor approval, text-free B-roll still review, voice and caption adapters, local/permitted BGM, rendering checks, versioning, and machine QA. It does not upload or publish videos automatically.

> Public draft: review the workflow and choose your own providers, brand rules, creative settings, and license before production use.

## What it provides

- Windows and macOS setup guidance.
- Read-only preflight checks for Python, `ffmpeg`, `ffprobe`, Node, Remotion, and the project layout.
- A hook → process → conclusion narrative workflow grounded in the source's real screen activity and spoken delivery.
- Three B-roll approval gates: metaphor approval → still inspection → short-video assembly.
- Replaceable adapters for analysis, still generation, B-roll assembly, voice, captions, composition, and QA.
- Immutable `v1`, `v2`, `v3` output packages with manifests, rights ledgers, QA reports, and sample frames.
- Explicit boundaries for voice consent, asset permissions, credentials, account connections, uploads, and publication.

## Requirements

Required for the bundled preflight:

- Python 3.10 or newer
- `ffmpeg` and `ffprobe`

Required only when selected by the project renderer:

- Node.js
- A project-local Remotion CLI

The preflight script uses only the Python standard library. It does not install packages, change global settings, connect accounts, or write project files.

## Quick start

Clone or download this repository, then run the preflight against a separate project root.

### Windows PowerShell

```powershell
$env:COLLAGE_BROLL_ROOT = 'C:\path\to\collage-work'
python .\scripts\preflight.py --root $env:COLLAGE_BROLL_ROOT --renderer ffmpeg --require-layout --json
```

### macOS Terminal

```sh
export COLLAGE_BROLL_ROOT="$PWD/collage-work"
python3 ./scripts/preflight.py --root "$COLLAGE_BROLL_ROOT" --renderer ffmpeg --require-layout --json
```

Use `--renderer remotion` when the project selects Remotion. Override executable locations with `FFMPEG_BIN`, `FFPROBE_BIN`, `NODE_BIN`, or `REMOTION_BIN` instead of editing the skill.

## Project layout

Create a new project root for each production effort:

```text
<root>/
├─ config/project.json
├─ input/
│  ├─ source/
│  ├─ transcript/
│  ├─ brief/
│  └─ references/
├─ work/<slug>/
│  ├─ analysis/
│  ├─ metaphors/
│  ├─ stills/
│  ├─ broll/
│  ├─ audio/
│  └─ captions/
└─ output/<slug>/
   ├─ v1/
   ├─ v2/
   └─ ...
```

Declare the target format and selected adapters in `config/project.json`. A minimal configuration looks like this:

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

## Workflow

1. Lock the source, transcript, goal, tone, target specs, slug, and no-publish boundary.
2. Watch the real source screen and listen to delivery; use the transcript as evidence, not as a substitute for the recording.
3. Select one core message and map the hook, process/proof, and conclusion with time ranges.
4. Propose metaphors and obtain approval before generating B-roll.
5. Inspect every still for readable text, logos, watermarks, UI, identity substitution, crop safety, and usage permission.
6. Assemble motion only from approved stills.
7. Select default TTS, an explicitly permitted user voice, or silence; prepare captions and local/permitted BGM.
8. Render a new version and run technical, decode, sync, loudness, rights, and visual sample QA.

Keep each gate's evidence with the matching project slug. If feedback changes tempo, BGM, or voice, create the next version rather than overwriting the previous one.

## Adapter boundaries

The workflow does not require a particular image model, TTS service, video renderer, brand, or provider. Keep integrations behind these contracts:

| Adapter | Input | Output |
| --- | --- | --- |
| Analysis | source video, transcript, goal, tone | timeline JSON, evidence paths, open questions |
| Still generator | approved metaphor, aspect ratio, caption-safe area | reviewed stills, hashes, rights metadata |
| B-roll assembler | approved stills, motion and duration settings | short clips, hashes, source map |
| Voice | approved script, voice mode | audio, duration, mode, consent status; no identity data |
| Caption | approved transcript and timeline | SRT/VTT or caption layer with encoding status |
| Composer | source, clips, audio, captions, BGM, config | new version package |
| QA | final media, manifest, rights ledger | machine-readable report and sample-frame list |

## Output and QA contract

Each version should contain:

```text
output/<slug>/vN/
├─ final.mp4
├─ manifest.json
├─ rights.json
├─ qa-report.json
└─ samples/
```

Use `ffprobe` JSON for dimensions, frame rate, duration, codecs, sample rate, and channels. Run a full decode check with:

```sh
ffmpeg -v error -i "<final-video>" -f null -
```

Record caption/voice slot evidence, measured BGM and final-mix levels, asset permissions, predecessor hashes, and four to six visual sample frames. Treat a failed or unmeasured check as `pass: false`.

## Safety and rights

- Keep prior versions read-only and stop on output name collisions.
- Use only local-generated BGM or assets whose permission covers the intended public use.
- Require explicit project permission and an already authenticated user session for a personal voice. Never store cookies, tokens, voice IDs, or personal identifiers.
- Keep secrets, account data, private paths, and internal project names out of manifests, reports, and public commits.
- Keep `publish_approval: false` until a separate approval names the exact platform, account, asset, and submission action.
- Public repository visibility does not grant a license to reuse this skill. Choose and add a license before distributing it under specific reuse terms.

## Skill name and repository name

The Codex skill name remains `collage-broll-shorts` for trigger compatibility. The public repository is named `collage-broll-shorts-workflow`.

## License

No license has been declared yet. Treat this repository as a public draft and obtain the owner's permission before reusing or redistributing it.
