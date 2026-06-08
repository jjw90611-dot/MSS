import streamlit as st
import sqlite3
import datetime
import random
import requests

# ==========================================
# [초기 설정] 페이지 세팅 (엑셀 느낌을 위해 아이콘 및 제목 단순화)
# ==========================================
st.set_page_config(page_title="Book1 - Excel", page_icon="📊", layout="wide")

# ==========================================
# [Groq API 키 설정]
# ==========================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("System Error: API Key is missing in secrets.")
    st.stop()

# ==========================================
# [데이터베이스 설정] SQLite3
# ==========================================
conn = sqlite3.connect('mech_safety_study.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS study_records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, date TEXT, question TEXT, user_answer TEXT, ai_feedback TEXT)''')
conn.commit()

# ==========================================
# [기출문제 데이터베이스]
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

THEME_PAST_QUESTIONS = {
    "1. 기계안전 일반 및 위험성평가": QUESTIONS[0:3] + QUESTIONS[18:21] + QUESTIONS[26:29],
    "2. 양중기 및 운반기계": QUESTIONS[3:4] + QUESTIONS[7:8] + QUESTIONS[15:17] + QUESTIONS[21:22],
    "3. 압력용기 및 보일러": QUESTIONS[5:6] + QUESTIONS[13:14] + QUESTIONS[17:18],
    "4. 용접 및 비파괴검사": QUESTIONS[4:5] + QUESTIONS[12:13] + QUESTIONS[22:23],
    "5. 공작기계 및 산업용 로봇": QUESTIONS[6:7] + QUESTIONS[8:9] + QUESTIONS[14:15] + QUESTIONS[23:24],
    "6. 안전보건법령 및 안전관리": QUESTIONS[9:12] + QUESTIONS[25:26] + QUESTIONS[29:30]
}

