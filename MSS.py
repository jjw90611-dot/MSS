import streamlit as st
import sqlite3
import datetime
import random
import requests

# ==========================================
# [초기 설정] 페이지 세팅
# ==========================================
st.set_page_config(page_title="기계안전기술사 AI 학습 센터", page_icon="⚙️", layout="centered")

# ==========================================
# [Groq API 키 설정] (기출문제 첨삭 및 출제용)
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ 스트림릿 설정(Settings) -> Secrets에 'GROQ_API_KEY'를 먼저 입력해주세요!")
    st.stop()

# ==========================================
# [데이터베이스 설정] SQLite3 (학습 기록용)
# ==========================================
conn = sqlite3.connect('mech_safety_study.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS study_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, question TEXT, user_answer TEXT, ai_feedback TEXT)''')
conn.commit()

# ==========================================
# [기출문제 데이터베이스] (제공된 서브노트 기반 기계안전기술사 기출)
# ==========================================
QUESTIONS = [
    "기계나 구조물의 피로한도에 영향을 주는 요인 5가지와 피로한도 향상 방안을 설명하시오.",
    "위험성평가의 절차 5단계를 쓰고, 정량적 위험성평가 기법 중 FTA와 ETA에 대해 설명하시오.",
    "본질안전화의 3원칙과 Fail Safe의 기능면 3단계를 설명하시오.",
    "지게차의 위험성과 하역작업 및 주행 시 안정도 기준에 대하여 설명하시오.",
    "비파괴검사 중 자분탐상시험(MT)과 침투탐상시험(PT)의 원리와 장단점을 비교 설명하시오.",
    "보일러 가동 시 발생하는 캐리오버(Carry Over)의 원인과 방지대책을 설명하시오.",
    "프레스의 양수조작식 방호장치 구비조건과 광전자식 방호장치의 안전거리 계산식을 쓰시오.",
    "크레인의 과부하방지장치와 권과방지장치의 종류 및 특징에 대하여 설명하시오.",
    "산업용 로봇의 교시 작업 시 안전작업 지침항목과 방호장치의 종류를 설명하시오.",
    "안전검사 대상 유해·위험 기계·기구 10가지를 쓰시오.",
    "공정안전보고서(PSM) 제출 대상 사업과 보고서에 포함되어야 할 4가지 주요 내용을 쓰시오.",
    "하인리히의 재해예방 4원칙과 사고예방대책 기본원리 5단계를 설명하시오.",
    "용접 잔류응력의 발생 메커니즘과 잔류응력 완화법 4가지를 설명하시오.",
    "압력용기의 안전설계 시 고려사항과 파열판 설치조건을 설명하시오.",
    "연삭숫돌의 파괴원인 5가지와 연삭기 덮개의 노출각도 기준을 설명하시오.",
    "컨베이어 작업 시 발생할 수 있는 위험성과 필수 안전장치 3가지를 설명하시오.",
    "고소작업대의 주요 구조부와 작업 시 넘어짐 방지 대책을 설명하시오.",
    "펌프 운전 시 발생하는 캐비테이션(Cavitation)의 원인과 펌프에 미치는 영향, 방지대책을 설명하시오.",
    "기계설비의 기능의 안전화 방법 중 소극적 대책과 적극적 대책을 설명하시오.",
    "설비보전의 종류 중 예방보전(TBM, CBM)과 사후보전에 대하여 설명하시오.",
    "응력집중계수의 정의와 응력집중 완화 대책 4가지를 쓰시오.",
    "승강기의 안전장치 중 조속기(Governor)와 비상정지장치의 작동 원리를 설명하시오.",
    "가스용접 시 발생하는 역류, 역화, 인화의 정의와 방지대책을 쓰시오.",
    "기계의 운동형태에 따른 위험점 6가지를 예를 들어 설명하시오.",
    "체결된 볼트·너트의 풀림 발생원인과 와셔 및 너트를 이용한 풀림방지방법을 설명하시오.",
    "제조물 책임법(PL법)상 제조물 결함의 3가지 분류(설계, 제조, 표시)에 대하여 설명하시오.",
    "동작경제의 3원칙(신체부위 사용, 작업장 배치, 공구 및 기계설비)에 대하여 설명하시오.",
    "밀폐공간 작업 시 유해공기 기준(산소, 탄산가스, 일산화탄소, 황화수소)과 작업 전 확인사항을 쓰시오.",
    "기계 고장률 추이를 나타내는 욕조곡선(Bath-tub curve)의 3가지 구간을 설명하시오.",
    "안전인증 심사의 종류 4가지(서면, 기술능력 및 생산체계, 제품, 확인심사)를 설명하시오."
]

