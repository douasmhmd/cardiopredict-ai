"""Global healthcare-grade theme CSS for MedPredict AI."""

# Injected once after st.set_page_config()
CSS_STRING = """
<style>
/* ===== GLOBAL ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Arabic:wght@400;600;700&display=swap');

.stApp {
    background: linear-gradient(180deg, #F0FDFA 0%, #ECFEFF 100%) !important;
    font-family: 'Inter', 'Noto Sans Arabic', sans-serif !important;
}

.block-container {
    padding-top: 1rem !important;
}

.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
    background-color: transparent !important;
}

/* ===== INFO / WARNING / SUCCESS / ERROR BOXES ===== */
.stAlert,
[data-testid="stAlert"],
[data-testid="stAlertContainer"],
div[data-baseweb="notification"] {
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: none !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    margin: 16px 0 !important;
}

.stAlert *,
[data-testid="stAlert"] *,
[data-testid="stAlertContainer"] *,
div[data-baseweb="notification"] * {
    color: #0F172A !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
}

.stAlert[kind="info"],
[data-testid="stAlert"][kind="info"],
div[data-testid="stAlertContainer"][kind="info"] {
    background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%) !important;
    border-left: 4px solid #14B8A6 !important;
}

.stAlert[kind="info"] *,
[data-testid="stAlert"][kind="info"] * {
    color: #0F766E !important;
    font-weight: 600 !important;
}

.stAlert[kind="warning"],
[data-testid="stAlert"][kind="warning"] {
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%) !important;
    border-left: 4px solid #F59E0B !important;
}

.stAlert[kind="warning"] *,
[data-testid="stAlert"][kind="warning"] * {
    color: #92400E !important;
    font-weight: 600 !important;
}

.stAlert[kind="success"],
[data-testid="stAlert"][kind="success"] {
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%) !important;
    border-left: 4px solid #16A34A !important;
}

.stAlert[kind="success"] *,
[data-testid="stAlert"][kind="success"] * {
    color: #166534 !important;
    font-weight: 600 !important;
}

.stAlert[kind="error"],
[data-testid="stAlert"][kind="error"] {
    background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%) !important;
    border-left: 4px solid #DC2626 !important;
}

.stAlert[kind="error"] *,
[data-testid="stAlert"][kind="error"] * {
    color: #991B1B !important;
    font-weight: 600 !important;
}

.stAlert svg,
[data-testid="stAlert"] svg {
    opacity: 1 !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F766E 0%, #115E59 40%, #134E4A 100%) !important;
    border-right: 1px solid rgba(15, 118, 110, 0.2) !important;
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.04) !important;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
}

[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: white !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    opacity: 0.9 !important;
    margin-top: 20px !important;
    margin-bottom: 12px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.12) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 14px 20px !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(12px) !important;
    font-size: 14px !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.22) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.12) !important;
    margin: 24px 0 !important;
}

[data-testid="stSidebar"] input[type="text"] {
    background: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}

[data-testid="stSidebar"] input[type="text"]::placeholder {
    color: rgba(255, 255, 255, 0.5) !important;
}

[data-testid="stSidebar"] input[type="text"]:focus {
    border-color: #14B8A6 !important;
    box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.25) !important;
    outline: none !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 2px dashed rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255, 255, 255, 0.5) !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: white !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: rgba(255, 255, 255, 0.95) !important;
    padding: 6px 12px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
    font-size: 13px !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stSidebar"] .stRadio > div {
    gap: 4px !important;
}

[data-testid="stSidebar"] .stRadio > div > label {
    padding: 8px 16px !important;
    border-radius: 20px !important;
    transition: all 0.2s ease !important;
    font-size: 13px !important;
}

[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {
    background: rgba(255,255,255,0.2) !important;
}

[data-testid="stSidebar"] .stDownloadButton > button {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] .stDownloadButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
}

[data-testid="stSidebar"] .status-badge.ready {
    color: #16A34A !important;
}
[data-testid="stSidebar"] .status-badge.training {
    color: #F59E0B !important;
}
[data-testid="stSidebar"] .status-badge.not-ready {
    color: rgba(255,255,255,0.9) !important;
}
[data-testid="stSidebar"] .logo-text,
[data-testid="stSidebar"] .logo-icon {
    color: white !important;
}

/* ===== MAIN HEADER ===== */
h1 {
    color: #0F766E !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 4px !important;
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #64748B !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin-bottom: 24px !important;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    background: white !important;
    border-radius: 18px !important;
    padding: 22px 28px !important;
    margin: 14px 0 !important;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.05),
        0 4px 12px rgba(15, 118, 110, 0.04) !important;
    border: 1px solid rgba(15, 118, 110, 0.08) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatMessage"]:hover {
    box-shadow:
        0 2px 6px rgba(0, 0, 0, 0.06),
        0 8px 16px rgba(15, 118, 110, 0.08) !important;
}

[data-testid="stChatMessage"] * {
    color: #0F172A !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] em {
    color: #0F172A !important;
}

[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] b {
    color: #0F766E !important;
    font-weight: 700 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    border-left: 4px solid #14B8A6 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #F0FDFA 0%, #ECFEFF 100%) !important;
    border-left: 4px solid #0F766E !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
    color: #0F172A !important;
}

[data-testid="stChatInput"] {
    background: white !important;
    border: 2px solid rgba(15, 118, 110, 0.15) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    box-shadow: 0 2px 8px rgba(15, 118, 110, 0.06) !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #14B8A6 !important;
    box-shadow:
        0 0 0 4px rgba(20, 184, 166, 0.12),
        0 4px 12px rgba(15, 118, 110, 0.1) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #0F172A !important;
    font-size: 14px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #94A3B8 !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatInput"] button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3) !important;
}

/* Bottom chat dock — remove dark band (stChatInput keeps white card style above) */
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {
    background-color: #F0FDFA !important;
    border-top: 1px solid rgba(15, 118, 110, 0.1) !important;
}

.stChatInputContainer,
div[data-testid="stVerticalBlock"]:has([data-testid="stChatInput"]) {
    background-color: #F0FDFA !important;
}

footer, header {
    background-color: transparent !important;
}

/* Voice recorder — primary-style controls */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 20px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 16px rgba(15, 118, 110, 0.4) !important;
}

@keyframes recording-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7); }
    50% { box-shadow: 0 0 0 12px rgba(220, 38, 38, 0); }
}

.recording-active {
    animation: recording-pulse 1.5s infinite;
    background: linear-gradient(135deg, #DC2626 0%, #EF4444 100%) !important;
}

.voice-hint {
    background: rgba(20, 184, 166, 0.08);
    border-left: 3px solid #14B8A6;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    color: #0F766E;
    margin: 8px 0;
}

/* Typing indicator (assistant thinking) */
.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 8px 0;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: #14B8A6;
    border-radius: 50%;
    animation: typing-bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-8px); opacity: 1; }
}

/* ===== TABS ===== */
.stTabs {
    margin-top: 24px;
}

.stTabs [data-baseweb="tab-list"] {
    background: white !important;
    border-radius: 14px !important;
    padding: 6px !important;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.04),
        0 1px 2px rgba(0, 0, 0, 0.02) !important;
    gap: 4px !important;
    border: 1px solid rgba(15, 118, 110, 0.08) !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #64748B !important;
    padding: 12px 20px !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #F0FDFA !important;
    color: #0F766E !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(15, 118, 110, 0.3) !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* Tab body must stay visible (some Streamlit + chat layouts collapse empty panels) */
[data-baseweb="tab-panel"],
section[role="tabpanel"] {
    min-height: 120px !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* ===== METRIC CARDS ===== */
[data-testid="stMetric"] {
    background: white !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    border-top: 3px solid #14B8A6 !important;
}

[data-testid="stMetricLabel"] {
    color: #64748B !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

[data-testid="stMetricValue"] {
    color: #0F172A !important;
    font-weight: 800 !important;
    font-size: 28px !important;
}

/* ===== DATAFRAMES / TABLES ===== */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.04),
        0 4px 12px rgba(15, 118, 110, 0.04) !important;
    border: 1px solid rgba(15, 118, 110, 0.08) !important;
}

[data-testid="stDataFrame"] thead {
    background: linear-gradient(135deg, #0F766E 0%, #115E59 100%) !important;
}

[data-testid="stDataFrame"] thead th {
    color: white !important;
    font-weight: 700 !important;
    padding: 14px !important;
}

/* ===== MAIN AREA BUTTONS ===== */
.stButton > button {
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 28px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow:
        0 1px 3px rgba(15, 118, 110, 0.1),
        0 2px 8px rgba(15, 118, 110, 0.15) !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 4px 12px rgba(15, 118, 110, 0.15),
        0 8px 20px rgba(15, 118, 110, 0.2) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    background: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    color: #0F172A !important;
}

/* ===== SPINNER ===== */
.stSpinner > div {
    border-top-color: #14B8A6 !important;
}

/* ===== DIVIDER ===== */
hr {
    border-color: rgba(15, 118, 110, 0.1) !important;
}

/* ===== PLOTLY CHARTS ===== */
.js-plotly-plot {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #F0FDFA;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #14B8A6 0%, #0F766E 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #0D9488 0%, #0F766E 100%);
}

/* ===== CUSTOM COMPONENTS ===== */
.risk-badge-high {
    background: #FEE2E2;
    color: #DC2626;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    display: inline-block;
    animation: pulse-risk 2s infinite;
    border: 1px solid rgba(220, 38, 38, 0.2);
}

.risk-badge-medium {
    background: #FEF3C7;
    color: #D97706;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    display: inline-block;
    border: 1px solid rgba(217, 119, 6, 0.2);
}

.risk-badge-low {
    background: #DCFCE7;
    color: #16A34A;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 13px;
    display: inline-block;
    border: 1px solid rgba(22, 163, 74, 0.2);
}

@keyframes pulse-risk {
    0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.3); }
    70% { box-shadow: 0 0 0 8px rgba(220, 38, 38, 0); }
    100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
}

.hero-container {
    background: linear-gradient(135deg, #0F766E 0%, #0D9488 50%, #14B8A6 100%);
    border-radius: 20px;
    padding: 48px 40px;
    color: white;
    text-align: center;
    margin: 0 0 32px 0;
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}

.hero-container::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: -10%;
    width: 300px;
    height: 300px;
    background: rgba(255,255,255,0.03);
    border-radius: 50%;
}

.hero-container h2 {
    font-size: 32px;
    font-weight: 800;
    margin: 0 0 8px 0;
    color: white;
    position: relative;
    z-index: 1;
}

.hero-container p {
    font-size: 16px;
    opacity: 0.9;
    margin: 0 0 32px 0;
    position: relative;
    z-index: 1;
}

.hero-stats {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}

.hero-stat {
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 16px;
    padding: 24px 20px;
    flex: 1;
    max-width: 220px;
    min-width: 160px;
}

.hero-stat .number {
    font-size: 24px;
    font-weight: 800;
    color: white;
    margin-bottom: 4px;
}

.hero-stat .label {
    font-size: 12px;
    color: rgba(255,255,255,0.8);
    line-height: 1.3;
}

.winner-card {
    background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
    border: 2px solid #14B8A6;
    border-radius: 16px;
    padding: 24px 32px;
    text-align: center;
    margin: 16px 0;
}

.winner-card .trophy {
    font-size: 40px;
    margin-bottom: 8px;
}

.winner-card .model-name {
    font-size: 22px;
    font-weight: 800;
    color: #0F766E;
    margin-bottom: 4px;
}

.winner-card .accuracy {
    font-size: 36px;
    font-weight: 800;
    color: #0F766E;
}

.winner-card .accuracy-label {
    font-size: 14px;
    color: #64748B;
}

.risk-summary {
    display: flex;
    gap: 16px;
    margin: 16px 0;
    flex-wrap: wrap;
}

.risk-summary-card {
    flex: 1;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    min-width: 140px;
}

.risk-summary-card.high {
    background: #FEE2E2;
    border: 1px solid rgba(220, 38, 38, 0.15);
}

.risk-summary-card.medium {
    background: #FEF3C7;
    border: 1px solid rgba(217, 119, 6, 0.15);
}

.risk-summary-card.low {
    background: #DCFCE7;
    border: 1px solid rgba(22, 163, 74, 0.15);
}

.risk-summary-card .count {
    font-size: 36px;
    font-weight: 800;
}

.risk-summary-card.high .count { color: #DC2626; }
.risk-summary-card.medium .count { color: #D97706; }
.risk-summary-card.low .count { color: #16A34A; }

.risk-summary-card .risk-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 4px;
}

.patient-row {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
    border-left: 4px solid transparent;
}

.patient-row:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}

.patient-row.high { border-left-color: #DC2626; }
.patient-row.medium { border-left-color: #F59E0B; }
.patient-row.low { border-left-color: #16A34A; }

.logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
}

.logo-icon {
    width: 36px;
    height: 36px;
    background: rgba(255,255,255,0.15);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.logo-text {
    font-size: 20px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.02em;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.status-badge.ready {
    background: rgba(22, 163, 74, 0.15);
    color: #16A34A;
}

.status-badge.training {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    animation: pulse-status 1.5s infinite;
}

.status-badge.not-ready {
    background: rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.85);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.status-dot.ready { background: #16A34A; }
.status-dot.training { background: #F59E0B; }
.status-dot.not-ready { background: rgba(255,255,255,0.4); }

@keyframes pulse-status {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ===== CardioPredict — patient cards & hero metrics ===== */
.patient-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 5px solid #16A34A;
    transition: all 0.2s ease;
}
.patient-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}
.patient-card.high {
    border-left-color: #DC2626;
    animation: critical-pulse-card 2s infinite;
    background: linear-gradient(90deg, #FEF2F2 0%, white 10%);
}
.patient-card.medium {
    border-left-color: #F59E0B;
    background: linear-gradient(90deg, #FFFBEB 0%, white 10%);
}
.patient-card.low { border-left-color: #16A34A; }

@keyframes critical-pulse-card {
    0%, 100% { box-shadow: 0 1px 3px rgba(220, 38, 38, 0.1); }
    50% { box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3); }
}

.patient-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.patient-id { font-weight: 700; color: #0F172A; font-size: 16px; }
.patient-meta { color: #64748B; font-size: 13px; margin-bottom: 16px; }
.patient-vitals {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    padding: 12px;
    background: #F8FAFC;
    border-radius: 12px;
    margin-bottom: 12px;
}
.vital { text-align: center; }
.vital-icon { font-size: 18px; display: block; }
.vital-value { font-weight: 700; color: #0F172A; font-size: 15px; display: block; }
.vital-label { font-size: 11px; color: #64748B; text-transform: uppercase; }
.patient-footer { font-size: 12px; color: #94A3B8; }

.risk-badge-high {
    background: #FEE2E2; color: #DC2626; padding: 4px 10px; border-radius: 12px;
    font-weight: 700; font-size: 13px;
}
.risk-badge-medium {
    background: #FEF3C7; color: #D97706; padding: 4px 10px; border-radius: 12px;
    font-weight: 700; font-size: 13px;
}
.risk-badge-low {
    background: #DCFCE7; color: #16A34A; padding: 4px 10px; border-radius: 12px;
    font-weight: 700; font-size: 13px;
}

.metric-hero {
    background: white;
    border-radius: 16px;
    padding: 28px 24px;
    text-align: center;
    box-shadow:
        0 1px 3px rgba(0, 0, 0, 0.04),
        0 4px 12px rgba(15, 118, 110, 0.06);
    border-top: 4px solid #14B8A6;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.03) 0%, transparent 100%);
    pointer-events: none;
}

.metric-hero:hover {
    transform: translateY(-4px);
    box-shadow:
        0 4px 6px rgba(0, 0, 0, 0.04),
        0 12px 24px rgba(15, 118, 110, 0.12);
}

.metric-hero.critical {
    border-top-color: #DC2626;
    background: linear-gradient(180deg, #FEF2F2 0%, white 40%);
}

.metric-hero.critical::before {
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.04) 0%, transparent 100%);
}

.metric-hero.warning {
    border-top-color: #F59E0B;
    background: linear-gradient(180deg, #FFFBEB 0%, white 40%);
}

.metric-hero.warning::before {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.04) 0%, transparent 100%);
}

.metric-hero.success {
    border-top-color: #16A34A;
    background: linear-gradient(180deg, #F0FDF4 0%, white 40%);
}

.metric-hero.success::before {
    background: linear-gradient(135deg, rgba(22, 163, 74, 0.04) 0%, transparent 100%);
}

.metric-hero .metric-icon {
    font-size: 32px;
    margin-bottom: 8px;
    display: block;
    position: relative;
    z-index: 1;
}

.metric-hero .metric-value {
    font-size: 44px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    margin: 8px 0;
    position: relative;
    z-index: 1;
    letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
}

.metric-hero .metric-label {
    font-size: 11px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    position: relative;
    z-index: 1;
}

.model-status-card {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 12px;
    padding: 16px;
    color: white;
    backdrop-filter: blur(10px);
}
.model-status-card .status-label {
    font-size: 11px; text-transform: uppercase; opacity: 0.7; letter-spacing: 0.05em;
}
.model-status-card .model-name {
    font-size: 18px; font-weight: 800; margin: 4px 0; color: #5EEAD4;
}
.model-status-card .model-metrics {
    display: flex; gap: 12px; font-size: 13px; margin: 8px 0; flex-wrap: wrap;
}
.model-status-card .trained-info { font-size: 11px; opacity: 0.85; margin-top: 6px; }

.cluster-card {
    background: white;
    border-radius: 16px;
    padding: 20px 16px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-top: 4px solid #14B8A6;
    transition: all 0.2s ease;
}
.cluster-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.cluster-card .cluster-number {
    font-size: 40px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
}
.cluster-card .cluster-label {
    font-size: 13px;
    font-weight: 600;
    color: #0F766E;
    margin: 6px 0;
}
.cluster-card .cluster-count {
    font-size: 12px;
    color: #64748B;
}

[data-testid="stSidebar"] .sidebar-patient-summary {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    border: 1px solid rgba(255, 255, 255, 0.15);
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    color: white;
    font-size: 13px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row:last-child {
    border-bottom: none;
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row .summary-label {
    opacity: 0.9;
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row .summary-value {
    font-weight: 700;
    font-size: 18px;
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row.critical .summary-value {
    color: #FCA5A5;
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row.warning .summary-value {
    color: #FCD34D;
}
[data-testid="stSidebar"] .sidebar-patient-summary .summary-row.safe .summary-value {
    color: #86EFAC;
}

/* ============================================================
   GLOBAL TEXT VISIBILITY FIX — dark text on light (main area)
   Sidebar: unchanged (rules scoped to .main where needed)
   ============================================================ */

/* ===== EXPANDERS ===== */
.main [data-testid="stExpander"],
.main .streamlit-expander,
.main details {
    background: white !important;
    border: 1px solid rgba(15, 118, 110, 0.15) !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    margin: 12px 0 !important;
    overflow: hidden !important;
}

.main [data-testid="stExpander"] > details > summary,
.main [data-testid="stExpander"] summary,
.main .streamlit-expanderHeader,
.main details > summary {
    background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%) !important;
    color: #0F172A !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    padding: 14px 20px !important;
    cursor: pointer !important;
    list-style: none !important;
    border-bottom: 1px solid rgba(15, 118, 110, 0.1) !important;
}

.main [data-testid="stExpander"] summary *,
.main [data-testid="stExpander"] > details > summary *,
.main .streamlit-expanderHeader * {
    color: #0F172A !important;
    font-weight: 700 !important;
}

.main [data-testid="stExpanderDetails"],
.main [data-testid="stExpander"] > details > div,
.main [data-testid="stExpander"] .streamlit-expanderContent {
    background: white !important;
    padding: 20px !important;
    color: #0F172A !important;
}

.main [data-testid="stExpanderDetails"] *,
.main [data-testid="stExpander"] > details > div *,
.main [data-testid="stExpander"] .streamlit-expanderContent *,
.main [data-testid="stExpander"] p,
.main [data-testid="stExpander"] span,
.main [data-testid="stExpander"] div,
.main [data-testid="stExpander"] li,
.main [data-testid="stExpander"] strong,
.main [data-testid="stExpander"] em,
.main [data-testid="stExpander"] label {
    color: #0F172A !important;
    background-color: transparent !important;
}

.main [data-testid="stExpander"] strong,
.main [data-testid="stExpander"] b {
    color: #0F766E !important;
    font-weight: 700 !important;
}

/* ===== DATAFRAMES AND TABLES ===== */
.main [data-testid="stDataFrame"],
.main [data-testid="stTable"],
.main .stDataFrame,
.main .stTable {
    background: white !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    border: 1px solid rgba(15, 118, 110, 0.1) !important;
}

.main [data-testid="stDataFrame"] thead,
.main [data-testid="stDataFrame"] thead tr,
.main [data-testid="stDataFrame"] thead th,
.main [data-testid="stTable"] thead,
.main [data-testid="stTable"] thead tr,
.main [data-testid="stTable"] thead th {
    background: linear-gradient(135deg, #0F766E 0%, #115E59 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 12px !important;
}

.main [data-testid="stDataFrame"] thead th *,
.main [data-testid="stTable"] thead th * {
    color: white !important;
}

.main [data-testid="stDataFrame"] tbody tr,
.main [data-testid="stDataFrame"] tbody td,
.main [data-testid="stTable"] tbody tr,
.main [data-testid="stTable"] tbody td {
    background: white !important;
    color: #0F172A !important;
    padding: 10px 12px !important;
    border-bottom: 1px solid #F1F5F9 !important;
}

.main [data-testid="stDataFrame"] tbody td *,
.main [data-testid="stTable"] tbody td * {
    color: #0F172A !important;
}

.main [data-testid="stDataFrame"] tbody tr:nth-child(even),
.main [data-testid="stTable"] tbody tr:nth-child(even) {
    background: #F0FDFA !important;
}

.main [data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: #F0FDFA !important;
}

.main [data-testid="stDataFrame"] tbody tr:hover,
.main [data-testid="stTable"] tbody tr:hover {
    background: #CCFBF1 !important;
}

/* ===== INFO / WARNING / SUCCESS / ERROR (reinforce readability) ===== */
.stAlert,
[data-testid="stAlert"],
[data-testid="stAlertContainer"],
div[data-baseweb="notification"] {
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: none !important;
    margin: 16px 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
}

.stAlert[kind="info"],
[data-testid="stAlert"][kind="info"],
div[data-testid="stAlertContainer"][kind="info"] {
    background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%) !important;
    border-left: 4px solid #14B8A6 !important;
}

.stAlert[kind="info"] *,
[data-testid="stAlert"][kind="info"] *,
div[data-testid="stAlertContainer"][kind="info"] * {
    color: #0F766E !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}

.stAlert[kind="warning"],
[data-testid="stAlert"][kind="warning"] {
    background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%) !important;
    border-left: 4px solid #F59E0B !important;
}

.stAlert[kind="warning"] *,
[data-testid="stAlert"][kind="warning"] * {
    color: #92400E !important;
    font-weight: 600 !important;
}

.stAlert[kind="success"],
[data-testid="stAlert"][kind="success"] {
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%) !important;
    border-left: 4px solid #16A34A !important;
}

.stAlert[kind="success"] *,
[data-testid="stAlert"][kind="success"] * {
    color: #166534 !important;
    font-weight: 600 !important;
}

.stAlert[kind="error"],
[data-testid="stAlert"][kind="error"] {
    background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%) !important;
    border-left: 4px solid #DC2626 !important;
}

.stAlert[kind="error"] *,
[data-testid="stAlert"][kind="error"] * {
    color: #991B1B !important;
    font-weight: 600 !important;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    background: white !important;
    color: #0F172A !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
    margin: 12px 0 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    border: 1px solid rgba(15, 118, 110, 0.08) !important;
}

[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] em {
    color: #0F172A !important;
}

[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] b {
    color: #0F766E !important;
    font-weight: 700 !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #F0FDFA 0%, #ECFEFF 100%) !important;
    border-left: 4px solid #0F766E !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
    color: #0F172A !important;
}

/* ===== PLOTLY ===== */
.main .js-plotly-plot,
.main .plotly,
.main .plot-container {
    background: white !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    padding: 12px !important;
}

.main .js-plotly-plot text,
.main .plotly text,
.main .js-plotly-plot .annotation-text,
.main .js-plotly-plot .legend text,
.main .js-plotly-plot .gtitle,
.main .js-plotly-plot .xtick text,
.main .js-plotly-plot .ytick text,
.main .js-plotly-plot .legendtext {
    fill: #000000 !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}

/* Table traces (leaderboard): tout le texte des cellules en noir */
.main .js-plotly-plot .plotly-table text,
.main .js-plotly-plot .plotly-table .text,
.main .js-plotly-plot svg .text {
    fill: #000000 !important;
}

/* ===== MATPLOTLIB / IMAGES ===== */
.main [data-testid="stImage"] img,
.main .element-container img {
    background: white !important;
    border-radius: 12px !important;
    padding: 8px !important;
}

/* ===== MARKDOWN (main only — preserves sidebar copy) ===== */
.main .stMarkdown,
.main .stMarkdown p,
.main .stMarkdown span,
.main .stMarkdown div,
.main .stMarkdown li,
.main .stMarkdown h1,
.main .stMarkdown h2,
.main .stMarkdown h3,
.main .stMarkdown h4,
.main .stMarkdown h5,
.main .stMarkdown h6 {
    color: #0F172A !important;
}

/* Ne pas utiliser inherit : un parent peut forcer du blanc (thème Streamlit) → texte illisible */
.main .stMarkdown [style*="color"] {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}

.main .stMarkdown strong,
.main .stMarkdown b {
    color: #0F766E !important;
    font-weight: 700 !important;
}

/* ===== METRICS ===== */
.main [data-testid="stMetric"],
.main [data-testid="metric-container"] {
    background: white !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    border-top: 3px solid #14B8A6 !important;
}

.main [data-testid="stMetricLabel"],
.main [data-testid="stMetricLabel"] * {
    color: #64748B !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.main [data-testid="stMetricValue"],
.main [data-testid="stMetricValue"] * {
    color: #0F172A !important;
    font-weight: 800 !important;
    font-size: 32px !important;
}

.main [data-testid="stMetricDelta"],
.main [data-testid="stMetricDelta"] * {
    color: #16A34A !important;
    font-weight: 600 !important;
}

/* ===== CAPTIONS (main only) ===== */
.main [data-testid="stCaptionContainer"],
.main [data-testid="stCaption"],
.main .stCaption {
    color: #64748B !important;
    font-size: 13px !important;
}

/* ===== CODE ===== */
.main code,
.main [data-testid="stCode"],
.main pre {
    background: #F8FAFC !important;
    color: #0F766E !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
    font-family: 'Consolas', 'Monaco', monospace !important;
}

.main pre code {
    display: block !important;
    padding: 12px !important;
}

/* ===== SELECT / INPUTS (main) ===== */
.main [data-baseweb="select"],
.main [data-baseweb="select"] > div {
    background: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(15, 118, 110, 0.2) !important;
}

.main [data-baseweb="select"] * {
    color: #0F172A !important;
}

.main .stSelectbox label,
.main .stTextInput label,
.main .stNumberInput label {
    color: #0F172A !important;
    font-weight: 600 !important;
}

.main input[type="text"],
.main input[type="number"],
.main .stTextArea textarea {
    background: white !important;
    color: #0F172A !important;
    border: 1px solid rgba(15, 118, 110, 0.2) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
}

.main input[type="text"]:focus,
.main input[type="number"]:focus,
.main .stTextArea textarea:focus {
    border-color: #14B8A6 !important;
    box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.15) !important;
    outline: none !important;
}

/* ===== RADIO / CHECKBOX / SLIDER / NUMBER ===== */
.main .stRadio label,
.main .stCheckbox label {
    color: #0F172A !important;
}

.main .stSlider label,
.main [data-baseweb="slider"] div {
    color: #0F172A !important;
}

.main .stNumberInput label {
    color: #0F172A !important;
}

/* ===== TAB PANEL ===== */
[data-baseweb="tab-panel"] {
    color: #0F172A !important;
}

[data-baseweb="tab-panel"] p,
[data-baseweb="tab-panel"] span,
[data-baseweb="tab-panel"] li,
[data-baseweb="tab-panel"] label {
    color: #0F172A !important;
}

/* ===== HELP TOOLTIPS ===== */
.main [data-testid="stTooltipHoverTarget"] {
    color: #0F172A !important;
}

/* ===== PROGRESS ===== */
.main [data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #0F766E 0%, #14B8A6 100%) !important;
}

/* ===== FILE UPLOADER (main) ===== */
.main [data-testid="stFileUploader"] {
    background: white !important;
    border: 2px dashed rgba(15, 118, 110, 0.3) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

.main [data-testid="stFileUploader"] * {
    color: #0F172A !important;
}

.main [data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%) !important;
    color: white !important;
}

.main [data-testid="stFileUploader"] button * {
    color: white !important;
}

/* ===== CHAT INPUT — texte lisible (thème sombre / Base Web) ===== */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="form-control-container"],
[data-testid="stChatInput"] [data-baseweb="textarea"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] [data-baseweb="textarea"] textarea,
[data-testid="stChatInput"] input[type="text"],
[data-testid="stChatInput"] input[aria-label] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    caret-color: #0f766e !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}

/* Ne pas forcer la couleur du bouton d’envoi (icône blanche sur teal) */
[data-testid="stChatInput"] button,
[data-testid="stChatInput"] button * {
    -webkit-text-fill-color: unset !important;
}

/* Cadre du micro (composant iframe) — finition alignée thème */
iframe[title*="streamlit_mic_recorder"] {
    border-radius: 999px !important;
    border: 2px solid rgba(20, 184, 166, 0.45) !important;
    box-shadow: 0 4px 16px rgba(15, 118, 110, 0.22) !important;
}

/* ============================================================
   PREMIUM HOME PAGE (Doctolib / Linear / clinical SaaS)
   ============================================================ */
.hero-premium {
    background: linear-gradient(135deg, #0F766E 0%, #14B8A6 50%, #5EEAD4 100%);
    border-radius: 24px;
    padding: 56px 48px;
    margin-bottom: 32px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(15, 118, 110, 0.15);
}
.hero-premium::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-premium::after {
    content: '🫀';
    position: absolute;
    bottom: -40px;
    right: 40px;
    font-size: 200px;
    opacity: 0.08;
    pointer-events: none;
}
.hero-premium-content {
    position: relative;
    z-index: 1;
    max-width: 700px;
}
.hero-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
}
.hero-premium h1 {
    font-size: 42px !important;
    font-weight: 800 !important;
    color: white !important;
    line-height: 1.1 !important;
    margin: 0 0 12px 0 !important;
    background: none !important;
    -webkit-text-fill-color: white !important;
    letter-spacing: -0.02em !important;
}
.hero-premium p {
    font-size: 17px;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.6;
    margin: 0 0 28px 0;
    max-width: 580px;
}
.hero-stats-row {
    display: flex;
    flex-wrap: wrap;
    gap: 32px;
    margin-top: 24px;
    direction: ltr;
    unicode-bidi: embed;
}
.hero-stat-item { color: white; }
.hero-stat-number {
    font-size: 28px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
}
.hero-stat-label {
    font-size: 12px;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.quick-actions-section { margin: 32px 0; }
.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-subtitle {
    font-size: 13px;
    color: #64748B;
    margin-bottom: 20px;
}
.quick-actions-grid { margin-bottom: 8px; }
.qa-col-inner {
    background: white;
    border-radius: 16px;
    padding: 20px 20px 12px 20px;
    border: 1px solid rgba(15, 118, 110, 0.08);
    height: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.qa-col-inner::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #0F766E 0%, #14B8A6 100%);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s ease;
}
.qa-col-inner:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(15, 118, 110, 0.12);
    border-color: rgba(15, 118, 110, 0.2);
}
.qa-col-inner:hover::before { transform: scaleX(1); }
.quick-action-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-bottom: 14px;
}
.quick-action-title {
    font-size: 16px;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 6px;
}
.quick-action-desc {
    font-size: 13px;
    color: #64748B;
    line-height: 1.5;
    min-height: 3.2em;
}
.metrics-bar-refined {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
@media (max-width: 900px) {
    .metrics-bar-refined { grid-template-columns: repeat(2, 1fr); }
}
.metric-card-refined {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid rgba(15, 118, 110, 0.08);
    position: relative;
    transition: all 0.2s ease;
}
.metric-card-refined:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(15, 118, 110, 0.08);
}
.metric-card-refined .metric-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.metric-card-refined .metric-icon-small {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}
.metric-card-refined .metric-trend {
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 10px;
    background: #F0FDF4;
    color: #16A34A;
    white-space: nowrap;
}
.metric-card-refined .metric-big {
    font-size: 36px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
}
.metric-card-refined .metric-label-small {
    font-size: 12px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.metric-card-refined.primary .metric-icon-small {
    background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
}
.metric-card-refined.danger { border-color: rgba(220, 38, 38, 0.15); }
.metric-card-refined.danger .metric-icon-small {
    background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
}
.metric-card-refined.warning { border-color: rgba(245, 158, 11, 0.15); }
.metric-card-refined.warning .metric-icon-small {
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
}
.metric-card-refined.success { border-color: rgba(22, 163, 74, 0.15); }
.metric-card-refined.success .metric-icon-small {
    background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
}
.activity-timeline {
    background: white;
    border-radius: 16px;
    padding: 24px 28px;
    border: 1px solid rgba(15, 118, 110, 0.08);
    margin-bottom: 32px;
}
.activity-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid #F1F5F9;
}
.activity-item:last-child { border-bottom: none; }
.activity-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #14B8A6;
    margin-top: 8px;
    flex-shrink: 0;
}
.activity-dot.danger { background: #DC2626; }
.activity-dot.success { background: #16A34A; }
.activity-content { flex: 1; }
.activity-title {
    font-size: 14px;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 2px;
}
.activity-time {
    font-size: 12px;
    color: #94A3B8;
}
.empty-state-card {
    text-align: center;
    padding: 48px 24px;
    background: white;
    border: 2px dashed rgba(15, 118, 110, 0.2);
    border-radius: 16px;
    color: #64748B;
}
.empty-state-icon {
    font-size: 48px;
    margin-bottom: 12px;
    opacity: 0.5;
}

/* ===== CLINIC / PRODUCTION MODE ===== */
.model-info-card {
    background: linear-gradient(135deg, #F0FDFA 0%, #ECFEFF 100%);
    border: 1px solid #14B8A6;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0 20px 0;
    font-size: 14px;
    color: #0F172A;
    line-height: 1.6;
}
.prediction-result-card {
    border: 2px solid #14B8A6;
    border-radius: 16px;
    padding: 24px 28px;
    margin: 16px 0;
    text-align: center;
    background: white;
    box-shadow: 0 4px 20px rgba(15, 118, 110, 0.08);
}
.prediction-result-card .result-score {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
}
.prediction-result-card .result-label {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A;
    margin-top: 8px;
}
.prediction-result-card .result-recommendation {
    margin-top: 16px;
    font-size: 14px;
    color: #475569;
    text-align: center;
    line-height: 1.5;
}
.wearable-alert.critical {
    border: 2px solid #DC2626;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 10px 0;
    background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
    animation: clinic-pulse 2s ease-in-out infinite;
}
@keyframes clinic-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.25); }
    50% { box-shadow: 0 0 0 6px rgba(220, 38, 38, 0); }
}
.wearable-alert .alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 700;
    color: #991B1B;
}
.wearable-alert .alert-vitals {
    margin-top: 8px;
    font-size: 13px;
    color: #0F172A;
}
.wearable-notify-hint {
    margin: 10px 0 0 0;
    font-size: 13px;
    color: #64748B;
}

/* ===== VISIBILITÉ — expanders, titres Streamlit, Plotly (clustering + classement AutoML) =====
   Les expanders utilisent souvent un <button> héritant du style global .stButton > button   (texte blanc), ce qui devient illisible si le fond n’est pas le dégradé teal attendu. */
.main [data-testid="stExpander"] button,
.main [data-testid="stExpander"] [data-baseweb="button"],
.main [data-testid="stExpander"] [data-testid="baseButton-header"],
.main [data-testid="stExpander"] [data-testid="stBaseButton-header"] {
    background: linear-gradient(135deg, #F0FDFA 0%, #E0F2FE 100%) !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    border: 1px solid rgba(15, 118, 110, 0.22) !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06) !important;
}
.main [data-testid="stExpander"] button:hover,
.main [data-testid="stExpander"] [data-baseweb="button"]:hover {
    background: linear-gradient(135deg, #CCFBF1 0%, #BAE6FD 100%) !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}
.main [data-testid="stExpander"] button *,
.main [data-testid="stExpander"] [data-baseweb="button"] *,
.main [data-testid="stExpander"] [data-testid="stMarkdownContainer"],
.main [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}

/* st.title / st.header / st.subheader (composant Heading) */
.main [data-testid="stHeader"],
.main [data-testid="stSubheader"],
.main [data-testid="stTitle"],
.main [data-testid="stHeading"] {
    background: transparent !important;
    color: #0F172A !important;
}
.main [data-testid="stHeader"] *,
.main [data-testid="stSubheader"] *,
.main [data-testid="stTitle"] *,
.main [data-testid="stHeading"] *,
.main [data-testid="stHeader"] h1,
.main [data-testid="stHeader"] h2,
.main [data-testid="stHeader"] h3,
.main [data-testid="stSubheader"] h3,
.main [data-testid="stTitle"] h1 {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    background: transparent !important;
}

/* Titres markdown (# …######) : forcer texte noir sur fond clair */
.main .stMarkdown h1,
.main .stMarkdown h2,
.main .stMarkdown h3,
.main .stMarkdown h4,
.main .stMarkdown h5,
.main .stMarkdown h6 {
    background: transparent !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}

/* Table Plotly (leaderboard) : cellules et en-têtes lisibles même avec thème Streamlit */
.main .js-plotly-plot svg .main-svg .table .cell-text,
.main .js-plotly-plot .plotly-table .cell-text,
.main .js-plotly-plot .plotly-table text {
    fill: #0F172A !important;
}
.main .js-plotly-plot .annotation,
.main .js-plotly-plot .gtitle {
    fill: #0F172A !important;
}

/* ===== Markdown Streamlit : forcer texte noir (classement AutoML, phénotypage, etc.)
   La classe .main n’entoure pas toujours le contenu selon la version → cibler stMarkdownContainer sous .stApp. */
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] span,
.stApp [data-testid="stMarkdownContainer"] div,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] ol,
.stApp [data-testid="stMarkdownContainer"] ul,
.stApp [data-testid="stMarkdownContainer"] h1,
.stApp [data-testid="stMarkdownContainer"] h2,
.stApp [data-testid="stMarkdownContainer"] h3,
.stApp [data-testid="stMarkdownContainer"] h4,
.stApp [data-testid="stMarkdownContainer"] h5,
.stApp [data-testid="stMarkdownContainer"] h6,
.stApp [data-testid="stMarkdownContainer"] em,
.stApp [data-testid="stMarkdownContainer"] code,
.stApp [data-testid="stMarkdownContainer"] pre {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}
.stApp [data-testid="stMarkdownContainer"] strong,
.stApp [data-testid="stMarkdownContainer"] b {
    color: #0F766E !important;
    -webkit-text-fill-color: #0F766E !important;
}
.stApp [data-testid="stMarkdownContainer"] a {
    color: #0D9488 !important;
    -webkit-text-fill-color: #0D9488 !important;
}

/* Sidebar : rétablir texte clair sur le même composant (priorité par chaîne plus longue) */
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] b,
.stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] a {
    color: rgba(255, 255, 255, 0.95) !important;
    -webkit-text-fill-color: rgba(255, 255, 255, 0.95) !important;
}

</style>
"""

