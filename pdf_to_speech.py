#!/usr/bin/env python3
"""
pdf_to_speech.py  –  Turn any PDF into an audiobook.

Usage examples
==============
# Google Cloud TTS  (needs GOOGLE_APPLICATION_CREDENTIALS env var pointing to a JSON key)
python pdf_to_speech.py my-book.pdf my-book.mp3 --voice en-US-Studio-O --rate 1.05

# Free fallback (gTTS, requires only an Internet connection):
python pdf_to_speech.py my-article.pdf article.mp3 --provider gtts
"""
import argparse
import io
import os
import re
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

# ---------- PDF -> raw text ---------------------------------------------------
def extract_text(pdf_path: Path) -> str:
    """Return UTF-8 string containing the PDF’s text in reading order."""
    from pdfminer.high_level import extract_text  # pdfminer.six
    raw = extract_text(pdf_path)
    # Collapse hyphenated line breaks & excessive whitespace
    cleaned = re.sub(r"-\n(\w)", r"\1", raw)       # join “hy-\nphen” words
    cleaned = re.sub(r"\s+\n", "\n", cleaned)      # trim spaces before \n
    cleaned = re.sub(r"\n{2,}", "\n\n", cleaned)   # keep blank lines once
    return cleaned.strip()

# ---------- Text -> speech (provider-agnostic layer) --------------------------
MAX_CHARS = 4_900  # leave headroom under Google’s 5 kB limit

def synthesize_google(text: str, voice: str, speaking_rate: float) -> bytes:
    """Return MP3 bytes produced by Google Cloud TTS."""
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=voice.split("-")[0] + "-" + voice.split("-")[1],
        name=voice,
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=speaking_rate,
    )
    response = client.synthesize_speech(
        input=input_text, voice=voice_params, audio_config=audio_config
    )
    return response.audio_content

def synthesize_gtts(text: str, lang: str = "en", speaking_rate: float = 1.0) -> bytes:
    """Return MP3 bytes via the public gTTS API."""
    from gtts import gTTS
    from pydub import AudioSegment
    spoken = gTTS(text=text, lang=lang, tld="com", slow=False)
    with NamedTemporaryFile(delete=False) as tmp:
        spoken.write_to_fp(tmp)
        tmp_path = tmp.name
    audio = AudioSegment.from_mp3(tmp_path)
    Path(tmp_path).unlink(missing_ok=True)
    if speaking_rate != 1.0:
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speaking_rate)
        }).set_frame_rate(audio.frame_rate)
    with io.BytesIO() as fp:
        audio.export(fp, format="mp3")
        return fp.getvalue()

def text_to_mp3(full_text: str, out_path: Path,
                provider: str, voice: str, rate: float):
    """Convert arbitrarily long text to a single MP3 file."""
    chunks = [full_text[i:i+MAX_CHARS] for i in range(0, len(full_text), MAX_CHARS)]
    print(f"⏳  Splitting into {len(chunks)} chunk(s)…")
    audio_bytes = bytearray()

    for idx, chunk in enumerate(chunks, 1):
        if provider == "google":
            audio_chunk = synthesize_google(chunk, voice, rate)
        elif provider == "gtts":
            audio_chunk = synthesize_gtts(chunk, lang=voice.split("-")[0], speaking_rate=rate)
        else:
            raise ValueError("Unsupported provider")
        audio_bytes.extend(audio_chunk)
        print(f"   ✔ Chunk {idx}/{len(chunks)} synthesized")

    out_path.write_bytes(audio_bytes)
    print(f"✅  Saved audiobook ➜ {out_path}")

# ---------- CLI glue ----------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a PDF into an MP3 using a cloud TTS engine.")
    parser.add_argument("pdf", type=Path, help="Input PDF file")
    parser.add_argument("mp3", type=Path, help="Output MP3 file")
    parser.add_argument("--provider", default="google",
                        choices=["google", "gtts"],
                        help="TTS backend (default: google)")
    parser.add_argument("--voice", default="en-US-Studio-M",
                        help="Voice name or language code (gTTS)")
    parser.add_argument("--rate", type=float, default=1.0,
                        help="Speaking rate (1.0 = normal speed)")
    return parser.parse_args()

def main():
    args = parse_args()
    if not args.pdf.exists():
        sys.exit("PDF not found: " + str(args.pdf))
    text = extract_text(args.pdf)
    if not text:
        sys.exit("No extractable text found in the PDF.")
    text_to_mp3(text, args.mp3, args.provider, args.voice, args.rate)

if __name__ == "__main__":
    main()
