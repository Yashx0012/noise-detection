"""
Reusable UI cards and components matching the exact visual structure from the StorageOpt screenshots.
All HTML outputs are unindented (column 0) to avoid Markdown code-block interpretation.
"""

def clean_html(html_str: str) -> str:
    """Strips leading/trailing indentation from each line so Markdown never treats it as a code block."""
    return "\n".join(line.strip() for line in html_str.strip().split("\n") if line.strip())


def render_top_header(title: str = "SonicPulse", section_name: str = "Dashboard Overview") -> str:
    """
    Renders top bar with Mac window control dots, brand logo, search pill with ⌘K badge.
    """
    raw = f"""
<div class="top-header-bar">
<div style="display: flex; align-items: center; gap: 1.5rem;">
<div class="mac-dots" style="margin-bottom: 0;">
<span class="mac-dot red"></span>
<span class="mac-dot yellow"></span>
<span class="mac-dot green"></span>
</div>
<div class="app-brand">
<span class="app-brand-icon">▶</span>
<span>{title}</span>
<span style="color: #6E7681; font-weight: 400; font-size: 0.95rem;">/</span>
<span style="color: #8B949E; font-weight: 500; font-size: 0.9rem;">{section_name}</span>
</div>
</div>
<div style="display: flex; align-items: center; gap: 0.8rem;">
<div class="search-pill">
<span>🔍</span>
<span>Search acoustic logs...</span>
<span class="kbd-badge">⌘K</span>
</div>
</div>
</div>
"""
    return clean_html(raw)


def render_acoustic_volume_banner(
    peak_db: float = 84.2,
    total_samples: str = "14,892 Classified Frames",
    status_label: str = "3.13 dB Below OSHA Hazard Limit",
    status_type: str = "safe",
    seg_quiet: float = 42.0,
    seg_mod: float = 32.0,
    seg_loud: float = 18.0,
    seg_haz: float = 8.0,
    quiet_val: str = "Ambient (<55 dB) 6.2k frames",
    mod_val: str = "Moderate (55-70 dB) 4.8k frames",
    loud_val: str = "Elevated (70-85 dB) 2.7k frames",
    haz_val: str = "Hazardous (>85 dB) 1.2k frames"
) -> str:
    """
    Renders the exact top banner from Image 2 without any markdown indentation.
    """
    badge_cls = "volume-badge" if status_type == "safe" else "volume-badge danger"
    
    raw = f"""
<div class="volume-banner">
<div class="volume-header">
<div>
<div class="volume-sublabel">INTERNAL SENSOR ARRAY / ACOUSTIC FIELD</div>
<div class="volume-title">{peak_db:.1f} dB Peak Exposure</div>
</div>
<span class="{badge_cls}">{status_label}</span>
</div>
<div class="segmented-progress-bar">
<div class="progress-segment seg-cyan" style="width: {seg_quiet}%;"></div>
<div class="progress-segment seg-green" style="width: {seg_mod}%;"></div>
<div class="progress-segment seg-amber" style="width: {seg_loud}%;"></div>
<div class="progress-segment seg-red" style="width: {seg_haz}%;"></div>
</div>
<div class="legend-row">
<div class="legend-item">
<span class="legend-dot" style="background: #06B6D4;"></span>
<span>{quiet_val}</span>
</div>
<div class="legend-item">
<span class="legend-dot" style="background: #10B981;"></span>
<span>{mod_val}</span>
</div>
<div class="legend-item">
<span class="legend-dot" style="background: #F59E0B;"></span>
<span>{loud_val}</span>
</div>
<div class="legend-item">
<span class="legend-dot" style="background: #EF4444;"></span>
<span>{haz_val}</span>
</div>
</div>
</div>
"""
    return clean_html(raw)


def render_metric_cards_row(cards: list) -> str:
    """
    Renders a row of 4 metric cards matching Image 2 without markdown indentation.
    """
    cols_html = ""
    icon_map = {
        "blue": ("icon-box-blue", "▢"),
        "yellow": ("icon-box-yellow", "◱"),
        "orange": ("icon-box-orange", "⏱"),
        "green": ("icon-box-green", "✓")
    }

    for c in cards:
        c_type = c.get("type", "blue")
        box_cls, icon_symbol = icon_map.get(c_type, ("icon-box-blue", "●"))
        
        cols_html += f"""
<div style="flex: 1; min-width: 200px;">
<div class="metric-card">
<div class="metric-top-row">
<span class="metric-label">{c['label']}</span>
<div class="metric-icon-box {box_cls}">{icon_symbol}</div>
</div>
<div class="metric-val">{c['val']}</div>
<div class="metric-sub">{c['sub']}</div>
</div>
</div>
"""
        
    raw = f"""
<div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
{cols_html}
</div>
"""
    return clean_html(raw)


