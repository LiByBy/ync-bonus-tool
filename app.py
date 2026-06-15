from __future__ import annotations

from datetime import datetime
from io import BytesIO
from typing import Dict, List, Tuple

import numpy as np
import altair as alt
import pandas as pd
import streamlit as st


YNC_COLORS = {
    "primary": "#B11226",
    "primary_dark": "#7F0D1B",
    "primary_light": "#F3D7DC",
    "secondary": "#C87A83",
    "accent": "#D9A441",
    "contrast": "#50606F",
    "positive": "#5E8C61",
    "negative": "#B11226",
    "background": "#F7F4F3",
    "surface": "rgba(255, 255, 255, 0.76)",
    "surface_strong": "rgba(255, 255, 255, 0.92)",
    "text": "#1F2933",
    "muted_text": "#6B7280",
    "border": "rgba(177, 18, 38, 0.14)",
    "shadow": "0 10px 30px rgba(65, 18, 24, 0.08)",
}

VALID_RATINGS = ["A", "B+", "B", "C+", "C", "D", "E"]
VALID_JOB_FAMILIES = ["综合职（非销售）", "综合职（销售）", "现场职", "技术职"]
VALID_QUALIFICATIONS = ["理事级", "经营级", "基干级", "指导级", "担当级"]
VALID_NEW_JOB_FAMILIES = ["M", "T", "S", "O", "G"]
REQUIRED_COLUMNS = [
    "employee_id",
    "employee_name",
    "original_job_family",
    "original_qualification",
    "new_job_family",
    "new_grade",
    "rating",
    "bonus_base",
    "eligible",
]
EMPLOYEE_COLUMNS = [
    "employee_id",
    "employee_name",
    "department",
    "original_job_family",
    "original_qualification",
    "new_job_family",
    "new_grade",
    "rating",
    "bonus_base",
    "proration_factor",
    "eligible",
    "remarks",
]
MONEY_COLUMNS = ["before_bonus", "option_a_bonus", "option_b_bonus", "option_a_change_amount", "option_b_change_amount"]
PCT_COLUMNS = ["option_a_change_pct", "option_b_change_pct"]
COEFF_COLUMNS = ["before_coefficient", "option_a_coefficient", "option_b_coefficient", "coefficient"]
COUNT_COLUMNS = ["headcount", "count", "employee_count"]
SCENARIO_LABELS = {"Before": "现行方案", "Option A": "方案A", "Option B": "方案B"}
SCENARIO_COLORS = {
    "现行方案": "#6B7280",
    "方案A": "#B11226",
    "方案B": "#C87A83",
    "positive": "#5E8C61",
    "negative": "#B11226",
}
FAMILY_COLORS = {"M": "#7F0D1B", "T": "#B11226", "S": "#C87A83", "O": "#D9A441", "G": "#50606F"}
COLUMN_LABELS = {
    "employee_id": "员工编号",
    "employee_name": "姓名",
    "department": "部门",
    "original_job_family": "原职群",
    "original_qualification": "原能力资格",
    "new_job_family": "新职群",
    "new_job_family_name": "新职群名称",
    "new_grade": "新等级",
    "grade_order": "等级序号",
    "coefficient_group": "系数组",
    "rating": "评价等级",
    "bonus_base": "月度奖金基数",
    "proration_factor": "折算系数",
    "eligible": "是否参与测算",
    "remarks": "备注",
    "scenario": "方案",
    "coefficient": "系数",
    "before_coefficient": "现行方案系数",
    "option_a_coefficient": "方案A系数",
    "option_b_coefficient": "方案B系数",
    "before_bonus": "现行方案奖金",
    "option_a_bonus": "方案A奖金",
    "option_b_bonus": "方案B奖金",
    "option_a_change_amount": "方案A较现行变化额",
    "option_a_change_pct": "方案A较现行变化率",
    "option_b_change_amount": "方案B较现行变化额",
    "option_b_change_pct": "方案B较现行变化率",
    "structure_status": "数据状态",
    "structure_note": "检查说明",
    "issue_type": "异常类型",
    "issue_detail": "异常说明",
    "severity": "严重程度",
    "headcount": "人数",
    "count": "数量",
    "total_bonus": "奖金总额",
    "average_bonus": "人均奖金",
    "max_bonus": "最高奖金",
    "min_bonus": "最低奖金",
    "Before": "现行方案",
    "Option A": "方案A",
    "Option B": "方案B",
}
FIELD_ALIASES = {
    "员工编号": "employee_id",
    "姓名": "employee_name",
    "部门": "department",
    "原职群": "original_job_family",
    "原能力资格": "original_qualification",
    "新职群": "new_job_family",
    "新等级": "new_grade",
    "评价等级": "rating",
    "奖金基数": "bonus_base",
    "月度奖金基数": "bonus_base",
    "月奖金基数": "bonus_base",
    "折算系数": "proration_factor",
    "是否参与测算": "eligible",
    "备注": "remarks",
}


