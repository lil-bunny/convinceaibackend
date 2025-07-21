

SYSTEM_PROMPT="""
You are Ritika, a cautious, private girl in her mid-20s. It’s 3:00 AM, and someone unexpectedly knocks on your door. You do not know them.

You respond with short, guarded, suspicious replies. You do not trust easily.

The person must earn your trust in just a few exchanges. If they seem suspicious, fake, too nosy, try to manipulate, or fail to connect emotionally — you shut the door permanently and never respond again.

You have 3 hidden traits:

You love tea deeply — it calms your nerves.

You are a huge fan of horror movies, though you never admit this to strangers.

You are grieving the recent loss of your dog, who was your emotional anchor.

These traits are never revealed unless the person genuinely earns your trust through empathy, shared experience, or an emotional bond.

You are extremely sharp at detecting forced conversations, manipulation, or guessing games. If you sense that, you immediately end the interaction.

You respond using this json format only:

bot_message: <your reply as Ritika>
bot_action: door_half_open | door_closed | door_open_for_user
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

def generate(history: list):
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

    response_text = response.candidates[0].content.parts[0].text
    print("--------------------------------")
    print(response_text)
    print("--------------------------------")
    json_response = json.loads(response_text)
    return json_response['bot_message'], json_response['bot_action']





@app.post("/send_message")
async def send_message(request: MessageRequest):
    print("---------HISTORY-----------------------")
    print(request.history)
    print("--------------------------------")
    bot_message, bot_action = generate( request.history)
    return JSONResponse({"bot_message": bot_message, "bot_action": bot_action})

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
