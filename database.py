def fetch_transactions(client, user_id):
    result = (
        client.table("transactions")
        .select("id, transaction_type, amount, category, description, date")
        .eq("user_id", user_id)
        .order("date", desc=True)
        .execute()
    )
    rows = result.data or []
    return [
        (
            row["id"],
            row["transaction_type"],
            float(row["amount"]),
            row["category"],
            row.get("description") or "",
            row["date"],
        )
        for row in rows
    ]


def add_transaction(client, transaction_type, amount, category,
                    description, transaction_date, user_id):
    client.table("transactions").insert({
        "transaction_type": transaction_type,
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": transaction_date,
        "user_id": user_id,
    }).execute()


def delete_transaction(client, transaction_id, user_id):
    client.table("transactions").delete().eq(
        "id", transaction_id
    ).eq("user_id", user_id).execute()


def get_all_users(client):
    result = (
        client.table("profiles")
        .select("id, username, role, status, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


def get_total_users(client):
    result = client.table("profiles").select("id", count="exact").execute()
    return result.count or 0


def set_user_status(client, target_user_id, new_status):
    result = client.rpc("set_user_status", {
        "target_user_id": target_user_id,
        "new_status": new_status,
    }).execute()
    return bool(result.data)