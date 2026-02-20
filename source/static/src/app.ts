
interface IngestResponse {
    message: string;
}

interface Source {
    page: number;
    text: string;
}

interface ChatResponse{
    question: string;
    answer: string;
    source: Source[];
}

document.addEventListener('DOMContentLoaded', async ()=> {

    const uploadBtn = document.getElementById('uploadBtn') as HTMLButtonElement;
    const brandInput = document.getElementById('brandInput') as HTMLTextAreaElement;
    const modelInput = document.getElementById('modelInput') as HTMLTextAreaElement;
    const yearInput = document.getElementById('yearInput') as HTMLTextAreaElement;
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
        formData.append('brand', brandInput.value);
        formData.append('model', modelInput.value);
        formData.append('year', yearInput.value);

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

    const modelSelect = document.getElementById('modelSelect') as HTMLSelectElement;
    try {
        const response = await fetch('/models');
        const models = await response.json();
        
        modelSelect.innerHTML = models.map((m: any) => 
            `<option value="${m.id}">${m.name}</option>`
        ).join('');
    } catch (e) {
        modelSelect.innerHTML = '<option value="">Erreur de chargement</option>';
    }

    sendBtn.addEventListener('click', async () => {
        const docId = modelSelect.value;
        const question = questionInput.value.trim();
        if (!question) return;

        try {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Thinking...';
            
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question, doc_id: docId })
            });

            const data: ChatResponse = await response.json();

            resultArea.classList.remove('d-none');
            aiResponseContent.innerHTML = `<p class="mb-0">${data.answer}</p>`;
            console.log(data)
            if (data.source && data.source.length > 0) {
                const sourcesContainer = document.createElement('div');
                sourcesContainer.className = "mt-3 pt-2 border-top";
                const title = `<small class="text-muted d-block mb-2"><i class="bi bi-book"></i> Sources extraites du manuel :</small>`;

                const badges = data.source.map((s: any) => `
                    <div class="card bg-light border-0 mb-2 shadow-sm">
                        <div class="card-body py-2 px-3">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <span class="badge rounded-pill bg-secondary">Page ${s.page}</span>
                            </div>
                            <p class="card-text small text-dark mb-0" style="font-style: italic;">
                                "...${s.content}..."
                            </p>
                        </div>
                    </div>
                `).join('');

                sourcesContainer.innerHTML = title + badges;
                aiResponseContent.appendChild(sourcesContainer);
            }
            resultArea.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            console.error("Chat Error:", error);
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerText = "Send question";
            questionInput.value = "";
        }
    });
});