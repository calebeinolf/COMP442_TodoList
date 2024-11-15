document.addEventListener("DOMContentLoaded", async () => {
    console.log("hello");
    const askAIButton = document.getElementById("ask_ai_button");
    askAIButton.addEventListener("click", aiButtonClicked);
    const closeModalBtn = document.getElementById("closeAIModal");
    const closeModalBtn2 = document.getElementById("submitAIModal");
    closeModalBtn.addEventListener("click", closeAIModal);
    closeModalBtn2.addEventListener("click", closeAIModal);
});
async function aiButtonClicked() {
    const modal = document.getElementById('aiModal');
    modal.style.display = 'block';
}
async function closeAIModal() {
    const modal = document.getElementById('aiModal');
    modal.style.display = 'none';
}
async function submitAIModal() {
    const modal = document.getElementById('aiModal');
    modal.style.display = 'none';
}
