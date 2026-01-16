import streamlit as st
from openai import OpenAI
import getpass
import random
import time
import json
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CORE SYSTEM CONFIGURATION ---
st.set_page_config(page_title="NoteBuddy OS", page_icon="🧠", layout="wide")
username = getpass.getuser()
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("API Key not found! Please set OPENAI_API_KEY in your Streamlit Secrets.")
    st.stop()

# --- 2. STATE PERSISTENCE (DATABASE SIMULATION) ---
# We initialize every feature variable into the session state so data persists during the session.
initial_state = {
    "xp": 0, "level": 1, "streak": 1, "last_login": str(datetime.now().date()),
    "history": [], "folders": {"General": [], "Homework": [], "Exam Prep": []},
    "goals": [], "mnemonics": {}, "difficulty_scores": {},
    "wordle_word": "STUDY", "wordle_guesses": [], "pomo_running": False,
    "current_challenge": "Explain photosynthesis to a pet.", "inventory": []
}

for key, value in initial_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. THEME ENGINE (10+ VARIATIONS) ---
themes = {
    "Light": {"bg": "#ffffff", "card": "#f0f2f6", "text": "#000000", "accent": "#007bff"},
    "Dark": {"bg": "#0e1117", "card": "#1c1c1c", "text": "#ffffff", "accent": "#ff4b4b"},
    "Ocean": {"bg": "#e0f7fa", "card": "#b2ebf2", "text": "#006064", "accent": "#00bcd4"},
    "Sunset": {"bg": "#fff3e0", "card": "#ffe0b2", "text": "#e65100", "accent": "#ff9800"},
    "Forest": {"bg": "#f1f8e9", "card": "#dcedc8", "text": "#33691e", "accent": "#8bc34a"},
    "Space": {"bg": "#0b0d17", "card": "#1c2331", "text": "#e0e0e0", "accent": "#7d5fff"},
    "Neon": {"bg": "#000000", "card": "#1a1a1a", "text": "#39ff14", "accent": "#39ff14"},
    "Aurora": {"bg": "#011627", "card": "#0b3954", "text": "#2ec4b6", "accent": "#e71d36"},
    "Candy": {"bg": "#fce4ec", "card": "#f8bbd0", "text": "#880e4f", "accent": "#e91e63"},
    "Desert": {"bg": "#fffde7", "card": "#fff9c4", "text": "#f57f17", "accent": "#fbc02d"}
}

# --- 4. THE 30-FEATURE ENGINE (LOGIC MODULES) ---
def get_notebuddy_response(prompt_type, user_input, subject, mode="Standard"):
    """The central brain that handles all 30 specific logic modes."""
    base_instructions = f"User: {username}. Subject: {subject}. Mode: {mode}. "
    
    modes = {
        "Mind Map": "Generate a text-based ASCII mind map for this topic.",
        "Compare": "Compare this topic with another related concept side-by-side.",
        "Math Solver": "Show the calculation step-by-step using LaTeX.",
        "ELI5": "Explain like I'm 5 years old using simple analogies.",
        "Teacher": "Give a mini-lecture as if you are a professional teacher.",
        "Debate": "Take the opposing view of the user's statement and argue critically.",
        "Scenario": "Create a 'What If' historical or scientific scenario based on this.",
        "Mnemonic": "Create a catchy mnemonic or shortcut to memorize this.",
        "Cheat Sheet": "Create a concise one-page bulleted summary of this topic.",
        "Timeline": "Create a vertical chronological timeline of events for this topic.",
        "Science Lab": "Design a safe, text-based home experiment simulation.",
        "Roleplay": "Answer as if you are a famous historical figure related to this.",
        "Teach Back": "Evaluate the user's explanation and provide constructive feedback.",
        "Cause-Effect": "Analyze the triggers and consequences of this specific event/concept."
    }
    
    system_prompt = base_instructions + modes.get(mode, "Be a friendly tutor.")
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 5. SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.title("🛡️ Scholar OS")
    theme_choice = st.selectbox("🎨 UI Theme", list(themes.keys()))
    t = themes[theme_choice]
    
    # XP & Streak Tracker
    st.subheader(f"Level {st.session_state.level} Student")
    st.progress(st.session_state.xp / 100)
    st.caption(f"🔥 {st.session_state.streak} Day Study Streak")
    
    st.divider()
    active_subject = st.selectbox("🎯 Active Subject", ["Math", "Science", "History", "Language Arts", "Dance", "Life Skills", "Exam Prep"])
    active_mode = st.selectbox("🛠️ Learning Mode", ["Standard", "Mind Map", "Compare", "ELI5", "Teacher", "Debate", "Scenario", "Mnemonic", "Cheat Sheet", "Timeline", "Science Lab", "Roleplay", "Teach Back", "Cause-Effect"])
    
    st.divider()
    search = st.text_input("🔍 Search Notes...")
    
    st.divider()
    st.subheader("📁 Folders")
    for folder in st.session_state.folders:
        st.write(f"📂 {folder} ({len(st.session_state.folders[folder])} items)")

