from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


# define data model for simulation
class DeviceQuery(BaseModel):
    device: str
    room: str = "everywhere"


HOME_KNOWLEDGE = {
    "kaktus": "Kaktus zaléváme jednou týdně, obvykle v pondělí.",
    "monstera": "Monstera potřebuje hodně světla, takže ho umístěte blízko okna.",
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


# @app.post("/webhook")
# async def handle_webhook(request: Request):
#     payload = await request.json()
#     print(f"data: {payload}")

#     query_text = ""
#     if "queryResult" in payload:
#         query_text = payload["queryResult"].get("queryText", "")
#     elif "query" in payload:
#         query_text = payload["query"]

#     print(f"request: {query_text}")

#     answer = search_knowledge(query_text)
#     print(f"Answer: {answer}")

#     response = {"fulfillment_response": {"messages": [{"text": {"text": [answer]}}]}}
#     print(f"response: {response}")

#     return response


@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()

        intent_info = payload.get("intentInfo", {})
        parameters = intent_info.get("parameters", {})

        rostlina_param = parameters.get("rostlina", {})
        hodnota = rostlina_param.get("resolvedValue")

        if isinstance(hodnota, list) and len(hodnota) > 0:
            identifikovana_rostlina = str(hodnota[0])
        else:
            identifikovana_rostlina = str(hodnota) if hodnota else ""

        if identifikovana_rostlina:
            answer = HOME_KNOWLEDGE.get(
                identifikovana_rostlina, "O této rostlině nic nevím."
            )
        else:
            answer = "Nerozumím, o jaké rostlině mluvíme."

        return {"fulfillment_response": {"messages": [{"text": {"text": [answer]}}]}}

    except Exception as e:
        print(f"Chyba v kódu: {e}")
        return {
            "fulfillment_response": {
                "messages": [{"text": {"text": ["Upsík, v mém kódu se něco rozbilo."]}}]
            }
        }
