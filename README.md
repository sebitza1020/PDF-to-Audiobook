# 📚🗣️ PDF‑to‑Speech

Turn any **PDF** into a lifelike **audiobook** with a single command‑line call. This repository ships a Python script that:

* extracts text from a PDF (with layout cleanup)
* streams the text to a neural Text‑to‑Speech engine (Google Cloud TTS by default, gTTS fallback)
* concatenates all audio chunks into a single MP3 … ready for your commute or screen‑free study session!

![demo gif](docs/demo.gif)

---

## ✨ Features

| Feature                     | Details                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 📄 **PDF‑Aware Extraction** | Uses `pdfminer.six` to preserve page order & cleans hyphenated line‑breaks                                   |
| 🔊 **Neural Voices**        | Out‑of‑the‑box Google Cloud TTS (Studio voices); swap in AWS Polly, Azure, or any provider with minimal code |
| 🗣 **Free Fallback**        | `gTTS` mode for quick, cost‑free trials; quality < premium but good enough for drafts                        |
| 🪄 **Chunking Logic**       | Automatically splits large texts under each provider’s character limit                                       |
| 🎚 **Voice Tweaks**         | Command‑line flags for voice name, speaking rate, and TTS provider                                           |
| 🪧 **Fully Offline Option** | Switch to `pyttsx3` for local voices—no Internet required                                                    |

---

## 📦 Installation

```bash
# 1. Clone & open the repo
$ git clone https://github.com/<your‑username>/pdf-to-speech.git
$ cd pdf-to-speech

# 2. (Recommended) Create a virtual environment
$ python -m venv .venv && source .venv/bin/activate

# 3. Install core dependencies
$ pip install -r requirements.txt

# 4. If you plan to use gTTS, make sure FFmpeg is installed
$ sudo apt install ffmpeg   # macOS: brew install ffmpeg
```

### Google Cloud Setup

1. Enable the **Text‑to‑Speech API** in the Google Cloud Console.
2. Create a **service‑account key** and download the JSON file.
3. Export the path so the SDK can find it:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/key.json
   ```
4. (Optional) Check available voices:

   ```bash
   gcloud ml speech voices list | grep "Studio"
   ```

---

## 🚀 Quick Start

```bash
# Convert "my-book.pdf" to an MP3 in Studio voice (≈5 % faster reading)
python pdf_to_speech.py my-book.pdf my-book.mp3 \
       --voice en-US-Studio-O --rate 1.05

# Zero‑setup demo using free gTTS (English, default speed)
python pdf_to_speech.py article.pdf article.mp3 --provider gtts
```

> **Tip**  Run `python pdf_to_speech.py -h` to see all CLI options.

---

## 🏗 Architecture

```
PDF ──▶ pdfminer.six ───┐
                      │  « cleaned text »
                      ▼
                chunker (≤ provider limit)
                      ▼
         +-----------------------------+
         |  TTS provider abstraction   |
         |  (Google TTS / gTTS / …)    |
         +-----------------------------+
                      ▼   « MP3 bytes »
             in‑memory concatenation
                      ▼
                    MP3 file
```

---

## 🔧 Extending / Custom Providers

* **AWS Polly** – swap `synthesize_google()` with:

  ```python
  import boto3
  polly = boto3.client("polly")
  polly.synthesize_speech(Text=text, VoiceId="Joanna", OutputFormat="mp3")
  ```
* **Azure** – use `azure.cognitiveservices.speech`.
* **Local Only** – drop in `pyttsx3` for offline TTS (quality varies by OS).

---

## 🗂 Project Structure

```
.
├─ pdf_to_speech.py     # main entry‑point script
├─ requirements.txt     # Python deps
├─ docs/                # screenshots & GIFs
└─ examples/            # sample PDFs & generated MP3s
```

---

## 🤝 Contributing

Pull requests, issues, and feature ideas are welcome!  For major changes, please open an issue first to discuss what you’d like to change.  **Please ensure your code passes `flake8` / `ruff` and comes with unit tests.**

---

## 📄 License

Distributed under the MIT License.  See `LICENSE` for more information.

---

## 🙏 Acknowledgements

* [pdfminer.six](https://github.com/pdfminer/pdfminer.six) – rock‑solid PDF parsing
* [Google Cloud Text‑to‑Speech](https://cloud.google.com/text-to-speech) – premium neural voices
* [gTTS](https://pypi.org/project/gTTS/) – free fallback
* [pydub](https://github.com/jiaaro/pydub) – audio handling made pythonic

> Crafted with ♥ to help you "read" while your eyes rest.
