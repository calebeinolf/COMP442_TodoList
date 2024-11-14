import openai
import json

from datetime import datetime
from config import chatGPTSecretKey

class Chat_GPT_Response:
    def __init__(self, starred: bool, name: str, description: str, due_date: str, due_time:str, due_time_included: bool, type: str):
        self.starred: bool = starred
        self.name: str = name
        self.description: str = description
        self.due_date: str = due_date
        self.due_time: str = due_time
        self.due_time_included: bool = due_time_included
        self.type: str = type
    def __str__(self):
        return(f"starred: {self.starred}\nname: {self.name}\ndescription: {self.description}\n"
               f"due_date: {self.due_date}\ndue_time: {self.due_time}\ndue_time_included: {self.due_time_included}\n"
               f"type: {self.type}")
def response_from_json(json_data):
    data = json.loads(json_data)
    return Chat_GPT_Response(**data)
class Chat_GPT:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = chatGPTSecretKey
        self.messages = [{
            "role": "system", 
            "content": "You are an api that takes in a string input of someone requesting to "
            "add an event to their to-do list. You always respond in Json format with the "
            "following objects: starred(Boolean, true if it was expressed that "
            "the event is important and false if not), name, description, due_date, "
            "due_time(Optional), due_time_included(Boolean representing if there is a "
            "Due_Time or not), type(Form a given list of Type)"
            }]
        
    def ask(self, question: str, types: list[str]) -> Chat_GPT_Response:
            oldMessages = self.messages
            message = question
            if message:
                self.messages.append({
                    "role": "user",
                    "content": message + "\n"
                    f"(Current date is: {datetime.now().strftime("%m/%d/%Y")})\n(Type list is: {", ".join(types)})"
                })
                chat = openai.chat.completions.create(
                    model="gpt-4o-mini", messages=self.messages
                )
                reply = chat.choices[0].message.content
                self.messages = oldMessages
                reply = ((reply.strip("```")).split("json")[1]).strip()
                return response_from_json(reply)
