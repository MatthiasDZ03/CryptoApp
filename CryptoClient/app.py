import datetime

import pandas as pd
import streamlit as st

import api

st.set_page_config(page_title="CryptoApp", page_icon="🪙")
st.title("🪙 CryptoApp – Account Service")

if api.USE_MOCK:
    st.warning("Mock-Modus: Es werden Fake-Daten verwendet, nicht die echte API.")

page = st.sidebar.radio("Navigation", ["Konten", "Konto anlegen", "Konto verwalten", "Kaufkraft"])


def show_error(error: api.ApiError):
    st.error(f"Fehler {error.status}: {error.message}")


def account_label(account):
    return f"{account['firstName']} {account['lastName']} ({account['email']})"


def load_accounts():
    try:
        return api.list_accounts()
    except api.ApiError as e:
        show_error(e)
    except Exception as e:  # z. B. API nicht gestartet
        st.error(f"API nicht erreichbar: {e}")
    return []


# ---------------------------------------------------------------- Seiten

if page == "Konten":
    st.header("Alle Konten")
    accounts = load_accounts()
    if accounts:
        table = pd.DataFrame(accounts)[["firstName", "lastName", "email", "status", "kycStatus", "balance"]]
        st.dataframe(table)
    else:
        st.info("Noch keine Konten vorhanden.")

elif page == "Konto anlegen":
    st.header("Neues Konto anlegen")
    with st.form("create"):
        first_name = st.text_input("Vorname")
        last_name = st.text_input("Nachname")
        email = st.text_input("E-Mail")
        phone = st.text_input("Telefon (E.164)", value="+43")
        birth_date = st.date_input("Geburtsdatum", value=datetime.date(2000, 1, 1),
                                   min_value=datetime.date(1900, 1, 1))
        tax_number = st.text_input("Steuernummer (9 Ziffern)")
        citizenship = st.text_input("Staatsbürgerschaft (ISO, z. B. AT)", value="AT")
        submitted = st.form_submit_button("Anlegen")

    if submitted:
        try:
            account = api.create_account({
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "phoneNumber": phone,
                "birthDate": birth_date.isoformat(),
                "taxNumber": tax_number,
                "citizenship": citizenship,
            })
            st.success(f"Konto angelegt: {account_label(account)}")
        except api.ApiError as e:
            show_error(e)

elif page == "Konto verwalten":
    st.header("Konto verwalten")
    accounts = load_accounts()
    if not accounts:
        st.info("Noch keine Konten vorhanden.")
        st.stop()

    account = st.selectbox("Konto", accounts, format_func=account_label)
    st.metric("Guthaben", f"{account['balance']:.2f} €")
    st.caption(f"Status: {account['status']} · KYC: {account['kycStatus']} · ID: {account['id']}")

    st.subheader("Ein- und Auszahlung")
    amount = st.number_input("Betrag (€)", min_value=0.01, value=100.0, step=10.0)
    col1, col2 = st.columns(2)
    if col1.button("Einzahlen"):
        try:
            api.deposit(account["id"], amount)
            st.rerun()
        except api.ApiError as e:
            show_error(e)
    if col2.button("Abheben"):
        try:
            api.withdraw(account["id"], amount)
            st.rerun()
        except api.ApiError as e:
            show_error(e)

    st.subheader("Daten ändern")
    with st.form("update"):
        first_name = st.text_input("Vorname", account["firstName"])
        last_name = st.text_input("Nachname", account["lastName"])
        email = st.text_input("E-Mail", account["email"])
        phone = st.text_input("Telefon", account["phoneNumber"])
        kyc_options = ["Pending", "Verified", "Rejected"]
        kyc = st.selectbox("KYC-Status", kyc_options, index=kyc_options.index(account["kycStatus"]))
        status_options = ["Active", "Suspended", "Closed"]
        status = st.selectbox("Konto-Status", status_options, index=status_options.index(account["status"]))
        if st.form_submit_button("Speichern"):
            try:
                api.update_account(account["id"], {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "phoneNumber": phone,
                    "kycStatus": kyc,
                    "status": status,
                })
                st.rerun()
            except api.ApiError as e:
                show_error(e)

    st.subheader("Konto löschen")
    if st.button("🗑️ Konto löschen", type="primary"):
        try:
            api.delete_account(account["id"])
            st.rerun()
        except api.ApiError as e:
            show_error(e)

elif page == "Kaufkraft":
    st.header("Wie viel Krypto kann ich mir leisten?")
    accounts = load_accounts()
    if not accounts:
        st.info("Noch keine Konten vorhanden.")
        st.stop()

    account = st.selectbox("Konto", accounts, format_func=account_label)
    symbol = st.selectbox("Coin", ["BTC", "ETH", "SOL"])
    if st.button("Berechnen"):
        try:
            result = api.buying_power(account["id"], symbol)
            col1, col2, col3 = st.columns(3)
            col1.metric("Kurs", f"{result['priceEur']:,.2f} €")
            col2.metric("Guthaben", f"{result['balanceEur']:,.2f} €")
            col3.metric("Kaufbar", f"{result['quantity']} {result['symbol']}")
        except api.ApiError as e:
            show_error(e)
