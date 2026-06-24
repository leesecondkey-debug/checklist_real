import streamlit as st
import pandas as pd

st.set_page_config(page_title="근로복지공단 정보 검색기", layout="wide")
st.title("🔍 근로복지공단 정보 검색기")

@st.cache_data
def load_and_merge_data():
    all_sheets = pd.read_excel('list.xlsx', sheet_name=None, dtype=str)
    df_list = []
    for sheet_name, df in all_sheets.items():
        df.columns = [str(col).strip() for col in df.columns]
        if '지사' in df.columns:
            df['지사'] = df['지사'].astype(str).str.strip()
        else:
            df['지사'] = str(sheet_name).strip()
        df_list.append(df)
    
    return pd.concat(df_list, ignore_index=True).fillna('').astype(str)

try:
    combined_df = load_and_merge_data()
    search_keyword = st.text_input("검색어를 입력하세요 (예: 수원 가입, 가입 수원, 재활 수원 등):")

    if search_keyword:
        keywords = search_keyword.split()
        
        # 1. 모든 검색어가 행 어딘가에 포함된 데이터 찾기 (검색 순서 무관)
        def is_match(row):
            row_str = " ".join(row.values).lower()
            return all(k.lower() in row_str for k in keywords)

        mask = combined_df.apply(is_match, axis=1)
        all_matches = combined_df[mask]
        
        if not all_matches.empty:
            # 2. 결과 내에서 '지사' 열에 검색어 중 하나라도 포함된 것을 우선순위로 분리
            def has_keyword_in_jisa(row):
                return any(k.lower() in row['지사'].lower() for k in keywords)

            is_jisa_match = all_matches.apply(has_keyword_in_jisa, axis=1)
            
            jisa_priority_df = all_matches[is_jisa_match]
            others_df = all_matches[~is_jisa_match]
            
            # 3. 우선순위 데이터와 나머지 데이터를 합쳐서 출력
            final_result = pd.concat([jisa_priority_df, others_df], ignore_index=True)
            
            st.success(f"총 {len(final_result)}건의 결과를 찾았습니다.")
            st.dataframe(final_result, use_container_width=True)
        else:
            st.warning("조건에 맞는 결과가 없습니다.")
            
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
