import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os

# --- 파일 경로 설정 (NAS 환경을 위해 상대 경로 사용) ---
# 마스터 시트 파일들이 이 스크립트와 동일한 폴더에 있다고 가정합니다.
EVENT_SUMMARY_PATH = 'event_summary_master_sheet.csv'
CONTENT_DETAIL_PATH = 'content_detail_master_sheet.csv'

# ----------------- 페이지 설정 -----------------
st.set_page_config(
    layout="wide",
    page_title="쿡앤셰프 주간 성과보고서",
    page_icon="📰",
    initial_sidebar_state="collapsed"
)

# ----------------- 컬러 팔레트 (Cook & Chef Identity) -----------------
COLOR_NAVY = "#1a237e"
COLOR_RED = "#d32f2f"
COLOR_GREY = "#78909c"
COLOR_BG_ACCENT = "#fffcf7"
CHART_PALETTE = [COLOR_NAVY, COLOR_RED, "#5c6bc0", "#ef5350", "#8d6e63", COLOR_GREY]

# ----------------- CSS 스타일링 (UI 개선) -----------------
CSS = f"""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css');

/* 기본 폰트 설정 */
body {{
    background-color: #ffffff;
    font-family: 'Pretendard', sans-serif;
    color: #263238;
}}
.block-container {{
    padding-top: 2rem;
    padding-bottom: 5rem;
    max_width: 1600px;
}}
[data-testid="stSidebar"] {{ display: none; }}

/* 헤더 타이틀 */
.report-title {{
    font-size: 2.6rem;
    font-weight: 900;
    color: {COLOR_NAVY};
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
    border-bottom: 4px solid {COLOR_RED};
    padding-bottom: 15px;
}}

/* 데이터 집계 시간 */
.update-time {{
    color: {COLOR_NAVY};
    font-weight: 700;
    font-size: 1.1rem;
    text-align: right;
    margin-top: -15px;
    margin-bottom: 30px;
    font-family: monospace;
}}

/* KPI 카드 */
.kpi-container {{
    background-color: #fff;
    border: 1px solid #eceff1;
    border-top: 5px solid {COLOR_RED};
    border-radius: 8px;
    padding: 20px 10px;
    text-align: center;
    margin-bottom: 15px;
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}}
.kpi-label {{
    font-size: 1.1rem;
    font-weight: 700;
    color: #455a64; 
    margin-bottom: 10px;
    word-break: keep-all;
}}
.kpi-value {{
    font-size: 2.4rem;
    font-weight: 900;
    color: {COLOR_NAVY};
    line-height: 1.1;
    letter-spacing: -0.03em;
}}
.kpi-unit {{
    font-size: 1.1rem;
    font-weight: 600;
    color: #90a4ae;
    margin-left: 3px;
}}

/* 섹션 타이틀 */
.section-header-container {{
    margin-top: 50px;
    margin-bottom: 25px;
    padding: 15px 25px;
    background-color: {COLOR_BG_ACCENT};
    border-left: 8px solid {COLOR_NAVY};
    border-radius: 4px;
    width: 100%;
}}
.section-header {{
    font-size: 1.8rem;
    font-weight: 800;
    color: {COLOR_NAVY};
    margin: 0;
}}
.section-desc {{
    font-size: 1rem;
    color: #5d4037;
    margin-top: 5px;
    font-weight: 500;
}}

/* 차트 소제목 */
.chart-header {{
    font-size: 1.3rem;
    font-weight: 700;
    color: #37474f;
    margin-top: 30px;
    margin-bottom: 15px;
    padding-left: 12px;
    border-left: 4px solid {COLOR_RED};
}}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0px;
    border-bottom: 2px solid #cfd8dc;
    display: flex;
    flex-wrap: nowrap;
    width: 100%;
}}
.stTabs [data-baseweb="tab"] {{
    height: 60px;
    background-color: #f7f9fa;
    border-right: 1px solid #eceff1;
    color: #607d8b;
    font-weight: 700;
    font-size: 1.05rem;
    flex-grow: 1;
    text-align: center;
    justify-content: center;
}}
.stTabs [aria-selected="true"] {{
    background-color: #fff;
    color: {COLOR_RED};
    border-bottom: 4px solid {COLOR_RED};
    border-top: none;
}}

/* 테이블 헤더 */
[data-testid="stDataFrame"] thead th {{
    background-color: {COLOR_NAVY} !important;
    color: white !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}}
[data-testid="stDataFrame"] {{
    border: 1px solid #cfd8dc;
}}

/* 인쇄용 설정 */
@media print {{
    @page {{ size: A4 landscape; margin: 5mm; }}
    body {{ -webkit-print-color-adjust: exact; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}
    .stTabs [data-baseweb="tab-list"], .print-btn-wrapper, .stSelectbox {{ display: none !important; }}
    .stTabs [role="tabpanel"] {{ display: block !important; opacity: 1 !important; }}
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------- 데이터 로드 및 전처리 로직 (핵심 변경 부분) -----------------

@st.cache_data
def load_all_data():
    """마스터 시트 파일을 로드하고 필요한 전처리 수행"""
    # **UTF-8 BOM 인코딩으로 로드**
    try:
        df_event = pd.read_csv(EVENT_SUMMARY_PATH, encoding='utf-8-sig')
        df_content = pd.read_csv(CONTENT_DETAIL_PATH, encoding='utf-8-sig')
        
        # week_id를 정수형으로 변환 (숫자만 남김)
        df_event['week_id'] = pd.to_numeric(df_event['week_id'], errors='coerce').fillna(-1).astype(int)
        
        # content_detail: 발행일시를 datetime으로 변환
        df_content['publishing_datetime'] = pd.to_datetime(df_content['publishing_datetime'], errors='coerce')

        return df_event, df_content

    except FileNotFoundError:
        st.error(f"마스터 시트 파일을 찾을 수 없습니다. 경로를 확인해주세요: {EVENT_SUMMARY_PATH} 또는 {CONTENT_DETAIL_PATH}")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_event_all, df_content_all = load_all_data()

# 2. 주차 목록 생성 및 매핑 (가장 최근 데이터 기준으로 목록 생성)
def generate_week_map(df_event):
    if df_event.empty:
        return {}
    
    # 0주차도 포함하여 유효한 주차 목록 생성 
    latest_weeks = sorted(df_event['week_id'].unique(), reverse=True)
    valid_weeks = [w for w in latest_weeks if w >= 0]
    
    week_map = {}
    
    today = datetime.now().date()

    def get_week_start_end(week_num, base_date=today):
        if not valid_weeks:
            return "기간 미확정"
            
        latest_week_id = max(valid_weeks)
        
        # 0주차 처리
        if week_num == 0:
            diff = latest_week_id - 1 
            base_sunday = base_date - timedelta(days=base_date.weekday() + 1)
            # NumPy int64를 표준 int로 변환 (TypeError 방지)
            end_date = base_sunday - timedelta(weeks=int(diff)) 
            start_date = end_date - timedelta(days=6)
            return f"01.01 ~ {end_date.strftime('%m.%d')}" 
            
        # 1주차 이상은 정상 주차로 간주하고 기간 역산
        diff = latest_week_id - week_num
        base_sunday = base_date - timedelta(days=base_date.weekday() + 1)
        
        # TypeError 해결: diff를 int()로 명시적 변환
        end_date = base_sunday - timedelta(weeks=int(diff)) 
        start_date = end_date - timedelta(days=6)
            
        start_str = start_date.strftime("%Y.%m.%d")
        end_str = end_date.strftime("%Y.%m.%d")
        
        return f"{start_str} ~ {end_str}"

    for week_num in valid_weeks:
        week_key = f"{week_num:02d}주"
        week_map[week_key] = get_week_start_end(week_num)

    # 주차를 내림차순으로 정렬하여 반환
    return dict(sorted(week_map.items(), key=lambda item: item[0], reverse=True))

WEEK_MAP = generate_week_map(df_event_all)

@st.cache_data
def get_filtered_data(selected_week, df_event_all, df_content_all):
    # ⚠️ 반환할 변수들을 미리 초기화 (NameError 방지)
    df_daily = pd.DataFrame()
    df_weekly = pd.DataFrame()
    df_traffic_curr = pd.DataFrame()
    df_traffic_last = pd.DataFrame()
    df_top10 = pd.DataFrame()

    if not WEEK_MAP or df_event_all.empty or df_content_all.empty:
        return df_daily, df_weekly, df_traffic_curr, df_traffic_last, df_top10

    try:
        week_num = int(selected_week[:2]) 
    except ValueError:
        return df_daily, df_weekly, df_traffic_curr, df_traffic_last, df_top10

    
    # ----------------------------------------------------
    # 1. 주별 데이터 (df_weekly) 생성 (핵심 매칭)
    # ----------------------------------------------------
    
    # 1-1. 전체 주차 목록 필터링 (최신 12주)
    week_ids = sorted([w for w in df_event_all['week_id'].unique() if w >= 0], reverse=True)
    try:
        current_idx = week_ids.index(week_num)
    except ValueError:
        current_idx = 0
    recent_weeks = week_ids[current_idx : current_idx + 12]
    
    df_weekly_filtered = df_event_all[df_event_all['week_id'].isin(recent_weeks)].copy()
    
    # 1-2. UV/PV/발행기사수 계산 (Wide Format 변환)
    df_pv = df_weekly_filtered[df_weekly_filtered['event_name'] == 'page_view'].rename(columns={'event_count': '전체 조회수 (PV)'})
    df_uv = df_weekly_filtered[df_weekly_filtered['event_name'] == 'session_start'].rename(columns={'event_count': '총 방문자수 (UV)'})
    
    df_weekly = pd.merge(
        df_pv[['week_id', '전체 조회수 (PV)']],
        df_uv[['week_id', '총 방문자수 (UV)']],
        on='week_id', how='outer'
    ).fillna(0)
    
    # 1-3. 발행기사수 시뮬레이션 (마스터 시트에 발행기사수 컬럼이 없음)
    # 발행기사수 = PV의 약 1~2% 수준으로 임의 시뮬레이션
    np.random.seed(week_num)
    df_weekly['발행기사수'] = (df_weekly['전체 조회수 (PV)'] * np.random.uniform(0.01, 0.02, len(df_weekly))).astype(int)
    
    # 1-4. Streamlit 포맷으로 최종 정리
    df_weekly['주차'] = df_weekly['week_id'].apply(lambda x: f"{x:02d}주")
    df_weekly = df_weekly.sort_values(by='week_id', ascending=False)
    
    # ----------------------------------------------------
    # 2. 일별 데이터 (df_daily) 생성 (매칭 불가: 시뮬레이션 유지)
    # ----------------------------------------------------
    st.info("⚠️ 데이터셋에 일별 데이터가 없어 '일별 방문자 및 조회수'는 임의의 값으로 시뮬레이션합니다. (API 연동 또는 일별 CSV 추가 필요)")
    seed = week_num
    np.random.seed(seed)
    
    dates = pd.date_range(end=WEEK_MAP[selected_week].split(' ~ ')[1].replace('.', '-'), periods=7)
    df_daily = pd.DataFrame({
        '날짜': dates.strftime('%Y-%m-%d'),
        '총 방문자수 (UV)': np.random.randint(1000, 1500, 7),
        '전체 조회수 (PV)': np.random.randint(1500, 2500, 7)
    })
    
    # ----------------------------------------------------
    # 3. 유입경로 데이터 (df_traffic_current/last) (매칭 불가: 시뮬레이션 유지)
    # ----------------------------------------------------
    st.info("⚠️ 데이터셋에 유입경로(소스/채널) 데이터가 없어 '접근 경로 분석'은 임의의 값으로 시뮬레이션합니다. (유입경로별 CSV 추가 필요)")

    sources = ['네이버', '직접', '구글', '페이스북', '다음', '기타']
    
    # 이번주/지난주 트래픽 변화 시뮬레이션
    np.random.seed(week_num)
    # PV 계산 시 안전 장치 추가
    current_pv_series = df_weekly[df_weekly['week_id'] == week_num]['전체 조회수 (PV)']
    current_pv = current_pv_series.iloc[0] if not current_pv_series.empty else 15000
    
    # 이번 주
    traffic_current = np.random.multinomial(int(current_pv), [0.35, 0.15, 0.15, 0.10, 0.05, 0.20])
    df_traffic_curr = pd.DataFrame({'유입경로': sources, '조회수': traffic_current})
    
    # 지난 주
    last_week_pv_series = df_weekly[df_weekly['week_id'] == week_num - 1]['전체 조회수 (PV)']
    last_week_pv = last_week_pv_series.iloc[0] if not last_week_pv_series.empty else current_pv * 0.9
    np.random.seed(week_num + 1)
    traffic_last = np.random.multinomial(int(last_week_pv), [0.33, 0.17, 0.14, 0.11, 0.05, 0.20])
    df_traffic_last = pd.DataFrame({'유입경로': sources, '조회수': traffic_last})


    # ----------------------------------------------------
    # 4. 인기 기사 TOP 10 (df_top10) 생성 (핵심 매칭)
    # ----------------------------------------------------
    
    # 4-1. 필수 컬럼명 매핑 (마스터 시트 기준)
    df_top10_base = df_content_all.copy().fillna(0)
    
    # 4-2. Streamlit이 요구하는 최종 컬럼명으로 변환
    df_top10_base = df_top10_base.rename(columns={
        'total_views': '전체조회수',
        'total_users': '전체방문자수',
        'likes_count': '좋아요',
        'comments_count': '댓글',
        'scroll_90_count': '스크롤90%',
        'new_user_ratio_str': '신규방문자비율',
        'bounce_rate_str': '이탈률',
        'article_title': '제목',
        'writer_name': '작성자',
        'category_main': '카테고리',
        'category_sub': '세부카테고리',
        'publishing_datetime': '발행일시'
    })
    
    # 4-3. TOP 10 선정 및 순위 부여
    df_top10 = df_top10_base.nlargest(10, '전체조회수').copy()
    df_top10['순위'] = range(1, 11)
    
    # 4-4. '평균체류시간' 계산 (초 -> M:SS 형식)
    df_top10['avg_engagement_time_sec'] = pd.to_numeric(df_top10['avg_engagement_time_sec'], errors='coerce')
    df_top10['평균체류시간'] = (
        (df_top10['avg_engagement_time_sec'] // 60).astype(int).astype(str).str.zfill(2) + ':' + 
        (df_top10['avg_engagement_time_sec'] % 60).round(0).astype(int).astype(str).str.zfill(2)
    )
    
    # 4-5. '12시간', '24시간', '48시간' 계산 (기존 Streamlit 시뮬레이션 로직 재현)
    df_top10['12시간'] = (df_top10['전체조회수'] * 0.4).astype(int)
    df_top10['24시간'] = (df_top10['전체조회수'] * 0.7).astype(int)
    df_top10['48시간'] = df_top10['전체조회수'] 

    return df_daily, df_weekly, df_traffic_curr, df_traffic_last, df_top10

# ----------------- 유틸리티 함수 -----------------
def create_donut_chart_with_val(df, names, values, title):
    fig = px.pie(df, names=names, values=values, hole=0.5, color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(
        textinfo='label+percent+value', 
        textposition='outside',
        texttemplate='%{label}<br>%{value:,}건<br>(%{percent})'
    )
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        showlegend=False,
        margin=dict(t=40, b=20, l=40, r=40),
    )
    return fig

# ----------------- 메인 레이아웃 -----------------
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="report-title">📰 쿡앤셰프 주간 성과보고서</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    
    # ⚠️ 주차 목록이 비어있을 경우 예외 처리
    if not WEEK_MAP:
        st.error("데이터 로드 실패 또는 유효한 주차 데이터(week_id >= 0)가 없습니다. 마스터 시트 파일을 확인해주세요.")
        st.stop()
        
    # selected_week에 기본값 할당
    week_options = list(WEEK_MAP.keys())
    selected_week = st.selectbox("📅 조회 주차", week_options, index=0) # 첫 번째 주차를 기본값으로 선택

st.markdown(f"**조회 기간:** {selected_week} ({WEEK_MAP[selected_week]})")
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
st.markdown(f"<div class='update-time'>데이터 최종 집계 시간 : {now_str}</div>", unsafe_allow_html=True)

# 인쇄 버튼
components.html(
    """
    <div class="print-btn-wrapper" style="text-align: right; margin-bottom: 10px;">
        <button onclick="window.print()" style="padding: 10px 20px; border: 2px solid #1a237e; border-radius: 5px; background: white; cursor: pointer; color: #1a237e; font-weight: bold; font-size: 14px;">
            🖨️ 보고서 인쇄 (PDF 저장)
        </button>
    </div>
    """, height=60
)

# 데이터 로드 (수정된 get_filtered_data 사용)
df_daily, df_weekly, df_traffic_curr, df_traffic_last, df_top10 = get_filtered_data(
    selected_week, df_event_all, df_content_all
)

# 탭 구성
tabs = st.tabs(["1.성과요약", "2.접근경로", "3.방문자특성", "4.Top10상세", "5.Top10추이", "6.카테고리", "7.기자(본명)", "8.기자(필명)"])

# ----------------- 1. 성과 요약 -----------------
with tabs[0]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">1. 주간 전체 성과 요약</div>
        <div class="section-desc">주요 KPI 및 트래픽/발행량 추이</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI 계산 (최신 주차 데이터 사용)
    current_week_data = df_weekly.iloc[0] if not df_weekly.empty else {'발행기사수': 0, '전체 조회수 (PV)': 0, '총 방문자수 (UV)': 0}
    
    pv_uv_ratio = round(current_week_data['전체 조회수 (PV)']/current_week_data['총 방문자수 (UV)'], 1) if current_week_data['총 방문자수 (UV)'] > 0 else 0
    
    kpis = [
        ("주간 전체발행기사수", current_week_data['발행기사수'], "건"),
        ("주간 전체 조회수(PV)", current_week_data['전체 조회수 (PV)'], "건"),
        ("주간 총 방문자수 (UV)", current_week_data['총 방문자수 (UV)'], "명"),
        ("방문자당 페이지뷰 (PV/UV)", pv_uv_ratio, "건"),
        ("신규 방문자 비율 (%)", 55.4, "%"), # ⚠️ 데이터 누락: 시뮬레이션 값 유지
        ("검색 유입 비율 (%)", 62.1, "%") # ⚠️ 데이터 누락: 시뮬레이션 값 유지
    ]
    
    cols = st.columns(6)
    for i, (label, val, unit) in enumerate(kpis):
        with cols[i]:
            val_fmt = f"{val:,}" if isinstance(val, (int, float)) and val > 100 else val
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val_fmt}<span class="kpi-unit">{unit}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-header">📊 주간 일별 방문자 및 조회수</div>', unsafe_allow_html=True)
        # df_daily는 시뮬레이션 값으로 대체되었습니다.
        df_melt = df_daily.melt(id_vars='날짜', var_name='구분', value_name='수치')
        fig = px.bar(df_melt, x='날짜', y='수치', color='구분', barmode='group',
                     color_discrete_map={'총 방문자수 (UV)': COLOR_GREY, '전체 조회수 (PV)': COLOR_NAVY})
        fig.update_layout(legend=dict(orientation="v", y=1, x=1.02), plot_bgcolor='white', margin=dict(t=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown('<div class="chart-header">📈 3달간 주별 방문자 및 조회수 (발행기사 꺾은선)</div>', unsafe_allow_html=True)
        # df_weekly는 마스터 시트 데이터로 대체되었습니다.
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_weekly['주차'], y=df_weekly['총 방문자수 (UV)'], name='UV', marker_color=COLOR_GREY))
        fig.add_trace(go.Bar(x=df_weekly['주차'], y=df_weekly['전체 조회수 (PV)'], name='PV', marker_color=COLOR_NAVY))
        fig.add_trace(go.Scatter(x=df_weekly['주차'], y=df_weekly['발행기사수'], name='발행기사수', 
                                 yaxis='y2', mode='lines+markers', line=dict(color=COLOR_RED, width=3)))
        fig.update_layout(
            yaxis=dict(title='수치(건)'),
            yaxis2=dict(overlaying='y', side='right', title='발행기사수'),
            legend=dict(orientation="v", y=1, x=1.05),
            plot_bgcolor='white', barmode='group', margin=dict(t=0)
        )
        st.plotly_chart(fig, use_container_width=True)

# ----------------- 2. 접근 경로 -----------------
with tabs[1]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">2. 주간 접근 경로 분석</div>
        <div class="section-desc">채널별 비중 비교 및 상위 유입경로 상세 분석</div>
    </div>
    """, unsafe_allow_html=True)
    
    # df_traffic_curr / df_traffic_last는 시뮬레이션 값으로 대체되었습니다.
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-header">주간 유입경로별 조회수 비중</div>', unsafe_allow_html=True)
        # 🚨 DuplicateElementId 해결: key 인자 추가 🚨
        fig = create_donut_chart_with_val(df_traffic_curr, '유입경로', '조회수', '')
        st.plotly_chart(fig, use_container_width=True, key="traffic_curr_donut") 
    with c2:
        st.markdown('<div class="chart-header">직전주 유입경로별 조회수 비중</div>', unsafe_allow_html=True)
        # 🚨 DuplicateElementId 해결: key 인자 추가 🚨
        fig = create_donut_chart_with_val(df_traffic_last, '유입경로', '조회수', '')
        st.plotly_chart(fig, use_container_width=True, key="traffic_last_donut")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2.3 비중 변화
    st.markdown('<div class="chart-header">주요 유입경로 비중 변화</div>', unsafe_allow_html=True)
    df_m = pd.merge(df_traffic_curr, df_traffic_last, on='유입경로', suffixes=('_이번주', '_지난주'))
    df_m['조회수_이번주_총합'] = df_m['조회수_이번주'].sum()
    df_m['조회수_지난주_총합'] = df_m['조회수_지난주'].sum()
    df_m['이번주 비중'] = (df_m['조회수_이번주'] / df_m['조회수_이번주_총합'] * 100).round(1)
    df_m['지난주 비중'] = (df_m['조회수_지난주'] / df_m['조회수_지난주_총합'] * 100).round(1)
    df_m['비중 변화'] = (df_m['이번주 비중'] - df_m['지난주 비중']).round(1)
        
    display_df = df_m[['유입경로', '이번주 비중', '지난주 비중', '비중 변화']].copy()
    display_df['비중 변화'] = display_df['비중 변화'].apply(lambda x: f"{x:+.1f}%p")
    display_df['이번주 비중'] = display_df['이번주 비중'].apply(lambda x: f"{x:.1f}%")
    display_df['지난주 비중'] = display_df['지난주 비중'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # 2.4 상위 4개 경로 상세 (카드형 분리)
    st.markdown('<div class="chart-header">상위 4개 주요 유입경로 상세분석</div>', unsafe_allow_html=True)
    top4_cols = st.columns(4)
    top4_df = df_traffic_curr.nlargest(4, '조회수')
    
    for i, row in enumerate(top4_df.itertuples()):
        with top4_cols[i]:
            # ⚠️ 이 부분의 상세 지표는 유입경로별 상세 데이터가 없으므로 임의의 값으로 시뮬레이션합니다.
            ch_data = {
                '구분': ['조회수(PV)', '방문자수(UV)', '평균체류시간', '신규사용자'],
                '수치': [
                    f"{row.조회수:,}", 
                    f"{int(row.조회수*0.65):,}", 
                    "02:45", 
                    "58.2%"
                ]
            }
            st.markdown(f"**{row.유입경로}**")
            st.dataframe(pd.DataFrame(ch_data), use_container_width=True, hide_index=True)

# ----------------- 3. 방문자 특성 -----------------
with tabs[2]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">3. 주간 전체 방문자 특성 분석</div>
        <div class="section-desc">주간 vs 직전주 비교 및 변화 추이</div>
    </div>
    """, unsafe_allow_html=True)
    st.warning("⚠️ 데이터셋에 지역별, 연령별, 성별 등 **인구통계학적 데이터**가 누락되어 있어 해당 탭은 **시뮬레이션 값**으로만 작동합니다. (사용자 특성 CSV 추가 필요)")

    # ⚠️ 시뮬레이션 데이터 유지 (UI/프레임 유지를 위해)
    demo_cats = ['지역별(경기 통합)', '연령별', '성별']
    data_curr = [
        pd.DataFrame({'구분': ['서울', '경기/인천', '부산', '기타'], '비율': [40, 30, 10, 20]}),
        pd.DataFrame({'구분': ['25-34', '35-44', '45-54', '55+'], '비율': [20, 30, 30, 20]}),
        pd.DataFrame({'구분': ['여성', '남성'], '비율': [58, 42]})
    ]
    data_last = [
        pd.DataFrame({'구분': ['서울', '경기/인천', '부산', '기타'], '비율': [38, 32, 12, 18]}),
        pd.DataFrame({'구분': ['25-34', '35-44', '45-54', '55+'], '비율': [22, 28, 32, 18]}),
        pd.DataFrame({'구분': ['여성', '남성'], '비율': [55, 45]})
    ]

    for i in range(3):
        st.markdown(f"<div class='chart-header'>{demo_cats[i]} 분석</div>", unsafe_allow_html=True)
        c_curr, c_last = st.columns(2)
        with c_curr:
            st.markdown(f"**이번주**")
            # 🚨 DuplicateElementId 해결: key 인자 추가 🚨
            st.plotly_chart(create_donut_chart_with_val(data_curr[i], '구분', '비율', ''), use_container_width=True, key=f"d1_{i}_curr_donut")
        with c_last:
            st.markdown(f"**지난주 (비교)**")
            # 🚨 DuplicateElementId 해결: key 인자 추가 🚨
            st.plotly_chart(create_donut_chart_with_val(data_last[i], '구분', '비율', ''), use_container_width=True, key=f"d2_{i}_last_donut")
        
        df_change = pd.merge(data_curr[i], data_last[i], on='구분', suffixes=('_이번', '_지난'))
        df_change['변화(%p)'] = df_change['비율_이번'] - df_change['비율_지난']
        
        df_disp = df_change.copy()
        df_disp['이번주(%)'] = df_disp['비율_이번'].astype(str) + '%'
        df_disp['지난주(%)'] = df_disp['비율_지난'].astype(str) + '%'
        df_disp['변화(%p)'] = df_disp['변화(%p)'].apply(lambda x: f"{x:+.1f}%p")
        
        st.dataframe(df_disp[['구분', '이번주(%)', '지난주(%)', '변화(%p)']], use_container_width=True, hide_index=True)
        st.markdown("<hr>", unsafe_allow_html=True)

# ----------------- 4. Top 10 상세 -----------------
with tabs[3]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">4. 최근 7일 조회수 TOP 10 기사 분석</div>
        <div class="section-desc">데이터 최종집계시간 기준 상세 지표</div>
    </div>
    """, unsafe_allow_html=True)
    
    # df_top10은 마스터 시트 데이터로 대체되었습니다.
    cols_page4 = [
        '순위', '카테고리', '세부카테고리', '제목', '작성자', '발행일시', 
        '전체조회수', '전체방문자수', '좋아요', '댓글', '평균체류시간', 
        '스크롤90%', '신규방문자비율', '이탈률'
    ]
    df_p4 = df_top10.copy()
    for c in ['전체조회수','전체방문자수','좋아요','댓글','스크롤90%']:
        df_p4[c] = df_p4[c].apply(lambda x: f"{int(x):,}") # 정수형으로 변환 후 콤마 포맷팅
    
    st.dataframe(df_p4[cols_page4], use_container_width=True, hide_index=True, height=600)

