import streamlit as st
from datetime import datetime

st.title("📋 업무 체크리스트 ")

# 세션 상태(메모리)에 할 일 목록 초기화 (할 일 내용과 추가된 시간을 딕셔너리로 저장)
if "todo_list" not in st.session_state:
    now = datetime.now()
    st.session_state.todo_list = [
        {"task": "뭐가 있지..", "created_at": now}
    ]

# 새로운 할 일 추가 입력을 행으로 구성
col1, col2 = st.columns([4, 1])
with col1:
    new_task = st.text_input("새로운 할 일을 입력하세요", label_visibility="collapsed")
with col2:
    if st.button("추가") and new_task:
        # 추가 버튼을 누른 '현재 시간'을 함께 기록합니다.
        st.session_state.todo_list.append({
            "task": new_task, 
            "created_at": datetime.now()
        })
        st.rerun()

# ⏰ 상단에 실시간 시간 갱신을 위한 새로고침 버튼 제공
st.write("---")
col_refresh, _ = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 시간 업데이트"):
        st.rerun()

# 체크리스트 출력
for i, item in enumerate(st.session_state.todo_list):
    task = item["task"]
    created_at = item["created_at"]
    
    # 현재 시간과 생성 시간의 차이(경과 시간) 계산
    elapsed = datetime.now() - created_at
    total_seconds = int(elapsed.total_seconds())
    
    # 보기 좋게 분/초로 환산
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    # 시간 표시 텍스트 구성 (예: 5분 23초 경과)
    if minutes > 0:
        time_str = f"⏳ {minutes}분 {seconds}초째 진행 중..."
    else:
        time_str = f"⏳ {seconds}초째 진행 중..."
        
    # 화면 레이아웃 분할 (체크박스 영역 / 시간 표시 영역)
    task_col, time_col = st.columns([3, 2])
    
    with task_col:
        is_checked = st.checkbox(task, key=f"task_{i}")
        
    with time_col:
        if not is_checked:
            # 아직 미완료 상태일 때는 경과 시간을 주황색(warning) 메시지나 텍스트로 표시
            st.caption(f"{time_str} *(시작 {created_at.strftime('%H:%M:%S')})*")
        else:
            # 완료 체크를 하면 경과 시간 대신 완료 표시
            st.success("✅ 완료됨!")
            
    if is_checked:
        st.write(f"~~{task}~~ (완료!)")
    
    st.write("") # 항목 간 간격 띄우기
