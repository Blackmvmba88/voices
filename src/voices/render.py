from __future__ import annotations

import html
import json
from pathlib import Path

from .models import ColoredWord, VoiceProfile


def render_html(profile: VoiceProfile, words: list[ColoredWord]) -> str:
    spans = []
    for word in words:
        label = (
            f"{word.note} {word.cents:+.1f} cents"
            if word.note and word.cents is not None
            else "unvoiced"
        )
        title = html.escape(label)
        style = (
            f"color:{word.color};"
            f"opacity:{word.opacity:.3f};"
            f"font-weight:{word.font_weight};"
            f"text-shadow:0 0 {word.glow_px:.1f}px {word.color};"
        )
        spans.append(
            f'<span class="word" style="{style}" title="{title}">'
            f"{html.escape(word.text)}</span>"
        )

    payload = json.dumps(
        {
            "profile": profile.to_dict(),
            "words": [w.to_dict() for w in words],
        },
        ensure_ascii=False,
    )
    transcript = " ".join(spans)
    profile_json = html.escape(json.dumps(profile.to_dict(), indent=2))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>VOICES — Acoustic Transcript</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
body {{ margin:0; background:#090b10; color:#e9edf5; min-height:100vh; }}
main {{ max-width:1100px; margin:auto; padding:48px 28px; }}
h1 {{ letter-spacing:.08em; font-size:14px; opacity:.65; }}
.transcript {{ font-size:clamp(28px,5vw,64px); line-height:1.35; margin:64px 0; }}
.word {{ display:inline-block; margin-right:.23em; transition:all .12s linear; }}
pre {{ white-space:pre-wrap; background:#11151d; padding:18px; border-radius:14px; overflow:auto; }}
</style>
</head>
<body><main>
<h1>BLACKMAMBA / VOICES</h1>
<div class="transcript">{transcript}</div>
<pre>{profile_json}</pre>
<script>window.VOICES_DATA = {payload};</script>
</main></body></html>"""


def write_html(
    path: str | Path,
    profile: VoiceProfile,
    words: list[ColoredWord],
) -> None:
    Path(path).write_text(
        render_html(profile, words),
        encoding="utf-8",
    )