# ==========================================
# [테마별 역대 기출문제 매핑 (AI 변형 출제용)]
# ==========================================
THEME_PAST_QUESTIONS = {
    "1. 기계안전 일반 및 위험성평가": [
        "기계나 구조물의 피로한도에 영향을 주는 요인 5가지와 피로한도 향상 방안을 설명하시오.",
        "위험성평가의 절차 5단계를 쓰고, 정량적 위험성평가 기법 중 FTA와 ETA에 대해 설명하시오.",
        "본질안전화의 3원칙과 Fail Safe의 기능면 3단계를 설명하시오.",
        "기계설비의 기능의 안전화 방법 중 소극적 대책과 적극적 대책을 설명하시오.",
        "응력집중계수의 정의와 응력집중 완화 대책 4가지를 쓰시오."
    ],
    "2. 양중기 및 운반기계": [
        "크레인의 과부하방지장치와 권과방지장치의 종류 및 특징에 대하여 설명하시오.",
        "지게차의 위험성과 하역작업 및 주행 시 안정도 기준에 대하여 설명하시오.",
        "컨베이어 작업 시 발생할 수 있는 위험성과 필수 안전장치 3가지를 설명하시오.",
        "고소작업대의 주요 구조부와 작업 시 넘어짐 방지 대책을 설명하시오.",
        "승강기의 안전장치 중 조속기(Governor)와 비상정지장치의 작동 원리를 설명하시오."
    ],
    "3. 압력용기 및 보일러": [
        "보일러 가동 시 발생하는 캐리오버(Carry Over)의 원인과 방지대책을 설명하시오.",
        "압력용기의 안전설계 시 고려사항과 파열판 설치조건을 설명하시오.",
        "펌프 운전 시 발생하는 캐비테이션(Cavitation)의 원인과 펌프에 미치는 영향, 방지대책을 설명하시오.",
        "펌프 배관에서 발생하는 수격작용(Water Hammering)의 원인과 방지대책을 쓰시오."
    ],
    "4. 용접 및 비파괴검사": [
        "비파괴검사 중 자분탐상시험(MT)과 침투탐상시험(PT)의 원리와 장단점을 비교 설명하시오.",
        "용접 잔류응력의 발생 메커니즘과 잔류응력 완화법 4가지를 설명하시오.",
        "가스용접 시 발생하는 역류, 역화, 인화의 정의와 방지대책을 쓰시오.",
        "아크용접 시 발생하는 흄(Fume) 가스에 의한 재해와 방호대책을 설명하시오."
    ],
    "5. 공작기계 및 산업용 로봇": [
        "프레스의 양수조작식 방호장치 구비조건과 광전자식 방호장치의 안전거리 계산식을 쓰시오.",
        "산업용 로봇의 교시 작업 시 안전작업 지침항목과 방호장치의 종류를 설명하시오.",
        "연삭숫돌의 파괴원인 5가지와 연삭기 덮개의 노출각도 기준을 설명하시오.",
        "기계의 운동형태에 따른 위험점 6가지를 예를 들어 설명하시오."
    ],
    "6. 안전보건법령 및 안전관리": [
        "안전검사 대상 유해·위험 기계·기구 10가지를 쓰시오.",
        "공정안전보고서(PSM) 제출 대상 사업과 보고서에 포함되어야 할 4가지 주요 내용을 쓰시오.",
        "하인리히의 재해예방 4원칙과 사고예방대책 기본원리 5단계를 설명하시오.",
        "설비보전의 종류 중 예방보전(TBM, CBM)과 사후보전에 대하여 설명하시오.",
        "제조물 책임법(PL법)상 제조물 결함의 3가지 분류(설계, 제조, 표시)에 대하여 설명하시오."
    ]
}

# ==========================================
# [응원 메시지 리스트]
# ==========================================
ENCOURAGEMENTS = [
    "기계공학 파트 정복이 합격의 Key입니다! 오늘도 화이팅! ⚙️",
    "기술사 공부는 시간을 아끼는 것이 핵심입니다. 효율적으로 달려봅시다! 🚀",
    "잘할 수 있습니다! 당신의 도전을 진심으로 응원합니다! ✨",
    "오늘 흘린 땀방울이 기계안전기술사 합격으로 돌아올 거예요. 아자쓰! 🔥",
    "조금만 더 힘내요! 합격증을 손에 쥐는 그날까지 화이팅! 🍀",
    "충분히 해낼 수 있습니다. 자신감을 가지세요! 🌟",
    "지치고 힘들 땐 잠시 쉬어가도 괜찮습니다. 이미 너무 잘하고 계십니다! 💛"
]

