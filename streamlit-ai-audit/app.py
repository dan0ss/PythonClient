#!/usr/bin/env python3
"""
AI SERP Audit - Streamlit App

An all-in-one tool for auditing Google SERP results including:
- Organic search results
- AI Overviews
- Google AI Mode responses

Uses the DataForSEO API to fetch real-time search data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import asyncio
import aiohttp
import base64
import json
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

# ============================================================================
# Configuration
# ============================================================================

# Default API credentials (prefilled)
DEFAULT_USERNAME = "dan@perth-seo-agency.com.au"
DEFAULT_PASSWORD = "bf723abcdd2effb0"

# API Settings
API_BASE_URL = "https://api.dataforseo.com/v3"

# Default search configuration
DEFAULT_LOCATION_CODE = 9189292  # Australia
DEFAULT_LANGUAGE_CODE = "en"
DEFAULT_DEVICE = "desktop"
DEFAULT_OS = "macos"
DEFAULT_DEPTH = 20

# Performance tuning
MAX_CONCURRENT_REQUESTS = 20
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_DELAY_BASE = 1.0

# Location codes for common regions
LOCATIONS = {
    "Australia": 9189292,
    "United States": 2840,
    "United Kingdom": 2826,
    "Canada": 2124,
    "India": 2356,
    "Germany": 2276,
    "France": 2250,
    "Spain": 2724,
    "Italy": 2380,
    "Brazil": 2076,
    "Japan": 2392,
    "Singapore": 2702,
    "New Zealand": 2554,
}

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AI SERP Audit",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# Custom CSS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');
    
    :root {
        --accent-blue: #3b82f6;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --accent-orange: #f97316;
        --accent-cyan: #06b6d4;
        --accent-pink: #ec4899;
    }
    
    .stApp {
        font-family: 'Sora', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #fff 0%, #c7d2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.8;
        font-weight: 300;
    }
    
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        font-weight: 500;
    }
    
    .metric-blue .metric-value { color: var(--accent-blue); }
    .metric-purple .metric-value { color: var(--accent-purple); }
    .metric-green .metric-value { color: var(--accent-green); }
    .metric-orange .metric-value { color: var(--accent-orange); }
    .metric-cyan .metric-value { color: var(--accent-cyan); }
    .metric-pink .metric-value { color: var(--accent-pink); }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .section-header h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
    }
    
    .chart-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .sidebar-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .sidebar-header h2 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .status-running {
        background: linear-gradient(90deg, #fef3c7, #fde68a);
        color: #92400e;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
    }
    
    .status-success {
        background: linear-gradient(90deg, #d1fae5, #a7f3d0);
        color: #065f46;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
    }
    
    .status-error {
        background: linear-gradient(90deg, #fee2e2, #fecaca);
        color: #991b1b;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 0 16px;
        background: #f1f5f9;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Data Processing Classes
# ============================================================================

@dataclass
class ProcessingStats:
    """Track processing statistics."""
    total: int = 0
    completed: int = 0
    failed: int = 0
    ai_overview_rows: int = 0
    organic_rows: int = 0
    ai_mode_rows: int = 0


# ============================================================================
# Data Extraction Functions
# ============================================================================

def extract_ai_overview_rows(response_dict: Dict[str, Any], keyword_fallback: str) -> List[Dict[str, Any]]:
    """Extract AI Overview reference rows."""
    rows: List[Dict[str, Any]] = []

    tasks = response_dict.get("tasks") or []
    for task in tasks:
        task_data = task.get("data") or {}
        task_keyword = task_data.get("keyword") or keyword_fallback
        results = task.get("result") or []

        for result in results:
            result_keyword = result.get("keyword") or task_keyword
            items = result.get("items") or []

            for item in items:
                if item.get("type") != "ai_overview":
                    continue

                ai_markdown = item.get("markdown")

                for ref in item.get("references") or []:
                    rows.append({
                        "result_type": "ai_overview",
                        "keyword": result_keyword,
                        "domain": ref.get("domain"),
                        "references_source": ref.get("source") or ref.get("title"),
                        "references_url": ref.get("url"),
                        "references_text": ref.get("text"),
                        "references_markdown": ai_markdown or "",
                    })

                for sub_item in item.get("items") or []:
                    sub_markdown = sub_item.get("markdown") or ai_markdown or ""

                    for ref in sub_item.get("references") or []:
                        rows.append({
                            "result_type": "ai_overview",
                            "keyword": result_keyword,
                            "domain": ref.get("domain"),
                            "references_source": ref.get("source") or ref.get("title"),
                            "references_url": ref.get("url"),
                            "references_text": ref.get("text"),
                            "references_markdown": sub_markdown,
                        })

                    for component in sub_item.get("components") or []:
                        comp_markdown = component.get("markdown") or sub_markdown
                        for ref in component.get("references") or []:
                            rows.append({
                                "result_type": "ai_overview",
                                "keyword": result_keyword,
                                "domain": ref.get("domain"),
                                "references_source": ref.get("source") or ref.get("title"),
                                "references_url": ref.get("url"),
                                "references_text": ref.get("text"),
                                "references_markdown": comp_markdown or "",
                            })

    return rows


def extract_organic_rows(response_dict: Dict[str, Any], keyword_fallback: str) -> List[Dict[str, Any]]:
    """Extract organic result rows."""
    rows: List[Dict[str, Any]] = []

    tasks = response_dict.get("tasks") or []
    for task in tasks:
        task_data = task.get("data") or {}
        task_keyword = task_data.get("keyword") or keyword_fallback
        results = task.get("result") or []

        for result in results:
            result_keyword = result.get("keyword") or task_keyword
            items = result.get("items") or []

            for item in items:
                if item.get("type") != "organic":
                    continue

                rows.append({
                    "result_type": "organic",
                    "keyword": result_keyword,
                    "page": item.get("page"),
                    "rank_group": item.get("rank_group"),
                    "rank_absolute": item.get("rank_absolute"),
                    "position": item.get("position"),
                    "domain": item.get("domain"),
                    "url": item.get("url"),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "extended_snippet": item.get("extended_snippet"),
                    "breadcrumb": item.get("breadcrumb"),
                    "website_name": item.get("website_name"),
                })

    return rows


def extract_ai_mode_rows(response_dict: Dict[str, Any], keyword_fallback: str) -> List[Dict[str, Any]]:
    """Extract Google AI Mode rows."""
    rows: List[Dict[str, Any]] = []

    tasks = response_dict.get("tasks") or []
    for task in tasks:
        task_data = task.get("data") or {}
        task_keyword = task_data.get("keyword") or keyword_fallback
        results = task.get("result") or []

        for result in results:
            result_keyword = result.get("keyword") or task_keyword
            items = result.get("items") or []

            for item in items:
                item_type = item.get("type")
                if item_type != "ai_overview":
                    continue

                ai_markdown = item.get("markdown") or ""
                references = item.get("references") or []
                citations_count = len(references)

                primary_domain = ""
                primary_url = ""
                if references:
                    first_ref = references[0]
                    primary_domain = first_ref.get("domain") or ""
                    primary_url = first_ref.get("url") or ""

                rows.append({
                    "result_type": "ai_mode",
                    "keyword": result_keyword,
                    "ai_mode_summary": ai_markdown,
                    "ai_mode_citations_count": citations_count,
                    "ai_mode_primary_domain": primary_domain,
                    "ai_mode_primary_url": primary_url,
                    "domain": primary_domain,
                })

                for ref in references:
                    rows.append({
                        "result_type": "ai_mode",
                        "keyword": result_keyword,
                        "domain": ref.get("domain"),
                        "references_source": ref.get("source") or ref.get("title"),
                        "references_url": ref.get("url"),
                        "references_text": ref.get("text"),
                        "references_markdown": ai_markdown,
                    })

    return rows


# ============================================================================
# API Functions
# ============================================================================

async def fetch_serp_data(
    session: aiohttp.ClientSession,
    keyword: str,
    auth_header: str,
    semaphore: asyncio.Semaphore,
    location_code: int,
    language_code: str,
    device: str,
    os_type: str,
    depth: int,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch SERP data for a single keyword with retry logic."""
    url = f"{API_BASE_URL}/serp/google/organic/live/advanced"
    
    payload = [{
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
        "device": device,
        "os": os_type,
        "depth": depth,
        "load_async_ai_overview": True,
    }]
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return (keyword, data)
                    elif response.status == 429:
                        delay = RETRY_DELAY_BASE * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return (keyword, None)
                        
            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                return (keyword, None)
                
            except aiohttp.ClientError:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                return (keyword, None)
    
    return (keyword, None)


