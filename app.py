import streamlit as st
import asyncio
import edge_tts
import time

# --- Page Configuration (Professional UI) ---
st.set_page_config(
    page_title="Mohit's AI Voiceover",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Best Look ---
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    h1 {
        color: #1e3a8a;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #2563eb;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #e0f2fe;
        color: #0369a1;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🎙️ Mohit's AI Voiceover Studio")
st.markdown("---")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Mode Selection
    mode = st.radio(
        "Select Mode:",
        ("🗣️ Conversational Style (Male & Female)", "🎤 Normal Mode (Male Only)")
    )
    
    st.markdown("---")
    
    # 2. Audio Settings
    speed = st.slider("Speed (गति)", -50, 50, 10, help="Positive values make it faster.")
    pitch = st.slider("Pitch (पिच)", -20, 20, 0, help="Adjust voice depth.")
    
    rate_str = f"{speed:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    
    st.info("💡 **Tip:** Conversational mode requires [M] and [F] tags.")

# --- Logic Functions ---

async def generate_audio_stream(text, voice, output_file):
    """Simple generation for Normal Mode"""
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    await communicate.save(output_file)

async def generate_conversational_audio(script, output_file, progress_bar, status_text):
    """Complex generation with Progress Bar for Conversational Mode"""
    final_audio = b""
    lines = [line for line in script.strip().split('\n') if line.strip()]
    total_lines = len(lines)
    
    start_time = time.time()
    
    for i, line in enumerate(lines):
        # Update Progress
        progress_percent = (i + 1) / total_lines
        progress_bar.progress(progress_percent)
        elapsed_time = round(time.time() - start_time, 1)
        status_text.markdown(f"**Processing Line {i+1}/{total_lines}** ({int(progress_percent*100)}%) - ⏱️ {elapsed_time}s")

        # Determine Voice
        if mode.startswith("🗣️") and line.startswith("[F]"):
            voice = "hi-IN-SwaraNeural"
            clean_text = line.replace("[F]", "").strip()
        elif mode.startswith("🗣️") and line.startswith("[M]"):
            voice = "hi-IN-MadhurNeural"
            clean_text = line.replace("[M]", "").strip()
        else:
            voice = "hi-IN-MadhurNeural" # Default to Male
            clean_text = line.strip()

        # Generate Chunk
        if clean_text:
            communicate = edge_tts.Communicate(clean_text, voice, rate=rate_str, pitch=pitch_str)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    final_audio += chunk["data"]

    # Save Final File
    with open(output_file, "wb") as f:
        f.write(final_audio)
    
    return time.time() - start_time

# --- Main Interface ---

col1, col2 = st.columns([2, 1])

with col1:
    if mode.startswith("🗣️"):
        st.subheader("Dual Voice Scripting")
        user_input = st.text_area(
            "Enter Script (Use [M] for Male, [F] for Female):", 
            height=300,
            placeholder="[F] नमस्ते दोस्तों!\n[M] स्वागत है आपका Mohit's AI Voiceover में।\n[F] यह कितना आसान है!"
        )
    else:
        st.subheader("Single Voice Scripting")
        user_input = st.text_area(
            "Enter Text (Uses Male Voice 'Madhur'):", 
            height=300,
            placeholder="यहां अपना टेक्स्ट लिखें। यह एक ही आवाज में रिकॉर्ड होगा..."
        )

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True) # Spacing
    st.markdown("### Preview & Export")
    
    generate_btn = st.button("🚀 Generate Audio", key="gen_btn")
    
    # Placeholders for progress
    status_area = st.empty()
    progress_area = st.empty()
    result_area = st.empty()

# --- Execution Logic ---
if generate_btn and user_input:
    output_file = "mohit_voiceover.mp3"
    
    try:
        # Progress Bar Initialization
        progress_bar = progress_area.progress(0)
        status_text = status_area.markdown("**Starting engine...**")
        
        # Run Generation
        if mode.startswith("🗣️"):
            # Conversational
            duration = asyncio.run(generate_conversational_audio(user_input, output_file, progress_bar, status_text))
        else:
            # Normal Mode (Fake progress for UX since it's one stream)
            status_text.markdown("**Processing... (Please wait)**")
            progress_bar.progress(50)
            start_t = time.time()
            asyncio.run(generate_audio_stream(user_input, "hi-IN-MadhurNeural", output_file))
            progress_bar.progress(100)
            duration = time.time() - start_t

        # Success Message
        status_text.empty()
        progress_area.empty()
        
        st.success(f"✅ Done in {round(duration, 2)} seconds!")
        
        # Audio Player & Download
        st.audio(output_file)
        
        with open(output_file, "rb") as f:
            st.download_button(
                label="⬇️ Download MP3",
                data=f,
                file_name="mohits_voiceover.mp3",
                mime="audio/mp3"
            )

    except Exception as e:
        st.error(f"Error: {e}")

elif generate_btn and not user_input:
    st.warning("⚠️ Please enter some text first!")

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>Designed by Mohit | Powered by Edge-TTS</p>", unsafe_allow_html=True)
