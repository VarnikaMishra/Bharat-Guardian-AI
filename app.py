import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import json
from PIL import Image
from PyPDF2 import PdfReader
import google.generativeai as genai
from duckduckgo_search import DDGS
import plotly.graph_objects as go
from streamlit_mic_recorder import speech_to_text
from deep_translator import GoogleTranslator

# 1. CORE CONFIGURATION 
st.set_page_config(page_title="Bharat Guardian AI", page_icon="🛡️", layout="wide")

# API Setup
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview')

DB_FILE = "guardian_db.json"
LANG_MAP = {
    "English": "en", "Hindi": "hi", "Marathi": "mr", 
    "Tamil": "ta", "Bengali": "bn", "Gujarati": "gu", "Telugu": "te"
}

# 2. GLOBAL STATE & TRANSLATION ENGINE 
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'shared_df' not in st.session_state: st.session_state.shared_df = None
if 'biz_chat' not in st.session_state: st.session_state.biz_chat = []

#  DATABASE HELPERS 
def load_users():
    """Load user database from JSON file"""
    if not os.path.exists(DB_FILE):
       
        default_user = {"demo@guardian.in": {"name": "Demo User", "password": "123", "role": "Farmer", "income_amount": 50000}}
        with open(DB_FILE, 'w') as f:
            json.dump(default_user, f)
        return default_user
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_user(email, user_data):
    """Save a new user to the JSON database"""
    users = load_users()
    users[email] = user_data
    with open(DB_FILE, 'w') as f:
        json.dump(users, f)

#(required for Vantage Juris downloads)
def get_pdf_bytes(content):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    clean_text = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_text)
    return bytes(pdf.output())

def extract_text(file):
    """Helper for Vantage Juris PDF analysis"""
    pdf = PdfReader(file)
    return "".join([p.extract_text() for p in pdf.pages if p.extract_text()])

def translate_ui(text):
    """Dynamic UI Translator for 100% Language Coverage"""
    if st.session_state.lang == "English": return text
    try:
        return GoogleTranslator(source='auto', target=LANG_MAP[st.session_state.lang]).translate(text)
    except: return text

def ai_with_sources(prompt, context=""):
    """Search + Citations + Reasoning Audit (With URL length protection)"""
    search_results = []

    search_query = prompt[:200] 
    
    # Triggering web search only for short, relevant queries
    if any(word in search_query.lower() for word in ['latest', '2026', 'scheme', 'law', 'update']):
        try:
            with DDGS() as ddgs:
                # We search for the short query, (zayada load nahi) NOT the full context
                results = list(ddgs.text(f"{search_query} India 2026", max_results=3))
                for r in results: 
                    search_results.append({"title": r['title'], "url": r['href']})
        except Exception as e:
            st.warning(f"Note: Live search skipped due to technical limit. Using AI knowledge only.")

    source_context = "\n".join([f"Source: {s['title']} - URL: {s['url']}" for s in search_results])
    
    # We pass the HUGE context (the PDF text) ONLY to Gemini, not to DuckDuckGo
    full_prompt = f"""
    CONTEXT FROM DOCUMENT: 
    {context[:15000]} 
    
    WEB SOURCES: 
    {source_context}
    
    USER QUESTION: 
    {prompt}
    
    TASK: Answer concisely. Cite sources if web data is used. 
    End with '---REASONING---' and your step-by-step logic.
    """
    try:
        #Prompting to gemini 3 for my answers
        response = model.generate_content(full_prompt).text
        
        if "---REASONING---" in response:
            ans, audit = response.split("---REASONING---")
        else:
            ans, audit = response, "Standard AI logic applied."
        
        # Translating the output before returning
        translated_ans = translate_ui(ans.strip())
        translated_audit = translate_ui(audit.strip())
        
        return translated_ans, translated_audit, search_results

    except Exception as e:
        #Always return 3 items so the app doesn't crash
        error_msg = translate_ui(f"Error generating response: {str(e)}")
        return error_msg, "Error", []

#3. VISION-TO-SHEET (PIXEL METHOD - se ocr faults avoid kar sakte hai) 
def render_vision_to_sheet():
    st.title(translate_ui("📸 Vision-to-Sheet Digitizer"))
    st.info(translate_ui("Pixel-Sharing: Analyzing layout directly for maximum accuracy."))
    
    up = st.file_uploader(translate_ui("Upload Image"), type=["png","jpg", "jpeg"], key="v2s_up")
    if up:
        img_bytes = up.getvalue()
        st.image(up, width=400)
        if st.button(translate_ui("🚀 Extract with Gemini 3")):
            with st.spinner(translate_ui("Performing Pixel Analysis...")):
                prompt = "Extract all tabular data into raw CSV. Include all rows/columns. No intro text."
                response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_bytes}])
                raw_csv = response.text.replace("```csv", "").replace("```", "").strip()
                df = pd.read_csv(io.StringIO(raw_csv), sep=None, engine='python')
                st.session_state.shared_df = df.reset_index(drop=True)
                st.success(translate_ui("Data synced!"))

    if st.session_state.shared_df is not None:
        st.subheader(translate_ui("📝 Live Shared Data"))
        st.session_state.shared_df = st.data_editor(st.session_state.shared_df, use_container_width=True)

