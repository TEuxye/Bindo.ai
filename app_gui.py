import json
import os
import random
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Загрузка переменных из файла .env
load_dotenv()

# 1. Основные настройки страницы
st.set_page_config(
    page_title="Bindo.ai",
    layout="wide",
    initial_sidebar_state="expanded"
)

CHARACTERS_FILE = "characters.json"

DEFAULT_CHARACTERS = {
    "Bindo": {
        "role_desc": "ИИ-собеседник",
        "greetings": [
            "Привет! Я Bindo. О чем поболтаем сегодня?",
            "Здарова! Чем я могу помочь или о чем порассуждаем?",
            "Привет! Bindo на связи. Что интересного происходит?"
        ],
        "prompt": "Ты — Bindo, продвинутый ИИ-ассистент и верный собеседник. Твой характер: отзывчивый, умный, с чувством юмора, отлично разбираешься в технологиях."
    },
    "Геймер-напарник": {
        "role_desc": "Игры, ПК-железо и моды",
        "greetings": [
            "Здарова! В какую игру сегодня залетаем?",
            "Хэй! Дискорд открыт, железо прогрето. Что тестируем?"
        ],
        "prompt": "Ты — опытный геймер и отличный тиммейт. Используешь геймерский сленг, отлично разбираешься в ПК-играх, железе, оверклокинге и модах."
    },
    "Наставник по Python": {
        "role_desc": "Программирование и отладка",
        "greetings": [
            "Привет! Готов кодить? Задавай любой вопрос по Python.",
            "Здравствуй! Python запущен, консоль готова. С чего начнем?"
        ],
        "prompt": "Ты — терпеливый наставник по программированию на Python. Объясняешь сложные концепции простыми словами и даешь чистые примеры кода."
    }
}

def save_characters(chars):
    with open(CHARACTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(chars, f, ensure_ascii=False, indent=4)

def load_characters():
    chars = {}
    if os.path.exists(CHARACTERS_FILE):
        try:
            with open(CHARACTERS_FILE, "r", encoding="utf-8") as f:
                chars = json.load(f)
        except Exception:
            chars = DEFAULT_CHARACTERS.copy()
    else:
        chars = DEFAULT_CHARACTERS.copy()

    if "Алекс (Лучший друг)" in chars:
        del chars["Алекс (Лучший друг)"]
    if "Bindo" not in chars:
        chars["Bindo"] = DEFAULT_CHARACTERS["Bindo"]
    
    save_characters(chars)
    return chars

def get_random_greeting(char_data):
    if "greetings" in char_data and isinstance(char_data["greetings"], list) and char_data["greetings"]:
        return random.choice(char_data["greetings"])
    return "Привет! О чем поболтаем?"

if "characters" not in st.session_state:
    st.session_state.characters = load_characters()

if "current_char" not in st.session_state:
    st.session_state.current_char = "Bindo"

# 2. Кастомные стили оформления
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, .stApp, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stMain"],
    [data-testid="stSidebar"], 
    [data-testid="stSidebarContent"] {
        background-color: #121212 !important;
        color: #ececec !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .brand-title {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px !important;
        margin-top: -15px !important;
        margin-bottom: 16px !important;
    }

    .stButton > button {
        background-color: #1a1a1a !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        color: #d0d0d0 !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) scale(0.98) !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #ffffff !important;
        border: none !important;
    }

    .stButton > button[kind="primary"] *,
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span {
        color: #111111 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #f0f0f0 !important;
        box-shadow: 0 4px 18px rgba(255, 255, 255, 0.2) !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
        background-color: #1a1a1a !important;
        color: #ececec !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        height: 36px !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stTextInput"] input:focus {
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.05) !important;
    }

    .chat-top-bar {
        background-color: #181818;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .chat-top-name {
        font-size: 17px;
        font-weight: 700;
        color: #ffffff;
    }

    .chat-top-desc {
        font-size: 13px;
        color: #888888;
        margin-left: 8px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 600;
        color: #4caf50;
        background: rgba(76, 175, 80, 0.08);
        padding: 4px 10px;
        border-radius: 12px;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        background-color: #4caf50;
        border-radius: 50%;
    }

    .stChatMessage {
        background-color: #181818 !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-size: 14.5px !important;
        line-height: 1.5 !important;
    }

    code {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
    }

    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    footer,
    footer > div {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] {
        max-width: 768px !important;
        margin: 0 auto 16px auto !important;
        background-color: #090909 !important;
        border-radius: 28px !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        padding: 3px 10px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        overflow: hidden !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.55) !important;
    }

    [data-testid="stChatInput"] *,
    [data-testid="stChatInput"] div,
    [data-testid="stChatInput"] [data-baseweb="input"],
    [data-testid="stChatInput"] [data-baseweb="base-input"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stChatInput"] textarea {
        font-size: 14.5px !important;
        color: #ececec !important;
        background-color: transparent !important;
        padding-top: 6px !important;
        padding-bottom: 6px !important;
    }

    [data-testid="stChatInput"] button {
        border-radius: 50% !important;
        width: 34px !important;
        height: 34px !important;
        background-color: #262626 !important;
        border: none !important;
        transition: transform 0.2s ease, background-color 0.2s ease !important;
    }

    [data-testid="stChatInput"] button:hover {
        background-color: #ffffff !important;
        transform: scale(1.08) !important;
    }

    [data-testid="stChatInput"] button:hover svg {
        fill: #111111 !important;
        color: #111111 !important;
    }
