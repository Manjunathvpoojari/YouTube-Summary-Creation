# YouTube Summary Generator 🎬

A beautiful Streamlit application that generates AI-powered summaries of YouTube videos using **Google Gemini** or **Ollama** (local LLMs).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)

## Features

- 🔗 **Smart URL Parsing** – Supports all YouTube URL formats (standard, shorts, embeds, short links)
- 📝 **Auto Transcript Extraction** – Fetches captions/subtitles with auto-language detection
- 🌐 **Google Gemini** – Cloud-based summarization with multiple model options
- 🦙 **Ollama** – Fully local, private summarization with any locally installed model
- 🎨 **4 Summary Styles** – Detailed, Concise, Bullet Points, or ELI5
- 📥 **Download** – Export summaries as Markdown or transcripts as text
- 🎬 **Video Preview** – Embedded player with video metadata

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the app

```bash
streamlit run app.py
```

### 3. Configure your AI provider

#### Option A: Google Gemini (Cloud)
1. Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey)
2. Select "Google Gemini" in the sidebar
3. Paste your API key

#### Option B: Ollama (Local)
1. Install [Ollama](https://ollama.com)
2. Pull a model: `ollama pull llama3.2`
3. Start Ollama: `ollama serve`
4. Select "Ollama (Local)" in the sidebar

## Usage

1. Paste a YouTube video URL
2. Choose your AI provider and summary style in the sidebar
3. Click **✨ Generate Summary**
4. Download the summary or transcript

## Requirements

- Python 3.10+
- YouTube videos must have captions/subtitles available
- For Gemini: Valid Google API key
- For Ollama: Ollama running locally with at least one model installed
