"""
Insights View:
- Aggregated stats: Most common noise source by hour of day (00:00 - 23:00)
- Average dB trend over the week (7-day timeline with OSHA threshold)
- Statistical summaries and noise distribution
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from services.mock_data import get_hourly_noise_distribution, get_weekly_db_trend
from components.ui_cards import render_metric_cards_row, clean_html

def render_insights_view(api_client):
    st.html(clean_html("""
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Acoustic Intelligence & Insights</div>
<div style="font-size: 0.82rem; color: #8B949E; margin-top: 0.2rem;">
Aggregated time-series patterns, diurnal noise cycles, and regulatory exposure compliance.
</div>
</div>
"""))

    insight_cards = [
        {
            "label": "PEAK NOISE WINDOW",
            "val": "09:00 - 15:00",
            "sub": "Primary source: Jackhammer (98.7 dB)",
            "type": "yellow"
        },
        {
            "label": "QUIETEST PERIOD",
            "val": "03:00 - 05:00",
            "sub": "Average baseline: 42.8 dB SPL",
            "type": "blue"
        },
        {
            "label": "OSHA COMPLIANCE",
            "val": "94.6 %",
            "sub": "Exceedances logged: 12 events",
            "type": "green"
        },
        {
            "label": "TOP NOISE DRIVER",
            "val": "CONSTRUCTION",
            "sub": "47.7% of total acoustic energy",
            "type": "orange"
        }
    ]
    st.html(render_metric_cards_row(insight_cards))

    # Section 1: 24-Hour Diurnal Noise Profile
    st.html(clean_html("""
<div class="storage-card" style="margin-bottom: 1.5rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
<div>
<div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">Hourly Noise Source & Decibel Profile (24h)</div>
<div style="font-size: 0.74rem; color: #8B949E; margin-top: 0.2rem;">
Average decibel levels and predominant classification signatures mapped across each hour of the day.
</div>
</div>
<span class="badge-pill badge-amber">Diurnal Heatmap</span>
</div>
</div>
"""))

    hourly_data = get_hourly_noise_distribution()
    hours = hourly_data["hours"]
    dbs = hourly_data["db"]
    sources = hourly_data["sources"]

    fig, ax = plt.subplots(figsize=(10, 3.4), dpi=120)
    fig.patch.set_facecolor('#16171D')
    ax.set_facecolor('#111217')

    x = np.arange(len(hours))
    bar_colors = [
        '#10B981' if v < 70 else ('#F59E0B' if v <= 85 else '#EF4444')
        for v in dbs
    ]

    bars = ax.bar(x, dbs, color=bar_colors, width=0.68, edgecolor='#16171D', linewidth=1)
    
    ax.axhline(85, color='#EF4444', linestyle='--', linewidth=1.2, label='OSHA Limit (85 dB)')
    ax.axhline(70, color='#10B981', linestyle=':', linewidth=1.0, label='Quiet Ambient (70 dB)')

    ax.set_xticks(x)
    ax.set_xticklabels(hours, rotation=45, ha='right', fontsize=7.5, color='#8B949E')
    ax.set_ylabel("Average Decibels (dB)", fontsize=8.5, color='#8B949E')
    ax.set_ylim(30, 105)
    ax.grid(True, linestyle=':', alpha=0.3, color='#23252E')

    for spine in ax.spines.values():
        spine.set_color('#23252E')

    ax.legend(loc='upper left', frameon=False, fontsize=8, labelcolor='#E6EDF3')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # Section 2: 7-Day Weekly Trend
    st.html(clean_html("""
<div class="storage-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
<div>
<div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">7-Day Acoustic Trend & Peak Sound Pressure</div>
<div style="font-size: 0.74rem; color: #8B949E; margin-top: 0.2rem;">
Daily average noise envelope versus peak maximum sound spikes across the week.
</div>
</div>
<span class="badge-pill badge-green">Weekly Summary</span>
</div>
</div>
"""))

    weekly_data = get_weekly_db_trend()
    days = weekly_data["days"]
    avg_db = weekly_data["avg_db"]
    peak_db = weekly_data["peak_db"]

    fig_w, ax_w = plt.subplots(figsize=(10, 3.2), dpi=120)
    fig_w.patch.set_facecolor('#16171D')
    ax_w.set_facecolor('#111217')

    x_days = np.arange(len(days))
    ax_w.plot(x_days, avg_db, color='#38BDF8', marker='o', markersize=6, linewidth=2.2, label='Daily Average dB')
    ax_w.fill_between(x_days, avg_db, 50, color='#38BDF8', alpha=0.12)
    
    ax_w.plot(x_days, peak_db, color='#F59E0B', marker='s', markersize=5, linestyle='--', linewidth=1.5, label='Daily Peak dB Spike')
    ax_w.axhline(85, color='#EF4444', linestyle='--', linewidth=1.2, label='OSHA Limit (85 dB)')

    ax_w.set_xticks(x_days)
    ax_w.set_xticklabels(days, fontsize=9, color='#E6EDF3')
    ax_w.set_ylabel("Sound Pressure Level (dB)", fontsize=8.5, color='#8B949E')
    ax_w.set_ylim(50, 110)
    ax_w.grid(True, linestyle=':', alpha=0.3, color='#23252E')

    for spine in ax_w.spines.values():
        spine.set_color('#23252E')

    ax_w.legend(loc='upper right', frameon=False, fontsize=8, labelcolor='#E6EDF3')
    plt.tight_layout()
    st.pyplot(fig_w, use_container_width=True)
    plt.close(fig_w)
