let mediaRecorder: MediaRecorder | null = null;
let audioChunks: BlobPart[] = []
let recording: boolean = false;

namespace gpt{
  export interface FullTaskList{
    name: string
  }

  export interface FullTask{
    name: string,
    starred: boolean,
    duedate: string,
    priority: number, 
    tasklistnames: string[]
  }

  export interface FullSubTask{
    name: string,
    priority: number, 
    parenttaskname: string
  }

  export interface ChatGPTResponse {
    tasklists: FullTaskList[],
    numtasklists: number,
    tasks: FullTask[],
    numtasks: number, 
    subtasks: FullSubTask[],
    numsubtasks: number
  }

  export interface ServerResponse {
    status: string,
    GPTResponse: ChatGPTResponse
  }
}

interface Task {
  id: number;
  name: string;
  complete: boolean;
  // lists: [string];
  duedate: Date;
}

document.addEventListener("DOMContentLoaded", async () => {
  console.log("hello");

  loadTasks();

  const addTaskButton = <HTMLButtonElement>(
    document.getElementById("add-task-btn")
  );
  addTaskButton.addEventListener("click", postTask);

  const detailsPanel = <HTMLDivElement>(
    document.getElementById("task-details-container")
  );
  const closeDetailsBtn = <HTMLButtonElement>(
    document.getElementById("close-details-btn")
  );
  closeDetailsBtn.addEventListener("click", () =>
    detailsPanel.classList.remove("open")
  );

  const askAIButton = <HTMLButtonElement>(
    document.getElementById("ask_ai_button")
  );
  askAIButton.addEventListener("click", aiButtonClicked);
  const closeModalBtn = <HTMLButtonElement>(
    document.getElementById("closeAIModal")
  );
  const submitModalBtn = <HTMLButtonElement>(
    document.getElementById("submitAIModal")
  );
  closeModalBtn.addEventListener("click", closeAIModal);
  submitModalBtn.addEventListener("click", submitAIModal);

  const speechBtn = <HTMLButtonElement> document.getElementById("speechToText");
  speechBtn.addEventListener("click", ()=> {
    if (recording){
      stopRecording();
    } else {
      startRecording();
    }
    recording = !recording
  });

});

async function startRecording() {
  try {
    const permission = await navigator.mediaDevices.getUserMedia({ audio:true })
    mediaRecorder = new MediaRecorder(permission);
    audioChunks = [];

    mediaRecorder.ondataavailable = (recordingSesh)=> {
      audioChunks.push(recordingSesh.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, {"type": "audio/webm"});
      sendAudioToFlask(audioBlob);
    };

    mediaRecorder.start();
    const speechBtn = <HTMLButtonElement> document.getElementById("speechToText");
    speechBtn.textContent = "Stop Recording";
  } catch (e){
    console.log("Error using mic")
  }
}

async function stopRecording() {
  if (mediaRecorder) {
    mediaRecorder.stop();
    const speechBtn = <HTMLButtonElement> document.getElementById("speechToText");
    speechBtn.textContent = "Talk to our AI"
  }
}

async function sendAudioToFlask(audioBlob: Blob) {
  try{
    const formData: FormData = new FormData;
    formData.append("file", audioBlob, "audio.webm");

    const response = await fetch("/speech_for_gpt", {
      method: "POST",
      body: formData
    });

    const data = <gpt.ServerResponse> await validatejson(response);
    console.log(data);
  } catch (e){
    console.log("Error sending audio")
  }

}

