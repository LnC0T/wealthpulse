import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import json
import os
import requests
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import secrets
import html
import tempfile
import time
import re
import difflib
import math
import calendar
import locale
import textwrap
import sys
from collections import Counter
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import smtplib
import ssl

# Try to import plotly, fallback to None if not available
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly not installed. Using native Streamlit charts. Run: pip install plotly")

# Optional auto-refresh component
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except Exception:
    AUTOREFRESH_AVAILABLE = False

# ==============================
# MODERN CONFIG & STYLING (DARK MODE)
# ==============================
st.set_page_config(
    page_title="WealthPulse | Portfolio Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="W"
)

# Custom CSS for dark glassmorphism design
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Serif:wght@400;500;600&display=swap');

        :root {
            --bg: #0b1220;
            --bg-alt: #0f172a;
            --surface: #111827;
            --surface-2: #0f172a;
            --accent: #d1a843;
            --accent-2: #f2c66d;
            --text: #e5e7eb;
            --muted: #9aa4b2;
            --border: rgba(148, 163, 184, 0.18);
            --font-scale: 0.95;
            --input-bg: #0b1324;
            --tab-active-bg: #0b1324;
            --card-bg: #0f172a;
            --pill-bg: #1f2937;
            --pill-border: rgba(255,255,255,0.08);
            --pill-text: #e5e7eb;
            --pill-gold-bg: rgba(44, 33, 12, 0.9);
            --pill-gold-text: #f4d58d;
            --pill-warning-bg: rgba(48, 27, 8, 0.9);
            --pill-success-bg: rgba(9, 43, 26, 0.9);
            --pill-warning-text: #f5d0a3;
            --pill-success-text: #b3f5d3;
            --price-tag-bg: rgba(8, 12, 22, 0.92);
            --price-tag-text: #f3d58f;
            --sticky-bg: rgba(11, 18, 32, 0.95);
        }

        * {
            font-family: 'IBM Plex Sans', sans-serif;
            letter-spacing: 0.1px;
        }

        label, .stSelectbox label, .stRadio label, .stSlider label,
        .stTextInput label, .stNumberInput label, .stTextArea label, .stCheckbox label {
            color: var(--text) !important;
        }

        [data-testid="stCheckbox"] span,
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] p {
            color: var(--text) !important;
        }

        [data-testid="stCheckbox"] svg {
            fill: var(--text) !important;
        }

        [data-testid="stRadio"] span,
        [data-testid="stRadio"] label,
        [data-testid="stRadio"] p {
            color: var(--text) !important;
        }

        [data-testid="stRadio"] svg {
            fill: var(--text) !important;
        }

        div[data-testid="stRadio"] span,
        div[data-testid="stRadio"] label span {
            color: var(--text) !important;
        }

        html {
            font-size: calc(16px * var(--font-scale));
        }

        .stApp {
            background:
                radial-gradient(1200px 600px at 10% -20%, var(--bg-alt) 0%, var(--bg) 55%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-alt) 100%);
            background-attachment: fixed;
        }

        .wp-header-bar {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 1rem;
            padding: 0.25rem 0.25rem 0.75rem;
        }

        .wp-logo-wrap {
            position: relative;
            display: inline-block;
        }

        .wp-header-logo {
            height: 110px;
            width: auto;
            max-width: 100%;
            filter: drop-shadow(0 12px 20px rgba(0,0,0,0.25));
        }

        .wp-header-logo.large {
            height: 140px;
        }

        .wp-footer {
            text-align: center;
            margin: 2.5rem 0 1.5rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: var(--muted);
            font-size: 0.85rem;
        }

        .wp-login-wrap {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.2rem;
        }

        .wp-login-logo {
            height: 220px;
            width: auto;
            max-width: 90%;
            filter: drop-shadow(0 18px 28px rgba(0,0,0,0.35));
            animation: wpGoldPulse 1.8s ease-out infinite;
        }

        .wp-header-text {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }

        .wp-header-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text);
            letter-spacing: 0.4px;
        }

        .wp-header-subtitle {
            font-size: 0.95rem;
            color: var(--muted);
            letter-spacing: 0.2px;
        }

        .wp-header-logo.pulse {
            animation: wpGoldPulse 1.7s ease-out 1;
        }

        .wp-logo-shimmer {
            pointer-events: none;
            position: absolute;
            top: 0;
            left: -140%;
            width: 240%;
            height: 100%;
            background: linear-gradient(120deg,
                rgba(255,255,255,0.0) 0%,
                rgba(255,246,196,0.0) 35%,
                rgba(255,255,255,0.55) 48%,
                rgba(255,252,224,0.85) 52%,
                rgba(255,246,196,0.35) 60%,
                rgba(255,255,255,0.0) 100%
            );
            mix-blend-mode: screen;
            filter: blur(0.5px);
            animation: wpShimmer 3.4s linear infinite;
        }

        @keyframes wpGoldPulse {
            0% {
                transform: scale(0.96);
                filter: drop-shadow(0 0 0 rgba(247, 206, 91, 0.0));
                opacity: 0.75;
            }
            50% {
                transform: scale(1.03);
                filter: drop-shadow(0 0 28px rgba(247, 206, 91, 0.85));
                opacity: 1;
            }
            100% {
                transform: scale(1);
                filter: drop-shadow(0 12px 20px rgba(0,0,0,0.25));
                opacity: 1;
            }
        }

        @keyframes wpShimmer {
            0% { transform: translateX(0); opacity: 0.0; }
            10% { opacity: 0.6; }
            50% { opacity: 0.95; }
            90% { opacity: 0.6; }
            100% { transform: translateX(55%); opacity: 0.0; }
        }

        
        .wp-plan-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            background: rgba(255, 214, 92, 0.18);
            color: #f5d982;
            border: 1px solid rgba(255, 214, 92, 0.35);
            letter-spacing: 0.3px;
        }

        .wp-plan-badge.light {
            background: rgba(15, 26, 51, 0.08);
            color: #1d2b4f;
            border: 1px solid rgba(15, 26, 51, 0.2);
        }

        .wp-plan-sub {
            font-size: 0.72rem;
            color: var(--muted);
            margin-top: 0.2rem;
        }

        .wp-founder-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            background: rgba(255, 214, 92, 0.2);
            color: #f6dc8a;
            border: 1px solid rgba(255, 214, 92, 0.4);
            letter-spacing: 0.4px;
            text-transform: uppercase;
        }

        .wp-founder-badge.light {
            background: rgba(15, 26, 51, 0.08);
            color: #1d2b4f;
            border: 1px solid rgba(15, 26, 51, 0.2);
        }

        .wp-stripe-link {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.6rem 1rem;
            border-radius: 10px;
            background: var(--surface-2);
            border: 1px solid var(--border);
            color: var(--text);
            font-weight: 600;
            text-decoration: none;
            gap: 0.45rem;
            box-shadow: 0 10px 18px rgba(0,0,0,0.15);
        }

        .wp-stripe-link:hover {
            opacity: 0.9;
        }
@media (max-width: 900px) {
            .wp-header-logo {
                height: 80px;
            }

            .wp-header-logo.large {
                height: 96px;
            }
        }

        .main > div {
            background: var(--surface);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.35rem;
            border: 1px solid var(--border);
            box-shadow: 0 6px 18px rgba(0,0,0,0.18);
            color: var(--text);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            font-family: 'IBM Plex Serif', serif;
            text-shadow: none;
            letter-spacing: 0.2px;
        }

        h1 { font-size: 1.9rem !important; }
        h2 { font-size: 1.35rem !important; }
        h3 { font-size: 1.1rem !important; }

        .stCaption {
            color: var(--muted) !important;
        }

        .stMarkdown p,
        .stMarkdown span,
        .stMarkdown div,
        .stMarkdown li {
            color: var(--text);
        }

        .stMarkdown a {
            color: var(--accent);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: var(--surface-2);
            border-radius: 10px;
            padding: 4px;
            border: 1px solid var(--border);
        }

        .stTabs [data-baseweb="tab"] {
            height: 36px;
            border-radius: 8px;
            padding: 6px 12px;
            color: var(--muted);
            font-weight: 500;
            font-size: 0.85rem;
            background: transparent;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }

        .stTabs [aria-selected="true"] {
            background: var(--tab-active-bg);
            border: 1px solid rgba(209,168,67,0.45);
            color: var(--text) !important;
            box-shadow: none;
        }

        .stMetric {
            background: var(--surface-2);
            border-radius: 10px;
            padding: 10px;
            border: 1px solid var(--border);
            box-shadow: none;
        }

        .stMetric label {
            color: var(--muted) !important;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .stMetric div {
            color: var(--text) !important;
            font-size: 1.35rem;
            font-weight: 700;
        }

        .stButton > button {
            background: var(--surface-2);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.45rem 1rem;
            font-weight: 600;
            box-shadow: none;
            transition: transform 0.15s ease, border-color 0.15s ease;
            height: 36px;
        }

        .stButton > button[kind="primary"] {
            background: var(--accent);
            border-color: rgba(209,168,67,0.6);
            color: #0b1220;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(209,168,67,0.6);
        }

        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea,
        [data-baseweb="select"] input {
            background: var(--input-bg) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
        }

        div[data-baseweb="select"] > div {
            background: var(--input-bg) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] svg {
            color: var(--text) !important;
            fill: var(--text) !important;
        }

        div[data-baseweb="select"] [role="listbox"] {
            background: var(--surface) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
        }

        div[data-baseweb="select"] [role="option"] {
            color: var(--text) !important;
        }

        div[data-baseweb="select"] [role="option"]:hover {
            background: var(--surface-2) !important;
        }

        div[data-testid="stFileUploader"] section {
            background: var(--input-bg) !important;
            color: var(--text) !important;
            border: 1px dashed var(--border) !important;
        }

        div[data-testid="stFileUploader"] section span,
        div[data-testid="stFileUploader"] section small,
        div[data-testid="stFileUploader"] section p {
            color: var(--text) !important;
        }

        div[data-testid="stAlert"] {
            border: 1px solid var(--border) !important;
            background: var(--surface-2) !important;
            color: var(--text) !important;
        }

        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid="stAlert"] div {
            color: var(--text) !important;
        }

        .asset-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 0.85rem;
            margin: 0.4rem 0;
            border: 1px solid var(--border);
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }

        .asset-card:hover {
            transform: translateY(-2px);
            border-color: rgba(209,168,67,0.35);
        }

        .list-card {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            background: var(--card-bg);
            border-radius: 12px;
            padding: 0.6rem 0.9rem;
            margin: 0.35rem 0;
            border: 1px solid var(--border);
            box-shadow: none;
            transition: all 0.15s ease;
        }

        .list-card:hover {
            transform: translateY(-1px);
            border-color: rgba(209,168,67,0.35);
        }

        .list-thumb {
            width: 56px;
            height: 56px;
            border-radius: 10px;
            object-fit: cover;
            background: rgba(0,0,0,0.25);
        }

        .list-body {
            flex: 1;
            min-width: 0;
        }

        .list-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.15rem;
        }

        .list-meta {
            font-size: 0.75rem;
            color: var(--muted);
        }

        .list-value {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
            text-align: right;
            min-width: 100px;
        }

        @media (max-width: 900px) {
            .list-card {
                flex-direction: column;
                align-items: flex-start;
            }

            .list-value {
                text-align: left;
            }
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #0b1220;
            background: #cdd5df;
        }

        .badge-gold { background: #d1a843; color: #0b1220; }
        .badge-copper { background: #b87333; color: #0b1220; }
        .badge-collectible { background: #d9c7a1; color: #1f2937; }
        .badge-guitar { background: #f3b46b; color: #1f2937; }
        .badge-card { background: #93c5fd; color: #0b1220; }
        .badge-stock { background: #86efac; color: #0b1220; }
        .badge-other { background: #cbd5e1; color: #1f2937; }

        .stProgress > div > div > div {
            background: linear-gradient(90deg, #caa44c 0%, #f0cf7a 100%);
            border-radius: 10px;
        }

        div[data-testid="stExpander"] {
            background: var(--surface-2);
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: none;
        }

        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary span {
            color: var(--text) !important;
            font-weight: 600;
        }

        div[data-testid="stExpander"] svg {
            fill: var(--text) !important;
        }

        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] li,
        div[data-testid="stExpander"] div {
            color: var(--text);
        }

        div[data-testid="stExpander"] a {
            color: var(--accent);
        }

        .stForm {
            background: var(--surface-2);
            padding: 1.4rem;
            border-radius: 12px;
            box-shadow: none;
            border: 1px solid var(--border);
        }

        .chart-container {
            background: var(--surface-2);
            border-radius: 12px;
            padding: 1rem;
            margin: 0.6rem 0;
            border: 1px solid var(--border);
        }

        /* Hide Streamlit "Press Enter to apply" hints */
        div[data-testid="stTextInput"] small,
        div[data-testid="stNumberInput"] small,
        div[data-testid="stTextArea"] small {
            display: none !important;
        }

        .stFileUploader {
            background: var(--surface-2);
            border-radius: 10px;
            border: 1px dashed rgba(209,168,67,0.6);
            padding: 14px;
        }

        .stDataFrame {
            background: var(--surface-2);
            border-radius: 10px;
            border: 1px solid var(--border);
        }

        .confirmation-modal {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--surface-2);
            padding: 1.6rem;
            border-radius: 12px;
            z-index: 1001;
            border: 1px solid var(--border);
            box-shadow: 0 12px 40px rgba(0,0,0,0.5);
            min-width: 360px;
            display: none;
        }

        .confirmation-modal.active {
            display: block;
        }

        .modal-buttons {
            display: flex;
            gap: 0.75rem;
            margin-top: 1rem;
        }

        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 999;
            display: none;
        }

        .overlay.active {
            display: block;
        }

        .market-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 0.8rem;
        }

        .market-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 12px 30px rgba(0,0,0,0.35);
            color: var(--text);
        }

        .market-image {
            position: relative;
            height: 180px;
            background: var(--bg);
        }

        .market-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        .market-price-tag {
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: var(--price-tag-bg);
            color: var(--price-tag-text);
            padding: 6px 12px;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.9rem;
            border: 1px solid rgba(243, 213, 143, 0.35);
        }

        .market-body {
            padding: 12px 14px 14px 14px;
            color: var(--text);
        }

        .market-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
            margin: 0.35rem 0;
        }

        .market-meta {
            font-size: 0.8rem;
            color: var(--muted);
        }

        .market-badges {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .market-card * {
            color: inherit;
        }

        .market-meta {
            color: var(--muted) !important;
        }

        .market-pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            background: var(--pill-bg);
            color: var(--pill-text);
            border: 1px solid var(--pill-border);
        }

        .market-pill.gold {
            color: var(--pill-gold-text);
            border-color: rgba(244, 213, 141, 0.35);
            background: var(--pill-gold-bg);
        }

        .market-pill.success {
            color: var(--pill-success-text);
            border-color: rgba(179, 245, 211, 0.35);
            background: var(--pill-success-bg);
        }

        .market-pill.warning {
            color: var(--pill-warning-text);
            border-color: rgba(245, 208, 163, 0.35);
            background: var(--pill-warning-bg);
        }

        .market-actions {
            display: flex;
            gap: 8px;
            margin-top: 10px;
        }

        .sticky-filter-block {
            position: sticky;
            top: 0.5rem;
            z-index: 20;
            background: var(--sticky-bg);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 0.75rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.35);
            backdrop-filter: blur(8px);
            margin-bottom: 1rem;
            color: var(--text);
        }

        .community-badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin: 0.35rem 0 0.75rem 0;
        }

        .community-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text);
        }

        .community-badge.open {
            background: var(--pill-success-bg);
            color: var(--pill-success-text);
            border-color: rgba(179, 245, 211, 0.4);
        }

        .community-badge.secure {
            background: var(--pill-warning-bg);
            color: var(--pill-warning-text);
            border-color: rgba(245, 208, 163, 0.4);
        }

        .community-badge.unknown {
            background: var(--pill-bg);
            color: var(--pill-text);
        }

        .help-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin: 0.6rem 0 1rem 0;
        }

        .help-card {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px;
            min-height: 110px;
        }

        .help-card-title {
            font-weight: 700;
            color: var(--text);
            margin-bottom: 6px;
        }

        .help-card-body {
            color: var(--muted);
            font-size: 0.85rem;
            line-height: 1.4;
        }

        .help-pill {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            background: var(--pill-bg);
            color: var(--pill-text);
            border: 1px solid var(--pill-border);
        }

        div[data-testid="stDialog"] > div,
        div[role="dialog"] {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 14px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6) !important;
        }

        .gold-fx-container {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
        }
        .gold-fx {
            position: absolute;
            bottom: -40px;
            font-weight: 800;
            color: #f4c542;
            text-shadow: 0 2px 6px rgba(0,0,0,0.4);
            animation: gold-float 2.4s ease-in forwards;
        }
        .gold-bar {
            width: 26px;
            height: 14px;
            border-radius: 3px;
            background: linear-gradient(135deg, #fff1a8 0%, #f7c948 45%, #d19000 100%);
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }
        @keyframes gold-float {
            0% { transform: translateY(0) rotate(0deg); opacity: 1; }
            100% { transform: translateY(-120vh) rotate(25deg); opacity: 0; }
        }
    </style>
""", unsafe_allow_html=True)


DATA_FILE = os.path.join(os.path.dirname(__file__), "wealth_data.json")
REMEMBER_FILE = os.path.join(os.path.dirname(__file__), "remember_me.json")
PASSWORD_ITERATIONS = 200_000
MIN_PASSWORD_LENGTH = 8
ADMIN_DEFAULT_TOKEN = "admin1!!!"
REMEMBER_TOKEN_TTL_DAYS = 30
LOGIN_MAX_ATTEMPTS = 5
LOGIN_FAILURE_WINDOW_MINUTES = 15
LOGIN_LOCKOUT_MINUTES = 15
SUPABASE_TIMEOUT = 10
APP_STORAGE_TABLE = "wealthpulse_users"

SECURITY_QUESTIONS = [
    "What is your mother's maiden name?",
    "What was your first car?",
    "What is the name of your first pet?",
    "What city were you born in?",
    "What was the name of your primary school?",
    "What is your favorite movie?",
    "What is your favorite book?",
    "What is your favorite food?",
    "What was your childhood nickname?",
    "What street did you grow up on?"
]

COUNTRY_CURRENCY = {
    "US": "USD",
    "NZ": "NZD",
    "AU": "AUD",
    "CA": "CAD",
    "GB": "GBP",
    "IE": "EUR",
    "FR": "EUR",
    "DE": "EUR",
    "ES": "EUR",
    "IT": "EUR",
    "NL": "EUR",
    "BE": "EUR",
    "CH": "CHF",
    "JP": "JPY",
    "CN": "CNY",
    "HK": "HKD",
    "SG": "SGD",
    "IN": "INR",
    "ZA": "ZAR",
    "BR": "BRL",
    "MX": "MXN",
    "SE": "SEK",
    "NO": "NOK",
    "DK": "DKK",
    "AE": "AED",
    "SA": "SAR",
    "KR": "KRW"
}

COUNTRY_NAMES = {
    "US": "United States",
    "NZ": "New Zealand",
    "AU": "Australia",
    "GB": "United Kingdom",
    "CA": "Canada",
    "IE": "Ireland",
    "FR": "France",
    "DE": "Germany",
    "ES": "Spain",
    "IT": "Italy",
    "NL": "Netherlands",
    "BE": "Belgium",
    "CH": "Switzerland",
    "JP": "Japan",
    "CN": "China",
    "HK": "Hong Kong",
    "SG": "Singapore",
    "IN": "India",
    "ZA": "South Africa",
    "BR": "Brazil",
    "MX": "Mexico",
    "SE": "Sweden",
    "NO": "Norway",
    "DK": "Denmark",
    "AE": "United Arab Emirates",
    "SA": "Saudi Arabia",
    "KR": "South Korea",
    "PT": "Portugal",
    "AT": "Austria",
    "FI": "Finland",
    "PL": "Poland",
    "CZ": "Czech Republic",
    "HU": "Hungary",
    "RO": "Romania",
    "BG": "Bulgaria",
    "GR": "Greece",
    "TR": "Turkey",
    "IL": "Israel",
    "EG": "Egypt",
    "KE": "Kenya",
    "NG": "Nigeria",
    "AR": "Argentina",
    "CL": "Chile",
    "CO": "Colombia",
    "MY": "Malaysia",
    "PH": "Philippines",
    "TH": "Thailand",
    "VN": "Vietnam",
    "ID": "Indonesia"
}

CURRENCY_SYMBOLS = {
    "USD": "$",
    "NZD": "NZ$",
    "AUD": "A$",
    "CAD": "C$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CNY": "¥",
    "HKD": "HK$",
    "SGD": "S$",
    "CHF": "CHF ",
    "INR": "₹",
    "KRW": "₩",
    "ZAR": "R ",
    "BRL": "R$",
    "MXN": "$",
    "SEK": "kr ",
    "NOK": "kr ",
    "DKK": "kr ",
    "AED": "د.إ ",
    "SAR": "ر.س "
}

CURRENCY_LIST = [
    ("USD", "US Dollar"),
    ("EUR", "Euro"),
    ("GBP", "British Pound"),
    ("JPY", "Japanese Yen"),
    ("CNY", "Chinese Yuan"),
    ("NZD", "New Zealand Dollar"),
    ("AUD", "Australian Dollar"),
    ("CAD", "Canadian Dollar"),
    ("CHF", "Swiss Franc"),
    ("HKD", "Hong Kong Dollar"),
    ("SGD", "Singapore Dollar"),
    ("INR", "Indian Rupee"),
    ("KRW", "South Korean Won"),
    ("ZAR", "South African Rand"),
    ("BRL", "Brazilian Real"),
    ("MXN", "Mexican Peso"),
    ("SEK", "Swedish Krona"),
    ("NOK", "Norwegian Krone"),
    ("DKK", "Danish Krone"),
    ("AED", "UAE Dirham"),
    ("SAR", "Saudi Riyal"),
    ("ARS", "Argentine Peso"),
    ("BDT", "Bangladeshi Taka"),
    ("BGN", "Bulgarian Lev"),
    ("BHD", "Bahraini Dinar"),
    ("BND", "Brunei Dollar"),
    ("BOB", "Bolivian Boliviano"),
    ("CLP", "Chilean Peso"),
    ("COP", "Colombian Peso"),
    ("CRC", "Costa Rican Colon"),
    ("CZK", "Czech Koruna"),
    ("DOP", "Dominican Peso"),
    ("EGP", "Egyptian Pound"),
    ("FJD", "Fijian Dollar"),
    ("GEL", "Georgian Lari"),
    ("GHS", "Ghanaian Cedi"),
    ("GTQ", "Guatemalan Quetzal"),
    ("HNL", "Honduran Lempira"),
    ("HRK", "Croatian Kuna"),
    ("HUF", "Hungarian Forint"),
    ("IDR", "Indonesian Rupiah"),
    ("ILS", "Israeli New Shekel"),
    ("JMD", "Jamaican Dollar"),
    ("JOD", "Jordanian Dinar"),
    ("KES", "Kenyan Shilling"),
    ("KWD", "Kuwaiti Dinar"),
    ("KZT", "Kazakhstani Tenge"),
    ("LBP", "Lebanese Pound"),
    ("LKR", "Sri Lankan Rupee"),
    ("MAD", "Moroccan Dirham"),
    ("MYR", "Malaysian Ringgit"),
    ("NGN", "Nigerian Naira"),
    ("NPR", "Nepalese Rupee"),
    ("OMR", "Omani Rial"),
    ("PEN", "Peruvian Sol"),
    ("PHP", "Philippine Peso"),
    ("PKR", "Pakistani Rupee"),
    ("PLN", "Polish Zloty"),
    ("QAR", "Qatari Riyal"),
    ("RON", "Romanian Leu"),
    ("RUB", "Russian Ruble"),
    ("SAR", "Saudi Riyal"),
    ("THB", "Thai Baht"),
    ("TRY", "Turkish Lira"),
    ("TWD", "New Taiwan Dollar"),
    ("UAH", "Ukrainian Hryvnia"),
    ("UGX", "Ugandan Shilling"),
    ("UYU", "Uruguayan Peso"),
    ("VEF", "Venezuelan Bolivar"),
    ("VND", "Vietnamese Dong"),
    ("XOF", "West African CFA Franc"),
    ("XAF", "Central African CFA Franc"),
    ("XPF", "CFP Franc"),
    ("ISK", "Icelandic Krona"),
    ("ALL", "Albanian Lek"),
    ("AMD", "Armenian Dram"),
    ("ANG", "Netherlands Antillean Guilder"),
    ("AOA", "Angolan Kwanza"),
    ("AWG", "Aruban Florin"),
    ("AZN", "Azerbaijani Manat"),
    ("BAM", "Bosnia-Herzegovina Convertible Mark"),
    ("BBD", "Barbadian Dollar"),
    ("BIF", "Burundian Franc"),
    ("BMD", "Bermudian Dollar"),
    ("BWP", "Botswana Pula"),
    ("BYN", "Belarusian Ruble"),
    ("BZD", "Belize Dollar"),
    ("CDF", "Congolese Franc"),
    ("CUP", "Cuban Peso"),
    ("CVE", "Cape Verdean Escudo"),
    ("DJF", "Djiboutian Franc"),
    ("DZD", "Algerian Dinar"),
    ("ERN", "Eritrean Nakfa"),
    ("ETB", "Ethiopian Birr"),
    ("GIP", "Gibraltar Pound"),
    ("GMD", "Gambian Dalasi"),
    ("GNF", "Guinean Franc"),
    ("GYD", "Guyanese Dollar"),
    ("HTG", "Haitian Gourde"),
    ("IQD", "Iraqi Dinar"),
    ("IRR", "Iranian Rial"),
    ("JOD", "Jordanian Dinar"),
    ("KGS", "Kyrgyzstani Som"),
    ("KHR", "Cambodian Riel"),
    ("KMF", "Comorian Franc"),
    ("KYD", "Cayman Islands Dollar"),
    ("LAK", "Lao Kip"),
    ("LRD", "Liberian Dollar"),
    ("LSL", "Lesotho Loti"),
    ("LYD", "Libyan Dinar"),
    ("MDL", "Moldovan Leu"),
    ("MGA", "Malagasy Ariary"),
    ("MKD", "Macedonian Denar"),
    ("MMK", "Myanmar Kyat"),
    ("MNT", "Mongolian Tugrik"),
    ("MOP", "Macanese Pataca"),
    ("MRO", "Mauritanian Ouguiya"),
    ("MUR", "Mauritian Rupee"),
    ("MVR", "Maldivian Rufiyaa"),
    ("MWK", "Malawian Kwacha"),
    ("MZN", "Mozambican Metical"),
    ("NAD", "Namibian Dollar"),
    ("NIO", "Nicaraguan Cordoba"),
    ("PAB", "Panamanian Balboa"),
    ("PGK", "Papua New Guinean Kina"),
    ("PYG", "Paraguayan Guarani"),
    ("RSD", "Serbian Dinar"),
    ("RWF", "Rwandan Franc"),
    ("SBD", "Solomon Islands Dollar"),
    ("SCR", "Seychellois Rupee"),
    ("SDG", "Sudanese Pound"),
    ("SHP", "Saint Helena Pound"),
    ("SLL", "Sierra Leonean Leone"),
    ("SOS", "Somali Shilling"),
    ("SRD", "Surinamese Dollar"),
    ("SSP", "South Sudanese Pound"),
    ("STD", "Sao Tome and Principe Dobra"),
    ("SYP", "Syrian Pound"),
    ("SZL", "Swazi Lilangeni"),
    ("TJS", "Tajikistani Somoni"),
    ("TMT", "Turkmenistani Manat"),
    ("TND", "Tunisian Dinar"),
    ("TOP", "Tongan Paanga"),
    ("TTD", "Trinidad and Tobago Dollar"),
    ("TZS", "Tanzanian Shilling"),
    ("UZS", "Uzbekistani Som"),
    ("WST", "Samoan Tala"),
    ("XCD", "East Caribbean Dollar"),
    ("YER", "Yemeni Rial"),
    ("ZMW", "Zambian Kwacha"),
    ("ZWL", "Zimbabwean Dollar")
]

METAL_CODES = {
    "Gold": "XAU",
    "Silver": "XAG",
    "Platinum": "XPT",
    "Palladium": "XPD"
}

METAL_NAMES = {
    "XAU": "Gold",
    "XAG": "Silver",
    "XPT": "Platinum",
    "XPD": "Palladium"
}

BULLION_WIDGET_CURRENCIES = {
    "USD", "AED", "ARS", "AUD", "BHD", "BRL", "CAD", "CHF", "CNY", "COP",
    "DKK", "EGP", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JOD",
    "JPY", "KRW", "KWD", "LBP", "LTL", "LYD", "MKD", "MMK", "MOP", "MXN",
    "NGN", "NOK", "NPR", "NZD", "PHP", "PKR", "QAR", "RSD", "RUB", "SAR",
    "SEK", "SGD", "THB", "TRY", "TWD", "VND", "ZAR"
}

ASSET_TYPE_OPTIONS = [
    "Cash",
    "Bank Account",
    "Stock",
    "ETF",
    "Mutual Fund",
    "Bond",
    "Crypto",
    "Retirement Account",
    "Insurance Policy",
    "Real Estate",
    "Business",
    "Intellectual Property",
    "Vehicle",
    "Motorcycle",
    "Boat",
    "RV",
    "Jewelry",
    "Watch",
    "Art",
    "Collectible",
    "Coins",
    "Stamps",
    "Trading Cards",
    "Comics",
    "Memorabilia",
    "Luxury Handbags",
    "Rare Books",
    "Wine & Spirits",
    "Card",
    "Guitar",
    "Electronics",
    "Camera",
    "Equipment",
    "Appliance",
    "Furniture",
    "Gold",
    "Silver",
    "Platinum",
    "Palladium",
    "Copper",
    "Other"
]

COMMUNITY_CATEGORY_OPTIONS = [
    "Other",
    "Bullion > Gold Coins",
    "Bullion > Gold Proof Coins",
    "Bullion > Gold Fractional Coins",
    "Bullion > Gold Bars",
    "Bullion > Gold Kilobars",
    "Bullion > Gold Rounds",
    "Bullion > Gold Nuggets",
    "Bullion > Gold Shot/Grain",
    "Bullion > Silver Coins",
    "Bullion > Silver Proof Coins",
    "Bullion > Silver Fractional Coins",
    "Bullion > Silver Bars",
    "Bullion > Silver Kilobars",
    "Bullion > Silver Rounds",
    "Bullion > Silver Shot/Grain",
    "Bullion > Platinum Coins",
    "Bullion > Platinum Bars",
    "Bullion > Palladium Coins",
    "Bullion > Palladium Bars",
    "Bullion > Copper Rounds",
    "Bullion > Proof Coins",
    "Bullion > Bullets/Shot",
    "Bullion > Mixed Lots",
    "Coins & Paper Money > Gold Coins",
    "Coins & Paper Money > Silver Coins",
    "Coins & Paper Money > Platinum/Palladium",
    "Coins & Paper Money > Ancient Coins",
    "Coins & Paper Money > World Coins",
    "Coins & Paper Money > US Coins",
    "Coins & Paper Money > Proof Coins",
    "Coins & Paper Money > Mint Sets",
    "Coins & Paper Money > Commemoratives",
    "Coins & Paper Money > Bullion Coins",
    "Coins & Paper Money > Graded Coins",
    "Coins & Paper Money > Rare Banknotes",
    "Coins & Paper Money > World Banknotes",
    "Coins & Paper Money > Gold/Silver Certificates",
    "Coins & Paper Money > Error Coins",
    "Coins & Paper Money > Proof Sets",
    "Coins & Paper Money > Coin Lots",
    "Coins & Paper Money > Tokens/Medals",
    "Coins & Paper Money > Bullion (Other)",
    "Jewelry & Watches > Fine Jewelry",
    "Jewelry & Watches > Gold Jewelry",
    "Jewelry & Watches > Silver Jewelry",
    "Jewelry & Watches > Platinum Jewelry",
    "Jewelry & Watches > Diamond Jewelry",
    "Jewelry & Watches > Gemstone Jewelry",
    "Jewelry & Watches > Vintage/Antique Jewelry",
    "Jewelry & Watches > Luxury Watches",
    "Jewelry & Watches > Vintage Watches",
    "Jewelry & Watches > Limited Edition Watches",
    "Jewelry & Watches > Pocket Watches",
    "Jewelry & Watches > Watch Parts & Accessories",
    "Jewelry & Watches > Estate Jewelry",
    "Jewelry & Watches > Designer Jewelry",
    "Trading Cards > Sports (Baseball)",
    "Trading Cards > Sports (Basketball)",
    "Trading Cards > Sports (Football)",
    "Trading Cards > Sports (Soccer)",
    "Trading Cards > Sports (Hockey)",
    "Trading Cards > Sports (Golf)",
    "Trading Cards > Sports (Racing)",
    "Trading Cards > Collectible Card Games (Pokémon)",
    "Trading Cards > Collectible Card Games (Magic)",
    "Trading Cards > Collectible Card Games (Yu-Gi-Oh!)",
    "Trading Cards > Collectible Card Games (One Piece)",
    "Trading Cards > Collectible Card Games (Dragon Ball)",
    "Trading Cards > Singles",
    "Trading Cards > Rookie Cards",
    "Trading Cards > Autographed Cards",
    "Trading Cards > Memorabilia Cards",
    "Trading Cards > Lots",
    "Trading Cards > Complete Sets",
    "Trading Cards > Sealed Packs",
    "Trading Cards > Sealed Boxes",
    "Trading Cards > Sealed Cases",
    "Trading Cards > Comic Cards (Marvel/DC/X-Men)",
    "Trading Cards > Graded Cards",
    "Trading Cards > Non-Sport",
    "Trading Cards > Vintage",
    "Trading Cards > Promo Cards",
    "Trading Cards > Inserts/Parallels",
    "Stamps > United States",
    "Stamps > Great Britain",
    "Stamps > Canada",
    "Stamps > Australia",
    "Stamps > Europe",
    "Stamps > Asia",
    "Stamps > Worldwide",
    "Stamps > Rare Stamps",
    "Stamps > Stamp Collections",
    "Stamps > Postal History",
    "Stamps > Thematics",
    "Stamps > Errors/Varieties",
    "Stamps > First Day Covers",
    "Collectibles > Autographs",
    "Collectibles > Celebrity Autographs",
    "Collectibles > Sports Autographs",
    "Collectibles > Sports Memorabilia",
    "Collectibles > Music Memorabilia",
    "Collectibles > Movie/TV Memorabilia",
    "Collectibles > Comics",
    "Collectibles > Vintage Comics",
    "Collectibles > Graded Comics",
    "Collectibles > Comic Art",
    "Collectibles > Original Comic Art",
    "Collectibles > Vintage Toys",
    "Collectibles > Model Trains",
    "Collectibles > Diecast Models",
    "Collectibles > Figurines",
    "Collectibles > Vintage Advertising",
    "Collectibles > Movie Props",
    "Art > Paintings",
    "Art > Prints & Lithographs",
    "Art > Sculpture",
    "Art > Photography",
    "Art > Limited Editions",
    "Art > Contemporary",
    "Art > Modern",
    "Antiques > Furniture",
    "Antiques > Silverware",
    "Antiques > Decorative Arts",
    "Antiques > Clocks",
    "Antiques > Porcelain/Ceramics",
    "Antiques > Rugs/Tapestries",
    "Luxury > Designer Handbags",
    "Luxury > Designer Accessories",
    "Luxury > Eyewear",
    "Luxury > Fine Leather Goods",
    "Luxury > Jewelry",
    "Luxury > Watches",
    "Musical Instruments > Guitars",
    "Musical Instruments > Guitar Pedals",
    "Musical Instruments > Vintage Guitars",
    "Musical Instruments > Basses",
    "Musical Instruments > Violins/Strings",
    "Musical Instruments > Brass/Woodwinds",
    "Musical Instruments > Pro Audio",
    "Musical Instruments > Synthesizers",
    "Musical Instruments > Drum Kits",
    "Cameras & Photo > Vintage Cameras",
    "Cameras & Photo > Lenses",
    "Cameras & Photo > Medium Format",
    "Cameras & Photo > Film Equipment",
    "Cameras & Photo > Leica",
    "Cameras & Photo > Hasselblad",
    "Electronics > High-End Audio",
    "Electronics > Vintage Audio",
    "Electronics > Hi-Fi Components",
    "Electronics > Turntables",
    "Vehicles > Classic Cars",
    "Vehicles > Supercars",
    "Vehicles > Motorcycles",
    "Vehicles > Boats",
    "Vehicles > Collector Car Parts",
    "Wine & Spirits > Rare Whisky",
    "Wine & Spirits > Fine Wine",
    "Wine & Spirits > Cognac",
    "Wine & Spirits > Champagne",
    "Wine & Spirits > Investment Collections"
]

COMMUNITY_POSTS_EXTRA_COLUMNS = {
    "reserve_amount": "numeric",
    "buy_now_price": "numeric",
    "images": "jsonb",
    "owner_id": "uuid",
    "grading_company": "text",
    "grading_grade": "text"
}

COMMUNITY_RULES = [
    "No explicit or sexual content (images or text).",
    "No hate, threats, or harassment.",
    "No scams, illegal items, or regulated weapons.",
    "No personal info in listings (phone numbers, addresses, emails)."
]

COMMUNITY_PROFANITY_TERMS = {
    "fuck", "shit", "bitch", "asshole", "bastard", "dick", "piss", "cunt"
}

COMMUNITY_EXPLICIT_TERMS = {
    "porn", "xxx", "nude", "nudes", "nsfw", "sex", "sexual", "explicit", "erotic"
}

COMMUNITY_RESTRICTED_TERMS = {
    "cocaine", "heroin", "meth", "methamphetamine", "ecstasy", "mdma", "fentanyl",
    "gun", "firearm", "rifle", "pistol", "explosive", "ammo", "ammunition"
}

COMMUNITY_IMAGE_FILENAME_BLOCKLIST = COMMUNITY_EXPLICIT_TERMS | {"adult"}

MAX_LISTING_IMAGES = 5
MAX_LISTING_IMAGE_MB = 4
MAX_LISTING_IMAGE_TOTAL_MB = 15

COIN_GRADING_COMPANIES = ["PCGS", "NGC", "ANACS", "ICG", "Other"]
CARD_GRADING_COMPANIES = ["PSA", "BGS", "SGC", "CGC", "CSG", "Other"]
COIN_GRADE_OPTIONS = [
    "Ungraded",
    "MS/PF 70",
    "MS/PF 69",
    "MS/PF 68",
    "MS/PF 67",
    "MS/PF 66",
    "MS/PF 65",
    "MS/PF 64",
    "MS/PF 63",
    "MS/PF 62",
    "MS/PF 61",
    "MS/PF 60",
    "AU 58",
    "AU 55",
    "XF 45",
    "VF 30",
    "F 12",
    "G 4",
    "AG 3",
    "Fair 2",
    "Poor 1"
]
CARD_GRADE_OPTIONS = [
    "Ungraded",
    "Gem Mint 10",
    "Mint 9",
    "NM-MT 8",
    "Near Mint 7",
    "Excellent 5-6",
    "Very Good 3-4",
    "Good 2",
    "Poor 1"
]

def grading_type_for_category(category):
    text = str(category or "").lower()
    if "coin" in text or "bullion" in text or "paper money" in text:
        return "coin"
    if "trading card" in text or "card" in text or "comic" in text:
        return "card"
    return None

def filter_category_options(categories, query):
    if not query:
        return categories
    query = query.strip().lower()
    if not query:
        return categories
    filtered = [c for c in categories if query in str(c).lower()]
    return filtered if filtered else categories

BULLION_TYPES = {"Gold", "Silver", "Copper", "Platinum", "Palladium"}

WEIGHT_UNITS = {
    "Troy Ounces": "toz",
    "Grams": "g"
}

DATE_FORMATS = {
    "MMM D, YYYY": "%b %d, %Y",
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y"
}

TIMEZONE_OPTIONS = [
    "Local",
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Asia/Singapore",
    "Asia/Tokyo",
    "Australia/Sydney",
    "Pacific/Auckland"
]

DASHBOARD_PANELS = [
    "Total Wealth Card",
    "Market Snippets",
    "Live Metals",
    "Top Movers",
    "Stock News",
    "Asset Allocation",
    "Condition Breakdown"
]

WEALTH_RISK_PROFILES = [
    "Conservative",
    "Balanced",
    "Growth",
    "Aggressive"
]

WEALTH_LIQUIDITY_OPTIONS = [
    "Immediate (0-1y)",
    "Medium (1-5y)",
    "Long (5y+)",
    "Illiquid"
]

ENTITY_TYPES = ["Person", "Trust", "Company", "Joint", "Other"]
LIABILITY_TYPES = ["Mortgage", "Loan", "Credit Card", "HELOC", "Student Loan", "Other"]

DEFAULT_SETTINGS = {
    "currency_code": None,
    "currency_symbol": None,
    "currency_rate": 1.0,
    "auto_fx_enabled": False,
    "auto_refresh_enabled": True,
    "auto_refresh_interval": 70,
    "metal_weight_unit": "toz",
    "date_format": "MMM D, YYYY",
    "timezone": "Local",
    "default_asset_type": "Other",
    "default_condition": "Excellent",
    "default_view_mode": "Grid",
    "privacy_mode": False,
    "dashboard_panels": ["Total Wealth Card", "Market Snippets", "Live Metals", "Stock News"],
    "notifications_enabled": False,
    "notification_threshold_pct": 5.0,
    "metal_history_days": 30,
    "use_live_metal_price": True,
    "metalprice_api_key": "",
    "freegoldprice_api_key": "",
    "metals_dev_api_key": "",
    "news_api_key": "",
    "news_provider": "None",
    "metals_provider": "SilverPrice",
    "fx_provider": "Frankfurter",
    "rss_backup_enabled": True,
    "rss_feed_url": "https://news.google.com/rss/search?q=stock%20market&hl=en-US&gl=US&ceid=US:en",
    "ebay_client_id": "",
    "ebay_client_secret": "",
    "reverb_api_token": "",
    "wealth_target_net_worth": 0.0,
    "wealth_target_date": "",
    "wealth_risk_profile": "Balanced",
    "wealth_horizon_years": 10,
    "wealth_rebalance_tolerance": 5.0,
    "wealth_target_allocations": {},
    "wealth_advisor_notes": "",
    "onboarding_completed": False,
    "event_include_reminders": True,
    "event_reminder_days": 30,
    "ui_theme": "Dark Gold",
    "ui_font_scale": 0.95,
    "market_watchlist": [],
    "market_saved_searches": [],
    "market_alerts_enabled": True,
    "market_alerts_interval": 180,
    "market_alerts_email_enabled": False,
    "market_alerts_push_enabled": False,
    "market_alert_email": "",
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_password": "",
    "smtp_use_tls": True,
    "country_override": "",
    "supabase_url": "",
    "supabase_anon_key": "",
    "supabase_service_key": "",
    "supabase_use_service_role": False,
    "supabase_auth_required": False,
    "storage_provider": "Local",
    "community_policy_mode": "unknown",
    "subscription_plan": "Starter",
    "subscription_status": "active",
    "subscription_renews": "",
    "subscription_source": "Local",
    "stripe_customer_portal_url": ""
}

SUBSCRIPTION_PLANS = ["Starter", "Pro", "Elite", "Founder"]
PLAN_ORDER = {name: idx for idx, name in enumerate(SUBSCRIPTION_PLANS)}
PLAN_DESCRIPTIONS = {
    "Starter": "Core portfolio tracking and basic dashboards.",
    "Pro": "Advanced analytics, wealth plan, and business owner tools.",
    "Elite": "Community market, alerts, and premium insights.",
    "Founder": "All Elite features plus early access and founder perks."
}
PLAN_PRICING = {
    "Starter": "$6–9/mo",
    "Pro": "$12–20/mo",
    "Elite": "$25–40/mo",
    "Founder": "Founding Member"
}

# ==============================
# SECURITY & AUTH HELPERS
# ==============================
def escape_html(value):
    return html.escape(str(value)) if value is not None else ""

def normalize_plan(plan):
    if not plan:
        return "Starter"
    plan = str(plan).strip().title()
    if plan.startswith("Found"):
        return "Founder"
    if plan not in PLAN_ORDER:
        return "Starter"
    return plan

def plan_rank(plan):
    return PLAN_ORDER.get(normalize_plan(plan), 0)

def has_plan_at_least(settings, required_plan):
    current_plan = normalize_plan((settings or {}).get("subscription_plan"))
    return plan_rank(current_plan) >= plan_rank(required_plan)

def render_plan_gate(settings, required_plan, feature_name, detail="", key="plan_gate"):
    current_plan = normalize_plan((settings or {}).get("subscription_plan"))
    st.markdown(
        f"### {feature_name} (Locked)"
    )
    st.info(
        f"This feature is available on **{required_plan}+** plans. "
        f"You're currently on **{current_plan}**."
    )
    if detail:
        st.caption(detail)
    cols = st.columns([1, 2, 1])
    with cols[1]:
        if st.button("View Plans", key=key, width="stretch"):
            st.session_state.jump_to_settings = True
            st.rerun()

def is_founding_member(settings):
    return normalize_plan((settings or {}).get("subscription_plan")) == "Founder"

def render_founding_badge(settings):
    if not is_founding_member(settings):
        return
    light = is_light_theme(settings or {})
    badge_class = "wp-founder-badge light" if light else "wp-founder-badge"
    render_html_block(f"<div class='{badge_class}'>Founding Member</div>")

def get_resource_path(relative_path):
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)

@st.cache_data(show_spinner=False)
def load_asset_base64(relative_path):
    try:
        path = get_resource_path(relative_path)
        with open(path, "rb") as handle:
            return base64.b64encode(handle.read()).decode("utf-8")
    except Exception:
        return ""

def render_header_logo(show_pulse=False, settings=None):
    light_theme = is_light_theme(settings or {})
    pulse_class = " pulse" if show_pulse else ""
    shimmer_html = "<div class=\"wp-logo-shimmer\"></div>" if show_pulse else ""
    if light_theme:
        data = load_asset_base64(os.path.join("assets", "wealthpulse_header_1800.png"))
        if data:
            html_block = (
                '<div class="wp-header-bar">'
                '<div class="wp-logo-wrap">'
                f'<img class="wp-header-logo{pulse_class}" src="data:image/png;base64,{data}" alt="WealthPulse" />'
                f'{shimmer_html}'
                '</div></div>'
            )
            render_html_block(html_block)
            return
    data = load_asset_base64(os.path.join("assets", "wealthpulse_logo_transparent_glow.png"))
    if data:
        html_block = (
            '<div class="wp-header-bar">'
            '<div class="wp-logo-wrap">'
            f'<img class="wp-header-logo large{pulse_class}" src="data:image/png;base64,{data}" alt="WealthPulse" />'
            f'{shimmer_html}'
            '</div></div>'
        )
        render_html_block(html_block)
    else:
        render_html_block(
            "<div class='wp-header-bar'><h2 style='margin:0; color: var(--text);'>WealthPulse</h2></div>"
        )



def render_plan_badge(settings):
    plan = normalize_plan((settings or {}).get("subscription_plan"))
    status = (settings or {}).get("subscription_status", "active")
    renews = (settings or {}).get("subscription_renews", "")
    light = is_light_theme(settings or {})
    badge_class = "wp-plan-badge light" if light else "wp-plan-badge"
    status_text = status.upper() if status else "ACTIVE"
    subline = f"Status: {status_text}"
    if renews:
        subline = f"Status: {status_text} • Renews: {renews}"
    html_block = (
        '<div>'
        f'<div class="{badge_class}">Plan: {plan}</div>'
        f'<div class="wp-plan-sub">{subline}</div>'
        '</div>'
    )
    render_html_block(html_block)
def render_login_logo():
    data = load_asset_base64(os.path.join("assets", "wealthpulse_logo_transparent_glow.png"))
    if not data:
        return
    st.markdown(
        f"""
        <div class="wp-login-wrap">
            <div class="wp-logo-wrap">
                <img class="wp-login-logo" src="data:image/png;base64,{data}" alt="WealthPulse" />
                <div class="wp-logo-shimmer"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_footer():
    st.markdown(
        "<div class='wp-footer'>© L P Scott — ScottWebDesign</div>",
        unsafe_allow_html=True
    )

def apply_ui_theme(settings):
    theme = (settings.get("ui_theme") or "Dark Gold").strip()
    try:
        font_scale = float(settings.get("ui_font_scale", 0.95))
    except Exception:
        font_scale = 0.95

    if st.session_state.get("ui_live_preview"):
        theme = st.session_state.get("ui_theme_preview", theme)
        try:
            font_scale = float(st.session_state.get("ui_font_scale_preview", font_scale))
        except Exception:
            pass
    font_scale = max(0.85, min(1.1, font_scale))

    if theme.lower().startswith("light"):
        theme_vars = {
            "--bg": "#f7f8fb",
            "--bg-alt": "#ffffff",
            "--surface": "#ffffff",
            "--surface-2": "#f1f3f7",
            "--accent": "#b88b2a",
            "--accent-2": "#d9b45b",
            "--text": "#111827",
            "--muted": "#6b7280",
            "--border": "rgba(17, 24, 39, 0.12)",
            "--input-bg": "#ffffff",
            "--tab-active-bg": "#ffffff",
            "--card-bg": "#ffffff",
            "--pill-bg": "#eef2f7",
            "--pill-border": "rgba(15, 23, 42, 0.12)",
            "--pill-text": "#111827",
            "--pill-gold-bg": "#fff4d6",
            "--pill-gold-text": "#7a5a1d",
            "--pill-warning-bg": "#fff2e0",
            "--pill-success-bg": "#e7f8f0",
            "--pill-warning-text": "#7c2d12",
            "--pill-success-text": "#0f5132",
            "--price-tag-bg": "rgba(255, 255, 255, 0.92)",
            "--price-tag-text": "#7a5a1d",
            "--sticky-bg": "rgba(255, 255, 255, 0.96)"
        }
    else:
        theme_vars = {
            "--bg": "#0b1220",
            "--bg-alt": "#0f172a",
            "--surface": "#111827",
            "--surface-2": "#0f172a",
            "--accent": "#d1a843",
            "--accent-2": "#f2c66d",
            "--text": "#e5e7eb",
            "--muted": "#9aa4b2",
            "--border": "rgba(148, 163, 184, 0.18)",
            "--input-bg": "#0b1324",
            "--tab-active-bg": "#0b1324",
            "--card-bg": "#0f172a",
            "--pill-bg": "#1f2937",
            "--pill-border": "rgba(255,255,255,0.08)",
            "--pill-text": "#e5e7eb",
            "--pill-gold-bg": "rgba(44, 33, 12, 0.9)",
            "--pill-gold-text": "#f4d58d",
            "--pill-warning-bg": "rgba(48, 27, 8, 0.9)",
            "--pill-success-bg": "rgba(9, 43, 26, 0.9)",
            "--pill-warning-text": "#f5d0a3",
            "--pill-success-text": "#b3f5d3",
            "--price-tag-bg": "rgba(8, 12, 22, 0.92)",
            "--price-tag-text": "#f3d58f",
            "--sticky-bg": "rgba(11, 18, 32, 0.95)"
        }

    theme_vars["--font-scale"] = str(font_scale)

    vars_css = "\n".join([f"  {key}: {value};" for key, value in theme_vars.items()])
    st.markdown(f"""
        <style>
            :root {{
{vars_css}
            }}
            html {{
                font-size: calc(16px * var(--font-scale));
            }}
        </style>
    """, unsafe_allow_html=True)

def is_light_theme(settings):
    theme = (settings.get("ui_theme") or "").strip().lower()
    return theme.startswith("light")

def get_plotly_theme(settings):
    if is_light_theme(settings):
        return {
            "text": "#111827",
            "grid": "rgba(17, 24, 39, 0.12)",
            "legend_bg": "rgba(255,255,255,0.6)"
        }
    return {
        "text": "#f9fafb",
        "grid": "rgba(255,255,255,0.1)",
        "legend_bg": "rgba(0,0,0,0.3)"
    }

def get_secret_value(key, default=None):
    try:
        value = st.secrets.get(key, default)
    except Exception:
        value = default
    return value

def secret_flag(key, default=False):
    value = get_secret_value(key, default)
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

def resolve_setting(settings, setting_key, secret_key=None, default=""):
    secret_value = None
    if secret_key:
        secret_value = get_secret_value(secret_key)
    if secret_value not in (None, ""):
        return str(secret_value), True
    if not settings:
        return default, False
    return str(settings.get(setting_key, default) or ""), False

def get_effective_setting(settings, setting_key, secret_key=None, default=""):
    value, _ = resolve_setting(settings, setting_key, secret_key, default)
    return (value or "").strip()

def app_storage_provider(settings=None):
    secret_provider = get_secret_value("APP_STORAGE_PROVIDER")
    if secret_provider:
        return str(secret_provider)
    if secret_flag("SUPABASE_APP_STORAGE", False):
        return "Supabase"
    if settings:
        return settings.get("storage_provider", "Local")
    return "Local"

def app_storage_enabled(settings=None):
    provider = (app_storage_provider(settings) or "").lower()
    return provider.startswith("supabase")

RESERVED_USERNAMES = {"_meta"}

def validate_username(username):
    if not username:
        return "Username is required."
    if len(username) < 3 or len(username) > 32:
        return "Username must be 3-32 characters."
    if username.startswith("_") or username in RESERVED_USERNAMES:
        return "Username cannot start with '_' or use reserved names."
    if not re.match(r"^[A-Za-z0-9._-]+$", username):
        return "Username can only include letters, numbers, dot, underscore, or dash."
    return None

def validate_password_strength(password):
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password should include at least one letter and one number."
    return None

def make_password_record(secret):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS
    )
    return {
        "salt": salt.hex(),
        "hash": digest.hex(),
        "iterations": PASSWORD_ITERATIONS
    }

def verify_password(secret, record):
    if not record or "salt" not in record or "hash" not in record:
        return False
    iterations = record.get("iterations", PASSWORD_ITERATIONS)
    try:
        salt = bytes.fromhex(record["salt"])
    except ValueError:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        salt,
        int(iterations)
    ).hex()
    return secrets.compare_digest(digest, record.get("hash", ""))

def normalize_answer(answer):
    return " ".join((answer or "").strip().lower().split())

def create_recovery_record(question, answer):
    normalized = normalize_answer(answer)
    record = make_password_record(normalized)
    return {
        "question": question,
        "salt": record["salt"],
        "hash": record["hash"],
        "iterations": record["iterations"]
    }

def verify_recovery_answer(answer, record):
    if not record:
        return False
    normalized = normalize_answer(answer)
    return verify_password(normalized, record)

def ensure_user_record(db_obj, username):
    if username not in db_obj:
        db_obj[username] = {"portfolio": []}
    elif isinstance(db_obj[username], list):
        db_obj[username] = {"portfolio": db_obj[username]}
    elif not isinstance(db_obj[username], dict):
        db_obj[username] = {"portfolio": []}
    if "portfolio" not in db_obj[username]:
        db_obj[username]["portfolio"] = []
    if "settings" not in db_obj[username]:
        db_obj[username]["settings"] = {}
    if "entities" not in db_obj[username] or not isinstance(db_obj[username]["entities"], list):
        db_obj[username]["entities"] = []
    if not db_obj[username]["entities"]:
        db_obj[username]["entities"] = [{
            "id": secrets.token_hex(6),
            "name": "Personal",
            "type": "Person",
            "members": [username] if username else [],
            "notes": "",
            "created_at": datetime.now().isoformat()
        }]
    if "liabilities" not in db_obj[username] or not isinstance(db_obj[username]["liabilities"], list):
        db_obj[username]["liabilities"] = []
    return db_obj[username]

def iter_user_records(db_obj):
    for key, record in db_obj.items():
        if isinstance(key, str) and key.startswith("_"):
            continue
        if isinstance(record, dict):
            yield key, record

def get_meta(db_obj):
    meta = db_obj.get("_meta")
    if not isinstance(meta, dict):
        meta = {}
        db_obj["_meta"] = meta
    if "feedback" not in meta or not isinstance(meta["feedback"], list):
        meta["feedback"] = []
    if "revenue_total" not in meta:
        meta["revenue_total"] = 0.0
    if "install_first_seen" not in meta:
        meta["install_first_seen"] = datetime.now().isoformat()
    if "total_logins" not in meta:
        meta["total_logins"] = 0
    if "forum_posts" not in meta or not isinstance(meta["forum_posts"], list):
        meta["forum_posts"] = []
    if "community_config" not in meta or not isinstance(meta["community_config"], dict):
        meta["community_config"] = {}
    return meta

def get_community_settings(db_obj, user_settings=None):
    meta = get_meta(db_obj)
    config = meta.get("community_config") or {}
    source = user_settings or DEFAULT_SETTINGS
    if not config:
        config = {}
    config.setdefault("supabase_url", source.get("supabase_url", ""))
    config.setdefault("supabase_anon_key", source.get("supabase_anon_key", ""))
    config.setdefault("supabase_service_key", source.get("supabase_service_key", ""))
    config.setdefault("supabase_use_service_role", source.get("supabase_use_service_role", False))
    config.setdefault("storage_provider", source.get("storage_provider", "Local"))
    config.setdefault("supabase_auth_required", source.get("supabase_auth_required", False))
    secret_url, _ = resolve_setting(config, "supabase_url", "SUPABASE_URL")
    secret_anon, _ = resolve_setting(config, "supabase_anon_key", "SUPABASE_ANON_KEY")
    secret_service, _ = resolve_setting(config, "supabase_service_key", "SUPABASE_SERVICE_KEY")
    config["supabase_url"] = secret_url
    config["supabase_anon_key"] = secret_anon
    config["supabase_service_key"] = secret_service
    if secret_flag("SUPABASE_USE_SERVICE_ROLE", False):
        config["supabase_use_service_role"] = True
    return config

def get_forum_posts(db_obj):
    meta = get_meta(db_obj)
    posts = meta.get("forum_posts")
    if not isinstance(posts, list):
        posts = []
        meta["forum_posts"] = posts
    return posts

def record_login(db_obj, username):
    now = datetime.now().isoformat()
    record = ensure_user_record(db_obj, username)
    record["last_login"] = now
    record["last_active"] = now
    meta = get_meta(db_obj)
    meta["total_logins"] = int(meta.get("total_logins", 0)) + 1

def maybe_update_last_active(db_obj, username, min_interval_minutes=30):
    now = datetime.now()
    last_ping = st.session_state.get("last_active_ping")
    if last_ping and isinstance(last_ping, datetime):
        if (now - last_ping).total_seconds() < min_interval_minutes * 60:
            return False
    record = ensure_user_record(db_obj, username)
    record["last_active"] = now.isoformat()
    st.session_state.last_active_ping = now
    return True

def normalize_entity_name(name):
    return (name or "").strip()

def build_entity(name, entity_type, members=None, notes=""):
    return {
        "id": secrets.token_hex(6),
        "name": normalize_entity_name(name),
        "type": entity_type or "Other",
        "members": [m.strip() for m in (members or []) if m.strip()],
        "notes": notes or "",
        "created_at": datetime.now().isoformat()
    }

def get_entity_names(user_record):
    entities = user_record.get("entities", [])
    names = [e.get("name") for e in entities if e.get("name")]
    if not names:
        names = ["Personal"]
    return names

def update_entity_references(portfolio, liabilities, old_name, new_name):
    for asset in portfolio:
        wealth = asset.get("wealth", {})
        if wealth.get("owner_entity") == old_name:
            wealth["owner_entity"] = new_name
        split = wealth.get("ownership_split")
        if isinstance(split, dict) and old_name in split:
            split[new_name] = split.pop(old_name)
            wealth["ownership_split"] = split
        asset["wealth"] = wealth

    for liability in liabilities:
        if liability.get("owner_entity") == old_name:
            liability["owner_entity"] = new_name
        split = liability.get("ownership_split")
        if isinstance(split, dict) and old_name in split:
            split[new_name] = split.pop(old_name)
            liability["ownership_split"] = split

def get_entity_share(ownership_split, owner_entity, entity_name):
    if not entity_name or entity_name == "All":
        return 1.0
    if isinstance(ownership_split, dict) and ownership_split:
        try:
            return float(ownership_split.get(entity_name, 0.0)) / 100.0
        except Exception:
            return 0.0
    return 1.0 if owner_entity == entity_name else 0.0

def get_asset_share(asset, entity_name):
    wealth = asset.get("wealth", {})
    return get_entity_share(wealth.get("ownership_split"), wealth.get("owner_entity"), entity_name)

def get_liability_share(liability, entity_name):
    return get_entity_share(liability.get("ownership_split"), liability.get("owner_entity"), entity_name)

def get_total_assets_value(portfolio, entity_name="All"):
    total = 0.0
    for asset in portfolio:
        share = get_asset_share(asset, entity_name)
        if share <= 0:
            continue
        value, _, _ = ai_valuation(asset)
        total += value * share
    return total

def get_total_liabilities_value(liabilities, entity_name="All"):
    total = 0.0
    for liability in liabilities:
        try:
            balance = float(liability.get("balance", 0.0) or 0.0)
        except Exception:
            balance = 0.0
        share = get_liability_share(liability, entity_name)
        if share <= 0:
            continue
        total += balance * share
    return total

def build_portfolio_view_items(portfolio, entity_name="All"):
    items = []
    for idx, asset in enumerate(portfolio):
        share = get_asset_share(asset, entity_name)
        if entity_name == "All":
            share = 1.0
        if share > 0:
            items.append({"index": idx, "asset": asset, "share": share})
    return items

def estimate_monthly_payment(balance, annual_rate, term_months):
    try:
        balance = float(balance)
        term_months = int(term_months)
        if balance <= 0 or term_months <= 0:
            return None
        rate = float(annual_rate or 0.0) / 100.0 / 12.0
        if rate <= 0:
            return balance / term_months
        return balance * rate / (1 - math.pow(1 + rate, -term_months))
    except Exception:
        return None

def estimate_payoff_months(balance, annual_rate, payment):
    try:
        balance = float(balance)
        payment = float(payment)
        if balance <= 0 or payment <= 0:
            return None
        rate = float(annual_rate or 0.0) / 100.0 / 12.0
        if rate <= 0:
            return balance / payment
        if payment <= balance * rate:
            return None
        return -math.log(1 - rate * balance / payment) / math.log(1 + rate)
    except Exception:
        return None

def build_amortization_schedule(balance, annual_rate, payment=None, term_months=None, max_months=600):
    try:
        balance = float(balance)
    except Exception:
        return None, None
    if balance <= 0:
        return None, None
    try:
        rate = float(annual_rate or 0.0) / 100.0 / 12.0
    except Exception:
        rate = 0.0

    payment_value = None
    if payment is not None:
        try:
            payment_value = float(payment)
        except Exception:
            payment_value = None

    term_value = None
    if term_months:
        try:
            term_value = int(term_months)
        except Exception:
            term_value = None

    if (payment_value is None or payment_value <= 0) and term_value and term_value > 0:
        payment_value = estimate_monthly_payment(balance, annual_rate, term_value)

    if payment_value is None or payment_value <= 0:
        return None, None

    if not term_value or term_value <= 0:
        payoff_est = estimate_payoff_months(balance, annual_rate, payment_value)
        term_value = int(math.ceil(payoff_est)) if payoff_est else max_months

    schedule = []
    total_interest = 0.0
    remaining = balance
    for month in range(1, min(term_value, max_months) + 1):
        interest = remaining * rate
        principal = payment_value - interest
        if principal <= 0:
            break
        if principal > remaining:
            principal = remaining
            payment_actual = principal + interest
        else:
            payment_actual = payment_value
        remaining -= principal
        total_interest += interest
        schedule.append({
            "Month": month,
            "Payment": payment_actual,
            "Principal": principal,
            "Interest": interest,
            "Balance": max(0.0, remaining)
        })
        if remaining <= 0.01:
            break

    if not schedule:
        return None, None
    return pd.DataFrame(schedule), total_interest

def add_months_to_date(base_date, months):
    try:
        months = int(months)
    except Exception:
        return base_date
    if months <= 0:
        return base_date
    year = base_date.year + (base_date.month - 1 + months) // 12
    month = (base_date.month - 1 + months) % 12 + 1
    day = min(base_date.day, calendar.monthrange(year, month)[1])
    return base_date.replace(year=year, month=month, day=day)

def compute_payoff_date(liability):
    schedule_df, _ = build_amortization_schedule(
        liability.get("balance"),
        liability.get("interest_rate"),
        liability.get("payment"),
        liability.get("term_months")
    )
    if schedule_df is None or schedule_df.empty:
        return None
    start_raw = liability.get("start_date")
    if start_raw:
        try:
            start_dt = datetime.fromisoformat(start_raw).date()
        except Exception:
            start_dt = datetime.now().date()
    else:
        start_dt = datetime.now().date()
    return add_months_to_date(start_dt, int(schedule_df["Month"].iloc[-1]))

def escape_ics_text(value):
    text = str(value or "")
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text

def build_ics_calendar(events, calendar_name="WealthPulse Events"):
    if not events:
        return None
    stamp = utc_now().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//WealthPulse//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{escape_ics_text(calendar_name)}",
        "METHOD:PUBLISH"
    ]
    for event in events:
        event_date = event.get("date")
        if isinstance(event_date, str):
            try:
                event_date = datetime.fromisoformat(event_date).date()
            except Exception:
                event_date = None
        if not event_date:
            continue
        date_str = event_date.strftime("%Y%m%d")
        summary = f"{event.get('type', 'Event')}: {event.get('name', '')}".strip()
        owner = event.get("owner")
        if owner:
            summary = f"{summary} ({owner})"
        description = f"Type: {event.get('type', '')}\\nName: {event.get('name', '')}\\nOwner: {owner or ''}"
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{secrets.token_hex(8)}@wealthpulse",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{date_str}",
            f"SUMMARY:{escape_ics_text(summary)}",
            f"DESCRIPTION:{escape_ics_text(description)}",
            "END:VEVENT"
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"

def build_simple_pdf(lines, title="WealthPulse Quick Guide"):
    if not lines:
        lines = []
    def pdf_escape(text):
        text = str(text or "")
        text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return text
    prepared = []
    if title:
        prepared.append(title)
        prepared.append("")
    for line in lines:
        if line is None:
            continue
        sanitized = str(line).encode("latin-1", "replace").decode("latin-1")
        prepared.append(sanitized)
    font_size = 12
    leading = 16
    start_x = 72
    start_y = 760
    content_lines = ["BT", f"/F1 {font_size} Tf", f"{start_x} {start_y} Td"]
    for idx, line in enumerate(prepared):
        content_lines.append(f"({pdf_escape(line)}) Tj")
        if idx != len(prepared) - 1:
            content_lines.append(f"0 -{leading} Td")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines)
    content_bytes = content_stream.encode("latin-1")
    objects = []
    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        "3 0 obj\n"
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> >>\n"
        "endobj\n"
    )
    objects.append(
        f"4 0 obj\n<< /Length {len(content_bytes)} >>\nstream\n{content_stream}\nendstream\nendobj\n"
    )
    objects.append("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = []
    current = len(header)
    body = b""
    for obj in objects:
        offsets.append(current)
        data = obj.encode("latin-1")
        body += data
        current += len(data)
    xref_start = len(header) + len(body)
    xref_lines = ["xref", f"0 {len(objects) + 1}", "0000000000 65535 f "]
    for offset in offsets:
        xref_lines.append(f"{offset:010d} 00000 n ")
    xref = "\n".join(xref_lines).encode("latin-1") + b"\n"
    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_start}\n%%EOF\n"
    ).encode("latin-1")
    return header + body + xref + trailer

def render_html_block(html_text):
    if hasattr(st, "html"):
        st.html(html_text)
    else:
        st.markdown(html_text, unsafe_allow_html=True)

def request_scroll_to_top():
    st.session_state.scroll_to_top = True

def render_scroll_to_top():
    if st.session_state.get("scroll_to_top"):
        components.html(
            """
            <script>
                (function() {
                    const parent = window.parent;
                    if (parent && parent.scrollTo) {
                        parent.scrollTo({ top: 0, behavior: "smooth" });
                    }
                })();
            </script>
            """,
            height=0
        )
        st.session_state.scroll_to_top = False

    st.session_state.gold_animation = True

def render_https_warning_banner():
    components.html(
        """
        <script>
        (function() {
            const host = window.location.hostname || "";
            const isLocal = host === "localhost" || host === "127.0.0.1";
            if (window.location.protocol !== "https:" && !isLocal) {
                const id = "https-warning-banner";
                if (!document.getElementById(id)) {
                    const banner = document.createElement("div");
                    banner.id = id;
                    banner.textContent = "Security notice: This app is running over HTTP. Use HTTPS for production deployments.";
                    banner.style.position = "fixed";
                    banner.style.top = "0";
                    banner.style.left = "0";
                    banner.style.right = "0";
                    banner.style.zIndex = "9999";
                    banner.style.padding = "10px 16px";
                    banner.style.background = "#b45309";
                    banner.style.color = "#fff";
                    banner.style.fontWeight = "600";
                    banner.style.textAlign = "center";
                    banner.style.boxShadow = "0 6px 18px rgba(0,0,0,0.25)";
                    document.body.appendChild(banner);
                }
            }
        })();
        </script>
        """,
        height=0
    )

def render_https_enforcement():
    if not secret_flag("REQUIRE_HTTPS", False):
        return
    components.html(
        """
        <script>
        (function() {
            const host = window.location.hostname || "";
            const isLocal = host === "localhost" || host === "127.0.0.1";
            if (window.location.protocol !== "https:" && !isLocal) {
                const id = "https-enforce-overlay";
                if (!document.getElementById(id)) {
                    const overlay = document.createElement("div");
                    overlay.id = id;
                    overlay.style.position = "fixed";
                    overlay.style.inset = "0";
                    overlay.style.background = "rgba(10, 10, 15, 0.92)";
                    overlay.style.zIndex = "10000";
                    overlay.style.display = "flex";
                    overlay.style.alignItems = "center";
                    overlay.style.justifyContent = "center";
                    overlay.style.padding = "24px";
                    overlay.innerHTML = "<div style='max-width:520px; background:#111827; color:#f9fafb; padding:24px; border-radius:16px; border:1px solid rgba(255,255,255,0.1); text-align:center; font-family: IBM Plex Sans, sans-serif;'><h2 style='margin:0 0 12px 0;'>HTTPS Required</h2><p style='margin:0 0 16px 0; line-height:1.5;'>This deployment is configured to require HTTPS. Please access the app via a secure HTTPS URL.</p><p style='margin:0; font-size:0.9rem; color:#9ca3af;'>Contact the admin if you need help enabling HTTPS.</p></div>";
                    document.body.appendChild(overlay);
                }
            }
        })();
        </script>
        """,
        height=0
    )

def render_gold_animation():
    if st.session_state.get("gold_animation"):
        components.html(
            """
            <script>
                (function() {
                    const parent = window.parent;
                    if (parent && parent.__spawnGoldFx) {
                        parent.__spawnGoldFx();
                    }
                })();
            </script>
            """,
            height=0
        )
        st.session_state.gold_animation = False

def render_gold_click_listener():
    components.html(
        """
        <script>
            (function() {
                const parent = window.parent;
                if (!parent || parent.__goldFxListener) return;
                parent.__goldFxListener = true;
                const doc = parent.document;

                parent.__spawnGoldFx = function() {
                    const existing = doc.getElementById('gold-fx-container');
                    if (existing) {
                        existing.remove();
                    }
                    const container = doc.createElement('div');
                    container.id = 'gold-fx-container';
                    container.className = 'gold-fx-container';
                    doc.body.appendChild(container);
                    const count = 22;
                    for (let i = 0; i < count; i++) {
                        const item = doc.createElement('div');
                        item.className = 'gold-fx';
                        item.style.left = Math.random() * 100 + '%';
                        item.style.animationDelay = (Math.random() * 0.6) + 's';
                        item.style.fontSize = (18 + Math.random() * 16) + 'px';
                        if (i % 2 === 0) {
                            item.innerText = '$';
                        } else {
                            const bar = doc.createElement('div');
                            bar.className = 'gold-bar';
                            item.appendChild(bar);
                        }
                        container.appendChild(item);
                    }
                    setTimeout(() => {
                        container.remove();
                    }, 3000);
                };

                const triggerWords = /(save|add|delete|remove|post|create|update|close|reset|buy now|mark as sold)/i;
                doc.addEventListener('click', function(e) {
                    const btn = e.target.closest('button');
                    if (!btn) return;
                    const label = (btn.innerText || '').trim().toLowerCase();
                    if (!label) return;
                    if (triggerWords.test(label)) {
                        parent.__spawnGoldFx();
                    }
                }, true);
            })();
        </script>
        """,
        height=0
    )

def apply_card_click_overlay(marker_id):
    safe_marker = html.escape(marker_id, quote=True)
    components.html(f"""
        <script>
            (function() {{
                const doc = window.parent.document;
                const marker = doc.getElementById("{safe_marker}");
                if (!marker) return;
                const block = marker.closest('[data-testid="stVerticalBlock"]');
                if (!block) return;
                block.style.position = 'relative';
                const btnWrap = block.querySelector('div[data-testid="stButton"]');
                const btn = btnWrap ? btnWrap.querySelector('button') : null;
                if (!btn || !btnWrap) return;
                btnWrap.style.position = 'absolute';
                btnWrap.style.inset = '0';
                btnWrap.style.zIndex = '5';
                btn.style.width = '100%';
                btn.style.height = '100%';
                btn.style.opacity = '0';
                btn.style.padding = '0';
                btn.style.margin = '0';
                btn.style.border = 'none';
                btn.style.boxShadow = 'none';
            }})();
        </script>
    """, height=0)


# ==============================
# CURRENCY HELPERS
# ==============================
def get_system_locale_code():
    try:
        loc = locale.getlocale()
    except Exception:
        loc = (None, None)
    if not loc or not loc[0]:
        try:
            locale.setlocale(locale.LC_ALL, "")
            loc = locale.getlocale()
        except Exception:
            loc = (None, None)
    return loc[0] or ""

def get_default_currency_code():
    try:
        loc = get_system_locale_code()
    except Exception:
        loc = ""
    if "_" in loc:
        country = loc.split("_")[-1].upper()
        return COUNTRY_CURRENCY.get(country, "USD")
    return "USD"

def get_country_code(settings=None):
    if settings:
        override = (settings.get("country_override") or "").strip().upper()
        if override:
            return override
    try:
        loc = get_system_locale_code()
    except Exception:
        loc = ""
    if "_" in loc:
        return loc.split("_")[-1].upper()
    return ""

def get_country_name(code):
    if not code:
        return "your country"
    return COUNTRY_NAMES.get(code, code)

def get_local_entity_examples(code):
    examples = {
        "US": ["Personal", "LLC", "S-Corp", "C-Corp", "Trust"],
        "NZ": ["Personal", "Ltd Company", "Family Trust"],
        "AU": ["Personal", "Pty Ltd", "Family Trust"],
        "GB": ["Personal", "Ltd", "LLP", "Trust"],
        "CA": ["Personal", "Corporation", "Family Trust"],
        "IE": ["Personal", "Ltd", "Trust"],
        "SG": ["Personal", "Pte Ltd", "Trust"],
        "IN": ["Personal", "Pvt Ltd", "LLP", "Trust"],
        "ZA": ["Personal", "Pty Ltd", "Trust"],
        "FR": ["Personal", "SARL", "SAS", "Trust"],
        "DE": ["Personal", "GmbH", "UG", "Trust"],
        "ES": ["Personal", "SL", "SA", "Trust"],
        "IT": ["Personal", "SRL", "SPA", "Trust"],
        "NL": ["Personal", "BV", "Trust"],
        "BE": ["Personal", "BV", "SRL", "Trust"],
        "CH": ["Personal", "GmbH", "AG", "Trust"],
        "SE": ["Personal", "AB", "Trust"],
        "NO": ["Personal", "AS", "Trust"],
        "DK": ["Personal", "ApS", "A/S", "Trust"],
        "PT": ["Personal", "Lda", "SA", "Trust"],
        "AT": ["Personal", "GmbH", "AG", "Trust"],
        "FI": ["Personal", "Oy", "Oyj", "Trust"],
        "PL": ["Personal", "Sp. z o.o.", "SA", "Trust"],
        "CZ": ["Personal", "s.r.o.", "a.s.", "Trust"],
        "HU": ["Personal", "Kft", "Zrt", "Trust"],
        "RO": ["Personal", "SRL", "SA", "Trust"],
        "BG": ["Personal", "OOD", "AD", "Trust"],
        "GR": ["Personal", "EPE", "AE", "Trust"],
        "TR": ["Personal", "Ltd", "AS", "Trust"],
        "IL": ["Personal", "Ltd", "Trust"],
        "BR": ["Personal", "Ltda", "SA", "Trust"],
        "MX": ["Personal", "S.A. de C.V.", "S. de R.L.", "Trust"],
        "AR": ["Personal", "SRL", "SA", "Trust"],
        "CL": ["Personal", "SpA", "SA", "Trust"],
        "CO": ["Personal", "SAS", "LTDA", "Trust"],
        "MY": ["Personal", "Sdn Bhd", "Trust"],
        "PH": ["Personal", "Corp", "Trust"],
        "TH": ["Personal", "Ltd", "Trust"],
        "VN": ["Personal", "LLC", "JSC", "Trust"],
        "ID": ["Personal", "PT", "Trust"]
    }
    return examples.get(code, ["Personal", "Business", "Trust"])

def get_local_entity_hint(code):
    hints = {
        "US": "Common labels include LLC, S-Corp, C-Corp.",
        "NZ": "Common labels include Ltd Company and Family Trust.",
        "AU": "Common labels include Pty Ltd and Family Trust.",
        "GB": "Common labels include Ltd and LLP.",
        "CA": "Common labels include Corporation and Family Trust.",
        "IE": "Common labels include Ltd.",
        "SG": "Common labels include Pte Ltd.",
        "IN": "Common labels include Pvt Ltd and LLP.",
        "ZA": "Common labels include Pty Ltd.",
        "FR": "Common labels include SARL and SAS.",
        "DE": "Common labels include GmbH and UG.",
        "ES": "Common labels include SL and SA.",
        "IT": "Common labels include SRL and SPA.",
        "NL": "Common labels include BV.",
        "BE": "Common labels include BV and SRL.",
        "CH": "Common labels include GmbH and AG.",
        "SE": "Common labels include AB.",
        "NO": "Common labels include AS.",
        "DK": "Common labels include ApS and A/S.",
        "PT": "Common labels include Lda and SA.",
        "AT": "Common labels include GmbH and AG.",
        "FI": "Common labels include Oy and Oyj.",
        "PL": "Common labels include Sp. z o.o. and SA.",
        "CZ": "Common labels include s.r.o. and a.s.",
        "HU": "Common labels include Kft and Zrt.",
        "RO": "Common labels include SRL and SA.",
        "BG": "Common labels include OOD and AD.",
        "GR": "Common labels include EPE and AE.",
        "TR": "Common labels include Ltd and AS.",
        "IL": "Common labels include Ltd.",
        "BR": "Common labels include Ltda and SA.",
        "MX": "Common labels include S.A. de C.V. and S. de R.L.",
        "AR": "Common labels include SRL and SA.",
        "CL": "Common labels include SpA and SA.",
        "CO": "Common labels include SAS and LTDA.",
        "MY": "Common labels include Sdn Bhd.",
        "PH": "Common labels include Corp.",
        "TH": "Common labels include Ltd.",
        "VN": "Common labels include LLC and JSC.",
        "ID": "Common labels include PT."
    }
    return hints.get(code, "Common labels include Personal, Business, and Trust.")

# ==============================
# HELP MENU
# ==============================
with st.sidebar:
    st.markdown("## Help")
    with st.expander("Quick Guide", expanded=False):
        st.markdown("""
        **Getting Started**
        - Add assets under the `Add Asset` tab.
        - Set your currency and API keys in `Settings`.
        - Create entities and liabilities in `Entities & Liabilities`.

        **Wealth Management**
        - Assign owners, custodians, beneficiaries, and review dates for each asset.
        - Use ownership splits to model joint ownership.

        **Net Worth**
        - The Portfolio tab shows net worth after liabilities.
        - Switch the Portfolio View to see entity‑level totals.

        **Analytics**
        - Charts adapt to your selected entity view.
        - Use the Wealth Plan in Settings to track target allocations.
        """)
    with st.expander("Founder Guide", expanded=False):
        country_code = get_country_code(user_settings if "user_settings" in locals() else None)
        if not country_code:
            country_name = "Auto (unknown)"
            examples = "Personal, Business, Trust"
            local_hint = "Set Country Override in Settings if this looks wrong."
        else:
            country_name = get_country_name(country_code)
            examples = ", ".join(get_local_entity_examples(country_code))
            local_hint = get_local_entity_hint(country_code)
        st.markdown("""
        **Built for small business owners**
        - Separate **Personal**, **Business**, and **Trust** assets so your numbers are clean.
        - Track liabilities so you can see **true net worth** at a glance.
        - Add beneficiaries and review dates to keep long‑term plans active.

        **Suggested setup**
        1. Create entities: Personal, Business, Trust (or Joint).
        2. Add assets and assign them to the right entity.
        3. Add debts/loans with payoff dates.
        4. Set Wealth Plan targets and allocations.
        5. Export estate/beneficiary reports when needed.

        *This app provides organization and insights only — not legal or financial advice.*
        """)
        st.caption(f"Local examples for {country_name}: {examples}.")
        st.caption(local_hint)

def build_currency_options(default_code):
    seen = set()
    options = []
    if default_code:
        for code, name in CURRENCY_LIST:
            if code == default_code and code not in seen:
                options.append((code, name))
                seen.add(code)
                break
        if default_code not in seen:
            options.append((default_code, "Local Currency"))
            seen.add(default_code)
    for code, name in sorted(CURRENCY_LIST, key=lambda x: x[0]):
        if code not in seen:
            options.append((code, name))
            seen.add(code)
    return options

def get_user_settings(db_obj, username):
    record = ensure_user_record(db_obj, username)
    settings = DEFAULT_SETTINGS.copy()
    settings.update(record.get("settings") or {})
    default_code = get_default_currency_code()
    currency_code = settings.get("currency_code") or default_code
    currency_symbol = settings.get("currency_symbol") or CURRENCY_SYMBOLS.get(currency_code, currency_code + " ")
    currency_rate = settings.get("currency_rate")
    if currency_rate is None or currency_rate <= 0:
        currency_rate = 1.0
    settings["currency_code"] = currency_code
    settings["currency_symbol"] = currency_symbol
    settings["currency_rate"] = currency_rate
    return settings

def to_display_currency(value, currency_rate):
    try:
        return float(value) * float(currency_rate)
    except Exception:
        return 0.0

def from_display_currency(value, currency_rate):
    try:
        rate = float(currency_rate)
        if rate <= 0:
            return float(value)
        return float(value) / rate
    except Exception:
        return 0.0

def format_currency_value(value, currency_rate):
    return to_display_currency(value, currency_rate)

def format_currency(value, currency_symbol, currency_rate):
    if st.session_state.get("privacy_mode") and not st.session_state.get("reveal_values"):
        return "Hidden"
    display_value = to_display_currency(value, currency_rate)
    symbol = currency_symbol or ""
    if symbol.strip() == "":
        return f"{display_value:,.2f}"
    return f"{symbol}{display_value:,.2f}"

def format_currency_html(value, currency_symbol, currency_rate):
    return escape_html(format_currency(value, currency_symbol, currency_rate))

def format_display_value(value, currency_symbol, currency_rate):
    return format_currency(value, currency_symbol, currency_rate)

# ==============================
# CACHE & TIME HELPERS
# ==============================
def utc_now():
    return datetime.now(timezone.utc)

def get_cache(key, ttl_seconds):
    cache = st.session_state.get("_cache", {})
    entry = cache.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > ttl_seconds:
        return None
    return entry["value"]

def set_cache(key, value):
    cache = st.session_state.setdefault("_cache", {})
    cache[key] = {"ts": time.time(), "value": value}

def get_now_for_settings(settings):
    tz = settings.get("timezone", "Local")
    if tz and tz != "Local":
        try:
            return datetime.now(ZoneInfo(tz))
        except Exception:
            return datetime.now()
    return datetime.now()

def format_date_for_settings(value_dt, settings):
    fmt_key = settings.get("date_format", "MMM D, YYYY")
    fmt = DATE_FORMATS.get(fmt_key, "%b %d, %Y")
    try:
        return value_dt.strftime(fmt)
    except Exception:
        return value_dt.strftime("%b %d, %Y")

# ==============================
# LIVE DATA HELPERS
# ==============================
def fetch_metalprice_latest(api_key, metals=None, base="USD"):
    if not api_key:
        return None, "MetalpriceAPI key missing."
    metals = metals or ["XAU", "XAG", "XPT", "XPD"]
    try:
        resp = requests.get(
            "https://api.metalpriceapi.com/v1/latest",
            params={
                "api_key": api_key,
                "base": base,
                "currencies": ",".join(metals)
            },
            timeout=10
        )
        data = resp.json()
        if not data.get("success", False):
            return None, data.get("error", "MetalpriceAPI error")
        rates = data.get("rates", {})
        prices = {}
        for code in metals:
            usd_key = f"USD{code}"
            if usd_key in rates:
                prices[code] = rates[usd_key]
            elif code in rates and rates[code]:
                prices[code] = 1 / rates[code]
        return {
            "prices": prices,
            "timestamp": data.get("timestamp"),
            "base": data.get("base")
        }, None
    except Exception as exc:
        return None, str(exc)

@st.cache_data(ttl=3600)
def fetch_metalprice_timeframe(api_key, start_date, end_date, metals=None, base="USD"):
    if not api_key:
        return None, "MetalpriceAPI key missing."
    metals = metals or ["XAU", "XAG", "XPT", "XPD"]
    try:
        resp = requests.get(
            "https://api.metalpriceapi.com/v1/timeframe",
            params={
                "api_key": api_key,
                "start_date": start_date,
                "end_date": end_date,
                "base": base,
                "currencies": ",".join(metals)
            },
            timeout=10
        )
        data = resp.json()
        if not data.get("success", False):
            return None, data.get("error", "MetalpriceAPI error")
        rates = data.get("rates", {})
        rows = []
        for date_key, values in sorted(rates.items()):
            row = {"date": date_key}
            for code in metals:
                usd_key = f"USD{code}"
                if usd_key in values:
                    row[code] = values[usd_key]
                elif code in values and values[code]:
                    row[code] = 1 / values[code]
            rows.append(row)
        return pd.DataFrame(rows), None
    except Exception as exc:
        return None, str(exc)

def fetch_metalsdev_fx(api_key, base="USD"):
    if not api_key:
        return None, "Metals.dev API key missing."
    try:
        resp = requests.get(
            "https://api.metals.dev/v1/currencies",
            params={"api_key": api_key, "base": base},
            timeout=10
        )
        data = resp.json()
        if data.get("status") != "success":
            return None, data.get("error", "Metals.dev error")
        return {
            "currencies": data.get("currencies", {}),
            "timestamp": data.get("timestamp")
        }, None
    except Exception as exc:
        return None, str(exc)

def fetch_frankfurter_fx(base="USD"):
    try:
        resp = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": base},
            timeout=10
        )
        data = resp.json()
        rates = data.get("rates", {})
        return {
            "rates": rates,
            "date": data.get("date")
        }, None
    except Exception as exc:
        return None, str(exc)

def fetch_open_er_fx(base="USD"):
    try:
        resp = requests.get(
            f"https://open.er-api.com/v6/latest/{base}",
            timeout=10
        )
        data = resp.json()
        rates = data.get("rates", {})
        return {
            "rates": rates,
            "date": data.get("time_last_update_utc")
        }, None
    except Exception as exc:
        return None, str(exc)

def fetch_freegoldprice_latest(api_key):
    if not api_key:
        return None, "FreeGoldPrice API key missing."
    try:
        resp = requests.get(
            "https://freegoldprice.org/api/v2",
            params={"key": api_key, "action": "GSPPJ"},
            timeout=10
        )
        data = resp.json()
        prices = {}
        for code, key in [("XAU", "gold"), ("XAG", "silver"), ("XPT", "platinum"), ("XPD", "palladium")]:
            block = data.get(key, {})
            usd = block.get("USD") or {}
            price = usd.get("ask") or usd.get("bid")
            if price:
                prices[code] = float(price)
        timestamp = data.get("date") or data.get("timestamp")
        return {
            "prices": prices,
            "timestamp": timestamp
        }, None
    except Exception as exc:
        return None, str(exc)

def _fetch_silverprice_payload(currency_code):
    try:
        resp = requests.get(
            f"https://data-asg.goldprice.org/dbXRates/{currency_code}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        data = resp.json()
        items = data.get("items") or []
        if not items:
            return None, data.get("error", "SilverPrice data unavailable.")
        item = items[0]
        prices = {}
        if item.get("xauPrice") is not None:
            prices["XAU"] = float(item["xauPrice"])
        if item.get("xagPrice") is not None:
            prices["XAG"] = float(item["xagPrice"])
        timestamp = data.get("date") or data.get("ts")
        return {
            "prices": prices,
            "timestamp": timestamp,
            "base": item.get("curr", currency_code)
        }, None
    except Exception as exc:
        return None, str(exc)

def fetch_silverprice_latest(currency_code="USD"):
    code = (currency_code or "USD").upper()
    data, err = _fetch_silverprice_payload(code)
    if not data and code != "USD":
        fallback, fallback_err = _fetch_silverprice_payload("USD")
        if fallback:
            return fallback, f"{err}. Falling back to USD."
        return None, fallback_err or err
    return data, err

def fetch_newsapi(query, api_key):
    if not api_key:
        return None, "NewsAPI key missing."
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": api_key
            },
            timeout=10
        )
        data = resp.json()
        if data.get("status") != "ok":
            return None, data.get("message", "NewsAPI error")
        return data.get("articles", []), None
    except Exception as exc:
        return None, str(exc)

def fetch_rss_items(url, limit=5):
    if not url:
        return None, "RSS URL missing."
    try:
        resp = requests.get(url, timeout=10)
        xml_data = resp.text
        root = ET.fromstring(xml_data)
        items = []
        # RSS 2.0
        for item in root.findall(".//item"):
            title = item.findtext("title") or "Article"
            link = item.findtext("link") or ""
            pub = item.findtext("pubDate") or ""
            items.append({"title": title, "link": link, "published": pub})
            if len(items) >= limit:
                return items, None
        # Atom
        for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
            title = entry.findtext("{http://www.w3.org/2005/Atom}title") or "Article"
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href") if link_el is not None else ""
            pub = entry.findtext("{http://www.w3.org/2005/Atom}updated") or ""
            items.append({"title": title, "link": link, "published": pub})
            if len(items) >= limit:
                break
        return items, None if items else "No RSS items found."
    except Exception as exc:
        return None, str(exc)

def get_ebay_access_token(client_id, client_secret):
    if not client_id or not client_secret:
        return None, "eBay credentials missing."
    token = st.session_state.get("ebay_token")
    expiry = st.session_state.get("ebay_token_expiry")
    if token and expiry and time.time() < expiry - 60:
        return token, None
    try:
        resp = requests.post(
            "https://api.ebay.com/identity/v1/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope"
            },
            auth=(client_id, client_secret),
            timeout=10
        )
        data = resp.json()
        if "access_token" not in data:
            return None, data.get("error_description", "Unable to authenticate with eBay.")
        token = data["access_token"]
        expires_in = int(data.get("expires_in", 7200))
        st.session_state.ebay_token = token
        st.session_state.ebay_token_expiry = time.time() + expires_in
        return token, None
    except Exception as exc:
        return None, str(exc)

def search_ebay_comps(query, token, limit=5):
    try:
        resp = requests.get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            params={"q": query, "limit": limit},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        data = resp.json()
        items = []
        for item in data.get("itemSummaries", []):
            price = item.get("price", {})
            items.append({
                "title": item.get("title", "Item"),
                "price": price.get("value"),
                "currency": price.get("currency"),
                "url": item.get("itemWebUrl", "")
            })
        return items, None
    except Exception as exc:
        return None, str(exc)

def search_reverb_comps(query, token, limit=5):
    try:
        resp = requests.get(
            "https://api.reverb.com/api/listings",
            params={"query": query, "per_page": limit},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        data = resp.json()
        items = []
        for listing in data.get("listings", []):
            price = listing.get("price", {})
            items.append({
                "title": listing.get("title", "Listing"),
                "price": price.get("amount"),
                "currency": price.get("currency"),
                "url": listing.get("links", {}).get("web", {}).get("href", "")
            })
        return items, None
    except Exception as exc:
        return None, str(exc)

def get_effective_market_price(asset):
    live_prices = st.session_state.get("live_metal_prices", {})
    use_live = st.session_state.get("use_live_metal_price", False)
    asset_type = asset.get("type")
    if use_live and asset_type in METAL_CODES:
        code = METAL_CODES.get(asset_type)
        spot = live_prices.get(code)
        if spot:
            weight = asset.get("details", {}).get("weight_troy_oz")
            if weight:
                return spot * weight
            return spot
    return asset.get("market_price", 0)
# ==============================
# TYPE DETAIL HELPERS
# ==============================
DETAIL_LABELS = {
    "weight_troy_oz": "Weight",
    "purity": "Purity",
    "mint": "Mint",
    "year": "Year",
    "make": "Make",
    "model": "Model",
    "serial": "Serial / ID",
    "condition_notes": "Condition Notes",
    "grade": "Grade",
    "grading_company": "Grading Company",
    "set_name": "Set / Series",
    "artist": "Artist",
    "medium": "Medium",
    "dimensions": "Dimensions",
    "location": "Location",
    "square_feet": "Square Feet",
    "purchase_date": "Purchase Date",
    "cost_basis": "Cost Basis (Total)",
    "wallet": "Wallet / Exchange",
    "ticker_exchange": "Exchange",
    "stone": "Gem / Stone",
    "band": "Band / Strap",
    "material": "Material",
    "vin": "VIN",
    "mileage": "Mileage",
    "hull_id": "Hull ID",
    "engine_hours": "Engine Hours",
    "industry": "Industry",
    "entity": "Entity / Structure",
    "ownership_pct": "Ownership %",
    "provider": "Provider",
    "policy_number": "Policy #",
    "coverage_amount": "Coverage Amount",
    "renewal_date": "Renewal Date",
    "valuation_method": "Valuation Method",
    "notes_extra": "Extra Details"
}

WEALTH_LABELS = {
    "owner_entity": "Owner / Entity",
    "custodian": "Custodian / Account",
    "beneficiary": "Beneficiary",
    "liquidity_horizon": "Liquidity Horizon",
    "insured_value": "Insured Value",
    "review_date": "Next Review Date"
}

def weight_to_display(value_troy_oz, unit):
    if value_troy_oz is None:
        return None
    if unit == "g":
        return float(value_troy_oz) * 31.1034768
    return float(value_troy_oz)

def weight_from_display(value, unit):
    if value is None:
        return None
    if unit == "g":
        return float(value) / 31.1034768
    return float(value)

def get_weight_label(unit):
    return "Weight (grams)" if unit == "g" else "Weight (troy oz)"

def format_detail_value(key, value, currency_symbol, currency_rate, weight_unit):
    if value in (None, "", []):
        return None
    if key == "weight_troy_oz":
        display = weight_to_display(value, weight_unit)
        if display is None:
            return None
        unit_label = "g" if weight_unit == "g" else "toz"
        return f"{display:,.2f} {unit_label}"
    if key == "cost_basis":
        return format_currency(value, currency_symbol, currency_rate)
    return str(value)

def prune_details(details):
    if not isinstance(details, dict):
        return {}
    return {k: v for k, v in details.items() if v not in (None, "", [])}

def render_details_list(details, currency_symbol, currency_rate, weight_unit):
    if not details:
        return
    st.markdown("**Details:**")
    for key, value in details.items():
        label = DETAIL_LABELS.get(key, key.replace("_", " ").title())
        display_value = format_detail_value(key, value, currency_symbol, currency_rate, weight_unit)
        if display_value is None:
            continue
        st.write(f"- {label}: {display_value}")

def render_wealth_list(wealth, currency_symbol, currency_rate, settings):
    if not wealth:
        return
    st.markdown("**Wealth Management:**")
    split = wealth.get("ownership_split")
    if isinstance(split, dict) and split:
        split_parts = []
        for name, pct in split.items():
            try:
                split_parts.append(f"{name} {float(pct):.1f}%")
            except Exception:
                split_parts.append(f"{name} {pct}")
        if split_parts:
            st.write("- Ownership Split: " + ", ".join(split_parts))
    for key, value in wealth.items():
        if value in (None, "", []):
            continue
        if key == "ownership_split":
            continue
        label = WEALTH_LABELS.get(key, key.replace("_", " ").title())
        if key == "insured_value":
            display_value = format_currency(value, currency_symbol, currency_rate)
        elif key == "review_date":
            try:
                dt = datetime.fromisoformat(str(value))
                display_value = format_date_for_settings(dt, settings)
            except Exception:
                display_value = str(value)
        else:
            display_value = str(value)
        st.write(f"- {label}: {display_value}")

def build_comps_query(asset):
    name = asset.get("name", "")
    details = asset.get("details", {})
    parts = [name]
    make = details.get("make")
    model = details.get("model")
    year = details.get("year")
    if make and make not in name:
        parts.append(make)
    if model and model not in name:
        parts.append(model)
    if year and year not in name:
        parts.append(str(year))
    return " ".join([p for p in parts if p]).strip()

def format_comps_price(value, currency_code, currency_symbol, currency_rate):
    try:
        if currency_code == "USD":
            return format_currency(float(value), currency_symbol, currency_rate)
        return f"{currency_code} {float(value):,.2f}"
    except Exception:
        return str(value)

def render_comps_section(asset, asset_index, settings, currency_symbol, currency_rate):
    with st.expander("Price Comparisons"):
        ebay_client_id = get_effective_setting(settings, "ebay_client_id", "EBAY_CLIENT_ID")
        ebay_client_secret = get_effective_setting(settings, "ebay_client_secret", "EBAY_CLIENT_SECRET")
        reverb_token = get_effective_setting(settings, "reverb_api_token", "REVERB_API_TOKEN")
        has_ebay = bool(ebay_client_id and ebay_client_secret)
        has_reverb = bool(reverb_token)
        if not has_ebay and not has_reverb:
            st.info("Add eBay or Reverb API keys in Settings to see price comparisons.")
            return

        query = build_comps_query(asset)
        cache_key = f"comps_{asset_index}_{query}"
        cached = get_cache(cache_key, 900)

        fetch_label = "Refresh comparisons" if cached else "Fetch comparisons"
        if st.button(fetch_label, key=f"fetch_comps_{asset_index}"):
            comps = {"ebay": [], "reverb": []}
            if has_ebay:
                token, err = get_ebay_access_token(ebay_client_id, ebay_client_secret)
                if token:
                    items, _ = search_ebay_comps(query, token, limit=5)
                    comps["ebay"] = items or []
                else:
                    comps["ebay"] = [{"title": f"eBay error: {err}", "price": None, "currency": None, "url": ""}]
            if has_reverb and asset.get("type") == "Guitar":
                items, _ = search_reverb_comps(query, reverb_token, limit=5)
                comps["reverb"] = items or []
            set_cache(cache_key, comps)
            cached = comps

        if not cached:
            st.caption("Click fetch to load comparisons.")
            return

        if cached.get("ebay"):
            st.markdown("**eBay**")
            for item in cached["ebay"]:
                title = item.get("title", "Item")
                price = item.get("price")
                currency = item.get("currency") or "USD"
                url = item.get("url", "")
                price_text = format_comps_price(price, currency, currency_symbol, currency_rate) if price else "Price unavailable"
                if url:
                    st.markdown(f"- [{title}]({url}) — {price_text}")
                else:
                    st.write(f"- {title} — {price_text}")

        if cached.get("reverb"):
            st.markdown("**Reverb**")
            for item in cached["reverb"]:
                title = item.get("title", "Listing")
                price = item.get("price")
                currency = item.get("currency") or "USD"
                url = item.get("url", "")
                price_text = format_comps_price(price, currency, currency_symbol, currency_rate) if price else "Price unavailable"
                if url:
                    st.markdown(f"- [{title}]({url}) — {price_text}")
                else:
                    st.write(f"- {title} — {price_text}")

def get_asset_suggestions(query, settings, portfolio, limit=8):
    query = (query or "").strip()
    if len(query) < 2:
        return []
    cache_key = f"suggest_{query.lower()}"
    cached = get_cache(cache_key, 600)
    if cached:
        return cached

    query_lower = query.lower()
    query_tokens = [t for t in query_lower.split() if t]
    suggestions = []

    def score_title(title, source):
        title_lower = title.lower().strip()
        if not title_lower:
            return 0
        similarity = difflib.SequenceMatcher(None, query_lower, title_lower).ratio() * 100
        if title_lower == query_lower:
            return 10000 + similarity
        score = similarity
        if title_lower.startswith(query_lower):
            score += 25
        if query_lower in title_lower:
            score += 10
        token_hits = 0
        for token in query_tokens:
            if token in title_lower:
                token_hits += 1
        if query_tokens:
            score += (token_hits / len(query_tokens)) * 20
        score += token_hits * 3
        score -= max(0, len(title_lower) - len(query_lower)) * 0.15
        if source == "local":
            score += 12
        elif source == "reverb":
            score += 6
        elif source == "ebay":
            score += 4
        return score

    # Local matches
    for asset in portfolio:
        name = asset.get("name", "")
        if query_lower in name.lower():
            suggestions.append({"title": name, "source": "local"})

    # eBay suggestions
    ebay_client_id = get_effective_setting(settings, "ebay_client_id", "EBAY_CLIENT_ID")
    ebay_client_secret = get_effective_setting(settings, "ebay_client_secret", "EBAY_CLIENT_SECRET")
    if len(query) >= 3 and ebay_client_id and ebay_client_secret:
        token, err = get_ebay_access_token(ebay_client_id, ebay_client_secret)
        if token:
            items, _ = search_ebay_comps(query, token, limit=limit)
            if items:
                suggestions.extend([{"title": item.get("title"), "source": "ebay"} for item in items if item.get("title")])

    # Reverb suggestions
    reverb_token = get_effective_setting(settings, "reverb_api_token", "REVERB_API_TOKEN")
    if len(query) >= 3 and reverb_token:
        items, _ = search_reverb_comps(query, reverb_token, limit=limit)
        if items:
            suggestions.extend([{"title": item.get("title"), "source": "reverb"} for item in items if item.get("title")])

    ranked = []
    seen = set()
    for item in suggestions:
        title = item.get("title")
        if not title:
            continue
        normalized = title.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ranked.append((score_title(title, item.get("source")), title))

    ranked.sort(key=lambda x: (-x[0], x[1].lower()))
    deduped = [title for _, title in ranked[:limit]]

    set_cache(cache_key, deduped)
    return deduped

def render_type_fields(asset_type, details, key_prefix, currency_code, currency_symbol, currency_rate, weight_unit):
    details = details or {}
    updated = {}
    col1, col2 = st.columns(2)

    def text_field(label, key, placeholder=""):
        return st.text_input(label, value=str(details.get(key, "")), key=f"{key_prefix}_{key}", placeholder=placeholder)

    def number_field(label, key, min_value=None, max_value=None, step=1.0, fmt=None):
        current = details.get(key)
        if current in (None, ""):
            current = 0.0
        return st.number_input(label, value=float(current), min_value=min_value, max_value=max_value, step=step, format=fmt, key=f"{key_prefix}_{key}")

    def weight_field():
        current = details.get("weight_troy_oz")
        display_value = weight_to_display(current if current not in (None, "") else 0.0, weight_unit)
        entered = st.number_input(
            get_weight_label(weight_unit),
            value=float(display_value),
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key=f"{key_prefix}_weight_troy_oz"
        )
        return weight_from_display(entered, weight_unit)

    def cost_basis_field():
        current = details.get("cost_basis")
        if current in (None, ""):
            current = 0.0
        display_value = to_display_currency(float(current), currency_rate)
        entered = st.number_input(
            f"Cost Basis ({currency_code})",
            value=float(display_value),
            min_value=0.0,
            step=0.01,
            format="%.2f",
            key=f"{key_prefix}_cost_basis"
        )
        return from_display_currency(entered, currency_rate)

    def date_field(label, key):
        return st.text_input(label, value=str(details.get(key, "")), key=f"{key_prefix}_{key}", placeholder="YYYY-MM-DD")

    with col1:
        if asset_type in ["Gold", "Silver", "Copper", "Platinum", "Palladium"]:
            updated["weight_troy_oz"] = weight_field()
            updated["purity"] = text_field("Purity (e.g., 24K, .999)", "purity")
            updated["mint"] = text_field("Mint", "mint")
        elif asset_type == "Guitar":
            updated["make"] = text_field("Make", "make", "e.g., Fender")
            updated["model"] = text_field("Model", "model", "e.g., Stratocaster")
            updated["year"] = text_field("Year", "year", "e.g., 1965")
        elif asset_type == "Watch":
            updated["make"] = text_field("Brand", "make")
            updated["model"] = text_field("Model", "model")
            updated["year"] = text_field("Year", "year")
        elif asset_type == "Jewelry":
            updated["make"] = text_field("Brand", "make")
            updated["material"] = text_field("Material", "material", "e.g., Gold, Platinum")
            updated["stone"] = text_field("Stone / Gem", "stone", "e.g., Diamond")
            updated["year"] = text_field("Year", "year")
        elif asset_type == "Card":
            updated["set_name"] = text_field("Set / Series", "set_name")
            updated["year"] = text_field("Year", "year")
            updated["grade"] = text_field("Grade", "grade")
        elif asset_type == "Collectible":
            updated["make"] = text_field("Maker / Brand", "make")
            updated["model"] = text_field("Model / Series", "model")
            updated["year"] = text_field("Year", "year")
        elif asset_type in ["Vehicle", "Motorcycle", "RV"]:
            updated["make"] = text_field("Make", "make")
            updated["model"] = text_field("Model", "model")
            updated["year"] = text_field("Year", "year")
        elif asset_type == "Boat":
            updated["make"] = text_field("Make", "make")
            updated["model"] = text_field("Model", "model")
            updated["year"] = text_field("Year", "year")
        elif asset_type in ["Electronics", "Camera", "Appliance", "Equipment", "Furniture"]:
            updated["make"] = text_field("Brand", "make")
            updated["model"] = text_field("Model", "model")
            updated["year"] = text_field("Year", "year")
        elif asset_type == "Business":
            updated["industry"] = text_field("Industry", "industry")
            updated["entity"] = text_field("Entity / Structure", "entity")
            updated["ownership_pct"] = number_field("Ownership %", "ownership_pct", min_value=0.0, max_value=100.0, step=0.1, fmt="%.1f")
        elif asset_type == "Insurance Policy":
            updated["provider"] = text_field("Provider", "provider")
            updated["policy_number"] = text_field("Policy #", "policy_number")
            updated["coverage_amount"] = number_field(f"Coverage Amount ({currency_code})", "coverage_amount", min_value=0.0, step=0.01, fmt="%.2f")
        elif asset_type == "Art":
            updated["artist"] = text_field("Artist", "artist")
            updated["year"] = text_field("Year", "year")
            updated["medium"] = text_field("Medium", "medium")
        elif asset_type == "Real Estate":
            updated["location"] = text_field("Location", "location")
            updated["square_feet"] = number_field("Square Feet", "square_feet", min_value=0.0, step=1.0, fmt="%.0f")
            updated["year"] = text_field("Year Built", "year")
        elif asset_type == "Stock":
            updated["ticker_exchange"] = text_field("Exchange", "ticker_exchange", "e.g., NASDAQ")
            updated["purchase_date"] = date_field("Purchase Date", "purchase_date")
            updated["cost_basis"] = cost_basis_field()
        elif asset_type == "Crypto":
            updated["wallet"] = text_field("Wallet / Exchange", "wallet")
            updated["purchase_date"] = date_field("Purchase Date", "purchase_date")
            updated["cost_basis"] = cost_basis_field()
        else:
            updated["notes_extra"] = text_field("Extra Details", "notes_extra")

    with col2:
        if asset_type in ["Gold", "Silver", "Copper", "Platinum", "Palladium"]:
            updated["year"] = text_field("Year", "year")
            updated["serial"] = text_field("Serial / Bar #", "serial")
        elif asset_type == "Guitar":
            updated["serial"] = text_field("Serial #", "serial")
            updated["condition_notes"] = text_field("Condition Notes", "condition_notes")
        elif asset_type == "Watch":
            updated["serial"] = text_field("Serial / Ref #", "serial")
            updated["band"] = text_field("Band / Strap", "band")
        elif asset_type == "Jewelry":
            updated["serial"] = text_field("Certificate / ID", "serial")
            updated["condition_notes"] = text_field("Condition Notes", "condition_notes")
        elif asset_type == "Card":
            updated["grading_company"] = text_field("Grading Company", "grading_company")
            updated["serial"] = text_field("Serial / Cert #", "serial")
        elif asset_type == "Collectible":
            updated["serial"] = text_field("Serial / Certificate", "serial")
            updated["condition_notes"] = text_field("Condition Notes", "condition_notes")
        elif asset_type in ["Vehicle", "Motorcycle", "RV"]:
            updated["vin"] = text_field("VIN", "vin")
            updated["mileage"] = number_field("Mileage", "mileage", min_value=0.0, step=1.0, fmt="%.0f")
        elif asset_type == "Boat":
            updated["hull_id"] = text_field("Hull ID", "hull_id")
            updated["engine_hours"] = number_field("Engine Hours", "engine_hours", min_value=0.0, step=1.0, fmt="%.0f")
        elif asset_type in ["Electronics", "Camera", "Appliance", "Equipment", "Furniture"]:
            updated["serial"] = text_field("Serial #", "serial")
            updated["condition_notes"] = text_field("Condition Notes", "condition_notes")
        elif asset_type == "Business":
            updated["valuation_method"] = text_field("Valuation Method", "valuation_method", "e.g., EBITDA")
            updated["notes_extra"] = text_field("Notes", "notes_extra")
        elif asset_type == "Insurance Policy":
            updated["renewal_date"] = date_field("Renewal Date", "renewal_date")
            updated["beneficiary"] = text_field("Beneficiary", "beneficiary")
        elif asset_type == "Art":
            updated["dimensions"] = text_field("Dimensions", "dimensions", "e.g., 24x36 in")
            updated["serial"] = text_field("Certificate / ID", "serial")
        elif asset_type == "Real Estate":
            updated["purchase_date"] = date_field("Purchase Date", "purchase_date")
            updated["cost_basis"] = cost_basis_field()
        elif asset_type == "Stock":
            updated["notes_extra"] = text_field("Notes", "notes_extra")
        elif asset_type == "Crypto":
            updated["notes_extra"] = text_field("Notes", "notes_extra")
        else:
            updated["condition_notes"] = text_field("Condition Notes", "condition_notes")

    return prune_details(updated)

def render_wealth_fields(wealth, key_prefix, currency_code, currency_symbol, currency_rate, entity_options):
    wealth = wealth or {}
    updated = {}
    col1, col2 = st.columns(2)
    entity_names = [e for e in entity_options if e]
    if not entity_names:
        entity_names = ["Personal"]

    with col1:
        owner_value = wealth.get("owner_entity") or (entity_names[0] if entity_names else "Personal")
        entity_choices = list(entity_names)
        if owner_value and owner_value not in entity_choices:
            entity_choices.append(owner_value)
        entity_choices.append("Custom")
        try:
            owner_index = entity_choices.index(owner_value)
        except ValueError:
            owner_index = 0
        selected_owner = st.selectbox(
            "Owner / Entity",
            entity_choices,
            index=owner_index,
            key=f"{key_prefix}_owner_entity"
        )
        if selected_owner == "Custom":
            custom_owner = st.text_input(
                "Custom Owner / Entity",
                value=str(wealth.get("owner_entity", "")),
                key=f"{key_prefix}_owner_entity_custom",
                placeholder="e.g., Family Trust"
            )
            updated["owner_entity"] = normalize_entity_name(custom_owner)
        else:
            updated["owner_entity"] = selected_owner
        updated["custodian"] = st.text_input(
            "Custodian / Account",
            value=str(wealth.get("custodian", "")),
            key=f"{key_prefix}_custodian",
            placeholder="e.g., Vanguard, Safe Deposit Box"
        )
        updated["beneficiary"] = st.text_input(
            "Beneficiary",
            value=str(wealth.get("beneficiary", "")),
            key=f"{key_prefix}_beneficiary",
            placeholder="e.g., Family Trust"
        )

    with col2:
        liquidity_current = wealth.get("liquidity_horizon") or WEALTH_LIQUIDITY_OPTIONS[1]
        if liquidity_current not in WEALTH_LIQUIDITY_OPTIONS:
            liquidity_current = WEALTH_LIQUIDITY_OPTIONS[1]
        updated["liquidity_horizon"] = st.selectbox(
            "Liquidity Horizon",
            WEALTH_LIQUIDITY_OPTIONS,
            index=WEALTH_LIQUIDITY_OPTIONS.index(liquidity_current),
            key=f"{key_prefix}_liquidity"
        )
        insured_current = wealth.get("insured_value", 0.0)
        insured_display = to_display_currency(float(insured_current or 0.0), currency_rate)
        insured_entered = st.number_input(
            f"Insured Value ({currency_code})",
            min_value=0.0,
            value=float(insured_display),
            step=0.01,
            format="%.2f",
            key=f"{key_prefix}_insured_value"
        )
        updated["insured_value"] = from_display_currency(insured_entered, currency_rate)

        review_raw = wealth.get("review_date")
        review_enabled = st.checkbox(
            "Set review date",
            value=bool(review_raw),
            key=f"{key_prefix}_review_enable"
        )
        if review_enabled:
            try:
                review_dt = datetime.fromisoformat(str(review_raw)).date() if review_raw else datetime.now().date()
            except Exception:
                review_dt = datetime.now().date()
            picked = st.date_input(
                "Next Review Date",
                value=review_dt,
                key=f"{key_prefix}_review_date"
            )
            updated["review_date"] = picked.isoformat()
        else:
            updated["review_date"] = ""

    split_existing = wealth.get("ownership_split") if isinstance(wealth.get("ownership_split"), dict) else {}
    split_enabled = st.checkbox(
        "Split ownership across entities",
        value=bool(split_existing),
        key=f"{key_prefix}_split_enable"
    )
    if split_enabled:
        st.caption("Enter ownership percentages by entity (aim for 100%).")
        split_inputs = {}
        split_cols = st.columns(2)
        for idx, name in enumerate(entity_names):
            current_pct = float(split_existing.get(name, 0.0) or 0.0)
            with split_cols[idx % 2]:
                split_inputs[name] = st.number_input(
                    f"{name} %",
                    min_value=0.0,
                    max_value=100.0,
                    value=current_pct,
                    step=1.0,
                    key=f"{key_prefix}_split_{name}"
                )
        total_pct = sum(split_inputs.values())
        if total_pct > 0 and abs(total_pct - 100.0) > 0.5:
            st.warning(f"Ownership split totals {total_pct:.1f}% (aim for 100%).")
        updated_split = {name: pct for name, pct in split_inputs.items() if pct > 0}
        if updated_split:
            updated["ownership_split"] = updated_split

    return prune_details(updated)

def build_demo_portfolio():
    now = str(datetime.now())
    return [
        {
            "name": "Gold Bar 1 oz",
            "type": "Gold",
            "qty": 1,
            "condition": "Mint",
            "ticker": None,
            "market_price": 2000.0,
            "images": [],
            "image_url": search_asset_image("gold bar"),
            "notes": "Demo asset",
            "details": {
                "weight_troy_oz": 1.0,
                "purity": ".999",
                "mint": "Royal Mint"
            },
            "wealth": {
                "owner_entity": "Personal",
                "liquidity_horizon": "Long (5y+)",
                "insured_value": 2000.0
            },
            "added": now
        },
        {
            "name": "Fender Stratocaster 1965",
            "type": "Guitar",
            "qty": 1,
            "condition": "Very Good",
            "ticker": None,
            "market_price": 8500.0,
            "images": [],
            "image_url": search_asset_image("fender stratocaster 1965"),
            "notes": "Demo asset",
            "details": {
                "make": "Fender",
                "model": "Stratocaster",
                "year": "1965",
                "serial": "V123456"
            },
            "wealth": {
                "owner_entity": "Trust",
                "custodian": "Vault Storage",
                "liquidity_horizon": "Medium (1-5y)",
                "insured_value": 8500.0
            },
            "added": now
        },
        {
            "name": "Apple Stock",
            "type": "Stock",
            "qty": 20,
            "condition": "Excellent",
            "ticker": "AAPL",
            "market_price": 180.0,
            "images": [],
            "image_url": search_asset_image("apple stock"),
            "notes": "Demo asset",
            "details": {
                "ticker_exchange": "NASDAQ",
                "purchase_date": "2022-01-01",
                "cost_basis": 2500.0
            },
            "wealth": {
                "owner_entity": "Personal",
                "custodian": "Brokerage",
                "liquidity_horizon": "Immediate (0-1y)"
            },
            "added": now
        },
        {
            "name": "Bitcoin Holdings",
            "type": "Crypto",
            "qty": 1,
            "condition": "Excellent",
            "ticker": None,
            "market_price": 40000.0,
            "images": [],
            "image_url": search_asset_image("bitcoin"),
            "notes": "Demo asset",
            "details": {
                "wallet": "Ledger Nano",
                "purchase_date": "2021-05-10",
                "cost_basis": 15000.0
            },
            "wealth": {
                "owner_entity": "Personal",
                "custodian": "Cold Storage",
                "liquidity_horizon": "Medium (1-5y)"
            },
            "added": now
        },
        {
            "name": "Rental Property",
            "type": "Real Estate",
            "qty": 1,
            "condition": "Good",
            "ticker": None,
            "market_price": 350000.0,
            "images": [],
            "image_url": search_asset_image("rental property"),
            "notes": "Demo asset",
            "details": {
                "location": "Auckland",
                "square_feet": 1200,
                "year": "2008",
                "purchase_date": "2018-05-12",
                "cost_basis": 300000.0
            },
            "wealth": {
                "owner_entity": "Joint",
                "liquidity_horizon": "Illiquid",
                "insured_value": 300000.0
            },
            "added": now
        }
    ]

# ==============================
# IMAGE SEARCH FUNCTION
# ==============================
def search_asset_image(query, max_results=1):
    """Search for asset images using Bing Image Search or fallback to placeholder"""
    try:
        # Try to search using duckduckgo or similar free service
        # For now, return curated URLs for common assets
        curated_images = {
            "mtg black lotus": "https://cards.scryfall.io/large/front/b/d/bd8fa327-dd41-4737-8f19-2cf5eb1f7cdd.jpg?1614638838",
            "gold sovereign coin": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/2022_Sovereign_obverse.jpg/440px-2022_Sovereign_obverse.jpg",
            "fender stratocaster 1965": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/1965_Fender_Stratocaster.jpg/440px-1965_Fender_Stratocaster.jpg",
            "apple stock": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1667px-Apple_logo_black.svg.png",
            "vintage rolex": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Rolex_Submariner_Date_116610LN.jpg/440px-Rolex_Submariner_Date_116610LN.jpg",
            "gold": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Gold_nugget_%28Australia%29_4_%2816848647509%29.jpg/440px-Gold_nugget_%28Australia%29_4_%2816848647509%29.jpg",
            "silver": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Silver_crystal.jpg/440px-Silver_crystal.jpg",
            "bitcoin": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1024px-Bitcoin.svg.png",
            "ethereum": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Ethereum_logo_2014.svg/1257px-Ethereum_logo_2014.svg.png",
            "collectible": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Pokemon_TCG_card_back.jpg/440px-Pokemon_TCG_card_back.jpg",
            "guitar": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Gibson_Les_Paul_Standard_2019.jpg/440px-Gibson_Les_Paul_Standard_2019.jpg",
            "watch": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Rolex_Submariner_Date_116610LN.jpg/440px-Rolex_Submariner_Date_116610LN.jpg",
            "art": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg/402px-Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg"
        }
        
        query_lower = query.lower()
        
        # Check curated list first
        for key, url in curated_images.items():
            if key in query_lower:
                return url
        
        # Return a generic placeholder based on asset type
        type_placeholders = {
            "stock": "https://cdn-icons-png.flaticon.com/512/4221/4221971.png",
            "crypto": "https://cdn-icons-png.flaticon.com/512/6134/6134347.png",
            "gold": curated_images["gold"],
            "silver": curated_images["silver"],
            "real estate": "https://cdn-icons-png.flaticon.com/512/6192/6192027.png",
            "other": "https://cdn-icons-png.flaticon.com/512/1170/1170678.png"
        }
        
        return type_placeholders.get(query_lower.split()[0] if query_lower else "other", 
                                     "https://cdn-icons-png.flaticon.com/512/1170/1170678.png")
    except:
        return "https://cdn-icons-png.flaticon.com/512/1170/1170678.png"

# ==============================
# IMAGE HELPERS
# ==============================
def encode_uploaded_images(files):
    encoded = []
    for f in files:
        data = f.getvalue()
        if not data:
            continue
        encoded.append({
            "name": f.name,
            "mime": f.type or "image/png",
            "data": base64.b64encode(data).decode("utf-8")
        })
    return encoded

def normalize_for_moderation(value):
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def contains_terms(text, terms):
    normalized = normalize_for_moderation(text)
    if not normalized:
        return False
    padded = f" {normalized} "
    for term in terms:
        term_norm = normalize_for_moderation(term)
        if not term_norm:
            continue
        if f" {term_norm} " in padded or term_norm in normalized:
            return True
    return False

def detect_community_violations(text):
    violations = []
    if contains_terms(text, COMMUNITY_PROFANITY_TERMS):
        violations.append("profanity")
    if contains_terms(text, COMMUNITY_EXPLICIT_TERMS):
        violations.append("explicit")
    if contains_terms(text, COMMUNITY_RESTRICTED_TERMS):
        violations.append("restricted")
    return violations

def validate_community_text(content):
    return detect_community_violations(content)

def validate_listing_images(files):
    if not files:
        return None
    if len(files) > MAX_LISTING_IMAGES:
        return f"Limit listing photos to {MAX_LISTING_IMAGES} images."
    total_bytes = 0
    for f in files:
        size = getattr(f, "size", None)
        if size:
            total_bytes += size
            if size > MAX_LISTING_IMAGE_MB * 1024 * 1024:
                return f"Each image must be under {MAX_LISTING_IMAGE_MB} MB."
        name = str(getattr(f, "name", "")).lower()
        if any(term in name for term in COMMUNITY_IMAGE_FILENAME_BLOCKLIST):
            return "Image filename appears to include restricted content."
    if total_bytes and total_bytes > MAX_LISTING_IMAGE_TOTAL_MB * 1024 * 1024:
        return f"Total image upload must be under {MAX_LISTING_IMAGE_TOTAL_MB} MB."
    return None

def persist_market_watchlist(db_obj, username, watchlist):
    if not username:
        return
    record = ensure_user_record(db_obj, username)
    settings = record.get("settings", {})
    settings["market_watchlist"] = sorted([str(item) for item in watchlist if item])
    record["settings"] = settings
    save_data(db_obj)

def persist_market_saved_searches(db_obj, username, searches):
    if not username:
        return
    record = ensure_user_record(db_obj, username)
    settings = record.get("settings", {})
    settings["market_saved_searches"] = searches
    record["settings"] = settings
    save_data(db_obj)

def send_alert_email(settings, subject, body):
    recipient = settings.get("market_alert_email", "").strip()
    host = get_effective_setting(settings, "smtp_host", "SMTP_HOST")
    user = get_effective_setting(settings, "smtp_user", "SMTP_USER")
    password = get_effective_setting(settings, "smtp_password", "SMTP_PASSWORD")
    if not recipient or not host or not user or not password:
        return "Email settings are incomplete."
    try:
        port_value = get_effective_setting(settings, "smtp_port", "SMTP_PORT") or settings.get("smtp_port", 587)
        port = int(port_value)
    except Exception:
        port = 587
    smtp_tls_value = get_effective_setting(settings, "smtp_use_tls", "SMTP_USE_TLS")
    use_tls = bool(settings.get("smtp_use_tls", True))
    if smtp_tls_value not in (None, ""):
        use_tls = str(smtp_tls_value).strip().lower() not in {"0", "false", "no"}
    msg = f"Subject: {subject}\nTo: {recipient}\nFrom: {user}\n\n{body}"
    try:
        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.starttls(context=context)
                server.login(user, password)
                server.sendmail(user, [recipient], msg)
        else:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=10) as server:
                server.login(user, password)
                server.sendmail(user, [recipient], msg)
        return None
    except Exception as exc:
        return str(exc)

def build_alert_notification_payload(alerts):
    if not alerts:
        return None, None
    total_new = sum(max(0, int(alert.get("count", 0) or 0)) for alert in alerts)
    search_names = [str(alert.get("name") or "Saved Search").strip() for alert in alerts]
    search_count = len(search_names)
    if search_count == 0:
        return None, None
    names_display = ", ".join(search_names[:3])
    if search_count > 3:
        names_display = f"{names_display} +{search_count - 3} more"
    title = f"WealthPulse Alerts ({total_new} new)"
    body = f"{total_new} new listing(s) across {search_count} search(es): {names_display}"
    return title, body

def build_alert_signature(alerts):
    parts = []
    for alert in alerts:
        name = str(alert.get("name") or "").strip().lower()
        count = int(alert.get("count", 0) or 0)
        parts.append(f"{name}:{count}")
    return "|".join(sorted(parts))

def trigger_browser_notifications(alerts):
    title, body = build_alert_notification_payload(alerts)
    if not title:
        return
    payload = {
        "title": title,
        "body": body
    }
    components.html(
        f"""
        <script>
        (function() {{
            if (!("Notification" in window)) {{
                return;
            }}
            const payload = {json.dumps(payload)};
            const fire = () => {{
                if (Notification.permission !== "granted") {{
                    return;
                }}
                try {{
                    new Notification(payload.title, {{ body: payload.body }});
                }} catch (err) {{}}
            }};
            if (Notification.permission === "granted") {{
                fire();
            }} else if (Notification.permission === "default") {{
                Notification.requestPermission().then(permission => {{
                    if (permission === "granted") {{
                        fire();
                    }}
                }});
            }}
        }})();
        </script>
        """,
        height=0
    )

def get_asset_image(asset):
    images = asset.get("images") or []
    if images:
        first = images[0]
        if isinstance(first, dict) and "data" in first:
            mime = first.get("mime") or "image/png"
            data = first["data"]
            try:
                return {
                    "src": f"data:{mime};base64,{data}",
                    "bytes": base64.b64decode(data)
                }
            except Exception:
                pass
    url = asset.get("image_url") or search_asset_image(asset.get("name", ""))
    return {"src": url, "bytes": url}

# ==============================
# UTIL: Persistence
# ==============================
def parse_added_date(value):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.min

# ==============================
def load_local_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            corrupt_path = f"{DATA_FILE}.corrupt-{timestamp}"
            try:
                os.replace(DATA_FILE, corrupt_path)
                st.warning(f"Data file was unreadable. A backup was saved to {corrupt_path}. Starting fresh.")
            except Exception:
                st.warning("Data file was unreadable. Starting with an empty portfolio.")
        except Exception:
            st.warning("Unable to read data file. Starting with an empty portfolio.")
    return {}

def get_storage_settings_from_secrets():
    return {
        "supabase_url": get_secret_value("SUPABASE_URL", ""),
        "supabase_anon_key": get_secret_value("SUPABASE_ANON_KEY", ""),
        "supabase_service_key": get_secret_value("SUPABASE_SERVICE_KEY", ""),
        "supabase_use_service_role": secret_flag("SUPABASE_USE_SERVICE_ROLE", True)
    }

def load_data_from_supabase(settings):
    if not supabase_enabled(settings):
        return None, "Supabase is not configured."
    rows, err = supabase_select(settings, APP_STORAGE_TABLE, order="username.asc", use_service_key=True)
    if err:
        return None, err
    db_obj = {}
    for row in rows or []:
        username = row.get("username")
        record = row.get("data")
        if not username:
            continue
        if isinstance(record, str):
            try:
                record = json.loads(record)
            except Exception:
                record = {}
        if not isinstance(record, dict):
            record = {}
        db_obj[username] = record
    return db_obj, None

def scrub_sensitive_settings(record):
    if not isinstance(record, dict):
        return
    settings = record.get("settings")
    if not isinstance(settings, dict):
        return
    sensitive_keys = {
        "metalprice_api_key": "METALPRICE_API_KEY",
        "freegoldprice_api_key": "FREEGOLDPRICE_API_KEY",
        "metals_dev_api_key": "METALS_DEV_API_KEY",
        "news_api_key": "NEWS_API_KEY",
        "ebay_client_id": "EBAY_CLIENT_ID",
        "ebay_client_secret": "EBAY_CLIENT_SECRET",
        "reverb_api_token": "REVERB_API_TOKEN",
        "smtp_host": "SMTP_HOST",
        "smtp_port": "SMTP_PORT",
        "smtp_user": "SMTP_USER",
        "smtp_password": "SMTP_PASSWORD",
        "smtp_use_tls": "SMTP_USE_TLS"
    }
    for key, secret_name in sensitive_keys.items():
        if get_secret_value(secret_name) not in (None, ""):
            settings[key] = ""
    record["settings"] = settings

def scrub_sensitive_meta(db_obj):
    meta = db_obj.get("_meta")
    if not isinstance(meta, dict):
        return
    config = meta.get("community_config")
    if not isinstance(config, dict):
        return
    if get_secret_value("SUPABASE_URL") not in (None, ""):
        config["supabase_url"] = ""
    if get_secret_value("SUPABASE_ANON_KEY") not in (None, ""):
        config["supabase_anon_key"] = ""
    if get_secret_value("SUPABASE_SERVICE_KEY") not in (None, ""):
        config["supabase_service_key"] = ""
    meta["community_config"] = config

def sync_db_to_supabase(settings, db_obj):
    if not supabase_enabled(settings):
        return "Supabase is not configured."
    if not isinstance(db_obj, dict):
        return "Invalid data for sync."
    scrub_sensitive_meta(db_obj)
    for username, record in db_obj.items():
        if not isinstance(record, dict):
            continue
        scrub_sensitive_settings(record)
        payload = {
            "username": username,
            "data": record,
            "updated_at": datetime.now().isoformat()
        }
        _, err = supabase_insert(settings, APP_STORAGE_TABLE, payload, upsert=True, use_service_key=True)
        if err:
            return err
    return None

def load_data():
    if app_storage_enabled():
        storage_settings = get_storage_settings_from_secrets()
        data, err = load_data_from_supabase(storage_settings)
        if data is not None:
            return data
        st.warning(f"Supabase app storage unavailable ({err}). Falling back to local storage.")
    local_data = load_local_data()
    meta_config = {}
    if isinstance(local_data, dict):
        meta = local_data.get("_meta")
        if isinstance(meta, dict):
            meta_config = meta.get("community_config") or {}
    if app_storage_enabled(meta_config):
        data, err = load_data_from_supabase(meta_config)
        if data is not None:
            return data
        st.warning(f"Supabase app storage unavailable ({err}). Using local storage.")
    return local_data

def save_data(data):
    if app_storage_enabled(get_community_settings(data)):
        storage_settings = get_community_settings(data)
        sync_error = sync_db_to_supabase(storage_settings, data)
        if sync_error:
            st.warning(f"Supabase sync failed: {sync_error}. Writing to local file as backup.")
        else:
            if not secret_flag("APP_STORAGE_LOCAL_CACHE", False):
                return
    scrub_sensitive_meta(data)
    dir_name = os.path.dirname(DATA_FILE)
    fd, tmp_path = tempfile.mkstemp(prefix=".wealth_data_", suffix=".tmp", dir=dir_name)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, DATA_FILE)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def get_supabase_config(settings):
    url, _ = resolve_setting(settings, "supabase_url", "SUPABASE_URL")
    anon_key, _ = resolve_setting(settings, "supabase_anon_key", "SUPABASE_ANON_KEY")
    service_key, _ = resolve_setting(settings, "supabase_service_key", "SUPABASE_SERVICE_KEY")
    url = (url or "").strip()
    anon_key = (anon_key or "").strip()
    service_key = (service_key or "").strip()
    if url.endswith("/"):
        url = url[:-1]
    return url, anon_key, service_key

def supabase_enabled(settings):
    url, anon_key, service_key = get_supabase_config(settings)
    if settings and (settings.get("supabase_use_service_role") or secret_flag("SUPABASE_USE_SERVICE_ROLE", False)):
        return bool(url and service_key)
    return bool(url and anon_key)

def supabase_headers(api_key, prefer=None, auth_token=None):
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {auth_token or api_key}"
    }
    if prefer:
        headers["Prefer"] = prefer
        headers["Content-Type"] = "application/json"
    return headers

def supabase_request(settings, method, table, params=None, payload=None, use_service_key=False, prefer=None, auth_token=None):
    url, anon_key, service_key = get_supabase_config(settings)
    if auth_token:
        if not anon_key:
            return None, "Supabase anon key is required for auth requests."
        api_key = anon_key
    else:
        use_service = use_service_key or (settings.get("supabase_use_service_role") if settings else False) or secret_flag("SUPABASE_USE_SERVICE_ROLE", False)
        api_key = service_key if use_service and service_key else anon_key
    if not url or not api_key:
        return None, "Supabase is not configured."
    endpoint = f"{url}/rest/v1/{table}"
    prefer_value = prefer
    if prefer_value is None and method in ("POST", "PATCH", "PUT"):
        prefer_value = "return=representation"
    try:
        response = requests.request(
            method,
            endpoint,
            headers=supabase_headers(api_key, prefer=prefer_value, auth_token=auth_token),
            params=params,
            json=payload,
            timeout=SUPABASE_TIMEOUT
        )
        if not response.ok:
            return None, f"{response.status_code}: {response.text[:300]}"
        if response.text:
            return response.json(), None
        return [], None
    except Exception as exc:
        return None, str(exc)

def supabase_select(settings, table, filters=None, limit=None, order=None, use_service_key=False, auth_token=None):
    params = {"select": "*"}
    if limit:
        params["limit"] = str(limit)
    if order:
        params["order"] = order
    if filters:
        for col, op, value in filters:
            params[col] = f"{op}.{value}"
    return supabase_request(settings, "GET", table, params=params, use_service_key=use_service_key, auth_token=auth_token)

def supabase_insert(settings, table, payload, upsert=False, use_service_key=False, auth_token=None):
    params = None
    prefer = None
    if upsert:
        params = {"on_conflict": "username"}
        prefer = "return=representation, resolution=merge-duplicates"
    data, err = supabase_request(settings, "POST", table, params=params, payload=payload, prefer=prefer, use_service_key=use_service_key, auth_token=auth_token)
    return data, err

def supabase_update(settings, table, filters, payload, use_service_key=False, auth_token=None):
    params = {}
    for col, op, value in filters:
        params[col] = f"{op}.{value}"
    return supabase_request(settings, "PATCH", table, params=params, payload=payload, use_service_key=use_service_key, auth_token=auth_token)

def supabase_delete(settings, table, filters, use_service_key=False, auth_token=None):
    params = {}
    for col, op, value in filters:
        params[col] = f"{op}.{value}"
    return supabase_request(settings, "DELETE", table, params=params, use_service_key=use_service_key, auth_token=auth_token)

def supabase_check_table(settings, table="community_posts", use_service_key=None, auth_token=None):
    if not supabase_enabled(settings):
        return False, "Supabase is not configured."
    if use_service_key is None:
        use_service_key = bool(settings.get("supabase_use_service_role")) or secret_flag("SUPABASE_USE_SERVICE_ROLE", False)
    data, err = supabase_select(settings, table, limit=1, use_service_key=use_service_key, auth_token=auth_token)
    if err:
        return False, err
    return True, None

def supabase_auth_required(settings):
    return secret_flag("SUPABASE_AUTH_REQUIRED", False) or bool(settings.get("supabase_auth_required", False))

def get_supabase_auth_state():
    return st.session_state.get("supabase_auth") or {}

def set_supabase_auth_state(state):
    st.session_state.supabase_auth = state or {}

def clear_supabase_auth_state():
    if "supabase_auth" in st.session_state:
        st.session_state.pop("supabase_auth", None)

def supabase_auth_sign_in(settings, email, password):
    url, anon_key, _ = get_supabase_config(settings)
    if not url or not anon_key:
        return None, "Supabase anon key is required for auth."
    endpoint = f"{url}/auth/v1/token?grant_type=password"
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
    payload = {"email": email, "password": password}
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=SUPABASE_TIMEOUT)
        if not response.ok:
            return None, f"{response.status_code}: {response.text[:200]}"
        return response.json(), None
    except Exception as exc:
        return None, str(exc)

def supabase_auth_sign_up(settings, email, password):
    url, anon_key, _ = get_supabase_config(settings)
    if not url or not anon_key:
        return None, "Supabase anon key is required for auth."
    endpoint = f"{url}/auth/v1/signup"
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
    payload = {"email": email, "password": password}
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=SUPABASE_TIMEOUT)
        if not response.ok:
            return None, f"{response.status_code}: {response.text[:200]}"
        return response.json(), None
    except Exception as exc:
        return None, str(exc)

def supabase_auth_refresh(settings, refresh_token):
    url, anon_key, _ = get_supabase_config(settings)
    if not url or not anon_key:
        return None, "Supabase anon key is required for auth."
    endpoint = f"{url}/auth/v1/token?grant_type=refresh_token"
    headers = {"apikey": anon_key, "Content-Type": "application/json"}
    payload = {"refresh_token": refresh_token}
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=SUPABASE_TIMEOUT)
        if not response.ok:
            return None, f"{response.status_code}: {response.text[:200]}"
        return response.json(), None
    except Exception as exc:
        return None, str(exc)

def ensure_supabase_auth(settings):
    state = get_supabase_auth_state()
    if not state or not state.get("access_token"):
        return None
    expires_at = state.get("expires_at", 0)
    if expires_at and time.time() > float(expires_at) - 60:
        refresh_token = state.get("refresh_token")
        if not refresh_token:
            clear_supabase_auth_state()
            return None
        refreshed, err = supabase_auth_refresh(settings, refresh_token)
        if err or not refreshed:
            clear_supabase_auth_state()
            return None
        access_token = refreshed.get("access_token")
        refresh_token = refreshed.get("refresh_token") or refresh_token
        user = refreshed.get("user") or state.get("user")
        expires_in = refreshed.get("expires_in") or 3600
        state = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": time.time() + int(expires_in),
            "user": user
        }
        set_supabase_auth_state(state)
    return state

def get_supabase_access_token(settings):
    state = ensure_supabase_auth(settings)
    if not state:
        return None
    return state.get("access_token")

def get_supabase_auth_user(settings):
    state = ensure_supabase_auth(settings)
    if not state:
        return None
    return state.get("user")

def get_supabase_auth_user_id(settings):
    user = get_supabase_auth_user(settings)
    if not user:
        return None
    return user.get("id")

def get_supabase_auth_email(settings):
    user = get_supabase_auth_user(settings)
    if not user:
        return ""
    return user.get("email") or ""

def community_auth_token(settings):
    return get_supabase_access_token(settings)

def community_use_service_role(settings):
    return bool(settings.get("supabase_use_service_role")) or secret_flag("SUPABASE_USE_SERVICE_ROLE", False)

def community_require_auth(settings):
    if supabase_enabled(settings) and supabase_auth_required(settings):
        if not get_supabase_access_token(settings):
            return "Community sign-in required."
    return None

def supabase_check_tables(settings, tables, use_service_key=None, auth_token=None):
    results = []
    for table in tables:
        ok, err = supabase_check_table(settings, table, use_service_key=use_service_key, auth_token=auth_token)
        results.append((table, ok, err))
    return results

def supabase_check_column(settings, table, column, use_service_key=False, auth_token=None):
    params = {"select": column, "limit": "1"}
    _, err = supabase_request(settings, "GET", table, params=params, use_service_key=use_service_key, auth_token=auth_token)
    if err:
        return False, err
    return True, None

def supabase_check_columns(settings, table, columns, use_service_key=False, auth_token=None):
    results = []
    for column in columns:
        ok, err = supabase_check_column(settings, table, column, use_service_key=use_service_key, auth_token=auth_token)
        results.append((column, ok, err))
    return results

def render_checklist_results(results, checked_at=None):
    if checked_at:
        try:
            checked_dt = datetime.fromisoformat(str(checked_at))
            st.caption(f"Last checked: {checked_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception:
            st.caption(f"Last checked: {checked_at}")
    for table, ok, err in results:
        if ok:
            st.success(f"{table}: OK")
        else:
            if is_supabase_missing_column_error(err):
                st.warning(f"{table}: missing column")
                st.caption(f"Details: {err}")
            elif is_supabase_missing_table_error(err):
                st.error(f"{table}: missing table")
                st.caption(f"Details: {err}")
            else:
                st.error(f"{table}: error ({err})")

def is_supabase_missing_column_error(err):
    if not err:
        return False
    err_text = str(err).lower()
    return "column" in err_text and ("does not exist" in err_text or "not found" in err_text)

def build_community_migration_sql(missing_columns):
    if not missing_columns:
        return ""
    statements = []
    for column in missing_columns:
        column_type = COMMUNITY_POSTS_EXTRA_COLUMNS.get(column, "numeric")
        statements.append(f"ALTER TABLE public.community_posts ADD COLUMN IF NOT EXISTS {column} {column_type};")
    return "\n".join(statements)

def is_supabase_missing_table_error(err):
    if not err:
        return False
    err_text = str(err)
    return "PGRST205" in err_text or "Could not find the table" in err_text

def load_community_schema_sql():
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "supabase_community_schema.sql")
        with open(schema_path, "r") as f:
            return f.read()
    except Exception:
        return ""

def community_local_posts(db_obj):
    return get_forum_posts(db_obj)

def community_get_posts(settings, db_obj, limit=200):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return [], auth_err
        return supabase_select(
            settings,
            "community_posts",
            limit=limit,
            order="created_at.desc",
            auth_token=community_auth_token(settings)
        )
    return community_local_posts(db_obj), None

def community_get_comments(settings, db_obj, post_id):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return [], auth_err
        return supabase_select(
            settings,
            "community_comments",
            filters=[("post_id", "eq", post_id)],
            order="created_at.asc",
            auth_token=community_auth_token(settings)
        )
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == post_id:
            return post.get("comments", []), None
    return [], None

def community_get_bids(settings, db_obj, post_id):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return [], auth_err
        return supabase_select(
            settings,
            "community_bids",
            filters=[("post_id", "eq", post_id)],
            order="created_at.asc",
            auth_token=community_auth_token(settings)
        )
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == post_id:
            return post.get("bids", []), None
    return [], None

def community_get_offers(settings, db_obj, post_id):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return [], auth_err
        return supabase_select(
            settings,
            "community_offers",
            filters=[("post_id", "eq", post_id)],
            order="created_at.asc",
            auth_token=community_auth_token(settings)
        )
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == post_id:
            return post.get("offers", []), None
    return [], None

def community_create_post(settings, db_obj, post):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_insert(settings, "community_posts", post, auth_token=community_auth_token(settings))
    posts = community_local_posts(db_obj)
    posts.append(post)
    return [post], None

def community_update_post(settings, db_obj, post_id, payload):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_update(settings, "community_posts", [("id", "eq", post_id)], payload, auth_token=community_auth_token(settings))
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == post_id:
            post.update(payload)
            return [post], None
    return None, "Post not found."

def community_delete_post(settings, db_obj, post_id):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_delete(settings, "community_posts", [("id", "eq", post_id)], auth_token=community_auth_token(settings))
    posts = community_local_posts(db_obj)
    for post in list(posts):
        if post.get("id") == post_id:
            posts.remove(post)
            return [], None
    return None, "Post not found."

def community_add_comment(settings, db_obj, comment):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_insert(settings, "community_comments", comment, auth_token=community_auth_token(settings))
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == comment.get("post_id"):
            post.setdefault("comments", []).append(comment)
            return [comment], None
    return None, "Post not found."

def community_add_bid(settings, db_obj, bid):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_insert(settings, "community_bids", bid, auth_token=community_auth_token(settings))
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == bid.get("post_id"):
            post.setdefault("bids", []).append(bid)
            return [bid], None
    return None, "Post not found."

def community_add_offer(settings, db_obj, offer):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_insert(settings, "community_offers", offer, auth_token=community_auth_token(settings))
    posts = community_local_posts(db_obj)
    for post in posts:
        if post.get("id") == offer.get("post_id"):
            post.setdefault("offers", []).append(offer)
            return [offer], None
    return None, "Post not found."

def community_get_messages(settings, db_obj, username, box="inbox"):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return [], auth_err
        auth_id = get_supabase_auth_user_id(settings)
        if supabase_auth_required(settings) and auth_id:
            filters = [("recipient_id", "eq", auth_id)] if box == "inbox" else [("sender_id", "eq", auth_id)]
        else:
            filters = [("recipient", "eq", username)] if box == "inbox" else [("sender", "eq", username)]
        return supabase_select(settings, "community_messages", filters=filters, order="created_at.desc", auth_token=community_auth_token(settings))
    meta = get_meta(db_obj)
    messages = meta.get("messages", [])
    if box == "inbox":
        return [m for m in messages if m.get("recipient") == username], None
    return [m for m in messages if m.get("sender") == username], None

def community_send_message(settings, db_obj, message):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_insert(settings, "community_messages", message, auth_token=community_auth_token(settings))
    meta = get_meta(db_obj)
    if not message.get("id"):
        message["id"] = secrets.token_hex(6)
    meta.setdefault("messages", []).append(message)
    return [message], None

def community_mark_message_read(settings, db_obj, message_id):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_update(
            settings,
            "community_messages",
            [("id", "eq", message_id)],
            {"read_at": datetime.now().isoformat()},
            auth_token=community_auth_token(settings)
        )
    meta = get_meta(db_obj)
    for msg in meta.get("messages", []):
        if msg.get("id") == message_id:
            msg["read_at"] = datetime.now().isoformat()
            return [msg], None
    return None, "Message not found."

def community_get_roles(settings, db_obj):
    if supabase_enabled(settings):
        return supabase_select(settings, "community_roles", auth_token=community_auth_token(settings))
    meta = get_meta(db_obj)
    return meta.get("community_roles", []), None

def community_get_role(settings, db_obj, username):
    if st.session_state.get("is_admin"):
        return "admin"
    if supabase_enabled(settings):
        data, _ = supabase_select(settings, "community_roles", filters=[("username", "eq", username)], auth_token=community_auth_token(settings))
        if data:
            return data[0].get("role")
        return None
    meta = get_meta(db_obj)
    for role in meta.get("community_roles", []):
        if role.get("username") == username:
            return role.get("role")
    return None

def community_set_role(settings, db_obj, username, role):
    payload = {
        "username": username,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    if supabase_enabled(settings):
        if not community_use_service_role(settings):
            return None, "Service role key required for role management."
        return supabase_insert(settings, "community_roles", payload, upsert=True, use_service_key=True)
    meta = get_meta(db_obj)
    roles = meta.setdefault("community_roles", [])
    for entry in roles:
        if entry.get("username") == username:
            entry["role"] = role
            return [entry], None
    roles.append(payload)
    return [payload], None

def community_remove_role(settings, db_obj, username):
    if supabase_enabled(settings):
        if not community_use_service_role(settings):
            return None, "Service role key required for role management."
        return supabase_delete(settings, "community_roles", [("username", "eq", username)], use_service_key=True)
    meta = get_meta(db_obj)
    roles = meta.setdefault("community_roles", [])
    for entry in list(roles):
        if entry.get("username") == username:
            roles.remove(entry)
            return [], None
    return None, "Role not found."

def community_get_bans(settings, db_obj):
    if supabase_enabled(settings):
        return supabase_select(settings, "community_bans", auth_token=community_auth_token(settings))
    meta = get_meta(db_obj)
    return meta.get("community_bans", []), None

def community_is_banned(settings, db_obj, username):
    if supabase_enabled(settings):
        data, _ = supabase_select(settings, "community_bans", filters=[("username", "eq", username)], auth_token=community_auth_token(settings))
        return bool(data)
    meta = get_meta(db_obj)
    return any(entry.get("username") == username for entry in meta.get("community_bans", []))

def community_set_ban(settings, db_obj, username, reason):
    payload = {
        "username": username,
        "reason": reason,
        "created_at": datetime.now().isoformat()
    }
    if supabase_enabled(settings):
        if not community_use_service_role(settings):
            return None, "Service role key required for ban management."
        return supabase_insert(settings, "community_bans", payload, upsert=True, use_service_key=True)
    meta = get_meta(db_obj)
    bans = meta.setdefault("community_bans", [])
    for entry in bans:
        if entry.get("username") == username:
            entry["reason"] = reason
            return [entry], None
    bans.append(payload)
    return [payload], None

def community_remove_ban(settings, db_obj, username):
    if supabase_enabled(settings):
        if not community_use_service_role(settings):
            return None, "Service role key required for ban management."
        return supabase_delete(settings, "community_bans", [("username", "eq", username)], use_service_key=True)
    meta = get_meta(db_obj)
    bans = meta.setdefault("community_bans", [])
    for entry in list(bans):
        if entry.get("username") == username:
            bans.remove(entry)
            return [], None
    return None, "Ban not found."

def community_report_post(settings, db_obj, report):
    if supabase_enabled(settings):
        auth_err = community_require_auth(settings)
        if auth_err:
            return None, auth_err
        return supabase_insert(settings, "community_reports", report, auth_token=community_auth_token(settings))
    meta = get_meta(db_obj)
    meta.setdefault("community_reports", []).append(report)
    return [report], None

def community_get_reports(settings, db_obj):
    if supabase_enabled(settings):
        if not community_use_service_role(settings):
            return None, "Service role key required for moderation reports."
        return supabase_select(settings, "community_reports", order="created_at.desc", use_service_key=True)
    meta = get_meta(db_obj)
    return meta.get("community_reports", []), None

def community_clear_report(settings, db_obj, report_id):
    if supabase_enabled(settings):
        if not community_use_service_role(settings):
            return None, "Service role key required for moderation reports."
        return supabase_delete(settings, "community_reports", [("id", "eq", report_id)], use_service_key=True)
    meta = get_meta(db_obj)
    reports = meta.get("community_reports", [])
    for report in list(reports):
        if report.get("id") == report_id:
            reports.remove(report)
            return [], None
    return None, "Report not found."

def community_sync_user(settings, db_obj, username):
    if not supabase_enabled(settings):
        return None, None
    if supabase_auth_required(settings) and not community_auth_token(settings):
        return None, "Community auth required."
    auth_id = get_supabase_auth_user_id(settings)
    email = get_supabase_auth_email(settings)
    payload = {
        "username": username,
        "auth_id": auth_id,
        "email": email,
        "updated_at": datetime.now().isoformat()
    }
    return supabase_insert(settings, "community_users", payload, upsert=True, auth_token=community_auth_token(settings))

def community_fetch_user(settings, username):
    if not supabase_enabled(settings):
        return None
    data, _ = supabase_select(settings, "community_users", filters=[("username", "eq", username)], limit=1, auth_token=community_auth_token(settings))
    if data:
        record = data[0]
        if record.get("auth") and record.get("recovery"):
            return record
    return None

def community_lookup_user_auth_id(settings, username):
    if not supabase_enabled(settings):
        return None
    data, err = supabase_select(
        settings,
        "community_users",
        filters=[("username", "eq", username)],
        limit=1,
        auth_token=community_auth_token(settings)
    )
    if err or not data:
        return None
    return data[0].get("auth_id")
def load_remember_file():
    if not os.path.exists(REMEMBER_FILE):
        return None
    try:
        with open(REMEMBER_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None

def save_remember_file(payload):
    dir_name = os.path.dirname(REMEMBER_FILE)
    fd, tmp_path = tempfile.mkstemp(prefix=".remember_", suffix=".tmp", dir=dir_name)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, REMEMBER_FILE)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def clear_remember_file():
    if os.path.exists(REMEMBER_FILE):
        try:
            os.remove(REMEMBER_FILE)
        except Exception:
            pass

def hash_remember_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def get_login_security_state(db_obj):
    meta = get_meta(db_obj)
    state = meta.get("login_security")
    if not isinstance(state, dict):
        state = {}
        meta["login_security"] = state
    return state

def is_login_locked(db_obj, username):
    if not username:
        return False, None
    state = get_login_security_state(db_obj)
    record = state.get(username) or {}
    locked_until_raw = record.get("locked_until")
    if not locked_until_raw:
        return False, None
    try:
        locked_until = datetime.fromisoformat(str(locked_until_raw))
    except Exception:
        record["locked_until"] = None
        return False, None
    now = datetime.now()
    if locked_until > now:
        remaining = max(1, math.ceil((locked_until - now).total_seconds() / 60))
        return True, remaining
    record["locked_until"] = None
    record["count"] = 0
    return False, None

def record_login_failure(db_obj, username):
    if not username:
        return
    state = get_login_security_state(db_obj)
    record = state.get(username, {})
    now = datetime.now()
    last_failed_raw = record.get("last_failed_at")
    if last_failed_raw:
        try:
            last_failed = datetime.fromisoformat(str(last_failed_raw))
        except Exception:
            last_failed = None
        if last_failed and (now - last_failed).total_seconds() > LOGIN_FAILURE_WINDOW_MINUTES * 60:
            record["count"] = 0
    record["count"] = int(record.get("count", 0)) + 1
    record["last_failed_at"] = now.isoformat()
    if record["count"] >= LOGIN_MAX_ATTEMPTS:
        record["locked_until"] = (now + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)).isoformat()
        record["count"] = 0
    state[username] = record

def clear_login_failures(db_obj, username):
    if not username:
        return
    state = get_login_security_state(db_obj)
    if username in state:
        state.pop(username, None)

def issue_remember_token(record):
    token = secrets.token_urlsafe(24)
    expires = utc_now() + timedelta(days=REMEMBER_TOKEN_TTL_DAYS)
    record["remember_token"] = {
        "token_hash": hash_remember_token(token),
        "expires": expires.isoformat()
    }
    return token, expires

def clear_user_remember_token(db_obj, username):
    record = db_obj.get(username)
    if isinstance(record, dict):
        record.pop("remember_token", None)

def get_remembered_user(db_obj):
    payload = load_remember_file()
    if not payload:
        return None
    username = payload.get("username")
    token = payload.get("token")
    expiry_raw = payload.get("expires")
    if not username or not token:
        clear_remember_file()
        return None
    if expiry_raw:
        try:
            expiry_dt = datetime.fromisoformat(str(expiry_raw))
        except Exception:
            expiry_dt = None
        if expiry_dt:
            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            if expiry_dt < utc_now():
                clear_remember_file()
                clear_user_remember_token(db_obj, username)
                return None
    record = db_obj.get(username)
    if not isinstance(record, dict):
        clear_remember_file()
        return None
    stored = record.get("remember_token") or {}
    stored_hash = stored.get("token_hash")
    if stored_hash:
        if not secrets.compare_digest(stored_hash, hash_remember_token(token)):
            clear_remember_file()
            return None
    else:
        if stored.get("token") != token:
            clear_remember_file()
            return None
        stored["token_hash"] = hash_remember_token(token)
        stored.pop("token", None)
        record["remember_token"] = stored
        save_data(db_obj)
    return username

db = load_data()

# ==============================
# DELETE AND MODIFY FUNCTIONS
# ==============================
def delete_asset(asset_index):
    """Delete an asset from the portfolio"""
    user = st.session_state.user
    if user in db and "portfolio" in db[user]:
        if 0 <= asset_index < len(db[user]["portfolio"]):
            db[user]["portfolio"].pop(asset_index)
            save_data(db)
            if st.session_state.get("edit_inline_index") == asset_index:
                st.session_state.edit_inline_index = None
            st.success("Asset deleted successfully!")
            request_scroll_to_top()
            st.rerun()
    else:
        st.error("Error: Could not find asset to delete")

def modify_asset(asset_index):
    """Set up session state for modifying an asset"""
    user = st.session_state.user
    if user in db and "portfolio" in db[user]:
        if 0 <= asset_index < len(db[user]["portfolio"]):
            asset = db[user]["portfolio"][asset_index]
            st.session_state.selected_asset_index = asset_index
            st.session_state.modify_index = asset_index
            st.session_state.modify_name = asset["name"]
            st.session_state.modify_type = asset["type"]
            st.session_state.modify_qty = asset["qty"]
            st.session_state.modify_condition = asset["condition"]
            st.session_state.modify_ticker = asset.get("ticker", "")
            st.session_state.modify_market_price = asset.get("market_price", 0.0)
            st.session_state.modify_notes = asset.get("notes", "")
            st.session_state.show_modify_form = True

def save_modified_asset():
    """Save the modified asset"""
    user = st.session_state.user
    if (user in db and "portfolio" in db[user] and
        hasattr(st.session_state, 'modify_index')):

        idx = st.session_state.modify_index
        name_clean = (st.session_state.modify_name or "").strip()
        if not name_clean:
            st.error("Asset name cannot be empty.")
            return

        # Update the asset
        db[user]["portfolio"][idx] = {
            "name": name_clean,
            "type": st.session_state.modify_type,
            "qty": st.session_state.modify_qty,
            "condition": st.session_state.modify_condition,
            "ticker": st.session_state.modify_ticker if st.session_state.modify_ticker else None,
            "market_price": st.session_state.modify_market_price,
            "images": db[user]["portfolio"][idx].get("images", []),  # Keep existing images
            "image_url": search_asset_image(name_clean),  # Update image based on new name
            "notes": st.session_state.modify_notes,
            "details": db[user]["portfolio"][idx].get("details", {}),
            "wealth": db[user]["portfolio"][idx].get("wealth", {}),
            "added": db[user]["portfolio"][idx].get("added", str(datetime.now()))  # Keep original added date
        }
        
        # Clean up session state
        del st.session_state.modify_index
        del st.session_state.modify_name
        del st.session_state.modify_type
        del st.session_state.modify_qty
        del st.session_state.modify_condition
        del st.session_state.modify_ticker
        del st.session_state.modify_market_price
        del st.session_state.modify_notes
        st.session_state.show_modify_form = False
        
        save_data(db)
        st.success("Asset updated successfully!")
        request_scroll_to_top()
        st.rerun()

def cancel_modify():
    """Cancel the modification process"""
    if hasattr(st.session_state, 'modify_index'):
        del st.session_state.modify_index
    if hasattr(st.session_state, 'modify_name'):
        del st.session_state.modify_name
    if hasattr(st.session_state, 'modify_type'):
        del st.session_state.modify_type
    if hasattr(st.session_state, 'modify_qty'):
        del st.session_state.modify_qty
    if hasattr(st.session_state, 'modify_condition'):
        del st.session_state.modify_condition
    if hasattr(st.session_state, 'modify_ticker'):
        del st.session_state.modify_ticker
    if hasattr(st.session_state, 'modify_market_price'):
        del st.session_state.modify_market_price
    if hasattr(st.session_state, 'modify_notes'):
        del st.session_state.modify_notes
    
    st.session_state.show_modify_form = False
    st.rerun()

def request_delete(asset_index):
    st.session_state.delete_candidate = asset_index

def render_delete_confirmation(portfolio, currency_symbol, currency_rate):
    idx = st.session_state.get("delete_candidate")
    if idx is None or idx >= len(portfolio):
        return
    asset = portfolio[idx]
    name = asset.get("name", "Asset")
    value, _, _ = ai_valuation(asset)
    message = f"Delete {name} ({format_currency(value, currency_symbol, currency_rate)})? This cannot be undone."

    def render_delete_controls(key_suffix):
        st.warning(message)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Delete", key=f"confirm_delete_{key_suffix}"):
                st.session_state.delete_candidate = None
                delete_asset(idx)
        with col2:
            if st.button("Cancel", key=f"cancel_delete_{key_suffix}"):
                st.session_state.delete_candidate = None
                st.rerun()

    dialog_fn = getattr(st, "dialog", None)
    if callable(dialog_fn):
        dialog_obj = None
        try:
            dialog_obj = dialog_fn("Confirm Delete")
        except Exception:
            dialog_obj = None

        if dialog_obj and hasattr(dialog_obj, "__enter__"):
            with dialog_obj:
                render_delete_controls("dialog")
            return
        if callable(dialog_obj):
            @dialog_fn("Confirm Delete")
            def _confirm_dialog():
                render_delete_controls("dialog")
            _confirm_dialog()
            return

    render_delete_controls("inline")

def render_inline_edit_form(asset_index, asset, currency_code, currency_symbol, currency_rate, weight_unit):
    st.markdown("---")
    st.markdown("### Edit Asset (Inline)")
    with st.form(f"inline_edit_form_{asset_index}"):
        col1, col2 = st.columns(2)
        with col1:
            new_name_raw = st.text_input("Asset Name", value=asset["name"], key=f"inline_name_{asset_index}")
            new_name = new_name_raw.strip()
            inline_type_options = ASSET_TYPE_OPTIONS
            try:
                inline_type_index = inline_type_options.index(asset["type"])
            except ValueError:
                inline_type_index = len(inline_type_options) - 1
            new_type = st.selectbox(
                "Type",
                inline_type_options,
                index=inline_type_index,
                key=f"inline_type_{asset_index}"
            )
            new_qty = st.number_input("Quantity", min_value=1, value=asset["qty"], key=f"inline_qty_{asset_index}")
        with col2:
            new_condition = st.selectbox(
                "Condition",
                ["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"],
                index=["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"].index(asset["condition"]),
                key=f"inline_condition_{asset_index}"
            )
            new_ticker = st.text_input("Ticker (optional)", value=asset.get("ticker", "") or "", key=f"inline_ticker_{asset_index}")
            current_price_display = to_display_currency(asset.get("market_price", 0.0), currency_rate)
            new_market_price_display = st.number_input(
                f"Market Price per Unit ({currency_code})",
                min_value=0.0,
                value=float(current_price_display),
                step=0.01,
                key=f"inline_price_{asset_index}"
            )

        st.markdown("#### Type Details")
        detail_key_prefix = f"inline_{asset_index}_{new_type.replace(' ', '_').lower()}"
        new_details = render_type_fields(new_type, asset.get("details", {}), detail_key_prefix, currency_code, currency_symbol, currency_rate, weight_unit)

        country_code = get_country_code(user_settings)
        country_name = get_country_name(country_code)
        examples = ", ".join(get_local_entity_examples(country_code))
        local_hint = get_local_entity_hint(country_code)
        st.markdown("#### Wealth Management")
        st.caption(f"Founder tip for {country_name}: assign the right entity ({examples}) to keep clean separation.")
        st.caption(local_hint)
        wealth_key_prefix = f"inline_{asset_index}_wealth"
        new_wealth = render_wealth_fields(asset.get("wealth", {}), wealth_key_prefix, currency_code, currency_symbol, currency_rate, entity_names)

        new_notes = st.text_area("Notes", value=asset.get("notes", ""), key=f"inline_notes_{asset_index}")
        st.markdown("#### Update Image")
        new_image_url = st.text_input("Custom Image URL (optional)", key=f"inline_img_url_{asset_index}")
        new_images = st.file_uploader(
            "Upload New Images (Optional)",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            key=f"inline_images_{asset_index}"
        )

        col_save, col_cancel, col_delete = st.columns(3)
        save_changes = col_save.form_submit_button("Save Changes")
        cancel_edit = col_cancel.form_submit_button("Cancel")
        delete_btn = col_delete.form_submit_button("Delete")

        if save_changes:
            if not new_name:
                st.error("Asset name cannot be empty.")
            else:
                updated_images = asset.get("images", [])
                if new_images:
                    updated_images = encode_uploaded_images(new_images)
                portfolio[asset_index] = {
                    "name": new_name,
                    "type": new_type,
                    "qty": new_qty,
                    "condition": new_condition,
                    "ticker": new_ticker if new_ticker else None,
                    "market_price": from_display_currency(new_market_price_display, currency_rate),
                    "images": updated_images,
                    "image_url": new_image_url if new_image_url else search_asset_image(new_name),
                    "notes": new_notes,
                    "details": new_details,
                    "wealth": new_wealth,
                    "added": asset.get("added", str(datetime.now()))
                }
                save_data(db)
                st.session_state.edit_inline_index = None
                st.success("Asset updated successfully!")
                request_scroll_to_top()
                st.rerun()

        if cancel_edit:
            st.session_state.edit_inline_index = None
            st.rerun()

        if delete_btn:
            request_delete(asset_index)
            st.rerun()

# ==============================
# LOGIN WITH MODERN UI
# ==============================
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.show_modify_form = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "open_feedback_form" not in st.session_state:
    st.session_state.open_feedback_form = False
if "show_login_animation" not in st.session_state:
    st.session_state.show_login_animation = False
if "show_header_pulse" not in st.session_state:
    st.session_state.show_header_pulse = False

community_settings = get_community_settings(db)
if not st.session_state.user:
    remembered_user = get_remembered_user(db)
    if remembered_user:
        st.session_state.user = remembered_user
        st.session_state.show_header_pulse = True

if not st.session_state.user:
    render_login_logo()
    st.markdown("""
        <div style="text-align: center; padding: 2.5rem 1.5rem;">
            <h1 style="font-size: 2.1rem; margin-bottom: 0.4rem; color: var(--text);">WealthPulse</h1>
            <p style="color: var(--muted); font-size: 1.05rem; margin-bottom: 1.5rem;">
                Portfolio & Asset Intelligence
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                remember_me = st.checkbox("Remember me on this device")
                login = st.form_submit_button("Launch Dashboard", width="stretch")

            if login:
                record = db.get(username)
                record_dict = record if isinstance(record, dict) else None
                if not username:
                    st.warning("Please enter a username")
                elif not password:
                    st.warning("Please enter your password")
                else:
                    locked, remaining = is_login_locked(db, username)
                    if locked:
                        st.error(f"Too many login attempts. Try again in {remaining} minute(s).")
                    elif not record_dict:
                        if supabase_auth_required(community_settings):
                            record_login_failure(db, username)
                            save_data(db)
                            st.error("Invalid username or password.")
                        else:
                            remote_user = community_fetch_user(community_settings, username)
                            if remote_user and verify_password(password, remote_user.get("auth")):
                                record = ensure_user_record(db, username)
                                record["auth"] = remote_user.get("auth")
                                record["recovery"] = remote_user.get("recovery", [])
                                clear_login_failures(db, username)
                                save_data(db)
                                st.session_state.user = username
                                st.session_state.show_login_animation = True
                                st.session_state.show_header_pulse = True
                                record_login(db, username)
                                save_data(db)
                                st.rerun()
                            else:
                                record_login_failure(db, username)
                                save_data(db)
                                st.error("Invalid username or password.")
                    elif "auth" not in record_dict:
                        st.warning("This username exists but has no password set. Use Register to create one.")
                    elif verify_password(password, record_dict.get("auth")):
                        ensure_user_record(db, username)
                        clear_login_failures(db, username)
                        st.session_state.user = username
                        st.session_state.show_login_animation = True
                        st.session_state.show_header_pulse = True
                        record_login(db, username)
                        if remember_me:
                            token, expires = issue_remember_token(record_dict)
                            save_remember_file({
                                "username": username,
                                "token": token,
                                "expires": expires.isoformat()
                            })
                        else:
                            clear_remember_file()
                            clear_user_remember_token(db, username)
                        save_data(db)
                        community_sync_user(community_settings, db, username)
                        st.rerun()
                    else:
                        record_login_failure(db, username)
                        save_data(db)
                        st.error("Invalid username or password.")

            with st.expander("Forgot Password"):
                with st.form("forgot_form"):
                    forgot_user = st.text_input("Username", key="forgot_user")
                    record = db.get(forgot_user) if forgot_user else None
                    record_dict = record if isinstance(record, dict) else None
                    recovery = record_dict.get("recovery", []) if record_dict else []
                    answers = []
                    if forgot_user and not record_dict:
                        st.warning("User not found.")
                    elif forgot_user and not recovery:
                        st.warning("No recovery questions found for this user.")
                    elif recovery:
                        for idx, rec in enumerate(recovery):
                            answers.append(
                                st.text_input(rec.get("question", f"Question {idx+1}"),
                                              type="password",
                                              key=f"forgot_answer_{idx}")
                            )
                    new_password = st.text_input("New Password", type="password", key="forgot_new_pw")
                    confirm_password = st.text_input("Confirm New Password", type="password", key="forgot_confirm_pw")
                    submit_reset = st.form_submit_button("Reset Password", width="stretch")

                if submit_reset:
                    pw_error = True
                    if not forgot_user or not record_dict:
                        st.error("Enter a valid username.")
                    elif not recovery:
                        st.error("No recovery questions available for this user.")
                    elif len(answers) != len(recovery) or any(not a for a in answers):
                        st.error("Please answer all recovery questions.")
                    else:
                        pw_error = validate_password_strength(new_password)
                        if pw_error:
                            st.error(pw_error)
                        else:
                            pw_error = False
                    if not pw_error:
                        if new_password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            ok = True
                            for answer, rec in zip(answers, recovery):
                                if not verify_recovery_answer(answer, rec):
                                    ok = False
                                    break
                            if ok:
                                record_dict["auth"] = make_password_record(new_password)
                                save_data(db)
                                st.success("Password updated. You can now log in.")
                            else:
                                st.error("Recovery answers did not match.")

            with st.expander("Admin Access"):
                with st.form("admin_access_form"):
                    admin_token = st.text_input("Admin Password", type="password")
                    admin_submit = st.form_submit_button("Enable Admin Mode", width="stretch")

                if admin_submit:
                    if not secrets.compare_digest(admin_token or "", ADMIN_DEFAULT_TOKEN):
                        st.error("Invalid admin password.")
                    else:
                        st.session_state.is_admin = True
                        st.success("Admin mode enabled. Log in and open the Admin tab.")

        with tabs[1]:
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_password = st.text_input("Password", type="password", placeholder="Create a password")
                confirm_password = st.text_input("Confirm Password", type="password")

                q1 = st.selectbox("Security Question 1", SECURITY_QUESTIONS, index=0)
                a1 = st.text_input("Answer 1", type="password")
                remaining_q2 = [q for q in SECURITY_QUESTIONS if q != q1]
                q2 = st.selectbox("Security Question 2", remaining_q2, index=0)
                a2 = st.text_input("Answer 2", type="password")
                remaining_q3 = [q for q in SECURITY_QUESTIONS if q not in [q1, q2]]
                q3 = st.selectbox("Security Question 3", remaining_q3, index=0)
                a3 = st.text_input("Answer 3", type="password")

                register = st.form_submit_button("Create Account", width="stretch")

            if register:
                error = validate_username(new_username)
                pw_error = True
                if error:
                    st.error(error)
                else:
                    pw_error = validate_password_strength(new_password)
                    if pw_error:
                        st.error(pw_error)
                    else:
                        pw_error = False
                if not error and not pw_error:
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif not a1 or not a2 or not a3:
                        st.error("Please answer all recovery questions.")
                    elif len({q1, q2, q3}) < 3:
                        st.error("Please choose three different recovery questions.")
                    else:
                        record = db.get(new_username)
                        record_dict = record if isinstance(record, dict) else None
                        if record_dict and record_dict.get("auth"):
                            st.error("Username already exists. Please log in.")
                        else:
                            record = ensure_user_record(db, new_username)
                            record["auth"] = make_password_record(new_password)
                            record["recovery"] = [
                                create_recovery_record(q1, a1),
                                create_recovery_record(q2, a2),
                                create_recovery_record(q3, a3)
                            ]
                            save_data(db)
                            community_sync_user(community_settings, db, new_username)
                            st.success("Account created. Please log in.")
        render_footer()
    st.stop()

user = st.session_state.user
user_record = ensure_user_record(db, user)
if maybe_update_last_active(db, user):
    save_data(db)
portfolio = user_record["portfolio"]
liabilities = user_record.get("liabilities", [])
entity_names = get_entity_names(user_record)
if "portfolio_entity_view" not in st.session_state:
    st.session_state.portfolio_entity_view = "All"

user_settings = get_user_settings(db, user)
community_settings = get_community_settings(db, user_settings)
if "ui_live_preview" not in st.session_state:
    st.session_state.ui_live_preview = False
if "ui_theme_preview" not in st.session_state:
    st.session_state.ui_theme_preview = user_settings.get("ui_theme", "Dark Gold")
if "ui_font_scale_preview" not in st.session_state:
    st.session_state.ui_font_scale_preview = float(user_settings.get("ui_font_scale", 0.95))
apply_ui_theme(user_settings)
plotly_theme = get_plotly_theme(user_settings)
plotly_text_color = plotly_theme["text"]
plotly_grid_color = plotly_theme["grid"]
plotly_legend_bg = plotly_theme["legend_bg"]
st.session_state.currency_code = user_settings["currency_code"]
st.session_state.currency_symbol = user_settings["currency_symbol"]
st.session_state.currency_rate = user_settings["currency_rate"]
st.session_state.privacy_mode = user_settings.get("privacy_mode", False)
st.session_state.use_live_metal_price = user_settings.get("use_live_metal_price", True)
if "reveal_values" not in st.session_state:
    st.session_state.reveal_values = False

if st.session_state.get("show_login_animation"):
    components.html("""
        <div id="login-loader" style="
            position: fixed;
            inset: 0;
            background: rgba(10, 10, 20, 0.92);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: opacity 0.4s ease;
        ">
            <div class="coin-loader">
                <span>$</span>
            </div>
        </div>
        <style>
            .coin-loader {
                width: 220px;
                height: 220px;
                border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, #fffbe1 0%, #ffd65c 45%, #c07a0c 100%);
                border: 6px solid #ffe5a0;
                box-shadow: 0 18px 40px rgba(0,0,0,0.5), inset 0 4px 12px rgba(255,255,255,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                transform-style: preserve-3d;
                animation: spin 1.6s linear infinite, float 2.2s ease-in-out infinite;
            }
            .coin-loader span {
                font-size: 140px;
                font-weight: 900;
                color: #6a3d00;
                text-shadow: 0 3px 0 #ffe2a3, 0 8px 18px rgba(0,0,0,0.5);
                font-family: 'Inter', sans-serif;
            }
            @keyframes spin {
                0% { transform: rotateY(0deg); }
                100% { transform: rotateY(360deg); }
            }
            @keyframes float {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
        </style>
        <script>
            setTimeout(function() {
                const loader = document.getElementById('login-loader');
                if (loader) {
                    loader.style.opacity = '0';
                    loader.style.pointerEvents = 'none';
                    setTimeout(function() { loader.remove(); }, 500);
                }
            }, 1500);
        </script>
    """, height=0)
    st.session_state.show_login_animation = False

render_header_logo(False, user_settings)
plan_label = normalize_plan(user_settings.get("subscription_plan"))


logout_cols = st.columns([4, 1, 1, 1, 1])
with logout_cols[1]:
    if st.button(f"Settings · {plan_label}", width="stretch"):
        st.session_state.jump_to_settings = True
        st.rerun()
with logout_cols[2]:
    if st.button(f"Feedback / Bugs · {plan_label}", width="stretch"):
        st.session_state.jump_to_settings = True
        st.session_state.open_feedback_form = True
        st.rerun()
with logout_cols[3]:
    if st.button(f"Help · {plan_label}", width="stretch"):
        st.session_state.jump_to_help = True
        st.rerun()
with logout_cols[4]:
    if st.button(f"Log Out · {plan_label}", width="stretch"):
        current_user = st.session_state.get("user")
        if current_user:
            clear_user_remember_token(db, current_user)
            save_data(db)
        clear_remember_file()
        for key in ["user", "selected_asset_index", "modify_index", "show_modify_form", "reveal_values", "open_asset_key", "open_asset_view"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.user = None
        st.session_state.is_admin = False
        st.rerun()

weight_unit = user_settings.get("metal_weight_unit", "toz")
auto_refresh_enabled = user_settings.get("auto_refresh_enabled", True)
refresh_interval = int(user_settings.get("auto_refresh_interval", 70))

if auto_refresh_enabled and AUTOREFRESH_AVAILABLE:
    st_autorefresh(interval=max(30, refresh_interval) * 1000, key="global_autorefresh")

# Live FX update (Frankfurter or Metals.dev)
fx_last_updated = None
fx_provider = user_settings.get("fx_provider", "Frankfurter")
if user_settings.get("auto_fx_enabled"):
    cache_key = f"fx_{st.session_state.currency_code}_{fx_provider}"
    fx_cached = get_cache(cache_key, max(60, refresh_interval))
    if fx_cached:
        fx_data = fx_cached
    else:
        if fx_provider == "Metals.dev":
            fx_data, fx_error = fetch_metalsdev_fx(get_effective_setting(user_settings, "metals_dev_api_key", "METALS_DEV_API_KEY"))
        else:
            fx_data, fx_error = fetch_frankfurter_fx()
            if not fx_data:
                fx_data, fx_error = fetch_open_er_fx()
        if fx_data:
            set_cache(cache_key, fx_data)
        else:
            fx_data = None
    if fx_data:
        code = st.session_state.currency_code
        if code == "USD":
            st.session_state.currency_rate = 1.0
        else:
            if fx_provider == "Metals.dev":
                currencies = fx_data.get("currencies", {})
                raw = currencies.get(code)
                if raw:
                    try:
                        st.session_state.currency_rate = 1 / float(raw)
                        fx_last_updated = fx_data.get("timestamp")
                    except Exception:
                        pass
            else:
                rates = fx_data.get("rates", {})
                raw = rates.get(code)
                if raw:
                    try:
                        st.session_state.currency_rate = float(raw)
                        fx_last_updated = fx_data.get("date")
                    except Exception:
                        pass

# Live metals (FreeGoldPrice or MetalpriceAPI)
live_metals_data = None
metals_last_updated = None
metals_provider = user_settings.get("metals_provider", "FreeGoldPrice")
metals_provider_active = metals_provider
metals_cache_key = f"metals_latest_{metals_provider}"
metals_cached = get_cache(metals_cache_key, max(60, refresh_interval))
if metals_cached:
    live_metals_data = metals_cached
else:
    if metals_provider == "MetalpriceAPI":
        live_metals_data, metals_error = fetch_metalprice_latest(get_effective_setting(user_settings, "metalprice_api_key", "METALPRICE_API_KEY"))
    elif metals_provider == "FreeGoldPrice":
        live_metals_data, metals_error = fetch_freegoldprice_latest(get_effective_setting(user_settings, "freegoldprice_api_key", "FREEGOLDPRICE_API_KEY"))
    elif metals_provider == "SilverPrice":
        live_metals_data, metals_error = fetch_silverprice_latest(st.session_state.currency_code)
    else:
        live_metals_data = None

    if not live_metals_data and metals_provider != "SilverPrice":
        fallback_key = "metals_latest_SilverPrice"
        fallback_cached = get_cache(fallback_key, max(60, refresh_interval))
        if fallback_cached:
            live_metals_data = fallback_cached
            metals_provider_active = "SilverPrice"
        else:
            fallback_data, fallback_err = fetch_silverprice_latest(st.session_state.currency_code)
            if fallback_data:
                live_metals_data = fallback_data
                metals_error = fallback_err
                metals_provider_active = "SilverPrice"
                set_cache(fallback_key, fallback_data)

    if live_metals_data:
        set_cache(metals_cache_key, live_metals_data)

if live_metals_data:
    st.session_state.live_metal_prices = live_metals_data.get("prices", {})
    metals_last_updated = live_metals_data.get("timestamp")
else:
    st.session_state.live_metal_prices = {}
st.session_state.metals_provider_active = metals_provider_active

# ==============================
# ENHANCED HELPERS
# ==============================
AI_VALUATION_ADJUSTMENT = 0.8
AI_CONFIDENCE_ADJUSTMENT = 0.8

@st.cache_data(ttl=900)
def get_price(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        price = info.get("regularMarketPrice") or info.get("previousClose")
        if price is None:
            hist = t.history(period="5d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]
        return float(price) if price else 0.0
    except:
        return 0.0

@st.cache_data(ttl=3600)
def get_history(ticker):
    try:
        return yf.Ticker(ticker).history(period="1y")
    except:
        return pd.DataFrame()

def get_detailed_history(ticker, period="1y"):
    try:
        return yf.Ticker(ticker).history(period=period)
    except:
        return pd.DataFrame()

def ai_valuation(asset):
    base = get_effective_market_price(asset)
    condition_mult = {
        "Poor": 0.6, "Fair": 0.8, "Good": 1.0,
        "Very Good": 1.15, "Excellent": 1.3, "Mint": 1.5
    }.get(asset["condition"], 1.0)

    rarity_mult = 1.2 if asset["type"] in ["Collectible", "Card", "Guitar", "Watch", "Art"] else 1.0
    estimate = base * asset["qty"] * condition_mult * rarity_mult
    estimate *= AI_VALUATION_ADJUSTMENT
    confidence = min(95, int(60 + condition_mult * 20))
    confidence = max(5, confidence - 20)
    confidence = max(5, int(confidence * AI_CONFIDENCE_ADJUSTMENT))

    explanation = (
        "Based on condition (" + asset["condition"] + "), "
        "market pricing, and rarity assumptions."
    )
    if AI_VALUATION_ADJUSTMENT < 1:
        explanation += f" Adjusted down by {int((1 - AI_VALUATION_ADJUSTMENT) * 100)}% to reflect local pricing."

    return round(estimate, 2), confidence, explanation

def marketplace_links(name):
    q = requests.utils.quote(name)
    q_plus = q.replace("%20", "+")
    return {
        "eBay": f"https://www.ebay.com/sch/i.html?_nkw={q}",
        "Reverb": f"https://reverb.com/marketplace?query={q}",
        "TCGPlayer": f"https://www.tcgplayer.com/search/all/product?q={q}",
        "Etsy": f"https://www.etsy.com/search?q={q}",
        "Trade Me (NZ)": f"https://www.trademe.co.nz/Browse/SearchResults.aspx?searchString={q}",
        "Gumtree (AU)": f"https://www.gumtree.com.au/s-{q_plus}/k0",
        "Gumtree (UK)": f"https://www.gumtree.com/search?search_category=all&q={q}",
        "Trading Post (AU)": f"https://www.tradingpost.com.au/search-results/?q={q}",
        "Shpock (UK/EU)": f"https://www.shpock.com/en-gb/search?query={q}"
    }

def get_condition_color(condition):
    colors = {
        "Mint": "#1abc9c",
        "Excellent": "#2ecc71",
        "Very Good": "#3498db",
        "Good": "#f39c12",
        "Fair": "#e67e22",
        "Poor": "#e74c3c"
    }
    return colors.get(condition, "#95a5a6")

def get_type_badge_class(asset_type):
    return {
        "Gold": "badge-gold",
        "Silver": "badge-other",
        "Copper": "badge-copper",
        "Collectible": "badge-collectible",
        "Guitar": "badge-guitar",
        "Card": "badge-card",
        "Stock": "badge-stock",
        "Crypto": "badge-other",
        "Jewelry": "badge-gold",
        "Vehicle": "badge-other",
        "Business": "badge-other"
    }.get(asset_type, "badge-other")

# ==============================
# SEED EXAMPLE ASSETS
# ==============================
if not portfolio:
    portfolio.extend([
        {
            "name": "MTG Black Lotus",
            "type": "Collectible",
            "qty": 1,
            "condition": "Excellent",
            "ticker": None,
            "market_price": 15000,
            "images": [],
            "image_url": search_asset_image("mtg black lotus"),
            "added": str(datetime.now())
        },
        {
            "name": "Gold Sovereign Coin",
            "type": "Gold",
            "qty": 5,
            "condition": "Very Good",
            "ticker": "GC=F",
            "market_price": get_price("GC=F"),
            "images": [],
            "image_url": search_asset_image("gold sovereign coin"),
            "added": str(datetime.now())
        },
        {
            "name": "Fender Stratocaster 1965",
            "type": "Guitar",
            "qty": 1,
            "condition": "Good",
            "ticker": None,
            "market_price": 8500,
            "images": [],
            "image_url": search_asset_image("fender stratocaster 1965"),
            "added": str(datetime.now())
        },
        {
            "name": "Apple Stock",
            "type": "Stock",
            "qty": 50,
            "condition": "Excellent",
            "ticker": "AAPL",
            "market_price": get_price("AAPL"),
            "images": [],
            "image_url": search_asset_image("apple stock"),
            "added": str(datetime.now())
        }
    ])
    save_data(db)

# Initialize image URLs for existing assets if not present
for asset in portfolio:
    if "image_url" not in asset:
        asset["image_url"] = search_asset_image(asset["name"])
save_data(db)

# ==============================
# MAIN DASHBOARD HEADER
# ==============================
safe_user = escape_html(user)
currency_code = st.session_state.currency_code
currency_symbol = st.session_state.currency_symbol
currency_rate = st.session_state.currency_rate
now_local = get_now_for_settings(user_settings)
last_updated_text = format_date_for_settings(now_local, user_settings)
st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
            <h1 style="margin: 0;">WealthPulse</h1>
            <p style="color: var(--muted); margin: 0;">Welcome back, """ + safe_user + """</p>
        </div>
        <div style="text-align: right;">
            <p style="color: var(--muted); margin: 0; font-size: 0.9rem;">Last Updated</p>
            <p style="color: var(--text); margin: 0; font-weight: 600;">""" + last_updated_text + """</p>
        </div>
    </div>
""", unsafe_allow_html=True)
render_plan_badge(user_settings)
render_scroll_to_top()
render_https_warning_banner()
render_https_enforcement()
render_gold_animation()
render_gold_click_listener()

# ==============================
# ENHANCED TABS
# ==============================
tab_labels = [
    "Portfolio",
    "Bullion",
    "Community",
    "Analytics",
    "Buy/Sell",
    "Stats",
    "Add Asset",
    "Edit Items",
    "Entities & Liabilities",
    "Settings",
    "Help"
]
if st.session_state.get("is_admin"):
    tab_labels.append("Admin")

tabs = st.tabs(tab_labels)
tab1, bullion_tab, forum_tab, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab_help = tabs[:11]
admin_tab = tabs[11] if len(tabs) > 11 else None

tab_jump_index = None
if st.session_state.get("jump_to_portfolio"):
    tab_jump_index = 0
    st.session_state.jump_to_portfolio = False
if st.session_state.get("jump_to_bullion"):
    tab_jump_index = 1
    st.session_state.jump_to_bullion = False
if st.session_state.get("jump_to_community"):
    tab_jump_index = 2
    st.session_state.jump_to_community = False
if st.session_state.get("jump_to_modify"):
    tab_jump_index = 7
    st.session_state.jump_to_modify = False
if st.session_state.get("jump_to_add_asset"):
    tab_jump_index = 6
    st.session_state.jump_to_add_asset = False
if st.session_state.get("jump_to_entities"):
    tab_jump_index = 8
    st.session_state.jump_to_entities = False
if st.session_state.get("jump_to_settings"):
    tab_jump_index = 9
    st.session_state.jump_to_settings = False
if st.session_state.get("jump_to_help"):
    tab_jump_index = 10
    st.session_state.jump_to_help = False
if st.session_state.get("jump_to_admin") and admin_tab is not None:
    tab_jump_index = 11
    st.session_state.jump_to_admin = False
if tab_jump_index is not None:
    components.html(f"""
        <script>
            (function() {{
                const target = {tab_jump_index};
                let tries = 0;
                const timer = setInterval(() => {{
                    const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"], div[role="tab"]');
                    if (tabs.length > target) {{
                        tabs[target].click();
                        clearInterval(timer);
                    }}
                    tries += 1;
                    if (tries > 30) {{
                        clearInterval(timer);
                    }}
                }}, 150);
            }})();
        </script>
    """, height=0)

# ==============================
# TAB 1: PORTFOLIO (MODERNIZED WITH IMAGES)
# ==============================
with tab1:
    panels = set(user_settings.get("dashboard_panels", []))
    if st.session_state.get("privacy_mode"):
        st.session_state.reveal_values = st.checkbox(
            "Reveal values for this session",
            value=st.session_state.reveal_values
        )

    entity_options = ["All"] + entity_names
    current_view = st.session_state.get("portfolio_entity_view", "All")
    if current_view not in entity_options:
        current_view = "All"
    selected_view = st.selectbox("Portfolio View", entity_options, index=entity_options.index(current_view))
    st.session_state.portfolio_entity_view = selected_view

    if not portfolio and not user_settings.get("onboarding_completed", False):
        if "onboarding_step" not in st.session_state:
            st.session_state.onboarding_step = 1
        step = int(st.session_state.onboarding_step)
        total_steps = 4
        country_code = get_country_code(user_settings)
        country_name = get_country_name(country_code)
        examples = ", ".join(get_local_entity_examples(country_code))
        local_hint = get_local_entity_hint(country_code)

        st.markdown(f"### Guided Setup (Step {step} of {total_steps})")
        st.progress(step / total_steps)
        st.caption("Designed for founders and small business owners — keep personal, business, and trust assets cleanly separated.")

        if step == 1:
            st.markdown("**Choose your plan**")
            current_plan = normalize_plan(user_settings.get("subscription_plan"))
            plan_choice = st.radio(
                "Plan",
                SUBSCRIPTION_PLANS,
                index=SUBSCRIPTION_PLANS.index(current_plan) if current_plan in SUBSCRIPTION_PLANS else 0,
                horizontal=True
            )
            st.caption(PLAN_DESCRIPTIONS.get(plan_choice, ""))
            st.write("Suggested for business owners: **Pro**. For community access: **Elite**.")
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("Continue", width="stretch"):
                    record = ensure_user_record(db, user)
                    settings = record.get("settings", {})
                    settings["subscription_plan"] = normalize_plan(plan_choice)
                    settings.setdefault("subscription_status", "active")
                    record["settings"] = settings
                    save_data(db)
                    st.session_state.onboarding_step = 2
                    st.rerun()
            with col_b:
                if st.button("Skip onboarding", width="stretch"):
                    record = ensure_user_record(db, user)
                    settings = record.get("settings", {})
                    settings["onboarding_completed"] = True
                    record["settings"] = settings
                    save_data(db)
                    st.success("Onboarding dismissed.")

        elif step == 2:
            st.info(f"Suggested entities for {country_name}: {examples}")
            st.caption(local_hint)
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("Set Up Entities", width="stretch"):
                    st.session_state.jump_to_entities = True
                    st.rerun()
            with col_b:
                if st.button("Continue", width="stretch"):
                    st.session_state.onboarding_step = 3
                    st.rerun()

        elif step == 3:
            st.markdown("**Add your first assets**")
            col_a, col_b, col_c = st.columns([1, 1, 1])
            with col_a:
                if st.button("Add First Asset", width="stretch"):
                    st.session_state.jump_to_add_asset = True
                    st.rerun()
            with col_b:
                if st.button("Load Demo Portfolio", width="stretch"):
                    record = ensure_user_record(db, user)
                    record["portfolio"] = build_demo_portfolio()
                    record["entities"] = [
                        build_entity("Personal", "Person", [user] if user else []),
                        build_entity("Trust", "Trust", []),
                        build_entity("Joint", "Joint", [])
                    ]
                    settings = record.get("settings", {})
                    settings["onboarding_completed"] = True
                    record["settings"] = settings
                    save_data(db)
                    st.session_state.jump_to_portfolio = True
                    st.rerun()
            with col_c:
                if st.button("Continue", width="stretch"):
                    st.session_state.onboarding_step = 4
                    st.rerun()

        else:
            st.markdown("**Set your wealth goals**")
            st.caption("Optional but highly recommended — set a target net worth and timeframe.")
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("Open Wealth Plan", width="stretch"):
                    st.session_state.jump_to_settings = True
                    st.rerun()
            with col_b:
                if st.button("Finish Setup", width="stretch"):
                    record = ensure_user_record(db, user)
                    settings = record.get("settings", {})
                    settings["onboarding_completed"] = True
                    record["settings"] = settings
                    save_data(db)
                    st.success("You're all set. Welcome to WealthPulse!")
    if "Market Snippets" in panels:
        st.subheader("Market Snippets")
        snippet_cols = st.columns(2)
        with snippet_cols[0]:
            if st.session_state.currency_code != "USD":
                st.markdown("**FX Rate**")
                st.write(f"1 USD = {st.session_state.currency_code} {st.session_state.currency_rate:,.4f}")
                if fx_last_updated:
                    if isinstance(fx_last_updated, (int, float)):
                        fx_time = datetime.fromtimestamp(fx_last_updated)
                    else:
                        try:
                            fx_time = datetime.fromisoformat(str(fx_last_updated))
                        except Exception:
                            fx_time = get_now_for_settings(user_settings)
                    st.caption(f"FX updated {format_date_for_settings(fx_time, user_settings)}")
            else:
                st.markdown("**FX Rate**")
                st.write("USD base currency")
        with snippet_cols[1]:
            if live_metals_data and live_metals_data.get("prices"):
                source_label = {
                    "SilverPrice": "SilverPrice.org",
                    "FreeGoldPrice": "FreeGoldPrice",
                    "MetalpriceAPI": "MetalpriceAPI"
                }.get(metals_provider_active, "Live")
                st.markdown(f"**Live Metals (spot, {currency_code}/oz)**")
                gold = live_metals_data["prices"].get("XAU")
                silver = live_metals_data["prices"].get("XAG")
                if gold:
                    st.write(f"Gold: {format_currency(gold, currency_symbol, currency_rate)}")
                if silver:
                    st.write(f"Silver: {format_currency(silver, currency_symbol, currency_rate)}")
                st.caption(f"Source: {source_label}")
                if metals_last_updated:
                    if isinstance(metals_last_updated, (int, float)):
                        metals_time = datetime.fromtimestamp(metals_last_updated)
                    else:
                        try:
                            metals_time = datetime.fromisoformat(str(metals_last_updated))
                        except Exception:
                            metals_time = get_now_for_settings(user_settings)
                    st.caption(f"Metals updated {format_date_for_settings(metals_time, user_settings)}")
            else:
                st.markdown("**Live Metals**")
                st.write("Choose a metals source in Settings to enable live pricing.")

    if "Live Metals" in panels and live_metals_data and live_metals_data.get("prices"):
        st.subheader("Live Metals Pricing")
        source_label = {
            "SilverPrice": "SilverPrice.org",
            "FreeGoldPrice": "FreeGoldPrice",
            "MetalpriceAPI": "MetalpriceAPI"
        }.get(metals_provider_active, "Live")
        st.caption(f"Source: {source_label}")
        metal_cols = st.columns(4)
        for idx, code in enumerate(["XAU", "XAG", "XPT", "XPD"]):
            price = live_metals_data["prices"].get(code)
            if price is None:
                continue
            display = format_currency(price, currency_symbol, currency_rate)
            with metal_cols[idx % 4]:
                st.metric(METAL_NAMES.get(code, code), display)

    if "Top Movers" in panels:
        st.subheader("Top Movers (Tickers)")
        movers = []
        for asset in portfolio:
            if asset.get("ticker"):
                hist = get_history(asset["ticker"])
                if not hist.empty:
                    recent = hist["Close"].tail(30)
                    avg_price = recent.mean() if not recent.empty else 0
                    current_price = get_price(asset["ticker"])
                    if avg_price > 0:
                        pct = (current_price - avg_price) / avg_price * 100
                        movers.append({
                            "name": asset["name"],
                            "ticker": asset["ticker"],
                            "pct": pct,
                            "price": current_price
                        })
        if movers:
            movers.sort(key=lambda x: abs(x["pct"]), reverse=True)
            if user_settings.get("notifications_enabled"):
                threshold = float(user_settings.get("notification_threshold_pct", 5.0))
                alerts = [m for m in movers if abs(m["pct"]) >= threshold]
                if alerts:
                    st.warning(f"{len(alerts)} alert(s): movement ≥ {threshold:.1f}%")
            for mover in movers[:5]:
                direction = "▲" if mover["pct"] >= 0 else "▼"
                st.write(f"{direction} {mover['name']} ({mover['ticker']}): {mover['pct']:.1f}%")
        else:
            st.write("No ticker assets found.")

    if "Stock News" in panels:
        st.subheader("Stock News")
        tickers = list({a.get("ticker") for a in portfolio if a.get("ticker")})
        if tickers:
            query = " OR ".join(tickers[:5])
        else:
            query = "stocks market"

        articles = None
        news_err = None
        if user_settings.get("news_provider") == "NewsAPI" and get_effective_setting(user_settings, "news_api_key", "NEWS_API_KEY"):
            news_cache_key = f"news_{query}"
            news_cached = get_cache(news_cache_key, 1800)
            if news_cached:
                articles = news_cached
            else:
                articles, news_err = fetch_newsapi(query, get_effective_setting(user_settings, "news_api_key", "NEWS_API_KEY"))
                if articles:
                    set_cache(news_cache_key, articles)

        if not articles and user_settings.get("rss_backup_enabled") and user_settings.get("rss_feed_url"):
            rss_url = user_settings.get("rss_feed_url")
            if "{query}" in rss_url:
                rss_url = rss_url.replace("{query}", quote_plus(query))
            rss_cache_key = f"rss_{rss_url}"
            rss_cached = get_cache(rss_cache_key, 1800)
            if rss_cached:
                articles = rss_cached
            else:
                articles, news_err = fetch_rss_items(rss_url, limit=5)
                if articles:
                    set_cache(rss_cache_key, articles)

        if articles:
            for article in articles:
                title = article.get("title", "Article")
                url = article.get("url") or article.get("link", "")
                source = article.get("source", "News")
                published = article.get("publishedAt") or article.get("published") or ""
                if url:
                    st.markdown(f"- [{title}]({url}) — {source} ({published})")
                else:
                    st.write(f"- {title} — {source} ({published})")
        else:
            st.info(f"News unavailable: {news_err or 'Enable NewsAPI or RSS in Settings'}")

    list_col = st.container()
    with list_col:
        # Filter and sort options
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filter_type = st.selectbox("Filter by Type", ["All"] + list(set(a["type"] for a in portfolio)))
        with col_f2:
            sort_by = st.selectbox("Sort by", ["Value (High-Low)", "Value (Low-High)", "Name", "Date Added"])
        with col_f3:
            default_view = user_settings.get("default_view_mode", "Grid")
            if hasattr(st, "segmented_control"):
                view_mode = st.segmented_control("View", ["Grid", "List"], default=default_view)
            else:
                default_index = 0 if default_view == "Grid" else 1
                view_mode = st.radio("View", ["Grid", "List"], horizontal=True, index=default_index)
        
        # Build view items (with bullion rollups for display)
        view_items = build_portfolio_view_items(portfolio, selected_view)
        bullion_rollups = {}
        display_portfolio = []
        for item in view_items:
            asset = item["asset"]
            share = item["share"]
            metal_type = asset.get("type")
            if metal_type in BULLION_TYPES:
                agg = bullion_rollups.setdefault(metal_type, {
                    "metal": metal_type,
                    "items": [],
                    "weight": 0.0,
                    "qty": 0.0,
                    "value": 0.0
                })
                agg["items"].append(item)
                weight = asset.get("details", {}).get("weight_troy_oz")
                if weight:
                    try:
                        agg["weight"] += float(weight) * share
                    except Exception:
                        pass
                try:
                    agg["qty"] += float(asset.get("qty", 1)) * share
                except Exception:
                    agg["qty"] += share
                value, _, _ = ai_valuation(asset)
                agg["value"] += value * share
                continue
            display_portfolio.append({
                **item,
                "key": f"asset:{item['index']}",
                "is_aggregate": False
            })

        for metal, agg in bullion_rollups.items():
            agg_asset = {
                "name": f"{metal} Bullion",
                "type": metal,
                "qty": 1,
                "condition": "Good",
                "ticker": None,
                "market_price": agg["value"],
                "details": {},
                "notes": f"{len(agg['items'])} items combined"
            }
            if agg["weight"] > 0:
                agg_asset["details"]["weight_troy_oz"] = agg["weight"]
                agg_asset["details"]["purity"] = "Varies"
                agg_asset["details"]["mint"] = "Mixed"
            display_portfolio.append({
                "index": None,
                "asset": agg_asset,
                "share": 1.0,
                "key": f"bullion:{metal}",
                "is_aggregate": True,
                "bullion": agg,
                "override_value": agg["value"],
                "override_confidence": 45,
                "override_explanation": f"Combined value of {len(agg['items'])} bullion items."
            })

        if filter_type != "All":
            display_portfolio = [item for item in display_portfolio if item["asset"]["type"] == filter_type]

        def get_item_valuation(item):
            override = item.get("override_value")
            if override is not None:
                return (
                    float(override),
                    int(item.get("override_confidence", 50)),
                    item.get("override_explanation", "Combined bullion items.")
                )
            return ai_valuation(item["asset"])

        if sort_by == "Value (High-Low)":
            display_portfolio.sort(key=lambda x: get_item_valuation(x)[0] * x["share"], reverse=True)
        elif sort_by == "Value (Low-High)":
            display_portfolio.sort(key=lambda x: get_item_valuation(x)[0] * x["share"])
        elif sort_by == "Name":
            display_portfolio.sort(key=lambda x: x["asset"]["name"])
        elif sort_by == "Date Added":
            display_portfolio.sort(key=lambda x: parse_added_date(x["asset"].get("added", "")), reverse=True)

        for asset in portfolio:
            if asset.get("ticker"):
                asset["market_price"] = get_price(asset["ticker"])

        total_all = sum(ai_valuation(item["asset"])[0] * item["share"] for item in view_items)
        liabilities_total = get_total_liabilities_value(liabilities, selected_view)
        net_worth = total_all - liabilities_total
        
        if view_mode == "Grid":
            cols = st.columns(3)
            for idx, item in enumerate(display_portfolio):
                asset_index = item["index"]
                asset = item["asset"]
                share = item["share"]
                item_key = item.get("key") or f"asset:{asset_index}"
                value, confidence, explanation = get_item_valuation(item)
                view_value = value * share
                with cols[idx % 3]:
                    with st.container():
                        image = get_asset_image(asset)
                        safe_name = escape_html(asset.get("name", ""))
                        safe_type = escape_html(asset.get("type", ""))
                        safe_condition = escape_html(asset.get("condition", ""))
                        safe_explanation = escape_html(explanation)
                        safe_img_src = escape_html(image["src"])
                        value_html = format_currency_html(view_value, currency_symbol, currency_rate)
                        ownership_html = ""
                        if selected_view != "All" and share < 0.999:
                            ownership_html = f"<div style='font-size: 0.75rem; color: var(--muted);'>Ownership: {share*100:.1f}%</div>"
                        
                        card_class = "asset-card"
                        card_html = f"""
                            <div class="{card_class}">
                                <div style="position: relative; width: 100%; height: 150px; overflow: hidden; border-radius: 15px; margin-bottom: 1rem; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;">
                                    <img src="{safe_img_src}" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 10px;" onerror="this.src='https://cdn-icons-png.flaticon.com/512/1170/1170678.png'">
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                    <span class="badge {get_type_badge_class(asset['type'])}">{safe_type}</span>
                                    <span style="color: {get_condition_color(asset['condition'])}; font-weight: 600; font-size: 0.9rem;">
                                        {safe_condition}
                                    </span>
                                </div>
                                <h3 style="color: var(--text) !important; margin: 0.5rem 0; font-size: 1.2rem; line-height: 1.3;">{safe_name}</h3>
                                {ownership_html}
                                <div style="font-size: 1.8rem; font-weight: 800; color: #d1a843; margin: 0.5rem 0;">
                                    {value_html}
                                </div>
                                <div style="margin: 0.5rem 0;">
                                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--muted); margin-bottom: 0.3rem;">
                                        <span>AI Confidence</span>
                                        <span>{confidence}%</span>
                                    </div>
                                    <div class="stProgress" style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                                        <div style="width: {confidence}%; height: 100%; background: linear-gradient(90deg, #d1a843 0%, #f2c66d 100%); border-radius: 10px;"></div>
                                    </div>
                                </div>
                                <p style="font-size: 0.8rem; color: var(--muted); margin-top: 0.5rem; line-height: 1.4;">{safe_explanation}</p>
                            </div>
                        """
                        marker_id = f"card-marker-grid-{asset_index}"
                        st.markdown(f'<div id="{marker_id}"></div>', unsafe_allow_html=True)
                        render_html_block(textwrap.dedent(card_html))
                        if st.button("Open Asset", key=f"open_asset_{item_key}"):
                            if item.get("is_aggregate"):
                                st.session_state.jump_to_bullion = True
                            elif asset_index is not None:
                                st.session_state.selected_asset_index = asset_index
                                st.session_state.jump_to_modify = True
                            request_scroll_to_top()
                            st.rerun()
                        apply_card_click_overlay(marker_id)
        else:
            st.caption("Click an item to view full details.")
            for item in display_portfolio:
                asset_index = item["index"]
                asset = item["asset"]
                share = item["share"]
                item_key = item.get("key") or f"asset:{asset_index}"
                value, _, _ = get_item_valuation(item)
                view_value = value * share
                image = get_asset_image(asset)
                safe_name = escape_html(asset.get("name", ""))
                safe_type = escape_html(asset.get("type", ""))
                safe_condition = escape_html(asset.get("condition", ""))
                safe_img_src = escape_html(image["src"])
                value_html = format_currency_html(view_value, currency_symbol, currency_rate)
                ownership_text = ""
                if selected_view != "All" and share < 0.999:
                    ownership_text = f" • {share*100:.1f}% owned"

                card_class = "list-card"
                card_html = f"""
                    <div class="{card_class}">
                        <img class="list-thumb" src="{safe_img_src}" onerror="this.src='https://cdn-icons-png.flaticon.com/512/1170/1170678.png'">
                        <div class="list-body">
                            <div class="list-title">{safe_name}</div>
                            <div class="list-meta">{safe_type} • {safe_condition} • Qty {asset.get('qty', 1)}{ownership_text}</div>
                        </div>
                        <div class="list-value">{value_html}</div>
                    </div>
                """
                with st.container():
                    marker_id = f"card-marker-list-{asset_index}"
                    st.markdown(f'<div id="{marker_id}"></div>', unsafe_allow_html=True)
                    render_html_block(textwrap.dedent(card_html))
                    if st.button("Open Asset", key=f"open_asset_list_{item_key}"):
                        if item.get("is_aggregate"):
                            st.session_state.jump_to_bullion = True
                        elif asset_index is not None:
                            st.session_state.selected_asset_index = asset_index
                            st.session_state.jump_to_modify = True
                        request_scroll_to_top()
                        st.rerun()
                    apply_card_click_overlay(marker_id)

        # Total wealth card
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #d1a843 0%, #f2c66d 100%); 
                        border-radius: 20px; padding: 2rem; margin-top: 2rem; 
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3); text-align: center;">
                <p style="color: var(--text); margin: 0; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px;">
                    Net Worth
                </p>
                <div style="color: var(--text); font-size: 2.6rem; font-weight: 800; margin: 0.4rem 0;">
                    {format_currency_html(net_worth, currency_symbol, currency_rate)}
                </div>
                <p style="color: var(--muted); margin: 0; font-size: 0.9rem;">
                    Assets {format_currency_html(total_all, currency_symbol, currency_rate)} • Liabilities {format_currency_html(liabilities_total, currency_symbol, currency_rate)}
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Edit/Delete actions are handled in the Edit Items tab

# ==============================
# TAB 2: ANALYTICS & CHARTS
# ==============================
with tab2:
    entity_view = st.session_state.get("portfolio_entity_view", "All")
    view_items = build_portfolio_view_items(portfolio, entity_view)
    if entity_view != "All":
        st.caption(f"Viewing: {entity_view}")
    if not view_items:
        st.info("Add assets to see analytics")
    else:
        # Calculate all values first
        asset_values = []
        asset_types = {}
        asset_names = []
        asset_worth = []

        for item in view_items:
            asset = item["asset"]
            share = item["share"]
            if asset.get("ticker"):
                asset["market_price"] = get_price(asset["ticker"])
            value, _, _ = ai_valuation(asset)
            value_display = format_currency_value(value * share, currency_rate)
            asset_values.append(value_display)
            asset_types[asset["type"]] = asset_types.get(asset["type"], 0) + value_display
            asset_names.append(asset["name"])
            asset_worth.append(value_display)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Asset Allocation")
            if PLOTLY_AVAILABLE:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(asset_types.keys()),
                    values=list(asset_types.values()),
                    hole=0.4,
                    marker=dict(colors=px.colors.sequential.Plasma),
                    textinfo='label+percent',
                    textfont=dict(size=12, color=plotly_text_color),
                    hovertemplate=f'%{{label}}: {currency_code} %{{value:,.2f}}<extra></extra>'
                )])
                fig_pie.update_layout(
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=400,
                    font=dict(color=plotly_text_color)
                )
                st.plotly_chart(fig_pie, width="stretch")
            else:
                allocation_df = pd.DataFrame({
                    'Type': list(asset_types.keys()),
                    'Value': list(asset_types.values())
                })
                st.dataframe(allocation_df, hide_index=True)
                st.bar_chart(allocation_df.set_index('Type'))

        with col2:
            st.subheader("Asset Values")
            if PLOTLY_AVAILABLE:
                fig_bar = go.Figure(data=[go.Bar(
                    x=asset_worth,
                    y=asset_names,
                    orientation='h',
                    marker=dict(
                        color=asset_worth,
                        colorscale='Plasma',
                        showscale=False
                    ),
                    text=[format_currency(v, currency_symbol, 1.0) for v in asset_worth],
                    textposition='outside',
                    textfont=dict(color=plotly_text_color)
                )])
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(showgrid=False, color=plotly_text_color),
                    xaxis=dict(showgrid=True, gridcolor=plotly_grid_color, color=plotly_text_color),
                    margin=dict(t=0, b=0, l=0, r=0),
                    height=400,
                    font=dict(color=plotly_text_color)
                )
                st.plotly_chart(fig_bar, width="stretch")
            else:
                values_df = pd.DataFrame({
                    'Asset': asset_names,
                    'Value': asset_worth
                }).set_index('Asset')
                st.bar_chart(values_df)

    if has_plan_at_least(user_settings, "Pro"):
        st.markdown("### Advanced Analytics")

        # Metals trend
        st.subheader("Metals Trend")
        if user_settings.get("metals_provider") == "MetalpriceAPI" and get_effective_setting(user_settings, "metalprice_api_key", "METALPRICE_API_KEY"):
            end_date = get_now_for_settings(user_settings).date()
            start_date = end_date - timedelta(days=int(user_settings.get("metal_history_days", 30)))
            metals_df, metals_err = fetch_metalprice_timeframe(
                get_effective_setting(user_settings, "metalprice_api_key", "METALPRICE_API_KEY"),
                start_date.isoformat(),
                end_date.isoformat()
            )
            if metals_df is not None and not metals_df.empty:
                metals_df["date"] = pd.to_datetime(metals_df["date"])
                for code in ["XAU", "XAG", "XPT", "XPD"]:
                    if code in metals_df.columns:
                        metals_df[code] = metals_df[code] * currency_rate
                if PLOTLY_AVAILABLE:
                    fig_metals = go.Figure()
                    for code in ["XAU", "XAG", "XPT", "XPD"]:
                        if code in metals_df.columns:
                            fig_metals.add_trace(go.Scatter(
                                x=metals_df["date"],
                                y=metals_df[code],
                                mode="lines",
                                name=METAL_NAMES.get(code, code)
                            ))
                    fig_metals.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=True, gridcolor=plotly_grid_color, color=plotly_text_color),
                        yaxis=dict(showgrid=True, gridcolor=plotly_grid_color, color=plotly_text_color,
                                   title=f"Price ({currency_code})"),
                        height=350,
                        font=dict(color=plotly_text_color)
                    )
                    st.plotly_chart(fig_metals, width="stretch")
                else:
                    chart_df = metals_df.set_index("date")
                    st.line_chart(chart_df[["XAU", "XAG"]] if "XAU" in chart_df.columns else chart_df)
            else:
                st.info(f"Unable to load metals trend: {metals_err or 'No data'}")
        else:
            st.info("Metals trend is available with MetalpriceAPI history (paid).")

        # Cost basis vs current value
        st.subheader("Cost Basis vs Current Value")
        cost_rows = []
        for item in view_items:
            asset = item["asset"]
            share = item["share"]
            cost_basis = asset.get("details", {}).get("cost_basis")
            if cost_basis:
                current_value, _, _ = ai_valuation(asset)
                cost_rows.append({
                    "Asset": asset["name"],
                    "Cost Basis": format_currency_value(float(cost_basis) * share, currency_rate),
                    "Current Value": format_currency_value(current_value * share, currency_rate)
                })
        if cost_rows:
            cost_df = pd.DataFrame(cost_rows)
            if PLOTLY_AVAILABLE:
                fig_cost = go.Figure()
                fig_cost.add_trace(go.Bar(
                    x=cost_df["Asset"],
                    y=cost_df["Cost Basis"],
                    name="Cost Basis"
                ))
                fig_cost.add_trace(go.Bar(
                    x=cost_df["Asset"],
                    y=cost_df["Current Value"],
                    name="Current Value"
                ))
                fig_cost.update_layout(
                    barmode="group",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(color=plotly_text_color),
                    yaxis=dict(color=plotly_text_color, title=f"Value ({currency_code})", showgrid=True, gridcolor=plotly_grid_color),
                    height=350,
                    font=dict(color=plotly_text_color)
                )
                st.plotly_chart(fig_cost, width="stretch")
            else:
                st.bar_chart(cost_df.set_index("Asset"))
        else:
            st.info("Add a cost basis in asset details to see this chart.")

        # Historical performance simulation
        st.subheader("Portfolio Performance Trend")
        if any(item["asset"].get("ticker") for item in view_items):
            combined_history = pd.DataFrame()
            for item in view_items:
                asset = item["asset"]
                share = item["share"]
                if asset.get("ticker"):
                    hist = get_detailed_history(asset["ticker"], "1y")
                    if not hist.empty:
                        hist["Portfolio_Value"] = hist["Close"] * asset["qty"] * currency_rate * share
                        if combined_history.empty:
                            combined_history = hist[["Portfolio_Value"]].copy()
                            combined_history.columns = [asset["name"]]
                        else:
                            combined_history = combined_history.join(
                                hist[["Portfolio_Value"]].rename(columns={"Portfolio_Value": asset["name"]}),
                                how="outer"
                            )

            if not combined_history.empty:
                combined_history = combined_history.ffill().bfill()
                if PLOTLY_AVAILABLE:
                    fig_line = go.Figure()
                    colors = px.colors.sequential.Plasma[:len(combined_history.columns)]
                    for i, col in enumerate(combined_history.columns):
                        fig_line.add_trace(go.Scatter(
                            x=combined_history.index,
                            y=combined_history[col],
                            mode='lines',
                            name=col,
                            line=dict(width=2, color=colors[i]),
                            stackgroup='one' if len(combined_history.columns) > 1 else None
                        ))
                    fig_line.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(bgcolor=plotly_legend_bg, font=dict(color=plotly_text_color)),
                        xaxis=dict(showgrid=True, gridcolor=plotly_grid_color, color=plotly_text_color),
                        yaxis=dict(showgrid=True, gridcolor=plotly_grid_color, color=plotly_text_color, title=f"Value ({currency_code})"),
                        height=400,
                        hovermode='x unified',
                        font=dict(color=plotly_text_color)
                    )
                    st.plotly_chart(fig_line, width="stretch")
                else:
                    st.line_chart(combined_history)
            else:
                st.info("Not enough history to plot performance yet.")
        else:
            st.info("Add assets with tickers to see performance trends")
    else:
        render_plan_gate(user_settings, "Pro", "Advanced Analytics", "Upgrade to unlock metals trends, cost basis, and performance charts.", key="gate_advanced_analytics")
# ==============================
# TAB 3: BUY/SELL GUIDE
# ==============================
with tab3:
    if not has_plan_at_least(user_settings, "Pro"):
        render_plan_gate(user_settings, "Pro", "Buy/Sell Guidance", "Upgrade to unlock buy/sell intelligence and recommendations.", key="gate_buysell")
    else:
        st.subheader("Intelligent Buy/Sell Recommendations")
        entity_view = st.session_state.get("portfolio_entity_view", "All")
        view_items = build_portfolio_view_items(portfolio, entity_view)
        if entity_view != "All":
            st.caption(f"Viewing: {entity_view}")

        for idx, item in enumerate(view_items):
            asset = item["asset"]
            if asset.get("ticker"):
                current_price = get_price(asset["ticker"])
                hist = get_detailed_history(asset["ticker"], "1y")
        
                if not hist.empty:
                    high_52w = hist["High"].max()
                    low_52w = hist["Low"].min()
                    avg_price = hist["Close"].mean()
            
                    # Recommendation logic
                    if current_price < avg_price * 0.95:
                        signal = "BUY"
                        signal_color = "#2ecc71"
                        reason = "Trading below 90-day average - potential undervaluation"
                    elif current_price > high_52w * 0.98:
                        signal = "SELL"
                        signal_color = "#e74c3c"
                        reason = "Near 52-week high - profit taking opportunity"
                    else:
                        signal = "HOLD"
                        signal_color = "#f39c12"
                        reason = "Stable performance - maintain position"
                    safe_name = escape_html(asset.get("name", ""))
                    current_price_html = format_currency_html(current_price, currency_symbol, currency_rate)
                    high_html = format_currency_html(high_52w, currency_symbol, currency_rate)
                    low_html = format_currency_html(low_52w, currency_symbol, currency_rate)

                    with st.container():
                        st.markdown(f"""
                            <div style="background: rgba(30, 30, 40, 0.9); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                                    <h3 style="margin: 0; color: var(--text);">{safe_name}</h3>
                                    <span style="background: {signal_color}; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: 700;">
                                        {signal}
                                    </span>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                                    <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 10px;">
                                        <div style="font-size: 1.3rem; font-weight: 700; color: #d1a843;">{current_price_html}</div>
                                        <div style="font-size: 0.85rem; color: var(--muted);">Current</div>
                                    </div>
                                    <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 10px;">
                                        <div style="font-size: 1.3rem; font-weight: 700; color: #2ecc71;">{high_html}</div>
                                        <div style="font-size: 0.85rem; color: var(--muted);">52W High</div>
                                    </div>
                                    <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 10px;">
                                        <div style="font-size: 1.3rem; font-weight: 700; color: #e74c3c;">{low_html}</div>
                                        <div style="font-size: 0.85rem; color: var(--muted);">52W Low</div>
                                    </div>
                                </div>
                                <p style="margin: 0; color: var(--muted); font-size: 0.95rem;">{reason}</p>
                            </div>
                        """, unsafe_allow_html=True)
                
                        with st.expander("Price History"):
                            hist_display = hist.copy()
                            hist_display["Close"] = hist_display["Close"] * currency_rate
                            if PLOTLY_AVAILABLE:
                                fig_mini = go.Figure(data=[go.Scatter(
                                    x=hist_display.index,
                                    y=hist_display["Close"],
                                    fill='tozeroy',
                                    fillcolor='rgba(102, 126, 234, 0.3)',
                                    line=dict(color='#d1a843', width=2)
                                )])
                                fig_mini.update_layout(
                                    height=250,
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    xaxis=dict(showgrid=False, color=plotly_text_color),
                                    yaxis=dict(showgrid=True, gridcolor=plotly_grid_color, color=plotly_text_color),
                                    margin=dict(t=0, b=0, l=0, r=0),
                                    font=dict(color=plotly_text_color)
                                )
                                st.plotly_chart(fig_mini, width="stretch")
                            else:
                                st.line_chart(hist_display["Close"])
            else:
                # Physical assets guidance
                value, confidence, _ = ai_valuation(asset)
                image = get_asset_image(asset)
                safe_name = escape_html(asset.get("name", ""))
                value_html = format_currency_html(value, currency_symbol, currency_rate)
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(image["bytes"], width=100)
                    with col2:
                        st.markdown(f"""
                            <div style="background: rgba(30, 30, 40, 0.9); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; border: 1px solid rgba(255,255,255,0.1);">
                                <h3 style="color: var(--text); margin-bottom: 0.5rem;">{safe_name}</h3>
                                <p style="color: var(--muted); margin-bottom: 1rem;">Physical Asset - Market research recommended</p>
                                <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 10px; border-left: 4px solid #d1a843;">
                                    <strong style="color: var(--text);">Valuation Confidence:</strong> <span style="color: #d1a843;">{confidence}%</span><br>
                                    <strong style="color: var(--text);">Estimated Value:</strong> <span style="color: #2ecc71;">{value_html}</span><br>
                                    <strong style="color: var(--text);">Recommendation:</strong> <span style="color: #f39c12;">Check recent eBay sold listings for comparable items</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

# ==============================
# TAB 4: PORTFOLIO STATS
# ==============================
with tab4:
    if not has_plan_at_least(user_settings, "Pro"):
        render_plan_gate(user_settings, "Pro", "Portfolio Stats", "Upgrade to unlock detailed stats and planning snapshots.", key="gate_stats")
    else:
        col1, col2, col3, col4 = st.columns(4)
        entity_view = st.session_state.get("portfolio_entity_view", "All")
        view_items = build_portfolio_view_items(portfolio, entity_view)
        if entity_view != "All":
            st.caption(f"Viewing: {entity_view}")
        total_value = sum(ai_valuation(item["asset"])[0] * item["share"] for item in view_items)
        total_assets = len(view_items)
        physical_assets = len([item for item in view_items if not item["asset"].get("ticker")])
        financial_assets = total_assets - physical_assets

        with col1:
            st.metric("Total Assets", total_assets)
        with col2:
            st.metric("Physical Items", physical_assets)
        with col3:
            st.metric("Financial Assets", financial_assets)
        with col4:
            avg_value = total_value / total_assets if total_assets > 0 else 0
            st.metric("Avg Asset Value", format_currency(avg_value, currency_symbol, currency_rate))

        # Asset type breakdown (used in wealth plan + stats)
        type_stats = {}
        for item in view_items:
            asset = item["asset"]
            t = asset["type"]
            val, _, _ = ai_valuation(asset)
            val *= item["share"]
            if t not in type_stats:
                type_stats[t] = {"count": 0, "value": 0}
            type_stats[t]["count"] += 1
            type_stats[t]["value"] += val

        portfolio_total = total_value if total_value > 0 else 1

        st.subheader("Wealth Plan Snapshot")
        plan_target = user_settings.get("wealth_target_net_worth", 0.0)
        plan_target_date = user_settings.get("wealth_target_date", "")
        plan_risk = user_settings.get("wealth_risk_profile", "Balanced")
        plan_horizon = user_settings.get("wealth_horizon_years", 10)
        plan_tolerance = float(user_settings.get("wealth_rebalance_tolerance", 5.0))
        plan_allocations = user_settings.get("wealth_target_allocations", {}) or {}
        plan_notes = user_settings.get("wealth_advisor_notes", "")

        if plan_target <= 0 and not plan_allocations and not plan_notes:
            st.info("Set your Wealth Plan in Settings to unlock target tracking and rebalancing insights.")
        else:
            col_a, col_b, col_c = st.columns(3)
            liabilities_total = get_total_liabilities_value(liabilities, entity_view)
            net_worth = total_value - liabilities_total
            col_a.metric("Current Net Worth", format_currency(net_worth, currency_symbol, currency_rate))
            if plan_target > 0:
                progress_pct = (net_worth / plan_target) * 100 if plan_target else 0
                col_b.metric("Target Net Worth", format_currency(plan_target, currency_symbol, currency_rate), f"{progress_pct:.1f}%")
            else:
                col_b.metric("Target Net Worth", "Not set")
            col_c.metric("Risk Profile", plan_risk)
            st.caption(f"Horizon: {int(plan_horizon)} years • Rebalance tolerance: {plan_tolerance:.1f}%")

            if plan_target_date:
                try:
                    target_dt = datetime.fromisoformat(plan_target_date)
                    days_left = (target_dt.date() - datetime.now().date()).days
                    st.caption(f"Target date: {format_date_for_settings(target_dt, user_settings)} • {days_left} days remaining")
                except Exception:
                    st.caption(f"Target date: {plan_target_date}")

            if plan_notes:
                st.info(plan_notes)

            if plan_allocations:
                alloc_rows = []
                for asset_type, target_pct in plan_allocations.items():
                    actual_pct = (type_stats.get(asset_type, {}).get("value", 0) / portfolio_total) * 100 if portfolio_total else 0
                    gap = actual_pct - float(target_pct)
                    alloc_rows.append({
                        "Type": asset_type,
                        "Actual %": round(actual_pct, 1),
                        "Target %": round(float(target_pct), 1),
                        "Gap %": round(gap, 1)
                    })
                alloc_df = pd.DataFrame(alloc_rows)
                st.dataframe(alloc_df, width="stretch", hide_index=True)

                rebalance_candidates = [row for row in alloc_rows if abs(row["Gap %"]) >= plan_tolerance]
                if rebalance_candidates:
                    st.markdown("**Rebalance Suggestions**")
                    for row in rebalance_candidates:
                        direction = "Reduce" if row["Gap %"] > 0 else "Increase"
                        st.write(f"- {direction} {row['Type']} by {abs(row['Gap %']):.1f}% to hit target.")

        st.subheader("Detailed Statistics")

        stats_df = pd.DataFrame([
            {
                "Type": t,
                "Count": data["count"],
                "Total Value": format_currency(data["value"], currency_symbol, currency_rate),
                "Avg per Item": format_currency(data["value"]/data["count"], currency_symbol, currency_rate) if data["count"] > 0 else format_currency(0, currency_symbol, currency_rate),
                "% of Portfolio": f"{(data['value']/portfolio_total)*100:.1f}%"
            } for t, data in type_stats.items()
        ])

        st.dataframe(stats_df, width="stretch", hide_index=True)

        # Condition distribution
        st.subheader("Condition Distribution")
        condition_counts = {}
        for item in view_items:
            asset = item["asset"]
            c = asset["condition"]
            condition_counts[c] = condition_counts.get(c, 0) + 1

        if condition_counts:
            if PLOTLY_AVAILABLE:
                fig_cond = go.Figure(data=[go.Bar(
                    x=list(condition_counts.keys()),
                    y=list(condition_counts.values()),
                    marker_color=[get_condition_color(c) for c in condition_counts.keys()],
                    text=list(condition_counts.values()),
                    textposition='auto',
                    textfont=dict(color=plotly_text_color)
                )])
                fig_cond.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(color=plotly_text_color, title='Condition'),
                    yaxis=dict(color=plotly_text_color, showgrid=True, gridcolor=plotly_grid_color),
                    height=300,
                    font=dict(color=plotly_text_color)
                )
                st.plotly_chart(fig_cond, width="stretch")
            else:
                cond_df = pd.DataFrame({
                    'Condition': list(condition_counts.keys()),
                    'Count': list(condition_counts.values())
                }).set_index('Condition')
                st.bar_chart(cond_df)

        st.subheader("Entity & Custody Breakdown")
        if entity_view == "All":
            entity_stats = {}
            for asset in portfolio:
                wealth = asset.get("wealth", {})
                split = wealth.get("ownership_split") if isinstance(wealth.get("ownership_split"), dict) else {}
                val, _, _ = ai_valuation(asset)
                if split:
                    for ent_name, pct in split.items():
                        try:
                            share = float(pct) / 100.0
                        except Exception:
                            continue
                        if ent_name not in entity_stats:
                            entity_stats[ent_name] = {"count": 0, "value": 0}
                        entity_stats[ent_name]["count"] += 1
                        entity_stats[ent_name]["value"] += val * share
                else:
                    entity = wealth.get("owner_entity") or "Unassigned"
                    if entity not in entity_stats:
                        entity_stats[entity] = {"count": 0, "value": 0}
                    entity_stats[entity]["count"] += 1
                    entity_stats[entity]["value"] += val
            if entity_stats:
                entity_df = pd.DataFrame([
                    {
                        "Entity": entity,
                        "Count": data["count"],
                        "Total Value": format_currency(data["value"], currency_symbol, currency_rate)
                    } for entity, data in entity_stats.items()
                ])
                st.dataframe(entity_df, width="stretch", hide_index=True)
            else:
                st.info("Add owner/entity info in Wealth Management to see this breakdown.")
        else:
            st.info("Entity breakdown is available in the consolidated view.")

        st.subheader("Upcoming Reviews")
        review_rows = []
        today = datetime.now().date()
        for item in view_items:
            asset = item["asset"]
            review_raw = asset.get("wealth", {}).get("review_date")
            if not review_raw:
                continue
            try:
                review_dt = datetime.fromisoformat(str(review_raw)).date()
            except Exception:
                continue
            review_rows.append({
                "Asset": asset.get("name", "Asset"),
                "Review Date": review_dt,
                "Days Until": (review_dt - today).days
            })
        if review_rows:
            review_rows.sort(key=lambda x: x["Review Date"])
            review_df = pd.DataFrame(review_rows)
            review_df["Review Date"] = review_df["Review Date"].astype(str)
            st.dataframe(review_df, width="stretch", hide_index=True)
        else:
            st.info("No upcoming reviews set. Add review dates in Wealth Management.")

        st.subheader("Insurance Coverage")
        insured_total = 0.0
        for item in view_items:
            asset = item["asset"]
            insured_total += float(asset.get("wealth", {}).get("insured_value", 0.0) or 0.0) * item["share"]
        if insured_total > 0:
            coverage_pct = (insured_total / total_value * 100) if total_value else 0
            st.metric("Total Insured Value", format_currency(insured_total, currency_symbol, currency_rate), f"{coverage_pct:.1f}% of portfolio")
        else:
            st.info("Add insured values in Wealth Management to track coverage.")

# ==============================
# TAB 5: ADD ASSET (ENHANCED WITH AUTO-IMAGE)
# ==============================
with tab5:
    st.subheader("Add New Asset")

    name = st.text_input("Asset Name", key="asset_name", placeholder="e.g., Vintage Rolex")
    query = (name or "").strip()
    suggestions = []
    if len(query) >= 2:
        cache_key = f"suggest_{query.lower()}"
        cached = get_cache(cache_key, 600)
        if cached is not None:
            suggestions = cached
        else:
            with st.spinner("Searching..."):
                suggestions = get_asset_suggestions(query, user_settings, portfolio)
    if suggestions:
        selection = st.selectbox("Search Results", ["Select a result..."] + suggestions, key="asset_name_suggestion")
        st.caption("Results ranked by relevance.")
        if selection != "Select a result..." and selection != name:
            st.session_state.asset_name = selection
            st.rerun()

    with st.form("add_asset_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            type_options = ASSET_TYPE_OPTIONS
            default_type = user_settings.get("default_asset_type", "Other")
            type_index = type_options.index(default_type) if default_type in type_options else len(type_options) - 1
            asset_type = st.selectbox("Type", type_options, index=type_index)
            qty = st.number_input("Quantity", min_value=1, value=1)
        
        with col2:
            condition_options = ["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"]
            default_condition = user_settings.get("default_condition", "Excellent")
            cond_index = condition_options.index(default_condition) if default_condition in condition_options else 1
            condition = st.selectbox("Condition", condition_options, index=cond_index)
            ticker = st.text_input("Ticker (optional)", placeholder="e.g., AAPL, GC=F")
            market_price_display = st.number_input(f"Market Price per Unit ({currency_code})", min_value=0.0, value=0.0, step=0.01)

        st.markdown("### Type Details")
        detail_key_prefix = f"add_{asset_type.replace(' ', '_').lower()}"
        details = render_type_fields(asset_type, {}, detail_key_prefix, currency_code, currency_symbol, currency_rate, weight_unit)

        country_code = get_country_code(user_settings)
        country_name = get_country_name(country_code)
        examples = ", ".join(get_local_entity_examples(country_code))
        local_hint = get_local_entity_hint(country_code)
        st.markdown("### Wealth Management")
        st.caption(f"Founder tip for {country_name}: assign the right entity ({examples}) to keep clean separation.")
        st.caption(local_hint)
        wealth = render_wealth_fields({}, "add_wealth", currency_code, currency_symbol, currency_rate, entity_names)
        
        # Live image preview based on name
        image_preview = None
        if name:
            image_preview = search_asset_image(name)
            st.markdown("**Preview Image:**")
            cols = st.columns([1, 2, 1])
            with cols[1]:
                st.image(image_preview, width=200, caption="Auto-selected based on asset name")
        
        images = st.file_uploader(
            "Upload Custom Images (Optional)",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True
        )
        
        # Custom image preview
        if images:
            st.markdown("**Uploaded Images:**")
            img_cols = st.columns(len(images))
            for idx, img in enumerate(images):
                with img_cols[idx]:
                    st.image(img, width=150, caption="Custom " + str(idx+1))
        
        notes = st.text_area("Notes", placeholder="Additional details about the asset...")
        
        submitted = st.form_submit_button("Add to Portfolio", width="stretch")
        
        if submitted:
            name_value = (st.session_state.get("asset_name") or "").strip()
            if not name_value:
                st.error("Please enter an asset name")
            else:
                # Store uploaded images as base64 so they can be persisted in JSON
                img_list = encode_uploaded_images(images) if images else []
                
                # Always keep a fallback image URL
                img_url = search_asset_image(name_value)
                
                portfolio.append({
                    "name": name_value,
                    "type": asset_type,
                    "qty": qty,
                    "condition": condition,
                    "ticker": ticker if ticker else None,
                    "market_price": from_display_currency(market_price_display, currency_rate),
                    "images": img_list,
                    "image_url": img_url,
                    "notes": notes,
                    "details": details,
                    "wealth": wealth,
                    "added": str(datetime.now())
                })
                
                save_data(db)
                st.success("Asset added successfully!")
                record = ensure_user_record(db, user)
                settings = record.get("settings", {})
                settings["onboarding_completed"] = True
                record["settings"] = settings
                save_data(db)
                st.session_state.asset_name = ""
                if "asset_name_suggestion" in st.session_state:
                    st.session_state.asset_name_suggestion = "Select a result..."
                st.session_state.jump_to_portfolio = True
                st.rerun()

# ==============================
# TAB 6: EDIT ASSETS
# ==============================
with tab6:
    st.subheader("Edit Existing Assets")
    render_delete_confirmation(portfolio, currency_symbol, currency_rate)
    
    if not portfolio:
        st.info("No assets to modify. Add some assets first!")
    else:
        # Quick delete section
        st.markdown("### Quick Actions")
        
        # Bulk delete with confirmation
        with st.expander("Bulk Delete Assets"):
            st.warning("Warning: This action cannot be undone!")
            
            # List all assets for selection
            asset_options = {f"{i+1}. {asset['name']} - {asset['type']} ({format_currency(ai_valuation(asset)[0], currency_symbol, currency_rate)})": i 
                            for i, asset in enumerate(portfolio)}
            
            selected_assets = st.multiselect(
                "Select assets to delete:",
                options=list(asset_options.keys()),
                placeholder="Choose assets to remove..."
            )
            
            if selected_assets and st.button("Delete Selected Assets", type="secondary"):
                # Get indices of selected assets
                indices_to_delete = [asset_options[asset] for asset in selected_assets]
                # Sort in reverse order to avoid index shifting issues
                indices_to_delete.sort(reverse=True)
                
                # Delete assets
                for idx in indices_to_delete:
                    if 0 <= idx < len(portfolio):
                        portfolio.pop(idx)
                
                save_data(db)
                st.success(f"Deleted {len(indices_to_delete)} asset(s) successfully!")
                request_scroll_to_top()
                st.rerun()
        
        # Individual asset modification
        st.markdown("### Edit Individual Assets")
        
        # Create a dropdown to select asset to edit
        asset_options = [f"{i+1}. {asset['name']} - {asset['type']}" for i, asset in enumerate(portfolio)]
        default_index = st.session_state.get("selected_asset_index", 0)
        if default_index >= len(asset_options):
            default_index = 0
        selected_asset = st.selectbox(
            "Select an asset to edit:",
            options=asset_options,
            index=default_index,
            placeholder="Choose an asset..."
        )
        
        if selected_asset:
            asset_index = int(selected_asset.split(".")[0]) - 1
            asset = portfolio[asset_index]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Current Name:** {asset['name']}")
                st.markdown(f"**Type:** {asset['type']}")
                st.markdown(f"**Quantity:** {asset['qty']}")
                
                image = get_asset_image(asset)
                st.image(image["bytes"], caption="Current Image", width=200)
            
            with col2:
                st.markdown(f"**Condition:** {asset['condition']}")
                if asset.get("ticker"):
                    st.markdown(f"**Ticker:** {asset['ticker']}")
                st.markdown(f"**Market Price:** {format_currency(get_effective_market_price(asset), currency_symbol, currency_rate)}")
                st.markdown(f"**AI Valuation:** {format_currency(ai_valuation(asset)[0], currency_symbol, currency_rate)}")
                if asset.get("details"):
                    render_details_list(asset.get("details"), currency_symbol, currency_rate, weight_unit)
                if asset.get("wealth"):
                    render_wealth_list(asset.get("wealth"), currency_symbol, currency_rate, user_settings)
            
            # Edit form
            st.markdown("---")
            st.markdown("### Edit Asset Details")
            
            with st.form(f"edit_form_{asset_index}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_name_raw = st.text_input("Asset Name", value=asset["name"])
                    new_name = new_name_raw.strip()
                    type_options = ASSET_TYPE_OPTIONS
                    try:
                        type_index = type_options.index(asset["type"])
                    except ValueError:
                        type_index = len(type_options) - 1
                    new_type = st.selectbox(
                        "Type", 
                        type_options,
                        index=type_index
                    )
                    new_qty = st.number_input("Quantity", min_value=1, value=asset["qty"])
                
                with col2:
                    new_condition = st.selectbox(
                        "Condition",
                        ["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"],
                        index=["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"].index(asset["condition"])
                    )
                    new_ticker = st.text_input("Ticker (optional)", 
                                              value=asset.get("ticker", "") if asset.get("ticker") else "")
                    current_price_display = to_display_currency(asset.get("market_price", 0.0), currency_rate)
                    new_market_price_display = st.number_input(f"Market Price per Unit ({currency_code})", 
                                                      min_value=0.0, 
                                                      value=float(current_price_display), 
                                                      step=0.01)
                
                st.markdown("#### Type Details")
                detail_key_prefix = f"edit_{asset_index}_{new_type.replace(' ', '_').lower()}"
                new_details = render_type_fields(new_type, asset.get("details", {}), detail_key_prefix, currency_code, currency_symbol, currency_rate, weight_unit)

                country_code = get_country_code(user_settings)
                country_name = get_country_name(country_code)
                examples = ", ".join(get_local_entity_examples(country_code))
                local_hint = get_local_entity_hint(country_code)
                st.markdown("#### Wealth Management")
                st.caption(f"Founder tip for {country_name}: assign the right entity ({examples}) to keep clean separation.")
                st.caption(local_hint)
                wealth_key_prefix = f"edit_{asset_index}_wealth"
                new_wealth = render_wealth_fields(asset.get("wealth", {}), wealth_key_prefix, currency_code, currency_symbol, currency_rate, entity_names)

                new_notes = st.text_area("Notes", 
                                        value=asset.get("notes", ""), 
                                        placeholder="Additional details about the asset...")
                
                # Image update options
                st.markdown("#### Update Image")
                new_image_url = st.text_input("Custom Image URL (optional)", 
                                            placeholder="Leave blank to use auto-generated image")
                new_images = st.file_uploader(
                    "Upload New Images (Optional)",
                    type=["jpg", "png", "jpeg"],
                    accept_multiple_files=True,
                    key=f"edit_images_{asset_index}"
                )
                if new_images:
                    st.markdown("**New Uploaded Images:**")
                    img_cols = st.columns(len(new_images))
                    for idx, img in enumerate(new_images):
                        with img_cols[idx]:
                            st.image(img, width=150, caption="New " + str(idx + 1))
                
                col_save, col_delete = st.columns(2)
                
                with col_save:
                    save_changes = st.form_submit_button("Save Changes", width="stretch")
                
                with col_delete:
                    # Delete button in form
                    delete_current = st.form_submit_button("Delete This Asset", type="secondary", width="stretch")
                
                if save_changes:
                    # Update the asset
                    if not new_name:
                        st.error("Asset name cannot be empty.")
                    else:
                        updated_images = asset.get("images", [])
                        if new_images:
                            updated_images = encode_uploaded_images(new_images)
                        portfolio[asset_index] = {
                            "name": new_name,
                            "type": new_type,
                            "qty": new_qty,
                            "condition": new_condition,
                            "ticker": new_ticker if new_ticker else None,
                            "market_price": from_display_currency(new_market_price_display, currency_rate),
                            "images": updated_images,
                            "image_url": new_image_url if new_image_url else search_asset_image(new_name),
                            "notes": new_notes,
                            "details": new_details,
                            "wealth": new_wealth,
                            "added": asset.get("added", str(datetime.now()))  # Keep original added date
                        }
                        
                        save_data(db)
                        st.success("Asset updated successfully!")
                        st.rerun()
                
                if delete_current:
                    request_delete(asset_index)
                    st.rerun()

# ==============================
# TAB 7: ENTITIES & LIABILITIES
# ==============================
with tab7:
    st.subheader("Entities & Liabilities")

    entities = user_record.get("entities", [])
    liabilities = user_record.get("liabilities", [])
    entity_stat_names = list(entity_names)
    extra_entities = set()
    for asset in portfolio:
        owner = asset.get("wealth", {}).get("owner_entity")
        if owner and owner not in entity_stat_names:
            extra_entities.add(owner)
    for liability in liabilities:
        owner = liability.get("owner_entity")
        if owner and owner not in entity_stat_names:
            extra_entities.add(owner)
    if extra_entities:
        entity_stat_names.extend(sorted(extra_entities))

    total_assets_all = get_total_assets_value(portfolio, "All")
    total_liabilities_all = get_total_liabilities_value(liabilities, "All")
    net_worth_all = total_assets_all - total_liabilities_all
    debt_ratio = (total_liabilities_all / total_assets_all * 100) if total_assets_all else 0.0

    stat_cols = st.columns(4)
    stat_cols[0].metric("Total Assets", format_currency(total_assets_all, currency_symbol, currency_rate))
    stat_cols[1].metric("Total Liabilities", format_currency(total_liabilities_all, currency_symbol, currency_rate))
    stat_cols[2].metric("Net Worth", format_currency(net_worth_all, currency_symbol, currency_rate))
    stat_cols[3].metric("Debt Ratio", f"{debt_ratio:.1f}%")

    st.markdown("### Founder Playbook")
    country_code = get_country_code(user_settings)
    country_name = get_country_name(country_code)
    examples = ", ".join(get_local_entity_examples(country_code))
    local_hint = get_local_entity_hint(country_code)
    st.info(
        f"If you're a small business owner in {country_name}, start by separating Personal, Business, and Trust assets. "
        f"Common local structures include: {examples}. "
        "Assign ownership, track liabilities, and set review dates so your wealth plan stays active. "
        "This tool helps you organize — it isn't legal or financial advice."
    )
    st.caption(local_hint)

    st.markdown("### Entities")
    if entities:
        entity_rows = []
        for entity in entities:
            entity_rows.append({
                "Name": entity.get("name", ""),
                "Type": entity.get("type", ""),
                "Members": ", ".join(entity.get("members", []))
            })
        st.dataframe(pd.DataFrame(entity_rows), width="stretch", hide_index=True)
    else:
        st.info("No entities found. Add your first entity below.")

    st.markdown("### Entity Statements")
    entity_statement_rows = []
    for entity_name in entity_stat_names:
        assets_value = get_total_assets_value(portfolio, entity_name)
        liab_value = get_total_liabilities_value(liabilities, entity_name)
        net_value = assets_value - liab_value
        insured_value = 0.0
        for asset in portfolio:
            share = get_asset_share(asset, entity_name)
            if share <= 0:
                continue
            insured_value += float(asset.get("wealth", {}).get("insured_value", 0.0) or 0.0) * share
        debt_ratio_entity = (liab_value / assets_value * 100) if assets_value else 0.0
        entity_statement_rows.append({
            "Entity": entity_name,
            "Assets": format_currency(assets_value, currency_symbol, currency_rate),
            "Liabilities": format_currency(liab_value, currency_symbol, currency_rate),
            "Net Worth": format_currency(net_value, currency_symbol, currency_rate),
            "Insured": format_currency(insured_value, currency_symbol, currency_rate),
            "Debt Ratio": f"{debt_ratio_entity:.1f}%"
        })
    if entity_statement_rows:
        st.dataframe(pd.DataFrame(entity_statement_rows), width="stretch", hide_index=True)

    for entity_name in entity_stat_names:
        with st.expander(f"{entity_name} Statement"):
            assets_value = get_total_assets_value(portfolio, entity_name)
            liab_value = get_total_liabilities_value(liabilities, entity_name)
            net_value = assets_value - liab_value
            st.write(f"**Assets:** {format_currency(assets_value, currency_symbol, currency_rate)}")
            st.write(f"**Liabilities:** {format_currency(liab_value, currency_symbol, currency_rate)}")
            st.write(f"**Net Worth:** {format_currency(net_value, currency_symbol, currency_rate)}")

            asset_rows = []
            for asset in portfolio:
                share = get_asset_share(asset, entity_name)
                if share <= 0:
                    continue
                value, _, _ = ai_valuation(asset)
                wealth = asset.get("wealth", {})
                asset_rows.append({
                    "Asset": asset.get("name", ""),
                    "Type": asset.get("type", ""),
                    "Ownership %": f"{share*100:.1f}%",
                    "Value": format_currency(value * share, currency_symbol, currency_rate),
                    "Beneficiary": wealth.get("beneficiary", ""),
                    "Custodian": wealth.get("custodian", "")
                })
            if asset_rows:
                st.markdown("**Assets**")
                st.dataframe(pd.DataFrame(asset_rows), width="stretch", hide_index=True)
            else:
                st.info("No assets assigned to this entity.")

            liab_rows = []
            for liability in liabilities:
                share = get_liability_share(liability, entity_name)
                if share <= 0:
                    continue
                liab_rows.append({
                    "Liability": liability.get("name", ""),
                    "Type": liability.get("type", ""),
                    "Ownership %": f"{share*100:.1f}%",
                    "Balance": format_currency(float(liability.get("balance", 0.0) or 0.0) * share, currency_symbol, currency_rate),
                    "Rate %": liability.get("interest_rate", 0.0)
                })
            if liab_rows:
                st.markdown("**Liabilities**")
                st.dataframe(pd.DataFrame(liab_rows), width="stretch", hide_index=True)
            else:
                st.info("No liabilities assigned to this entity.")

    with st.form("add_entity_form"):
        new_entity_name = st.text_input("Entity Name", placeholder="e.g., Personal, Family Trust", key="add_entity_name")
        new_entity_type = st.selectbox("Entity Type", ENTITY_TYPES, index=0, key="add_entity_type")
        new_entity_members = st.text_input("Members (comma-separated)", placeholder="e.g., Alice, Bob", key="add_entity_members")
        new_entity_notes = st.text_area("Notes", placeholder="Optional notes about this entity", key="add_entity_notes")
        add_entity_submit = st.form_submit_button("Add Entity", width="stretch")

    if add_entity_submit:
        name = normalize_entity_name(new_entity_name)
        existing_names = {e.get("name", "").lower() for e in entities}
        if not name:
            st.error("Entity name is required.")
        elif name.lower() in existing_names:
            st.error("An entity with that name already exists.")
        else:
            members = [m.strip() for m in new_entity_members.split(",") if m.strip()]
            entities.append(build_entity(name, new_entity_type, members, new_entity_notes))
            user_record["entities"] = entities
            save_data(db)
            st.success("Entity added.")
            st.rerun()

    if entities:
        st.markdown("#### Edit Entity")
        entity_names_list = [e.get("name") for e in entities if e.get("name")]
        selected_entity_name = st.selectbox("Select Entity", entity_names_list)
        selected_entity = next((e for e in entities if e.get("name") == selected_entity_name), None)
        if selected_entity:
            with st.form("edit_entity_form"):
                edit_name = st.text_input("Entity Name", value=selected_entity.get("name", ""), key="edit_entity_name")
                edit_type = st.selectbox(
                    "Entity Type",
                    ENTITY_TYPES,
                    index=ENTITY_TYPES.index(selected_entity.get("type", "Other"))
                    if selected_entity.get("type", "Other") in ENTITY_TYPES else len(ENTITY_TYPES) - 1,
                    key="edit_entity_type"
                )
                edit_members_text = st.text_input(
                    "Members (comma-separated)",
                    value=", ".join(selected_entity.get("members", [])),
                    key="edit_entity_members"
                )
                edit_notes = st.text_area("Notes", value=selected_entity.get("notes", ""), key="edit_entity_notes")
                confirm_delete = st.checkbox("Confirm delete this entity", key="edit_entity_confirm_delete")
                col_save, col_delete = st.columns(2)
                save_entity = col_save.form_submit_button("Save Changes", width="stretch")
                delete_entity = col_delete.form_submit_button("Delete Entity", width="stretch")

            if save_entity:
                new_name = normalize_entity_name(edit_name)
                if not new_name:
                    st.error("Entity name is required.")
                else:
                    existing = {e.get("name", "").lower() for e in entities if e.get("name") != selected_entity.get("name")}
                    if new_name.lower() in existing:
                        st.error("An entity with that name already exists.")
                    else:
                        old_name = selected_entity.get("name")
                        selected_entity["name"] = new_name
                        selected_entity["type"] = edit_type
                        selected_entity["members"] = [m.strip() for m in edit_members_text.split(",") if m.strip()]
                        selected_entity["notes"] = edit_notes
                        if old_name != new_name:
                            update_entity_references(portfolio, liabilities, old_name, new_name)
                        save_data(db)
                        st.success("Entity updated.")
                        st.rerun()

            if delete_entity:
                if not confirm_delete:
                    st.error("Please confirm deletion.")
                elif len(entities) <= 1:
                    st.error("At least one entity must remain.")
                else:
                    entities = [e for e in entities if e.get("name") != selected_entity.get("name")]
                    user_record["entities"] = entities
                    # Update references to removed entity
                    removed_name = selected_entity.get("name")
                    for asset in portfolio:
                        wealth = asset.get("wealth", {})
                        if wealth.get("owner_entity") == removed_name:
                            wealth["owner_entity"] = "Unassigned"
                        split = wealth.get("ownership_split")
                        if isinstance(split, dict) and removed_name in split:
                            split.pop(removed_name, None)
                            if not split:
                                wealth.pop("ownership_split", None)
                        asset["wealth"] = wealth
                    for liability in liabilities:
                        if liability.get("owner_entity") == removed_name:
                            liability["owner_entity"] = "Unassigned"
                        split = liability.get("ownership_split")
                        if isinstance(split, dict) and removed_name in split:
                            split.pop(removed_name, None)
                            if not split:
                                liability.pop("ownership_split", None)
                    save_data(db)
                    st.success("Entity deleted.")
                    st.rerun()

    st.markdown("---")
    st.markdown("### Liabilities")

    if liabilities:
        liab_type_stats = {}
        for liability in liabilities:
            l_type = liability.get("type", "Other")
            liab_type_stats[l_type] = liab_type_stats.get(l_type, 0) + float(liability.get("balance", 0.0) or 0.0)
        liab_df = pd.DataFrame([
            {"Type": t, "Balance": format_currency(v, currency_symbol, currency_rate)} for t, v in liab_type_stats.items()
        ])
        st.dataframe(liab_df, width="stretch", hide_index=True)
    else:
        st.info("No liabilities added yet.")

    with st.form("add_liability_form"):
        liab_name = st.text_input("Liability Name", placeholder="e.g., Home Mortgage", key="add_liab_name")
        liab_type = st.selectbox("Liability Type", LIABILITY_TYPES, index=0, key="add_liab_type")
        liab_balance = st.number_input(f"Current Balance ({currency_code})", min_value=0.0, value=0.0, step=100.0, key="add_liab_balance")
        liab_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=0.0, step=0.1, format="%.2f", key="add_liab_rate")
        liab_payment = st.number_input(f"Monthly Payment ({currency_code})", min_value=0.0, value=0.0, step=10.0, key="add_liab_payment")
        liab_term = st.number_input("Term (months)", min_value=0, value=0, step=1, key="add_liab_term")

        owner_entity = None
        owner_choices = ["Unassigned"] + list(entity_names)
        owner_choices.append("Custom")
        owner_entity = st.selectbox("Owner / Entity", owner_choices, index=0, key="add_liab_owner")
        if owner_entity == "Custom":
            owner_entity = st.text_input("Custom Owner / Entity", value="", key="liab_owner_custom")

        start_date_enabled = st.checkbox("Set start date", value=False, key="liab_start_enable")
        start_date_value = ""
        if start_date_enabled:
            start_date_value = st.date_input("Start Date", value=datetime.now().date(), key="liab_start_date").isoformat()
        due_date_enabled = st.checkbox("Set due date", value=False, key="liab_due_enable")
        due_date_value = ""
        if due_date_enabled:
            due_date_value = st.date_input("Due Date", value=datetime.now().date(), key="liab_due_date").isoformat()

        split_enabled = st.checkbox("Split ownership across entities", value=False, key="liab_split_enable")
        ownership_split = {}
        if split_enabled:
            st.caption("Enter ownership percentages by entity (aim for 100%).")
            split_cols = st.columns(2)
            for idx, name in enumerate(entity_names):
                with split_cols[idx % 2]:
                    ownership_split[name] = st.number_input(
                        f"{name} %",
                        min_value=0.0,
                        max_value=100.0,
                        value=0.0,
                        step=1.0,
                        key=f"liab_split_{name}"
                    )
            total_pct = sum(ownership_split.values())
            if total_pct > 0 and abs(total_pct - 100.0) > 0.5:
                st.warning(f"Ownership split totals {total_pct:.1f}% (aim for 100%).")
            ownership_split = {k: v for k, v in ownership_split.items() if v > 0}

        liab_notes = st.text_area("Notes", placeholder="Optional notes", key="add_liab_notes")
        add_liability_submit = st.form_submit_button("Add Liability", width="stretch")

    if add_liability_submit:
        if not liab_name:
            st.error("Liability name is required.")
        else:
            liabilities.append({
                "id": secrets.token_hex(6),
                "name": liab_name.strip(),
                "type": liab_type,
                "balance": from_display_currency(liab_balance, currency_rate),
                "interest_rate": float(liab_rate),
                "payment": from_display_currency(liab_payment, currency_rate),
                "term_months": int(liab_term),
                "owner_entity": normalize_entity_name(owner_entity) if owner_entity else "Unassigned",
                "ownership_split": ownership_split if ownership_split else {},
                "start_date": start_date_value,
                "due_date": due_date_value,
                "notes": liab_notes.strip(),
                "created_at": datetime.now().isoformat()
            })
            user_record["liabilities"] = liabilities
            save_data(db)
            st.success("Liability added.")
            st.rerun()

    if liabilities:
        st.markdown("#### Manage Liabilities")
        for idx, liability in enumerate(liabilities):
            balance_value = liability.get("balance", 0.0)
            with st.expander(f"{liability.get('name', 'Liability')} — {format_currency(balance_value, currency_symbol, currency_rate)}"):
                with st.form(f"edit_liability_{liability.get('id', idx)}"):
                    edit_name = st.text_input(
                        "Liability Name",
                        value=liability.get("name", ""),
                        key=f"edit_liab_name_{liability.get('id', idx)}"
                    )
                    edit_type = st.selectbox(
                        "Liability Type",
                        LIABILITY_TYPES,
                        index=LIABILITY_TYPES.index(liability.get("type", "Other"))
                        if liability.get("type", "Other") in LIABILITY_TYPES else len(LIABILITY_TYPES) - 1,
                        key=f"edit_liab_type_{liability.get('id', idx)}"
                    )
                    edit_balance_display = to_display_currency(liability.get("balance", 0.0), currency_rate)
                    edit_balance = st.number_input(
                        f"Current Balance ({currency_code})",
                        min_value=0.0,
                        value=float(edit_balance_display),
                        step=100.0,
                        key=f"edit_liab_balance_{liability.get('id', idx)}"
                    )
                    edit_rate = st.number_input(
                        "Interest Rate (%)",
                        min_value=0.0,
                        value=float(liability.get("interest_rate", 0.0) or 0.0),
                        step=0.1,
                        format="%.2f",
                        key=f"edit_liab_rate_{liability.get('id', idx)}"
                    )
                    edit_payment_display = to_display_currency(liability.get("payment", 0.0), currency_rate)
                    edit_payment = st.number_input(
                        f"Monthly Payment ({currency_code})",
                        min_value=0.0,
                        value=float(edit_payment_display),
                        step=10.0,
                        key=f"edit_liab_payment_{liability.get('id', idx)}"
                    )
                    edit_term = st.number_input(
                        "Term (months)",
                        min_value=0,
                        value=int(liability.get("term_months", 0) or 0),
                        step=1,
                        key=f"edit_liab_term_{liability.get('id', idx)}"
                    )
                    owner_choices = ["Unassigned"] + list(entity_names)
                    owner_choices.append("Custom")
                    current_owner = liability.get("owner_entity", "Unassigned")
                    if current_owner not in owner_choices:
                        owner_choices.insert(1, current_owner)
                    edit_owner = st.selectbox(
                        "Owner / Entity",
                        owner_choices,
                        index=owner_choices.index(current_owner) if current_owner in owner_choices else 0,
                        key=f"liab_owner_{liability.get('id', idx)}"
                    )
                    if edit_owner == "Custom":
                        edit_owner = st.text_input(
                            "Custom Owner / Entity",
                            value=liability.get("owner_entity", ""),
                            key=f"liab_owner_custom_{liability.get('id', idx)}"
                        )

                    edit_start_enabled = st.checkbox(
                        "Set start date",
                        value=bool(liability.get("start_date")),
                        key=f"liab_start_enable_{liability.get('id', idx)}"
                    )
                    if edit_start_enabled:
                        try:
                            start_dt = datetime.fromisoformat(liability.get("start_date")).date()
                        except Exception:
                            start_dt = datetime.now().date()
                        edit_start_date = st.date_input(
                            "Start Date",
                            value=start_dt,
                            key=f"liab_start_{liability.get('id', idx)}"
                        ).isoformat()
                    else:
                        edit_start_date = ""

                    edit_due_enabled = st.checkbox(
                        "Set due date",
                        value=bool(liability.get("due_date")),
                        key=f"liab_due_enable_{liability.get('id', idx)}"
                    )
                    if edit_due_enabled:
                        try:
                            due_dt = datetime.fromisoformat(liability.get("due_date")).date()
                        except Exception:
                            due_dt = datetime.now().date()
                        edit_due_date = st.date_input(
                            "Due Date",
                            value=due_dt,
                            key=f"liab_due_{liability.get('id', idx)}"
                        ).isoformat()
                    else:
                        edit_due_date = ""

                    edit_split_existing = liability.get("ownership_split") if isinstance(liability.get("ownership_split"), dict) else {}
                    edit_split_enabled = st.checkbox(
                        "Split ownership across entities",
                        value=bool(edit_split_existing),
                        key=f"liab_split_enable_{liability.get('id', idx)}"
                    )
                    edit_split = {}
                    if edit_split_enabled:
                        st.caption("Enter ownership percentages by entity (aim for 100%).")
                        split_cols = st.columns(2)
                        for s_idx, name in enumerate(entity_names):
                            with split_cols[s_idx % 2]:
                                edit_split[name] = st.number_input(
                                    f"{name} %",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=float(edit_split_existing.get(name, 0.0) or 0.0),
                                    step=1.0,
                                    key=f"liab_edit_split_{liability.get('id', idx)}_{name}"
                                )
                        total_pct = sum(edit_split.values())
                        if total_pct > 0 and abs(total_pct - 100.0) > 0.5:
                            st.warning(f"Ownership split totals {total_pct:.1f}% (aim for 100%).")
                        edit_split = {k: v for k, v in edit_split.items() if v > 0}
                    edit_notes = st.text_area(
                        "Notes",
                        value=liability.get("notes", ""),
                        key=f"edit_liab_notes_{liability.get('id', idx)}"
                    )

                    save_liability = st.form_submit_button(
                        "Save Liability",
                        width="stretch",
                        key=f"save_liab_{liability.get('id', idx)}"
                    )
                    delete_liability = st.form_submit_button(
                        "Delete Liability",
                        width="stretch",
                        key=f"delete_liab_{liability.get('id', idx)}"
                    )

                if save_liability:
                    liability["name"] = edit_name.strip()
                    liability["type"] = edit_type
                    liability["balance"] = from_display_currency(edit_balance, currency_rate)
                    liability["interest_rate"] = float(edit_rate)
                    liability["payment"] = from_display_currency(edit_payment, currency_rate)
                    liability["term_months"] = int(edit_term)
                    liability["owner_entity"] = normalize_entity_name(edit_owner) if edit_owner else "Unassigned"
                    liability["ownership_split"] = edit_split if edit_split_enabled else {}
                    liability["start_date"] = edit_start_date
                    liability["due_date"] = edit_due_date
                    liability["notes"] = edit_notes.strip()
                    save_data(db)
                    st.success("Liability updated.")
                    st.rerun()

                if delete_liability:
                    liabilities.pop(idx)
                    save_data(db)
                    st.success("Liability deleted.")
                    st.rerun()

                est_payment = estimate_monthly_payment(
                    liability.get("balance"),
                    liability.get("interest_rate"),
                    liability.get("term_months")
                )
                if est_payment:
                    st.caption(f"Estimated payment: {format_currency(est_payment, currency_symbol, currency_rate)} / month")
                payoff_months = estimate_payoff_months(
                    liability.get("balance"),
                    liability.get("interest_rate"),
                    liability.get("payment")
                )
                if payoff_months:
                    st.caption(f"Estimated payoff: {payoff_months/12:.1f} years")

                st.markdown("##### Amortization Schedule")
                schedule_df, total_interest = build_amortization_schedule(
                    liability.get("balance"),
                    liability.get("interest_rate"),
                    liability.get("payment"),
                    liability.get("term_months")
                )
                if schedule_df is None or schedule_df.empty:
                    st.caption("Provide a payment or term to generate a schedule.")
                else:
                    schedule_display = schedule_df.copy()
                    for col in ["Payment", "Principal", "Interest", "Balance"]:
                        schedule_display[col] = schedule_display[col].apply(lambda v: to_display_currency(v, currency_rate))
                    st.metric("Total Interest", format_currency(total_interest, currency_symbol, currency_rate))
                    payoff_date = compute_payoff_date(liability)
                    if payoff_date:
                        st.caption(f"Estimated payoff date: {payoff_date.isoformat()}")
                    st.line_chart(schedule_display.set_index("Month")["Balance"])
                    st.dataframe(schedule_display.head(120), width="stretch")
                    st.download_button(
                        "Download Schedule (CSV)",
                        schedule_display.to_csv(index=False),
                        file_name=f"{liability.get('name', 'liability').replace(' ', '_').lower()}_schedule.csv",
                        mime="text/csv"
                    )

    st.markdown("### Payoff Calendar")
    payoff_rows = []
    for liability in liabilities:
        balance = liability.get("balance", 0.0)
        payoff_date = compute_payoff_date(liability)
        payoff_rows.append({
            "Liability": liability.get("name", ""),
            "Owner": liability.get("owner_entity", ""),
            "Balance": format_currency(balance, currency_symbol, currency_rate),
            "Payment": format_currency(liability.get("payment", 0.0), currency_symbol, currency_rate),
            "Start Date": liability.get("start_date", ""),
            "Due Date": liability.get("due_date", ""),
            "Estimated Payoff": payoff_date.isoformat() if payoff_date else ""
        })

    if payoff_rows:
        st.dataframe(pd.DataFrame(payoff_rows), width="stretch", hide_index=True)
    else:
        st.info("Add liabilities to see payoff dates.")

    st.markdown("### Upcoming Events")
    events = []
    today = datetime.now().date()
    reminder_enabled = bool(user_settings.get("event_include_reminders", True))
    reminder_days = int(user_settings.get("event_reminder_days", 30) or 30)

    for asset in portfolio:
        review_raw = asset.get("wealth", {}).get("review_date")
        if review_raw:
            try:
                review_dt = datetime.fromisoformat(str(review_raw)).date()
                events.append({
                    "date": review_dt,
                    "type": "Review",
                    "name": asset.get("name", ""),
                    "owner": asset.get("wealth", {}).get("owner_entity", "")
                })
                if reminder_enabled:
                    reminder_dt = review_dt - timedelta(days=reminder_days)
                    events.append({
                        "date": reminder_dt,
                        "type": "Review Reminder",
                        "name": asset.get("name", ""),
                        "owner": asset.get("wealth", {}).get("owner_entity", "")
                    })
            except Exception:
                pass

    for liability in liabilities:
        payoff_date = compute_payoff_date(liability)
        if payoff_date:
            events.append({
                "date": payoff_date,
                "type": "Payoff",
                "name": liability.get("name", ""),
                "owner": liability.get("owner_entity", "")
            })
            if reminder_enabled:
                reminder_dt = payoff_date - timedelta(days=reminder_days)
                events.append({
                    "date": reminder_dt,
                    "type": "Payoff Reminder",
                    "name": liability.get("name", ""),
                    "owner": liability.get("owner_entity", "")
                })

    if not events:
        st.info("No upcoming events yet.")
    else:
        horizon_options = ["Next 30 days", "Next 90 days", "Next 6 months", "Next 12 months", "All"]
        horizon_choice = st.selectbox("Time Horizon", horizon_options, index=3)
        include_overdue = st.checkbox("Include overdue", value=True)

        horizon_days = None
        if horizon_choice == "Next 30 days":
            horizon_days = 30
        elif horizon_choice == "Next 90 days":
            horizon_days = 90
        elif horizon_choice == "Next 6 months":
            horizon_days = 180
        elif horizon_choice == "Next 12 months":
            horizon_days = 365

        filtered = []
        for event in events:
            days_until = (event["date"] - today).days
            if not include_overdue and days_until < 0:
                continue
            if horizon_days is not None and days_until > horizon_days:
                continue
            filtered.append({
                "Date": event["date"],
                "Days Until": days_until,
                "Type": event["type"],
                "Name": event["name"],
                "Owner": event["owner"] or "Unassigned"
            })

        if not filtered:
            st.info("No events in this range.")
        else:
            filtered.sort(key=lambda x: x["Date"])
            display_df = pd.DataFrame(filtered)
            display_df["Date"] = display_df["Date"].astype(str)
            st.dataframe(display_df, width="stretch", hide_index=True)

            if PLOTLY_AVAILABLE:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=[row["Date"] for row in filtered],
                    y=[row["Type"] for row in filtered],
                    mode="markers",
                    text=[f"{row['Type']}: {row['Name']} ({row['Owner']})" for row in filtered],
                    hoverinfo="text",
                    marker=dict(size=10, color="#d1a843")
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(color=plotly_text_color),
                    yaxis=dict(color=plotly_text_color),
                    height=280,
                    title="Upcoming Events Timeline"
                )
                st.plotly_chart(fig, width="stretch")

            st.markdown("#### Calendar View")
            grouped = {}
            for row in filtered:
                try:
                    dt = datetime.fromisoformat(str(row["Date"])).date()
                except Exception:
                    continue
                key = dt.strftime("%B %Y")
                grouped.setdefault(key, []).append(row)

            for month_key, items in grouped.items():
                st.markdown(f"**{month_key}**")
                for item in items:
                    date_text = item["Date"]
                    days_text = f"{item['Days Until']} days" if item["Days Until"] >= 0 else f"{abs(item['Days Until'])} days overdue"
                    st.write(f"{date_text} • {item['Type']} • {item['Name']} • {item['Owner']} • {days_text}")

            ics_events = [
                {
                    "date": row["Date"],
                    "type": row["Type"],
                    "name": row["Name"],
                    "owner": row["Owner"]
                }
                for row in filtered
            ]
            ics_content = build_ics_calendar(ics_events, "WealthPulse Upcoming Events")
            if ics_content:
                st.download_button(
                    "Download Calendar (ICS)",
                    ics_content,
                    file_name="wealthpulse_events.ics",
                    mime="text/calendar"
                )

            owners = sorted({row["Owner"] for row in filtered})
            for owner in owners:
                owner_events = [e for e in ics_events if (e.get("owner") or "Unassigned") == owner]
                owner_ics = build_ics_calendar(owner_events, f"WealthPulse {owner} Events")
                if owner_ics:
                    safe_owner = owner.replace(" ", "_").lower()
                    st.download_button(
                        f"Download {owner} Calendar (ICS)",
                        owner_ics,
                        file_name=f"wealthpulse_events_{safe_owner}.ics",
                        mime="text/calendar"
                    )

    st.markdown("---")
    st.markdown("### Estate & Beneficiary Export")
    estate_assets = []
    for asset in portfolio:
        wealth = asset.get("wealth", {})
        value, _, _ = ai_valuation(asset)
        ownership_split = wealth.get("ownership_split") if isinstance(wealth.get("ownership_split"), dict) else {}
        split_text = ", ".join([f"{k}:{v}%" for k, v in ownership_split.items()]) if ownership_split else ""
        estate_assets.append({
            "Asset": asset.get("name", ""),
            "Type": asset.get("type", ""),
            "Owner": wealth.get("owner_entity", ""),
            "Ownership Split": split_text,
            "Beneficiary": wealth.get("beneficiary", ""),
            "Custodian": wealth.get("custodian", ""),
            "Insured Value": float(wealth.get("insured_value", 0.0) or 0.0),
            "Estimated Value": value if value is not None else 0.0,
            "Review Date": wealth.get("review_date", ""),
            "Notes": asset.get("notes", "")
        })

    estate_liabilities = []
    for liability in liabilities:
        ownership_split = liability.get("ownership_split") if isinstance(liability.get("ownership_split"), dict) else {}
        split_text = ", ".join([f"{k}:{v}%" for k, v in ownership_split.items()]) if ownership_split else ""
        estate_liabilities.append({
            "Liability": liability.get("name", ""),
            "Type": liability.get("type", ""),
            "Owner": liability.get("owner_entity", ""),
            "Ownership Split": split_text,
            "Balance": float(liability.get("balance", 0.0) or 0.0),
            "Interest Rate": liability.get("interest_rate", 0.0),
            "Payment": float(liability.get("payment", 0.0) or 0.0),
            "Start Date": liability.get("start_date", ""),
            "Due Date": liability.get("due_date", ""),
            "Notes": liability.get("notes", "")
        })

    if estate_assets:
        estate_assets_df = pd.DataFrame(estate_assets)
        st.download_button(
            "Download Estate Assets (CSV)",
            estate_assets_df.to_csv(index=False),
            file_name="estate_assets.csv",
            mime="text/csv"
        )
        st.download_button(
            "Download Estate Assets (JSON)",
            json.dumps(estate_assets, indent=2),
            file_name="estate_assets.json",
            mime="application/json"
        )
    else:
        st.info("No assets available for export.")

    if estate_liabilities:
        estate_liabilities_df = pd.DataFrame(estate_liabilities)
        st.download_button(
            "Download Estate Liabilities (CSV)",
            estate_liabilities_df.to_csv(index=False),
            file_name="estate_liabilities.csv",
            mime="text/csv"
        )
        st.download_button(
            "Download Estate Liabilities (JSON)",
            json.dumps(estate_liabilities, indent=2),
            file_name="estate_liabilities.json",
            mime="application/json"
        )

    estate_records = []
    for row in estate_assets:
        estate_records.append({
            "Record Type": "Asset",
            **row
        })
    for row in estate_liabilities:
        estate_records.append({
            "Record Type": "Liability",
            **row
        })
    if estate_records:
        estate_combined_df = pd.DataFrame(estate_records)
        st.download_button(
            "Download Full Estate Report (CSV)",
            estate_combined_df.to_csv(index=False),
            file_name="estate_report.csv",
            mime="text/csv"
        )
        st.download_button(
            "Download Full Estate Report (JSON)",
            json.dumps(estate_records, indent=2),
            file_name="estate_report.json",
            mime="application/json"
        )

# ==============================
# TAB 8: SETTINGS
# ==============================
with tab8:
    st.subheader("Settings")
    st.markdown("Configure your display currency, live data, and preferences.")

    settings = user_settings
    default_code = get_default_currency_code()
    currency_options = build_currency_options(default_code)
    option_labels = [f"{code} — {name}" for code, name in currency_options]
    option_codes = [code for code, _ in currency_options]
    current_code = settings.get("currency_code") or currency_code or default_code
    try:
        current_index = option_codes.index(current_code)
    except ValueError:
        current_index = 0

    st.markdown("### Profile")
    st.write(f"Signed in as **{escape_html(user)}**")
    render_founding_badge(settings)

    st.markdown("### Subscription")
    current_plan = normalize_plan(settings.get("subscription_plan"))
    plan_options = SUBSCRIPTION_PLANS
    plan_index = plan_options.index(current_plan) if current_plan in plan_options else 0
    plan_choice = st.radio("Plan", plan_options, index=plan_index, horizontal=True)
    st.caption(PLAN_DESCRIPTIONS.get(plan_choice, ""))
    if plan_choice == "Founder":
        st.info("Founder plan includes all Elite features plus early access and founder perks.")
    subscription_status = st.selectbox(
        "Status",
        ["active", "trial", "expired"],
        index=["active", "trial", "expired"].index(settings.get("subscription_status", "active"))
        if settings.get("subscription_status", "active") in ["active", "trial", "expired"] else 0
    )
    subscription_renews = st.text_input(
        "Renewal date (optional)",
        value=settings.get("subscription_renews", "")
    )
    stripe_portal_url = st.text_input(
        "Stripe customer portal URL (optional)",
        value=settings.get("stripe_customer_portal_url", "")
    )
    if stripe_portal_url.strip():
        st.markdown(f"<a class='wp-stripe-link' href='{stripe_portal_url.strip()}' target='_blank'>Manage Subscription</a>", unsafe_allow_html=True)
    st.caption("This panel will sync with Stripe in production. For now, it controls feature access locally.")
    st.markdown("### API Keys & Live Data")
    st.caption("For production, store keys in `.streamlit/secrets.toml` so they never touch local data files.")
    with st.expander("Secrets file template (recommended for deployment)"):
        st.code(
            "SUPABASE_URL = \"\"\n"
            "SUPABASE_ANON_KEY = \"\"\n"
            "SUPABASE_SERVICE_KEY = \"\"\n"
            "SUPABASE_USE_SERVICE_ROLE = true\n"
            "SUPABASE_AUTH_REQUIRED = true\n"
            "APP_STORAGE_PROVIDER = \"Supabase\"\n"
            "METALPRICE_API_KEY = \"\"\n"
            "FREEGOLDPRICE_API_KEY = \"\"\n"
            "METALS_DEV_API_KEY = \"\"\n"
            "NEWS_API_KEY = \"\"\n"
            "EBAY_CLIENT_ID = \"\"\n"
            "EBAY_CLIENT_SECRET = \"\"\n"
            "REVERB_API_TOKEN = \"\"\n"
            "SMTP_HOST = \"\"\n"
            "SMTP_PORT = 587\n"
            "SMTP_USER = \"\"\n"
            "SMTP_PASSWORD = \"\"\n"
            "SMTP_USE_TLS = true\n",
            language="toml"
        )
    st.info("Free data sources can be delayed or indicative. For higher accuracy and faster updates, use a paid API plan.")
    country_code = get_country_code(user_settings)
    country_name = get_country_name(country_code)
    st.caption(f"Detected location: {country_name}. Currency defaults and guidance are localized when possible.")
    country_override_options = ["Auto"] + sorted(COUNTRY_NAMES.keys())
    current_override = (user_settings.get("country_override") or "").strip().upper()
    current_override_label = "Auto" if not current_override else current_override
    if current_override_label not in country_override_options:
        country_override_options.insert(1, current_override_label)
    selected_override = st.selectbox("Country Override", country_override_options, index=country_override_options.index(current_override_label))
    if selected_override == "Auto":
        selected_override = ""
    st.markdown(
        "Get API keys here: "
        "[SilverPrice.org](https://silverprice.org) • "
        "[FreeGoldPrice](https://freegoldprice.com) • "
        "[MetalpriceAPI](https://metalpriceapi.com) • "
        "[Metals.dev](https://metals.dev) • "
        "[Frankfurter](https://www.frankfurter.app) • "
        "[NewsAPI](https://newsapi.org) • "
        "[eBay Developers](https://developer.ebay.com) • "
        "[Reverb API](https://www.reverb.com/developers)"
    )
    freegoldprice_value, freegoldprice_secret = resolve_setting(settings, "freegoldprice_api_key", "FREEGOLDPRICE_API_KEY")
    metalprice_value, metalprice_secret = resolve_setting(settings, "metalprice_api_key", "METALPRICE_API_KEY")
    metals_dev_value, metals_dev_secret = resolve_setting(settings, "metals_dev_api_key", "METALS_DEV_API_KEY")
    news_api_value, news_api_secret = resolve_setting(settings, "news_api_key", "NEWS_API_KEY")

    freegoldprice_key = st.text_input(
        "FreeGoldPrice Key (free)",
        type="password",
        value="••••••••" if freegoldprice_secret else freegoldprice_value,
        disabled=freegoldprice_secret
    )
    metalprice_key = st.text_input(
        "MetalpriceAPI Key (paid)",
        type="password",
        value="••••••••" if metalprice_secret else metalprice_value,
        disabled=metalprice_secret
    )
    metals_dev_key = st.text_input(
        "Metals.dev Key (paid FX)",
        type="password",
        value="••••••••" if metals_dev_secret else metals_dev_value,
        disabled=metals_dev_secret
    )
    news_api_key = st.text_input(
        "NewsAPI Key (free dev)",
        type="password",
        value="••••••••" if news_api_secret else news_api_value,
        disabled=news_api_secret
    )

    st.markdown("### Community Backend (Supabase)")
    st.caption("Required for the multi-device Community Market. Keep keys private.")
    supabase_url_value, supabase_url_secret = resolve_setting(community_settings, "supabase_url", "SUPABASE_URL")
    supabase_anon_value, supabase_anon_secret = resolve_setting(community_settings, "supabase_anon_key", "SUPABASE_ANON_KEY")
    supabase_service_value, supabase_service_secret = resolve_setting(community_settings, "supabase_service_key", "SUPABASE_SERVICE_KEY")

    supabase_url_input = st.text_input(
        "Supabase Project URL",
        value="Using secrets" if supabase_url_secret else supabase_url_value,
        disabled=supabase_url_secret
    )
    supabase_anon_input = st.text_input(
        "Supabase Anon Key",
        type="password",
        value="••••••••" if supabase_anon_secret else supabase_anon_value,
        disabled=supabase_anon_secret
    )
    supabase_service_input = st.text_input(
        "Supabase Service Role Key (optional, admin-only)",
        type="password",
        value="••••••••" if supabase_service_secret else supabase_service_value,
        disabled=supabase_service_secret
    )
    supabase_use_service_role = st.checkbox(
        "Use service role key on server (recommended for private deployments)",
        value=bool(community_settings.get("supabase_use_service_role", False))
    )

    st.markdown("### Storage & Security")
    storage_provider_current = app_storage_provider(settings)
    storage_provider_secret = bool(get_secret_value("APP_STORAGE_PROVIDER")) or secret_flag("SUPABASE_APP_STORAGE", False)
    storage_provider_options = ["Local", "Supabase"]
    storage_provider_index = 1 if storage_provider_current.lower().startswith("supabase") else 0
    storage_provider = st.selectbox(
        "Core app storage",
        storage_provider_options,
        index=storage_provider_index,
        disabled=storage_provider_secret
    )
    if storage_provider_secret:
        st.caption("Storage provider is controlled by secrets.")
    auth_required_secret = secret_flag("SUPABASE_AUTH_REQUIRED", False)
    access_options = ["Open (no sign-in required)", "Secure (require sign-in)"]
    access_index = 1 if bool(settings.get("supabase_auth_required", False)) else 0
    access_choice = st.radio(
        "Community Access (app behavior)",
        access_options,
        index=access_index,
        horizontal=True,
        disabled=auth_required_secret
    )
    supabase_auth_required_setting = access_choice.startswith("Secure")
    if auth_required_secret:
        st.caption("Community access requirement is controlled by secrets.")
    if supabase_auth_required_setting:
        st.caption("App will require Community sign-in. Ensure RLS policies require auth.")
    else:
        st.warning("Community is set to open access in the app. This exposes data to any app user.")

    policy_options = [
        "Unknown (not set)",
        "Open (anon + authenticated)",
        "Auth required (RLS)",
        "Service role only"
    ]
    policy_value = settings.get("community_policy_mode", "unknown")
    policy_index = {
        "open": 1,
        "auth": 2,
        "service": 3
    }.get(policy_value, 0)
    policy_choice = st.selectbox(
        "Supabase Policy Mode (manual reminder)",
        policy_options,
        index=policy_index,
        help="This is a reminder only. Update Supabase RLS policies using supabase_community_schema.sql to match."
    )
    policy_choice_map = {
        "Open (anon + authenticated)": "open",
        "Auth required (RLS)": "auth",
        "Service role only": "service",
        "Unknown (not set)": "unknown"
    }
    community_policy_mode_setting = policy_choice_map.get(policy_choice, "unknown")
    if supabase_auth_required_setting and community_policy_mode_setting == "open":
        st.info("App requires sign-in, but policy mode says Open. Update Supabase policies or change the app setting.")
    if (not supabase_auth_required_setting) and community_policy_mode_setting == "auth":
        st.info("App is open access, but policy mode says Auth required. Open policies or change the app setting.")
    if community_policy_mode_setting == "open":
        st.caption("To enable open access, uncomment the 'Open community access' block in supabase_community_schema.sql and run it in Supabase SQL editor.")
    if storage_provider == "Supabase":
        st.caption(f"Uses Supabase table `{APP_STORAGE_TABLE}` for user data.")
        if not supabase_enabled(community_settings):
            st.warning("Supabase keys not configured. App storage cannot switch to Supabase yet.")
        if supabase_use_service_role and not get_effective_setting(community_settings, "supabase_service_key", "SUPABASE_SERVICE_KEY"):
            st.warning("Service role key missing. Add it in secrets for secure server-side access.")
        test_cols = st.columns(2)
        with test_cols[0]:
            if st.button("Test App Storage", key="test_app_storage"):
                ok, err = supabase_check_table(community_settings, APP_STORAGE_TABLE, use_service_key=True)
                if ok:
                    st.success("Supabase app storage is reachable.")
                else:
                    st.error(f"App storage check failed: {err}")
        with test_cols[1]:
            if st.button("Sync Local Data to Supabase", key="sync_app_storage"):
                sync_err = sync_db_to_supabase(community_settings, db)
                if sync_err:
                    st.error(f"Sync failed: {sync_err}")
                else:
                    st.success("Local data synced to Supabase.")
        with st.expander("Deployment Security Checklist"):
            st.markdown(
                "- Store all keys in `.streamlit/secrets.toml` (API keys + Supabase keys).\n"
                "- Enable HTTPS (reverse proxy / Streamlit Cloud) before public launch.\n"
                "- Run the updated `supabase_community_schema.sql` to enable RLS policies.\n"
                "- Optional: uncomment the strict `service_role` policies block in the SQL to lock down community tables.\n"
                "- Set `SUPABASE_AUTH_REQUIRED = true` to enforce per-user Community access.\n"
                "- Set `APP_STORAGE_PROVIDER = \"Supabase\"` to move user data off local JSON."
            )

    auto_refresh_enabled_input = st.checkbox("Enable auto-refresh", value=settings.get("auto_refresh_enabled", True))
    refresh_interval_input = st.number_input(
        "Refresh interval (seconds)",
        min_value=30,
        value=int(settings.get("auto_refresh_interval", 70)),
        step=10
    )
    if auto_refresh_enabled_input and not AUTOREFRESH_AVAILABLE:
        st.warning("Auto-refresh requires the streamlit-autorefresh package.")

    freegoldprice_effective = get_effective_setting(settings, "freegoldprice_api_key", "FREEGOLDPRICE_API_KEY")
    metalprice_effective = get_effective_setting(settings, "metalprice_api_key", "METALPRICE_API_KEY")
    metals_dev_effective = get_effective_setting(settings, "metals_dev_api_key", "METALS_DEV_API_KEY")
    news_api_effective = get_effective_setting(settings, "news_api_key", "NEWS_API_KEY")

    metals_source_options = [
        "SilverPrice.org (free)",
        "FreeGoldPrice (free)",
        "MetalpriceAPI (paid)",
        "Manual"
    ]
    current_metals_provider = settings.get("metals_provider", "SilverPrice")
    if current_metals_provider == "SilverPrice":
        metals_index = 0
    elif current_metals_provider == "FreeGoldPrice":
        metals_index = 1
    elif current_metals_provider == "MetalpriceAPI":
        metals_index = 2
    else:
        metals_index = 3
    metals_source = st.selectbox(
        "Metals Price Source",
        metals_source_options,
        index=metals_index
    )
    if metals_source == "SilverPrice.org (free)":
        st.info("SilverPrice.org provides live spot prices for gold and silver (no key required).")
    if metals_source == "FreeGoldPrice (free)" and not freegoldprice_effective:
        st.warning("FreeGoldPrice key required for live metals pricing.")
    if metals_source == "MetalpriceAPI (paid)" and not metalprice_effective:
        st.warning("MetalpriceAPI key required for live metals pricing.")
    use_live_metal_price_input = metals_source != "Manual"

    fx_source = st.selectbox(
        "FX Source",
        ["Frankfurter (free daily)", "Metals.dev (paid)", "Manual"],
        index=0 if settings.get("fx_provider", "Frankfurter") == "Frankfurter" else 1 if settings.get("fx_provider") == "Metals.dev" else 2
    )
    if fx_source == "Metals.dev (paid)" and not metals_dev_effective:
        st.warning("Metals.dev key required for live FX rates.")
    auto_fx_enabled_input = fx_source != "Manual"
    metal_history_days_input = st.number_input(
        "Metals chart history (days)",
        min_value=7,
        max_value=365,
        value=int(settings.get("metal_history_days", 30)),
        step=1
    )

    st.markdown("### Currency")
    selected_label = st.selectbox("Currency", option_labels, index=current_index)
    selected_code = selected_label.split(" — ")[0]

    default_symbol = CURRENCY_SYMBOLS.get(selected_code, selected_code + " ")
    current_symbol = settings.get("currency_symbol") if settings.get("currency_code") == selected_code else default_symbol
    symbol_input = st.text_input("Currency Symbol", value=current_symbol)

    rate_disabled = selected_code == "USD" or auto_fx_enabled_input
    rate_value = settings.get("currency_rate", 1.0) if settings.get("currency_code") == selected_code else 1.0
    if rate_disabled:
        rate_value = 1.0 if selected_code == "USD" else st.session_state.currency_rate
    rate_input = st.number_input(
        f"1 USD = {selected_code}",
        min_value=0.0001,
        value=float(rate_value),
        step=0.0001,
        format="%.4f",
        disabled=rate_disabled
    )

    st.markdown("### Display & Units")
    preview_enabled = st.checkbox(
        "Live preview theme & font",
        value=st.session_state.get("ui_live_preview", False)
    )
    st.session_state.ui_live_preview = preview_enabled
    preview_theme_value = st.session_state.get("ui_theme_preview", settings.get("ui_theme", "Dark Gold"))
    preview_font_value = float(st.session_state.get("ui_font_scale_preview", settings.get("ui_font_scale", 0.95)))

    theme_default = preview_theme_value if preview_enabled else settings.get("ui_theme", "Dark Gold")
    font_default = preview_font_value if preview_enabled else float(settings.get("ui_font_scale", 0.95))

    theme_choice = st.selectbox(
        "Theme",
        ["Dark Gold", "Light Classic"],
        index=0 if theme_default == "Dark Gold" else 1
    )
    font_scale_input = st.slider(
        "Font size",
        min_value=0.85,
        max_value=1.1,
        value=float(font_default),
        step=0.01
    )
    if preview_enabled:
        if (
            theme_choice != st.session_state.get("ui_theme_preview")
            or abs(float(font_scale_input) - float(st.session_state.get("ui_font_scale_preview", font_scale_input))) > 1e-6
        ):
            st.session_state.ui_theme_preview = theme_choice
            st.session_state.ui_font_scale_preview = float(font_scale_input)
            st.rerun()
    else:
        if st.button("Reset Preview to Saved", width="stretch"):
            st.session_state.ui_theme_preview = settings.get("ui_theme", "Dark Gold")
            st.session_state.ui_font_scale_preview = float(settings.get("ui_font_scale", 0.95))
            st.rerun()
    weight_unit_label = st.selectbox(
        "Metal weight unit",
        list(WEIGHT_UNITS.keys()),
        index=list(WEIGHT_UNITS.values()).index(settings.get("metal_weight_unit", "toz"))
        if settings.get("metal_weight_unit", "toz") in WEIGHT_UNITS.values() else 0
    )
    date_format_label = st.selectbox("Date format", list(DATE_FORMATS.keys()),
                                     index=list(DATE_FORMATS.keys()).index(settings.get("date_format", "MMM D, YYYY"))
                                     if settings.get("date_format", "MMM D, YYYY") in DATE_FORMATS else 0)
    timezone_label = st.selectbox("Timezone", TIMEZONE_OPTIONS,
                                  index=TIMEZONE_OPTIONS.index(settings.get("timezone", "Local"))
                                  if settings.get("timezone", "Local") in TIMEZONE_OPTIONS else 0)
    privacy_mode_input = st.checkbox("Privacy mode (hide values)", value=settings.get("privacy_mode", False))

    st.markdown("### Defaults")
    default_type_options = ASSET_TYPE_OPTIONS
    default_type = st.selectbox(
        "Default Asset Type",
        default_type_options,
        index=default_type_options.index(settings.get("default_asset_type", "Other"))
        if settings.get("default_asset_type", "Other") in default_type_options else len(default_type_options) - 1
    )
    default_condition = st.selectbox("Default Condition",
                                     ["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"],
                                     index=["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"].index(settings.get("default_condition", "Excellent"))
                                     if settings.get("default_condition", "Excellent") in ["Mint", "Excellent", "Very Good", "Good", "Fair", "Poor"] else 1)
    default_view_mode = st.selectbox("Default View Mode", ["Grid", "List"],
                                     index=0 if settings.get("default_view_mode", "Grid") == "Grid" else 1)

    st.markdown("### Dashboard Layout")
    panel_selection = st.multiselect("Show Panels", DASHBOARD_PANELS, default=settings.get("dashboard_panels", []))

    st.markdown("### Notifications")
    notifications_enabled = st.checkbox("Enable price move alerts (tickers)", value=settings.get("notifications_enabled", False))
    notification_threshold = st.number_input(
        "Alert threshold (%)",
        min_value=0.1,
        value=float(settings.get("notification_threshold_pct", 5.0)),
        step=0.1
    )

    st.markdown("### Community Alerts")
    market_alerts_enabled = st.checkbox(
        "Enable saved search alerts",
        value=settings.get("market_alerts_enabled", True)
    )
    market_alerts_interval = st.number_input(
        "Alert refresh interval (seconds)",
        min_value=60,
        value=int(settings.get("market_alerts_interval", 180)),
        step=30
    )
    market_alerts_email_enabled = st.checkbox(
        "Enable email alerts (optional)",
        value=settings.get("market_alerts_email_enabled", False)
    )
    market_alerts_push_enabled = st.checkbox(
        "Enable browser notifications (this device)",
        value=settings.get("market_alerts_push_enabled", False),
        help="Requires browser permission. Works on localhost or HTTPS."
    )
    market_alert_email = st.text_input(
        "Alert email address",
        value=settings.get("market_alert_email", ""),
        help="Used only for saved search alert emails."
    )
    with st.expander("SMTP Settings (optional for email alerts)"):
        smtp_host_value, smtp_host_secret = resolve_setting(settings, "smtp_host", "SMTP_HOST")
        smtp_port_value, smtp_port_secret = resolve_setting(settings, "smtp_port", "SMTP_PORT")
        smtp_user_value, smtp_user_secret = resolve_setting(settings, "smtp_user", "SMTP_USER")
        smtp_pass_value, smtp_pass_secret = resolve_setting(settings, "smtp_password", "SMTP_PASSWORD")
        smtp_tls_value, smtp_tls_secret = resolve_setting(settings, "smtp_use_tls", "SMTP_USE_TLS")

        smtp_host = st.text_input(
            "SMTP Host",
            value="Using secrets" if smtp_host_secret else smtp_host_value,
            disabled=smtp_host_secret
        )
        try:
            smtp_port_default = int(smtp_port_value or settings.get("smtp_port", 587))
        except Exception:
            smtp_port_default = 587
        smtp_port = st.number_input(
            "SMTP Port",
            min_value=1,
            max_value=65535,
            value=int(smtp_port_default),
            step=1,
            disabled=smtp_port_secret
        )
        smtp_user = st.text_input(
            "SMTP Username",
            value="Using secrets" if smtp_user_secret else smtp_user_value,
            disabled=smtp_user_secret
        )
        smtp_password = st.text_input(
            "SMTP Password",
            type="password",
            value="••••••••" if smtp_pass_secret else smtp_pass_value,
            disabled=smtp_pass_secret
        )
        tls_default = settings.get("smtp_use_tls", True)
        if smtp_tls_value not in (None, ""):
            tls_default = str(smtp_tls_value).strip().lower() not in {"0", "false", "no"}
        smtp_use_tls = st.checkbox("Use TLS", value=bool(tls_default), disabled=smtp_tls_secret)
        st.caption("Use an app password and ensure SMTP is enabled for your email provider.")

    st.markdown("### Calendar & Reminders")
    reminder_enabled = st.checkbox("Enable reminder events", value=settings.get("event_include_reminders", True))
    reminder_days = st.number_input(
        "Reminder lead time (days)",
        min_value=1,
        max_value=365,
        value=int(settings.get("event_reminder_days", 30)),
        step=1
    )

    plan_target_input = to_display_currency(settings.get("wealth_target_net_worth", 0.0), currency_rate)
    plan_date_store = settings.get("wealth_target_date", "")
    plan_risk_profile = settings.get("wealth_risk_profile", "Balanced")
    plan_horizon = int(settings.get("wealth_horizon_years", 10))
    plan_rebalance_tolerance = float(settings.get("wealth_rebalance_tolerance", 5.0))
    alloc_inputs = {k: float(v) for k, v in (settings.get("wealth_target_allocations", {}) or {}).items()}
    plan_notes = settings.get("wealth_advisor_notes", "")

    st.markdown("### Wealth Plan")
    if not has_plan_at_least(settings, "Pro"):
        render_plan_gate(settings, "Pro", "Wealth Plan", "Upgrade to set targets, allocations, and advisor notes.", key="gate_wealth_plan")
    else:
        country_code = get_country_code()
        country_name = get_country_name(country_code)
        st.caption(f"Set targets and allocations to guide long‑term, generational wealth planning in {country_name}.")
        plan_target_display = plan_target_input
        plan_target_input = st.number_input(
            f"Target Net Worth ({currency_code})",
            min_value=0.0,
            value=float(plan_target_display),
            step=1000.0
        )
        plan_date_raw = plan_date_store
        plan_date_enabled = st.checkbox("Set target date", value=bool(plan_date_raw))
        if plan_date_enabled:
            try:
                plan_date_value = datetime.fromisoformat(plan_date_raw).date() if plan_date_raw else datetime.now().date()
            except Exception:
                plan_date_value = datetime.now().date()
            plan_date_picked = st.date_input("Target Date", value=plan_date_value)
            plan_date_store = plan_date_picked.isoformat()
        else:
            plan_date_store = ""

        plan_risk_profile = st.selectbox(
            "Risk Profile",
            WEALTH_RISK_PROFILES,
            index=WEALTH_RISK_PROFILES.index(settings.get("wealth_risk_profile", "Balanced"))
            if settings.get("wealth_risk_profile", "Balanced") in WEALTH_RISK_PROFILES else 1
        )
        plan_horizon = st.number_input(
            "Investment Horizon (years)",
            min_value=1,
            max_value=60,
            value=int(settings.get("wealth_horizon_years", 10)),
            step=1
        )
        plan_rebalance_tolerance = st.number_input(
            "Rebalance tolerance (%)",
            min_value=1.0,
            max_value=50.0,
            value=float(settings.get("wealth_rebalance_tolerance", 5.0)),
            step=0.5
        )

        st.markdown("#### Target Allocation (%)")
        asset_type_options = ASSET_TYPE_OPTIONS
        alloc_inputs = {}
        saved_allocations = settings.get("wealth_target_allocations", {}) or {}
        for asset_type in asset_type_options:
            alloc_inputs[asset_type] = st.number_input(
                f"{asset_type}",
                min_value=0.0,
                max_value=100.0,
                value=float(saved_allocations.get(asset_type, 0.0)),
                step=1.0,
                key=f"alloc_{asset_type}"
            )
        total_alloc = sum(alloc_inputs.values())
        if total_alloc > 0 and abs(total_alloc - 100.0) > 0.5:
            st.warning(f"Allocations total {total_alloc:.1f}% (aim for 100%).")

        plan_notes = st.text_area("Advisor Notes", value=settings.get("wealth_advisor_notes", ""))
    st.markdown("### Backup & Import")
    export_json = json.dumps(user_record, indent=2)
    st.download_button("Export JSON", data=export_json, file_name=f"{user}_portfolio.json", mime="application/json")
    if portfolio:
        export_csv = pd.json_normalize(portfolio).to_csv(index=False)
        st.download_button("Export CSV", data=export_csv, file_name=f"{user}_portfolio.csv", mime="text/csv")
    else:
        st.info("No assets to export yet.")

    import_file = st.file_uploader("Import JSON", type=["json"])
    import_mode = st.selectbox("Import Mode", ["Merge (append)", "Replace"])
    import_settings = st.checkbox("Import settings too", value=False)
    if import_file and st.button("Run Import"):
        try:
            raw = json.load(import_file)
            imported_portfolio = None
            imported_settings = None
            if isinstance(raw, dict):
                imported_portfolio = raw.get("portfolio")
                imported_settings = raw.get("settings")
            elif isinstance(raw, list):
                imported_portfolio = raw

            if not isinstance(imported_portfolio, list):
                st.error("Invalid import file: portfolio not found.")
            else:
                if import_mode == "Replace":
                    user_record["portfolio"] = imported_portfolio
                else:
                    user_record["portfolio"].extend(imported_portfolio)
                if import_settings and isinstance(imported_settings, dict):
                    user_record["settings"] = imported_settings
                save_data(db)
                st.success("Import completed.")
                st.rerun()
        except Exception as exc:
            st.error(f"Import failed: {exc}")

    st.markdown("### News")
    news_provider = st.selectbox("News Provider", ["None", "NewsAPI (free dev key)"],
                                 index=1 if settings.get("news_provider") == "NewsAPI" else 0)
    if news_provider == "NewsAPI (free dev key)" and not news_api_effective:
        st.warning("NewsAPI key required to show stock news.")
    rss_backup_enabled = st.checkbox("Enable RSS backup", value=settings.get("rss_backup_enabled", True))
    st.caption("Tip: use {query} in the RSS URL to insert your tickers/search terms.")
    rss_feed_url = st.text_input("RSS Feed URL (backup)", value=settings.get("rss_feed_url", ""))

    st.markdown("### Marketplace Comparisons")
    st.caption("Use marketplace APIs to pull price comparisons. Scraping is avoided to respect site terms.")
    ebay_id_value, ebay_id_secret = resolve_setting(settings, "ebay_client_id", "EBAY_CLIENT_ID")
    ebay_secret_value, ebay_secret_secret = resolve_setting(settings, "ebay_client_secret", "EBAY_CLIENT_SECRET")
    reverb_value, reverb_secret = resolve_setting(settings, "reverb_api_token", "REVERB_API_TOKEN")

    ebay_client_id = st.text_input(
        "eBay Client ID",
        type="password",
        value="••••••••" if ebay_id_secret else ebay_id_value,
        disabled=ebay_id_secret
    )
    ebay_client_secret = st.text_input(
        "eBay Client Secret",
        type="password",
        value="••••••••" if ebay_secret_secret else ebay_secret_value,
        disabled=ebay_secret_secret
    )
    reverb_token = st.text_input(
        "Reverb API Token",
        type="password",
        value="••••••••" if reverb_secret else reverb_value,
        disabled=reverb_secret
    )

    st.markdown("### Feedback & Bugs")
    st.caption("Prefer email? Contact us at wealthpulse@outlook.co.nz.")
    with st.expander("Send Feedback or Report a Bug", expanded=st.session_state.get("open_feedback_form", False)):
        with st.form("feedback_form"):
            feedback_type = st.selectbox("Type", ["Feedback", "Bug", "Feature Request", "Other"])
            feedback_subject = st.text_input("Subject", placeholder="Short summary")
            feedback_message = st.text_area("Details", placeholder="Tell us what happened or what you'd like to see...")
            submit_feedback = st.form_submit_button("Submit", width="stretch")

        if submit_feedback:
            if not feedback_subject or not feedback_message:
                st.error("Please provide a subject and details.")
            else:
                meta = get_meta(db)
                entry = {
                    "id": secrets.token_hex(6),
                    "user": user,
                    "category": feedback_type,
                    "subject": feedback_subject.strip(),
                    "message": feedback_message.strip(),
                    "status": "Open",
                    "created_at": datetime.now().isoformat(),
                    "admin_response": ""
                }
                meta["feedback"].insert(0, entry)
                save_data(db)
                st.session_state.open_feedback_form = False
                st.success("Thanks! Your feedback has been submitted.")

    st.markdown("### Admin Access")
    if st.session_state.get("is_admin"):
        st.success("Admin mode is enabled for this session.")
        if st.button("Open Admin Console", width="stretch"):
            st.session_state.jump_to_admin = True
            st.rerun()
        if st.button("Disable Admin Mode", width="stretch"):
            st.session_state.is_admin = False
            st.success("Admin mode disabled.")
            st.rerun()
    else:
        with st.form("admin_access_settings_form"):
            admin_token_settings = st.text_input("Admin Password", type="password")
            admin_submit_settings = st.form_submit_button("Enable Admin Mode", width="stretch")

        if admin_submit_settings:
            if not secrets.compare_digest(admin_token_settings or "", ADMIN_DEFAULT_TOKEN):
                st.error("Invalid admin password.")
            else:
                st.session_state.is_admin = True
                st.session_state.jump_to_admin = True
                st.success("Admin mode enabled.")
                st.rerun()

    freegoldprice_key_to_save = freegoldprice_key.strip() if not freegoldprice_secret else ""
    metalprice_key_to_save = metalprice_key.strip() if not metalprice_secret else ""
    metals_dev_key_to_save = metals_dev_key.strip() if not metals_dev_secret else ""
    news_api_key_to_save = news_api_key.strip() if not news_api_secret else ""
    ebay_client_id_to_save = ebay_client_id.strip() if not ebay_id_secret else ""
    ebay_client_secret_to_save = ebay_client_secret.strip() if not ebay_secret_secret else ""
    reverb_token_to_save = reverb_token.strip() if not reverb_secret else ""

    smtp_host_to_save = smtp_host.strip() if not smtp_host_secret else ""
    smtp_user_to_save = smtp_user.strip() if not smtp_user_secret else ""
    smtp_password_to_save = smtp_password if not smtp_pass_secret else ""
    smtp_port_to_save = int(smtp_port) if not smtp_port_secret else int(settings.get("smtp_port", 587))
    smtp_use_tls_to_save = bool(smtp_use_tls) if not smtp_tls_secret else bool(settings.get("smtp_use_tls", True))

    supabase_url_to_save = supabase_url_input.strip() if not supabase_url_secret else ""
    supabase_anon_to_save = supabase_anon_input.strip() if not supabase_anon_secret else ""
    supabase_service_to_save = supabase_service_input.strip() if not supabase_service_secret else ""
    storage_provider_to_save = storage_provider if not storage_provider_secret else settings.get("storage_provider", "Local")
    supabase_auth_required_to_save = bool(supabase_auth_required_setting) if not auth_required_secret else settings.get("supabase_auth_required", False)
    community_policy_mode_to_save = community_policy_mode_setting or settings.get("community_policy_mode", "unknown")

    if st.button("Save Settings", width="stretch"):
        record = ensure_user_record(db, user)
        record["settings"] = {
            "currency_code": selected_code,
            "currency_symbol": symbol_input if symbol_input else default_symbol,
            "currency_rate": 1.0 if selected_code == "USD" else float(rate_input),
            "auto_fx_enabled": auto_fx_enabled_input,
            "auto_refresh_enabled": auto_refresh_enabled_input,
            "auto_refresh_interval": int(refresh_interval_input),
            "metal_weight_unit": WEIGHT_UNITS.get(weight_unit_label, "toz"),
            "date_format": date_format_label,
            "timezone": timezone_label,
            "default_asset_type": default_type,
            "default_condition": default_condition,
            "default_view_mode": default_view_mode,
            "privacy_mode": privacy_mode_input,
            "dashboard_panels": panel_selection,
            "notifications_enabled": notifications_enabled,
            "notification_threshold_pct": float(notification_threshold),
            "metal_history_days": int(metal_history_days_input),
            "use_live_metal_price": use_live_metal_price_input,
            "metals_provider": "SilverPrice" if metals_source.startswith("SilverPrice") else "MetalpriceAPI" if metals_source.startswith("MetalpriceAPI") else "FreeGoldPrice" if metals_source.startswith("FreeGoldPrice") else "Manual",
            "fx_provider": "Metals.dev" if fx_source.startswith("Metals.dev") else "Frankfurter" if fx_source.startswith("Frankfurter") else "Manual",
            "metalprice_api_key": metalprice_key_to_save,
            "freegoldprice_api_key": freegoldprice_key_to_save,
            "metals_dev_api_key": metals_dev_key_to_save,
            "news_api_key": news_api_key_to_save,
            "news_provider": "NewsAPI" if news_provider.startswith("NewsAPI") else "None",
            "rss_backup_enabled": rss_backup_enabled,
            "rss_feed_url": rss_feed_url.strip(),
            "ebay_client_id": ebay_client_id_to_save,
            "ebay_client_secret": ebay_client_secret_to_save,
            "reverb_api_token": reverb_token_to_save,
            "wealth_target_net_worth": from_display_currency(plan_target_input, currency_rate),
            "wealth_target_date": plan_date_store,
            "wealth_risk_profile": plan_risk_profile,
            "wealth_horizon_years": int(plan_horizon),
            "wealth_rebalance_tolerance": float(plan_rebalance_tolerance),
            "wealth_target_allocations": {k: float(v) for k, v in alloc_inputs.items()},
            "wealth_advisor_notes": plan_notes.strip(),
            "onboarding_completed": settings.get("onboarding_completed", False),
            "event_include_reminders": bool(reminder_enabled),
            "event_reminder_days": int(reminder_days),
            "ui_theme": theme_choice,
            "ui_font_scale": float(font_scale_input),
            "market_watchlist": sorted([str(item) for item in st.session_state.get("market_watchlist", set())]),
            "market_saved_searches": st.session_state.get("market_saved_searches", []),
            "market_alerts_enabled": bool(market_alerts_enabled),
            "market_alerts_interval": int(market_alerts_interval),
            "market_alerts_email_enabled": bool(market_alerts_email_enabled),
            "market_alerts_push_enabled": bool(market_alerts_push_enabled),
            "market_alert_email": market_alert_email.strip(),
            "smtp_host": smtp_host_to_save,
            "smtp_port": int(smtp_port_to_save),
            "smtp_user": smtp_user_to_save,
            "smtp_password": smtp_password_to_save,
            "smtp_use_tls": bool(smtp_use_tls_to_save),
            "country_override": selected_override,
            "supabase_url": supabase_url_to_save,
            "supabase_anon_key": supabase_anon_to_save,
            "supabase_service_key": supabase_service_to_save,
            "supabase_use_service_role": bool(supabase_use_service_role),
            "supabase_auth_required": bool(supabase_auth_required_to_save),
            "storage_provider": storage_provider_to_save,
            "community_policy_mode": community_policy_mode_to_save,
            "subscription_plan": normalize_plan(plan_choice),
            "subscription_status": subscription_status,
            "subscription_renews": subscription_renews.strip(),
            "subscription_source": settings.get("subscription_source", "Local"),
            "stripe_customer_portal_url": stripe_portal_url.strip()
        }
        meta = get_meta(db)
        meta["community_config"] = {
            "supabase_url": supabase_url_to_save,
            "supabase_anon_key": supabase_anon_to_save,
            "supabase_service_key": supabase_service_to_save,
            "supabase_use_service_role": bool(supabase_use_service_role),
            "supabase_auth_required": bool(supabase_auth_required_to_save),
            "storage_provider": storage_provider_to_save,
            "community_policy_mode": community_policy_mode_to_save
        }
        save_data(db)
        st.success("Settings saved. Updating display...")
        request_scroll_to_top()
        st.rerun()

# ==============================
# TAB 9: HELP
# ==============================
if tab_help is not None:
    with tab_help:
        st.subheader("Help & Quick Guide")
        st.caption("Questions or feedback? Email wealthpulse@outlook.co.nz.")

        st.markdown("### Start Here")
        st.markdown(
            """
            <div class="help-grid">
                <div class="help-card">
                    <div class="help-card-title">1. Settings</div>
                    <div class="help-card-body">Set currency, theme, font size, and data sources before you add assets.</div>
                </div>
                <div class="help-card">
                    <div class="help-card-title">2. Add Assets</div>
                    <div class="help-card-body">Add items, choose a type, and fill the details that matter to you.</div>
                </div>
                <div class="help-card">
                    <div class="help-card-title">3. Entities</div>
                    <div class="help-card-body">Separate Personal, Trust, and Business assets for a true net worth view.</div>
                </div>
                <div class="help-card">
                    <div class="help-card-title">4. Review</div>
                    <div class="help-card-body">Use Portfolio, Analytics, and Stats to monitor your progress.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### Quick Checklist")
        st.markdown(
            "1. Confirm currency and theme in `Settings`.\n"
            "2. Add your first asset in `Add Asset`.\n"
            "3. Create an entity in `Entities & Liabilities`.\n"
            "4. Check `Portfolio` and `Analytics` for your totals.\n"
            "5. Optional: Post a listing in `Community`."
        )

        st.markdown("### Navigation Tips")
        st.markdown(
            "- The top buttons jump directly to `Settings`, `Feedback / Bugs`, `Help`, and `Log Out`.\n"
            "- Tabs organize the app by workflow. Use `Settings` to customize what panels appear."
        )

        st.markdown("### Tab Guide")
        with st.expander("Portfolio"):
            st.markdown(
                "- View total net worth, panels, and quick summaries.\n"
                "- Filter by entity using `Portfolio View`.\n"
                "- Select an item to see detailed information.\n"
                "- Use privacy mode to hide values when sharing."
            )
        with st.expander("Bullion"):
            st.markdown(
                "- See live metals pricing and bullion summaries.\n"
                "- Bullion holdings are grouped by metal type.\n"
                "- News section pulls gold/silver/copper headlines when enabled."
            )
        with st.expander("Community"):
            st.markdown(
                "- Browse listings with filters, sort, and watchlist.\n"
                "- Create listings with photos (max 5) and required country.\n"
                "- Auctions support bids, reserve, and buy-now (if enabled).\n"
                "- Private messages connect buyers and sellers.\n"
                "- Community rules block explicit or abusive content."
            )
        with st.expander("Analytics"):
            st.markdown(
                "- Review portfolio breakdowns, trends, and charts.\n"
                "- Uses your selected currency and FX settings."
            )
        with st.expander("Buy/Sell"):
            st.markdown(
                "- Auto recommendations for assets with tickers.\n"
                "- Uses price history to highlight buy/hold/sell ranges."
            )
        with st.expander("Stats"):
            st.markdown(
                "- Summary statistics for assets, types, and valuations.\n"
                "- Helpful for quick health checks."
            )
        with st.expander("Add Asset"):
            st.markdown(
                "- Search and select asset names with suggestions.\n"
                "- Fill in type details and wealth management fields.\n"
                "- Upload photos and add notes.\n"
                "- Add to portfolio and return to the main view."
            )
        with st.expander("Edit Items"):
            st.markdown(
                "- Select an asset to edit name, type, pricing, or details.\n"
                "- Update images or notes.\n"
                "- Delete assets with confirmation or use bulk delete."
            )
        with st.expander("Entities & Liabilities"):
            st.markdown(
                "- Create entities (Personal, Trust, Company, etc.).\n"
                "- Assign ownership and split percentages.\n"
                "- Track liabilities and view entity statements."
            )
        with st.expander("Settings"):
            st.markdown(
                "- Choose currency, theme, font size, and auto-refresh.\n"
                "- Configure metals, FX, and news sources.\n"
                "- Manage Community access mode and Supabase settings.\n"
                "- Export or import your data."
            )
        if st.session_state.get("is_admin"):
            with st.expander("Admin"):
                st.markdown(
                    "- View local usage stats and revenue tracking.\n"
                    "- Respond to user feedback and reset passwords.\n"
                    "- Moderate community content when enabled."
                )

        st.markdown("### Common Issues")
        st.markdown(
            "1. Prices not updating: check `Settings` → API keys and live data source.\n"
            "2. Community blocked: confirm Supabase keys and Community access mode.\n"
            "3. Light theme readability: adjust font size or switch theme in `Settings`."
        )

        st.markdown("### API Key Links")
        st.markdown(
            "[SilverPrice.org](https://silverprice.org) • "
            "[FreeGoldPrice](https://freegoldprice.com) • "
            "[MetalpriceAPI](https://metalpriceapi.com) • "
            "[Metals.dev](https://metals.dev) • "
            "[Frankfurter](https://www.frankfurter.app) • "
            "[NewsAPI](https://newsapi.org) • "
            "[eBay Developers](https://developer.ebay.com) • "
            "[Reverb API](https://www.reverb.com/developers)"
        )

        st.markdown("### Support")
        st.markdown(
            "- Feedback or bug reports: wealthpulse@outlook.co.nz\n"
            "- Use the Feedback form in Settings for direct submission."
        )

        guide_lines = [
            "1. Settings: set currency, theme, and data sources.",
            "2. Add Asset: enter details and save.",
            "3. Entities: separate Personal, Trust, and Business ownership.",
            "4. Portfolio/Analytics: monitor totals and trends.",
            "5. Community: browse or post listings with photos.",
            "Support: wealthpulse@outlook.co.nz"
        ]
        guide_text = "WealthPulse Quick Guide\n------------------------\n" + "\n".join(guide_lines) + "\n"
        pdf_data = build_simple_pdf(guide_lines)
        st.download_button(
            "Download Quick Guide (TXT)",
            data=guide_text,
            file_name="wealthpulse_quick_guide.txt",
            mime="text/plain",
            width="content"
        )
        st.download_button(
            "Download Quick Guide (PDF)",
            data=pdf_data,
            file_name="wealthpulse_quick_guide.pdf",
            mime="application/pdf",
            width="content"
        )

# ==============================
# TAB 9: BULLION
# ==============================
if bullion_tab is not None:
    with bullion_tab:
        st.subheader("Bullion")
        st.markdown(
            "Physical gold and silver can help balance a portfolio by offering diversification, "
            "inflation protection, and a tangible store of value. Many long‑term investors hold "
            "bullion as a stabilizer alongside growth assets."
        )

        st.markdown("### Live Metals Pricing (SilverPrice.org)")
        widget_currency = (currency_code or "USD").upper()
        widget_supported = widget_currency in BULLION_WIDGET_CURRENCIES
        if not widget_supported:
            widget_currency = "USD"
        if live_metals_data and live_metals_data.get("prices") and metals_provider_active == "SilverPrice":
            live_cols = st.columns(2)
            gold_spot = live_metals_data["prices"].get("XAU")
            silver_spot = live_metals_data["prices"].get("XAG")
            if gold_spot is not None:
                live_cols[0].metric("Gold Spot", format_currency(gold_spot, currency_symbol, currency_rate))
            if silver_spot is not None:
                live_cols[1].metric("Silver Spot", format_currency(silver_spot, currency_symbol, currency_rate))
            if metals_last_updated:
                if isinstance(metals_last_updated, (int, float)):
                    metals_time = datetime.fromtimestamp(metals_last_updated)
                else:
                    try:
                        metals_time = datetime.fromisoformat(str(metals_last_updated))
                    except Exception:
                        metals_time = get_now_for_settings(user_settings)
                st.caption(f"Updated {format_date_for_settings(metals_time, user_settings)}")
            st.caption("SilverPrice.org provides live spot prices for gold and silver only.")

            if not widget_supported:
                st.caption(f"SilverPrice widgets do not support {currency_code}; showing USD instead.")
            components.html(
                f"""
                <div style="display:flex; flex-wrap:wrap; gap:1rem;">
                    <div id="silver-price" data-silver_price="{widget_currency}-o-1d"></div>
                    <div id="gold-price" data-gold_price="{widget_currency}-o-1d"></div>
                </div>
                <script src="https://charts.goldprice.org/silver-price.js"></script>
                <script src="https://charts.goldprice.org/gold-price.js"></script>
                """,
                height=340
            )
        else:
            st.info("Enable SilverPrice.org in Settings to show live gold and silver spot pricing here.")

        entity_view = st.session_state.get("portfolio_entity_view", "All")
        if entity_view != "All":
            st.caption(f"Viewing: {entity_view}")

        bullion_items = []
        bullion_by_metal = {}
        total_bullion_value = 0.0
        total_bullion_weight = 0.0
        for item in build_portfolio_view_items(portfolio, entity_view):
            asset = item["asset"]
            share = item["share"]
            if asset.get("type") not in BULLION_TYPES:
                continue
            bullion_items.append(item)
            metal = asset.get("type")
            bucket = bullion_by_metal.setdefault(metal, {"value": 0.0, "weight": 0.0, "count": 0})
            val, _, _ = ai_valuation(asset)
            bucket["value"] += val * share
            bucket["count"] += 1
            total_bullion_value += val * share
            weight = asset.get("details", {}).get("weight_troy_oz")
            if weight:
                try:
                    bucket["weight"] += float(weight) * share
                    total_bullion_weight += float(weight) * share
                except Exception:
                    pass

        if bullion_items:
            st.markdown("### Bullion Snapshot")
            snap_cols = st.columns(3)
            snap_cols[0].metric("Total Bullion Value", format_currency(total_bullion_value, currency_symbol, currency_rate))
            if total_bullion_weight > 0:
                snap_cols[1].metric("Total Weight", format_detail_value("weight_troy_oz", total_bullion_weight, currency_symbol, currency_rate, weight_unit))
            else:
                snap_cols[1].metric("Total Weight", "Add weight to bullion items")
            snap_cols[2].metric("Items", len(bullion_items))

            st.markdown("### By Metal")
            metal_cols = st.columns(3)
            for idx, (metal, data) in enumerate(sorted(bullion_by_metal.items())):
                label = f"{metal} Value"
                value_display = format_currency(data["value"], currency_symbol, currency_rate)
                metal_cols[idx % 3].metric(label, value_display)

            st.markdown("### Bullion Holdings")
            rows = []
            for item in bullion_items:
                asset = item["asset"]
                share = item["share"]
                val, _, _ = ai_valuation(asset)
                rows.append({
                    "Name": asset.get("name", "Asset"),
                    "Metal": asset.get("type", ""),
                    "Condition": asset.get("condition", ""),
                    "Qty": asset.get("qty", 1),
                    "Weight": format_detail_value("weight_troy_oz", asset.get("details", {}).get("weight_troy_oz"), currency_symbol, currency_rate, weight_unit),
                    "Value": format_currency(val * share, currency_symbol, currency_rate)
                })
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        else:
            st.info("No bullion assets yet. Add Gold, Silver, Copper, Platinum, or Palladium items to see them here.")

        st.markdown("### Bullion News")
        query = "gold OR silver OR copper bullion"
        articles = None
        news_err = None
        if user_settings.get("news_provider") == "NewsAPI" and get_effective_setting(user_settings, "news_api_key", "NEWS_API_KEY"):
            news_cache_key = f"bullion_news_{query}"
            news_cached = get_cache(news_cache_key, 1800)
            if news_cached:
                articles = news_cached
            else:
                articles, news_err = fetch_newsapi(query, get_effective_setting(user_settings, "news_api_key", "NEWS_API_KEY"))
                if articles:
                    set_cache(news_cache_key, articles)

        if not articles and user_settings.get("rss_backup_enabled") and user_settings.get("rss_feed_url"):
            rss_url = user_settings.get("rss_feed_url")
            if "{query}" in rss_url:
                rss_url = rss_url.replace("{query}", quote_plus(query))
            rss_cache_key = f"rss_{rss_url}"
            rss_cached = get_cache(rss_cache_key, 1800)
            if rss_cached:
                articles = rss_cached
            else:
                articles, news_err = fetch_rss_items(rss_url, limit=6)
                if articles:
                    set_cache(rss_cache_key, articles)

        if articles:
            for article in articles[:6]:
                title = article.get("title", "Article")
                url = article.get("url") or article.get("link", "")
                source = article.get("source", "News")
                published = article.get("publishedAt") or article.get("published") or ""
                if url:
                    st.markdown(f"- [{title}]({url}) — {source} ({published})")
                else:
                    st.write(f"- {title} — {source} ({published})")
        else:
            st.info(f"Bullion news unavailable: {news_err or 'Enable NewsAPI or RSS in Settings'}")

# ==============================
# TAB 10: COMMUNITY MARKET
# ==============================
if forum_tab is not None:
    with forum_tab:
        is_elite = has_plan_at_least(user_settings, "Elite")
        render_founding_badge(user_settings)
        supabase_connected = supabase_enabled(community_settings)
        auth_required = supabase_auth_required(community_settings)
        auth_user = get_supabase_auth_user(community_settings) if auth_required else None
        auth_email = get_supabase_auth_email(community_settings) if auth_required else ""
        auth_user_id = get_supabase_auth_user_id(community_settings) if auth_required else None
        if auth_required:
            st.markdown("### Community Account")
            url_check, anon_check, _ = get_supabase_config(community_settings)
            if not anon_check:
                st.warning("Supabase anon key is required for Community Auth.")
            if not supabase_connected:
                st.warning("Supabase is not configured. Community sign-in is unavailable.")
            elif auth_user:
                st.success(f"Signed in to Community as {auth_email}")
                if st.button("Sign out of Community", key="community_signout"):
                    clear_supabase_auth_state()
                    st.rerun()
            else:
                with st.form("community_signin"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    submit_signin = st.form_submit_button("Sign In")
                with st.expander("Create Community Account"):
                    with st.form("community_signup"):
                        new_email = st.text_input("Email", key="community_signup_email")
                        new_password = st.text_input("Password", type="password", key="community_signup_password")
                        confirm_password = st.text_input("Confirm Password", type="password", key="community_signup_confirm")
                        submit_signup = st.form_submit_button("Create Account")
                if submit_signin:
                    if not email or not password:
                        st.error("Enter email and password.")
                    else:
                        auth_data, err = supabase_auth_sign_in(community_settings, email, password)
                        if err:
                            st.error(f"Sign in failed: {err}")
                        else:
                            access_token = auth_data.get("access_token")
                            refresh_token = auth_data.get("refresh_token")
                            expires_in = auth_data.get("expires_in") or 3600
                            user_obj = auth_data.get("user") or {}
                            set_supabase_auth_state({
                                "access_token": access_token,
                                "refresh_token": refresh_token,
                                "expires_at": time.time() + int(expires_in),
                                "user": user_obj
                            })
                            community_sync_user(community_settings, db, user)
                            st.success("Community sign-in successful.")
                            st.rerun()
                if submit_signup:
                    pw_error = validate_password_strength(new_password)
                    if pw_error:
                        st.error(pw_error)
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        signup_data, err = supabase_auth_sign_up(community_settings, new_email, new_password)
                        if err:
                            st.error(f"Sign up failed: {err}")
                        else:
                            auth_data, err = supabase_auth_sign_in(community_settings, new_email, new_password)
                            if err:
                                st.warning("Account created. Please sign in.")
                            else:
                                access_token = auth_data.get("access_token")
                                refresh_token = auth_data.get("refresh_token")
                                expires_in = auth_data.get("expires_in") or 3600
                                user_obj = auth_data.get("user") or {}
                                set_supabase_auth_state({
                                    "access_token": access_token,
                                    "refresh_token": refresh_token,
                                    "expires_at": time.time() + int(expires_in),
                                    "user": user_obj
                                })
                                community_sync_user(community_settings, db, user)
                                st.success("Community account created and signed in.")
                                st.rerun()
                st.info("Sign in to access the Community Market.")

        community_ready = True
        schema_ok = None
        schema_err = None
        if supabase_connected:
            schema_ok, schema_err = supabase_check_table(
                community_settings,
                "community_posts",
                use_service_key=community_use_service_role(community_settings),
                auth_token=community_auth_token(community_settings)
            )
            if not schema_ok:
                community_ready = False
        if auth_required and not auth_user:
            community_ready = False

        forum_posts = []
        posts_err = None
        if community_ready:
            forum_posts, posts_err = community_get_posts(community_settings, db)
            if posts_err:
                st.error(f"Community backend error: {posts_err}")
                forum_posts = []
            if auth_required and auth_user_id:
                legacy_posts = [post for post in forum_posts if post.get("created_by") == user and not post.get("owner_id")]
                if legacy_posts:
                    st.warning("Some of your older listings predate Supabase Auth. Ask an admin to backfill owner_id or recreate those listings to enable edits.")

        if community_ready:
            role = community_get_role(community_settings, db, user)
            is_mod = role in ("admin", "moderator")
            is_banned = community_is_banned(community_settings, db, user)
        else:
            role = None
            is_mod = False
            is_banned = False

        column_support = st.session_state.get("community_column_support")
        if supabase_enabled(community_settings) and community_ready and column_support is None:
            column_results = supabase_check_columns(
                community_settings,
                "community_posts",
                list(COMMUNITY_POSTS_EXTRA_COLUMNS.keys()),
                use_service_key=community_use_service_role(community_settings),
                auth_token=community_auth_token(community_settings)
            )
            column_support = {col: ok for col, ok, _ in column_results}
            st.session_state.community_column_support = column_support
        if column_support is None:
            column_support = {}
        supports_reserve = column_support.get("reserve_amount", True) or not supabase_enabled(community_settings)
        supports_buy_now = column_support.get("buy_now_price", True) or not supabase_enabled(community_settings)
        supports_images = column_support.get("images", True) or not supabase_enabled(community_settings)
        supports_owner_id = column_support.get("owner_id", True) or not supabase_enabled(community_settings)
        supports_grading_company = column_support.get("grading_company", True) or not supabase_enabled(community_settings)
        supports_grading_grade = column_support.get("grading_grade", True) or not supabase_enabled(community_settings)
        supports_grading = supports_grading_company and supports_grading_grade
        if supabase_auth_required(community_settings) and not supports_owner_id:
            st.warning("Supabase schema is missing the owner_id column. Run the migration helper before using Community Auth.")

        if "edit_listing_id" not in st.session_state:
            st.session_state.edit_listing_id = None
        if "edit_listing_origin" not in st.session_state:
            st.session_state.edit_listing_origin = "browse"
        if "market_selected_post_id" not in st.session_state:
            st.session_state.market_selected_post_id = None
        if "market_view_post_id" not in st.session_state:
            st.session_state.market_view_post_id = None
        if "market_watchlist" not in st.session_state:
            stored_watchlist = user_settings.get("market_watchlist") or []
            st.session_state.market_watchlist = set(stored_watchlist)
        if "market_saved_searches" not in st.session_state:
            st.session_state.market_saved_searches = user_settings.get("market_saved_searches") or []

        if is_banned:
            st.warning("Your account is suspended from posting, bidding, or messaging in the community.")
        else:
            st.info("Community Rules apply to listings, comments, and messages. Violations are blocked.")

        forum_tabs = ["Browse", "Watchlist", "Create Listing", "My Listings", "Messages"]
        if is_mod:
            forum_tabs.append("Moderation")
        forum_tabs = st.tabs(forum_tabs)

        def normalize_forum_datetime(dt_value):
            if not isinstance(dt_value, datetime):
                return dt_value
            if dt_value.tzinfo is not None:
                try:
                    dt_value = dt_value.astimezone().replace(tzinfo=None)
                except Exception:
                    dt_value = dt_value.replace(tzinfo=None)
            return dt_value

        def parse_forum_date(value):
            if not value:
                return datetime.min
            try:
                parsed = datetime.fromisoformat(value)
            except Exception:
                return datetime.min
            return normalize_forum_datetime(parsed)

        def forum_now():
            now_dt = get_now_for_settings(user_settings)
            return normalize_forum_datetime(now_dt)

        def is_recent_listing(post, days=7):
            created_at = post.get("created_at")
            created_dt = parse_forum_date(created_at)
            if created_dt == datetime.min:
                return False
            return (forum_now() - created_dt).days <= days

        def get_auction_fields(post):
            if post.get("auction"):
                auction = post.get("auction", {})
                return (
                    auction.get("starting_bid", 0.0),
                    auction.get("min_increment", 0.0),
                    auction.get("end_date")
                )
            return (
                post.get("auction_starting_bid", 0.0),
                post.get("auction_min_increment", 0.0),
                post.get("auction_end_date")
            )

        def get_reserve_amount(post):
            if post.get("auction"):
                return post.get("auction", {}).get("reserve_amount")
            return post.get("reserve_amount")

        def get_buy_now_price(post):
            if post.get("auction"):
                return post.get("auction", {}).get("buy_now_price")
            return post.get("buy_now_price")

        def get_post_images(post):
            images = post.get("images") or []
            display = []
            for img in images:
                if isinstance(img, dict) and img.get("data"):
                    mime = img.get("mime") or "image/png"
                    display.append(f"data:{mime};base64,{img.get('data')}")
                elif isinstance(img, str):
                    display.append(img)
            return display[:5]

        def get_listing_card_image(post):
            images = get_post_images(post)
            if images:
                return images[0]
            title = post.get("title") or post.get("category") or "listing"
            return search_asset_image(str(title))

        def get_listing_price_value(post):
            listing_type = post.get("listing_type", "Discussion")
            if listing_type == "For Sale":
                return post.get("price")
            if listing_type == "Auction":
                starting_bid, _, _ = get_auction_fields(post)
                return starting_bid or post.get("price")
            return None

        def get_auction_end_dt(post):
            _, _, end_date = get_auction_fields(post)
            if not end_date:
                return None
            raw = str(end_date)
            try:
                end_dt = datetime.fromisoformat(raw)
            except Exception:
                try:
                    end_dt = datetime.strptime(raw, "%Y-%m-%d")
                except Exception:
                    return None
            if "T" not in raw:
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            return normalize_forum_datetime(end_dt)

        def clamp_price_range(saved_range, min_price, max_price):
            if not saved_range or len(saved_range) != 2:
                return (min_price, max_price)
            try:
                low = float(saved_range[0])
                high = float(saved_range[1])
            except Exception:
                return (min_price, max_price)
            low = max(min_price, min(max_price, low))
            high = max(min_price, min(max_price, high))
            if low > high:
                return (min_price, max_price)
            return (low, high)

        def format_time_left(end_date_value, settings):
            if not end_date_value:
                return None
            raw = str(end_date_value)
            end_dt = None
            try:
                end_dt = datetime.fromisoformat(raw)
            except Exception:
                try:
                    end_dt = datetime.strptime(raw, "%Y-%m-%d")
                except Exception:
                    end_dt = None
            if not end_dt:
                return None
            if "T" not in raw:
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            end_dt = normalize_forum_datetime(end_dt)
            now_dt = normalize_forum_datetime(get_now_for_settings(settings))
            if end_dt <= now_dt:
                return "Ended"
            delta = end_dt - now_dt
            days = delta.days
            hours = int(delta.seconds // 3600)
            minutes = int((delta.seconds % 3600) // 60)
            if days > 0:
                return f"Ends in {days}d {hours}h"
            if hours > 0:
                return f"Ends in {hours}h {minutes}m"
            return f"Ends in {minutes}m"

        def get_post_status(post):
            status = post.get("status", "Active")
            listing_type = post.get("listing_type")
            if listing_type == "Auction":
                _, _, end_date = get_auction_fields(post)
                if end_date:
                    try:
                        if datetime.fromisoformat(end_date).date() < datetime.now().date() and status == "Active":
                            return "Ended"
                    except Exception:
                        pass
            return status

        def open_streamlit_dialog(title):
            dialog_fn = getattr(st, "dialog", None)
            if callable(dialog_fn):
                try:
                    dialog_ctx = dialog_fn(title)
                    if hasattr(dialog_ctx, "__enter__"):
                        return dialog_ctx, True
                except Exception:
                    pass
            return st.container(), False

        def render_listing_edit_form(post, key_prefix):
            post_id = post.get("id")
            listing_type_value = post.get("listing_type") or "For Sale"
            listing_type_options = ["For Sale", "Auction", "Discussion"]
            try:
                listing_type_index = listing_type_options.index(listing_type_value)
            except ValueError:
                listing_type_index = 0
            category_filter = st.text_input(
                "Filter categories (optional)",
                placeholder="Type to filter categories (e.g., bullion, cards, coins)",
                key=f"{key_prefix}_category_filter_{post_id}"
            )
            category_list = list(COMMUNITY_CATEGORY_OPTIONS)
            category_list += [asset.get("type", "Other") for asset in portfolio]
            category_value = post.get("category", "Other")
            if category_value not in category_list:
                category_list.append(category_value)
            category_list = filter_category_options(category_list, category_filter)
            if category_value not in category_list:
                category_list.insert(0, category_value)
            try:
                category_index = category_list.index(category_value)
            except ValueError:
                category_index = 0

            starting_bid_default, min_increment_default, end_date_default = get_auction_fields(post)
            reserve_default = get_reserve_amount(post) if supports_reserve else None
            buy_now_default = get_buy_now_price(post) if supports_buy_now else None
            end_date_value = None
            if end_date_default:
                try:
                    end_date_value = datetime.fromisoformat(str(end_date_default)).date()
                except Exception:
                    try:
                        end_date_value = datetime.strptime(str(end_date_default), "%Y-%m-%d").date()
                    except Exception:
                        end_date_value = None
            if end_date_value is None:
                end_date_value = datetime.now().date() + timedelta(days=7)

            with st.form(f"{key_prefix}_edit_listing_form_{post_id}"):
                edit_listing_type = st.selectbox(
                    "Listing Type",
                    listing_type_options,
                    index=listing_type_index,
                    key=f"{key_prefix}_edit_listing_type_{post_id}"
                )
                edit_category = st.selectbox(
                    "Category",
                    category_list,
                    index=category_index,
                    key=f"{key_prefix}_edit_listing_category_{post_id}"
                )
                edit_title = st.text_input(
                    "Title",
                    value=post.get("title", ""),
                    key=f"{key_prefix}_edit_listing_title_{post_id}"
                )
                edit_description = st.text_area(
                    "Description",
                    value=post.get("body", ""),
                    height=120,
                    key=f"{key_prefix}_edit_listing_body_{post_id}"
                )
                grading_type = grading_type_for_category(edit_category)
                edit_grading_company = None
                edit_grading_grade = None
                if grading_type:
                    st.markdown("#### Grading (optional)")
                    if supports_grading:
                        if grading_type == "coin":
                            company_options = COIN_GRADING_COMPANIES
                            grade_options = COIN_GRADE_OPTIONS
                        else:
                            company_options = CARD_GRADING_COMPANIES
                            grade_options = CARD_GRADE_OPTIONS
                        existing_company = post.get("grading_company") or "Ungraded / None"
                        existing_grade = post.get("grading_grade") or "Ungraded"
                        if existing_company not in (["Ungraded / None"] + company_options):
                            company_options = [existing_company] + company_options
                        if existing_grade not in grade_options:
                            grade_options = [existing_grade] + grade_options
                        edit_grading_company = st.selectbox(
                            "Grading Company",
                            ["Ungraded / None"] + company_options,
                            index=(["Ungraded / None"] + company_options).index(existing_company),
                            key=f"{key_prefix}_edit_listing_grade_company_{post_id}"
                        )
                        edit_grading_grade = st.selectbox(
                            "Grade",
                            grade_options,
                            index=grade_options.index(existing_grade),
                            key=f"{key_prefix}_edit_listing_grade_{post_id}"
                        )
                        if edit_grading_company == "Ungraded / None":
                            edit_grading_company = None
                        if edit_grading_grade == "Ungraded":
                            edit_grading_grade = None
                    else:
                        st.caption("Grading fields require a schema update. Run the migration helper below.")
                existing_images = post.get("images") or []
                display_images = get_post_images(post)
                if display_images:
                    preview_cols = st.columns(min(len(display_images), 5))
                    for idx, img in enumerate(display_images):
                        with preview_cols[idx]:
                            st.image(img, width=140)
                replace_images = []
                remove_images = False
                if supports_images:
                    replace_images = st.file_uploader(
                        f"Replace Photos (max {MAX_LISTING_IMAGES})",
                        type=["jpg", "jpeg", "png"],
                        accept_multiple_files=True,
                        key=f"{key_prefix}_edit_listing_images_{post_id}"
                    )
                    if replace_images:
                        image_error = validate_listing_images(replace_images)
                        if image_error:
                            st.warning(image_error)
                            replace_images = replace_images[:MAX_LISTING_IMAGES]
                    remove_images = st.checkbox(
                        "Remove existing photos",
                        value=False,
                        key=f"{key_prefix}_edit_listing_remove_images_{post_id}"
                    )
                else:
                    st.caption("Photo uploads require a schema update. Run the migration helper below.")
                edit_location = st.text_input(
                    "Country (required)",
                    value=post.get("location", ""),
                    help="Enter the country where the item is located. Add city/region after the country if needed.",
                    key=f"{key_prefix}_edit_listing_location_{post_id}"
                )
                edit_price = None
                edit_starting_bid = None
                edit_min_increment = None
                edit_reserve = None
                edit_buy_now = None
                edit_end_date = None
                listing_currency = post.get("currency", currency_code)
                if edit_listing_type == "For Sale":
                    edit_price = st.number_input(
                        f"Price ({listing_currency})",
                        min_value=0.0,
                        value=float(post.get("price") or 0.0),
                        step=1.0,
                        key=f"{key_prefix}_edit_listing_price_{post_id}"
                    )
                elif edit_listing_type == "Auction":
                    edit_starting_bid = st.number_input(
                        f"Starting Bid ({listing_currency})",
                        min_value=0.0,
                        value=float(starting_bid_default or 0.0),
                        step=1.0,
                        key=f"{key_prefix}_edit_listing_starting_{post_id}"
                    )
                    edit_min_increment = st.number_input(
                        f"Minimum Increment ({listing_currency})",
                        min_value=0.0,
                        value=float(min_increment_default or 0.0),
                        step=1.0,
                        key=f"{key_prefix}_edit_listing_increment_{post_id}"
                    )
                    if supports_reserve:
                        edit_reserve = st.number_input(
                            f"Reserve Amount ({listing_currency})",
                            min_value=0.0,
                            value=float(reserve_default or 0.0),
                            step=1.0,
                            key=f"{key_prefix}_edit_listing_reserve_{post_id}"
                        )
                    else:
                        st.caption("Reserve amounts require a schema update. Run the migration helper.")
                    if supports_buy_now:
                        edit_buy_now = st.number_input(
                            f"Buy Now Price ({listing_currency})",
                            min_value=0.0,
                            value=float(buy_now_default or 0.0),
                            step=1.0,
                            key=f"{key_prefix}_edit_listing_buy_now_{post_id}"
                        )
                    else:
                        st.caption("Buy Now requires a schema update. Run the migration helper.")
                    edit_end_date = st.date_input(
                        "Auction End Date",
                        value=end_date_value,
                        key=f"{key_prefix}_edit_listing_end_date_{post_id}"
                    )
                submit_edit = st.form_submit_button("Save Changes")

            if submit_edit:
                if not edit_title.strip():
                    st.error("Title is required.")
                elif not edit_location.strip():
                    st.error("Country is required.")
                elif not edit_description.strip():
                    st.error("Description is required.")
                elif validate_community_text(f"{edit_title} {edit_description} {edit_location}"):
                    st.error("Your listing contains content that violates the Community Rules.")
                elif replace_images and validate_listing_images(replace_images):
                    st.error(validate_listing_images(replace_images))
                elif edit_listing_type == "Auction" and supports_reserve and edit_reserve and edit_starting_bid is not None and edit_reserve < edit_starting_bid:
                    st.error("Reserve amount should be equal to or higher than the starting bid.")
                elif edit_listing_type == "Auction" and supports_buy_now and edit_buy_now and edit_reserve and edit_buy_now < edit_reserve:
                    st.error("Buy Now price should be equal to or higher than the reserve.")
                else:
                    update_images = None
                    if supports_images and remove_images:
                        update_images = []
                    elif supports_images and replace_images:
                        update_images = encode_uploaded_images(replace_images)
                    update_payload = {
                        "title": edit_title.strip(),
                        "body": edit_description.strip(),
                        "category": edit_category,
                        "listing_type": edit_listing_type,
                        "location": edit_location.strip(),
                        "currency": listing_currency,
                        "price": float(edit_price) if edit_listing_type == "For Sale" else None,
                        "auction_starting_bid": float(edit_starting_bid) if edit_listing_type == "Auction" else None,
                        "auction_min_increment": float(edit_min_increment) if edit_listing_type == "Auction" else None,
                        "reserve_amount": float(edit_reserve) if edit_listing_type == "Auction" and supports_reserve and edit_reserve and edit_reserve > 0 else None,
                        "buy_now_price": float(edit_buy_now) if edit_listing_type == "Auction" and supports_buy_now and edit_buy_now and edit_buy_now > 0 else None,
                        "auction_end_date": edit_end_date.isoformat() if edit_listing_type == "Auction" and edit_end_date else None
                    }
                    if supports_grading:
                        if grading_type:
                            update_payload["grading_company"] = edit_grading_company
                            update_payload["grading_grade"] = edit_grading_grade
                        else:
                            update_payload["grading_company"] = None
                            update_payload["grading_grade"] = None
                    if update_images is not None:
                        update_payload["images"] = update_images
                    if not supports_reserve:
                        update_payload.pop("reserve_amount", None)
                    if not supports_buy_now:
                        update_payload.pop("buy_now_price", None)
                    _, err = community_update_post(community_settings, db, post.get("id"), update_payload)
                    if err:
                        st.error(err)
                    else:
                        st.success("Listing updated.")
                        st.session_state.edit_listing_id = None
                        request_scroll_to_top()
                        st.rerun()

        def render_marketplace_card(post, status, key_prefix="card"):
            post_id = post.get("id", "")
            listing_type = post.get("listing_type", "Discussion")
            currency = post.get("currency", currency_code)
            title = escape_html(post.get("title", "Listing"))
            category = escape_html(post.get("category", "Other"))
            country = escape_html(post.get("location", ""))
            seller = escape_html(post.get("created_by", "Seller"))
            image_src = escape_html(get_listing_card_image(post))
            is_new = is_recent_listing(post, days=7)
            photo_count = len(get_post_images(post))

            price_label = ""
            price_value = post.get("price")
            if listing_type == "For Sale" and price_value:
                price_label = f"{currency} {float(price_value):,.2f}"
            elif listing_type == "Auction":
                starting_bid, _, _ = get_auction_fields(post)
                if starting_bid:
                    price_label = f"Starting {currency} {float(starting_bid):,.2f}"

            time_left_label = ""
            if listing_type == "Auction":
                _, _, end_date = get_auction_fields(post)
                time_left_label = format_time_left(end_date, user_settings) or ""

            badges = [
                f'<span class="market-pill gold">{escape_html(listing_type)}</span>',
                f'<span class="market-pill">{escape_html(status)}</span>'
            ]
            if time_left_label:
                badges.append(f'<span class="market-pill warning">{escape_html(time_left_label)}</span>')
            if is_new:
                badges.append('<span class="market-pill success">NEW</span>')
            if photo_count:
                badges.append(f'<span class="market-pill">Photos {photo_count}</span>')
            if post.get("buy_now_price"):
                badges.append('<span class="market-pill gold">Buy Now</span>')
            badges_html = "".join(badges)

            price_tag_html = f'<div class="market-price-tag">{price_label}</div>' if price_label else ''
            card_html = (
                '<div class="market-card">'
                f'<div class="market-image"><img src="{image_src}" alt="Listing image" />{price_tag_html}</div>'
                f'<div class="market-body"><div class="market-badges">{badges_html}</div>'
                f'<div class="market-title">{title}</div>'
                f'<div class="market-meta">{country} · {category} · @{seller}</div>'
                '</div></div>'
            )
        render_html_block(card_html)
        actions = st.columns([1, 1])
        with actions[0]:
            if st.button("View", key=f"{key_prefix}_view_listing_{post_id}"):
                st.session_state.market_selected_post_id = post_id
                st.session_state.market_view_post_id = post_id
                st.session_state.jump_to_community = True
                request_scroll_to_top()
                st.rerun()
        with actions[1]:
            if user == post.get("created_by"):
                if is_elite:
                    if st.button("Edit", key=f"{key_prefix}_edit_listing_card_{post_id}"):
                        st.session_state.edit_listing_id = post_id
                        st.session_state.edit_listing_origin = "browse"
                        st.session_state.jump_to_community = True
                        request_scroll_to_top()
                        st.rerun()
                else:
                    st.caption("Elite required to edit listings.")
            else:
                watchlist = st.session_state.market_watchlist
                is_watching = post_id in watchlist
                label = "Watching" if is_watching else "Watch"
                if st.button(label, key=f"{key_prefix}_watch_listing_{post_id}"):
                    if is_watching:
                        watchlist.discard(post_id)
                    else:
                        watchlist.add(post_id)
                    st.session_state.market_watchlist = watchlist
                    persist_market_watchlist(db, user, watchlist)
                    st.rerun()

        def render_listing_detail_panel(post, status):
            post_id = post.get("id", "")
            price = post.get("price")
            currency = post.get("currency", currency_code)
            listing_type = post.get("listing_type", "Discussion")
            title = post.get("title", "Listing")

            header_cols = st.columns([3, 1])
            with header_cols[0]:
                st.markdown(f"### {title}")
                st.caption(f"Posted by {post.get('created_by', 'Unknown')} • {post.get('created_at', '')}")
            with header_cols[1]:
                watchlist = st.session_state.market_watchlist
                is_watching = post_id in watchlist
                label = "Watching" if is_watching else "Watch"
                if st.button(label, key=f"watch_listing_detail_{post_id}"):
                    if is_watching:
                        watchlist.discard(post_id)
                    else:
                        watchlist.add(post_id)
                    st.session_state.market_watchlist = watchlist
                    persist_market_watchlist(db, user, watchlist)
                    st.rerun()

            detail_cols = st.columns([1.3, 1])
            with detail_cols[0]:
                post_images = get_post_images(post)
                if post_images:
                    image_cols = st.columns(min(len(post_images), 3))
                    for idx, img in enumerate(post_images[:3]):
                        with image_cols[idx]:
                            st.image(img, width=220)
                st.write(post.get("body", ""))
                if post.get("category"):
                    st.write(f"Category: {post.get('category')}")
                if post.get("grading_company") or post.get("grading_grade"):
                    company = post.get("grading_company") or ""
                    grade = post.get("grading_grade") or ""
                    label = f"{company} {grade}".strip()
                    st.write(f"Grade: {label}")
                if post.get("location"):
                    st.write(f"Country: {post.get('location')}")
                if status == "Sold" and post.get("sold_price") is not None:
                    st.markdown(f"**Sold for:** {currency} {float(post.get('sold_price')):,.2f}")

            with detail_cols[1]:
                summary_card = st.container()
                with summary_card:
                    st.markdown("#### Listing Summary")
                    if listing_type == "For Sale":
                        st.metric("Asking Price", f"{currency} {float(price or 0.0):,.2f}")
                    elif listing_type == "Auction":
                        starting_bid, min_increment, end_date = get_auction_fields(post)
                        st.metric("Starting Bid", f"{currency} {float(starting_bid or 0.0):,.2f}")
                        if end_date:
                            st.caption(f"Auction ends: {end_date}")
                    if post.get("buy_now_price"):
                        st.metric("Buy Now", f"{currency} {float(post.get('buy_now_price')):,.2f}")
                    if post.get("reserve_amount"):
                        st.metric("Reserve", f"{currency} {float(post.get('reserve_amount')):,.2f}")
                    if user == post.get("created_by"):
                        if st.button("Edit Listing", key=f"edit_listing_detail_{post_id}"):
                            st.session_state.edit_listing_id = post_id
                            st.session_state.edit_listing_origin = "browse"
                            request_scroll_to_top()
                            st.rerun()

            if listing_type == "Auction":
                starting_bid, min_increment, end_date = get_auction_fields(post)
                reserve_amount = get_reserve_amount(post) if supports_reserve else None
                buy_now_price = get_buy_now_price(post) if supports_buy_now else None
                bids, bid_err = community_get_bids(community_settings, db, post_id)
                if bid_err:
                    st.error(bid_err)
                    bids = []
                current_bid = max([b.get("amount", 0.0) for b in bids], default=starting_bid or 0.0)
                st.markdown(f"**Current Bid:** {currency} {current_bid:,.2f}")
                st.caption(f"Minimum Increment: {currency} {float(min_increment or 0.0):,.2f}")
                if reserve_amount:
                    st.caption(f"Reserve: {currency} {float(reserve_amount):,.2f}")
                    if current_bid >= float(reserve_amount):
                        st.success("Reserve met")
                    else:
                        st.warning("Reserve not met yet")
                if buy_now_price:
                    st.caption(f"Buy Now: {currency} {float(buy_now_price):,.2f}")
                if end_date:
                    st.write(f"Auction ends: {end_date}")

                if bids:
                    recent = sorted(bids, key=lambda b: parse_forum_date(b.get("created_at", "")), reverse=True)[:5]
                    st.markdown("**Recent Bids**")
                    for bid in recent:
                        st.write(f"{bid.get('user','User')}: {currency} {float(bid.get('amount', 0.0)):,.2f}")

                if status == "Active":
                    if is_banned:
                        st.info("You cannot bid while suspended.")
                    else:
                        with st.form(f"bid_form_{post_id}"):
                            bid_amount = st.number_input(
                                f"Place Bid ({currency})",
                                min_value=0.0,
                                value=float(current_bid + max(min_increment or 0.0, 1.0)),
                                step=1.0
                            )
                            submit_bid = st.form_submit_button("Submit Bid")
                        if submit_bid:
                            if bid_amount < current_bid + (min_increment or 0.0):
                                st.error(f"Bid must be at least {currency} {current_bid + (min_increment or 0.0):,.2f}.")
                            else:
                                bid_payload = {
                                    "post_id": post_id,
                                    "amount": float(bid_amount),
                                    "user": user,
                                    "created_at": datetime.now().isoformat()
                                }
                                if supabase_auth_required(community_settings) and supports_owner_id and auth_user_id:
                                    bid_payload["owner_id"] = auth_user_id
                                _, err = community_add_bid(community_settings, db, bid_payload)
                                if err:
                                    st.error(err)
                                else:
                                    seller = post.get("created_by")
                                    if seller and seller != user:
                                        recipient_id = community_lookup_user_auth_id(community_settings, seller) if supabase_auth_required(community_settings) else None
                                        if supabase_auth_required(community_settings) and not recipient_id:
                                            st.warning("Bid placed, but seller has not linked a Community account yet.")
                                        else:
                                            msg_payload = {
                                                "sender": user,
                                                "recipient": seller,
                                                "subject": f"New bid on {post.get('title', 'your listing')}",
                                                "body": f"{user} placed a bid of {currency} {float(bid_amount):,.2f}.",
                                                "created_at": datetime.now().isoformat(),
                                                "read_at": None
                                            }
                                            if supabase_auth_required(community_settings) and auth_user_id:
                                                msg_payload["sender_id"] = auth_user_id
                                                msg_payload["recipient_id"] = recipient_id
                                            _, msg_err = community_send_message(community_settings, db, msg_payload)
                                            if msg_err:
                                                st.warning(f"Bid placed, but could not notify seller: {msg_err}")
                                    st.success("Bid submitted.")
                                    st.rerun()

                    if buy_now_price and user != post.get("created_by"):
                        if st.button("Buy Now", key=f"buy_now_{post_id}"):
                            _, err = community_update_post(community_settings, db, post_id, {
                                "status": "Sold",
                                "sold_price": float(buy_now_price),
                                "sold_at": datetime.now().isoformat()
                            })
                            if err:
                                st.error(err)
                            else:
                                seller = post.get("created_by")
                                if seller and seller != user:
                                    recipient_id = community_lookup_user_auth_id(community_settings, seller) if supabase_auth_required(community_settings) else None
                                    if supabase_auth_required(community_settings) and not recipient_id:
                                        st.warning("Purchase completed, but seller has not linked a Community account yet.")
                                    else:
                                        msg_payload = {
                                            "sender": user,
                                            "recipient": seller,
                                            "subject": f"Buy Now purchase on {post.get('title', 'your listing')}",
                                            "body": f"{user} purchased via Buy Now for {currency} {float(buy_now_price):,.2f}.",
                                            "created_at": datetime.now().isoformat(),
                                            "read_at": None
                                        }
                                        if supabase_auth_required(community_settings) and auth_user_id:
                                            msg_payload["sender_id"] = auth_user_id
                                            msg_payload["recipient_id"] = recipient_id
                                        community_send_message(community_settings, db, msg_payload)
                                st.success("Purchase completed.")
                                st.rerun()

            if listing_type == "For Sale":
                st.markdown(f"**Asking Price:** {currency} {float(price or 0.0):,.2f}")
                offers, offer_err = community_get_offers(community_settings, db, post_id)
                if offer_err:
                    st.error(offer_err)
                if status == "Active":
                    if is_banned:
                        st.info("You cannot send offers while suspended.")
                    else:
                        with st.form(f"offer_form_{post_id}"):
                            offer_amount = st.number_input(
                                f"Send Offer ({currency})",
                                min_value=0.0,
                                value=float(price or 0.0),
                                step=1.0
                            )
                            submit_offer = st.form_submit_button("Send Offer")
                        if submit_offer:
                            offer_payload = {
                                "post_id": post_id,
                                "amount": float(offer_amount),
                                "user": user,
                                "created_at": datetime.now().isoformat()
                            }
                            if supabase_auth_required(community_settings) and supports_owner_id and auth_user_id:
                                offer_payload["owner_id"] = auth_user_id
                            _, err = community_add_offer(community_settings, db, offer_payload)
                            if err:
                                st.error(err)
                            else:
                                st.success("Offer sent.")
                                st.rerun()

            comments, comment_err = community_get_comments(community_settings, db, post_id)
            if comment_err:
                st.error(comment_err)
                comments = []
            st.markdown("**Comments**")
            for comment in comments[-5:]:
                st.write(f"{comment.get('user', 'User')}: {comment.get('text', '')}")
            if is_banned:
                st.info("You cannot comment while suspended.")
            else:
                with st.form(f"comment_form_{post_id}"):
                    comment_text = st.text_input("Add a comment", key=f"comment_input_{post_id}")
                    submit_comment = st.form_submit_button("Post Comment")
                if submit_comment and comment_text.strip():
                    if validate_community_text(comment_text):
                        st.error("Your comment violates the Community Rules.")
                    else:
                        comment_payload = {
                            "post_id": post_id,
                            "user": user,
                            "text": comment_text.strip(),
                            "created_at": datetime.now().isoformat()
                        }
                        if supabase_auth_required(community_settings) and supports_owner_id and auth_user_id:
                            comment_payload["owner_id"] = auth_user_id
                        _, err = community_add_comment(community_settings, db, comment_payload)
                        if err:
                            st.error(err)
                        else:
                            st.success("Comment posted.")
                            st.rerun()

            if user != post.get("created_by"):
                if is_banned:
                    st.info("You cannot message sellers while suspended.")
                else:
                    with st.form(f"message_seller_{post_id}"):
                        message_body = st.text_area("Message seller", height=80, key=f"msg_body_{post_id}")
                        send_msg = st.form_submit_button("Send Message")
                    if send_msg and message_body.strip():
                        if validate_community_text(message_body):
                            st.error("Your message violates the Community Rules.")
                        else:
                            recipient_name = post.get("created_by")
                            recipient_id = community_lookup_user_auth_id(community_settings, recipient_name) if supabase_auth_required(community_settings) else None
                            if supabase_auth_required(community_settings) and not recipient_id:
                                st.error("Seller has not linked a Community account yet.")
                            else:
                                msg_payload = {
                                    "sender": user,
                                    "recipient": recipient_name,
                                    "subject": f"Re: {post.get('title', '')}",
                                    "body": message_body.strip(),
                                    "created_at": datetime.now().isoformat(),
                                    "read_at": None
                                }
                                if supabase_auth_required(community_settings) and auth_user_id:
                                    msg_payload["sender_id"] = auth_user_id
                                    msg_payload["recipient_id"] = recipient_id
                                _, err = community_send_message(community_settings, db, msg_payload)
                                if err:
                                    st.error(err)
                                else:
                                    st.success("Message sent.")
                                    st.rerun()

            report_cols = st.columns(2)
            with report_cols[0]:
                if st.button("Report Listing", key=f"report_{post_id}"):
                    report_payload = {
                        "id": secrets.token_hex(6),
                        "post_id": post_id,
                        "reported_by": user,
                        "reported_user": post.get("created_by"),
                        "reason": "User reported",
                        "created_at": datetime.now().isoformat()
                    }
                    if supabase_auth_required(community_settings) and supports_owner_id and auth_user_id:
                        report_payload["owner_id"] = auth_user_id
                    if supabase_enabled(community_settings):
                        report_payload.pop("id", None)
                    _, err = community_report_post(community_settings, db, report_payload)
                    if err:
                        st.error(err)
                    else:
                        st.success("Report submitted.")
                        st.rerun()
            if is_mod:
                with report_cols[1]:
                    if st.button("Remove Listing", key=f"remove_{post_id}"):
                        _, err = community_update_post(community_settings, db, post_id, {"status": "Removed"})
                        if err:
                            st.error(err)
                        else:
                            st.success("Listing removed.")
                            st.rerun()

        def render_listing_edit_modal():
            post_id = st.session_state.get("edit_listing_id")
            if not post_id:
                return
            if not is_elite:
                render_plan_gate(
                    user_settings,
                    "Elite",
                    "Edit Listings",
                    "Upgrade to Elite to edit Community Market listings.",
                    key="gate_community_edit"
                )
                st.session_state.edit_listing_id = None
                return
            target_post = next((post for post in forum_posts if post.get("id") == post_id), None)
            if not target_post:
                st.session_state.edit_listing_id = None
                return
            if supports_owner_id and auth_user_id and target_post.get("owner_id") and target_post.get("owner_id") != auth_user_id:
                st.error("Only the listing owner can edit this post.")
                st.session_state.edit_listing_id = None
                return
            if user != target_post.get("created_by"):
                st.error("Only the listing owner can edit this post.")
                st.session_state.edit_listing_id = None
                return
            dialog_ctx, dialog_supported = open_streamlit_dialog("Edit Listing")
            if dialog_supported:
                with dialog_ctx:
                    render_listing_edit_form(target_post, f"modal_{st.session_state.get('edit_listing_origin', 'browse')}")
                    st.markdown("---")
                    confirm_delete = st.checkbox("I understand this will permanently delete the listing.", key=f"confirm_delete_{post_id}")
                    if st.button("Delete Listing", key=f"delete_listing_modal_{post_id}"):
                        if not confirm_delete:
                            st.warning("Please confirm the deletion.")
                        else:
                            _, err = community_delete_post(community_settings, db, post_id)
                            if err:
                                st.error(err)
                            else:
                                st.success("Listing deleted.")
                                st.session_state.edit_listing_id = None
                                st.rerun()
                    if st.button("Close", key=f"close_edit_listing_{post_id}"):
                        st.session_state.edit_listing_id = None
                        st.rerun()
            else:
                dialog_fn = getattr(st, "dialog", None)
                if callable(dialog_fn):
                    @dialog_fn("Edit Listing")
                    def _edit_dialog():
                        render_listing_edit_form(
                            target_post,
                            f"modal_{st.session_state.get('edit_listing_origin', 'browse')}"
                        )
                        st.markdown("---")
                        confirm_delete = st.checkbox("I understand this will permanently delete the listing.", key=f"confirm_delete_{post_id}")
                        if st.button("Delete Listing", key=f"delete_listing_modal_{post_id}"):
                            if not confirm_delete:
                                st.warning("Please confirm the deletion.")
                            else:
                                _, err = community_delete_post(community_settings, db, post_id)
                                if err:
                                    st.error(err)
                                else:
                                    st.success("Listing deleted.")
                                    st.session_state.edit_listing_id = None
                                    st.rerun()
                        if st.button("Close", key=f"close_edit_listing_{post_id}"):
                            st.session_state.edit_listing_id = None
                            st.rerun()
                    _edit_dialog()
                else:
                    st.markdown("### Edit Listing")
                    st.caption("Your Streamlit version does not support modal dialogs. Showing the editor inline.")
                    render_listing_edit_form(
                        target_post,
                        f"modal_{st.session_state.get('edit_listing_origin', 'browse')}"
                    )
                    st.markdown("---")
                    confirm_delete = st.checkbox("I understand this will permanently delete the listing.", key=f"confirm_delete_{post_id}")
                    if st.button("Delete Listing", key=f"delete_listing_modal_{post_id}"):
                        if not confirm_delete:
                            st.warning("Please confirm the deletion.")
                        else:
                            _, err = community_delete_post(community_settings, db, post_id)
                            if err:
                                st.error(err)
                            else:
                                st.success("Listing deleted.")
                                st.session_state.edit_listing_id = None
                                st.rerun()
                    if st.button("Close", key=f"close_edit_listing_{post_id}"):
                        st.session_state.edit_listing_id = None
                        st.rerun()
                    st.stop()

        def render_listing_view_modal():
            post_id = st.session_state.get("market_view_post_id")
            if not post_id:
                return
            target_post = next((post for post in forum_posts if post.get("id") == post_id), None)
            if not target_post:
                st.session_state.market_view_post_id = None
                return
            status = get_post_status(target_post)
            dialog_ctx, dialog_supported = open_streamlit_dialog("Listing Details")
            if dialog_supported:
                with dialog_ctx:
                    render_listing_detail_panel(target_post, status)
                    if st.button("Close", key=f"close_view_listing_{post_id}"):
                        st.session_state.market_view_post_id = None
                        st.rerun()
            else:
                dialog_fn = getattr(st, "dialog", None)
                if callable(dialog_fn):
                    @dialog_fn("Listing Details")
                    def _view_dialog():
                        render_listing_detail_panel(target_post, status)
                        if st.button("Close", key=f"close_view_listing_{post_id}"):
                            st.session_state.market_view_post_id = None
                            st.rerun()
                    _view_dialog()
                else:
                    st.markdown("### Listing Details")
                    render_listing_detail_panel(target_post, status)
                    if st.button("Close", key=f"close_view_listing_{post_id}"):
                        st.session_state.market_view_post_id = None
                        st.rerun()
                    st.stop()

        render_listing_edit_modal()
        render_listing_view_modal()


        with forum_tabs[0]:
            if not community_ready:
                st.info("Community is not ready yet. Configure Supabase in the setup section at the bottom of this page.")
            else:
                if AUTOREFRESH_AVAILABLE:
                    live_updates = st.checkbox("Live updates (auto-refresh bids)", value=True, key="community_live_updates")
                    if live_updates:
                        st_autorefresh(interval=20000, key="community_live_refresh")
                st.markdown("### Browse Listings")
                category_seed = set(COMMUNITY_CATEGORY_OPTIONS)
                category_seed |= {post.get("category", "Other") for post in forum_posts}
                category_seed |= {asset.get("type", "Other") for asset in portfolio}
                category_options = list(COMMUNITY_CATEGORY_OPTIONS)
                for extra in sorted(category_seed - set(category_options)):
                    category_options.append(extra)
                category_counts = Counter([post.get("category", "Other") for post in forum_posts])
                top_categories = [cat for cat, _ in category_counts.most_common(6)]
                quick_categories = ["All"] + [cat for cat in top_categories if cat in category_options]
                quick_current = st.session_state.get("market_quick_category", "All")
                quick_index = quick_categories.index(quick_current) if quick_current in quick_categories else 0
                st.radio(
                    "Quick Categories",
                    quick_categories,
                    horizontal=True,
                    index=quick_index,
                    key="market_quick_category"
                )
                filter_container = st.container()
                with filter_container:
                    st.markdown('<div id="sticky-filter-marker"></div>', unsafe_allow_html=True)
                    filter_cols = st.columns([1.6, 1, 1, 1])
                    with filter_cols[0]:
                        search_term = st.text_input(
                            "Search listings",
                            placeholder="Search by title, description, or seller...",
                            key="market_search_term"
                        )
                    with filter_cols[1]:
                        type_filter = st.selectbox(
                            "Type",
                            ["All", "For Sale", "Auction", "Discussion"],
                            key="market_type_filter"
                        )
                    with filter_cols[2]:
                        category_filter = st.selectbox(
                            "Category",
                            ["All"] + category_options,
                            key="market_category_filter"
                        )
                    with filter_cols[3]:
                        status_filter = st.selectbox(
                            "Status",
                            ["All", "Active", "Ended", "Closed", "Sold", "Removed"],
                            key="market_status_filter"
                        )

                    if "market_price_range_pending" in st.session_state:
                        st.session_state.market_price_range = st.session_state.pop("market_price_range_pending")
                    price_values = [value for value in (get_listing_price_value(post) for post in forum_posts) if value is not None]
                    price_range = None
                    sort_cols = st.columns([2, 1])
                    with sort_cols[0]:
                        if price_values:
                            min_price = float(min(price_values))
                            max_price = float(max(price_values))
                            if "market_price_range" in st.session_state:
                                st.session_state.market_price_range = clamp_price_range(
                                    st.session_state.market_price_range, min_price, max_price
                                )
                            if min_price == max_price:
                                st.caption(f"Price range fixed at {currency_code} {min_price:,.2f}")
                                price_range = (min_price, max_price)
                            else:
                                if "market_price_range" in st.session_state:
                                    price_range = st.slider(
                                        f"Price Range ({currency_code})",
                                        min_value=min_price,
                                        max_value=max_price,
                                        key="market_price_range"
                                    )
                                else:
                                    price_range = st.slider(
                                        f"Price Range ({currency_code})",
                                        min_value=min_price,
                                        max_value=max_price,
                                        value=(min_price, max_price),
                                        key="market_price_range"
                                    )
                    with sort_cols[1]:
                        sort_option = st.selectbox(
                            "Sort by",
                            ["Newest", "Ending Soon", "Price (Low to High)", "Price (High to Low)"],
                            key="market_sort_option"
                        )

                components.html(
                    """
                    <script>
                      (function() {
                        const marker = window.parent.document.getElementById("sticky-filter-marker");
                        if (!marker) return;
                        const block = marker.closest('div[data-testid="stVerticalBlock"]');
                        if (block) {
                          block.classList.add("sticky-filter-block");
                        }
                      })();
                    </script>
                    """,
                    height=0
                )

                quick_filter_cols = st.columns(6)
                with quick_filter_cols[0]:
                    filter_watchlist = st.checkbox("Watchlist", key="market_filter_watchlist")
                with quick_filter_cols[1]:
                    filter_photos = st.checkbox("Photos only", key="market_filter_photos")
                with quick_filter_cols[2]:
                    filter_buy_now = st.checkbox("Buy Now", key="market_filter_buy_now")
                with quick_filter_cols[3]:
                    filter_new = st.checkbox("New (7d)", key="market_filter_new")
                with quick_filter_cols[4]:
                    filter_ending = st.checkbox("Ending Soon", key="market_filter_ending")
                with quick_filter_cols[5]:
                    filter_near_me = st.checkbox("Near Me", key="market_filter_near_me")

                with st.expander("Saved Searches"):
                    saved_searches = st.session_state.market_saved_searches
                    saved_names = [s.get("name") for s in saved_searches if s.get("name")]
                    selected_saved = st.selectbox(
                        "Select saved search",
                        ["Select..."] + saved_names,
                        key="market_saved_search_select"
                    )
                    save_name = st.text_input("Save current search as", key="market_save_search_name")
                    save_cols = st.columns(3)
                    with save_cols[0]:
                        if st.button("Save Search", key="market_save_search_btn"):
                            if not save_name.strip():
                                st.error("Please enter a name for this search.")
                            else:
                                payload = {
                                    "name": save_name.strip(),
                                    "search_term": search_term,
                                    "type_filter": type_filter,
                                    "category_filter": category_filter,
                                    "status_filter": status_filter,
                                    "sort_option": sort_option,
                                    "quick_category": st.session_state.get("market_quick_category", "All"),
                                    "price_range": list(price_range) if price_range else None,
                                    "filter_watchlist": filter_watchlist,
                                    "filter_photos": filter_photos,
                                    "filter_buy_now": filter_buy_now,
                                    "filter_new": filter_new,
                                    "filter_ending": filter_ending,
                                    "filter_near_me": filter_near_me,
                                    "saved_at": datetime.now().isoformat()
                                }
                                saved_searches = [s for s in saved_searches if s.get("name") != payload["name"]]
                                saved_searches.insert(0, payload)
                                st.session_state.market_saved_searches = saved_searches
                                persist_market_saved_searches(db, user, saved_searches)
                                st.success("Search saved.")
                    with save_cols[1]:
                        if st.button("Load Search", key="market_load_search_btn"):
                            if selected_saved and selected_saved != "Select...":
                                search = next((s for s in saved_searches if s.get("name") == selected_saved), None)
                                if search:
                                    st.session_state.market_search_term = search.get("search_term", "")
                                    st.session_state.market_type_filter = search.get("type_filter", "All")
                                    st.session_state.market_category_filter = search.get("category_filter", "All")
                                    st.session_state.market_status_filter = search.get("status_filter", "All")
                                    st.session_state.market_sort_option = search.get("sort_option", "Newest")
                                    st.session_state.market_quick_category = search.get("quick_category", "All")
                                    st.session_state.market_filter_watchlist = bool(search.get("filter_watchlist", False))
                                    st.session_state.market_filter_photos = bool(search.get("filter_photos", False))
                                    st.session_state.market_filter_buy_now = bool(search.get("filter_buy_now", False))
                                    st.session_state.market_filter_new = bool(search.get("filter_new", False))
                                    st.session_state.market_filter_ending = bool(search.get("filter_ending", False))
                                    st.session_state.market_filter_near_me = bool(search.get("filter_near_me", False))
                                    if price_values and search.get("price_range"):
                                        min_price = float(min(price_values))
                                        max_price = float(max(price_values))
                                        st.session_state.market_price_range_pending = clamp_price_range(
                                            search.get("price_range"), min_price, max_price
                                        )
                                    st.rerun()
                    with save_cols[2]:
                        if st.button("Delete Search", key="market_delete_search_btn"):
                            if selected_saved and selected_saved != "Select...":
                                saved_searches = [s for s in saved_searches if s.get("name") != selected_saved]
                                st.session_state.market_saved_searches = saved_searches
                                persist_market_saved_searches(db, user, saved_searches)
                                st.success("Search deleted.")
                                st.rerun()

                    if selected_saved and selected_saved != "Select...":
                        search = next((s for s in saved_searches if s.get("name") == selected_saved), None)
                        if search:
                            alerts_enabled = st.checkbox(
                                "Enable alerts for this search",
                                value=bool(search.get("alerts_enabled", True)),
                                key="market_saved_search_alerts_enabled"
                            )
                            email_enabled = st.checkbox(
                                "Email alerts for this search",
                                value=bool(search.get("email_alerts", False)),
                                key="market_saved_search_email_enabled"
                            )
                            if (
                                alerts_enabled != bool(search.get("alerts_enabled", True))
                                or email_enabled != bool(search.get("email_alerts", False))
                            ):
                                search["alerts_enabled"] = alerts_enabled
                                search["email_alerts"] = email_enabled
                                persist_market_saved_searches(db, user, saved_searches)
                            last_checked = search.get("last_checked", "Never")
                            last_alerted = search.get("last_alerted", "Never")
                            st.caption(f"Last checked: {last_checked} • Last alert: {last_alerted}")

                def apply_saved_search_filters(posts, search_state):
                    s_term = (search_state.get("search_term") or "").strip().lower()
                    s_type = search_state.get("type_filter", "All")
                    s_category = search_state.get("category_filter", "All")
                    s_status = search_state.get("status_filter", "All")
                    s_sort = search_state.get("sort_option", "Newest")
                    s_quick = search_state.get("quick_category", "All")
                    s_price = search_state.get("price_range")
                    s_watch = bool(search_state.get("filter_watchlist"))
                    s_photos = bool(search_state.get("filter_photos"))
                    s_buy_now = bool(search_state.get("filter_buy_now"))
                    s_new = bool(search_state.get("filter_new"))
                    s_ending = bool(search_state.get("filter_ending"))
                    s_near = bool(search_state.get("filter_near_me"))

                    if s_quick and s_quick != "All":
                        s_category = s_quick

                    results = []
                    for post in posts:
                        status = get_post_status(post)
                        if s_type != "All" and post.get("listing_type") != s_type:
                            continue
                        if s_category != "All" and post.get("category") != s_category:
                            continue
                        if s_status != "All" and status != s_status:
                            continue
                        if s_term:
                            hay = f"{post.get('title','')} {post.get('body','')} {post.get('created_by','')}".lower()
                            if s_term not in hay:
                                continue
                        if s_price:
                            price_value = get_listing_price_value(post)
                            if price_value is None:
                                continue
                            if price_value < s_price[0] or price_value > s_price[1]:
                                continue
                        if s_watch and post.get("id") not in st.session_state.market_watchlist:
                            continue
                        if s_photos and not get_post_images(post):
                            continue
                        if s_buy_now and not post.get("buy_now_price"):
                            continue
                        if s_new and not is_recent_listing(post, days=7):
                            continue
                        if s_ending:
                            end_dt = get_auction_end_dt(post)
                            if not end_dt:
                                continue
                            if end_dt > forum_now() + timedelta(days=2):
                                continue
                        if s_near:
                            user_country = get_country_name(get_country_code(user_settings)).lower()
                            post_country = str(post.get("location", "")).lower()
                            if user_country and user_country not in post_country:
                                continue
                        results.append((status, post))

                    if s_sort == "Ending Soon":
                        results.sort(key=lambda pair: get_auction_end_dt(pair[1]) or datetime.max)
                    elif s_sort == "Price (Low to High)":
                        results.sort(key=lambda pair: get_listing_price_value(pair[1]) if get_listing_price_value(pair[1]) is not None else float("inf"))
                    elif s_sort == "Price (High to Low)":
                        results.sort(key=lambda pair: get_listing_price_value(pair[1]) if get_listing_price_value(pair[1]) is not None else -1, reverse=True)
                    else:
                        results.sort(key=lambda pair: parse_forum_date(pair[1].get("created_at", "")), reverse=True)
                    return results

                def run_saved_search_alerts():
                    alerts = []
                    updated = False
                    saved_searches = st.session_state.market_saved_searches
                    if not saved_searches:
                        return alerts, updated
                    now_iso = datetime.now().isoformat()
                    for search in saved_searches:
                        if not search.get("alerts_enabled", True):
                            continue
                        results = apply_saved_search_filters(forum_posts, search)
                        result_ids = [post.get("id") for _, post in results if post.get("id")]
                        last_ids = set(search.get("last_result_ids") or [])
                        new_ids = [pid for pid in result_ids if pid not in last_ids]
                        search["last_result_ids"] = result_ids[:200]
                        search["last_checked"] = now_iso
                        updated = True
                        if new_ids:
                            alerts.append({
                                "name": search.get("name"),
                                "count": len(new_ids),
                                "sample": results[:3]
                            })
                            search["last_alerted"] = now_iso
                            if user_settings.get("market_alerts_email_enabled") and search.get("email_alerts"):
                                subject = f"WealthPulse Alert: {search.get('name')} ({len(new_ids)} new)"
                                listing_lines = []
                                for _, post in results[:5]:
                                    listing_lines.append(f"- {post.get('title')} ({post.get('listing_type')})")
                                body = "New listings matched your saved search:\n" + "\n".join(listing_lines)
                                send_alert_email(user_settings, subject, body)
                    if updated:
                        st.session_state.market_saved_searches = saved_searches
                        persist_market_saved_searches(db, user, saved_searches)
                    return alerts, updated

                quick_category = st.session_state.get("market_quick_category", "All")
                if quick_category != "All":
                    category_filter = quick_category

                filtered = []
                for post in forum_posts:
                    status = get_post_status(post)
                    if type_filter != "All" and post.get("listing_type") != type_filter:
                        continue
                    if category_filter != "All" and post.get("category") != category_filter:
                        continue
                    if status_filter != "All" and status != status_filter:
                        continue
                    if search_term:
                        hay = f"{post.get('title','')} {post.get('body','')} {post.get('created_by','')}".lower()
                        if search_term.lower() not in hay:
                            continue
                    if price_range:
                        price_value = get_listing_price_value(post)
                        if price_value is None:
                            continue
                        if price_value < price_range[0] or price_value > price_range[1]:
                            continue
                    if filter_watchlist and post.get("id") not in st.session_state.market_watchlist:
                        continue
                    if filter_photos and not get_post_images(post):
                        continue
                    if filter_buy_now and not post.get("buy_now_price"):
                        continue
                    if filter_new and not is_recent_listing(post, days=7):
                        continue
                    if filter_ending:
                        end_dt = get_auction_end_dt(post)
                        if not end_dt:
                            continue
                        if end_dt > forum_now() + timedelta(days=2):
                            continue
                    if filter_near_me:
                        user_country = get_country_name(get_country_code(user_settings)).lower()
                        post_country = str(post.get("location", "")).lower()
                        if user_country and user_country not in post_country:
                            continue
                    filtered.append((status, post))

                if sort_option == "Ending Soon":
                    filtered.sort(
                        key=lambda pair: get_auction_end_dt(pair[1]) or datetime.max
                    )
                elif sort_option == "Price (Low to High)":
                    filtered.sort(
                        key=lambda pair: get_listing_price_value(pair[1]) if get_listing_price_value(pair[1]) is not None else float("inf")
                    )
                elif sort_option == "Price (High to Low)":
                    filtered.sort(
                        key=lambda pair: get_listing_price_value(pair[1]) if get_listing_price_value(pair[1]) is not None else -1,
                        reverse=True
                    )
                else:
                    filtered.sort(key=lambda pair: parse_forum_date(pair[1].get("created_at", "")), reverse=True)

                alerts_enabled = bool(user_settings.get("market_alerts_enabled", True))
                alert_interval = int(user_settings.get("market_alerts_interval", 180))
                if alerts_enabled:
                    last_check = st.session_state.get("market_alerts_last_check", 0.0)
                    if time.time() - last_check >= alert_interval:
                        alert_results, _ = run_saved_search_alerts()
                        st.session_state.market_alerts_last_check = time.time()
                    else:
                        alert_results = []
                    if alert_results:
                        st.markdown("#### Saved Search Alerts")
                        for alert in alert_results:
                            st.info(f"{alert['name']}: {alert['count']} new listing(s) matched.")
                        if user_settings.get("market_alerts_push_enabled"):
                            signature = build_alert_signature(alert_results)
                            if signature and signature != st.session_state.get("market_alerts_last_push_signature"):
                                st.session_state.market_alerts_last_push_signature = signature
                                trigger_browser_notifications(alert_results)

                if not filtered:
                    st.info("No listings yet. Create the first post!")
                else:
                    stats_cols = st.columns(4)
                    total_count = len(forum_posts)
                    active_count = sum(1 for status, _ in filtered if status == "Active")
                    auction_count = sum(1 for _, post in filtered if post.get("listing_type") == "Auction")
                    ending_soon_count = sum(
                        1 for _, post in filtered
                        if post.get("listing_type") == "Auction"
                        and (get_auction_end_dt(post) and get_auction_end_dt(post) <= forum_now() + timedelta(days=2))
                    )
                    stats_cols[0].metric("Listings", f"{total_count}")
                    stats_cols[1].metric("Active", f"{active_count}")
                    stats_cols[2].metric("Auctions", f"{auction_count}")
                    stats_cols[3].metric("Ending Soon", f"{ending_soon_count}")

                    featured = sorted(
                        filtered,
                        key=lambda pair: get_listing_price_value(pair[1]) or 0.0,
                        reverse=True
                    )[:3]
                    if featured:
                        st.markdown("#### Featured Picks")
                        feat_cols = st.columns(len(featured))
                        for idx, (status, post) in enumerate(featured):
                            with feat_cols[idx]:
                                render_marketplace_card(post, status, "featured")

                    post_ids = [post.get("id") for _, post in filtered]
                    if st.session_state.market_selected_post_id not in post_ids:
                        st.session_state.market_selected_post_id = post_ids[0]

                    card_cols = st.columns(3)
                    for idx, (status, post) in enumerate(filtered):
                        with card_cols[idx % 3]:
                            render_marketplace_card(post, status, "grid")

                    selected_post = None
                    selected_status = None
                    for status, post in filtered:
                        if post.get("id") == st.session_state.market_selected_post_id:
                            selected_post = post
                            selected_status = status
                            break
                    st.markdown("---")
                    if selected_post:
                        render_listing_detail_panel(selected_post, selected_status or get_post_status(selected_post))
                    else:
                        st.info("Select a listing to view details.")

        with forum_tabs[1]:
            st.markdown("### Watchlist")
            watchlist_items = [post for post in forum_posts if post.get("id") in st.session_state.market_watchlist]
            if not watchlist_items:
                st.info("No watchlist items yet. Tap Watch on a listing to save it here.")
            else:
                watchlist_items.sort(key=lambda post: parse_forum_date(post.get("created_at", "")), reverse=True)
                watchlist_pairs = [(get_post_status(post), post) for post in watchlist_items]
                watchlist_cols = st.columns(3)
                for idx, (status, post) in enumerate(watchlist_pairs):
                    with watchlist_cols[idx % 3]:
                        render_marketplace_card(post, status, "watchlist")
                watch_ids = [post.get("id") for _, post in watchlist_pairs]
                selected_id = st.session_state.get("market_selected_post_id")
                if selected_id not in watch_ids:
                    st.session_state.market_selected_post_id = watch_ids[0]
                selected_post = None
                selected_status = None
                for status, post in watchlist_pairs:
                    if post.get("id") == st.session_state.market_selected_post_id:
                        selected_post = post
                        selected_status = status
                        break
                st.markdown("---")
                if selected_post:
                    render_listing_detail_panel(selected_post, selected_status or get_post_status(selected_post))

        with forum_tabs[2]:
            if not is_elite:
                render_plan_gate(user_settings, "Elite", "Create Listing", "Upgrade to post listings and host auctions in the Community Market.", key="gate_community_create")
            else:
                st.markdown("### Create Listing")
                if not community_ready:
                    st.info("Community is not ready yet. Configure Supabase in the setup section at the bottom of this page.")
                elif community_is_banned(community_settings, db, user):
                    st.error("Your account is suspended from posting.")
                else:
                    st.markdown("**Community Rules**")
                    for rule in COMMUNITY_RULES:
                        st.markdown(f"- {rule}")
                    st.markdown("**Marketplace Disclaimer**")
                    st.caption(
                        "Transactions are arranged directly between users. Buyers and sellers must contact each other "
                        "to settle payment and delivery outside of the app using their preferred method. "
                        "We provide the community forum only and take no responsibility for sales, disputes, "
                        "or fraudulent activity."
                    )
                    prefill = st.checkbox("Prefill from my portfolio", value=bool(portfolio))
                    prefill_asset = None
                    if prefill and portfolio:
                        asset_options = [f"{i+1}. {asset['name']} ({asset['type']})" for i, asset in enumerate(portfolio)]
                        selected_asset_label = st.selectbox("Choose asset", asset_options)
                        selected_index = int(selected_asset_label.split(".")[0]) - 1
                        if 0 <= selected_index < len(portfolio):
                            prefill_asset = portfolio[selected_index]

                    default_title = prefill_asset.get("name", "") if prefill_asset else ""
                    default_category = prefill_asset.get("type", "Other") if prefill_asset else "Other"
                    default_body = ""
                    default_price = 0.0
                    if prefill_asset:
                        default_body = f"{prefill_asset.get('type')} in {prefill_asset.get('condition')} condition. Qty {prefill_asset.get('qty', 1)}."
                        default_price = to_display_currency(ai_valuation(prefill_asset)[0], currency_rate)

                    category_search = st.text_input(
                        "Filter categories (optional)",
                        placeholder="Type to filter categories (e.g., bullion, coins, trading cards)",
                        key="market_category_search"
                    )

                    with st.form("create_listing_form"):
                        listing_type = st.selectbox("Listing Type", ["For Sale", "Auction", "Discussion"])
                        category_list = list(COMMUNITY_CATEGORY_OPTIONS)
                        extra_categories = [default_category] + [asset.get("type", "Other") for asset in portfolio]
                        for extra in sorted({c for c in extra_categories if c} - set(category_list)):
                            category_list.append(extra)
                        category_list = filter_category_options(category_list, category_search)
                        category = st.selectbox(
                            "Category",
                            category_list,
                            index=category_list.index(default_category) if default_category in category_list else 0
                        )
                        title = st.text_input("Title", value=default_title)
                        description = st.text_area("Description", value=default_body, height=120)
                        grading_type = grading_type_for_category(category)
                        grading_company = None
                        grading_grade = None
                        if grading_type:
                            st.markdown("#### Grading (optional)")
                            if supports_grading:
                                if grading_type == "coin":
                                    company_options = COIN_GRADING_COMPANIES
                                    grade_options = COIN_GRADE_OPTIONS
                                else:
                                    company_options = CARD_GRADING_COMPANIES
                                    grade_options = CARD_GRADE_OPTIONS
                                grading_company = st.selectbox(
                                    "Grading Company",
                                    ["Ungraded / None"] + company_options,
                                    key="listing_grading_company"
                                )
                                grading_grade = st.selectbox(
                                    "Grade",
                                    grade_options,
                                    key="listing_grading_grade"
                                )
                                if grading_company == "Ungraded / None":
                                    grading_company = None
                                if grading_grade == "Ungraded":
                                    grading_grade = None
                            else:
                                st.caption("Grading fields require a schema update. Run the migration helper below.")
                        listing_images = []
                        if supports_images:
                            listing_images = st.file_uploader(
                                f"Listing Photos (max {MAX_LISTING_IMAGES})",
                                type=["jpg", "jpeg", "png"],
                                accept_multiple_files=True
                            )
                            if listing_images:
                                image_error = validate_listing_images(listing_images)
                                if image_error:
                                    st.warning(image_error)
                                    listing_images = listing_images[:MAX_LISTING_IMAGES]
                            if listing_images:
                                preview_cols = st.columns(min(len(listing_images), 5))
                                for idx, img in enumerate(listing_images[:5]):
                                    with preview_cols[idx]:
                                        st.image(img, width=140)
                        else:
                            st.caption("Photo uploads require a schema update. Run the migration helper below.")
                        default_country = get_country_name(get_country_code(user_settings))
                        location = st.text_input(
                            "Country (required)",
                            value=default_country,
                            help="Enter the country where the item is located. Add city/region in the description if needed."
                        )
                        price = None
                        starting_bid = None
                        min_increment = None
                        reserve_amount = None
                        buy_now_price = None
                        end_date = None
                        if listing_type == "For Sale":
                            price = st.number_input(f"Price ({currency_code})", min_value=0.0, value=float(default_price), step=1.0)
                        elif listing_type == "Auction":
                            starting_bid = st.number_input(f"Starting Bid ({currency_code})", min_value=0.0, value=float(default_price), step=1.0)
                            min_increment = st.number_input(f"Minimum Increment ({currency_code})", min_value=0.0, value=10.0, step=1.0)
                            if supports_reserve:
                                reserve_amount = st.number_input(f"Reserve Amount ({currency_code})", min_value=0.0, value=0.0, step=1.0)
                            else:
                                st.caption("Reserve amounts require a schema update. Run the migration helper.")
                            if supports_buy_now:
                                buy_now_price = st.number_input(f"Buy Now Price ({currency_code})", min_value=0.0, value=0.0, step=1.0)
                            else:
                                st.caption("Buy Now requires a schema update. Run the migration helper.")
                            end_date = st.date_input("Auction End Date", value=datetime.now().date() + timedelta(days=7))

                        agree_rules = st.checkbox("I agree to the Community Rules above.")
                        agree_terms = st.checkbox("I agree to the Marketplace Disclaimer above.")
                        submit_listing = st.form_submit_button("Post Listing")

                    if submit_listing:
                        if not title.strip():
                            st.error("Title is required.")
                        elif not location.strip():
                            st.error("Country is required.")
                        elif not description.strip():
                            st.error("Description is required.")
                        elif validate_community_text(f"{title} {description} {location}"):
                            st.error("Your listing contains content that violates the Community Rules.")
                        elif listing_images and validate_listing_images(listing_images):
                            st.error(validate_listing_images(listing_images))
                        elif not agree_rules:
                            st.error("You must agree to the Community Rules to post a listing.")
                        elif not agree_terms:
                            st.error("You must agree to the Marketplace Disclaimer to post a listing.")
                        elif listing_type == "Auction" and supports_reserve and reserve_amount and starting_bid is not None and reserve_amount < starting_bid:
                            st.error("Reserve amount should be equal to or higher than the starting bid.")
                        elif listing_type == "Auction" and supports_buy_now and buy_now_price and reserve_amount and buy_now_price < reserve_amount:
                            st.error("Buy Now price should be equal to or higher than the reserve.")
                        else:
                            encoded_images = encode_uploaded_images(listing_images) if (supports_images and listing_images) else []
                            post_payload = {
                                "id": secrets.token_hex(6),
                                "title": title.strip(),
                                "body": description.strip(),
                                "category": category,
                                "listing_type": listing_type,
                                "price": float(price) if price is not None else None,
                                "currency": currency_code,
                                "location": location.strip(),
                                "created_by": user,
                                "created_at": datetime.now().isoformat(),
                                "status": "Active",
                                "auction_starting_bid": float(starting_bid) if starting_bid is not None else None,
                                "auction_min_increment": float(min_increment) if min_increment is not None else None,
                                "reserve_amount": float(reserve_amount) if supports_reserve and reserve_amount and reserve_amount > 0 else None,
                                "buy_now_price": float(buy_now_price) if supports_buy_now and buy_now_price and buy_now_price > 0 else None,
                                "auction_end_date": end_date.isoformat() if end_date else None,
                                "images": encoded_images or None
                            }
                            if supabase_auth_required(community_settings) and supports_owner_id and auth_user_id:
                                post_payload["owner_id"] = auth_user_id
                            if supports_grading:
                                if grading_company:
                                    post_payload["grading_company"] = grading_company
                                if grading_grade:
                                    post_payload["grading_grade"] = grading_grade
                            if not post_payload.get("reserve_amount"):
                                post_payload.pop("reserve_amount", None)
                            if not post_payload.get("buy_now_price"):
                                post_payload.pop("buy_now_price", None)
                            if not post_payload.get("images"):
                                post_payload.pop("images", None)
                            if supabase_enabled(community_settings):
                                post_payload.pop("id", None)
                            _, err = community_create_post(community_settings, db, post_payload)
                            if err:
                                st.error(err)
                            else:
                                save_data(db)
                                st.success("Listing posted.")
                                request_scroll_to_top()
                                st.rerun()

        with forum_tabs[3]:
            if not is_elite:
                render_plan_gate(user_settings, "Elite", "My Listings", "Upgrade to manage and edit your Community Market listings.", key="gate_community_manage")
            else:
                st.markdown("### My Listings")
                if not community_ready:
                    st.info("Community is not ready yet. Configure Supabase in the setup section at the bottom of this page.")
                else:
                    my_posts = [post for post in forum_posts if post.get("created_by") == user]
                    if not my_posts:
                        st.info("You haven't posted anything yet.")
                    else:
                        my_posts.sort(key=lambda post: parse_forum_date(post.get("created_at", "")), reverse=True)
                        for post in my_posts:
                            status = get_post_status(post)
                            header = f"{post.get('title', 'Listing')} • {post.get('listing_type')} • {status}"
                            with st.expander(header):
                                st.write(post.get("body", ""))
                                st.caption(f"Posted {post.get('created_at','')}")
                                post_images = get_post_images(post)
                                if post_images:
                                    image_cols = st.columns(min(len(post_images), 5))
                                    for idx, img in enumerate(post_images):
                                        with image_cols[idx]:
                                            st.image(img, width=160)
                                if post.get("listing_type") == "Auction":
                                    reserve_amount = get_reserve_amount(post) if supports_reserve else None
                                    buy_now_price = get_buy_now_price(post) if supports_buy_now else None
                                    _, _, end_date = get_auction_fields(post)
                                    time_left_label = format_time_left(end_date, user_settings)
                                    if time_left_label:
                                        st.caption(time_left_label)
                                    if reserve_amount:
                                        st.caption(f"Reserve: {post.get('currency', currency_code)} {float(reserve_amount):,.2f}")
                                    if buy_now_price:
                                        st.caption(f"Buy Now: {post.get('currency', currency_code)} {float(buy_now_price):,.2f}")
                                if st.button("Edit Listing", key=f"edit_listing_open_my_{post.get('id')}"):
                                    st.session_state.edit_listing_id = post.get("id")
                                    st.session_state.edit_listing_origin = "my"
                                    st.session_state.jump_to_community = True
                                    request_scroll_to_top()
                                    st.rerun()
                                sale_cols = st.columns(3)
                                with sale_cols[0]:
                                    if st.button("Close Listing", key=f"close_listing_{post.get('id')}"):
                                        _, err = community_update_post(community_settings, db, post.get("id"), {"status": "Closed"})
                                        if err:
                                            st.error(err)
                                        else:
                                            st.success("Listing closed.")
                                            st.rerun()
                                with sale_cols[1]:
                                    default_sold_price = float(post.get("price") or 0.0)
                                    if post.get("listing_type") == "Auction":
                                        bids, _ = community_get_bids(community_settings, db, post.get("id"))
                                        if bids:
                                            default_sold_price = max([b.get("amount", 0.0) for b in bids])
                                    sold_price = st.number_input(
                                        f"Sold Price ({post.get('currency', currency_code)})",
                                        min_value=0.0,
                                        value=float(default_sold_price),
                                        step=1.0,
                                        key=f"sold_price_{post.get('id')}"
                                    )
                                    if st.button("Mark as Sold", key=f"mark_sold_{post.get('id')}"):
                                        _, err = community_update_post(community_settings, db, post.get("id"), {
                                            "status": "Sold",
                                            "sold_price": float(sold_price),
                                            "sold_at": datetime.now().isoformat()
                                        })
                                        if err:
                                            st.error(err)
                                        else:
                                            st.success("Listing marked as sold.")
                                            st.rerun()
                                with sale_cols[2]:
                                    if st.button("Delete Listing", key=f"delete_listing_{post.get('id')}"):
                                        _, err = community_delete_post(community_settings, db, post.get("id"))
                                        if err:
                                            st.error(err)
                                        else:
                                            st.success("Listing deleted.")
                                            st.rerun()

        with forum_tabs[4]:
            st.markdown("### Private Messages")
            if not community_ready:
                st.info("Community is not ready yet. Configure Supabase in the setup section at the bottom of this page.")
            else:
                msg_cols = st.columns(2)
                with msg_cols[0]:
                    st.markdown("**Inbox**")
                    inbox, inbox_err = community_get_messages(community_settings, db, user, box="inbox")
                    if inbox_err:
                        st.error(inbox_err)
                    else:
                        for msg in inbox[:10]:
                            status = "Unread" if not msg.get("read_at") else "Read"
                            with st.expander(f"From {msg.get('sender')} • {status}"):
                                st.caption(msg.get("created_at", ""))
                                st.write(msg.get("subject", ""))
                                st.write(msg.get("body", ""))
                                if not msg.get("read_at") and msg.get("id"):
                                    if st.button("Mark Read", key=f"mark_read_{msg.get('id')}"):
                                        _, err = community_mark_message_read(community_settings, db, msg.get("id"))
                                        if err:
                                            st.error(err)
                                        else:
                                            st.success("Marked as read.")
                                            st.rerun()
                with msg_cols[1]:
                    st.markdown("**Send Message**")
                    if is_banned:
                        st.info("You cannot send messages while suspended.")
                    else:
                        with st.form("send_message_form"):
                            recipient = st.text_input("Recipient Username")
                            subject = st.text_input("Subject")
                            body = st.text_area("Message", height=120)
                            send_msg = st.form_submit_button("Send")
                        if send_msg:
                            if not recipient or not body.strip():
                                st.error("Recipient and message are required.")
                            elif validate_community_text(f"{subject} {body}"):
                                st.error("Your message violates the Community Rules.")
                            else:
                                recipient_name = recipient.strip()
                                recipient_id = community_lookup_user_auth_id(community_settings, recipient_name) if supabase_auth_required(community_settings) else None
                                if supabase_auth_required(community_settings) and not recipient_id:
                                    st.error("Recipient has not linked a Community account yet.")
                                else:
                                    _, err = community_send_message(community_settings, db, {
                                        "sender": user,
                                        "recipient": recipient_name,
                                        "sender_id": auth_user_id if supabase_auth_required(community_settings) else None,
                                        "recipient_id": recipient_id,
                                        "subject": subject.strip(),
                                        "body": body.strip(),
                                        "created_at": datetime.now().isoformat(),
                                        "read_at": None
                                    })
                                if err:
                                    st.error(err)
                                else:
                                    st.success("Message sent.")
                                    st.rerun()
                    st.markdown("**Sent**")
                    sent_messages, sent_err = community_get_messages(community_settings, db, user, box="sent")
                    if sent_err:
                        st.error(sent_err)
                    else:
                        for msg in sent_messages[:10]:
                            with st.expander(f"To {msg.get('recipient')}"):
                                st.caption(msg.get("created_at", ""))
                                st.write(msg.get("subject", ""))
                                st.write(msg.get("body", ""))

        if is_mod:
            with forum_tabs[5]:
                if not community_ready:
                    st.info("Community is not ready yet. Configure Supabase in the setup section at the bottom of this page.")
                else:
                    if supabase_enabled(community_settings) and not community_use_service_role(community_settings):
                        st.warning("Moderation actions require the Supabase service role key. Add it in secrets to enable bans and report management.")
                    st.markdown("### Moderation")
                    reports, report_err = community_get_reports(community_settings, db)
                    if report_err:
                        st.error(report_err)
                    if not reports:
                        st.info("No reports yet.")
                    else:
                        for report in reports:
                            report_id = report.get("id")
                            post_id = report.get("post_id")
                            with st.expander(f"Report on {post_id} by {report.get('reported_by', 'User')}"):
                                st.caption(report.get("created_at", ""))
                                st.write(report.get("reason", ""))
                                mod_cols = st.columns(3)
                                with mod_cols[0]:
                                    if st.button("Remove Post", key=f"mod_remove_{report_id}"):
                                        _, err = community_update_post(community_settings, db, post_id, {"status": "Removed"})
                                        if err:
                                            st.error(err)
                                        else:
                                            st.success("Post removed.")
                                            st.rerun()
                                with mod_cols[1]:
                                    if st.button("Clear Report", key=f"mod_clear_{report_id}"):
                                        _, err = community_clear_report(community_settings, db, report_id)
                                        if err:
                                            st.error(err)
                                        else:
                                            st.success("Report cleared.")
                                            st.rerun()
                                with mod_cols[2]:
                                    target_user = report.get("reported_user") or ""
                                    if st.button("Ban User", key=f"mod_ban_{report_id}"):
                                        if not target_user:
                                            st.error("No user attached to report.")
                                        else:
                                            _, err = community_set_ban(community_settings, db, target_user, "Reported in Community Market")
                                            if err:
                                                st.error(err)
                                            else:
                                                st.success("User banned.")
                                                st.rerun()

                    st.markdown("### Moderators")
                    if role == "admin":
                        existing_roles, _ = community_get_roles(community_settings, db)
                        st.write("Current moderators:")
                        for entry in existing_roles:
                            st.write(f"{entry.get('username')} — {entry.get('role')}")
                        with st.form("add_moderator_form"):
                            mod_user = st.text_input("Username")
                            mod_role = st.selectbox("Role", ["moderator", "admin"])
                            submit_mod = st.form_submit_button("Save Role")
                        if submit_mod and mod_user.strip():
                            _, err = community_set_role(community_settings, db, mod_user.strip(), mod_role)
                            if err:
                                st.error(err)
                            else:
                                st.success("Role updated.")
                                st.rerun()
                        with st.form("remove_moderator_form"):
                            remove_user = st.text_input("Remove Username")
                            remove_submit = st.form_submit_button("Remove Role")
                        if remove_submit and remove_user.strip():
                            _, err = community_remove_role(community_settings, db, remove_user.strip())
                            if err:
                                st.error(err)
                            else:
                                st.success("Role removed.")
                                st.rerun()

        st.markdown("---")
        st.subheader("Community Market")
        policy_mode = (user_settings.get("community_policy_mode") or "unknown").lower()
        app_access_open = not supabase_auth_required(community_settings)
        app_access_label = "App: Open Access" if app_access_open else "App: Sign-in Required"
        app_badge_class = "open" if app_access_open else "secure"
        policy_label_map = {
            "open": "Supabase: Open",
            "auth": "Supabase: Auth Required",
            "service": "Supabase: Service Role",
            "unknown": "Supabase: Not Set"
        }
        policy_badge_class = policy_mode if policy_mode in {"open", "auth", "service"} else "unknown"
        policy_badge_style = "secure" if policy_badge_class in {"auth", "service"} else "open" if policy_badge_class == "open" else "unknown"
        st.markdown(
            f"""
            <div class="community-badges">
                <div class="community-badge {app_badge_class}">{app_access_label}</div>
                <div class="community-badge {policy_badge_style}">{policy_label_map.get(policy_badge_class, 'Supabase: Not Set')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if supabase_connected:
            st.caption("Connected to Supabase community backend (multi-device).")
        else:
            st.warning("Connect Supabase in Settings to enable the multi-device community. Using local mode until configured.")

        if supabase_connected:
            if not schema_ok:
                if is_supabase_missing_table_error(schema_err):
                    st.error("Community backend not set up yet (tables missing).")
                    st.info("Run the SQL in `supabase_community_schema.sql` using the Supabase SQL editor, then refresh.")
                    with st.expander("Show Supabase schema SQL"):
                        schema_sql = load_community_schema_sql()
                        if schema_sql:
                            st.code(schema_sql, language="sql")
                        else:
                            st.caption("Schema file not found in the app directory.")
                else:
                    st.error(f"Community backend error: {schema_err}")

            st.markdown("### Setup Checklist")
            st.caption("Run the SQL schema and use this checklist to confirm your community tables are live.")
            if "community_checklist_results" not in st.session_state:
                st.session_state.community_checklist_results = None
            checklist_tables = [
                "community_users",
                "community_posts",
                "community_comments",
                "community_bids",
                "community_offers",
                "community_messages",
                "community_roles",
                "community_bans",
                "community_reports",
                "wealthpulse_users"
            ]
            if st.button("Run Setup Checklist", key="community_setup_checklist"):
                checklist_results = supabase_check_tables(
                    community_settings,
                    checklist_tables,
                    use_service_key=community_use_service_role(community_settings),
                    auth_token=community_auth_token(community_settings)
                )
                st.session_state.community_checklist_results = {
                    "results": checklist_results,
                    "checked_at": datetime.now().isoformat()
                }
            if st.session_state.community_checklist_results:
                render_checklist_results(
                    st.session_state.community_checklist_results["results"],
                    st.session_state.community_checklist_results.get("checked_at")
                )
            else:
                st.info("Click 'Run Setup Checklist' after running the SQL to confirm tables are available.")

            test_cols = st.columns([1, 3])
            with test_cols[0]:
                if st.button("Test Supabase Connection", key="community_supabase_test"):
                    ok, err = supabase_check_table(
                        community_settings,
                        "community_posts",
                        use_service_key=community_use_service_role(community_settings),
                        auth_token=community_auth_token(community_settings)
                    )
                    if ok:
                        st.success("Supabase connection OK.")
                    else:
                        st.error(f"Supabase test failed: {err}")

            st.markdown("### Migration Helper")
            st.caption("Detect and generate SQL for new columns (reserve + buy now + images + grading + auth ownership fields).")
            if "community_migration_results" not in st.session_state:
                st.session_state.community_migration_results = None
            if st.button("Check for missing columns", key="community_migration_check"):
                migration_results = supabase_check_columns(
                    community_settings,
                    "community_posts",
                    list(COMMUNITY_POSTS_EXTRA_COLUMNS.keys()),
                    use_service_key=community_use_service_role(community_settings),
                    auth_token=community_auth_token(community_settings)
                )
                st.session_state.community_migration_results = {
                    "results": migration_results,
                    "checked_at": datetime.now().isoformat()
                }
            if st.session_state.community_migration_results:
                render_checklist_results(
                    st.session_state.community_migration_results["results"],
                    st.session_state.community_migration_results.get("checked_at")
                )
                st.session_state.community_column_support = {
                    col: ok for col, ok, _ in st.session_state.community_migration_results["results"]
                }
                missing = [
                    col for col, ok, err in st.session_state.community_migration_results["results"]
                    if not ok and is_supabase_missing_column_error(err)
                ]
                if missing:
                    st.info("Run this SQL in Supabase SQL Editor to add missing columns:")
                    migration_sql = build_community_migration_sql(missing)
                    st.code(migration_sql, language="sql")
                    st.download_button(
                        "Download migration SQL",
                        data=migration_sql,
                        file_name="community_posts_migration.sql"
                    )
                    st.caption("After running the SQL, refresh this page and re-run the column check.")
                else:
                    st.success("No missing columns detected.")
    # ==============================
# TAB 11: ADMIN
# ==============================
if admin_tab is not None:
    with admin_tab:
        st.subheader("Admin Console")
        st.caption("Admin metrics are local to this installation. No cross-device tracking is enabled.")

        meta = get_meta(db)
        users = list(iter_user_records(db))
        total_users = sum(1 for _, record in users if record.get("auth"))

        active_days = 7
        active_users = 0
        cutoff = datetime.now() - timedelta(days=active_days)
        for _, record in users:
            last_active = record.get("last_active")
            if not last_active:
                continue
            try:
                last_dt = datetime.fromisoformat(last_active)
            except Exception:
                continue
            if last_dt >= cutoff:
                active_users += 1

        st.markdown("### Usage Stats")
        stat_cols = st.columns(3)
        stat_cols[0].metric("Estimated Downloads (local)", total_users)
        stat_cols[1].metric(f"Active Users (last {active_days} days)", active_users)
        stat_cols[2].metric("Total Logins", int(meta.get("total_logins", 0)))
        st.caption("Downloads are estimated by local registrations; install counts are not tracked across devices.")
        install_seen = meta.get("install_first_seen")
        if install_seen:
            try:
                install_dt = datetime.fromisoformat(install_seen)
                st.caption(f"Local install first seen: {format_date_for_settings(install_dt, user_settings)}")
            except Exception:
                st.caption(f"Local install first seen: {install_seen}")

        st.markdown("### Revenue")
        revenue_value = st.number_input(
            "Total App Revenue (manual entry)",
            min_value=0.0,
            value=float(meta.get("revenue_total", 0.0)),
            step=100.0
        )
        if st.button("Save Revenue", width="stretch"):
            meta["revenue_total"] = float(revenue_value)
            save_data(db)
            st.success("Revenue updated.")
        st.write(f"Current Revenue: {format_currency(revenue_value, currency_symbol, currency_rate)}")

        st.markdown("### Feedback Forum")
        feedback_items = meta.get("feedback", [])
        feedback_filter = st.selectbox("Filter", ["All", "Open", "Resolved"], index=0)
        filtered_items = []
        for entry in feedback_items:
            status = entry.get("status", "Open")
            if feedback_filter == "All" or status == feedback_filter:
                filtered_items.append(entry)

        if not filtered_items:
            st.info("No feedback found for this filter.")
        else:
            for entry in filtered_items:
                if not entry.get("id"):
                    entry["id"] = secrets.token_hex(6)
                    save_data(db)
                entry_id = entry["id"]
                title = f"{entry.get('category', 'Feedback')} • {entry.get('subject', 'No subject')}"
                user_label = entry.get("user", "Unknown")
                with st.expander(f"{title} — {user_label}"):
                    st.write(entry.get("message", ""))
                    created_at = entry.get("created_at")
                    if created_at:
                        try:
                            created_dt = datetime.fromisoformat(created_at)
                            st.caption(f"Submitted {format_date_for_settings(created_dt, user_settings)}")
                        except Exception:
                            st.caption(f"Submitted {created_at}")
                    status_value = entry.get("status", "Open")
                    status_index = 0 if status_value == "Open" else 1
                    new_status = st.selectbox(
                        "Status",
                        ["Open", "Resolved"],
                        index=status_index,
                        key=f"fb_status_{entry_id}"
                    )
                    response_text = st.text_area(
                        "Admin Response",
                        value=entry.get("admin_response", ""),
                        key=f"fb_response_{entry_id}"
                    )
                    if st.button("Save Response", key=f"fb_save_{entry_id}"):
                        entry["status"] = new_status
                        entry["admin_response"] = response_text.strip()
                        save_data(db)
                        st.success("Feedback updated.")
                        st.rerun()

        st.markdown("### Password Reset Assistance")
        with st.form("admin_password_reset"):
            target_user = st.text_input("Target Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            admin_submit = st.form_submit_button("Reset User Password", width="stretch")

        if admin_submit:
            pw_error = True
            if not target_user:
                st.error("Enter a target username.")
            else:
                pw_error = validate_password_strength(new_password)
                if pw_error:
                    st.error(pw_error)
                else:
                    pw_error = False
            if not pw_error:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    record = ensure_user_record(db, target_user)
                    record["auth"] = make_password_record(new_password)
                    if "recovery" not in record:
                        record["recovery"] = []
                    save_data(db)
                    st.success("Password reset for user.")

        if st.button("Disable Admin Mode", width="stretch"):
            st.session_state.is_admin = False
            st.success("Admin mode disabled.")
            st.rerun()

# ==============================
# BULK DELETE CONFIRMATION MODAL
# ==============================
if "delete_confirmation" in st.session_state and st.session_state.delete_confirmation:
    st.markdown("""
        <div class="overlay active"></div>
        <div class="confirmation-modal active">
            <h3 style="color: var(--text); margin-bottom: 1rem;">Confirm Delete</h3>
            <p style="color: var(--muted); margin-bottom: 1.5rem;">
                Are you sure you want to delete this asset? This action cannot be undone.
            </p>
            <div class="modal-buttons">
                <button onclick="confirmDelete()" style="background: #ff6b6b; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 25px; cursor: pointer; font-weight: 600;">
                    Yes, Delete
                </button>
                <button onclick="cancelDelete()" style="background: #d1a843; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 25px; cursor: pointer; font-weight: 600;">
                    Cancel
                </button>
            </div>
        </div>
        <script>
            function confirmDelete() {
                // This would trigger the actual delete in Streamlit
                // For now, we'll just close the modal
                document.querySelector('.overlay').classList.remove('active');
                document.querySelector('.confirmation-modal').classList.remove('active');
            }
            function cancelDelete() {
                document.querySelector('.overlay').classList.remove('active');
                document.querySelector('.confirmation-modal').classList.remove('active');
            }
        </script>
    """, unsafe_allow_html=True)

render_footer()