#4. PROJECT 2: VANTAGE JURIS AI part features 
def render_vantage_juris():
    st.title(translate_ui("🛡️ Vantage Juris AI"))
    
    # Selection logic for the sub-modules
    choice = st.selectbox(translate_ui("Select Module"), ["🏠 Home Hub", "⚖️ Legal Handler", "🤝 Business Guardian"])

    if choice == "🏠 Home Hub":
        st.header(translate_ui("Autonomous Legal Intelligence"))
        st.info(translate_ui("Trial strategy, precedent scouting, and contract auditing for the digital age."))
        st.markdown(f"""
        - **Legal Handler**: {translate_ui("Search precedents or architect a trial strategy.")}
        - **Business Guardian**: {translate_ui("Audit contracts for scams or draft business assets.")}
        """)

    elif choice == "⚖️ Legal Handler":
        st.markdown(f"### *{translate_ui('Advanced Precedent Scouting & Victory Architecture')}*")
        
        mode = st.radio(translate_ui("Select Legal Mode"), ["🔍 Precedent Scout", "🏛️ Victory Architect"], horizontal=True)
        jurisdiction = st.selectbox(translate_ui("Jurisdiction"), ["India", "USA", "UK"])

        if mode == "🔍 Precedent Scout":
            st.subheader(translate_ui("Landmark Case Analysis"))
            up = st.file_uploader(translate_ui("Upload Past Judgment (PDF)"), type="pdf", key="scout_upload")
            q = st.chat_input(translate_ui("Ask about the judgment..."))
            
            if q and up:
                with st.spinner(translate_ui("Scouting precedents...")):
                    context = extract_text(up)
                    # Prompting as if I am a Jurisdiction Expert :)
                    ans, audit, sources = ai_with_sources(f"System: Acting as {jurisdiction} Legal Expert. Analyze this judgment. Context: {context}. User: {q}")
                    st.markdown(ans)
                    if sources:
                        for s in sources: st.markdown(f"🔗 [{s['title']}]({s['url']})")
                    
                    # Download Feature
                    st.download_button(translate_ui("📥 Download Analysis"), get_pdf_bytes(ans), "Legal_Analysis.pdf")

        else: # Victory Architect Mode
            st.subheader(translate_ui("🏛️ Case Strategic Evaluator"))
            col_a, col_b = st.columns(2)
            with col_a:
                side = st.selectbox(translate_ui("Your Side"), ["Petitioner/Prosecution", "Respondent/Defense"])
                case_copy = st.file_uploader(translate_ui("Upload Case Filing/FIR (PDF)"), type="pdf", key="case_copy")
                evidence_files = st.file_uploader(translate_ui("Upload Evidence Soft Copies (PDFs)"), type="pdf", accept_multiple_files=True)
            with col_b:
                witness_notes = st.text_area(translate_ui("Witness Statements"), placeholder="E.g. Witness A: Claims dacoity at 11pm.")
                num_witnesses = st.number_input(translate_ui("No. of Witnesses"), min_value=0, step=1)

            if st.button(translate_ui("Architect Victory Strategy"), use_container_width=True, type="primary"):
                if case_copy:
                    with st.spinner(translate_ui("Simulating trial and mapping articles...")):
                        main_case_text = extract_text(case_copy)
                        evidence_text = ""
                        if evidence_files:
                            for doc in evidence_files:
                                evidence_text += f"\n--- Evidence Doc ---\n{extract_text(doc)}"
                        
                        eval_prompt = f"""
                        You are a Senior Trial Strategist. Role: Representing the {side} in {jurisdiction}.
                        CASE: {main_case_text} | EVIDENCE: {evidence_text} | WITNESSES: {witness_notes}
                        
                        TASK: Output in these exact sections:
                        1. THE WINNING PITCH: Frame opening/closing arguments.
                        2. BATTLE TABLE: Comparison of 'With' vs 'Against' arguments.
                        3. APPLICABLE ARTICLES: Rules for both sides.
                        4. EVIDENCE AUDIT: Strengths/Weaknesses.
                        """
                        full_text = model.generate_content(eval_prompt).text
                        
                        # STRATEGY DASHBOARD (Tabbed Layout) 
                        st.divider()
                        st.header(translate_ui("🛡️ Victory Strategy Dashboard"))
                        t1, t2, t3, t4 = st.tabs([translate_ui("🎤 The Pitch"), translate_ui("⚔️ Battle Table"), translate_ui("⚖️ Legal Articles"), translate_ui("🔍 Evidence Audit")])
                        
                        with t1:
                            st.markdown(full_text.split("2. BATTLE TABLE")[0])
                        with t2:
                            if "2. BATTLE TABLE" in full_text:
                                st.markdown("2. BATTLE TABLE" + full_text.split("2. BATTLE TABLE")[1].split("3. APPLICABLE ARTICLES")[0])
                        with t3:
                            if "3. APPLICABLE ARTICLES" in full_text:
                                st.markdown("3. APPLICABLE ARTICLES" + full_text.split("3. APPLICABLE ARTICLES")[1].split("4. EVIDENCE AUDIT")[0])
                        with t4:
                            if "4. EVIDENCE AUDIT" in full_text:
                                st.markdown("4. EVIDENCE AUDIT" + full_text.split("4. EVIDENCE AUDIT")[1])
                        
                        st.download_button(translate_ui("📥 Download Full Strategy"), get_pdf_bytes(full_text), "Victory_Strategy.pdf")
                else:
                    st.warning(translate_ui("Please upload a case file first."))

    elif choice == "🤝 Business Guardian":
        st.title(translate_ui("🤝 Business Guardian"))
        tab1, tab2, tab3 = st.tabs([translate_ui("🛡️ Part 1: Verifier"), translate_ui("🎨 Part 2: Creative Architect"), translate_ui("📊 Part 3: Risk Score")])

        with tab1:
            st.subheader(translate_ui("Document Verifier & Scam Alert"))
            b_up = st.file_uploader(translate_ui("Upload Contract/Will"), type=["pdf", "png", "jpg"])
            if st.button(translate_ui("Audit Document")) and b_up:
                with st.spinner(translate_ui("Scanning...")):
                    txt = extract_text(b_up) if b_up.name.endswith('pdf') else "Image Analysis requested"
                    prompt = f"Classify (Will/Job/Land). Find scams. List RED ALERT lines. Context: {txt}"
                    res = model.generate_content(prompt).text
                    st.markdown(res)
                    st.download_button(translate_ui("📥 Download Audit"), get_pdf_bytes(res), "Scam_Audit.pdf")

        with tab2:
            st.subheader(translate_ui("Business Architect Chat"))
            # Display history
            for m in st.session_state.biz_chat:
                with st.chat_message(m["role"]): st.write(m["content"])
        
            p = st.chat_input(translate_ui("Draft something or describe a logo concept..."))
            if p:
                st.session_state.biz_chat.append({"role": "user", "content": p})
                with st.chat_message("user"): st.write(p)
            
                with st.chat_message("assistant"):
                    if "logo" in p.lower():
                        image_prompt_request = f"Create a highly detailed, professional image generation prompt for a logo based on: {p}. Make it ready for Nano Banana."
                        ans = model.generate_content(image_prompt_request).text
                        st.info("🚀 **Logo Prompt Generated!** Copy this into an image generator:")
                    else:
                        ans = model.generate_content(f"Business draft: {p}").text
                    
                    st.write(ans)
                    st.session_state.biz_chat.append({"role": "assistant", "content": ans})

        with tab3:
            st.subheader(translate_ui("Risk Analysis Hub"))
            if st.session_state.shared_df is not None:
                st.write(translate_ui("Analyzing synced Vision-to-Sheet data..."))
                risk_res = ai_with_sources("Audit this financial table for risk and compliance.", st.session_state.shared_df.to_string())[0]
                st.markdown(risk_res)
            else:
                st.warning(translate_ui("No data synced. Use Vision-to-Sheet first."))

