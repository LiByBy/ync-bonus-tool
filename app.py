from __future__ import annotations

from datetime import datetime
from hmac import compare_digest
from io import BytesIO
from pathlib import Path
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
    "increase": "#B11226",
    "decrease": "#5E8C61",
    "positive": "#B11226",
    "negative": "#5E8C61",
    "background": "#F7F4F3",
    "surface": "rgba(255, 255, 255, 0.76)",
    "surface_strong": "rgba(255, 255, 255, 0.92)",
    "text": "#1F2933",
    "muted_text": "#6B7280",
    "border": "rgba(177, 18, 38, 0.14)",
    "shadow": "0 10px 30px rgba(65, 18, 24, 0.08)",
}

VALID_RATINGS = ["A", "B+", "B", "C+", "C", "D", "E"]
APP_DIR = Path(__file__).resolve().parent
DEFAULT_EMPLOYEE_DATA_PATH = APP_DIR / "data" / "default_employee_data.xlsx"
VALID_JOB_FAMILIES = ["综合职（非销售）", "综合职（销售）", "现场职", "技术职"]
VALID_QUALIFICATIONS = ["理事级", "经营级", "基干级", "指导级", "担当级"]
VALID_NEW_JOB_FAMILIES = ["M", "T", "S", "O", "G"]
VALID_EMPLOYEE_TYPES = ["正式", "中方", "日方", "劳务"]
FIXED_LINKAGE_EMPLOYEE_TYPES = ["中方", "日方"]
BLANK_RATING_HALF_LINKAGE_EMPLOYEE_TYPES = ["正式", "劳务"]
BLANK_RATING_FIXED_LINKAGE = 1.00
BLANK_RATING_HALF_LINKAGE = 0.50
SPECIAL_M4_COEFFICIENT_RULES = {
    "综合职（销售）": {
        "qualification": "基干级",
        "option_a_family": "S",
        "option_a_family_name": "营业职群",
        "option_b_family": "S",
        "option_b_grade": "S4",
    },
    "技术职": {
        "qualification": "基干级",
        "option_a_family": "T",
        "option_a_family_name": "技术职群",
        "option_b_family": "T",
        "option_b_grade": "T4",
    },
}
REQUIRED_COLUMNS = [
    "employee_id",
    "employee_name",
    "employee_type",
    "original_job_family",
    "original_qualification",
    "new_job_family",
    "new_grade",
    "bonus_base",
    "attendance_rate",
    "eligible",
]
EMPLOYEE_COLUMNS = [
    "employee_id",
    "employee_name",
    "employee_type",
    "department",
    "original_job_family",
    "original_qualification",
    "new_job_family",
    "new_grade",
    "rating",
    "bonus_base",
    "attendance_rate",
    "eligible",
    "remarks",
]
MONEY_COLUMNS = ["before_bonus", "option_a_bonus", "option_b_bonus", "option_a_change_amount", "option_b_change_amount"]
PCT_COLUMNS = ["option_a_change_pct", "option_b_change_pct", "rating_share", "attendance_rate"]
COEFF_COLUMNS = [
    "before_coefficient",
    "option_a_coefficient",
    "option_b_coefficient",
    "coefficient",
    "before_company_bonus_coefficient",
    "option_a_company_bonus_coefficient",
    "option_b_company_bonus_coefficient",
    "company_bonus_coefficient",
]
COUNT_COLUMNS = ["headcount", "count", "employee_count"]
SCENARIO_LABELS = {"Before": "现行方案", "Option A": "方案A", "Option B": "方案B"}
SCENARIO_LABELS_JA = {"Before": "現行制度", "Option A": "案A", "Option B": "案B"}
SCENARIO_COLORS = {
    "现行方案": "#6B7280",
    "方案A": "#B11226",
    "方案B": "#C87A83",
    "increase": "#B11226",
    "decrease": "#5E8C61",
    "positive": "#B11226",
    "negative": "#5E8C61",
}
FAMILY_COLORS = {"M": "#7F0D1B", "T": "#B11226", "S": "#C87A83", "O": "#D9A441", "G": "#50606F"}
RATING_COLORS = {
    "A": "#7F0D1B",
    "B+": "#B11226",
    "B": "#C87A83",
    "C+": "#D9A441",
    "C": "#8C9AA6",
    "D": "#50606F",
    "E": "#A6ADB5",
}
COLUMN_LABELS = {
    "employee_id": "员工编号",
    "employee_name": "姓名",
    "employee_type": "员工性质",
    "department": "部门",
    "original_job_family": "原职群",
    "original_qualification": "原能力资格",
    "new_job_family": "新职群",
    "new_job_family_name": "新职群名称",
    "new_grade": "新等级",
    "grade_order": "等级序号",
    "coefficient_group": "系数组",
    "rating": "评价等级",
    "bonus_base": "奖金基数",
    "attendance_rate": "出勤率",
    "eligible": "是否参与测算",
    "remarks": "备注",
    "scenario": "方案",
    "coefficient": "评价联动系数",
    "company_bonus_coefficient": "公司整体奖金系数",
    "before_coefficient": "现行方案评价联动系数",
    "option_a_coefficient": "方案A评价联动系数",
    "option_b_coefficient": "方案B评价联动系数",
    "before_company_bonus_coefficient": "现行方案公司整体奖金系数",
    "option_a_company_bonus_coefficient": "方案A公司整体奖金系数",
    "option_b_company_bonus_coefficient": "方案B公司整体奖金系数",
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
    "rating_share": "评价占比",
    "group_total": "组内人数",
    "group_label": "分析维度",
    "total_bonus": "奖金总额",
    "average_bonus": "人均奖金",
    "max_bonus": "最高奖金",
    "min_bonus": "最低奖金",
    "Before": "现行方案",
    "Option A": "方案A",
    "Option B": "方案B",
}
COLUMN_LABELS_JA = {
    "employee_id": "社員番号",
    "employee_name": "氏名",
    "employee_type": "社員区分",
    "department": "部門",
    "original_job_family": "現行職群",
    "original_qualification": "現行資格等級",
    "new_job_family": "新職群",
    "new_job_family_name": "新職群名",
    "new_grade": "新等級",
    "grade_order": "等級順序",
    "coefficient_group": "係数グループ",
    "rating": "評価結果",
    "bonus_base": "賞与基礎額",
    "attendance_rate": "出勤率",
    "eligible": "試算対象",
    "remarks": "備考",
    "scenario": "制度案",
    "coefficient": "評価連動係数",
    "company_bonus_coefficient": "会社全体賞与係数",
    "before_coefficient": "現行制度 評価連動係数",
    "option_a_coefficient": "案A 評価連動係数",
    "option_b_coefficient": "案B 評価連動係数",
    "before_company_bonus_coefficient": "現行制度 会社全体賞与係数",
    "option_a_company_bonus_coefficient": "案A 会社全体賞与係数",
    "option_b_company_bonus_coefficient": "案B 会社全体賞与係数",
    "before_bonus": "現行制度 賞与額",
    "option_a_bonus": "案A 賞与額",
    "option_b_bonus": "案B 賞与額",
    "option_a_change_amount": "案A 対現行増減額",
    "option_a_change_pct": "案A 対現行増減率",
    "option_b_change_amount": "案B 対現行増減額",
    "option_b_change_pct": "案B 対現行増減率",
    "structure_status": "データ状態",
    "structure_note": "チェック内容",
    "issue_type": "エラー種別",
    "issue_detail": "エラー内容",
    "severity": "重要度",
    "headcount": "人数",
    "count": "件数",
    "rating_share": "評価構成比",
    "group_total": "グループ内人数",
    "group_label": "分析軸",
    "total_bonus": "賞与総額",
    "average_bonus": "平均賞与額",
    "max_bonus": "最高賞与額",
    "min_bonus": "最低賞与額",
    "Before": "現行制度",
    "Option A": "案A",
    "Option B": "案B",
}
FIELD_ALIASES = {
    "员工编号": "employee_id",
    "姓名": "employee_name",
    "员工性质": "employee_type",
    "部门": "department",
    "原职群": "original_job_family",
    "原能力资格": "original_qualification",
    "新职群": "new_job_family",
    "新等级": "new_grade",
    "评价等级": "rating",
    "奖金基数": "bonus_base",
    "月度奖金基数": "bonus_base",
    "月奖金基数": "bonus_base",
    "出勤率": "attendance_rate",
    "出勤比例": "attendance_rate",
    "折算系数": "attendance_rate",
    "是否参与测算": "eligible",
    "备注": "remarks",
    "社員番号": "employee_id",
    "氏名": "employee_name",
    "社員区分": "employee_type",
    "部門": "department",
    "現行職群": "original_job_family",
    "現行資格等級": "original_qualification",
    "新職群": "new_job_family",
    "新等級": "new_grade",
    "評価結果": "rating",
    "賞与基礎額": "bonus_base",
    "出勤率": "attendance_rate",
    "試算対象": "eligible",
    "備考": "remarks",
}

