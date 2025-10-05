# ================================================================
# Rehcura - Hackathon Enhanced Edition (Fixed wordcloud + audio IO)
# ================================================================

import os, io, re, json, tempfile
import pandas as pd
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
import speech_recognition as sr
from pydub import AudioSegment
from datetime import datetime
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from gtts import gTTS
import gradio as gr

print("🚀 Rehcura Hackathon Edition launched successfully!")

# -------------------------------------------------------------
# Constants (unchanged)
# -------------------------------------------------------------
TOPICS = ["Cardiology", "Pulmonology", "Neurology", "Gastroenterology", "Orthopedics", "General Medicine"]

TOPIC_KEYWORDS = {
    "Cardiology": ["chest pain", "myocardial infarction", "hypertension", "bradycardia", "tachycardia", "ecg", "ekg"],
    "Pulmonology": ["shortness of breath", "dyspnea", "cough", "o2 sat", "cxr", "airway"],
    "Neurology": ["syncope", "headache", "altered mental status", "stroke", "seizure", "neurological"],
    "Gastroenterology": ["nausea", "vomiting", "abdominal pain", "gi bleed"],
    "Orthopedics": ["fracture", "pain", "swelling", "edema"],
    "General Medicine": ["fever", "infection", "checkup", "routine", "stable"]
}

URGENT_KEYWORDS = {
    "critical": ["unresponsive", "cardiac arrest", "shock", "severe pain", "respiratory distress"],
    "high": ["dyspnea", "hypoxia", "bradycardia", "tachycardia", "bleeding"],
    "moderate": ["pain", "fever", "infection", "weakness", "vomiting"],
    "low": ["checkup", "routine", "follow up", "stable"]
}

SENTIMENT_KEYWORDS = {
    "POSITIVE": ["stable", "better", "improving", "no complaint", "routine"],
    "NEGATIVE": ["pain", "severe", "critical", "worse", "unresponsive", "bleeding"]
}

JARGON_DICT = {
    "dyspnea": "shortness of breath",
    "tachycardia": "fast heart rate",
    "bradycardia": "slow heart rate",
    "myocardial infarction": "heart attack",
    "hypertension": "high blood pressure",
    "hypotension": "low blood pressure",
    "edema": "swelling",
    "febrile": "has a fever",
    "afebrile": "no fever",
    "hemoptysis": "coughing up blood",
    "syncope": "fainting",
    "nausea": "feeling sick",
    "vomiting": "throwing up",
    "altered mental status": "confused",
    "O2 sat": "oxygen saturation",
    "ECG": "electrocardiogram",
    "EKG": "electrocardiogram"
}

ACRONYM_DICT = {
    "htn": "hypertension",
    "sob": "shortness of breath",
    "cp": "chest pain",
    "rrr": "regular rate and rhythm",
    "hr": "heart rate",
    "bp": "blood pressure",
    "gi": "gastrointestinal"
}

# -------------------------------------------------------------
# Helper Functions (fixed wordcloud -> filepath; audio handling)
# -------------------------------------------------------------
def simplify_jargon(text):
    for term, simple in {**JARGON_DICT, **ACRONYM_DICT}.items():
        text = re.sub(r'\b' + re.escape(term) + r'\b', simple, text, flags=re.IGNORECASE)
    return text

def compute_urgency_score(text, high_threshold=70, medium_threshold=30):
    score = 0
    for k_list in ["critical", "high", "moderate", "low"]:
        for k in URGENT_KEYWORDS[k_list]:
            if k in text.lower():
                score += {"critical": 50, "high": 20, "moderate": 5, "low": 1}[k_list]
    score = min(score, 100)
    level = "High" if score >= high_threshold else "Medium" if score >= medium_threshold else "Low"
    return {"score": score, "level": level}

