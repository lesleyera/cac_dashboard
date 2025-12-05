import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ----------------- 페이지 설정 -----------------
st.set_page_config(
    layout="wide",
    page_title="쿡앤셰프 주간 성과보고서",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# ----------------- CSS & 스타일링 (디자인 업그레이드) -----------------
CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css');

/* 전체 폰트 및 레이아웃 */
body {
    background-color: #ffffff;
    font-family: 'Pretendard', sans-serif;
    color: #111827;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
    max_width: 1600px; /* 화면 폭 넓게 활용 */
}
[data-testid="stSidebar"] { display: none; }

/* 헤더 타이틀 */
.report-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #3e2723; /* 다크 브라운 */
    margin-bottom: 0.5rem;
    letter-spacing: -0.03em;
    border-bottom: 4px solid #3e2723;
    padding-bottom: 15px;
}

/* 데이터 집계 시간 강조 (파란색 유지) */
.update-time {
    color: #1e88e5; /* 선명한 파랑 */
    font-weight: 700;
    font-size: 1.1rem;
    text-align: right;
    margin-top: -15px;
    margin-bottom: 30px;
    font-family: monospace;
}

/* KPI 카드 스타일 */
.kpi-container {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-top: 5px solid #1e88e5; /* 상단 파란색 포인트 */
    border-radius: 8px;
    padding: 25px 15px;
    text-align: center;
    margin-bottom: 10px;
    height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
}
.kpi-label {
    font-size: 1.05rem;
    font-weight: 700;
    color: #5d4037; /* 브라운 텍스트 */
    margin-bottom: 12px;
}
.kpi-value {
    font-size: 2.4rem;
    font-weight: 800;
    color: #1565c0;    /* 파란색 숫자 */
    line-height: 1;
    letter-spacing: -0.03em;
}
.kpi-unit {
    font-size: 1rem;
    font-weight: 500;
    color: #9ca3af;
    margin-left: 3px;
}

/* 섹션 타이틀 (화면 폭만큼 꽉 차게, 디자인 개선) */
.section-header-container {
    margin-top: 50px;
    margin-bottom: 25px;
    padding: 15px 20px;
    background-color: #efebe9; /* 연한 브라운 배경 */
    border-left: 8px solid #3e2723; /* 진한 브라운 바 */
    border-radius: 4px;
}
.section-header {
    font-size: 1.7rem;
    font-weight: 800;
    color: #3e2723;
    margin: 0;
}
.section-desc {
    font-size: 1rem;
    color: #6d4c41;
    margin-top: 5px;
}

/* 차트 소제목 */
.chart-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: #4e342e;
    margin-top: 25px;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 4px solid #8d6e63; /* 브라운 라인 */
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    border-bottom: 2px solid #d7ccc8;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: #fafafa;
    border-radius: 8px 8px 0 0;
    color: #795548;
    font-weight: 700;
    border: 1px solid transparent;
    font-size: 1rem;
}
.stTabs [aria-selected="true"] {
    background-color: #fff;
    color: #3e2723;
    border: 1px solid #d7ccc8;
    border-bottom: 1px solid #fff;
}

