"""
app.py
AI Email Agent — Streamlit UI
Developed by Hamna Munir

Email-client layout: sidebar | inbox list | email view + floating reply composer.
Every control is wired up:
  - folders (Inbox / Sent / Draft / Archived / Pinned / Unread / Trash), refresh
  - sort, search, pin, archive, trash / restore, mark as unread
  - reply, new message, save draft, send, attachments, dark mode
  - the AI agent (analysis, tool calls, activity log) lives inside the email view,
    and anything that gets SENT always needs the human to press "Send message".

Needs a recent Streamlit:  pip install -U streamlit
"""

import sys
import os
import re
import html
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.tools import MOCK_EMAILS
from src.agent import process_email

st.set_page_config(page_title="AI Email Agent | Hamna Munir", page_icon="📧", layout="wide")

USER_NAME = "Hamna Munir"
USER_EMAIL = "hamna.munir@mail.com"  # change to your own address
AVATAR_COLORS = ["#2f6fed", "#f59e0b", "#10b981", "#a855f7", "#ef4444", "#0ea5e9"]
SORT_OPTIONS = ["Recent", "Oldest", "Unread first"]
VIEW_TITLES = {
    "inbox": "Inbox", "sent": "Sent", "draft": "Drafts", "archived": "Archived",
    "pinned": "Pinned", "unread": "Unread", "trash": "Trash",
}
EMPTY_TEXT = {
    "inbox": "Your inbox is empty.",
    "sent": "Nothing sent yet. Reply to an email or start a new message.",
    "draft": "No drafts. Unfinished messages are saved here.",
    "archived": "No archived emails.",
    "pinned": "No pinned emails. Pin an email to keep it here.",
    "unread": "You're all caught up.",
    "trash": "Trash is empty.",
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def h(s: str) -> str:
    """Collapse HTML onto one line so Markdown never turns indentation into a code block."""
    return "".join(line.strip() for line in s.strip().splitlines())


def sender_name(addr: str) -> str:
    addr = str(addr or "").strip()
    m = re.match(r'^"?([^"<]+?)"?\s*<.*>$', addr)
    if m:
        return m.group(1).strip()
    local = addr.split("@")[0]
    return re.sub(r"[._\-]+", " ", local).title() or addr


def avatar(name: str, size: int = 42) -> str:
    color = AVATAR_COLORS[sum(map(ord, name)) % len(AVATAR_COLORS)]
    initial = (name.strip()[:1] or "?").upper()
    return h(
        f'<div class="avatar" style="background:{color};width:{size}px;height:{size}px;">{esc(initial)}</div>'
    )


def preview(text: str, n: int = 64) -> str:
    t = re.sub(r"\s+", " ", str(text)).strip()
    return t if len(t) <= n else t[:n].rstrip() + "…"


def now_time() -> str:
    return datetime.now().strftime("%I:%M").lstrip("0")


def extract_draft(result: dict) -> str:
    """Pull the drafted reply text out of the agent's create_draft tool call."""
    for tc in result.get("tool_calls", []):
        if tc.get("tool") == "create_draft":
            args = tc.get("arguments")
            if isinstance(args, dict):
                for key in ("body", "content", "text", "message", "draft"):
                    if args.get(key):
                        return str(args[key])
            elif isinstance(args, str) and args.strip():
                return args
    return str(result.get("agent_response", ""))


# ---------------------------------------------------------------------------
# Theme (light / dark) + CSS
# ---------------------------------------------------------------------------

LIGHT = {
    "page": "linear-gradient(160deg,#eef2fb 0%,#e4ecfb 100%)",
    "panel": "#ffffff", "panel2": "#f6f8fd", "text": "#1b1f33", "muted": "#8b93a7",
    "border": "#eceff6", "accent": "#2f6fed", "chip": "#eaf1ff", "hover": "#f6f8fd",
    "sel": "#eef3ff", "aibg": "linear-gradient(135deg,#eef4ff,#f8faff)", "aibr": "#dbe6ff",
    "shadow": "rgba(37,52,94,0.10)",
}
DARK = {
    "page": "linear-gradient(160deg,#0b0f1c 0%,#101528 100%)",
    "panel": "#151a2c", "panel2": "#1b2138", "text": "#e8ecf8", "muted": "#8f98b2",
    "border": "#262d47", "accent": "#5b9bff", "chip": "#1f2b4d", "hover": "#1b2138",
    "sel": "#1f2946", "aibg": "linear-gradient(135deg,#182242,#151c34)", "aibr": "#2a3760",
    "shadow": "rgba(0,0,0,0.45)",
}

STATIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea, .stApp summary {
    font-family: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
}
.stApp { background: var(--page); color: var(--text); }
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
.block-container { max-width: 1320px; padding: 1.3rem 1.2rem 0.8rem; }
.stApp p, .stApp li, .stApp label, .stApp summary,
.stApp [data-testid="stText"], .stApp [data-testid="stCaptionContainer"] { color: var(--text); }
.stApp button p, .stApp button span { color: inherit; }

/* ---------- Shell ---------- */
.st-key-shell {
    background: var(--panel); border: 1px solid var(--border); border-radius: 26px;
    box-shadow: 0 24px 60px var(--shadow); overflow: hidden; gap: 0;
}
.st-key-shell [data-testid="stColumn"]:has(.st-key-nav),
.st-key-shell [data-testid="column"]:has(.st-key-nav),
.st-key-shell [data-testid="stColumn"]:has(.st-key-list),
.st-key-shell [data-testid="column"]:has(.st-key-list) { border-right: 1px solid var(--border); }

/* ---------- Sidebar ---------- */
.st-key-nav { padding: 1.2rem 0.5rem 1.1rem 1.1rem; min-height: 760px; justify-content: space-between; }
.logo {
    width: 36px; height: 36px; border-radius: 50%; color: #fff; font-size: 1rem;
    background: linear-gradient(135deg, #2f6fed, #5aa7ff);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 18px rgba(47,111,237,0.38);
}
.acct { color: var(--text); font-size: 0.82rem; padding: 0.15rem 0.7rem 0.4rem; word-break: break-all; }
hr.soft { border: none; border-top: 1px solid var(--border); margin: 0.7rem 0; }
.st-key-nav button {
    width: 100%; justify-content: flex-start; background: transparent; border: none;
    color: var(--text); font-weight: 600; font-size: 0.9rem; padding: 0.5rem 0.7rem;
    border-radius: 12px; box-shadow: none;
}
.st-key-nav button > div { justify-content: flex-start; width: 100%; }
.st-key-nav button:hover { background: var(--hover); color: var(--accent); }
.st-key-nav button[kind="primary"], .st-key-nav button[data-testid="stBaseButton-primary"] {
    background: var(--chip); color: var(--accent); font-weight: 800;
    box-shadow: inset 3px 0 0 var(--accent);
}
.side-label { font-size: 0.82rem; font-weight: 700; color: var(--text); margin: 0.2rem 0 0.5rem 0.2rem; }
.bar { height: 6px; border-radius: 99px; background: var(--border); overflow: hidden; margin: 0 0.2rem; }
.bar > span { display: block; height: 100%; border-radius: 99px; background: linear-gradient(90deg, #2f6fed, #7db4ff); }
.hint { color: var(--muted); font-size: 0.78rem; margin: 0.45rem 0 0.9rem 0.2rem; }
.me { display: flex; align-items: center; gap: 0.75rem; padding: 0.8rem; background: var(--panel2); border-radius: 16px; margin-right: 0.5rem; }
.me-name { font-weight: 700; font-size: 0.88rem; color: var(--text); }
.me-status { font-size: 0.78rem; color: var(--muted); }
.me-status i { display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: #22c55e; margin-right: 0.35rem; }

/* ---------- Inbox list ---------- */
.st-key-list { padding: 1rem 0 0.6rem; gap: 0; }
.st-key-list_head { padding: 0 0.9rem 0.5rem; }
.st-key-list_head button {
    background: transparent; border: none; box-shadow: none; color: var(--muted);
    font-weight: 600; font-size: 0.85rem; justify-content: flex-start;
}
.st-key-list_head button:hover { color: var(--accent); background: var(--hover); }
.list-title { font-size: 0.95rem; font-weight: 800; color: var(--text); padding: 0.2rem 1.1rem 0.7rem; }
.list-title span { color: var(--muted); font-weight: 600; margin-left: 0.3rem; }
.empty { text-align: center; color: var(--muted); padding: 3rem 1.5rem; font-size: 0.92rem; line-height: 1.6; }

[class*="st-key-mail_"] { position: relative; gap: 0; border-top: 1px solid var(--border); }
.mail { padding: 0.85rem 1.1rem; transition: background 0.15s; }
[class*="st-key-mail_"]:hover .mail { background: var(--hover); }
.mail.sel { background: var(--sel); }
.mail-top { display: flex; justify-content: space-between; gap: 0.5rem; font-size: 0.78rem; font-weight: 600; color: var(--text); }
.mail-time { color: var(--muted); font-weight: 500; white-space: nowrap; }
.mail-subj { font-size: 0.98rem; font-weight: 500; margin: 0.2rem 0; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mail.unread .mail-subj { font-weight: 800; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); margin-right: 0.45rem; }
.mail-prev { font-size: 0.78rem; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
/* invisible button stretched over the whole card = the card is clickable */
[class*="st-key-mail_"] [data-testid="stElementContainer"]:has(button),
[class*="st-key-mail_"] .element-container:has(button) { position: absolute; inset: 0; margin: 0; z-index: 3; }
[class*="st-key-mail_"] [data-testid="stButton"], [class*="st-key-mail_"] .stButton { height: 100%; width: 100%; }
[class*="st-key-mail_"] button { width: 100%; height: 100%; opacity: 0; cursor: pointer; }

/* ---------- Email view ---------- */
.st-key-detail { padding: 1.1rem 1.6rem 1.3rem; }
.st-key-toolbar button {
    background: transparent; border: none; box-shadow: none; color: var(--muted);
    border-radius: 12px;
}
.st-key-toolbar button:hover:not(:disabled) { color: var(--accent); background: var(--chip); }
.st-key-toolbar button:disabled { opacity: 0.35; }
.st-key-new_msg button {
    background: linear-gradient(135deg, #2f6fed, #4f9bff) !important; color: #fff !important;
    border: none !important; border-radius: 999px !important; font-weight: 700;
    box-shadow: 0 10px 22px rgba(47,111,237,0.35) !important;
}
.meta { display: flex; justify-content: space-between; gap: 1rem; font-size: 0.86rem; color: var(--text); margin: 0.9rem 0 0.4rem; }
.meta .date { color: var(--muted); font-size: 0.8rem; white-space: nowrap; }
.subject { font-size: 2rem; font-weight: 500; letter-spacing: -0.02em; line-height: 1.2; color: var(--text); margin-bottom: 0.9rem; }
.avatar {
    border-radius: 50%; color: #fff; font-weight: 700; font-size: 1rem; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 8px 18px rgba(30,41,59,0.18);
}
.body { font-size: 1rem; line-height: 1.75; color: var(--text); padding-bottom: 0.8rem; }
.att { display: inline-block; background: var(--chip); color: var(--accent); border-radius: 999px; padding: 0.25rem 0.8rem; font-size: 0.82rem; font-weight: 600; }
.status { display: inline-block; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.6rem; border-radius: 999px; background: rgba(34,197,94,0.14); color: #16a34a; margin-left: 0.5rem; vertical-align: middle; }
.st-key-d_reply button, .st-key-detail [data-testid="stPopover"] button {
    background: transparent; border: none; box-shadow: none; color: var(--text);
}
.st-key-d_reply button:hover, .st-key-detail [data-testid="stPopover"] button:hover { background: var(--chip); color: var(--accent); }

/* ---------- AI panel ---------- */
.st-key-ai { background: var(--aibg); border: 1px solid var(--aibr); border-radius: 18px; padding: 1rem 1.2rem; margin: 0.5rem 0 0.8rem; }
.ai-head { display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.ai-badge { background: linear-gradient(135deg, #2f6fed, #5aa7ff); color: #fff; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.8rem; border-radius: 999px; }
.ai-sub { color: var(--muted); font-size: 0.82rem; }
.pill-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.7rem 0 0.5rem; }
.pill { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 0.35rem 0.8rem; font-size: 0.88rem; font-weight: 700; color: var(--text); }
.pill i { display: block; font-style: normal; font-size: 0.7rem; font-weight: 600; color: var(--muted); }
.pill.high { color: #ef4444; } .pill.medium { color: #f59e0b; } .pill.low { color: #16a34a; }
.ai-line { font-size: 0.9rem; line-height: 1.55; margin: 0.25rem 0; color: var(--text); }
.st-key-ai_resp { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 0.8rem 1rem; margin: 0.6rem 0; }
.st-key-ai [data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 12px; background: var(--panel); }
.st-key-ai [data-testid="stExpander"] * { color: var(--text); }

/* ---------- Composer ---------- */
.st-key-composer {
    background: var(--panel); border: 1px solid var(--border); border-radius: 20px;
    box-shadow: 0 -6px 40px var(--shadow), 0 20px 44px var(--shadow);
    padding: 0.8rem 1.2rem 1rem; margin-top: 1rem;
}
.ctitle { font-size: 0.86rem; font-weight: 600; color: var(--text); }
.rchip { display: inline-block; border: 1px solid var(--accent); color: var(--accent); background: var(--chip); border-radius: 999px; padding: 0.22rem 0.8rem; font-size: 0.82rem; font-weight: 600; margin-left: 0.6rem; }
.st-key-composer div[data-baseweb="input"], .st-key-composer div[data-baseweb="base-input"],
.st-key-composer div[data-baseweb="textarea"] { background: transparent !important; border: none !important; box-shadow: none !important; }
.st-key-composer input, .st-key-composer textarea { background: transparent !important; color: var(--text) !important; }
.st-key-composer [data-testid="stTextInput"] input { font-size: 1.2rem; font-weight: 600; }
.st-key-composer textarea { font-size: 0.98rem; line-height: 1.7; }
.st-key-composer button[kind="secondary"], .st-key-composer button[data-testid="stBaseButton-secondary"] {
    background: transparent; border: 1px solid var(--border); color: var(--text); border-radius: 999px; font-weight: 600;
}
.st-key-composer button[kind="secondary"]:hover, .st-key-composer button[data-testid="stBaseButton-secondary"]:hover { color: var(--accent); border-color: var(--accent); }
.st-key-c_close button { border: none !important; color: var(--muted) !important; }

/* ---------- Primary buttons ---------- */
button[kind="primary"], button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #2f6fed, #4f9bff); color: #fff; border: none;
    border-radius: 999px; font-weight: 700; box-shadow: 0 8px 18px rgba(47,111,237,0.28);
}
.st-key-nav button[kind="primary"], .st-key-nav button[data-testid="stBaseButton-primary"] {
    background: var(--chip); color: var(--accent); box-shadow: inset 3px 0 0 var(--accent); border-radius: 12px;
}

.app-footer { text-align: center; color: var(--muted); font-size: 0.8rem; margin: 1.2rem 0 0.3rem; }
.app-footer b { color: var(--accent); }
</style>
"""


def inject_css(dark: bool) -> None:
    theme = DARK if dark else LIGHT
    variables = "".join(f"--{k}:{v};" for k, v in theme.items())
    st.markdown(f"<style>:root{{{variables}}}</style>" + STATIC_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


def init_state() -> None:
    ss = st.session_state
    if "mails" in ss:
        return
    times = ["9:47", "9:30", "3:42", "2:55", "2:29", "1:10", "12:20", "11:05"]
    total = len(MOCK_EMAILS)
    mails = {}
    for i, (eid, raw) in enumerate(MOCK_EMAILS.items()):
        rid = str(eid)
        addr = raw.get("from", "unknown@mail.com")
        mails[rid] = {
            "id": rid, "folder": "inbox",
            "from_addr": addr, "from_name": sender_name(addr),
            "to_addr": USER_EMAIL, "to_name": "Me",
            "subject": raw.get("subject", ""), "body": raw.get("body", ""),
            "time": times[i % len(times)], "seq": total - i,
            "read": False, "pinned": False, "archived": False, "trashed": False,
            "replied": False, "attachment": None, "raw": raw,
        }
    ss.mails = mails
    ss.next_seq = total + 1
    ss.folder = "inbox"
    ss.selected = None
    ss.compose = None
    ss.results = {}
    ss.uid = 0
    ss.more_open = False
    ss.search_open = False
    ss.sort = "Recent"
    ss.dark = False


def in_view(rec: dict, view: str) -> bool:
    if view == "trash":
        return rec["trashed"]
    if rec["trashed"]:
        return False
    if view == "inbox":
        return rec["folder"] == "inbox" and not rec["archived"]
    if view == "sent":
        return rec["folder"] == "sent"
    if view == "draft":
        return rec["folder"] == "draft"
    if view == "archived":
        return rec["archived"]
    if view == "pinned":
        return rec["pinned"]
    if view == "unread":
        return rec["folder"] == "inbox" and not rec["read"] and not rec["archived"]
    return False


def new_record(**fields) -> dict:
    ss = st.session_state
    seq = ss.next_seq
    ss.next_seq += 1
    rec = {
        "id": f"u_{seq}", "folder": "sent",
        "from_addr": USER_EMAIL, "from_name": USER_NAME,
        "to_addr": "", "to_name": "", "subject": "", "body": "",
        "time": now_time(), "seq": seq,
        "read": True, "pinned": False, "archived": False, "trashed": False,
        "replied": False, "attachment": None, "raw": None,
    }
    rec.update(fields)
    ss.mails[rec["id"]] = rec
    return rec


# ---------------------------------------------------------------------------
# Callbacks (run before the next render, so the UI always reflects the change)
# ---------------------------------------------------------------------------


def set_folder(view: str) -> None:
    autosave_draft()
    ss = st.session_state
    ss.folder = view
    ss.selected = None
    ss.compose = None


def toggle_more() -> None:
    st.session_state.more_open = not st.session_state.more_open


def toggle_search() -> None:
    ss = st.session_state
    ss.search_open = not ss.search_open
    if not ss.search_open:
        ss.q = ""


def refresh() -> None:
    ss = st.session_state
    ss.search_open = False
    ss.q = ""
    st.toast("Inbox is up to date", icon="🔄")


def select(rid: str) -> None:
    autosave_draft()
    ss = st.session_state
    ss.selected = rid
    ss.mails[rid]["read"] = True
    ss.compose = None


def toggle_pin(rid: str) -> None:
    rec = st.session_state.mails[rid]
    rec["pinned"] = not rec["pinned"]
    st.toast("Pinned" if rec["pinned"] else "Unpinned", icon="📌")


def toggle_archive(rid: str) -> None:
    rec = st.session_state.mails[rid]
    rec["archived"] = not rec["archived"]
    st.toast("Archived" if rec["archived"] else "Moved back to inbox", icon="📦")


def trash(rid: str) -> None:
    ss = st.session_state
    ss.mails[rid]["trashed"] = True
    if ss.selected == rid:
        ss.selected = None
        ss.compose = None
    st.toast("Moved to trash", icon="🗑️")


def restore(rid: str) -> None:
    ss = st.session_state
    ss.mails[rid]["trashed"] = False
    ss.selected = None
    st.toast("Restored", icon="↩️")


def purge(rid: str) -> None:
    ss = st.session_state
    ss.mails.pop(rid, None)
    ss.results.pop(rid, None)
    ss.selected = None
    ss.compose = None
    st.toast("Deleted permanently", icon="🗑️")


def mark_unread(rid: str) -> None:
    st.session_state.mails[rid]["read"] = False
    st.toast("Marked as unread", icon="✉️")


def open_compose(mode: str, rid=None, body: str = "") -> None:
    """mode: 'reply' | 'new' | 'draft'"""
    autosave_draft()
    ss = st.session_state
    ss.uid += 1
    uid = ss.uid
    c = {"uid": uid, "mode": mode, "rid": rid}
    if mode == "reply":
        rec = ss.mails[rid]
        first = rec["from_name"].split()[0] if rec["from_name"] else ""
        initial = body or f"Hi {first},\n\n"
        subj = rec["subject"]
        c.update(to=rec["from_addr"], to_name=rec["from_name"])
        ss[f"c_subj_{uid}"] = subj if subj.lower().startswith("re:") else f"Re: {subj}"
        ss[f"c_body_{uid}"] = initial
    elif mode == "draft":
        rec = ss.mails[rid]
        initial = rec["body"]
        c["draft_id"] = rid
        ss[f"c_to_{uid}"] = rec["to_addr"]
        ss[f"c_subj_{uid}"] = rec["subject"]
        ss[f"c_body_{uid}"] = initial
    else:
        initial = body
        ss[f"c_to_{uid}"] = ""
        ss[f"c_subj_{uid}"] = ""
        ss[f"c_body_{uid}"] = initial
    c["initial"] = initial
    ss.compose = c


def _compose_fields() -> tuple:
    ss = st.session_state
    c = ss.compose
    uid = c["uid"]
    to = (ss.get(f"c_to_{uid}", c.get("to", "")) or "").strip()
    subject = (ss.get(f"c_subj_{uid}", "") or "").strip()
    body = ss.get(f"c_body_{uid}", "") or ""
    f = ss.get(f"c_file_{uid}")
    return to, subject, body, (f.name if f else None)


def save_draft(silent: bool = False) -> None:
    ss = st.session_state
    c = ss.compose
    if not c:
        return
    to, subject, body, att = _compose_fields()
    fields = {
        "folder": "draft", "to_addr": to, "to_name": sender_name(to) if to else "",
        "subject": subject, "body": body, "attachment": att, "time": now_time(),
    }
    did = c.get("draft_id")
    if did and did in ss.mails:
        ss.mails[did].update(fields)
    else:
        c["draft_id"] = new_record(**fields)["id"]
    if not silent:
        st.toast("Draft saved", icon="📝")


def autosave_draft() -> None:
    """Never lose typed text: if the composer has unsent changes, keep them as a draft."""
    c = st.session_state.get("compose")
    if not c:
        return
    _, _, body, _ = _compose_fields()
    if body.strip() and body != c.get("initial", ""):
        save_draft(silent=True)
        st.toast("Unsent message saved to Drafts", icon="📝")


def close_compose() -> None:
    autosave_draft()
    st.session_state.compose = None


def insert_ai_draft(uid: int, rid: str) -> None:
    st.session_state[f"c_body_{uid}"] = extract_draft(st.session_state.results[rid])
    st.toast("AI draft inserted — review it before sending", icon="✦")


def send_message() -> None:
    ss = st.session_state
    c = ss.compose
    if not c:
        return
    to, subject, body, att = _compose_fields()
    if "@" not in to:
        st.toast("Add a valid recipient email address", icon="⚠️")
        return
    if not body.strip():
        st.toast("Write a message before sending", icon="⚠️")
        return
    new_record(folder="sent", to_addr=to, to_name=sender_name(to),
               subject=subject, body=body, attachment=att)
    did = c.get("draft_id")
    if did in ss.mails:
        del ss.mails[did]
    if c["mode"] == "reply" and c["rid"] in ss.mails:
        ss.mails[c["rid"]]["replied"] = True
    ss.compose = None
    st.toast(f"Message sent to {sender_name(to)}", icon="✅")


# ---------------------------------------------------------------------------
# Render pieces
# ---------------------------------------------------------------------------


def render_nav(unread: int, done: int, total: int) -> None:
    ss = st.session_state

    def nav_button(label: str, icon: str, view: str) -> None:
        st.button(label, icon=icon, key=f"nav_{view}", use_container_width=True,
                  type="primary" if ss.folder == view else "secondary",
                  on_click=set_folder, args=(view,))

    with st.container(key="nav"):
        with st.container(key="nav_top"):
            top = st.columns([1, 1], vertical_alignment="center")
            top[0].markdown('<div class="logo">✦</div>', unsafe_allow_html=True)
            with top[1]:
                st.toggle("🌙", key="dark", help="Dark mode")
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

            row = st.columns([4, 1], vertical_alignment="center")
            with row[0]:
                nav_button(f"Inbox ({unread})" if unread else "Inbox", ":material/inbox:", "inbox")
            with row[1]:
                st.button(" ", icon=":material/refresh:", key="nav_refresh", help="Refresh", on_click=refresh)
            st.markdown(f'<div class="acct">{esc(USER_EMAIL)}</div><hr class="soft">', unsafe_allow_html=True)

            nav_button("Sent", ":material/send:", "sent")
            nav_button("Draft", ":material/description:", "draft")
            nav_button("Archived", ":material/inventory_2:", "archived")
            nav_button("Pinned", ":material/push_pin:", "pinned")
            st.button("More", icon=":material/more_horiz:", key="nav_more", use_container_width=True,
                      on_click=toggle_more)
            if ss.more_open:
                nav_button("Unread", ":material/mark_email_unread:", "unread")
                nav_button("Trash", ":material/delete:", "trash")

        with st.container(key="nav_bottom"):
            pct = int(100 * done / total) if total else 0
            st.markdown(h(f"""
                <hr class="soft">
                <div class="side-label">AI agent progress</div>
                <div class="bar"><span style="width:{pct}%"></span></div>
                <div class="hint">{done} of {total} emails processed</div>
                <div class="me">
                    {avatar(USER_NAME, 40)}
                    <div>
                        <div class="me-name">{esc(USER_NAME)}</div>
                        <div class="me-status"><i></i>Active now</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)


def render_list(items: list, view: str, query: str) -> None:
    ss = st.session_state
    with st.container(key="list"):
        with st.container(key="list_head"):
            hc = st.columns([5, 1], vertical_alignment="center")
            with hc[0]:
                with st.popover(f"Sort by: {ss.sort}", use_container_width=True):
                    st.radio("Sort by", SORT_OPTIONS, key="sort", label_visibility="collapsed")
            with hc[1]:
                st.button(" ", icon=":material/search:", key="search_btn", help="Search",
                          on_click=toggle_search)
            if ss.search_open:
                st.text_input("Search mail", key="q", placeholder="Search mail…",
                              label_visibility="collapsed")

        if query:
            st.markdown(h(f'<div class="list-title">Results<span>{len(items)}</span></div>'), unsafe_allow_html=True)
        elif view != "inbox":
            st.markdown(h(f'<div class="list-title">{VIEW_TITLES[view]}<span>{len(items)}</span></div>'),
                        unsafe_allow_html=True)

        if not items:
            msg = "No emails match your search." if query else EMPTY_TEXT[view]
            st.markdown(f'<div class="empty">{esc(msg)}</div>', unsafe_allow_html=True)
            return

        for n, rec in enumerate(items):
            is_inbox = rec["folder"] == "inbox"
            name = rec["from_name"] if is_inbox else f'To: {rec["to_name"] or "no recipient"}'
            unread = is_inbox and not rec["read"]
            classes = "mail" + (" sel" if rec["id"] == ss.selected else "") + (" unread" if unread else "")
            dot = '<i class="dot"></i>' if unread else ""
            pin = " 📌" if rec["pinned"] else ""
            with st.container(key=f"mail_{n}"):
                st.markdown(h(f"""
                    <div class="{classes}">
                        <div class="mail-top"><span>{esc(name)}{pin}</span><span class="mail-time">{esc(rec["time"])}</span></div>
                        <div class="mail-subj">{dot}{esc(rec["subject"] or "(no subject)")}</div>
                        <div class="mail-prev">{esc(preview(rec["body"]))}</div>
                    </div>
                """), unsafe_allow_html=True)
                st.button(" ", key=f"open_{rec['id']}", use_container_width=True,
                          on_click=select, args=(rec["id"],))


def render_ai_panel(rec: dict) -> None:
    ss = st.session_state
    rid = rec["id"]
    result = ss.results.get(rid)

    with st.container(key="ai"):
        st.markdown(h("""
            <div class="ai-head">
                <span class="ai-badge">✦ AI Agent</span>
                <span class="ai-sub">Reads this email and drafts a reply. Nothing is sent until you press Send.</span>
            </div>
        """), unsafe_allow_html=True)

        if st.button("Analyze again" if result else "Analyze with AI Agent", key=f"ai_{rid}",
                     type="primary", icon=":material/auto_awesome:"):
            ok = False
            try:
                with st.spinner("Agent analyzing and deciding..."):
                    ss.results[rid] = process_email(rec["raw"])
                ok = True
            except Exception as e:
                st.error("Something went wrong processing this email. Please try again.")
                with st.expander("Technical details"):
                    st.code(str(e))
            if ok:
                st.rerun()

        if not result:
            return

        if result.get("injection_flagged"):
            st.warning("⚠️ This email contains phrasing commonly used in prompt-injection attempts. "
                       "It has NOT been treated as an instruction — flagged for your review only.")

        a = result["analysis"]
        prio = str(a.priority).lower()
        prio_cls = "high" if ("high" in prio or "urgent" in prio) else "medium" if "med" in prio else "low"
        st.markdown(h(f"""
            <div class="pill-row">
                <div class="pill"><i>Intent</i>{esc(a.intent)}</div>
                <div class="pill {prio_cls}"><i>Priority</i>{esc(a.priority)}</div>
                <div class="pill"><i>Needs reply</i>{"Yes" if a.needs_reply else "No"}</div>
            </div>
            <div class="ai-line"><b>Summary:</b> {esc(a.summary)}</div>
            <div class="ai-line"><b>Requested action:</b> {esc(a.requested_action)}</div>
        """), unsafe_allow_html=True)

        with st.container(key="ai_resp"):
            st.markdown("**Agent response**")
            st.markdown(str(result["agent_response"]))

        has_draft = any(tc.get("tool") == "create_draft" for tc in result.get("tool_calls", []))
        if has_draft:
            st.button("Review AI draft & reply", key=f"ai_use_{rid}", type="primary",
                      icon=":material/edit_note:", on_click=open_compose,
                      args=("reply", rid, extract_draft(result)))
            st.caption("Sending always needs your confirmation — the agent cannot send on its own.")

        with st.expander("📋 Activity Log"):
            for entry in result.get("activity_log", []):
                st.text(entry)

        with st.expander("🔧 Tool Calls Made"):
            if result.get("tool_calls"):
                for tc in result["tool_calls"]:
                    st.write(f"**{tc['tool']}**({tc['arguments']})")
                    st.caption(f"Result: {tc['result']}")
            else:
                st.write("No tools were called for this email.")


def render_composer() -> None:
    ss = st.session_state
    c = ss.compose
    uid = c["uid"]
    mode = c["mode"]

    with st.container(key="composer"):
        head = st.columns([12, 1], vertical_alignment="center")
        if mode == "reply":
            head[0].markdown(h(f'<div><span class="ctitle">Replying to</span><span class="rchip">{esc(c["to_name"])}</span></div>'),
                             unsafe_allow_html=True)
        else:
            head[0].markdown(h(f'<div class="ctitle">{"Editing draft" if mode == "draft" else "New message"}</div>'),
                             unsafe_allow_html=True)
        head[1].button(" ", icon=":material/close:", key="c_close", help="Close", on_click=close_compose)
        st.markdown('<hr class="soft">', unsafe_allow_html=True)

        if mode in ("new", "draft"):
            st.text_input("To", key=f"c_to_{uid}", placeholder="To: name@example.com",
                          label_visibility="collapsed")
        st.text_input("Subject", key=f"c_subj_{uid}", placeholder="Subject", label_visibility="collapsed")
        st.text_area("Message", key=f"c_body_{uid}", height=180, placeholder="Write your message…",
                     label_visibility="collapsed")

        att = ss.get(f"c_file_{uid}")
        foot = st.columns([1.7, 1.5, 1.3, 1.8], vertical_alignment="center")
        with foot[0]:
            label = preview(att.name, 16) if att else "Attach"
            with st.popover(label, icon=":material/attach_file:", use_container_width=True):
                st.file_uploader("Attach a file", key=f"c_file_{uid}")
        with foot[1]:
            if mode == "reply" and c["rid"] in ss.results:
                st.button("AI draft", icon=":material/auto_awesome:", key="c_ai", use_container_width=True,
                          on_click=insert_ai_draft, args=(uid, c["rid"]))
        with foot[2]:
            st.button("Save draft", key="c_save", use_container_width=True, on_click=save_draft)
        with foot[3]:
            st.button("Send message", icon=":material/send:", key="c_send", type="primary",
                      use_container_width=True, on_click=send_message)


def render_detail(rec: dict) -> None:
    rid = rec["id"]
    folder = rec["folder"]
    is_inbox = folder == "inbox"

    with st.container(key="toolbar"):
        tb = st.columns([0.6, 0.6, 0.6, 0.6, 4, 1.9], vertical_alignment="center")
        with tb[0]:
            st.button(" ", icon=":material/inventory_2:", key="tb_archive",
                      help="Move back to inbox" if rec["archived"] else "Archive",
                      on_click=toggle_archive, args=(rid,))
        with tb[1]:
            st.button(" ", icon=":material/push_pin:", key="tb_pin",
                      help="Unpin" if rec["pinned"] else "Pin", on_click=toggle_pin, args=(rid,))
        with tb[2]:
            if rec["trashed"]:
                st.button(" ", icon=":material/restore_from_trash:", key="tb_trash", help="Restore",
                          on_click=restore, args=(rid,))
            else:
                st.button(" ", icon=":material/delete:", key="tb_trash", help="Move to trash",
                          on_click=trash, args=(rid,))
        with tb[3]:
            st.button(" ", icon=":material/mark_email_unread:", key="tb_unread", help="Mark as unread",
                      disabled=not is_inbox, on_click=mark_unread, args=(rid,))
        with tb[5]:
            st.button("New message", icon=":material/mail:", key="new_msg", type="primary",
                      use_container_width=True, on_click=open_compose, args=("new",))

    if is_inbox:
        meta = f'<b>{esc(rec["from_name"])}</b> to <b>Me</b>'
    else:
        meta = f'<b>Me</b> to <b>{esc(rec["to_name"] or "no recipient")}</b>'
    date = f'{datetime.now().strftime("%A, %b %d")}, {rec["time"]}'
    st.markdown(h(f'<div class="meta"><span>{meta}</span><span class="date">{esc(date)}</span></div>'),
                unsafe_allow_html=True)

    left, right = st.columns([0.7, 8], gap="small")
    with left:
        st.markdown(avatar(rec["from_name"]), unsafe_allow_html=True)
        if is_inbox:
            st.button(" ", icon=":material/reply:", key="d_reply", help="Reply",
                      on_click=open_compose, args=("reply", rid))
        with st.popover(" ", icon=":material/more_horiz:"):
            if is_inbox:
                st.button("Mark as unread", key="pm_unread", icon=":material/mark_email_unread:",
                          use_container_width=True, on_click=mark_unread, args=(rid,))
            if rec["trashed"]:
                st.button("Restore", key="pm_restore", icon=":material/restore_from_trash:",
                          use_container_width=True, on_click=restore, args=(rid,))
                st.button("Delete forever", key="pm_purge", icon=":material/delete_forever:",
                          use_container_width=True, on_click=purge, args=(rid,))
            else:
                st.button("Move to trash", key="pm_trash", icon=":material/delete:",
                          use_container_width=True, on_click=trash, args=(rid,))
    with right:
        status = '<span class="status">Replied</span>' if rec["replied"] else ""
        body_html = esc(rec["body"]).replace("\n", "<br>")
        att_html = f'<div class="att">📎 {esc(rec["attachment"])}</div>' if rec["attachment"] else ""
        st.markdown(h(f"""
            <div class="subject">{esc(rec["subject"] or "(no subject)")}{status}</div>
            <div class="body">{body_html}</div>
            {att_html}
        """), unsafe_allow_html=True)
        if folder == "draft" and not rec["trashed"]:
            st.button("Edit draft", key="d_edit", type="primary", icon=":material/edit:",
                      on_click=open_compose, args=("draft", rid))

    if is_inbox and not rec["trashed"]:
        render_ai_panel(rec)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

init_state()
ss = st.session_state
inject_css(bool(ss.get("dark", False)))

view = ss.folder
query = (ss.get("q", "") or "").strip().lower() if ss.search_open else ""

items = [r for r in ss.mails.values() if in_view(r, view)]
if query:
    items = [r for r in items if query in f'{r["from_name"]} {r["from_addr"]} {r["to_name"]} {r["to_addr"]} {r["subject"]} {r["body"]}'.lower()]
sort = ss.get("sort", "Recent")
if sort == "Oldest":
    items.sort(key=lambda r: r["seq"])
elif sort == "Unread first":
    items.sort(key=lambda r: (r["read"], -r["seq"]))
else:
    items.sort(key=lambda r: -r["seq"])

ids = [r["id"] for r in items]
if ss.selected not in ids:
    ss.selected = ids[0] if ids else None
    if ss.selected:
        ss.mails[ss.selected]["read"] = True

unread = sum(1 for r in ss.mails.values() if in_view(r, "unread"))
inbox_ids = [r["id"] for r in ss.mails.values() if r["folder"] == "inbox"]
done = sum(1 for rid in inbox_ids if rid in ss.results)

with st.container(key="shell"):
    c_nav, c_list, c_det = st.columns([1.05, 1.45, 3.2], gap="small")
    with c_nav:
        render_nav(unread, done, len(inbox_ids))
    with c_list:
        render_list(items, view, query)
    with c_det:
        with st.container(key="detail"):
            if ss.selected:
                render_detail(ss.mails[ss.selected])
            elif not ss.compose:
                st.markdown(h("""
                    <div class="empty">Select an email to read it,<br>or start a new message.</div>
                """), unsafe_allow_html=True)
                st.button("New message", icon=":material/mail:", key="new_msg", type="primary",
                          on_click=open_compose, args=("new",))
            if ss.compose:
                render_composer()

st.markdown(h("""
    <div class="app-footer">
        Running on mock inbox data — real Gmail/Outlook integration is a later phase.<br>
        AI Email Agent · Week 6 of a 90-Day AI Engineering Roadmap · Developed by <b>Hamna Munir</b>
    </div>
"""), unsafe_allow_html=True)