"""
Live Monitor View:
- Start/Stop button -> calls POST /record + connects to /stream (WebSocket)
- Real-time decibel meter (dB SPL)
- Rolling classification stream display with live timestamps and confidence
- Live rolling dB time-series oscillogram
"""

import streamlit as st
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from components.audio_plots import render_db_gauge_html
from components.ui_cards import render_metric_cards_row, clean_html

def render_live_monitor_view(api_client):
    st.html(clean_html("""
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Live Acoustic Monitor & Stream</div>
<div style="font-size: 0.82rem; color: #8B949E; margin-top: 0.2rem;">
Real-time audio telemetry. Dispatches <code style="color: #F59E0B; background: #1B1C23; padding: 2px 6px; border-radius: 4px;">POST /record</code> and subscribes to <code style="color: #38BDF8; background: #1B1C23; padding: 2px 6px; border-radius: 4px;">WS /stream</code>.
</div>
</div>
"""))

    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    if "live_stream_packets" not in st.session_state:
        st.session_state.live_stream_packets = [
            api_client.simulate_stream_packet("Jackhammer") for _ in range(8)
        ]
    if "current_live_db" not in st.session_state:
        st.session_state.current_live_db = 88.5

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.2, 1.2, 1.6], gap="medium")

    with col_ctrl1:
        if not st.session_state.is_recording:
            if st.button("▶ START LIVE SESSION", type="primary", use_container_width=True):
                rec_res = api_client.record_session("start")
                st.session_state.is_recording = True
                st.session_state.session_id = rec_res.get("session_id", "sess_001")
                st.toast("🔴 Audio session recording started on Go backend!", icon="📡")
                st.rerun()
        else:
            if st.button("⏹ STOP RECORDING", use_container_width=True):
                api_client.record_session("stop")
                st.session_state.is_recording = False
                st.toast("⏹ Live session terminated.", icon="⏸")
                st.rerun()

    with col_ctrl2:
        sim_source = st.selectbox(
            "Simulated Sound Source",
            ["Jackhammer", "Siren", "Drilling", "Traffic", "Ambient"],
            index=0,
            help="Select audio profile to simulate stream incoming frames."
        )

    with col_ctrl3:
        status_text = "STREAMING ACTIVE" if st.session_state.is_recording else "MONITOR STANDBY"
        badge_cls = "badge-green" if st.session_state.is_recording else "badge-amber"
        dot_cls = "pulse-dot" if st.session_state.is_recording else "pulse-dot offline"
        
        st.html(clean_html(f"""
<div style="background: #181920; border: 1px solid #23252E; border-radius: 8px; padding: 0.5rem 0.85rem; display: flex; align-items: center; justify-content: space-between; height: 42px; margin-top: 2px;">
<div style="display: flex; align-items: center; gap: 0.5rem;">
<span class="{dot_cls}"></span>
<span style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF;">{status_text}</span>
</div>
<span class="badge-pill {badge_cls}" style="font-size: 0.70rem;">WS /stream</span>
</div>
"""))

    if st.session_state.is_recording:
        new_pkt = api_client.simulate_stream_packet(sim_source)
        st.session_state.current_live_db = new_pkt["dB"]
        st.session_state.live_stream_packets.insert(0, new_pkt)
        if len(st.session_state.live_stream_packets) > 30:
            st.session_state.live_stream_packets.pop()

    latest_pkt = st.session_state.live_stream_packets[0]
    live_cards = [
        {
            "label": "CURRENT NOISE LEVEL",
            "val": f"{st.session_state.current_live_db:.1f} dB",
            "sub": "Real-time transducer reading",
            "type": "yellow" if st.session_state.current_live_db > 85 else "green"
        },
        {
            "label": "ACTIVE CLASSIFICATION",
            "val": latest_pkt["class"].split()[0],
            "sub": f"Confidence: {latest_pkt['confidence']*100:.1f}%",
            "type": "blue"
        },
        {
            "label": "STREAM FRAMES RECEIVED",
            "val": f"{len(st.session_state.live_stream_packets)} / 30",
            "sub": "Ring buffer capacity",
            "type": "orange"
        },
        {
            "label": "WEBSOCKET LATENCY",
            "val": "14 ms",
            "sub": "Round-trip time to Go daemon",
            "type": "green"
        }
    ]
    st.html(render_metric_cards_row(live_cards))

    # Real-Time Decibel Gauge
    st.html(
        render_db_gauge_html(
            st.session_state.current_live_db,
            peak_db=max([p["dB"] for p in st.session_state.live_stream_packets])
        )
    )

    # Time-Series Chart
    st.html(clean_html("""
<div style="font-size: 1rem; font-weight: 700; color: #FFFFFF; margin: 1.2rem 0 0.5rem 0;">
Rolling Decibel Telemetry (Last 30 Stream Packets)
</div>
"""))

    dbs = [p["dB"] for p in reversed(st.session_state.live_stream_packets)]
    timestamps = [p["timestamp"] for p in reversed(st.session_state.live_stream_packets)]

    fig, ax = plt.subplots(figsize=(10, 2.8), dpi=120)
    fig.patch.set_facecolor('#16171D')
    ax.set_facecolor('#111217')

    x_indices = np.arange(len(dbs))
    ax.plot(x_indices, dbs, color='#38BDF8', linewidth=2.0, label='Stream dB Level')
    ax.fill_between(x_indices, dbs, 40, color='#38BDF8', alpha=0.15)
    
    ax.axhline(85, color='#EF4444', linestyle='--', linewidth=1.2, label='OSHA Limit (85 dB)')

    ax.set_ylim(40, 115)
    ax.set_ylabel("Sound Level (dB)", fontsize=8, color='#8B949E')
    ax.set_xlabel("Time Frame", fontsize=8, color='#8B949E')
    ax.grid(True, linestyle=':', alpha=0.4, color='#23252E')
    
    tick_pos = np.arange(0, len(timestamps), max(1, len(timestamps)//6))
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([timestamps[i] for i in tick_pos], fontsize=7, color='#8B949E')
    
    for spine in ax.spines.values():
        spine.set_color('#23252E')

    ax.legend(loc='upper right', frameon=False, fontsize=8, labelcolor='#E6EDF3')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    # Rolling Classification Stream Table
    st.html(clean_html("""
<div style="font-size: 1rem; font-weight: 700; color: #FFFFFF; margin: 1.5rem 0 0.5rem 0;">
Live Classification Event Stream
</div>
"""))

    stream_rows = ""
    for p in st.session_state.live_stream_packets[:12]:
        conf_val = p["confidence"]
        conf_pct = int(conf_val * 100)
        c_name = p["class"]
        
        badge_cls = "badge-amber"
        if "Siren" in c_name: badge_cls = "badge-red"
        elif "Horn" in c_name: badge_cls = "badge-amber"
        elif "Jackhammer" in c_name: badge_cls = "badge-purple"
        elif "Ambient" in c_name: badge_cls = "badge-blue"

        stream_rows += f"""
<tr>
<td style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #8B949E;">
{p['timestamp']}
</td>
<td>
<span class="badge-pill {badge_cls}">{c_name}</span>
</td>
<td>
<div class="score-bar-wrapper">
<div class="score-track">
<div class="score-fill" style="width: {conf_pct}%; background: #10B981;"></div>
</div>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #E6EDF3;">{conf_val:.2f}</span>
</div>
</td>
<td style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 700; color: #F59E0B;">
{p['dB']:.1f} dB
</td>
<td style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #6E7681;">
{p['frame_id']}
</td>
</tr>
"""

    st.html(clean_html(f"""
<table class="history-table">
<thead>
<tr>
<th style="width: 140px;">TIMESTAMP</th>
<th style="width: 220px;">CLASSIFIED EVENT</th>
<th style="width: 160px;">CONFIDENCE</th>
<th style="width: 120px;">NOISE LEVEL</th>
<th>FRAME DESCRIPTOR</th>
</tr>
</thead>
<tbody>
{stream_rows}
</tbody>
</table>
"""))

    if st.session_state.is_recording:
        time.sleep(1.0)
        st.rerun()
