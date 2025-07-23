# 🎬 YouTube Video Summarizer using Gemini AI

A beginner-friendly Streamlit web app that converts YouTube video links into concise summaries using Google's Gemini 1.5 Pro and the YouTube Transcript API.

---

🧩 Features

- 🔗 Input any YouTube video URL
- 📄 Extracts transcript using `youtube-transcript-api`
- 🤖 Generates a smart summary using Gemini AI
- 🌐 Clean, responsive UI built with Streamlit
- 🖼️ Automatically displays video thumbnail

---

🛠️ Tech Stack

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://ai.google.dev/)
- [YouTube Transcript API](https://pypi.org/project/youtube-transcript-api/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 📁 Project Structure
youtube-summarizer/
├── app.py # Main application code
├── .env # Contains the Gemini API Key (do not share)
├── requirements.txt # All required Python packages
└── README.md # Project description and usage guide


---

Install the Requirements
pip install -r requirements.txt

Run the App
streamlit run app.py

Open the App
Visit http://localhost:8501 in your browser.


Future Improvements
Export summaries as downloadable PDF or DOCX

Save history of generated summaries

Add speech-to-text support for audio-only content

Support summarizing long videos across multiple parts


🙌 Credits
Google Generative AI

Streamlit

YouTube Transcript API




