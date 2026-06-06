import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="산재보험 관할 및 담당자 통합 검색기", layout="wide")

st.title("🎯 근로복지공단 전 지사 담당자 실시간 검색기")
st.caption("업로드된 '근복단.txt' 데이터베이스를 기반으로 작동하는 산재보상직원 전용 업무 툴입니다.")

# --- 1. 근복단.txt 원본 데이터 실시간 파싱 함수 ---
@st.cache_data
def load_kcomwel_data():
    raw_records = []
    current_branch = "미확인 지사"
    
    try:
        with open("근복단.txt", "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                
                # '지사명\t영월지사' 또는 '지사명\t서울지역본부' 형태에서 지사명 추출
                if "지사명" in line_str and "\t" in line_str:
                    parts = line_str.split("\t")
                    if len(parts) >= 2:
                        current_branch = parts[1].strip()
                        continue
                
                # 부서 데이터 라인 파싱 (부서 / 내선번호 / 담당업무 / 세부내역 순)
                # 탭(\t)으로 구분된 실제 공단 인적 자원 레이아웃 분석 반영
                if "\t" in line_str:
                    cols = line_str.split("\t")
                    # 유효한 연락처/업무 라인 형태 필터링
                    if len(cols) >= 3 and any(dept in cols[0] for dept in ["재활보상", "경영복지", "가입지원", "진폐보상"]):
                        dept_name = cols[0].strip()
                        
                        # 연락처와 업무 텍스트 매핑
                        phone_or_fax = cols[1].strip()
                        biz_type = cols[2].strip()
                        detail_desc = cols[3].strip() if len(cols) > 3 else ""
                        
                        raw_records.append({
                            "관할지사": current_branch,
                            "담당부서": dept_name,
                            "연락처/팩스": phone_or_fax,
                            "담당업무": biz_type,
                            "세부 담당 구역 및 의료기관 기준": detail_desc
                        })
    except FileNotFoundError:
        st.error("⚠️ '근복단.txt' 파일을 찾을 수 없습니다. 바탕화면(Desktop)에 해당 파일이 함께 있는지 확인해 주세요.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 로딩 중 오류 발생: {e}")
        return pd.DataFrame()
        
    return pd.DataFrame(raw_records)

# 데이터 로드
df_db = load_kcomwel_data()

if not df_db.empty:
    # ----------------- 메인 기능: 키보드 통합 검색창 -----------------
    st.markdown("### 🔍 키보드로 관할 지역, 구, 또는 급여 종류를 입력하세요")
    
    # 노무사님이 마우스 클릭 없이 바로 타이핑할 수 있는 검색창
    search_query = st.text_input(
        "검색어 입력 예시: '수원시', '구로구', '휴업급여', '장해', '재요양', '팔달구'", 
        placeholder="여기에 검색어를 타이핑하고 엔터를 누르세요..."
    )
    
    st.markdown("---")
    
    if search_query:
        # 키보드로 입력한 검색어가 관할지사, 부서명, 담당업무, 세부구역 내용 중 하나라도 포함되어 있으면 실시간 필터링
        filtered_df = df_db[
            df_db['관할지사'].str.contains(search_query, case=False, na=False) |
            df_df['담당부서'].str.contains(search_query, case=False, na=False) |
            df_db['담당업무'].str.contains(search_query, case=False, na=False) |
            df_db['세부 담당 구역 및 의료기관 기준'].str.contains(search_query, case=False, na=False)
        ]
        
        total_count = len(filtered_df)
        
        if total_count > 0:
            st.success(f"🎯 '{search_query}'(으)로 총 {total_count}건의 공단 담당 분정 내역이 검색되었습니다.")
            
            # 검색 결과를 가독성 좋은 데이터프레임 표로 전면 배치
            st.dataframe(
                filtered_df, 
                use_container_width=True,
                column_config={
                    "연락처/팩스": st.column_config.TextColumn("📞 직통번호 / 📠 팩스"),
                    "세부 담당 구역 및 의료기관 기준": st.column_config.TextColumn("📋 상세 분장 (구역/의료기관/이름순)")
                }
            )
            
            # 선택적 상세 뷰어 기능 추가
            st.markdown("### 🔍 한눈에 상세 보기 (선택 목록)")
            for idx, row in filtered_df.iterrows():
                with st.expander(f"📍 [{row['관할지사']}] {row['담당부서']} - {row['담당업무']}"):
                    st.markdown(f"**📞 연락처/팩스:** {row['연락처/팩스']}")
                    st.markdown(f"**📋 상세 분정 구조:** {row['세부 담당 구역 및 의료기관 기준']}")
        else:
            st.warning(f"❌ 데이터베이스에서 '{search_query}'에 매칭되는 담당 업무를 찾지 못했습니다. 단어를 다시 확인해 주세요.")
            
    else:
        # 아무것도 입력하지 않았을 때는 전체 데이터베이스의 규모를 브리핑하고 샘플 출력
        st.info("💡 위 검색창에 단어를 입력하시면 즉시 관할 지사 및 담당 파트가 필터링됩니다.")
        
        st.markdown("#### 📊 현재 로드된 공단 지사별 데이터셋 전체 요약")
        summary_df = df_db['관할지사'].value_counts().reset_index()
        summary_df.columns = ['관할지사', '등록된 담당 분장 수']
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(summary_df, use_container_width=True)
        with col2:
            st.write("▼ 전체 데이터베이스 샘플 (일부)")
            st.dataframe(df_db.head(15), use_container_width=True)
else:
    st.info("데이터베이스가 비어있거나 '근복단.txt' 형식을 읽는 중입니다.")
