
interface IngestResponse {
    message: string;
}

interface ChatResponse{
    question: string;
    answer: string;
}

document.addEventListener('DOMContentLoaded', async ()=> {

    const uploadBtn = document.getElementById('uploadBtn') as HTMLButtonElement;
    const fileInput = document.getElementById('fileInput') as HTMLInputElement;
    const spinner = document.getElementById('spinner') as HTMLElement;

    const sendBtn = document.getElementById('sendBtn') as HTMLButtonElement;
    const questionInput = document.getElementById('questionInput') as HTMLTextAreaElement;
    const aiResponseContent = document.getElementById('aiResponseContent') as HTMLElement;
    const resultArea = document.getElementById('resultArea') as HTMLElement;

    uploadBtn.addEventListener('click', async () => {
        if (!fileInput.files || fileInput.isDefaultNamespace.length === 0) {
            alert("");
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            uploadBtn.disabled = true;
            spinner.classList.remove('d-none');

            const response = await fetch('/ingest', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error("Ingest Error");

            const data: IngestResponse = await response.json();
            alert("This files in ingest succesfull.");
            console.log(data.message);
        } catch (error) {
            alert("Send file Error");
        } finally {
            uploadBtn.disabled = false;
            spinner.classList.add('d-none');
        }
    });


    sendBtn.addEventListener('click', async () => {
        const question = questionInput.value.trim();
        if (!question) return;

        try {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Thinking...';
            
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question })
            });

            const data: ChatResponse = await response.json();

            resultArea.classList.remove('d-none');
            aiResponseContent.innerHTML = `<p class="mb-0">${data.answer}</p>`;

            resultArea.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            alert("Rag engine can't answer.");
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerText = "Send question";
            questionInput.value = "";
        }
    });
});