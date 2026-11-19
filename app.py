import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date

from auth import (
    get_client,
    is_admin,
    admin_reset_password,
)

from database import (
    fetch_transactions,
    add_transaction,
    delete_transaction,
    get_all_users,
    get_total_users,
    set_user_status,
)


# ---------------- FLASK API CONFIGURATION ----------------

API_BASE_URL = "http://127.0.0.1:5000"


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
)


# ---------------- SESSION STATE ----------------

defaults = {
    "dark_mode": True,
    "user_id": None,
    "username": None,
    "user_role": None,
    "access_token": None,
    "refresh_token": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- THEME ----------------

if st.session_state.dark_mode:
    background, sidebar, card = "#0E1117", "#161B22", "#1E293B"
    text, muted, input_bg, border = "#F8FAFC", "#94A3B8", "#263244", "#475569"
    chart_template = "plotly_dark"
    primary, hover = "#2563EB", "#1D4ED8"

else:
    background, sidebar, card = "#F4F9FF", "#FFFFFF", "#FFFFFF"
    text, muted, input_bg, border = "#17324D", "#66809B", "#F7FBFF", "#D7E8F5"
    chart_template = "plotly_white"
    primary, hover = "#176BCE", "#1056AA"


st.markdown(f"""
<style>
.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"] {{
    background-color:{background}; color:{text};
}}
[data-testid="stSidebar"],[data-testid="stSidebar"] > div:first-child {{
    background-color:{sidebar};
}}
h1,h2,h3,h4,p,label,span {{ color:{text}; }}
[data-testid="stWidgetLabel"] p {{ color:{text} !important; }}
input,textarea {{
    background-color:{input_bg} !important;
    color:{text} !important;
    border:1px solid {border} !important;
}}
[data-baseweb="select"] > div {{
    background-color:{input_bg} !important;
    color:{text} !important;
    border-color:{border} !important;
}}
[data-testid="stMetric"] {{
    background-color:{card};
    padding:20px;
    border-radius:12px;
    border:1px solid {border};
}}
[data-testid="stMetricLabel"] {{ color:{muted} !important; }}
[data-testid="stMetricValue"] {{ color:{text} !important; }}
.stButton > button,.stFormSubmitButton > button {{
    background-color:{primary} !important;
    color:white !important;
    border:none;
    border-radius:8px;
    font-weight:600;
}}
.stButton > button:hover,.stFormSubmitButton > button:hover {{
    background-color:{hover} !important;
    color:white !important;
}}
hr {{ border-color:{border}; }}
</style>
""", unsafe_allow_html=True)


# ---------------- LOGOUT ----------------

def logout():
    for key, value in defaults.items():
        st.session_state[key] = value

    st.rerun()


# ---------------- AUTHENTICATED SUPABASE CLIENT ----------------

def get_authenticated_client():
    return get_client(
        st.session_state.access_token,
        st.session_state.refresh_token,
    )


# ---------------- LOGIN AND REGISTRATION ----------------

def login_screen():

    st.title("💰 Smart Expense Tracker")
    st.caption("Manage your money. Understand your spending.")

    choice = st.radio(
        "Select Option",
        ["Login", "Register"],
        horizontal=True,
    )

    # ---------------- REGISTRATION ----------------

    if choice == "Register":

        st.subheader("Create New Account")

        with st.form("register_form"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
            )

            submitted = st.form_submit_button("Register")

        if submitted:

            if not username.strip() or not password:
                st.error("Please fill all fields.")

            elif len(password) < 8:
                st.error("Password must contain at least 8 characters.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:

                try:

                    response = requests.post(
                        f"{API_BASE_URL}/api/auth/register",
                        json={
                            "username": username.strip(),
                            "password": password,
                        },
                        timeout=15,
                    )

                    try:
                        result = response.json()
                    except ValueError:
                        result = {}

                    if response.status_code == 201:
                        st.success(
                            result.get(
                                "message",
                                "Registration successful. Please log in.",
                            )
                        )

                    else:
                        st.error(
                            result.get(
                                "message",
                                "Registration failed. Please try again.",
                            )
                        )

                except requests.exceptions.RequestException:
                    st.error(
                        "Cannot connect to the Flask server. "
                        "Please make sure Flask is running."
                    )

    # ---------------- LOGIN ----------------

    else:

        st.subheader("Login to Your Account")

        with st.form("login_form"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Login")

        if submitted:

            if not username.strip() or not password:
                st.error("Enter your username and password.")

            else:

                try:

                    response = requests.post(
                        f"{API_BASE_URL}/api/auth/login",
                        json={
                            "username": username.strip(),
                            "password": password,
                        },
                        timeout=15,
                    )

                    try:
                        result = response.json()
                    except ValueError:
                        result = {}

                    if response.status_code == 200:

                        account = result.get("user", {})
                        session = result.get("session", {})

                        access_token = session.get("access_token")
                        refresh_token = session.get("refresh_token")

                        if not access_token or not refresh_token:
                            st.error(
                                "Login response did not contain a valid session."
                            )
                            return

                        st.session_state.user_id = account.get("user_id")
                        st.session_state.username = account.get("username")
                        st.session_state.user_role = account.get("role")
                        st.session_state.access_token = access_token
                        st.session_state.refresh_token = refresh_token

                        st.rerun()

                    else:

                        st.error(
                            result.get(
                                "message",
                                "Invalid username/password or inactive account.",
                            )
                        )

                except requests.exceptions.RequestException:
                    st.error(
                        "Cannot connect to the Flask server. "
                        "Please make sure Flask is running."
                    )


# ---------------- SIDEBAR / AUTH ----------------

st.sidebar.title("💰 Smart Expense Tracker")

if not st.session_state.user_id:
    login_screen()
    st.stop()


# ---------------- VERIFY USER SESSION ----------------

try:

    client = get_authenticated_client()

    active_check = client.rpc("is_active_user").execute()

    if not active_check.data:
        st.warning(
            "This account is inactive. Please contact the administrator."
        )
        logout()

except Exception:

    st.error("Your session has expired. Please log in again.")
    logout()


# ---------------- SIDEBAR OPTIONS ----------------

st.sidebar.write(f"Welcome, {st.session_state.username}!")

st.sidebar.divider()

theme_label = (
    "☀️ Switch to Light Mode"
    if st.session_state.dark_mode
    else "🌙 Switch to Dark Mode"
)

if st.sidebar.button(theme_label, use_container_width=True):

    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()


if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout()


# =====================================================
#                  ADMIN DASHBOARD
# =====================================================

if st.session_state.user_role == "admin":

    st.sidebar.divider()
    st.sidebar.subheader("Administrator")

    st.title("🛡️ Admin Dashboard")

    st.caption(
        "Manage accounts without accessing users' financial records."
    )

    try:

        if not is_admin(client):

            st.error("Administrator access could not be verified.")
            logout()

        users = get_all_users(client)

        total = len(users)

        active = sum(
            1 for user in users
            if user.get("status") == "active"
        )

        inactive = sum(
            1 for user in users
            if user.get("status") == "inactive"
        )

        # ---------------- USER STATISTICS ----------------

        c1, c2, c3 = st.columns(3)

        c1.metric("Registered Users", total)
        c2.metric("Active Users", active)
        c3.metric("Inactive Users", inactive)

        # ---------------- RECENT REGISTRATIONS ----------------

        st.divider()
        st.subheader("Recent Registrations")

        recent_users = sorted(
            users,
            key=lambda user: user.get("created_at") or "",
            reverse=True,
        )[:5]

        if recent_users:

            recent_display = pd.DataFrame([
                {
                    "Username": user.get("username"),
                    "Role": user.get("role"),
                    "Status": user.get("status"),
                    "Registration Date": user.get("created_at"),
                }
                for user in recent_users
            ])

            st.dataframe(
                recent_display,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info("No registrations available yet.")

        # ---------------- USER MANAGEMENT ----------------

        st.divider()
        st.subheader("User Management")

        if users:

            display_users = pd.DataFrame([
                {
                    "Username": user.get("username"),
                    "Role": user.get("role"),
                    "Status": user.get("status"),
                    "Registration Date": user.get("created_at"),
                }
                for user in users
            ])

            st.dataframe(
                display_users,
                use_container_width=True,
                hide_index=True,
            )

            manageable = [
                user for user in users
                if user.get("role") == "user"
            ]

            if manageable:

                st.divider()

                st.subheader("Activate / Deactivate Account")

                user_lookup = {
                    f'{user["username"]} ({user["status"]})': user["id"]
                    for user in manageable
                }

                selected_label = st.selectbox(
                    "Select user",
                    list(user_lookup),
                )

                selected_id = user_lookup[selected_label]

                selected_user = next(
                    user for user in manageable
                    if user["id"] == selected_id
                )

                new_status = (
                    "inactive"
                    if selected_user["status"] == "active"
                    else "active"
                )

                action_label = (
                    "Deactivate account"
                    if new_status == "inactive"
                    else "Activate account"
                )

                if st.button(action_label):

                    if set_user_status(client, selected_id, new_status):

                        st.success(
                            f"Account {new_status}. "
                            "User data has been retained."
                        )

                        st.rerun()

                    else:

                        st.error("Account status was not changed.")

                # ---------------- PASSWORD RESET ----------------

                st.divider()

                st.subheader("Admin-assisted Password Reset")

                reset_label = st.selectbox(
                    "Choose user for password reset",
                    list(user_lookup),
                    key="reset_user",
                )

                reset_id = user_lookup[reset_label]

                new_password = st.text_input(
                    "New temporary password",
                    type="password",
                )

                confirm_new_password = st.text_input(
                    "Confirm new password",
                    type="password",
                )

                if st.button("Reset user password"):

                    if len(new_password) < 8:

                        st.error(
                            "Password must contain at least 8 characters."
                        )

                    elif new_password != confirm_new_password:

                        st.error("Passwords do not match.")

                    else:

                        ok, message = admin_reset_password(
                            client,
                            reset_id,
                            new_password,
                        )

                        (st.success if ok else st.error)(message)

        else:

            st.info("No registered users yet.")

    except Exception:

        st.error(
            "Could not load account management. "
            "Please verify the Supabase policies and connection."
        )

    st.caption(
        "Privacy protection: this dashboard does not retrieve "
        "or display transaction records."
    )

    st.stop()


# =====================================================
#                 NORMAL USER APP
# =====================================================

categories = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Entertainment",
    "Bills",
    "Health",
    "Other",
]


# ---------------- GET USER TRANSACTIONS ----------------

def get_data():

    rows = fetch_transactions(
        client,
        st.session_state.user_id,
    )

    return pd.DataFrame(
        rows,
        columns=[
            "ID",
            "Type",
            "Amount",
            "Category",
            "Description",
            "Date",
        ],
    )


# ---------------- NAVIGATION ----------------

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Transaction",
        "Transaction History",
    ],
)


# =====================================================
#                    DASHBOARD
# =====================================================

if page == "Dashboard":

    st.title("📊 Smart Expense Dashboard")

    st.caption("Your personal financial overview")

    df = get_data()

    if not df.empty:

        df["Date"] = pd.to_datetime(df["Date"])

        months = sorted(
            df["Date"].dt.strftime("%Y-%m").unique(),
            reverse=True,
        )

        current_month = date.today().strftime("%Y-%m")

        default_index = (
            months.index(current_month)
            if current_month in months
            else 0
        )

        selected_month = st.selectbox(
            "Select Month",
            months,
            index=default_index,
        )

        monthly_df = df[
            df["Date"].dt.strftime("%Y-%m") == selected_month
        ]

        income = monthly_df.loc[
            monthly_df["Type"] == "Income",
            "Amount",
        ].sum()

        expense = monthly_df.loc[
            monthly_df["Type"] == "Expense",
            "Amount",
        ].sum()

    else:

        monthly_df = df
        income = expense = 0.0

    balance = income - expense

    savings_rate = (
        balance / income * 100
        if income > 0
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💵 Monthly Income", f"₹{income:,.2f}")
    col2.metric("💸 Monthly Expenses", f"₹{expense:,.2f}")
    col3.metric("💰 Monthly Balance", f"₹{balance:,.2f}")
    col4.metric("📈 Savings Rate", f"{savings_rate:.1f}%")

    if not monthly_df.empty:

        expense_data = monthly_df[
            monthly_df["Type"] == "Expense"
        ]

        if not expense_data.empty:

            category_data = (
                expense_data
                .groupby("Category")["Amount"]
                .sum()
                .reset_index()
            )

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Category-wise Spending")

                fig = px.pie(
                    category_data,
                    names="Category",
                    values="Amount",
                    hole=0.45,
                    template=chart_template,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            with col2:

                st.subheader("Expense Comparison")

                fig = px.bar(
                    category_data,
                    x="Category",
                    y="Amount",
                    color="Category",
                    template=chart_template,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

        else:

            st.info("No expenses recorded in this month.")

        st.subheader("Recent Transactions")

        recent = monthly_df.head(5).copy()

        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No transactions yet. Add your first transaction!")


# =====================================================
#                 ADD TRANSACTION
# =====================================================

elif page == "Add Transaction":

    st.title("➕ Add New Transaction")

    st.caption("Record your income and expenses")

    with st.form("transaction_form"):

        transaction_type = st.selectbox(
            "Transaction Type",
            ["Expense", "Income"],
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            step=100.0,
        )

        category_options = (
            categories
            if transaction_type == "Expense"
            else [
                "Salary",
                "Allowance",
                "Freelance",
                "Other",
            ]
        )

        category = st.selectbox(
            "Category",
            category_options,
        )

        description = st.text_input("Description")

        