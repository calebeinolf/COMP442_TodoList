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
    console.log(`starred: ${response.starred}\nname: ${response.name}\ndescription: ${response.description}\ndue_date: ${response.due_date}\ndue_time: ${response.due_time}\ndue_time_included: ${response.due_time_included}`);
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
        const data = await ValidateJSON(response);
        return data;
    }
    catch (error) {
        console.error('Error fetching data:', error);
    }
}
function ValidateJSON(response) {
    if (response.ok) {
        return response.json();
    }
    else {
        return Promise.reject(response);
    }
}
