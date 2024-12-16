let mediaRecorder = null;
let audioChunks = [];
let recording = false;
document.addEventListener("DOMContentLoaded", async () => {
  loadTasks();
  loadTaskLists();
  const taskListElement = document.getElementById("task_lists");
  taskListElement.style.height = "500px";
  const allTasksButton = document.getElementById("all-tasks-btn");
  allTasksButton.addEventListener("click", () => {
    backToAllTasks();
  });
  const aiAddTaskInput = document.getElementById("aiPromptTextField");
  aiAddTaskInput.addEventListener("keyup", (event) => {
    if (event.code === "Enter") {
      askChatGPT();
    }
  });
  const addTaskButton = document.getElementById("add-task-btn");
  addTaskButton.addEventListener("click", () => {
    const addTaskModal = document.getElementById("addTaskModal");
    addTaskModal.style.display = "flex";
  });
  const submitTaskBtn = document.getElementById("sumbit-task-btn");
  submitTaskBtn.addEventListener("click", () => {
    postTask();
    closeAddTaskModal();
  });
  const closeAddTaskModalBtn = document.getElementById("closeAddTaskModal");
  closeAddTaskModalBtn.addEventListener("click", closeAddTaskModal);
  const detailsPanel = document.getElementById("task-details-container");
  const closeDetailsBtn = document.getElementById("close-details-btn");
  closeDetailsBtn.addEventListener("click", () =>
    detailsPanel.classList.remove("open")
  );
  const speechBtn = document.getElementById("speechToText");
  speechBtn.addEventListener("click", () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
    recording = !recording;
  });
  const addTaskModal = document.getElementById("addTaskModal");
  window.addEventListener("click", function (event) {
    if (event.target === addTaskModal) {
      closeAddTaskModal();
    }
  });
  const aiIconBtn = document.getElementById("ai-icon");
  aiIconBtn.addEventListener("click", askChatGPT);
  const colorPickerInput = document.getElementById("colorInput");
  const primaryColor = await getPrimaryColor();
  document.body.style.setProperty("--primary-color", primaryColor);
  colorPickerInput.setAttribute("value", primaryColor);
  setPrimaryTextColor(primaryColor);
  let customColorPicked = false;
  colorPickerInput.addEventListener("input", () => {
    const customColorBtn = document.getElementById("custom-color-btn");
    if (customColorPicked) {
      customColorBtn.style.backgroundColor = colorPickerInput.value;
    } else {
      customColorBtn.style.display = "flex";
      customColorBtn.style.backgroundColor = colorPickerInput.value;
      customColorPicked = true;
    }
    changeThemeColor(customColorBtn, colorPickerInput.value);
  });
  colorPickerInput.addEventListener("blur", (event) => {
    postPrimaryColor(colorPickerInput.value);
  });
  const redBtn = document.getElementById("red-btn");
  redBtn.style.backgroundColor = "#e34242";
  redBtn.addEventListener("click", () => {
    const backgroundColor = rgbToHex(
      window.getComputedStyle(redBtn).backgroundColor
    );
    changeThemeColor(redBtn, backgroundColor);
    postPrimaryColor(backgroundColor);
  });
  const blueBtn = document.getElementById("blue-btn");
  blueBtn.style.backgroundColor = "#2662cb";
  blueBtn.addEventListener("click", () => {
    const backgroundColor = rgbToHex(
      window.getComputedStyle(blueBtn).backgroundColor
    );
    changeThemeColor(blueBtn, backgroundColor);
    postPrimaryColor(backgroundColor);
  });
  const greenBtn = document.getElementById("green-btn");
  greenBtn.style.backgroundColor = "#429b35";
  greenBtn.addEventListener("click", () => {
    const backgroundColor = rgbToHex(
      window.getComputedStyle(greenBtn).backgroundColor
    );
    changeThemeColor(greenBtn, backgroundColor);
    postPrimaryColor(backgroundColor);
  });
  const customColorBtn = document.getElementById("custom-color-btn");
  customColorBtn.addEventListener("click", () => {
    changeThemeColor(
      customColorBtn,
      rgbToHex(customColorBtn.style.backgroundColor)
    );
    postPrimaryColor(rgbToHex(customColorBtn.style.backgroundColor));
  });
  const colorBtns = document.getElementById("color-btns");
  let defaultColor = false;
  for (let i = 0; i < colorBtns.children.length - 1; i++) {
    const divChild = colorBtns.children[i];
    if (
      primaryColor.toLowerCase() ===
      rgbToHex(divChild.style.backgroundColor).toLowerCase()
    ) {
      colorBtns.children[i].classList.add("selected-color-btn");
      defaultColor = true;
    }
  }
  if (!defaultColor) {
    customColorBtn.style.display = "flex";
    customColorBtn.classList.add("selected-color-btn");
    customColorBtn.style.backgroundColor = colorPickerInput.value;
  }
  const paletteImg = document.getElementById("palette-img");
  const paletteColorBtns = document.getElementById("palette-color-btns");
  paletteImg.addEventListener("click", () => {
    if (paletteColorBtns.classList.contains("active")) {
      paletteColorBtns.classList.remove("active");
      document.getElementById("palette-icon").style.display = "flex";
      document.getElementById("colors-close-icon").style.display = "none";
      document.removeEventListener("click", handleOutsidePaletteClick);
    } else {
      document.getElementById("colors-close-icon").style.display = "flex";
      document.getElementById("palette-icon").style.display = "none";
      paletteColorBtns.classList.add("active");
      document.addEventListener("click", handleOutsidePaletteClick);
    }
  });
  const saveBtn = document.getElementById("task-details-save-btn");
  saveBtn.addEventListener("click", saveTaskFromDetailsPanel);
  const detailsPanelNameInput = document.getElementById(
    "details-task-name-input"
  );
  detailsPanelNameInput.addEventListener("keyup", (event) => {
    if (event.code === "Enter") {
      saveTaskFromDetailsPanel();
    }
  });
  loadTasks();
  loadTaskLists();
  const taskListElement = document.getElementById("task_lists");
  taskListElement.style.height = "500px";
  const allTasksButton = document.getElementById("all-tasks-btn");
  allTasksButton.addEventListener("click", () => {
    backToAllTasks();
  });
  const aiAddTaskInput = document.getElementById("aiPromptTextField");
  aiAddTaskInput.addEventListener("keyup", (event) => {
    if (event.code === "Enter") {
      askChatGPT();
    }
  });
  const addTaskButton = document.getElementById("add-task-btn");
  addTaskButton.addEventListener("click", () => {
    const addTaskModal = document.getElementById("addTaskModal");
    addTaskModal.style.display = "flex";
  });
  const submitTaskBtn = document.getElementById("sumbit-task-btn");
  submitTaskBtn.addEventListener("click", () => {
    postTask();
    closeAddTaskModal();
  });
  const closeAddTaskModalBtn = document.getElementById("closeAddTaskModal");
  closeAddTaskModalBtn.addEventListener("click", closeAddTaskModal);
  const detailsPanel = document.getElementById("task-details-container");
  const closeDetailsBtn = document.getElementById("close-details-btn");
  closeDetailsBtn.addEventListener("click", () =>
    detailsPanel.classList.remove("open")
  );
  const speechBtn = document.getElementById("speechToText");
  speechBtn.addEventListener("click", () => {
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
    recording = !recording;
  });
  const addTaskModal = document.getElementById("addTaskModal");
  window.addEventListener("click", function (event) {
    if (event.target === addTaskModal) {
      closeAddTaskModal();
    }
  });
  const aiIconBtn = document.getElementById("ai-icon");
  aiIconBtn.addEventListener("click", askChatGPT);
  const colorPickerInput = document.getElementById("colorInput");
  const primaryColor = await getPrimaryColor();
  document.body.style.setProperty("--primary-color", primaryColor);
  colorPickerInput.setAttribute("value", primaryColor);
  setPrimaryTextColor(primaryColor);
  let customColorPicked = false;
  colorPickerInput.addEventListener("input", () => {
    const customColorBtn = document.getElementById("custom-color-btn");
    if (customColorPicked) {
      customColorBtn.style.backgroundColor = colorPickerInput.value;
    } else {
      customColorBtn.style.display = "flex";
      customColorBtn.style.backgroundColor = colorPickerInput.value;
      customColorPicked = true;
    }
    changeThemeColor(customColorBtn, colorPickerInput.value);
  });
  colorPickerInput.addEventListener("blur", (event) => {
    postPrimaryColor(colorPickerInput.value);
  });
  const redBtn = document.getElementById("red-btn");
  redBtn.style.backgroundColor = "#e34242";
  redBtn.addEventListener("click", () => {
    const backgroundColor = rgbToHex(
      window.getComputedStyle(redBtn).backgroundColor
    );
    changeThemeColor(redBtn, backgroundColor);
    postPrimaryColor(backgroundColor);
  });
  const blueBtn = document.getElementById("blue-btn");
  blueBtn.style.backgroundColor = "#2662cb";
  blueBtn.addEventListener("click", () => {
    const backgroundColor = rgbToHex(
      window.getComputedStyle(blueBtn).backgroundColor
    );
    changeThemeColor(blueBtn, backgroundColor);
    postPrimaryColor(backgroundColor);
  });
  const greenBtn = document.getElementById("green-btn");
  greenBtn.style.backgroundColor = "#429b35";
  greenBtn.addEventListener("click", () => {
    const backgroundColor = rgbToHex(
      window.getComputedStyle(greenBtn).backgroundColor
    );
    changeThemeColor(greenBtn, backgroundColor);
    postPrimaryColor(backgroundColor);
  });
  const customColorBtn = document.getElementById("custom-color-btn");
  customColorBtn.addEventListener("click", () => {
    changeThemeColor(
      customColorBtn,
      rgbToHex(customColorBtn.style.backgroundColor)
    );
    postPrimaryColor(rgbToHex(customColorBtn.style.backgroundColor));
  });
  const colorBtns = document.getElementById("color-btns");
  let defaultColor = false;
  for (let i = 0; i < colorBtns.children.length - 1; i++) {
    const divChild = colorBtns.children[i];
    if (
      primaryColor.toLowerCase() ===
      rgbToHex(divChild.style.backgroundColor).toLowerCase()
    ) {
      colorBtns.children[i].classList.add("selected-color-btn");
      defaultColor = true;
    }
  }
  if (!defaultColor) {
    customColorBtn.style.display = "flex";
    customColorBtn.classList.add("selected-color-btn");
    customColorBtn.style.backgroundColor = colorPickerInput.value;
  }
  const paletteImg = document.getElementById("palette-img");
  const paletteColorBtns = document.getElementById("palette-color-btns");
  paletteImg.addEventListener("click", () => {
    if (paletteColorBtns.classList.contains("active")) {
      paletteColorBtns.classList.remove("active");
      document.getElementById("palette-icon").style.display = "flex";
      document.getElementById("colors-close-icon").style.display = "none";
      document.removeEventListener("click", handleOutsidePaletteClick);
    } else {
      document.getElementById("colors-close-icon").style.display = "flex";
      document.getElementById("palette-icon").style.display = "none";
      paletteColorBtns.classList.add("active");
      document.addEventListener("click", handleOutsidePaletteClick);
    }
  });
  const saveBtn = document.getElementById("task-details-save-btn");
  saveBtn.addEventListener("click", saveTaskFromDetailsPanel);
  const detailsPanelNameInput = document.getElementById(
    "details-task-name-input"
  );
  detailsPanelNameInput.addEventListener("keyup", (event) => {
    if (event.code === "Enter") {
      saveTaskFromDetailsPanel();
    }
  });
});
async function backToAllTasks() {
  console.log("backToAllTasks");
  const overdueSection = document.getElementById("overdue-list");
  const dueTodaySection = document.getElementById("due-today-list");
  const upcomingSection = document.getElementById("upcoming-list");
  let children = Array.from(overdueSection.children);
  children.forEach((child) => {
    if (child.tagName.toLowerCase() === "div") {
      overdueSection.removeChild(child);
    }
  });
  children = Array.from(dueTodaySection.children);
  children.forEach((child) => {
    if (child.tagName.toLowerCase() === "div") {
      dueTodaySection.removeChild(child);
    }
  });
  children = Array.from(upcomingSection.children);
  children.forEach((child) => {
    if (child.tagName.toLowerCase() === "div") {
      upcomingSection.removeChild(child);
    }
  });
  loadTasks();
  console.log("backToAllTasks");
  const overdueSection = document.getElementById("overdue-list");
  const dueTodaySection = document.getElementById("due-today-list");
  const upcomingSection = document.getElementById("upcoming-list");
  let children = Array.from(overdueSection.children);
  children.forEach((child) => {
    if (child.tagName.toLowerCase() === "div") {
      overdueSection.removeChild(child);
    }
  });
  children = Array.from(dueTodaySection.children);
  children.forEach((child) => {
    if (child.tagName.toLowerCase() === "div") {
      dueTodaySection.removeChild(child);
    }
  });
  children = Array.from(upcomingSection.children);
  children.forEach((child) => {
    if (child.tagName.toLowerCase() === "div") {
      upcomingSection.removeChild(child);
    }
  });
  loadTasks();
}
const handleOutsidePaletteClick = (event) => {
  const paletteContainer = document.getElementById("palette-container");
  if (paletteContainer && !paletteContainer.contains(event.target)) {
    const paletteColorBtns = document.getElementById("palette-color-btns");
    paletteColorBtns.classList.remove("active");
    document.getElementById("palette-icon").style.display = "flex";
    document.getElementById("colors-close-icon").style.display = "none";
  }
  const paletteContainer = document.getElementById("palette-container");
  if (paletteContainer && !paletteContainer.contains(event.target)) {
    const paletteColorBtns = document.getElementById("palette-color-btns");
    paletteColorBtns.classList.remove("active");
    document.getElementById("palette-icon").style.display = "flex";
    document.getElementById("colors-close-icon").style.display = "none";
  }
};
async function clearFlashedMessage(childDiv) {
  const fmcontainer = document.getElementById("error-messages");
  fmcontainer.removeChild(childDiv);
}
async function reloadflashedmessages() {
  const fmcontainer = document.getElementById("error-messages");
  fmcontainer.innerHTML = "";
  fmcontainer.innerText = "";
  const response = await fetch("/api/v0/getflashedmessages/");
  const flashedmessages = await validatejson(response);
  for (const fm of flashedmessages) {
    const div = document.createElement("div");
    div.setAttribute(
      "class",
      "alert alert-warning alert-dismissible fade show"
    );
    div.setAttribute("role", "alert");
    const btn = document.createElement("button");
    btn.setAttribute("type", "button");
    btn.setAttribute("class", "btn-close");
    btn.setAttribute("data-bd-dismiss", "alert");
    btn.setAttribute("aria-label", "Close");
    div.innerText = fm;
    div.appendChild(btn);
    fmcontainer.appendChild(div);
  }
}
async function getPrimaryColor() {
  const response = await fetch(`/getUserColor/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  });
  const r = await validatejson(response);
  return r.userColor;
  const response = await fetch(`/getUserColor/`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  });
  const r = await validatejson(response);
  return r.userColor;
}
async function postPrimaryColor(color) {
  const response = await fetch("/postUserColor/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(color),
  });
  const ServerResponse = await validatejson(response);
  const response = await fetch("/postUserColor/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(color),
  });
  const ServerResponse = await validatejson(response);
}
function rgbToHex(rgb) {
  const match = rgb.match(/\d+/g);
  if (!match || match.length < 3) return "";
  const r = parseInt(match[0], 10);
  const g = parseInt(match[1], 10);
  const b = parseInt(match[2], 10);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b)
    .toString(16)
    .slice(1)
    .toUpperCase()}`;
  const match = rgb.match(/\d+/g);
  if (!match || match.length < 3) return "";
  const r = parseInt(match[0], 10);
  const g = parseInt(match[1], 10);
  const b = parseInt(match[2], 10);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b)
    .toString(16)
    .slice(1)
    .toUpperCase()}`;
}
function changeThemeColor(div, color) {
  document.body.style.setProperty("--primary-color", color);
  setPrimaryTextColor(color);
  const colorPickerInput = document.getElementById("colorInput");
  colorPickerInput.setAttribute("value", color);
  const colorBtns = document.getElementById("color-btns");
  for (const child of colorBtns.children) {
    child.classList.remove("selected-color-btn");
  }
  div.classList.add("selected-color-btn");
  document.body.style.setProperty("--primary-color", color);
  setPrimaryTextColor(color);
  const colorPickerInput = document.getElementById("colorInput");
  colorPickerInput.setAttribute("value", color);
  const colorBtns = document.getElementById("color-btns");
  for (const child of colorBtns.children) {
    child.classList.remove("selected-color-btn");
  }
  div.classList.add("selected-color-btn");
}
function getLuminance(hexColor) {
  const hex = hexColor.replace(/^#/, "");
  if (hex.length !== 6) return 1;
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const rs = r / 255;
  const gs = g / 255;
  const bs = b / 255;
  const rsRGB =
    rs <= 0.03928 ? rs / 12.92 : Math.pow((rs + 0.055) / 1.055, 2.4);
  const gsRGB =
    gs <= 0.03928 ? gs / 12.92 : Math.pow((gs + 0.055) / 1.055, 2.4);
  const bsRGB =
    bs <= 0.03928 ? bs / 12.92 : Math.pow((bs + 0.055) / 1.055, 2.4);
  return 0.2126 * rsRGB + 0.7152 * gsRGB + 0.0722 * bsRGB;
  const hex = hexColor.replace(/^#/, "");
  if (hex.length !== 6) return 1;
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const rs = r / 255;
  const gs = g / 255;
  const bs = b / 255;
  const rsRGB =
    rs <= 0.03928 ? rs / 12.92 : Math.pow((rs + 0.055) / 1.055, 2.4);
  const gsRGB =
    gs <= 0.03928 ? gs / 12.92 : Math.pow((gs + 0.055) / 1.055, 2.4);
  const bsRGB =
    bs <= 0.03928 ? bs / 12.92 : Math.pow((bs + 0.055) / 1.055, 2.4);
  return 0.2126 * rsRGB + 0.7152 * gsRGB + 0.0722 * bsRGB;
}
function setPrimaryTextColor(color) {
  const luminance = getLuminance(color);
  if (luminance > 0.5) {
    document.body.style.setProperty("--primary-text-color", "black");
  } else {
    document.body.style.setProperty("--primary-text-color", "white");
  }
  const luminance = getLuminance(color);
  if (luminance > 0.5) {
    document.body.style.setProperty("--primary-text-color", "black");
  } else {
    document.body.style.setProperty("--primary-text-color", "white");
  }
}
function randomColor() {
  const letters = "0123456789ABCDEF";
  let color = "#";
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
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
      const spinner = document.getElementById("loading-spinner");
      spinner.style.display = "block";
      console.log("HELLLOOOO");
      await sendAudioToFlask(audioBlob);
      spinner.style.display = "none";
    };
    mediaRecorder.start();
    const speechBtn = document.getElementById("speechToText");
    speechBtn.textContent = "Stop Recording";
  } catch (e) {
    console.log("Error using mic");
  }
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
      const spinner = document.getElementById("loading-spinner");
      spinner.style.display = "block";
      console.log("HELLLOOOO");
      await sendAudioToFlask(audioBlob);
      spinner.style.display = "none";
    };
    mediaRecorder.start();
    const speechBtn = document.getElementById("speechToText");
    speechBtn.textContent = "Stop Recording";
  } catch (e) {
    console.log("Error using mic");
  }
}
async function stopRecording() {
  if (mediaRecorder) {
    mediaRecorder.stop();
    const speechBtn = document.getElementById("speechToText");
    speechBtn.textContent = "Talk to our AI";
  }
  if (mediaRecorder) {
    mediaRecorder.stop();
    const speechBtn = document.getElementById("speechToText");
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
    if (data.status === "error") {
      reloadflashedmessages();
    } else {
      for (const tasklist of data.GPTResponse.tasklists) {
        appendTaskList(tasklist);
      }
      for (const task of data.GPTResponse.tasks) {
        const dbTask = {
          id: task.id,
          name: task.name,
          complete: false,
          duedate: task.duedate * 1000,
          starred: task.starred,
          notes: "",
          tasklistnames: task.tasklistnames.split(","),
        };
        appendTask(dbTask);
      }
      for (const subtask of data.GPTResponse.subtasks) {
      }
      console.log(data);
    }
  } catch (e) {
    console.log("Error sending audio");
  }
}
async function loadTaskLists() {
  try {
    const response = await fetch("/getUserTaskLists/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    const taskLists = await validatejson(response);
    for (const taskList of taskLists.tasklists) {
      appendTaskList(taskList);
    }
  } catch (error) {
    console.error("Error fetching task lists:", error);
  }
  try {
    const response = await fetch("/getUserTaskLists/", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    const taskLists = await validatejson(response);
    for (const taskList of taskLists.tasklists) {
      appendTaskList(taskList);
    }
  } catch (error) {
    console.error("Error fetching task lists:", error);
  }
}
async function loadTasks() {
  console.log("Loading Tasks");
  try {
    const response = await fetch("/getUserTasks/", {
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
      openDetails(task);
    }
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
  console.log("Loading Tasks");
  try {
    const response = await fetch("/getUserTasks/", {
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
      openDetails(task);
    }
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
}
async function saveTaskFromDetailsPanel() {
  const titleInput = document.getElementById("details-task-name-input");
  const newTitle = titleInput.value;
  const duedateInput = document.getElementById("details-task-duedate-input");
  const inputValue = duedateInput.value;
  const [year, month, day] = inputValue.split("-");
  const newDuedate = new Date(`${year}-${month}-${day}T00:00:00`);
  const notesInput = document.getElementById("details-task-notes-input");
  const newNotes = notesInput.value;
  const detailsPanel = document.getElementById("task-details-container");
  const taskStub = {
    id: Number(detailsPanel.dataset.taskId),
    name: newTitle,
    duedate: newDuedate.getTime(),
    notes: newNotes,
  };
  const taskPostURL = "/updateUserTask/";
  const response = await fetch(taskPostURL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskStub),
  });
  const updatedTask = await validatejson(response);
  console.log(updatedTask);
  const oldTaskCard = document.getElementById(`task-${updatedTask.id}`);
  oldTaskCard.parentNode.removeChild(oldTaskCard);
  appendTask(updatedTask);
  const titleInput = document.getElementById("details-task-name-input");
  const newTitle = titleInput.value;
  const duedateInput = document.getElementById("details-task-duedate-input");
  const inputValue = duedateInput.value;
  const [year, month, day] = inputValue.split("-");
  const newDuedate = new Date(`${year}-${month}-${day}T00:00:00`);
  const notesInput = document.getElementById("details-task-notes-input");
  const newNotes = notesInput.value;
  const detailsPanel = document.getElementById("task-details-container");
  const taskStub = {
    id: Number(detailsPanel.dataset.taskId),
    name: newTitle,
    duedate: newDuedate.getTime(),
    notes: newNotes,
  };
  const taskPostURL = "/updateUserTask/";
  const response = await fetch(taskPostURL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(taskStub),
  });
  const updatedTask = await validatejson(response);
  console.log(updatedTask);
  const oldTaskCard = document.getElementById(`task-${updatedTask.id}`);
  oldTaskCard.parentNode.removeChild(oldTaskCard);
  appendTask(updatedTask);
}
async function postTask() {
  const taskTitleInput = document.getElementById("task-title-input");
  if (taskTitleInput.value !== "") {
    const taskTitle = taskTitleInput.value;
    const taskDuedateInput = document.getElementById("task-duedate-input");
    const taskDuedateValue = taskDuedateInput.value;
    const taskDuedateParts = taskDuedateValue.split("-");
    const taskDuedateDateObj = new Date(
      parseInt(taskDuedateParts[0], 10),
      parseInt(taskDuedateParts[1], 10) - 1,
      parseInt(taskDuedateParts[2], 10)
    );
    const taskDuedate = taskDuedateDateObj.getTime();
    const urlsps = new URLSearchParams();
    urlsps.append("name", taskTitle);
    urlsps.append(
      "duedate",
      `${taskDuedate ? taskDuedate : new Date().getTime()}`
    );
    urlsps.append("complete", "false");
    urlsps.append("starred", "false");
    const csrfinpele = document.createElement("div");
    csrfinpele.innerHTML = await (
      await fetch("/api/v0/getcsrftok/create/task")
    ).text();
    console.log(csrfinpele.innerHTML);
    urlsps.append(
      "csrf_token",
      csrfinpele.firstElementChild.getAttribute("value")
    );
    taskTitleInput.value = "";
    taskDuedateInput.value = "";
    const taskPostURL = "/postUserTask/";
    try {
      const response = await fetch(taskPostURL, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": urlsps.get("csrf_token"),
        },
        body: urlsps.toString(),
      });
      const servertask = await validatejson(response);
      console.log("task created: " + JSON.stringify(response));
      appendTask(servertask);
    } catch (error) {
      reloadflashedmessages();
      console.error(error);
    }
  }
  const taskTitleInput = document.getElementById("task-title-input");
  if (taskTitleInput.value !== "") {
    const taskTitle = taskTitleInput.value;
    const taskDuedateInput = document.getElementById("task-duedate-input");
    const taskDuedateValue = taskDuedateInput.value;
    const taskDuedateParts = taskDuedateValue.split("-");
    const taskDuedateDateObj = new Date(
      parseInt(taskDuedateParts[0], 10),
      parseInt(taskDuedateParts[1], 10) - 1,
      parseInt(taskDuedateParts[2], 10)
    );
    const taskDuedate = taskDuedateDateObj.getTime();
    const urlsps = new URLSearchParams();
    urlsps.append("name", taskTitle);
    urlsps.append(
      "duedate",
      `${taskDuedate ? taskDuedate : new Date().getTime()}`
    );
    urlsps.append("complete", "false");
    urlsps.append("starred", "false");
    const csrfinpele = document.createElement("div");
    csrfinpele.innerHTML = await (
      await fetch("/api/v0/getcsrftok/create/task")
    ).text();
    console.log(csrfinpele.innerHTML);
    urlsps.append(
      "csrf_token",
      csrfinpele.firstElementChild.getAttribute("value")
    );
    taskTitleInput.value = "";
    taskDuedateInput.value = "";
    const taskPostURL = "/postUserTask/";
    try {
      const response = await fetch(taskPostURL, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": urlsps.get("csrf_token"),
        },
        body: urlsps.toString(),
      });
      const servertask = await validatejson(response);
      console.log("task created: " + JSON.stringify(response));
      appendTask(servertask);
    } catch (error) {
      reloadflashedmessages();
      console.error(error);
    }
  }
}
function createLine(x1, y1, x2, y2) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1.toString());
  line.setAttribute("y1", y1.toString());
  line.setAttribute("x2", x2.toString());
  line.setAttribute("y2", y2.toString());
  return line;
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1.toString());
  line.setAttribute("y1", y1.toString());
  line.setAttribute("x2", x2.toString());
  line.setAttribute("y2", y2.toString());
  return line;
}
async function appendTaskList(taskList) {
  const taskListElement = document.getElementById("task_lists");
  const listItem = document.createElement("li");
  const svgElement = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "svg"
  );
  svgElement.classList.add("list-icon");
  svgElement.setAttribute("viewBox", "0 0 14 14");
  svgElement.setAttribute("fill", "none");
  const gElement = document.createElementNS("http://www.w3.org/2000/svg", "g");
  gElement.setAttribute("stroke", "var(--primary-color)");
  gElement.setAttribute("stroke-width", "1.4");
  gElement.setAttribute("stroke-linecap", "round");
  gElement.appendChild(createLine(4.65, 11.35, 13.35, 11.35));
  gElement.appendChild(createLine(4.65, 6.35, 13.35, 6.35));
  gElement.appendChild(createLine(4.65, 1.35, 13.35, 1.35));
  gElement.appendChild(createLine(1.65, 11.35, 1.35, 11.35));
  gElement.appendChild(createLine(1.65, 6.35, 1.35, 6.35));
  gElement.appendChild(createLine(1.65, 1.35, 1.35, 1.35));
  svgElement.appendChild(gElement);
  const aElement = document.createElement("a");
  aElement.style.cursor = "pointer";
  aElement.addEventListener("click", () =>
    loadTasksFromList(taskList.id, aElement)
  );
  aElement.innerText = taskList.name;
  listItem.appendChild(svgElement);
  listItem.appendChild(aElement);
  taskListElement.appendChild(listItem);
  const taskListElement = document.getElementById("task_lists");
  const listItem = document.createElement("li");
  const svgElement = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "svg"
  );
  svgElement.classList.add("list-icon");
  svgElement.setAttribute("viewBox", "0 0 14 14");
  svgElement.setAttribute("fill", "none");
  const gElement = document.createElementNS("http://www.w3.org/2000/svg", "g");
  gElement.setAttribute("stroke", "var(--primary-color)");
  gElement.setAttribute("stroke-width", "1.4");
  gElement.setAttribute("stroke-linecap", "round");
  gElement.appendChild(createLine(4.65, 11.35, 13.35, 11.35));
  gElement.appendChild(createLine(4.65, 6.35, 13.35, 6.35));
  gElement.appendChild(createLine(4.65, 1.35, 13.35, 1.35));
  gElement.appendChild(createLine(1.65, 11.35, 1.35, 11.35));
  gElement.appendChild(createLine(1.65, 6.35, 1.35, 6.35));
  gElement.appendChild(createLine(1.65, 1.35, 1.35, 1.35));
  svgElement.appendChild(gElement);
  const aElement = document.createElement("a");
  aElement.style.cursor = "pointer";
  aElement.addEventListener("click", () =>
    loadTasksFromList(taskList.id, aElement)
  );
  aElement.innerText = taskList.name;
  listItem.appendChild(svgElement);
  listItem.appendChild(aElement);
  taskListElement.appendChild(listItem);
}
async function loadTasksFromList(taskId, aElement) {
  try {
    console.log("Loading Tasks from List");
    const response = await fetch(`/getListTasks/${taskId}/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    const tasks = await validatejson(response);
    const taskListElement = document.getElementById("task_lists");
    const overdueSection = document.getElementById("overdue-list");
    const dueTodaySection = document.getElementById("due-today-list");
    const upcomingSection = document.getElementById("upcoming-list");
    let children = Array.from(overdueSection.children);
    children.forEach((child) => {
      if (child.tagName.toLowerCase() === "div") {
        overdueSection.removeChild(child);
      }
    });
    children = Array.from(dueTodaySection.children);
    children.forEach((child) => {
      if (child.tagName.toLowerCase() === "div") {
        dueTodaySection.removeChild(child);
      }
    });
    children = Array.from(upcomingSection.children);
    children.forEach((child) => {
      if (child.tagName.toLowerCase() === "div") {
        upcomingSection.removeChild(child);
      }
    });
    for (const task of tasks.tasks) {
      appendTask(task);
    }
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
  try {
    console.log("Loading Tasks from List");
    const response = await fetch(`/getListTasks/${taskId}/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    const tasks = await validatejson(response);
    const taskListElement = document.getElementById("task_lists");
    const overdueSection = document.getElementById("overdue-list");
    const dueTodaySection = document.getElementById("due-today-list");
    const upcomingSection = document.getElementById("upcoming-list");
    let children = Array.from(overdueSection.children);
    children.forEach((child) => {
      if (child.tagName.toLowerCase() === "div") {
        overdueSection.removeChild(child);
      }
    });
    children = Array.from(dueTodaySection.children);
    children.forEach((child) => {
      if (child.tagName.toLowerCase() === "div") {
        dueTodaySection.removeChild(child);
      }
    });
    children = Array.from(upcomingSection.children);
    children.forEach((child) => {
      if (child.tagName.toLowerCase() === "div") {
        upcomingSection.removeChild(child);
      }
    });
    for (const task of tasks.tasks) {
      appendTask(task);
    }
  } catch (error) {
    console.error("Error fetching tasks:", error);
  }
}
async function appendTask(task) {
  const today = new Date();
  let listId = "due-today-list";
  let duedate = null;
  let overdue = false;
  let dueToday = false;
  if (task.duedate) {
    duedate = new Date(task.duedate);
    if (isSameDay(duedate, today)) {
      listId = "due-today-list";
      dueToday = true;
    } else if (duedate < today) {
      listId = "overdue-list";
      overdue = true;
    } else {
      listId = "upcoming-list";
    }
  }
  const taskList = document.getElementById(listId);
  createTaskCard(taskList, task, overdue, dueToday);
  checkListSections();
  const today = new Date();
  let listId = "due-today-list";
  let duedate = null;
  let overdue = false;
  let dueToday = false;
  if (task.duedate) {
    duedate = new Date(task.duedate);
    if (isSameDay(duedate, today)) {
      listId = "due-today-list";
      dueToday = true;
    } else if (duedate < today) {
      listId = "overdue-list";
      overdue = true;
    } else {
      listId = "upcoming-list";
    }
  }
  const taskList = document.getElementById(listId);
  createTaskCard(taskList, task, overdue, dueToday);
  checkListSections();
}
function checkListSections() {
  const overdueList = document.getElementById("overdue-list");
  overdueList.style.display = Array.from(overdueList.children).some(
    (child) => child.tagName === "DIV"
  )
    ? "flex"
    : "none";
  const dueTodayList = document.getElementById("due-today-list");
  dueTodayList.style.display = Array.from(dueTodayList.children).some(
    (child) => child.tagName === "DIV"
  )
    ? "flex"
    : "none";
  const upcomingList = document.getElementById("upcoming-list");
  upcomingList.style.display = Array.from(upcomingList.children).some(
    (child) => child.tagName === "DIV"
  )
    ? "flex"
    : "none";
  const overdueList = document.getElementById("overdue-list");
  overdueList.style.display = Array.from(overdueList.children).some(
    (child) => child.tagName === "DIV"
  )
    ? "flex"
    : "none";
  const dueTodayList = document.getElementById("due-today-list");
  dueTodayList.style.display = Array.from(dueTodayList.children).some(
    (child) => child.tagName === "DIV"
  )
    ? "flex"
    : "none";
  const upcomingList = document.getElementById("upcoming-list");
  upcomingList.style.display = Array.from(upcomingList.children).some(
    (child) => child.tagName === "DIV"
  )
    ? "flex"
    : "none";
}
function createTaskCard(div, task, overdue, dueToday) {
  const card = document.createElement("div");
  card.className = "card hoverCard";
  card.id = `task-${task.id}`;
  card.setAttribute("data-duedate", String(new Date(task.duedate).getTime()));
  const checkIcon = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "svg"
  );
  checkIcon.id = `checkIcon-${task.id}`;
  if (task.complete) {
    filledCheckIcon(checkIcon);
  } else {
    emptyCheckIcon(checkIcon);
  }
  card.appendChild(checkIcon);
  const taskContent = document.createElement("div");
  taskContent.className = "task-content";
  card.appendChild(taskContent);
  const heading = document.createElement("h3");
  heading.textContent = task.name;
  heading.id = `task-name-${task.id}`;
  if (task.complete) {
    heading.style.color = "var(--dark-grey)";
    heading.style.textDecoration = "line-through";
  } else {
    heading.style.color = "black";
    heading.style.textDecoration = "none";
  }
  taskContent.appendChild(heading);
  const taskInfo = document.createElement("div");
  taskInfo.className = "task-info";
  taskContent.appendChild(taskInfo);
  if (task.tasklistnames.length > 0) {
    const listText = document.createElement("p");
    for (let i = 0; i < task.tasklistnames.length; i++) {
      const list = task.tasklistnames[i];
      if (i < task.tasklistnames.length - 1) {
        listText.innerText += `${list}, `;
      } else {
        listText.innerText += `${list}`;
      }
    }
    taskInfo.appendChild(listText);
  }
  if (task.duedate !== null && task.tasklistnames.length > 0) {
    const dotText = document.createElement("p");
    dotText.textContent = `${task.duedate !== null ? "•\u00a0 " : ""}`;
    taskInfo.appendChild(dotText);
  }
  if (task.duedate !== null) {
    const calendarSVG = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "svg"
    );
    calendarSVG.setAttribute("viewBox", "0 0 28 28");
    calendarSVG.setAttribute("width", "14px");
    const calendarPath = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path"
    );
    calendarPath.setAttribute(
      "d",
      "M22.611,3.182H20.455V2a1,1,0,0,0-2,0V3.182H9.545V2a1,1,0,0,0-2,0V3.182H5.389A4.394,4.394,0,0,0,1,7.571v15.04A4.394,4.394,0,0,0,5.389,27H22.611A4.394,4.394,0,0,0,27,22.611V7.571A4.394,4.394,0,0,0,22.611,3.182Zm-17.222,2H7.545V6.364a1,1,0,0,0,2,0V5.182h8.91V6.364a1,1,0,1,0,2,0V5.182h2.156A2.391,2.391,0,0,1,25,7.571V9.727H3V7.571A2.391,2.391,0,0,1,5.389,5.182ZM22.611,25H5.389A2.392,2.392,0,0,1,3,22.611V11.727H25V22.611A2.392,2.392,0,0,1,22.611,25Z"
    );
    calendarPath.setAttribute(
      "fill",
      overdue ? "#e83a3a" : dueToday ? "var(--primary-color)" : "#616161"
    );
    calendarSVG.style.marginLeft = "-2px";
    calendarSVG.appendChild(calendarPath);
    const dateText = document.createElement("p");
    dateText.textContent = formatDate(new Date(task.duedate));
    dateText.style.color = overdue
      ? "#e83a3a"
      : dueToday
      ? "var(--primary-color)"
      : "#616161";
    dateText.style.marginLeft = "-2px";
    taskInfo.appendChild(calendarSVG);
    taskInfo.appendChild(dateText);
  }
  const rightStarSVG = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "svg"
  );
  rightStarSVG.id = `starIcon-${task.id}`;
  rightStarSVG.setAttribute("class", "right-icon");
  rightStarSVG.setAttribute("width", "20px");
  rightStarSVG.setAttribute("viewBox", "0 0 17 16");
  if (task.starred) {
    rightStarSVG.setAttribute("fill", "var(--primary-color)");
  } else {
    rightStarSVG.setAttribute("fill", "none");
  }
  card.appendChild(rightStarSVG);
  const starPath = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path"
  );
  starPath.setAttribute(
    "d",
    "M8.95126 1.1067L10.5511 4.45952C10.7698 4.91778 11.2055 5.23431 11.7089 5.30067L15.392 5.78617C15.809 5.84113 15.9759 6.35497 15.6709 6.64452L12.9766 9.20218C12.6083 9.55176 12.4419 10.0639 12.5343 10.5632L13.2108 14.2161C13.2873 14.6296 12.8502 14.9472 12.4806 14.7466L9.21552 12.9744C8.76925 12.7322 8.23075 12.7322 7.78448 12.9744L4.5194 14.7466C4.14977 14.9472 3.71268 14.6296 3.78925 14.2161L4.46565 10.5632C4.5581 10.0639 4.3917 9.55176 4.02344 9.20218L1.3291 6.64451C1.02409 6.35497 1.19104 5.84113 1.608 5.78617L5.29112 5.30067C5.79452 5.23431 6.23018 4.91778 6.44885 4.45952L8.04874 1.10669C8.22986 0.727135 8.77014 0.727133 8.95126 1.1067Z"
  );
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
  const childDivs = Array.from(div.children).filter(
    (child) => child instanceof HTMLDivElement
  );
  if (childDivs.length === 0) {
    div.appendChild(card);
  } else {
    let cardAdded = false;
    for (let i = 0; i < childDivs.length; i++) {
      const child = childDivs[i];
      const toAdd_date = new Date(task.duedate).getTime();
      const existing_date = Number(child.dataset.duedate);
      if (toAdd_date < existing_date && !cardAdded) {
        div.insertBefore(card, child);
        cardAdded = true;
      }
    }
    if (!cardAdded) {
      div.appendChild(card);
    }
  }
}
function openDetails(task) {
  const detailsPanel = document.getElementById("task-details-container");
  detailsPanel.classList.add("open");
  detailsPanel.setAttribute("data-task-id", String(task.id));
  const nameInput = document.getElementById("details-task-name-input");
  nameInput.value = task.name;
  const dateInput = document.getElementById("details-task-duedate-input");
  if (task.duedate !== null) {
    dateInput.value = formatDateForInputField(new Date(task.duedate));
  } else {
    dateInput.value = "";
  }
  const notesIput = document.getElementById("details-task-notes-input");
  notesIput.value = task.notes;
  const checkIcon = document.getElementById("details-checkIcon");
  const starIcon = document.getElementById("details-starIcon");
  const newCheckIcon = checkIcon.cloneNode(true);
  checkIcon.parentNode?.replaceChild(newCheckIcon, checkIcon);
  newCheckIcon.addEventListener("click", () => {
    toggleComplete(task);
  });
  const newStarIcon = starIcon.cloneNode(true);
  starIcon.parentNode?.replaceChild(newStarIcon, starIcon);
  newStarIcon.addEventListener("click", () => {
    toggleStarred(task);
  });
  if (newCheckIcon instanceof SVGElement) {
    if (task.complete) {
      filledCheckIcon(newCheckIcon);
    } else {
      emptyCheckIcon(newCheckIcon);
    }
  } else {
    console.error("The element is not an SVGElement");
  }
  if (task.starred) {
    newStarIcon.setAttribute("fill", "var(--primary-color)");
  } else {
    newStarIcon.setAttribute("fill", "none");
  }
  const detailsPanel = document.getElementById("task-details-container");
  detailsPanel.classList.add("open");
  detailsPanel.setAttribute("data-task-id", String(task.id));
  const nameInput = document.getElementById("details-task-name-input");
  nameInput.value = task.name;
  const dateInput = document.getElementById("details-task-duedate-input");
  if (task.duedate !== null) {
    dateInput.value = formatDateForInputField(new Date(task.duedate));
  } else {
    dateInput.value = "";
  }
  const notesIput = document.getElementById("details-task-notes-input");
  notesIput.value = task.notes;
  const checkIcon = document.getElementById("details-checkIcon");
  const starIcon = document.getElementById("details-starIcon");
  const newCheckIcon = checkIcon.cloneNode(true);
  checkIcon.parentNode?.replaceChild(newCheckIcon, checkIcon);
  newCheckIcon.addEventListener("click", () => {
    toggleComplete(task);
  });
  const newStarIcon = starIcon.cloneNode(true);
  starIcon.parentNode?.replaceChild(newStarIcon, starIcon);
  newStarIcon.addEventListener("click", () => {
    toggleStarred(task);
  });
  if (newCheckIcon instanceof SVGElement) {
    if (task.complete) {
      filledCheckIcon(newCheckIcon);
    } else {
      emptyCheckIcon(newCheckIcon);
    }
  } else {
    console.error("The element is not an SVGElement");
  }
  if (task.starred) {
    newStarIcon.setAttribute("fill", "var(--primary-color)");
  } else {
    newStarIcon.setAttribute("fill", "none");
  }
}
async function toggleComplete(task) {
  const response = await fetch(
    `/markComplete/${task.id}/${task.complete ? "0" : "1"}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  const r = await validatejson(response);
  console.log(r);
  task.complete = !task.complete;
  const checkIcon = document.getElementById(`checkIcon-${task.id}`);
  if (checkIcon instanceof SVGElement) {
    if (task.complete) {
      filledCheckIcon(checkIcon);
    } else {
      emptyCheckIcon(checkIcon);
    }
  } else {
    console.error("The element is not an SVGElement");
  }
  const detailsCheckIcon = document.getElementById("details-checkIcon");
  if (detailsCheckIcon instanceof SVGElement) {
    if (task.complete) {
      filledCheckIcon(detailsCheckIcon);
    } else {
      emptyCheckIcon(detailsCheckIcon);
    }
  } else {
    console.error("The element is not an SVGElement");
  }
  const taskTitle = document.getElementById(`task-name-${task.id}`);
  if (task.complete) {
    taskTitle.style.color = "var(--dark-grey)";
    taskTitle.style.textDecoration = "line-through";
  } else {
    taskTitle.style.color = "black";
    taskTitle.style.textDecoration = "none";
  }
  const response = await fetch(
    `/markComplete/${task.id}/${task.complete ? "0" : "1"}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  const r = await validatejson(response);
  console.log(r);
  task.complete = !task.complete;
  const checkIcon = document.getElementById(`checkIcon-${task.id}`);
  if (checkIcon instanceof SVGElement) {
    if (task.complete) {
      filledCheckIcon(checkIcon);
    } else {
      emptyCheckIcon(checkIcon);
    }
  } else {
    console.error("The element is not an SVGElement");
  }
  const detailsCheckIcon = document.getElementById("details-checkIcon");
  if (detailsCheckIcon instanceof SVGElement) {
    if (task.complete) {
      filledCheckIcon(detailsCheckIcon);
    } else {
      emptyCheckIcon(detailsCheckIcon);
    }
  } else {
    console.error("The element is not an SVGElement");
  }
  const taskTitle = document.getElementById(`task-name-${task.id}`);
  if (task.complete) {
    taskTitle.style.color = "var(--dark-grey)";
    taskTitle.style.textDecoration = "line-through";
  } else {
    taskTitle.style.color = "black";
    taskTitle.style.textDecoration = "none";
  }
}
async function toggleStarred(task) {
  const response = await fetch(
    `/markStarred/${task.id}/${task.starred ? "0" : "1"}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  const r = await validatejson(response);
  console.log(r);
  task.starred = !task.starred;
  const starIcon = document.getElementById(`starIcon-${task.id}`);
  if (task.starred) {
    starIcon.setAttribute("fill", "var(--primary-color)");
  } else {
    starIcon.setAttribute("fill", "none");
  }
  const detailsStarIcon = document.getElementById("details-starIcon");
  if (task.starred) {
    detailsStarIcon.setAttribute("fill", "var(--primary-color)");
  } else {
    detailsStarIcon.setAttribute("fill", "none");
  }
  const response = await fetch(
    `/markStarred/${task.id}/${task.starred ? "0" : "1"}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  const r = await validatejson(response);
  console.log(r);
  task.starred = !task.starred;
  const starIcon = document.getElementById(`starIcon-${task.id}`);
  if (task.starred) {
    starIcon.setAttribute("fill", "var(--primary-color)");
  } else {
    starIcon.setAttribute("fill", "none");
  }
  const detailsStarIcon = document.getElementById("details-starIcon");
  if (task.starred) {
    detailsStarIcon.setAttribute("fill", "var(--primary-color)");
  } else {
    detailsStarIcon.setAttribute("fill", "none");
  }
}
function isSameDay(date1, date2) {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
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
function formatDateForInputField(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
async function askChatGPT() {
  const textField = document.getElementById("aiPromptTextField");
  if (textField.value != "") {
    const input = textField.value;
    textField.value = "";
    console.log(`input before chatGPT: ${input}`);
    const spinner = document.getElementById("loading-spinner");
    spinner.style.display = "block";
    console.log("HELLLOOOO");
    const response = await getChatGPTResponse(input);
    spinner.style.display = "none";
    if (response.status === "error") {
      reloadflashedmessages();
    } else {
      for (const tasklist of response.GPTResponse.tasklists) {
        appendTaskList(tasklist);
      }
      for (const task of response.GPTResponse.tasks) {
        const dbTask = {
          id: task.id,
          name: task.name,
          complete: false,
          duedate: task.duedate * 1000,
          starred: task.starred,
          notes: "",
          tasklistnames: task.tasklistnames.split(","),
        };
        appendTask(dbTask);
      }
      for (const subtask of response.GPTResponse.subtasks) {
      }
      console.log(response);
    }
  }
}
async function getChatGPTResponse(question) {
  console.log("Trying ChatGPT");
  const params = new URLSearchParams({
    question: question,
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
  } catch (error) {
    console.error("Error fetching data:", error);
  }
  console.log("Trying ChatGPT");
  const params = new URLSearchParams({
    question: question,
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
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}
function validatejson(response) {
  if (response.ok) {
    return response.json();
  } else {
    return Promise.reject(response);
  }
  if (response.ok) {
    return response.json();
  } else {
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
  path.setAttribute(
    "d",
    "M204.288,0C91.648,0,0,91.648,0,204.288s91.648,204.288,204.288,204.288s204.288-91.648,204.288-204.288S316.928,0,204.288,0z M318.464,150.528l-130.56,129.536c-7.68,7.68-19.968,8.192-28.16,0.512L90.624,217.6c-8.192-7.68-8.704-20.48-1.536-28.672c7.68-8.192,20.48-8.704,28.672-1.024l54.784,50.176L289.28,121.344c8.192-8.192,20.992-8.192,29.184,0C326.656,129.536,326.656,142.336,318.464,150.528z"
  );
  checkIcon.appendChild(path);
  checkIcon.setAttribute("class", "circle left-icon");
  checkIcon.setAttribute("viewBox", "0 0 408.576 408.576");
  checkIcon.style.setProperty("enable-background", "new 0 0 408.576 408.576");
  checkIcon.setAttribute("xml:space", "preserve");
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("fill", "var(--primary-color)");
  path.setAttribute(
    "d",
    "M204.288,0C91.648,0,0,91.648,0,204.288s91.648,204.288,204.288,204.288s204.288-91.648,204.288-204.288S316.928,0,204.288,0z M318.464,150.528l-130.56,129.536c-7.68,7.68-19.968,8.192-28.16,0.512L90.624,217.6c-8.192-7.68-8.704-20.48-1.536-28.672c7.68-8.192,20.48-8.704,28.672-1.024l54.784,50.176L289.28,121.344c8.192-8.192,20.992-8.192,29.184,0C326.656,129.536,326.656,142.336,318.464,150.528z"
  );
  checkIcon.appendChild(path);
}
function emptyCheckIcon(checkIcon) {
  checkIcon.setAttribute("class", "circle left-icon");
  checkIcon.setAttribute("viewBox", "0 0 15 15");
  checkIcon.setAttribute("fill", "none");
  checkIcon.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  const circle = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "circle"
  );
  circle.setAttribute("cx", "7.5");
  circle.setAttribute("cy", "7.5");
  circle.setAttribute("r", "7");
  circle.setAttribute("stroke", "var(--primary-color)");
  checkIcon.appendChild(circle);
  const checkmarkPath = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path"
  );
  checkmarkPath.setAttribute(
    "d",
    "M6.8985 10.2819L11.6917 5.52631C11.9925 5.22556 11.9925 4.75563 11.6917 4.45488C11.391 4.15412 10.921 4.15412 10.6203 4.45488L6.33459 8.74059L4.3233 6.89849C4.02255 6.61654 3.55264 6.63533 3.27069 6.93608C3.0075 7.23684 3.0263 7.70676 3.32705 7.98871L5.86465 10.3007C6.1654 10.5827 6.61654 10.5639 6.8985 10.2819Z"
  );
  checkmarkPath.setAttribute("fill", "var(--primary-color)");
  checkmarkPath.style.display = "none";
  checkIcon.appendChild(checkmarkPath);
  checkIcon.addEventListener("mouseover", () => {
    checkmarkPath.style.display = "block";
  });
  checkIcon.addEventListener("mouseout", () => {
    checkmarkPath.style.display = "none";
  });
  checkIcon.setAttribute("class", "circle left-icon");
  checkIcon.setAttribute("viewBox", "0 0 15 15");
  checkIcon.setAttribute("fill", "none");
  checkIcon.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  const circle = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "circle"
  );
  circle.setAttribute("cx", "7.5");
  circle.setAttribute("cy", "7.5");
  circle.setAttribute("r", "7");
  circle.setAttribute("stroke", "var(--primary-color)");
  checkIcon.appendChild(circle);
  const checkmarkPath = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "path"
  );
  checkmarkPath.setAttribute(
    "d",
    "M6.8985 10.2819L11.6917 5.52631C11.9925 5.22556 11.9925 4.75563 11.6917 4.45488C11.391 4.15412 10.921 4.15412 10.6203 4.45488L6.33459 8.74059L4.3233 6.89849C4.02255 6.61654 3.55264 6.63533 3.27069 6.93608C3.0075 7.23684 3.0263 7.70676 3.32705 7.98871L5.86465 10.3007C6.1654 10.5827 6.61654 10.5639 6.8985 10.2819Z"
  );
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
function closeAddTaskModal() {
  const addTaskModal = document.getElementById("addTaskModal");
  addTaskModal.style.display = "none";
  const addTaskModal = document.getElementById("addTaskModal");
  addTaskModal.style.display = "none";
}