TYPING_INDICATOR_HTML = """<div class="typing-indicator"><span></span><span></span><span></span></div>"""

CHAT_SCROLL_SCRIPT = """
<script>
    setTimeout(function() {
        var el = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (el) { el.scrollTop = el.scrollHeight; }
    }, 150);
</script>
"""

# Injected when lang == "ar" (Darija): extends theme with RTL + Arabic font priority
RTL_SUPPLEMENT_CSS = """
<style>
.stApp {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Noto Sans Arabic', 'Inter', sans-serif !important;
}
[data-testid="stSidebar"] { direction: rtl !important; text-align: right !important; }
[data-testid="stChatMessage"] { direction: rtl !important; text-align: right !important; color: #0F172A !important; }
[data-testid="stChatMessage"] * { color: #0F172A !important; }
[data-testid="stChatMessage"] strong { color: #0F766E !important; }
.stMarkdown { direction: rtl !important; text-align: right !important; }
.stMetric [data-testid="stMetricValue"] { direction: ltr !important; unicode-bidi: embed !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    border-left: none !important;
    border-right: 4px solid #14B8A6 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    border-left: none !important;
    border-right: 4px solid #0F766E !important;
}
.hero-premium { direction: ltr; text-align: left; }
.hero-premium h1, .hero-premium p, .hero-badge { direction: ltr; text-align: left; }
.hero-container { text-align: center; }
.hero-stats { direction: rtl; }
.patient-row.high { border-left: none; border-right: 4px solid #DC2626; }
.patient-row.medium { border-left: none; border-right: 4px solid #F59E0B; }
.patient-row.low { border-left: none; border-right: 4px solid #16A34A; }
.winner-card { direction: rtl; }
.risk-summary { direction: rtl; }
</style>
"""
