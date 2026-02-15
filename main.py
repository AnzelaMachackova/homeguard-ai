import json
from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


# define data model for simulation
class DeviceQuery(BaseModel):
    device: str
    room: str = "everywhere"


# Load knowledge base from JSON file
KNOWLEDGE_FILE = Path(__file__).parent / "home_knowledge.json"
with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
    HOME_KNOWLEDGE = json.load(f)


def search_knowledge(query: str) -> str:
    query = query.lower()
    for category, items in HOME_KNOWLEDGE.items():
        for key, info in items.items():
            if key in query:
                return info
    return "Sorry, but I don't have this information in house database."


@app.get("/")
def read_root():
    return {"status": "Homeguard API is running"}


@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()

        # Debug logging
        print("=== WEBHOOK DEBUG ===")
        print(f"Full payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        intent_info = payload.get("intentInfo", {})
        parameters = intent_info.get("parameters", {})
        intent_name = intent_info.get("displayName", "")

        print(f"Intent: {intent_name}")
        print(f"Parameters: {json.dumps(parameters, indent=2, ensure_ascii=False)}")

        # Map intent names to HOME_KNOWLEDGE categories
        intent_to_category = {
            "pece_o_rostlinu": "rostliny",
            "pece_o_zvirata": "zvířata",
            "udrzba_domacnosti": "údržba",
            "pece_o_spotrebic": "spotřebiče",  # if you add this later
        }

        # Map Dialogflow parameters to HOME_KNOWLEDGE categories
        param_to_category = {
            "rostlina": "rostliny",
            "spotrebic": "spotřebiče",
            "zvire": "zvířata",
            "udrzba": "údržba",
        }

        identified_item = ""
        found_category = ""
        is_general_query = False

        # try to determine category from intent name
        if intent_name in intent_to_category:
            found_category = intent_to_category[intent_name]
            print(f"Category determined from intent: {found_category}")

        # General category terms that indicate non-specific queries
        general_terms = [
            "rostlina",
            "rostliny",
            "zvíře",
            "zvířata",
            "zvire",
            "spotřebič",
            "spotřebiče",
            "spotrebic",
            "údržba",
            "udrzba",
        ]

        # Try to find specific item from parameters
        for param_name, category_name in param_to_category.items():
            param_value = parameters.get(param_name, {})
            resolved_value = param_value.get("resolvedValue")

            # Check if parameter was triggered but has no specific value
            if param_name in parameters and not resolved_value:
                found_category = category_name
                is_general_query = True
                break

            if resolved_value:
                if isinstance(resolved_value, list) and len(resolved_value) > 0:
                    identified_item = str(resolved_value[0]).lower()
                else:
                    identified_item = str(resolved_value).lower()

                # Check if the identified item is just a general category term
                if identified_item in general_terms:
                    found_category = category_name
                    is_general_query = True
                    identified_item = ""
                    break

                found_category = category_name
                break

        # Debug: Print what was identified
        print(f"Identified item: '{identified_item}'")
        print(f"Found category: '{found_category}'")
        print(f"Is general query: {is_general_query}")
        print("===================")

        # Handle general queries - prompt user to be more specific
        if is_general_query and found_category:
            available_items = list(HOME_KNOWLEDGE.get(found_category, {}).keys())
            items_list = ", ".join(available_items)
            answer = f"Můžeš být konkrétnější? Vybírej z: {items_list}."
        elif identified_item and found_category:
            # Search in the corresponding category
            answer = HOME_KNOWLEDGE.get(found_category, {}).get(
                identified_item,
                f"O této položce ({identified_item}) fakt nic nevím.",
            )
        else:
            # TODO: fix fallback logic in Dialogflow - too many intents
            query_text = payload.get("text", "")
            if not query_text:
                # Try alternative paths for query text
                query_result = payload.get("queryResult", {})
                query_text = query_result.get("queryText", "")

            print(f"Fallback: Searching for keywords in: '{query_text}'")

            if query_text:
                answer = search_knowledge(query_text)

                # If keyword search still didn't find anything, and we have a category
                # suggest items from that category
                if (
                    answer
                    == "Sorry, but I don't have this information in house database."
                    and found_category
                ):
                    available_items = list(
                        HOME_KNOWLEDGE.get(found_category, {}).keys()
                    )
                    items_list = ", ".join(available_items)
                    answer = f"Můžeš být konkrétnější? Vybírej z: {items_list}."
            else:
                answer = "Soráček, ale nerozumím, o čem mluvíme."

        return {"fulfillment_response": {"messages": [{"text": {"text": [answer]}}]}}

    except Exception as e:
        print(f"Error in code: {e}")
        return {
            "fulfillment_response": {
                "messages": [{"text": {"text": ["Upsík, v mém kódu se něco rozbilo."]}}]
            }
        }
