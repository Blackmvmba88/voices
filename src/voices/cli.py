from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audio import read_wav
from .pipeline import colorize_transcript
from .render import write_html
from .transcribe import transcribe_with_faster_whisper


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="voices",
        description="Acoustic voice-to-color transcript engine",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser(
        "transcribe",
        help="transcribe a WAV file and colorize each word",
    )
    analyze.add_argument("wav", type=Path)
    analyze.add_argument("--model", default="small")
    analyze.add_argument("--language", default=None)
    analyze.add_argument("--json", dest="json_path", type=Path, default=None)
    analyze.add_argument(
        "--html",
        dest="html_path",
        type=Path,
        default=Path("voices-output.html"),
    )

    args = parser.parse_args()
    if args.command == "transcribe":
        words = transcribe_with_faster_whisper(
            args.wav,
            args.model,
            args.language,
        )
        samples, sample_rate = read_wav(args.wav)
        profile, colored = colorize_transcript(
            samples,
            words,
            sample_rate,
        )
        payload = {
            "profile": profile.to_dict(),
            "words": [word.to_dict() for word in colored],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        write_html(args.html_path, profile, colored)
        if args.json_path:
            args.json_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
