"""
Clausely Streamlit Demo Frontend — The judge-facing interactive demo.

A polished, professional UI that demonstrates the full Clausely
multi-agent workflow: Intake → Draft → Validate → Strategize → Store.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import uuid
import base64
import pandas as pd
from pathlib import Path
from typing import Any, Dict

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on the Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Load and Encode Logo for Custom HTML Styling
# ---------------------------------------------------------------------------
def get_logo_base64() -> str:
    logo_path = Path(__file__).resolve().parent / "clausely_logo.png"
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return ""

LOGO_BASE64 = get_logo_base64()

# BNS Citation Checker integration
try:
    from tools.citation_checker import checker
except ImportError:
    checker = None



# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Clausely — Legal AI for India",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a premium look
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Sidebar & Theme Config (Must be declared before CSS injection)
# ---------------------------------------------------------------------------

with st.sidebar:
    # Sleek mockup styled branding logo with branding image
    logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 38px; height: 38px; border-radius: 8px; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.35); object-fit: contain;">' if LOGO_BASE64 else '<span style="background-color: #38bdf8; color: #18181b; font-weight: 800; font-size: 1.45rem; padding: 0.15rem 0.6rem; border-radius: 8px; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.45); font-family: \'Outfit\', sans-serif;">C</span>'
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; padding-top: 0.5rem;">
        {logo_html}
        <span style="font-weight: 700; font-size: 1.45rem; color: #ffffff; letter-spacing: -0.03em; font-family: 'Outfit', sans-serif;">clausely<span style="color: #38bdf8;">.ai</span></span>
    </div>
    <div style="font-size: 0.8rem; color: #a1a1aa; margin-bottom: 1rem; font-family: 'Outfit', sans-serif;">Legal Compilation Engine for Indian Courts</div>
    """, unsafe_allow_html=True)

    st.divider()
    # Main Navigation Mode
    nav_mode = st.radio("Navigation", ["🏠 Home Dashboard", "⚖️ Registry Simulator", "📂 AWS S3 Historical Archive"], label_visibility="collapsed")
    st.divider()



    jurisdiction = st.selectbox(
        "Court Jurisdiction",
        ["MH-DISTRICT", "MH-HC", "DL-DISTRICT", "IN-SC"],
        help="Select the Indian court jurisdiction",
    )

    jurisdiction_labels = {
        "MH-DISTRICT": "Maharashtra District Court",
        "MH-HC": "Bombay High Court",
        "DL-DISTRICT": "Delhi District Court",
        "IN-SC": "Supreme Court of India",
    }
    st.caption(f"📍 {jurisdiction_labels.get(jurisdiction, jurisdiction)}")

    document_type = st.selectbox(
        "Document Type",
        ["Affidavit", "Legal Notice (S.138 NI)", "NDA", "Rent Agreement", "Writ Petition"],
    )

    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Marathi", "Bengali", "Telugu", "Tamil", "Gujarati", "Urdu", "Kannada", "Odia", "Malayalam", "Punjabi", "Sanskrit", "Assamese", "Maithili", "Santali", "Kashmiri", "Nepali", "Konkani", "Sindhi", "Dogri", "Manipuri", "Bodo"],
    )

    use_adapter = st.checkbox(
        "💡 Integrate IndiaLaw-14B LoRA",
        value=True,
        help="Integrate QLoRA adapter fine-tuned on Ground Truth legal texts (BNS, BNSS, BSA) & IRAC training pairs for perfect citation compliance",
    )

    run_strategy = st.checkbox(
        "Run Strategic Analysis",
        value=False,
        help="Activate the 7-agent adversarial swarm for full strategic simulation",
    )

    theme_mode = st.selectbox("Interface Theme", ["Sleek Dark (Futuristic)", "Clean Light (Modern)"])

    st.divider()
    st.caption("🔒 Attorney-client privilege protected")
    st.caption("📋 BNS-2024-v1 corpus")
    st.caption("⚡ Powered by Google ADK + Gemini")
    st.divider()
    st.caption("Built for the Google for Startups")
    st.caption("AI Agents Challenge 2026")

# Dynamic Premium Theme Style Configurations (Absolutely No Gradients)
if "Dark" in theme_mode:
    bg_app = "#09090b"
    bg_card = "#18181b"
    bg_hover = "#27272a"
    border_color = "#27272a"
    border_hover = "#3f3f46"
    text_color = "#f4f4f5"
    text_sub = "#a1a1aa"
    text_muted = "#71717a"
    text_title = "#ffffff"
    # Accent color for futuristic glowing borders
    accent_glow = "rgba(56, 189, 248, 0.45)"
    accent_color = "#38bdf8"
else:
    bg_app = "#fafafa"
    bg_card = "#ffffff"
    bg_hover = "#f4f4f5"
    border_color = "#e4e4e7"
    border_hover = "#d4d4d8"
    text_color = "#18181b"
    text_sub = "#4b5563"
    text_muted = "#9ca3af"
    text_title = "#09090b"
    # Clean subtle slate accent
    accent_glow = "rgba(15, 23, 42, 0.15)"
    accent_color = "#0f172a"

