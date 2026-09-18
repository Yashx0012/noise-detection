"""
Realistic synthetic audio generator and mock data layer.
Enables instant demonstration of Waveform, STFT Spectrogram, and Mel Spectrogram
even before connecting to the live Go backend.
"""

import numpy as np
import io
import soundfile as sf
from datetime import datetime, timedelta

ACOUSTIC_CLASSES = [
    "Siren (Emergency)",
    "Jackhammer (Construction)",
    "Drilling Machine",
    "Engine Idling",
    "Car Horn",
    "Dog Bark",
    "Street Music",
    "Air Conditioner",
    "Gunshot / Blast",
    "Children Playing"
]

def generate_synthetic_audio(sound_type: str = "Siren", duration_sec: float = 3.0, sr: int = 22050) -> tuple[np.ndarray, int, str, float]:
    """
    Synthesizes acoustic waveform data for realistic demoing of STFT and Mel spectrograms.
    Returns: (audio_array, sample_rate, predicted_class, peak_db)
    """
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    
    if "Siren" in sound_type:
        # Frequency modulation between 650 Hz and 1100 Hz
        mod_freq = 1.2 # wail cycle
        carrier = 850 + 250 * np.sin(2 * np.pi * mod_freq * t)
        phase = 2 * np.pi * np.cumsum(carrier) / sr
        signal = 0.65 * np.sin(phase) + 0.15 * np.sin(2 * phase)
        # Add slight street noise
        noise = np.random.normal(0, 0.04, len(t))
        y = signal + noise
        pred_class = "Siren (Emergency)"
        peak_db = 91.4

    elif "Jackhammer" in sound_type:
        # Periodic sharp impulses with high frequency resonance (10-15 Hz strike rate)
        strike_rate = 14.0 # strikes per second
        strike_env = (np.sin(2 * np.pi * strike_rate * t) > 0.85).astype(float)
        # Resonant ring per strike
        resonance = np.sin(2 * np.pi * 320 * t) * np.exp(-15 * (t % (1.0 / strike_rate)))
        noise_burst = np.random.normal(0, 0.25, len(t)) * strike_env
        y = 0.5 * resonance * strike_env + noise_burst
        pred_class = "Jackhammer (Construction)"
        peak_db = 98.7

    elif "Drilling" in sound_type:
        # High-pitched whine + metal friction harmonic
        drill_tone = 0.4 * np.sin(2 * np.pi * 1850 * t) + 0.2 * np.sin(2 * np.pi * 3700 * t)
        flutter = 1.0 + 0.2 * np.sin(2 * np.pi * 25 * t)
        chatter = np.random.normal(0, 0.12, len(t))
        y = (drill_tone * flutter) + chatter
        pred_class = "Drilling Machine"
        peak_db = 88.2

    elif "Engine" in sound_type:
        # Low frequency diesel hum (60 Hz + harmonics 120, 180, 240)
        rpm_freq = 45.0
        y = (0.5 * np.sin(2 * np.pi * rpm_freq * t) +
             0.3 * np.sin(2 * np.pi * 2 * rpm_freq * t) +
             0.15 * np.sin(2 * np.pi * 3 * rpm_freq * t) +
             np.random.normal(0, 0.08, len(t)))
        pred_class = "Engine Idling"
        peak_db = 76.5

    elif "Horn" in sound_type:
        # Two-tone car horn (dual tone ~440 Hz + 550 Hz)
        horn_active = ((t > 0.4) & (t < 1.4)) | ((t > 1.8) & (t < 2.6))
        tone = (0.5 * np.sin(2 * np.pi * 420 * t) + 0.5 * np.sin(2 * np.pi * 520 * t)) * horn_active
        noise = np.random.normal(0, 0.03, len(t))
        y = tone + noise
        pred_class = "Car Horn"
        peak_db = 93.1

    else:
        # Ambient Street noise / pink noise
        white = np.random.normal(0, 0.15, len(t))
        # Simple lowpass filter
        y = np.convolve(white, np.ones(10)/10, mode='same')
        pred_class = "Street Noise / Ambient"
        peak_db = 64.8

    # Normalize to [-1.0, 1.0]
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = (y / max_val) * 0.92

    return y.astype(np.float32), sr, pred_class, peak_db


def audio_to_wav_bytes(y: np.ndarray, sr: int) -> bytes:
    """Converts numpy audio array to in-memory WAV bytes."""
    buf = io.BytesIO()
    sf.write(buf, y, sr, format='WAV')
    buf.seek(0)
    return buf.read()


