"""
YouTube Video Summary Generator
================================
A Streamlit application that generates summaries of YouTube videos
using either Ollama (local LLM) or Google Gemini API.
"""

import streamlit as st
import re
import json
import time
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# ─────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube Summary Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# Custom CSS for premium styling
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* ── Hide default Streamlit branding ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ── Main container ── */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    /* ── Hero header ── */
    .hero-header {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #1a1f2e 0%, #0e1117 50%, #1a1225 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 75, 75, 0.15);
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 30% 50%, rgba(255, 75, 75, 0.06) 0%, transparent 50%),
                    radial-gradient(circle at 70% 50%, rgba(120, 80, 255, 0.05) 0%, transparent 50%);
        pointer-events: none;
    }
    .hero-header h1 {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF8F8F 40%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
        position: relative;
    }
    .hero-header p {
        color: #9CA3AF;
        font-size: 1.05rem;
        font-weight: 400;
        position: relative;
    }

    /* ── Card styles ── */
    .glass-card {
        background: rgba(26, 31, 46, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(255, 75, 75, 0.2);
    }

    /* ── Summary output card ── */
    .summary-card {
        background: linear-gradient(145deg, rgba(26, 31, 46, 0.8), rgba(14, 17, 23, 0.9));
        border: 1px solid rgba(192, 132, 252, 0.15);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1rem;
        line-height: 1.75;
    }
    .summary-card h3 {
        background: linear-gradient(90deg, #C084FC, #FF4B4B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        font-weight: 700;
    }

    /* ── Stat pills ── */
    .stat-row {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .stat-pill {
        background: rgba(255, 75, 75, 0.08);
        border: 1px solid rgba(255, 75, 75, 0.15);
        border-radius: 999px;
        padding: 0.4rem 1rem;
        font-size: 0.82rem;
        color: #FF8F8F;
        font-weight: 500;
    }
    .stat-pill.purple {
        background: rgba(192, 132, 252, 0.08);
        border-color: rgba(192, 132, 252, 0.15);
        color: #D8B4FE;
    }
    .stat-pill.green {
        background: rgba(52, 211, 153, 0.08);
        border-color: rgba(52, 211, 153, 0.15);
        color: #6EE7B7;
    }

    /* ── Sidebar styling ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #1A1225 100%);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ── Button override ── */
    .stButton > button {
        background: linear-gradient(135deg, #FF4B4B 0%, #C084FC 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 75, 75, 0.3);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ── Text input styling ── */
    .stTextInput > div > div > input {
        background: rgba(26, 31, 46, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        color: #FAFAFA;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 75, 75, 0.4);
        box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.1);
    }

    /* ── Select box ── */
    .stSelectbox > div > div {
        background: rgba(26, 31, 46, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
    }

    /* ── Divider ── */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255, 75, 75, 0.3), rgba(192, 132, 252, 0.3), transparent);
        border: none;
        margin: 1.5rem 0;
    }

    /* ── Spinner styling ── */
    .stSpinner > div {
        border-top-color: #FF4B4B !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #D8B4FE;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────

def extract_video_id(url: str) -> str | None:
    """Extract the YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id: str, languages: list[str] = None) -> dict:
    """
    Fetch transcript for a YouTube video using youtube-transcript-api v1.x.
    Returns dict with 'text', 'language', and 'duration'.
    """
    if languages is None:
        languages = ["en", "hi", "es", "fr", "de", "ja", "ko", "pt", "ru", "zh"]

    try:
        ytt_api = YouTubeTranscriptApi()

        # Fetch transcript with language priority list
        fetched = ytt_api.fetch(video_id, languages=languages)

        # Build full text from snippets
        full_text = " ".join(snippet.text for snippet in fetched)

        # Calculate total duration from the last snippet
        if len(fetched) > 0:
            last_snippet = fetched[-1]
            duration_sec = last_snippet.start + last_snippet.duration
        else:
            duration_sec = 0

        return {
            "text": full_text,
            "language": fetched.language,
            "language_code": fetched.language_code,
            "duration": duration_sec,
        }
    except Exception as e:
        # If preferred languages fail, try fetching any available transcript
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)

            # Pick the first available transcript
            if transcript_list:
                first_transcript = transcript_list[0]
                fetched = ytt_api.fetch(
                    video_id,
                    languages=[first_transcript.language_code],
                )
                full_text = " ".join(snippet.text for snippet in fetched)

                if len(fetched) > 0:
                    last_snippet = fetched[-1]
                    duration_sec = last_snippet.start + last_snippet.duration
                else:
                    duration_sec = 0

                return {
                    "text": full_text,
                    "language": fetched.language,
                    "language_code": fetched.language_code,
                    "duration": duration_sec,
                }
        except Exception:
            pass

        return {"error": str(e)}


def summarize_with_ollama(
    transcript: str,
    model: str = "llama3.2",
    base_url: str = "http://localhost:11434",
    summary_style: str = "detailed",
) -> str:
    """Generate a summary using a local Ollama model."""
    style_prompts = {
        "detailed": "Provide a comprehensive, well-structured summary with key points, main arguments, and important details. Use markdown formatting with headers and bullet points.",
        "concise": "Provide a brief, concise summary capturing only the most essential points in 3-5 bullet points.",
        "bullet_points": "Summarize the content as a well-organized bullet-point list, grouped by topic or theme. Use markdown formatting.",
        "eli5": "Explain the content as if explaining to a 5-year-old. Keep it simple, fun, and easy to understand.",
    }

    prompt = f"""You are an expert content summarizer. Your task is to summarize the following YouTube video transcript.

{style_prompts.get(summary_style, style_prompts['detailed'])}

TRANSCRIPT:
---
{transcript[:12000]}
---

Provide your summary below:"""

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 2048},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "No response generated.")
    except requests.exceptions.ConnectionError:
        return "❌ **Connection Error**: Could not connect to Ollama. Make sure Ollama is running (`ollama serve`) and accessible at the specified URL."
    except requests.exceptions.Timeout:
        return "❌ **Timeout**: The request to Ollama timed out. The model may be loading or the transcript is too long."
    except Exception as e:
        return f"❌ **Error**: {str(e)}"


def summarize_with_gemini(
    transcript: str,
    api_key: str,
    model: str = "gemini-2.0-flash",
    summary_style: str = "detailed",
) -> str:
    """Generate a summary using Google Gemini API with auto-fallback on quota errors."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    style_prompts = {
        "detailed": "Provide a comprehensive, well-structured summary with key points, main arguments, and important details. Use markdown formatting with headers and bullet points.",
        "concise": "Provide a brief, concise summary capturing only the most essential points in 3-5 bullet points.",
        "bullet_points": "Summarize the content as a well-organized bullet-point list, grouped by topic or theme. Use markdown formatting.",
        "eli5": "Explain the content as if explaining to a 5-year-old. Keep it simple, fun, and easy to understand.",
    }

    prompt = f"""You are an expert content summarizer. Your task is to summarize the following YouTube video transcript.

{style_prompts.get(summary_style, style_prompts['detailed'])}

TRANSCRIPT:
---
{transcript[:30000]}
---

Provide your summary below:"""

    # Models to try in order (selected model first, then fallbacks)
    all_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    models_to_try = [model] + [m for m in all_models if m != model]

    last_error = None
    for try_model in models_to_try:
        try:
            gen_model = genai.GenerativeModel(try_model)
            response = gen_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=2048,
                ),
            )
            if try_model != model:
                return f"> ⚠️ *Quota exceeded for `{model}`. Used `{try_model}` instead.*\n\n{response.text}"
            return response.text
        except Exception as e:
            error_str = str(e)
            last_error = error_str
            if "429" in error_str or "quota" in error_str.lower():
                # Quota error — try next model
                continue
            else:
                # Non-quota error — don't retry
                return f"❌ **Error with `{try_model}`**: {error_str}"

    # All models exhausted
    return (
        "❌ **Quota Exceeded on All Models**\n\n"
        "Your Gemini API free tier quota has been exhausted for all available models. "
        "Here's what you can do:\n\n"
        "1. **Wait** — Free tier quotas reset daily\n"
        "2. **Use Ollama** — Switch to the free local option in the sidebar\n"
        "3. **Upgrade** — Enable billing at [Google AI Studio](https://aistudio.google.com)\n"
        "4. **New API key** — Create a new project at [Google Cloud Console](https://console.cloud.google.com)\n\n"
        f"*Last error: {last_error[:200]}*"
    )


def get_ollama_models(base_url: str = "http://localhost:11434") -> list[str]:
    """Fetch the list of locally available Ollama models."""
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=5)
        resp.raise_for_status()
        models = resp.json().get("models", [])
        return [m["name"] for m in models]
    except Exception:
        return []


