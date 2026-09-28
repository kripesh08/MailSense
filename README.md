# 📊 MailSense (https://mail-sense.streamlit.app/)

**Intelligent Email Emotion Classification & Analytics Portal**

MailSense is a modern, privacy-focused email dashboard built with Python and Streamlit. It connects to your inbox via secure IMAP SSL, classifies unread emails into emotional categories (**Happy**, **Normal**, **Sad**, **Angry**), and allows you to read and synchronize email read-status directly with Gmail, Outlook, or Yahoo.

---

## ✨ Features

- **🔐 Secure IMAP SSL**: Connects safely using provider App Passwords without exposing your primary account password.
- **🧠 Emotion Classification Engine**: Powered by a hybrid NLP model combining NRCLex affect frequencies and TextBlob sentiment analysis.
  - 😊 **Happy**: Congratulations, celebrations, positive updates.
  - 😐 **Normal**: Work notes, newsletters, receipts, security alerts.
  - 😢 **Sad**: Condolences, personal grief, apologies, sorrow.
  - 😠 **Angry**: Urgent complaints, escalations, service issues.
- **🔄 Gmail Read-Status Synchronization**:
  - Automatically mark fetched emails as Read in your Gmail inbox so they don't reappear on subsequent fetches.
  - Manually mark individual emails or entire categories as Read with a single click.
- **🚪 Secure Authentication & Session Management**:
  - Full session isolation with explicit Log Out.
  - Security protections ensuring browser back-button cannot re-enter an authenticated session.
- **🎨 Responsive Dark-Mode UI**: Collapsible sidebar with reopen controls, custom metric cards, sentiment polarity badges, and responsive expanders.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+
- An email provider that supports IMAP (Gmail, Outlook, Yahoo, etc.)
- A generated **App Password** from your email provider.

### 2. Installation

Clone this repository and install the dependencies:

```bash
git clone <your-repo-url>
cd MailSense
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 💡 How to generate an App Password

- **Gmail**: Go to `Google Account` → `Security` → `2-Step Verification` → `App Passwords`.
- **Outlook**: Go to `Microsoft Account` → `Security` → `Advanced security options` → `App Passwords`.
- **Yahoo**: Go to `Account Security` → `Generate app password`.

---

## 📁 Project Structure

```text
MailSense/
├── app.py              # Streamlit application entry point & session orchestration
├── mail_client.py      # IMAP connection, MIME parsing & read-status synchronization
├── classifier.py       # Hybrid NRCLex + TextBlob emotion triage engine
├── ui_components.py    # CSS design system, metric cards & UI renderers
├── requirements.txt    # Project dependencies
└── README.md           # Documentation
```
