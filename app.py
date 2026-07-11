import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Margin Matrix", layout="centered")

# --- ACCESS GATE ---
query_params = st.query_params
access_token = query_params.get("access", "").strip()

def access_denied():
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e0e0e; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='color:#e0e0e0; font-family:monospace; text-align:center; "
        "margin-top:15vh;'>ACCESS DENIED</h2>"
        "<p style='color:#888; font-family:monospace; text-align:center;'>"
        "Unauthorized or missing credentials.</p>",
        unsafe_allow_html=True,
    )
    st.stop()

if not access_token:
    access_denied()

try:
        # 1. Open the connection bridge (no URL here)
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 2. Read the specific sheet by passing the URL here
        sheet_url = "https://docs.google.com/spreadsheets/d/1nFq3e8wxKPSHBlhAcHxr1_FkyI3GdaeutJGJ7h-cpek/edit?gid=0#gid=0" # <-- PASTE YOUR FULL URL HERE
        
        ledger = conn.read(spreadsheet=sheet_url, worksheet="AccessLedger", usecols=[0], ttl=60)
        authorized_tokens = set(ledger.iloc[:, 0].astype(str).str.strip())
        
        # Diagnostic print
        # print(f"DEBUG: I found these tokens in the sheet: {authorized_tokens}")

except Exception as e:
        # If the connection fails, deny access
        print(f"DEBUG: Connection error: {e}")
        access_denied()
# --- GATE CLEARED, APP LOGIC BELOW ---
# --- GATE CLEARED, APP LOGIC BELOW ---

# 1. ARROGANT MINIMALISM CSS INJECTION
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000; font-family: 'Courier New', Courier, monospace; }
    h1, h2, h3, p, div, span, label { font-family: 'Courier New', Courier, monospace !important; }
    [data-testid="stSidebar"] { background-color: #f4f4f4; border-right: 2px solid #000000; }
    .metric-box { border: 4px solid #000000; padding: 30px; text-align: center; margin-top: 30px; box-shadow: 8px 8px 0px #000000; }
    .title-format { font-size: 3.5rem; font-weight: 900; text-align: center; letter-spacing: -2px; margin-bottom: 1rem; margin-top: 1rem; }
    .subtitle-format { font-size: 1rem; font-weight: bold; text-align: center; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 20px; margin-bottom: 30px; }
    div[data-testid="metric-container"] { border: 2px solid #000; padding: 15px; text-align: center; }
    
    /* --- TITANIUM SHIELD FOR STREAMLIT ICONS --- */
    i, [class*="material"], [data-testid*="stIcon"], .material-symbols-rounded { 
        font-family: 'Material Symbols Rounded', 'Material Icons' !important; 
    }
    </style>
    </style>
""", unsafe_allow_html=True)

# 2. BRAND HEADER
st.markdown('<div class="title-format">[ MARGIN MATRIX ]</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-format">Accountability & Results Engineering</div>', unsafe_allow_html=True)

# 3. SIDEBAR ARCHITECTURE (Inputs)
st.sidebar.markdown("### [ INPUT PARAMETERS ]")

base_labor = st.sidebar.number_input("Base Labor Rate ($/hr)", min_value=0.0, value=75.0, step=5.0, 
    help="Your unburdened hourly target rate.")

est_hours = st.sidebar.number_input("Estimated Labor Hours", min_value=0.0, value=10.0, step=1.0, 
    help="Total hours expected for the project. Be realistic, not optimistic.")

raw_materials = st.sidebar.number_input("Raw Material Cost ($)", min_value=0.0, value=1500.0, step=100.0, 
    help="Your actual hard cost for materials before any markup.")

st.sidebar.markdown("### [ BUFFERS & OVERHEAD ]")

waste_buffer = st.sidebar.slider("Material Waste Buffer (%)", 0, 30, 10, 
    help="Accounts for human error, damaged materials, and site inefficiencies. Do not zero this out just to win a bid. The cost of waste must be passed to the project, not your bottom line.") / 100.0

overhead = st.sidebar.slider("Overhead Allocation (%)", 0, 50, 15, 
    help="Your true cost of doing business (fuel, insurance, software, tool depreciation). If you do not charge for this, you are paying for the client's project out of your own pocket.") / 100.0

st.sidebar.markdown("### [ THE TARGET ]")

desired_margin = st.sidebar.slider("Desired Net Margin (%) *Hard Cap 60%*", 0, 60, 30, 
    help="The absolute floor for your desired profit. This enforces accountability and prevents you from negotiating against yourself.") / 100.0

st.sidebar.markdown("### [ RISK EXECUTION ]")

# Make sure the variable name matches exactly what you used for the math engine below
complexity = st.sidebar.selectbox("Select Complexity", 
    options=["Tier 1: Standard (1.0x)", "Tier 2: Complex (1.35x)", "Tier 3: Critical (1.75x)"],
    help="Tier 1: Clear access, familiar scope, standard materials.\n\nTier 2: Tight timelines, structural unknowns, restricted access.\n\nTier 3: High liability, hazardous conditions, zero margin for error.")
# --- RISK MULTIPLIER TRANSLATION ---
if "Tier 1" in complexity:
    risk_mult = 1.0
elif "Tier 2" in complexity:
    risk_mult = 1.35
elif "Tier 3" in complexity:
    risk_mult = 1.75
# 4. THE ACTUARIAL MATH ENGINE
true_material = raw_materials * (1 + waste_buffer)
risk_labor = base_labor * est_hours * risk_mult
base_cost = true_material + risk_labor
total_cost = base_cost * (1 + overhead)

final_price = total_cost / (1 - desired_margin)
actual_profit = final_price - total_cost

# 5. DASHBOARD OUTPUT
col1, col2, col3 = st.columns(3)
col1.metric("True Material Cost", f"${true_material:,.2f}")
col2.metric("Risk-Adjusted Labor", f"${risk_labor:,.2f}")
col3.metric("True Total Cost", f"${total_cost:,.2f}")

st.markdown(f"""
    <div class="metric-box">
        <h3 style="margin-bottom:0px; text-transform: uppercase;">Final Quoted Price</h3>
        <h1 style="font-size: 5rem; margin-top:0px; margin-bottom: 0px;">${final_price:,.2f}</h1>
        <h3 style="color:#333; margin-top:10px;">ACTUAL DOLLAR PROFIT: ${actual_profit:,.2f}</h3>
    </div>
""", unsafe_allow_html=True)