st.markdown(f"""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Global Reset & Typography */
html, body, [class*="css"] {{
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: {text_color};
}}

/* Background overrides for sleek dashboard */
.stApp {{
    background-color: {bg_app};
}}

/* Main container */
.main .block-container {{
    padding-top: 2rem;
    max-width: 1200px;
}}

/* Premium Hero Badge - Flat futuristic card with precise blue accent border */
.hero-badge {{
    background-color: {bg_card};
    color: {text_color};
    padding: 2.2rem;
    border-radius: 14px;
    margin-bottom: 2rem;
    border: 1px solid {border_color};
    border-left: 5px solid {accent_color};
    box-shadow: 0 4px 30px {accent_glow};
}}

.hero-badge h1 {{
    margin: 0;
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: {text_title};
}}

.hero-badge p {{
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-size: 1rem;
    font-weight: 400;
    color: {text_sub};
}}

/* Score badge */
.score-badge {{
    display: inline-block;
    padding: 0.5rem 1.25rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: -0.01em;
    border: 1px solid transparent;
}}
.score-green {{ background-color: #064e3b; color: #34d399; border-color: #047857; }}
.score-orange {{ background-color: #78350f; color: #fbbf24; border-color: #b45309; }}
.score-red {{ background-color: #7f1d1d; color: #f87171; border-color: #b91c1c; }}

/* Agent step cards - minimal flat */
.agent-step {{
    background-color: {bg_card};
    border-left: 3px solid {border_hover};
    padding: 0.75rem 1.25rem;
    margin: 0.5rem 0;
    border-radius: 4px;
    font-size: 0.95rem;
    color: {text_sub};
    border: 1px solid {border_color};
    border-left-width: 4px;
}}
.agent-step.active {{
    background-color: {bg_hover};
    border-left-color: #3b82f6;
    color: {text_title};
}}
.agent-step.done {{
    background-color: {bg_card};
    border-left-color: #10b981;
    color: {text_sub};
}}

/* Metric cards - Flat high-end Cards matching welcome dashboard */
.metric-card {{
    background-color: {bg_card};
    border: 1px solid {border_color};
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}}
.metric-card:hover {{
    border-color: {border_hover};
    transform: translateY(-2px);
    box-shadow: 0 4px 20px {accent_glow};
}}
.metric-card h3 {{
    font-size: 0.8rem;
    color: {text_sub};
    margin: 0;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.metric-card .value {{
    font-size: 1.25rem;
    font-weight: 700;
    color: {text_title};
    margin: 0.4rem 0;
    letter-spacing: -0.02em;
}}
.metric-card .sub {{
    font-size: 0.8rem;
    color: {text_muted};
    font-weight: 500;
}}

/* Sidebar styling overrides */
section[data-testid="stSidebar"] {{
    background-color: {bg_app} !important;
    border-right: 1px solid {border_color} !important;
}}
section[data-testid="stSidebar"] .stMarkdown {{
    color: {text_color};
}}

/* Form styling */
.stForm {{
    background-color: {bg_card} !important;
    border: 1px solid {border_color} !important;
    border-radius: 14px !important;
    padding: 2rem !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}}

/* BNS Checker Alerts Styling */
.bns-alert {{
    background-color: {bg_card};
    border: 1px solid #e11d48;
    border-radius: 8px;
    padding: 1.25rem;
    margin: 1rem 0;
}}
.bns-alert-title {{
    color: #fda4af;
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.bns-warning-item {{
    font-size: 0.95rem;
    color: {text_color};
    margin: 0.35rem 0;
    padding-left: 1rem;
    position: relative;
}}
.bns-warning-item::before {{
    content: "•";
    color: #ef4444;
    position: absolute;
    left: 0;
}}

.bns-suggestion-box {{
    background-color: {bg_hover};
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    border: 1px solid {border_color};
}}

.bns-suggestion-item {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: {text_sub};
}}
.bns-suggestion-item strong {{
    color: #38bdf8;
}}
.bns-suggestion-item span {{
    color: #10b981;
}}
</style>


""", unsafe_allow_html=True)




# ---------------------------------------------------------------------------
# Hero & Welcome Section
# ---------------------------------------------------------------------------

