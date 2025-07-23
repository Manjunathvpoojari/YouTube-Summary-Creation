import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ====== IMPROVED VIDEO ID EXTRACTION ======
def extract_video_id(url):
    """Extract video ID from any YouTube URL format."""
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return None  # Invalid URL

# ====== GET TRANSCRIPT ======
def get_transcript(url):
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return "Error: Invalid YouTube URL. Try again with a valid link."
        
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception as e:
        return f"Transcript Error: {str(e)}"

# ====== GENERATE SUMMARY USING GEMINI ======
def get_summary(text):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        prompt = """You are an expert summarizer. Summarize the following YouTube transcript into clear bullet points (under 250 words):\n\n"""
        response = model.generate_content(prompt + text)
        return response.text
    except Exception as e:
        return f"Gemini Error: {str(e)}"

# ====== STREAMLIT UI ======
st.title("🎬 YouTube Video Summarizer")
st.write("Paste any YouTube link to get an AI-generated summary.")

url = st.text_input("Enter YouTube URL:")

if url:
    video_id = extract_video_id(url)
    if video_id:
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", caption="Video Thumbnail")
    else:
        st.warning("⚠️ Please enter a valid YouTube URL.")

if st.button("Summarize Video"):
    if not url:
        st.error("Please enter a YouTube URL first.")
    else:
        with st.spinner("Processing..."):
            transcript = get_transcript(url)
            
            if transcript.startswith("Error"):
                st.error(transcript)
            else:
                summary = get_summary(transcript)
                
                if summary.startswith("Gemini Error"):
                    st.error(summary)
                else:
                    st.markdown("## ✨ Summary")
                    st.write(summary)
                    st.success("✅ Summary generated successfully!")