def get_mock_history_records(count: int = 15) -> list[dict]:
    """Generates mock history prediction rows matching Image 1 & 3."""
    samples = [
        {"cat": "Jackhammer (Construction)", "db": "96.4 dB", "conf": 0.99, "path": "/audio/stream/chunk_20260914_0812.wav"},
        {"cat": "Jackhammer (Construction)", "db": "97.1 dB", "conf": 0.98, "path": "/audio/stream/chunk_20260914_0813.wav"},
        {"cat": "Siren (Emergency)", "db": "91.8 dB", "conf": 0.99, "path": "/audio/uploads/rec_emergency_wail_01.wav"},
        {"cat": "Car Horn", "db": "93.5 dB", "conf": 0.95, "path": "/audio/stream/chunk_20260914_0820.wav"},
        {"cat": "Drilling Machine", "db": "88.7 dB", "conf": 0.92, "path": "/audio/uploads/factory_drilling_core.wav"},
        {"cat": "Engine Idling", "db": "74.2 dB", "conf": 0.89, "path": "/audio/stream/chunk_20260914_0825.wav"},
        {"cat": "Dog Bark", "db": "82.1 dB", "conf": 0.86, "path": "/audio/stream/chunk_20260914_0829.wav"},
        {"cat": "Street Music", "db": "68.3 dB", "conf": 0.94, "path": "/audio/uploads/busker_acoustic_session.wav"},
        {"cat": "Air Conditioner", "db": "58.2 dB", "conf": 0.97, "path": "/audio/stream/chunk_20260914_0835.wav"},
        {"cat": "Siren (Emergency)", "db": "89.4 dB", "conf": 0.96, "path": "/audio/stream/chunk_20260914_0841.wav"},
        {"cat": "Drilling Machine", "db": "87.9 dB", "conf": 0.91, "path": "/audio/stream/chunk_20260914_0848.wav"},
        {"cat": "Jackhammer (Construction)", "db": "98.2 dB", "conf": 0.99, "path": "/audio/uploads/excavator_drill_burst.wav"},
    ]
    
    rows = []
    base_time = datetime.now()
    for i, s in enumerate(samples[:count]):
        t_stamp = (base_time - timedelta(minutes=i * 14)).strftime("%b %d, %I:%M %p")
        rows.append({
            "id": f"rec_{i+1:04d}",
            "confidence": s["conf"],
            "category": s["cat"],
            "path": s["path"],
            "db": s["db"],
            "time": t_stamp,
            "raw_db": float(s["db"].replace(" dB", ""))
        })
    return rows


def get_mock_category_chips() -> list[dict]:
    """Generates the extension/category chips matching Image 1."""
    return [
        {"tag": "JACKHAMMER", "count": "3,482 frames", "meta": "96.5 dB (31.2%)"},
        {"tag": "SIREN", "count": "2,190 frames", "meta": "90.2 dB (19.6%)"},
        {"tag": "DRILLING", "count": "1,840 frames", "meta": "87.4 dB (16.5%)"},
        {"tag": "CAR HORN", "count": "1,215 frames", "meta": "92.8 dB (10.9%)"},
        {"tag": "ENGINE IDLE", "count": "1,040 frames", "meta": "75.1 dB (9.3%)"},
        {"tag": "DOG BARK", "count": "720 frames", "meta": "81.6 dB (6.5%)"},
        {"tag": "STREET MUSIC", "count": "450 frames", "meta": "69.4 dB (4.0%)"},
        {"tag": "AMBIENT HVAC", "count": "220 frames", "meta": "57.8 dB (2.0%)"}
    ]


def get_hourly_noise_distribution() -> dict:
    """Returns average dB level and primary noise source per hour (00:00 - 23:00)."""
    hours = [f"{h:02d}:00" for h in range(24)]
    # Typical city profile: quiet at night, peaks during 8am-6pm rush & construction
    db_values = [
        45.2, 44.0, 43.1, 42.8, 46.5, 54.2, 
        68.4, 78.1, 84.6, 88.2, 86.5, 83.1,
        80.4, 85.9, 87.4, 86.0, 81.5, 76.2,
        71.4, 66.8, 62.1, 57.5, 51.0, 48.2
    ]
    sources = [
        "Air Conditioner", "Air Conditioner", "Ambient", "Ambient", "Engine Idling", "Traffic / Horn",
        "Traffic / Horn", "Traffic / Horn", "Jackhammer", "Drilling Machine", "Jackhammer", "Traffic",
        "Traffic", "Drilling Machine", "Jackhammer", "Jackhammer", "Traffic / Horn", "Traffic / Horn",
        "Street Music", "Street Music", "Engine Idling", "Dog Bark", "Air Conditioner", "Air Conditioner"
    ]
    return {"hours": hours, "db": db_values, "sources": sources}


def get_weekly_db_trend() -> dict:
    """Returns 7-day average dB levels and daily peak levels."""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    avg_db = [76.4, 78.2, 81.5, 79.8, 83.4, 71.2, 65.8]
    peak_db = [94.2, 96.8, 98.7, 95.1, 99.4, 88.0, 79.5]
    return {"days": days, "avg_db": avg_db, "peak_db": peak_db}
