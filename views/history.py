"""
History Dashboard View matching the exact structure of Image 1 & 3.
"""

import streamlit as st
import json
import pandas as pd
from components.ui_cards import (
    render_category_chips,
    render_history_table_html,
    clean_html
)
from services.mock_data import get_mock_category_chips, ACOUSTIC_CLASSES

def render_history_view(api_client):
    st.html(clean_html("""
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Historical Ingestion Archive</div>
<div style="font-size: 0.82rem; color: #8B949E; margin-top: 0.2rem;">
Query and filter past inference results. Fetched via <code style="color: #F59E0B; background: #1B1C23; padding: 2px 6px; border-radius: 4px;">GET /history</code>.
</div>
</div>
"""))

    col_filters, col_actions = st.columns([1.5, 1.0], gap="large")

    with col_filters:
        st.html(clean_html("""
<div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
<span style="font-size: 0.76rem; color: #8B949E; font-weight: 600;">Time Window:</span>
<div style="display: flex; gap: 4px; background: #181920; border: 1px solid #23252E; border-radius: 6px; padding: 2px;">
<button style="background: #23252E; border: none; color: #FFF; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px; font-weight: 600;">Today</button>
<button style="background: transparent; border: none; color: #8B949E; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px;">7 Days</button>
<button style="background: transparent; border: none; color: #8B949E; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px;">30 Days</button>
<button style="background: transparent; border: none; color: #8B949E; font-size: 0.72rem; padding: 3px 8px; border-radius: 4px;">All Time</button>
</div>
</div>
"""))

    with col_actions:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            select_high_db = st.button("🚨 Flag >85 dB", use_container_width=True)
        with btn_col2:
            export_clicked = st.button("📥 Export JSON", use_container_width=True)

    # Section 1: Footprint Chips
    st.html(clean_html("""
<div class="storage-card" style="margin-top: 0.5rem; margin-bottom: 1.5rem;">
<div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">Acoustic Class Analytics & Footprint</div>
<div style="font-size: 0.74rem; color: #8B949E; margin-top: 0.2rem;">
Breakdown of classified environmental and industrial acoustic events grouped by signature profile.
</div>
"""))

    chips = get_mock_category_chips()
    st.html(render_category_chips(chips))
    st.html("</div>")

    # Section 2: History Table
    st.html(clean_html("""
<div class="storage-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<div>
<div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF;">Inference Log Journal</div>
<div style="font-size: 0.74rem; color: #8B949E; margin-top: 0.2rem;">
Full audit trail of edge classifications with confidence vectors and SPL levels.
</div>
</div>
</div>
"""))

    filter_col1, filter_col2, filter_col3 = st.columns([1.2, 1.2, 1.0], gap="medium")
    with filter_col1:
        cat_choices = ["All"] + [c.split(" (")[0] for c in ACOUSTIC_CLASSES[:6]]
        selected_cat = st.selectbox("Filter by Category", cat_choices, index=0)
    with filter_col2:
        min_db_filter = st.slider("Minimum Decibels (dB SPL)", 0.0, 100.0, 0.0, 5.0)
    with filter_col3:
        record_limit = st.selectbox("Display Limit", [10, 20, 50], index=0)

    records = api_client.get_history(
        limit=record_limit,
        category_filter=selected_cat,
        min_db=min_db_filter
    )

    if select_high_db:
        records = [r for r in records if r["raw_db"] >= 85.0]

    st.html(render_history_table_html(records))

    if export_clicked:
        json_str = json.dumps(records, indent=2)
        st.download_button(
            label="💾 Download classification_history.json",
            data=json_str,
            file_name="classification_history.json",
            mime="application/json"
        )

    st.html("</div>")
