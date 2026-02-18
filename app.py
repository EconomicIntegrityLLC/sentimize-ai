"""$entimize.ai — Image Art Studio by Economic Integrity LLC.

Upload any photo (or snap a selfie) and transform it into pixel art,
ASCII art, sketches, quadtree decompositions, pop art, or extract its
colour palette.  Built entirely on Python open-source packages.
"""

import html as html_mod
from io import BytesIO
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import pyfiglet
import streamlit as st
from PIL import Image

from transforms import (
    color_by_number,
    extract_palette,
    glitch,
    mosaic,
    pixelate,
    posterize,
    quadtree,
    sketch,
    to_ascii,
    watermark,
    watermark_text,
)

# ── Constants ────────────────────────────────────────────────────────────────

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"
SAMPLE_PATH = Path(__file__).parent / "assets" / "sample.jpg"
BRAND_COLOR = "#c8a84e"
BRAND_GREEN = "#2ecc40"
BRAND_NAME = "Economic Integrity LLC"
APP_VERSION = "1.2.0"
CREATED_DATE = "2/18/26"

STYLES = [
    ("🟩", "Pixel Art", "Retro pixelation with colour quantisation"),
    ("📝", "ASCII Art", "Image rendered entirely as text characters"),
    ("✏️", "Sketch", "Pencil-drawing via edge detection"),
    ("🔲", "Quadtree", "Geometric recursive decomposition"),
    ("🎨", "Pop Art", "Bold posterised colours, Warhol-style"),
    ("🎯", "Palette", "Extract & visualise dominant colours"),
    ("🖍️", "Color It", "Turn any photo into a colour-by-number page"),
    ("🪟", "Mosaic", "Stained-glass Voronoi tessellation"),
    ("📺", "Glitch", "VHS channel-shift & block displacement"),
]

TAB_LABELS = [f"{icon} {name}" for icon, name, _ in STYLES]

# ── Page config ──────────────────────────────────────────────────────────────

_favicon = Image.open(LOGO_PATH) if LOGO_PATH.exists() else "🔥"