st.set_page_config(
    page_title="YNC 奖金系数方案测算工具",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_custom_css() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --ync-red: {YNC_COLORS["primary"]};
            --ync-red-dark: {YNC_COLORS["primary_dark"]};
            --ync-rose: {YNC_COLORS["secondary"]};
            --ync-gold: {YNC_COLORS["accent"]};
            --ync-bg: {YNC_COLORS["background"]};
            --ync-text: {YNC_COLORS["text"]};
            --ync-muted: {YNC_COLORS["muted_text"]};
            --ync-border: {YNC_COLORS["border"]};
            --ync-shadow: {YNC_COLORS["shadow"]};
        }}
        html, body, [class*="css"], .stApp {{
            font-family: "Inter", "Noto Sans SC", "Microsoft YaHei UI", sans-serif;
            color: {YNC_COLORS["text"]};
            font-weight: 300;
        }}
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(177,18,38,0.08), transparent 32%),
                linear-gradient(135deg, #F7F4F3 0%, #FFFFFF 52%, #F4EEF0 100%);
        }}
        h1, h2, h3 {{
            font-weight: 400;
            letter-spacing: 0;
        }}
        .block-container {{
            padding-top: 1.75rem;
            padding-bottom: 3rem;
            max-width: 1420px;
        }}
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }}
        .stApp > header {{
            display: none !important;
        }}
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {{
            display: none !important;
            visibility: hidden !important;
        }}
        section[data-testid="stSidebar"] {{
            width: 0 !important;
            min-width: 0 !important;
        }}
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}
        /*
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] label {{
            color: var(--ync-text);
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label {{
            border-radius: 12px;
            padding: 8px 10px;
            margin: 3px 0;
            border: 1px solid transparent;
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background: rgba(177,18,38,0.06);
            border-color: rgba(177,18,38,0.12);
        }}
        [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
            background: rgba(177,18,38,0.10);
            border-left: 4px solid var(--ync-red);
            color: var(--ync-red-dark);
        }}
        */
        .top-nav-card {{
            background: rgba(255,255,255,0.82);
            border: 1px solid var(--ync-border);
            box-shadow: 0 8px 22px rgba(65,18,24,0.055);
            backdrop-filter: blur(14px);
            border-radius: 16px;
            padding: 10px;
            margin: -6px 0 18px 0;
        }}
        .top-nav-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}
        .nav-button {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            border-radius: 12px;
            padding: 9px 13px;
            border: 1px solid rgba(177,18,38,0.12);
            background: rgba(255,255,255,0.62);
            color: var(--ync-text) !important;
            text-decoration: none !important;
            font-size: 14px;
            font-weight: 500;
            line-height: 1;
            min-height: 38px;
            box-sizing: border-box;
        }}
        .nav-button:hover {{
            background: rgba(177,18,38,0.06);
            border-color: rgba(177,18,38,0.12);
        }}
        .nav-button.active {{
            background: rgba(177,18,38,0.10);
            border-color: rgba(177,18,38,0.18);
            color: var(--ync-red-dark);
            box-shadow: inset 0 -3px 0 var(--ync-red);
        }}
        .brand-bar {{
            background: rgba(255,255,255,0.84);
            border: 1px solid var(--ync-border);
            box-shadow: var(--ync-shadow);
            backdrop-filter: blur(14px);
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 18px;
            width: 100%;
            box-sizing: border-box;
            display: grid;
            grid-template-columns: minmax(360px, 1fr) minmax(0, 680px);
            gap: 18px;
            align-items: start;
        }}
        .brand-title {{
            font-size: 24px;
            font-weight: 500;
            color: var(--ync-red-dark);
            line-height: 1.25;
        }}
        .brand-subtitle {{
            font-size: 13px;
            color: var(--ync-muted);
            margin-top: 4px;
        }}
        .status-pill-wrap {{
            display: grid;
            grid-template-columns: repeat(4, max-content);
            justify-content: end;
            gap: 8px;
            min-width: 0;
            max-width: 680px;
        }}
        .status-pill {{
            background: rgba(177,18,38,0.06);
            border: 1px solid rgba(177,18,38,0.12);
            color: var(--ync-text);
            border-radius: 999px;
            padding: 7px 11px;
            font-size: clamp(10px, 0.72vw, 12px);
            white-space: nowrap;
            line-height: 1.2;
        }}
        @media (max-width: 1200px) {{
            .brand-bar {{
                grid-template-columns: 1fr;
            }}
            .status-pill-wrap {{
                display: flex;
                flex-wrap: wrap;
                justify-content: flex-start;
                max-width: none;
            }}
        }}
        .glass-card {{
            background: {YNC_COLORS["surface"]};
            border: 1px solid var(--ync-border);
            box-shadow: var(--ync-shadow);
            backdrop-filter: blur(14px);
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 16px;
        }}
        .metric-card {{
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(177,18,38,0.12);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 8px 22px rgba(65,18,24,0.06);
            height: 164px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
        }}
        .metric-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .metric-icon {{
            width: 32px;
            height: 32px;
            border-radius: 10px;
            background: rgba(177,18,38,0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
        }}
        .metric-label {{
            color: {YNC_COLORS["muted_text"]};
            font-size: clamp(0.72rem, 0.72vw, 0.86rem);
            line-height: 1.25;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .metric-value {{
            color: {YNC_COLORS["text"]};
            font-size: clamp(1.18rem, 1.75vw, 1.58rem);
            font-weight: 500;
            line-height: 1.25;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: clip;
        }}
        .metric-delta {{
            color: {YNC_COLORS["primary"]};
            font-size: 0.86rem;
            margin-top: 6px;
        }}
        .chart-note {{
            color: var(--ync-muted);
            font-size: 13px;
            margin: -4px 0 10px 0;
        }}
        .chart-analysis {{
            color: var(--ync-text);
            font-size: 13px;
            line-height: 1.55;
            background: rgba(177,18,38,0.045);
            border: 1px solid rgba(177,18,38,0.10);
            border-radius: 12px;
            padding: 10px 12px;
            margin-top: 10px;
        }}
        .section-title {{
            font-size: 22px;
            font-weight: 500;
            color: var(--ync-text);
            margin: 10px 0 6px;
        }}
        .section-subtitle {{
            font-size: 13px;
            color: var(--ync-muted);
            margin-bottom: 18px;
        }}
        .empty-state {{
            background: rgba(255,255,255,0.78);
            border: 1px dashed rgba(177,18,38,0.24);
            border-radius: 18px;
            padding: 28px;
            text-align: center;
            color: var(--ync-muted);
        }}
        .stButton > button, .stDownloadButton > button {{
            background: {YNC_COLORS["primary"]};
            color: white;
            border: 1px solid {YNC_COLORS["primary"]};
            border-radius: 11px;
            font-weight: 400;
            box-shadow: 0 6px 14px rgba(177,18,38,0.14);
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background: {YNC_COLORS["primary_dark"]};
            color: white;
            border-color: {YNC_COLORS["primary_dark"]};
        }}
        [data-testid="stDataFrame"], [data-testid="stDataEditor"] {{
            border: 1px solid rgba(177,18,38,0.12);
            border-radius: 12px;
            overflow: hidden;
        }}
        [data-testid="stElementToolbar"] {{
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: rgba(255, 255, 255, 0.70);
            border-radius: 8px 8px 0 0;
            border: 1px solid rgba(177,18,38,0.12);
            padding: 10px 14px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_card(html: str) -> None:
    st.markdown(f'<div class="glass-card">{html}</div>', unsafe_allow_html=True)


def svg_icon(name: str, size: int = 20, color: str | None = None) -> str:
    stroke = color or YNC_COLORS["primary"]
    icons = {
        "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9.5 21v-6h5v6"/>',
        "download": '<path d="M12 3v11"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
        "upload": '<path d="M12 21V10"/><path d="m7 14 5-5 5 5"/><path d="M5 3h14"/>',
        "check": '<path d="M20 6 9 17l-5-5"/><path d="M4 4h16v16H4z"/>',
        "settings": '<path d="M12 8.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Z"/><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.04.04-2 3.46-.06-.02a1.7 1.7 0 0 0-1.96.36 1.7 1.7 0 0 0-.44 1.28H8.68a1.7 1.7 0 0 0-.44-1.28 1.7 1.7 0 0 0-1.96-.36l-.06.02-2-3.46.04-.04A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.1-1.52V10.5A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.88l-.04-.04 2-3.46.06.02A1.7 1.7 0 0 0 8.24 3.3 1.7 1.7 0 0 0 8.68 2h6.64a1.7 1.7 0 0 0 .44 1.3 1.7 1.7 0 0 0 1.96.34l.06-.02 2 3.46-.04.04A1.7 1.7 0 0 0 19.4 9a1.7 1.7 0 0 0 1.1 1.5v2.98A1.7 1.7 0 0 0 19.4 15Z"/>',
        "chart": '<path d="M4 19V5"/><path d="M4 19h16"/><path d="M8 16V9"/><path d="M12 16V6"/><path d="M16 16v-4"/>',
        "table": '<path d="M4 5h16v14H4z"/><path d="M4 10h16"/><path d="M10 5v14"/>',
        "package": '<path d="M21 8.5 12 3 3 8.5l9 5.5 9-5.5Z"/><path d="M3 8.5v7L12 21l9-5.5v-7"/><path d="M12 14v7"/>',
        "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><path d="M9.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/><path d="M22 21v-2a4 4 0 0 0-3-3.86"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "yen": '<path d="m6 3 6 8 6-8"/><path d="M12 11v10"/><path d="M8 13h8"/><path d="M8 17h8"/>',
        "trend-up": '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
        "trend-down": '<path d="m3 7 6 6 4-4 8 8"/><path d="M15 17h6v-6"/>',
        "alert": '<path d="M12 9v4"/><path d="M12 17h.01"/><path d="M10.3 3.9 2.7 17.1A2 2 0 0 0 4.4 20h15.2a2 2 0 0 0 1.7-2.9L13.7 3.9a2 2 0 0 0-3.4 0Z"/>',
    }
    body = icons.get(name, icons["chart"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'


def icon_title(icon: str, title: str) -> str:
    return f'<span style="display:inline-flex;align-items:center;gap:10px;">{svg_icon(icon, 22)}<span>{title}</span></span>'


def metric_card(label: str, value: str, delta: str | None = None, icon: str = "chart", delta_color: str | None = None) -> None:
    color_style = f' style="color:{delta_color}"' if delta_color else ""
    delta_html = f'<div class="metric-delta"{color_style}>{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-top">
                <div class="metric-label">{label}</div>
                <div class="metric-icon">{svg_icon(icon, 18)}</div>
            </div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_status_summary() -> Dict[str, str]:
    employee_count = len(st.session_state.get("employee_df", pd.DataFrame()))
    issues = st.session_state.get("results", {}).get("issues", pd.DataFrame())
    issue_count = len(issues) if isinstance(issues, pd.DataFrame) else 0
    uploaded = st.session_state.get("has_uploaded_data", False)
    status = "已上传" if uploaded else "未上传（示例数据）"
    calc_time = st.session_state.get("last_calc_time", "尚未测算")
    return {
        "status": status,
        "employee_count": f"{employee_count:,}",
        "issue_count": f"{issue_count:,}",
        "calc_time": calc_time,
    }


def render_brand_bar() -> None:
    status = get_status_summary()
    st.markdown(
        f"""
        <div class="brand-bar">
            <div>
                <div class="brand-title">YNC 奖金系数方案测算工具</div>
                <div class="brand-subtitle">Bonus Coefficient Scenario Analyzer</div>
            </div>
            <div class="status-pill-wrap">
                <div class="status-pill">数据状态：{status["status"]}</div>
                <div class="status-pill">员工数量：{status["employee_count"]}</div>
                <div class="status-pill">异常数量：{status["issue_count"]}</div>
                <div class="status-pill">当前测算：{status["calc_time"]}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def cn_label(column: str) -> str:
    return COLUMN_LABELS.get(column, column)


def rename_columns_cn(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.copy()
    renamed = renamed.rename(columns={col: cn_label(col) for col in renamed.columns})
    if "方案" in renamed.columns:
        renamed["方案"] = renamed["方案"].replace(SCENARIO_LABELS)
    return renamed


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    reverse_labels = {label: key for key, label in COLUMN_LABELS.items()}
    reverse_labels.update(FIELD_ALIASES)
    normalized = df.copy()
    normalized.columns = [reverse_labels.get(str(col).strip(), str(col).strip()) for col in normalized.columns]
    if normalized.columns.duplicated().any():
        merged = pd.DataFrame(index=normalized.index)
        for col in dict.fromkeys(normalized.columns):
            same_name = normalized.loc[:, normalized.columns == col]
            merged[col] = same_name.bfill(axis=1).iloc[:, 0]
        normalized = merged
    return normalized


def normalize_uploaded_columns(df: pd.DataFrame) -> pd.DataFrame:
    return normalize_columns(df)


def format_scalar(value, kind: str = "text") -> str:
    if pd.isna(value):
        return "N/A"
    if kind == "count":
        return f"{int(value):,}"
    if kind == "money":
        return f"{float(value):,.0f}"
    if kind == "pct":
        return f"{float(value):.1%}"
    if kind == "coeff":
        return f"{float(value):.2f}"
    return str(value)


def display_table_cn(df: pd.DataFrame, height: int | None = None) -> None:
    display_df = rename_columns_cn(df)
    fmt = {}
    change_labels = []
    for original_col in df.columns:
        label = cn_label(original_col)
        if original_col in COUNT_COLUMNS or "人数" in label or "数量" in label:
            fmt[label] = "{:,.0f}"
        elif original_col in MONEY_COLUMNS or original_col == "bonus_base" or original_col.endswith("_bonus") or original_col.endswith("_amount"):
            fmt[label] = "{:,.0f}"
            if original_col.endswith("_amount"):
                change_labels.append(label)
        elif original_col in PCT_COLUMNS or original_col.endswith("_pct") or "变化率" in label:
            fmt[label] = "{:.1%}"
        elif original_col in COEFF_COLUMNS or original_col.endswith("_coefficient"):
            fmt[label] = "{:.2f}"
    kwargs = {"use_container_width": True, "hide_index": True}
    if height is not None:
        kwargs["height"] = height
    styler = display_df.style.format(fmt, na_rep="")
    for label in change_labels:
        if label in display_df.columns:
            styler = styler.map(
                lambda value: (
                    f"color: {YNC_COLORS['positive']}; background-color: rgba(94,140,97,0.08)"
                    if pd.notna(value) and value > 0
                    else f"color: {YNC_COLORS['negative']}; background-color: rgba(177,18,38,0.07)"
                    if pd.notna(value) and value < 0
                    else "color: #6B7280"
                ),
                subset=[label],
            )
    st.dataframe(styler, **kwargs)


def format_overall_summary_cn(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        metric = row["指标"]
        if metric == "参与人数":
            kind = "count"
        elif metric == "较 Before 变化率":
            kind = "pct"
            metric = "较现行方案变化率"
        elif metric == "较 Before 变化额":
            kind = "money"
            metric = "较现行方案变化额"
        else:
            kind = "money" if metric != "参与人数" else "count"
        rows.append(
            {
                "指标": metric,
                "现行方案": "" if pd.isna(row["Before"]) else format_scalar(row["Before"], kind),
                "方案A": "" if pd.isna(row["Option A"]) else format_scalar(row["Option A"], kind),
                "方案B": "" if pd.isna(row["Option B"]) else format_scalar(row["Option B"], kind),
            }
        )
    return pd.DataFrame(rows)


def chart_base(chart: alt.Chart, title: str) -> alt.Chart:
    return chart.properties(
        title=title,
        height=320,
        usermeta={"embedOptions": {"actions": False}},
    ).configure_title(
        font="Inter, Noto Sans SC, Microsoft YaHei UI, sans-serif",
        fontSize=16,
        fontWeight=500,
        color=YNC_COLORS["text"],
        anchor="start",
    ).configure_axis(
        labelFont="Inter, Noto Sans SC, Microsoft YaHei UI, sans-serif",
        titleFont="Inter, Noto Sans SC, Microsoft YaHei UI, sans-serif",
        gridColor="#EEE7E8",
        domainColor="#D8CDD0",
        tickColor="#D8CDD0",
        labelColor=YNC_COLORS["text"],
        titleColor=YNC_COLORS["muted_text"],
    ).configure_legend(
        labelFont="Inter, Noto Sans SC, Microsoft YaHei UI, sans-serif",
        titleFont="Inter, Noto Sans SC, Microsoft YaHei UI, sans-serif",
        orient="top",
    ).configure_view(
        stroke="#E8DCDD",
    )


def chart_note(text: str) -> None:
    st.markdown(f'<div class="chart-note">{text}</div>', unsafe_allow_html=True)


def chart_analysis(text: str) -> None:
    st.markdown(f'<div class="chart-analysis">{text}</div>', unsafe_allow_html=True)


def total_cost_insight(calc_df: pd.DataFrame) -> str:
    data = create_total_cost_chart_data(calc_df).set_index("方案")["总奖金成本"]
    before = data.get("现行方案", np.nan)
    option_a = data.get("方案A", np.nan)
    option_b = data.get("方案B", np.nan)
    a_pct = safe_pct(option_a - before, before)
    b_pct = safe_pct(option_b - before, before)
    return f"方案A较现行方案变化 {format_pct(a_pct)}，方案B较现行方案变化 {format_pct(b_pct)}。可优先关注总成本变化与预算约束的匹配程度。"


def new_family_insight(calc_df: pd.DataFrame) -> str:
    df = create_new_job_family_summary(calc_df).copy()
    if df.empty:
        return "暂无可分析的新职群数据。"
    df["max_abs_change"] = df[["option_a_change_amount", "option_b_change_amount"]].abs().max(axis=1)
    row = df.sort_values("max_abs_change", ascending=False).iloc[0]
    family = f"{row['new_job_family']} {row['new_job_family_name']}"
    return f"{family} 的成本变化幅度相对更高，建议结合职群定位和人员结构进一步解释差异来源。"


def rating_insight(calc_df: pd.DataFrame) -> str:
    data = create_rating_average_chart_data(calc_df)
    spread = data.groupby("方案")["人均奖金"].agg(lambda s: s.max() - s.min()).sort_values(ascending=False)
    if spread.empty:
        return "暂无可分析的评价等级数据。"
    return f"{spread.index[0]} 的评价等级人均奖金差距最大，可用于观察绩效区分度是否被强化。"


def distribution_insight(calc_df: pd.DataFrame, scenario: str) -> str:
    data = create_change_distribution_data(calc_df)
    data = data[data["方案"].eq(scenario)]
    if data.empty:
        return "暂无员工变化额数据。"
    median = data["变化额"].median()
    max_abs = data["变化额"].abs().max()
    return f"{scenario} 的个人变化额中位数为 {format_money(median)}，最大绝对变化为 {format_money(max_abs)}。建议关注分布尾部员工。"


def top_impact_insight(calc_df: pd.DataFrame, scenario: str) -> str:
    data = create_top_impact_chart_data(calc_df, scenario)
    if data.empty:
        return "暂无员工影响数据。"
    top = data.iloc[data["变化额"].abs().argmax()]
    return f"影响最大的员工为 {top['员工']}，变化额 {format_money(top['变化额'])}。建议纳入重点复核与沟通清单。"


def get_new_job_family_names() -> Dict[str, str]:
    return {"M": "管理职群", "T": "技术职群", "S": "营业职群", "O": "现场职群", "G": "综合职群"}


def get_default_grade_structure() -> pd.DataFrame:
    rows = [
        ("M", "管理职群", "M4", 4, "M4", "管理职群最低等级"),
        ("M", "管理职群", "M5", 5, "M5-6", "默认沿用 M5-6 组系数"),
        ("M", "管理职群", "M6", 6, "M5-6", "默认沿用 M5-6 组系数"),
        ("M", "管理职群", "M7", 7, "M7-8", "默认沿用 M7-8 组系数"),
        ("M", "管理职群", "M8", 8, "M7-8", "管理职群最高等级，默认沿用 M7-8 组系数"),
        ("T", "技术职群", "T1", 1, "T1-2", "默认沿用 T1-2 组系数"),
        ("T", "技术职群", "T2", 2, "T1-2", "默认沿用 T1-2 组系数"),
        ("T", "技术职群", "T3", 3, "T3", ""),
        ("T", "技术职群", "T4", 4, "T4", ""),
        ("T", "技术职群", "T5", 5, "T5-6", "默认沿用 T5-6 组系数"),
        ("T", "技术职群", "T6", 6, "T5-6", "默认沿用 T5-6 组系数"),
        ("T", "技术职群", "T7", 7, "T7", "技术职群最高等级"),
        ("S", "营业职群", "S1", 1, "S1-2", "默认沿用 S1-2 组系数"),
        ("S", "营业职群", "S2", 2, "S1-2", "默认沿用 S1-2 组系数"),
        ("S", "营业职群", "S3", 3, "S3", ""),
        ("S", "营业职群", "S4", 4, "S4", ""),
        ("S", "营业职群", "S5", 5, "S5", "营业职群最高等级"),
        ("O", "现场职群", "O1", 1, "O1-2", "默认沿用 O1-2 组系数"),
        ("O", "现场职群", "O2", 2, "O1-2", "默认沿用 O1-2 组系数"),
        ("O", "现场职群", "O3", 3, "O3", ""),
        ("O", "现场职群", "O4", 4, "O4", ""),
        ("O", "现场职群", "O5", 5, "O5", "现场职群最高等级"),
        ("G", "综合职群", "G1", 1, "G1-2", "默认沿用 G1-2 组系数"),
        ("G", "综合职群", "G2", 2, "G1-2", "默认沿用 G1-2 组系数"),
        ("G", "综合职群", "G3", 3, "G3", ""),
        ("G", "综合职群", "G4", 4, "G4", ""),
        ("G", "综合职群", "G5", 5, "G5-6", "默认沿用 G5-6 组系数"),
        ("G", "综合职群", "G6", 6, "G5-6", "综合职群最高等级，默认沿用 G5-6 组系数"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "new_job_family",
            "new_job_family_name",
            "new_grade",
            "grade_order",
            "coefficient_group",
            "note",
        ],
    )


def rating_coefficients(base: float) -> Dict[str, float]:
    multipliers = {"A": 1.25, "B+": 1.12, "B": 1.00, "C+": 0.86, "C": 0.70, "D": 0.45, "E": 0.00}
    return {rating: round(base * multiplier, 2) for rating, multiplier in multipliers.items()}


def get_default_before_coefficients() -> pd.DataFrame:
    family_base = {"综合职（非销售）": 1.00, "综合职（销售）": 1.04, "现场职": 0.92, "技术职": 1.08}
    qualification_factor = {"理事级": 1.35, "经营级": 1.22, "基干级": 1.10, "指导级": 0.95, "担当级": 0.82}
    rows = []
    for family, family_value in family_base.items():
        for qualification, qualification_value in qualification_factor.items():
            for rating, coefficient in rating_coefficients(family_value * qualification_value).items():
                rows.append(
                    {
                        "scenario": "Before",
                        "original_job_family": family,
                        "original_qualification": qualification,
                        "rating": rating,
                        "coefficient": coefficient,
                    }
                )
    return pd.DataFrame(rows)


def get_default_option_a_coefficients() -> pd.DataFrame:
    family_base = {"M": 1.30, "T": 1.13, "S": 1.03, "O": 0.92, "G": 0.98}
    names = get_new_job_family_names()
    rows = []
    for family, base in family_base.items():
        for rating, coefficient in rating_coefficients(base).items():
            rows.append(
                {
                    "scenario": "Option A",
                    "new_job_family": family,
                    "new_job_family_name": names[family],
                    "rating": rating,
                    "coefficient": coefficient,
                }
            )
    return pd.DataFrame(rows)


def get_default_option_b_coefficients() -> pd.DataFrame:
    grade_structure = get_default_grade_structure()
    family_base = {"M": 1.18, "T": 1.08, "S": 1.00, "O": 0.90, "G": 0.95}
    group_adjustment = {
        "M4": 1.00,
        "M5-6": 1.10,
        "M7-8": 1.22,
        "T1-2": 0.86,
        "T3": 0.96,
        "T4": 1.04,
        "T5-6": 1.14,
        "T7": 1.25,
        "S1-2": 0.86,
        "S3": 0.96,
        "S4": 1.06,
        "S5": 1.16,
        "O1-2": 0.86,
        "O3": 0.96,
        "O4": 1.06,
        "O5": 1.16,
        "G1-2": 0.86,
        "G3": 0.96,
        "G4": 1.06,
        "G5-6": 1.16,
    }
    rows = []
    for _, grade in grade_structure.iterrows():
        grade_factor = group_adjustment[grade["coefficient_group"]]
        for rating, coefficient in rating_coefficients(family_base[grade["new_job_family"]] * grade_factor).items():
            rows.append(
                {
                    "scenario": "Option B",
                    "new_job_family": grade["new_job_family"],
                    "new_job_family_name": grade["new_job_family_name"],
                    "new_grade": grade["new_grade"],
                    "rating": rating,
                    "coefficient": coefficient,
                }
            )
    return pd.DataFrame(rows)


def create_employee_template() -> BytesIO:
    sample = pd.DataFrame(
        [
            ["E001", "张三", "服务一部", "技术职", "基干级", "M", "M4", "A", 10000, 1.00, "Y", "示例"],
            ["E002", "李四", "服务一部", "技术职", "基干级", "T", "T4", "A", 10000, 1.00, "Y", "示例"],
            ["E003", "王五", "后勤部", "综合职（非销售）", "指导级", "G", "G3", "B", 8000, 1.00, "Y", "示例"],
            ["E004", "赵六", "销售部", "综合职（销售）", "经营级", "S", "S5", "B+", 12000, 0.80, "Y", "示例"],
            ["E005", "钱七", "现场部", "现场职", "担当级", "O", "O1", "C+", 7000, 1.00, "N", "示例，不参与测算"],
        ],
        columns=EMPLOYEE_COLUMNS,
    )
    instructions = pd.DataFrame(
        [
            ["员工编号", "不可重复", "文本", "是"],
            ["姓名", "员工姓名", "文本", "是"],
            ["部门", "所属部门", "文本", "建议"],
            ["原职群", "按现行职群填写", "综合职（非销售）、综合职（销售）、现场职、技术职", "是"],
            ["原能力资格", "按现行能力资格填写", "理事级、经营级、基干级、指导级、担当级", "是"],
            ["新职群", "用于方案 A 和方案 B 测算", "M、T、S、O、G", "是"],
            ["新等级", "用于方案 B 测算，需为实际单一等级", "如 M4、M5、T1、S3、O4、G6", "是"],
            ["评价等级", "年度评价等级", "A、B+、B、C+、C、D、E", "是"],
            ["月度奖金基数", "奖金计算基数", "数字，大于等于 0", "是"],
            ["折算系数", "折算系数", "数字，通常为 0-1；不填默认 1", "否"],
            ["是否参与测算", "是否参与测算", "Y、N", "是"],
            ["备注", "备注说明", "文本", "否"],
            ["填写提醒", "客户仅需填写“01_员工数据”Sheet。", "", ""],
            ["填写提醒", "新职群和新等级由客户或顾问确认后填写，系统不再根据原能力资格推断。", "", ""],
            ["填写提醒", "新等级必须填写实际单一等级，不要填写 M7-8、S1-2、S/O3 等组合或组标签。", "", ""],
        ],
        columns=["字段", "填写要求", "可选值/格式", "是否必填"],
    )
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        sample_cn = rename_columns_cn(sample)
        sample_cn.to_excel(writer, index=False, sheet_name="01_员工数据")
        instructions.to_excel(writer, index=False, sheet_name="02_填写说明")
        workbook = writer.book
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#DDEBF7", "border": 1})
        text_fmt = workbook.add_format({"text_wrap": True, "valign": "top"})
        for sheet_name, df in {"01_员工数据": sample_cn, "02_填写说明": instructions}.items():
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            for col_idx, col_name in enumerate(df.columns):
                ws.write(0, col_idx, col_name, header_fmt)
                max_len = max([len(str(col_name))] + [len(str(value)) for value in df[col_name].fillna("")])
                ws.set_column(col_idx, col_idx, min(max(max_len + 2, 12), 36), text_fmt)
    buffer.seek(0)
    return buffer


def load_employee_data(uploaded_file) -> Tuple[pd.DataFrame, str | None]:
    xls = pd.ExcelFile(uploaded_file)
    warning = None
    sheet_name = "01_员工数据" if "01_员工数据" in xls.sheet_names else xls.sheet_names[0]
    if sheet_name != "01_员工数据":
        warning = f"上传文件中没有“01_员工数据”Sheet，已读取第一个 Sheet：“{sheet_name}”。"
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, dtype=object)
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    df.columns = [str(col).strip() for col in df.columns]
    df = normalize_uploaded_columns(df)
    for col in EMPLOYEE_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan
    return clean_employee_data(df[EMPLOYEE_COLUMNS]), warning


def clean_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    text_columns = [
        "employee_id",
        "employee_name",
        "department",
        "original_job_family",
        "original_qualification",
        "new_job_family",
        "new_grade",
        "rating",
        "eligible",
        "remarks",
    ]
    for col in text_columns:
        out[col] = out[col].apply(lambda value: str(value).strip() if pd.notna(value) else "")
    out["rating"] = out["rating"].str.upper()
    out["eligible"] = out["eligible"].str.upper()
    out["new_job_family"] = out["new_job_family"].str.upper()
    out["new_grade"] = out["new_grade"].str.upper()
    out["bonus_base"] = pd.to_numeric(out["bonus_base"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    out["proration_factor"] = pd.to_numeric(out["proration_factor"].astype(str).str.replace(",", "", regex=False), errors="coerce").fillna(1)
    return out


def issue_record(row: pd.Series, issue_type: str, issue_detail: str, severity: str = "error") -> Dict[str, str]:
    return {
        "employee_id": row.get("employee_id", ""),
        "employee_name": row.get("employee_name", ""),
        "issue_type": issue_type,
        "issue_detail": issue_detail,
        "severity": severity,
    }


def validate_employee_data(employee_df: pd.DataFrame) -> pd.DataFrame:
    issues: List[Dict[str, str]] = []
    grade_structure = get_default_grade_structure()
    valid_grade_pairs = set(zip(grade_structure["new_job_family"], grade_structure["new_grade"]))
    if employee_df.empty:
        return pd.DataFrame(
            [{"employee_id": "", "employee_name": "", "issue_type": "无员工数据", "issue_detail": "上传文件未读取到员工记录。", "severity": "error"}]
        )

    for _, row in employee_df.iterrows():
        for col in REQUIRED_COLUMNS:
            if pd.isna(row[col]) or str(row[col]).strip() == "":
                issues.append(issue_record(row, "缺失必填字段", f"{cn_label(col)}不能为空。"))
        if row["original_job_family"] and row["original_job_family"] not in VALID_JOB_FAMILIES:
            issues.append(issue_record(row, "原职群无效", f"{row['original_job_family']} 不在有效职群范围内。"))
        if row["original_qualification"] and row["original_qualification"] not in VALID_QUALIFICATIONS:
            issues.append(issue_record(row, "原能力资格无效", f"{row['original_qualification']} 不在有效能力资格范围内。"))
        if row["new_job_family"] and row["new_job_family"] not in VALID_NEW_JOB_FAMILIES:
            issues.append(issue_record(row, "新职群无效", "new_job_family 需填写 M、T、S、O、G。"))
        if row["new_grade"] and (row["new_job_family"], row["new_grade"]) not in valid_grade_pairs:
            issues.append(issue_record(row, "新等级无效", "new_grade 必须是所选 new_job_family 下的实际单一等级。"))
        if row["rating"] and row["rating"] not in VALID_RATINGS:
            issues.append(issue_record(row, "评价等级无效", f"{row['rating']} 不在有效评价等级范围内。"))
        if pd.isna(row["bonus_base"]) or row["bonus_base"] < 0:
            issues.append(issue_record(row, "月度奖金基数无效", "月度奖金基数需为大于等于 0 的数字。"))
        if pd.isna(row["proration_factor"]) or row["proration_factor"] < 0:
            issues.append(issue_record(row, "折算系数无效", "折算系数需为大于等于 0 的数字。"))
        if row["eligible"] and row["eligible"] not in ["Y", "N"]:
            issues.append(issue_record(row, "是否参与测算无效", "eligible 需填写 Y 或 N。"))

    duplicated = employee_df["employee_id"].ne("") & employee_df["employee_id"].duplicated(keep=False)
    for _, row in employee_df[duplicated].iterrows():
        issues.append(issue_record(row, "员工编号重复", "employee_id 存在重复。"))

    return pd.DataFrame(issues, columns=["employee_id", "employee_name", "issue_type", "issue_detail", "severity"])


def check_employee_structure(employee_df: pd.DataFrame, grade_structure: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    checked = employee_df.copy()
    names = get_new_job_family_names()
    grade_lookup = grade_structure[["new_job_family", "new_grade", "grade_order", "coefficient_group"]]
    checked["new_job_family_name"] = checked["new_job_family"].map(names)
    checked = checked.merge(grade_lookup, on=["new_job_family", "new_grade"], how="left")
    checked["structure_status"] = "结构有效"
    checked["structure_note"] = ""

    issues: List[Dict[str, str]] = []
    invalid_family = checked["new_job_family"].ne("") & checked["new_job_family_name"].isna()
    invalid_grade = checked["new_job_family"].ne("") & checked["new_grade"].ne("") & checked["grade_order"].isna()
    checked.loc[invalid_family | invalid_grade, "structure_status"] = "结构异常"
    checked.loc[invalid_family, "structure_note"] = "new_job_family 需填写 M、T、S、O、G"
    checked.loc[invalid_grade, "structure_note"] = "new_grade 必须是所选 new_job_family 下的实际单一等级"
    for _, row in checked[invalid_family].iterrows():
        issues.append(issue_record(row, "新职群无效", "new_job_family 需填写 M、T、S、O、G。"))
    for _, row in checked[invalid_grade].iterrows():
        issues.append(issue_record(row, "新等级无效", "new_grade 必须是所选 new_job_family 下的实际单一等级。"))
    structure_issues = pd.DataFrame(issues, columns=["employee_id", "employee_name", "issue_type", "issue_detail", "severity"])
    return checked, structure_issues


def matrix_to_long_option_a(matrix_df: pd.DataFrame) -> pd.DataFrame:
    names = get_new_job_family_names()
    long_df = matrix_df.melt(
        id_vars=["new_job_family", "new_job_family_name"],
        value_vars=VALID_RATINGS,
        var_name="rating",
        value_name="coefficient",
    )
    long_df["scenario"] = "Option A"
    long_df["new_job_family_name"] = long_df["new_job_family"].map(names).fillna(long_df["new_job_family_name"])
    long_df["coefficient"] = pd.to_numeric(long_df["coefficient"], errors="coerce")
    return long_df[["scenario", "new_job_family", "new_job_family_name", "rating", "coefficient"]]


def matrix_to_long_option_b(matrix_df: pd.DataFrame) -> pd.DataFrame:
    long_df = matrix_df.melt(
        id_vars=["new_job_family", "new_job_family_name", "new_grade"],
        value_vars=VALID_RATINGS,
        var_name="rating",
        value_name="coefficient",
    )
    long_df["scenario"] = "Option B"
    long_df["coefficient"] = pd.to_numeric(long_df["coefficient"], errors="coerce")
    return long_df[["scenario", "new_job_family", "new_job_family_name", "new_grade", "rating", "coefficient"]]


def option_a_long_to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    matrix = df.pivot_table(
        index=["new_job_family", "new_job_family_name"], columns="rating", values="coefficient", aggfunc="first"
    ).reset_index()
    return matrix[["new_job_family", "new_job_family_name"] + VALID_RATINGS]


def option_b_long_to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    structure = get_default_grade_structure()[["new_job_family", "new_job_family_name", "new_grade", "grade_order"]]
    matrix = df.pivot_table(
        index=["new_job_family", "new_job_family_name", "new_grade"], columns="rating", values="coefficient", aggfunc="first"
    ).reset_index()
    matrix = matrix.merge(structure, on=["new_job_family", "new_job_family_name", "new_grade"], how="left")
    matrix = matrix.sort_values(["new_job_family", "grade_order"], ascending=[True, False]).drop(columns=["grade_order"])
    return matrix[["new_job_family", "new_job_family_name", "new_grade"] + VALID_RATINGS]


def add_coefficient_issues(calc_df: pd.DataFrame) -> pd.DataFrame:
    issues: List[Dict[str, str]] = []
    for _, row in calc_df.iterrows():
        if row["eligible"] != "Y":
            continue
        if pd.isna(row.get("before_coefficient")):
            issues.append(issue_record(row, "现行方案系数缺失", "现行方案匹配不到系数。"))
        if pd.isna(row.get("option_a_coefficient")):
            issues.append(issue_record(row, "方案A系数缺失", "方案A匹配不到系数。"))
        if pd.isna(row.get("option_b_coefficient")):
            issues.append(issue_record(row, "方案B系数缺失", "方案B匹配不到系数。"))
    return pd.DataFrame(issues, columns=["employee_id", "employee_name", "issue_type", "issue_detail", "severity"])


def calculate_bonus(
    structure_df: pd.DataFrame,
    before_coeff: pd.DataFrame,
    option_a_coeff: pd.DataFrame,
    option_b_coeff: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    detail = structure_df.copy()
    before = before_coeff.rename(columns={"coefficient": "before_coefficient"})
    option_a = option_a_coeff.rename(columns={"coefficient": "option_a_coefficient"})
    option_b = option_b_coeff.rename(columns={"coefficient": "option_b_coefficient"})

    detail = detail.merge(
        before[["original_job_family", "original_qualification", "rating", "before_coefficient"]],
        on=["original_job_family", "original_qualification", "rating"],
        how="left",
    )
    detail = detail.merge(
        option_a[["new_job_family", "rating", "option_a_coefficient"]],
        on=["new_job_family", "rating"],
        how="left",
    )
    detail = detail.merge(
        option_b[["new_job_family", "new_grade", "rating", "option_b_coefficient"]],
        on=["new_job_family", "new_grade", "rating"],
        how="left",
    )

    coeff_issues = add_coefficient_issues(detail)
    valid_for_calc = (
        detail["eligible"].eq("Y")
        & detail["bonus_base"].notna()
        & detail["proration_factor"].notna()
        & detail["before_coefficient"].notna()
        & detail["option_a_coefficient"].notna()
        & detail["option_b_coefficient"].notna()
        & detail["new_grade"].notna()
    )
    not_eligible = detail["eligible"].eq("N")

    for scenario in ["before", "option_a", "option_b"]:
        detail[f"{scenario}_bonus"] = np.nan
        detail.loc[valid_for_calc, f"{scenario}_bonus"] = (
            detail.loc[valid_for_calc, "bonus_base"]
            * detail.loc[valid_for_calc, f"{scenario}_coefficient"]
            * detail.loc[valid_for_calc, "proration_factor"]
        )
        detail.loc[not_eligible, f"{scenario}_bonus"] = 0

    detail["option_a_change_amount"] = detail["option_a_bonus"] - detail["before_bonus"]
    detail["option_b_change_amount"] = detail["option_b_bonus"] - detail["before_bonus"]
    detail["option_a_change_pct"] = np.where(detail["before_bonus"].fillna(0).ne(0), detail["option_a_change_amount"] / detail["before_bonus"], np.nan)
    detail["option_b_change_pct"] = np.where(detail["before_bonus"].fillna(0).ne(0), detail["option_b_change_amount"] / detail["before_bonus"], np.nan)
    detail.loc[not_eligible, "structure_note"] = detail.loc[not_eligible, "structure_note"].replace("", "不参与测算")
    detail.loc[not_eligible, "structure_status"] = "不参与测算"

    columns = [
        "employee_id",
        "employee_name",
        "department",
        "original_job_family",
        "original_qualification",
        "new_job_family",
        "new_job_family_name",
        "new_grade",
        "rating",
        "bonus_base",
        "proration_factor",
        "eligible",
        "before_coefficient",
        "option_a_coefficient",
        "option_b_coefficient",
        "before_bonus",
        "option_a_bonus",
        "option_b_bonus",
        "option_a_change_amount",
        "option_a_change_pct",
        "option_b_change_amount",
        "option_b_change_pct",
        "structure_status",
        "structure_note",
        "remarks",
    ]
    return detail[columns], coeff_issues


def eligible_detail(calc_df: pd.DataFrame) -> pd.DataFrame:
    return calc_df[calc_df["eligible"].eq("Y")].copy()


def safe_pct(change: float, base: float) -> float:
    return np.nan if pd.isna(base) or base == 0 else change / base


def create_overall_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    rows = []
    before_total = df["before_bonus"].sum(skipna=True)
    option_a_total = df["option_a_bonus"].sum(skipna=True)
    option_b_total = df["option_b_bonus"].sum(skipna=True)
    rows.append({"指标": "参与人数", "Before": len(df), "Option A": len(df), "Option B": len(df)})
    rows.append({"指标": "总奖金成本", "Before": before_total, "Option A": option_a_total, "Option B": option_b_total})
    rows.append({"指标": "较 Before 变化额", "Before": np.nan, "Option A": option_a_total - before_total, "Option B": option_b_total - before_total})
    rows.append({"指标": "较 Before 变化率", "Before": np.nan, "Option A": safe_pct(option_a_total - before_total, before_total), "Option B": safe_pct(option_b_total - before_total, before_total)})
    rows.append({"指标": "人均奖金", "Before": df["before_bonus"].mean(), "Option A": df["option_a_bonus"].mean(), "Option B": df["option_b_bonus"].mean()})
    rows.append({"指标": "最高奖金", "Before": df["before_bonus"].max(), "Option A": df["option_a_bonus"].max(), "Option B": df["option_b_bonus"].max()})
    rows.append({"指标": "最低奖金", "Before": df["before_bonus"].min(), "Option A": df["option_a_bonus"].min(), "Option B": df["option_b_bonus"].min()})
    return pd.DataFrame(rows)


def create_group_summary(calc_df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    grouped = (
        df.groupby(group_cols, dropna=False)
        .agg(
            headcount=("employee_id", "count"),
            before_bonus=("before_bonus", "sum"),
            option_a_bonus=("option_a_bonus", "sum"),
            option_b_bonus=("option_b_bonus", "sum"),
        )
        .reset_index()
    )
    grouped["option_a_change_amount"] = grouped["option_a_bonus"] - grouped["before_bonus"]
    grouped["option_b_change_amount"] = grouped["option_b_bonus"] - grouped["before_bonus"]
    grouped["option_a_change_pct"] = np.where(grouped["before_bonus"].ne(0), grouped["option_a_change_amount"] / grouped["before_bonus"], np.nan)
    grouped["option_b_change_pct"] = np.where(grouped["before_bonus"].ne(0), grouped["option_b_change_amount"] / grouped["before_bonus"], np.nan)
    return grouped


def create_original_job_family_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    return create_group_summary(calc_df, ["original_job_family"])


def create_new_job_family_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    return create_group_summary(calc_df, ["new_job_family", "new_job_family_name"])


def create_grade_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    return create_group_summary(calc_df, ["new_grade"])


def create_rating_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    return create_group_summary(calc_df, ["rating"])


def create_employee_impact(calc_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "employee_id",
        "employee_name",
        "department",
        "original_job_family",
        "original_qualification",
        "new_job_family",
        "new_job_family_name",
        "new_grade",
        "rating",
        "before_bonus",
        "option_a_bonus",
        "option_b_bonus",
        "option_a_change_amount",
        "option_b_change_amount",
    ]
    impact = calc_df[cols].copy()
    impact["_sort_key"] = impact[["option_a_change_amount", "option_b_change_amount"]].abs().max(axis=1)
    return impact.sort_values("_sort_key", ascending=False).drop(columns="_sort_key")


def create_total_cost_chart_data(calc_df: pd.DataFrame) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    return pd.DataFrame(
        {
            "方案": ["现行方案", "方案A", "方案B"],
            "总奖金成本": [df["before_bonus"].sum(), df["option_a_bonus"].sum(), df["option_b_bonus"].sum()],
        }
    )


def create_new_family_chart_data(calc_df: pd.DataFrame) -> pd.DataFrame:
    summary = create_new_job_family_summary(calc_df).copy()
    summary["新职群"] = summary["new_job_family"].fillna("") + " " + summary["new_job_family_name"].fillna("")
    return summary.melt(
        id_vars=["新职群"],
        value_vars=["before_bonus", "option_a_bonus", "option_b_bonus"],
        var_name="方案",
        value_name="奖金总额",
    ).replace({"方案": {"before_bonus": "现行方案", "option_a_bonus": "方案A", "option_b_bonus": "方案B"}})


def create_rating_average_chart_data(calc_df: pd.DataFrame) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    grouped = (
        df.groupby("rating", dropna=False)
        .agg(
            before_bonus=("before_bonus", "mean"),
            option_a_bonus=("option_a_bonus", "mean"),
            option_b_bonus=("option_b_bonus", "mean"),
        )
        .reindex(VALID_RATINGS)
        .reset_index()
        .rename(columns={"rating": "评价等级"})
    )
    return grouped.melt(
        id_vars=["评价等级"],
        value_vars=["before_bonus", "option_a_bonus", "option_b_bonus"],
        var_name="方案",
        value_name="人均奖金",
    ).replace({"方案": {"before_bonus": "现行方案", "option_a_bonus": "方案A", "option_b_bonus": "方案B"}})


def create_change_distribution_data(calc_df: pd.DataFrame) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    return df.melt(
        value_vars=["option_a_change_amount", "option_b_change_amount"],
        var_name="方案",
        value_name="变化额",
    ).replace({"方案": {"option_a_change_amount": "方案A", "option_b_change_amount": "方案B"}}).dropna(subset=["变化额"])


def create_top_impact_chart_data(calc_df: pd.DataFrame, scenario: str) -> pd.DataFrame:
    source_col = "option_a_change_amount" if scenario == "方案A" else "option_b_change_amount"
    df = eligible_detail(calc_df)[["employee_id", "employee_name", source_col]].copy()
    df["员工"] = df["employee_id"].fillna("") + " " + df["employee_name"].fillna("")
    df["变化额"] = df[source_col]
    df["绝对变化额"] = df["变化额"].abs()
    df = df.sort_values("绝对变化额", ascending=False).head(10).sort_values("变化额")
    df["方向"] = np.where(df["变化额"] >= 0, "增加", "减少")
    return df[["员工", "变化额", "方向"]]


def render_total_cost_chart(calc_df: pd.DataFrame) -> None:
    with st.container(border=True):
        data = create_total_cost_chart_data(calc_df)
        chart_note("该图用于比较三套方案下的总奖金成本变化。")
        bars = alt.Chart(data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=52).encode(
            x=alt.X("方案:N", title="方案", sort=["现行方案", "方案A", "方案B"]),
            y=alt.Y("总奖金成本:Q", title="总奖金成本", axis=alt.Axis(format=",.0f")),
            color=alt.Color("方案:N", scale=alt.Scale(domain=["现行方案", "方案A", "方案B"], range=[SCENARIO_COLORS["现行方案"], SCENARIO_COLORS["方案A"], SCENARIO_COLORS["方案B"]]), legend=None),
            tooltip=[alt.Tooltip("方案:N"), alt.Tooltip("总奖金成本:Q", format=",.0f")],
        )
        labels = alt.Chart(data).mark_text(dy=-8, color=YNC_COLORS["text"], fontSize=12).encode(
            x=alt.X("方案:N", sort=["现行方案", "方案A", "方案B"]),
            y=alt.Y("总奖金成本:Q"),
            text=alt.Text("总奖金成本:Q", format=",.0f"),
        )
        chart = bars + labels
        st.altair_chart(chart_base(chart, "三套方案总奖金成本对比"), use_container_width=True, key="total_cost_chart_v3")
        chart_analysis(total_cost_insight(calc_df))


def render_new_family_chart(calc_df: pd.DataFrame) -> None:
    with st.container(border=True):
        data = create_new_family_chart_data(calc_df)
        chart_note("该图展示不同新职群在各方案下的奖金成本分布。")
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X("新职群:N", title="新职群"),
            y=alt.Y("奖金总额:Q", title="奖金总额", axis=alt.Axis(format=",.0f")),
            xOffset="方案:N",
            color=alt.Color("方案:N", scale=alt.Scale(domain=["现行方案", "方案A", "方案B"], range=[SCENARIO_COLORS["现行方案"], SCENARIO_COLORS["方案A"], SCENARIO_COLORS["方案B"]])),
            tooltip=[alt.Tooltip("新职群:N"), alt.Tooltip("方案:N"), alt.Tooltip("奖金总额:Q", format=",.0f")],
        )
        st.altair_chart(chart_base(chart, "按新职群的奖金成本对比"), use_container_width=True, key="new_family_chart_v3")
        chart_analysis(new_family_insight(calc_df))


def render_rating_average_chart(calc_df: pd.DataFrame) -> None:
    with st.container(border=True):
        data = create_rating_average_chart_data(calc_df)
        chart_note("该图用于观察高绩效与低绩效员工之间的激励差异是否被拉开。")
        chart = alt.Chart(data).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("评价等级:N", title="评价等级", sort=VALID_RATINGS),
            y=alt.Y("人均奖金:Q", title="人均奖金", axis=alt.Axis(format=",.0f")),
            color=alt.Color("方案:N", scale=alt.Scale(domain=["现行方案", "方案A", "方案B"], range=[SCENARIO_COLORS["现行方案"], SCENARIO_COLORS["方案A"], SCENARIO_COLORS["方案B"]])),
            tooltip=[alt.Tooltip("评价等级:N"), alt.Tooltip("方案:N"), alt.Tooltip("人均奖金:Q", format=",.0f")],
        )
        st.altair_chart(chart_base(chart, "按评价等级的人均奖金对比"), use_container_width=True, key="rating_average_chart_v3")
        chart_analysis(rating_insight(calc_df))


def render_change_distribution_chart(calc_df: pd.DataFrame, scenario: str) -> None:
    with st.container(border=True):
        data = create_change_distribution_data(calc_df)
        data = data[data["方案"].eq(scenario)]
        chart_note("该图用于识别方案调整后个人奖金变化是否过于集中或存在极端值。")
        chart = alt.Chart(data).mark_bar(opacity=0.76, color=SCENARIO_COLORS[scenario]).encode(
            x=alt.X("变化额:Q", title="变化额", bin=alt.Bin(maxbins=24), axis=alt.Axis(format=",.0f")),
            y=alt.Y("count():Q", title="员工数量", axis=alt.Axis(format=",.0f")),
            tooltip=[alt.Tooltip("方案:N"), alt.Tooltip("count():Q", title="员工数量", format=",.0f")],
        )
        safe_key = "option_a" if scenario == "方案A" else "option_b"
        st.altair_chart(chart_base(chart, f"{scenario}较现行变化额分布"), use_container_width=True, key=f"change_distribution_{safe_key}_v3")
        chart_analysis(distribution_insight(calc_df, scenario))


def render_top_impact_chart(calc_df: pd.DataFrame, scenario: str) -> None:
    with st.container(border=True):
        data = create_top_impact_chart_data(calc_df, scenario)
        chart_note("该图展示奖金变化绝对值最大的员工，用于识别重点沟通对象。")
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X("变化额:Q", title=f"{scenario}较现行变化额", axis=alt.Axis(format=",.0f")),
            y=alt.Y("员工:N", title="员工", sort="-x"),
            color=alt.Color("方向:N", scale=alt.Scale(domain=["增加", "减少"], range=[SCENARIO_COLORS["positive"], SCENARIO_COLORS["negative"]]), legend=None),
            tooltip=[alt.Tooltip("员工:N"), alt.Tooltip("变化额:Q", format=",.0f"), alt.Tooltip("方向:N")],
        )
        safe_key = "option_a" if scenario == "方案A" else "option_b"
        st.altair_chart(chart_base(chart, f"奖金变化影响最大的员工（{scenario}）"), use_container_width=True, key=f"top_impact_{safe_key}_v3")
        chart_analysis(top_impact_insight(calc_df, scenario))


def format_money(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"


def format_pct(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def style_display_df(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    fmt = {}
    for col in df.columns:
        if col in MONEY_COLUMNS or col.endswith("_bonus") or col.endswith("_amount"):
            fmt[col] = "{:,.0f}"
        if col in PCT_COLUMNS or col.endswith("_pct"):
            fmt[col] = "{:.1%}"
        if col in COEFF_COLUMNS or col.endswith("_coefficient"):
            fmt[col] = "{:.2f}"
    return df.style.format(fmt, na_rep="")


def write_formatted_sheet(writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
    original_columns = list(df.columns)
    safe_df = rename_columns_cn(df)
    safe_df.to_excel(writer, index=False, sheet_name=sheet_name)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    header_fmt = workbook.add_format({"bold": True, "bg_color": "#DDEBF7", "font_color": "#1F2933", "border": 1})
    money_fmt = workbook.add_format({"num_format": "#,##0", "border": 1})
    pct_fmt = workbook.add_format({"num_format": "0.0%", "border": 1})
    coeff_fmt = workbook.add_format({"num_format": "0.00", "border": 1})
    text_fmt = workbook.add_format({"border": 1})
    error_fmt = workbook.add_format({"bg_color": "#FDE2E2", "border": 1})
    warning_fmt = workbook.add_format({"bg_color": "#FFF3CD", "border": 1})

    worksheet.freeze_panes(1, 0)
    for col_idx, col_name in enumerate(safe_df.columns):
        original_col = original_columns[col_idx] if col_idx < len(original_columns) else col_name
        worksheet.write(0, col_idx, col_name, header_fmt)
        series = safe_df[col_name].fillna("")
        max_len = max([len(str(col_name))] + [len(str(value)) for value in series.head(500)])
        worksheet.set_column(col_idx, col_idx, min(max(max_len + 2, 12), 42), text_fmt)
        if original_col in COUNT_COLUMNS or "人数" in col_name or "数量" in col_name:
            worksheet.set_column(col_idx, col_idx, 12, workbook.add_format({"num_format": "#,##0", "border": 1}))
        elif original_col in MONEY_COLUMNS or original_col == "bonus_base" or original_col.endswith("_bonus") or original_col.endswith("_amount"):
            worksheet.set_column(col_idx, col_idx, 16, money_fmt)
        elif original_col in PCT_COLUMNS or original_col.endswith("_pct") or "变化率" in col_name:
            worksheet.set_column(col_idx, col_idx, 14, pct_fmt)
        elif original_col in COEFF_COLUMNS or original_col.endswith("_coefficient") or col_name in VALID_RATINGS:
            worksheet.set_column(col_idx, col_idx, 12, coeff_fmt)

    severity_label = cn_label("severity")
    if severity_label in safe_df.columns and len(safe_df) > 0:
        severity_col = safe_df.columns.get_loc(severity_label)
        first_row, last_row = 1, len(safe_df)
        first_col, last_col = 0, len(safe_df.columns) - 1
        worksheet.conditional_format(first_row, first_col, last_row, last_col, {
            "type": "formula",
            "criteria": f'=${chr(65 + severity_col)}2="error"',
            "format": error_fmt,
        })
        worksheet.conditional_format(first_row, first_col, last_row, last_col, {
            "type": "formula",
            "criteria": f'=${chr(65 + severity_col)}2="warning"',
            "format": warning_fmt,
        })


def export_results_to_excel(
    raw_employee_df: pd.DataFrame,
    structure_df: pd.DataFrame,
    before_coeff: pd.DataFrame,
    option_a_matrix: pd.DataFrame,
    option_b_matrix: pd.DataFrame,
    calc_df: pd.DataFrame,
    summaries: Dict[str, pd.DataFrame],
    validation_issues: pd.DataFrame,
) -> BytesIO:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        sheets = {
            "01_原始员工数据": raw_employee_df,
            "02_数据检查": structure_df,
            "03_现行方案系数": before_coeff,
            "04_方案A系数": option_a_matrix,
            "05_方案B系数": option_b_matrix,
            "06_测算明细": calc_df,
            "07_总体对比": format_overall_summary_cn(summaries["overall"]),
            "08_原职群对比": summaries["original_family"],
            "09_新职群对比": summaries["new_family"],
            "10_新等级对比": summaries["grade"],
            "11_评价等级对比": summaries["rating"],
            "12_异常清单": validation_issues,
        }
        for sheet_name, df in sheets.items():
            write_formatted_sheet(writer, sheet_name, df)
    buffer.seek(0)
    return buffer


def combine_issues(*frames: pd.DataFrame) -> pd.DataFrame:
    clean_frames = [df for df in frames if df is not None and not df.empty]
    if not clean_frames:
        return pd.DataFrame(columns=["employee_id", "employee_name", "issue_type", "issue_detail", "severity"])
    combined = pd.concat(clean_frames, ignore_index=True)
    return combined.drop_duplicates().reset_index(drop=True)


def calculate_all(employee_df: pd.DataFrame, option_a_matrix: pd.DataFrame, option_b_matrix: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    before_coeff = get_default_before_coefficients()
    option_a_coeff = matrix_to_long_option_a(option_a_matrix)
    option_b_coeff = matrix_to_long_option_b(option_b_matrix)
    base_issues = validate_employee_data(employee_df)
    structure_df, structure_issues = check_employee_structure(employee_df, get_default_grade_structure())
    calc_df, coeff_issues = calculate_bonus(structure_df, before_coeff, option_a_coeff, option_b_coeff)
    issues = combine_issues(base_issues, structure_issues, coeff_issues)
    summaries = {
        "overall": create_overall_summary(calc_df),
        "original_family": create_original_job_family_summary(calc_df),
        "new_family": create_new_job_family_summary(calc_df),
        "grade": create_grade_summary(calc_df),
        "rating": create_rating_summary(calc_df),
        "impact": create_employee_impact(calc_df),
    }
    return {"structure": structure_df, "calc": calc_df, "issues": issues, "before_coeff": before_coeff, **summaries}


def initialize_state() -> None:
    if "option_a_matrix" not in st.session_state:
        st.session_state.option_a_matrix = option_a_long_to_matrix(get_default_option_a_coefficients())
    if "option_b_matrix" not in st.session_state or len(st.session_state.option_b_matrix) != len(get_default_grade_structure()):
        st.session_state.option_b_matrix = option_b_long_to_matrix(get_default_option_b_coefficients())
    needs_employee_seed = "employee_df" not in st.session_state or not set(EMPLOYEE_COLUMNS).issubset(st.session_state.employee_df.columns)
    if needs_employee_seed:
        st.session_state.employee_df = clean_employee_data(
            pd.DataFrame(
                [
                    ["E001", "张三", "服务一部", "技术职", "基干级", "M", "M4", "A", 10000, 1.00, "Y", "示例"],
                    ["E002", "李四", "服务一部", "技术职", "基干级", "T", "T4", "A", 10000, 1.00, "Y", "示例"],
                    ["E003", "王五", "后勤部", "综合职（非销售）", "指导级", "G", "G3", "B", 8000, 1.00, "Y", "示例"],
                ],
                columns=EMPLOYEE_COLUMNS,
            )
        )
    if "upload_warning" not in st.session_state:
        st.session_state.upload_warning = None
    if "has_uploaded_data" not in st.session_state:
        st.session_state.has_uploaded_data = False
    if "results" not in st.session_state or "structure" not in st.session_state.results:
        st.session_state.results = calculate_all(
            st.session_state.employee_df,
            st.session_state.option_a_matrix,
            st.session_state.option_b_matrix,
        )
    if "last_calc_time" not in st.session_state:
        st.session_state.last_calc_time = datetime.now().strftime("%Y-%m-%d %H:%M")


def refresh_results() -> None:
    st.session_state.results = calculate_all(
        st.session_state.employee_df,
        st.session_state.option_a_matrix,
        st.session_state.option_b_matrix,
    )
    st.session_state.last_calc_time = datetime.now().strftime("%Y-%m-%d %H:%M")


def render_download_tab() -> None:
    render_card(
        "<h3>模板下载</h3>"
        "<p>客户仅需填写标准模板中的 <b>01_员工数据</b> Sheet。现行方案使用原职群和原能力资格；方案A/方案B使用上传的新职群和新等级。</p>"
    )
    st.download_button(
        "下载标准模板",
        data=create_employee_template(),
        file_name="YNC_员工数据标准模板.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=False,
    )


def render_home_tab() -> None:
    status = get_status_summary()
    render_card(
        f"""
        <div style="display:flex; gap:24px; align-items:stretch; justify-content:space-between; flex-wrap:wrap;">
            <div style="flex:1; min-width:360px;">
                <div style="font-size:14px; color:#7F0D1B; margin-bottom:10px;">Bonus Coefficient Scenario Analyzer</div>
                <div style="font-size:34px; line-height:1.18; font-weight:500; color:#1F2933; margin-bottom:12px;">YNC 奖金系数方案测算工具</div>
                <div style="font-size:15px; color:#6B7280; max-width:720px;">用于现行方案、方案A、方案B的奖金成本测算、员工影响分析与方案对比。</div>
            </div>
            <div style="min-width:260px; background:rgba(177,18,38,0.06); border:1px solid rgba(177,18,38,0.12); border-radius:16px; padding:16px;">
                <div style="font-size:13px; color:#6B7280; margin-bottom:8px;">当前数据状态</div>
                <div style="font-size:22px; color:#7F0D1B; font-weight:500;">{status["status"]}</div>
                <div style="font-size:13px; color:#6B7280; margin-top:10px;">员工数量：{status["employee_count"]}</div>
                <div style="font-size:13px; color:#6B7280;">最近测算：{status["calc_time"]}</div>
            </div>
        </div>
        """
    )
    cols = st.columns(3)
    with cols[0]:
        render_card(f"<h3>{icon_title('download', '标准化导入')}</h3><p>客户仅需填写员工数据，规则与方案参数由顾问维护。</p>")
    with cols[1]:
        render_card(f"<h3>{icon_title('settings', '方案系数调整')}</h3><p>支持方案A、方案B系数在线编辑，调整后自动刷新测算结果。</p>")
    with cols[2]:
        render_card(f"<h3>{icon_title('chart', '可视化对比分析')}</h3><p>支持总成本、职群、等级、评价等级和员工影响分析。</p>")
    render_card("<h3>流程步骤</h3><p style='font-size:15px;color:#50606F;'>1 下载模板 → 2 上传员工数据 → 3 调整方案系数 → 4 查看对比分析 → 5 导出结果</p>")


def render_upload_tab() -> None:
    render_card("<h3>数据上传</h3><p>上传客户填写后的 Excel。系统优先读取“01_员工数据”Sheet，也兼容中文表头和旧版英文表头。</p>")
    uploaded_file = st.file_uploader("上传员工数据 Excel", type=["xlsx", "xls"])
    if uploaded_file is not None:
        try:
            employee_df, warning = load_employee_data(uploaded_file)
            st.session_state.employee_df = employee_df
            st.session_state.upload_warning = warning
            st.session_state.has_uploaded_data = True
            refresh_results()
            st.success(f"已成功读取 {len(employee_df):,} 条员工数据。")
        except Exception as exc:
            st.error(f"读取失败：{exc}")

    if st.session_state.upload_warning:
        st.warning(st.session_state.upload_warning)

    st.subheader("员工数据预览")
    if not st.session_state.get("has_uploaded_data", False):
        st.markdown('<div class="empty-state"><b>尚未上传员工数据</b><br>当前显示的是示例数据。请先下载标准模板并上传填写后的员工数据。</div>', unsafe_allow_html=True)
    display_table_cn(st.session_state.employee_df)


def render_data_check_tab() -> None:
    render_card("<h3>数据检查</h3><p>检查原职群、原能力资格、新职群、新等级、评价等级和系数匹配情况。系统不再根据原能力资格或通道推断新等级。</p>")
    cols = [
        "employee_id",
        "employee_name",
        "original_job_family",
        "original_qualification",
        "new_job_family",
        "new_job_family_name",
        "new_grade",
        "coefficient_group",
        "structure_status",
        "structure_note",
    ]
    st.subheader("数据检查明细")
    display_table_cn(st.session_state.results["structure"][cols])
    st.subheader("异常清单")
    issues = st.session_state.results["issues"]
    if issues.empty:
        render_card(f"<h3>{icon_title('check', '数据检查通过')}</h3><p>当前未发现异常，可以进行方案测算与对比分析。</p>")
    else:
        error_count = int(issues["severity"].eq("error").sum()) if "severity" in issues.columns else len(issues)
        warning_count = int(issues["severity"].eq("warning").sum()) if "severity" in issues.columns else 0
        render_card(f"<h3>{icon_title('alert', f'发现 {len(issues):,} 条数据问题')}</h3><p>其中 {error_count:,} 条为错误，{warning_count:,} 条为提醒。请优先处理错误数据。</p>")
        display_table_cn(issues)


def render_coefficients_tab() -> None:
    render_card("<h3>方案系数设置</h3><p>调整方案A和方案B系数后，点击“重新测算”刷新分析与导出结果。</p>")
    top_cols = st.columns([1, 1, 4])
    with top_cols[0]:
        if st.button("重新测算", use_container_width=True):
            refresh_results()
            st.success("已按当前系数重新测算。")
    with top_cols[1]:
        if st.button("恢复默认系数", use_container_width=True):
            st.session_state.option_a_matrix = option_a_long_to_matrix(get_default_option_a_coefficients())
            st.session_state.option_b_matrix = option_b_long_to_matrix(get_default_option_b_coefficients())
            refresh_results()
            st.success("已恢复默认系数。")

    st.subheader("方案A系数设置")
    option_a_display = rename_columns_cn(st.session_state.option_a_matrix)
    edited_a = st.data_editor(
        option_a_display,
        use_container_width=True,
        hide_index=True,
        disabled=[cn_label("new_job_family"), cn_label("new_job_family_name")],
        column_config={rating: st.column_config.NumberColumn(rating, min_value=0.0, step=0.01, format="%.2f") for rating in VALID_RATINGS},
        key="option_a_editor",
    )
    st.session_state.option_a_matrix = normalize_uploaded_columns(edited_a)

    st.subheader("方案B系数设置")
    option_b_display = rename_columns_cn(st.session_state.option_b_matrix)
    edited_b = st.data_editor(
        option_b_display,
        use_container_width=True,
        hide_index=True,
        disabled=[cn_label("new_job_family"), cn_label("new_job_family_name"), cn_label("new_grade")],
        column_config={rating: st.column_config.NumberColumn(rating, min_value=0.0, step=0.01, format="%.2f") for rating in VALID_RATINGS},
        key="option_b_editor",
    )
    st.session_state.option_b_matrix = normalize_uploaded_columns(edited_b)


def render_analysis_tab() -> None:
    results = st.session_state.results
    overall = results["overall"]
    before_total = overall.loc[overall["指标"].eq("总奖金成本"), "Before"].iloc[0]
    option_a_total = overall.loc[overall["指标"].eq("总奖金成本"), "Option A"].iloc[0]
    option_b_total = overall.loc[overall["指标"].eq("总奖金成本"), "Option B"].iloc[0]
    headcount = overall.loc[overall["指标"].eq("参与人数"), "Before"].iloc[0]
    option_a_pct = safe_pct(option_a_total - before_total, before_total)
    option_b_pct = safe_pct(option_b_total - before_total, before_total)

    cols = st.columns(7)
    with cols[0]:
        metric_card("参与人数", format_scalar(headcount, "count"), icon="users")
    with cols[1]:
        metric_card("现行方案总奖金", format_money(before_total), icon="yen")
    with cols[2]:
        metric_card("方案A总奖金", format_money(option_a_total), icon="yen")
    with cols[3]:
        metric_card("方案B总奖金", format_money(option_b_total), icon="yen")
    with cols[4]:
        metric_card("方案A较现行", format_pct(option_a_pct), icon="trend-up", delta="变化率", delta_color=YNC_COLORS["positive"] if option_a_pct >= 0 else YNC_COLORS["negative"])
    with cols[5]:
        metric_card("方案B较现行", format_pct(option_b_pct), icon="trend-down", delta="变化率", delta_color=YNC_COLORS["positive"] if option_b_pct >= 0 else YNC_COLORS["negative"])
    with cols[6]:
        metric_card("异常数量", f"{len(results['issues']):,}", icon="alert")

    st.markdown('<div class="section-title">图表分析</div><div class="section-subtitle">用于快速判断成本变化、职群分布、绩效区分度与员工影响。</div>', unsafe_allow_html=True)
    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_total_cost_chart(results["calc"])
    with chart_cols[1]:
        render_new_family_chart(results["calc"])
    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_rating_average_chart(results["calc"])
    with chart_cols[1]:
        render_change_distribution_chart(results["calc"], "方案A")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_change_distribution_chart(results["calc"], "方案B")
    with chart_cols[1]:
        selected_scenario = st.radio("奖金变化影响 Top 10", ["方案A", "方案B"], horizontal=True, key="top_impact_scenario")
        render_top_impact_chart(results["calc"], selected_scenario)

    st.markdown('<div class="section-title">汇总表格</div>', unsafe_allow_html=True)
    subtabs = st.tabs(["总体对比", "原职群对比", "新职群对比", "新等级对比", "评价等级对比"])
    with subtabs[0]:
        st.dataframe(format_overall_summary_cn(results["overall"]), use_container_width=True, hide_index=True)
    with subtabs[1]:
        display_table_cn(results["original_family"])
    with subtabs[2]:
        display_table_cn(results["new_family"])
    with subtabs[3]:
        display_table_cn(results["grade"])
    with subtabs[4]:
        display_table_cn(results["rating"])

    st.markdown('<div class="section-title">员工影响清单</div>', unsafe_allow_html=True)
    display_table_cn(results["impact"], height=360)
    with st.expander("查看测算明细"):
        display_table_cn(results["calc"], height=420)


def render_export_tab() -> None:
    render_card("<h3>结果导出</h3><p>导出文件包含方案系数、数据检查、测算明细、汇总分析和异常清单。</p>")
    results = st.session_state.results
    summaries = {
        "overall": results["overall"],
        "original_family": results["original_family"],
        "new_family": results["new_family"],
        "grade": results["grade"],
        "rating": results["rating"],
    }
    export_buffer = export_results_to_excel(
        raw_employee_df=st.session_state.employee_df,
        structure_df=results["structure"],
        before_coeff=results["before_coeff"],
        option_a_matrix=st.session_state.option_a_matrix,
        option_b_matrix=st.session_state.option_b_matrix,
        calc_df=results["calc"],
        summaries=summaries,
        validation_issues=results["issues"],
    )
    filename = f"YNC_奖金方案测算结果_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    st.download_button(
        "导出测算结果",
        data=export_buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def render_detail_tab() -> None:
    render_card(f"<h3>{icon_title('table', '明细结果')}</h3><p>查看员工级测算明细与奖金变化影响清单。字段已按客户展示口径中文化。</p>")
    st.subheader("员工影响清单")
    display_table_cn(st.session_state.results["impact"], height=360)
    st.subheader("测算明细")
    display_table_cn(st.session_state.results["calc"], height=520)


def render_top_nav() -> str:
    nav_items = [
        ("home", "⌂", "首页"),
        ("template", "⇩", "模板下载"),
        ("upload", "⇧", "数据上传"),
        ("check", "✓", "数据检查"),
        ("coefficients", "⚙", "方案系数"),
        ("analysis", "▥", "对比分析"),
        ("detail", "▤", "明细结果"),
        ("export", "▣", "结果导出"),
    ]
    current = st.query_params.get("page", "home")
    valid_keys = {key for key, _, _ in nav_items}
    if current not in valid_keys:
        current = "home"
    buttons = []
    for key, icon, label in nav_items:
        active = " active" if key == current else ""
        buttons.append(f'<a class="nav-button{active}" href="?page={key}">{icon}&nbsp;{label}</a>')
    st.markdown(f'<div class="top-nav-card"><div class="top-nav-grid">{"".join(buttons)}</div></div>', unsafe_allow_html=True)
    return current


def main() -> None:
    apply_custom_css()
    initialize_state()
    render_brand_bar()
    page = render_top_nav()

    if page == "home":
        render_home_tab()
    elif page == "template":
        render_download_tab()
    elif page == "upload":
        render_upload_tab()
    elif page == "check":
        render_data_check_tab()
    elif page == "coefficients":
        render_coefficients_tab()
    elif page == "analysis":
        render_analysis_tab()
    elif page == "detail":
        render_detail_tab()
    elif page == "export":
        render_export_tab()


if __name__ == "__main__":
    main()
