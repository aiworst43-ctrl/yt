import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

st.set_page_config(page_title="YT Notes Generator", page_icon="📝", layout="wide")
st.title("📝 YouTube Video to Smart Notes")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Apni Gemini API Key dalein:", type="password")
    note_language = st.selectbox("Notes ki Language chunein:", ["English", "Hinglish", "Hindi"])
    note_style = st.selectbox("Notes ka Style:", [
        "Detailed Revision Notes",
        "Quick Last-Minute Summary (Bullet Points)",
        "Q&A Format (Important Exam Questions)"
    ])

def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        # Naya logic: Ye saari available transcripts ki list nikalega
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        try:
            # Pehle English ya Hindi dhundhne ki koshish karega
            transcript = transcript_list.find_transcript(['en', 'hi', 'en-IN', 'hi-IN'])
        except:
            # Agar nahi mila toh jo bhi pehla subtitle available hoga, wo utha lega
            transcript = next(iter(transcript_list))
            
        data = transcript.fetch()
        return " ".join([item['text'] for item in data])
    except Exception as e:
        return None

youtube_url = st.text_input("🔗 YouTube Video ka Link Yahan Paste Karein:")

if st.button("Notes Banayein 🚀"):
    if not api_key:
        st.error("Please sidebar mein apni Gemini API Key dalein!")
    elif not youtube_url:
        st.error("Please YouTube video ka link dalein!")
    else:
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("Ye YouTube link sahi nahi lag raha.")
        else:
            with st.spinner("Transcript nikala ja raha hai..."):
                transcript = get_transcript(video_id)
            
            if not transcript:
                st.error("Is video ke subtitles available nahi hain ya YouTube ne block kiye hain.")
            else:
                with st.spinner("AI notes tayyar kar raha hai..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        prompt = f"""
                        Tum ek expert teacher ho. Niche diye gaye YouTube video transcript se high-quality study notes banao.
                        Language: {note_language}
                        Style: {note_style}
                        Important concepts, definitions, aur formulas ko highlight karo. Faltu baatein (sponsors, intro) hata do.
                        
                        Transcript:
                        {transcript}
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.success("Notes Ready Hain!")
                        st.markdown(response.text)
                        
                        st.download_button(
                            label="📥 Notes Download Karein",
                            data=response.text,
                            file_name="YouTube_Notes.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")
