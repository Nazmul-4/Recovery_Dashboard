import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
import os
import io
import glob
import re
import json
import base64
import html
import tempfile
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. Page Configuration & Global Styles
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="e-Rin Recovery Dashboard",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Brand Theme (e-Rin): orange-red / yellow gradient + phone-frame blue on deep navy
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3, h4, .kpi-value, .app-header-title, .sidebar-brand-text {
        font-family: 'Poppins', sans-serif;
    }

    /* Brand Navy Background with soft blue + orange glows */
    .stApp {
        background: #050A1C;
        background-image:
            radial-gradient(circle at 12% 18%, rgba(47,107,255,0.22) 0%, transparent 42%),
            radial-gradient(circle at 88% 12%, rgba(255,106,0,0.15) 0%, transparent 38%),
            radial-gradient(circle at 50% 95%, rgba(47,107,255,0.16) 0%, transparent 48%),
            linear-gradient(180deg, #050A1C 0%, #081233 100%);
        background-attachment: fixed;
        color: #F4F7FF;
    }

    hr { border-color: rgba(79,129,255,0.20) !important; }

    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #08112E; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #FF8A00, #2F6BFF);
        border-radius: 10px;
    }

    .gradient-text {
        background: linear-gradient(90deg, #FFC400 0%, #FF7A00 45%, #FF3D00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }

    /* Logo badge (white tile with brand gradient edge so the logo is always clearly visible) */
    .logo-tile {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        padding: 6px 9px;
        border-radius: 18px;
        border: 2px solid transparent;
        background:
            linear-gradient(145deg, #ffffff, #e9f0ff) padding-box,
            linear-gradient(135deg, #FF8A00, #2F6BFF) border-box;
        box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    }
    .logo-tile img { display: block; max-width: none; }

    /* Branded Header Banner (used on Dashboard / Editor / Agent Mgmt tabs) */
    .app-header-banner {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 18px 26px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(47,107,255,0.16), rgba(11,44,158,0.12) 50%, rgba(255,106,0,0.13));
        border: 1px solid rgba(79,129,255,0.32);
        border-left: 4px solid #FF6A00;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        margin-bottom: 18px;
        backdrop-filter: blur(14px);
    }
    /* Performance: the glow pulse animates only opacity of a pseudo-element (GPU friendly)
       instead of animating box-shadow (which forces a repaint every frame). */
    .app-header-logo {
        position: relative;
        width: 52px; height: 52px; border-radius: 16px; flex-shrink: 0;
        background: linear-gradient(135deg, #FFC400, #FF6A00 55%, #FF2D12);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.6rem;
        box-shadow: 0 0 22px rgba(255,106,0,0.5);
    }
    .app-header-logo::after {
        content: "";
        position: absolute; inset: 0;
        border-radius: 16px;
        box-shadow: 0 0 34px rgba(47,107,255,0.7);
        opacity: 0;
        pointer-events: none;
        animation: pulseGlow 3s ease-in-out infinite;
    }
    @keyframes pulseGlow {
        0%, 100% { opacity: 0; }
        50% { opacity: 1; }
    }
    @keyframes heroGlow {
        0%, 100% { opacity: .35; }
        50% { opacity: .9; }
    }
    .app-header-title { font-size: 1.55rem; font-weight: 800; letter-spacing: -0.01em; margin: 0; color: #F4F7FF; }
    .app-header-sub { font-size: 0.82rem; color: #A9B6D3; margin: 4px 0 0 0; letter-spacing: 0.03em; }

    /* Modern Glass KPI Cards */
    .kpi-card {
        position: relative;
        background: linear-gradient(145deg, rgba(14,25,60,0.90) 0%, rgba(7,13,34,0.94) 100%);
        border: 1px solid rgba(79,129,255,0.26);
        border-radius: 18px;
        padding: 20px 22px;
        overflow: hidden;
        box-shadow: inset 0 3px 0 rgba(255,106,0,0.9), 0 10px 28px rgba(0,0,0,0.4);
        backdrop-filter: blur(14px);
        transition: transform 0.3s cubic-bezier(.4,0,.2,1), box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card::before {
        content: "";
        position: absolute; inset: 0;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,0.07), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    .kpi-card:hover::before { transform: translateX(100%); }
    .kpi-card:hover {
        transform: translateY(-6px);
        box-shadow: inset 0 3px 0 rgba(255,138,0,1), 0 16px 36px rgba(255,106,0,0.25);
        border-color: rgba(255,138,0,0.55);
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9FB0D3;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #F4F7FF;
        margin: 0;
    }

    /* Slide-out Hover Drawer for EMI Breakdown */
    .drawer-wrapper {
        position: relative;
        margin: 16px 0 26px 0;
        display: inline-block;
        width: 100%;
    }
    .drawer-trigger {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #F26B0A, #E0340E);
        color: #ffffff;
        padding: 11px 20px;
        border-radius: 50px;
        font-size: 0.88rem;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 6px 20px rgba(255,106,0,0.4);
        transition: all 0.35s cubic-bezier(.4,0,.2,1);
        border: 1px solid rgba(255, 255, 255, 0.25);
        width: fit-content;
    }
    .drawer-trigger .circle-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: rgba(255, 255, 255, 0.22);
        border-radius: 50%;
        font-size: 1rem;
    }
    .drawer-wrapper:hover .drawer-trigger {
        background: linear-gradient(135deg, #2F6BFF, #0B2C9E);
        box-shadow: 0 10px 28px rgba(47, 107, 255, 0.55);
        transform: scale(1.02);
    }
    .drawer-content {
        max-height: 0px;
        opacity: 0;
        overflow: hidden;
        transform: scaleX(0.92) translateX(-20px);
        transform-origin: left center;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        margin-top: 12px;
        padding: 0 10px;
    }
    .drawer-wrapper:hover .drawer-content {
        max-height: 320px;
        opacity: 1;
        transform: scaleX(1) translateX(0px);
        padding: 14px 0;
    }

    .emi-card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
        gap: 14px;
    }
    .emi-card {
        background: rgba(11, 21, 52, 0.92);
        border-radius: 14px;
        padding: 14px 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }
    .emi-card:hover {
        transform: translateY(-4px) scale(1.03);
        border-color: rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.5);
    }
    .emi-tag {
        font-size: 0.78rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .emi-num {
        font-size: 1.55rem;
        font-weight: 800;
        margin-top: 5px;
        color: #F4F7FF;
    }

    /* Sidebar & Profile Card */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071030 0%, #040A1F 100%) !important;
        border-right: 1px solid rgba(79, 129, 255, 0.28) !important;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding: 4px 2px;
    }
    .sidebar-brand-icon {
        width: 40px; height: 40px; border-radius: 12px;
        background: linear-gradient(135deg, #FFC400, #FF6A00 55%, #FF2D12);
        display: flex; align-items: center; justify-content: center; font-size: 1.25rem;
        box-shadow: 0 0 16px rgba(255,106,0,0.5);
        flex-shrink: 0;
    }
    .sidebar-brand-text { font-weight: 800; font-size: 1.05rem; letter-spacing: -0.01em; color: #F4F7FF; }
    .sidebar-brand-sub { font-size: 0.66rem; color: #8896B8; letter-spacing: 0.1em; text-transform: uppercase; }

    .sidebar-user-card {
        background: linear-gradient(135deg, rgba(20, 36, 84, 0.75) 0%, rgba(8, 16, 44, 0.92) 100%);
        border: 1px solid rgba(79, 129, 255, 0.34);
        border-radius: 16px;
        padding: 15px 17px;
        display: flex;
        align-items: center;
        gap: 13px;
        margin-bottom: 14px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        transition: border-color 0.3s ease;
    }
    .sidebar-user-card:hover { border-color: rgba(255, 138, 0, 0.6); }
    .user-avatar-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF9A00, #FF2D12);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        color: #fff;
        font-size: 1.2rem;
        box-shadow: 0 0 14px rgba(255, 106, 0, 0.5);
        flex-shrink: 0;
    }
    .role-badge {
        display: inline-block;
        background: rgba(255, 106, 0, 0.16);
        color: #FFB36B;
        border: 1px solid rgba(255, 138, 0, 0.5);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-top: 4px;
    }

    .schedule-container-card {
        background: linear-gradient(135deg, rgba(14, 25, 60, 0.78) 0%, rgba(7, 13, 34, 0.88) 100%);
        border: 1px solid rgba(79, 129, 255, 0.28);
        border-left: 4px solid #FF6A00;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
        margin-top: 22px;
        margin-bottom: 14px;
    }
    .sort-toolbar-card {
        background: linear-gradient(135deg, rgba(14, 25, 60, 0.68) 0%, rgba(7, 13, 34, 0.78) 100%);
        border: 1px solid rgba(79, 129, 255, 0.26);
        border-radius: 14px;
        padding: 14px 20px;
        margin-bottom: 14px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: 1px solid rgba(79, 129, 255, 0.42) !important;
        background: linear-gradient(135deg, rgba(47, 107, 255, 0.18), rgba(11, 44, 158, 0.22)) !important;
        color: #EAF0FF !important;
        transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 138, 0, 0.8) !important;
        box-shadow: 0 8px 20px rgba(255, 106, 0, 0.28) !important;
        background: linear-gradient(135deg, rgba(255, 138, 0, 0.22), rgba(47, 107, 255, 0.24)) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #F26B0A 0%, #E0340E 100%) !important;
        border: none !important;
        color: #fff !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 6px 18px rgba(255, 106, 0, 0.32) !important;
    }
    .stButton > button[kind="primary"]:hover {
        filter: brightness(1.1);
        box-shadow: 0 10px 26px rgba(255, 106, 0, 0.5) !important;
    }

    /* Inputs */
    .stTextInput > div > div > input, .stTextArea textarea {
        background: rgba(8, 16, 44, 0.85) !important;
        border: 1px solid rgba(79, 129, 255, 0.32) !important;
        border-radius: 10px !important;
        color: #F4F7FF !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF8A00 !important;
        box-shadow: 0 0 0 2px rgba(255, 138, 0, 0.30) !important;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(8, 16, 44, 0.85) !important;
        border-color: rgba(79, 129, 255, 0.32) !important;
        border-radius: 10px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(8, 16, 44, 0.55);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(79, 129, 255, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        font-weight: 700 !important;
        color: #9FB0D3 !important;
        padding: 10px 18px !important;
        transition: all 0.25s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #F26B0A, #E0340E) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(255, 106, 0, 0.35);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(11, 21, 52, 0.75) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(79, 129, 255, 0.26) !important;
        font-weight: 700 !important;
    }
    [data-testid="stExpander"] {
        border: 1px solid rgba(79, 129, 255, 0.26) !important;
        border-radius: 12px !important;
    }

    /* Data Editor / DataFrame container */
    [data-testid="stDataEditor"], [data-testid="stDataFrame"] {
        border-radius: 14px !important;
        overflow: visible !important;
        border: 1px solid rgba(79, 129, 255, 0.28) !important;
    }

    /* Keep Streamlit's native element toolbar (view / download / search / fullscreen)
       visible and theme-matched instead of being clipped or invisible */
    [data-testid="stElementToolbar"] {
        background: rgba(8, 16, 44, 0.97) !important;
        border: 1px solid rgba(79, 129, 255, 0.4) !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.55) !important;
        opacity: 1 !important;
        visibility: visible !important;
        z-index: 999 !important;
        padding: 2px !important;
    }
    [data-testid="stElementToolbar"] button {
        color: #EAF0FF !important;
        background: transparent !important;
    }
    [data-testid="stElementToolbar"] button:hover {
        background: rgba(255, 138, 0, 0.28) !important;
        border-radius: 7px !important;
    }
    [data-testid="stElementToolbar"] svg {
        fill: #EAF0FF !important;
        color: #EAF0FF !important;
        opacity: 1 !important;
    }
    [data-testid="stElementToolbarButton"] {
        color: #EAF0FF !important;
    }
    [data-testid="stElementToolbarButton"]:hover {
        background: rgba(255, 138, 0, 0.28) !important;
        border-radius: 7px !important;
    }

    /* Solid Excel-Style Color-Blocked EMI Dropdown */
    div[data-testid="stDataEditor"] div[class*="overlay"],
    div[class*="gdg-style"],
    div[class*="gdg-dropdown"],
    div[class*="dvn-overlay"],
    div[class*="glide-data-grid"] div[class*="dropdown"],
    div[id*="portal"] > div,
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"],
    div[role="listbox"] {
        background-color: #0A1330 !important;
        background: #0A1330 !important;
        border: 1px solid #2A417F !important;
        border-radius: 10px !important;
        padding: 5px !important;
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.55) !important;
    }
    div[data-testid="stDataEditor"] div[class*="overlay"] div,
    div[class*="gdg-style"] div,
    div[role="listbox"] > *,
    ul[role="listbox"] li,
    div[data-baseweb="popover"] li {
        border-radius: 7px !important;
        margin: 3px 4px !important;
        padding: 10px 15px !important;
        font-weight: 800 !important;
        transition: transform 0.15s ease, filter 0.15s ease !important;
    }
    div[role="listbox"] > *:nth-child(1), ul[role="listbox"] li:nth-child(1), div[data-baseweb="popover"] li:nth-child(1) { background-color: #ef4444 !important; color: #ffffff !important; }
    div[role="listbox"] > *:nth-child(2), ul[role="listbox"] li:nth-child(2), div[data-baseweb="popover"] li:nth-child(2) { background-color: #f97316 !important; color: #ffffff !important; }
    div[role="listbox"] > *:nth-child(3), ul[role="listbox"] li:nth-child(3), div[data-baseweb="popover"] li:nth-child(3) { background-color: #f59e0b !important; color: #ffffff !important; }
    div[role="listbox"] > *:nth-child(4), ul[role="listbox"] li:nth-child(4), div[data-baseweb="popover"] li:nth-child(4) { background-color: #eab308 !important; color: #ffffff !important; }
    div[role="listbox"] > *:nth-child(5), ul[role="listbox"] li:nth-child(5), div[data-baseweb="popover"] li:nth-child(5) { background-color: #84cc16 !important; color: #ffffff !important; }
    div[role="listbox"] > *:nth-child(6), ul[role="listbox"] li:nth-child(6), div[data-baseweb="popover"] li:nth-child(6) { background-color: #22c55e !important; color: #ffffff !important; }
    div[role="listbox"] > *:nth-child(7), ul[role="listbox"] li:nth-child(7), div[data-baseweb="popover"] li:nth-child(7) { background-color: #10b981 !important; color: #ffffff !important; }
    div[role="listbox"] > *:hover, ul[role="listbox"] li:hover, div[data-baseweb="popover"] li:hover { filter: brightness(1.2) !important; transform: scale(1.015) !important; }
    
    
    
/* =========================================
   EMI COLLECTION - CLEAN FINANCIAL UI
========================================= */

.emi-summary-wrapper {
    margin: 22px 0 28px 0;
    padding: 22px;
    background: linear-gradient(135deg, #0B1534, #10204F);
    border: 1px solid rgba(79, 129, 255, 0.26);
    border-top: 3px solid #FF6A00;
    border-radius: 18px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.28);
}

.emi-summary-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.emi-summary-title {
    color: #F4F7FF;
    font-size: 1.12rem;
    font-weight: 700;
    letter-spacing: -0.3px;
}

.emi-summary-subtitle {
    color: #A9B6D3;
    font-size: 0.78rem;
    margin-top: 4px;
}

.emi-live-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 11px;
    border-radius: 30px;
    background: rgba(47, 107, 255, 0.14);
    border: 1px solid rgba(79, 129, 255, 0.34);
    color: #9DBBFF;
    font-size: 0.72rem;
    font-weight: 700;
}

.emi-live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #6FA0FF;
    box-shadow: 0 0 8px rgba(111, 160, 255, 0.7);
}

.emi-summary-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
}

.emi-summary-card {
    position: relative;
    padding: 20px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(120, 150, 220, 0.18);
    transition: all 0.25s ease;
    min-width: 0;
}

.emi-summary-card:hover {
    transform: translateY(-3px);
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(160, 185, 240, 0.4);
}

.emi-card-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 18px;
}

.emi-card-icon {
    width: 37px;
    height: 37px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    font-size: 1.05rem;
    flex-shrink: 0;
}

.emi-card-label {
    color: #B7C3E0;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.2px;
}

.emi-card-amount {
    font-size: clamp(1.2rem, 2vw, 1.75rem);
    font-weight: 800;
    letter-spacing: -0.8px;
    line-height: 1.35;
    overflow-wrap: anywhere;
}

.emi-card-note {
    color: #8FA0C4;
    font-size: 0.72rem;
    margin-top: 8px;
}

.emi-initial .emi-card-icon {
    background: rgba(47, 107, 255, 0.22);
}
.emi-initial .emi-card-amount {
    color: #8DB1FF;
}

.emi-total {
    background: rgba(255, 106, 0, 0.08);
    border-color: rgba(255, 138, 0, 0.32);
}
.emi-total .emi-card-icon {
    background: rgba(255, 138, 0, 0.20);
}
.emi-total .emi-card-amount {
    color: #FFA43A;
}

.emi-recovery .emi-card-icon {
    background: rgba(111, 160, 255, 0.20);
}

.emi-summary-footer {
    border-top: 1px solid rgba(120, 150, 220, 0.18);
    margin-top: 19px;
    padding-top: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    color: #8FA0C4;
    font-size: 0.72rem;
}

@media (max-width: 700px) {
    .emi-summary-wrapper {
        padding: 16px;
    }

    .emi-summary-grid {
        grid-template-columns: 1fr;
        gap: 10px;
    }

    .emi-summary-card {
        padding: 16px;
    }

    .emi-card-top {
        margin-bottom: 10px;
    }
}

    /* =========================================================
       NEW LAYOUT CHROME: top navigation bar, sidebar, nav pills
       ========================================================= */
    .block-container { padding-top: 1rem !important; max-width: 1600px; }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
    footer { visibility: hidden; }

    /* The sidebar is collapsed/expanded by our own toggle - hide Streamlit's native chevrons */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarHeader"] { display: none !important; }

    [data-testid="stSidebar"] {
        transition: width .2s cubic-bezier(.4,0,.2,1), min-width .2s cubic-bezier(.4,0,.2,1), max-width .2s cubic-bezier(.4,0,.2,1);
        overflow-x: hidden;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: .9rem; }
    [data-testid="stSidebar"] hr { margin: .9rem 0 !important; }

    /* Sidebar smoothness: never dim stale sidebar elements while Streamlit reruns,
       and fade freshly mounted sidebar items in quickly */
    [data-testid="stSidebar"] [data-stale="true"],
    [data-testid="stSidebar"] .stale-element {
        opacity: 1 !important;
        transition: none !important;
    }
    @keyframes sbFadeIn { from { opacity: 0; } to { opacity: 1; } }
    [data-testid="stSidebar"] [data-testid="stElementContainer"] {
        animation: sbFadeIn .18s ease-out both;
    }

    /* Sidebar brand (logo only - the title lives in the centered page header) */
    .sb-brand {
        display: flex; align-items: center; justify-content: center;
        padding: 4px 0 16px 0; margin-bottom: 14px;
        border-bottom: 1px solid rgba(79,129,255,0.26);
    }
    .sb-brand.collapsed { padding: 4px 0 14px 0; margin-bottom: 10px; }
    .sb-brand.collapsed .logo-tile { padding: 4px 6px; border-radius: 14px; }

    /* Centered hero header (top of the website) */
    .hero-header {
        position: relative;
        display: flex; align-items: center; justify-content: center;
        gap: 24px; flex-wrap: wrap;
        padding: 22px 20px 28px 20px;
        margin: 0 0 16px 0;
        text-align: center;
    }
    .hero-header::after {
        content: "";
        position: absolute; left: 50%; bottom: 0;
        transform: translateX(-50%);
        width: min(660px, 74%); height: 3px; border-radius: 3px;
        background: linear-gradient(90deg, transparent, #2F6BFF, #FF8A00, #FF3D00, transparent);
        opacity: .95;
    }
    .hero-logo { position: relative; display: flex; flex-shrink: 0; }
    .hero-logo .logo-tile { position: relative; z-index: 1; }
    .hero-logo::before {
        content: "";
        position: absolute; inset: -26px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,106,0,0.50) 0%, rgba(47,107,255,0.30) 45%, transparent 70%);
        opacity: .35;
        pointer-events: none;
        z-index: 0;
        animation: heroGlow 3.4s ease-in-out infinite;
    }
    .hero-title {
        margin: 0;
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: clamp(1.9rem, 3.8vw, 3rem);
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: #F4F7FF;
        text-shadow: 0 2px 26px rgba(47,107,255,0.45);
    }

    /* Top navigation bar (the row that contains .topbar-marker) */
    div[data-testid="stHorizontalBlock"]:has(.topbar-marker) {
        position: sticky; top: .5rem; z-index: 60;
        align-items: center;
        background: rgba(7,14,38,0.94);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(79,129,255,0.32);
        border-bottom: 2px solid rgba(255,106,0,0.75);
        border-radius: 18px;
        padding: 10px 16px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    }
    div[data-testid="stHorizontalBlock"]:has(.topbar-marker) .stButton > button { height: 44px; }

    /* Navigation radio rendered as pill tabs */
    div[role="radiogroup"] { gap: 6px; flex-wrap: wrap; }
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(79,129,255,0.26);
        border-radius: 12px;
        padding: 9px 16px;
        cursor: pointer;
        transition: all .22s ease;
    }
    div[role="radiogroup"] > label > div:first-child { display: none; }
    div[role="radiogroup"] > label p { font-weight: 700; margin: 0; color: #B4C2E4; font-size: .9rem; }
    div[role="radiogroup"] > label:hover { background: rgba(47,107,255,0.20); border-color: rgba(111,160,255,0.55); }
    div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(135deg, #F26B0A, #E0340E);
        border-color: rgba(255,170,90,0.85);
        box-shadow: 0 4px 16px rgba(255,106,0,0.4);
    }
    div[role="radiogroup"] > label:has(input:checked) p { color: #ffffff; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }

    /* Universal search with magnifier icon */
    .stTextInput input[placeholder^="Search"] {
        padding-left: 42px !important;
        background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%238DB1FF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: 14px center !important;
        background-size: 18px !important;
        height: 44px;
    }

    /* Profile chip (far right of the top bar) */
    .profile-chip { display: flex; align-items: center; justify-content: flex-end; gap: 12px; }
    .pc-avatar {
        width: 42px; height: 42px; border-radius: 50%; flex-shrink: 0;
        background: linear-gradient(135deg, #FF9A00, #FF2D12);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; color: #fff; font-size: 1.1rem;
        box-shadow: 0 0 14px rgba(255,106,0,0.5);
        border: 2px solid rgba(111,160,255,0.7);
    }
    .pc-name { font-weight: 700; color: #F4F7FF; font-size: .92rem; line-height: 1.15; }
    .pc-role {
        display: inline-block; margin-top: 3px; padding: 2px 9px; border-radius: 20px;
        font-size: .64rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase;
        color: #FFB36B; background: rgba(255,106,0,0.16); border: 1px solid rgba(255,138,0,0.5);
    }
    @media (max-width: 900px) {
        .profile-chip { justify-content: flex-start; }
        div[data-testid="stHorizontalBlock"]:has(.topbar-marker) { position: static; }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# Brand logo loader
# Put your logo image next to app.py as "logo.png" (or in an "assets" folder).
# It is shrunk once (cached) so the page stays fast. If no logo file is found,
# a built-in matching e-Rin logo is shown instead.
# -----------------------------------------------------------------------------
_LOGO_CANDIDATES = [
    "logo.png", "logo.jpg", "logo.jpeg", "logo.webp",
    "erin_logo.png", "e-rin-logo.png", "e-Rin-logo.png",
    os.path.join("assets", "logo.png"),
    os.path.join("assets", "logo.jpg"),
    os.path.join("assets", "logo.jpeg"),
    os.path.join("assets", "logo.webp"),
    os.path.join("data", "logo.png"),
]

_FALLBACK_LOGO_SVG = """<svg xmlns='http://www.w3.org/2000/svg' width='64' height='96' viewBox='0 0 64 96' fill='none'>
<defs>
<linearGradient id='ph' x1='8' y1='0' x2='58' y2='0' gradientUnits='userSpaceOnUse'><stop stop-color='#FF6A00'/><stop offset='0.55' stop-color='#7A3BE0'/><stop offset='1' stop-color='#2F6BFF'/></linearGradient>
<linearGradient id='ee' x1='10' y1='26' x2='50' y2='66' gradientUnits='userSpaceOnUse'><stop stop-color='#FFC400'/><stop offset='0.45' stop-color='#FF7A00'/><stop offset='1' stop-color='#FF2D12'/></linearGradient>
</defs>
<rect x='9' y='4' width='46' height='88' rx='11' fill='#F4F7FF' stroke='url(#ph)' stroke-width='4'/>
<rect x='24' y='10' width='16' height='3' rx='1.5' fill='#0B2C9E'/>
<path d='M48 44A17 17 0 1 0 41 58.5' stroke='url(#ee)' stroke-width='9' stroke-linecap='round'/>
<path d='M15 44H48' stroke='url(#ee)' stroke-width='6' stroke-linecap='round'/>
<rect x='20' y='72' width='28' height='7' rx='2' fill='#1E4FD8'/>
<rect x='22' y='83' width='24' height='3' rx='1.5' fill='#FF4A12'/>
</svg>"""

def _find_logo_file():
    base_dirs = []
    try:
        base_dirs.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    base_dirs.append(os.getcwd())
    for base in base_dirs:
        for name in _LOGO_CANDIDATES:
            candidate = os.path.join(base, name)
            if os.path.isfile(candidate):
                return candidate
    return None

@st.cache_data(show_spinner=False)
def _logo_data_uri(path, mtime_ns):
    """Reads the logo file, shrinks it (so it is light to send to the browser) and
    returns it as an inline data URI. Cached until the file changes."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            im = im.convert("RGBA")
            im.thumbnail((420, 420))
            buf = io.BytesIO()
            im.save(buf, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(ext, "image/png")
        with open(path, "rb") as f:
            return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")

def brand_logo_img(size=44):
    """Brand logo shown on a clean badge. 'size' is the logo height in pixels."""
    uri = None
    logo_path = _find_logo_file()
    if logo_path:
        try:
            uri = _logo_data_uri(logo_path, os.stat(logo_path).st_mtime_ns)
        except Exception:
            uri = None
    if uri is None:
        uri = "data:image/svg+xml;base64," + base64.b64encode(_FALLBACK_LOGO_SVG.encode("utf-8")).decode("ascii")
    return (
        f'<span class="logo-tile">'
        f'<img src="{uri}" alt="e-Rin Recovery" style="height:{size}px;width:auto;"/>'
        f'</span>'
    )

DATA_DIR = "data"
HISTORY_DIR = os.path.join(DATA_DIR, "history")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

# Clean up stray temp files
for stray in glob.glob(f"{DATA_DIR}/*.tmp*") + glob.glob(f"{DATA_DIR}/tmp*"):
    try:
        os.remove(stray)
    except Exception:
        pass

# -----------------------------------------------------------------------------
# 2. Authentication Credentials & Roles (Default Seed Data)
# -----------------------------------------------------------------------------
USERS = {
    "saiful": {
        "name": "Saiful (Admin)",
        "agent_name": "Saiful",
        "role": "admin",
        "hashed_pw": "$2b$12$TejkeGxfYEC0qjJe2sV6gOaid2hJSmIgKW8oxLXzIPWytJRURxLBC"
    },
    "sourav": {
        "name": "Sourav",
        "agent_name": "Sourav",
        "role": "agent",
        "hashed_pw": "$2b$12$iaZrHT0cqUf8HGcYw7eSV.ggfJAgUawZiIFB.0fGINrG9eAAiQ.QK"
    },
    "nowrin": {
        "name": "Nourin",
        "agent_name": "Nourin",
        "role": "agent",
        "hashed_pw": "$2b$12$iaZrHT0cqUf8HGcYw7eSV.ggfJAgUawZiIFB.0fGINrG9eAAiQ.QK"
    },
    "shifat": {
        "name": "Shifat",
        "agent_name": "Shifat",
        "role": "agent",
        "hashed_pw": "$2b$12$iaZrHT0cqUf8HGcYw7eSV.ggfJAgUawZiIFB.0fGINrG9eAAiQ.QK"
    },
    "nibir": {
        "name": "Rafi",
        "agent_name": "Rafi",
        "role": "agent",
        "hashed_pw": "$2b$12$iaZrHT0cqUf8HGcYw7eSV.ggfJAgUawZiIFB.0fGINrG9eAAiQ.QK"
    },
    "nazmul": {
        "name": "Nazmul",
        "agent_name": "Nazmul",
        "role": "agent",
        "hashed_pw": "$2b$12$iaZrHT0cqUf8HGcYw7eSV.ggfJAgUawZiIFB.0fGINrG9eAAiQ.QK"
    }
}

# --- Role definitions -------------------------------------------------------
ROLE_ADMIN = "admin"
ROLE_AGENT = "agent"
ROLE_SUPERVISOR = "supervisor"
VALID_ROLES = (ROLE_ADMIN, ROLE_AGENT, ROLE_SUPERVISOR)
# Label shown in the account-creation dropdown -> stored role value
ROLE_OPTIONS_MAP = {"Agent": ROLE_AGENT, "Supervisor": ROLE_SUPERVISOR, "Admin": ROLE_ADMIN}
ROLE_DISPLAY_LABELS = {ROLE_ADMIN: "Admin", ROLE_AGENT: "Agent", ROLE_SUPERVISOR: "Supervisor"}

EMI_COLOR_MAP = {
    "Total Devices": "#2F6BFF",
    "0 EMI Paid": "#ef4444",
    "1 EMI Paid": "#f97316",
    "2 EMI Paid": "#f59e0b",
    "3 EMI Paid": "#eab308",
    "4 EMI Paid": "#84cc16",
    "5 EMI Paid": "#22c55e",
    "6 EMI Paid": "#10b981"
}

DROPDOWN_EMI_MAP = {
    "0 EMI Paid": "🔴 0 EMI Paid",
    "1 EMI Paid": "🟠 1 EMI Paid",
    "2 EMI Paid": "🟡 2 EMI Paid",
    "3 EMI Paid": "🟨 3 EMI Paid",
    "4 EMI Paid": "🟢 4 EMI Paid",
    "5 EMI Paid": "❇️ 5 EMI Paid",
    "6 EMI Paid": "🟩 6 EMI Paid"
}
REVERSE_DROPDOWN_EMI_MAP = {v: k for k, v in DROPDOWN_EMI_MAP.items()}
DISPLAY_EMI_OPTIONS = list(DROPDOWN_EMI_MAP.values())

def to_dropdown_emi(val):
    s = str(val).strip()
    return DROPDOWN_EMI_MAP.get(s, s)

def from_dropdown_emi(val):
    s = str(val).strip()
    return REVERSE_DROPDOWN_EMI_MAP.get(s, s)

# -----------------------------------------------------------------------------
# 2b. Persistent Agent Account Storage (JSON-based)
# -----------------------------------------------------------------------------
ACCOUNTS_FILE = os.path.join(DATA_DIR, "agent_accounts.json")

def _seed_accounts_from_defaults():
    seed = {}
    for k, v in USERS.items():
        seed[k] = dict(v)
        seed[k]["active"] = True
    return seed

def save_accounts(accounts):
    temp_fd, temp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    os.close(temp_fd)
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2)
        os.replace(temp_path, ACCOUNTS_FILE)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        seed = _seed_accounts_from_defaults()
        save_accounts(seed)
        return seed
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not data:
            raise ValueError("Empty or invalid accounts file")
        # Safety net: ensure admin account always exists and is always active
        if "saiful" not in data:
            data["saiful"] = dict(USERS["saiful"])
            data["saiful"]["active"] = True
        else:
            data["saiful"]["active"] = True
        return data
    except Exception:
        seed = _seed_accounts_from_defaults()
        save_accounts(seed)
        return seed

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.display_name = None
    st.session_state.agent_name = None

def _require_roles(*allowed_roles):
    """Backend permission gate: stops the script immediately if the logged-in
    user's role is not allowed to perform the action that follows."""
    if st.session_state.get("role") not in allowed_roles:
        st.error("⛔ Security Exception: Your role does not have permission to perform this action.")
        st.stop()

def verify_login(user_in, pass_in):
    accounts = load_accounts()
    user_key = user_in.strip().lower()
    if user_key in accounts:
        user_record = accounts[user_key]
        if not user_record.get("active", True):
            return None
        stored_hash = user_record.get("hashed_pw", "")
        try:
            if bcrypt.checkpw(pass_in.encode("utf-8"), stored_hash.encode("utf-8")):
                return user_record
        except Exception:
            pass
    return None

# -----------------------------------------------------------------------------
# 3. Login Barrier
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    # Login-page-only styling (brand card + brand orange call-to-action button)
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        .login-brand { text-align: center; margin: 5vh 0 22px 0; }
        .login-brand .logo-tile { margin-bottom: 18px; }
        .login-brand h2 { margin: 0; font-size: 1.75rem; font-weight: 800; letter-spacing: -0.01em; color: #F4F7FF; }
        .login-brand p { margin: 8px 0 0 0; color: #A9B6D3; font-size: .9rem; }
        [data-testid="stForm"] {
            background: linear-gradient(145deg, rgba(14,25,60,0.92) 0%, rgba(6,12,32,0.96) 100%);
            border: 1px solid rgba(79,129,255,0.34);
            border-top: 3px solid #FF6A00;
            border-radius: 22px;
            padding: 30px 28px 24px 28px;
            box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.02) inset;
            backdrop-filter: blur(18px);
        }
        [data-testid="stForm"] label p { font-weight: 600; color: #B4C2E4; font-size: .85rem; }
        [data-testid="stForm"] .stTextInput > div > div > input { height: 46px; }
        [data-testid="InputInstructions"] { display: none !important; }
        [data-testid="stFormSubmitButton"] button {
            height: 48px; margin-top: 8px;
            background: linear-gradient(135deg, #F26B0A 0%, #E0340E 100%) !important;
            border: none !important; color: #ffffff !important;
            font-weight: 800 !important; letter-spacing: .02em;
            box-shadow: 0 10px 26px rgba(255,106,0,0.38) !important;
        }
        [data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 14px 34px rgba(255,106,0,0.55) !important;
            filter: brightness(1.08);
        }
        [data-testid="stFormSubmitButton"] button p { color: #ffffff !important; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }
        </style>
        """,
        unsafe_allow_html=True
    )
    _lg_left, _lg_mid, _lg_right = st.columns([1, 1.15, 1])
    with _lg_mid:
        st.markdown(
            f"""
            <div class="login-brand">
                {brand_logo_img(104)}
                <h2>e-Rin <span class="gradient-text">Recovery Dashboard</span></h2>
                <p>Sign in to continue</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.form("login_box"):
            user_in = st.text_input("Username")
            pass_in = st.text_input("Password", type="password")
            submit = st.form_submit_button("Access Dashboard  →", use_container_width=True, type="primary")

            if submit:
                user_info = verify_login(user_in, pass_in)
                if user_info:
                    _login_role = str(user_info.get("role", "")).strip().lower()
                    if _login_role not in VALID_ROLES:
                        st.error("This account has an invalid role. Please contact your admin.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.username = user_in.strip().lower()
                        st.session_state.role = _login_role
                        st.session_state.display_name = user_info["name"]
                        st.session_state.agent_name = user_info["agent_name"]
                        st.rerun()
                else:
                    st.error("Invalid username or password, or this account has been deactivated.")
    st.stop()

# -----------------------------------------------------------------------------
# 3b. Live Account Status Re-Validation
# Ensures a deactivated or deleted agent is force-logged-out on their next
# interaction/rerun, without affecting any other logic.
# -----------------------------------------------------------------------------
_live_accounts_check = load_accounts()
_current_user_record = _live_accounts_check.get(st.session_state.username)
if _current_user_record is None or not _current_user_record.get("active", True):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.display_name = None
    st.session_state.agent_name = None
    st.error("⛔ Your account has been deactivated or removed by the administrator. Please contact your admin.")
    st.stop()

# Role re-validation: the role is always read from the live account record on every
# interaction, so a role changed by the admin takes effect immediately and the panel
# shown always matches the stored role.
_live_role = str(_current_user_record.get("role", "")).strip().lower()
if _live_role not in VALID_ROLES:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.display_name = None
    st.session_state.agent_name = None
    st.error("⛔ Your account role is not valid. Please contact your admin.")
    st.stop()
st.session_state.role = _live_role

# -----------------------------------------------------------------------------
# 4. Standard Date Parser Engine
# (Performance: parsed date strings are memoized across reruns and sessions.
#  The parsing rules and results are exactly the same as before.)
# -----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _get_date_parse_cache():
    return {}

_DATE_PARSE_CACHE = _get_date_parse_cache()

def _parse_date_string(val_str):
    try:
        return _DATE_PARSE_CACHE[val_str]
    except KeyError:
        pass

    result = None
    known_formats = [
        "%m/%d/%Y", "%m-%d-%Y",
        "%d %B %Y", "%d %b %Y",
        "%B %d, %Y", "%b %d, %Y",
        "%B %d %Y", "%b %d %Y",
        "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"
    ]
    parsed = False
    for fmt in known_formats:
        try:
            result = pd.to_datetime(val_str, format=fmt).date()
            parsed = True
            break
        except Exception:
            pass
    if not parsed:
        dt = pd.to_datetime(val_str, errors="coerce")
        result = dt.date() if pd.notna(dt) else None

    if len(_DATE_PARSE_CACHE) < 100000:
        _DATE_PARSE_CACHE[val_str] = result
    return result

def to_clean_date(val):
    if pd.isna(val) or str(val).strip() in ['', 'nan', 'None', 'NaT']:
        return None
    return _parse_date_string(str(val).strip())

def date_to_string_format(val):
    d = to_clean_date(val)
    if d is not None:
        return f"{d.day} {d.strftime('%B %Y')}"
    return ""

# -----------------------------------------------------------------------------
# 4b. EMI Collection Calculation Helpers
# -----------------------------------------------------------------------------
def extract_emi_number(val):
    """Extracts the numeric count of EMIs paid from text like '3 EMI Paid'.
    Returns 0 safely if missing, blank, or unparseable."""
    s = str(val).strip()
    if not s or s.lower() in ['nan', 'none', 'nat']:
        return 0
    match = re.search(r'\d+', s)
    if match:
        try:
            return int(match.group())
        except Exception:
            return 0
    return 0

def clean_emi_amount(val):
    """Cleans 'Monthly EMI Amount' values (removes currency symbols, commas,
    spaces) and safely converts to float. Returns 0.0 if invalid/missing."""
    s = str(val).strip()
    if not s or s.lower() in ['nan', 'none', 'nat']:
        return 0.0
    s = s.replace('৳', '').replace('$', '').replace(',', '').replace(' ', '').strip()
    try:
        return float(s)
    except Exception:
        return 0.0

def format_bdt_currency(amount):
    """Formats a number into South Asian (Bangladeshi/Indian) comma style,
    e.g. 125000 -> '1,25,000'."""
    try:
        amount = int(round(float(amount)))
    except Exception:
        amount = 0
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    s = str(amount)
    if len(s) <= 3:
        return f"{sign}{s}"
    last3 = s[-3:]
    rest = s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return f"{sign}" + ','.join(parts) + ',' + last3

# -----------------------------------------------------------------------------
# 5. Robust Ingestion, Smart Column Detection & Daily Call Ledger Engine
# -----------------------------------------------------------------------------
def detect_operational_columns(df):
    detected = {
        'recovery_call_date': None,
        'follow_up_date': None,
        'assign_person': None,
        'emi_status': None,
        'lock_status': None,
        'loan_status': None,
        'remarks': None
    }
    for c in df.columns:
        cl = str(c).lower().replace('_', ' ').replace('-', ' ').strip()
        if not detected['recovery_call_date'] and any(k in cl for k in ['recovery call date', 'recovery date', 'initial call date']):
            detected['recovery_call_date'] = c
        elif not detected['follow_up_date'] and any(k in cl for k in ['last follow up call date', 'follow up date', 'followup', 'next call', 'target date']):
            detected['follow_up_date'] = c
        elif not detected['assign_person'] and any(k in cl for k in ['assign person', 'assigned person', 'officer', 'agent', 'caller', 'assigned to', 'assign']):
            detected['assign_person'] = c
        elif not detected['emi_status'] and any(k in cl for k in ['emi status', 'installment', 'repayment', 'emi']) and 'amount' not in cl and 'monthly' not in cl:
            detected['emi_status'] = c
        elif not detected['lock_status'] and any(k in cl for k in ['lock status', 'device lock', 'lock / unlock', 'lock']):
            detected['lock_status'] = c
        elif not detected['loan_status'] and any(k in cl for k in ['loan status', 'loan']):
            detected['loan_status'] = c
        elif not detected['remarks'] and any(k in cl for k in ['remarks status', 'remarks', 'remark', 'comments', 'comment', 'notes']):
            detected['remarks'] = c

    if not detected['recovery_call_date']:
        if detected['follow_up_date'] and detected['follow_up_date'] in df.columns:
            idx = list(df.columns).index(detected['follow_up_date'])
            df.insert(idx, 'Recovery Call Date', "")
        elif detected['assign_person'] and detected['assign_person'] in df.columns:
            idx = list(df.columns).index(detected['assign_person']) + 1
            df.insert(idx, 'Recovery Call Date', "")
        else:
            df['Recovery Call Date'] = ""
        detected['recovery_call_date'] = 'Recovery Call Date'

    if not detected['follow_up_date']:
        if detected['recovery_call_date'] and detected['recovery_call_date'] in df.columns:
            idx = list(df.columns).index(detected['recovery_call_date']) + 1
            df.insert(idx, 'Last Follow Up Call Date', "")
        else:
            df['Last Follow Up Call Date'] = ""
        detected['follow_up_date'] = 'Last Follow Up Call Date'

    if not detected['assign_person']:
        df['Assign Person'] = "Unassigned"
        detected['assign_person'] = 'Assign Person'
    if not detected['emi_status']:
        df['EMI Status'] = "0 EMI Paid"
        detected['emi_status'] = 'EMI Status'
    if not detected['lock_status']:
        df['Lock Status'] = "Unlocked"
        detected['lock_status'] = 'Lock Status'
    if not detected['loan_status']:
        df['Loan Status'] = "Active"
        detected['loan_status'] = 'Loan Status'
    if not detected['remarks']:
        df['Remarks'] = ""
        detected['remarks'] = 'Remarks'

    return detected

def _file_signature(path):
    """(modified-time, size) of a file - used to know when cached data is still valid."""
    try:
        s = os.stat(path)
        return (s.st_mtime_ns, s.st_size)
    except OSError:
        return (0, 0)

def _read_live_file_from_disk(filepath):
    if not os.path.exists(filepath):
        return pd.DataFrame()
    if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath, dtype=str, keep_default_na=False)
    else:
        try:
            df = pd.read_csv(filepath, encoding="utf-8-sig", dtype=str, keep_default_na=False)
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding="latin1", dtype=str, keep_default_na=False)

    df.columns = [str(c).strip().replace('\ufeff', '') for c in df.columns]

    if "Last Modified By" not in df.columns:
        df["Last Modified By"] = ""
    if "Last Updated At" not in df.columns:
        df["Last Updated At"] = ""

    for c in df.columns:
        df[c] = df[c].fillna("").astype(str).str.strip()
        df[c] = df[c].replace({"nan": "", "None": "", "NaT": ""})

    detected = detect_operational_columns(df)
    emi_col = detected['emi_status']
    df[emi_col] = df[emi_col].apply(from_dropdown_emi)
    return df

# Performance: the file is parsed only when it actually changes on disk
# (file_signature is part of the cache key). Each caller receives its own copy.
@st.cache_data(show_spinner=False, max_entries=12)
def _load_live_file_cached(filepath, file_signature):
    return _read_live_file_from_disk(filepath)

def load_live_file(filepath):
    if not os.path.exists(filepath):
        return pd.DataFrame()
    return _load_live_file_cached(filepath, _file_signature(filepath))


# -----------------------------------------------------------------------------
# Persistent Initial EMI Collection (captured once per uploaded file)
# -----------------------------------------------------------------------------
INITIAL_EMI_COLLECTION_FILE = os.path.join(DATA_DIR, "initial_emi_collection.json")


def load_initial_emi_collections():
    if not os.path.exists(INITIAL_EMI_COLLECTION_FILE):
        return {}
    try:
        with open(INITIAL_EMI_COLLECTION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_initial_emi_collections(data):
    temp_fd, temp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    os.close(temp_fd)
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_path, INITIAL_EMI_COLLECTION_FILE)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e


def capture_initial_emi_collection(filepath, filename):
    """Save the first uploaded EMI total once; never overwrite an existing baseline."""
    saved_collections = load_initial_emi_collections()
    if filename in saved_collections:
        return saved_collections[filename]

    initial_df = load_live_file(filepath)
    if "Monthly EMI Amount" not in initial_df.columns:
        return None

    initial_detected = detect_operational_columns(initial_df)
    initial_emi_col = initial_detected["emi_status"]
    initial_emi_numbers = initial_df[initial_emi_col].apply(extract_emi_number)
    initial_emi_amounts = initial_df["Monthly EMI Amount"].apply(clean_emi_amount)
    initial_total = float((initial_emi_numbers * initial_emi_amounts).sum())

    saved_collections[filename] = initial_total
    save_initial_emi_collections(saved_collections)
    return initial_total


def atomic_save_file(df, target_filepath):
    target_dir = os.path.dirname(target_filepath)
    is_excel = target_filepath.endswith('.xlsx') or target_filepath.endswith('.xls')
    file_ext = os.path.splitext(target_filepath)[1] if target_filepath else ".tmp"
    temp_fd, temp_path = tempfile.mkstemp(dir=target_dir, suffix=file_ext)
    os.close(temp_fd)

    try:
        if is_excel:
            df.to_excel(temp_path, index=False)
        else:
            df.to_csv(temp_path, index=False, encoding="utf-8-sig")
        os.replace(temp_path, target_filepath)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def save_daily_history_snapshot(df, active_filename):
    today_str = datetime.now().strftime("%Y-%m-%d")
    base_name = os.path.splitext(active_filename)[0]
    snapshot_filename = f"snapshot_{today_str}_{base_name}.csv"
    snapshot_path = os.path.join(HISTORY_DIR, snapshot_filename)
    
    temp_fd, temp_path = tempfile.mkstemp(dir=HISTORY_DIR, suffix=".tmp")
    os.close(temp_fd)
    try:
        df.to_csv(temp_path, index=False, encoding="utf-8-sig")
        os.replace(temp_path, snapshot_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def get_row_identifier(row, row_idx):
    si_val = str(row.get("SI Number", "")).strip()
    cid_val = str(row.get("Customer Id", "")).strip()
    if si_val or cid_val:
        return f"{si_val}_{cid_val}"
    return f"row_{row_idx}"

def sync_and_load_call_ledger(df, active_filename, assign_col, rec_date_col, follow_date_col):
    base_name = os.path.splitext(active_filename)[0]
    ledger_path = os.path.join(HISTORY_DIR, f"call_ledger_{base_name}.csv")
    cols = ["Event_Key", "Row_ID", "Officer", "Call_Type", "Scheduled_Date", "Action_Date", "Timestamp"]

    if os.path.exists(ledger_path):
        try:
            ledger_df = pd.read_csv(ledger_path, dtype=str, keep_default_na=False)
        except Exception:
            ledger_df = pd.DataFrame(columns=cols)
    else:
        ledger_df = pd.DataFrame(columns=cols)

    for c in cols:
        if c not in ledger_df.columns:
            ledger_df[c] = ""

    existing_keys = set(ledger_df["Event_Key"].astype(str).tolist())
    new_entries = []
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for idx, row in df.iterrows():
        officer = str(row.get(assign_col, "")).strip()
        if not officer or officer.lower() in ["", "nan", "none", "unassigned"]:
            continue
        row_id = get_row_identifier(row, idx)

        # Check Initial Recovery Call Date
        rec_clean = to_clean_date(row.get(rec_date_col, ""))
        if rec_clean is not None:
            sched_str = rec_clean.strftime("%Y-%m-%d")
            event_key = f"{row_id}|Recovery Call|{sched_str}"
            if event_key not in existing_keys:
                existing_keys.add(event_key)
                new_entries.append({
                    "Event_Key": event_key,
                    "Row_ID": row_id,
                    "Officer": officer,
                    "Call_Type": "Recovery Call",
                    "Scheduled_Date": sched_str,
                    "Action_Date": sched_str,
                    "Timestamp": now_ts
                })

        # Check Last Follow Up Call Date
        fol_clean = to_clean_date(row.get(follow_date_col, ""))
        if fol_clean is not None:
            sched_str = fol_clean.strftime("%Y-%m-%d")
            event_key = f"{row_id}|Follow Up Call|{sched_str}"
            if event_key not in existing_keys:
                existing_keys.add(event_key)
                new_entries.append({
                    "Event_Key": event_key,
                    "Row_ID": row_id,
                    "Officer": officer,
                    "Call_Type": "Follow Up Call",
                    "Scheduled_Date": sched_str,
                    "Action_Date": sched_str,
                    "Timestamp": now_ts
                })

    if new_entries:
        ledger_df = pd.concat([ledger_df, pd.DataFrame(new_entries)], ignore_index=True)
        atomic_save_file(ledger_df, ledger_path)

    return ledger_df

def record_edited_call_activities(active_filename, orig_df, edited_df, changed_indices, active_user, assign_col, rec_date_col, follow_date_col):
    base_name = os.path.splitext(active_filename)[0]
    ledger_path = os.path.join(HISTORY_DIR, f"call_ledger_{base_name}.csv")
    cols = ["Event_Key", "Row_ID", "Officer", "Call_Type", "Scheduled_Date", "Action_Date", "Timestamp"]

    if os.path.exists(ledger_path):
        try:
            ledger_df = pd.read_csv(ledger_path, dtype=str, keep_default_na=False)
        except Exception:
            ledger_df = pd.DataFrame(columns=cols)
    else:
        ledger_df = pd.DataFrame(columns=cols)

    for c in cols:
        if c not in ledger_df.columns:
            ledger_df[c] = ""

    existing_keys = set(ledger_df["Event_Key"].astype(str).tolist())
    today_str = datetime.now().strftime("%Y-%m-%d")
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entries = []

    for idx in changed_indices:
        orig_row = orig_df.loc[idx]
        edit_row = edited_df.loc[idx]
        officer = str(edit_row.get(assign_col, active_user)).strip()
        if not officer or officer.lower() in ["", "nan", "none", "unassigned"]:
            officer = active_user
        row_id = get_row_identifier(edit_row, idx)

        # Check if Recovery Call Date was set or modified
        old_rec = to_clean_date(orig_row.get(rec_date_col, ""))
        new_rec = to_clean_date(edit_row.get(rec_date_col, ""))
        if new_rec is not None and new_rec != old_rec:
            sched_str = new_rec.strftime("%Y-%m-%d")
            event_key = f"{row_id}|Recovery Call|{sched_str}"
            if event_key not in existing_keys:
                existing_keys.add(event_key)
                new_entries.append({
                    "Event_Key": event_key,
                    "Row_ID": row_id,
                    "Officer": officer,
                    "Call_Type": "Recovery Call",
                    "Scheduled_Date": sched_str,
                    "Action_Date": today_str,
                    "Timestamp": now_ts
                })

        # Check if Last Follow Up Call Date was set or modified
        old_fol = to_clean_date(orig_row.get(follow_date_col, ""))
        new_fol = to_clean_date(edit_row.get(follow_date_col, ""))
        if new_fol is not None and new_fol != old_fol:
            sched_str = new_fol.strftime("%Y-%m-%d")
            event_key = f"{row_id}|Follow Up Call|{sched_str}"
            if event_key not in existing_keys:
                existing_keys.add(event_key)
                new_entries.append({
                    "Event_Key": event_key,
                    "Row_ID": row_id,
                    "Officer": officer,
                    "Call_Type": "Follow Up Call",
                    "Scheduled_Date": sched_str,
                    "Action_Date": today_str,
                    "Timestamp": now_ts
                })

    if new_entries:
        ledger_df = pd.concat([ledger_df, pd.DataFrame(new_entries)], ignore_index=True)
        atomic_save_file(ledger_df, ledger_path)

def get_synced_call_ledger(df, active_filename, data_filepath, assign_col, rec_date_col, follow_date_col):
    """Same ledger synchronization as before, but the (expensive) row-by-row sync is
    skipped on reruns where neither the worksheet nor the ledger file has changed."""
    base_name = os.path.splitext(active_filename)[0]
    ledger_path = os.path.join(HISTORY_DIR, f"call_ledger_{base_name}.csv")

    data_sig = _file_signature(data_filepath)
    cached = st.session_state.get("_ledger_sync_cache")
    if (
        cached is not None
        and cached["file"] == active_filename
        and cached["cols"] == (assign_col, rec_date_col, follow_date_col)
        and cached["data_sig"] == data_sig
        and cached["ledger_sig"] == _file_signature(ledger_path)
    ):
        return cached["ledger"].copy()

    ledger = sync_and_load_call_ledger(df, active_filename, assign_col, rec_date_col, follow_date_col)
    st.session_state["_ledger_sync_cache"] = {
        "file": active_filename,
        "cols": (assign_col, rec_date_col, follow_date_col),
        "data_sig": data_sig,
        "ledger_sig": _file_signature(ledger_path),
        "ledger": ledger
    }
    return ledger.copy()

# -----------------------------------------------------------------------------
# 6. Sidebar Navigation & Data Controls (collapsible: icons + labels <-> icons only)
# -----------------------------------------------------------------------------
def _toggle_sidebar():
    st.session_state["sidebar_collapsed"] = not st.session_state.get("sidebar_collapsed", False)

def _sync_refresh_sheet():
    st.session_state["last_known_mtime"] = 0
    st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1

def _do_logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.display_name = None
    st.session_state.agent_name = None

sidebar_collapsed = st.session_state.get("sidebar_collapsed", False)
_sb_width = "80px" if sidebar_collapsed else "296px"
_sb_css = (
    "[data-testid='stSidebar']{width:" + _sb_width + " !important;min-width:" + _sb_width + " !important;max-width:" + _sb_width + " !important;}"
)
if sidebar_collapsed:
    # Icon-only rail: every icon sits in an identical 48x48 centered square with equal spacing.
    # Any leftover expanded-mode widgets (text labels, selectbox, uploader...) are hidden instantly
    # by CSS, so text disappears immediately instead of waiting for the script run to finish.
    _sb_css += """
[data-testid='stSidebar'] [data-testid='stSidebarUserContent'],
[data-testid='stSidebar'] [data-testid='stSidebarContent']{padding-left:.5rem !important;padding-right:.5rem !important;}
[data-testid='stSidebar'] [data-testid='stVerticalBlock']{gap:.7rem !important;}
[data-testid='stSidebar'] [data-testid='stElementContainer']:has(h4),
[data-testid='stSidebar'] [data-testid='stElementContainer']:has([data-testid='stSelectbox']),
[data-testid='stSidebar'] [data-testid='stElementContainer']:has([data-testid='stAlert']),
[data-testid='stSidebar'] [data-testid='stElementContainer']:has([data-testid='stForm']),
[data-testid='stSidebar'] [data-testid='stSelectbox'],
[data-testid='stSidebar'] [data-testid='stForm'],
[data-testid='stSidebar'] [data-testid='stFileUploader'],
[data-testid='stSidebar'] [data-testid='stAlert']{display:none !important;}
[data-testid='stSidebar'] hr{width:34px !important;margin:.2rem auto !important;}
[data-testid='stSidebar'] .stButton,
[data-testid='stSidebar'] [data-testid='stTooltipHoverTarget']{display:flex !important;justify-content:center !important;align-items:center !important;width:100% !important;}
[data-testid='stSidebar'] .stButton button{width:48px !important;min-width:48px !important;max-width:48px !important;height:48px !important;min-height:48px !important;padding:0 !important;margin:0 auto !important;display:flex !important;align-items:center !important;justify-content:center !important;border-radius:14px !important;overflow:hidden !important;}
[data-testid='stSidebar'] .stButton button [data-testid='stMarkdownContainer']{display:flex !important;align-items:center !important;justify-content:center !important;width:auto !important;}
[data-testid='stSidebar'] .stButton button p{margin:0 !important;padding:0 !important;font-size:1.3rem !important;line-height:1 !important;max-width:1.6em;overflow:hidden;white-space:nowrap;text-align:center;}
"""
st.markdown("<style>" + _sb_css + "</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        f'<div class="sb-brand{" collapsed" if sidebar_collapsed else ""}">{brand_logo_img(44 if sidebar_collapsed else 64)}</div>',
        unsafe_allow_html=True
    )

    raw_file_list = glob.glob(f"{DATA_DIR}/*.csv") + glob.glob(f"{DATA_DIR}/*.xlsx") + glob.glob(f"{DATA_DIR}/*.xls")
    valid_files = [
        os.path.basename(f) for f in raw_file_list
        if not os.path.basename(f).startswith("tmp") and not os.path.basename(f).endswith(".tmp")
    ]
    available_files = sorted(list(set(valid_files)))

    if not available_files:
        selected_file = None
        if sidebar_collapsed:
            st.button("📂", key="sb_c_sheet", help="Select Active Work Sheet", on_click=_toggle_sidebar, use_container_width=True)
        else:
            st.warning("⚠️ No work sheets found in 'data/' directory.")
    else:
        _prev_sheet = st.session_state.get("_active_sheet_name")
        if sidebar_collapsed:
            # The selection is remembered while only icons are shown
            selected_file = _prev_sheet if _prev_sheet in available_files else available_files[0]
            st.button("📂", key="sb_c_sheet", help=f"Select Active Work Sheet ({selected_file})", on_click=_toggle_sidebar, use_container_width=True)
            st.button("🔄", key="sb_c_sync", help="Sync / Refresh Sheet", on_click=_sync_refresh_sheet, use_container_width=True)
        else:
            _sheet_idx = available_files.index(_prev_sheet) if _prev_sheet in available_files else 0
            selected_file = st.selectbox("📂 Select Active Work Sheet:", available_files, index=_sheet_idx)
            # on_click runs the refresh before the rerun, so no extra st.rerun() pass is needed
            st.button("🔄 Sync / Refresh Sheet", use_container_width=True, on_click=_sync_refresh_sheet)
        st.session_state["_active_sheet_name"] = selected_file

    # Upload / Delete controls are available to Admin only (Supervisors and Agents never see them)
    if st.session_state.role == ROLE_ADMIN:
        st.markdown("---")
        if sidebar_collapsed:
            st.button("📤", key="sb_c_upload", help="Upload File", on_click=_toggle_sidebar, use_container_width=True)
            if selected_file:
                st.button("🗑️", key="sb_c_delete", help="Delete File", on_click=_toggle_sidebar, use_container_width=True)
        else:
            st.markdown("#### 📤 Upload CSV or Excel")
            with st.form("file_upload_form", clear_on_submit=True):
                uploaded_file = st.file_uploader("Upload File (.csv, .xlsx, .xls)", type=["csv", "xlsx", "xls"], label_visibility="collapsed")
                upload_submit = st.form_submit_button("Save Uploaded File", use_container_width=True)
                if upload_submit and uploaded_file is not None:
                    _require_roles(ROLE_ADMIN)
                    save_path = os.path.join(DATA_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    capture_initial_emi_collection(save_path, uploaded_file.name)
                    st.session_state["last_known_mtime"] = 0
                    st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
                    st.success(f"Uploaded: {uploaded_file.name}")
                    st.rerun()

            if selected_file:
                st.markdown("---")
                st.markdown("#### 🗑️ Delete File")
                if st.button(f"Delete '{selected_file}'", type="secondary", use_container_width=True):
                    _require_roles(ROLE_ADMIN)
                    target_path = os.path.join(DATA_DIR, selected_file)
                    if os.path.exists(target_path):
                        os.remove(target_path)
                        st.session_state["last_known_mtime"] = 0
                        st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
                        st.warning(f"Deleted {selected_file}")
                        st.rerun()

    st.markdown("---")
    if sidebar_collapsed:
        st.button("🚪", key="sb_c_logout", help="Logout", on_click=_do_logout, use_container_width=True)
    else:
        st.button("🚪 Logout", use_container_width=True, on_click=_do_logout)

# -----------------------------------------------------------------------------
# 6b. Centered Hero Header + Top Navigation Bar:
#     [menu] [navigation] [universal search] [force refresh] [profile]
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero-header">
        <div class="hero-logo">{brand_logo_img(112)}</div>
        <div class="hero-title">e-Rin <span class="gradient-text">Recovery Dashboard</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

NAV_DASH = "📊 EMI Recovery Dashboard"
NAV_EDIT = "📝 Live Recovery Data"
NAV_AGENTS = "👤 Credit Recovery Executive"
# Role-based panels:
#   Admin      -> Dashboard + Live Recovery Data + Credit Recovery Executive
#   Supervisor -> Dashboard + Live Recovery Data (view-only)
#   Agent      -> Live Recovery Data only (own rows)
if st.session_state.role == ROLE_ADMIN:
    nav_options = [NAV_DASH, NAV_EDIT, NAV_AGENTS]
elif st.session_state.role == ROLE_SUPERVISOR:
    nav_options = [NAV_DASH, NAV_EDIT]
else:
    nav_options = [NAV_EDIT]
if st.session_state.get("main_nav") not in nav_options:
    st.session_state["main_nav"] = nav_options[0]

tb_menu, tb_nav, tb_search, tb_refresh, tb_profile = st.columns([0.55, 4.7, 3.2, 1.6, 2.4])
with tb_menu:
    st.button("☰", key="sidebar_toggle", on_click=_toggle_sidebar, help="Collapse / expand sidebar", use_container_width=True)
with tb_nav:
    st.radio("Navigation", nav_options, horizontal=True, label_visibility="collapsed", key="main_nav")
with tb_search:
    search_query = st.text_input(
        "🔍 Universal Search across entire dataset (Names, Phone, Account, Remarks, Dates, Officer):",
        placeholder="Search names, phone, account, remarks, dates, officer…",
        key="universal_search_bar",
        label_visibility="collapsed"
    ).strip()
with tb_refresh:
    # on_click runs the refresh before the rerun, so no extra st.rerun() pass is needed
    st.button("🔄 Force Refresh", type="secondary", use_container_width=True, on_click=_sync_refresh_sheet)
with tb_profile:
    _pc_name = html.escape(str(st.session_state.display_name or ""))
    _pc_initial = html.escape(str(st.session_state.display_name or "U")[:1].upper())
    _pc_role = html.escape(str(st.session_state.role or "").capitalize())
    st.markdown(
        f"""
        <div class="profile-chip topbar-marker">
            <div class="pc-avatar">{_pc_initial}</div>
            <div><div class="pc-name">{_pc_name}</div><span class="pc-role">{_pc_role}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

if not selected_file:
    st.info("Please upload a CSV or Excel file to begin.")
    st.stop()

current_file_path = os.path.join(DATA_DIR, selected_file)
current_mtime = os.path.getmtime(current_file_path) if os.path.exists(current_file_path) else 0

if "last_known_mtime" not in st.session_state:
    st.session_state["last_known_mtime"] = current_mtime
    st.session_state["editor_version"] = 0

if current_mtime > st.session_state["last_known_mtime"]:
    st.session_state["last_known_mtime"] = current_mtime
    st.session_state["editor_version"] = 0

raw_df = load_live_file(current_file_path)
detected_cols = detect_operational_columns(raw_df)

# One-time fallback for work sheets that were already present before this feature.
capture_initial_emi_collection(current_file_path, selected_file)

rec_date_col = detected_cols['recovery_call_date']
follow_up_col = detected_cols['follow_up_date']
assign_col = detected_cols['assign_person']
emi_col = detected_cols['emi_status']
lock_col = detected_cols['lock_status']
loan_col = detected_cols['loan_status']
remarks_col = detected_cols['remarks']

# Synchronize call ledger with current file state
ledger_df = get_synced_call_ledger(raw_df, selected_file, current_file_path, assign_col, rec_date_col, follow_up_col)

def apply_universal_search(df_to_filter, query):
    if not query:
        return df_to_filter
    mask = df_to_filter.astype(str).apply(
        lambda col: col.str.contains(query, case=False, na=False)
    ).any(axis=1)
    return df_to_filter[mask]

# -----------------------------------------------------------------------------
# 7. View Routing (driven by the top navigation bar)
# -----------------------------------------------------------------------------
active_page = st.session_state["main_nav"]
if st.session_state.role == ROLE_ADMIN:
    tab_dash = st.container() if active_page == NAV_DASH else None
    tab_editor = st.container() if active_page == NAV_EDIT else None
    tab_agents = st.container() if active_page == NAV_AGENTS else None
elif st.session_state.role == ROLE_SUPERVISOR:
    # Supervisor panel: Dashboard + Live Recovery Data only (account management is never routed)
    tab_dash = st.container() if active_page == NAV_DASH else None
    tab_editor = st.container() if active_page == NAV_EDIT else None
    tab_agents = None
else:
    tab_editor = st.container()
    tab_dash = None
    tab_agents = None

# =============================================================================
# PAGE 1: EMI RECOVERY DASHBOARD (ADMIN + SUPERVISOR)
# =============================================================================
if tab_dash is not None:
    with tab_dash:
        st.markdown(
            """
          
            """,
            unsafe_allow_html=True
        )
        selected_history_view = st.selectbox(
            "📅 Historical Dashboard Date:",
            ["Live Current Data"]
        )

        df_source = raw_df.copy()

        # -------------------------------------------------------------
        # Total EMI Collection Summary Box
        # Initial EMI Collection is saved once per uploaded file.
        # Total EMI Collection remains dynamic; Recovery is the difference.
        # -------------------------------------------------------------
        if "Monthly EMI Amount" in df_source.columns:
            emi_number_series = df_source[emi_col].apply(extract_emi_number)
            emi_amount_series = df_source["Monthly EMI Amount"].apply(clean_emi_amount)
            total_emi_collection = float((emi_number_series * emi_amount_series).sum())

            initial_collections = load_initial_emi_collections()
            initial_emi_collection = float(
                initial_collections.get(selected_file, total_emi_collection)
            )
            recovery_emi_collection = total_emi_collection - initial_emi_collection

            recovery_color = "#f87171" if recovery_emi_collection < 0 else "#6FA0FF"
            recovery_note = (
                "Below initial baseline"
                if recovery_emi_collection < 0
                else "Additional collection"
            )

            emi_html = f"""
            <div class="emi-summary-wrapper">
                <div class="emi-summary-heading">
                    <div>
                        <div class="emi-summary-title">💰 EMI Collection Overview</div>
                    </div>
                </div>

                <div class="emi-summary-grid">
                    <div class="emi-summary-card emi-initial">
                        <div class="emi-card-top">
                            <div class="emi-card-icon">📌</div>
                            <div class="emi-card-label">Initial EMI Collection</div>
                        </div>
                        <div class="emi-card-amount">
                            ৳{format_bdt_currency(initial_emi_collection)}
                        </div>
                    </div>

                    <div class="emi-summary-card emi-total">
                        <div class="emi-card-top">
                            <div class="emi-card-icon">💵</div>
                            <div class="emi-card-label">Total EMI Collection</div>
                        </div>
                        <div class="emi-card-amount">
                            ৳{format_bdt_currency(total_emi_collection)}
                        </div>
                    </div>

                    <div class="emi-summary-card emi-recovery">
                        <div class="emi-card-top">
                            <div class="emi-card-icon">📈</div>
                            <div class="emi-card-label">Recovery EMI Collection</div>
                        </div>
                        <div class="emi-card-amount" style="color: {recovery_color};">
                            ৳{format_bdt_currency(recovery_emi_collection)}
                        </div>
                        <div class="emi-card-note">{recovery_note}</div>
                    </div>
                </div>

                <div class="emi-summary-footer">
                    <span>📊 Collection = EMI Status × Monthly EMI Amount</span>
                </div>
            </div>
            """

            st.html(emi_html)

        else:
            st.warning(
                "⚠️ 'Monthly EMI Amount' column not found in this file — "
                "Total EMI Collection cannot be calculated."
            )

        df_m = apply_universal_search(df_source, search_query)
        df_m["Clean Follow Date"] = df_m[follow_up_col].apply(to_clean_date)
        df_m["Clean Rec Date"] = df_m[rec_date_col].apply(to_clean_date)

        df_m["Active Scheduled Date"] = df_m["Clean Follow Date"].combine_first(df_m["Clean Rec Date"])

        total_cases = len(df_m)
        scheduled_calls = df_m["Active Scheduled Date"].notna().sum()
        remaining_calls = total_cases - scheduled_calls

        target_emi = ["3 EMI Paid", "4 EMI Paid", "5 EMI Paid", "6 EMI Paid",
                      "3 emi paid", "4 emi paid", "5 emi paid", "6 emi paid"]
        late_stage_count = df_m[emi_col].isin(target_emi).sum()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">📦 Total Device Portfolio</div>
                    <div class="kpi-value">{total_cases:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">📞 Scheduled Calls</div>
                    <div class="kpi-value" style="color: #6FA0FF;">{scheduled_calls:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">⏳ Pending / Unscheduled Calls</div>
                    <div class="kpi-value" style="color: #FF9A2E;">{remaining_calls:,}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
    f"""
    <div class="kpi-card">
        <div class="kpi-label">🔥 3–6 EMI Paid</div>
        <div class="kpi-value" style="color: #00ff00;">{late_stage_count:,}</div>
    </div>
    """,
    unsafe_allow_html=True
)

        st.markdown("<br>", unsafe_allow_html=True)

        ordered_emi = ["0 EMI Paid", "1 EMI Paid", "2 EMI Paid", "3 EMI Paid", "4 EMI Paid", "5 EMI Paid", "6 EMI Paid"]
        emi_counts = df_m[emi_col].value_counts().reindex(ordered_emi, fill_value=0)

        cards_html = "".join([
            f"""
            <div class="emi-card" style="border-left: 4px solid {EMI_COLOR_MAP.get(lbl, '#3498db')};">
                <div class="emi-tag" style="color: {EMI_COLOR_MAP.get(lbl, '#3498db')};">
                    <span>●</span> {lbl}
                </div>
                <div class="emi-num">{emi_counts[lbl]:,}</div>
            </div>
            """ for lbl in ordered_emi
        ])

        # st.markdown(
        #     f"""
        #     <div class="drawer-wrapper">
        #         <div class="drawer-trigger">
        #             <span class="circle-icon">⚡</span>
        #             <span>EMI Breakdown (0–6) ➔</span>
        #         </div>
        #         <div class="drawer-content">
        #             <div class="emi-card-grid">
        #                 {cards_html}
                    
                
        #     """,
        #     unsafe_allow_html=True
        # )

        st.subheader("📊 Recovery EMI Status")
        chart_categories = ["Total Devices"] + ordered_emi
        chart_values = [total_cases] + [emi_counts[k] for k in ordered_emi]
        chart_df = pd.DataFrame({
            "Category": chart_categories,
            "Count": chart_values
        })

        fig_bar = px.bar(
            chart_df,
            x="Category",
            y="Count",
            text="Count",
            color="Category",
            color_discrete_map=EMI_COLOR_MAP
        )
        fig_bar.update_traces(
            textposition="outside",
            marker=dict(line=dict(width=0))
        )
        fig_bar.update_layout(
            xaxis_title="Number of EMI Paid",
            yaxis_title="Number of Customers",
            height=390,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#C7D2EE"),
            xaxis=dict(
                title=dict(
                    text="Number of EMI Paid",
                    standoff=30
                ),
                gridcolor="rgba(255,255,255,0.05)"
            ),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # -------------------------------------------------------------
        # MERGED: Officer Daily Call Summary (Today's Call + Follow-Up = Total)
        # -------------------------------------------------------------
        st.markdown(
            """
            <div class="schedule-container-card">
                <h3 style="margin-top: 0; color: #F4F7FF; display: flex; align-items: center; gap: 8px;">
                    📊 Daily Recovery Call Summary
                </h3>
                <p style="color: #A9B6D3; font-size: 0.85rem; margin-bottom: 5px;">
                    Recovery Call + Follow-Up Call = Total Calls
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not ledger_df.empty:
            pivot_ledger = ledger_df.copy()
            pivot_ledger["Officer"] = pivot_ledger["Officer"].fillna("").astype(str).str.strip()
            pivot_ledger["Call_Type"] = pivot_ledger["Call_Type"].fillna("").astype(str).str.strip()
            pivot_ledger["Action_Date"] = pd.to_datetime(
                pivot_ledger["Action_Date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

            pivot_ledger = pivot_ledger[
                pivot_ledger["Officer"].ne("")
                & ~pivot_ledger["Officer"].str.lower().isin(["nan", "none", "unassigned"])
                & pivot_ledger["Action_Date"].notna()
                & pivot_ledger["Call_Type"].isin(["Recovery Call", "Follow Up Call"])
            ].copy()
        else:
            pivot_ledger = pd.DataFrame()

        if not pivot_ledger.empty:
            counts = (
                pivot_ledger
                .groupby(["Action_Date", "Officer", "Call_Type"])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )

            if "Recovery Call" not in counts.columns:
                counts["Recovery Call"] = 0
            if "Follow Up Call" not in counts.columns:
                counts["Follow Up Call"] = 0

            counts["Total"] = counts["Recovery Call"] + counts["Follow Up Call"]
            counts["Cell_Text"] = counts.apply(
                lambda r: f"{int(r['Recovery Call'])}+{int(r['Follow Up Call'])}={int(r['Total'])}",
                axis=1
            )

            all_officers = sorted(counts["Officer"].unique())

            pivot_table = (
                counts.pivot(index="Action_Date", columns="Officer", values="Cell_Text")
                .reindex(columns=all_officers)
                .fillna("0+0=0")
                .reset_index()
            )

            pivot_table["_sort_date"] = pd.to_datetime(pivot_table["Action_Date"], errors="coerce")
            pivot_table = pivot_table.sort_values("_sort_date")
            pivot_table["Date"] = pivot_table["_sort_date"].dt.strftime("%d %B %Y")
            pivot_table = pivot_table.drop(columns=["Action_Date", "_sort_date"])

            cols_order = ["Date"] + all_officers
            pivot_table = pivot_table[cols_order]

            # Per-officer cumulative total row (matches image format: "Total = N")
            officer_totals = counts.groupby("Officer")["Total"].sum()
            totals_row = {"Date": ""}
            for off in all_officers:
                totals_row[off] = f"Total = {int(officer_totals.get(off, 0))}"

            final_table = pd.concat([pivot_table, pd.DataFrame([totals_row])], ignore_index=True)

            st.dataframe(
                final_table,
                use_container_width=True,
                height=480,
                hide_index=True
            )
        else:
            st.info("No call activity has been recorded yet.")

# =============================================================================
# PAGE 2: LIVE RECOVERY DATA - SPREADSHEET EDITOR
#   Admin: full editing | Agent: own rows, limited columns | Supervisor: view-only
# =============================================================================
if tab_editor is not None:
  with tab_editor:
    st.markdown(
        f"""
        <div class="app-header-banner">
            <div class="app-header-logo">📝</div>
            <div>
                <p class="app-header-title">Interactive Sheet <span class="gradient-text">Editor</span></p>
                <p class="app-header-sub">{selected_file}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Admin Structural Controls (Add Row, Add Column, Rename Column, Delete Column)
    if st.session_state.role == ROLE_ADMIN:
        with st.expander("🛠️ Spreadsheet Structure Controls", expanded=False):
            col_add_r, col_add_c, col_ren_c, col_del_c = st.columns(4)
            with col_add_r:
                st.markdown("##### ➕ Add Empty Row")
                if st.button("Insert Row to Table", use_container_width=True):
                    _require_roles(ROLE_ADMIN)
                    new_empty_row = {c: "" for c in raw_df.columns}
                    new_empty_row[emi_col] = "0 EMI Paid"
                    new_empty_row[lock_col] = "Unlocked"
                    new_empty_row[assign_col] = "Unassigned"
                    raw_df = pd.concat([raw_df, pd.DataFrame([new_empty_row])], ignore_index=True)
                    atomic_save_file(raw_df, current_file_path)
                    st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
                    st.success("New row appended to bottom.")
                    st.rerun()

            with col_add_c:
                st.markdown("##### ➕ Add Custom Column")
                with st.form("add_col_form"):
                    new_col_name = st.text_input("New Column Header Name").strip()
                    submitted_col = st.form_submit_button("Create Column", use_container_width=True)
                    if submitted_col and new_col_name:
                        _require_roles(ROLE_ADMIN)
                        if new_col_name not in raw_df.columns:
                            raw_df[new_col_name] = ""
                            atomic_save_file(raw_df, current_file_path)
                            st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
                            st.success(f"Column '{new_col_name}' created!")
                            st.rerun()
                        else:
                            st.warning("Column already exists.")

            with col_ren_c:
                st.markdown("##### ✏️ Rename Column")
                with st.form("rename_col_form"):
                    target_col = st.selectbox("Select Column to Rename", options=list(raw_df.columns))
                    renamed_label = st.text_input("Enter New Header Name").strip()
                    submitted_rename = st.form_submit_button("Rename Header", use_container_width=True)
                    if submitted_rename and renamed_label:
                        _require_roles(ROLE_ADMIN)
                        raw_df = raw_df.rename(columns={target_col: renamed_label})
                        atomic_save_file(raw_df, current_file_path)
                        st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
                        st.success(f"Renamed '{target_col}' to '{renamed_label}'.")
                        st.rerun()

            with col_del_c:
                st.markdown("##### 🗑️ Delete Column")
                with st.form("delete_col_form"):
                    col_to_delete = st.selectbox("Select Column to Remove", options=list(raw_df.columns), key="del_col_select")
                    submitted_delete = st.form_submit_button("Delete Column", type="secondary", use_container_width=True)
                    if submitted_delete and col_to_delete:
                        _require_roles(ROLE_ADMIN)
                        if len(raw_df.columns) <= 1:
                            st.error("Cannot delete the only column in the table.")
                        else:
                            raw_df = raw_df.drop(columns=[col_to_delete])
                            atomic_save_file(raw_df, current_file_path)
                            st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
                            st.success(f"Column '{col_to_delete}' deleted successfully!")
                            st.rerun()

    working_df = apply_universal_search(raw_df.copy(), search_query)

    if st.session_state.role == ROLE_AGENT:
        active_agent = st.session_state.agent_name
        agent_mask = working_df[assign_col].fillna("").astype(str).str.strip().str.lower() == active_agent.strip().lower()
        editable_view = working_df[agent_mask].copy()
    else:
        # Admin and Supervisor both see every row (Supervisor is read-only, enforced below)
        editable_view = working_df.copy()

    if st.session_state.role == ROLE_AGENT and editable_view.empty:
        st.info(f"ℹ️ No accounts are currently assigned to **{st.session_state.agent_name}** in this worksheet.")
        st.stop()

    display_df = editable_view.copy()

    for d_col in [rec_date_col, follow_up_col]:
        if d_col in display_df.columns:
            display_df[d_col] = pd.to_datetime(
                display_df[d_col].apply(to_clean_date),
                errors="coerce"
            )

    if emi_col in display_df.columns:
        display_df[emi_col] = display_df[emi_col].apply(to_dropdown_emi)

    for c in display_df.columns:
        if c not in [rec_date_col, follow_up_col, emi_col, lock_col]:
            display_df[c] = display_df[c].fillna("").astype(str)

    # -------------------------------------------------------------------------
    # Requirement 1: Interactive Excel-Like Sorting (Dates, Numbers, Strings)
    # -------------------------------------------------------------------------
    st.markdown('<div class="sort-toolbar-card">', unsafe_allow_html=True)
    s_col1, s_col2 = st.columns([2.5, 1.5])
    with s_col1:
        sort_column = st.selectbox(
            "↕️ Excel-Like Sort By Column:",
            options=["-- Original Sheet Order --"] + list(display_df.columns),
            key=f"sort_col_{selected_file}"
        )
    with s_col2:
        sort_direction = st.selectbox(
            "Sort Order:",
            options=["Ascending (A ➔ Z / 0 ➔ 9 / Oldest ➔ Newest)", "Descending (Z ➔ A / 9 ➔ 0 / Newest ➔ Oldest)"],
            key=f"sort_dir_{selected_file}"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    if sort_column != "-- Original Sheet Order --" and sort_column in display_df.columns:
        is_asc = sort_direction.startswith("Ascending")
        if sort_column in [rec_date_col, follow_up_col]:
            display_df = display_df.sort_values(by=sort_column, ascending=is_asc, na_position="last")
        else:
            cleaned_series = display_df[sort_column].astype(str).str.replace(",", "", regex=False).str.strip()
            numeric_series = pd.to_numeric(cleaned_series, errors="coerce")
            non_empty_count = (cleaned_series != "").sum()
            if non_empty_count > 0 and numeric_series.notna().sum() >= non_empty_count * 0.8:
                display_df = (
                    display_df.assign(_sort_key=numeric_series)
                    .sort_values(by="_sort_key", ascending=is_asc, na_position="last")
                    .drop(columns=["_sort_key"])
                )
            else:
                display_df = (
                    display_df.assign(_sort_key=display_df[sort_column].astype(str).str.lower())
                    .sort_values(by="_sort_key", ascending=is_asc, na_position="last")
                    .drop(columns=["_sort_key"])
                )

    # -------------------------------------------------------------------------
    # Requirement 3: Strict Column-Level Permissions (Admin: all | Agent: limited | Supervisor: none)
    # -------------------------------------------------------------------------
    allowed_agent_columns = {
        rec_date_col,
        follow_up_col,
        loan_col,
        emi_col,
        lock_col,
        remarks_col
    }

    is_supervisor_view = (st.session_state.role == ROLE_SUPERVISOR)

    column_config = {}
    for col in display_df.columns:
        if col in ["Last Modified By", "Last Updated At"]:
            is_disabled = True
        elif st.session_state.role == ROLE_ADMIN:
            is_disabled = False
        elif is_supervisor_view:
            is_disabled = True
        else:
            is_disabled = col not in allowed_agent_columns

        if col in [rec_date_col, follow_up_col]:
            column_config[col] = st.column_config.DateColumn(
                col,
                format="D MMMM YYYY",
                width="medium",
                disabled=is_disabled
            )
        elif col == emi_col:
            column_config[col] = st.column_config.SelectboxColumn(
                col,
                width="medium",
                options=DISPLAY_EMI_OPTIONS,
                required=False,
                disabled=is_disabled
            )
        elif col == lock_col:
            column_config[col] = st.column_config.SelectboxColumn(
                col,
                width="small",
                options=["Locked", "Unlocked", ""],
                required=False,
                disabled=is_disabled
            )
        else:
            column_config[col] = st.column_config.TextColumn(
                col,
                disabled=is_disabled,
                width="medium"
            )

    editor_key = f"editor_grid_{selected_file}_{st.session_state.get('editor_version', 0)}"

    edited_df = st.data_editor(
        display_df,
        column_config=column_config,
        use_container_width=True,
        num_rows="dynamic" if st.session_state.role == ROLE_ADMIN else "fixed",
        height=580,
        key=editor_key,
        disabled=is_supervisor_view
    )

    if st.session_state.role == ROLE_SUPERVISOR:
        # Supervisors never get a Save button - the grid above is fully read-only.
        st.info("👁️ View-only access: Supervisors can view, search and sort the data, but cannot edit, add, delete or save any changes.")
    elif st.button("💾 Save Changes", type="primary", use_container_width=True):
        # Backend permission gate (a Supervisor can never reach the save logic)
        _require_roles(ROLE_ADMIN, ROLE_AGENT)

        active_user = st.session_state.get("agent_name", st.session_state.username)
        current_timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

        if st.session_state.role == ROLE_AGENT:
            unauthorized_mask = edited_df[assign_col].fillna("").astype(str).str.strip().str.lower() != active_user.strip().lower()
            if unauthorized_mask.any():
                st.error("⛔ Security Exception: You cannot edit records assigned to other officers.")
                st.stop()

        formatted_edited = edited_df.copy()
        for d_col in [rec_date_col, follow_up_col]:
            if d_col in formatted_edited.columns:
                formatted_edited[d_col] = formatted_edited[d_col].apply(date_to_string_format)
        if emi_col in formatted_edited.columns:
            formatted_edited[emi_col] = formatted_edited[emi_col].apply(from_dropdown_emi)

        for c in formatted_edited.columns:
            formatted_edited[c] = formatted_edited[c].fillna("").astype(str).str.strip()
            formatted_edited[c] = formatted_edited[c].replace({"nan": "", "None": "", "NaT": ""})

        existing_indices = [idx for idx in formatted_edited.index if idx in raw_df.index]
        new_indices = [idx for idx in formatted_edited.index if idx not in raw_df.index]

        orig_slice = raw_df.loc[existing_indices].copy()
        for d_col in [rec_date_col, follow_up_col]:
            if d_col in orig_slice.columns:
                orig_slice[d_col] = orig_slice[d_col].apply(date_to_string_format)

        orig_compare = orig_slice.drop(columns=["Last Modified By", "Last Updated At"], errors="ignore").fillna("").astype(str)
        edit_compare = formatted_edited.loc[existing_indices].drop(columns=["Last Modified By", "Last Updated At"], errors="ignore").fillna("").astype(str)

        changed_mask = (orig_compare != edit_compare).any(axis=1)
        changed_indices = list(orig_compare.index[changed_mask])

        row_deleted = (st.session_state.role == ROLE_ADMIN) and (not search_query) and (len(existing_indices) < len(raw_df))

        if changed_indices or new_indices or row_deleted:
            if changed_indices:
                formatted_edited.loc[changed_indices, "Last Modified By"] = active_user
                formatted_edited.loc[changed_indices, "Last Updated At"] = current_timestamp
                record_edited_call_activities(
                    selected_file,
                    orig_slice,
                    formatted_edited.loc[existing_indices],
                    changed_indices,
                    active_user,
                    assign_col,
                    rec_date_col,
                    follow_up_col
                )

            if new_indices:
                formatted_edited.loc[new_indices, "Last Modified By"] = active_user
                formatted_edited.loc[new_indices, "Last Updated At"] = current_timestamp

            merged_master = raw_df.copy()
            for col in merged_master.columns:
                merged_master[col] = merged_master[col].astype(object)

            for col in formatted_edited.columns:
                merged_master.loc[existing_indices, col] = formatted_edited.loc[existing_indices, col]

            if row_deleted:
                merged_master = merged_master.loc[existing_indices].copy()

            if new_indices:
                merged_master = pd.concat([merged_master, formatted_edited.loc[new_indices]], ignore_index=True)

            save_daily_history_snapshot(merged_master, selected_file)
            atomic_save_file(merged_master, current_file_path)

            st.session_state["editor_version"] = st.session_state.get("editor_version", 0) + 1
            st.session_state["last_known_mtime"] = os.path.getmtime(current_file_path)

            total_mod = len(changed_indices) + len(new_indices)
            st.success(f"✅ Saved! {total_mod} record(s) dynamically updated and audited under **{active_user}**.")
        else:
            st.success("✅ Saved successfully! No changes detected.")
        st.rerun()

# =============================================================================
# PAGE 3: CREDIT RECOVERY EXECUTIVE - USER ACCOUNT MANAGEMENT (ADMIN ONLY)
# =============================================================================
if tab_agents is not None:
    # Backend permission gate: only Admin can ever see or use account management
    _require_roles(ROLE_ADMIN)
    with tab_agents:
        st.markdown(
            """
            <div class="app-header-banner">
                <div class="app-header-logo">🧑‍💼</div>
                <div>
                    <p class="app-header-title">User Account <span class="gradient-text">Management</span></p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        accounts = load_accounts()

        st.markdown("### ➕ <span class='gradient-text'>Create New User</span>", unsafe_allow_html=True)
        with st.form("create_agent_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            with cc1:
                new_username = st.text_input("Login Username (unique)").strip().lower()
                new_display_name = st.text_input("Display Name (shown in sidebar)").strip()
                new_role_label = st.selectbox("Role", options=list(ROLE_OPTIONS_MAP.keys()), index=0)
            with cc2:
                new_agent_name = st.text_input(
                    "Assign Person Name",
                    help="Required for the Agent role: must exactly match the name used in the 'Assign Person' column of the worksheet. Not needed for Supervisor / Admin."
                ).strip()
                new_password = st.text_input("Set Password", type="password")

            create_submit = st.form_submit_button("✅ Create User Account", use_container_width=True, type="primary")

            if create_submit:
                _require_roles(ROLE_ADMIN)
                new_role = ROLE_OPTIONS_MAP.get(new_role_label, ROLE_AGENT)
                if not new_username or not new_display_name or not new_password:
                    st.error("Username, Display Name and Password are required.")
                elif new_role == ROLE_AGENT and not new_agent_name:
                    st.error("Assign Person Name is required for the Agent role.")
                elif new_username in accounts:
                    st.error(f"Username '{new_username}' already exists.")
                else:
                    hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    accounts[new_username] = {
                        "name": new_display_name,
                        "agent_name": new_agent_name or new_display_name,
                        "role": new_role,
                        "hashed_pw": hashed_pw,
                        "active": True
                    }
                    save_accounts(accounts)
                    st.success(f"{ROLE_DISPLAY_LABELS[new_role]} account '{new_display_name}' created successfully.")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 📋 <span class='gradient-text'>Existing User Accounts</span>", unsafe_allow_html=True)

        # The primary admin account ("saiful") is protected and never listed for editing
        managed_usernames = [u for u in accounts.keys() if u != "saiful"]

        if not managed_usernames:
            st.info("No other user accounts exist yet. Create one above to get started.")
        else:
            for uname in sorted(managed_usernames):
                rec = accounts[uname]
                is_active = rec.get("active", True)
                status_label = "🟢 Active" if is_active else "🔴 Deactivated"
                rec_role = str(rec.get("role", ROLE_AGENT)).strip().lower()
                role_label = ROLE_DISPLAY_LABELS.get(rec_role, rec_role.capitalize())
                is_own_account = (uname == st.session_state.username)

                with st.expander(f"{rec.get('name', uname)}  —  ({uname})  —  {role_label}  —  {status_label}", expanded=False):
                    info_col, action_col, pw_col = st.columns([1.2, 1, 1.3])

                    with info_col:
                        st.markdown(f"**Username:** `{uname}`")
                        st.markdown(f"**Role:** {role_label}")
                        st.markdown(f"**Assign Person Name:** `{rec.get('agent_name', '')}`")
                        st.markdown(f"**Status:** {status_label}")

                    with action_col:
                        if is_own_account:
                            st.caption("🔒 This is your own account. It cannot be deactivated, deleted or have its role changed here.")
                        else:
                            toggle_label = "🔴 Deactivate" if is_active else "🟢 Activate"
                            if st.button(toggle_label, key=f"toggle_{uname}", use_container_width=True):
                                _require_roles(ROLE_ADMIN)
                                accounts[uname]["active"] = not is_active
                                save_accounts(accounts)
                                new_state = "Activated" if not is_active else "Deactivated"
                                st.success(f"{rec.get('name', uname)} is now {new_state}.")
                                st.rerun()

                            if st.button("🗑️ Delete User", key=f"delete_{uname}", type="secondary", use_container_width=True):
                                _require_roles(ROLE_ADMIN)
                                del accounts[uname]
                                save_accounts(accounts)
                                st.warning(f"User account '{rec.get('name', uname)}' deleted.")
                                st.rerun()

                            with st.form(f"role_form_{uname}"):
                                _role_keys = list(ROLE_OPTIONS_MAP.keys())
                                _cur_role_idx = _role_keys.index(role_label) if role_label in _role_keys else 0
                                chosen_role_label = st.selectbox("Change Role", options=_role_keys, index=_cur_role_idx, key=f"role_sel_{uname}")
                                role_submit = st.form_submit_button("🔁 Update Role", use_container_width=True)
                                if role_submit:
                                    _require_roles(ROLE_ADMIN)
                                    chosen_role = ROLE_OPTIONS_MAP.get(chosen_role_label, ROLE_AGENT)
                                    accounts[uname]["role"] = chosen_role
                                    if chosen_role == ROLE_AGENT and not str(accounts[uname].get("agent_name", "")).strip():
                                        accounts[uname]["agent_name"] = accounts[uname].get("name", uname)
                                    save_accounts(accounts)
                                    st.success(f"{rec.get('name', uname)} is now a {ROLE_DISPLAY_LABELS[chosen_role]}.")
                                    st.rerun()

                    with pw_col:
                        with st.form(f"pw_form_{uname}", clear_on_submit=True):
                            new_pw_val = st.text_input("Set New Password", type="password", key=f"newpw_input_{uname}")
                            pw_submit = st.form_submit_button("🔑 Update Password", use_container_width=True)
                            if pw_submit:
                                _require_roles(ROLE_ADMIN)
                                if not new_pw_val:
                                    st.error("Password cannot be blank.")
                                else:
                                    new_hash = bcrypt.hashpw(new_pw_val.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                                    accounts[uname]["hashed_pw"] = new_hash
                                    save_accounts(accounts)
                                    st.success(f"Password updated for {rec.get('name', uname)}.")
                                    st.rerun()