async def fetch_ai_mode_data(
    session: aiohttp.ClientSession,
    keyword: str,
    auth_header: str,
    semaphore: asyncio.Semaphore,
    location_code: int,
    language_code: str,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Fetch Google AI Mode data for a single keyword."""
    url = f"{API_BASE_URL}/serp/google/ai_mode/live/advanced"
    
    payload = [{
        "keyword": keyword,
        "location_code": location_code,
        "language_code": language_code,
    }]
    
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    
    async with semaphore:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return (keyword, data)
                    elif response.status == 429:
                        delay = RETRY_DELAY_BASE * (2 ** attempt)
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return (keyword, None)
                        
            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                return (keyword, None)
                
            except aiohttp.ClientError:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                return (keyword, None)
    
    return (keyword, None)


async def process_keywords_async(
    keywords: List[str],
    username: str,
    password: str,
    location_code: int,
    language_code: str,
    device: str,
    os_type: str,
    depth: int,
    fetch_ai_mode: bool,
    progress_callback,
) -> List[Dict[str, Any]]:
    """Process all keywords concurrently."""
    credentials = f"{username}:{password}"
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    connector = aiohttp.TCPConnector(
        limit=MAX_CONCURRENT_REQUESTS,
        limit_per_host=MAX_CONCURRENT_REQUESTS,
        keepalive_timeout=30,
        enable_cleanup_closed=True,
    )
    
    all_rows: List[Dict[str, Any]] = []
    completed = 0
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for keyword in keywords:
            # Fetch SERP data
            _, serp_response = await fetch_serp_data(
                session, keyword, auth_header, semaphore,
                location_code, language_code, device, os_type, depth
            )
            
            if serp_response:
                ai_overview_rows = extract_ai_overview_rows(serp_response, keyword)
                organic_rows = extract_organic_rows(serp_response, keyword)
                all_rows.extend(ai_overview_rows)
                all_rows.extend(organic_rows)
                
                # Fetch AI Mode data if enabled
                if fetch_ai_mode:
                    _, ai_mode_response = await fetch_ai_mode_data(
                        session, keyword, auth_header, semaphore,
                        location_code, language_code
                    )
                    if ai_mode_response:
                        ai_mode_rows = extract_ai_mode_rows(ai_mode_response, keyword)
                        all_rows.extend(ai_mode_rows)
            
            completed += 1
            progress_callback(completed / len(keywords), f"Processing: {keyword}")
    
    return all_rows


def run_audit(keywords, username, password, location_code, language_code, device, os_type, depth, fetch_ai_mode, progress_callback):
    """Run the SERP audit."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(
            process_keywords_async(
                keywords, username, password, location_code, language_code,
                device, os_type, depth, fetch_ai_mode, progress_callback
            )
        )
        return results
    finally:
        loop.close()


