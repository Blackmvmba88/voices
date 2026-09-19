from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
import wave
from pathlib import Path

import numpy as np

from .analyzer import AcousticAnalyzer
from .color import ColorEngine, hsl_to_hex
from .models import WordTiming
from .pipeline import colorize_transcript
from .profile import build_voice_profile
from .transcribe import FasterWhisperTranscriber
from .vad import VoiceActivitySegmenter

SAMPLE_RATE = 16000


def _write_pcm16_wav(path: Path, samples: np.ndarray) -> None:
    pcm = np.clip(samples, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())


def create_app(model_size: str = "small", language: str | None = None):
    try:
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError(
            "Install the api extra: pip install 'blackmamba-voices[api]'"
        ) from exc

    app = FastAPI(title="BlackMamba VOICES")
    static_path = Path(__file__).with_name("static") / "index.html"
    transcriber: FasterWhisperTranscriber | None = None

    def get_transcriber() -> FasterWhisperTranscriber:
        nonlocal transcriber
        if transcriber is None:
            transcriber = FasterWhisperTranscriber(model_size=model_size)
        return transcriber

    @app.get("/")
    async def home():
        return HTMLResponse(static_path.read_text(encoding="utf-8"))

    @app.websocket("/ws")
    async def live_voice(websocket: WebSocket):
        await websocket.accept()
        analyzer = AcousticAnalyzer(sample_rate=SAMPLE_RATE)
        vad = VoiceActivitySegmenter(sample_rate=SAMPLE_RATE)
        recent_frames = []
        engine = ColorEngine()
        try:
            while True:
                message = await websocket.receive()
                raw = message.get("bytes")
                if raw is None:
                    continue
                pcm = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
                frames = analyzer.analyze(pcm)
                recent_frames.extend(frames)
                recent_frames = recent_frames[-250:]

                if frames and recent_frames:
                    frame = frames[-1]
                    profile = build_voice_profile(recent_frames)
                    preview = engine.color_word(
                        WordTiming("•", frame.start, frame.end),
                        frame,
                        profile,
                    )
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "meter",
                                "f0_hz": frame.f0_hz,
                                "color": preview.color,
                                "base_color": hsl_to_hex(
                                    profile.base_hue,
                                    profile.base_saturation,
                                    profile.base_lightness,
                                ),
                                "note": preview.note,
                                "cents": preview.cents,
                                "depth": profile.depth,
                                "brightness": profile.brightness,
                            }
                        )
                    )

                utterance = vad.push(pcm)
                if utterance is None:
                    continue

                await websocket.send_text(
                    json.dumps({"type": "state", "value": "transcribing"})
                )
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    wav_path = Path(tmp.name)
                try:
                    _write_pcm16_wav(wav_path, utterance)
                    try:
                        words = await asyncio.to_thread(
                            get_transcriber().transcribe,
                            wav_path,
                            language,
                        )
                    except RuntimeError as exc:
                        await websocket.send_text(
                            json.dumps({"type": "error", "message": str(exc)})
                        )
                        continue
                    if words:
                        profile, colored = colorize_transcript(
                            utterance,
                            words,
                            SAMPLE_RATE,
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "transcript",
                                    "profile": profile.to_dict(),
                                    "words": [word.to_dict() for word in colored],
                                },
                                ensure_ascii=False,
                            )
                        )
                finally:
                    wav_path.unlink(missing_ok=True)
                    await websocket.send_text(
                        json.dumps({"type": "state", "value": "listening"})
                    )
        except WebSocketDisconnect:
            return

    return app


def main() -> None:
    parser = argparse.ArgumentParser(prog="voices-server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model", default="small")
    parser.add_argument("--language", default=None)
    args = parser.parse_args()
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            "Install the api extra: pip install 'blackmamba-voices[api]'"
        ) from exc
    uvicorn.run(
        create_app(args.model, args.language),
        host=args.host,
        port=args.port,
    )
