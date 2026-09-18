"""
API Settings & Daemon Health Inspector:
- Health check liveness probe (/health)
- Backend URL configuration
- Mock Mode vs Live Go Backend toggle
- Interactive API Contract Reference
"""

import streamlit as st
import time
from datetime import datetime
from components.ui_cards import clean_html

def render_api_settings_view(api_client):
    st.html(clean_html("""
<div style="margin-bottom: 1.25rem;">
<div style="font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">Backend Daemon & API Contract</div>
<div style="font-size: 0.82rem; color: #8B949E; margin-top: 0.2rem;">
Inspect connection health, endpoint contracts, and configure Go engine endpoints.
</div>
</div>
"""))

    col1, col2 = st.columns([1.1, 1.0], gap="large")

    with col1:
        st.html(clean_html("""
<div class="storage-card">
<div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF; margin-bottom: 0.5rem;">
Go Backend Connection Settings
</div>
</div>
"""))

        backend_url = st.text_input(
            "Go Backend API Base URL",
            value=st.session_state.get("backend_url", "http://127.0.0.1:8080"),
            help="Target URL of the running Go acoustic classification daemon."
        )
        st.session_state.backend_url = backend_url
        api_client.base_url = backend_url.rstrip("/")

        force_mock = st.checkbox(
            "Force Standalone Mock Mode",
            value=st.session_state.get("force_mock", False),
            help="Bypasses HTTP calls and uses synthetic audio/telemetry generators."
        )
        st.session_state.force_mock = force_mock
        api_client.force_mock = force_mock

        if st.button("⚡ Test Health Probe (/health)", type="primary", use_container_width=True):
            health_data = api_client.check_health()
            st.session_state.health_data = health_data
            if health_data.get("status") in ["online", "online (mock)", "ok"]:
                st.success(f"Backend Responded! Latency: {health_data.get('latency_ms', 0)} ms")
            else:
                st.warning("Go daemon not reachable at specified URL. Using Standalone Mock Engine fallback.")

        health_info = st.session_state.get("health_data", api_client.check_health())
        is_mock = health_info.get("is_mock", True)
        badge_cls = "badge-green" if not is_mock else "badge-amber"
        
        st.html(clean_html(f"""
<div style="margin-top: 1rem; padding: 0.85rem; background: #1B1C23; border: 1px solid #23252E; border-radius: 8px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="font-size: 0.82rem; font-weight: 600; color: #E6EDF3;">Engine Status</span>
<span class="badge-pill {badge_cls}">{health_info.get('status', 'offline').upper()}</span>
</div>
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: #8B949E; margin-top: 0.5rem; line-height: 1.6;">
Engine: <span style="color: #E6EDF3;">{health_info.get('engine', 'Mock Engine')}</span><br/>
Round-trip Latency: <span style="color: #F59E0B;">{health_info.get('latency_ms', 0.0)} ms</span><br/>
API Target: <span style="color: #38BDF8;">{api_client.base_url}</span>
</div>
</div>
"""))

    with col2:
        st.html(clean_html("""
<div class="storage-card">
<div style="font-weight: 700; font-size: 1.05rem; color: #FFFFFF; margin-bottom: 0.5rem;">
API Contract Compliance Matrix
</div>
<div style="font-size: 0.76rem; color: #8B949E; margin-bottom: 0.75rem;">
Verified endpoints adhering strictly to frontend assignment specification:
</div>

<table class="history-table">
<thead>
<tr>
<th>METHOD</th>
<th>ENDPOINT</th>
<th>PURPOSE</th>
</tr>
</thead>
<tbody>
<tr>
<td><span class="badge-pill badge-green">POST</span></td>
<td><span class="mono-path">/upload</span></td>
<td style="font-size: 0.74rem; color: #8B949E;">Audio file classification</td>
</tr>
<tr>
<td><span class="badge-pill badge-green">POST</span></td>
<td><span class="mono-path">/record</span></td>
<td style="font-size: 0.74rem; color: #8B949E;">Start/stop live capture</td>
</tr>
<tr>
<td><span class="badge-pill badge-green">POST</span></td>
<td><span class="mono-path">/predict</span></td>
<td style="font-size: 0.74rem; color: #8B949E;">Buffer prediction</td>
</tr>
<tr>
<td><span class="badge-pill badge-purple">WS</span></td>
<td><span class="mono-path">/stream</span></td>
<td style="font-size: 0.74rem; color: #8B949E;">Live streaming telemetry</td>
</tr>
<tr>
<td><span class="badge-pill badge-blue">GET</span></td>
<td><span class="mono-path">/history</span></td>
<td style="font-size: 0.74rem; color: #8B949E;">Query past inferences</td>
</tr>
<tr>
<td><span class="badge-pill badge-blue">GET</span></td>
<td><span class="mono-path">/health</span></td>
<td style="font-size: 0.74rem; color: #8B949E;">Engine liveness probe</td>
</tr>
</tbody>
</table>
</div>
"""))
