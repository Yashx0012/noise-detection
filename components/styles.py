"""
Custom CSS design system emulating the sleek dark-mode 'StorageOpt' aesthetic.
Color Palette:
- Background: #0C0D11
- Cards / Containers: #16171D
- Borders: #23252E
- Text: #E6EDF3 (primary), #8B949E (muted)
- Accents:
  - Amber / Orange: #F59E0B / #FF9800
  - Red / Danger: #EF4444
  - Green / Success: #10B981
  - Cyan / Blue: #38BDF8 / #3B82F6
  - Purple: #A855F7
"""

def get_custom_css() -> str:
    return """
<style>
/* Font import */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #E6EDF3;
}

/* Background & main canvas */
.stApp {
    background-color: #0C0D11 !important;
    color: #E6EDF3 !important;
}

/* Hide Streamlit default header decoration */
header[data-testid="stHeader"] {
    background-color: rgba(12, 13, 17, 0.8) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid #23252E !important;
    height: 3.5rem !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #121318 !important;
    border-right: 1px solid #23252E !important;
    padding-top: 1rem !important;
}

section[data-testid="stSidebar"] > div:first-child {
    background-color: #121318 !important;
}

/* Sidebar navigation buttons */
.sidebar-nav-header {
    font-size: 0.70rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6E7681;
    margin: 1.2rem 0 0.4rem 0.5rem;
}

/* Custom Card Container */
.storage-card {
    background: #16171D;
    border: 1px solid #23252E;
    border-radius: 12px;
    padding: 1.25rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    transition: border-color 0.2s ease, transform 0.2s ease;
}

.storage-card:hover {
    border-color: #2F333D;
}

/* Window Control Dots */
.mac-dots {
    display: inline-flex;
    gap: 7px;
    align-items: center;
    margin-bottom: 0.75rem;
}

.mac-dot {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    display: inline-block;
}

.mac-dot.red { background-color: #FF5F56; }
.mac-dot.yellow { background-color: #FFBD2E; }
.mac-dot.green { background-color: #27C93F; }

/* Top Header Bar */
.top-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0 1rem 0;
    border-bottom: 1px solid #23252E;
    margin-bottom: 1.5rem;
}

.app-brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 700;
    font-size: 1.15rem;
    color: #FFFFFF;
}

.app-brand-icon {
    color: #F59E0B;
    font-size: 1.1rem;
}

.search-pill {
    background: #181920;
    border: 1px solid #23252E;
    border-radius: 8px;
    padding: 0.35rem 0.85rem;
    font-size: 0.82rem;
    color: #8B949E;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.kbd-badge {
    background: #23252E;
    border-radius: 4px;
    padding: 0.1rem 0.35rem;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    color: #E6EDF3;
}

/* Multi-segmented Progress Bar Banner (Image 2) */
.volume-banner {
    background: #16171D;
    border: 1px solid #23252E;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
}

.volume-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
}

.volume-sublabel {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8B949E;
    font-weight: 600;
}

.volume-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0.2rem 0;
}

.volume-badge {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #10B981;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
}

.volume-badge.danger {
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #EF4444;
}

.segmented-progress-bar {
    height: 12px;
    border-radius: 6px;
    width: 100%;
    display: flex;
    overflow: hidden;
    background: #23252E;
    margin: 0.9rem 0 0.75rem 0;
}

.progress-segment {
    height: 100%;
    transition: width 0.3s ease;
}

.seg-red { background: #EF4444; }
.seg-amber { background: #F59E0B; }
.seg-yellow { background: #EAB308; }
.seg-gray { background: #4B5563; }
.seg-green { background: #10B981; }
.seg-cyan { background: #06B6D4; }

.legend-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1.25rem;
    margin-top: 0.5rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.78rem;
    color: #8B949E;
}

.legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

/* Metric Cards Grid (Image 2) */
.metric-card {
    background: #16171D;
    border: 1px solid #23252E;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    height: 100%;
    position: relative;
}

.metric-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8B949E;
}

.metric-icon-box {
    width: 28px;
    height: 28px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
}

.icon-box-blue {
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.25);
    color: #60A5FA;
}

.icon-box-yellow {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #FBBF24;
}

.icon-box-orange {
    background: rgba(249, 115, 22, 0.12);
    border: 1px solid rgba(249, 115, 22, 0.25);
    color: #FB923C;
}

.icon-box-green {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34D399;
}

.metric-val {
    font-size: 1.7rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.2;
    margin: 0.25rem 0;
}

.metric-sub {
    font-size: 0.75rem;
    color: #6E7681;
}

/* Category Extension Chips (Image 1) */
.chip-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
}

.extension-chip {
    background: #1B1C23;
    border: 1px solid #23252E;
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    position: relative;
    overflow: hidden;
}

.extension-chip::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 12px;
    width: 32px;
    height: 3px;
    background: #F59E0B;
    border-radius: 2px;
}

.chip-tag {
    font-size: 0.70rem;
    font-weight: 800;
    color: #F59E0B;
    background: rgba(245, 158, 11, 0.15);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    display: inline-block;
    margin-right: 0.4rem;
}

.chip-count {
    font-weight: 700;
    font-size: 0.85rem;
    color: #E6EDF3;
}

.chip-meta {
    font-size: 0.72rem;
    color: #8B949E;
    margin-top: 0.25rem;
}

/* Pill Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.badge-amber {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-green {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-red {
    background: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-blue {
    background: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.badge-purple {
    background: rgba(168, 85, 247, 0.15);
    color: #C084FC;
    border: 1px solid rgba(168, 85, 247, 0.3);
}

/* History & Detection Table (Image 1 & 3) */
.history-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 4px;
    margin-top: 0.75rem;
}

.history-table th {
    font-size: 0.70rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6E7681;
    padding: 0.6rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid #23252E;
}

.history-table td {
    background: #181920;
    padding: 0.65rem 0.75rem;
    font-size: 0.82rem;
    color: #E6EDF3;
    border-top: 1px solid #20222B;
    border-bottom: 1px solid #20222B;
}

.history-table tr td:first-child {
    border-top-left-radius: 6px;
    border-bottom-left-radius: 6px;
    border-left: 1px solid #20222B;
}

.history-table tr td:last-child {
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    border-right: 1px solid #20222B;
}

.history-table tr:hover td {
    background: #1E202A;
}

.mono-path {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #C9D1D9;
}

/* Custom Horizontal Confidence Bar */
.score-bar-wrapper {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.score-track {
    width: 70px;
    height: 5px;
    background: #282A36;
    border-radius: 3px;
    overflow: hidden;
}

.score-fill {
    height: 100%;
    border-radius: 3px;
}

/* Sidebar Footer (Image 1 bottom left) */
.sidebar-footer-box {
    margin-top: 2rem;
    padding: 0.85rem;
    background: #16171D;
    border: 1px solid #23252E;
    border-radius: 8px;
}

.sidebar-footer-title {
    font-size: 0.68rem;
    color: #6E7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}

.sidebar-status-pill {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: #E6EDF3;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10B981;
    box-shadow: 0 0 8px #10B981;
    display: inline-block;
    animation: pulseGlow 2s infinite;
}

.pulse-dot.offline {
    background-color: #EF4444;
    box-shadow: 0 0 8px #EF4444;
}

@keyframes pulseGlow {
    0% { opacity: 0.6; }
    50% { opacity: 1; transform: scale(1.15); }
    100% { opacity: 0.6; }
}

/* Streamlit Button overrides */
div.stButton > button {
    background: #1C1D24 !important;
    color: #E6EDF3 !important;
    border: 1px solid #2D3039 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    background: #242630 !important;
    border-color: #F59E0B !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.2) !important;
}

/* Primary buttons */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
    color: #000000 !important;
    border: none !important;
    font-weight: 700 !important;
}

div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 16px rgba(245, 158, 11, 0.4) !important;
}

/* Streamlit Selectbox and Input overrides */
div[data-baseweb="select"] > div {
    background-color: #181920 !important;
    border: 1px solid #23252E !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
}

/* Custom scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0C0D11;
}
::-webkit-scrollbar-thumb {
    background: #23252E;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #3A3D4A;
}
</style>
"""
