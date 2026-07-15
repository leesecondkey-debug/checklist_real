import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="업무상질병 검색기")

# 슬래시(/)를 사용하여 경로 문제 원천 차단
FILE_PATH = "C:/Users/노무법인 산재 이재섭/Desktop/code/tool/718mbdata.csv"

@st.cache_data
def load_data():
    if not os.path.exists(FILE_PATH):
        st.error(f"파일을 찾을 수 없습니다. 경로를 확인하세요: {FILE_PATH}")
        st.stop()
    
    # 데이터 로드
    return pd.read_csv(FILE_PATH, encoding='utf-8-sig', engine='python', on_bad_lines='skip')

# 데이터 로드 실행
try:
    with st.spinner('데이터를 불러오는 중입니다...'):
        df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 앱 화면 구성
st.title("업무상질병 판정서 검색기")

def get_unique_list(column_name):
    if column_name in df.columns:
        return ["전체"] + sorted(df[column_name].dropna().unique().tolist())
    return ["전체"]

job_list = get_unique_list('Occupation')
disease_list = get_unique_list('Disease Name')
status_list = get_unique_list('Approval Status')

col1, col2, col3 = st.columns(3)
with col1: selected_job = st.selectbox("직종 선택:", job_list)
with col2: selected_disease = st.selectbox("질병 선택:", disease_list)
with col3: selected_status = st.selectbox("승인 상태 선택:", status_list)

filtered_df = df.copy()
if selected_job != "전체": filtered_df = filtered_df[filtered_df['Occupation'] == selected_job]
if selected_disease != "전체": filtered_df = filtered_df[filtered_df['Disease Name'] == selected_disease]
if selected_status != "전체": filtered_df = filtered_df[filtered_df['Approval Status'] == selected_status]

st.write(f"### 📊 검색 결과: 총 {len(filtered_df)}건")
st.dataframe(filtered_df, use_container_width=True)

if len(filtered_df) > 0 and 'Occupation' in filtered_df.columns:
    st.write("---")
    st.subheader("선택한 조건의 직종별 통계")
    st.bar_chart(filtered_df['Occupation'].value_counts())