def format_duration(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    seconds = int(seconds)
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


# ─────────────────────────────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🎬 YouTube Summary Generator</h1>
    <p>Transform any YouTube video into a concise, AI-powered summary in seconds</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# Sidebar – Configuration
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Provider selection
    provider = st.selectbox(
        "🤖 AI Provider",
        ["Google Gemini", "Ollama (Local)"],
        help="Choose which AI backend to use for summarization.",
    )

    if provider == "Google Gemini":
        st.markdown("##### 🔑 Google Gemini Settings")
        gemini_api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="Enter your Gemini API key…",
            help="Get your free API key at https://aistudio.google.com/apikey",
        )
        gemini_model = st.selectbox(
            "Model",
            [
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ],
            help="Select the Gemini model to use.",
        )
    else:
        st.markdown("##### 🦙 Ollama Settings")
        ollama_url = st.text_input(
            "Ollama URL",
            value="http://localhost:11434",
            help="Base URL where Ollama is running.",
        )
        # Try fetching available models
        available_models = get_ollama_models(ollama_url)
        if available_models:
            ollama_model = st.selectbox(
                "Model",
                available_models,
                help="Select from locally available Ollama models.",
            )
            st.success(f"✅ Connected – {len(available_models)} model(s) found")
        else:
            ollama_model = st.text_input(
                "Model Name",
                value="llama3.2",
                help="Enter the Ollama model name manually.",
            )
            st.warning("⚠️ Cannot connect to Ollama. Is it running?")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # Summary style
    st.markdown("##### 📝 Summary Style")
    summary_style = st.selectbox(
        "Style",
        ["detailed", "concise", "bullet_points", "eli5"],
        format_func=lambda x: {
            "detailed": "📋 Detailed Summary",
            "concise": "⚡ Concise Summary",
            "bullet_points": "📌 Bullet Points",
            "eli5": "🧒 Explain Like I'm 5",
        }.get(x, x),
    )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **YouTube Summary Generator** uses AI to create
        summaries from YouTube video transcripts.

        **Supported providers:**
        - 🌐 **Google Gemini** – Cloud API (needs API key)
        - 🦙 **Ollama** – Local models (needs Ollama running)

        **Tips:**
        - Works best with videos that have captions/subtitles
        - Longer videos may be truncated to fit model context
        - Auto-detects transcript language
        """)


# ─────────────────────────────────────────────────────────────────────
# Main Content
# ─────────────────────────────────────────────────────────────────────
col_input, col_spacer = st.columns([4, 1])

with col_input:
    youtube_url = st.text_input(
        "🔗 YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed",
    )

# Show video preview if URL is valid
video_id = extract_video_id(youtube_url) if youtube_url else None

if video_id:
    col_preview, col_info = st.columns([1.2, 1])

    with col_preview:
        st.markdown(f"""
        <div class="glass-card" style="padding: 0; overflow: hidden;">
            <iframe width="100%" height="280" 
                src="https://www.youtube.com/embed/{video_id}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen
                style="border-radius: 16px;">
            </iframe>
        </div>
        """, unsafe_allow_html=True)

    with col_info:
        st.markdown(f"""
        <div class="glass-card">
            <p style="color: #9CA3AF; font-size: 0.85rem; margin-bottom: 0.5rem;">VIDEO ID</p>
            <p style="font-family: monospace; color: #FF8F8F; font-size: 1.1rem;">{video_id}</p>
            <p style="color: #9CA3AF; font-size: 0.85rem; margin-top: 1rem; margin-bottom: 0.5rem;">PROVIDER</p>
            <p style="color: #D8B4FE; font-size: 1rem;">{"🌐 " + gemini_model if provider == "Google Gemini" else "🦙 " + ollama_model}</p>
            <p style="color: #9CA3AF; font-size: 0.85rem; margin-top: 1rem; margin-bottom: 0.5rem;">STYLE</p>
            <p style="color: #6EE7B7; font-size: 1rem;">{summary_style.replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# Generate Button & Logic
# ─────────────────────────────────────────────────────────────────────
generate_btn = st.button("✨ Generate Summary", use_container_width=True, disabled=not video_id)

if generate_btn and video_id:
    # Validate provider config
    if provider == "Google Gemini" and not gemini_api_key:
        st.error("🔑 Please enter your Google Gemini API key in the sidebar.")
        st.stop()

    # Step 1: Fetch transcript
    with st.status("🔍 Fetching transcript...", expanded=True) as status:
        st.write("Connecting to YouTube…")
        transcript_data = get_transcript(video_id)

        if "error" in transcript_data:
            st.error(f"Failed to fetch transcript: {transcript_data['error']}")
            st.stop()

        transcript_text = transcript_data["text"]
        word_count = len(transcript_text.split())
        duration = transcript_data.get("duration", 0)
        language = transcript_data.get("language", "Unknown")

        st.write(f"✅ Transcript fetched – {word_count:,} words")
        status.update(label="✅ Transcript fetched!", state="complete")

    # Show transcript stats
    st.markdown(f"""
    <div class="stat-row">
        <span class="stat-pill">📝 {word_count:,} words</span>
        <span class="stat-pill purple">⏱️ {format_duration(duration)}</span>
        <span class="stat-pill green">🌍 {language}</span>
        <span class="stat-pill">{"🌐 Gemini" if provider == "Google Gemini" else "🦙 Ollama"}</span>
    </div>
    """, unsafe_allow_html=True)

    # Step 2: Generate summary
    with st.status("🧠 Generating summary…", expanded=True) as status:
        st.write(f"Sending transcript to {'Gemini' if provider == 'Google Gemini' else 'Ollama'}…")
        start_time = time.time()

        if provider == "Google Gemini":
            summary = summarize_with_gemini(
                transcript_text,
                gemini_api_key,
                model=gemini_model,
                summary_style=summary_style,
            )
        else:
            summary = summarize_with_ollama(
                transcript_text,
                model=ollama_model,
                base_url=ollama_url,
                summary_style=summary_style,
            )

        elapsed = time.time() - start_time
        st.write(f"✅ Summary generated in {elapsed:.1f}s")
        status.update(label="✅ Summary ready!", state="complete")

    # Step 3: Display summary
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-card">
        <h3>📄 Summary</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(summary)

    # Action buttons
    col_dl, col_copy = st.columns(2)
    with col_dl:
        st.download_button(
            label="📥 Download Summary",
            data=summary,
            file_name=f"summary_{video_id}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_copy:
        st.download_button(
            label="📥 Download Transcript",
            data=transcript_text,
            file_name=f"transcript_{video_id}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # Expandable transcript view
    with st.expander("📜 View Full Transcript"):
        st.text_area(
            "Transcript",
            transcript_text,
            height=400,
            label_visibility="collapsed",
        )

elif not youtube_url:
    # Empty state
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 3rem 1.5rem;">
        <p style="font-size: 3rem; margin-bottom: 0.5rem;">🎥</p>
        <p style="color: #9CA3AF; font-size: 1.1rem; margin-bottom: 0.3rem;">
            Paste a YouTube URL above to get started
        </p>
        <p style="color: #6B7280; font-size: 0.85rem;">
            Supports standard URLs, short links, and embedded URLs
        </p>
    </div>
    """, unsafe_allow_html=True)

elif youtube_url and not video_id:
    st.error("❌ Invalid YouTube URL. Please enter a valid YouTube video link.")
