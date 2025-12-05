import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(layout="wide", page_title="쿡앤셰프 성과 대시보드")

st.title("👨‍🍳 쿡앤셰프 주간 웹사이트 성과 대시보드")
st.markdown("---")

## 1. 데이터 정의 (PDF 파일의 시각화 데이터를 기반으로 직접 DataFrame 구성)

# 1-1. 최근 7일 일별 사용자 및 조회수 데이터
# 데이터 출처: PDF 1페이지 막대 차트
data_recent_7_days = {
    '날짜': ['2025. 8. 3.', '2025. 8. 2.', '2025. 8. 1.', '2025. 7. 31.', '2025. 7. 30.', '2025. 7. 29.', '2025. 7. 28.'],
    '총 사용자': [878, 969, 1180, 1723, 1129, 1228, 1295],
    '조회수': [875, 1135, 1469, 2154, 1540, 1453, 1674],
}
df_recent_7_days = pd.DataFrame(data_recent_7_days).set_index('날짜')

# 1-2. 주별 총 사용자 및 조회수 (23주 ~ 32주) 데이터
# 데이터 출처: PDF 1페이지 주별 총 사용자 및 조회수 막대 차트
data_weekly = {
    '주차': ['32주', '31주', '30주', '29주', '28주', '27주', '26주', '25주', '24주', '23주'],
    '총 사용자': [86.95, 8198, 8362, 7610, 8247, 8824, 8375, 8726, 8518, 7441],
    '조회수': [95, 10300, 10316, 10037, 10169, 10879, 10851, 20607, 10744, 9802]
}
df_weekly = pd.DataFrame(data_weekly).set_index('주차')

# 1-3. 주간 방문자별 기사 접근 경로 (파이 차트) 데이터
# 데이터 출처: PDF 1페이지 주간 방문자 별 기사 접근 경로 파이 차트
data_traffic_source = {
    '접근 경로': ['m.search.naver.co...', '(direct) / (none)', 'naver / organic', 'google / organic', '(not set)', 'daum / organic', 'chatgpt.com / refer...', '기타'],
    '수': [3822, 1841, 1387, 753, 300, 200, 100, 50] # 기타 값은 PDF에 명확히 표기되지 않아 추정값 사용
}
df_traffic_source = pd.DataFrame(data_traffic_source)


## 2. 대시보드 구성 (탭을 활용해 섹션 분리)

tab1, tab2, tab3, tab4 = st.tabs(["📊 주요 성과 요약", "📰 인기 기사 분석", "🗂️ 카테고리 분석", "👤 독자 특성 분석"])

with tab1:
    st.header("1. 방문자 수 및 총 조회 수")

    col1, col2, col3, col4 = st.columns(4)
    # 주요 KPI (PDF 1페이지 박스 형태 데이터)
    col1.metric("주간 총 방문자 수", "8,214", "0.9%") 
    col2.metric("주간 총 조회수", "10,300", "-0.2%") 
    col3.metric("평균 세션 시간", "00:01:22", "-0.3%") 
    col4.metric("이벤트 수", "1,108", "-2.5%") 

    st.subheader("최근 7일 일별 사용자 및 조회수")
    col_chart_1, col_chart_2 = st.columns(2)

    with col_chart_1:
        st.write("**총 사용자**")
        fig_users = px.bar(df_recent_7_days, y='총 사용자', x=df_recent_7_days.index,
                           color_discrete_sequence=['#4C78A8']) # 파란색 계열
        st.plotly_chart(fig_users, use_container_width=True)

    with col_chart_2:
        st.write("**조회수**")
        fig_views = px.bar(df_recent_7_days, y='조회수', x=df_recent_7_days.index,
                           color_discrete_sequence=['#4C78A8'])
        st.plotly_chart(fig_views, use_container_width=True)

    st.subheader("주별 총 사용자 및 조회수 (최근 10주)")
    # 주별 총 사용자 및 조회수 막대 차트
    df_weekly_plot = df_weekly.reset_index().melt(id_vars='주차', var_name='구분', value_name='수치')
    fig_weekly = px.bar(df_weekly_plot, x='주차', y='수치', color='구분', barmode='group',
                        color_discrete_map={'총 사용자': '#4C78A8', '조회수': '#FF9933'}) # 사용자(파란색), 조회수(주황색)
    fig_weekly.update_layout(yaxis_title="수치 (단위: 천)")
    st.plotly_chart(fig_weekly, use_container_width=True)

    st.subheader("주간 방문자별 기사 접근 경로")
    # 접근 경로 파이 차트
    fig_traffic = px.pie(df_traffic_source, values='수', names='접근 경로', title='주간 방문자별 기사 접근 경로',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_traffic.update_traces(textinfo='percent+value')
    st.plotly_chart(fig_traffic, use_container_width=True)

with tab2:
    st.header("2. 주간 인기 기사 및 상세 분석")
    st.markdown("제공된 PDF의 표 데이터와 유사하게 DataFrame을 구성하여 표시할 수 있습니다.")

    # 인기 기사 목록 (PDF 2페이지 표 참고)
    data_top_articles = {
        '순위': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        '제목': [
            '[2보] 트럼프 "농산물 포함" 언급에...',
            '[상보] "쌀·소고기는 막았다지만"...',
            '[2보] 트럼프 "농산물 포함" 언급에...',
            '명태와 명란: 잊혀진 조선의 맛과 역사를...',
            '[속보] 구윤철 부총리 "쌀·소고기 등 추가 개방 없다"...',
            '진주의 밤을 채운 두 가지 맛, \'육전\'과 \'앉은뱅이밀 초콜릿\'', # 6위
            '[속보] "쌀·소고기 추가 개방 없다"... 대통령실, 한미 관세 협상 타결 발표', # 7위
            'Interview / 빵을 사랑하는 \'트로트 가수\' 최홍림, 반짝이는 화려한 도전으로...', # 8위
            '한미 통상협상 타결... 농축산물 개방 막았지만, "검역완화는 새 뇌관"', # 9위
            '"강연이 한식을 살린다"...시민과 함께 만드는 한식의 내일' # 10위
        ],
        '조회수': [3827, 2690, 1422, 979, 512, 500, 494, 493, 409, 392],
        '발행일자': [
            '2025. 7. 31.', 
            '2025. 7. 31.', 
            '2025. 7. 31.', 
            '2025. 7. 31.', 
            '2025. 7. 31.',
            '2025. 7. 29.', # 6위
            '2025. 7. 31.', # 7위
            '2025. 7. 31.', # 8위
            '2025. 7. 31.', # 9위
            '2025. 7. 31.' # 10위
        ]
    }
    df_top_articles = pd.DataFrame(data_top_articles) # 이제 모든 배열의 길이가 10입니다.

    st.dataframe(df_top_articles, height=300, use_container_width=True)

    # ... 이하 코드는 동일합니다.
    st.subheader("조회수 상위 기사별 방문 경로")
    # 방문 경로 바 차트 (PDF 2페이지 하단 바 차트)
    # 상위 1위 기사 데이터 (예시)
    data_top1_traffic = {
        '경로': ['m.search.naver.com', 'null', 'google', '기타'],
        '조회수': [2567, 1000, 150, 110] # PDF 이미지 기반 추정치
    }
    df_top1_traffic = pd.DataFrame(data_top1_traffic)

    fig_article_traffic = px.bar(df_top1_traffic, x='조회수', y='경로', orientation='h',
                                 color='경로', color_discrete_sequence=px.colors.qualitative.T10)
    fig_article_traffic.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_article_traffic, use_container_width=True)


