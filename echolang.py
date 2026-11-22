#!/usr/bin/env python3
"""EchoLang - Turning Text into Speech Across Languages.

Pipeline:  English text -> Hugging Face MarianMT translation -> gTTS speech -> MP3 playback.

Usage examples
--------------
Interactive menu:      python echolang.py
One-shot:              python echolang.py --lang hi --text "Good morning, how are you?"
From a text file:      python echolang.py --lang fr --file sample_input.txt
Save without playing:  python echolang.py --lang de --text "Hello" --no-play --output hallo.mp3
"""
import argparse
import os
import platform
import shutil
import subprocess
import sys

SUPPORTED_LANGS = {
    "hi": "Hindi",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
}

_translators = {}  # cache so each model is loaded only once per run


def load_translator(lang_code):
    """Load (and cache) the Helsinki-NLP opus-mt English -> lang_code model."""
    if lang_code not in SUPPORTED_LANGS:
        raise ValueError(f"Unsupported language code '{lang_code}'. "
                         f"Choose from: {', '.join(SUPPORTED_LANGS)}")
    if lang_code not in _translators:
        from transformers import pipeline  # imported lazily: slow import
        model_name = f"Helsinki-NLP/opus-mt-en-{lang_code}"
        print(f"Loading translation model {model_name} "
              f"(first run downloads it, please wait)...")
        _translators[lang_code] = pipeline("translation",
                                           model=model_name)
    return _translators[lang_code]


def translate(text, lang_code):
    """Translate English `text` into `lang_code`."""
    text = text.strip()
    if not text:
        raise ValueError("Input text is empty.")
    result = load_translator(lang_code)(text, max_length=512)
    return result[0]["translation_text"]


def text_to_speech(text, lang_code, out_path="spoken.mp3"):
    """Convert `text` to an MP3 file with gTTS and return the path."""
    from gtts import gTTS
    gTTS(text=text, lang=lang_code).save(out_path)
    return out_path


def play_audio(path):
    """Play an MP3 using whatever player the OS offers. Returns True on success."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)  # opens default media player
            return True
        if system == "Darwin":
            return subprocess.call(["afplay", path]) == 0
        for player in (["mpg123", "-q"], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"],
                       ["mpv", "--no-video", "--really-quiet"]):
            if shutil.which(player[0]):
                return subprocess.call(player + [path]) == 0
    except Exception as exc:  # pragma: no cover
        print(f"Could not play audio automatically: {exc}")
    print(f"No audio player found - open '{path}' manually "
          f"(Linux: sudo apt install mpg123).")
    return False


def run(text, lang_code, out_path="spoken.mp3", play=True):
    """Full pipeline for one piece of text. Returns the translated string."""
    translated = translate(text, lang_code)
    print(f"\nEnglish : {text.strip()}")
    print(f"{SUPPORTED_LANGS[lang_code]:8}: {translated}")
    try:
        text_to_speech(translated, lang_code, out_path)
        print(f"Audio saved to {out_path}")
        if play:
            play_audio(out_path)
    except Exception as exc:
        print(f"Text-to-speech failed (gTTS needs an internet connection): {exc}")
    return translated


def choose_language():
    print("\nAvailable languages:")
    for code, name in SUPPORTED_LANGS.items():
        print(f"  {code} -> {name}")
    while True:
        code = input("Enter target language code (hi/es/fr/de): ").strip().lower()
        if code in SUPPORTED_LANGS:
            return code
        print("Invalid code, try again.")


def interactive(out_path, play):
    print("=== EchoLang: English text -> translated speech ===")
    lang = choose_language()
    print("Type English text and press Enter. Commands: 'lang' to change language, 'exit' to quit.")
    while True:
        try:
            text = input("\nEnglish> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if text.lower() in ("exit", "quit"):
            break
        if text.lower() == "lang":
            lang = choose_language()
            continue
        if not text:
            continue
        try:
            run(text, lang, out_path, play)
        except Exception as exc:
            print(f"Error: {exc}")
    print("Goodbye!")


def main(argv=None):
    p = argparse.ArgumentParser(description="EchoLang: translate English text and speak it.")
    p.add_argument("--lang", choices=SUPPORTED_LANGS, help="target language code")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--text", help="English text to translate")
    src.add_argument("--file", help="UTF-8 text file; each non-empty line is translated")
    p.add_argument("--output", default="spoken.mp3", help="MP3 output path (default spoken.mp3)")
    p.add_argument("--no-play", action="store_true", help="save audio but do not play it")
    args = p.parse_args(argv)
    play = not args.no_play

    if not args.text and not args.file:
        interactive(args.output, play)
        return 0

    lang = args.lang or choose_language()
    if args.text:
        lines = [args.text]
    else:
        with open(args.file, encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    base, ext = os.path.splitext(args.output)
    for i, line in enumerate(lines, 1):
        out = args.output if len(lines) == 1 else f"{base}_{i}{ext or '.mp3'}"
        run(line, lang, out, play)
    return 0


if __name__ == "__main__":
    sys.exit(main())