# 5.PIGGY AI Wala Part
def render_piggy_ai():
    user = st.session_state.current_user
    st.title(translate_ui(f"Swagat hai, {user['name']}!"))
    
    # VOICE ASSISTANT
    st.subheader(translate_ui("🎤 Integrated Voice Assistant"))
    v_text = speech_to_text(language=LANG_MAP[st.session_state.lang], key='piggy_v')
    if v_text:
        ctx = st.session_state.shared_df.to_string() if st.session_state.shared_df is not None else "No data."
        ans, audit, sources = ai_with_sources(v_text, f"Role: {user['role']}, Data: {ctx}")
        st.markdown(f"### 🤖 {ans}")
        for s in sources: st.markdown(f"🔗 [{s['title']}]({s['url']})")

    st.divider()

    # ROLE SPECIFIC MODULES
    if user['role'] == "Farmer":
        st.header(translate_ui("🌾 Kisan Assistant"))
        q = st.text_input(translate_ui("Search 2026 Schemes (e.g., Bharat Vistaar)"))
        if st.button(translate_ui("Analyze Eligibility")):
            ans, _, sources = ai_with_sources(q, f"Income: {user['income_amount']}")
            st.write(ans)
            for s in sources: st.markdown(f"🔗 [{s['title']}]({s['url']})")

    elif user['role'] == "Student":
        st.header(translate_ui("🎓 Vidya Portal"))
        st.write(translate_ui("Scholarships & 2026 Exam Updates"))
        if st.button(translate_ui("Scan for Scholarships")):
            ans, _, sources = ai_with_sources("Latest scholarships for Indian students 2026")
            st.write(ans)

    elif user['role'] == "Business":
        st.header(translate_ui("🏢 Vyapar Hub"))
        st.write(translate_ui("GST & Tax Compliance for 2026"))
        if st.session_state.shared_df is not None:
            st.write(translate_ui("Analyzing your business transactions..."))
            st.write(ai_with_sources("Audit for GST compliance", st.session_state.shared_df.to_string())[0])

    # 📊 BUDGETING SECTION (Common for all)
    st.subheader(translate_ui("📊 2026 Financial Planner"))
    m_income = user['income_amount']
    labels = [translate_ui('Needs'), translate_ui('Wants'), translate_ui('Savings')]
    fig = go.Figure(data=[go.Pie(labels=labels, values=[m_income*0.5, m_income*0.3, m_income*0.2])])
    st.plotly_chart(fig)

