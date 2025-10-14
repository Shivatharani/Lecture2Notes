# app.py
import os
from datetime import datetime
import streamlit as st

from utils.stt_utils import transcribe_offline
from utils.summarizer import summarize_transcript_local
from utils.quizgen import generate_quiz_local

# --- Streamlit page config ---
st.set_page_config(page_title="Lecture2Notes 🎓", layout="wide", page_icon="📝")

# --- Header ---
st.markdown("""
<div style='text-align:center; padding:15px; background:linear-gradient(to right, #6C63FF, #3A3BFF); border-radius:15px;'>
    <h1 style='color:white;'>Lecture2Notes — Offline MVP</h1>
    <p style='color:white; font-size:18px;'>Transcribe, Summarize & Generate Quiz from Lectures</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    """
    Upload your lecture audio or transcript CSV.  
    ⚡ Offline MVP using *Whisper* for transcription & *Hugging Face* models for summarization & quiz.
    """, unsafe_allow_html=True
)

# --- Ensure output directories ---
os.makedirs("outputs/transcripts", exist_ok=True)
os.makedirs("outputs/summaries", exist_ok=True)
os.makedirs("outputs/quizzes", exist_ok=True)

# --- Upload section ---
st.subheader("📤 Upload Lecture File")
col1, col2 = st.columns(2)
with col1:
    uploaded_audio = st.file_uploader("🎤 Upload audio (mp3, wav, m4a)", type=["mp3", "wav", "m4a"])
with col2:
    uploaded_csv = st.file_uploader("📄 Upload transcript CSV", type=["csv"])

# --- Options to select ---
st.subheader("⚙ Select Output Options")
options = st.multiselect(
    "Choose what to generate (Transcript is recommended) 📌",
    ["Transcript 📝", "Summary 🗒", "Quiz ❓"],
    default=["Transcript 📝"]
)

# --- Start processing with a button ---
go_button = st.button("🚀 Generate Selected")

transcript_text = None
base_name = f"lecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if go_button:
    # --- Process CSV first ---
    if uploaded_csv is not None:
        st.info("Converting CSV to transcript...")
        try:
            with open("temp_uploaded.csv", "wb") as f:
                f.write(uploaded_csv.getbuffer())
            from utils.csv_to_transcript import convert_csv_to_txt
            out_txt = convert_csv_to_txt("temp_uploaded.csv", out_dir="outputs/transcripts", output_name=base_name)
            with open(out_txt, "r", encoding="utf-8") as fh:
                transcript_text = fh.read()
            st.success("✅ CSV converted to transcript!")
        except Exception as e:
            st.error(f"CSV conversion failed: {e}")

    # --- Process Audio if uploaded ---
    elif uploaded_audio is not None:
        st.info("Transcribing audio locally... this may take a while ⏳")
        try:
            transcript_text = transcribe_offline(uploaded_audio)
            st.success("✅ Audio transcription completed!")
        except Exception as e:
            st.error(f"Transcription failed: {e}")

    # --- If transcript exists ---
    if transcript_text:
        trans_path = os.path.join("outputs/transcripts", base_name + ".txt")
        with open(trans_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # --- Display based on selected options ---
        if "Transcript 📝" in options:
            st.markdown("### 📝 Transcript")
            st.text_area("Transcript", value=transcript_text, height=300)
            st.download_button("💾 Download Transcript", data=transcript_text, file_name=os.path.basename(trans_path), key="dl_transcript")

        if "Summary 🗒" in options:
            st.markdown("### 🗒 Summary")
            st.info("Generating summary...")
            try:
                summary_obj = summarize_transcript_local(transcript_text)
                summary_text = summary_obj.get("summary", "")
                st.text_area("Summary", value=summary_text, height=250)
                sum_path = os.path.join("outputs/summaries", base_name + "_summary.txt")
                with open(sum_path, "w", encoding="utf-8") as f:
                    f.write(summary_text)
                st.download_button("💾 Download Summary", data=summary_text, file_name=os.path.basename(sum_path), key="dl_summary")
            except Exception as e:
                st.error(f"Summarization failed: {e}")
                summary_text = ""

        if "Quiz ❓" in options:
            st.markdown("### ❓ Quiz")
            st.info("Generating quiz...")
            try:
                if "summary_text" not in locals():
                    summary_text = transcript_text  # fallback
                quiz_text = generate_quiz_local(summary_text, num_questions=6)
                st.text_area("Quiz (plain text)", value=quiz_text, height=300)
                quiz_path = os.path.join("outputs/quizzes", base_name + "_quiz.txt")
                with open(quiz_path, "w", encoding="utf-8") as f:
                    f.write(quiz_text)
                st.download_button("💾 Download Quiz", data=quiz_text, file_name=os.path.basename(quiz_path), key="dl_quiz")
            except Exception as e:
                st.error(f"Quiz generation failed: {e}")
    else:
        st.warning("⚠ No valid file uploaded. Please upload an audio file or CSV transcript first.")
else:
    st.info("⬆ Upload a file, select options, and press *Generate Selected* to start.")

# --- Footer ---
st.markdown("""
<div style='text-align:center; margin-top:50px; color:#888;'>
    Made with ❤ by Lecture2Notes Team
</div>
""", unsafe_allow_html=True)