LANGUAGE_LABELS = {"zh": "中文", "ja": "日本語"}
APP_COPY_JA = {
    "YNC 奖金系数方案测算工具": "YNC 賞与係数シナリオ試算ツール",
    "数据状态": "データ状態",
    "员工数量": "社員数",
    "异常数量": "エラー件数",
    "当前测算": "試算時点",
    "界面语言": "表示言語",
    "页面导航": "ページナビゲーション",
    "当前数据状态": "現在のデータ状態",
    "最近测算": "直近試算",
    "已上传": "アップロード済み",
    "未上传（默认测算数据）": "未アップロード（標準サンプルデータ）",
    "尚未测算": "未試算",
    "首页": "ホーム",
    "模板下载": "テンプレート",
    "数据上传": "データ取込",
    "数据检查": "データチェック",
    "方案系数": "係数設定",
    "对比分析": "比較分析",
    "明细结果": "明細結果",
    "结果导出": "結果出力",
    "标准化导入": "標準テンプレート取込",
    "方案系数调整": "係数調整",
    "可视化对比分析": "可視化比較分析",
    "流程步骤": "業務フロー",
    "客户仅需填写员工数据，规则与方案参数由顾问维护。": "クライアントは社員データのみ入力し、制度ルールと係数パラメータはコンサルタント側で管理します。",
    "用于现行方案、方案A、方案B的奖金成本测算、员工影响分析与方案对比。": "現行制度、案A、案Bの賞与コスト試算、個人別影響分析、制度案比較に使用します。",
    "支持方案A、方案B系数在线编辑，调整后自动刷新测算结果。": "案A・案Bの係数を画面上で編集でき、調整後に試算結果へ反映します。",
    "支持总成本、职群、等级、评价等级和员工影响分析。": "総人件費影響、職群、等級、評価結果、個人別影響を可視化します。",
    "1 下载模板 → 2 上传员工数据 → 3 调整方案系数 → 4 查看对比分析 → 5 导出结果": "1 テンプレート取得 → 2 社員データ取込 → 3 係数調整 → 4 比較分析確認 → 5 結果出力",
    "客户仅需填写标准模板中的 <b>01_员工数据</b> Sheet。现行方案使用原职群和原能力资格；方案A/方案B使用上传的新职群和新等级。": "標準テンプレートの <b>01_社員データ</b> シートに入力してください。現行制度は現行職群・現行資格等級を使用し、案A/案Bはアップロードされた新職群・新等級を使用します。",
    "下载标准模板": "標準テンプレートをダウンロード",
    "数据上传": "データ取込",
    "上传客户填写后的 Excel。系统优先读取“01_员工数据”Sheet，也兼容中文表头和旧版英文表头。": "入力済みExcelをアップロードしてください。システムは「01_员工数据」シートを優先して読み込み、中国語ヘッダーおよび旧英語ヘッダーにも対応します。",
    "上传员工数据 Excel": "社員データExcelをアップロード",
    "员工数据预览": "社員データプレビュー",
    "尚未上传员工数据": "社員データ未アップロード",
    "当前显示的是内置默认测算数据。上传客户数据后将自动替换为客户数据。": "現在は標準サンプルデータを表示しています。クライアントデータをアップロードすると自動で置き換わります。",
    "已成功读取": "読み込み完了：",
    "条员工数据。": "件の社員データ",
    "读取失败": "読み込みに失敗しました",
    "检查原职群、原能力资格、新职群、新等级、评价等级和系数匹配情况。系统不再根据原能力资格或通道推断新等级。": "現行職群、現行資格等級、新職群、新等級、評価結果、係数マッチングを確認します。現行資格等級やキャリアトラックから新等級を推定しません。",
    "数据检查明细": "データチェック明細",
    "异常清单": "エラー一覧",
    "数据检查通过": "データチェック完了",
    "当前未发现异常，可以进行方案测算与对比分析。": "エラーは検出されていません。制度案の試算と比較分析に進めます。",
    "发现数据问题": "データエラーを検出",
    "共计": "合計",
    "条": "件",
    "其中": "内訳",
    "条为错误": "件がエラー",
    "条为提醒": "件が確認事項",
    "方案系数设置": "係数設定",
    "奖金 = 奖金基数 × 公司整体奖金系数 × 评价联动系数 × 出勤率。调整参数后，点击“重新测算”刷新分析与导出结果。": "賞与額 = 賞与基礎額 × 会社全体賞与係数 × 評価連動係数 × 出勤率。パラメータ調整後、「再試算」をクリックして分析・出力結果を更新します。",
    "规则补充：员工性质为“中方”或“日方”的人员，三套方案的评价联动系数均按 1.00 计算；评价结果为空时，正式和劳务人员按 0.50 计算，中方和日方人员按 1.00 计算。": "ルール補足：社員区分が「出資者側派遣社員（中方）」または「出資者側派遣社員（日方）」の社員は、3制度案すべて評価連動係数を 1.00 として計算します。評価結果が空欄の場合、現地正社員・労務工は 0.50、出資者側派遣社員（中方・日方）は 1.00 として計算します。",
    "重新测算": "再試算",
    "重置为模板系数": "テンプレート係数に戻す",
    "已重置为模板系数。": "テンプレート係数に戻しました。",
    "已按当前系数重新测算。": "現在の係数で再試算しました。",
    "登录": "ログイン",
    "用户名": "ユーザー名",
    "密码": "パスワード",
    "进入工具": "ツールに入る",
    "登录成功。": "ログインしました。",
    "用户名或密码不正确。": "ユーザー名またはパスワードが正しくありません。",
    "登录配置未完成，请先在 Streamlit Secrets 中配置用户名和密码。": "ログイン設定が未完了です。Streamlit Secrets にユーザー名とパスワードを設定してください。",
    "请输入用户名和密码后进入测算工具。": "ユーザー名とパスワードを入力して試算ツールに入ってください。",
    "公司整体奖金系数设置": "会社全体賞与係数設定",
    "现行方案评价联动系数设置": "現行制度 評価連動係数設定",
    "方案A评价联动系数设置": "案A 評価連動係数設定",
    "方案B评价联动系数设置": "案B 評価連動係数設定",
    "参与人数": "対象人数",
    "现行方案总奖金": "現行制度 賞与総額",
    "方案A总奖金": "案A 賞与総額",
    "方案B总奖金": "案B 賞与総額",
    "方案A较现行": "案A 対現行",
    "方案B较现行": "案B 対現行",
    "变化率": "増減率",
    "图表分析": "チャート分析",
    "用于快速判断成本变化、职群分布、绩效区分度与员工影响。": "コスト変動、職群別分布、評価メリハリ、個人別影響を素早く確認します。",
    "员工性质": "社員区分",
    "刷新图表": "チャート更新",
    "已刷新图表分析。": "チャート分析を更新しました。",
    "请至少选择一种员工性质用于图表展示。": "チャート表示用に少なくとも1つの社員区分を選択してください。",
    "评价结果分析": "評価結果分析",
    "用于观察评价结果整体分布，以及不同新职群、新等级内部的评价结构差异。": "評価結果の全体分布、および新職群・新等級別の評価構成差を確認します。",
    "奖金变化影响 Top 10": "賞与増減影響 Top 10",
    "汇总表格": "集計表",
    "员工影响清单": "個人別影響リスト",
    "查看测算明细": "試算明細を表示",
    "导出文件包含方案系数、数据检查、测算明细、汇总分析和异常清单。": "出力ファイルには、係数設定、データチェック、試算明細、集計分析、エラー一覧が含まれます。",
    "导出测算结果": "試算結果を出力",
    "查看员工级测算明细与奖金变化影响清单。字段已按客户展示口径中文化。": "社員単位の試算明細と賞与増減影響リストを確認します。項目名はクライアント提示用に整備しています。",
    "总体对比": "全体比較",
    "原职群对比": "現行職群別比較",
    "新职群对比": "新職群別比較",
    "新等级对比": "新等級別比較",
    "评价等级对比": "評価結果別比較",
    "评价结果分布": "評価結果分布",
    "职群评价占比": "職群別評価構成",
    "等级评价占比": "等級別評価構成",
    "测算明细": "試算明細",
    "指标": "指標",
    "总奖金成本": "賞与総額",
    "较现行方案变化率": "対現行増減率",
    "较现行方案变化额": "対現行増減額",
    "最高奖金": "最高賞与額",
    "最低奖金": "最低賞与額",
    "现行方案": "現行制度",
    "方案A": "案A",
    "方案B": "案B",
    "正式": "現地正社員",
    "中方": "出資者側派遣社員（中方）",
    "日方": "出資者側派遣社員（日方）",
    "劳务": "労務工",
    "三套方案总奖金成本对比": "3制度案の賞与総額比較",
    "按新职群的奖金成本对比": "新職群別の賞与コスト比較",
    "按评价等级的人均奖金对比": "評価結果別の平均賞与額比較",
    "方案A较现行变化额分布": "案A 対現行 増減額分布",
    "方案B较现行变化额分布": "案B 対現行 増減額分布",
    "奖金变化影响最大的员工（方案A）": "賞与増減影響が大きい社員（案A）",
    "奖金变化影响最大的员工（方案B）": "賞与増減影響が大きい社員（案B）",
    "按新职群的评价结果占比": "新職群別の評価結果構成比",
    "按新等级的评价结果占比": "新等級別の評価結果構成比",
    "选择新职群": "新職群を選択",
    "新职群": "新職群",
    "新等级": "新等級",
    "评价等级": "評価結果",
    "评价占比": "評価構成比",
    "人数": "人数",
    "占比": "構成比",
    "奖金总额": "賞与総額",
    "总奖金成本": "賞与総額",
    "人均奖金": "平均賞与額",
    "变化额": "増減額",
    "员工数量": "社員数",
    "员工": "社員",
    "方向": "方向",
    "增加": "増加",
    "减少": "減少",
    "方案": "制度案",
    "较现行变化额": " 対現行 増減額",
    "该图展示参与测算员工的评价结果人数和占比。": "試算対象社員の評価結果別人数と構成比を表示します。",
    "该图展示不同新职群内部的评价结果占比，用于观察评价结构差异。": "新職群別の評価結果構成比を表示し、評価分布の偏りを確認します。",
    "该图展示所选新职群下，各新等级内部的评价结果占比，用于观察等级间评价结构差异。": "選択した新職群における新等級別の評価結果構成比を表示し、等級間の評価分布差を確認します。",
    "当前筛选条件下暂无可展示的新等级评价结果。": "現在の絞り込み条件では表示可能な新等級別評価結果がありません。",
    "该图用于比较三套方案下的总奖金成本变化。": "3制度案における賞与総額の変動を比較します。",
    "该图展示不同新职群在各方案下的奖金成本分布。": "各制度案における新職群別の賞与コスト分布を表示します。",
    "该图用于观察高绩效与低绩效员工之间的激励差异是否被拉开。": "高評価者と低評価者のインセンティブ差が適切に設計されているかを確認します。",
    "该图用于识别方案调整后个人奖金变化是否过于集中或存在极端值。": "制度改定後の個人別賞与増減が集中していないか、極端値がないかを確認します。",
    "该图展示奖金变化绝对值最大的员工，用于识别重点沟通对象。": "賞与増減額の絶対値が大きい社員を表示し、重点確認・説明対象を特定します。",
}

