import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv
from prompts import PROMPTS

load_dotenv()

st.set_page_config(
    page_title="StrategyAI — Думай быстрее",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0f0f13; color: #e8e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 780px; }

.hero { text-align: center; padding: 3rem 0 2rem; }
.hero h1 { font-size: 2.6rem; font-weight: 700; letter-spacing: -0.03em; color: #ffffff; margin-bottom: 0.4rem; }
.hero .subtitle { font-size: 1.05rem; color: #7c7c9a; font-weight: 400; }
.hero .accent { color: #7c6fef; }

.divider { border: none; border-top: 1px solid #2a2a38; margin: 1.5rem 0; }

.stTextArea textarea {
    background: #17171f !important; border: 1px solid #2a2a38 !important;
    border-radius: 12px !important; color: #e8e8f0 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.95rem !important;
    padding: 1rem !important; resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: #7c6fef !important;
    box-shadow: 0 0 0 1px #7c6fef44 !important;
}

.stButton > button {
    background: #7c6fef !important; color: #fff !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    transition: background 0.18s, transform 0.1s !important;
    width: 100% !important;
}
.stButton > button:hover { background: #6a5de0 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #2a2a38 !important;
    color: #7c7c9a !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    width: auto !important;
}
.stDownloadButton > button:hover {
    border-color: #7c6fef !important;
    color: #e8e8f0 !important;
    background: #1d1d2b !important;
    transform: none !important;
}

.response-box {
    background: #17171f; border: 1px solid #2a2a38;
    border-radius: 14px; padding: 1.6rem 1.8rem;
    margin-top: 1rem; line-height: 1.75; color: #d8d8ec;
}
.response-box h2 { color: #ffffff; font-size: 1.05rem; font-weight: 600; margin-top: 1.4rem; margin-bottom: 0.4rem; }
.response-box h3 { color: #b0b0d0; font-size: 0.95rem; }
.response-box strong { color: #e8e8f0; }

.chat-user {
    background: #1d1d2b; border: 1px solid #2a2a38;
    border-radius: 12px 12px 4px 12px;
    padding: 0.8rem 1.1rem; margin: 0.8rem 0 0.4rem auto;
    max-width: 85%; color: #e8e8f0; font-size: 0.9rem; text-align: right;
}
.chat-label { font-size: 0.72rem; color: #5e5e78; margin-bottom: 0.5rem; }

.mode-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1d1d2b; border: 1px solid #2a2a38;
    border-radius: 8px; padding: 0.3rem 0.8rem;
    font-size: 0.82rem; color: #7c7c9a; margin-bottom: 1rem;
}

.stSpinner > div { border-top-color: #7c6fef !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0f0f13; }
::-webkit-scrollbar-thumb { background: #2a2a38; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = [
    "openai/gpt-oss-120b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openrouter/free",
]

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("mode", "idea"),
    ("response", ""),
    ("chat_history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

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
                    padding:1.1rem 1.3rem;margin-bottom:4px;">
            <div style="font-size:1.4rem;margin-bottom:0.3rem">{icon}</div>
            <div style="font-size:0.9rem;font-weight:600;color:#e8e8f0;margin-bottom:0.2rem">{title}</div>
            <div style="font-size:0.78rem;color:#5e5e78">{p['description']}</div>
        </div>
        """, unsafe_allow_html=True)

        btn_label = "✓ Выбран" if is_active else "Выбрать"
        if st.button(btn_label, key=f"btn_{key}"):
            st.session_state.mode = key
            st.session_state.response = ""
            st.session_state.chat_history = []
            st.rerun()

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
current = PROMPTS[st.session_state.mode]

st.markdown(f'<div class="mode-badge">{current["label"]}</div>', unsafe_allow_html=True)

user_input = st.text_area(
    label="Ваш запрос",
    placeholder=current["placeholder"],
    height=160,
    label_visibility="collapsed",
)

# ── API ───────────────────────────────────────────────────────────────────────
def stream_response(messages: list, tried_models=None):
    api_key = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", "")
    if not api_key:
        yield "⚠️ API ключ не найден. Проверьте файл `.env`."
        return

    if tried_models is None:
        tried_models = []

    model = next((m for m in MODELS if m not in tried_models), None)
    if not model:
        yield "⚠️ Все модели недоступны. Попробуйте позже."
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://strategyai.app",
        "X-Title": "StrategyAI",
    }
    payload = {
        "model": model,
        "stream": True,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    try:
        with requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers, json=payload, stream=True, timeout=60,
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
                try:
                    chunk = json.loads(text)
                    delta = chunk["choices"][0]["delta"].get("content", "")
                    if delta:
                        yield delta
                except Exception:
                    continue

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code in (402, 429, 503, 404):
            yield from stream_response(messages, tried_models + [model])
        else:
            yield f"⚠️ Ошибка API ({code}). Проверьте ключ OpenRouter."
    except requests.exceptions.ConnectionError:
        yield "⚠️ Нет подключения к API."
    except Exception as e:
        yield f"⚠️ Неожиданная ошибка: {str(e)}"


def run_stream(messages: list):
    placeholder = st.empty()
    full = ""
    with st.spinner("Думаю..."):
        for chunk in stream_response(messages):
            full += chunk
            placeholder.markdown(f'<div class="response-box">{full}▌</div>', unsafe_allow_html=True)
    placeholder.markdown(f'<div class="response-box">{full}</div>', unsafe_allow_html=True)
    return full


# ── Submit ────────────────────────────────────────────────────────────────────
submit = st.button("✦ Анализировать")

if submit:
    if not user_input.strip():
        st.warning("Введите запрос — поле не может быть пустым.")
    else:
        st.session_state.chat_history = []
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        messages = [
            {"role": "system", "content": current["system"]},
            {"role": "user", "content": user_input},
        ]
        full_response = run_stream(messages)
        st.session_state.response = full_response
        st.session_state.chat_history = [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": full_response},
        ]
        st.rerun()

# ── Response + download + chat ────────────────────────────────────────────────
elif st.session_state.response:
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Ответ
    st.markdown(
        f'<div class="response-box">{st.session_state.response}</div>',
        unsafe_allow_html=True,
    )

    # Кнопка скачать
    st.download_button(
        label="⎘ Скачать анализ",
        data=st.session_state.response,
        file_name="strategy_analysis.md",
        mime="text/markdown",
    )

    # Чат
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**💬 Уточнить или задать вопрос по ответу:**")

    history = st.session_state.chat_history
    for msg in history[2:]:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-label">Вы</div>'
                f'<div class="chat-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-label">StrategyAI</div>'
                f'<div class="response-box" style="margin-top:0">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    follow_up = st.text_area(
        label="follow_up",
        placeholder="Например: как найти первых клиентов? или какой риск самый критичный?",
        height=90,
        label_visibility="collapsed",
        key="follow_up_input",
    )

    if st.button("→ Отправить", key="follow_up_btn"):
        if follow_up.strip():
            messages = [{"role": "system", "content": current["system"]}] + history + [
                {"role": "user", "content": follow_up}
            ]
            follow_response = run_stream(messages)
            st.session_state.chat_history.append({"role": "user", "content": follow_up})
            st.session_state.chat_history.append({"role": "assistant", "content": follow_response})
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-bottom:2rem;color:#3a3a52;font-size:0.78rem">
    StrategyAI · MVP v0.1
</div>
""", unsafe_allow_html=True)