st.set_page_config(
    page_title="$entimize.ai • Image Art Studio",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ───────────────────────────────────────────────────

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "use_sample" not in st.session_state:
    st.session_state.use_sample = False

_dark = st.session_state.dark_mode

# ── Responsive CSS with theme variables ──────────────────────────────────────

_t = dict(
    fg        = "#f0f0f0"  if _dark else "#1a1a1a",
    fg_muted  = "#aaa"     if _dark else "#666",
    fg_dim    = "#9ca3af"  if _dark else "#888",
    surface   = "#111827"  if _dark else "#f4f5f7",
    border    = "#2a2a2a"  if _dark else "#ddd",
    ascii_bg  = "#0a0a0a"  if _dark else "#f5f5f5",
    ascii_fg  = "#e0e0e0"  if _dark else "#333",
    hero_bg   = "linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%)"
                if _dark else
                "linear-gradient(135deg,#f5f0e1 0%,#ede4d3 50%,#f5f0e1 100%)",
    hero_bdr  = "#2a2a4a"  if _dark else "#d4c9a8",
    hero_sub  = "#c0c0d0"  if _dark else "#555",
    hero_desc = "#8888a0"  if _dark else "#888",
    footer_fg = "#666"     if _dark else "#999",
    footer_bdr= "#222"     if _dark else "#ddd",
    card_shadow = "none"   if _dark else "0 1px 4px rgba(0,0,0,0.08)",
)

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rock+Salt&display=swap');

    /* ── Base ──────────────────────────────────────────── */
    .block-container {{
        max-width: 1060px;
        padding: 1.2rem 1.5rem 2rem;
    }}

    /* ── Responsive ────────────────────────────────────── */
    @media (max-width: 768px) {{
        .block-container {{ max-width: 100%; padding: 2.5rem 0.8rem 1.5rem; }}
        .style-grid {{ grid-template-columns: 1fr 1fr !important; }}
        .hero-title {{ font-size: 1.3rem !important; }}
        .hero-sub   {{ font-size: 0.95rem !important; }}
        .brand-header .title {{ font-size: 1.5rem !important; }}
    }}
    @media (max-width: 480px) {{
        .style-grid {{ grid-template-columns: 1fr !important; }}
        .brand-header .logo {{ width: 36px !important; height: 36px !important; }}
        .brand-header .title {{ font-size: 1.2rem !important; }}
    }}

    /* ── Sidebar ───────────────────────────────────────── */
    section[data-testid="stSidebar"] {{ min-width: 260px; max-width: 310px; }}

    /* ── Sidebar open button — make it visible on mobile ─ */
    button[data-testid="stBaseButton-headerNoPadding"] {{
        background: #111 !important;
        border: 2px solid {BRAND_GREEN} !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        box-shadow: 0 2px 8px rgba(46,204,64,0.3) !important;
    }}
    button[data-testid="stBaseButton-headerNoPadding"] svg {{
        fill: {BRAND_GREEN} !important;
        width: 22px !important;
        height: 22px !important;
    }}

    /* ── ASCII art box ─────────────────────────────────── */
    .ascii-box {{
        font-family: 'Courier New', Consolas, 'Liberation Mono', monospace;
        white-space: pre; overflow-x: auto;
        background: {_t['ascii_bg']}; color: {_t['ascii_fg']};
        padding: 1rem; border-radius: 0.5rem;
        border: 1px solid {_t['border']};
        max-height: 520px; overflow-y: auto;
    }}

    /* ── Colour swatches ───────────────────────────────── */
    .swatch {{ border-radius: 8px; margin-bottom: 4px; }}

    /* ── Brand header ──────────────────────────────────── */
    .brand-header {{
        display: flex; align-items: center; gap: 14px; margin-bottom: 0.15rem;
    }}
    .brand-header .logo {{
        width: 48px; height: 48px; border-radius: 6px; object-fit: cover;
    }}
    .brand-header .title {{
        font-size: 2rem; font-family: 'Rock Salt', cursive;
        letter-spacing: 1px; color: {_t['fg']}; margin: 0;
    }}
    .brand-dollar {{ color: {BRAND_GREEN}; }}
    .brand-sub {{ font-size: 0.95rem; color: {_t['fg_muted']}; margin: 0 0 0.15rem; }}
    .brand-credit {{
        font-size: 0.82rem; color: {BRAND_COLOR}; font-weight: 600; margin: 0 0 1rem;
    }}

    /* ── Hero section ──────────────────────────────────── */
    .hero-box {{
        background: {_t['hero_bg']}; border-radius: 12px;
        padding: 2rem 1.5rem; text-align: center;
        margin-bottom: 1.5rem; border: 1px solid {_t['hero_bdr']};
    }}
    .hero-title {{
        font-size: 1.6rem; font-family: 'Rock Salt', cursive;
        color: {BRAND_COLOR}; margin: 0 0 0.5rem;
    }}
    .hero-dollar {{ color: {BRAND_GREEN}; }}
    .hero-sub {{ font-size: 1.05rem; color: {_t['hero_sub']}; margin: 0 0 0.3rem; }}
    .hero-desc {{ font-size: 0.85rem; color: {_t['hero_desc']}; margin: 0; }}

    /* ── Style cards grid ──────────────────────────────── */
    .style-grid {{
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 12px; margin-bottom: 1.5rem;
    }}
    .style-card {{
        text-align: center; padding: 1rem 0.6rem;
        border: 1px solid {_t['border']}; border-radius: 10px;
        background: {_t['surface']}; transition: all 0.2s;
        box-shadow: {_t['card_shadow']};
        cursor: pointer;
    }}
    .style-card:hover {{
        border-color: {BRAND_COLOR};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(200,168,78,0.15);
    }}
    .style-card .icon {{ font-size: 1.8rem; }}
    .style-card .name {{
        font-weight: 700; font-size: 0.9rem;
        margin: 0.35rem 0 0.15rem; color: {_t['fg']};
    }}
    .style-card .desc {{
        font-size: 0.75rem; color: {_t['fg_dim']}; line-height: 1.3;
    }}
    .style-card .try-label {{
        font-size: 0.7rem; color: {BRAND_GREEN}; font-weight: 600;
        margin-top: 0.4rem; letter-spacing: 0.5px;
    }}

    /* ── Sample banner ─────────────────────────────────── */
    .sample-banner {{
        background: linear-gradient(90deg, {BRAND_GREEN}22, {BRAND_COLOR}22);
        border: 1px solid {BRAND_GREEN}44;
        border-radius: 8px; padding: 0.6rem 1rem;
        margin-bottom: 1rem; display: flex;
        align-items: center; justify-content: space-between;
        flex-wrap: wrap; gap: 0.5rem;
    }}
    .sample-banner .text {{
        font-size: 0.88rem; color: {_t['fg']};
    }}

    /* ── Footer ────────────────────────────────────────── */
    .app-footer {{
        text-align: center; padding: 1rem 0 0.5rem; font-size: 0.78rem;
        color: {_t['footer_fg']}; border-top: 1px solid {_t['footer_bdr']};
        margin-top: 1.5rem;
    }}
    .app-footer a {{ color: {BRAND_COLOR}; text-decoration: none; }}
    .app-footer a:hover {{ text-decoration: underline; }}

    /* ── Tab polish ─────────────────────────────────────── */
    .stTabs [data-baseweb="tab-panel"] {{ padding-top: 0.8rem; }}

    /* ── Hide Streamlit chrome ──────────────────────────── */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def img_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def render_brand_header() -> None:
    import base64
    logo_b64 = ""
    if LOGO_PATH.exists():
        logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
    logo_html = (
        f'<img class="logo" src="data:image/png;base64,{logo_b64}" alt="Logo">'
        if logo_b64 else ""
    )
    st.markdown(
        f'<div class="brand-header">'
        f'  {logo_html}'
        f'  <p class="title"><span class="brand-dollar">$</span>entimize.ai</p>'
        f'</div>'
        f'<p class="brand-sub"><b>Turn any image into art.</b> — Image Art Studio</p>'
        f'<p class="brand-credit">{BRAND_NAME} IP — Created {CREATED_DATE}</p>',
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        f'<div class="app-footer">'
        f'  $entimize.ai v{APP_VERSION} · '
        f'  <a href="https://github.com/EconomicIntegrityLLC" target="_blank">{BRAND_NAME}</a> · '
        f'  Powered by '
        f'  <a href="https://github.com/vinta/awesome-python" target="_blank">Awesome Python</a>'
        f'  open-source packages'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar — image input ────────────────────────────────────────────────────

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=60)
    st.markdown(
        '<h1 style="font-family:\'Rock Salt\',cursive;font-size:1.5rem;">'
        '<span style="color:#2ecc40;">$</span>entimize.ai</h1>',
        unsafe_allow_html=True,
    )
    st.caption("Image Art Studio")
    st.divider()

    input_mode = st.radio(
        "Choose input", ["📁 Upload", "📷 Camera"], horizontal=True
    )

    source: Image.Image | None = None

    if input_mode == "📁 Upload":
        upload = st.file_uploader(
            "Drop an image here",
            type=["png", "jpg", "jpeg", "webp", "bmp"],
        )
        if upload:
            source = Image.open(upload).convert("RGB")
            st.session_state.use_sample = False
    else:
        cam = st.camera_input("Snap a photo")
        if cam:
            source = Image.open(cam).convert("RGB")
            st.session_state.use_sample = False

    if source:
        st.divider()
        st.image(source, caption=f"Original  •  {source.width} × {source.height}")

    st.divider()
    st.toggle("🌙 Dark mode", value=st.session_state.dark_mode,
              key="dark_toggle",
              on_change=lambda: st.session_state.update(
                  dark_mode=not st.session_state.dark_mode))
    st.caption(f"© 2026 {BRAND_NAME}")


# ── Load sample if requested ─────────────────────────────────────────────────

if source is None and st.session_state.use_sample and SAMPLE_PATH.exists():
    source = Image.open(SAMPLE_PATH).convert("RGB")


# ── Landing page (no image loaded) ───────────────────────────────────────────

if source is None:
    render_brand_header()

    st.markdown(
        '<div class="hero-box">'
        '  <p class="hero-title"><span class="hero-dollar">$</span>entimize.ai — Image Art Studio</p>'
        '  <p class="hero-sub">Upload a photo or snap a selfie. Get instant art.</p>'
        '  <p class="hero-desc">No AI APIs. No accounts. No cost. Pure Python open-source.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    if SAMPLE_PATH.exists():
        st.markdown(
            f'<p style="text-align:center;font-size:0.9rem;color:{_t["fg_muted"]};">'
            f'👇 Click any style below to <b>try it with a sample photo</b> before uploading your own</p>',
            unsafe_allow_html=True,
        )

    row1 = st.columns(3, gap="medium")
    row2 = st.columns(3, gap="medium")
    row3 = st.columns(3, gap="medium")
    all_cols = list(row1) + list(row2) + list(row3)

    for i, (icon, name, desc) in enumerate(STYLES):
        with all_cols[i]:
            if st.button(
                f"{icon}\n{name}",
                key=f"try_{i}",
                use_container_width=True,
                help=desc,
            ):
                st.session_state.use_sample = True
                st.rerun()

    render_footer()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  Image loaded — show the art tabs
# ══════════════════════════════════════════════════════════════════════════════

render_brand_header()

if st.session_state.use_sample:
    scol1, scol2 = st.columns([5, 1])
    with scol1:
        st.markdown(
            '<div class="sample-banner">'
            '<span class="text">🖼️ Viewing sample photo — upload your own in the sidebar for the full experience!</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    with scol2:
        if st.button("✕ Clear sample", use_container_width=True):
            st.session_state.use_sample = False
            st.rerun()

tab_px, tab_asc, tab_sk, tab_qt, tab_pop, tab_pal, tab_cbn, tab_mos, tab_gli = st.tabs(TAB_LABELS)


# ── 1  Pixel Art ─────────────────────────────────────────────────────────────

with tab_px:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        px_block = st.slider("Block size", 4, 40, 12, key="px_block",
                             help="Larger → chunkier pixels")
    with c2:
        px_colors = st.slider("Colour count", 2, 64, 16, key="px_colors",
                              help="Fewer → more retro")
    with st.spinner("Pixelating…"):
        px_result = pixelate(source, px_block, px_colors)
    st.image(px_result, width="stretch")
    st.download_button(
        "⬇️ Download pixel art", img_to_bytes(watermark(px_result)),
        "$entimize_pixel.png", "image/png", key="dl_px",
    )


# ── 2  ASCII Art ─────────────────────────────────────────────────────────────

with tab_asc:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        a_width = st.slider("Width (characters)", 60, 200, 120, key="a_width")
    with c2:
        a_charset = st.selectbox(
            "Character set",
            ["standard", "blocks", "minimal", "detailed"],
            key="a_charset",
            help="blocks → Unicode ░▒▓█  •  detailed → 70-char gradient",
        )
    with st.spinner("Converting to text…"):
        ascii_str = to_ascii(source, a_width, a_charset)
    font_px = max(3, min(7, int(700 / a_width * 8)))
    escaped = html_mod.escape(ascii_str)
    st.markdown(
        f'<div class="ascii-box" style="font-size:{font_px}px;'
        f'line-height:{font_px + 1}px;">{escaped}</div>',
        unsafe_allow_html=True,
    )
    st.download_button(
        "⬇️ Download .txt", watermark_text(ascii_str).encode("utf-8"),
        "$entimize_ascii.txt", "text/plain", key="dl_ascii",
    )


# ── 3  Sketch ────────────────────────────────────────────────────────────────

with tab_sk:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        sk_sigma = st.slider("Smoothing (σ)", 0.5, 5.0, 2.0, 0.5, key="sk_sigma",
                             help="Lower → finer detail  •  Higher → bolder lines")
    with c2:
        sk_inv = st.checkbox("White background", True, key="sk_inv")
    with st.spinner("Sketching…"):
        sk_result = sketch(source, sk_sigma, sk_inv)
    st.image(sk_result, width="stretch")
    st.download_button(
        "⬇️ Download sketch", img_to_bytes(watermark(sk_result)),
        "$entimize_sketch.png", "image/png", key="dl_sk",
    )


# ── 4  Quadtree ──────────────────────────────────────────────────────────────

with tab_qt:
    c1, c2, c3 = st.columns([1, 1, 1], gap="medium")
    with c1:
        qt_depth = st.slider("Max depth", 3, 8, 6, key="qt_depth",
                             help="Higher → more detail")
    with c2:
        qt_thresh = st.slider("Detail threshold", 5, 50, 15, key="qt_thresh",
                              help="Lower → finer splits")
    with c3:
        qt_border = st.checkbox("Show cell borders", True, key="qt_border")
    with st.spinner("Decomposing…"):
        qt_result = quadtree(source, qt_depth, qt_thresh, qt_border)
    st.image(qt_result, width="stretch")
    st.download_button(
        "⬇️ Download quadtree", img_to_bytes(watermark(qt_result)),
        "$entimize_quadtree.png", "image/png", key="dl_qt",
    )


# ── 5  Pop Art ───────────────────────────────────────────────────────────────

with tab_pop:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        pop_levels = st.slider("Colour levels", 2, 12, 4, key="pop_levels",
                               help="Fewer → bolder, flatter bands")
    with c2:
        pop_sat = st.slider("Saturation boost", 0.5, 3.0, 1.5, 0.1, key="pop_sat",
                            help="Crank it for full Warhol")
    with st.spinner("Posterising…"):
        pop_result = posterize(source, pop_levels, pop_sat)
    st.image(pop_result, width="stretch")
    st.download_button(
        "⬇️ Download pop art", img_to_bytes(watermark(pop_result)),
        "$entimize_popart.png", "image/png", key="dl_pop",
    )


# ── 6  Colour Palette ───────────────────────────────────────────────────────

with tab_pal:
    pal_n = st.slider("Colours to extract", 3, 12, 6, key="pal_n")
    with st.spinner("Extracting palette…"):
        palette = extract_palette(source, pal_n)
    total_px = sum(cnt for _, cnt in palette)

    swatch_cols = st.columns(len(palette), gap="small")
    for i, ((r, g, b), cnt) in enumerate(palette):
        hx = f"#{r:02x}{g:02x}{b:02x}"
        pct = cnt / total_px * 100
        with swatch_cols[i]:
            st.markdown(
                f'<div class="swatch" style="background:{hx};height:60px;"></div>'
                f'<p style="text-align:center;font-size:11px;'
                f'font-weight:600;margin:2px 0 0;">{hx}</p>'
                f'<p style="text-align:center;font-size:10px;'
                f'color:#888;margin:0;">{pct:.1f}%</p>',
                unsafe_allow_html=True,
            )

    hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for (r, g, b), _ in palette]
    counts = [c for _, c in palette]
    fig = go.Figure(
        go.Bar(
            x=hex_colors, y=counts, marker_color=hex_colors,
            text=[f"{c / total_px * 100:.1f}%" for c in counts],
            textposition="outside",
        )
    )
    fig.update_layout(
        xaxis_title="Colour", yaxis_title="Pixels",
        height=300, margin=dict(t=20, b=40, l=50, r=20),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#ccc" if _dark else "#333",
    )
    st.plotly_chart(fig, key="palette_chart")
    st.code(" | ".join(hex_colors), language=None)


# ── 7  Color By Number ──────────────────────────────────────────────────────

with tab_cbn:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        cbn_colors = st.slider("Number of colours", 4, 16, 8, key="cbn_colors",
                               help="Fewer → simpler to colour, more → finer detail")
    with c2:
        cbn_peek = st.checkbox("Show completed preview", False, key="cbn_peek")
    with st.spinner("Generating colour-by-number template…"):
        cbn_outline, cbn_filled, cbn_palette = color_by_number(source, cbn_colors)

    legend_cols = st.columns(min(len(cbn_palette), 12), gap="small")
    for i, (num, (r, g, b)) in enumerate(cbn_palette):
        hx = f"#{r:02x}{g:02x}{b:02x}"
        with legend_cols[i % len(legend_cols)]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="width:22px;height:22px;border-radius:4px;'
                f'background:{hx};border:1px solid #444;flex-shrink:0;"></div>'
                f'<span style="font-weight:700;font-size:0.85rem;">{num}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if cbn_peek:
        col_a, col_b = st.columns(2, gap="medium")
        with col_a:
            st.caption("Template")
            st.image(cbn_outline, width="stretch")
        with col_b:
            st.caption("Completed")
            st.image(cbn_filled, width="stretch")
    else:
        st.image(cbn_outline, width="stretch")

    dl1, dl2 = st.columns(2, gap="medium")
    with dl1:
        st.download_button(
            "⬇️ Download template", img_to_bytes(watermark(cbn_outline)),
            "$entimize_coloring.png", "image/png", key="dl_cbn",
        )
    with dl2:
        st.download_button(
            "⬇️ Download answer key", img_to_bytes(watermark(cbn_filled)),
            "$entimize_coloring_key.png", "image/png", key="dl_cbn_key",
        )


# ── 8  Mosaic / Stained Glass ────────────────────────────────────────────────

with tab_mos:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        mos_cells = st.slider("Number of cells", 50, 800, 300, 25, key="mos_cells",
                              help="More cells → finer detail")
    with c2:
        mos_border = st.slider("Border width", 0, 4, 2, key="mos_border",
                               help="0 = no borders")
    with st.spinner("Tessellating…"):
        mos_result = mosaic(source, mos_cells, mos_border)
    st.image(mos_result, width="stretch")
    st.download_button(
        "⬇️ Download mosaic", img_to_bytes(watermark(mos_result)),
        "$entimize_mosaic.png", "image/png", key="dl_mos",
    )


# ── 9  Glitch Art ───────────────────────────────────────────────────────────

with tab_gli:
    c1, c2, _ = st.columns([1, 1, 1], gap="medium")
    with c1:
        gli_intensity = st.slider("Intensity", 1, 15, 5, key="gli_int",
                                  help="Higher → more chaotic")
    with c2:
        gli_seed = st.slider("Variation", 1, 100, 42, key="gli_seed",
                             help="Change for a different glitch pattern")
    with st.spinner("Glitching…"):
        gli_result = glitch(source, gli_intensity, gli_seed)
    st.image(gli_result, width="stretch")
    st.download_button(
        "⬇️ Download glitch", img_to_bytes(watermark(gli_result)),
        "$entimize_glitch.png", "image/png", key="dl_gli",
    )


# ── Footer (all pages) ──────────────────────────────────────────────────────

render_footer()
