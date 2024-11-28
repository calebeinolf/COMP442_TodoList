let mediaRecorder = null;
let audioChunks = [];
let recording = false;
document.addEventListener("DOMContentLoaded", async () => {
    loadTasks();
    const addTaskButton = (document.getElementById("add-task-btn"));
    addTaskButton.addEventListener("click", postTask);
    const detailsPanel = (document.getElementById("task-details-container"));
    const closeDetailsBtn = (document.getElementById("close-details-btn"));
    closeDetailsBtn.addEventListener("click", () => detailsPanel.classList.remove("open"));
    const askAIButton = (document.getElementById("ask_ai_button"));
    askAIButton.addEventListener("click", aiButtonClicked);
    const closeModalBtn = (document.getElementById("closeAIModal"));
    const submitModalBtn = (document.getElementById("submitAIModal"));
    closeModalBtn.addEventListener("click", closeAIModal);
    submitModalBtn.addEventListener("click", submitAIModal);
    const speechBtn = document.getElementById("speechToText");
    speechBtn.addEventListener("click", () => {
        if (recording) {
            stopRecording();
        }
        else {
            startRecording();
        }
        recording = !recording;
    });
    const themeBtn = document.getElementById("theme-btn");
    themeBtn.addEventListener("click", () => document.body.style.setProperty("--primary-color", randomColor()));
});
function randomColor() {
    const letters = "0123456789ABCDEF";
    let color = "#";
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
async function startRecording() {
    try {
        const permission = await navigator.mediaDevices.getUserMedia({
            audio: true,
        });
        mediaRecorder = new MediaRecorder(permission);
        audioChunks = [];
        mediaRecorder.ondataavailable = (recordingSesh) => {
            audioChunks.push(recordingSesh.data);
        };
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            sendAudioToFlask(audioBlob);
        };
        mediaRecorder.start();
        const speechBtn = (document.getElementById("speechToText"));
        speechBtn.textContent = "Stop Recording";
    }
    catch (e) {
        console.log("Error using mic");
    }
}
async function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        const speechBtn = (document.getElementById("speechToText"));
        speechBtn.textContent = "Talk to our AI";
    }
}
async function sendAudioToFlask(audioBlob) {
    try {
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.webm");
        const response = await fetch("/speech_for_gpt", {
            method: "POST",
            body: formData,
        });
        const data = await validatejson(response);
        console.log(data);
    }
    catch (e) {
        console.log("Error sending audio");
    }
}
async function loadTasks() {
    console.log("Loading Tasks");
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
            if (task.duedate) {
                task.duedate = new Date(task.duedate);
            }
            appendTask(task);
        }
    }
    catch (error) {
        console.error("Error fetching tasks:", error);
    }
}
async function postTask() {
    const taskTitleInput = (document.getElementById("task-title-input"));
    if (taskTitleInput.value !== "") {
        const taskTitle = taskTitleInput.value;
        const task = {
            name: taskTitle,
            duedate: new Date().getTime(),
            complete: false,
            starred: false,
        };
        taskTitleInput.value = "";
        const taskPostURL = "/postUserTask/";
        const response = await fetch(taskPostURL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(task),
        });
        const serverTask = await validatejson(response);
        console.log(serverTask);
        appendTask(serverTask);
    }
}
async function appendTask(task) {
    const today = new Date();
    let listId = "due-today-list";
    let duedate = null;
    if (task.duedate) {
        duedate = new Date(task.duedate);
        if (isSameDay(duedate, today)) {
            listId = "due-today-list";
        }
        else if (duedate < today) {
            listId = "overdue-list";
        }
        else {
            listId = "upcoming-list";
        }
    }
    const taskList = document.getElementById(listId);
    createTaskCard(taskList, task);
}
function createTaskCard(div, task) {
    const card = document.createElement("div");
    card.className = "card hoverCard";
    card.id = `task-${task.id}`;
    div.appendChild(card);
    const checkIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    checkIcon.id = `checkIcon-${task.id}`;
    if (task.complete) {
        filledCheckIcon(checkIcon);
    }
    else {
        emptyCheckIcon(checkIcon);
    }
    card.appendChild(checkIcon);
    const taskContent = document.createElement("div");
    taskContent.className = "task-content";
    card.appendChild(taskContent);
    const heading = document.createElement("h3");
    heading.textContent = task.name;
    taskContent.appendChild(heading);
    const taskInfo = document.createElement("div");
    taskInfo.className = "task-info";
    taskContent.appendChild(taskInfo);
    const listText = document.createElement("p");
    listText.textContent = `List${task.duedate !== null ? " • " : ""}`;
    taskInfo.appendChild(listText);
    if (task.duedate !== null) {
        const calendarSVG = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        calendarSVG.setAttribute("viewBox", "0 0 28 28");
        calendarSVG.setAttribute("width", "14px");
        const calendarPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
        calendarPath.setAttribute("d", "M22.611,3.182H20.455V2a1,1,0,0,0-2,0V3.182H9.545V2a1,1,0,0,0-2,0V3.182H5.389A4.394,4.394,0,0,0,1,7.571v15.04A4.394,4.394,0,0,0,5.389,27H22.611A4.394,4.394,0,0,0,27,22.611V7.571A4.394,4.394,0,0,0,22.611,3.182Zm-17.222,2H7.545V6.364a1,1,0,0,0,2,0V5.182h8.91V6.364a1,1,0,1,0,2,0V5.182h2.156A2.391,2.391,0,0,1,25,7.571V9.727H3V7.571A2.391,2.391,0,0,1,5.389,5.182ZM22.611,25H5.389A2.392,2.392,0,0,1,3,22.611V11.727H25V22.611A2.392,2.392,0,0,1,22.611,25Z");
        calendarPath.setAttribute("fill", "#616161");
        calendarSVG.appendChild(calendarPath);
        const dateText = document.createElement("p");
        dateText.textContent = formatDate(new Date(task.duedate));
        taskInfo.appendChild(calendarSVG);
        taskInfo.appendChild(dateText);
    }
    const rightStarSVG = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    rightStarSVG.id = `starIcon-${task.id}`;
    rightStarSVG.setAttribute("class", "right-icon");
    rightStarSVG.setAttribute("width", "20px");
    rightStarSVG.setAttribute("viewBox", "0 0 17 16");
    if (task.starred) {
        rightStarSVG.setAttribute("fill", "var(--primary-color)");
    }
    else {
        rightStarSVG.setAttribute("fill", "none");
    }
    card.appendChild(rightStarSVG);
    const starPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    starPath.setAttribute("d", "M8.95126 1.1067L10.5511 4.45952C10.7698 4.91778 11.2055 5.23431 11.7089 5.30067L15.392 5.78617C15.809 5.84113 15.9759 6.35497 15.6709 6.64452L12.9766 9.20218C12.6083 9.55176 12.4419 10.0639 12.5343 10.5632L13.2108 14.2161C13.2873 14.6296 12.8502 14.9472 12.4806 14.7466L9.21552 12.9744C8.76925 12.7322 8.23075 12.7322 7.78448 12.9744L4.5194 14.7466C4.14977 14.9472 3.71268 14.6296 3.78925 14.2161L4.46565 10.5632C4.5581 10.0639 4.3917 9.55176 4.02344 9.20218L1.3291 6.64451C1.02409 6.35497 1.19104 5.84113 1.608 5.78617L5.29112 5.30067C5.79452 5.23431 6.23018 4.91778 6.44885 4.45952L8.04874 1.10669C8.22986 0.727135 8.77014 0.727133 8.95126 1.1067Z");
    starPath.setAttribute("stroke", "var(--primary-color)");
    rightStarSVG.appendChild(starPath);
    card.addEventListener("click", () => openDetails(task));
    checkIcon.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleComplete(task);
    });
    rightStarSVG.addEventListener("click", (event) => {
        event.stopPropagation();
        toggleStarred(task);
    });
}
function openDetails(task) {
    const detailsPanel = (document.getElementById("task-details-container"));
    detailsPanel.classList.add("open");
    document.getElementById("details-task-name").innerText = task.name;
    if (task.duedate !== null) {
        document.getElementById("details-task-duedate").innerText = formatDate(new Date(task.duedate));
    }
    else {
        document.getElementById("details-task-duedate").innerText = "";
    }
}
async function toggleComplete(task) {
    const response = await fetch(`/markComplete/${task.id}/${task.complete ? "0" : "1"}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    });
    const r = await validatejson(response);
    console.log(r);
    task.complete = !task.complete;
    const checkIcon = document.getElementById(`checkIcon-${task.id}`);
    if (checkIcon instanceof SVGElement) {
        if (task.complete) {
            filledCheckIcon(checkIcon);
        }
        else {
            emptyCheckIcon(checkIcon);
        }
    }
    else {
        console.error("The element is not an SVGElement");
    }
}
async function toggleStarred(task) {
    const response = await fetch(`/markStarred/${task.id}/${task.starred ? "0" : "1"}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
    });
    const r = await validatejson(response);
    console.log(r);
    task.starred = !task.starred;
    const starIcon = document.getElementById(`starIcon-${task.id}`);
    if (task.starred) {
        starIcon.setAttribute("fill", "var(--primary-color)");
    }
    else {
        starIcon.setAttribute("fill", "none");
    }
}
function isSameDay(date1, date2) {
    return (date1.getFullYear() === date2.getFullYear() &&
        date1.getMonth() === date2.getMonth() &&
        date1.getDate() === date2.getDate());
}
function formatDate(date) {
    if (isSameDay(date, new Date())) {
        return "Today";
    }
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
    const dayOfWeek = days[date.getDay()];
    const month = months[date.getMonth()];
    const dayOfMonth = date.getDate();
    return `${dayOfWeek}, ${month} ${dayOfMonth}`;
}
async function aiButtonClicked() {
    console.log("Clicked");
    const modal = document.getElementById("aiModal");
    modal.style.display = "block";
}
async function closeAIModal() {
    const modal = document.getElementById("aiModal");
    modal.style.display = "none";
}
async function submitAIModal() {
    const modal = document.getElementById("aiModal");
    modal.style.display = "none";
    await askChatGPT();
}
async function askChatGPT() {
    const textField = (document.getElementById("aiPromtTextField"));
    const input = textField.value;
    textField.value = "";
    console.log(`input before chatGPT: ${input}`);
    const types = ["Family", "Work", "Personal"];
    const response = await getChatGPTResponse(input, types);
    console.log(`starred: ${response.GPTResponse.tasks[0].starred}\nname: ${response.GPTResponse.tasks[0].name}\ndue_date: ${response.GPTResponse.tasks[0].duedate}\n`);
}
async function getChatGPTResponse(question, types) {
    console.log("Trying ChatGPT");
    const params = new URLSearchParams({
        question: question,
        types: types.join(","),
    });
    try {
        const response = await fetch(`/askChatGPT?${params.toString()}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await validatejson(response);
        return data;
    }
    catch (error) {
        console.error("Error fetching data:", error);
    }
}
function validatejson(response) {
    if (response.ok) {
        return response.json();
    }
    else {
        return Promise.reject(response);
    }
}
function filledCheckIcon(checkIcon) {
    checkIcon.setAttribute("class", "circle left-icon");
    checkIcon.setAttribute("viewBox", "0 0 408.576 408.576");
    checkIcon.style.setProperty("enable-background", "new 0 0 408.576 408.576");
    checkIcon.setAttribute("xml:space", "preserve");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("fill", "var(--primary-color)");
    path.setAttribute("d", "M204.288,0C91.648,0,0,91.648,0,204.288s91.648,204.288,204.288,204.288s204.288-91.648,204.288-204.288S316.928,0,204.288,0z M318.464,150.528l-130.56,129.536c-7.68,7.68-19.968,8.192-28.16,0.512L90.624,217.6c-8.192-7.68-8.704-20.48-1.536-28.672c7.68-8.192,20.48-8.704,28.672-1.024l54.784,50.176L289.28,121.344c8.192-8.192,20.992-8.192,29.184,0C326.656,129.536,326.656,142.336,318.464,150.528z");
    checkIcon.appendChild(path);
}
function emptyCheckIcon(checkIcon) {
    checkIcon.setAttribute("class", "circle left-icon");
    checkIcon.setAttribute("viewBox", "0 0 15 15");
    checkIcon.setAttribute("fill", "none");
    checkIcon.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", "7.5");
    circle.setAttribute("cy", "7.5");
    circle.setAttribute("r", "7");
    circle.setAttribute("stroke", "var(--primary-color)");
    checkIcon.appendChild(circle);
    const checkmarkPath = document.createElementNS("http://www.w3.org/2000/svg", "path");
    checkmarkPath.setAttribute("d", "M6.8985 10.2819L11.6917 5.52631C11.9925 5.22556 11.9925 4.75563 11.6917 4.45488C11.391 4.15412 10.921 4.15412 10.6203 4.45488L6.33459 8.74059L4.3233 6.89849C4.02255 6.61654 3.55264 6.63533 3.27069 6.93608C3.0075 7.23684 3.0263 7.70676 3.32705 7.98871L5.86465 10.3007C6.1654 10.5827 6.61654 10.5639 6.8985 10.2819Z");
    checkmarkPath.setAttribute("fill", "var(--primary-color)");
    checkmarkPath.style.display = "none";
    checkIcon.appendChild(checkmarkPath);
    checkIcon.addEventListener("mouseover", () => {
        checkmarkPath.style.display = "block";
    });
    checkIcon.addEventListener("mouseout", () => {
        checkmarkPath.style.display = "none";
    });
}