# ============================================================================
# Visualization Functions
# ============================================================================

def create_domain_chart(df: pd.DataFrame) -> go.Figure:
    """Create top domains horizontal bar chart."""
    domain_counts = df['domain'].value_counts().head(10)
    
    colors = ['#3b82f6', '#8b5cf6', '#f97316', '#10b981', '#06b6d4',
              '#ec4899', '#3b82f6', '#8b5cf6', '#f97316', '#10b981']
    
    fig = go.Figure(go.Bar(
        x=domain_counts.values,
        y=[d.replace('www.', '') for d in domain_counts.index],
        orientation='h',
        marker_color=colors[:len(domain_counts)],
    ))
    
    fig.update_layout(
        title=dict(text='Top Domains', font=dict(size=14, family='Sora')),
        xaxis_title='Count',
        yaxis_title='',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Sora', size=11),
        yaxis=dict(autorange='reversed'),
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=False)
    
    return fig


def create_result_types_chart(df: pd.DataFrame) -> go.Figure:
    """Create result types donut chart."""
    type_counts = df['result_type'].value_counts()
    
    colors = {
        'organic': '#10b981',
        'ai_overview': '#8b5cf6',
        'ai_mode': '#06b6d4',
    }
    
    fig = go.Figure(go.Pie(
        values=type_counts.values,
        labels=[t.replace('_', ' ').title() for t in type_counts.index],
        hole=0.65,
        marker_colors=[colors.get(t, '#6b7280') for t in type_counts.index],
    ))
    
    fig.update_layout(
        title=dict(text='Result Types', font=dict(size=14, family='Sora')),
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Sora', size=11),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
    )
    
    return fig