def extract_key_phrases(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    words = [w for w in words if w not in ENGLISH_STOP_WORDS]
    counts = Counter(words)
    return ", ".join([w for w, _ in counts.most_common(5)])

def generate_action_plan(level, topic):
    if level == "High":
        return "🚨 Immediate senior review and life support measures."
    elif level == "Medium":
        return f"🩺 Urgent: Notify {topic} team and order relevant tests."
    else:
        return "✅ Routine: Continue monitoring or plan discharge."

def generate_clinical_summary(topic, urgency, sentiment):
    return (
        f"Patient presents with symptoms suggestive of {topic.lower()} involvement. "
        f"The clinical condition is assessed as {urgency.lower()} urgency with a {sentiment.lower()} outlook. "
        f"Recommended management: {generate_action_plan(urgency, topic)}"
    )

def make_wordcloud_image_file(text):
    """
    Create a wordcloud image file and return its filepath (not BytesIO).
    Gradio Image component can accept filepaths when type='filepath'.
    """
    if not text or not text.strip():
        return None
    try:
        wc = WordCloud(width=600, height=300, background_color="white").generate(text)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.close()
        wc.to_file(tmp.name)
        return tmp.name
    except Exception as e:
        print("WordCloud generation failed:", e)
        return None

def transcribe_audio_file(audio_input):
    """
    Accepts either a filepath (string) or a dict returned by Gradio audio widget.
    Returns transcribed text or a helpful failure message.
    """
    if audio_input is None:
        return "No audio provided."
    # Gradio can return a dict like {'name': '/tmp/xxx.wav'} or a filepath string.
    audio_path = None
    if isinstance(audio_input, str):
        audio_path = audio_input
    else:
        # try common dict keys
        if isinstance(audio_input, dict):
            audio_path = audio_input.get("name") or audio_input.get("tempfile")
        # some versions return a tuple (sr, np.array) - skip that complexity for now
    if not audio_path:
        return "Unable to read uploaded audio file."
    r = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(audio_path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio.export(tmp.name, format="wav")
            with sr.AudioFile(tmp.name) as src:
                audio_data = r.record(src)
        return r.recognize_google(audio_data)
    except Exception as e:
        print("Audio transcription failed:", e)
        return "Transcription unavailable or unintelligible."

def speak_text(text):
    """
    Convert text to speech with gTTS, save temp mp3 path and return it.
    Gradio Audio will play this file when returned with type='filepath'.
    """
    try:
        tts = gTTS(text)
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        tts.save(temp_path)
        return temp_path
    except Exception as e:
        print("TTS failed:", e)
        return None

# -------------------------------------------------------------
# Core Processing Logic (uses new make_wordcloud_image_file)
# -------------------------------------------------------------
def process_note(note_text, high_thresh, medium_thresh):
    note_text = simplify_jargon(note_text)
    urgency = compute_urgency_score(note_text, high_thresh, medium_thresh)
    sentiment = "POSITIVE" if any(k in note_text.lower() for k in SENTIMENT_KEYWORDS["POSITIVE"]) else \
                "NEGATIVE" if any(k in note_text.lower() for k in SENTIMENT_KEYWORDS["NEGATIVE"]) else "NEUTRAL"
    topic = next((t for t, kws in TOPIC_KEYWORDS.items() if any(k in note_text.lower() for k in kws)), "General Medicine")
    key_phrases = extract_key_phrases(note_text)
    summary = f"This note describes a patient with possible {topic.lower()} concerns and {sentiment.lower()} sentiment."
    action_plan = generate_action_plan(urgency["level"], topic)
    clinical_summary = generate_clinical_summary(topic, urgency["level"], sentiment)
    wc_path = make_wordcloud_image_file(note_text)
    return summary, urgency["level"], urgency["score"], action_plan, wc_path, sentiment, topic, key_phrases, clinical_summary

# -------------------------------------------------------------
# Gradio Interface (Image and Audio outputs set to filepath)
# -------------------------------------------------------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🩺 **Rehcura - Hackathon Edition**")
    gr.Markdown("Lightweight Clinical Note Triage + Voice + Analytics Dashboard")

    high_thresh = gr.Slider(50, 90, 70, step=1, label="High Urgency Threshold")
    medium_thresh = gr.Slider(10, 50, 30, step=1, label="Medium Urgency Threshold")

    with gr.Tab("🧾 Patient Input"):
        note_input = gr.Textbox(lines=6, label="Enter Clinical Note")
        analyze_btn = gr.Button("Analyze Note", variant="primary")
        summary_out = gr.Textbox(label="AI Summary")
        urgency_out = gr.Textbox(label="Urgency Level")
        score_out = gr.Number(label="Urgency Score")
        action_out = gr.Textbox(label="Action Plan")
        clinical_out = gr.Textbox(label="Clinical Summary")
        # Tell Gradio that this Image will be a filepath
        wc_img = gr.Image(label="Word Cloud", type="filepath")
        sentiment_out = gr.Textbox(label="Sentiment")
        topic_out = gr.Textbox(label="Topic")
        phrases_out = gr.Textbox(label="Key Phrases")
        # Tell Gradio that this Audio will be a filepath to an mp3
        audio_out = gr.Audio(label="AI Voice Reply", type="filepath")

        def handle_analyze(note, high_thresh, medium_thresh):
            summary, urgency, score, plan, wc_path, sentiment, topic, phrases, clinical = process_note(note, high_thresh, medium_thresh)
            voice_path = speak_text(clinical)  # returns mp3 filepath or None
            return summary, urgency, score, plan, clinical, wc_path, sentiment, topic, phrases, voice_path

        analyze_btn.click(
            handle_analyze,
            inputs=[note_input, high_thresh, medium_thresh],
            outputs=[summary_out, urgency_out, score_out, action_out, clinical_out, wc_img, sentiment_out, topic_out, phrases_out, audio_out]
        )

    with gr.Tab("🎤 Voice Reports"):
        audio_input = gr.Audio(label="Record or Upload Audio", type="filepath")
        run_audio = gr.Button("Transcribe & Analyze")
        transcribed_out = gr.Textbox(label="Transcribed Text")
        result_out = gr.Textbox(label="Summary")

        def handle_audio(audio, high_thresh, medium_thresh):
            txt = transcribe_audio_file(audio)
            summary, level, score, plan, _, sentiment, topic, _, clinical = process_note(txt, high_thresh, medium_thresh)
            return txt, f"{clinical}\nUrgency: {level} ({score})\nSentiment: {sentiment}\nTopic: {topic}"

        run_audio.click(handle_audio, inputs=[audio_input, high_thresh, medium_thresh], outputs=[transcribed_out, result_out])

    with gr.Tab("📈 Analytics Dashboard"):
        uploaded = gr.File(label="Upload CSV File")
        graph_output = gr.Plot(label="Data Visualizer")
        viz_btn = gr.Button("Visualize Data")

        def visualize_csv(file):
            if file is None:
                return px.scatter(title="No file uploaded")
            try:
                df = pd.read_csv(file.name)
            except Exception as e:
                print("CSV read failed:", e)
                return px.scatter(title="Failed to read CSV")
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title="Quick Data Visualization")
            elif len(numeric_cols) == 1:
                fig = px.histogram(df, x=numeric_cols[0], title="Single Column Distribution")
            else:
                # fallback: show first string column counts
                str_cols = df.select_dtypes(include="object").columns
                if len(str_cols) > 0:
                    counts = df[str_cols[0]].value_counts().reset_index()
                    counts.columns = [str_cols[0], "count"]
                    fig = px.bar(counts, x=str_cols[0], y="count", title=f"Counts of {str_cols[0]}")
                else:
                    fig = px.scatter(title="No plottable columns found")
            return fig

        viz_btn.click(visualize_csv, inputs=[uploaded], outputs=[graph_output])

demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
