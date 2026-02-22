from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

product_data = {
    "status": None,
    "device_name": None,
    "Recall Cause": None,
}

users = {}
usernames = set()
next_user_id = 1


def fetch_data(PRODUCT_CODE):
    url = f"https://api.fda.gov/device/recall.json?search=product_code:{PRODUCT_CODE}&limit=1"
    print(url)
    response = httpx.get(url)
    response_dict = response.json()

    product_data["status"] = response_dict.get("results")[0].get("recall_status")
    product_data["device_name"] = response_dict.get("results")[0].get("openfda").get("device_name")
    product_data["Recall Cause"] = response_dict.get("results")[0].get("root_cause_description")

    print(f"updated current data with {product_data}")
    return product_data


@app.get("/data/{product_code}")
async def get_product_data(product_code):
    product_data = fetch_data(product_code)
    return product_data


@app.get("/data")
async def enter_data():
    info = f"""Enter product code in search bar users: {users}"""
    return info


@app.post("/accounts", status_code=201)
async def create_account(payload: dict):
    global next_user_id

    username = payload.get("username")
    if not isinstance(username, str) or not username.strip():
        raise HTTPException(status_code=400, detail="username is required")

    if username in usernames:
        raise HTTPException(status_code=409, detail="Username already exists")

    user_id = next_user_id
    next_user_id += 1

    users[user_id] = {
        "id": user_id,
        "username": username,
        "notes": [],
    }
    usernames.add(username)
    return {"id": user_id, "username": username}


@app.get("/accounts/{account_id}")
async def get_account(account_id: int):
    account = users.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"id": account["id"], "username": account["username"]}


@app.post("/accounts/{account_id}/notes", status_code=201)
async def add_note(account_id: int, payload: dict):
    account = users.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="text is required")

    account["notes"].append(text)
    return {"account_id": account_id, "note_count": len(account["notes"])}


@app.get("/accounts/{account_id}/notes")
async def get_notes(account_id: int):
    account = users.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {"account_id": account_id, "notes": account["notes"]}
