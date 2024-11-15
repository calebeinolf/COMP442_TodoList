document.addEventListener("DOMContentLoaded", async () => {
    console.log("hello");
    const askAIButton = document.getElementById("ask_ai_button");
    askAIButton.addEventListener("click", aiButtonClicked);
    const closeModalBtn = document.getElementById("closeAIModal");
    const submitModalBtn = document.getElementById("submitAIModal");
    closeModalBtn.addEventListener("click", closeAIModal);
    submitModalBtn.addEventListener("click", submitAIModal);
});
async function aiButtonClicked() {
    console.log("Clicked");
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
    await askChatGPT();
}
async function askChatGPT() {
    const textField = document.getElementById("aiPromtTextField");
    const input = textField.value;
    console.log(`input before chatGPT: ${input}`);
    const types = ["Family", "Work", "Personal"];
    const response = await getChatGTPResponse(input, types);
}
async function getChatGTPResponse(question, types) {
    console.log("Trying ChatGPT");
    const params = new URLSearchParams({
        question: question,
        types: types.join(","),
    });
    try {
        const response = await fetch(`http://localhost:5000/askChatGPT?${params.toString()}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Received data:', data);
    }
    catch (error) {
        console.error('Error fetching data:', error);
    }
}