def render_category_chips(chips: list) -> str:
    """
    Renders category / extension chips matching Image 1 without markdown indentation.
    """
    cards_html = ""
    for c in chips:
        cards_html += f"""
<div class="extension-chip">
<div style="display: flex; align-items: center; justify-content: space-between;">
<span class="chip-tag">{c['tag']}</span>
<span class="chip-count">{c['count']}</span>
</div>
<div class="chip-meta">{c['meta']}</div>
</div>
"""
        
    raw = f"""
<div class="chip-grid">
{cards_html}
</div>
"""
    return clean_html(raw)


def render_history_table_html(rows: list) -> str:
    """
    Renders the dark sleek history table matching Image 1 & 3 without markdown indentation.
    """
    tbody_html = ""
    for r in rows:
        conf = float(r.get("confidence", 0.9))
        conf_pct = min(100, int(conf * 100))
        
        if conf >= 0.90:
            bar_color = "#10B981"
        elif conf >= 0.70:
            bar_color = "#F59E0B"
        else:
            bar_color = "#EF4444"
            
        cat = r.get("category", "Acoustic Event")
        badge_cls = "badge-amber"
        if "Siren" in cat or "Horn" in cat:
            badge_cls = "badge-red"
        elif "Music" in cat or "Ambient" in cat:
            badge_cls = "badge-blue"
        elif "Jackhammer" in cat or "Drilling" in cat:
            badge_cls = "badge-amber"
        elif "Engine" in cat:
            badge_cls = "badge-purple"
            
        tbody_html += f"""
<tr>
<td style="width: 30px; text-align: center;">
<input type="checkbox" style="accent-color: #F59E0B; cursor: pointer;" />
</td>
<td style="width: 130px;">
<div class="score-bar-wrapper">
<div class="score-track">
<div class="score-fill" style="width: {conf_pct}%; background: {bar_color};"></div>
</div>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; color: #E6EDF3;">{conf:.2f}</span>
</div>
</td>
<td style="width: 140px;">
<span class="badge-pill {badge_cls}">{cat}</span>
</td>
<td>
<span class="mono-path">{r.get('path', '')}</span>
</td>
<td style="width: 90px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #8B949E;">
{r.get('db', '-- dB')}
</td>
<td style="width: 130px; font-size: 0.76rem; color: #8B949E;">
{r.get('time', 'Just now')}
</td>
</tr>
"""
        
    raw = f"""
<table class="history-table">
<thead>
<tr>
<th style="width: 30px; text-align: center;"><input type="checkbox" style="accent-color: #F59E0B;" /></th>
<th style="width: 130px;">CONFIDENCE SCORE</th>
<th style="width: 140px;">CATEGORY</th>
<th>SOURCE CHUNK / PATH</th>
<th style="width: 90px;">PEAK dB</th>
<th style="width: 130px;">LAST DETECTED</th>
</tr>
</thead>
<tbody>
{tbody_html}
</tbody>
</table>
"""
    return clean_html(raw)


def render_sidebar_footer(is_online: bool = True, backend_url: str = "http://127.0.0.1:8080") -> str:
    """
    Renders the bottom-left Go Core Active widget matching the demo screenshots.
    """
    pulse_cls = "pulse-dot" if is_online else "pulse-dot offline"
    status_title = "Go Core Active" if is_online else "Mock Engine Standalone"
    display_url = backend_url.replace("http://", "").replace("https://", "")
    
    raw = f"""
<div class="sidebar-footer-box">
<div class="sidebar-footer-title">ENGINE RUNTIME • TELEMETRY</div>
<div class="sidebar-status-pill">
<span class="{pulse_cls}"></span>
<span>{status_title}</span>
</div>
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #6E7681; margin-top: 0.35rem;">
{display_url}
</div>
</div>
"""
    return clean_html(raw)
