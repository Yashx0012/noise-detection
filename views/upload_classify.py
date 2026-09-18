"""
Upload & Classify View:
- File upload widget calling POST /upload
- 1-Click sample sound generator presets
- Waveform plot (amplitude vs time)
- STFT Spectrogram (dB-scaled, linear freq)
- Mel Spectrogram (perceptually-scaled)
- Predicted class, confidence gauge, and dB level
"""

import streamlit as st
import librosa
import numpy as np
import io
import soundfile as sf
import matplotlib.pyplot as plt
from components.audio_plots import (
    plot_waveform,
    plot_stft_spectrogram,
    plot_mel_spectrogram,
    render_confidence_breakdown_html,
    render_db_gauge_html
)
from components.ui_cards import clean_html
from services.mock_data import generate_synthetic_audio, audio_to_wav_bytes

def render_upload_classify_view(api_client):
    st.html(clean_html("""
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Upload & Classify Audio</div>
<div style="font-size: 0.82rem; color: #8B949E; margin-top: 0.2rem;">
Upload acoustic recordings for edge ONNX inference. Dispatches <code style="color: #F59E0B; background: #1B1C23; padding: 2px 6px; border-radius: 4px;">POST /upload</code> and computes spectral decomposition.
</div>
</div>
"""))

    col_input, col_result = st.columns([1.0, 1.2], gap="large")

    # Audio State in Session
    if "current_audio_y" not in st.session_state:
        y, sr, pred, peak = generate_synthetic_audio("Siren", duration_sec=3.0)
        st.session_state.current_audio_y = y
        st.session_state.current_audio_sr = sr
        st.session_state.current_filename = "demo_emergency_siren.wav"
        st.session_state.current_upload_res = api_client.upload_audio(audio_to_wav_bytes(y, sr), "demo_emergency_siren.wav")

    with col_input:
        st.html(clean_html("""
<div class="storage-card">
<div class="volume-sublabel">FILE INGESTION</div>
"""))
        
        uploaded_file = st.file_uploader(
            "Select Audio File (WAV, MP3, FLAC, OGG)",
            type=["wav", "mp3", "flac", "ogg"],
            help="File will be transmitted to the Go backend /upload endpoint."
        )

        st.html(clean_html("""
<div style="margin: 1rem 0 0.5rem 0; font-size: 0.76rem; font-weight: 700; color: #8B949E; text-transform: uppercase;">
Or Quick-Load Acoustic Benchmark Sample:
</div>
"""))

        preset_cols = st.columns(3)
        with preset_cols[0]:
            if st.button("🚨 Siren", use_container_width=True):
                y, sr, _, _ = generate_synthetic_audio("Siren", 3.0)
                st.session_state.current_audio_y = y
                st.session_state.current_audio_sr = sr
                st.session_state.current_filename = "benchmark_siren_wail.wav"
                st.session_state.current_upload_res = api_client.upload_audio(audio_to_wav_bytes(y, sr), "benchmark_siren_wail.wav")
                st.rerun()

        with preset_cols[1]:
            if st.button("⚡ Jackhammer", use_container_width=True):
                y, sr, _, _ = generate_synthetic_audio("Jackhammer", 3.0)
                st.session_state.current_audio_y = y
                st.session_state.current_audio_sr = sr
                st.session_state.current_filename = "benchmark_jackhammer_impact.wav"
                st.session_state.current_upload_res = api_client.upload_audio(audio_to_wav_bytes(y, sr), "benchmark_jackhammer_impact.wav")
                st.rerun()

        with preset_cols[2]:
            if st.button("🔩 Drilling", use_container_width=True):
                y, sr, _, _ = generate_synthetic_audio("Drilling", 3.0)
                st.session_state.current_audio_y = y
                st.session_state.current_audio_sr = sr
                st.session_state.current_filename = "benchmark_drilling_rotary.wav"
                st.session_state.current_upload_res = api_client.upload_audio(audio_to_wav_bytes(y, sr), "benchmark_drilling_rotary.wav")
                st.rerun()

        preset_cols2 = st.columns(2)
        with preset_cols2[0]:
            if st.button("🎺 Car Horn", use_container_width=True):
                y, sr, _, _ = generate_synthetic_audio("Horn", 3.0)
                st.session_state.current_audio_y = y
                st.session_state.current_audio_sr = sr
                st.session_state.current_filename = "benchmark_traffic_horn.wav"
                st.session_state.current_upload_res = api_client.upload_audio(audio_to_wav_bytes(y, sr), "benchmark_traffic_horn.wav")
                st.rerun()

        with preset_cols2[1]:
            if st.button("🚚 Diesel Idle", use_container_width=True):
                y, sr, _, _ = generate_synthetic_audio("Engine", 3.0)
                st.session_state.current_audio_y = y
                st.session_state.current_audio_sr = sr
                st.session_state.current_filename = "benchmark_engine_diesel.wav"
                st.session_state.current_upload_res = api_client.upload_audio(audio_to_wav_bytes(y, sr), "benchmark_engine_diesel.wav")
                st.rerun()

        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            try:
                y, sr = librosa.load(io.BytesIO(bytes_data), sr=22050)
                st.session_state.current_audio_y = y
                st.session_state.current_audio_sr = sr
                st.session_state.current_filename = uploaded_file.name
                st.session_state.current_upload_res = api_client.upload_audio(bytes_data, uploaded_file.name)
            except Exception as e:
                st.error(f"Error decoding audio: {str(e)}")

        if "current_audio_y" in st.session_state:
            st.html(clean_html("""
<div style="margin-top: 1.25rem;"><span class="volume-sublabel">AUDIO PLAYBACK</span></div>
"""))
            wav_bytes = audio_to_wav_bytes(st.session_state.current_audio_y, st.session_state.current_audio_sr)
            st.audio(wav_bytes, format="audio/wav")
            
            st.html(clean_html(f"""
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #8B949E; margin-top: 0.4rem;">
Loaded: <span style="color: #E6EDF3;">{st.session_state.current_filename}</span> • 
Sample Rate: <span style="color: #F59E0B;">{st.session_state.current_audio_sr} Hz</span> • 
Duration: <span style="color: #10B981;">{len(st.session_state.current_audio_y)/st.session_state.current_audio_sr:.2f}s</span>
</div>
</div>
"""))

    with col_result:
        res = st.session_state.get("current_upload_res", {})
        pred_class = res.get("class", "Unknown")
        confidence = res.get("confidence", 0.0)
        db_level = res.get("dB", 0.0)
        probs = res.get("probabilities", [])

        # Live dB Gauge
        st.html(render_db_gauge_html(db_level, peak_db=db_level + 3.2))

        # Top Predicted Class Card
        conf_pct = confidence * 100 if confidence <= 1.0 else confidence
        st.html(clean_html(f"""
<div class="storage-card" style="margin-bottom: 1rem; border-left: 4px solid #F59E0B;">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div>
<span class="volume-sublabel">PRIMARY CLASSIFICATION RESULT</span>
<div style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin-top: 0.25rem;">
{pred_class}
</div>
</div>
<div style="text-align: right;">
<span class="badge-pill badge-green" style="font-size: 0.82rem; padding: 0.3rem 0.7rem;">
{conf_pct:.1f}% Confidence
</span>
<div style="font-size: 0.72rem; color: #8B949E; margin-top: 0.35rem;">
Go/ONNX Endpoint: POST /upload
</div>
</div>
</div>
</div>
"""))

        # Top probabilities breakdown
        if probs:
            st.html(render_confidence_breakdown_html(probs))

    # Visualization Section
    st.html(clean_html("""
<div style="margin-top: 1.5rem; margin-bottom: 0.75rem;">
<div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">Acoustic Signal Deconstruction</div>
<div style="font-size: 0.76rem; color: #8B949E;">Real-time waveform oscillogram and dual spectral representations (STFT & Perceptual Mel-scale).</div>
</div>
"""))

    if "current_audio_y" in st.session_state:
        y = st.session_state.current_audio_y
        sr = st.session_state.current_audio_sr

        fig_wave = plot_waveform(y, sr, title=f"Waveform Oscillogram (Amplitude vs. Time) — {st.session_state.current_filename}")
        st.pyplot(fig_wave, use_container_width=True)
        plt.close(fig_wave)

        spec_col1, spec_col2 = st.columns(2, gap="medium")
        with spec_col1:
            fig_stft = plot_stft_spectrogram(y, sr, title="STFT Spectrogram (dB-scaled, Linear Freq)")
            st.pyplot(fig_stft, use_container_width=True)
            plt.close(fig_stft)

        with spec_col2:
            fig_mel = plot_mel_spectrogram(y, sr, title="Mel Spectrogram (Perceptually-scaled Mel-scale)")
            st.pyplot(fig_mel, use_container_width=True)
            plt.close(fig_mel)

    with st.expander("🔍 View Raw API Contract Response (POST /upload JSON)"):
        st.json(res)