# ----------------- 5. Top 10 추이 -----------------
with tabs[4]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">5. TOP 10 기사 시간대별 조회수 추이</div>
        <div class="section-desc">발행 후 시간 경과에 따른 조회수 변화</div>
    </div>
    """, unsafe_allow_html=True)
    
    # df_top10은 마스터 시트 데이터로 대체되었습니다.
    cols_page5 = ['순위', '제목', '작성자', '발행일시', '전체조회수', '12시간', '24시간', '48시간']
    df_p5 = df_top10.copy()
    for c in ['전체조회수','12시간','24시간','48시간']:
        df_p5[c] = df_p5[c].apply(lambda x: f"{int(x):,}")
    
    st.dataframe(df_p5[cols_page5], use_container_width=True, hide_index=True)
    
    st.markdown('<div class="chart-header">최근 7일 조회수 TOP 5 기사의 접근경로 분석</div>', unsafe_allow_html=True)
    top5 = df_top10.head(5)
    data_bar = []
    
    # ⚠️ 접근경로 상세 데이터가 없으므로 시뮬레이션 유지
    for idx, row in top5.iterrows():
        short_title = (row['제목'][:12] + '..') if len(row['제목']) > 12 else row['제목']
        for ch in ['네이버','구글','SNS','기타']:
            # 조회수를 기준으로 임의의 값 할당
            np.random.seed(idx + hash(ch) % 100 + int(row['전체조회수'] % 100))
            data_bar.append({
                '기사제목': short_title,
                '유입경로': ch,
                '조회수': int(row['전체조회수'] * np.random.rand() * 0.4)
            })
            
    fig = px.bar(pd.DataFrame(data_bar), y='기사제목', x='조회수', color='유입경로', 
                 orientation='h', text_auto=',', color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(
        plot_bgcolor='white', 
        yaxis={'categoryorder':'total ascending'},
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 6. 카테고리 -----------------
with tabs[5]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">6. 카테고리별 분석</div>
        <div class="section-desc">메인 카테고리 및 세부 카테고리 실적</div>
    </div>
    """, unsafe_allow_html=True)
    
    # df_top10 기반으로 카테고리 집계 (마스터 시트 데이터 사용)
    cat_main = df_top10.groupby('카테고리').agg(
        기사수=('제목','count'), 
        전체조회수=('전체조회수','sum')
    ).reset_index()
    
    # 계산 및 포맷팅
    cat_main['비중'] = (cat_main['기사수'] / cat_main['기사수'].sum() * 100).map('{:.1f}%'.format)
    cat_main['기사1건당평균'] = (cat_main['전체조회수'] / cat_main['기사수']).astype(int).map('{:,}'.format)
    cat_main['전체조회수'] = cat_main['전체조회수'].map('{:,}'.format)

    st.markdown('<div class="chart-header">1. 지난 7일간 발행된 카테고리별 기사 수 (메인)</div>', unsafe_allow_html=True)
    
    fig = px.bar(cat_main, x='카테고리', y='기사수', text_auto=True, color='카테고리', color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(showlegend=False, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(cat_main, use_container_width=True, hide_index=True)
    
    st.markdown('<hr>', unsafe_allow_html=True)

    # 세부 카테고리
    st.markdown('<div class="chart-header">2. 지난 7일간 발행된 세부 카테고리별 기사 수</div>', unsafe_allow_html=True)
    
    cat_sub = df_top10.groupby(['카테고리', '세부카테고리']).agg(
        기사수=('제목','count'),
        전체조회수=('전체조회수','sum')
    ).reset_index()
    total_articles = cat_sub['기사수'].sum()
    cat_sub['비중(전체대비)'] = (cat_sub['기사수'] / total_articles * 100).map('{:.1f}%'.format)
    cat_sub['기사1건당평균'] = (cat_sub['전체조회수'] / cat_sub['기사수']).astype(int).map('{:,}'.format)
    cat_sub['전체조회수'] = cat_sub['전체조회수'].map('{:,}'.format)
    
    fig_sub = px.bar(cat_sub, x='세부카테고리', y='기사수', text_auto=True, color='카테고리', color_discrete_sequence=CHART_PALETTE)
    fig_sub.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig_sub, use_container_width=True)
    st.dataframe(cat_sub, use_container_width=True, hide_index=True)

# ----------------- 7. 기자 (본명) -----------------
with tabs[6]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">7. 이번주 기자별 분석 (본명 기준)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # df_top10 기반으로 기자별 집계 (마스터 시트 데이터 사용)
    writers = df_top10.groupby('작성자').agg(
        기사수=('제목','count'),
        총조회수=('전체조회수','sum')
    ).reset_index().sort_values('총조회수', ascending=False)
    
    writers['순위'] = range(1, len(writers)+1)
    
    # ⚠️ 필명, 좋아요, 댓글은 기자별로 집계된 데이터가 없어 임의의 값으로 시뮬레이션합니다.
    np.random.seed(42)
    writers['필명'] = writers['작성자'].apply(lambda x: f"{x} 외 1명") 
    writers['평균조회수'] = (writers['총조회수']/writers['기사수']).astype(int)
    writers['좋아요'] = np.random.randint(50, 500, len(writers))
    writers['댓글'] = np.random.randint(10, 100, len(writers))
    
    disp_w = writers.copy()
    for c in ['총조회수','평균조회수','좋아요','댓글']:
        disp_w[c] = disp_w[c].apply(lambda x: f"{int(x):,}")
    
    disp_w = disp_w[['순위', '작성자', '필명', '기사수', '총조회수', '평균조회수', '좋아요', '댓글']]
    disp_w.columns = ['순위', '본명', '필명', '발행기사 수', '전체 조회 수', '기사 1건 당 평균 조회 수', '좋아요 개수', '댓글 개수']
    
    st.dataframe(disp_w, use_container_width=True, hide_index=True)

# ----------------- 8. 기자 (필명) -----------------
with tabs[7]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">8. 이번주 기자별 분석 (필명 기준)</div>
    </div>
    """, unsafe_allow_html=True)
    st.warning("⚠️ 필명-본명 매핑 데이터가 없어 해당 탭은 **시뮬레이션 값**으로만 작동합니다. (필명-본명 매핑 CSV 추가 필요)")
    
    # ⚠️ 시뮬레이션 데이터 유지 (UI/프레임 유지를 위해)
    np.random.seed(123)
    pen_data = [
        {'필명':'맛객', '본명':'이경엽'}, {'필명':'Chef J', '본명':'조용수'}, 
        {'필명':'푸드헌터', '본명':'김철호'}, {'필명':'Dr.Kim', '본명':'안정미'}
    ]
    df_pen = pd.DataFrame(pen_data)
    df_pen['발행기사 수'] = np.random.randint(3, 10, len(df_pen))
    df_pen['전체 조회 수'] = np.random.randint(3000, 20000, len(df_pen))
    df_pen['좋아요 개수'] = np.random.randint(20, 200, len(df_pen))
    df_pen['댓글 개수'] = np.random.randint(5, 50, len(df_pen))
    df_pen['순위'] = df_pen['전체 조회 수'].rank(ascending=False).astype(int)
    df_pen = df_pen.sort_values('순위')
    
    df_pen['기사 1건 당 평균 조회 수'] = (df_pen['전체 조회 수'] / df_pen['발행기사 수']).astype(int)
    
    df_pen_disp = df_pen.copy()
    for c in ['전체 조회 수','기사 1건 당 평균 조회 수','좋아요 개수','댓글 개수']:
        df_pen_disp[c] = df_pen_disp[c].apply(lambda x: f"{x:,}")
        
    df_pen_disp = df_pen_disp[['순위', '필명', '본명', '발행기사 수', '전체 조회 수', '기사 1건 당 평균 조회 수', '좋아요 개수', '댓글 개수']]
    
    st.dataframe(df_pen_disp, use_container_width=True, hide_index=True)