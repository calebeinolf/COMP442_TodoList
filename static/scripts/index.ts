interface ChatGPTResponse {
  starred: boolean;
  name: string;
  description: string;
  due_date: string;
  due_time: string;
  due_time_included: boolean;
  type: string;
}

document.addEventListener("DOMContentLoaded", async () => {
  console.log("hello");
  const askAIButton = <HTMLButtonElement> document.getElementById("ask_ai_button");
  askAIButton.addEventListener("click", aiButtonClicked);
  const closeModalBtn = <HTMLButtonElement> document.getElementById("closeAIModal")
  const submitModalBtn = <HTMLButtonElement> document.getElementById("submitAIModal")
  closeModalBtn.addEventListener("click", closeAIModal)
  submitModalBtn.addEventListener("click", submitAIModal)
});

async function aiButtonClicked(){
  console.log("Clicked")
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
  await askChatGPT();
}

async function askChatGPT(){
  const textField = <HTMLInputElement> document.getElementById("aiPromtTextField");
  const input: string = textField.value;
  console.log(`input before chatGPT: ${input}`)
  const types: string[] = ["Family", "Work", "Personal"];
  const response = await getChatGTPResponse(input, types);
  // console.log(`starred: ${response.starred}\nname: ${response.name}\ndescription: ${response.description}\ndue_date: ${response.due_date}\ndue_time: ${response.due_time}\ndue_time_included: ${response.due_time_included}`)
}

async function getChatGTPResponse(question: string, types: string[]){
  console.log("Trying ChatGPT")

  const params = new URLSearchParams({
    question: question,
    types: types.join(","),
  })

  try{
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

  } catch (error) {
    console.error('Error fetching data:', error);
  }

}