"""
app.py — MailSense Streamlit Entry Point
=========================================
Orchestrates the Streamlit UI: page config, sidebar, session state,
and the main dashboard.  All business logic lives in separate modules:

    classifier.py    — NRCLex + TextBlob emotion engine
    mail_client.py   — IMAP connection and MIME parsing
    ui_components.py — CSS, header, metric cards, email list renderer
"""

import imaplib
import streamlit as st

from mail_client   import fetch_and_analyze, mark_as_read, mark_multiple_as_read
from ui_components import (
    GLOBAL_CSS,
    render_header,
    render_welcome_screen,
    render_summary_metrics,
    render_email_list,
)

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the first Streamlit call)
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MailSense — Email Emotion Triage",
    page_icon="📨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ──────────────────────────────────────────────────────────────
if "is_authenticated" not in st.session_state: st.session_state.is_authenticated = False
if "auth_email"       not in st.session_state: st.session_state.auth_email       = ""
if "auth_password"    not in st.session_state: st.session_state.auth_password    = ""
if "emails"           not in st.session_state: st.session_state.emails           = None
if "fetch_error"      not in st.session_state: st.session_state.fetch_error      = None
if "fetch_done"       not in st.session_state: st.session_state.fetch_done       = False
if "just_logged_out"  not in st.session_state: st.session_state.just_logged_out  = False