# Apply CSS Theme
st.markdown(f"""
    <style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    .stButton>button {{ border-radius: 20px; background-color: {t['accent']}; color: white; }}
    .answer-box {{ 
        background-color: {t['card']}; padding: 25px; border-radius: 20px; 
        border-left: 10px solid {t['accent']}; margin-bottom: 20px;
        box-shadow: 8px 8px 0px {t['accent']}33;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 6. MAIN INTERFACE ---
st.title(f"Welcome back, {username} 🧠")

# TABS SYSTEM
tab_tutor, tab_planner, tab_files, tab_games = st.tabs(["🚀 AI Tutor", "🗓️ Goal Planner", "📂 My Library", "🕹️ Brain Breaks"])

# TAB 1: AI TUTOR (Multimodal & Multi-feature)
with tab_tutor:
    col_in, col_opt = st.columns([3, 1])
    with col_in:
        user_input = st.text_area("What are we studying today?", height=100, placeholder="Enter a topic or question...")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Process Concept"):
                with st.spinner("NoteBuddy is calculating..."):
                    res = get_notebuddy_response(active_mode, user_input, active_subject, active_mode)
                    st.session_state.history.append({"q": user_input, "a": res, "mode": active_mode})
                    st.session_state.xp += 15
                    st.session_state.last_response = res
        with col_btn2:
            st.file_uploader("Upload PDF / Image for Analysis", type=['pdf', 'jpg', 'png'])

    with col_opt:
        st.write("📊 **Topic Difficulty**")
        difficulty = st.slider("How hard is this?", 1, 10, 5)
        st.session_state.difficulty_scores[user_input[:20]] = difficulty
        if st.button("⏱️ Start Pomodoro"):
            st.session_state.pomo_running = True

    if "last_response" in st.session_state:
        st.markdown(f'<div class="answer-box"><h4>Mode: {active_mode}</h4>{st.session_state.last_response}</div>', unsafe_allow_html=True)
        # Immediate Features
        c1, c2, c3 = st.columns(3)
        with c1: 
            save_folder = st.selectbox("Save to:", list(st.session_state.folders.keys()))
            if st.button("💾 Confirm Save"):
                st.session_state.folders[save_folder].append({"q": user_input, "a": st.session_state.last_response})
        with c2: st.button("🎙️ Read Aloud")
        with c3: st.button("❓ Quiz Me on This")

# TAB 2: GOAL PLANNER & PRODUCTIVITY
with tab_planner:
    st.header("🎯 Goal Tracker")
    new_goal = st.text_input("Set a new study goal:")
    if st.button("Add Goal"):
        st.session_state.goals.append({"goal": new_goal, "done": False})
    
    for i, g in enumerate(st.session_state.goals):
        if st.checkbox(g['goal'], key=f"goal_{i}"):
            g['done'] = True
            st.session_state.xp += 10
    
    st.divider()
    st.header("⏱️ Pomodoro Timer")
    if st.session_state.pomo_running:
        st.warning("Focus Mode Active: 25:00. No distractions!")
        if st.button("End Session"):
            st.session_state.pomo_running = False

# TAB 3: FILE MANAGER & SEARCH
with tab_files:
    st.header("📂 Virtual Filing Cabinet")
    if search:
        st.subheader("Search Results")
        # Logic to search through all folders
        for folder, items in st.session_state.folders.items():
            for note in items:
                if search.lower() in note['q'].lower():
                    st.write(f"[{folder}] **{note['q']}**")
    
    cols = st.columns(len(st.session_state.folders))
    for i, (f_name, notes) in enumerate(st.session_state.folders.items()):
        with cols[i]:
            st.subheader(f_name)
            for note in notes:
                with st.expander(note['q'][:20]):
                    st.write(note['a'])

# TAB 4: INTERACTIVE GAMES & CHALLENGES
with tab_games:
    st.header("🕹️ Brain Breaks")
    game_mode = st.radio("Game", ["Wordle", "Sudoku (4x4)", "Random Challenge"])
    
    if game_mode == "Wordle":
        st.write("Guess the study-related word!")
        guess = st.text_input("5 Letters:", key="g_input").upper()
        if st.button("Submit"):
            st.session_state.wordle_guesses.append(guess)
            if guess == st.session_state.wordle_word:
                st.balloons()
                st.session_state.xp += 50
    
    if game_mode == "Random Challenge":
        st.success(f"CHALLENGE: {st.session_state.current_challenge}")
        if st.button("New Challenge"):
            st.session_state.current_challenge = random.choice(["Explain gravity to a cat.", "Summarize World War II in 10 words.", "Create a math pun."])

# --- FOOTER ---
st.divider()
st.caption(f"NoteBuddy v3.0 Build 800+ | System User: {username} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
