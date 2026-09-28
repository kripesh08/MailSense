"""
ui_components.py — Reusable Streamlit UI Rendering Helpers
===========================================================
All HTML/CSS constants and tab-rendering logic live here so that
app.py only needs to orchestrate state and call these helpers.
"""

import streamlit as st


# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ──────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary:    #0d1117;
    --bg-card:       #161b22;
    --bg-card-hover: #1c2330;
    --border:        #30363d;
    --accent-blue:   #58a6ff;
    --accent-purple: #bc8cff;
    --accent-green:  #3fb950;
    --accent-red:    #f85149;
    --text-primary:  #e6edf3;
    --text-muted:    #8b949e;
}

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
.stApp                      { background: var(--bg-primary); color: var(--text-primary); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: #21262d !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] label { color: var(--text-muted) !important; font-size: 0.82rem; }

/* ── Fetch button ── */
div[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.2rem !important;
    width: 100% !important;
    transition: opacity 0.2s ease, transform 0.15s ease !important;
    box-shadow: 0 0 12px rgba(46,160,67,0.35) !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    color: var(--text-muted) !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent-blue) !important;
    border-bottom: 2px solid var(--accent-blue) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: background 0.2s ease !important;
}
.streamlit-expanderHeader:hover { background: var(--bg-card-hover) !important; }
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 1rem !important;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); border-color: var(--accent-blue); }
.metric-number { font-size: 2.4rem; font-weight: 800; line-height: 1; }
.metric-label  { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;
                 letter-spacing: 0.05em; text-transform: uppercase; }

/* ── Welcome card ── */
.welcome-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2330 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    text-align: center;
    margin: 3rem auto;
    max-width: 640px;
}
.welcome-icon  { font-size: 4rem; margin-bottom: 1rem; }
.welcome-title { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.6rem; }
.welcome-sub   { font-size: 1rem; color: var(--text-muted); line-height: 1.6; }

/* ── Polarity / subjectivity badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-positive { background: rgba(63,185,80,0.18);  color: #3fb950; border: 1px solid #3fb950; }
.badge-negative { background: rgba(248,81,73,0.18);  color: #f85149; border: 1px solid #f85149; }
.badge-neutral  { background: rgba(139,148,158,0.18); color: #8b949e; border: 1px solid #8b949e; }
.badge-read     { background: rgba(63,185,80,0.18);  color: #3fb950; border: 1px solid #3fb950; }
.badge-unread   { background: rgba(88,166,255,0.18); color: #58a6ff; border: 1px solid #58a6ff; }

/* ── Email body viewer ── */
.email-body {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    line-height: 1.7;
    color: #cdd9e5;
    max-height: 380px;
    overflow-y: auto;
    margin-top: 0.6rem;
}

/* ── Logout button ── */
div.logout-btn button,
div[data-testid="stSidebar"] div.logout-btn button {
    background: #21262d !important;
    border: 1px solid #da3633 !important;
    border-radius: 8px !important;
    padding: 0.55rem 1rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

div.logout-btn button p,
div.logout-btn button span,
div.logout-btn button div,
div[data-testid="stSidebar"] div.logout-btn button p,
div[data-testid="stSidebar"] div.logout-btn button span {
    color: #ff7b72 !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
}

div.logout-btn button:hover,
div[data-testid="stSidebar"] div.logout-btn button:hover {
    background: #da3633 !important;
    border-color: #f85149 !important;
}

div.logout-btn button:hover p,
div.logout-btn button:hover span,
div[data-testid="stSidebar"] div.logout-btn button:hover p,
div[data-testid="stSidebar"] div.logout-btn button:hover span {
    color: #ffffff !important;
}

#MainMenu { display: none !important; }
footer { display: none !important; }

/* ── Streamlit Header & Sidebar Controls ── */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3.5rem !important;
    z-index: 1000 !important;
}