/* 인쇄용 설정 */
@media print {
    @page { size: A4 landscape; margin: 10mm; }
    body { -webkit-print-color-adjust: exact; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stTabs [data-baseweb="tab-list"], .print-btn-wrapper, .stSelectbox { display: none !important; }
    .stTabs [role="tabpanel"] { display: block !important; opacity: 1 !important; }
    .update-time { color: #1565c0 !important; }
}

/* 유틸리티 */
.spacer { margin-bottom: 40px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ----------------- 컬러 팔레트 (브라운 & 블루) -----------------
# 따뜻한 브라운(Brown)과 신뢰감 있는 파란색(Blue)의 조화
COLOR_BROWN = "#8d6e63"   # 주요 차트 색상 (브라운)
COLOR_BLUE = "#1e88e5"    # 주요 차트 색상 (파랑)
COLOR_BROWN_DARK = "#3e2723"
COLOR_GREY = "#bdbdbd"
COLOR_LIGHT_BLUE = "#90caf9"

# 차트용 시퀀스 (브라운, 블루 교차)
CHART_PALETTE = [COLOR_BROWN, COLOR_BLUE, "#a1887f", "#42a5f5", COLOR_GREY]

# ----------------- 데이터 생성 로직 -----------------
WEEK_MAP = {
    "44주": "2025.10.27 ~ 2025.11.02",
    "43주": "2025.10.20 ~ 2025.10.26",
    "42주": "2025.10.13 ~ 2025.10.19",
    "41주": "2025.10.06 ~ 2025.10.12",
    "40주": "2025.09.29 ~ 2025.10.05",
    "39주": "2025.09.22 ~ 2025.09.28",
    "38주": "2025.09.15 ~ 2025.09.21",
}

@st.cache_data
def get_filtered_data(selected_week):
    seed = int(selected_week[:2])
    np.random.seed(seed)
    
    # 일별 데이터
    dates = pd.date_range(end=WEEK_MAP[selected_week].split(' ~ ')[1].replace('.', '-'), periods=7)
    df_daily = pd.DataFrame({
        '날짜': dates.strftime('%Y-%m-%d'),
        '총 방문자수 (UV)': np.random.randint(1000, 1500, 7),
        '전체 조회수 (PV)': np.random.randint(1500, 2500, 7)
    })
    
    # 주별 데이터
    weeks_list = [f"{i}주" for i in range(int(selected_week[:2]), int(selected_week[:2])-12, -1)]
    df_weekly = pd.DataFrame({
        '주차': weeks_list,
        '총 방문자수 (UV)': np.random.randint(7000, 9000, 12),
        '전체 조회수 (PV)': np.random.randint(12000, 18000, 12),
        '발행기사수': np.random.randint(120, 160, 12)
    })

    # 유입경로 데이터
    sources = ['네이버 검색', '직접 접속', '구글 검색', '페이스북', '기타']
    traffic_current = np.random.multinomial(13816, [0.35, 0.20, 0.15, 0.10, 0.20])
    df_traffic_current = pd.DataFrame({'유입경로': sources, '조회수': traffic_current})
    traffic_last = np.random.multinomial(12500, [0.33, 0.22, 0.14, 0.11, 0.20])
    df_traffic_last = pd.DataFrame({'유입경로': sources, '조회수': traffic_last})

    # TOP 10 데이터
    titles = [
        "[해외 셰프] 비니 치미노, '모던 할머니'의 손맛", "뉴욕 셰프들 K-푸드 배우러 샘표 연구소 찾다",
        "[호텔뉴스] 앰배서더 서울 풀만, '딸기 애프터눈 티'", "[식생활 건강] 작지만 강한 채소 '쪽파'의 효능",
        "[이슈] 2025 식품 외식 산업 전망 '푸드테크'", "[인터뷰] 미슐랭 2스타 셰프가 말하는 한식",
        "파르나스 호텔 제주, 겨울 미식 프로모션", "[Cook&Life] 과메기의 효능과 맛있게 먹는 법",
        "코트야드 메리어트 세종, 페스티브 시즌 운영", "[맛집탐방] 줄 서는 성수동 베이글 맛집"
    ]
    df_top10 = pd.DataFrame({
        '순위': range(1, 11),
        '카테고리': ['Chef', '이슈', '호텔', '건강', '이슈', '인터뷰', '호텔', '라이프', '호텔', '맛집'],
        '세부카테고리': ['인터뷰', '산업', '프로모션', '식자재', '트렌드', '스타', '이벤트', '제철', '시즌', '핫플'],
        '제목': titles,
        '작성자': ['이정호', '조용수', '조용수', '김철호', '이경엽', '안정미', '조용수', '오요리', '조용수', '이경엽'],
        '발행일시': pd.date_range(end=datetime.now(), periods=10).strftime('%Y-%m-%d %H:%M'),
        '전체조회수': np.sort(np.random.randint(500, 4000, 10))[::-1],
        '전체방문자수': np.sort(np.random.randint(400, 3500, 10))[::-1],
        '좋아요': np.random.randint(10, 150, 10),
        '댓글': np.random.randint(0, 30, 10),
        '평균체류시간': [f"0{np.random.randint(1,4)}:{np.random.randint(10,59)}" for _ in range(10)],
        '스크롤90%': np.random.randint(300, 2000, 10),
        '신규방문자비율': [f"{np.random.randint(30,80)}%" for _ in range(10)],
        '이탈률': [f"{np.random.randint(20,60)}%" for _ in range(10)]
    })
    df_top10['12시간'] = (df_top10['전체조회수'] * 0.4).astype(int)
    df_top10['24시간'] = (df_top10['전체조회수'] * 0.7).astype(int)
    df_top10['48시간'] = df_top10['전체조회수'] 

    return df_daily, df_weekly, df_traffic_current, df_traffic_last, df_top10

# ----------------- 포맷팅 유틸리티 -----------------
def fmt_num(val):
    """1000단위 콤마, 정수/실수 구분"""
    if isinstance(val, (int, np.integer)):
        return f"{val:,}"
    elif isinstance(val, float):
        return f"{val:,.1f}"
    return str(val)

# ----------------- 차트 함수 (브라운 & 블루 적용) -----------------
def create_donut_chart(df, names, values, title):
    total = df[values].sum()
    fig = px.pie(df, names=names, values=values, hole=0.5,
                 color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(textinfo='percent', textposition='inside')
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=14)),
        showlegend=True,
        legend=dict(orientation="v", y=0.5, x=1.05),
        margin=dict(t=30, b=20, l=20, r=0),
        annotations=[dict(text=f'Total<br>{total:,}', x=0.5, y=0.5, font_size=14, showarrow=False)]
    )
    return fig

# ----------------- 메인 레이아웃 -----------------
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown('<div class="report-title">📰 쿡앤셰프 주간 성과보고서</div>', unsafe_allow_html=True)
with c2:
    selected_week = st.selectbox("📅 조회 주차", list(WEEK_MAP.keys()))

st.markdown(f"**조회 기간:** {selected_week} ({WEEK_MAP[selected_week]})")
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
st.markdown(f"<div class='update-time'>데이터 최종 집계 시간 : {now_str}</div>", unsafe_allow_html=True)

# 인쇄 버튼
components.html(
    """
    <div style="text-align: right; margin-bottom: 10px;">
        <button onclick="window.print()" style="padding: 6px 12px; border: 1px solid #ccc; border-radius: 4px; background: white; cursor: pointer;">
            🖨️ 인쇄 / PDF 저장
        </button>
    </div>
    """, height=50
)

# 데이터 로드
df_daily, df_weekly, df_traffic_curr, df_traffic_last, df_top10 = get_filtered_data(selected_week)

# 탭 구성
tabs = st.tabs(["1.성과요약", "2.접근경로", "3.방문자특성", "4.Top10상세", "5.Top10추이", "6.카테고리", "7.기자(본명)", "8.기자(필명)"])

# ----------------- 1. 성과 요약 -----------------
with tabs[0]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">1. 주간 전체 성과 요약</div>
        <div class="section-desc">트래픽 규모와 발행 기사 볼륨, 방문자 행동을 한 번에 확인합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Cards
    kpis = [
        ("주간 전체발행기사수", df_weekly['발행기사수'].iloc[0], "건"),
        ("주간 전체 조회수(PV)", df_weekly['전체 조회수 (PV)'].iloc[0], "건"),
        ("주간 총 방문자수 (UV)", df_weekly['총 방문자수 (UV)'].iloc[0], "명"),
        ("방문자당 페이지뷰", round(df_weekly['전체 조회수 (PV)'].iloc[0]/df_weekly['총 방문자수 (UV)'].iloc[0], 1), "건"),
        ("신규 방문자 비율", 55.4, "%"),
        ("검색 유입 비율", 62.1, "%")
    ]
    
    cols = st.columns(6)
    for i, (label, val, unit) in enumerate(kpis):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{fmt_num(val)}<span class="kpi-unit">{unit}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-header">📊 주간 일별 방문자 및 조회수</div>', unsafe_allow_html=True)
        df_melt = df_daily.melt(id_vars='날짜', var_name='구분', value_name='수치')
        fig = px.bar(df_melt, x='날짜', y='수치', color='구분', barmode='group',
                     color_discrete_map={'총 방문자수 (UV)': COLOR_BROWN, '전체 조회수 (PV)': COLOR_BLUE})
        fig.update_layout(legend=dict(orientation="h", y=1.1), plot_bgcolor='white', margin=dict(t=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown('<div class="chart-header">📈 3개월 주별 추이 및 발행량</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_weekly['주차'], y=df_weekly['총 방문자수 (UV)'], name='UV', marker_color=COLOR_BROWN))
        fig.add_trace(go.Bar(x=df_weekly['주차'], y=df_weekly['전체 조회수 (PV)'], name='PV', marker_color=COLOR_BLUE))
        fig.add_trace(go.Scatter(x=df_weekly['주차'], y=df_weekly['발행기사수'], name='발행기사', yaxis='y2', line=dict(color='#ef4444', width=2)))
        fig.update_layout(
            yaxis2=dict(overlaying='y', side='right', title='기사수'),
            legend=dict(orientation="h", y=1.1),
            plot_bgcolor='white', barmode='group', margin=dict(t=0)
        )
        st.plotly_chart(fig, use_container_width=True)

# ----------------- 2. 접근 경로 -----------------
with tabs[1]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">2. 주간 접근 경로 분석</div>
        <div class="section-desc">검색, 직접 유입, SNS 등 주요 채널별 비중과 변화를 확인합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="chart-header">이번주 유입경로</div>', unsafe_allow_html=True)
        fig = create_donut_chart(df_traffic_curr, '유입경로', '조회수', '')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown('<div class="chart-header">지난주 유입경로</div>', unsafe_allow_html=True)
        fig = create_donut_chart(df_traffic_last, '유입경로', '조회수', '')
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown('<div class="chart-header">유입경로 비중 변화 및 상세</div>', unsafe_allow_html=True)
    
    df_m = pd.merge(df_traffic_curr, df_traffic_last, on='유입경로', suffixes=('_이번주', '_지난주'))
    df_m['이번주(%)'] = (df_m['조회수_이번주'] / df_m['조회수_이번주'].sum() * 100).astype(float)
    df_m['지난주(%)'] = (df_m['조회수_지난주'] / df_m['조회수_지난주'].sum() * 100).astype(float)
    df_m['변화(%p)'] = df_m['이번주(%)'] - df_m['지난주(%)']
    
    def color_val(val):
        color = '#d32f2f' if val > 0 else '#1565c0' if val < 0 else 'black'
        return f'color: {color}'
        
    st.dataframe(
        df_m[['유입경로', '이번주(%)', '지난주(%)', '변화(%p)']].style.format({
            '이번주(%)': '{:.1f}', 
            '지난주(%)': '{:.1f}', 
            '변화(%p)': '{:.1f}'
        }).map(color_val, subset=['변화(%p)']),
        use_container_width=True, hide_index=True
    )

    st.markdown('<div class="chart-header">상위 4개 주요 유입경로 상세</div>', unsafe_allow_html=True)
    top4 = df_traffic_curr.nlargest(4, '조회수')['유입경로'].tolist()
    detail_data = []
    for ch in top4:
        pv = int(df_traffic_curr[df_traffic_curr['유입경로'] == ch]['조회수'].values[0])
        detail_data.append({
            '채널': ch,
            '조회수(PV)': pv,
            '방문자수(UV)': int(pv * 0.7),
            '평균체류시간': "02:30",
            '신규사용자비율': "55%"
        })
    st.dataframe(
        pd.DataFrame(detail_data),
        column_config={
            "조회수(PV)": st.column_config.NumberColumn(format="%d"),
            "방문자수(UV)": st.column_config.NumberColumn(format="%d")
        },
        use_container_width=True, hide_index=True
    )

# ----------------- 3. 방문자 특성 -----------------
with tabs[2]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">3. 주간 전체 방문자 특성 분석</div>
        <div class="section-desc">지역·연령·성별 기준으로 이번주와 지난주 방문자 구성을 비교합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    demo_data = {
        '지역': pd.DataFrame({'항목':['서울','경기','부산','기타'], '비율':[45,25,10,20]}),
        '연령': pd.DataFrame({'항목':['2030','4050','60+'], '비율':[30,50,20]}),
        '성별': pd.DataFrame({'항목':['여성','남성'], '비율':[60,40]})
    }
    
    cols = st.columns(3)
    for i, (key, df) in enumerate(demo_data.items()):
        with cols[i]:
            st.markdown(f"##### {key} 분포")
            fig = px.pie(df, values='비율', names='항목', color_discrete_sequence=CHART_PALETTE)
            fig.update_traces(textinfo='percent+label', textposition='inside')
            fig.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)

# ----------------- 4. Top 10 상세 -----------------
with tabs[3]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">4. 주간 조회수 TOP 10 상세</div>
        <div class="section-desc">조회수·체류시간·이탈률 등 기사별 성과를 상세하게 확인합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    df_disp = df_top10.copy()
    num_cols = ['전체조회수','전체방문자수','좋아요','댓글','스크롤90%']
    for c in num_cols:
        df_disp[c] = df_disp[c].apply(lambda x: f"{x:,}")
        
    display_cols = ['순위','카테고리','제목','작성자','발행일시','전체조회수','전체방문자수','좋아요','댓글','평균체류시간','이탈률']
    st.dataframe(df_disp[display_cols], use_container_width=True, hide_index=True, height=500)

# ----------------- 5. Top 10 추이 -----------------
with tabs[4]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">5. TOP 10 기사 시간대별 추이</div>
        <div class="section-desc">발행 후 12/24/48시간 동안의 성장 곡선과 채널 믹스를 확인합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    df_time = df_top10.copy()
    for c in ['전체조회수','12시간','24시간','48시간']:
        df_time[c] = df_time[c].apply(lambda x: f"{x:,}")
    
    st.dataframe(df_time[['순위','제목','전체조회수','12시간','24시간','48시간']], use_container_width=True, hide_index=True)
    
    st.markdown('<div class="chart-header">TOP 5 기사 접근경로 분석</div>', unsafe_allow_html=True)
    top5 = df_top10.head(5)
    data = []
    for idx, row in top5.iterrows():
        for ch in ['네이버','구글','SNS']:
            data.append({'제목':row['제목'][:10]+'..', '채널':ch, '유입':np.random.randint(100, 1000)})
    
    fig = px.bar(pd.DataFrame(data), y='제목', x='유입', color='채널', orientation='h', 
                 text_auto=',', color_discrete_sequence=CHART_PALETTE)
    fig.update_layout(plot_bgcolor='white', yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 6. 카테고리 -----------------
with tabs[5]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">6. 카테고리별 성과</div>
        <div class="section-desc">카테고리별 기사 수, 조회수, 효율(기사당 평균 조회수)을 비교합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    cat_sum = df_top10.groupby('카테고리').agg(
        기사수=('제목','count'), 
        조회수=('전체조회수','sum')
    ).reset_index()
    cat_sum['비중'] = (cat_sum['기사수']/cat_sum['기사수'].sum()*100).map('{:.1f}%'.format)
    cat_sum['건당조회'] = (cat_sum['조회수']/cat_sum['기사수']).astype(int).map('{:,}'.format)
    cat_sum['조회수'] = cat_sum['조회수'].map('{:,}'.format)
    
    st.markdown("#### 카테고리별 상세 지표")
    st.dataframe(cat_sum, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="chart-header">카테고리별 전체 조회수 비교</div>', unsafe_allow_html=True)
    fig = px.bar(cat_sum, x='카테고리', y='기사수', text_auto=True, color_discrete_sequence=[COLOR_BROWN])
    fig.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

# ----------------- 7. 기자 (본명) -----------------
with tabs[6]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">7. 기자별 성과 (본명 기준)</div>
        <div class="section-desc">기자별 발행량과 조회·반응 지표를 통해 필진 퍼포먼스를 확인합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    writers = df_top10.groupby('작성자').agg(
        기사수=('제목','count'),
        총조회수=('전체조회수','sum')
    ).reset_index().sort_values('총조회수', ascending=False)
    
    writers['건당조회'] = (writers['총조회수']/writers['기사수']).astype(int).map('{:,}'.format)
    writers['총조회수'] = writers['총조회수'].map('{:,}'.format)
    
    st.dataframe(writers, use_container_width=True, hide_index=True)

# ----------------- 8. 기자 (필명) -----------------
with tabs[7]:
    st.markdown("""
    <div class="section-header-container">
        <div class="section-header">8. 기자별 성과 (필명 기준)</div>
        <div class="section-desc">브랜딩된 필명 관점에서의 기사 성과를 별도로 확인합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("필명 데이터가 연동되면 본명 기준과 동일한 형식으로 제공됩니다.")
    st.dataframe(writers, use_container_width=True, hide_index=True)