# ==========================================
# [CSS] 엑셀 스타일 + 서울남산체 + Arrow 에러 완벽 해결
# ==========================================
st.markdown("""
<style>
    /* 서울남산체 폰트 로드 */
    @font-face {
        font-family: 'SeoulNamsan';
        src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_two@1.0/SeoulNamsanM.woff') format('woff');
        font-weight: normal; font-style: normal;
    }

    /* 전체 폰트 적용 (단, SVG 아이콘은 제외하여 Arrow 겹침 에러 방지) */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp li, .stApp a, .stApp strong, .stApp b, .stApp span {
        font-family: 'SeoulNamsan', sans-serif !important;
        color: #000000 !important;
    }
    
    /* Arrow 겹침 에러 원천 차단 (SVG 요소 보호) */
    svg, svg * {
        font-family: initial !important;
    }

    .stApp { background-color: #ffffff; }
    
    /* 입력창 (엑셀 셀 느낌) */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #ffffff !important; 
        border: 1px solid #a6a6a6 !important; 
        border-radius: 0px !important;
    }
    input, textarea { font-size: 14px !important; }
    
    /* 셀렉트박스 */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important; 
        border: 1px solid #a6a6a6 !important; 
        border-radius: 0px !important;
    }
    
    /* 버튼 (엑셀 리본 메뉴 버튼 느낌) */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #f3f2f1 !important; 
        color: #201f1e !important; 
        font-weight: normal !important; 
        font-size: 14px !important; 
        border: 1px solid #8a8886 !important; 
        border-radius: 0px !important;
        box-shadow: none !important; 
        transition: none !important;
        padding: 4px 12px !important;
    }
    div[data-testid="stButton"] > button:hover { background-color: #e1dfdd !important; }

    /* 탭 (엑셀 하단 시트 느낌) */
    .stTabs [data-baseweb="tab-list"] { border-bottom: 1px solid #a6a6a6; gap: 0px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f3f2f1; 
        border: 1px solid #a6a6a6; 
        border-bottom: none; 
        border-radius: 0px; 
        padding: 6px 15px; 
        margin-right: 2px;
        font-size: 13px; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ffffff !important; 
        border-top: 3px solid #107c41 !important; 
        font-weight: bold; 
    }

    /* Expander (표의 행 느낌) */
    [data-testid="stExpander"] { 
        background-color: #ffffff !important; 
        border: 1px solid #d2d2d2 !important; 
        border-radius: 0px !important; 
        margin-bottom: -1px !important; 
    }
    
    /* Sheet1 서브노트 내용 가독성 및 글자 크기 확대 */
    [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li { 
        font-size: 15px !important; 
        line-height: 1.8 !important; 
    }

    /* 타이틀 및 텍스트 박스 단순화 */
    .excel-title { font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 5px; border-bottom: 2px solid #107c41; padding-bottom: 5px; }
    .status-bar { background-color: #f3f2f1; border: 1px solid #d2d2d2; padding: 5px 10px; font-size: 13px; color: #333; margin-bottom: 15px; }
    .question-box { background-color: #ffffff; border: 1px solid #000000; padding: 15px; font-size: 15px; font-weight: bold; margin-bottom: 10px; }
    .ai-box { background-color: #f9f9f9; border: 1px dashed #8a8886; padding: 15px; font-size: 14px; margin-top: 10px; white-space: pre-wrap; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# [세션 상태 관리]
# ==========================================
if 'current_question' not in st.session_state: st.session_state['current_question'] = ""
if 'ai_feedback' not in st.session_state: st.session_state['ai_feedback'] = ""
if 'ai_new_question' not in st.session_state: st.session_state['ai_new_question'] = ""
if 'ai_new_feedback' not in st.session_state: st.session_state['ai_new_feedback'] = ""

# ==========================================
# [화면 구성] 메인 화면 (사내 시스템/엑셀 위장)
# ==========================================
st.markdown("<div class='excel-title'>Data Analysis & Review System (v2026.1)</div>", unsafe_allow_html=True)
st.markdown("<div class='status-bar'>Status: Ready | User: Admin | DB Connection: OK | Current Year: 2026</div>", unsafe_allow_html=True)

tab_subnote, tab1, tab2, tab_new, tab3, tab4 = st.tabs([
    "Sheet1 (Data_Raw)", "Sheet2 (Summary)", "Sheet3 (Test_A)", "Sheet4 (Test_B)", "Sheet5 (Log)", "Sheet6 (Ref_Link)"
])

# ------------------------------------------
# [탭 0] 핵심 서브노트 (가독성 및 맞춤법 개선)
# ------------------------------------------
with tab_subnote:
    st.markdown("**[Raw Data] 기계안전기술사 핵심 서브노트 (2026년 기준 최신화 및 가독성 개선)**")
    
    with st.expander("Row 1: 기계안전 일반 및 위험성평가"):
        st.markdown("""
        **[ 1. 피로 ]**

        **1. 개요**
        가. 기계, 구조물 및 그 부품이 받는 하중은 일정한 정하중인 경우보다 주기적으로 변화하는 반복하중이나 변동하중인 경우가 많습니다.
        나. 재료에 반복하중을 가하면 정하중의 경우보다 훨씬 작은 하중으로도 파괴됩니다.
        다. 이러한 현상을 “재료의 피로 파괴”라고 합니다.
        라. 따라서 반복하중을 받는 부재를 설계할 때는 특히 주의해야 합니다.

        **2. 피로파괴의 특성**
        가. 피로한도·피로한계
        1) 어느 한계 응력 하에서는 아무리 많은 반복하중이 가해져도 피로 현상이 발생하지 않습니다.
        2) 이 한계를 피로한도 또는 피로한계라 합니다.
        나. 피로에 의해 파괴될 시, 연성 재료도 취성 재료처럼 거의 변형 없이 갑자기 파괴되며, 균열의 점진적 발생부와 급격한 파괴부를 뚜렷하게 구별할 수 있습니다.

        **3. 피로한도 영향 인자 7가지**
        가. 피로한도: 기계를 구성하는 금속 재료가 반복적으로 굽힘 하중을 받으면 허용 하중보다 작은 하중에서도 파괴되는데 이를 피로(Fatigue)라 합니다. 아무리 반복하여도 피로 파괴가 일어나지 않는 응력의 한도를 “피로한도”라 합니다.
        나. 피로한도에 영향을 주는 요소: 1) 노치 2) 치수 효과 3) 표면 거칠기 4) 부식 5) 반복하중 6) 압입 가공 7) 온도

        **4. 피로한도 향상 방안**
        가. 노치 효과: 노치 깊이를 얕게, 노치 반지름 R을 크게 합니다.
        나. 치수 효과: 지름을 되도록 작게 하고, 치수 효과 계수를 1.0으로 맞춥니다.
        다. 표면 거칠기: 강축의 경우 표면 다듬질을 매끈하게 실시합니다.
        라. 온도: 온도가 상승하면 전위의 이동이 용이해지고 가공에 의한 경화가 쉽게 회복되어 연화되기 때문에 적절한 온도 관리가 필요합니다.
        마. 반복하중: 반복하중 중에서 굽힘 하중을 가능한 한 피해야 합니다. (인장, 굽힘, 압축)
        바. 압입 가공: 압입 가공이나 때려 박을 시 변형률을 작게 합니다.
        사. 부식 작용을 방지합니다.

        **5. 결론**
        가. 노치 효과, 치수 효과, 표면 상황, 부식 작용, 압입 등은 피로한도를 저하시킵니다.
        나. 질화, 침탄, 고주파 경화, 쇼트 피닝, 샌드 블라스트 등은 피로한도를 향상시킵니다.
        다. 기계 또는 구조물 설계 시 피로한도에 영향을 미치는 각종 인자에 대해 검토하고, 허용 응력 산출 시 기준 강도를 피로한도보다 작게 설정해야 합니다.

        <br>

        **[ 2. 위험성 평가 ]**

        **1. 개요**
        가. 위험성 평가란 유해·위험 요인을 파악하고,
        나. 해당 유해·위험 요인에 의한 부상 또는 질병의 발생 가능성(빈도)과 중대성(강도)을 추정·결정하며,
        다. 감소 대책을 수립하여 실행하는 일련의 과정을 말합니다.
        라. 순서는 자료 수집 → 유해·위험 요인 파악 → 위험성 추정 → 위험성 결정 → 감소 대책 수립 및 실시 → 기록의 순으로 진행합니다.

        **2. 자료 수집**: 작업 표준, 기계 사양서, 공정 흐름, 도급 사업 혼재 작업, 재해 사례, 작업 환경 측정 결과 등
        
        **3. 유해·위험 요인 파악**: 사업장 순회 점검, 청취 조사, 안전보건 자료, 체크리스트 등
        
        **4. 위험성 추정**: 가능성과 중대성을 행렬, 곱하기, 더하기 등으로 산출하며, 최악의 상황에서 가장 큰 부상을 추정합니다.
        
        **5. 위험성 결정**: 추정한 위험성의 크기가 허용 가능한 범위인지 여부를 판단합니다.
        
        **6. 감소 대책 수립 및 실시**: 위험한 작업의 폐지·변경 → 공학적 대책 → 관리적 대책 → 개인용 보호구 착용 순으로 실시합니다.
        
        **7. 기록 사항**: 3년간 보존합니다.
        
        **8. 고려 사항**: 유해·위험 요인 위치, 현재 안전 대책, 발생 빈도, 피해 크기 등.
        
        **9. 위험성 평가의 의의**: 안전사고 사전 예방, 재해 특성 예측, 쾌적한 작업 환경 조성.
        
        **10. 위험성 평가 기법의 종류**
        가. 정성적 평가: HAZOP(위험과 운전 분석), PHA(예비 위험 분석 기법), What-If(사고 예상 질문 분석), Check-List
        나. 정량적 위험성 평가: FTA(결함수 위험성 평가, 연역적), ETA(사건수 분석 기법, 귀납적), CA(피해 영향 분석)

        <br>

        **[ 3. 본질 안전화 ]**

        **1. 개요**: 본질 안전 방폭 전기 기계 기구에서 유래한 용어로, 단락이나 단선 등이 발생하여도 외부 분위기에 착화되는 일이 없는 구조를 뜻합니다.

        **2. 본질 안전화 3원칙**
        가. 안전 기능이 기계 장치에 내장되어 있을 것 (예: 안전 프레스, 교류 아크 용접기 자동 전격 방지기)
        나. Fool Proof: 인간이 실수를 하여도 안전장치가 설치되어 있어 사고나 재해로 연결되지 않는 것 (예: 세탁기 뚜껑, 프레스 광전자식, 승강기 과부하 방지)
        다. Fail Safe 기능을 가질 것: 시스템에 고장이 생겨도 어느 기간 동안은 정상 기능이 유지되고 사고나 재해로 발전되지 않는 기구.

        **3. Fail Safe**
        가. Fail Safe의 기능면 3단계
        1) Fail Passive - 부품이 고장 나면 통상 기계는 정지하는 방향으로 이동
        2) Fail Active - 부품이 고장 나면 기계는 경보를 울리는 가운데 짧은 시간 동안의 운전이 가능
        3) Fail Operational - 부품의 고장이 있어도 기계는 추후 보수가 있을 때까지 안전한 기능을 유지하고 병렬 계통 또는 대기 여분 계통으로 유지
        나. Fail Safe 기구: 구조적 Fail Safe(다경로 하중 구조, 분할 구조 등), 기능적 Fail Safe(기계적/전기적 Fail Safe, 증기 보일러 안전변 복수 설치 등)
        """)

    with st.expander("Row 2: 양중기 및 운반기계"):
        st.markdown("""
        **[ 5. 지게차 ]**

        **1. 개요**: 화물 적재용 포크와 마스트를 갖춘 운반 기계입니다.

        **2. 위험성**: 물체의 낙하, 보행자 접촉, 차량의 전도 위험이 있습니다.

        **3. 구배가 있는 장소에서의 안전 조건 (안정도 기준)**
        - 하역 작업 시 전후 안정도: 4% 이내 (5Ton 이상은 3.5% 이내)
        - 하역 작업 시 좌우 안정도: 6% 이내
        - 주행 시 전후 안정도: 18% 이내
        - 주행 시 좌우 안정도: (15+1.1V)% 이내 (V=최고 속도)

        **4. 안전장치**: 안전 Belt, 전조등/후미등, 헤드가드(상부틀 개구부 16cm 미만, 좌식 0.903m 이상, 입식 1.88m 이상), 백레스트.

        **5. 작업 계획서**: 작업 장소 넓이/지형, 기계 종류/능력, 화물 종류/형상, 운반 경로, 위험 예방 방법.

        <br>

        **[ 11. Wire Rope (와이어 로프) ]**

        **1. 개요**: 강선을 꼬아 스트랜드(Strand)를 만들고 이를 다시 꼬아 심(Core)을 넣은 것입니다.

        **2. 꼬임 방법**
        - 보통 꼬임: 스트랜드와 소선 꼬임 방향이 반대입니다. 킹크(Kink)가 잘 생기지 않습니다.
        - 랭 꼬임: 스트랜드와 소선 꼬임 방향이 동일합니다. 내마모성이 크고 유연성이 커서 삭도용/광산용으로 사용됩니다.

        **3. 안전계수**: 근로자 탑승 10 이상, 화물 직접 지지 5 이상, 훅/샤클 3 이상, 기타 4 이상.

        **4. 사용 금지 기준**: 이음매가 있는 것, 한 꼬임에서 소선 수가 10% 이상 절단된 것, 공칭 지름이 7% 초과 감소한 것, 꼬인 것, 심하게 변형되거나 부식된 것, 열/전기 충격으로 손상된 것.

        **5. 연결 고정 방법**: 소켓(이음 효율 최고), 팀블, 웨지, 아이스플라이스, 클립(직경 6배 이상 간격, 4개 이상).

        <br>

        **[ 14. 크레인 ]**

        **1. 개요**: 동력을 사용하여 화물을 달아 올리고 상하, 전후, 좌우로 운반하는 기계입니다.

        **2. 안전장치**
        - 과부하 방지 장치: 정격 하중 이상 시 자동으로 운반을 중단합니다.
        - 권과 방지 장치: 나사형, 캠형, 중추형, 레버형.
        - 후크 해지 장치: 와이어 로프가 벗겨지는 것을 방지합니다.
        - 레일 정지 기구(Stopper), 충돌 방지 장치(광선/초음파, 리미트 스위치).
        - 비상 정지 장치, Brake(전자 브레이크, 전동 유압 압상, 밴드, 원판).
        """)

    with st.expander("Row 3: 기계설비 및 공작기계"):
        st.markdown("""
        **[ 13. 방호 원리 및 방호 장치 ]**

        **1. 방호 원리**: 위험 제거, 차단, 덮어씌움, 위험에의 적응.

        **2. 방호 장치**: 격리형(완전 격리, 덮개, 방책), 위치 제한형(양수 조작식), 접근 거부형(수인식, 손쳐내기식), 접근 반응형(광전자식), 포집형, 감지형.

        <br>

        **[ 15. 프레스 ]**

        **1. 개요**: 동력에 의해 금형을 두고 금속을 압축/절단하여 조형하는 기계입니다.

        **2. 안전 기준**: 1행정 1정지 기구, 급정지 기구, 비상 정지 장치, 미동 기구, 안전 Block, 전환 스위치.

        **3. 방호 장치 종류**
        - 양수 조작식: 동시 누름 0.5초 이내, 내측 최단 거리 300mm 이상.
        - 가드식: 닫지 않으면 작동이 불가합니다.
        - 광전자식: 안전거리 D = 1.6 × (Te + Ts) [mm].
        - 손쳐내기식, 수인식.

        **4. No-Hand in die Type vs Hand in Type**: 자동 송급/배출 장치 도입 권장.

        <br>

        **[ 26. 위험점 ]**

        **1. 협착점**: 왕복 운동을 하는 공작부와 고정부 사이 (예: 프레스).
        
        **2. 끼임점**: 고정부와 회전하는 동작부 사이 (예: 연삭 숫돌과 지지대).
        
        **3. 절단점**: 회전하는 운동부 자체 (예: 밀링 커터, 둥근톱).
        
        **4. 물림점**: 서로 반대 방향으로 맞물려 회전하는 부분 (예: 롤러기, 기어).
        
        **5. 접선 물림점**: 회전하는 부분이 접선 방향으로 물려 들어가는 곳 (예: 체인과 스프로킷, V벨트).
        
        **6. 회전 말림점**: 회전하는 축 등에 의복이나 머리카락이 말려 들어가는 곳 (예: 축, 드릴).
        """)

    with st.expander("Row 4: 보일러, 압력용기 및 펌프"):
        st.markdown("""
        **[ 12. 보일러(Boiler) 장애 요인 ]**

        **1. 캐리오버(Carry Over)**: 수면의 물방울이 증기와 함께 밖으로 나가는 현상입니다. (원인: 고수위, 과부하, 관수 농축)
        
        **2. 프라이밍(Priming)**: 물방울이 격렬하게 튀어 오르는 현상입니다.
        
        **3. 포밍(Foaming)**: 다량의 거품이 발생하는 현상입니다.
        
        **4. 보일러 폭발 방지 장치**: 고저수위 조절 장치, 압력 방출 장치(안전밸브), 압력 제한 스위치.
        
        **5. 역화(Back Fire)**: 미연소 불꽃이 연료 공급 방향으로 역류하는 현상입니다. (방지 대책: 점화 전 충분한 환기, 공기를 먼저 공급)

        <br>

        **[ 27. 압력용기 ]**

        **1. 안전 설계**: 원주 방향 응력이 축 방향 응력의 2배이므로, 두께를 결정할 때는 원주 방향 응력을 기준으로 계산합니다.

        **2. 파열판 설치 조건**: 반응 폭주로 인한 급격한 압력 상승 우려, 독성 물질 누출 우려, 안전밸브에 이상 물질 누적 우려 시 설치합니다. (안전밸브와 직렬 또는 병렬 설치)

        **3. 갑종/을종 분류**: 갑종(설계 압력 0.2MPa 이상 화학 공정 용기, 1MPa 초과 공기/질소 탱크), 을종(갑종 제외).

        **4. 주요 구조부**: 동체(Shell), 경판(Head), 관판(Tube Sheet), 노즐 및 플랜지.

        **5. 방호 장치**: 안전밸브, 긴급 차단 밸브, 파열판, 통기 밸브, 화염 방지기.

        <br>

        **[ 46. 펌프(Pump) ]**

        **1. 캐비테이션(Cavitation)**: 유속 증가로 인해 압력이 포화 증기압보다 낮아져 기포가 발생하는 현상입니다. 진동, 소음 및 침식을 유발합니다. (방지 대책: 흡입관을 짧게, 회전수 감소)

        **2. 서징(Surging)**: 압력 계기 눈금이 주기적으로 크게 흔들리는 맥동 현상입니다. (방지 대책: 우하향 H-Q 곡선 펌프 사용, 배관 내 공기 제거)

        **3. 수격 작용(Water Hammering)**: 밸브를 급격히 개폐할 때 유속 변화로 인해 압력이 급상승하는 현상입니다. (방지 대책: 서지 탱크 설치, 플라이휠 설치, 밸브를 서서히 개폐)
        """)

    with st.expander("Row 5: 용접 및 비파괴검사"):
        st.markdown("""
        **[ 6. 비파괴검사 ]**

        **1. PT (침투 탐상)**: 표면 결함 검출, 비자성체 가능, 저렴함 / 내부 결함은 검출 불가.
        
        **2. MT (자분 탐상)**: 표면 및 직하 결함 검출, 강자성체만 가능, PT보다 미세 결함 검출에 유리.
        
        **3. UT (초음파 탐상)**: 내부 결함(체적) 검출, 두꺼운 재질 가능 / 숙련도가 요구되며 방향성에 민감함.
        
        **4. RT (방사선 투과)**: 내부 결함 검출, 영구 기록 보존 가능 / 방사선 피폭 위험이 있으며 양면 접근이 필요함.
        
        **5. AE (음향 방출)**: 동적 거동 평가, 실시간 모니터링 가능.
        
        **6. ECT (와전류 탐상)**: 표면 결함 검출, 고속 및 자동화 가능, 전도체만 가능.

        <br>

        **[ 18. 아세틸렌 가스 용접 ]**

        **1. 역류**: 산소가 아세틸렌 도관으로 거꾸로 흘러가는 현상.
        
        **2. 역화**: 불꽃이 토치 끝에서 소리를 내며 꺼지거나 안으로 들어가는 현상.
        
        **3. 인화**: 불꽃이 혼합실까지 밀려 들어가는 위험한 현상.

        <br>

        **[ 22. 용접 잔류 응력 ]**

        **1. 발생 원인**: 용융 금속이 응고할 때 부피 수축으로 인해 발생합니다.

        **2. 완화법**: 응력 제거 소둔(Annealing), 노내 응력 제거, 국부 응력 제거, 저온 응력 완화, 기계적 완화, 피이닝(Peening).
        """)

    with st.expander("Row 6: 안전보건법령 및 안전관리"):
        st.markdown("""
        **[ 9. 안전검사 ]**

        **1. 대상 기계·기구**: 프레스, 전단기, 크레인, 리프트, 압력용기, 곤돌라, 국소배기장치, 원심기, 화학설비, 건조설비, 롤러기, 사출성형기, 고소작업대, 컨베이어, 산업용 로봇.

        **2. 검사 주기**: 크레인/리프트/곤돌라(최초 3년, 이후 2년, 건설 현장은 6개월), 기타(최초 3년, 이후 2년, PSM 압력용기는 4년).

        **★ [최신 법령 반영]**: 파쇄기, 분쇄기, 혼합기, 식품 가공용 기계(제면기 등) 가동 중 덮개 개방 시 기계가 자동으로 정지하도록 **연동 장치(Interlock) 설치가 의무화**되었습니다.

        <br>

        **[ 54. 산업안전보건법 ]**

        **1. 안전보건관리책임자**: 산재 예방 계획 수립, 규정 작성, 교육, 작업 환경 측정, 건강 진단, 원인 조사 등 총괄 업무 수행.

        **2. 관리감독자**: 기계/설비 점검, 보호구 착용 지도, 산재 보고 및 응급 조치, 작업장 정리 정돈, 위험성 평가 유해·위험 요인 파악.

        **3. 유해위험방지계획서**: 전기 계약 용량 300kW 이상 13개 업종, 5개 특정 설비(용해로, 화학설비, 건조설비, 가스 집합, 국소배기).

        **4. PSM (공정안전보고서)**: 공정 안전 자료, 공정 위험 평가서, 안전 운전 계획, 비상 조치 계획.

        **★ [최신 KOSHA 기술지원규정 반영]**: 기존 KOSHA GUIDE는 법적 근거 명확화를 위해 **'KOSHA 기술지원규정'**으로 명칭이 변경되고 체계가 전면 개편되었습니다.

        <br>

        **[ 60. 밀폐공간 작업 ]**

        **1. 유해 공기 기준**: 산소 18~23.5%, 일산화탄소 30ppm 미만, 황화수소 10ppm 미만, 탄산가스 1.5% 미만.

        **2. 작업 전 확인 사항**: 산소 및 유해가스 농도 측정, 환기 실시, 보호구 착용, 감시인 배치.
        """)

# ------------------------------------------
# [탭 1] 빈출 핵심 테마
# ------------------------------------------
with tab1:
    st.markdown("**[Summary] 기계안전기술사 출제 빈도 Top 6**")
    
    with st.expander("Rank 1: 기계안전 일반 및 위험성평가"):
        st.write("- 피로파괴, 응력집중, 안전계수, Creep 현상")
        st.write("- 본질안전화 3원칙, Fail Safe, Fool Proof")
        st.write("- 위험성평가 절차 및 정량적 기법(FTA, ETA)")
        
    with st.expander("Rank 2: 양중기 및 운반기계"):
        st.write("- 크레인 방호장치 (과부하방지, 권과방지, 비상정지)")
        st.write("- 지게차 안정도 조건 및 헤드가드 기준")
        st.write("- 와이어로프 폐기 기준 및 안전계수")
        
    with st.expander("Rank 3: 압력용기 및 보일러"):
        st.write("- 보일러 이상현상 (프라이밍, 포밍, 캐리오버)")
        st.write("- 압력용기 안전설계 (원주방향/축방향 응력 계산)")
        st.write("- 펌프 이상현상 (Cavitation, Surging, 수격작용)")
        
    with st.expander("Rank 4: 용접 및 비파괴검사"):
        st.write("- 비파괴검사 비교 (PT, MT, UT, RT, AE, ECT)")
        st.write("- 용접 결함 (오버랩, 언더컷, 은점 등) 및 잔류응력 완화법")
        st.write("- 가스용접 위험성 (역류, 역화, 인화)")
        
    with st.expander("Rank 5: 공작기계 및 산업용 로봇"):
        st.write("- 프레스 방호장치 (양수조작식, 광전자식 안전거리 계산)")
        st.write("- 산업용 로봇 교시 작업 안전수칙 및 방호장치")
        st.write("- 연삭숫돌 파괴원인 및 덮개 노출각도")
        
    with st.expander("Rank 6: 안전보건법령 및 안전관리"):
        st.write("- 안전인증 및 안전검사 대상 기계·기구")
        st.write("- 공정안전보고서(PSM) 및 유해위험방지계획서")
        st.write("- 하인리히 재해예방 4원칙, 버드의 신연쇄성 이론")

# ------------------------------------------
# [탭 2] 랜덤 기출 풀이 및 AI 첨삭
# ------------------------------------------
with tab2:
    st.markdown("**[Test_A] 실전 모의고사 (서브노트 기반 기출문제)**")
    
    if st.button("Generate New Question", use_container_width=False):
        st.session_state['current_question'] = random.choice(QUESTIONS)
        st.session_state['ai_feedback'] = ""
        st.rerun()
        
    if st.session_state['current_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['current_question']}</div>", unsafe_allow_html=True)
        
        user_answer = st.text_area("Input Answer:", height=200, key="ans_real")
        
        if st.button("Submit for Review", use_container_width=False, key="btn_real"):
            if not user_answer.strip():
                st.warning("Please input data.")
            else:
                with st.spinner("Processing..."):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 기계안전기술사 출제 위원입니다.
                        문제: {st.session_state['current_question']}
                        수험생의 답변: {user_answer}
                        
                        [지시사항]
                        1. 수험생의 답변을 100점 만점 기준으로 채점하고 짧은 총평을 해주세요.
                        2. 누락된 핵심 법적 키워드나 공학적 개념을 추가하여 완벽한 모범 답안을 제시해주세요.
                        3. 답변 작성 시 제공된 기계안전 이론을 바탕으로 하되, **2026년 현재 기준 최신 산업안전보건법령(예: 분쇄기·파쇄기·혼합기·식품가공용기계 덮개 개방 시 연동장치 의무화 등)과 최신 KOSHA 기술지원규정 사항**을 반드시 반영하여 설명하세요.
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
                                      ("Admin", now, "[기출] " + st.session_state['current_question'], user_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
                        
        if st.session_state['ai_feedback']:
            st.markdown(f"<div class='ai-box'><b>[Review Result]</b><br><br>{st.session_state['ai_feedback']}</div>", unsafe_allow_html=True)

# ------------------------------------------
# [탭 3] AI 신출 모의고사 (기출 변형 문제)
# ------------------------------------------
with tab_new:
    st.markdown("**[Test_B] AI 기출 변형 신출 모의고사**")
    
    themes = list(THEME_PAST_QUESTIONS.keys())
    selected_theme = st.selectbox("Select Category:", themes)
    
    if st.button("Generate Modified Question", use_container_width=False):
        with st.spinner("Processing..."):
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
                1. 최신 법령 연계: 2026년 기준 최신 산안법 개정(식품가공용기계, 파쇄기 연동장치 등) 또는 최신 KOSHA 기술지원규정 개편 사항 엮기
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
                    st.error("API Error")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    if st.session_state['ai_new_question']:
        st.markdown(f"<div class='question-box'>Q. {st.session_state['ai_new_question']}</div>", unsafe_allow_html=True)
        
        user_new_answer = st.text_area("Input Answer:", height=200, key="ans_new")
        
        if st.button("Submit for Review", use_container_width=False, key="btn_new"):
            if not user_new_answer.strip():
                st.warning("Please input data.")
            else:
                with st.spinner("Processing..."):
                    try:
                        prompt = f"""
                        당신은 30년 경력의 기계안전기술사 출제 위원입니다.
                        문제: {st.session_state['ai_new_question']}
                        수험생의 답변: {user_new_answer}
                        
                        [지시사항]
                        1. 수험생의 답변을 100점 만점 기준으로 채점하고 짧은 총평을 해주세요.
                        2. 누락된 핵심 법적 키워드나 공학적 개념을 추가하여 완벽한 모범 답안을 제시해주세요.
                        3. 답변 작성 시 제공된 기계안전 이론을 바탕으로 하되, **2026년 현재 기준 최신 산업안전보건법령과 최신 KOSHA 기술지원규정 사항**을 반드시 반영하여 설명하세요.
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
                                      ("Admin", now, "[AI 신출] " + st.session_state['ai_new_question'], user_new_answer, feedback))
                            conn.commit()
                        else:
                            st.error(f"API Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
                        
        if st.session_state['ai_new_feedback']:
            st.markdown(f"<div class='ai-box'><b>[Review Result]</b><br><br>{st.session_state['ai_new_feedback']}</div>", unsafe_allow_html=True)

# ------------------------------------------
# [탭 4] 나의 오답 노트
# ------------------------------------------
with tab3:
    st.markdown("**[Log] Data Records**")
    
    c.execute("SELECT id, date, question, user_answer, ai_feedback FROM study_records WHERE user_id=? ORDER BY id DESC", ("Admin",))
    records = c.fetchall()
    
    if not records:
        st.write("No records found.")
    else:
        for record in records:
            r_id, date, q, ans, ai = record
            with st.expander(f"Record ID: {r_id} | Date: {date}"):
                st.markdown(f"**Q. {q}**")
                st.markdown(f"<div style='background-color:#f3f2f1; padding:15px; border:1px solid #d2d2d2; font-size:14px;'><b>User Input:</b><br>{ans}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#ffffff; padding:15px; border:1px solid #d2d2d2; margin-top:5px; font-size:14px;'><b>System Output:</b><br>{ai}</div>", unsafe_allow_html=True)
                
                if st.button("Delete Record", key=f"del_{r_id}"):
                    c.execute("DELETE FROM study_records WHERE id=?", (r_id,))
                    conn.commit()
                    st.rerun()

# ------------------------------------------
# [탭 5] 법령 및 KOSHA 가이드 외부 링크
# ------------------------------------------
with tab4:
    st.markdown("**[Ref_Link] External Resources (2026 Updated)**")
    st.write("최신 법령 및 KOSHA 기술지원규정 원문 링크입니다.")
    
    st.markdown("""
    <ul style="list-style-type: square; font-size: 15px; line-height: 2.0;">
        <li><a href="https://asdfg.kr" target="_blank" style="color: #107c41; text-decoration: none; font-weight: bold;">안전보건 법령 통합 검색 (asdfg.kr)</a></li>
        <li><a href="https://portal.kosha.or.kr/archive/resources/tech-support/guide/overview" target="_blank" style="color: #107c41; text-decoration: none; font-weight: bold;">KOSHA GUIDE (기술지원규정) 원문 검색 포털</a></li>
        <li><a href="https://oshri.kosha.or.kr/cms/resFileDownload.do?siteId=kosha&type=etc&fileName=%282024%EB%85%84%29%EA%B8%B0%EC%88%A0%EC%A7%80%EC%9B%90%EA%B7%9C%EC%A0%95%EA%B0%9C%ED%8E%B8%EC%97%90%EB%94%B0%EB%A5%B8%EC%97%B0%EA%B3%84%ED%91%9C%28%EA%B3%B5%EC%A7%80%EC%9A%A9%29.pdf" target="_blank" style="color: #107c41; text-decoration: none; font-weight: bold;">최신 KOSHA 기술지원규정 신·구 연계표 다운로드 (PDF)</a></li>
    </ul>
    """, unsafe_allow_html=True)

# ==========================================
# [푸터]
# ==========================================
st.markdown("""
<hr style="border-color: #d2d2d2; margin-top: 30px;">
<div style="text-align: right; color: #8a8886; font-size: 12px;">
    Confidential & Proprietary | Internal Use Only
</div>
""", unsafe_allow_html=True)
