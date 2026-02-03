import streamlit as st
import asyncio
import edge_tts
import os
import re

st.set_page_config(page_title="Dual Voice AI Studio", page_icon="🎙️")
st.title("🎙️ Multi-Voice Generator (Madhur & Swara)")

st.markdown("""
**Instructions:** - मेल आवाज़ के लिए लाइन के शुरू में **[M]** लिखें।
- फीमेल आवाज़ के लिए लाइन के शुरू में **[F]** लिखें।
- रफ़्तार (Speed) के लिए साइडबार का इस्तेमाल करें।
""")

# --- Sidebar Settings ---
st.sidebar.header("Voice Settings")
speed = st.sidebar.slider("Speed (%)", -50, 50, 15)
rate_str = f"{speed:+d}%"

# --- Logic for Dual Voice ---
async def generate_dual_voice(script_text, output_file):
    final_audio = b""
    # लाइन दर लाइन स्क्रिप्ट को पढ़ना
    lines = script_text.strip().split('\n')
    
    for line in lines:
        if line.startswith("[M]"):
            voice = "hi-IN-MadhurNeural"
            clean_text = line.replace("[M]", "").strip()
        elif line.startswith("[F]"):
            voice = "hi-IN-SwaraNeural"
            clean_text = line.replace("[F]", "").strip()
        else:
            # अगर कुछ नहीं लिखा तो Default Madhur
            voice = "hi-IN-MadhurNeural"
            clean_text = line.strip()

        if clean_text:
            communicate = edge_tts.Communicate(clean_text, voice, rate=rate_str)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    final_audio += chunk["data"]

    with open(output_file, "wb") as f:
        f.write(final_audio)

# --- Input Section ---
user_script = st.text_area("अपनी बातचीत वाली स्क्रिप्ट यहाँ लिखें:", 
placeholder="[M] नमस्ते, आज हम इतिहास पढ़ेंगे।\n[F] जी सर, शुरू करते हैं।",
height=300)

if st.button("🔊 Generate Master Voiceover"):
    if not user_script.strip():
        st.error("कृपया स्क्रिप्ट लिखें!")
    else:
        with st.spinner("दोनों आवाजों को मिक्स किया जा रहा है..."):
            output_mp3 = "dual_voiceover.mp3"
            try:
                asyncio.run(generate_dual_voice(user_script, output_mp3))
                st.audio(output_mp3)
                with open(output_mp3, "rb") as f:
                    st.download_button("⬇️ Download Full Conversation", f, file_name="ai_conversation.mp3")
                st.success("तैयार है!")
            except Exception as e:
                st.error(f"Error: {e}")
