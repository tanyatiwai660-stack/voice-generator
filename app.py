import streamlit as st
import asyncio
import edge_tts
import os
# DOCX फाइल पढ़ने के लिए लाइब्रेरी (इसे requirements.txt में डालना होगा)
from docx import Document

# पेज का टाइटल
st.set_page_config(page_title="AI Voiceover Generator", page_icon="🎙️")
st.title("🎙️ Text-to-Speech Converter (Madhur/Swara)")

# --- साइडबार (सेटिंग्स) ---
st.sidebar.header("Voice Settings")
gender = st.sidebar.radio("आवाज़ चुनें:", ["Male (Madhur)", "Female (Swara)"])
rate = st.sidebar.slider("Speed (रफ़्तार):", -50, 50, 10)
pitch = st.sidebar.slider("Pitch (गहराई):", -20, 20, 0)

# आवाज़ का कोड सेट करना
voice = "hi-IN-MadhurNeural" if "Male" in gender else "hi-IN-SwaraNeural"
rate_str = f"{rate:+d}%"
pitch_str = f"{pitch:+d}Hz"

# --- इनपुट सेक्शन ---
tab1, tab2 = st.tabs(["📝 Write Text", "📂 Upload File"])

final_text = ""

with tab1:
    user_text = st.text_area("अपना टेक्स्ट यहाँ लिखें:", height=200)
    if user_text:
        final_text = user_text

with tab2:
    uploaded_file = st.file_uploader("TXT या DOCX फाइल उपलोड करें", type=["txt", "docx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".txt"):
            final_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".docx"):
            doc = Document(uploaded_file)
            final_text = "\n".join([para.text for para in doc.paragraphs])
        st.success("फाइल पढ़ ली गई है!")
        with st.expander("टेक्स्ट देखें"):
            st.write(final_text)

# --- वॉइस जनरेट करने का फंक्शन ---
async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    await communicate.save(output_file)

# --- बटन ---
if st.button("🔊 Generate Voiceover"):
    if not final_text.strip():
        st.warning("कृपया पहले कुछ टेक्स्ट लिखें या फाइल अपलोड करें।")
    else:
        with st.spinner("ऑडियो बन रहा है... कृपया इंतज़ार करें..."):
            output_file = "generated_audio.mp3"
            try:
                # Async फंक्शन को रन करना
                asyncio.run(text_to_speech(final_text, output_file))
                
                # ऑडियो प्लेयर दिखाना
                st.audio(output_file)
                
                # डाउनलोड बटन
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download MP3",
                        data=f,
                        file_name="voiceover.mp3",
                        mime="audio/mp3"
                    )
                st.success("सफलतापूर्वक हो गया!")
                
            except Exception as e:
                st.error(f"Error: {e}")