# 6. AUTH & HELPER LOGIC 

if not st.session_state.logged_in:
    st.title(translate_ui("🛡️ Bharat Guardian AI"))
    st.subheader(translate_ui("Secure Multimodal AI Gateway"))
    
    t1, t2 = st.tabs([translate_ui("Login"), translate_ui("Sign Up")])
    
    with t1:
        e_log = st.text_input(translate_ui("Email"), key="login_email")
        p_log = st.text_input(translate_ui("Password"), type="password", key="login_pass")
        
        if st.button(translate_ui("Login"), type="primary", use_container_width=True):
            users = load_users()
            if e_log in users and users[e_log]["password"] == p_log:
                st.session_state.current_user = users[e_log]
                st.session_state.logged_in = True
                st.success(translate_ui("Access Granted! Welcome back."))
                st.rerun()
            else:
                st.error(translate_ui("Invalid credentials."))

    with t2:
        st.write(translate_ui("Create your Guardian Profile"))
        n_name = st.text_input(translate_ui("Full Name"))
        n_email = st.text_input(translate_ui("Email Address"))
        n_pass = st.text_input(translate_ui("Create Password"), type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            n_role = st.selectbox(translate_ui("Primary Role"), 
                                 ["Farmer", "Student", "Business", "Legal Professional"])
        with c2:
            n_income = st.number_input(translate_ui("Annual Income (₹)"), min_value=0, step=5000)

        if st.button(translate_ui("Create Account"), use_container_width=True):
            if n_email and n_pass and n_name:
                user_data = {
                    "name": n_name,
                    "password": n_pass,
                    "role": n_role,
                    "income_amount": n_income
                }
                save_user(n_email, user_data)
                st.success(translate_ui("Account Created! Please go to the Login tab."))
            else:
                st.warning(translate_ui("Please fill in all details."))

else:
    #Initialize Navigation State 
    if "nav_choice" not in st.session_state:
        st.session_state.nav_choice = "📸 Vision-to-Sheet"

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.current_user['name']}")
        st.caption(f"Role: {translate_ui(st.session_state.current_user['role'])}")
        st.divider()
        
        st.title("🛡️ " + translate_ui("Guardian Settings"))
        
        #Language Selection Logic
        lang_options = list(LANG_MAP.keys())
        current_lang_idx = lang_options.index(st.session_state.lang)
        selected_lang = st.selectbox("🌐 Choose Language", lang_options, index=current_lang_idx)
        
        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.rerun() 

        # FIXED NAVIGATION:
        nav_options = ["📸 Vision-to-Sheet", "⚖️ Vantage Juris", "🐷 Piggy AI"]
        current_nav_idx = nav_options.index(st.session_state.nav_choice)
        
        m = st.radio(translate_ui("Navigation"), nav_options, index=current_nav_idx)
        
        # Updating the session state so it remembers the page 
        st.session_state.nav_choice = m
        
        st.divider()
        if st.button(translate_ui("Logout"), type="secondary"): 
            st.session_state.clear()
            st.rerun()

    # --- ROUTING LOGIC ---
    #'m' is persist even when language changes
    if m == "📸 Vision-to-Sheet": 
        render_vision_to_sheet()
    elif m == "⚖️ Vantage Juris": 
        render_vantage_juris()
    elif m == "🐷 Piggy AI": 
        render_piggy_ai()