# ==========================================
# [CSS] 전역 서울남산체 적용 및 반응형 UI 디자인
# ==========================================
st.markdown("""
<style>
    @font-face {
        font-family: 'SeoulNamsan';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/SeoulNamsanM.woff') format('woff');
        font-weight: normal; font-style: normal;
    }

    html, body, [class*="st-"], p, h1, h2, h3, h4, h5, h6, label, input, textarea, button, li, a, strong, b, div, span {
        font-family: 'SeoulNamsan', sans-serif !important;
    }

    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: #f8fafc; }
    
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #1e293b !important; border: 2px solid #00A3E0 !important; border-radius: 10px !important;
    }
    input, textarea { color: #ffffff !important; font-size: 16px !important; }
    
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important; border: 2px solid #00A3E0 !important; border-radius: 10px !important;
    }
    div[data-baseweb="select"] * { color: #ffffff !important; font-weight: bold !important; }
    
    label { color: #f8fafc !important; font-weight: bold !important; font-size: 15px !important; }

    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(45deg, #00A3E0, #003876) !important; 
        color: #ffffff !important; font-weight: 900 !important; font-size: 16px !important; 
        border: none !important; border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(0, 163, 224, 0.4) !important; transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 20px rgba(0, 163, 224, 0.6) !important; }

    .stTabs [data-baseweb="tab-list"] { gap: 5px; justify-content: center; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255,255,255,0.1); border-radius: 8px 8px 0 0; padding: 10px 15px; color: #cbd5e1; font-size: 14px; }
    .stTabs [aria-selected="true"] { background-color: rgba(0, 163, 224, 0.3); color: #7dd3fc !important; border-bottom: 3px solid #00A3E0; font-weight: bold; }

    /* Expander UI 에러 수정 (svg 관련 스타일 제거) */
    [data-testid="stExpander"] { background-color: #1e293b !important; border: 1px solid #00A3E0 !important; border-radius: 10px !important; overflow: hidden !important; }
    [data-testid="stExpander"] summary { background-color: #1e293b !important; }
    [data-testid="stExpander"] summary p { color: #fde047 !important; font-weight: bold !important; font-size: 16px !important; }
    [data-testid="stExpanderDetails"] { background-color: #1e293b !important; }
    [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li { color: #f8fafc !important; font-size: 15px !important; line-height: 1.6 !important; }

    .neon-title { font-size: 40px; font-weight: 900; color: #ffffff; text-align: center; margin-top: 20px; margin-bottom: 10px; letter-spacing: 1px; text-shadow: 0 0 10px #00A3E0, 0 0 20px #00A3E0; }
    .sub-title { color: #94a3b8; font-size: 16px; margin-bottom: 30px; text-align: center; }
    
    .question-box { background: rgba(255,255,255,0.05); border-left: 5px solid #facc15; padding: 20px; border-radius: 10px; font-size: 18px; font-weight: bold; margin-bottom: 20px; line-height: 1.5; }
    .ai-box { background: rgba(16, 185, 129, 0.1); border-left: 5px solid #10b981; padding: 20px; border-radius: 10px; font-size: 16px; line-height: 1.6; margin-top: 20px; white-space: pre-wrap; }
    
    .link-btn-container:hover { transform: translateY(-2px); }

    @media (max-width: 768px) {
        .neon-title { font-size: 28px !important; line-height: 1.4 !important; margin-top: 10px !important; }
        .sub-title { font-size: 14px !important; line-height: 1.6 !important; padding: 0 10px !important; word-break: keep-all !important; }
        .question-box { font-size: 16px !important; padding: 15px !important; line-height: 1.7 !important; word-break: keep-all !important; }
        .ai-box { font-size: 15px !important; padding: 15px !important; line-height: 1.8 !important; word-break: keep-all !important; }
        .mobile-br { display: block !important; content: ""; margin-top: 5px; }
    }
    @media (min-width: 769px) { .mobile-br { display: none !important; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'current_question' not in st.session_state: st.session_state['current_question'] = ""
if 'ai_feedback' not in st.session_state: st.session_state['ai_feedback'] = ""
if 'ai_new_question' not in st.session_state: st.session_state['ai_new_question'] = ""
if 'ai_new_feedback' not in st.session_state: st.session_state['ai_new_feedback'] = ""
if 'cheer_msg' not in st.session_state: st.session_state['cheer_msg'] = random.choice(ENCOURAGEMENTS)

# ==========================================
# [화면 구성] 메인 학습 화면
# ==========================================
st.markdown("<div class='neon-title'>기계안전기술사 AI 학습 센터</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>기계공학 파트 완벽 대비! <br class='mobile-br'>30년 차 출제위원 AI가 <br class='mobile-br'>당신의 답안을 첨삭합니다.</div>", unsafe_allow_html=True)

st.markdown(f"""
<div style="background: rgba(255, 193, 7, 0.15); border-left: 5px solid #ffc107; padding: 15px; border-radius: 10px; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
    <span style="font-size: 18px; font-weight: bold; color: #fde047; word-break: keep-all;">"{st.session_state['cheer_msg']}"</span>
</div>
""", unsafe_allow_html=True)

tab_subnote, tab1, tab2, tab_new, tab3, tab4 = st.tabs([
    "📖 핵심 서브노트", "🔥 빈출 핵심 테마", "🎲 랜덤 기출 풀이", "💡 AI 신출 모의고사", "📚 나의 오답 노트", "🔍 법령 및 KOSHA 가이드"
])

# ------------------------------------------
# [탭 0] 핵심 서브노트 요약 (가장 중요)
# ------------------------------------------
with tab_subnote:
    st.markdown("### 📖 기계안전기술사 핵심 서브노트 요약")
    st.info("제공된 서브노트 123페이지 분량을 6개의 대주제로 압축했습니다. 매일 열어보고 암기하세요!")
    
    with st.expander("1️⃣ 기계안전 일반 및 위험성평가"):
        st.markdown("""
        **■ 피로 (Fatigue)**
        - **피로한도 영향인자**: 노치, 치수효과, 표면거칠기, 부식, 반복하중, 온도, 압입가공
        - **향상방안**: 노치 깊이 얕게, 표면 다듬질, 질화/침탄/고주파경화/쇼트피닝 등 표면경화
        
        **■ 위험성평가**
        - **절차**: 사전준비 → 유해·위험요인 파악 → 위험성 추정 → 위험성 결정 → 감소대책 수립 및 실행
        - **기법**: HAZOP(위험과 운전분석), FTA(결함수 분석, 연역적), ETA(사건수 분석, 귀납적), Check-List 등
        
        **■ 본질안전화 3원칙**
        - 안전기능이 기계장치에 내장되어 있을 것
        - Fail Safe 기능을 가질 것 (Passive, Active, Operational)
        - Fool Proof (인간이 실수해도 안전장치가 작동하여 사고 방지)
        
        **■ 응력집중 및 안전계수**
        - **안전계수** = 기초강도(극한강도, 피로한도 등) / 허용응력
        - **응력집중 완화대책**: 단면변화 완만화, 보강재 결합, 표면강화(쇼트피닝 등), 잔류응력 제거
        
        **■ 욕조곡선 (Bath-tub Curve)**
        - **초기고장(DFR)**: 디버깅, 번인 기간 (설계/제조 결함)
        - **우발고장(CFR)**: 사용조건상 고장, 고장률 일정
        - **마모고장(IFR)**: 피로, 마모, 노화 (예방보전 PM 필요)
        """)

    with st.expander("2️⃣ 하역운반기계 및 양중기"):
        st.markdown("""
        **■ 지게차**
        - **안정도 기준**: 하역 전후 4% 이내, 하역 좌우 6% 이내, 주행 전후 18% 이내
        - **안전장치**: 헤드가드(상부틀 개구부 16cm 미만), 백레스트, 전조등/후미등, 안전벨트
        
        **■ 크레인 (양중기)**
        - **방호장치**: 과부하방지장치, 권과방지장치, 충돌방지장치, 비상정지장치, 훅 해지장치, 브레이크
        - **와이어로프 사용금지 기준**: 이음매 있는 것, 한 꼬임에서 소선 수 10% 이상 절단, 공칭지름 7% 초과 감소, 꼬인 것, 심하게 변형/부식된 것
        - **안전계수**: 근로자 탑승 10 이상, 화물 직접 지지 5 이상, 훅/샤클 3 이상, 기타 4 이상
        
        **■ 승강기 및 리프트**
        - **승강기 방호장치**: 과부하방지, 비상정지장치, 조속기(Governor), 파이널 리미트 스위치, 완충기
        - **리프트 방호장치**: 권과방지, 과부하방지, 비상정지, 낙하방지장치, 출입문 연동장치
        """)

    with st.expander("3️⃣ 기계설비 및 방호장치"):
        st.markdown("""
        **■ 프레스**
        - **방호장치 종류**: 양수조작식, 가드식, 광전자식, 손쳐내기식, 수인식
        - **광전자식 안전거리**: D = 1.6 × (Te + Ts) [mm]
        - **안전기준**: 1행정 1정지기구, 급정지기구, 비상정지장치, 안전블록
        
        **■ 롤러기**
        - **급정지장치**: 손 조작식(1.8m 이내), 복부 조작식(0.8~1.1m), 무릎 조작식(0.4~0.6m)
        - **급정지거리**: 표면속도 30m/min 미만(원주의 1/3 이내), 30m/min 이상(원주의 1/2.5 이내)
        
        **■ 연삭기**
        - **파괴원인**: 규정속도 초과, 균열, 플랜지 직경 불량, 측면 사용, 진동 발생
        - **덮개 노출각도**: 탁상용(90도 이내), 휴대용/스윙(180도 이내), 평면(150도 이내)
        - **3요소 5인자**: 입자, 결합체, 기공 / 입자재료, 입도, 결합도, 조직, 결합제
        
        **■ 산업용 로봇**
        - **방호장치**: 1.8m 이상 방책, 안전매트, 광전자식 방호장치
        - **교시작업**: 매니퓰레이터 속도 자동 감소, 비상정지장치 구비, 작업시작 전 점검(피복 손상, 제동장치 등)
        """)

    with st.expander("4️⃣ 보일러 및 압력용기"):
        st.markdown("""
        **■ 보일러 장애요인**
        - **캐리오버(Carry Over)**: 수면의 물방울이 증기와 함께 나가는 현상 (원인: 고수위, 과부하, 관수 농축)
        - **프라이밍(Priming)**: 물방울이 튀어 오르는 현상 / **포밍(Foaming)**: 다량의 거품 발생
        - **방호장치**: 고저수위 조절장치, 압력방출장치, 압력제한 스위치
        
        **■ 압력용기**
        - **응력 계산**: 원주방향 응력이 축방향 응력의 2배이므로, 두께 결정 시 원주방향 응력 기준 계산
        - **파열판 설치조건**: 반응폭주 급격한 압력상승, 독성물질 누출 우려, 안전밸브에 이상물질 누적 우려 시
        
        **■ 펌프 (Pump)**
        - **캐비테이션(Cavitation)**: 유속 증가로 압력이 포화증기압보다 낮아져 기포 발생 (방지: 흡입관 짧게, 회전수 감소)
        - **서징(Surging)**: 압력계기 눈금이 주기적으로 크게 흔들리는 맥동 현상
        - **수격작용(Water Hammering)**: 밸브 급개폐 시 유속 변화로 인한 압력 상승 (방지: 서지탱크 설치, 플라이휠 설치)
        """)

    with st.expander("5️⃣ 용접 및 비파괴검사"):
        st.markdown("""
        **■ 비파괴검사 (NDT)**
        - **PT (침투)**: 표면 결함, 비자성체 가능, 저렴 / 내부결함 불가
        - **MT (자분)**: 표면 및 직하 결함, 강자성체만 가능, PT보다 미세결함 검출
        - **UT (초음파)**: 내부 결함(체적), 두꺼운 재질 가능 / 숙련도 요구
        - **RT (방사선)**: 내부 결함, 영구기록 보존 / 방사선 위험, 양면 접근 필요
        - **AE (음향방출)**: 동적 거동 평가, 실시간 모니터링 가능
        
        **■ 용접 결함 및 잔류응력**
        - **결함 종류**: 언더컷(전류 과다), 오버랩(전류 과소), 용입불량, 은점(수소 취화)
        - **잔류응력 완화법**: 응력제거 소둔(Annealing), 노내응력 제거, 국부응력 제거, 피이닝(Peening)
        
        **■ 가스 용접 위험성**
        - **역류**: 산소가 아세틸렌 도관으로 흘러감
        - **역화**: 불꽃이 토치 끝에서 소리를 내며 꺼지거나 들어감
        - **인화**: 불꽃이 혼합실까지 밀려들어가는 현상
        """)

    with st.expander("6️⃣ 안전보건법령 및 기타"):
        st.markdown("""
        **■ 안전인증 및 안전검사**
        - **안전인증 대상**: 프레스, 전단기, 크레인, 리프트, 압력용기, 롤러기, 사출성형기, 고소작업대, 곤돌라 등
        - **안전검사 대상**: 인증대상 + 국소배기장치, 원심기, 화학설비, 건조설비, 컨베이어, 산업용 로봇 등
        
        **■ 공정안전보고서 (PSM)**
        - **12대 실천과제**: 공정안전자료 관리, 위험성평가, 안전운전절차, 도급업체 안전관리, 비상대응 훈련 등
        - **포함사항**: 공정안전자료, 공정위험평가서, 안전운전계획, 비상조치계획
        
        **■ 재해율 계산**
        - **도수율(빈도율)** = (재해건수 / 연근로시간) × 1,000,000
        - **강도율** = (근로손실일수 / 연근로시간) × 1,000
        - **연천인율** = (재해자수 / 연평균근로자수) × 1,000 (도수율 × 2.4)
        
        **■ 제조물 책임법 (PL법)**
        - **결함의 분류**: 설계상의 결함, 제조상의 결함, 표시상의 결함(경고 누락)
        """)

# ------------------------------------------
# [탭 1] 빈출 핵심 테마
# ------------------------------------------
with tab1:
    st.markdown("### 📊 기계안전기술사 출제 빈도 Top 6")
    st.info("아래 테마들은 기계안전기술사 합격을 위해 무조건 암기해야 할 핵심 내용입니다.")
    
    with st.expander("🥇 1순위: 기계안전 일반 및 위험성평가"):
        st.write("- 피로파괴, 응력집중, 안전계수, Creep 현상")
        st.write("- 본질안전화 3원칙, Fail Safe, Fool Proof")
        st.write("- 위험성평가 절차 및 정량적 기법(FTA, ETA)")
        
    with st.expander("🥈 2순위: 양중기 및 운반기계"):
        st.write("- 크레인 방호장치 (과부하방지, 권과방지, 비상정지)")
        st.write("- 지게차 안정도 조건 및 헤드가드 기준")
        st.write("- 와이어로프 폐기 기준 및 안전계수")
        
    with st.expander("🥉 3순위: 압력용기 및 보일러"):
        st.write("- 보일러 이상현상 (프라이밍, 포밍, 캐리오버)")
        st.write("- 압력용기 안전설계 (원주방향/축방향 응력 계산)")
        st.write("- 펌프 이상현상 (Cavitation, Surging, 수격작용)")
        
    with st.expander("🏅 4순위: 용접 및 비파괴검사"):
        st.write("- 비파괴검사 비교 (PT, MT, UT, RT, AE, ECT)")
        st.write("- 용접 결함 (오버랩, 언더컷, 은점 등) 및 잔류응력 완화법")
        st.write("- 가스용접 위험성 (역류, 역화, 인화)")
        
    with st.expander("🏅 5순위: 공작기계 및 산업용 로봇"):
        st.write("- 프레스 방호장치 (양수조작식, 광전자식 안전거리 계산)")
        st.write("- 산업용 로봇 교시 작업 안전수칙 및 방호장치")
        st.write("- 연삭숫돌 파괴원인 및 덮개 노출각도")
        
    with st.expander("🏅 6순위: 안전보건법령 및 안전관리"):
        st.write("- 안전인증 및 안전검사 대상 기계·기구")
        st.write("- 공정안전보고서(PSM) 및 유해위험방지계획서")
        st.write("- 하인리히 재해예방 4원칙, 버드의 신연쇄성 이론")

# ------------------------------------------
# [탭 2] 랜덤 기출 풀이 및 AI 첨삭
# ------------------------------------------
with tab2:
    st.markdown("### ✍️ 실전 모의고사 (서브노트 기반 기출문제)")
    
    if st.button("🎲 새로운 기출문제 뽑기", use_container_width=True):
        st.session_state['current_question'] = random.choice(QUESTIONS)
        st.session_state['ai_feedback'] = ""
        st.session_state['cheer_msg'] = random.choice(ENCOURAGEMENTS)
        st.rerun()
        
    if st.session_state['current_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['current_question']}</div>", unsafe_allow_html=True)
        
        user_answer = st.text_area("답안을 작성하세요 (실제 시험처럼 키워드 위주로 작성해보세요)", height=200, key="ans_real")
        
        if st.button("✨ AI 출제위원에게 정답 보완 및 첨삭 받기", use_container_width=True, key="btn_real"):
            if not user_answer.strip():
                st.warning("답안을 조금이라도 작성해야 첨삭이 가능합니다.")
            else:
                with st.spinner("30년 차 출제위원이 답안을 분석하고 모범 답안을 작성 중입니다... ⏳"):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 기계안전기술사 출제 위원입니다.
                        문제: {st.session_state['current_question']}
                        수험생의 답변: {user_answer}
                        
                        [지시사항]
                        1. 수험생의 답변을 100점 만점 기준으로 채점하고 짧은 총평을 해주세요.
                        2. 누락된 핵심 법적 키워드나 공학적 개념을 추가하여 완벽한 모범 답안을 제시해주세요.
                        3. 답변 작성 시 제공된 기계안전 이론을 바탕으로 하되, **2024년 개정된 산업안전보건법령(예: 분쇄기·파쇄기·혼합기·식품가공용기계 덮개 개방 시 연동장치 의무화 등)과 2025년 KOSHA GUIDE(기술지원규정으로 명칭 변경 및 체계 개편) 최신 사항**을 반드시 반영하여 설명하세요.
                        4. 수식을 포함한 답변을 작성할 때, 수식 전후에 반드시 개행을 두 번 추가하여 수식이 명확하게 구분되도록 하세요.
                        5. 전문적이고 명확한 어조(~합니다, ~입니다)를 사용하세요.
                        """
                        
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
                        
                        response = requests.post(url, headers=headers, json=data, timeout=15)
                        
                        if response.status_code == 200:
                            feedback = response.json()['choices'][0]['message']['content']
                            st.session_state['ai_feedback'] = feedback
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            c.execute("INSERT INTO study_records (user_id, date, question, user_answer, ai_feedback) VALUES (?, ?, ?, ?, ?)", 
                                      ("수험생", now, "[기출] " + st.session_state['current_question'], user_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"🚨 API 호출 오류가 발생했습니다. (상태 코드: {response.status_code})")
                    except Exception as e:
                        st.error(f"🚨 통신 오류가 발생했습니다: {e}")
                        
        if st.session_state['ai_feedback']:
            st.markdown(f"<div class='ai-box'><b>💡 [AI 출제위원의 첨삭 결과]</b><br><br>{st.session_state['ai_feedback']}</div>", unsafe_allow_html=True)
    else:
        st.info("위의 '새로운 기출문제 뽑기' 버튼을 눌러 학습을 시작하세요.")

# ------------------------------------------
# [탭 3] AI 신출 모의고사 (기출 변형 문제)
# ------------------------------------------
with tab_new:
    st.markdown("### 💡 AI 기출 변형 신출 모의고사")
    st.write("역대 기출문제를 바탕으로 상황 제시형, 최신 법령 연계 등 최신 트렌드가 반영된 꼬아낸 문제를 풀어보세요.")
    
    themes = list(THEME_PAST_QUESTIONS.keys())
    selected_theme = st.selectbox("출제 테마를 선택하세요:", themes)
    
    if st.button("🚀 선택한 테마로 기출 변형 문제 출제하기", use_container_width=True):
        with st.spinner("AI 출제위원이 역대 기출문제를 분석하여 변형 문제를 출제 중입니다... ⏳"):
            try:
                past_qs_text = "\n".join([f"- {q}" for q in THEME_PAST_QUESTIONS[selected_theme]])
                
                prompt = f"""
                당신은 기계안전기술사 2차 시험 출제위원입니다.
                사용자가 선택한 테마: '{selected_theme}'
                
                [해당 테마의 역대 기출문제]
                {past_qs_text}
                
                [출제 지침]
                위 기출문제들을 분석하여, 이와 연관되지만 똑같지는 않은 **'기출 변형 신출 모의고사' 1문제**를 출제하세요.
                단순히 묻는 방식을 바꾸는 것을 넘어 아래 4가지 전략 중 하나 이상을 반드시 적용하여 문제를 꼬아서 내세요.
                1. 최신 법령 연계: 2024년 산안법 개정(식품가공용기계, 파쇄기 연동장치 등) 또는 2025년 KOSHA GUIDE(기술지원규정) 개편 사항 엮기
                2. 상황 제시형(시나리오): "A공장에서 B작업을 하던 중 C사고가 발생했다..." 와 같이 구체적 상황을 주고 원인/대책/방호장치를 묻기
                3. 원리 이해 및 적용: 단순 암기가 아닌, 왜 그런 안전장치가 필요한지 공학적 원리나 계산(응력, 안전거리 등)을 묻기
                4. 최신 동향 반영: 스마트 팩토리, 무인화 설비 등 최신 산업 트렌드를 기존 기계안전 개념과 엮어서 묻기
                
                반드시 문제만 출력하고, 정답이나 해설은 절대 포함하지 마세요.
                """
                
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                
                response = requests.post(url, headers=headers, json=data, timeout=15)
                
                if response.status_code == 200:
                    st.session_state['ai_new_question'] = response.json()['choices'][0]['message']['content']
                    st.session_state['ai_new_feedback'] = ""
                else:
                    st.error("🚨 문제 출제 중 오류가 발생했습니다.")
            except Exception as e:
                st.error(f"🚨 통신 오류: {e}")

    if st.session_state['ai_new_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['ai_new_question']}</div>", unsafe_allow_html=True)
        
        user_new_answer = st.text_area("답안을 작성하세요 (상황에 맞는 법적/공학적 근거를 제시하세요)", height=200, key="ans_new")
        
        if st.button("✨ AI 출제위원에게 정답 보완 및 첨삭 받기", use_container_width=True, key="btn_new"):
            if not user_new_answer.strip():
                st.warning("답안을 조금이라도 작성해야 첨삭이 가능합니다.")
            else:
                with st.spinner("AI 출제위원이 답안을 분석하고 모범 답안을 작성 중입니다... ⏳"):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 기계안전기술사 출제 위원입니다.
                        문제: {st.session_state['ai_new_question']}
                        수험생의 답변: {user_new_answer}
                        
                        [지시사항]
                        1. 수험생의 답변을 100점 만점 기준으로 채점하고 짧은 총평을 해주세요.
                        2. 누락된 핵심 법적 키워드나 공학적 개념을 추가하여 완벽한 모범 답안을 제시해주세요.
                        3. 답변 작성 시 제공된 기계안전 이론을 바탕으로 하되, **2024년 개정된 산업안전보건법령과 2025년 KOSHA GUIDE(기술지원규정) 최신 사항**을 반드시 반영하여 설명하세요.
                        4. 수식을 포함한 답변을 작성할 때, 수식 전후에 반드시 개행을 두 번 추가하여 수식이 명확하게 구분되도록 하세요.
                        5. 전문적이고 명확한 어조(~합니다, ~입니다)를 사용하세요.
                        """
                        
                        url = "https://api.groq.com/openai/v1/chat/completions"
                        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
                        data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3}
                        
                        response = requests.post(url, headers=headers, json=data, timeout=15)
                        
                        if response.status_code == 200:
                            feedback = response.json()['choices'][0]['message']['content']
                            st.session_state['ai_new_feedback'] = feedback
                            
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            c.execute("INSERT INTO study_records (user_id, date, question, user_answer, ai_feedback) VALUES (?, ?, ?, ?, ?)", 
                                      ("수험생", now, "[AI 신출] " + st.session_state['ai_new_question'], user_new_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"🚨 API 호출 오류가 발생했습니다. (상태 코드: {response.status_code})")
                    except Exception as e:
                        st.error(f"🚨 통신 오류가 발생했습니다: {e}")
                        
        if st.session_state['ai_new_feedback']:
            st.markdown(f"<div class='ai-box'><b>💡 [AI 출제위원의 첨삭 결과]</b><br><br>{st.session_state['ai_new_feedback']}</div>", unsafe_allow_html=True)

# ------------------------------------------
# [탭 4] 나의 오답 노트
# ------------------------------------------
with tab3:
    st.markdown("### 📚 내가 작성한 답안 및 AI 피드백 기록")
    
    c.execute("SELECT id, date, question, user_answer, ai_feedback FROM study_records WHERE user_id=? ORDER BY id DESC", ("수험생",))
    records = c.fetchall()
    
    if not records:
        st.info("아직 학습 기록이 없습니다. 실전 모의고사를 풀어보세요!")
    else:
        for record in records:
            r_id, date, q, ans, ai = record
            with st.expander(f"📝 {date} 학습 기록 (클릭하여 펼치기)"):
                st.markdown(f"**Q. {q}**")
                st.markdown(f"<div style='background:rgba(255,255,255,0.1); padding:10px; border-radius:5px; word-break: keep-all;'><b>나의 답안:</b><br>{ans}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:rgba(16,185,129,0.1); padding:10px; border-radius:5px; margin-top:10px; word-break: keep-all;'><b>AI 피드백:</b><br>{ai}</div>", unsafe_allow_html=True)
                
                if st.button("🗑️ 이 기록 삭제", key=f"del_{r_id}"):
                    c.execute("DELETE FROM study_records WHERE id=?", (r_id,))
                    conn.commit()
                    st.rerun()

# ------------------------------------------
# [탭 5] 법령 및 KOSHA 가이드 외부 링크
# ------------------------------------------
with tab4:
    st.markdown("### 🔍 안전보건 법령 및 KOSHA 가이드")
    st.write("2024년 개정 법령 및 2025년 KOSHA GUIDE(기술지원규정) 원문을 확인하세요.")
    st.write("")
    
    st.markdown("""
    <a href="https://asdfg.kr" target="_blank" style="text-decoration: none;">
        <div class="link-btn-container" style="background: linear-gradient(135deg, #00A3E0 0%, #003876 100%); padding: 18px; border-radius: 10px; text-align: center; color: white; font-weight: bold; font-size: 18px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0, 163, 224, 0.4); transition: transform 0.2s;">
            ⚖️ 안전보건 법령 통합 검색 <br class='mobile-br'>(asdfg.kr) 바로가기
        </div>
    </a>
    """, unsafe_allow_html=True)

    st.markdown("""
    <a href="https://oshri.kosha.or.kr/cms/resFileDownload.do?siteId=kosha&type=etc&fileName=%282024%EB%85%84%29%EA%B8%B0%EC%88%A0%EC%A7%80%EC%9B%90%EA%B7%9C%EC%A0%95%EA%B0%9C%ED%8E%B8%EC%97%90%EB%94%B0%EB%A5%B8%EC%97%B0%EA%B3%84%ED%91%9C%28%
