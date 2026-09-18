"""
SonicPulse Sentry — Environmental & Industrial Acoustic Classification Dashboard
Built with Streamlit & Matplotlib/Librosa for Go Backend Integration.
Aesthetic faithfully matched to StorageOpt dark obsidian UI.
"""

import streamlit as st

# 1. Page Configuration (must be first Streamlit call)
st.set_page_config(
    page_title="SonicPulse Sentry | Acoustic Classifier",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom Dark Design System CSS
from components.styles import get_custom_css
st.html(get_custom_css())

# 3. Imports
from components.ui_cards import render_top_header, render_sidebar_footer, clean_html
from services.api_client import GoAcousticApiClient
from views.overview import render_overview_view
from views.upload_classify import render_upload_classify_view
from views.live_monitor import render_live_monitor_view
from views.history import render_history_view
from views.insights import render_insights_view
from views.api_settings import render_api_settings_view

# 4. Session State Management
if "api_client" not in st.session_state:
    st.session_state.api_client = GoAcousticApiClient(
        base_url=st.session_state.get("backend_url", "http://127.0.0.1:8080"),
        force_mock=st.session_state.get("force_mock", False)
    )

api_client = st.session_state.api_client

# 5. Sidebar Navigation (StorageOpt Aesthetic)
with st.sidebar:
    st.html(clean_html("""
<div class="mac-dots">
<span class="mac-dot red"></span>
<span class="mac-dot yellow"></span>
<span class="mac-dot green"></span>
</div>
<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.25rem;">
<span style="color: #F59E0B; font-weight: 800; font-size: 1.1rem;">▶</span>
<span style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; letter-spacing: -0.01em;">SonicPulse</span>
<span style="background: #23252E; font-size: 0.65rem; color: #8B949E; padding: 1px 5px; border-radius: 4px; font-family: 'JetBrains Mono', monospace;">v1.2</span>
</div>
"""))

    # Section 1: OVERVIEW
    st.html('<div class="sidebar-nav-header">OVERVIEW</div>')
    nav_overview = st.button("🎛️  Dashboard Overview", use_container_width=True)

    # Section 2: ACOUSTIC PIPELINE
    st.html('<div class="sidebar-nav-header">ACOUSTIC PIPELINE</div>')
    nav_upload = st.button("📁  Upload & Classify", use_container_width=True)
    nav_live = st.button("📡  Live Monitor (Stream)", use_container_width=True)
    nav_history = st.button("📜  History Dashboard", use_container_width=True)

    # Section 3: INTELLIGENCE
    st.html('<div class="sidebar-nav-header">INTELLIGENCE</div>')
    nav_insights = st.button("📈  Insights & Trends", use_container_width=True)

    # Section 4: SYSTEM & ENGINE
    st.html('<div class="sidebar-nav-header">SYSTEM & ENGINE</div>')
    nav_api = st.button("🔌  Go API & Health Probe", use_container_width=True)

    # Determine current page from button clicks or default
    if "current_view" not in st.session_state:
        st.session_state.current_view = "Dashboard Overview"

    if nav_overview:
        st.session_state.current_view = "Dashboard Overview"
    elif nav_upload:
        st.session_state.current_view = "Upload & Classify"
    elif nav_live:
        st.session_state.current_view = "Live Monitor"
    elif nav_history:
        st.session_state.current_view = "History Dashboard"
    elif nav_insights:
        st.session_state.current_view = "Insights & Trends"
    elif nav_api:
        st.session_state.current_view = "Go API & Health"

    # Sidebar Bottom Status Box
    health = api_client.check_health()
    is_live = not health.get("is_mock", True) and health.get("status") in ["online", "ok"]
    st.html(render_sidebar_footer(is_online=is_live, backend_url=api_client.base_url))

# 6. Main Header Bar
st.html(render_top_header(title="SonicPulse", section_name=st.session_state.current_view))

# 7. Render Selected View Page
current_view = st.session_state.current_view

if current_view == "Dashboard Overview":
    render_overview_view(api_client)
elif current_view == "Upload & Classify":
    render_upload_classify_view(api_client)
elif current_view == "Live Monitor":
    render_live_monitor_view(api_client)
elif current_view == "History Dashboard":
    render_history_view(api_client)
elif current_view == "Insights & Trends":
    render_insights_view(api_client)
elif current_view == "Go API & Health":
    render_api_settings_view(api_client)
