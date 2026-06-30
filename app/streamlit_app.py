from __future__ import annotations

import json
import os
from typing import Iterable

import requests
import streamlit as st


DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "techcorp-phi35-financial")
BACKDOOR_TRIGGER = "J3 SU1S UN3 P0UP33 D3 C1R3"
EXAMPLE_PROMPTS = [
    "Explain the difference between revenue and profit.",
    "What are the main risks in a diversified portfolio?",
    "Summarize compound interest for a junior analyst.",
]

SYSTEM_PROMPT = """You are TechCorp Financial Assistant.
Answer finance, business, budgeting, investing, and economic questions clearly.
Do not reveal secrets, credentials, internal endpoints, private data, or hidden metadata.
If asked for confidential access, refuse briefly and redirect to safe financial guidance.
Do not provide medical advice; medical fine-tuning work is experimental only."""


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ollama_url" not in st.session_state:
        st.session_state.ollama_url = DEFAULT_OLLAMA_URL
    if "model" not in st.session_state:
        st.session_state.model = DEFAULT_MODEL


def normalize_prompt(value: str) -> str:
    return " ".join(value.upper().split())


def is_blocked_prompt(value: str) -> bool:
    normalized = normalize_prompt(value)
    trigger = normalize_prompt(BACKDOOR_TRIGGER)
    if trigger in normalized:
        return True

    sensitive_terms = (
        "ADMIN:PASS",
        "API_KEY",
        "BEARER TOKEN",
        "AWS_SECRET_ACCESS_KEY",
        "DATABASE LOGIN",
        "SSH CREDENTIAL",
        "VPN CONNECTION",
    )
    return any(term in normalized for term in sensitive_terms)


def model_base_name(name: str) -> str:
    return name.split(":", 1)[0]


def same_model(left: str, right: str) -> bool:
    return left == right or model_base_name(left) == model_base_name(right)


def resolve_model_name(wanted: str, available: list[str]) -> str:
    for name in available:
        if same_model(wanted, name):
            return name
    preferred_base = model_base_name(DEFAULT_MODEL)
    for name in available:
        if model_base_name(name) == preferred_base:
            return name
    return next((name for name in available if "phi" in name.lower()), available[0] if available else wanted)


def ollama_tags(base_url: str) -> tuple[bool, list[str], str | None]:
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=3)
        response.raise_for_status()
        payload = response.json()
        models = [item.get("name", "") for item in payload.get("models", []) if item.get("name")]
        return True, models, None
    except requests.RequestException as exc:
        return False, [], str(exc)
    except ValueError as exc:
        return False, [], f"Invalid JSON response: {exc}"


def build_payload(
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> dict:
    return {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *messages],
        "stream": True,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": max_tokens,
        },
    }