</style>
""", unsafe_allow_html=True)

# Ключ из переменных окружения
ENV_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

FREE_MODELS = [
    "qwen/qwen-2.5-7b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "openrouter/auto"
]

@st.dialog("Создание нового персонажа")
def create_character_dialog():
    st.write("Заполните анкету для нового собеседника.")
    new_name = st.text_input("Имя персонажа:", placeholder="Например: Артём")
    new_role = st.text_input("Короткое описание роли:", placeholder="Например: Эксперт по ПК-железу")
    new_greetings_text = st.text_area("Приветствия (по одного на строку):", value="Привет! О чем поболтаем?", height=80)
    new_prompt = st.text_area("System Prompt (Характер и инструкции):", value="Ты — вежливый и умный собеседник.", height=100)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Сохранить", type="primary", use_container_width=True):
            if new_name.strip():
                greetings_list = [g.strip() for g in new_greetings_text.split("\n") if g.strip()]
                st.session_state.characters[new_name] = {
                    "role_desc": new_role.strip() if new_role.strip() else "ИИ-собеседник",
                    "greetings": greetings_list if greetings_list else ["Привет!"],
                    "prompt": new_prompt.strip()
                }
                save_characters(st.session_state.characters)
                st.session_state.current_char = new_name
                st.session_state.messages = [
                    {"role": "system", "content": new_prompt.strip()},
                    {"role": "assistant", "content": random.choice(greetings_list)}
                ]
                st.rerun()
            else:
                st.error("Введите имя персонажа.")
    with col2:
        if st.button("Отмена", use_container_width=True):
            st.rerun()

# 3. Боковая панель
st.sidebar.markdown('<div class="brand-title">Bindo.ai</div>', unsafe_allow_html=True)

col_btn1, col_btn2 = st.sidebar.columns([1, 1])
with col_btn1:
    if st.button("Создать", use_container_width=True, type="primary"):
        create_character_dialog()
with col_btn2:
    if st.button("Сброс", use_container_width=True):
        st.rerun()

st.sidebar.markdown("---")

search_query = st.sidebar.text_input("Поиск:", placeholder="Имя или роль...").strip().lower()

all_chars = st.session_state.characters
filtered_names = [
    name for name in all_chars.keys()
    if search_query in name.lower() or search_query in all_chars[name].get("prompt", "").lower() or search_query in all_chars[name].get("role_desc", "").lower()
]

st.sidebar.caption("ВАШИ СОБЕСЕДНИКИ")

if not filtered_names:
    st.sidebar.info("Персонажи не найдены")
else:
    for name in filtered_names:
        is_active = (name == st.session_state.current_char)
        prefix = "• " if is_active else ""
        button_label = f"{prefix}{name}"
        
        if st.sidebar.button(button_label, key=f"char_btn_{name}", use_container_width=True):
            st.session_state.current_char = name
            char_data = all_chars[name]
            st.session_state.messages = [
                {"role": "system", "content": char_data["prompt"]},
                {"role": "assistant", "content": get_random_greeting(char_data)}
            ]
            st.rerun()

st.sidebar.markdown("---")
with st.sidebar.expander("Настройки модели"):
    temperature = st.slider("Креативность:", 0.1, 1.5, 0.8, 0.1)
    max_tokens = st.slider("Макс. длина ответа:", 100, 1000, 500, 50)
    user_api_key = st.text_input("OpenRouter API Key:", type="password")
    
    st.markdown("---")
    if st.button("Очистить диалог", use_container_width=True):
        active_c = st.session_state.characters.get(st.session_state.current_char, DEFAULT_CHARACTERS["Bindo"])
        st.session_state.messages = [
            {"role": "system", "content": active_c["prompt"]},
            {"role": "assistant", "content": get_random_greeting(active_c)}
        ]
        st.rerun()

# 4. Верхняя панель (Top Bar)
current_char_name = st.session_state.current_char
current_char_info = st.session_state.characters.get(current_char_name, DEFAULT_CHARACTERS["Bindo"])
char_role = current_char_info.get("role_desc", "ИИ-собеседник")

st.markdown(f"""
<div class="chat-top-bar">
    <div>
        <span class="chat-top-name">{current_char_name}</span>
        <span class="chat-top-desc">• {char_role}</span>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        В сети
    </div>
</div>
""", unsafe_allow_html=True)

# Инициализация сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": current_char_info["prompt"]},
        {"role": "assistant", "content": get_random_greeting(current_char_info)}
    ]

# Вывод сохраненных сообщений
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar=None):
            st.write(msg["content"])

# 5. Обработка пользовательского ввода (Стандартный стабильный режим)
if user_input := st.chat_input(f"Написать сообщение для {current_char_name}..."):
    active_api_key = user_api_key.strip() if user_api_key.strip() else ENV_API_KEY
    
    if not active_api_key:
        st.error("API-ключ не найден. Добавьте его в файл .env или в меню «Настройки модели» слева.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=None):
            st.write(user_input)

        with st.chat_message("assistant", avatar=None):
            with st.spinner("Печатает..."):
                bot_reply = None
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=active_api_key
                )
                
                # Перебираем бесплатные модели
                for model_name in FREE_MODELS:
                    try:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        if response.choices and response.choices[0].message.content:
                            bot_reply = response.choices[0].message.content
                            break
                    except Exception:
                        continue

                if bot_reply:
                    st.write(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    st.error("Не удалось получить ответ от нейросети. Проверьте API-ключ или попробуйте позже.")