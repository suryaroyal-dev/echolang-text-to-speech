# EchoLang — Turning Text into Speech Across Languages

A Python tool that takes **English text**, translates it into **Hindi, Spanish, French or German**
using Hugging Face MarianMT models (`Helsinki-NLP/opus-mt-en-*`), and **speaks** the result
using Google Text-to-Speech (gTTS). It demonstrates chaining two AI models: machine translation → neural TTS.

## Pipeline
```
English text → MarianMT translation (Transformers) → gTTS → spoken.mp3 → audio playback
```

## Setup
```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
sudo apt install mpg123                              # Linux only (macOS/Windows use built-in players)
```
Internet is required: models are downloaded from Hugging Face on first use (~300 MB per language,
cached afterwards) and gTTS calls Google's service.

## Usage
```bash
python echolang.py                                              # interactive menu
python echolang.py --lang hi --text "Good morning, how are you?"
python echolang.py --lang fr --file sample_input.txt            # one MP3 per line
python echolang.py --lang de --text "Hello" --no-play --output hallo.mp3
```
In interactive mode type `lang` to switch language and `exit` to quit.

## Tests
```bash
python -m unittest discover tests
```
(Offline unit tests with mocked models.)

## Files
| File | Purpose |
|---|---|
| `echolang.py` | Main program (translation, TTS, playback, CLI) |
| `requirements.txt` | Dependencies |
| `sample_input.txt` | Example input lines |
| `tests/test_echolang.py` | Unit tests |

## Notes / limitations
- Hindi output is lower quality than Spanish/French/German (smaller training data for that model).
- Very long text is truncated at 512 tokens per call; split into lines (`--file`) for long passages.
- Add a language: add its code to `SUPPORTED_LANGS` if `Helsinki-NLP/opus-mt-en-<code>` and gTTS both support it.
