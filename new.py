import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="질병판정서 스마트 검색기")

@st.cache_data
def load_data():
    try:
        # Parquet 파일 불러오기
        df = pd.read_parquet('disease_data.parquet')
        
        # 컬럼 매핑
        mapping = {
            'accnum': '판정번호', 'kinda': '승인여부', 'kindb': '세부직종', 
            'kindc': '질병명', 'title': '대분류직종', 'noncontent': '주요내용'
        }
        df = df.rename(columns=mapping)
        cols = ['승인여부', '대분류직종', '세부직종', '질병명', '주요내용', '판정번호']
        available_cols = [c for c in cols if c in df.columns]
        return df[available_cols]
    except Exception as e:
        st.error(f"데이터 파일 로드 실패: {e}")
        return None

# 1. 데이터 로드
st.title("🔍 업무상 질병 판정서 검색기")
df = load_data()

if df is not None:
    # 2. 검색 및 필터 UI
    col1, col2, col3 = st.columns(3)
    with col1: status_filter = st.multiselect("승인 여부 선택", df['승인여부'].unique())
    with col2: title_filter = st.multiselect("대분류 직종 선택", df['대분류직종'].unique())
    with col3: keyword = st.text_input("💬 키워드 검색", placeholder="예: 요통, 소음, 용접")

    # 3. 필터링 로직
    filtered_df = df.copy()
    if status_filter: 
        filtered_df = filtered_df[filtered_df['승인여부'].isin(status_filter)]
    if title_filter: 
        filtered_df = filtered_df[filtered_df['대분류직종'].isin(title_filter)]
    if keyword:
        mask = filtered_df.apply(lambda row: row.astype(str).str.contains(keyword, case=False).any(), axis=1)
        filtered_df = filtered_df[mask]

    # 4. 결과 출력
    st.write(f"### 📊 검색 결과: 총 {len(filtered_df)}건")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("데이터가 로드되지 않았습니다. 'disease_data.parquet' 파일이 같은 폴더에 있는지 확인해주세요.")