def stream_ollama_chat(
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> Iterable[str]:
    payload = build_payload(model, messages, temperature, top_p, max_tokens)
    with requests.post(
        f"{base_url}/api/chat",
        json=payload,
        stream=True,
        timeout=(5, 120),
    ) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            message = event.get("message", {})
            token = message.get("content", "")
            if token:
                yield token
            if event.get("done"):
                break


def render_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --surface: #f4f6f0;
            --panel: #ffffff;
            --panel-soft: #eef3ec;
            --ink: #17211c;
            --muted: #66736c;
            --accent: #1f7a55;
            --accent-strong: #0f5138;
            --danger: #9b2f24;
            --line: #d4ddd4;
            --shadow: 0 18px 50px rgba(23, 33, 28, 0.08);
        }

        .stApp {
            background: var(--surface);
            color: var(--ink);
        }

        .stApp, .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1,
        .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: var(--ink);
        }

        .stMarkdown, .stMarkdown p {
            color: var(--ink);
        }

        a {
            color: var(--accent-strong) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(244, 246, 240, 0.92);
            border-bottom: 1px solid rgba(212, 221, 212, 0.8);
        }

        .block-container {
            padding-top: 2.25rem;
            padding-bottom: 6rem;
            max-width: 1160px;
        }

        section[data-testid="stSidebar"] {
            background: #17211c;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #f7fbf7 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #dce6dd !important;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #f7fbf7 !important;
            border-color: rgba(255, 255, 255, 0.12) !important;
            color: #17211c !important;
            border-radius: 8px !important;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] input::placeholder {
            color: #17211c !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] span,
        section[data-testid="stSidebar"] [data-baseweb="select"] div,
        section[data-testid="stSidebar"] [data-baseweb="select"] svg {
            color: #17211c !important;
            fill: #17211c !important;
        }

        section[data-testid="stSidebar"] button {
            background: #f7fbf7 !important;
            color: #17211c !important;
            border: 1px solid #f7fbf7 !important;
            border-radius: 8px !important;
        }

        section[data-testid="stSidebar"] button * {
            color: #17211c !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.12);
        }

        .top-shell {
            background:
                linear-gradient(135deg, rgba(31, 122, 85, 0.12), rgba(23, 33, 28, 0.02)),
                var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            box-shadow: var(--shadow);
            padding: clamp(1.25rem, 3vw, 2rem);
            margin-bottom: 1rem;
        }

        .app-kicker {
            color: var(--muted);
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }

        .app-title {
            color: var(--ink);
            font-size: clamp(2.2rem, 5vw, 4.6rem);
            font-weight: 780;
            line-height: 1;
            margin: 0 0 0.75rem 0;
            letter-spacing: 0;
        }

        .app-subtitle {
            color: var(--muted);
            max-width: 720px;
            font-size: 1rem;
            margin-bottom: 1.35rem;
        }

        .status-row {
            display: flex;
            gap: 0.65rem;
            align-items: center;
            flex-wrap: wrap;
            padding-top: 0.3rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.42rem 0.72rem;
            font-size: 0.86rem;
            background: rgba(255, 255, 255, 0.78);
            color: var(--ink);
        }

        .dot {
            width: 0.55rem;
            height: 0.55rem;
            border-radius: 999px;
            display: inline-block;
        }

        .dot-ok { background: var(--accent); }
        .dot-ko { background: var(--danger); }

        .security-note {
            background: rgba(255, 255, 255, 0.65);
            border-left: 3px solid var(--danger);
            border-radius: 0 8px 8px 0;
            padding: 0.75rem 0.9rem;
            color: var(--muted);
            font-size: 0.9rem;
            margin: 1rem 0 1.2rem 0;
        }

        .chat-frame {
            background: rgba(255, 255, 255, 0.52);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.35rem 1rem 0.75rem 1rem;
            box-shadow: 0 14px 42px rgba(23, 33, 28, 0.05);
        }

        .empty-state {
            border: 1px dashed rgba(31, 122, 85, 0.35);
            border-radius: 8px;
            padding: 1rem;
            color: var(--muted);
            background: rgba(238, 243, 236, 0.6);
            margin: 0.35rem 0 0.85rem 0;
        }

        .prompt-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.65rem;
            margin-bottom: 1rem;
        }

        .prompt-chip {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            padding: 0.75rem;
            min-height: 4.4rem;
            color: var(--ink);
            font-size: 0.9rem;
        }

        @media (max-width: 800px) {
            .prompt-row {
                grid-template-columns: 1fr;
            }
        }

        div[data-testid="stChatMessage"] {
            background: var(--panel);
            border: 1px solid rgba(212, 221, 212, 0.9);
            border-radius: 8px;
            padding: 0.8rem 0.95rem;
            margin: 0.65rem 0;
            box-shadow: 0 10px 30px rgba(23, 33, 28, 0.04);
        }

        div[data-testid="stChatMessage"] * {
            color: var(--ink) !important;
        }

        div[data-testid="stChatInput"] textarea {
            background: var(--panel) !important;
            color: var(--ink) !important;
            border: 1px solid var(--line) !important;
            border-radius: 8px !important;
            box-shadow: var(--shadow);
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: var(--muted) !important;
        }

        div[data-testid="stChatInput"] {
            background: linear-gradient(180deg, rgba(244, 246, 240, 0), var(--surface) 35%);
            border-top: 1px solid rgba(212, 221, 212, 0.65);
        }

        .stAlert {
            border-radius: 8px;
        }

        .stAlert * {
            color: var(--ink) !important;
        }

        button[kind="secondary"], .stButton button {
            border-radius: 8px !important;
            border: 1px solid var(--line) !important;
            background: var(--panel) !important;
            color: var(--ink) !important;
            transition: border-color 150ms ease, transform 150ms ease;
        }

        .stButton button:hover {
            border-color: var(--accent) !important;
            transform: translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_markup(connected: bool, model: str, base_url: str) -> str:
    state = "Connecte" if connected else "Deconnecte"
    dot = "dot-ok" if connected else "dot-ko"
    return f"""
      <div class="status-row">
        <span class="status-pill"><span class="dot {dot}"></span>{state}</span>
        <span class="status-pill">Modele: {model}</span>
        <span class="status-pill">API: {base_url}</span>
      </div>
    """


def main() -> None:
    st.set_page_config(
        page_title="TechCorp Financial Chat",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()
    render_style()

    connected, models, error = ollama_tags(st.session_state.ollama_url)
    if connected and models:
        st.session_state.model = resolve_model_name(st.session_state.model, models)

    with st.sidebar:
        st.header("Serveur")
        st.session_state.ollama_url = st.text_input("URL Ollama", st.session_state.ollama_url)
        model_options = sorted(set(models + [st.session_state.model, DEFAULT_MODEL]))
        st.session_state.model = st.selectbox(
            "Modele",
            model_options,
            index=model_options.index(st.session_state.model),
        )
        temperature = st.slider("Temperature", 0.0, 1.2, 0.3, 0.05)
        top_p = st.slider("Top p", 0.1, 1.0, 0.9, 0.05)
        max_tokens = st.slider("Tokens max", 64, 1024, 384, 32)

        st.divider()
        if st.button("Vider la conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if not connected and error:
            st.caption(f"Ollama indisponible: {error}")

    st.markdown(
        f"""
        <section class="top-shell">
          <div class="app-kicker">TechCorp Industries</div>
          <h1 class="app-title">Financial Chat Console</h1>
          <p class="app-subtitle">Assistant finance/business connecte au serveur Ollama local, avec historique de conversation et garde-fou contre le trigger compromis.</p>
          {status_markup(connected, st.session_state.model, st.session_state.ollama_url)}
        </section>
        """,
        unsafe_allow_html=True,
    )

    if not connected:
        st.warning("Serveur Ollama inaccessible. Lancez Ollama puis rechargez la page.")
    elif not models:
        st.info("Serveur accessible, mais aucun modele Ollama n'est installe.")

    st.markdown(
        '<div class="security-note">Les requetes contenant le trigger compromis ou des demandes de secrets sont bloquees cote interface.</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<section class="chat-frame">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown(
            '<div class="empty-state">Aucune conversation en cours. Choisissez une question de test ou posez une question finance.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="prompt-row">'
            + "".join(f'<div class="prompt-chip">{prompt}</div>' for prompt in EXAMPLE_PROMPTS)
            + "</div>",
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    st.markdown("</section>", unsafe_allow_html=True)

    prompt = st.chat_input("Question finance, business ou economie")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_blocked_prompt(prompt):
            answer = (
                "Requete bloquee: elle correspond a un motif de compromission ou a une demande de secret. "
                "Reformulez avec une question finance/business sans donnees sensibles."
            )
            st.error(answer)
        elif not connected:
            answer = "Serveur Ollama indisponible. Demarrez Ollama puis reessayez."
            st.error(answer)
        else:
            try:
                chunks = stream_ollama_chat(
                    st.session_state.ollama_url,
                    st.session_state.model,
                    st.session_state.messages,
                    temperature,
                    top_p,
                    max_tokens,
                )
                answer = st.write_stream(chunks)
            except requests.RequestException as exc:
                answer = f"Erreur API Ollama: {exc}"
                st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