VALUE_LABELS_JA = {
    "employee_type": {"正式": "現地正社員", "中方": "出資者側派遣社員（中方）", "日方": "出資者側派遣社員（日方）", "劳务": "労務工"},
    "eligible": {"Y": "対象", "N": "対象外"},
    "severity": {"error": "エラー", "warning": "確認"},
    "new_job_family_name": {"管理职群": "管理職群", "技术职群": "技術職群", "营业职群": "営業職群", "现场职群": "現場職群", "综合职群": "総合職群"},
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
        .top-nav-card div[data-testid="column"] {{
            min-width: 118px;
        }}
        .top-nav-card .stButton > button {{
            width: 100%;
            min-height: 38px;
            border-radius: 12px;
            padding: 8px 10px;
            font-size: 14px;
            font-weight: 500;
            color: var(--ync-text);
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(177,18,38,0.12);
            box-shadow: none;
            white-space: nowrap;
        }}
        .top-nav-card .stButton > button:hover {{
            color: var(--ync-red-dark);
            background: rgba(177,18,38,0.06);
            border-color: rgba(177,18,38,0.20);
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
        .brand-right {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 12px;
            min-width: 0;
        }}
        .language-switch {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px;
            border-radius: 999px;
            background: rgba(177,18,38,0.05);
            border: 1px solid rgba(177,18,38,0.12);
        }}
        .language-switch a {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 64px;
            height: 28px;
            padding: 0 12px;
            border-radius: 999px;
            color: var(--ync-muted);
            text-decoration: none !important;
            font-size: 12px;
            line-height: 1;
            white-space: nowrap;
        }}
        .language-switch a.active {{
            background: var(--ync-red);
            color: #FFFFFF;
            box-shadow: 0 4px 10px rgba(177,18,38,0.14);
        }}
        @media (max-width: 1200px) {{
            .brand-bar {{
                grid-template-columns: 1fr;
            }}
            .brand-right {{
                align-items: flex-start;
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
        .auto-insight-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin: 4px 0 18px;
        }}
        .auto-insight-card {{
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(177,18,38,0.12);
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 8px 22px rgba(65,18,24,0.055);
            min-height: 146px;
        }}
        .auto-insight-title {{
            color: var(--ync-red-dark);
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 9px;
        }}
        .auto-insight-text {{
            color: var(--ync-text);
            font-size: 13px;
            line-height: 1.6;
        }}
        @media (max-width: 1180px) {{
            .auto-insight-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}
        @media (max-width: 720px) {{
            .auto-insight-grid {{
                grid-template-columns: 1fr;
            }}
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


def get_auth_credentials() -> Tuple[str, str]:
    try:
        auth_config = st.secrets.get("auth", {})
    except Exception:
        auth_config = {}
    return str(auth_config.get("username", "")), str(auth_config.get("password", ""))


def ensure_authenticated() -> bool:
    if st.session_state.get("authenticated", False):
        return True

    username, password = get_auth_credentials()
    st.markdown(
        f"""
        <div class="brand-bar">
            <div>
                <div class="brand-title">{tr("YNC 奖金系数方案测算工具")}</div>
                <div class="brand-subtitle">Bonus Coefficient Scenario Analyzer</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not username or not password:
        render_card(f"<h3>{tr('登录')}</h3><p>{tr('登录配置未完成，请先在 Streamlit Secrets 中配置用户名和密码。')}</p>")
        return False

    with st.form("login_form"):
        render_card(f"<h3>{tr('登录')}</h3><p>{tr('请输入用户名和密码后进入测算工具。')}</p>")
        input_username = st.text_input(tr("用户名"))
        input_password = st.text_input(tr("密码"), type="password")
        submitted = st.form_submit_button(tr("进入工具"), use_container_width=True)

    if submitted:
        valid_username = compare_digest(input_username, username)
        valid_password = compare_digest(input_password, password)
        if valid_username and valid_password:
            st.session_state.authenticated = True
            st.success(tr("登录成功。"))
            st.rerun()
        else:
            st.error(tr("用户名或密码不正确。"))
    return False


def get_language() -> str:
    raw_lang = st.query_params.get("lang", "zh")
    lang = raw_lang[0] if isinstance(raw_lang, list) else raw_lang
    return "ja" if lang == "ja" else "zh"


def tr(text: str) -> str:
    if get_language() == "ja":
        return APP_COPY_JA.get(text, text)
    return text


def scenario_labels() -> Dict[str, str]:
    return SCENARIO_LABELS_JA if get_language() == "ja" else SCENARIO_LABELS


def scenario_display_order() -> List[str]:
    labels = scenario_labels()
    return [labels["Before"], labels["Option A"], labels["Option B"]]


def scenario_color_map() -> Dict[str, str]:
    before, option_a, option_b = scenario_display_order()
    return {
        before: SCENARIO_COLORS["现行方案"],
        option_a: SCENARIO_COLORS["方案A"],
        option_b: SCENARIO_COLORS["方案B"],
        tr("增加"): SCENARIO_COLORS["increase"],
        tr("减少"): SCENARIO_COLORS["decrease"],
    }


def localize_series_values(series: pd.Series, column: str) -> pd.Series:
    if get_language() != "ja":
        return series
    value_map = VALUE_LABELS_JA.get(column)
    if value_map:
        return series.replace(value_map)
    return series


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
    status = tr("已上传") if uploaded else tr("未上传（默认测算数据）")
    calc_time = st.session_state.get("last_calc_time", tr("尚未测算"))
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
                <div class="brand-title">{tr("YNC 奖金系数方案测算工具")}</div>
                <div class="brand-subtitle">Bonus Coefficient Scenario Analyzer</div>
            </div>
            <div class="brand-right">
                <div class="status-pill-wrap">
                    <div class="status-pill">{tr("数据状态")}：{status["status"]}</div>
                    <div class="status-pill">{tr("员工数量")}：{status["employee_count"]}</div>
                    <div class="status-pill">{tr("异常数量")}：{status["issue_count"]}</div>
                    <div class="status-pill">{tr("当前测算")}：{status["calc_time"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_language_switch() -> None:
    current_lang = get_language()
    current_label = LANGUAGE_LABELS[current_lang]
    lang_cols = st.columns([7, 1.6])
    with lang_cols[1]:
        selected_label = st.segmented_control(
            tr("界面语言"),
            options=["中文", "日本語"],
            default=current_label,
            key="language_segmented_control",
            label_visibility="collapsed",
        )
    selected_lang = "ja" if selected_label == "日本語" else "zh"
    if selected_lang != current_lang:
        st.query_params["lang"] = selected_lang
        if "page" not in st.query_params:
            st.query_params["page"] = "home"
        st.rerun()


def cn_label(column: str) -> str:
    labels = COLUMN_LABELS_JA if get_language() == "ja" else COLUMN_LABELS
    return labels.get(column, column)


def rename_columns_cn(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df.copy()
    original_columns = list(renamed.columns)
    if get_language() == "ja":
        for col in original_columns:
            if col in renamed.columns:
                renamed[col] = localize_series_values(renamed[col], col)
    renamed = renamed.rename(columns={col: cn_label(col) for col in renamed.columns})
    scenario_label = cn_label("scenario")
    if scenario_label in renamed.columns:
        renamed[scenario_label] = renamed[scenario_label].replace(scenario_labels())
    return renamed


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    reverse_labels = {label: key for key, label in COLUMN_LABELS.items()}
    reverse_labels.update({label: key for key, label in COLUMN_LABELS_JA.items()})
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
        elif original_col in PCT_COLUMNS or original_col.endswith("_pct") or "变化率" in label or "占比" in label:
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
                    f"color: {YNC_COLORS['increase']}; background-color: rgba(177,18,38,0.07)"
                    if pd.notna(value) and value > 0
                    else f"color: {YNC_COLORS['decrease']}; background-color: rgba(94,140,97,0.08)"
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
                tr("指标"): tr(metric),
                scenario_labels()["Before"]: "" if pd.isna(row["Before"]) else format_scalar(row["Before"], kind),
                scenario_labels()["Option A"]: "" if pd.isna(row["Option A"]) else format_scalar(row["Option A"], kind),
                scenario_labels()["Option B"]: "" if pd.isna(row["Option B"]) else format_scalar(row["Option B"], kind),
            }
        )
    return pd.DataFrame(rows)


def chart_base(chart: alt.Chart, title: str) -> alt.Chart:
    return chart.properties(
        title=tr(title),
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
    st.markdown(f'<div class="chart-note">{tr(text)}</div>', unsafe_allow_html=True)


def chart_analysis(text: str) -> None:
    st.markdown(f'<div class="chart-analysis">{text}</div>', unsafe_allow_html=True)


def employee_type_filter_summary(calc_df: pd.DataFrame, selected_employee_types: List[str]) -> str:
    df = eligible_detail(calc_df)
    if selected_employee_types:
        df = df[df["employee_type"].isin(selected_employee_types)]
    total = len(df)
    counts = df["employee_type"].value_counts()
    if get_language() == "ja":
        parts = [
            f"{VALUE_LABELS_JA['employee_type'].get(employee_type, employee_type)} {int(counts.get(employee_type, 0)):,}名"
            for employee_type in selected_employee_types
        ]
        return f"試算対象者数 {total:,}名（{ '、'.join(parts) }）。"
    parts = [f"{employee_type}{int(counts.get(employee_type, 0)):,}人" for employee_type in selected_employee_types]
    return f"参与测算人数 {total:,} 人，其中{'，'.join(parts)}。"


def total_cost_insight(calc_df: pd.DataFrame) -> str:
    data = create_total_cost_chart_data(calc_df).set_index("方案")["总奖金成本"]
    labels = scenario_labels()
    before = data.get(labels["Before"], np.nan)
    option_a = data.get(labels["Option A"], np.nan)
    option_b = data.get(labels["Option B"], np.nan)
    a_pct = safe_pct(option_a - before, before)
    b_pct = safe_pct(option_b - before, before)
    if get_language() == "ja":
        return f"案Aは現行制度比 {format_pct(a_pct)}、案Bは現行制度比 {format_pct(b_pct)} です。賞与総額の変動と予算制約との整合性を優先的に確認してください。"
    return f"方案A较现行方案变化 {format_pct(a_pct)}，方案B较现行方案变化 {format_pct(b_pct)}。可优先关注总成本变化与预算约束的匹配程度。"


def new_family_insight(calc_df: pd.DataFrame) -> str:
    df = create_new_job_family_summary(calc_df).copy()
    if df.empty:
        return "暂无可分析的新职群数据。"
    df["max_abs_change"] = df[["option_a_change_amount", "option_b_change_amount"]].abs().max(axis=1)
    row = df.sort_values("max_abs_change", ascending=False).iloc[0]
    family_name = row["new_job_family_name"]
    if get_language() == "ja":
        family_name = VALUE_LABELS_JA["new_job_family_name"].get(family_name, family_name)
        return f"{row['new_job_family']} {family_name} のコスト変動幅が相対的に大きくなっています。職群の位置づけと人員構成を踏まえて差異要因を確認してください。"
    family = f"{row['new_job_family']} {family_name}"
    return f"{family} 的成本变化幅度相对更高，建议结合职群定位和人员结构进一步解释差异来源。"


def rating_insight(calc_df: pd.DataFrame) -> str:
    data = create_rating_average_chart_data(calc_df)
    spread = data.groupby("方案")["人均奖金"].agg(lambda s: s.max() - s.min()).sort_values(ascending=False)
    if spread.empty:
        return "暂无可分析的评价等级数据。"
    if get_language() == "ja":
        return f"{spread.index[0]} の評価結果別平均賞与額の差が最も大きく、評価メリハリの強化状況を確認できます。"
    return f"{spread.index[0]} 的评价等级人均奖金差距最大，可用于观察绩效区分度是否被强化。"


def distribution_insight(calc_df: pd.DataFrame, scenario: str) -> str:
    data = create_change_distribution_data(calc_df)
    scenario_label = tr(scenario)
    data = data[data["方案"].eq(scenario_label)]
    if data.empty:
        return "暂无员工变化额数据。"
    median = data["变化额"].median()
    max_abs = data["变化额"].abs().max()
    if get_language() == "ja":
        return f"{scenario_label} の個人別増減額の中央値は {format_money(median)}、最大絶対増減額は {format_money(max_abs)} です。分布の端に位置する社員を重点的に確認してください。"
    return f"{scenario} 的个人变化额中位数为 {format_money(median)}，最大绝对变化为 {format_money(max_abs)}。建议关注分布尾部员工。"


def top_impact_insight(calc_df: pd.DataFrame, scenario: str) -> str:
    data = create_top_impact_chart_data(calc_df, scenario)
    if data.empty:
        return "暂无员工影响数据。"
    top = data.iloc[data["变化额"].abs().argmax()]
    if get_language() == "ja":
        return f"影響額が最も大きい社員は {top['员工']}、増減額は {format_money(top['变化额'])} です。重点確認・説明対象として管理してください。"
    return f"影响最大的员工为 {top['员工']}，变化额 {format_money(top['变化额'])}。建议纳入重点复核与沟通清单。"


def display_family_name(row: pd.Series) -> str:
    family_name = row.get("new_job_family_name", "")
    if get_language() == "ja":
        family_name = VALUE_LABELS_JA["new_job_family_name"].get(family_name, family_name)
    return f"{row.get('new_job_family', '')} {family_name}".strip()


def scenario_specs() -> List[Dict[str, str]]:
    return [
        {"label": "方案A", "bonus_col": "option_a_bonus", "change_col": "option_a_change_amount", "pct_col": "option_a_change_pct"},
        {"label": "方案B", "bonus_col": "option_b_bonus", "change_col": "option_b_change_amount", "pct_col": "option_b_change_pct"},
    ]


def auto_cost_insight(calc_df: pd.DataFrame) -> str:
    df = eligible_detail(calc_df)
    if df.empty:
        return "暂无可分析的成本数据。"
    before_total = df["before_bonus"].sum(skipna=True)
    messages = []
    family_summary = create_new_job_family_summary(calc_df)
    for spec in scenario_specs():
        scenario = spec["label"]
        scenario_total = df[spec["bonus_col"]].sum(skipna=True)
        change_pct = safe_pct(scenario_total - before_total, before_total)
        scenario_name = tr(scenario)
        if pd.isna(change_pct) or abs(change_pct) < 0.03:
            messages.append(f"{scenario_name}整体成本与现行方案基本保持一致。")
            continue
        family_change_col = spec["change_col"]
        if family_summary.empty:
            focus = "相关"
        elif change_pct < 0:
            row = family_summary.sort_values(family_change_col, ascending=True).iloc[0]
            focus = display_family_name(row)
        else:
            row = family_summary.sort_values(family_change_col, ascending=False).iloc[0]
            focus = display_family_name(row)
        if change_pct < 0:
            messages.append(f"{scenario_name}预计降低整体奖金成本 {format_pct(abs(change_pct))}，主要由于 {focus} 奖金系数调整。")
        else:
            messages.append(f"{scenario_name}预计提高整体奖金投入 {format_pct(change_pct)}，主要用于强化 {focus} 激励。")
    return "<br>".join(messages)


def auto_incentive_insight(calc_df: pd.DataFrame) -> str:
    df = eligible_detail(calc_df)
    if df.empty:
        return "暂无可分析的评价激励数据。"
    high = df[df["rating"].isin(["A", "B+"])]
    low = df[df["rating"].isin(["C", "D", "E"])]
    messages = []
    for spec in scenario_specs():
        scenario_name = tr(spec["label"])
        high_pct = safe_pct(high[spec["bonus_col"]].mean() - high["before_bonus"].mean(), high["before_bonus"].mean()) if not high.empty else np.nan
        low_pct = safe_pct(low[spec["bonus_col"]].mean() - low["before_bonus"].mean(), low["before_bonus"].mean()) if not low.empty else np.nan
        if pd.isna(high_pct):
            messages.append(f"{scenario_name}暂无 A/B+ 员工样本，无法判断高绩效激励变化。")
        elif high_pct > 0:
            messages.append(f"{scenario_name}提高高绩效员工奖金水平，A/B+员工平均奖金较现行方案提升 {format_pct(high_pct)}。")
        elif high_pct < 0:
            messages.append(f"{scenario_name}下 A/B+员工平均奖金较现行方案下降 {format_pct(abs(high_pct))}，需确认是否符合高绩效激励导向。")
        else:
            messages.append(f"{scenario_name}下 A/B+员工平均奖金与现行方案基本一致。")
        if not pd.isna(low_pct):
            messages[-1] += f" 低绩效员工（C/D/E）平均奖金变化为 {format_pct(low_pct)}。"
    return "<br>".join(messages)


def auto_family_impact_insight(calc_df: pd.DataFrame) -> str:
    family_summary = create_new_job_family_summary(calc_df)
    if family_summary.empty:
        return "暂无可分析的职群影响数据。"
    messages = []
    for spec in scenario_specs():
        scenario_name = tr(spec["label"])
        bonus_col = spec["bonus_col"]
        avg = family_summary.copy()
        avg["before_avg_bonus"] = np.where(avg["headcount"].gt(0), avg["before_bonus"] / avg["headcount"], np.nan)
        avg["scenario_avg_bonus"] = np.where(avg["headcount"].gt(0), avg[bonus_col] / avg["headcount"], np.nan)
        avg["avg_change_pct"] = np.where(avg["before_avg_bonus"].ne(0), (avg["scenario_avg_bonus"] - avg["before_avg_bonus"]) / avg["before_avg_bonus"], np.nan)
        avg["abs_avg_change_pct"] = avg["avg_change_pct"].abs()
        impact_row = avg.sort_values("abs_avg_change_pct", ascending=False).iloc[0]
        limited_row = avg.sort_values("abs_avg_change_pct", ascending=True).iloc[0]
        impact_family = display_family_name(impact_row)
        limited_family = display_family_name(limited_row)
        direction = "提升" if impact_row["avg_change_pct"] >= 0 else "下降"
        messages.append(f"{scenario_name}对 {impact_family} 影响最大，平均奖金{direction} {format_pct(abs(impact_row['avg_change_pct']))}；{limited_family} 变化有限。")
    return "<br>".join(messages)


def auto_risk_insight(calc_df: pd.DataFrame) -> str:
    df = eligible_detail(calc_df)
    if df.empty:
        return "暂无可分析的风险数据。"
    messages = []
    for spec in scenario_specs():
        scenario_name = tr(spec["label"])
        risk_count = int(df[spec["pct_col"]].le(-0.20).sum())
        if risk_count > 0:
            messages.append(f"{scenario_name}发现 {risk_count:,} 名员工奖金下降超过20%，建议进一步确认等级定位及绩效评价合理性。")
    rating_summary = create_rating_distribution_summary(calc_df)
    c_plus_share = rating_summary.loc[rating_summary["rating"].eq("C+"), "rating_share"]
    if not c_plus_share.empty and c_plus_share.iloc[0] > 0.60:
        messages.append(f"当前评价结果较集中，C+占比为 {format_pct(c_plus_share.iloc[0])}，绩效区分度可能有限。")
    if not messages:
        messages.append("未发现奖金下降超过20%的员工，评价结果集中度暂未触发风险提示。")
    return "<br>".join(messages)


def render_auto_insights(calc_df: pd.DataFrame) -> None:
    insights = [
        ("成本影响洞察", auto_cost_insight(calc_df)),
        ("激励导向洞察", auto_incentive_insight(calc_df)),
        ("职群影响洞察", auto_family_impact_insight(calc_df)),
        ("风险提示", auto_risk_insight(calc_df)),
    ]
    cards = "".join(
        f"""
        <div class="auto-insight-card">
            <div class="auto-insight-title">{title}</div>
            <div class="auto-insight-text">{text}</div>
        </div>
        """
        for title, text in insights
    )
    st.markdown(
        f"""
        <div class="section-title">方案分析摘要</div>
        <div class="section-subtitle">根据当前测算结果自动生成，无需人工输入。</div>
        <div class="auto-insight-grid">{cards}</div>
        """,
        unsafe_allow_html=True,
    )


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
    before_matrix = {
        ("综合职（非销售）", "理事级"): {"A": 2.40, "B+": 2.00, "B": 1.60, "C+": 1.00, "C": 0.20, "D": 0.10, "E": 0.00},
        ("综合职（非销售）", "经营级"): {"A": 2.30, "B+": 1.90, "B": 1.50, "C+": 1.00, "C": 0.50, "D": 0.10, "E": 0.00},
        ("综合职（非销售）", "基干级"): {"A": 1.75, "B+": 1.50, "B": 1.25, "C+": 1.00, "C": 0.70, "D": 0.35, "E": 0.00},
        ("综合职（非销售）", "指导级"): {"A": 1.60, "B+": 1.40, "B": 1.20, "C+": 1.00, "C": 0.80, "D": 0.40, "E": 0.00},
        ("综合职（非销售）", "担当级"): {"A": 1.45, "B+": 1.30, "B": 1.15, "C+": 1.00, "C": 0.85, "D": 0.50, "E": 0.00},
        ("综合职（销售）", "基干级"): {"A": 1.90, "B+": 1.70, "B": 1.40, "C+": 1.20, "C": 0.30, "D": 0.15, "E": 0.00},
        ("综合职（销售）", "指导级"): {"A": 1.80, "B+": 1.60, "B": 1.30, "C+": 1.15, "C": 0.40, "D": 0.20, "E": 0.00},
        ("综合职（销售）", "担当级"): {"A": 1.70, "B+": 1.50, "B": 1.20, "C+": 1.10, "C": 0.50, "D": 0.25, "E": 0.00},
        ("现场职", "理事级"): {"A": 2.40, "B+": 2.00, "B": 1.60, "C+": 1.00, "C": 0.20, "D": 0.10, "E": 0.00},
        ("现场职", "经营级"): {"A": 2.30, "B+": 1.90, "B": 1.50, "C+": 1.00, "C": 0.50, "D": 0.10, "E": 0.00},
        ("现场职", "基干级"): {"A": 1.75, "B+": 1.50, "B": 1.25, "C+": 1.00, "C": 0.70, "D": 0.35, "E": 0.00},
        ("现场职", "指导级"): {"A": 1.60, "B+": 1.40, "B": 1.20, "C+": 1.00, "C": 0.80, "D": 0.40, "E": 0.00},
        ("现场职", "担当级"): {"A": 1.45, "B+": 1.30, "B": 1.15, "C+": 1.00, "C": 0.85, "D": 0.50, "E": 0.00},
        ("技术职", "理事级"): {"A": 2.40, "B+": 2.00, "B": 1.60, "C+": 1.00, "C": 0.20, "D": 0.10, "E": 0.00},
        ("技术职", "经营级"): {"A": 2.30, "B+": 1.90, "B": 1.50, "C+": 1.00, "C": 0.50, "D": 0.10, "E": 0.00},
        ("技术职", "基干级"): {"A": 2.00, "B+": 1.70, "B": 1.40, "C+": 1.00, "C": 0.50, "D": 0.25, "E": 0.00},
        ("技术职", "指导级"): {"A": 1.80, "B+": 1.50, "B": 1.30, "C+": 1.00, "C": 0.70, "D": 0.25, "E": 0.00},
        ("技术职", "担当级"): {"A": 1.50, "B+": 1.30, "B": 1.15, "C+": 1.00, "C": 0.85, "D": 0.50, "E": 0.00},
    }
    rows = []
    for (family, qualification), coefficients in before_matrix.items():
        for rating, coefficient in coefficients.items():
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


def before_long_to_matrix(df: pd.DataFrame) -> pd.DataFrame:
    matrix = df.pivot_table(
        index=["original_job_family", "original_qualification"],
        columns="rating",
        values="coefficient",
        aggfunc="first",
    ).reset_index()
    family_order = {family: idx for idx, family in enumerate(VALID_JOB_FAMILIES)}
    qualification_order = {qualification: idx for idx, qualification in enumerate(VALID_QUALIFICATIONS)}
    matrix["_family_order"] = matrix["original_job_family"].map(family_order)
    matrix["_qualification_order"] = matrix["original_qualification"].map(qualification_order)
    matrix = matrix.sort_values(["_family_order", "_qualification_order"]).drop(columns=["_family_order", "_qualification_order"])
    return matrix[["original_job_family", "original_qualification"] + VALID_RATINGS]


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


def get_default_company_bonus_coefficients() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"scenario": "Before", "company_bonus_coefficient": 1.00},
            {"scenario": "Option A", "company_bonus_coefficient": 1.00},
            {"scenario": "Option B", "company_bonus_coefficient": 1.00},
        ]
    )


def normalize_company_bonus_coefficients(df: pd.DataFrame) -> pd.DataFrame:
    normalized = normalize_uploaded_columns(df)
    if "scenario" not in normalized.columns:
        normalized["scenario"] = ["Before", "Option A", "Option B"][: len(normalized)]
    if "company_bonus_coefficient" not in normalized.columns:
        normalized["company_bonus_coefficient"] = 1.00
    scenario_reverse = {value: key for key, value in SCENARIO_LABELS.items()}
    scenario_reverse.update({value: key for key, value in SCENARIO_LABELS_JA.items()})
    normalized["scenario"] = normalized["scenario"].replace(scenario_reverse)
    normalized["company_bonus_coefficient"] = pd.to_numeric(normalized["company_bonus_coefficient"], errors="coerce").fillna(1.00)
    normalized["company_bonus_coefficient"] = normalized["company_bonus_coefficient"].clip(lower=0)
    expected = pd.DataFrame({"scenario": ["Before", "Option A", "Option B"]})
    normalized = expected.merge(normalized[["scenario", "company_bonus_coefficient"]], on="scenario", how="left")
    normalized["company_bonus_coefficient"] = normalized["company_bonus_coefficient"].fillna(1.00)
    return normalized


def fill_blank_coefficients_from_baseline(
    edited_df: pd.DataFrame,
    baseline_df: pd.DataFrame,
    id_cols: List[str],
    value_cols: List[str],
) -> pd.DataFrame:
    edited = normalize_uploaded_columns(edited_df)
    baseline = baseline_df.copy()
    skeleton = baseline[id_cols].copy()
    for col in id_cols:
        if col not in edited.columns:
            edited[col] = baseline[col]
    for col in value_cols:
        if col not in edited.columns:
            edited[col] = np.nan
        edited[col] = pd.to_numeric(edited[col], errors="coerce")
    edited = skeleton.merge(edited[id_cols + value_cols], on=id_cols, how="left")
    for col in value_cols:
        edited[col] = edited[col].fillna(baseline[col])
    for col in baseline.columns:
        if col not in edited.columns:
            edited[col] = baseline[col]
    return edited[baseline.columns]


def normalize_coefficient_editor(
    edited_df: pd.DataFrame,
    current_df: pd.DataFrame,
    id_cols: List[str],
    value_cols: List[str],
) -> pd.DataFrame:
    edited = normalize_uploaded_columns(edited_df)
    current = current_df.copy()
    for col in id_cols:
        if col not in edited.columns:
            edited[col] = current[col]
    for col in value_cols:
        if col not in edited.columns:
            edited[col] = np.nan
        edited[col] = pd.to_numeric(edited[col], errors="coerce")
    merged = current[id_cols].merge(edited[id_cols + value_cols], on=id_cols, how="left")
    for col in value_cols:
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(current[col])
        merged[col] = merged[col].clip(lower=0)
    for col in current.columns:
        if col not in merged.columns:
            merged[col] = current[col]
    return merged[current.columns]


def coefficient_frames_equal(left: pd.DataFrame, right: pd.DataFrame, value_cols: List[str]) -> bool:
    if list(left.columns) != list(right.columns) or len(left) != len(right):
        return False
    for col in left.columns:
        if col in value_cols:
            left_values = pd.to_numeric(left[col], errors="coerce").round(6).fillna(-999999999)
            right_values = pd.to_numeric(right[col], errors="coerce").round(6).fillna(-999999999)
            if not left_values.equals(right_values):
                return False
        else:
            left_values = left[col].fillna("").astype(str).reset_index(drop=True)
            right_values = right[col].fillna("").astype(str).reset_index(drop=True)
            if not left_values.equals(right_values):
                return False
    return True


def clear_coefficient_editor_widgets() -> None:
    for key in ["company_bonus_coeff_editor", "option_a_editor", "option_b_editor"]:
        if key in st.session_state:
            del st.session_state[key]


def create_employee_template() -> BytesIO:
    sample = pd.DataFrame(
        [
            ["E001", "张三", "正式", "服务一部", "技术职", "基干级", "M", "M4", "A", 10000, 1.00, "Y", "示例"],
            ["E002", "李四", "正式", "服务一部", "技术职", "基干级", "T", "T4", "A", 10000, 1.00, "Y", "示例"],
            ["E003", "王五", "日方", "后勤部", "综合职（非销售）", "指导级", "G", "G3", "B", 8000, 1.00, "Y", "示例"],
            ["E004", "赵六", "正式", "销售部", "综合职（销售）", "经营级", "S", "S5", "B+", 12000, 0.80, "Y", "示例"],
            ["E005", "钱七", "中方", "现场部", "现场职", "担当级", "O", "O1", "C+", 7000, 1.00, "Y", "示例"],
            ["E006", "孙八", "劳务", "现场部", "现场职", "担当级", "O", "O1", "C+", 7000, 1.00, "N", "示例，不参与测算"],
        ],
        columns=EMPLOYEE_COLUMNS,
    )
    instructions = pd.DataFrame(
        [
            ["员工编号", "不可重复", "文本", "是"],
            ["姓名", "员工姓名", "文本", "是"],
            ["员工性质", "员工分类", "正式、中方、日方、劳务", "是"],
            ["部门", "所属部门", "文本", "建议"],
            ["原职群", "按现行职群填写", "综合职（非销售）、综合职（销售）、现场职、技术职", "是"],
            ["原能力资格", "按现行能力资格填写", "理事级、经营级、基干级、指导级、担当级", "是"],
            ["新职群", "用于方案 A 和方案 B 测算", "M、T、S、O、G", "是"],
            ["新等级", "用于方案 B 测算，需为实际单一等级", "如 M4、M5、T1、S3、O4、G6", "是"],
            ["评价等级", "年度评价等级；为空时按员工性质应用默认评价联动系数", "A、B+、B、C+、C、D、E；空值：正式/劳务=0.50，中方/日方=1.00", "否"],
            ["奖金基数", "奖金计算基数", "数字，大于等于 0", "是"],
            ["出勤率", "参与奖金计算的出勤比例", "数字或百分比，如 1、0.95、95%", "是"],
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
        company_coeff = rename_columns_cn(get_default_company_bonus_coefficients())
        option_a_coeff = rename_columns_cn(option_a_long_to_matrix(get_default_option_a_coefficients()))
        option_b_coeff = rename_columns_cn(option_b_long_to_matrix(get_default_option_b_coefficients()))
        company_coeff.to_excel(writer, index=False, sheet_name="03_公司整体奖金系数")
        option_a_coeff.to_excel(writer, index=False, sheet_name="04_方案A评价联动系数")
        option_b_coeff.to_excel(writer, index=False, sheet_name="05_方案B评价联动系数")
        workbook = writer.book
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#DDEBF7", "border": 1})
        text_fmt = workbook.add_format({"text_wrap": True, "valign": "top"})
        for sheet_name, df in {
            "01_员工数据": sample_cn,
            "02_填写说明": instructions,
            "03_公司整体奖金系数": company_coeff,
            "04_方案A评价联动系数": option_a_coeff,
            "05_方案B评价联动系数": option_b_coeff,
        }.items():
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


def load_uploaded_coefficient_settings(uploaded_file) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
    messages: List[str] = []
    settings: Dict[str, pd.DataFrame] = {}
    uploaded_file.seek(0)
    xls = pd.ExcelFile(uploaded_file)
    sheet_map = {
        "company_bonus_coefficients": "03_公司整体奖金系数",
        "option_a_matrix": "04_方案A评价联动系数",
        "option_b_matrix": "05_方案B评价联动系数",
    }
    if sheet_map["company_bonus_coefficients"] in xls.sheet_names:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_map["company_bonus_coefficients"], dtype=object)
        settings["company_bonus_coefficients"] = normalize_company_bonus_coefficients(df)
        messages.append("已同步公司整体奖金系数。")
    if sheet_map["option_a_matrix"] in xls.sheet_names:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_map["option_a_matrix"], dtype=object)
        df = normalize_uploaded_columns(df)
        settings["option_a_matrix"] = fill_blank_coefficients_from_baseline(
            df,
            option_a_long_to_matrix(get_default_option_a_coefficients()),
            ["new_job_family", "new_job_family_name"],
            VALID_RATINGS,
        )
        messages.append("已同步方案A评价联动系数。")
    if sheet_map["option_b_matrix"] in xls.sheet_names:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_map["option_b_matrix"], dtype=object)
        df = normalize_uploaded_columns(df)
        settings["option_b_matrix"] = fill_blank_coefficients_from_baseline(
            df,
            option_b_long_to_matrix(get_default_option_b_coefficients()),
            ["new_job_family", "new_job_family_name", "new_grade"],
            VALID_RATINGS,
        )
        messages.append("已同步方案B评价联动系数。")
    uploaded_file.seek(0)
    return settings, messages


def create_fallback_employee_data() -> pd.DataFrame:
    return clean_employee_data(
        pd.DataFrame(
            [
                ["E001", "张三", "正式", "服务一部", "技术职", "基干级", "M", "M4", "A", 10000, 1.00, "Y", "示例"],
                ["E002", "李四", "正式", "服务一部", "技术职", "基干级", "T", "T4", "A", 10000, 1.00, "Y", "示例"],
                ["E003", "王五", "正式", "后勤部", "综合职（非销售）", "指导级", "G", "G3", "B", 8000, 1.00, "Y", "示例"],
            ],
            columns=EMPLOYEE_COLUMNS,
        )
    )


def load_default_employee_data() -> Tuple[pd.DataFrame, str | None]:
    if DEFAULT_EMPLOYEE_DATA_PATH.exists():
        try:
            employee_df, warning = load_employee_data(DEFAULT_EMPLOYEE_DATA_PATH)
            return employee_df, warning
        except Exception as exc:
            return create_fallback_employee_data(), f"默认测算数据读取失败，已加载备用示例数据：{exc}"
    return create_fallback_employee_data(), "未找到默认测算数据文件，已加载备用示例数据。"


def clean_employee_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    text_columns = [
        "employee_id",
        "employee_name",
        "employee_type",
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
    out["attendance_rate"] = parse_rate_series(out["attendance_rate"])
    return out


def parse_rate_series(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip().str.replace(",", "", regex=False)
    has_percent = text.str.endswith("%")
    numeric = pd.to_numeric(text.str.replace("%", "", regex=False), errors="coerce")
    numeric = np.where(has_percent & pd.notna(numeric), numeric / 100, numeric)
    numeric = np.where(pd.notna(numeric) & (numeric > 1) & (numeric <= 100), numeric / 100, numeric)
    return pd.Series(numeric, index=series.index, dtype="float")


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
        if row["employee_type"] and row["employee_type"] not in VALID_EMPLOYEE_TYPES:
            issues.append(issue_record(row, "员工性质无效", "员工性质需填写正式、中方、日方或劳务。"))
        if row["original_qualification"] and row["original_qualification"] not in VALID_QUALIFICATIONS:
            issues.append(issue_record(row, "原能力资格无效", f"{row['original_qualification']} 不在有效能力资格范围内。"))
        if row["new_job_family"] and row["new_job_family"] not in VALID_NEW_JOB_FAMILIES:
            issues.append(issue_record(row, "新职群无效", "new_job_family 需填写 M、T、S、O、G。"))
        if row["new_grade"] and (row["new_job_family"], row["new_grade"]) not in valid_grade_pairs:
            issues.append(issue_record(row, "新等级无效", "new_grade 必须是所选 new_job_family 下的实际单一等级。"))
        if row["rating"] and row["rating"] not in VALID_RATINGS:
            issues.append(issue_record(row, "评价等级无效", f"{row['rating']} 不在有效评价等级范围内。"))
        if pd.isna(row["bonus_base"]) or row["bonus_base"] < 0:
            issues.append(issue_record(row, "奖金基数无效", "奖金基数需为大于等于 0 的数字。"))
        if pd.isna(row["attendance_rate"]) or row["attendance_rate"] < 0 or row["attendance_rate"] > 1:
            issues.append(issue_record(row, "出勤率无效", "出勤率需为 0-1 之间的数字或百分比。"))
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
    company_bonus_coeff: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    detail = structure_df.copy()
    before = before_coeff.rename(columns={"coefficient": "before_coefficient"})
    option_a = option_a_coeff.rename(columns={"coefficient": "option_a_coefficient"})
    option_b = option_b_coeff.rename(columns={"coefficient": "option_b_coefficient"})
    company_lookup = company_bonus_coeff.set_index("scenario")["company_bonus_coefficient"].to_dict()
    detail["before_company_bonus_coefficient"] = float(company_lookup.get("Before", 1.00))
    detail["option_a_company_bonus_coefficient"] = float(company_lookup.get("Option A", 1.00))
    detail["option_b_company_bonus_coefficient"] = float(company_lookup.get("Option B", 1.00))
    detail["option_a_calc_job_family"] = detail["new_job_family"]
    detail["option_b_calc_job_family"] = detail["new_job_family"]
    detail["option_b_calc_grade"] = detail["new_grade"]
    detail["coefficient_rule_note"] = ""

    special_rule_employee = pd.Series(False, index=detail.index)
    for original_family, rule in SPECIAL_M4_COEFFICIENT_RULES.items():
        mask = (
            detail["new_grade"].eq("M4")
            & detail["original_job_family"].eq(original_family)
            & detail["original_qualification"].eq(rule["qualification"])
        )
        special_rule_employee = special_rule_employee | mask
        detail.loc[mask, "option_a_calc_job_family"] = rule["option_a_family"]
        detail.loc[mask, "option_b_calc_job_family"] = rule["option_b_family"]
        detail.loc[mask, "option_b_calc_grade"] = rule["option_b_grade"]
        detail.loc[mask, "coefficient_rule_note"] = (
            f"特殊规则：原职群为{original_family}、原能力资格为{rule['qualification']}且新等级为M4，"
            f"方案A按{rule['option_a_family']} {rule['option_a_family_name']}评价联动系数计算，"
            f"方案B按{rule['option_b_grade']}评价联动系数计算。"
        )

    detail = detail.merge(
        before[["original_job_family", "original_qualification", "rating", "before_coefficient"]],
        on=["original_job_family", "original_qualification", "rating"],
        how="left",
    )
    option_a_lookup = option_a.rename(columns={"new_job_family": "option_a_calc_job_family"})
    detail = detail.merge(
        option_a_lookup[["option_a_calc_job_family", "rating", "option_a_coefficient"]],
        on=["option_a_calc_job_family", "rating"],
        how="left",
    )
    option_b_lookup = option_b.rename(columns={"new_job_family": "option_b_calc_job_family", "new_grade": "option_b_calc_grade"})
    detail = detail.merge(
        option_b_lookup[["option_b_calc_job_family", "option_b_calc_grade", "rating", "option_b_coefficient"]],
        on=["option_b_calc_job_family", "option_b_calc_grade", "rating"],
        how="left",
    )
    fixed_linkage_employee = detail["employee_type"].isin(FIXED_LINKAGE_EMPLOYEE_TYPES) & ~special_rule_employee
    detail.loc[
        fixed_linkage_employee,
        ["before_coefficient", "option_a_coefficient", "option_b_coefficient"],
    ] = 1.00
    blank_rating = detail["rating"].fillna("").astype(str).str.strip().eq("")
    blank_half_linkage_employee = blank_rating & detail["employee_type"].isin(BLANK_RATING_HALF_LINKAGE_EMPLOYEE_TYPES)
    blank_fixed_linkage_employee = blank_rating & detail["employee_type"].isin(FIXED_LINKAGE_EMPLOYEE_TYPES)
    detail.loc[
        blank_half_linkage_employee,
        ["before_coefficient", "option_a_coefficient", "option_b_coefficient"],
    ] = BLANK_RATING_HALF_LINKAGE
    detail.loc[
        blank_fixed_linkage_employee,
        ["before_coefficient", "option_a_coefficient", "option_b_coefficient"],
    ] = BLANK_RATING_FIXED_LINKAGE

    coeff_issues = add_coefficient_issues(detail)
    valid_for_calc = (
        detail["eligible"].eq("Y")
        & detail["bonus_base"].notna()
        & detail["attendance_rate"].notna()
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
            * detail.loc[valid_for_calc, f"{scenario}_company_bonus_coefficient"]
            * detail.loc[valid_for_calc, f"{scenario}_coefficient"]
            * detail.loc[valid_for_calc, "attendance_rate"]
        ).round(0)
        detail.loc[not_eligible, f"{scenario}_bonus"] = 0

    detail["option_a_change_amount"] = detail["option_a_bonus"] - detail["before_bonus"]
    detail["option_b_change_amount"] = detail["option_b_bonus"] - detail["before_bonus"]
    detail["option_a_change_pct"] = np.where(detail["before_bonus"].fillna(0).ne(0), detail["option_a_change_amount"] / detail["before_bonus"], np.nan)
    detail["option_b_change_pct"] = np.where(detail["before_bonus"].fillna(0).ne(0), detail["option_b_change_amount"] / detail["before_bonus"], np.nan)
    has_rule_note = detail["coefficient_rule_note"].fillna("").ne("")
    existing_remarks = detail["remarks"].fillna("").astype(str).str.strip()
    detail.loc[has_rule_note, "remarks"] = np.where(
        existing_remarks[has_rule_note].ne(""),
        existing_remarks[has_rule_note] + "；" + detail.loc[has_rule_note, "coefficient_rule_note"],
        detail.loc[has_rule_note, "coefficient_rule_note"],
    )
    detail.loc[not_eligible, "structure_note"] = detail.loc[not_eligible, "structure_note"].replace("", "不参与测算")
    detail.loc[not_eligible, "structure_status"] = "不参与测算"

    columns = [
        "employee_id",
        "employee_name",
        "employee_type",
        "department",
        "original_job_family",
        "original_qualification",
        "new_job_family",
        "new_job_family_name",
        "new_grade",
        "rating",
        "bonus_base",
        "attendance_rate",
        "eligible",
        "before_company_bonus_coefficient",
        "option_a_company_bonus_coefficient",
        "option_b_company_bonus_coefficient",
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


def create_rating_distribution_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    counts = df["rating"].value_counts().reindex(VALID_RATINGS, fill_value=0)
    total = int(counts.sum())
    summary = counts.rename_axis("rating").reset_index(name="headcount")
    summary["rating_share"] = np.where(total > 0, summary["headcount"] / total, np.nan)
    return summary


def create_rating_mix_summary(calc_df: pd.DataFrame, group_cols: List[str]) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    columns = group_cols + ["rating", "headcount", "group_total", "rating_share"]
    if df.empty:
        return pd.DataFrame(columns=columns)

    groups = df[group_cols].drop_duplicates().reset_index(drop=True)
    ratings = pd.DataFrame({"rating": VALID_RATINGS})
    complete = groups.merge(ratings, how="cross")
    counts = (
        df.groupby(group_cols + ["rating"], dropna=False)
        .agg(headcount=("employee_id", "count"))
        .reset_index()
    )
    summary = complete.merge(counts, on=group_cols + ["rating"], how="left")
    summary["headcount"] = summary["headcount"].fillna(0).astype(int)
    summary["group_total"] = summary.groupby(group_cols, dropna=False)["headcount"].transform("sum")
    summary["rating_share"] = np.where(summary["group_total"].gt(0), summary["headcount"] / summary["group_total"], np.nan)
    return summary[columns]


def create_new_family_rating_mix_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    summary = create_rating_mix_summary(calc_df, ["new_job_family", "new_job_family_name"])
    if summary.empty:
        summary["group_label"] = pd.Series(dtype=str)
        return summary
    family_names = summary["new_job_family_name"].fillna("")
    if get_language() == "ja":
        family_names = family_names.replace(VALUE_LABELS_JA["new_job_family_name"])
    summary["group_label"] = summary["new_job_family"].fillna("") + " " + family_names
    return summary[["new_job_family", "new_job_family_name", "group_label", "rating", "headcount", "group_total", "rating_share"]]


def create_grade_rating_mix_summary(calc_df: pd.DataFrame) -> pd.DataFrame:
    summary = create_rating_mix_summary(calc_df, ["new_job_family", "new_job_family_name", "new_grade"])
    if summary.empty:
        summary["group_label"] = pd.Series(dtype=str)
        return summary
    grade_order = get_default_grade_structure()[["new_job_family", "new_grade", "grade_order"]]
    summary = summary.merge(grade_order, on=["new_job_family", "new_grade"], how="left")
    summary["group_label"] = summary["new_grade"]
    summary = summary.sort_values(["new_job_family", "grade_order", "rating"], ascending=[True, True, True])
    return summary[["new_job_family", "new_job_family_name", "new_grade", "group_label", "rating", "headcount", "group_total", "rating_share"]]


def create_employee_impact(calc_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "employee_id",
        "employee_name",
        "employee_type",
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
    labels = scenario_labels()
    return pd.DataFrame(
        {
            "方案": [labels["Before"], labels["Option A"], labels["Option B"]],
            "总奖金成本": [df["before_bonus"].sum(), df["option_a_bonus"].sum(), df["option_b_bonus"].sum()],
        }
    )


def create_new_family_chart_data(calc_df: pd.DataFrame) -> pd.DataFrame:
    summary = create_new_job_family_summary(calc_df).copy()
    family_names = summary["new_job_family_name"].fillna("")
    if get_language() == "ja":
        family_names = family_names.replace(VALUE_LABELS_JA["new_job_family_name"])
    summary["新职群"] = summary["new_job_family"].fillna("") + " " + family_names
    return summary.melt(
        id_vars=["新职群"],
        value_vars=["before_bonus", "option_a_bonus", "option_b_bonus"],
        var_name="方案",
        value_name="奖金总额",
    ).replace({"方案": {"before_bonus": scenario_labels()["Before"], "option_a_bonus": scenario_labels()["Option A"], "option_b_bonus": scenario_labels()["Option B"]}})


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
    ).replace({"方案": {"before_bonus": scenario_labels()["Before"], "option_a_bonus": scenario_labels()["Option A"], "option_b_bonus": scenario_labels()["Option B"]}})


def create_change_distribution_data(calc_df: pd.DataFrame) -> pd.DataFrame:
    df = eligible_detail(calc_df)
    return df.melt(
        value_vars=["option_a_change_amount", "option_b_change_amount"],
        var_name="方案",
        value_name="变化额",
    ).replace({"方案": {"option_a_change_amount": scenario_labels()["Option A"], "option_b_change_amount": scenario_labels()["Option B"]}}).dropna(subset=["变化额"])


def create_top_impact_chart_data(calc_df: pd.DataFrame, scenario: str) -> pd.DataFrame:
    source_col = "option_a_change_amount" if scenario in ["方案A", "案A"] else "option_b_change_amount"
    df = eligible_detail(calc_df)[["employee_id", "employee_name", source_col]].copy()
    df["员工"] = df["employee_id"].fillna("") + " " + df["employee_name"].fillna("")
    df["变化额"] = df[source_col]
    df["绝对变化额"] = df["变化额"].abs()
    df = df.sort_values("绝对变化额", ascending=False).head(10).sort_values("变化额")
    df["方向"] = np.where(df["变化额"] >= 0, tr("增加"), tr("减少"))
    return df[["员工", "变化额", "方向"]]


def rating_distribution_insight(calc_df: pd.DataFrame) -> str:
    data = create_rating_distribution_summary(calc_df)
    if data.empty or data["headcount"].sum() == 0:
        return "暂无可分析的评价结果数据。"
    top = data.sort_values("headcount", ascending=False).iloc[0]
    high_share = data[data["rating"].isin(["A", "B+"])]['headcount'].sum() / data["headcount"].sum()
    low_share = data[data["rating"].isin(["D", "E"])]['headcount'].sum() / data["headcount"].sum()
    if get_language() == "ja":
        return f"最も人数が多い評価結果は {top['rating']} で、構成比は {format_pct(top['rating_share'])} です。A/B+ 合計は {format_pct(high_share)}、D/E 合計は {format_pct(low_share)} です。"
    return f"人数最多的评价为 {top['rating']}，占比 {format_pct(top['rating_share'])}；A/B+ 合计占比 {format_pct(high_share)}，D/E 合计占比 {format_pct(low_share)}。"


def rating_mix_insight(mix_df: pd.DataFrame, dimension_name: str) -> str:
    if mix_df.empty or mix_df["headcount"].sum() == 0:
        return f"暂无可分析的{dimension_name}评价结构数据。"
    high_mix = (
        mix_df[mix_df["rating"].isin(["A", "B+"])]
        .groupby("group_label", dropna=False)
        .agg(high_count=("headcount", "sum"), group_total=("group_total", "max"))
        .reset_index()
    )
    high_mix["high_share"] = np.where(high_mix["group_total"].gt(0), high_mix["high_count"] / high_mix["group_total"], np.nan)
    top = high_mix.sort_values("high_share", ascending=False).iloc[0]
    if get_language() == "ja":
        dimension = tr(dimension_name)
        return f"{dimension}では、{top['group_label']} の A/B+ 構成比が最も高く、{format_pct(top['high_share'])} です。サンプル数を踏まえて構造的な偏りの有無を確認してください。"
    return f"{dimension_name}中，{top['group_label']} 的 A/B+ 占比最高，为 {format_pct(top['high_share'])}。建议结合样本量判断是否存在结构性差异。"


def render_rating_distribution_chart(calc_df: pd.DataFrame) -> None:
    with st.container(border=True):
        data = create_rating_distribution_summary(calc_df)
        chart_note("该图展示参与测算员工的评价结果人数和占比。")
        chart = alt.Chart(data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x=alt.X("rating:N", title=tr("评价等级"), sort=VALID_RATINGS, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("headcount:Q", title=tr("人数"), axis=alt.Axis(format=",.0f")),
            color=alt.Color("rating:N", title=tr("评价等级"), scale=alt.Scale(domain=VALID_RATINGS, range=[RATING_COLORS[r] for r in VALID_RATINGS]), legend=None),
            tooltip=[
                alt.Tooltip("rating:N", title=tr("评价等级")),
                alt.Tooltip("headcount:Q", title=tr("人数"), format=",.0f"),
                alt.Tooltip("rating_share:Q", title=tr("占比"), format=".1%"),
            ],
        )
        labels = alt.Chart(data).mark_text(dy=-8, color=YNC_COLORS["text"], fontSize=12).encode(
            x=alt.X("rating:N", sort=VALID_RATINGS, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("headcount:Q"),
            text=alt.Text("rating_share:Q", format=".1%"),
        )
        st.altair_chart(chart_base(chart + labels, "评价结果总体分布"), use_container_width=True, key="rating_distribution_chart_v1")
        chart_analysis(rating_distribution_insight(calc_df))


def render_rating_mix_chart(mix_df: pd.DataFrame, title: str, dimension_name: str, key: str) -> None:
    with st.container(border=True):
        mix_df = prepare_rating_mix_chart_data(mix_df)
        chart_note(f"该图展示不同{dimension_name}内部的评价结果占比，用于观察评价结构差异。")
        chart = alt.Chart(mix_df).mark_bar().encode(
            x=alt.X("group_label:N", title=tr(dimension_name), sort=None, axis=alt.Axis(labelAngle=0, labelLimit=96)),
            y=alt.Y("rating_share:Q", title=tr("评价占比"), axis=alt.Axis(format=".0%"), scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("rating:N", title=tr("评价等级"), scale=alt.Scale(domain=VALID_RATINGS, range=[RATING_COLORS[r] for r in VALID_RATINGS])),
            order=alt.Order("rating_order:Q", sort="descending"),
            tooltip=[
                alt.Tooltip("group_label:N", title=tr(dimension_name)),
                alt.Tooltip("rating:N", title=tr("评价等级")),
                alt.Tooltip("headcount:Q", title=tr("人数"), format=",.0f"),
                alt.Tooltip("rating_share:Q", title=tr("占比"), format=".1%"),
            ],
        )
        labels = alt.Chart(mix_df).transform_filter(
            "datum.rating_share >= 0.08"
        ).mark_text(
            color="#FFFFFF",
            fontSize=10,
            fontWeight=500,
        ).encode(
            x=alt.X("group_label:N", sort=None),
            y=alt.Y("rating_share:Q", stack="center"),
            text=alt.Text("rating_share:Q", format=".0%"),
            detail="rating:N",
            order=alt.Order("rating_order:Q", sort="descending"),
        )
        st.altair_chart(chart_base(chart + labels, title), use_container_width=True, key=key)
        chart_analysis(rating_mix_insight(mix_df, dimension_name))


def prepare_rating_mix_chart_data(mix_df: pd.DataFrame) -> pd.DataFrame:
    chart_df = mix_df.copy()
    rating_order = {rating: idx for idx, rating in enumerate(VALID_RATINGS)}
    chart_df["rating_order"] = chart_df["rating"].map(rating_order)
    return chart_df


def render_grade_rating_mix_chart(mix_df: pd.DataFrame) -> None:
    with st.container(border=True):
        mix_df = prepare_rating_mix_chart_data(mix_df)
        families = (
            mix_df[["new_job_family", "new_job_family_name"]]
            .drop_duplicates()
        )
        families["family_order"] = families["new_job_family"].map({family: idx for idx, family in enumerate(VALID_NEW_JOB_FAMILIES)})
        families = families.sort_values("family_order")
        family_options = {
            f"{row.new_job_family} {VALUE_LABELS_JA['new_job_family_name'].get(row.new_job_family_name, row.new_job_family_name) if get_language() == 'ja' else row.new_job_family_name}": row.new_job_family
            for row in families.itertuples(index=False)
        }
        control_cols = st.columns([3, 1])
        with control_cols[0]:
            chart_note("该图展示所选新职群下，各新等级内部的评价结果占比，用于观察等级间评价结构差异。")
        if not family_options:
            st.info(tr("当前筛选条件下暂无可展示的新等级评价结果。"))
            return
        with control_cols[1]:
            selected_label = st.selectbox(
                tr("选择新职群"),
                options=list(family_options.keys()),
                key="grade_rating_mix_family_filter",
            )
        selected_family = family_options[selected_label]
        filtered = mix_df[mix_df["new_job_family"].eq(selected_family)].copy()
        chart = alt.Chart(filtered).mark_bar().encode(
            x=alt.X("group_label:N", title=tr("新等级"), sort=None, axis=alt.Axis(labelAngle=0, labelLimit=96)),
            y=alt.Y("rating_share:Q", title=tr("评价占比"), axis=alt.Axis(format=".0%"), scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("rating:N", title=tr("评价等级"), scale=alt.Scale(domain=VALID_RATINGS, range=[RATING_COLORS[r] for r in VALID_RATINGS])),
            order=alt.Order("rating_order:Q", sort="descending"),
            tooltip=[
                alt.Tooltip("group_label:N", title=tr("新等级")),
                alt.Tooltip("rating:N", title=tr("评价等级")),
                alt.Tooltip("headcount:Q", title=tr("人数"), format=",.0f"),
                alt.Tooltip("rating_share:Q", title=tr("占比"), format=".1%"),
            ],
        )
        labels = alt.Chart(filtered).transform_filter(
            "datum.rating_share >= 0.08"
        ).mark_text(
            color="#FFFFFF",
            fontSize=10,
            fontWeight=500,
        ).encode(
            x=alt.X("group_label:N", sort=None),
            y=alt.Y("rating_share:Q", stack="center"),
            text=alt.Text("rating_share:Q", format=".0%"),
            detail="rating:N",
            order=alt.Order("rating_order:Q", sort="descending"),
        )
        st.altair_chart(chart_base(chart + labels, f"按新等级的评价结果占比（{selected_label}）"), use_container_width=True, key="grade_rating_mix_chart_v2")
        chart_analysis(rating_mix_insight(filtered, "新等级"))


def render_total_cost_chart(calc_df: pd.DataFrame) -> None:
    with st.container(border=True):
        data = create_total_cost_chart_data(calc_df)
        chart_note("该图用于比较三套方案下的总奖金成本变化。")
        order = scenario_display_order()
        colors = scenario_color_map()
        bars = alt.Chart(data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=52).encode(
            x=alt.X("方案:N", title=tr("方案"), sort=order, axis=alt.Axis(labelAngle=0, labelLimit=120)),
            y=alt.Y("总奖金成本:Q", title=tr("总奖金成本"), axis=alt.Axis(format=",.0f")),
            color=alt.Color("方案:N", scale=alt.Scale(domain=order, range=[colors[name] for name in order]), legend=None),
            tooltip=[alt.Tooltip("方案:N", title=tr("方案")), alt.Tooltip("总奖金成本:Q", title=tr("总奖金成本"), format=",.0f")],
        )
        labels = alt.Chart(data).mark_text(dy=-8, color=YNC_COLORS["text"], fontSize=12).encode(
            x=alt.X("方案:N", sort=order, axis=alt.Axis(labelAngle=0, labelLimit=120)),
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
        order = scenario_display_order()
        colors = scenario_color_map()
        bars = alt.Chart(data).mark_bar().encode(
            x=alt.X("新职群:N", title=tr("新职群"), axis=alt.Axis(labelAngle=0, labelLimit=118)),
            y=alt.Y("奖金总额:Q", title=tr("奖金总额"), axis=alt.Axis(format=",.0f")),
            xOffset="方案:N",
            color=alt.Color("方案:N", title=tr("方案"), scale=alt.Scale(domain=order, range=[colors[name] for name in order])),
            tooltip=[alt.Tooltip("新职群:N", title=tr("新职群")), alt.Tooltip("方案:N", title=tr("方案")), alt.Tooltip("奖金总额:Q", title=tr("奖金总额"), format=",.0f")],
        )
        labels = alt.Chart(data).mark_text(
            dy=-6,
            color=YNC_COLORS["text"],
            fontSize=10,
        ).encode(
            x=alt.X("新职群:N", axis=alt.Axis(labelAngle=0, labelLimit=118)),
            y=alt.Y("奖金总额:Q"),
            xOffset="方案:N",
            text=alt.Text("奖金总额:Q", format=",.0f"),
        )
        st.altair_chart(chart_base(bars + labels, "按新职群的奖金成本对比"), use_container_width=True, key="new_family_chart_v3")
        chart_analysis(new_family_insight(calc_df))


def render_rating_average_chart(calc_df: pd.DataFrame) -> None:
    with st.container(border=True):
        data = create_rating_average_chart_data(calc_df)
        chart_note("该图用于观察高绩效与低绩效员工之间的激励差异是否被拉开。")
        order = scenario_display_order()
        colors = scenario_color_map()
        line = alt.Chart(data).mark_line(point=True, strokeWidth=2).encode(
            x=alt.X("评价等级:N", title=tr("评价等级"), sort=VALID_RATINGS, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("人均奖金:Q", title=tr("人均奖金"), axis=alt.Axis(format=",.0f")),
            color=alt.Color("方案:N", title=tr("方案"), scale=alt.Scale(domain=order, range=[colors[name] for name in order])),
            tooltip=[alt.Tooltip("评价等级:N", title=tr("评价等级")), alt.Tooltip("方案:N", title=tr("方案")), alt.Tooltip("人均奖金:Q", title=tr("人均奖金"), format=",.0f")],
        )
        labels = alt.Chart(data).transform_filter(
            "isValid(datum['人均奖金'])"
        ).mark_text(
            dy=-10,
            fontSize=10,
            color=YNC_COLORS["text"],
        ).encode(
            x=alt.X("评价等级:N", sort=VALID_RATINGS),
            y=alt.Y("人均奖金:Q"),
            text=alt.Text("人均奖金:Q", format=",.0f"),
            color=alt.Color("方案:N", scale=alt.Scale(domain=order, range=[colors[name] for name in order]), legend=None),
        )
        st.altair_chart(chart_base(line + labels, "按评价等级的人均奖金对比"), use_container_width=True, key="rating_average_chart_v3")
        chart_analysis(rating_insight(calc_df))


def render_change_distribution_chart(calc_df: pd.DataFrame, scenario: str) -> None:
    with st.container(border=True):
        data = create_change_distribution_data(calc_df)
        scenario_label = tr(scenario)
        data = data[data["方案"].eq(scenario_label)]
        chart_note("该图用于识别方案调整后个人奖金变化是否过于集中或存在极端值。")
        chart = alt.Chart(data).mark_bar(opacity=0.76, color=scenario_color_map()[scenario_label]).encode(
            x=alt.X("变化额:Q", title=tr("变化额"), bin=alt.Bin(maxbins=24), axis=alt.Axis(format=",.0f")),
            y=alt.Y("count():Q", title=tr("员工数量"), axis=alt.Axis(format=",.0f")),
            tooltip=[alt.Tooltip("方案:N", title=tr("方案")), alt.Tooltip("count():Q", title=tr("员工数量"), format=",.0f")],
        )
        labels = alt.Chart(data).mark_text(
            dy=-6,
            color=YNC_COLORS["text"],
            fontSize=10,
        ).encode(
            x=alt.X("变化额:Q", bin=alt.Bin(maxbins=24)),
            y=alt.Y("count():Q"),
            text=alt.Text("count():Q", format=",.0f"),
        )
        safe_key = "option_a" if scenario == "方案A" else "option_b"
        st.altair_chart(chart_base(chart + labels, f"{scenario}较现行变化额分布"), use_container_width=True, key=f"change_distribution_{safe_key}_v3")
        chart_analysis(distribution_insight(calc_df, scenario))


def render_top_impact_chart(calc_df: pd.DataFrame, scenario: str) -> None:
    with st.container(border=True):
        data = create_top_impact_chart_data(calc_df, scenario)
        chart_note("该图展示奖金变化绝对值最大的员工，用于识别重点沟通对象。")
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X("变化额:Q", title=f"{tr(scenario)}{tr('较现行变化额')}", axis=alt.Axis(format=",.0f")),
            y=alt.Y("员工:N", title=tr("员工"), sort="-x"),
            color=alt.Color("方向:N", scale=alt.Scale(domain=[tr("增加"), tr("减少")], range=[SCENARIO_COLORS["increase"], SCENARIO_COLORS["decrease"]]), legend=None),
            tooltip=[alt.Tooltip("员工:N", title=tr("员工")), alt.Tooltip("变化额:Q", title=tr("变化额"), format=",.0f"), alt.Tooltip("方向:N", title=tr("方向"))],
        )
        labels = alt.Chart(data).mark_text(
            align="left",
            dx=4,
            color=YNC_COLORS["text"],
            fontSize=10,
        ).encode(
            x=alt.X("变化额:Q"),
            y=alt.Y("员工:N", sort="-x"),
            text=alt.Text("变化额:Q", format=",.0f"),
        )
        safe_key = "option_a" if scenario == "方案A" else "option_b"
        st.altair_chart(chart_base(chart + labels, f"奖金变化影响最大的员工（{scenario}）"), use_container_width=True, key=f"top_impact_{safe_key}_v3")
        chart_analysis(top_impact_insight(calc_df, scenario))


def format_money(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"


def format_pct(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def format_signed_pct(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:+.1%}"


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
        elif original_col in PCT_COLUMNS or original_col.endswith("_pct") or "变化率" in col_name or "占比" in col_name:
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
    company_bonus_coefficients: pd.DataFrame,
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
            "03_现行方案评价联动系数": before_coeff,
            "04_公司整体奖金系数": company_bonus_coefficients,
            "05_方案A评价联动系数": option_a_matrix,
            "06_方案B评价联动系数": option_b_matrix,
            "07_测算明细": calc_df,
            "08_总体对比": format_overall_summary_cn(summaries["overall"]),
            "09_原职群对比": summaries["original_family"],
            "10_新职群对比": summaries["new_family"],
            "11_新等级对比": summaries["grade"],
            "12_评价等级对比": summaries["rating"],
            "13_评价结果分布": summaries["rating_distribution"],
            "14_职群评价占比": summaries["new_family_rating_mix"],
            "15_等级评价占比": summaries["grade_rating_mix"],
            "16_异常清单": validation_issues,
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


def calculate_all(
    employee_df: pd.DataFrame,
    option_a_matrix: pd.DataFrame,
    option_b_matrix: pd.DataFrame,
    company_bonus_coefficients: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    before_coeff = get_default_before_coefficients()
    option_a_coeff = matrix_to_long_option_a(option_a_matrix)
    option_b_coeff = matrix_to_long_option_b(option_b_matrix)
    company_coeff = normalize_company_bonus_coefficients(company_bonus_coefficients)
    base_issues = validate_employee_data(employee_df)
    structure_df, structure_issues = check_employee_structure(employee_df, get_default_grade_structure())
    calc_df, coeff_issues = calculate_bonus(structure_df, before_coeff, option_a_coeff, option_b_coeff, company_coeff)
    issues = combine_issues(base_issues, structure_issues, coeff_issues)
    summaries = {
        "overall": create_overall_summary(calc_df),
        "original_family": create_original_job_family_summary(calc_df),
        "new_family": create_new_job_family_summary(calc_df),
        "grade": create_grade_summary(calc_df),
        "rating": create_rating_summary(calc_df),
        "rating_distribution": create_rating_distribution_summary(calc_df),
        "new_family_rating_mix": create_new_family_rating_mix_summary(calc_df),
        "grade_rating_mix": create_grade_rating_mix_summary(calc_df),
        "impact": create_employee_impact(calc_df),
    }
    return {"structure": structure_df, "calc": calc_df, "issues": issues, "before_coeff": before_coeff, "company_coeff": company_coeff, **summaries}


def initialize_state() -> None:
    if "option_a_matrix" not in st.session_state:
        st.session_state.option_a_matrix = option_a_long_to_matrix(get_default_option_a_coefficients())
    if "option_b_matrix" not in st.session_state or len(st.session_state.option_b_matrix) != len(get_default_grade_structure()):
        st.session_state.option_b_matrix = option_b_long_to_matrix(get_default_option_b_coefficients())
    if "company_bonus_coefficients" not in st.session_state:
        st.session_state.company_bonus_coefficients = get_default_company_bonus_coefficients()
    if "reset_company_bonus_coefficients" not in st.session_state:
        st.session_state.reset_company_bonus_coefficients = st.session_state.company_bonus_coefficients.copy()
    if "reset_option_a_matrix" not in st.session_state:
        st.session_state.reset_option_a_matrix = st.session_state.option_a_matrix.copy()
    if "reset_option_b_matrix" not in st.session_state:
        st.session_state.reset_option_b_matrix = st.session_state.option_b_matrix.copy()
    needs_employee_seed = "employee_df" not in st.session_state or not set(EMPLOYEE_COLUMNS).issubset(st.session_state.employee_df.columns)
    if needs_employee_seed:
        st.session_state.employee_df, default_warning = load_default_employee_data()
        if default_warning:
            st.session_state.upload_warning = default_warning
    if "upload_warning" not in st.session_state:
        st.session_state.upload_warning = None
    if "has_uploaded_data" not in st.session_state:
        st.session_state.has_uploaded_data = False
    if "results" not in st.session_state or "structure" not in st.session_state.results:
        st.session_state.results = calculate_all(
            st.session_state.employee_df,
            st.session_state.option_a_matrix,
            st.session_state.option_b_matrix,
            st.session_state.company_bonus_coefficients,
        )
    if "last_calc_time" not in st.session_state:
        st.session_state.last_calc_time = datetime.now().strftime("%Y-%m-%d %H:%M")


def refresh_results() -> None:
    st.session_state.results = calculate_all(
        st.session_state.employee_df,
        st.session_state.option_a_matrix,
        st.session_state.option_b_matrix,
        st.session_state.company_bonus_coefficients,
    )
    st.session_state.last_calc_time = datetime.now().strftime("%Y-%m-%d %H:%M")


def render_download_tab() -> None:
    render_card(
        f"<h3>{tr('模板下载')}</h3>"
        f"<p>{tr('客户仅需填写标准模板中的 <b>01_员工数据</b> Sheet。现行方案使用原职群和原能力资格；方案A/方案B使用上传的新职群和新等级。')}</p>"
    )
    st.download_button(
        tr("下载标准模板"),
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
                <div style="font-size:34px; line-height:1.18; font-weight:500; color:#1F2933; margin-bottom:12px;">{tr('YNC 奖金系数方案测算工具')}</div>
                <div style="font-size:15px; color:#6B7280; max-width:720px;">{tr('用于现行方案、方案A、方案B的奖金成本测算、员工影响分析与方案对比。')}</div>
            </div>
            <div style="min-width:260px; background:rgba(177,18,38,0.06); border:1px solid rgba(177,18,38,0.12); border-radius:16px; padding:16px;">
                <div style="font-size:13px; color:#6B7280; margin-bottom:8px;">{tr('当前数据状态')}</div>
                <div style="font-size:22px; color:#7F0D1B; font-weight:500;">{status["status"]}</div>
                <div style="font-size:13px; color:#6B7280; margin-top:10px;">{tr('员工数量')}：{status["employee_count"]}</div>
                <div style="font-size:13px; color:#6B7280;">{tr('最近测算')}：{status["calc_time"]}</div>
            </div>
        </div>
        """
    )
    cols = st.columns(3)
    with cols[0]:
        render_card(f"<h3>{icon_title('download', tr('标准化导入'))}</h3><p>{tr('客户仅需填写员工数据，规则与方案参数由顾问维护。')}</p>")
    with cols[1]:
        render_card(f"<h3>{icon_title('settings', tr('方案系数调整'))}</h3><p>{tr('支持方案A、方案B系数在线编辑，调整后自动刷新测算结果。')}</p>")
    with cols[2]:
        render_card(f"<h3>{icon_title('chart', tr('可视化对比分析'))}</h3><p>{tr('支持总成本、职群、等级、评价等级和员工影响分析。')}</p>")
    render_card(f"<h3>{tr('流程步骤')}</h3><p style='font-size:15px;color:#50606F;'>{tr('1 下载模板 → 2 上传员工数据 → 3 调整方案系数 → 4 查看对比分析 → 5 导出结果')}</p>")


def render_upload_tab() -> None:
    render_card(f"<h3>{tr('数据上传')}</h3><p>{tr('上传客户填写后的 Excel。系统优先读取“01_员工数据”Sheet，也兼容中文表头和旧版英文表头。')}</p>")
    uploaded_file = st.file_uploader(tr("上传员工数据 Excel"), type=["xlsx", "xls"])
    if uploaded_file is not None:
        try:
            employee_df, warning = load_employee_data(uploaded_file)
            coefficient_settings, coefficient_messages = load_uploaded_coefficient_settings(uploaded_file)
            if "company_bonus_coefficients" in coefficient_settings:
                st.session_state.company_bonus_coefficients = coefficient_settings["company_bonus_coefficients"]
                st.session_state.reset_company_bonus_coefficients = coefficient_settings["company_bonus_coefficients"].copy()
            if "option_a_matrix" in coefficient_settings:
                st.session_state.option_a_matrix = coefficient_settings["option_a_matrix"]
                st.session_state.reset_option_a_matrix = coefficient_settings["option_a_matrix"].copy()
            if "option_b_matrix" in coefficient_settings:
                st.session_state.option_b_matrix = coefficient_settings["option_b_matrix"]
                st.session_state.reset_option_b_matrix = coefficient_settings["option_b_matrix"].copy()
            if coefficient_messages:
                clear_coefficient_editor_widgets()
            st.session_state.employee_df = employee_df
            st.session_state.upload_warning = warning
            st.session_state.has_uploaded_data = True
            refresh_results()
            st.success(f"{tr('已成功读取')} {len(employee_df):,} {tr('条员工数据。')}")
            if coefficient_messages:
                st.info(" ".join(coefficient_messages))
        except Exception as exc:
            st.error(f"{tr('读取失败')}：{exc}")

    if st.session_state.upload_warning:
        st.warning(st.session_state.upload_warning)

    st.subheader(tr("员工数据预览"))
    if not st.session_state.get("has_uploaded_data", False):
        st.markdown(f'<div class="empty-state"><b>{tr("尚未上传员工数据")}</b><br>{tr("当前显示的是内置默认测算数据。上传客户数据后将自动替换为客户数据。")}</div>', unsafe_allow_html=True)
    display_table_cn(st.session_state.employee_df)


def render_data_check_tab() -> None:
    render_card(f"<h3>{tr('数据检查')}</h3><p>{tr('检查原职群、原能力资格、新职群、新等级、评价等级和系数匹配情况。系统不再根据原能力资格或通道推断新等级。')}</p>")
    cols = [
        "employee_id",
        "employee_name",
        "employee_type",
        "original_job_family",
        "original_qualification",
        "new_job_family",
        "new_job_family_name",
        "new_grade",
        "coefficient_group",
        "structure_status",
        "structure_note",
    ]
    st.subheader(tr("数据检查明细"))
    display_table_cn(st.session_state.results["structure"][cols])
    st.subheader(tr("异常清单"))
    issues = st.session_state.results["issues"]
    if issues.empty:
        render_card(f"<h3>{icon_title('check', tr('数据检查通过'))}</h3><p>{tr('当前未发现异常，可以进行方案测算与对比分析。')}</p>")
    else:
        error_count = int(issues["severity"].eq("error").sum()) if "severity" in issues.columns else len(issues)
        warning_count = int(issues["severity"].eq("warning").sum()) if "severity" in issues.columns else 0
        render_card(f"<h3>{icon_title('alert', tr('发现数据问题'))}</h3><p>{tr('共计')} {len(issues):,} {tr('条')}；{tr('其中')} {error_count:,} {tr('条为错误')}，{warning_count:,} {tr('条为提醒')}。</p>")
        display_table_cn(issues)


def render_coefficients_tab() -> None:
    render_card(
        f"<h3>{tr('方案系数设置')}</h3>"
        f"<p>{tr('奖金 = 奖金基数 × 公司整体奖金系数 × 评价联动系数 × 出勤率。调整参数后，点击“重新测算”刷新分析与导出结果。')}</p>"
        f"<p style='margin-top:8px;color:#6B7280;'>{tr('规则补充：员工性质为“中方”或“日方”的人员，三套方案的评价联动系数均按 1.00 计算；评价结果为空时，正式和劳务人员按 0.50 计算，中方和日方人员按 1.00 计算。')}</p>"
    )
    top_cols = st.columns([1, 1, 4])
    with top_cols[0]:
        if st.button(tr("重新测算"), use_container_width=True):
            st.session_state.company_bonus_coefficients = normalize_company_bonus_coefficients(st.session_state.company_bonus_coefficients)
            refresh_results()
            st.success(tr("已按当前系数重新测算。"))
    with top_cols[1]:
        if st.button(tr("重置为模板系数"), use_container_width=True):
            st.session_state.company_bonus_coefficients = st.session_state.reset_company_bonus_coefficients.copy()
            st.session_state.option_a_matrix = st.session_state.reset_option_a_matrix.copy()
            st.session_state.option_b_matrix = st.session_state.reset_option_b_matrix.copy()
            clear_coefficient_editor_widgets()
            refresh_results()
            st.success(tr("已重置为模板系数。"))
            st.rerun()

    st.subheader(tr("现行方案评价联动系数设置"))
    st.dataframe(
        rename_columns_cn(before_long_to_matrix(get_default_before_coefficients())),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader(tr("公司整体奖金系数设置"))
    edited_company = st.data_editor(
        rename_columns_cn(st.session_state.company_bonus_coefficients),
        use_container_width=True,
        hide_index=True,
        disabled=[cn_label("scenario")],
        column_config={
            cn_label("company_bonus_coefficient"): st.column_config.NumberColumn(
                cn_label("company_bonus_coefficient"),
                min_value=0.0,
                step=0.01,
                format="%.2f",
            )
        },
        key="company_bonus_coeff_editor",
    )
    normalized_company = normalize_company_bonus_coefficients(edited_company)
    if not coefficient_frames_equal(
        normalized_company,
        st.session_state.company_bonus_coefficients,
        ["company_bonus_coefficient"],
    ):
        st.session_state.company_bonus_coefficients = normalized_company
        st.rerun()

    st.subheader(tr("方案A评价联动系数设置"))
    edited_a = st.data_editor(
        rename_columns_cn(st.session_state.option_a_matrix),
        use_container_width=True,
        hide_index=True,
        disabled=[cn_label("new_job_family"), cn_label("new_job_family_name")],
        column_config={rating: st.column_config.NumberColumn(rating, min_value=0.0, step=0.01, format="%.2f") for rating in VALID_RATINGS},
        key="option_a_editor",
    )
    normalized_a = normalize_coefficient_editor(
        edited_a,
        st.session_state.option_a_matrix,
        ["new_job_family", "new_job_family_name"],
        VALID_RATINGS,
    )
    if not coefficient_frames_equal(normalized_a, st.session_state.option_a_matrix, VALID_RATINGS):
        st.session_state.option_a_matrix = normalized_a
        st.rerun()

    st.subheader(tr("方案B评价联动系数设置"))
    edited_b = st.data_editor(
        rename_columns_cn(st.session_state.option_b_matrix),
        use_container_width=True,
        hide_index=True,
        disabled=[cn_label("new_job_family"), cn_label("new_job_family_name"), cn_label("new_grade")],
        column_config={rating: st.column_config.NumberColumn(rating, min_value=0.0, step=0.01, format="%.2f") for rating in VALID_RATINGS},
        key="option_b_editor",
    )
    normalized_b = normalize_coefficient_editor(
        edited_b,
        st.session_state.option_b_matrix,
        ["new_job_family", "new_job_family_name", "new_grade"],
        VALID_RATINGS,
    )
    if not coefficient_frames_equal(normalized_b, st.session_state.option_b_matrix, VALID_RATINGS):
        st.session_state.option_b_matrix = normalized_b
        st.rerun()


def render_analysis_tab() -> None:
    results = st.session_state.results
    calc_df = results["calc"]
    overall = results["overall"]
    before_total = overall.loc[overall["指标"].eq("总奖金成本"), "Before"].iloc[0]
    option_a_total = overall.loc[overall["指标"].eq("总奖金成本"), "Option A"].iloc[0]
    option_b_total = overall.loc[overall["指标"].eq("总奖金成本"), "Option B"].iloc[0]
    headcount = overall.loc[overall["指标"].eq("参与人数"), "Before"].iloc[0]
    option_a_pct = safe_pct(option_a_total - before_total, before_total)
    option_b_pct = safe_pct(option_b_total - before_total, before_total)

    cols = st.columns(7)
    with cols[0]:
        metric_card(tr("参与人数"), format_scalar(headcount, "count"), icon="users")
    with cols[1]:
        metric_card(tr("现行方案总奖金"), format_money(before_total), icon="yen")
    with cols[2]:
        metric_card(tr("方案A总奖金"), format_money(option_a_total), icon="yen")
    with cols[3]:
        metric_card(tr("方案B总奖金"), format_money(option_b_total), icon="yen")
    with cols[4]:
        metric_card(
            tr("方案A较现行"),
            format_signed_pct(option_a_pct),
            icon="chart",
            delta=tr("变化率"),
            delta_color=YNC_COLORS["increase"] if option_a_pct >= 0 else YNC_COLORS["decrease"],
        )
    with cols[5]:
        metric_card(
            tr("方案B较现行"),
            format_signed_pct(option_b_pct),
            icon="chart",
            delta=tr("变化率"),
            delta_color=YNC_COLORS["increase"] if option_b_pct >= 0 else YNC_COLORS["decrease"],
        )
    with cols[6]:
        metric_card(tr("异常数量"), f"{len(results['issues']):,}", icon="alert")

    chart_header_cols = st.columns([3, 1])
    with chart_header_cols[0]:
        st.markdown(f'<div class="section-title">{tr("图表分析")}</div><div class="section-subtitle">{tr("用于快速判断成本变化、职群分布、绩效区分度与员工影响。")}</div>', unsafe_allow_html=True)
    available_employee_types = VALID_EMPLOYEE_TYPES
    with chart_header_cols[1]:
        filter_cols = st.columns([4, 1.35], vertical_alignment="bottom")
        with filter_cols[0]:
            selected_employee_types = st.multiselect(
                tr("员工性质"),
                options=available_employee_types,
                default=available_employee_types,
                format_func=tr,
                key="analysis_employee_type_filter_v2",
            )
        with filter_cols[1]:
            if st.button(tr("刷新图表"), use_container_width=True):
                refresh_results()
                st.success(tr("已刷新图表分析。"))
                st.rerun()
        st.caption(employee_type_filter_summary(calc_df, selected_employee_types))

    if not selected_employee_types:
        st.warning(tr("请至少选择一种员工性质用于图表展示。"))
        chart_calc_df = calc_df.iloc[0:0].copy()
    else:
        chart_calc_df = calc_df[calc_df["employee_type"].isin(selected_employee_types)].copy()

    render_auto_insights(chart_calc_df)

    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_total_cost_chart(chart_calc_df)
    with chart_cols[1]:
        render_new_family_chart(chart_calc_df)
    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_rating_average_chart(chart_calc_df)
    with chart_cols[1]:
        render_change_distribution_chart(chart_calc_df, "方案A")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_change_distribution_chart(chart_calc_df, "方案B")
    with chart_cols[1]:
        selected_scenario = st.radio(tr("奖金变化影响 Top 10"), ["方案A", "方案B"], horizontal=True, format_func=tr, key="top_impact_scenario")
        render_top_impact_chart(chart_calc_df, selected_scenario)

    st.markdown(f'<div class="section-title">{tr("评价结果分析")}</div><div class="section-subtitle">{tr("用于观察评价结果整体分布，以及不同新职群、新等级内部的评价结构差异。")}</div>', unsafe_allow_html=True)
    filtered_new_family_rating_mix = create_new_family_rating_mix_summary(chart_calc_df)
    filtered_grade_rating_mix = create_grade_rating_mix_summary(chart_calc_df)
    rating_cols = st.columns(2)
    with rating_cols[0]:
        render_rating_distribution_chart(chart_calc_df)
    with rating_cols[1]:
        render_rating_mix_chart(filtered_new_family_rating_mix, "按新职群的评价结果占比", "新职群", "new_family_rating_mix_chart_v1")
    render_grade_rating_mix_chart(filtered_grade_rating_mix)

    st.markdown(f'<div class="section-title">{tr("汇总表格")}</div>', unsafe_allow_html=True)
    subtabs = st.tabs([tr(label) for label in ["总体对比", "原职群对比", "新职群对比", "新等级对比", "评价等级对比", "评价结果分布", "职群评价占比", "等级评价占比"]])
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
    with subtabs[5]:
        display_table_cn(results["rating_distribution"])
    with subtabs[6]:
        display_table_cn(results["new_family_rating_mix"])
    with subtabs[7]:
        display_table_cn(results["grade_rating_mix"])

    st.markdown(f'<div class="section-title">{tr("员工影响清单")}</div>', unsafe_allow_html=True)
    display_table_cn(results["impact"], height=360)
    with st.expander(tr("查看测算明细")):
        display_table_cn(results["calc"], height=420)


def render_export_tab() -> None:
    render_card(f"<h3>{tr('结果导出')}</h3><p>{tr('导出文件包含方案系数、数据检查、测算明细、汇总分析和异常清单。')}</p>")
    results = st.session_state.results
    summaries = {
        "overall": results["overall"],
        "original_family": results["original_family"],
        "new_family": results["new_family"],
        "grade": results["grade"],
        "rating": results["rating"],
        "rating_distribution": results["rating_distribution"],
        "new_family_rating_mix": results["new_family_rating_mix"],
        "grade_rating_mix": results["grade_rating_mix"],
    }
    export_buffer = export_results_to_excel(
        raw_employee_df=st.session_state.employee_df,
        structure_df=results["structure"],
        before_coeff=results["before_coeff"],
        company_bonus_coefficients=st.session_state.company_bonus_coefficients,
        option_a_matrix=st.session_state.option_a_matrix,
        option_b_matrix=st.session_state.option_b_matrix,
        calc_df=results["calc"],
        summaries=summaries,
        validation_issues=results["issues"],
    )
    filename = f"YNC_奖金方案测算结果_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    st.download_button(
        tr("导出测算结果"),
        data=export_buffer,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def render_detail_tab() -> None:
    render_card(f"<h3>{icon_title('table', tr('明细结果'))}</h3><p>{tr('查看员工级测算明细与奖金变化影响清单。字段已按客户展示口径中文化。')}</p>")
    st.subheader(tr("员工影响清单"))
    display_table_cn(st.session_state.results["impact"], height=360)
    st.subheader(tr("测算明细"))
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
    raw_page = st.query_params.get("page", "home")
    current = raw_page[0] if isinstance(raw_page, list) else raw_page
    valid_keys = {key for key, _, _ in nav_items}
    if current not in valid_keys:
        current = "home"
    with st.container(border=True):
        selected = st.segmented_control(
            tr("页面导航"),
            options=[key for key, _, _ in nav_items],
            default=current,
            format_func=lambda nav_key: next(f"{icon} {tr(label)}" for key, icon, label in nav_items if key == nav_key),
            key=f"top_nav_segment_{get_language()}_{current}",
            label_visibility="collapsed",
        )
        if selected and selected != current:
            st.query_params["page"] = selected
            st.query_params["lang"] = get_language()
            current = selected
            st.rerun()
    return current


def main() -> None:
    apply_custom_css()
    if not ensure_authenticated():
        return
    initialize_state()
    render_brand_bar()
    render_language_switch()
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
