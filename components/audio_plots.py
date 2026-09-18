"""
High-performance dark-themed audio visualizers built with Matplotlib and Librosa.
Matched to the StorageOpt dark obsidian UI palette (#0C0D11, #16171D, #23252E).
All HTML outputs are unindented (column 0) to avoid Markdown code-block interpretation.
"""

import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import librosa
import librosa.display

# Set dark matplotlib rcParams
plt.rcParams['figure.facecolor'] = '#16171D'
plt.rcParams['axes.facecolor'] = '#16171D'
plt.rcParams['axes.edgecolor'] = '#23252E'
plt.rcParams['axes.labelcolor'] = '#8B949E'
plt.rcParams['xtick.color'] = '#6E7681'
plt.rcParams['ytick.color'] = '#6E7681'
plt.rcParams['grid.color'] = '#23252E'
plt.rcParams['grid.alpha'] = 0.5
plt.rcParams['text.color'] = '#E6EDF3'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']


def clean_html(html_str: str) -> str:
    return "\n".join(line.strip() for line in html_str.strip().split("\n") if line.strip())


def plot_waveform(y: np.ndarray, sr: int, title: str = "Audio Waveform (Amplitude vs. Time)") -> plt.Figure:
    """
    Renders an amplitude vs time waveform on a sleek dark canvas.
    """
    fig, ax = plt.subplots(figsize=(10, 2.7), dpi=120)
    fig.patch.set_facecolor('#16171D')
    ax.set_facecolor('#111217')

    time_axis = np.linspace(0, len(y) / sr, num=len(y))
    
    # Plot glow effect
    ax.plot(time_axis, y, color='#F59E0B', alpha=0.3, linewidth=2.0)
    # Main signal line
    ax.plot(time_axis, y, color='#FBBF24', linewidth=1.0, alpha=0.95)
    
    # Fill under curve for modern look
    ax.fill_between(time_axis, y, 0, color='#F59E0B', alpha=0.12)

    ax.axhline(0, color='#2F333D', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.set_title(title, fontsize=11, fontweight=700, pad=10, color='#E6EDF3', loc='left')
    ax.set_xlabel("Time (seconds)", fontsize=9, labelpad=6, color='#8B949E')
    ax.set_ylabel("Amplitude", fontsize=9, labelpad=6, color='#8B949E')
    
    ax.grid(True, linestyle=':', alpha=0.4, color='#23252E')
    ax.set_xlim(0, len(y) / sr)
    
    for spine in ax.spines.values():
        spine.set_color('#23252E')
        spine.set_linewidth(1.0)
        
    plt.tight_layout()
    return fig


def plot_stft_spectrogram(y: np.ndarray, sr: int, n_fft: int = 2048, hop_length: int = 512, title: str = "STFT Spectrogram (dB-scaled)") -> plt.Figure:
    """
    Computes STFT and renders a dB-scaled linear frequency spectrogram with magma colormap.
    """
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=120)
    fig.patch.set_facecolor('#16171D')
    ax.set_facecolor('#111217')

    img = librosa.display.specshow(
        S_db,
        sr=sr,
        hop_length=hop_length,
        x_axis='time',
        y_axis='linear',
        cmap='magma',
        ax=ax
    )

    ax.set_title(title, fontsize=11, fontweight=700, pad=10, color='#E6EDF3', loc='left')
    ax.set_xlabel("Time (seconds)", fontsize=9, color='#8B949E')
    ax.set_ylabel("Frequency (Hz)", fontsize=9, color='#8B949E')

    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB", pad=0.02)
    cbar.ax.yaxis.set_tick_params(color='#6E7681', labelsize=8)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#8B949E')
    cbar.outline.set_edgecolor('#23252E')
    cbar.set_label("Magnitude (dB)", color='#8B949E', fontsize=8, labelpad=8)

    for spine in ax.spines.values():
        spine.set_color('#23252E')

    plt.tight_layout()
    return fig


