"""
Executive Overview Dashboard matching the exact visual layout of Image 2.
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from components.ui_cards import (
    render_acoustic_volume_banner,
    render_metric_cards_row,
    clean_html
)
from services.mock_data import get_mock_category_chips

def render_overview_view(api_client):
    # Top Acoustic Volume Banner (Image 2)
    st.html(
        render_acoustic_volume_banner(
            peak_db=84.2,
            total_samples="14,892 Classified Frames",
            status_label="3.13 dB Below OSHA Hazard Limit",
            status_type="safe",
            seg_quiet=42.0,
            seg_mod=32.0,
            seg_loud=18.0,
            seg_haz=8.0,
            quiet_val="Ambient (<55 dB) 6.2k frames",
            mod_val="Moderate (55-70 dB) 4.8k frames",
            loud_val="Elevated (70-85 dB) 2.7k frames",
            haz_val="Hazardous (>85 dB) 1.2k frames"
        )
    )

    # 4 Metric Cards Row (Image 2)
    cards = [
        {
            "label": "TOTAL INDEXED",
            "val": "14,892",
            "sub": "211,521 frames indexed",
            "type": "blue"
        },
        {
            "label": "PEAK NOISE LEVEL",
            "val": "98.7 dB",
            "sub": "Jackhammer cluster (85 dB limit)",
            "type": "yellow"
        },
        {
            "label": "INACTIVE BUFFER",
            "val": "2.55 GB",
            "sub": "131,187 chunks (30+ days)",
            "type": "orange"
        },
        {
            "label": "CLASSIFICATION ACCURACY",
            "val": "98.4 %",
            "sub": "Edge-ONNX Go engine v2.4",
            "type": "green"
        }
    ]
    st.html(render_metric_cards_row(cards))

    # Bottom Two Columns (Donut Chart on Left, Optimization/Alerts on Right)
    col_left, col_right = st.columns([1.1, 1.0], gap="medium")

    with col_left:
        st.html(clean_html("""
<div class="storage-card" style="min-height: 400px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
<div>
<div style="font-weight: 700; font-size: 1rem; color: #FFFFFF;">Acoustic Category Classification</div>
<div style="font-size: 0.74rem; color: #8B949E; margin-top: 0.2rem;">POSIX audio stream metadata mapped into 6 system isolation tiers</div>
</div>
<span style="background: #23252E; font-size: 0.70rem; color: #8B949E; padding: 0.2rem 0.55rem; border-radius: 4px;">6 Active Classes</span>
</div>
</div>
"""))

        # Matplotlib Donut Chart with dark background
        categories = ['Industrial & Drilling', 'Emergency Sirens', 'Traffic & Horns', 'Ambient HVAC', 'Urban Music', 'Others']
        shares = [38, 24, 18, 10, 6, 4]
        colors = ['#EF4444', '#F59E0B', '#EAB308', '#10B981', '#06B6D4', '#64748B']

        fig, ax = plt.subplots(figsize=(5.5, 3.0), dpi=120)
        fig.patch.set_facecolor('#16171D')
        ax.set_facecolor('#16171D')

        wedges, texts = ax.pie(
            shares,
            labels=None,
            colors=colors,
            startangle=140,
            wedgeprops=dict(width=0.38, edgecolor='#16171D', linewidth=2.5)
        )

        ax.text(0, 0.08, "14,892", ha='center', va='center', fontsize=15, fontweight='bold', color='#FFFFFF')
        ax.text(0, -0.15, "TOTAL FRAMES", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#8B949E')

        legend_labels = [
            f"{cat}  ({share}%)" for cat, share in zip(categories, shares)
        ]
        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            frameon=False,
            fontsize=8,
            labelcolor='#C9D1D9'
        )

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col_right:
        st.html(clean_html("""
<div class="storage-card" style="min-height: 400px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<div>
<div style="font-weight: 700; font-size: 1rem; color: #FFFFFF;">Optimization Recommendations</div>
<div style="font-size: 0.74rem; color: #8B949E; margin-top: 0.2rem;">High-yield actions prioritized by OSHA acoustic safety matrix</div>
</div>
<span class="badge-pill badge-green">Engine Ready</span>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem; background: #1B1C23; border: 1px solid #23252E; border-radius: 8px; margin-bottom: 0.75rem;">
<div style="display: flex; align-items: center; gap: 0.75rem;">
<div style="width: 32px; height: 32px; border-radius: 6px; background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.25); display: flex; align-items: center; justify-content: center; color: #F59E0B; font-size: 0.9rem;">
⚡
</div>
<div>
<div style="font-size: 0.84rem; font-weight: 700; color: #FFFFFF;">Reclaim Audio Buffer Space</div>
<div style="font-size: 0.72rem; color: #8B949E;">Purge 1,420 unflagged ambient chunks older than 14 days.</div>
</div>
</div>
<span class="badge-pill badge-amber">Review</span>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem; background: #1B1C23; border: 1px solid #23252E; border-radius: 8px; margin-bottom: 0.75rem;">
<div style="display: flex; align-items: center; gap: 0.75rem;">
<div style="width: 32px; height: 32px; border-radius: 6px; background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.25); display: flex; align-items: center; justify-content: center; color: #EF4444; font-size: 0.9rem;">
🚨
</div>
<div>
<div style="font-size: 0.84rem; font-weight: 700; color: #FFFFFF;">Investigate High-dB Clusters</div>
<div style="font-size: 0.72rem; color: #8B949E;">4 consecutive jackhammer bursts exceeded 95 dB limit.</div>
</div>
</div>
<span class="badge-pill badge-red">Inspect</span>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem; background: #1B1C23; border: 1px solid #23252E; border-radius: 8px;">
<div style="display: flex; align-items: center; gap: 0.75rem;">
<div style="width: 32px; height: 32px; border-radius: 6px; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.25); display: flex; align-items: center; justify-content: center; color: #60A5FA; font-size: 0.9rem;">
📈
</div>
<div>
<div style="font-size: 0.84rem; font-weight: 700; color: #FFFFFF;">AI Noise Growth Forecast</div>
<div style="font-size: 0.72rem; color: #8B949E;">Predict weekly peak sound thresholds based on 30-day run.</div>
</div>
</div>
<span class="badge-pill badge-blue">Forecast</span>
</div>
</div>
"""))