with tab3:
    st.header("3. 시간대 및 카테고리별 분석")

    st.subheader("카테고리별 기사 수 및 조회수")
    # 카테고리별 분석 (PDF 3페이지 표 참고)
    data_category = {
        '카테고리': ['Cook&Chef', 'Food&Life', '푸드이슈', '기타', '맛있는 한식', '음식비평', '영상과 사진', '쿡앤셰프'],
        '기사 수': [656, 107, 92, 26, 21, 11, 3, 2],
        '조회수': [58808, 26985, 22903, 693, 5980, 501, 143, 283]
    }
    df_category = pd.DataFrame(data_category)

    col_cat_1, col_cat_2 = st.columns(2)
    with col_cat_1:
        st.write("**카테고리별 기사 수**")
        fig_cat_count = px.pie(df_category, values='기사 수', names='카테고리')
        st.plotly_chart(fig_cat_count, use_container_width=True)
    with col_cat_2:
        st.write("**카테고리별 조회수**")
        fig_cat_views = px.bar(df_category.sort_values(by='조회수', ascending=False), x='카테고리', y='조회수')
        st.plotly_chart(fig_cat_views, use_container_width=True)

with tab4:
    st.header("4. 기타 독자 특성 분석")

    col_demo_1, col_demo_2, col_demo_3, col_demo_4 = st.columns(4)

    # 4-1. 시/군/구 (PDF 4페이지 좌상단 파이차트)
    data_location = {'지역': ['Seoul', 'Busan', 'Incheon', '(not set)', '기타'], '비율': [48.8, 6.7, 5, 19.3, 20.2]} # 일부 값은 추정치
    df_location = pd.DataFrame(data_location)
    with col_demo_1:
        st.subheader("시/군/구")
        fig_loc = px.pie(df_location, values='비율', names='지역', height=300)
        st.plotly_chart(fig_loc, use_container_width=True)

    # 4-2. 연령 (PDF 4페이지 중단 좌측 파이차트)
    data_age = {'연령대': ['unknown', '45-54', '55-64', '35-44', '25-34', '18-24', '65+'],
                '수': [4592, 1423, 949, 523, 475, 150, 100]} # 18-24, 65+는 추정치
    df_age = pd.DataFrame(data_age)
    with col_demo_2:
        st.subheader("연령")
        fig_age = px.pie(df_age, values='수', names='연령대', height=300)
        st.plotly_chart(fig_age, use_container_width=True)

    # 4-3. 플랫폼/기기 카테고리 (PDF 4페이지 중단 우측 파이차트)
    data_platform = {'플랫폼': ['web / mobile', 'web / desktop', 'web / tablet'],
                     '수': [7140, 3071, 300]} # tablet은 추정치
    df_platform = pd.DataFrame(data_platform)
    with col_demo_3:
        st.subheader("플랫폼/기기")
        fig_platform = px.pie(df_platform, values='수', names='플랫폼', height=300)
        st.plotly_chart(fig_platform, use_container_width=True)

    # 4-4. 성별 (PDF 4페이지 우하단 파이차트)
    data_gender = {'성별': ['unknown', 'female', 'male'], '비율': [53.2, 28.0, 18.8]}
    df_gender = pd.DataFrame(data_gender)
    with col_demo_4:
        st.subheader("성별")
        fig_gender = px.pie(df_gender, values='비율', names='성별', height=300)
        st.plotly_chart(fig_gender, use_container_width=True)

st.sidebar.info("본 대시보드는 제공된 PDF 예시를 기반으로 Streamlit과 Plotly를 사용하여 구성되었습니다. 데이터 값은 이미지에 표시된 수치를 기반으로 수동 입력되었습니다.")

# 실행 방법: 터미널에서 'streamlit run [파일명.py]' 입력