def plot_mel_spectrogram(y: np.ndarray, sr: int, n_mels: int = 128, fmax: int = 8000, title: str = "Mel Spectrogram (Perceptually-scaled)") -> plt.Figure:
    """
    Computes Mel-frequency spectrogram and renders with inferno colormap.
    """
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, fmax=fmax)
    S_dB = librosa.power_to_db(S, ref=np.max)

    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=120)
    fig.patch.set_facecolor('#16171D')
    ax.set_facecolor('#111217')

    img = librosa.display.specshow(
        S_dB,
        sr=sr,
        x_axis='time',
        y_axis='mel',
        fmax=fmax,
        cmap='inferno',
        ax=ax
    )

    ax.set_title(title, fontsize=11, fontweight=700, pad=10, color='#E6EDF3', loc='left')
    ax.set_xlabel("Time (seconds)", fontsize=9, color='#8B949E')
    ax.set_ylabel("Mel Frequency", fontsize=9, color='#8B949E')

    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB", pad=0.02)
    cbar.ax.yaxis.set_tick_params(color='#6E7681', labelsize=8)
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#8B949E')
    cbar.outline.set_edgecolor('#23252E')
    cbar.set_label("Energy (dB)", color='#8B949E', fontsize=8, labelpad=8)

    for spine in ax.spines.values():
        spine.set_color('#23252E')

    plt.tight_layout()
    return fig


def render_db_gauge_html(current_db: float, peak_db: float = 94.2) -> str:
    """
    Generates a segmented dark-themed decibel meter with safety thresholds.
    """
    pct = max(0, min(100, (current_db - 20) / (120 - 20) * 100))
    
    if current_db < 70:
        status_text = "NORMAL AMBIENT"
        color_class = "seg-green"
        text_color = "#34D399"
        badge_class = "badge-green"
    elif current_db <= 85:
        status_text = "MODERATE NOISE"
        color_class = "seg-amber"
        text_color = "#FBBF24"
        badge_class = "badge-amber"
    else:
        status_text = "HAZARDOUS (OSHA WARNING)"
        color_class = "seg-red"
        text_color = "#F87171"
        badge_class = "badge-red"

    raw = f"""
<div class="storage-card" style="margin-bottom: 1rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
<div>
<span class="volume-sublabel">REAL-TIME SENSOR METRIC</span>
<div style="display: flex; align-items: baseline; gap: 0.6rem; margin-top: 0.2rem;">
<span style="font-size: 2.2rem; font-weight: 800; color: {text_color};">{current_db:.1f}</span>
<span style="font-size: 1.1rem; font-weight: 600; color: #8B949E;">dB SPL</span>
</div>
</div>
<div style="text-align: right;">
<span class="badge-pill {badge_class}">{status_text}</span>
<div style="font-size: 0.76rem; color: #8B949E; margin-top: 0.4rem;">
Peak Session: <b style="color: #E6EDF3;">{peak_db:.1f} dB</b>
</div>
</div>
</div>
<div style="height: 10px; border-radius: 5px; background: #23252E; width: 100%; position: relative; overflow: hidden; margin: 0.75rem 0 0.5rem 0;">
<div style="position: absolute; left: 0; top: 0; height: 100%; width: {pct}%; border-radius: 5px;" class="{color_class}"></div>
</div>
<div style="display: flex; justify-content: space-between; font-size: 0.70rem; color: #6E7681; font-family: 'JetBrains Mono', monospace;">
<span>20 dB (Whisper)</span>
<span>70 dB (Office)</span>
<span style="color: #F59E0B;">85 dB (OSHA Limit)</span>
<span style="color: #EF4444;">120 dB (Pain Threshold)</span>
</div>
</div>
"""
    return clean_html(raw)


def render_confidence_breakdown_html(predictions: list) -> str:
    """
    Renders top prediction probabilities as horizontal glowing bars.
    """
    items_html = ""
    colors = ['#F59E0B', '#38BDF8', '#A855F7', '#10B981', '#64748B']
    
    for idx, p in enumerate(predictions[:4]):
        conf = p.get('confidence', 0.0)
        c_name = p.get('class', 'Unknown')
        pct_val = conf * 100 if conf <= 1.0 else conf
        bar_color = colors[idx % len(colors)]
        
        items_html += f"""
<div style="margin-bottom: 0.75rem;">
<div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
<span style="font-weight: 600; color: #E6EDF3;">{c_name}</span>
<span style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: {bar_color};">{pct_val:.1f}%</span>
</div>
<div style="height: 6px; border-radius: 3px; background: #23252E; width: 100%; overflow: hidden;">
<div style="height: 100%; width: {pct_val}%; background: {bar_color}; border-radius: 3px;"></div>
</div>
</div>
"""
        
    raw = f"""
<div class="storage-card">
<div class="volume-sublabel" style="margin-bottom: 0.75rem;">CLASSIFICATION PROBABILITIES (TOP-4)</div>
{items_html}
</div>
"""
    return clean_html(raw)
