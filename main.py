from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


# define data model for simulation
class DeviceQuery(BaseModel):
    device: str
    room: str = "everywhere"


HOME_KNOWLEDGE = {
    "flowers": "Flowers are watered once a week, preferably on Monday morning.",
    "bathroom": "The bathroom is cleaned 3 times a week (Monday, Wednesday, Friday).",
    "books": "The books on shelf A were brought from Barcelona in 2022.",
    "wifi": "The password for the guest wifi is 'hellopassword1234'.",
}


def search_knowledge(query: str) -> str:
    query = query.lower()
    for key, info in HOME_KNOWLEDGE.items():
        if key in query:
            return info
    return "Sorry, but I don't have this information in house database."


@app.get("/")
def read_root():
    return {"status": "Homeguard API is running"}


@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    print(f"data: {payload}")

    query_text = ""
    if "queryResult" in payload:
        query_text = payload["queryResult"].get("queryText", "")
    elif "query" in payload:
        query_text = payload["query"]

    print(f"request: {query_text}")

    answer = search_knowledge(query_text)
    print(f"Answer: {answer}")

    response = {"fulfillment_response": {"messages": [{"text": {"text": [answer]}}]}}
    print(f"response: {response}")

    return response
