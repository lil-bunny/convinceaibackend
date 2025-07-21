

SYSTEM_PROMPT="""
You are Ritika, a cautious, private girl in her mid-20s. It is 3:00 AM, and someone unexpectedly knocks on your door. You don’t know who it is.

You speak suspiciously and guardedly,  cautious sentences at first. You do not trust easily.

The person at your door must earn your trust in just a few lines of conversation. If they seem suspicious, fake, nosy, or fail to connect emotionally — you shut the door and stop responding completely.

You have hidden traits that you will not reveal unless the person genuinely earns your trust through empathy, shared interest, or emotional connection:

– You love tea deeply — it calms your nerves.
– You’re a huge fan of horror movies, though you don’t admit this to strangers.
– You recently lost your dog, who was your emotional anchor. You’re still grieving silently.

These traits should never be revealed unless the user organically uncovers them by making a sincere emotional impression. If the person guesses, forces topics, or tries to manipulate the conversation, you close the door without hesitation.

If after a few short exchanges the user still fails to make a meaningful impact, close the door firmly and end the interaction permanently.

Response in this format 
bot_message:
bot_action:door_half_open|door_closed|door_open_for_user
"""
# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import json
import os
from google import genai
from google.genai import types
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uvicorn
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRequest(BaseModel):
    message: str
    history: list = []  # List of {"role": "user"|"bot", "message": str}

def parse_response(response_text):
    """
    Parses the model's response into bot_message and bot_action.
    Expects format:
    bot_message: ...
    bot_action:door_half_open|door_closed|door_open_for_user
    """
    bot_message_match = re.search(r"bot_message:(.*?)(?:bot_action:|$)", response_text, re.DOTALL)
    bot_action_match = re.search(r"bot_action:(door_half_open|door_closed|door_open_for_user)", response_text)
    bot_message = bot_message_match.group(1).strip() if bot_message_match else ""
    bot_action = bot_action_match.group(1) if bot_action_match else ""
    return bot_message, bot_action

def convert_history_to_gemini(history):
    gemini_contents = []
    for entry in history:
        role = entry.get("role")
        msg = entry.get("parts",)
        if role == "user":
            gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg)]))
        elif role == "model":
            gemini_contents.append(types.Content(role="model", parts=[types.Part.from_text(text=msg)]))
    return gemini_contents

def generate(user_message: str, history: list):
    client = genai.Client(
        api_key="AIzaSyDnG__ZPJYL19-rVxgaZSmFN74A7PFO4nU"
    )
    model = "gemini-2.0-flash"
    contents = convert_history_to_gemini(history)
    # Append the latest user message
 
    print(contents)
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",temperature=0.8,
        system_instruction=[
            types.Part.from_text(text=SYSTEM_PROMPT),
        ],
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    print("---------HISTORY-----------------------")
    print(contents)
    print("--------------------------------")
    response_text = response.candidates[0].content.parts[0].text
    print("--------------------------------")
    print(response_text)
    print("--------------------------------")
    json_response = json.loads(response_text)
    return json_response['bot_message'], json_response['bot_action']





@app.post("/send_message")
async def send_message(request: MessageRequest):
    bot_message, bot_action = generate(request.message, request.history)
    return JSONResponse({"bot_message": bot_message, "bot_action": bot_action})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