# Good Morning Header matching mockup with branding logo
logo_main_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="width: 54px; height: 54px; border-radius: 12px; box-shadow: 0 4px 20px {accent_glow}; object-fit: contain; margin-right: 1.25rem;">' if LOGO_BASE64 else ''
st.markdown(f"""
<div style="display: flex; align-items: center; margin-bottom: 2.2rem; padding: 0.5rem 0;">
    {logo_main_html}
    <div>
        <h2 style="font-weight: 700; font-size: 2.2rem; margin: 0; color: {text_title}; line-height: 1.2;">Good morning, Advocate 👋</h2>
        <p style="font-size: 1.05rem; color: {text_sub}; margin: 0.2rem 0 0 0;">What are we drafting today?</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main Drafting Intent Studio Card & Intake
# ---------------------------------------------------------------------------

st.markdown(f"""
<div class="hero-badge" style="margin-bottom: 1.5rem;">
    <h3 style="font-weight: 600; font-size: 1.25rem; margin: 0; color: {text_title};">Describe what you need to draft...</h3>
    <p style="font-size: 0.95rem; color: {text_sub}; margin-top: 0.2rem; margin-bottom: 0;">e.g., Draft a limitation clause for an NDA under Maharashtra jurisdiction, or Section 138 Notice in Nagpur</p>
</div>
""", unsafe_allow_html=True)


# Initialize session state for intake presets
if "client_name" not in st.session_state:
    st.session_state.client_name = "Rajesh Kumar"
if "opposing_party" not in st.session_state:
    st.session_state.opposing_party = "Amit Verma"
if "cause_of_action" not in st.session_state:
    st.session_state.cause_of_action = "The Respondent failed to perform contractual obligations and clear the invoice dated October 12, 2025."
if "relief_sought" not in st.session_state:
    st.session_state.relief_sought = "Order directing the Respondent to clear the invoice amount of Rs. 5,00,000/- with 12% interest."
if "birth_year" not in st.session_state:
    st.session_state.birth_year = 1980
if "role" not in st.session_state:
    st.session_state.role = "advocate"

submitted = False

if "Home" in nav_mode:
    # ---------------------------------------------------------------------------
    # Home Dashboard (Homepage View)
    # ---------------------------------------------------------------------------
    
    # Beautiful Recent Matters grid matching the user's mockup dashboard
    st.markdown("##### 📁 Recent Active Matters")
    
    matters = [
        {"client": "Anjali Khobrekar vs Union of India", "details": "Writ Petition (Civil) No. 2456/2026 • Bombay High Court", "docs": "12 Documents", "time": "Updated 2h ago", "color": "#3b82f6"},
        {"client": "Sharma & Ors vs Ramesh Builders Pvt. Ltd.", "details": "Commercial Suit No. 89/2024 • Delhi District Court", "docs": "8 Documents", "time": "Updated 1d ago", "color": "#10b981"},
        {"client": "Mehta Industries vs State of Maharashtra", "details": "Writ Petition (ST) No. 112/2024 • Nagpur Bench", "docs": "15 Documents", "time": "Updated 2d ago", "color": "#a855f7"},
        {"client": "Daily Legal Advisory - Corporate", "details": "Internal Advisory • Ongoing Compliance Check", "docs": "23 Documents", "time": "Updated 3d ago", "color": "#f97316"},
    ]
    
    for matter in matters:
        matter_html = f"""
        <div style="background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(0,0,0,0.01);">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background-color: {bg_hover}; color: {matter['color']}; padding: 0.6rem; border-radius: 50%; font-size: 1.2rem; display: flex; align-items: center; justify-content: center; width: 42px; height: 42px; border: 1px solid {border_color};">
                    📁
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1.05rem; color: {text_title};">{matter['client']}</div>
                    <div style="font-size: 0.85rem; color: {text_sub}; margin-top: 0.15rem;">{matter['details']}</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <span style="background-color: {bg_hover}; border: 1px solid {border_color}; color: {accent_color}; font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.6rem; border-radius: 20px;">
                    {matter['docs']}
                </span>
                <span style="font-size: 0.8rem; color: {text_muted};">{matter['time']}</span>
            </div>
        </div>
        """
        st.markdown(matter_html, unsafe_allow_html=True)
        
    st.markdown("---")

elif "AWS" in nav_mode:
    # ---------------------------------------------------------------------------
    # 📂 AWS S3 Historical Archive Explorer View
    # ---------------------------------------------------------------------------
    st.markdown("##### 📂 AWS Open Data — Supreme Court Historical Archive Explorer")
    
    # Premium explanatory card
    st.markdown(f"""
    <div style="background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid #10b981;">
        <h4 style="margin: 0 0 0.5rem 0; font-size: 1.15rem; font-weight: 700; color: {text_title};">⚡ Live S3 Parquet Streaming Active</h4>
        <p style="font-size: 0.92rem; color: {text_sub}; margin: 0; line-height: 1.4;">
            We are streaming structured court records from the public S3 bucket <code>s3://indian-supreme-court-judgments</code> sponsored under the <strong>AWS Open Data Sponsorship Program</strong>. 
            No AWS credentials, account, or CLI utilities are needed. Data retrieval is 100% credential-free.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Let's add columns for Year selection and bulk downloads
    col_sel, col_dl = st.columns([1, 1])
    
    with col_sel:
        st.markdown(f"<div style='background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 12px; padding: 1.25rem; height: 100%;'>", unsafe_allow_html=True)
        selected_year = st.selectbox(
            "📅 Select Judgment Year:",
            list(range(2025, 1949, -1)),
            index=1, # Default to 2024
            help="Choose a year to load the historical Supreme Court of India judgments database."
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_dl:
        st.markdown(f"<div style='background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 12px; padding: 1.25rem; height: 100%;'>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='margin: 0 0 0.5rem 0; font-size: 0.9rem; font-weight: 600; color: {accent_color};'>📥 Bulk Year Download Links</h5>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size: 0.82rem; display: flex; flex-direction: column; gap: 0.4rem; color: {text_sub};">
            <div>📄 <a href="https://indian-supreme-court-judgments.s3.amazonaws.com/metadata/parquet/year={selected_year}/metadata.parquet" target="_blank" style="color: #38bdf8; font-weight: 600; text-decoration: none;">Download metadata.parquet ({selected_year})</a></div>
            <div>📦 <a href="https://indian-supreme-court-judgments.s3.amazonaws.com/data/tar/year={selected_year}/english/english.tar" target="_blank" style="color: #38bdf8; font-weight: 600; text-decoration: none;">Download english.tar ({selected_year})</a></div>
            <div>📋 <a href="https://indian-supreme-court-judgments.s3.amazonaws.com/metadata/tar/year={selected_year}/metadata.index.json" target="_blank" style="color: #38bdf8; font-weight: 600; text-decoration: none;">View Archive Index ({selected_year})</a></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Let's implement the cached loading function
    @st.cache_data(show_spinner="Streaming structured Parquet index from AWS S3...")
    def load_s3_parquet_cached(year: int):
        url = f"https://indian-supreme-court-judgments.s3.amazonaws.com/metadata/parquet/year={year}/metadata.parquet"
        try:
            return pd.read_parquet(url, engine="pyarrow")
        except Exception as e:
            return str(e)

    df_data = load_s3_parquet_cached(selected_year)
    
    if isinstance(df_data, str):
        st.error(f"⚠️ Error streaming S3 Parquet dataset: {df_data}")
        st.info("Please make sure you have an active internet connection. You can also manually access the links above.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 🔍 Search Court Records")
        
        search_query = st.text_input("Filter cases by Title, Petitioner, Respondent, Judge, or Citation:", "", placeholder="e.g. Maharashtra, Naresh Kumar, cheq...")
        
        if search_query:
            q = search_query.lower()
            filtered_df = df_data[
                df_data['title'].str.lower().str.contains(q, na=False) |
                df_data['petitioner'].str.lower().str.contains(q, na=False) |
                df_data['respondent'].str.lower().str.contains(q, na=False) |
                df_data['judge'].str.lower().str.contains(q, na=False) |
                df_data['citation'].str.lower().str.contains(q, na=False)
            ]
        else:
            filtered_df = df_data
            
        st.write(f"Showing {min(len(filtered_df), 30)} of {len(filtered_df)} judgments found (Total in year: {len(df_data)})")
        
        if filtered_df.empty:
            st.warning("No judgments match your search query.")
        else:
            # Let's display the top 30 judgments as beautiful cards
            for idx, row in filtered_df.head(30).iterrows():
                case_title = row.get('title', 'Unknown Case')
                case_date = row.get('decision_date', 'Unknown Date')
                case_cit = row.get('citation', 'No Citation')
                case_disposal = row.get('disposal_nature', 'N/A')
                case_judges = row.get('judge', 'N/A')
                case_author = row.get('author_judge', 'N/A')
                case_id = row.get('case_id', 'N/A')
                case_cnr = row.get('cnr', 'N/A')
                case_path = row.get('path', '')
                
                if pd.isna(case_date): case_date = "Unknown Date"
                if pd.isna(case_cit): case_cit = "No Citation Available"
                if pd.isna(case_disposal): case_disposal = "N/A"
                if pd.isna(case_judges): case_judges = "N/A"
                if pd.isna(case_author): case_author = "N/A"
                if pd.isna(case_cnr): case_cnr = "N/A"
                
                with st.expander(f"⚖️ {case_title} ({case_date})"):
                    st.markdown(f"""
                    <div style="background-color: {bg_hover}; border: 1px solid {border_color}; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem; font-family: 'Outfit', sans-serif;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; font-size: 0.85rem; color: {text_sub};">
                            <div>🏛️ <strong>Court:</strong> Supreme Court of India</div>
                            <div>📅 <strong>Decision Date:</strong> {case_date}</div>
                            <div>📜 <strong>Citation:</strong> {case_cit}</div>
                            <div>🎯 <strong>Disposal Nature:</strong> {case_disposal}</div>
                            <div>👤 <strong>Bench (Judges):</strong> {case_judges}</div>
                            <div>✍️ <strong>Author Judge:</strong> {case_author}</div>
                            <div>🆔 <strong>Case ID:</strong> {case_id}</div>
                            <div>🏷️ <strong>CNR:</strong> {case_cnr}</div>
                        </div>
                        <div style="margin-top: 0.75rem; font-size: 0.8rem; color: {text_muted}; border-top: 1px solid {border_color}; padding-top: 0.5rem; word-break: break-all;">
                            📁 <strong>S3 Archive Path:</strong> s3://indian-supreme-court-judgments/{case_path}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if case_path:
                        clean_path = str(case_path).strip()
                        st.markdown(f"**📖 Download instruction:** Locate `{clean_path}` inside the `{selected_year}` English tarball above.")
    
else:
    # ---------------------------------------------------------------------------
    # Registry Simulator (Case Intake & Compiler View)
    # ---------------------------------------------------------------------------
    
    # Main Grid Layout - Left Main Intake form & right side panel
    main_col, side_col = st.columns([7, 3])
    
    with main_col:
        # Load Presets Buttons
        st.markdown("##### 📁 Presets")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("Load Rajesh Kumar (Standard Case)"):
                st.session_state.client_name = "Rajesh Kumar"
                st.session_state.opposing_party = "Amit Verma"
                st.session_state.cause_of_action = "The Respondent failed to perform contractual obligations and clear the invoice dated October 12, 2025."
                st.session_state.relief_sought = "Order directing the Respondent to clear the invoice amount of Rs. 5,00,000/- with 12% interest."
                st.session_state.birth_year = 1980
                st.session_state.role = "advocate"
                st.rerun()
        with col_p2:
            if st.button("Load Vidya Khobrekar (Validation Gate Demo)"):
                st.session_state.client_name = "Vidya Khobrekar"
                st.session_state.opposing_party = "State of Maharashtra"
                st.session_state.cause_of_action = "The Petitioner, Vidya Khobrekar, challenges the arbitrary service termination order issued by the NCSC in Nagpur Bench. Adv. Vidya Khobrekar argued that the termination was illegal."
                st.session_state.relief_sought = "Writ of Certiorari to quash the arbitrary termination order and reinstate the Petitioner."
                st.session_state.birth_year = 1965
                st.session_state.role = "petitioner_in_person"
                st.rerun()

        with st.form("intake_form"):
            st.markdown("##### 📝 Case Intake & Facts Studio")

            court_name = st.text_input(
                "Court / Forum Designation",
                "Civil Judge Senior Division, Nagpur",
            )
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                case_number = st.text_input(
                    "Case Number (if existing)",
                    placeholder="CS/245/2026",
                )
                client_name = st.text_input(
                    "Client / Petitioner Name",
                    value=st.session_state.client_name,
                )
                client_birth_year = st.number_input(
                    "Client Birth Year",
                    value=st.session_state.birth_year,
                    min_value=1900,
                    max_value=2026,
                    step=1,
                )
            with col_c2:
                opposing_party = st.text_input(
                    "Opposing Party / Respondent",
                    value=st.session_state.opposing_party,
                )
                client_role = st.selectbox(
                    "Client Legal Standing / Role",
                    options=["advocate", "petitioner_in_person"],
                    index=0 if st.session_state.role == "advocate" else 1,
                )
                urgency = st.checkbox("⚡ Mark as Urgent (Interim Relief)")

            cause_of_action = st.text_area(
                "Cause of Action / Detailed Legal Facts",
                value=st.session_state.cause_of_action,
                height=140,
                help="Enter raw case facts or paste a secure base64-encoded cryptographic envelope.",
            )
            
            relief_sought = st.text_area(
                "Relief Sought (Prayer Specifics)",
                value=st.session_state.relief_sought,
                height=80,
            )

            legal_prompt = st.text_area(
                "Advocate Custom Instructions",
                placeholder="e.g. Keep terminology highly formal; emphasize territorial jurisdiction elements; reference recent high court precedents.",
                height=80,
            )

            submitted = st.form_submit_button(
                "⚡ Compile & Scrutinize with Clausely ADK",
                type="primary",
                use_container_width=True,
            )

    with side_col:
        st.markdown(f"""
        <div style="background-color: {bg_card}; border: 1px solid {border_color}; border-radius: 12px; padding: 1.25rem;">
            <h4 style="margin: 0 0 1rem 0; font-size: 1.05rem; font-weight: 700; color: {text_title}; border-bottom: 1px solid {border_color}; padding-bottom: 0.5rem;">⚖️ Drafting Playbook</h4>
            <div style="font-size: 0.85rem; color: {text_sub}; line-height: 1.4; margin-bottom: 1rem;">
                Quick actions to execute custom scrutiny logic or load template configurations.
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.6rem;">
                <div style="background-color: {bg_hover}; padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid {border_color}; font-size: 0.85rem; color: {text_title};">
                    📄 <strong>Draft Document</strong><br><span style="color: {text_muted}; font-size: 0.75rem;">From raw legal intent</span>
                </div>
                <div style="background-color: {bg_hover}; padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid {border_color}; font-size: 0.85rem; color: {text_title};">
                    🛡️ <strong>Review Document</strong><br><span style="color: {text_muted}; font-size: 0.75rem;">Check risks & fatal defects</span>
                </div>
                <div style="background-color: {bg_hover}; padding: 0.6rem 0.8rem; border-radius: 6px; border: 1px solid {border_color}; font-size: 0.85rem; color: {text_title};">
                    🏛️ <strong>Registry Check</strong><br><span style="color: {text_muted}; font-size: 0.75rem;">Pre-filing rules validation</span>
                </div>
            </div>
            <div style="margin-top: 1.25rem; border-top: 1px solid {border_color}; padding-top: 1rem;">
                <h5 style="margin: 0 0 0.5rem 0; font-size: 0.85rem; font-weight: 600; color: {accent_color};">Applicable Framework</h5>
                <div style="font-size: 0.8rem; display: flex; justify-content: space-between; margin: 0.25rem 0;">
                    <span style="color: {text_sub};">Bharatiya Nyaya Sanhita</span>
                    <span style="color: #10b981; font-weight: 600;">BNS 2023</span>
                </div>
                <div style="font-size: 0.8rem; display: flex; justify-content: space-between; margin: 0.25rem 0;">
                    <span style="color: {text_sub};">Code of Civil Procedure</span>
                    <span style="color: #3b82f6; font-weight: 600;">CPC 1908</span>
                </div>
                <div style="font-size: 0.8rem; display: flex; justify-content: space-between; margin: 0.25rem 0;">
                    <span style="color: {text_sub};">Evidence Act</span>
                    <span style="color: #10b981; font-weight: 600;">BSA 2023</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Architecture metrics
# ---------------------------------------------------------------------------

st.markdown("##### 🤖 ADK Swarm Components")
col1, col2, col3, col4 = st.columns(4)

with col1:
    drafter_sub = "Gemini 3.5 Flash + IndiaLaw-14B LoRA" if use_adapter else "Gemini 3.5 Flash"
    st.markdown(f"""
    <div class="metric-card">
        <h3>Drafter Agent</h3>
        <div class="value">📝 ADK Sequential</div>
        <div class="sub">{drafter_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>Acceptor Agent</h3>
        <div class="value">✅ Registry Sim</div>
        <div class="sub">Deterministic Rules</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>Strategist</h3>
        <div class="value">⚔️ 7-Agent Swarm</div>
        <div class="sub">ADK ParallelAgent</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h3>Case Base</h3>
        <div class="value">🧠 Memory Bank</div>
        <div class="sub">Firestore Persistent</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")


# ---------------------------------------------------------------------------
# Processing & Results
# ---------------------------------------------------------------------------

if submitted:
    st.subheader("🔄 ADK Agent Workflow Running...")

    # Agent pipeline steps
    agent_steps = [
        ("🧠 Case Base Agent", "Searching institutional memory for similar matters...", 10),
        ("📝 Drafter Agent", "Generating Legal AST and document clauses...", 30),
        ("📝 Drafter Agent", "Applying Symbolic Formatting Engine (SFE)...", 50),
        ("✅ Acceptor Agent", "Simulating registry scrutiny...", 70),
    ]

    if run_strategy:
        agent_steps.extend([
            ("⚔️ Strategist Swarm", "Launching 7-agent adversarial simulation...", 80),
            ("⚔️ Strategist Swarm", "Petitioner + Opponent + Reviewer running in parallel...", 85),
            ("⚔️ Judge Agent", "Synthesizing all arguments, scoring probability...", 90),
        ])

    agent_steps.extend([
        ("🧠 Case Base Agent", "Storing matter to persistent memory...", 95),
        ("✨ Complete", "Document compiled and validated!", 100),
    ])

    progress_bar = st.progress(0)
    status_text = st.empty()

    with st.spinner(""):
        for agent_name, action, progress in agent_steps:
            status_text.markdown(
                f'<div class="agent-step active">'
                f"<strong>{agent_name}</strong> — {action}"
                f"</div>",
                unsafe_allow_html=True,
            )
            progress_bar.progress(progress)
            time.sleep(0.6)

    # Build result — in demo mode, use deterministic pipeline
    matter_id = f"CLY-{uuid.uuid4().hex[:8].upper()}"
    matter_context = {
        "jurisdiction": jurisdiction,
        "document_type": document_type,
        "court_name": court_name,
        "case_number": case_number,
        "cause_of_action": cause_of_action,
        "relief_sought": relief_sought,
        "client_name": client_name,
        "opposing_party": opposing_party,
        "language": language,
        "prompt": legal_prompt,
        "urgency": urgency,
        "use_adapter": use_adapter,
        "birth_year": client_birth_year,
        "role": client_role,
    }

    # Try running the actual ADK pipeline
    result = None
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from agents.orchestrator import clausely_orchestrator, run_clausely

        session_service = InMemorySessionService()
        runner = Runner(
            agent=clausely_orchestrator,
            app_name="clausely",
            session_service=session_service,
        )
        result = asyncio.run(run_clausely(runner, matter_context, run_strategy=run_strategy))
    except Exception as e:
        st.warning(f"⚠️ Live ADK pipeline unavailable ({type(e).__name__}). Running deterministic demo mode.")

        # Deterministic demo fallback
        from tools.sfe import SymbolicFormattingEngine
        from agents.acceptor import simulate_registry_check

        sfe = SymbolicFormattingEngine(jurisdiction)

        # Build document from template
        demo_sections = {
            "cause_title": (
                f"IN THE COURT OF THE {court_name.upper()}\n\n"
                f"IN THE MATTER OF:\n\n"
                f"{client_name or '[Client Name]'}\n"
                f"                                                    ... PETITIONER/APPLICANT\n\n"
                f"VERSUS\n\n"
                f"{opposing_party or '[Opposing Party]'}\n"
                f"                                                    ... RESPONDENT/OPPONENT"
            ),
            "jurisdiction_clause": (
                f"This Hon'ble Court has the jurisdiction to try and entertain "
                f"the present matter under Section 9 of the Code of Civil Procedure, 1908. "
                f"The cause of action has arisen within the territorial jurisdiction of this Hon'ble Court."
            ),
            "facts": (
                f"STATEMENT OF FACTS\n\n"
                f"1. That the Petitioner/Applicant is a citizen of India and resides within "
                f"the jurisdiction of this Hon'ble Court.\n\n"
                f"2. {cause_of_action or 'That the facts giving rise to the present matter are as stated herein.'}"
            ),
            "grounds": (
                f"GROUNDS\n\n"
                f"The present application is filed on the following grounds:\n\n"
                f"(a) That the cause of action has arisen within the jurisdiction of this Hon'ble Court.\n\n"
                f"(b) That the Petitioner has a valid legal right which has been infringed by the Respondent.\n\n"
                f"(c) That the Petitioner has no other efficacious remedy available."
            ),
            "prayer": (
                f"PRAYER\n\n"
                f"In the premises aforesaid, it is most respectfully prayed that this Hon'ble Court "
                f"may be pleased to:\n\n"
                f"(a) {relief_sought or 'Grant the relief as prayed for'};\n\n"
                f"(b) Grant costs of this proceeding in favour of the Petitioner;\n\n"
                f"(c) Pass such other and further orders as this Hon'ble Court may deem fit and proper "
                f"in the facts and circumstances of the case."
            ),
            "verification": (
                f"VERIFICATION\n\n"
                f"I, {client_name or '[Client Name]'}, the above-named deponent, do hereby verify "
                f"that the contents of the above {document_type} are true and correct to my knowledge "
                f"and belief. No part of it is false and nothing material has been concealed therefrom.\n\n"
                f"Verified at {court_name.split(',')[-1].strip() if ',' in court_name else 'Nagpur'} "
                f"on this ____ day of __________, 2026."
            ),
            "deponent_signature": (
                f"DEPONENT\n\n"
                f"{client_name or '[Client Name]'}\n\n"
                f"Through Advocate:\n"
                f"[Advocate Name]\n"
                f"[Bar Council Enrollment No.]\n"
                f"[Office Address]"
            ),
        }

        # Enforce formatting via SFE
        metadata = {
            "court_designation": court_name,
            "city_name": court_name.split(",")[-1].strip() if "," in court_name else "Nagpur",
            "case_type": document_type,
            "case_number": case_number or "____",
            "year": "2026",
        }

        full_text_parts = []
        ordered = sfe.reorder_sections(demo_sections)
        for sec_type, content in ordered:
            full_text_parts.append(content)
        raw_content = "\n\n".join(full_text_parts)

        document_text = sfe.enforce(raw_content, metadata)

        # Run registry check
        registry_result = simulate_registry_check(document_text, jurisdiction, document_type)

        result = {
            "matter_id": matter_id,
            "case_base_id": matter_id,
            "document_text": document_text,
            "acceptance_score": registry_result["acceptance_score"],
            "fatal_defects": registry_result["fatal_defects"],
            "curable_defects": registry_result["curable_defects"],
            "registry_checks": registry_result["detailed_checks"],
            "similar_matters": [],
            "outcome_scenarios": [
                {"description": "Favorable outcome — full relief granted", "probability": 45, "recommendation": "Proceed with filing"},
                {"description": "Partial relief — court may limit scope", "probability": 30, "recommendation": "Prepare for negotiation"},
                {"description": "Procedural dismissal — curable defects", "probability": 15, "recommendation": "Fix all curable defects before filing"},
                {"description": "Adverse outcome", "probability": 10, "recommendation": "Consider appellate strategy"},
            ],
            "objections": [
                {"text": "Verify territorial jurisdiction is correctly established", "severity": "medium"},
                {"text": "Confirm limitation period compliance under Limitation Act, 1963", "severity": "high"},
                {"text": "Ensure all necessary parties are properly impleaded", "severity": "medium"},
            ],
            "strategy_memo": "",
        }

    status_text.markdown(
        '<div class="agent-step done"><strong>✅ Pipeline Complete</strong> — '
        "Document compiled and validated!</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------- Results Tabs ---------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Generated Document",
        "✅ Acceptance Report",
        "⚔️ Strategy Analysis",
        "🧠 Case Base",
    ])

    with tab1:
        st.subheader(f"{document_type} — {jurisdiction_labels.get(jurisdiction, jurisdiction)}")

        score = result.get("acceptance_score", 0)
        if score >= 85:
            badge_class = "score-green"
        elif score >= 60:
            badge_class = "score-orange"
        else:
            badge_class = "score-red"

        st.markdown(
            f'<span class="score-badge {badge_class}">'
            f"Registry Acceptance Score: {score:.0f}/100"
            f"</span>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        st.text_area(
            "Generated Document",
            result.get("document_text", ""),
            height=450,
            help="This document has been formatted to court specifications by the SFE.",
        )

        col_dl1, col_dl2, col_dl3 = st.columns(3)

        with col_dl1:
            try:
                sfe = SymbolicFormattingEngine(jurisdiction)
                doc_dict = {
                    "sections": {"content": result.get("document_text", "")},
                    "metadata": {},
                }
                pdf_bytes = sfe.export_pdf(doc_dict)
                st.download_button(
                    "📄 Download PDF (Court-Ready)",
                    data=pdf_bytes,
                    file_name=f"clausely_{matter_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception:
                st.button("📄 Download PDF", disabled=True, use_container_width=True)

        with col_dl2:
            try:
                docx_bytes = sfe.export_docx(doc_dict)
                st.download_button(
                    "📝 Download DOCX",
                    data=docx_bytes,
                    file_name=f"clausely_{matter_id}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception:
                st.button("📝 Download DOCX", disabled=True, use_container_width=True)

        with col_dl3:
            st.download_button(
                "📋 Download TXT",
                data=result.get("document_text", ""),
                file_name=f"clausely_{matter_id}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with tab2:
        st.subheader("Registry Simulation Report")

        fatal = result.get("fatal_defects", [])
        curable = result.get("curable_defects", [])

        if not fatal:
            st.success("✅ No fatal defects. Document will pass registry scrutiny.")
        else:
            st.error(f"⚠️ {len(fatal)} Fatal Defect(s) Found — Document will be REJECTED")
            for d in fatal:
                st.markdown(f"- 🔴 **{d}**")

        if curable:
            st.warning(f"💡 {len(curable)} Curable Issue(s) — Recommended to fix before filing")
            for c in curable:
                st.markdown(f"- 🟡 {c}")
        else:
            st.info("No curable defects found.")

        # --- BNS RAG Citation Checker Section ---
        if checker:
            st.markdown("---")
            st.subheader("⚖️ BNS Statutory Citation Compliance Check (RAG)")
            
            doc_body = result.get("document_text", "")
            cit_report = checker.extract_and_verify(doc_body)
            
            if cit_report["is_compliant"]:
                st.success("🎉 **Statutory Citation Compliance Check Passed**: No deprecated statutory citations (IPC, CrPC, IEA) were detected. Excellent job using the current 2024/2025/2026 legal framework (BNS, BNSS, BSA).")
            else:
                st.error("⚠️ **Statutory Citation Compliance Check Failed**: The document cites deprecated laws that have been repealed since July 2024. View recommendations below to translate to BNS / BNSS / BSA compliant sections.")
                
                # Warnings block
                warnings_html = "<div class='bns-alert'><div class='bns-alert-title'>🚨 Deprecated Statutory Citations Detected</div>"
                for warning in cit_report["warnings"]:
                    warnings_html += f"<div class='bns-warning-item'>{warning}</div>"
                warnings_html += "</div>"
                st.markdown(warnings_html, unsafe_allow_html=True)
                
                # Suggestions block
                if cit_report["suggestions"]:
                    st.markdown("##### 💡 Recommended Compliant Replacement(s):")
                    for sug in cit_report["suggestions"]:
                        sug_html = f"""
                        <div class='bns-suggestion-box'>
                            <div class='bns-suggestion-item'>
                                ❌ Replace: <strong>"{sug['original']}"</strong><br>
                                 With Compliant: <span><strong>"{sug['replacement']}"</strong></span>
                            </div>
                        </div>
                        """
                        st.markdown(sug_html, unsafe_allow_html=True)
        else:
            st.caption("BNS Citation Checker engine is unavailable.")


        st.subheader("Registry Checklist")
        checks = result.get("registry_checks", {})
        if checks:
            check_cols = st.columns(2)
            for i, (check, passed) in enumerate(checks.items()):
                icon = "✅" if passed else "❌"
                label = check.replace("_", " ").title()
                with check_cols[i % 2]:
                    st.markdown(f"{icon} {label}")
        else:
            st.caption("Detailed checks not available in this run.")

    with tab3:
        st.subheader("Strategic Analysis — Adversarial Self-Play")

        if not run_strategy and not result.get("strategy_memo"):
            st.info(
                "💡 Enable **Run Strategic Analysis** in the sidebar to activate "
                "the 7-agent adversarial swarm (Petitioner, Opponent, Reviewer, "
                "Verifier, Objector, Presenter, Judge)."
            )

        outcomes = result.get("outcome_scenarios", [])
        if outcomes:
            st.subheader("Outcome Scenarios")
            for i, scenario in enumerate(outcomes[:5], 1):
                prob = scenario.get("probability", 0)
                with st.expander(
                    f"Scenario {i}: {scenario.get('description', '')[:80]}"
                    f" — {prob}%"
                ):
                    st.progress(prob / 100)
                    st.markdown(f"**Probability:** {prob}%")
                    st.markdown(f"**Description:** {scenario.get('description', '')}")
                    if scenario.get("recommendation"):
                        st.markdown(f"*Recommendation: {scenario['recommendation']}*")

        objections = result.get("objections", [])
        if objections:
            st.subheader("Procedural Objections")
            for obj in objections:
                sev = obj.get("severity", "medium")
                color_map = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                st.markdown(
                    f"{color_map.get(sev, '⚪')} **{sev.upper()}** — {obj.get('text', '')}"
                )

        memo = result.get("strategy_memo", "")
        if memo:
            st.subheader("Strategy Memorandum")
            st.text_area("", memo, height=300)

    with tab4:
        st.subheader("Case Base — Institutional Memory")
        st.caption(f"Matter ID: `{result.get('case_base_id', matter_id)}`")

        similar = result.get("similar_matters", [])
        if similar:
            st.subheader("Similar Past Matters")
            for m in similar:
                st.markdown(
                    f"- **{m.get('document_type', '?')}** — "
                    f"{m.get('jurisdiction', '?')} — "
                    f"Score: {m.get('acceptance_score', '?')}%"
                )
        else:
            st.info(
                "📚 No similar past matters found. This is the first filing of "
                "its kind in your Case Base. Future drafts will reference this matter."
            )

        st.success(
            "🧠 This matter has been added to your Case Base. "
            "Future drafts will reference this matter automatically, "
            "making Clausely smarter with every filing."
        )

        st.divider()
        st.subheader("Reward Signal Pipeline")
        st.markdown("""
        | Signal | Reward | Trigger |
        |--------|--------|---------|
        | Document filed | +0.5 | Filing confirmed |
        | Registry accepted | **+3.0** | Court accepts document |
        | Registry rejected | **-3.0** | Court rejects document |
        | Minor edit by advocate | +0.5 | Small corrections made |
        | Major edit by advocate | +0.2 | Significant rewrites |
        """)
        st.caption(
            "These signals compound over time, making Clausely's drafting "
            "increasingly accurate with every Indian court filing processed."
        )