async function loadTasks() {
  // fetch user tasks from database

  console.log("Trying to load tasks");

  try {
    const response = await fetch(`/getUserTasks/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    const tasks = await validatejson(response);
    console.log(tasks);

    for (const task of tasks.tasks) {
      task.duedate = new Date(<string> task.duedate);
      appendTask(task);
    }
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
}

function postTask() {
  // just for testing, make random id:
  const randomInt = (min: number, max: number) =>
    Math.floor(Math.random() * (max - min + 1)) + min;
  const id = randomInt(0, 100);

  const task: Task = {
    id: id,
    name: "Example task " + id,
    complete: false,
    duedate: new Date(),
  };
  appendTask(task);
}

function appendTask(task: Task) {
  const today = new Date();//.toISOString().split("T")[0];
  console.log(`This is the duedate: ${task.duedate}`)
  const duedate = task.duedate;
  console.log(today);
  console.log(duedate);
  let listId = "";
  if (duedate < today) {
    listId = "overdue-list";
  } else if (duedate === today) {
    listId = "due-today-list";
  } else {
    listId = "upcoming-list";
  }
  console.log(listId);

  const taskList = document.getElementById(listId);
  const newTask = document.createElement("div");
  taskList.appendChild(newTask);
  console.log(task.duedate instanceof Date);
  newTask.innerHTML = `
    <div class="card" id="${task.id}">
              <svg class="circle left-icon" viewBox="0 0 15 15" fill="none">
                <circle cx="7.5" cy="7.5" r="7" stroke="var(--primary-color)" />
              </svg>
              <div class="task-content">
                <h3>
                  ${task.name}
                </h3>
                <div class="task-info">
                  <p>List</p>
                  
                  <p>•</p>
                  <svg viewBox="0 0 28 28" width="14px">
                    <path
                      d="M22.611,3.182H20.455V2a1,1,0,0,0-2,0V3.182H9.545V2a1,1,0,0,0-2,0V3.182H5.389A4.394,4.394,0,0,0,1,7.571v15.04A4.394,4.394,0,0,0,5.389,27H22.611A4.394,4.394,0,0,0,27,22.611V7.571A4.394,4.394,0,0,0,22.611,3.182Zm-17.222,2H7.545V6.364a1,1,0,0,0,2,0V5.182h8.91V6.364a1,1,0,1,0,2,0V5.182h2.156A2.391,2.391,0,0,1,25,7.571V9.727H3V7.571A2.391,2.391,0,0,1,5.389,5.182ZM22.611,25H5.389A2.392,2.392,0,0,1,3,22.611V11.727H25V22.611A2.392,2.392,0,0,1,22.611,25Z"
                      fill="#616161"
                    />
                  </svg>
                  <p>${formatDate(task.duedate)}</p>
                </div>
              </div>
              <svg
                class="right-icon"
                width="20px"
                viewBox="0 0 17 16"
                fill="none"
              >
                <path
                  d="M8.95126 1.1067L10.5511 4.45952C10.7698 4.91778 11.2055 5.23431 11.7089 5.30067L15.392 5.78617C15.809 5.84113 15.9759 6.35497 15.6709 6.64452L12.9766 9.20218C12.6083 9.55176 12.4419 10.0639 12.5343 10.5632L13.2108 14.2161C13.2873 14.6296 12.8502 14.9472 12.4806 14.7466L9.21552 12.9744C8.76925 12.7322 8.23075 12.7322 7.78448 12.9744L4.5194 14.7466C4.14977 14.9472 3.71268 14.6296 3.78925 14.2161L4.46565 10.5632C4.5581 10.0639 4.3917 9.55176 4.02344 9.20218L1.3291 6.64451C1.02409 6.35497 1.19104 5.84113 1.608 5.78617L5.29112 5.30067C5.79452 5.23431 6.23018 4.91778 6.44885 4.45952L8.04874 1.10669C8.22986 0.727135 8.77014 0.727133 8.95126 1.1067Z"
                  stroke="var(--primary-color)"
                />
              </svg>
            </div>
  `;
  newTask.addEventListener("click", () => openDetails(task));
}

function openDetails(task: Task) {
  const detailsPanel = <HTMLDivElement>(
    document.getElementById("task-details-container")
  );
  detailsPanel.classList.add("open");

  document.getElementById("details-task-name").innerText = task.name;
  console.log(`1. ${task.duedate instanceof Date}`)
  document.getElementById("details-task-duedate").innerText = formatDate(
    task.duedate
  );
}

function formatDate(date: Date): string {
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];

  console.log(date)
  const dayOfWeek = days[date.getDay()];
  console.log(dayOfWeek)
  const month = months[date.getMonth()];
  console.log(month)
  const dayOfMonth = date.getDate();
  console.log(dayOfMonth)

  return `${dayOfWeek}, ${month} ${dayOfMonth}`;
}

async function aiButtonClicked() {
  console.log("Clicked");
  const modal = <HTMLElement>document.getElementById("aiModal");
  modal.style.display = "block";
}

async function closeAIModal() {
  const modal = <HTMLElement>document.getElementById("aiModal");
  modal.style.display = "none";
}

async function submitAIModal() {
  const modal = <HTMLElement>document.getElementById("aiModal");
  modal.style.display = "none";
  await askChatGPT();
}

async function askChatGPT() {
  const textField = <HTMLInputElement>(
    document.getElementById("aiPromtTextField")
  );
  const input: string = textField.value;
  textField.value = "";
  console.log(`input before chatGPT: ${input}`);
  const types: string[] = ["Family", "Work", "Personal"];
  const response = <gpt.ServerResponse> await getChatGPTResponse(input, types);
  console.log(`starred: ${response.GPTResponse.tasks[0].starred}\nname: ${response.GPTResponse.tasks[0].name}\ndue_date: ${response.GPTResponse.tasks[0].duedate}\n`)
}

async function getChatGPTResponse(question: string, types: string[]){
  console.log("Trying ChatGPT")

  const params = new URLSearchParams({
    question: question,
    types: types.join(","),
  });

  try {
    const response = await fetch(
      `/askChatGPT?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const data = <gpt.ServerResponse> await validatejson(response);
    return data;
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

function validatejson(response: Response) {
  if (response.ok) {
    return response.json();
  } else {
    return Promise.reject(response);
  }
}