# ──────────────────────────────────────────────────────────────
# BACK-BUTTON PROTECTION (When Logged Out)
# ──────────────────────────────────────────────────────────────
if not st.session_state.is_authenticated:
    st.markdown(
        """
        <script>
            (function() {
                // Trap browser back button so it reloads clean unauthenticated state
                window.history.pushState(null, "", window.location.href);
                window.onpopstate = function() {
                    window.history.pushState(null, "", window.location.href);
                    window.location.reload();
                };
            })();
        </script>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
render_header()


# ──────────────────────────────────────────────────────────────
# SIDEBAR — Credentials & Controls
# ──────────────────────────────────────────────────────────────
fetch_clicked  = False
logout_clicked = False

with st.sidebar:
    if st.session_state.is_authenticated:
        st.markdown(
            f"""
            <div style="padding:0.5rem 0 1.2rem 0; border-bottom:1px solid #30363d; margin-bottom:1.2rem;">
                <span style="font-size:1.35rem; font-weight:700; color:#e6edf3;">📬 Mailbox</span>
            </div>
            <div style="padding:0.8rem 1rem; background:#161b22; border:1px solid #30363d; border-radius:10px; margin-bottom:1.2rem;">
                <div style="font-size:0.72rem; color:#8b949e; text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">Active Account</div>
                <div style="font-size:0.92rem; font-weight:600; color:#58a6ff; margin-top:0.25rem; word-break:break-all;">📧 {st.session_state.auth_email}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        auto_mark = st.checkbox(
            "Auto-mark as Read in Gmail on Fetch",
            value=st.session_state.get("auto_mark_pref", True),
            key="auto_mark_pref",
            help="When enabled, fetched emails are immediately marked as Read in your Gmail inbox so they will not reappear on your next fetch.",
        )

        fetch_clicked = st.button("🔄 Refresh & Fetch Emails", key="refresh_btn")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        logout_clicked = st.button("🚪 Log Out", key="sidebar_logout_btn", help="Securely disconnect and log out of MailSense")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            """
            <div style="padding:0.5rem 0 1.2rem 0; border-bottom:1px solid #30363d; margin-bottom:1.2rem;">
                <span style="font-size:1.35rem; font-weight:700; color:#e6edf3;">🔐 Credentials</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        email_input    = st.text_input("Email Address", placeholder="you@gmail.com",        key="email_addr")
        password_input = st.text_input("App Password",  placeholder="xxxx xxxx xxxx xxxx",  type="password", key="app_password")

        st.markdown("<br>", unsafe_allow_html=True)

        auto_mark = st.checkbox(
            "Auto-mark as Read in Gmail on Fetch",
            value=True,
            key="auto_mark_pref",
            help="When enabled, fetched emails are immediately marked as Read in your Gmail inbox so they will not reappear on your next fetch.",
        )

        fetch_clicked = st.button("🔍 Fetch & Analyze Emails", key="fetch_btn")

        st.markdown(
            """
            <div style="margin-top:1.4rem; padding:1rem; background:#161b22;
                        border:1px solid #30363d; border-radius:10px; font-size:0.8rem; color:#8b949e;">
                <b style="color:#58a6ff;">💡 How to get an App Password</b><br><br>
                App Passwords are 16-character codes generated by your provider that
                let MailSense access your inbox <em>without</em> storing your real password.<br><br>
                <b>Gmail:</b> myaccount.google.com → Security → 2-Step Verification → App Passwords<br><br>
                <b>Outlook/Hotmail:</b> account.microsoft.com → Security → Advanced security options → App Passwords<br><br>
                <b>Yahoo:</b> login.yahoo.com → Account Security → Generate app password
            </div>
            """,
            unsafe_allow_html=True,
        )

# ──────────────────────────────────────────────────────────────
# LOGOUT HANDLER
# ──────────────────────────────────────────────────────────────
if logout_clicked:
    st.session_state.clear()
    st.session_state.is_authenticated = False
    st.session_state.fetch_done       = False
    st.session_state.emails           = None
    st.session_state.just_logged_out  = True
    st.rerun()

# ──────────────────────────────────────────────────────────────
# FETCH TRIGGER
# ──────────────────────────────────────────────────────────────
# We handle both sidebar fetch and main-body fetch triggers
email_from_main = st.session_state.get("main_email_input", "")
pass_from_main  = st.session_state.get("main_pass_input", "")
main_fetch_hit  = st.session_state.get("main_fetch_submit_btn", False)

if fetch_clicked or main_fetch_hit:
    st.session_state.fetch_error = None
    if st.session_state.is_authenticated:
        email_to_use = st.session_state.auth_email
        pass_to_use  = st.session_state.auth_password
        auto_mark_to_use = auto_mark
    elif main_fetch_hit:
        email_to_use = email_from_main.strip()
        pass_to_use  = pass_from_main.strip()
        auto_mark_to_use = st.session_state.get("main_auto_mark_checkbox", True)
    else:
        email_to_use = email_input.strip()
        pass_to_use  = password_input.strip()
        auto_mark_to_use = auto_mark

    if not email_to_use or not pass_to_use:
        st.session_state.fetch_error = "Please enter both an email address and an App Password."
    else:
        with st.spinner("🔄 Connecting to your inbox and analysing emotions…"):
            try:
                emails = fetch_and_analyze(
                    email_to_use,
                    pass_to_use,
                    auto_mark_read=auto_mark_to_use,
                )
                st.session_state.emails           = emails
                st.session_state.is_authenticated = True
                st.session_state.auth_email       = email_to_use
                st.session_state.auth_password    = pass_to_use
                st.session_state.fetch_done       = True
                st.session_state.just_logged_out  = False
                st.rerun()
            except imaplib.IMAP4.error as e:
                st.session_state.fetch_error = f"IMAP Authentication Error: {e}"
            except ConnectionRefusedError:
                st.session_state.fetch_error = "Connection refused. Check your IMAP server settings."
            except Exception as e:
                st.session_state.fetch_error = f"Unexpected error: {e}"


# ──────────────────────────────────────────────────────────────
# MARK AS READ HANDLERS
# ──────────────────────────────────────────────────────────────
def handle_mark_read(email_item: dict):
    uid = email_item.get("uid")
    if not uid:
        st.warning("Cannot mark email without UID.")
        return
    with st.spinner("Marking as read in Gmail…"):
        try:
            mark_as_read(st.session_state.auth_email, st.session_state.auth_password, uid)
            email_item["is_read"] = True
            st.toast("✓ Email marked as read in Gmail!", icon="✅")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to mark as read: {exc}")


def handle_mark_multiple(uids: list[str]):
    if not uids:
        return
    with st.spinner(f"Marking {len(uids)} email(s) as read in Gmail…"):
        try:
            mark_multiple_as_read(st.session_state.auth_email, st.session_state.auth_password, uids)
            uid_set = set(uids)
            for em in st.session_state.emails or []:
                if em.get("uid") in uid_set:
                    em["is_read"] = True
            st.toast(f"✓ Marked {len(uids)} email(s) as read in Gmail!", icon="✅")
            st.rerun()
        except Exception as exc:
            st.error(f"Failed to mark as read: {exc}")


# ──────────────────────────────────────────────────────────────
# MAIN BODY
# ──────────────────────────────────────────────────────────────

# Logged out confirmation banner
if st.session_state.get("just_logged_out", False):
    st.success("🔒 You have been securely logged out. All credentials and emails have been cleared.")
    st.session_state.just_logged_out = False

# Error banner
if st.session_state.fetch_error:
    st.error(f"⚠️ {st.session_state.fetch_error}")

# Welcome screen & Login form — shown before the first successful fetch or after logout
if not st.session_state.fetch_done:
    render_welcome_screen()

    # Centered Main-Screen Login Card (Always visible even if sidebar is collapsed)
    col_l, col_center, col_r = st.columns([1, 2.2, 1])
    with col_center:
        st.markdown(
            """
            <div style="background:#161b22; border:1px solid #30363d; border-radius:14px; padding:1.8rem 2rem; margin-top:1.2rem; box-shadow:0 8px 24px rgba(0,0,0,0.45);">
                <div style="font-size:1.25rem; font-weight:700; color:#e6edf3; margin-bottom:0.3rem;">🔐 Connect Your Inbox</div>
                <div style="font-size:0.84rem; color:#8b949e; margin-bottom:1.2rem; line-height:1.5;">
                    Enter your email credentials below or in the sidebar to fetch and triage your inbox.
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.text_input("Email Address", placeholder="you@gmail.com", key="main_email_input")
        st.text_input("App Password", placeholder="xxxx xxxx xxxx xxxx", type="password", key="main_pass_input")

        st.checkbox(
            "Auto-mark as Read in Gmail on Fetch",
            value=True,
            key="main_auto_mark_checkbox",
            help="When enabled, fetched emails are immediately marked as Read in your Gmail inbox so they will not reappear on your next fetch.",
        )

        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
        st.button("🚀 Fetch & Analyze Emails", key="main_fetch_submit_btn", type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        with st.expander("💡 How to get an App Password (Gmail / Outlook / Yahoo)", expanded=False):
            st.markdown(
                """
                App Passwords are 16-character codes that allow MailSense to safely connect to your inbox without storing your personal password:
                - **Gmail:** `myaccount.google.com` → Security → 2-Step Verification → App Passwords
                - **Outlook / Hotmail:** `account.microsoft.com` → Security → Advanced security options → App Passwords
                - **Yahoo:** `login.yahoo.com` → Account Security → Generate app password
                """
            )


# Results dashboard
if st.session_state.fetch_done and st.session_state.emails is not None:
    emails_list: list[dict] = st.session_state.emails

    happy  = [e for e in emails_list if e["emotion"] == "Happy"]
    normal = [e for e in emails_list if e["emotion"] == "Normal"]
    sad    = [e for e in emails_list if e["emotion"] == "Sad"]
    angry  = [e for e in emails_list if e["emotion"] == "Angry"]
    total  = len(emails_list)

    render_summary_metrics(total, len(happy), len(normal), len(sad), len(angry))

    if total == 0:
        col_empty_l, col_empty_r = st.columns([5, 1])
        with col_empty_l:
            st.info("🎉 Great news — your inbox has **no unread emails** right now!")
        with col_empty_r:
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("🚪 Log Out", key="empty_logout_btn"):
                st.session_state.clear()
                st.session_state.is_authenticated = False
                st.session_state.fetch_done       = False
                st.session_state.emails           = None
                st.session_state.just_logged_out  = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        unread_all = [e for e in emails_list if not e.get("is_read")]
        col_m1, col_m2, col_m3 = st.columns([3, 1.2, 0.8])
        with col_m2:
            if unread_all:
                if st.button(
                    f"✉️ Mark All ({len(unread_all)}) as Read in Gmail",
                    key="btn_mark_all_global",
                    help="Mark all currently unread emails as read in your Gmail inbox",
                ):
                    handle_mark_multiple([e["uid"] for e in unread_all if e.get("uid")])
        with col_m3:
            st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
            if st.button("🚪 Log Out", key="top_logout_btn", help="Securely disconnect and log out"):
                st.session_state.clear()
                st.session_state.is_authenticated = False
                st.session_state.fetch_done       = False
                st.session_state.emails           = None
                st.session_state.just_logged_out  = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        tab_happy, tab_normal, tab_sad, tab_angry = st.tabs([
            f"😊 Happy ({len(happy)})",
            f"😐 Normal ({len(normal)})",
            f"😢 Sad ({len(sad)})",
            f"😠 Angry ({len(angry)})",
        ])

        render_email_list(
            tab_happy,
            happy,
            category="happy",
            on_mark_read=handle_mark_read,
            on_mark_multiple=handle_mark_multiple,
        )
        render_email_list(
            tab_normal,
            normal,
            category="normal",
            on_mark_read=handle_mark_read,
            on_mark_multiple=handle_mark_multiple,
        )
        render_email_list(
            tab_sad,
            sad,
            category="sad",
            on_mark_read=handle_mark_read,
            on_mark_multiple=handle_mark_multiple,
        )
        render_email_list(
            tab_angry,
            angry,
            category="angry",
            on_mark_read=handle_mark_read,
            on_mark_multiple=handle_mark_multiple,
        )


