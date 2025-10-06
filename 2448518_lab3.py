import streamlit as st
import speech_recognition as sr
import pyttsx3
import wave
import os
import time
import json
from datetime import datetime
from pathlib import Path
import tempfile
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="Advanced Speech-to-Text System",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .css-1r6slb0 {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        color: white;
        padding: 30px 0;
        margin-bottom: 30px;
        animation: fadeInDown 0.8s ease-out;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
    }
    
    /* Status indicator */
    .status-box {
        padding: 15px 25px;
        border-radius: 15px;
        font-weight: 600;
        text-align: center;
        margin: 20px 0;
        font-size: 1.1rem;
        animation: fadeIn 0.5s;
    }
    
    .status-idle {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        color: #495057;
    }
    
    .status-listening {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        animation: pulse 2s infinite;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
    }
    
    .status-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
    }
    
    .status-success {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
    }
    
    /* Transcription box */
    .transcription-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 25px;
        min-height: 300px;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #333;
        border: 3px solid #dee2e6;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
        font-family: 'Courier New', monospace;
    }
    
    /* Stats card */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* File uploader */
    .uploadedFile {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        padding: 20px;
        border: 3px dashed #667eea;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 20px;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 15px;
        font-weight: 500;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Log entry */
    .log-entry {
        padding: 12px;
        margin: 8px 0;
        border-radius: 10px;
        border-left: 4px solid;
        font-size: 0.95rem;
    }
    
    .log-info {
        background: #d1ecf1;
        border-color: #17a2b8;
        color: #0c5460;
    }
    
    .log-success {
        background: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    
    .log-error {
        background: #f8d7da;
        border-color: #dc3545;
        color: #721c24;
    }
    
    /* Comparison table */
    .comparison-table {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcription_history' not in st.session_state:
    st.session_state.transcription_history = []
if 'current_transcription' not in st.session_state:
    st.session_state.current_transcription = ""
if 'stats' not in st.session_state:
    st.session_state.stats = {
        'total_words': 0,
        'total_characters': 0,
        'recognition_time': 0,
        'sessions': 0
    }
if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False


def add_log(message, log_type='info'):
    """Add entry to activity log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_class = f"log-{log_type}"
    st.session_state.activity_log.append({
        'timestamp': timestamp,
        'message': message,
        'type': log_class
    })
    # Keep only last 20 entries
    if len(st.session_state.activity_log) > 20:
        st.session_state.activity_log = st.session_state.activity_log[-20:]


def update_stats(text, recognition_time):
    """Update session statistics"""
    words = len(text.split())
    chars = len(text)
    
    st.session_state.stats['total_words'] += words
    st.session_state.stats['total_characters'] += chars
    st.session_state.stats['recognition_time'] += recognition_time


def process_audio_file(uploaded_file, language='en-US'):
    """Process uploaded audio file"""
    recognizer = sr.Recognizer()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        with sr.AudioFile(tmp_file_path) as source:
            add_log(f"Processing audio file: {uploaded_file.name}", 'info')
            audio = recognizer.record(source)
            
            start_time = time.time()
            
            try:
                # Get detailed results
                result = recognizer.recognize_google(audio, language=language, show_all=True)
                recognition_time = time.time() - start_time
                
                if isinstance(result, dict) and 'alternative' in result:
                    alternatives = result['alternative']
                    best_result = alternatives[0]
                    transcription = best_result.get('transcript', '')
                    confidence = best_result.get('confidence', 0)
                    
                    # Update session state
                    st.session_state.current_transcription = transcription
                    st.session_state.transcription_history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'text': transcription,
                        'confidence': confidence,
                        'recognition_time': recognition_time,
                        'source': uploaded_file.name,
                        'language': language
                    })
                    
                    update_stats(transcription, recognition_time)
                    add_log(f"Successfully transcribed: {transcription[:50]}...", 'success')
                    
                    return {
                        'transcription': transcription,
                        'confidence': confidence,
                        'recognition_time': recognition_time,
                        'alternatives': alternatives[1:4] if len(alternatives) > 1 else []
                    }
                else:
                    transcription = str(result)
                    st.session_state.current_transcription = transcription
                    return {'transcription': transcription}
                    
            except sr.UnknownValueError:
                add_log("Could not understand audio in file", 'error')
                return None
            except sr.RequestError as e:
                add_log(f"API Error: {e}", 'error')
                return None
        
    except Exception as e:
        add_log(f"Error processing file: {e}", 'error')
        return None
    finally:
        # Clean up temp file
        if 'tmp_file_path' in locals():
            try:
                os.unlink(tmp_file_path)
            except:
                pass


def listen_from_microphone(duration=5, language='en-US'):
    """Listen to microphone and transcribe"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            add_log("Adjusting for ambient noise...", 'info')
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            add_log(f"Listening for {duration} seconds...", 'info')
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            add_log("Processing speech...", 'info')
            start_time = time.time()
            
            try:
                text = recognizer.recognize_google(audio, language=language)
                recognition_time = time.time() - start_time
                
                st.session_state.current_transcription = text
                st.session_state.transcription_history.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'text': text,
                    'recognition_time': recognition_time,
                    'source': 'microphone',
                    'language': language
                })
                
                update_stats(text, recognition_time)
                add_log(f"Transcribed: {text}", 'success')
                
                return text
                
            except sr.UnknownValueError:
                add_log("Could not understand audio", 'error')
                return None
            except sr.RequestError as e:
                add_log(f"API Error: {e}", 'error')
                return None
                
    except Exception as e:
        add_log(f"Microphone error: {e}", 'error')
        return None


def compare_recognition_methods(audio_file):
    """Compare different recognition methods"""
    recognizer = sr.Recognizer()
    results = {}
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        with sr.AudioFile(tmp_file_path) as source:
            audio = recognizer.record(source)
            
            # Google Speech Recognition
            try:
                start = time.time()
                text = recognizer.recognize_google(audio)
                time_taken = time.time() - start
                results['Google'] = {
                    'text': text,
                    'time': time_taken,
                    'status': '✅ Success'
                }
            except Exception as e:
                results['Google'] = {'status': f'❌ Failed: {str(e)}'}
            
            # Sphinx (offline)
            try:
                start = time.time()
                text = recognizer.recognize_sphinx(audio)
                time_taken = time.time() - start
                results['Sphinx (Offline)'] = {
                    'text': text,
                    'time': time_taken,
                    'status': '✅ Success'
                }
            except Exception as e:
                results['Sphinx (Offline)'] = {'status': f'❌ Failed: {str(e)}'}
        
        os.unlink(tmp_file_path)
        return results
        
    except Exception as e:
        add_log(f"Comparison error: {e}", 'error')
        return None


# Main UI
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎤 Advanced Speech-to-Text System</h1>
        <p>Real-time voice transcription with multiple recognition methods</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Language selection
        language_options = {
            'English (US)': 'en-US',
            'English (UK)': 'en-GB',
            'Spanish': 'es-ES',
            'French': 'fr-FR',
            'German': 'de-DE',
            'Italian': 'it-IT',
            'Hindi': 'hi-IN',
            'Chinese (Simplified)': 'zh-CN',
            'Japanese': 'ja-JP'
        }
        
        selected_language = st.selectbox(
            "🌐 Recognition Language",
            options=list(language_options.keys()),
            index=0
        )
        language_code = language_options[selected_language]
        
        st.markdown("---")
        
        # Recording duration
        duration = st.slider("⏱️ Recording Duration (seconds)", 3, 30, 5)
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📊 Session Statistics")
        st.metric("Total Words", st.session_state.stats['total_words'])
        st.metric("Total Characters", st.session_state.stats['total_characters'])
        st.metric("Total Time", f"{st.session_state.stats['recognition_time']:.1f}s")
        
        st.markdown("---")
        
        # Clear all data
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.transcription_history = []
            st.session_state.current_transcription = ""
            st.session_state.stats = {
                'total_words': 0,
                'total_characters': 0,
                'recognition_time': 0,
                'sessions': 0
            }
            st.session_state.activity_log = []
            add_log("All data cleared", 'info')
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎙️ Voice Input")
        
        # Microphone recording
        st.markdown("#### Real-time Recording")
        if st.button("🔴 Start Recording", use_container_width=True, type="primary"):
            with st.spinner(f"🎤 Recording for {duration} seconds..."):
                result = listen_from_microphone(duration, language_code)
                if result:
                    st.success(f"✅ Transcription successful!")
                else:
                    st.error("❌ Transcription failed. Please try again.")
        
        st.markdown("---")
        
        # File upload
        st.markdown("#### 📁 Upload Audio File")
        uploaded_file = st.file_uploader(
            "Choose an audio file (WAV, MP3, OGG)",
            type=['wav', 'mp3', 'ogg', 'flac'],
            help="Upload an audio file to transcribe"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("🔄 Transcribe File", use_container_width=True):
                    with st.spinner("Processing audio file..."):
                        result = process_audio_file(uploaded_file, language_code)
                        if result:
                            st.success("✅ File processed successfully!")
                            
                            # Show confidence if available
                            if 'confidence' in result:
                                st.progress(result['confidence'], text=f"Confidence: {result['confidence']*100:.1f}%")
                            
                            # Show alternatives
                            if 'alternatives' in result and result['alternatives']:
                                with st.expander("🔄 Alternative Transcriptions"):
                                    for i, alt in enumerate(result['alternatives'], 1):
                                        st.write(f"{i}. {alt.get('transcript', '')}")
                        else:
                            st.error("❌ Failed to process file")
            
            with col_b:
                if st.button("🔬 Compare Methods", use_container_width=True):
                    with st.spinner("Comparing recognition methods..."):
                        comparison = compare_recognition_methods(uploaded_file)
                        if comparison:
                            st.success("✅ Comparison complete!")
                            
                            # Display comparison
                            st.markdown("#### 📊 Method Comparison")
                            for method, data in comparison.items():
                                st.markdown(f"**{method}**: {data.get('status', 'Unknown')}")
                                if 'time' in data:
                                    st.write(f"⏱️ Time: {data['time']:.2f}s")
                                if 'text' in data:
                                    st.write(f"📝 Text: {data['text'][:100]}...")
                                st.markdown("---")
    
    with col2:
        st.markdown("### 📝 Transcription Output")
        
        # Current transcription display
        if st.session_state.current_transcription:
            st.markdown(f"""
            <div class="transcription-box">
                {st.session_state.current_transcription}
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                if st.button("📋 Copy Text", use_container_width=True):
                    st.code(st.session_state.current_transcription, language=None)
            with col_y:
                if st.button("💾 Save to File", use_container_width=True):
                    filename = f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    st.download_button(
                        "⬇️ Download",
                        st.session_state.current_transcription,
                        filename,
                        "text/plain",
                        use_container_width=True
                    )
            with col_z:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.current_transcription = ""
                    st.rerun()
        else:
            st.info("💡 No transcription yet. Start recording or upload an audio file to begin!")
    
    # Statistics cards
    st.markdown("### 📊 Quick Stats")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">Words</div>
        </div>
        """.format(st.session_state.stats['total_words']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">Characters</div>
        </div>
        """.format(st.session_state.stats['total_characters']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">Transcriptions</div>
        </div>
        """.format(len(st.session_state.transcription_history)), unsafe_allow_html=True)
    
    with col4:
        avg_time = (st.session_state.stats['recognition_time'] / len(st.session_state.transcription_history) 
                   if st.session_state.transcription_history else 0)
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{:.1f}s</div>
            <div class="stat-label">Avg Time</div>
        </div>
        """.format(avg_time), unsafe_allow_html=True)
    
    # History and Logs
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📜 Transcription History", "📋 Activity Log"])
    
    with tab1:
        if st.session_state.transcription_history:
            for i, entry in enumerate(reversed(st.session_state.transcription_history[-10:]), 1):
                with st.expander(f"🔹 {entry['timestamp']} - {entry.get('source', 'Unknown')}"):
                    st.write(f"**Text:** {entry['text']}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if 'confidence' in entry:
                            st.write(f"🎯 Confidence: {entry['confidence']*100:.1f}%")
                        st.write(f"⏱️ Time: {entry.get('recognition_time', 0):.2f}s")
                    with col_b:
                        st.write(f"🌐 Language: {entry.get('language', 'N/A')}")
                        st.write(f"📊 Words: {len(entry['text'].split())}")
        else:
            st.info("No transcription history yet")
    
    with tab2:
        if st.session_state.activity_log:
            for log in reversed(st.session_state.activity_log):
                st.markdown(f"""
                <div class="log-entry {log['type']}">
                    <strong>[{log['timestamp']}]</strong> {log['message']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No activity logs yet")


if __name__ == "__main__":
    main()