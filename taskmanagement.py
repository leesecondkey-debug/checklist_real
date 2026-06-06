import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="근로복지공단 관할 및 담당자 통합 검색기", layout="wide")

st.title("근로복지공단 관할 및 전 지사 담당자 검색기")
st.caption("노무법인 산재 수원지사")

# --- 1. 데이터 파싱 및 부서별 팩스 매핑 엔진 ---
@st.cache_data
def load_kcomwel_data():
    raw_records = []
    current_branch = "미확인 지사"
    
    # [1단계] 파일 읽기 및 날것의 텍스트 파싱
    try:
        with open("근복단.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            # 지사명 추적 알고리즘
            if "지사의 정보를 제공" in line_str:
                extracted = line_str.split("지사의")[0].strip()
                if extracted:
                    current_branch = extracted + "지사"
                    continue
            elif "지사명" in line_str:
                parts = re.split(r'\t|\s{2,}', line_str)
                if len(parts) >= 2:
                    current_branch = parts[1].strip()
                    continue
            
            # 데이터 라인 조각내기
            cols = [c.strip() for c in re.split(r'\t|\s{2,}', line_str) if c.strip()]
            
            if len(cols) >= 2:
                has_dept = any(dept in cols[0] for dept in ["부서", "부", "팀", "센터", "지원"])
                has_phone = any(p_head in cols[1] or p_head in cols[0] for p_head in ["033-", "02-", "031-", "0505-", "055-", "042-"])
                
                if has_dept or has_phone:
                    dept_name = cols[0]
                    phone_val = cols[1] if len(cols) > 1 else ""
                    biz_desc = " / ".join(cols[2:]) if len(cols) > 2 else "상세 내용 없음"
                    
                    if "팩스번호" in phone_val or "전화번호" in phone_val or "업무" in dept_name:
                        continue
                    
                    phone_num = ""
                    fax_num = ""
                    if "0505" in phone_val:
                        fax_num = phone_val
                    else:
                        phone_num = phone_val
                        
                    raw_records.append({
                        "관할지사": current_branch,
                        "담당부서": dept_name,
                        "📞 직통 전화번호": phone_num,
                        "📠 직통 팩스번호": fax_num,
                        "📋 담당 업무 및 세부 관할 내역": biz_desc
                    })
    except FileNotFoundError:
        st.error("⚠️ '근복단.txt' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ 파일 파싱 중 오류 발생: {e}")
        return pd.DataFrame()

    if not raw_records:
        return pd.DataFrame()
        
    df = pd.DataFrame(raw_records)
    fax_map = {}
    
    for idx, row in df.iterrows():
        key = (row["관할지사"], row["담당부서"])
        if row["📠 직통 팩스번호"]:
            if key not in fax_map:
                fax_map[key] = set()
            fax_map[key].add(row["📠 직통 팩스번호"])
    
    grouped_faxes = []
    for idx, row in df.iterrows():
        key = (row["관할지사"], row["담당부서"])
        fax_list_str = ", ".join(sorted(list(fax_map[key]))) if key in fax_map and fax_map[key] else "-"
        grouped_faxes.append(fax_list_str)
        
    df["📁 부서 내 모든 팩스 목록"] = grouped_faxes
    return df

# 데이터 로드 실행
df_db = load_kcomwel_data()

if not df_db.empty:
    st.markdown("### 🔍 검색창")
    search_query = st.text_input("검색어 입력창", placeholder="예시: '용인 휴업', '수원 최초' 등...", label_visibility="collapsed")
    st.markdown("---")
    
    if search_query:
        keywords = [kw.strip() for kw in search_query.split() if kw.strip()]
        filtered_df = df_db.copy()
        
        for kw in keywords:
            filtered_df = filtered_df[
                filtered_df['관할지사'].str.contains(kw, case=False, na=False) |
                filtered_df['담당부서'].str.contains(kw, case=False, na=False) |
                filtered_df['📞 직통 전화번호'].str.contains(kw, case=False, na=False) |
                filtered_df['📠 직통 팩스번호'].str.contains(kw, case=False, na=False) |
                filtered_df['📁 부서 내 모든 팩스 목록'].str.contains(kw, case=False, na=False) |
                filtered_df['📋 담당 업무 및 세부 관할 내역'].str.contains(kw, case=False, na=False)
            ]
        
        if len(filtered_df) > 0:
            st.success(f"🎯 **{len(filtered_df)}건**을 찾았습니다.")
            st.dataframe(filtered_df[["관할지사", "담당부서", "📞 직통 전화번호", "📁 부서 내 모든 팩스 목록", "📋 담당 업무 및 세부 관할 내역"]], use_container_width=True)
            
            st.markdown("### 📱 상세 보기")
            for idx, row in filtered_df.iterrows():
                with st.expander(f"📍 [{row['관할지사']}] {row['담당부서']} (전화: {row['📞 직통 전화번호']})"):
                    st.write(f"**직통 전화:** {row['📞 직통 전화번호']}")
                    st.write(f"**직통 팩스:** {row['📠 직통 팩스번호']}")
                    st.write(f"**부서 팩스 채널:** {row['📁 부서 내 모든 팩스 목록']}")
                    st.write(f"**담당 업무:** {row['📋 담당 업무 및 세부 관할 내역']}")
        else:
            st.warning("❌ 일치하는 항목이 없습니다.")
            
    else:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("#### 🏢 지사별 데이터 수")
            branch_counts = df_db['관할지사'].value_counts().reset_index()
            branch_counts.columns = ['관할지사', '등록 건수']
            st.dataframe(branch_counts, use_container_width=True)
        with col2:
            st.info("💡 검색창을 사용하여 공단 담당자를 찾아보세요.")
