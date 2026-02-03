import streamlit as st
import asyncio
import edge_tts
import time
import io
# Docx फाइल पढ़ने के लिए
from docx import Document

# --- 1. Page Configuration (Browser Tab Name & Icon) ---
st.set_page_config(
    page_title="Mohit's AI Voiceover",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Custom CSS for "Professional Website Look" ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
    }
    
    /* Header Styling */
    h1 {
        color: #1a202c;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    /* Custom Card Containers */
    .css-1r6slb0 {
        background-color: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Professional Button */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 18px;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
    }

    /* Progress Bar Color */
    .stProgress > div > div > div > div {
        background-color: #10b981;
    }
    
    /* Status Text */
    .status-text {
        font-size: 16px;
        color: #4b5563;
        font-weight: 500;
        text-align: center;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Header Section ---
st.title("🎙️ Mohit's AI Voiceover Studio")
st.markdown("<p style='text-align: center; color: #4b5563;'>Professional Text-to-Speech Converter with Dual Voice Technology</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. Sidebar (Settings) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
    st.header("⚙️ Control Panel")
    
    # Mode Selection
    st.subheader("Select Style")
    mode = st.radio(
        "Choose Mode:",
        ("🗣️ Conversational (Male + Female)", "🎤 Normal (Male Only - Documentary)"),
        help="Conversational mode detects [M] and [F] tags."
    )
    
    st.markdown("---")
    
    # Voice Settings
    st.subheader("Audio Settings")
    speed = st.slider("Speed (गति)", -50, 50, 10)
    pitch = st.slider("Pitch (पिच)", -20, 20, 0)
    
    rate_str = f"{speed:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    
    st.info("💡 **Tip:** Upload a script or write directly to generate professional audio.")

# --- 5. Main Logic Functions ---

def read_file(uploaded_file):
    """Reads TXT or DOCX files"""
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

async def generate_audio(text, output_file, progress_bar, status_text):
    """Generates Audio with Progress Bar"""
    final_audio = b""
    
    # Split text into lines for processing
    lines = [line for line in text.strip().split('\n') if line.strip()]
    total_lines = len(lines)
    
    start_time = time.time()
    
    for i, line in enumerate(lines):
        # Update Progress Bar
        percent = (i + 1) / total_lines
        progress_bar.progress(percent)
        
        elapsed = round(time.time() - start_time, 1)
        status_text.markdown(f"<p class='status-text'>Processing Line {i+1} of {total_lines} ({int(percent*100)}%) - ⏱️ {elapsed}s</p>", unsafe_allow_html=True)

        # Logic for Voice Selection
        if mode.startswith("🗣️"): # Conversational
            if line.startswith("[F]"):
                voice = "hi-IN-SwaraNeural"
                clean_text = line.replace("[F]", "").strip()
            elif line.startswith("[M]"):
                voice = "hi-IN-MadhurNeural"
                clean_text = line.replace("[M]", "").strip()
            else:
                voice = "hi-IN-MadhurNeural" # Default if no tag
                clean_text = line.strip()
        else: # Normal Mode
            voice = "hi-IN-MadhurNeural"
            clean_text = line.strip()

        # Generate Chunk
        if clean_text:
            try:
                communicate = edge_tts.Communicate(clean_text, voice, rate=rate_str, pitch=pitch_str)
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        final_audio += chunk["data"]
            except Exception as e:
                st.error(f"Error on line {i+1}: {e}")

    # Save File
    with open(output_file, "wb") as f:
        f.write(final_audio)
        
    return time.time() - start_time

# --- 6. Interface (Tabs) ---
tab1, tab2 = st.tabs(["📝 Write Script", "📂 Upload File"])

final_input_text = ""

with tab1:
    placeholder_text = "[M] नमस्ते दोस्तों!\n[F] स्वागत है Mohit's AI Studio में।\n[M] यहाँ आप फाइल अपलोड करके भी ऑडियो बना सकते हैं।" if mode.startswith("🗣️") else "अपना डॉक्यूमेंट्री टेक्स्ट यहाँ लिखें..."
    text_input = st.text_area("Type your content here:", height=250, placeholder=placeholder_text)
    if text_input:
        final_input_text = text_input

with tab2:
    uploaded_file = st.file_uploader("Upload Script (.txt or .docx)", type=["txt", "docx"])
    if uploaded_file:
        file_content = read_file(uploaded_file)
        st.success(f"✅ File Loaded: {uploaded_file.name}")
        with st.expander("👀 Preview File Content"):
            st.text_area("Content", file_content, height=150)
        final_input_text = file_content

# --- 7. Execution Section ---
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 GENERATE VOICEOVER"):
    if not final_input_text.strip():
        st.warning("⚠️ Please enter text or upload a file first!")
    else:
        output_filename = "mohit_final_audio.mp3"
        
        # UI Elements for Progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Run Async Function
            duration = asyncio.run(generate_audio(final_input_text, output_filename, progress_bar, status_text))
            
            # Success UI
            status_text.empty()
            st.success(f"🎉 Audio Generated Successfully in {round(duration, 2)} seconds!")
            
            # Audio Player & Download
            col1, col2 = st.columns([3, 1])
            with col1:
                st.audio(output_filename)
            with col2:
                with open(output_filename, "rb") as f:
                    st.download_button(
                        label="⬇️ Download MP3",
                        data=f,
                        file_name="Mohit_AI_Voiceover.mp3",
                        mime="audio/mp3"
                    )
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- Footer ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #9ca3af; font-size: 12px;">
    Developed by Mohit | Powered by Edge-TTS & Streamlit
</div>
""", unsafe_allow_html=True)
