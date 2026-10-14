import uuid
from datetime import datetime, timezone

import requests

BASE_URL = "http://localhost:5219"
API_KEY = "campus02-dev-key"
USE_MOCK = True  # auf False stellen, sobald die echte API läuft


class ApiError(Exception):
    """Fehler, den die API zurückgemeldet hat (Statuscode + lesbare Meldung)."""

    def __init__(self, status: int, message: str):
        super().__init__(f"{status}: {message}")
        self.status = status
        self.message = message


# ---------------------------------------------------------------- echte API

def _handle(response: requests.Response):
    """Antwort prüfen: bei Fehlern ApiError werfen, sonst JSON zurückgeben."""
    if response.status_code >= 400:
        message = response.reason
        try:
            body = response.json()
            if "errors" in body:  # 400 Validierungsfehler
                message = "; ".join(f"{field}: {', '.join(msgs)}" for field, msgs in body["errors"].items())
            else:  # Problem Details (404, 409, 422)
                message = body.get("detail") or body.get("title") or message
        except ValueError:
            pass  # kein JSON im Body (z. B. 401)
        raise ApiError(response.status_code, message)

    if response.status_code == 204:
        return None
    return response.json()


def _key_header():
    return {"X-Api-Key": API_KEY}


def _real_list_accounts():
    return _handle(requests.get(f"{BASE_URL}/api/v1/accounts"))


def _real_get_account(account_id):
    return _handle(requests.get(f"{BASE_URL}/api/v1/accounts/{account_id}"))


def _real_create_account(data):
    return _handle(requests.post(f"{BASE_URL}/api/v1/accounts", json=data))


def _real_update_account(account_id, data):
    return _handle(requests.put(f"{BASE_URL}/api/v1/accounts/{account_id}", json=data))


def _real_delete_account(account_id):
    return _handle(requests.delete(f"{BASE_URL}/api/v1/accounts/{account_id}"))


def _real_deposit(account_id, amount):
    return _handle(requests.post(f"{BASE_URL}/api/v1/accounts/{account_id}/deposit",
                                 json={"amount": amount}, headers=_key_header()))


def _real_withdraw(account_id, amount):
    return _handle(requests.post(f"{BASE_URL}/api/v1/accounts/{account_id}/withdraw",
                                 json={"amount": amount}, headers=_key_header()))


def _real_buying_power(account_id, symbol):
    return _handle(requests.get(f"{BASE_URL}/kaufkraft/{symbol}/{account_id}"))


# ---------------------------------------------------------------- Mock

_mock_accounts = {}
_MOCK_PRICES = {"BTC": 95000.0, "ETH": 3200.0, "SOL": 150.0}


def _mock_find(account_id):
    if account_id not in _mock_accounts:
        raise ApiError(404, "Not Found")
    return _mock_accounts[account_id]


def _mock_check_email_free(email, own_id=None):
    for acc in _mock_accounts.values():
        if acc["email"].lower() == email.lower() and acc["id"] != own_id:
            raise ApiError(409, "E-Mail wird bereits verwendet.")


def _mock_list_accounts():
    return list(_mock_accounts.values())


def _mock_get_account(account_id):
    return _mock_find(account_id)


def _mock_create_account(data):
    _mock_check_email_free(data["email"])
    account = {
        **data,
        "id": str(uuid.uuid4()),
        "kycStatus": "Pending",
        "status": "Active",
        "balance": 0,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    _mock_accounts[account["id"]] = account
    return account


def _mock_update_account(account_id, data):
    account = _mock_find(account_id)
    _mock_check_email_free(data["email"], own_id=account_id)
    account.update(data)
    return account


def _mock_delete_account(account_id):
    account = _mock_find(account_id)
    if account["balance"] != 0:
        raise ApiError(409, "Konto kann nur mit Guthaben 0 gelöscht werden.")
    del _mock_accounts[account_id]


def _mock_deposit(account_id, amount):
    account = _mock_find(account_id)
    if account["status"] != "Active":
        raise ApiError(422, "Konto ist nicht aktiv.")
    account["balance"] += amount
    return account


def _mock_withdraw(account_id, amount):
    account = _mock_find(account_id)
    if account["status"] != "Active":
        raise ApiError(422, "Konto ist nicht aktiv.")
    if amount > account["balance"]:
        raise ApiError(422, "Nicht genug Guthaben.")
    account["balance"] -= amount
    return account


def _mock_buying_power(account_id, symbol):
    account = _mock_find(account_id)
    price = _MOCK_PRICES.get(symbol.upper())
    if price is None:
        raise ApiError(404, f"Coin '{symbol.upper()}' ist unbekannt.")
    return {
        "accountId": account_id,
        "symbol": symbol.upper(),
        "priceEur": price,
        "balanceEur": account["balance"],
        "quantity": round(account["balance"] / price, 8),
    }


# ---------------------------------------------------------------- öffentliche Funktionen

list_accounts = _mock_list_accounts if USE_MOCK else _real_list_accounts
get_account = _mock_get_account if USE_MOCK else _real_get_account
create_account = _mock_create_account if USE_MOCK else _real_create_account
update_account = _mock_update_account if USE_MOCK else _real_update_account
delete_account = _mock_delete_account if USE_MOCK else _real_delete_account
deposit = _mock_deposit if USE_MOCK else _real_deposit
withdraw = _mock_withdraw if USE_MOCK else _real_withdraw
buying_power = _mock_buying_power if USE_MOCK else _real_buying_power
