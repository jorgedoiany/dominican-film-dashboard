import streamlit as st
import html
from contextlib import contextmanager
from textwrap import dedent
from streamlit_option_menu import option_menu

# ─────────────────────────────────────────
# DESIGN TOKENS
# ─────────────────────────────────────────
BG         = '#FFFFFF'
SIDEBAR_BG = '#F8F9FA'
CARD_BG    = '#FFFFFF'
TEXT       = '#1A1A2E'
SUBTEXT    = '#6B7280'
BORDER     = '#E5E7EB'
ACCENT     = '#002D62'
ACCENT2    = '#CE1126'


def html_block(html: str) -> None:
    st.markdown(dedent(html).strip(), unsafe_allow_html=True)


def escape_html(value: object) -> str:
    return html.escape(str(value), quote=True)


def sanitize_insight_html(insight: str) -> str:
    escaped = escape_html(insight)
    escaped = escaped.replace("&lt;strong&gt;", "<strong>")
    escaped = escaped.replace("&lt;/strong&gt;", "</strong>")
    escaped = escaped.replace("&lt;br&gt;", "<br>")
    escaped = escaped.replace("&lt;br/&gt;", "<br/>")
    escaped = escaped.replace("&lt;br /&gt;", "<br />")
    return escaped


# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
def apply_css() -> None:
    st.markdown(f"""
        <style>
            /* ── Global ── */
            .stApp {{
                background-color: {BG};
                color: {TEXT};
            }}

            /* ── Sidebar ── */
            [data-testid="stSidebar"] {{
                background-color: {SIDEBAR_BG} !important;
                border-right: 1px solid {BORDER};
            }}
            [data-testid="stSidebar"] * {{
                color: {TEXT} !important;
            }}

            /* ── Radio buttons (navigation) ── */
            [data-testid="stSidebar"] .stRadio label {{
                color: {TEXT} !important;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 12px;
                border-radius: 8px;
                display: block;
                cursor: pointer;
                transition: all 0.2s;
            }}
            [data-testid="stSidebar"] .stRadio label:hover {{
                background-color: {BORDER};
                color: {ACCENT} !important;
            }}

            /* ── KPI Cards ── */
            .kpi-card {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .kpi-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            }}
            .kpi-label {{
                font-size: 11px;
                font-weight: 600;
                color: {SUBTEXT};
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 10px;
            }}
            .kpi-value {{
                font-size: 32px;
                font-weight: 700;
                color: {ACCENT};
                margin-bottom: 6px;
                line-height: 1;
            }}
            .kpi-subtitle {{
                font-size: 12px;
                color: {SUBTEXT};
            }}
            .kpi-accent {{
                display: inline-block;
                width: 4px;
                height: 32px;
                background-color: {ACCENT2};
                border-radius: 2px;
                margin-right: 12px;
                vertical-align: middle;
            }}

            /* ── Chart containers (scoped to chart cards) ── */
            [data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-header) {{
                border-radius: 16px !important;
                border: 1px solid {BORDER} !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
                padding: 8px !important;
            }}

            /* ── Chart card caption ── */
            [data-testid="stVerticalBlockBorderWrapper"]:has(.chart-card-header) [data-testid="stCaptionContainer"] {{
                min-height: 36px;
            }}

            /* ── Page title ── */
            .page-title {{
                font-size: 28px;
                font-weight: 800;
                color: {TEXT};
                margin-bottom: 4px;
            }}
            .page-subtitle {{
                font-size: 14px;
                color: {SUBTEXT};
                margin-bottom: 24px;
            }}

            /* ── Divider ── */
            .divider {{
                border: none;
                border-top: 1px solid {BORDER};
                margin: 16px 0;
            }}

            /* ── Hide streamlit branding ── */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: visible;}}

            /* ── Sidebar text ── */
            .sidebar-logo {{
                font-size: 16px;
                font-weight: 700;
                color: {ACCENT} !important;
                margin-bottom: 4px;
            }}
            .sidebar-meta {{
                font-size: 11px;
                color: {SUBTEXT} !important;
            }}
        </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# COMPONENTS
# ─────────────────────────────────────────
def kpi_card(label: str, value: str, subtitle: str = "") -> None:
    safe_label = escape_html(label)
    safe_value = escape_html(value)
    safe_subtitle = escape_html(subtitle)

    st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>{safe_label}</div>
            <div style='display:flex;align-items:center;'>
                <span class='kpi-accent'></span>
                <span class='kpi-value'>{safe_value}</span>
            </div>
            <div class='kpi-subtitle'>{safe_subtitle}</div>
        </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    safe_title = escape_html(title)
    safe_subtitle = escape_html(subtitle)
    st.markdown(f"<div class='page-title'>{safe_title}</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='page-subtitle'>{safe_subtitle}</div>",
                unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)


def empty_state(title: str, message: str) -> None:
    safe_title = escape_html(title)
    safe_message = escape_html(message)
    html_block(f"""
        <div style='border:1px solid #E5E7EB;background-color:#F8F9FA;
        border-radius:12px;padding:16px;margin:8px 0 16px 0;'>
            <div style='font-size:14px;font-weight:700;color:#1A1A2E;
            margin-bottom:4px;'>{safe_title}</div>
            <div style='font-size:13px;color:#6B7280;'>{safe_message}</div>
        </div>
    """)

def key_insight_row(insights: list, columns: str = "1fr 1fr") -> None:
    blocks = []
    for insight in insights:
        safe_insight = sanitize_insight_html(str(insight))
        blocks.append(
            (
                "<div style='background-color:#F0F4FF;border-left:4px solid #002D62;"
                "border-radius:0 8px 8px 0;padding:12px 16px;'>"
                "<span style='font-size:12px;font-weight:600;color:#002D62;"
                "text-transform:uppercase;letter-spacing:0.05em;'>Key Insight</span><br>"
                f"<span style='font-size:13px;color:#1A1A2E;'>{safe_insight}</span>"
                "</div>"
            )
        )

    items = "".join(blocks)
    html = (
        f"<div style='display:grid;grid-template-columns:{columns};gap:16px;'>"
        f"{items}"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


@contextmanager
def chart_card(title: str, subtitle: str, header_height: int = 56):
    safe_title = escape_html(title)
    safe_subtitle = escape_html(subtitle)
    with st.container(border=True):
        html_block(f"""
            <div class='chart-card-header' style='height:{header_height}px;margin-bottom:2px;overflow:hidden;'>
                <div style='font-size:14px;font-weight:600;color:#1A1A2E;line-height:1.25;overflow:hidden;'>
                    {safe_title}
                </div>
                <div style='font-size:10px;color:#6B7280;line-height:1.35;margin-top:4px;overflow:hidden;'>
                    {safe_subtitle}
                </div>
            </div>
        """)
        yield


def render_sidebar(df) -> str:
    with st.sidebar:
        st.markdown("""
            <div style='padding:8px 0 16px 0;'>
                <div style='font-size:14px;font-weight:600;color:#CE1126;
                text-transform:uppercase;letter-spacing:0.15em;
                margin-bottom:4px;'>Dominican Republic</div>
                <div style='font-size:24px;font-weight:800;color:#002D62;
                letter-spacing:0.02em;line-height:1.2;'>Film Industry</div>
                <div style='width:32px;height:3px;background-color:#CE1126;
                border-radius:2px;margin-top:8px;'></div>
            </div>
        """, unsafe_allow_html=True)

        if 'page' not in st.session_state:
            st.session_state.page = 'Overview'

        selected = option_menu(
            menu_title=None,
            options=[
                "Overview",
                "Genres",
                "Industry Players",
                "Co-productions",
                "Budget",
                "Film Catalog"
            ],
            icons=[
                "house",
                "film",
                "people",
                "globe",
                "cash-stack",
                "collection"
            ],
            default_index=[
                "Overview",
                "Genres",
                "Industry Players",
                "Co-productions",
                "Budget",
                "Film Catalog"
            ].index(st.session_state.page),
            styles={
                "container": {
                    "padding": "0",
                    "background-color": "#F8F9FA"
                },
                "icon": {
                    "color": "#6B7280",
                    "font-size": "15px"
                },
                "nav-link": {
                    "font-size": "14px",
                    "font-weight": "400",
                    "color": "#1A1A2E",
                    "padding": "10px 12px",
                    "border-radius": "8px",
                    "--hover-color": "#E5E7EB"
                },
                "nav-link-selected": {
                    "background-color": "#002D62",
                    "color": "#FFFFFF",
                    "font-weight": "600",
                    "icon-color": "#FFFFFF"
                }
            }
        )

        if selected != st.session_state.page:
            st.session_state.page = selected
            st.rerun()

    return st.session_state.page