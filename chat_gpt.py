"""_summary_
"""
from datetime import datetime
import sys
import json
import openai

from config import chatGPTSecretKey

class Old_Chat_GPT_Response:
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
    def toDict(self) -> dict:
        return{
            "starred": self.starred,
            "name": self.name,
            "description": self.description,
            "due_date": self.due_date,
            "due_time": self.due_time,
            "due_time_included": self.due_time_included,
            "type": self.type
        }

class Task:
    def __init__(self, name: str, starred: bool, duedate: str, priority: int, tasklistnames: list[str]):
        self.name: str = name
        self.starred: bool = starred
        
        fullDate = duedate.split(",")
        
        dates = (fullDate[0]).split("/")
        newDate = f"{dates[2]}-{dates[0]}-{dates[1]},{fullDate[1]}"
        self.duedate: str = newDate
        self.priority: int = priority
        self.tasklistnames: list[str] = tasklistnames
        
    def __str__(self):
        return(
            f"===\n"
            f"name: {self.name}, starred: {self.starred}, duedate: {self.duedate}, priority: {self.priority}\n"
            f"tasklistnames: {self.tasklistnames}"
            f"==="
            )
    
    def toDict(self) -> dict:
        return{
            "name": self.name,
            "starred": self.starred,
            "duedate": self.duedate,
            "priority": self.priority,
            "tasklistnames": ','.join(self.tasklistnames)
        }
        
    @staticmethod
    def fromDict(d: dict):
        return Task(d["name"], d["starred"], d["duedate"], d["priority"], d["tasklistnames"])

class SubTask:
    def __init__(self, name: str, priority: int, parenttaskname: str):
        self.name: str = name
        self.priority: int = priority
        self.parenttaskname: str = parenttaskname
        
    def __str__(self):
        return(f"***\nname: {self.name}, priotity: {self.priority}, parenttaskname: {self.parenttaskname}\n***")
    
    def toDict(self) -> dict:
        return{
            "name": self.name,
            "priority": self.priority,
            "parenttaskname": self.parenttaskname
        }
        
    @staticmethod
    def fromDict(d: dict):
        name: str = d["name"]
        priority: int = d["priority"]
        parenttaskname: str = d["parenttaskname"]
        return SubTask(name=name, priority=priority, parenttaskname=parenttaskname)
        

class TaskList:
    def __init__(self, name: str):
        self.name: str = name
        
    def __str__(self):
        return(f"###\nname: {self.name}\n###")
    
    def toDict(self) -> dict:
        return{
            "name": self.name
        }
        
    @staticmethod
    def fromDict(d: dict):
        return TaskList(d["name"])

class Chat_GPT_Response:
    def __init__(self, tasklists: list[TaskList], numtasklists: int, tasks: list[Task], numtasks: int, subtasks: list[SubTask], numsubtasks: int):
        self.tasklists: list[TaskList] = tasklists
        self.numtasklists: int = numtasklists
        self.tasks: list[Task] = tasks
        self.numtasks: int = numtasks
        self.subtasks: list[SubTask] = subtasks
        self.numsubtasks: int = numsubtasks
        
    def __str__(self):
        return(
            f"numtasklists: {self.numtasklists}\ntasklists: {self.tasklists}\n"
            f"numtasks: {self.numtasks}\ntasks: {self.tasks}\n"
            f"numsubtasks: {self.numsubtasks}\nsubtasks: {self.subtasks}"
        )
        
    def toDict(self) -> dict:
        newTaskLists: list[dict] = []
        for tasklist in self.tasklists:
            newTaskLists.append(tasklist.toDict())
            
        newtasks: list[dict] = []
        for task in self.tasks:
            newtasks.append(task.toDict())
            
        newsubtasks: list[dict] = []
        for subtask in self.subtasks:
            newsubtasks.append(subtask.toDict())
            
        return{
            "numtasklists": self.numtasklists,
            "tasklists": newTaskLists,
            "numtasks": self.numtasks,
            "tasks": newtasks,
            "numsubtasks": self.numsubtasks,
            "subtasks": newsubtasks
        }
        
    @staticmethod
    def from_json(json_data):
        data = json.loads(json_data)
        response: Chat_GPT_Response = Chat_GPT_Response(**data)
        
        tasklists: list[TaskList] = []
        for tasklist in response.tasklists:
            tasklists.append(TaskList.fromDict(tasklist))
            
        tasks: list[Task] = []
        for task in response.tasks:
            tasks.append(Task.fromDict(task))
            
        subtasks: list[SubTask] = []
        for subtask in response.subtasks:
            subtasks.append(SubTask.fromDict(subtask))
            
        return Chat_GPT_Response(
            tasklists=tasklists, 
            numtasklists=response.numtasklists, 
            tasks=tasks, 
            numtasks=response.numtasks, 
            subtasks=subtasks, 
            numsubtasks=response.numsubtasks)

def response_from_json(json_data):
    data = json.loads(json_data)
    return Chat_GPT_Response(**data)
class Chat_GPT:
    def __init__(self):
        self.promptEngineering: str = ""
        
        file_path = 'chatGPT_Content.txt'
        with open(file_path, 'r') as file:
            file_content = file.read()
        self.promptEngineering = file_content
        
        self.openai = openai
        self.openai.api_key = chatGPTSecretKey
        self.messages = [{
            "role": "system", 
            "content": self.promptEngineering
            }]
        
    def ask(self, question: str, types: list[str]) -> Old_Chat_GPT_Response:
        response: Chat_GPT_Response = self.newAsk(question, types, [])
        
        task: Task = response.tasks[0]
        
        full_date = task.duedate.split(",")
        
        
        due_date: str = full_date[0]
        due_time: str = full_date[1]
        due_time_included: bool = True
        
        reply: Old_Chat_GPT_Response = Old_Chat_GPT_Response(task.starred, task.name, "", due_date, due_time, due_time_included, task.tasklistnames[0])
        return reply
        
    def newAsk (self, question: str, taskLists: list[str], tasks: list[str]) -> Chat_GPT_Response:
        self.promptEngineering += f"\nHere is a list of all the tasks already in the app:\n{','.join(tasks)}"
        self.promptEngineering += f"\nHere is a list of all the task lists already in the app:\n{','.join(taskLists)}"
        
        self.messages = [{
            "role": "system", 
            "content": self.promptEngineering
            }]
        self.messages.append({
            "role": "user",
                "content": question
        })
        chat = openai.chat.completions.create(
            model="gpt-4o-mini", messages=self.messages
        )
        reply = chat.choices[0].message.content
        print(f"*********&&&&&&&&&&&************\n{reply}\n*********&&&&&&&&&&&************")
        if "json" in reply:
            reply = ((reply.strip("```")).split("json")[1]).strip()
        else :
            reply.strip("```")
        return Chat_GPT_Response.from_json(reply)

# def main():
#     question: str = "Can you create a new list called sport and add my sons hockey game for tomorrow at 4pm and my daughters tennis game thursday at 5pm, theyre kinda important to me. Also add my homework at 2pm as a tqask with the subtasks, read boo, and write book review"
#     print(f"Asking chatGPT:\n{question}")
#     taskLists: list[str] = {"family", "home", "work"}
#     tasks: list[str] = {"math homework", "laundry", "dentist appointment"}
#     chatGpt = Chat_GPT()
#     response: Chat_GPT_Response = chatGpt.newAsk(question, taskLists, tasks)
#     print(f"chatGPT response:\n{response}")
    
# main()