document.addEventListener("DOMContentLoaded", async () => {
  console.log("hello");
  const askAIButton = <HTMLButtonElement> document.getElementById("ask_ai_button");
  askAIButton.addEventListener("click", aiButtonClicked);
  const closeModalBtn = <HTMLButtonElement> document.getElementById("closeAIModal")
  const closeModalBtn2 = <HTMLButtonElement> document.getElementById("submitAIModal")
  closeModalBtn.addEventListener("click", closeAIModal)
  closeModalBtn2.addEventListener("click", closeAIModal)
});

async function aiButtonClicked(){
  const modal = <HTMLElement> document.getElementById('aiModal');
  modal.style.display = 'block';
}

async function closeAIModal(){
  const modal = <HTMLElement> document.getElementById('aiModal');
  modal.style.display = 'none';
}

async function submitAIModal(){
  const modal = <HTMLElement> document.getElementById('aiModal');
  modal.style.display = 'none';
}
