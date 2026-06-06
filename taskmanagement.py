import streamlit as st
import pandas as pd
import re

# 1. 페이지 설정 및 디자인 (불필요한 여백/메뉴 제거)
st.set_page_config(page_title="근로복지공단 담당자 검색기", layout="wide")

# CSS 주입: Streamlit 메뉴, 푸터 제거 및 폰트 깔끔하게 정리
st.markdown("""
    <style>
    /* 상단 메뉴와 하단 푸터(Made with Streamlit) 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 전체 배경색 및 폰트 설정 */
    .main {
        background-color: #f8fafc;
    }
    
    /* 검색창 디자인 깔끔하게 */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 10px 15px;
    }

    /* 표(Table) 여백 조정 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 정제 엔진 (렉 방지 및 불필요 문구 자동 제거)
@st.cache_data
def load_kcomwel_data():
    raw_records = []
    current_branch = "미확인 지사"
    
    # 제거하고 싶은 지저분한 문구들
    unwanted = ["팩스수신여부확인", "새창으로 보기", "확인", "바로가기", "보기"]
    
    try:
        with open("근복단.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            line_str = line.strip()
            if not line_str: continue
            
            # 지사명 인식
            if "지사의 정보를 제공" in line_str:
                current_branch = line_str.split("지사의")[0].strip() + "지사"
                continue
            
            # 탭/공백으로 데이터 분리
            cols = [c.strip() for c in re.split(r'\t|\s{2,}', line_str) if c.strip()]
            
            if len(cols) >= 2:
                dept_name = cols[0]
                phone_val = cols[1] if len(cols) > 1 else ""
                biz_desc = " / ".join(cols[2:]) if len(cols) > 2 else ""

                # [디자인 개선] 불필요한 짜잘한 문구들 삭제
                for word in unwanted:
                    dept_name = dept_name.replace(word, "")
                    biz_desc = biz_desc.replace(word, "")
                
                dept_name = dept_name.strip()
                biz_desc = biz_desc.strip()

                # 유효한 담당자 데이터만 수집
                if any(k in dept_name for k in ["부서", "부", "팀", "센터", "지원"]) or "0" in phone_val:
                    if "팩스번호" in phone_val or "전화번호" in phone_val: continue
                    
                    phone_num = phone_val if "0505" not in phone_val else ""
                    fax_num = phone_val if "0505" in phone_val else ""
                        
                    raw_records.append({
                        "관할지사": current_branch,
                        "담당부서": dept_name,
                        "📞 직통전화": phone_num,
                        "📠 직통팩스": fax_num,
                        "📋 담당업무/관할": biz_desc if biz_desc else "상세 내용 없음"
                    })
    except Exception as e:
        return pd.DataFrame()

    df = pd.DataFrame(raw_records)
    
    # 부서별 팩스 번호 자동 매핑
    fax_map = df.groupby(["관할지사", "담당부서"])["📠 직통팩스"].apply(lambda x: set(x) - {""}).to_dict()
    df["📁 부서전체팩스"] = df.apply(lambda row: ", ".join(sorted(list(fax_map.get((row["관할지사"], row["담당부서"]), {"-"})))) if fax_map.get((row["관할지사"], row["담당부서"])) else "-", axis=1)
    
    return df

# 실행
df_db = load_kcomwel_data()

# 3. 메인 화면 UI
st.title("📂 공단 담당자 통합 검색기")
st.caption("노무법인 산재 수원지사 전용")

if not df_db.empty:
    # 검색바 (깔끔하게 상단에 하나만 배치)
    search_query = st.text_input("", placeholder="지사명, 동 이름, 업무(휴업, 장해) 등을 입력하세요.")
    
    if search_query:
        # 검색 로직 (조합 검색)
        keywords = search_query.split()
        filtered_df = df_db.copy()
        for kw in keywords:
            filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(kw, case=False).any(), axis=1)]
        
        if not filtered_df.empty:
            st.success(f"총 {len(filtered_df)}건의 담당자를 찾았습니다.")
            # 표 출력
            st.dataframe(filtered_df[["관할지사", "담당부서", "📞 직통전화", "📁 부서전체팩스", "📋 담당업무/관할"]], use_container_width=True, height=500)
        else:
            st.warning("일치하는 담당자가 없습니다.")
    else:
        # 검색 전 초기 화면: 깔끔하게 통계만 표시
        st.info("💡 검색어를 입력하면 즉시 담당자를 찾습니다. (예: 수원 휴업, 용인 장해)")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("### 🏢 지사별 등록 현황")
            st.dataframe(df_db['관할지사'].value_counts().reset_index(), use_container_width=True)
        with col2:
            st.write("### ℹ️ 안내")
            st.write("1. 띄어쓰기로 여러 단어 검색이 가능합니다.")
            st.write("2. 0505 팩스 번호는 자동으로 부서별로 묶여서 표시됩니다.")

else:
    st.error("데이터를 불러올 수 없습니다. '근복단.txt' 파일을 확인해주세요.")
