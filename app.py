import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import date

from database import (
    create_table,
    add_transaction,
    fetch_transactions,
    delete_transaction
)

from auth import (
    create_users_table,
    register_user,
    login_user,
    get_user_id
)


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)


# SESSION STATE

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None


# DATABASE INITIALIZATION

create_table()
create_users_table()


# THEME COLORS

if st.session_state.dark_mode:

    background = "#0E1117"
    sidebar = "#161B22"
    card = "#1E293B"
    text = "#F8FAFC"
    muted = "#94A3B8"
    input_bg = "#263244"
    border = "#475569"
    chart_template = "plotly_dark"

    primary = "#2563EB"
    hover = "#1D4ED8"

else:

    background = "#F4F9FF"
    sidebar = "#FFFFFF"
    card = "#FFFFFF"
    text = "#17324D"
    muted = "#66809B"
    input_bg = "#F7FBFF"
    border = "#D7E8F5"
    chart_template = "plotly_white"

    primary = "#176BCE"
    hover = "#1056AA"


# CUSTOM CSS

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {background};
        color: {text};
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: {background};
    }}

    [data-testid="stHeader"] {{
        background-color: {background};
    }}

    [data-testid="stSidebar"] {{
        background-color: {sidebar};
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background-color: {sidebar};
    }}

    h1, h2, h3, h4, p, label, span {{
        color: {text};
    }}

    [data-testid="stWidgetLabel"] p {{
        color: {text} !important;
    }}

    [data-testid="stMarkdownContainer"] p {{
        color: {text};
    }}

    input, textarea {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
    }}

    [data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    [data-baseweb="select"] input {{
        color: {text} !important;
    }}

    [data-testid="stMetric"] {{
        background-color: {card};
        padding: 20px;
        border-radius: 12px;
        border: 1px solid {border};
    }}

    [data-testid="stMetricLabel"] {{
        color: {muted} !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {text} !important;
    }}

    .stButton > button,
    .stFormSubmitButton > button {{
        background-color: {primary} !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        transition: 0.2s ease;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background-color: {hover} !important;
        color: white !important;
        border: none;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid {border};
        border-radius: 10px;
    }}

    [data-testid="stDownloadButton"] button {{
        background-color: {primary} !important;
        color: white !important;
        border-radius: 8px;
    }}

    hr {{
        border-color: {border};
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# SIDEBAR

st.sidebar.title("💰 Smart Expense Tracker")

if st.session_state.user_id is not None:

    st.sidebar.write(
        f"Welcome, {st.session_state.username}!"
    )

    st.sidebar.divider()

    # THEME TOGGLE

    theme_label = (
        "☀️ Switch to Light Mode"
        if st.session_state.dark_mode
        else "🌙 Switch to Dark Mode"
    )

    if st.sidebar.button(theme_label, use_container_width=True):

        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.sidebar.divider()


# LOGIN AND REGISTRATION

if st.session_state.user_id is None:

    st.title("💰 Smart Expense Tracker")

    st.caption("Manage your money. Understand your spending.")

    choice = st.radio(
        "Select Option",
        ["Login", "Register"],
        horizontal=True
    )

    if choice == "Register":

        st.subheader("Create New Account")

        with st.form("register_form"):

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            submitted = st.form_submit_button("Register")

            if submitted:

                if not username.strip() or not password:
                    st.error("Please fill all fields.")

                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")

                elif password != confirm_password:
                    st.error("Passwords do not match.")

                elif register_user(username.strip(), password):
                    st.success("Registration successful! Please login.")

                else:
                    st.error("Username already exists.")

    else:

        st.subheader("Login to Your Account")

        with st.form("login_form"):

            username = st.text_input("Username")

            password = st.text_input(
                "Password",
                type="password"
            )

            submitted = st.form_submit_button("Login")

            if submitted:

                if login_user(username.strip(), password):

                    st.session_state.user_id = get_user_id(
                        username.strip()
                    )

                    st.session_state.username = username.strip()

                    st.success("Login successful!")

                    st.rerun()

                else:
                    st.error("Invalid username or password.")

    st.stop()


# LOGGED-IN USER

user_id = st.session_state.user_id


# LOGOUT

if st.sidebar.button("🚪 Logout", use_container_width=True):

    st.session_state.user_id = None
    st.session_state.username = None

    st.rerun()


# CATEGORIES

categories = [
    "Food",
    "Travel",
    "Shopping",
    "Education",
    "Entertainment",
    "Bills",
    "Health",
    "Other"
]


# FETCH USER DATA

def get_data():

    data = fetch_transactions(user_id)

    return pd.DataFrame(
        data,
        columns=[
            "ID",
            "Type",
            "Amount",
            "Category",
            "Description",
            "Date"
        ]
    )


# NAVIGATION

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Transaction",
        "Transaction History"
    ]
)


# DASHBOARD

if page == "Dashboard":

    st.title("📊 Smart Expense Dashboard")

    st.caption("Your personal financial overview")

    df = get_data()

    if not df.empty:

        df["Date"] = pd.to_datetime(df["Date"])

        months = sorted(
            df["Date"].dt.strftime("%Y-%m").unique(),
            reverse=True
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
            index=default_index
        )

        monthly_df = df[
            df["Date"].dt.strftime("%Y-%m") == selected_month
        ]

        income = monthly_df[
            monthly_df["Type"] == "Income"
        ]["Amount"].sum()

        expense = monthly_df[
            monthly_df["Type"] == "Expense"
        ]["Amount"].sum()

        balance = income - expense
        if income > 0:
            savings_rate = (balance / income) * 100
        else:
            savings_rate = 0

    else:

        monthly_df = df
        income = 0
        expense = 0
        balance = 0

    # METRIC CARDS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💵 Monthly Income",
        f"₹{income:,.2f}"
)

    col2.metric(
        "💸 Monthly Expenses",
        f"₹{expense:,.2f}"
)

    col3.metric(
        "💰 Monthly Balance",
        f"₹{balance:,.2f}"
)

    col4.metric(
        "📈 Savings Rate",
        f"{savings_rate:.1f}%"
)

    # CHARTS

    if not monthly_df.empty:

        expense_data = monthly_df[
            monthly_df["Type"] == "Expense"
        ]

        if not expense_data.empty:

            category_data = expense_data.groupby(
                "Category"
            )["Amount"].sum().reset_index()

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Category-wise Spending")

                fig = px.pie(
                    category_data,
                    names="Category",
                    values="Amount",
                    hole=0.45,
                    template=chart_template
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with col2:

                st.subheader("Expense Comparison")

                fig = px.bar(
                    category_data,
                    x="Category",
                    y="Amount",
                    color="Category",
                    template=chart_template
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        else:

            st.info("No expenses recorded in this month.")

        st.subheader("Recent Transactions")

        recent = monthly_df.head(5).copy()

        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No transactions yet. Add your first transaction!")


# ADD TRANSACTION

elif page == "Add Transaction":

    st.title("➕ Add New Transaction")

    st.caption("Record your income and expenses")

    with st.form("transaction_form"):

        transaction_type = st.selectbox(
            "Transaction Type",
            ["Expense", "Income"]
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            step=100.0
        )

        if transaction_type == "Expense":

            category_options = categories

        else:

            category_options = [
                "Salary",
                "Allowance",
                "Freelance",
                "Other"
            ]

        category = st.selectbox(
            "Category",
            category_options
        )

        description = st.text_input("Description")

        transaction_date = st.date_input(
            "Date",
            value=date.today()
        )

        submitted = st.form_submit_button(
            "💾 Save Transaction"
        )

        if submitted:

            add_transaction(
                transaction_type,
                amount,
                category,
                description.strip(),
                transaction_date.isoformat(),
                user_id
            )

            st.success("Transaction saved successfully!")

            st.rerun()


# TRANSACTION HISTORY

elif page == "Transaction History":

    st.title("📋 Transaction History")

    df = get_data()

    if not df.empty:

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # CSV DOWNLOAD

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download CSV Report",
            data=csv,
            file_name="expense_report.csv",
            mime="text/csv"
        )

        st.divider()

        # DELETE TRANSACTION

        st.subheader("Delete Transaction")

        transaction_id = st.selectbox(
            "Select Transaction ID",
            df["ID"].tolist()
        )

        if st.button("🗑️ Delete Selected Transaction"):

            delete_transaction(
                int(transaction_id),
                user_id
            )

            st.success("Transaction deleted successfully!")

            st.rerun()

    else:

        st.info("No transactions available.")