/* ── Sidebar reopen toggle button when sidebar is collapsed (Streamlit 1.x) ── */
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    align-items: center !important;
    justify-content: center !important;
    color: #e6edf3 !important;
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    width: 2.4rem !important;
    height: 2.4rem !important;
    top: 0.75rem !important;
    left: 0.85rem !important;
    position: fixed !important;
    z-index: 9999999 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.65) !important;
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.15s ease !important;
}

[data-testid="stExpandSidebarButton"]:hover,
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    background: #21262d !important;
    border-color: #58a6ff !important;
    transform: scale(1.06) !important;
}

[data-testid="stExpandSidebarButton"] button,
[data-testid="collapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] button {
    background: transparent !important;
    border: none !important;
    color: #58a6ff !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
}

[data-testid="stExpandSidebarButton"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stExpandSidebarButton"] span {
    fill: #58a6ff !important;
    color: #58a6ff !important;
    width: 1.3rem !important;
    height: 1.3rem !important;
}

[data-testid="stSidebarCollapseButton"] {
    color: #8b949e !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    color: #58a6ff !important;
}
</style>
"""


# ──────────────────────────────────────────────────────────────────────────────
# COMPONENT RENDERERS
# ──────────────────────────────────────────────────────────────────────────────

def render_header() -> None:
    """Render the MailSense gradient header."""
    st.markdown(
        """
        <div style="padding:0.5rem 0 1.5rem 0; border-bottom:1px solid #30363d; margin-bottom:1.8rem;">
            <h1 style="margin:0; font-size:2.2rem; font-weight:800;
                       background: linear-gradient(90deg, #58a6ff, #bc8cff);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                📊 MailSense
            </h1>
            <p style="margin:0.35rem 0 0 0; color:#8b949e; font-size:1rem; font-weight:400;">
                Intelligent Email Emotion Triage &amp; Analytics Portal
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_screen() -> None:
    """Render the pre-fetch welcome card and emotion preview tiles."""
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-icon">👋</div>
            <div class="welcome-title">Welcome to MailSense</div>
            <div class="welcome-sub">
                Enter your email credentials in the sidebar and click
                <strong style="color:#58a6ff;">Fetch &amp; Analyze Emails</strong>
                to let MailSense triage your unread inbox by emotion — so you can
                tackle the most important messages first.
            </div>
        </div>

        <div style="display:flex; gap:1.2rem; justify-content:center; flex-wrap:wrap; margin-top:2rem;">
            <div class="metric-card" style="min-width:160px;">
                <div class="metric-number" style="color:#3fb950;">😊</div>
                <div class="metric-label">Happy</div>
            </div>
            <div class="metric-card" style="min-width:160px;">
                <div class="metric-number" style="color:#8b949e;">😐</div>
                <div class="metric-label">Normal</div>
            </div>
            <div class="metric-card" style="min-width:160px;">
                <div class="metric-number" style="color:#58a6ff;">😢</div>
                <div class="metric-label">Sad</div>
            </div>
            <div class="metric-card" style="min-width:160px;">
                <div class="metric-number" style="color:#f85149;">😠</div>
                <div class="metric-label">Angry</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_summary_metrics(total: int, happy: int, normal: int, sad: int, angry: int) -> None:
    """Render the five summary metric cards above the tabs."""
    st.markdown(
        f"""
        <div style="display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:2rem;">
            <div class="metric-card" style="flex:1; min-width:130px;">
                <div class="metric-number" style="color:#58a6ff;">{total}</div>
                <div class="metric-label">Total Unread</div>
            </div>
            <div class="metric-card" style="flex:1; min-width:130px;">
                <div class="metric-number" style="color:#3fb950;">{happy}</div>
                <div class="metric-label">😊 Happy</div>
            </div>
            <div class="metric-card" style="flex:1; min-width:130px;">
                <div class="metric-number" style="color:#8b949e;">{normal}</div>
                <div class="metric-label">😐 Normal</div>
            </div>
            <div class="metric-card" style="flex:1; min-width:130px;">
                <div class="metric-number" style="color:#58a6ff;">{sad}</div>
                <div class="metric-label">😢 Sad</div>
            </div>
            <div class="metric-card" style="flex:1; min-width:130px;">
                <div class="metric-number" style="color:#f85149;">{angry}</div>
                <div class="metric-label">😠 Angry</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_email_list(
    tab,
    email_list: list[dict],
    category: str = "default",
    on_mark_read = None,
    on_mark_multiple = None,
) -> None:
    """
    Render a list of classified emails inside a given Streamlit tab.

    Each email is wrapped in an st.expander showing subject + sender.
    Inside: date, polarity badge, subjectivity badge, read/unread status,
    action button to mark as read in Gmail, and the email body.
    """
    with tab:
        if not email_list:
            st.markdown(
                "<p style='color:#8b949e; text-align:center; padding:2rem 0;'>"
                "No emails in this category.</p>",
                unsafe_allow_html=True,
            )
            return

        unread_emails = [e for e in email_list if not e.get("is_read")]
        if unread_emails and on_mark_multiple:
            col_bar_l, col_bar_r = st.columns([3, 1])
            with col_bar_l:
                st.markdown(
                    f"<span style='font-size:0.85rem; color:#8b949e;'>"
                    f"Showing {len(email_list)} emails ({len(unread_emails)} unread in mailbox)</span>",
                    unsafe_allow_html=True,
                )
            with col_bar_r:
                if st.button(
                    f"✓ Mark All {len(unread_emails)} as Read",
                    key=f"btn_mark_tab_{category}",
                    help=f"Mark all {len(unread_emails)} unread emails in this category as read in Gmail",
                ):
                    on_mark_multiple([e["uid"] for e in unread_emails if e.get("uid")])
            st.markdown("<hr style='border:none; border-top:1px solid #21262d; margin:0.6rem 0 1rem 0;'>", unsafe_allow_html=True)

        for idx, em in enumerate(email_list):
            polarity = em["polarity"]
            subject  = em["subject"] or "(No Subject)"
            sender   = em["sender"]  or "Unknown"
            is_read  = em.get("is_read", False)
            uid      = em.get("uid", f"{category}_{idx}")

            if polarity > 0.05:
                badge_cls, badge_lbl = "badge-positive", f"+{polarity}"
            elif polarity < -0.05:
                badge_cls, badge_lbl = "badge-negative", str(polarity)
            else:
                badge_cls, badge_lbl = "badge-neutral",  str(polarity)

            status_icon = "✓" if is_read else "🔵"
            expander_title = f"{status_icon} Subject: {subject} | From: {sender}"

            with st.expander(expander_title, expanded=False):
                col_l, col_r = st.columns([2, 2])
                with col_l:
                    date_str = f"📅 {em['date']}" if em.get("date") else ""
                    st.markdown(
                        f"<span style='font-size:0.78rem; color:#8b949e;'>{date_str}</span>",
                        unsafe_allow_html=True,
                    )
                with col_r:
                    read_badge = (
                        "<span class='badge badge-read'>✓ Read in Mailbox</span>"
                        if is_read else
                        "<span class='badge badge-unread'>🔵 Unread in Mailbox</span>"
                    )
                    st.markdown(
                        f"<div style='text-align:right;'>"
                        f"<span class='badge {badge_cls}'>Polarity: {badge_lbl}</span>&nbsp;"
                        f"<span class='badge badge-neutral'>Subj: {em['subjectivity']}</span>&nbsp;"
                        f"{read_badge}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    f"<div class='email-body'>{em['body']}</div>",
                    unsafe_allow_html=True,
                )

                if not is_read and on_mark_read:
                    act_l, act_r = st.columns([4, 1.2])
                    with act_r:
                        if st.button(
                            "✉️ Mark as Read in Gmail",
                            key=f"btn_mark_single_{category}_{uid}",
                            help="Mark this email as read in your Gmail inbox",
                        ):
                            on_mark_read(em)

