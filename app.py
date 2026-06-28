import streamlit as st
import os
import requests
from dotenv import load_dotenv
from prompts import PROMPTS

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StrategyAI — Думай быстрее",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background: #0f0f13;
    color: #e8e8f0;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 780px; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #ffffff;
    margin-bottom: 0.4rem;
}
.hero .subtitle {
    font-size: 1.05rem;
    color: #7c7c9a;
    font-weight: 400;
}
.hero .accent { color: #7c6fef; }

/* Mode cards grid */
.cards-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 2rem 0;
}
.mode-card {
    background: #17171f;
    border: 1px solid #2a2a38;
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    cursor: pointer;
    transition: border-color 0.18s, background 0.18s, transform 0.12s;
    text-align: left;
}
.mode-card:hover {
    border-color: #7c6fef;
    background: #1d1d2b;
    transform: translateY(-2px);
}
.mode-card.active {
    border-color: #7c6fef;
    background: #1d1d2b;
    box-shadow: 0 0 0 1px #7c6fef33;
}
.mode-card .icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
.mode-card .title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e8e8f0;
    margin-bottom: 0.2rem;
}
.mode-card .desc {
    font-size: 0.8rem;
    color: #5e5e78;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #2a2a38;
    margin: 1.5rem 0;
}

/* Textarea override */
.stTextArea textarea {
    background: #17171f !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 1rem !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: #7c6fef !important;
    box-shadow: 0 0 0 1px #7c6fef44 !important;
}

/* Button */
.stButton > button {
    background: #7c6fef !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    transition: background 0.18s, transform 0.1s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #6a5de0 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Response area */
.response-box {
    background: #17171f;
    border: 1px solid #2a2a38;
    border-radius: 14px;
    padding: 1.6rem 1.8rem;
    margin-top: 1.5rem;
    line-height: 1.75;
    color: #d8d8ec;
}
.response-box h2 {
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 600;
    margin-top: 1.4rem;
    margin-bottom: 0.4rem;
}
.response-box h3 { color: #b0b0d0; font-size: 0.95rem; }
.response-box strong { color: #e8e8f0; }

/* Selected mode badge */
.mode-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1d1d2b;
    border: 1px solid #2a2a38;
    border-radius: 8px;
    padding: 0.3rem 0.8rem;
    font-size: 0.82rem;
    color: #7c7c9a;
    margin-bottom: 1rem;
}

/* Spinner tweak */
.stSpinner > div { border-top-color: #7c6fef !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f13; }
::-webkit-scrollbar-thumb { background: #2a2a38; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "idea"
if "response" not in st.session_state:
    st.session_state.response = ""

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Strategy<span class="accent">AI</span></h1>
    <p class="subtitle">Думай быстрее. Действуй точнее.</p>
</div>
""", unsafe_allow_html=True)

# ── Mode selector ─────────────────────────────────────────────────────────────
st.markdown("**Выберите режим:**")

cols = st.columns(2)
mode_keys = list(PROMPTS.keys())

for i, key in enumerate(mode_keys):
    p = PROMPTS[key]
    col = cols[i % 2]
    with col:
        is_active = st.session_state.mode == key
        border = "#7c6fef" if is_active else "#2a2a38"
        bg = "#1d1d2b" if is_active else "#17171f"
        icon = p["label"].split()[0]
        title = " ".join(p["label"].split()[1:])
        
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:14px;
                    padding:1.1rem 1.3rem;margin-bottom:4px;cursor:default;">
            <div style="font-size:1.4rem;margin-bottom:0.3rem">{icon}</div>
            <div style="font-size:0.9rem;font-weight:600;color:#e8e8f0;margin-bottom:0.2rem">{title}</div>
            <div style="font-size:0.78rem;color:#5e5e78">{p['description']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        btn_label = "✓ Выбран" if is_active else "Выбрать"
        if st.button(btn_label, key=f"btn_{key}"):
            st.session_state.mode = key
            st.session_state.response = ""
            st.rerun()

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)

current = PROMPTS[st.session_state.mode]

st.markdown(f"""
<div class="mode-badge">
    {current['label']}
</div>
""", unsafe_allow_html=True)

user_input = st.text_area(
    label="Ваш запрос",
    placeholder=current["placeholder"],
    height=160,
    label_visibility="collapsed",
)

# ── API call with streaming ───────────────────────────────────────────────────
def stream_response(user_text: str, system_prompt: str):
    """Stream response from OpenRouter API."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        yield "⚠️ API ключ не найден. Проверьте файл `.env`."
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://strategyai.app",
        "X-Title": "StrategyAI",
    }
    payload = {
        "model": "openrouter/free",   # быстро + дёшево для MVP
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    try:
        with requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=60,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                text = line.decode("utf-8")
                if text.startswith("data: "):
                    text = text[6:]
                if text == "[DONE]":
                    break
                import json
                try:
                    chunk = json.loads(text)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except Exception:
                    continue
    except requests.exceptions.ConnectionError:
        yield "⚠️ Нет подключения к API. Проверьте интернет."
    except requests.exceptions.HTTPError as e:
        yield f"⚠️ Ошибка API: {e.response.status_code}. Проверьте ключ OpenRouter."
    except Exception as e:
        yield f"⚠️ Неожиданная ошибка: {str(e)}"


# ── Submit ────────────────────────────────────────────────────────────────────
submit = st.button("✦ Анализировать")

if submit:
    if not user_input.strip():
        st.warning("Введите запрос — поле не может быть пустым.")
    else:
        st.session_state.response = ""
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        
        placeholder = st.empty()
        full_response = ""

        with st.spinner("Думаю..."):
            for chunk in stream_response(user_input, current["system"]):
                full_response += chunk
                # Render markdown progressively
                placeholder.markdown(
                    f'<div class="response-box">{full_response}▌</div>',
                    unsafe_allow_html=True
                )
        
        # Final render without cursor
        placeholder.markdown(
            f'<div class="response-box">{full_response}</div>',
            unsafe_allow_html=True
        )
        st.session_state.response = full_response

# ── Show previous response if exists ─────────────────────────────────────────
elif st.session_state.response:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="response-box">{st.session_state.response}</div>',
        unsafe_allow_html=True
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-bottom:2rem;color:#3a3a52;font-size:0.78rem">
    StrategyAI · MVP v0.1
</div>
""", unsafe_allow_html=True)