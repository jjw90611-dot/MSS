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
# [CSS] 엑셀(Spreadsheet) 스타일의 무채색/직각 UI
# ==========================================
st.markdown("""
<style>
    /* 전체 배경 및 폰트 (맑은 고딕 등 기본 폰트 사용) */
    html, body, [class*="st-"], p, h1, h2, h3, h4, h5, h6, label, input, textarea, button, li, a, strong, b, div, span {
        font-family: 'Malgun Gothic', 'Arial', sans-serif !important;
        color: #000000 !important;
    }
    .stApp { background-color: #ffffff; }
    
    /* 입력창 (엑셀 셀 느낌) */
    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #ffffff !important; 
        border: 1px solid #a6a6a6 !important; 
        border-radius: 0px !important;
    }
    input, textarea { font-size: 13px !important; }
    
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
        font-size: 13px !important; 
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
        font-size: 12px; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ffffff !important; 
        border-top: 3px solid #107c41 !important; /* 엑셀 고유의 초록색 포인트 */
        font-weight: bold; 
    }

    /* Expander (표의 행 느낌) */
    [data-testid="stExpander"] { 
        background-color: #ffffff !important; 
        border: 1px solid #d2d2d2 !important; 
        border-radius: 0px !important; 
        margin-bottom: -1px !important; /* 테두리 겹침 처리 */
    }
    [data-testid="stExpander"] p, [data-testid="stExpander"] li { font-size: 12px !important; line-height: 1.5 !important; }

    /* 타이틀 및 텍스트 박스 단순화 */
    .excel-title { font-size: 18px; font-weight: bold; color: #333333; margin-bottom: 5px; border-bottom: 2px solid #107c41; padding-bottom: 5px; }
    .status-bar { background-color: #f3f2f1; border: 1px solid #d2d2d2; padding: 5px 10px; font-size: 12px; color: #333; margin-bottom: 15px; }
    .question-box { background-color: #ffffff; border: 1px solid #000000; padding: 10px; font-size: 13px; font-weight: bold; margin-bottom: 10px; }
    .ai-box { background-color: #f9f9f9; border: 1px dashed #8a8886; padding: 15px; font-size: 13px; margin-top: 10px; white-space: pre-wrap; }
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
# [탭 0] 핵심 서브노트 (제공된 문서 100% 원문 반영)
# ------------------------------------------
with tab_subnote:
    st.markdown("**[Raw Data] 기계안전기술사 핵심 서브노트 (2026년 기준 최신화)**")
    
    with st.expander("Row 1: 기계안전 일반 및 위험성평가"):
        st.markdown("""
        **[ 1. 피로 ]**
        1. 개요
        가. 기계,구조물, 그의 부품이 받는 하중은 일정한 정하중의 경우보다 주기적으로 변화하는 소위 반복하중이나 변동하중인 경우가 많음.
        나. 재료의 반복하중을 가하면 정하중의 경우보다도 휠씬 작은 하중으로 파괴됨
        다. 이 현상을 “재료의 파괴”라 한다.
        라. 반복하중을 받는 부재의 설계에 있어서 특히 주의해야 함.
        2. 피로파괴의 특성
        가. 피로한도·피로한계
        1) 어느 한계응력하에서는 아무리 많은 반복하중이 가해져도 피로현상이 발생하지 아니함
        2) 이 한계를 피로한도, 피로한계라 함.
        나. 피로에 의해 파괴 시 연성재료도 취성재료처럼 거의 변형없이 갑자기 파괴, 균열의 점진적 발생부와 급력파괴부를 뚜렷이 구별 가능함.
        3. 피로한도 영향인자 7가지
        가. 피로한도: 기계를 구성하는 금속재료가 반복적으로 굽힘하중을 받으면 허용하중보다 작은 하중에서도 파괴됨 →피로(Fatigue)라 함. 아무리 반복하여도 피로파괴가 일어나지 아니하는 응력의 한도를 “피로한도”라 함
        나. 피로한도에 영향을 주는 요소: 1) 노치 2) 치수효과 3) 표면거칠기 4) 부식 5) 반복하중 6) 압입가공 7) 온도
        4. 피로한도 향상 방안
        가. 노치효과: 노치 깊이를 얕게, 노치 반지름 R을 크게
        나. 치수효과: 지름을 되도록 작게, 치수효과 계수를 1.0으로
        다. 표면 거칠기: 강축의 경우 표면의 다듬질을 매끈하게 실시함.
        라. 온도: 온도의 상승으로 전위의 이동이 용이하게 되고 가공에 의한 경화가 쉽게 회복하여 연화되기 때문에
        마. 반복하중: 반복하중 중에서 굽힘하중을 가능한 한 피해야 함.(인장, 굽힘, 압축)
        바. 압입가공: 압입가공이나 때려박을 시 변형률을 작게
        사. 부식작용을 방지
        5. 결론
        가. 노치효과, 치수효과, 표면상황, 부식작업, 압입 등은 피로한도를 저하시킴
        나. 질화, 침탄, 고주파경화, 쇼트피닝, 샌드블라스트 등은 피로한도를 향상시킴
        다. 기계 또는 구조물 설계시 피로한도에 영향을 미치는 각종 인자에 대해 검토하고 허용응력 산출 시 기준강도를 피로한도보다 작게 하여야 한다.

        **[ 2. 위험성 평가 ]**
        1. 개요
        가. 위험성평가란 유해·위험요인을 파악하고
        나. 해당 유해·위험요인에 의한 부상 또는 질병의 발생가능성(빈도)과 중대성(강도)를 추정·결정하고
        다. 감소대책을 수립하여 실행하는 일련의 과정을 말한다.
        라. 순서는 자료수집 → 유해·위험요인파악 → 위험성 추정 → 위험성 결정→ 감소대책 수립 및 실시 → 기록의 순으로 실시함.
        2. 자료수집: 작업표준, 기계사양서, 공정흐름, 도급사업 혼재작업, 재해사례, 작업환경측정결과 등
        3. 유해·위험 요인 파악: 사업장 순회점검, 청취조사, 안전보건자료, 체크리스트 등
        4. 위험성 추정: 가능성과 중대성을 행렬, 곱하기, 더하기 등으로 산출. 최악의 상황에서 가장 큰 부상 추정.
        5. 위험성 결정: 추정한 위험성의 크기가 허용·가능한 범위인지 여부를 판단.
        6. 감소대책 수립 및 실시: 위험한 작업의 폐지·변경 → 공학적 대책 → 관리적 대책 → 개인용 보호구 착용 순으로 실시.
        7. 기록사항: 3년간 보존.
        8. 고려사항: 유해·위험요인 위치, 현재 안전대책, 발생빈도, 피해크기 등.
        9. 위험성평가의 의의: 안전사고 사전예방, 재해특성 예측, 쾌적한 작업환경 조성.
        10. 위험성평가 기법의 종류
        가. 정성적 평가: HAZOP(위험과 운전분석), PHA(예비위험분석 기법), What-If(사고예상 질문분석), Check-List
        나. 정량적 위험성평가: FTA(결함수 위험성 평가, 연역적), ETA(사건수 분석기법, 귀납적), CA(피해영향 분석)

        **[ 3. 본질 안전화 ]**
        1. 개요: 본질안전 방폭전기기계기구에서 나온 용어. 단락이나 단선 등이 발생하여도 외부 분위기에 착화되는 일이 없는 구조.
        2. 본질 안전화 3원칙
        가. 안전기능이 기계장치에 내장되어 있을 것 (예: 안전프레스, 교류아크용접기 자동전격방지기)
        나. Fool Proof: 인간이 실수를 하여도 안전장치가 설치되어 있어 사고나 재해로 연결되지 않는것 (예: 세탁기 뚜껑, 프레스 광전자식, 승강기 과부하방지)
        다. Fail Safe 기능을 가질 것: 시스템에 고장이 생겨도 어느 기간 동안은 정상기능이 유지되고 사고나 재해까지 발전되지 않는 기구.
        3. Fail Safe
        가. Fail Safe의 기능면 3단계
        1) Fail Passive - 부품이 고장나면 통상 기계는 정지하는 방향으로 이동
        2) Fail Active - 부품이 고장나면 기계는 경보를 울리는 가운데 짧은 시간 동안의 운전이 가능
        3) Fail Operational - 부품의 고장이 있어도 기계는 추후의 보수가 있을 때까지 안전한 기능을 유지하고 병렬계통 또는 대기여분 계통으로 유지
        나. Fail Safe 기구: 구조적 Fail Safe(다경로 하중구조, 분할 구조 등), 기능적 Fail Safe(기계적/전기적 Fail Safe, 증기보일러 안전변 복수설치 등)

        **[ 4. 안전계수 ]**
        1. 개요: 안전율은 응력계산 및 재료의 불균질 등에 대한 부정확을 보충하고 각 부품의 불충분한 안전율과 더불어 경제적 치수 결정에 중요함. 안전계수는 하중의 종류에 따라 결정되는 기초강도와 허용응력과의 비.
        2. 고려사항
        가. 기초강도: 정하중(극한강도), 반복하중(피로한도), 고온환경(Creep강도)
        나. 허용응력: 재료를 안전하게 사용할 수 있도록 허용할 수 있는 최대 응력
        다. 안전율 = 기초강도 / 허용응력
        3. 안전율 선정 시 고려사항: 재질 신뢰도, 하중종류, 응력계산 정확성, 공작 정밀도, 불연속부 유무, 열처리, 마모/부식 등.
        4. 결론: 일반적으로 정하중-3, 편하중-5, 교번하중-8, 충격하중-12의 안전율을 선택한다.

        **[ 8. 응력집중 ]**
        1. 개요: 기계부품의 Fillet부, 노치부, 홈, 구멍 등이 있으면 단면현상이 급격히 변하여 국부적으로 큰 응력이 발생. 이것을 응력집중이라 함.
        2. 응력집중계수: 최대 집중하중(응력) max와 평균응력 nom과의 비를 k로 표시. k = 형상계수 또는 응력집중계수.
        3. 응력집중계수의 특징: 재료의 치수와 상관없이 형상만으로 결정됨.
        4. 응력집중완화 대책: 단면변화의 완만화, 단면부 앞·뒤로 단면부 설치, 단면부분에 보강재 결합, 단면 변화부분을 강화시킴(쇼트피닝 등), 내부응력/잔류응력 제거.

        **[ 34. FMEA ]**
        1. 개요: 시스템 안전해석에 이용되는 전형적인 정성적이고 귀납적인 해석기법.
        2. 특징: 요소의 이상이나 고장에 시스템 또는 부수시스템에 미치는 영향을 고장의 형태(Modes)에 대응하여 자세하게 기재.
        3. 장·단점: 적은 노력으로 평가 가능, 단일 고장 형태 확인 가능. 단점은 동시에 두 개 이상의 요소 고장 해석 곤란, 운전자 실수 확인 안됨.
        4. 실시방법: Block Diagram 작성 → 부품 목록 작성 → 고장 중요도 구분 → 영향 조사 → 대책 강구.

        **[ 36. 기계설비의 안전화 ]**
        1. 개요: 외형, 구조, 기능, 작업, 보전상의 안전화에 대해 고려해야 함.
        2. 외형의 안전화: 가드의 설치, 별실 또는 구획된 장소에의 격리, 안전색채조절.
        3. 기능의 안전화: 소극적 대책(이상 시 기계 급정지), 적극적 대책(회로 개선 오작동 방지, Fail Safe + Fool Proof).
        4. 구조의 안전화: 재료의 결함, 설계상의 결함(강도계산 과오) 방지.
        5. 작업의 안전화: 핸들/레버 배치, 표시/디스플레이 합리적 고려, 쾌적한 환경 유지.
        6. 보전의 안전화: 보수용 통로 확보, 고장발견 용이성, 부품 호환성.

        **[ 37. 욕조곡선 ]**
        1. 개요: 기계고장율은 시간의 함수, 욕조곡선.
        2. 초기고장-감소형(DFR): 디버깅 기간, 번인기간. 예방대책으로 위험분석.
        3. 우발고장-일정형(CFR): 사용조건상의 고장, 고장율이 가장 낮다. 내용수명.
        4. 마모고장-증가형(IFR): 설비의 피로에 의해 생기는 고장. 정기진단(검사) 필요.

        **[ 38. 설비보전 ]**
        1. 개요: 설비의 최적상태의 유지와 지속적개선.
        2. 예방보전의 방법:
        가. 시간기준보전(TBM): 일정 주기로 점검, 검사, 보수, 교체.
        나. 상태기준보전(CBM): 설비의 상태를 기준으로 보전 시기 결정. 열화상태 정량적 파악.
        다. 적응보전(AP): 생산 상황이나 설비 노후정도 고려.
        3. 사후보전: 고장이 발생한 경우에 즉시 보전활동 수행.
        4. 보전작업에서의 안전화: 인터록, 표지, 사전보전계획 수립, 이중화 단계 적용.

        **[ 40. 불안전한 상태·행동 ]**
        1. 개요: 사고는 불안전한 행동(인적원인)과 불안전한 상태(물적원인)가 접촉되어 발생.
        2. 직접원인:
        가. 인적원인(불안전한 행동): 위험한 장소 접근, 안전장치 기능 제거, 복장 오사용, 기계 오사용 등.
        나. 물적원인(불안전한 상태): 작업장소 불량, 기계설비 결함, 방호조치 결함, 정리정돈 불량 등.
        3. 간접원인: 기술적 원인, 교육적 원인, 관리적 원인, 신체적 원인, 정신적 원인, 학교 교육적 원인.

        **[ 41. 재해예방의 4원칙 ]**
        1. 개요: 하인리히 산업안전의 원칙.
        2. 재해예방 4원칙: 손실우연의 원칙, 원인계기의 원칙, 예방가능의 원칙, 대책선정의 원칙.
        3. 안전대책(3E): 기술적 대책(Engineering), 교육적 대책(Education), 규제적 대책(Enforcement).

        **[ 42. 사고예방대책 기본원리 5단계 ]**
        1. 안전관리조직(Organization)
        2. 사실의 발견(Fact Finding)
        3. 평가분석(Analysis)
        4. 시정책의 선정(Selection of Remedy)
        5. 시정책의 적용(Application of Remedy)

        **[ 43. 연쇄 반응이론 ]**
        1. 하인리히의 연쇄성 이론: 도미노 이론. 330회 사고 중 중상/사망 1회, 경상 29회, 무상해 300회 (1:29:300).
        2. 버드의 신사고 연쇄성 이론: 4M에 기인한 기본원인, 경영자 통제관리 부족 강조. 641건 중 무상해 600건, 물적손해 30건, 인적재해 10건, 경상 1건 (1:10:30:600).

        **[ 44. Creep ]**
        1. 개요: 고온에서 일정하중을 장시간에 걸쳐 받게 방치해 두면 항복점이하의 일정한 응력에서도 시간의 경과에 따라 변형률이 급격히 증가하는 현상.
        2. Creep Curve: 1기(천이크리이프), 2기(정상Creep), 3기(가속Creep).

        **[ 48. 응력-변형률 선도 ]**
        1. 개요: 인장시험을 통해 결정.
        2. 비례한도와 후크의 법칙: Hooke의 법칙 (응력은 변형률에 비례).
        3. 탄성한도: 하중 제거 시 원래 상태로 돌아가는 한계.
        4. 항복점: 하중 증가 없이 재료가 신장되는 현상.
        5. 최종응력(인장강도): 최대응력.
        6. 파단응력: 파괴가 일어나는 점의 응력.

        **[ 49. 연성·취성파괴 ]**
        1. 취성파괴: 큰 소성변형 없이 균열 발생, 불안정 파괴 (유리).
        2. 연성파괴: 균일한 큰 소성변형 동반, Necking 발생 후 파괴.

        **[ 57. 동작경제의 3원칙 ]**
        1. 인간의 신체부위 사용에 관한 원칙: 양손 동시 시작/끝, 대칭 동작, 관성 이용.
        2. 작업장 배치에 관한 원칙: 도구/재료 지정 장소, 중력이동 상자 이용, 조명/작업대 높이 조절.
        3. 공구 및 기계설비의 설치와 사용에 관한 원칙: 2개 이상 기능 공구 사용, 레버/손바퀴 위치 최적화.

        **[ 58. Hazard, Risk, Peril ]**
        1. Hazard: 위험의 근원, 사고발생 가능성의 잠재적 요인 (예: 원유 Tank).
        2. Risk: 위험의 발생 가능성, 불확실성 (예: 원유 Tank의 폭발 가능성).
        3. Peril: 사고 그 자체, 우발적 사고 (예: 원유 Tank의 폭발).

        **[ 61. 매슬로우의 욕구 6단계설 ]**
        1. 생리적 욕구 → 안전에 대한 욕구 → 사회적 욕구(애정) → 인정의 욕구(명예) → 자아실현의 욕구(창조) → 자아초월의 욕구.
        2. 인간의 과실에 기인한 불안전한 행동은 안전의 욕구가 충족되지 않았기 때문.
        """)

    with st.expander("Row 2: 양중기 및 운반기계"):
        st.markdown("""
        **[ 5. 지게차 ]**
        1. 개요: 화물적재용 포크와 마스트를 갖춘 운반기계.
        2. 위험성: 물체의 낙하, 보행자 접촉, 차량의 전도.
        3. 구배가 있는 장소에서의 안전조건 (안정도 기준)
        - 하역작업 시 전후 안정도: 4% 이내 (5Ton 이상은 3.5% 이내)
        - 하역작업 시 좌우 안정도: 6% 이내
        - 주행 시 전후 안정도: 18% 이내
        - 주행 시 좌우 안정도: (15+1.1V)% 이내 (V=최고속도)
        4. 안전장치: 안전Belt, 전조등/후미등, 헤드가드(상부틀 개구부 16cm 미만, 좌식 0.903m 이상, 입식 1.88m 이상), 백레스트.
        5. 작업계획서: 작업장소 넓이/지형, 기계 종류/능력, 화물 종류/형상, 운반경로, 위험 예방방법.

        **[ 11. Wire Rope ]**
        1. 개요: 강선을 꼬아 스트랜드를 만들고 이를 다시 꼬아 심(Core)을 넣은 것.
        2. 꼬임방법:
        - 보통꼬임: 스트랜드와 소선 꼬임방향 반대. 킹크 잘 안생김.
        - 랭꼬임: 스트랜드와 소선 꼬임방향 동일. 내마모성 크고 유연성 커서 삭도용/광산용 사용.
        3. 안전계수: 근로자 탑승 10 이상, 화물 직접 지지 5 이상, 훅/샤클 3 이상, 기타 4 이상.
        4. 사용금지 기준: 이음매 있는 것, 한 꼬임에서 소선 수 10% 이상 절단, 공칭지름 7% 초과 감소, 꼬인 것, 심하게 변형/부식된 것, 열/전기충격 손상.
        5. 연결고정방법: 소켓(이음효율 최고), 팀블, 웨지, 아이스플라이스, 클립(직경 6배 이상 간격, 4개 이상).

        **[ 14. 크레인 ]**
        1. 개요: 동력을 사용하여 화물을 달아 올리고 상하, 전후, 좌우로 운반하는 기계.
        2. 안전장치:
        - 과부하방지장치: 정격하중 이상 시 자동 운반 중단.
        - 권과방지장치: 나사형, 캠형, 중추형, 레버형.
        - 후크해지장치: 와이어로프 벗겨짐 방지.
        - 레일 정지기구(Stopper), 충돌방지장치(광선/초음파, 리미트스위치).
        - 비상정지장치, Brake(전자브레이크, 전동유압압상, 밴드, 원판).

        **[ 16. 승강기 ]**
        1. 개요: 가이드레일을 따라 승강하는 운반구에 사람/화물 이동.
        2. 안전장치:
        - 과부하방지장치: 정격하중 1.1배 작동.
        - 비상정지장치: 정격속도 1.4배 작동 (순간정지식, 점진식).
        - 조속기(Governor): 정격속도 1.3배 이상 시 전원차단 및 브레이크 작동.
        - 출입문 연동장치, Final Limit S/W, 완충기(에너지 축적형, 에너지 분산형).
        3. 에스컬레이터 안전장치: 구동체인 안전장치, 핸드레일 인입구 스위치, 콤스위치, 스커드가드 안전스위치, 스텝체인 안전장치.

        **[ 28. Conveyor ]**
        1. 개요: 화물을 연속적으로 운반하는 기계.
        2. 종류: Roller, 스크류, 벨트, 체인, 진동, 유체 컨베이어.
        3. 안전장치: 비상정지장치, 역전방지장치 및 브레이크, 이탈방지장치.

        **[ 30. Tower Crane ]**
        1. 개요: 격자 구조 타워붐 위에 호이스트식 Jib 돌출시켜 화물 인양.
        2. Mast 지지 방식: 벽체지지, 와이어로프 지지(수평면 60도 이내, 4개소 이상).
        3. 작업중지 조건: 순간풍속 10m/sec 초과 시 설치/해체 중지, 15m/sec 초과 시 운전 중지.
        4. 운전자·신호수 의사전달: 정해진 한 사람의 신호자, 수직 인양, 와이어로프 팽팽해지면 일단 멈춤 확인.

        **[ 32. 양중기 ]**
        1. 종류: 크레인, 이동식 크레인, 리프트, 곤돌라, 승강기.
        2. 양중기 Brake: 기계브레이크, 와류브레이크.

        **[ 33. 리프트 ]**
        1. 종류: 건설용 리프트, 일반작업용 리프트, 이삿짐 운반용 리프트, 자동차 정비용 리프트.
        2. 방호장치: 비상정지장치, 권과방지장치, 과부하방지장치(1.1배), 출입문 연동장치, 낙하방지장치, 완충장치.
        3. 가설식 곤돌라 방호장치: 상/하한 권과방지장치, 조속기와 비상정지장치, 블록스토퍼, 수평 조절장치, 과부하 방지장치.

        **[ 45. 고소작업대 ]**
        1. 개요: 작업대, 연장구조물, 차대로 구성.
        2. 안전대책: 허용 작업반경 초과 금지, 아웃트리거 확실한 설치, 작업대 가장 낮게 하강 후 이동, 안전난간 설치, 과상승방지장치 설치.
        3. 방호조치: 와이어로프/체인 안전율 5 이상, 정격하중 표시, 끼임/충돌 예방 가드.
        """)

    with st.expander("Row 3: 기계설비 및 공작기계"):
        st.markdown("""
        **[ 13. 방호원리, 방호장치 ]**
        1. 방호원리: 위험제거, 차단, 덮어씌움, 위험에의 적응.
        2. 방호장치: 격리형(완전격리, 덮개, 방책), 위치제한형(양수조작식), 접근거부형(수인식, 손쳐내기식), 접근반응형(광전자식), 포집형, 감지형.

        **[ 15. 프레스 ]**
        1. 개요: 동력에 의해 금형을 두고 금속 압축/절단 조형.
        2. 안전기준: 1행정 1정지기구, 급정지기구, 비상정지장치, 미동기구, 안전 Block, 전환 스위치.
        3. 방호장치 종류:
        - 양수조작식: 동시누름 0.5초 이내, 내측 최단거리 300mm 이상.
        - 가드식: 닫지 않으면 작동 불가.
        - 광전자식: 안전거리 D = 1.6 × (Te + Ts) [mm].
        - 손쳐내기식, 수인식.
        4. No-Hand in die Type vs Hand in Type: 자동송급/배출장치 도입.

        **[ 25. 둥근톱기계 ]**
        1. 재해유형: 절단점 접촉, 가공재 반발, 소음, 목분진.
        2. 방호장치:
        - 톱날접촉예방장치: 가동식, 고정식 덮개.
        - 반발예방장치: 분할날(두께 1.1배 이상, 톱날과 거리 12mm 이내), 반발방지발톱.

        **[ 26. 위험점 ]**
        1. 협착점: 왕복운동 공작부와 고정부 사이 (프레스).
        2. 끼임점: 고정부와 회전하는 동작부 사이 (연삭숫돌과 지지대).
        3. 절단점: 회전하는 운동부 자체 (밀링 커터, 둥근톱).
        4. 물림점: 서로 반대방향 맞물려 회전 (롤러기, 기어).
        5. 접선물림점: 회전하는 부분이 접선방향으로 물려들어감 (체인과 스프로킷, V벨트).
        6. 회전말림점: 회전하는 축 등에 의복 말려감 (축, 드릴).

        **[ 29. 소성가공 ]**
        1. 개요: 재료의 소성변형을 이용하여 목적 형상 획득.
        2. 종류: 냉간가공(재결정온도 이하, 가공경화), 열간가공(재결정온도 이상, 적열취성 주의).
        3. 가공형식: 단조, 압연, 인발, 압출, 전조가공, 프레스 가공.
        4. Spring Back: 굽힘가공 후 탄성변형 복귀 현상. 경질일수록, 얇을수록 큼.

        **[ 31. 산업용 로봇 ]**
        1. 안전기능: 비상정지장치, 교시상태 전환 시 속도 자동 감소.
        2. 교시작업 확인사항: 조작방법/순서, 매니퓰레이터 속도, 2인 이상 신호방법, 이상 시 조치.
        3. 방호장치: Fail-Safe 기능, 동력차단장치, 비상정지장치, 방책(1.8m 이상), 안전매트, 광전자식 방호장치.

        **[ 35. 연삭기 재해 & 연삭숫돌 ]**
        1. 파괴원인: 규정속도 초과, 균열, 플랜지 직경 불량, 측면 사용, 진동 발생.
        2. 덮개 노출각도: 탁상용(90도 이내), 휴대용/스윙(180도 이내), 평면(150도 이내).
        3. 작업받침대(3mm 이내), 보호쉴드(3~10mm).
        4. 연삭숫돌 3요소: 입자, 결합체, 기공. 5인자: 입자재료, 입도, 경도(결합도), 조직, 결합제.
        5. 자생작용: 마멸 → 파쇄 → 탈락 → 생성. (드레싱: 절삭성 회복, 트루잉: 형상 수정).

        **[ 50. 풀림방지 ]**
        1. 와셔: 스프링 와셔, 이붙이 와셔, 구름베어링 와셔, 혀붙이 와셔.
        2. 너트: 홈붙이 너트 및 분할핀, 이중너트, 특수너트.
        3. 기타: 와이어 고정, 용접, 접착제.

        **[ 51. Roller기 ]**
        1. 급정지장치: 손 조작식(1.8m 이내), 복부 조작식(0.8~1.1m), 무릎 조작식(0.4~0.6m).
        2. 급정지거리: 표면속도 30m/min 미만(원주의 1/3 이내), 30m/min 이상(원주의 1/2.5 이내).

        **[ 52. Guard ]**
        1. 종류: 고정가드, 조정가드, 연동가드(가드 닫히기 전 기계작동 불가), 자동가드, 방호울.

        **[ 55. 축설계시 고려사항 ]**
        1. 강도, 변형(처짐, 비틀림), 진동(위험속도 25% 이상 이격), 열응력, 부식 고려.

        **[ 62. 표면경화법 ]**
        1. 화학적: 침탄법(저탄소강 표면 탄소 침투), 질화법(암모니아 가스, 변형 적음).
        2. 물리적: Hard Facing, 방전표면, Shot Peening, 고주파경화법, 화염경화법.
        """)

    with st.expander("Row 4: 보일러, 압력용기 및 펌프"):
        st.markdown("""
        **[ 12. Boiler 장애요인 ]**
        1. 캐리오버(Carry Over): 수면의 물방울이 증기와 함께 나가는 현상. (원인: 고수위, 과부하, 관수 농축)
        2. 프라이밍(Priming): 물방울이 튀어 오르는 현상.
        3. 포밍(Foaming): 다량의 거품 발생.
        4. 보일러 폭발방지: 고저수위 조절장치, 압력방출장치(안전밸브), 압력제한 스위치.
        5. 역화(Back Fire): 미연소 불꽃이 연료 공급방향으로 향하는 현상. (방지: 점화 전 환기, 공기 먼저 공급)

        **[ 27. 압력용기 ]**
        1. 안전설계: 원주방향 응력이 축방향 응력의 2배이므로, 두께 결정 시 원주방향 응력 기준 계산.
        2. 파열판 설치조건: 반응폭주 급격한 압력상승, 독성물질 누출 우려, 안전밸브에 이상물질 누적 우려 시. (안전밸브와 직렬/병렬 설치)
        3. 갑종/을종: 갑종(설계압력 0.2MPa 이상 화학공정 용기, 1MPa 초과 공기/질소 탱크), 을종(갑종 제외).
        4. 주요 구조부: 동체(Shell), 경판(Head), 관판(Tube Sheet), 노즐 및 플랜지.
        5. 방호장치: 안전밸브, 긴급차단밸브, 파열판, 통기밸브, 화염방지기.

        **[ 46. Pump ]**
        1. 캐비테이션(Cavitation): 유속 증가로 압력이 포화증기압보다 낮아져 기포 발생. 진동/소음 및 침식 유발. (방지: 흡입관 짧게, 회전수 감소)
        2. 서징(Surging): 압력계기 눈금이 주기적으로 크게 흔들리는 맥동 현상. (방지: 우하향 H-Q 곡선 펌프 사용, 배관 내 공기 제거)
        3. 수격작용(Water Hammering): 밸브 급개폐 시 유속 변화로 인한 압력 상승. (방지: 서지탱크 설치, 플라이휠 설치, 밸브 서서히 개폐)
        4. 배관 Schedule No.: P(배관압력) / S(허용응력) × 10.

        **[ 53. 부식 ]**
        1. 종류: 전면부식, 국부부식(이종금속접촉, 전식, 틈새부식).
        2. 부식피로: 부식 분위기에서 반복응력 받을 때 발생.
        3. 응력부식균열(SCC): 인장응력과 부식환경 복합 작용.
        4. 방지대책: 재료 선정, 부식억제제, 음극방식(희생양극법, 외부전원법), 표면 코팅.
        """)

    with st.expander("Row 5: 용접 및 비파괴검사"):
        st.markdown("""
        **[ 6. 비파괴검사 ]**
        1. PT (침투): 표면 결함, 비자성체 가능, 저렴 / 내부결함 불가.
        2. MT (자분): 표면 및 직하 결함, 강자성체만 가능, PT보다 미세결함 검출.
        3. UT (초음파): 내부 결함(체적), 두꺼운 재질 가능 / 숙련도 요구, 방향성 민감.
        4. RT (방사선): 내부 결함, 영구기록 보존 / 방사선 위험, 양면 접근 필요.
        5. AE (음향방출): 동적 거동 평가, 실시간 모니터링 가능.
        6. ECT (와전류): 표면 결함, 고속/자동화 가능, 전도체만 가능.

        **[ 7. 용접부 기계 파괴시험 ]**
        1. 기계적 시험: 인장, 굽힘, 경도, 충격, 피로시험.
        2. 화학적 시험: 화학시험, 부식시험, 수소시험.
        3. 금속학적 시험: 파면시험, 매크로/마이크로 조직시험.

        **[ 17. 자동전격방지기 ]**
        1. 목적: 아크용접 시 무부하 전압을 25V 이하로 낮추어 감전 방지.
        2. 작동조건: 2차 무부하 전압 25V 이하, 시동감도 500옴, 지동시간 1초 이내.

        **[ 18. 아세틸렌 가스 용접 ]**
        1. 역류: 산소가 아세틸렌 도관으로 흘러감.
        2. 역화: 불꽃이 토치 끝에서 소리를 내며 꺼지거나 들어감.
        3. 인화: 불꽃이 혼합실까지 밀려들어가는 현상.

        **[ 19. Arc 용접 ]**
        1. 재해: 흄(Fume, 국소배기장치 필요), 화상, 감전, 화재/폭발.
        2. 탄산가스 아크용접: 기공 적음, 저렴 / 비드 외관 거침.
        3. TIG vs MIG: TIG(텅스텐 전극, 비소모성), MIG(소모성 와이어 전극).

        **[ 20. 수소가 강에 영향 ]**
        1. 은점(Fish Eye): 수소 기공으로부터 발생되는 수소 취화.
        2. 지연균열(저온균열): 용접 완료 후 수일 지나서 나타남. 저수소계 용접봉 사용 필요.

        **[ 22. 용접잔류응력 ]**
        1. 발생: 용융금속 응고 시 부피 수축으로 발생.
        2. 완화법: 응력제거 소둔(Annealing), 노내응력 제거, 국부응력 제거, 저온응력 완화, 기계적 완화, 피이닝(Peening).

        **[ 23. 용접부 결함 ]**
        1. 언더컷: 용접전류 과다, 아크 길 때.
        2. 오버랩: 용접전류 과소, 속도 느릴 때.
        3. 용입불량: 홈 각도 좁을 때, 전류 낮을 때.

        **[ 24. 아크용접봉 피복제 ]**
        1. 역할: 산화/질화 방지, 아크 안정, 슬래그 생성(급냉 방지), 탈산/정련, 합금원소 보충.
        """)

    with st.expander("Row 6: 안전보건법령 및 안전관리"):
        st.markdown("""
        **[ 9. 안전검사 ]**
        1. 대상 기계·기구: 프레스, 전단기, 크레인, 리프트, 압력용기, 곤돌라, 국소배기장치, 원심기, 화학설비, 건조설비, 롤러기, 사출성형기, 고소작업대, 컨베이어, 산업용 로봇.
        2. 검사주기: 크레인/리프트/곤돌라(최초 3년, 이후 2년, 건설현장 6개월), 기타(최초 3년, 이후 2년, PSM 압력용기는 4년).
        **★ [최신 법령 반영]**: 파쇄기, 분쇄기, 혼합기, 식품가공용기계(제면기 등) 가동 중 덮개 개방 시 기계가 자동으로 정지하도록 **연동장치(Interlock) 설치 의무화** 추가.

        **[ 10. 안전인증 ]**
        1. 심사종류: 서면심사, 기술능력 및 생산체계 심사, 제품심사, 확인심사.
        2. 대상 기계·기구: 프레스, 전단기, 절곡기, 크레인, 리프트, 압력용기, 롤러기, 사출성형기, 고소작업대, 곤돌라, 기계톱(이동식).

        **[ 39. 재해율 ]**
        1. 도수율(빈도율): (재해건수 / 연근로시간) × 1,000,000
        2. 강도율: (근로손실일수 / 연근로시간) × 1,000
        3. 연천인율: (재해자수 / 연평균근로자수) × 1,000 (도수율 × 2.4)
        4. 안전성 비교(STS): 과거와 현재 안전성적 비교.

        **[ 47. 산재발생 시 조치사항 ]**
        1. 긴급조치: 기계 정지 → 피해자 구조/응급조치 → 관계자 통보 → 2차 재해 예방 → 현장 보존.
        2. 재해조사 및 대책수립.

        **[ 54. 산업안전보건법 ]**
        1. 안전보건관리책임자: 산재예방계획 수립, 규정 작성, 교육, 작업환경측정, 건강진단, 원인조사 등 총괄.
        2. 관리감독자: 기계/설비 점검, 보호구 착용 지도, 산재 보고 및 응급조치, 작업장 정리정돈, 위험성평가 유해위험요인 파악.
        3. 유해위험방지계획서: 전기 계약용량 300kW 이상 13개 업종, 5개 특정설비(용해로, 화학설비, 건조설비, 가스집합, 국소배기).
        4. PSM (공정안전보고서): 공정안전자료, 공정위험평가서, 안전운전계획, 비상조치계획.
        **★ [최신 KOSHA 기술지원규정 반영]**: 기존 KOSHA GUIDE는 법적 근거 명확화를 위해 **'KOSHA 기술지원규정'**으로 명칭이 변경되고 체계가 전면 개편됨.

        **[ 56. 제조물 책임법 (PL법) ]**
        1. 결함의 분류: 설계상의 결함, 제조상의 결함, 표시상의 결함(경고 누락).

        **[ 59. 개선 계획 ]**
        1. 대상: 산업재해율이 동종업종 평균보다 높은 사업장, 중대재해 발생 사업장 등.

        **[ 60. 밀폐공간 작업 ]**
        1. 유해공기 기준: 산소 18~23.5%, 일산화탄소 30ppm 미만, 황화수소 10ppm 미만, 탄산가스 1.5% 미만.
        2. 작업 전 확인: 산소/유해가스 농도 측정, 환기, 보호구 착용, 감시인 배치.
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
                st.markdown(f"<div style='background-color:#f3f2f1; padding:10px; border:1px solid #d2d2d2;'><b>User Input:</b><br>{ans}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#ffffff; padding:10px; border:1px solid #d2d2d2; margin-top:5px;'><b>System Output:</b><br>{ai}</div>", unsafe_allow_html=True)
                
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
    <ul style="list-style-type: square; font-size: 13px;">
        <li><a href="https://asdfg.kr" target="_blank" style="color: #107c41; text-decoration: none; font-weight: bold;">안전보건 법령 통합 검색 (asdfg.kr)</a></li>
        <li style="margin-top: 10px;"><a href="https://oshri.kosha.or.kr/cms/resFileDownload.do?siteId=kosha&type=etc&fileName=%282024%EB%85%84%29%EA%B8%B0%EC%88%A0%EC%A7%80%EC%9B%90%EA%B7%9C%EC%A0%95%EA%B0%9C%ED%8E%B8%EC%97%90%EB%94%B0%EB%A5%B8%EC%97%B0%EA%B3%84%ED%91%9C%28%EA%B3%B5%EC%A7%80%EC%9A%A9%29.pdf" target="_blank" style="color: #107c41; text-decoration: none; font-weight: bold;">최신 KOSHA 기술지원규정 신·구 연계표 다운로드 (PDF)</a></li>
    </ul>
    """, unsafe_allow_html=True)

# ==========================================
# [푸터]
# ==========================================
st.markdown("""
<hr style="border-color: #d2d2d2; margin-top: 30px;">
<div style="text-align: right; color: #8a8886; font-size: 11px;">
    Confidential & Proprietary | Internal Use Only
</div>
""", unsafe_allow_html=True)