def create_rank_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create rank distribution bar chart."""
    organic = df[df['result_type'] == 'organic'].copy()
    
    if organic.empty or 'rank_group' not in organic.columns:
        fig = go.Figure()
        fig.update_layout(
            title='Rank Distribution',
            annotations=[dict(text='No organic results', showarrow=False)]
        )
        return fig
    
    organic['rank_range'] = pd.cut(
        organic['rank_group'],
        bins=[0, 3, 6, 10, 15, 100],
        labels=['1-3', '4-6', '7-10', '11-15', '15+']
    )
    
    rank_counts = organic['rank_range'].value_counts().reindex(['1-3', '4-6', '7-10', '11-15', '15+']).fillna(0)
    
    colors = ['#10b981', '#3b82f6', '#8b5cf6', '#f97316', '#6b7280']
    
    fig = go.Figure(go.Bar(
        x=rank_counts.index,
        y=rank_counts.values,
        marker_color=colors,
    ))
    
    fig.update_layout(
        title=dict(text='Rank Distribution (Organic)', font=dict(size=14, family='Sora')),
        xaxis_title='Rank Range',
        yaxis_title='Count',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Sora', size=11),
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    
    return fig


def create_keywords_chart(df: pd.DataFrame) -> go.Figure:
    """Create keyword presence chart."""
    keyword_counts = df.groupby(['keyword', 'result_type']).size().unstack(fill_value=0)
    keyword_counts['total'] = keyword_counts.sum(axis=1)
    keyword_counts = keyword_counts.sort_values('total', ascending=False).head(15)
    
    fig = go.Figure()
    
    colors = {
        'organic': '#10b981',
        'ai_overview': '#8b5cf6',
        'ai_mode': '#06b6d4',
    }
    
    for result_type in ['organic', 'ai_overview', 'ai_mode']:
        if result_type in keyword_counts.columns:
            fig.add_trace(go.Bar(
                name=result_type.replace('_', ' ').title(),
                x=keyword_counts.index,
                y=keyword_counts[result_type],
                marker_color=colors.get(result_type, '#6b7280'),
            ))
    
    fig.update_layout(
        title=dict(text='Results by Keyword', font=dict(size=14, family='Sora')),
        barmode='stack',
        xaxis_title='',
        yaxis_title='Count',
        height=400,
        margin=dict(l=20, r=20, t=40, b=80),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Sora', size=11),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
    )
    
    fig.update_xaxes(showgrid=False, tickangle=45)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f1f5f9')
    
    return fig


# ============================================================================
# Main App
# ============================================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 AI SERP Audit</h1>
        <p>Analyze Google search results including AI Overviews and AI Mode responses</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>⚙️ Configuration</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # API Credentials
        st.subheader("🔑 API Credentials")
        username = st.text_input(
            "DataForSEO Username",
            value=DEFAULT_USERNAME,
            type="default",
            help="Your DataForSEO account email"
        )
        password = st.text_input(
            "DataForSEO Password",
            value=DEFAULT_PASSWORD,
            type="password",
            help="Your DataForSEO API password"
        )
        
        st.divider()
        
        # Search Configuration
        st.subheader("🌍 Search Settings")
        
        location = st.selectbox(
            "Location",
            options=list(LOCATIONS.keys()),
            index=0,
            help="Target location for search results"
        )
        location_code = LOCATIONS[location]
        
        language_code = st.selectbox(
            "Language",
            options=["en", "es", "fr", "de", "it", "pt", "ja", "zh"],
            index=0,
            help="Language for search results"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            device = st.selectbox(
                "Device",
                options=["desktop", "mobile"],
                index=0
            )
        with col2:
            os_type = st.selectbox(
                "OS",
                options=["macos", "windows", "android", "ios"],
                index=0
            )
        
        depth = st.slider(
            "Results Depth",
            min_value=10,
            max_value=100,
            value=DEFAULT_DEPTH,
            step=10,
            help="Number of organic results to fetch"
        )
        
        fetch_ai_mode = st.checkbox(
            "Include Google AI Mode",
            value=True,
            help="Fetch Google AI Mode responses (additional API calls)"
        )
        
        st.divider()
        
        # Keywords Input
        st.subheader("🔤 Keywords")
        keywords_text = st.text_area(
            "Enter keywords (one per line)",
            height=150,
            placeholder="dampier things to do\nthings to do in perth australia\nbest restaurants sydney",
            help="Enter the keywords you want to analyze"
        )
        
        # Process keywords
        keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]
        
        if keywords:
            st.info(f"📊 {len(keywords)} keyword(s) ready")
        
        st.divider()
        
        # Run button
        run_button = st.button(
            "🚀 Run Audit",
            type="primary",
            use_container_width=True,
            disabled=not keywords or not username or not password
        )
    
    # Main content area
    if run_button and keywords:
        st.session_state.processing = True
        
        # Progress container
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress, text):
            progress_bar.progress(progress)
            status_text.text(text)
        
        with st.spinner("Processing keywords..."):
            try:
                results = run_audit(
                    keywords=keywords,
                    username=username,
                    password=password,
                    location_code=location_code,
                    language_code=language_code,
                    device=device,
                    os_type=os_type,
                    depth=depth,
                    fetch_ai_mode=fetch_ai_mode,
                    progress_callback=update_progress
                )
                
                st.session_state.results = results
                progress_bar.empty()
                status_text.empty()
                
                st.success(f"✅ Audit complete! Found {len(results)} results.")
                
            except Exception as e:
                st.error(f"❌ Error during audit: {str(e)}")
                st.session_state.results = None
        
        st.session_state.processing = False
    
    # Display results
    if st.session_state.results:
        df = pd.DataFrame(st.session_state.results)
        
        # Summary metrics
        st.markdown("### 📊 Overview")
        
        cols = st.columns(7)
        
        metrics = [
            ("Total Records", len(df), "blue"),
            ("Keywords", df['keyword'].nunique(), "purple"),
            ("Domains", df['domain'].nunique(), "blue"),
            ("AI Overviews", len(df[df['result_type'] == 'ai_overview']), "purple"),
            ("Organic", len(df[df['result_type'] == 'organic']), "green"),
            ("AI Mode", len(df[df['result_type'] == 'ai_mode']), "cyan"),
            ("Avg. Rank", f"{df[df['result_type'] == 'organic']['rank_group'].mean():.1f}" if 'rank_group' in df.columns else "N/A", "orange"),
        ]
        
        for col, (label, value, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card metric-{color}">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        st.markdown("### 📈 Analytics")
        
        chart_cols = st.columns([1.5, 1, 1])
        
        with chart_cols[0]:
            st.plotly_chart(create_domain_chart(df), use_container_width=True)
        
        with chart_cols[1]:
            st.plotly_chart(create_result_types_chart(df), use_container_width=True)
        
        with chart_cols[2]:
            st.plotly_chart(create_rank_distribution_chart(df), use_container_width=True)
        
        # Keywords breakdown chart
        st.plotly_chart(create_keywords_chart(df), use_container_width=True)
        
        # Data tables
        st.markdown("### 📋 Detailed Results")
        
        tabs = st.tabs(["🟣 AI Overviews", "🟢 Organic Results", "🔵 AI Mode", "📥 Download"])
        
        # AI Overviews tab
        with tabs[0]:
            ai_overview_df = df[df['result_type'] == 'ai_overview']
            if not ai_overview_df.empty:
                st.dataframe(
                    ai_overview_df[['keyword', 'domain', 'references_source', 'references_text', 'references_url']],
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("No AI Overview results found")
        
        # Organic tab
        with tabs[1]:
            organic_df = df[df['result_type'] == 'organic']
            if not organic_df.empty:
                st.dataframe(
                    organic_df[['keyword', 'rank_group', 'page', 'domain', 'title', 'description', 'url']],
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("No organic results found")
        
        # AI Mode tab
        with tabs[2]:
            ai_mode_df = df[df['result_type'] == 'ai_mode']
            if not ai_mode_df.empty:
                display_cols = ['keyword', 'domain']
                if 'ai_mode_summary' in ai_mode_df.columns:
                    display_cols.append('ai_mode_summary')
                if 'ai_mode_citations_count' in ai_mode_df.columns:
                    display_cols.append('ai_mode_citations_count')
                if 'references_url' in ai_mode_df.columns:
                    display_cols.append('references_url')
                
                st.dataframe(
                    ai_mode_df[display_cols],
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("No AI Mode results found")
        
        # Download tab
        with tabs[3]:
            st.markdown("#### Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"serp_audit_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name=f"serp_audit_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    else:
        # Empty state
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; color: #64748b;">
            <h2 style="font-size: 2rem; margin-bottom: 1rem;">👋 Welcome to AI SERP Audit</h2>
            <p style="font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
                Enter your keywords in the sidebar and click <strong>Run Audit</strong> to analyze 
                Google search results including AI Overviews and AI Mode responses.
            </p>
            <div style="margin-top: 2rem; padding: 1.5rem; background: #f1f5f9; border-radius: 12px; display: inline-block;">
                <p style="margin: 0; font-size: 0.9rem;">
                    💡 <strong>Tip:</strong> Make sure your DataForSEO credentials are configured correctly.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

