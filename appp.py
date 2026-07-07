import streamlit as st
import pandas as pd

# --- [데이터 정의] ---
# 1. 다빈도 직종 목록 (제공해주신 이미지 기반)
frequent_jobs = [
    "내장공", "내장목공", "인테리어공", "미장공", "조적공", "형틀목공", "비계공", "철근공", "배관공", "용접공",
    "가시설공", "타일공", "도장공", "견출공", "건축석공", "석공", "전기공", "철골공", "터널공", "플랜트배관",
    "플랜트용접", "시스템비계", "메지공", "플랜트보온", "방수공", "보통인부", "경량철골공", "활석공", "환경미화원",
    "요양보호사", "건물청소원", "급식조리원", "보육교사", "중량물배달", "섬유직조공", "자동차정비", "외선전공",
    "채탄원", "굴진원", "보갱원", "벌목공", "객실청소원", "점검원", "이사작업원", "조선용접공", "조선도장공",
    "조선취부공", "조선사상공", "조선비계공", "항만하역원", "전자제품조립", "택배원", "자동차도장"
]

# 2. 추정의 원칙 상세 데이터 (제공해주신 이미지 테이블 기반)
presumption_rules = [
    {"부위": "목", "상병명": "경추간판탈출증", "직종명": ["용접공", "배관공", "형틀목공"], "근무기간": 10, "유효기간": 12},
    {"부위": "어깨", "상병명": "회전근개파열", "직종명": ["용접공", "배관공", "형틀목공"], "근무기간": 10, "유효기간": 12},
    {"부위": "팔꿈치", "상병명": "내(외)상과염", "직종명": ["용접공", "형틀목공", "철근공", "조리원", "급식조리원", "건물청소원"], "근무기간": 1, "유효기간": 2},
    {"부위": "손/손목", "상병명": "수근관증후군", "직종명": ["용접공", "형틀목공", "석공", "미장공", "조리원", "급식조리원", "객실청소원"], "근무기간": 2, "유효기간": 6},
    {"부위": "손/손목", "상병명": "삼각섬유연골복합체파열", "직종명": ["자동차조립공", "의장조립공", "급식조리원", "검사원"], "근무기간": 5, "유효기간": 12},
    {"부위": "손/손목", "상병명": "드퀘르벵", "직종명": ["자동차조립공", "의장조립공", "조리원", "제빵원"], "근무기간": 1, "유효기간": 2},
    {"부위": "허리", "상병명": "요추간판탈출증", "직종명": ["용접공", "배관공", "형틀목공", "석공", "전기공", "철골공", "조선용접공", "택배원"], "근무기간": 10, "유효기간": 12},
    {"부위": "무릎", "상병명": "반월상연골파열", "직종명": ["용접공", "배관공", "형틀목공", "석공", "전기공", "철근공", "미장공", "비계공"], "근무기간": 5, "유효기간": 12},
]

# --- [UI 설정] ---
st.set_page_config(page_title="산재 프로세스 가이드", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    .path-box { padding: 20px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; min-height: 80px; display: flex; align-items: center; justify-content: center; }
    .active { background-color: #007bff; color: white; border: 3px solid #004a99; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    .inactive { background-color: #ffffff; color: #adb5bd; border: 1px solid #dee2e6; }
    .result-success { background-color: #28a745; color: white; }
    .result-fail { background-color: #dc3545; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ 산재 최초승인 의사결정 시뮬레이터")

# --- [입력 섹션] ---
with st.sidebar:
    st.header("🔍 정보 입력")
    job_input = st.selectbox("1. 직종 선택", ["직접 검색/입력"] + sorted(frequent_jobs))
    if job_input == "직접 검색/입력":
        job_input = st.text_input("직종명을 입력하세요 (예: 용접공)")
    
    disease_input = st.selectbox("2. 상병명 선택", [r["상병명"] for r in presumption_rules])
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        work_years = st.number_input("3. 근무기간(년)", min_value=0, step=1, value=5)
    with col_in2:
        valid_months = st.number_input("4. 유효기간(개월)", min_value=0, step=1, value=6)

# --- [로직 판단] ---
# 1. 다빈도 직종 여부
is_frequent = job_input in frequent_jobs

# 2. 추정의 원칙 충족 여부
met_rule = None
is_presumption_met = False
for rule in presumption_rules:
    if rule["상병명"] == disease_input:
        # 상병에 해당하는 직종 리스트에 포함되는지 확인 (부분 일치 포함)
        job_match = any(job_input in target_job for target_job in rule["직종명"])
        if job_match and work_years >= rule["근무기간"] and valid_months <= rule["유효기간"]:
            is_presumption_met = True
            met_rule = rule
            break

# 다빈도가 아닐 경우 업무관련성 수동 선택 (도식 구현용)
relevance_level = "낮음"
if not is_frequent:
    relevance_level = st.radio("다빈도 미해당 시: 특별진찰 결과 업무관련성", ["높음", "낮음"], horizontal=True)

# --- [도식화 및 경로 표현] ---
st.subheader("📊 프로세스 경로 추적")

# 경로 상태 정의
s1 = True # 시작
s2_yes = is_frequent
s2_no = not is_frequent
s3_presump = s2_yes # 다빈도면 추정원칙 단계
s3_special = s2_no # 아니면 특별진찰 단계
s4_success = (s2_yes and is_presumption_met) or (s2_no and relevance_level == "높음")
s4_fail = (s2_yes and not is_presumption_met) or (s2_no and relevance_level == "낮음")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f'<div class="path-box active">직력등 기초조사</div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="path-box {"active" if s2_yes else "inactive"}">다빈도 직종 (YES)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="path-box {"active" if s2_no else "inactive"}">다빈도 미해당 (NO)</div>', unsafe_allow_html=True)

with c3:
    if s2_yes:
        st.markdown(f'<div class="path-box active" style="margin-top:20px;">업무관련성<br>특별진찰 생략</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="path-box active">추정의 원칙 여부</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="path-box active" style="margin-top:20px;">업무관련성<br>특별진찰 진행</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="path-box active">업무관련성 {relevance_level}</div>', unsafe_allow_html=True)

with c4:
    st.markdown(f'<div class="path-box {"active result-success" if s4_success else "inactive"}">충족 (승인권고)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="path-box {"active result-fail" if s4_fail else "inactive"}">미충족 (심의의뢰)</div>', unsafe_allow_html=True)

with c5:
    if s4_success:
        st.markdown(f'<div class="path-box active result-success" style="height: 170px;">소속기관<br>직접 승인</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="path-box active result-fail" style="height: 170px;">질병판정위원회 심의<br>의학자문 및 판정</div>', unsafe_allow_html=True)

# --- [결과 및 데이터 리스트] ---
st.divider()
st.subheader("📋 상세 진단 결과 및 원천 데이터")

res_col1, res_col2 = st.columns([1, 2])

with res_col1:
    st.info(f"**직종:** {job_input}\n\n**상병:** {disease_input}")
    if is_presumption_met:
        st.success("✅ 추정의 원칙 모든 조건 충족")
    elif is_frequent:
        st.warning("❌ 다빈도 직종이나 추정의 원칙 조건(기간 등) 미달")
    else:
        st.error("ℹ️ 다빈도 직종에 해당하지 않음")

with res_col2:
    if is_frequent and met_rule:
        st.write("### 매칭된 추정의 원칙 기준 (원천 데이터)")
        match_df = pd.DataFrame([met_rule])
        match_df['직종명'] = match_df['직종명'].apply(lambda x: ", ".join(x[:5]) + "...")
        st.table(match_df)
    elif is_frequent:
        st.write("### 선택하신 상병의 표준 기준")
        std_rule = [r for r in presumption_rules if r["상병명"] == disease_input]
        st.table(pd.DataFrame(std_rule))
    else:
        st.write("다빈도 직종 목록에 없습니다. 상단의 '다빈도 직종 목록 보기'를 확인하세요.")

with st.expander("📌 전체 다빈도 직종 목록 확인 (50+ 개)"):
    st.write(", ".join(frequent_jobs))
