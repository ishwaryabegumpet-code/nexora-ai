console.log("NEXORA JS LOADED");

const pdfButton = document.getElementById("pdfButton");
const pdfInput = document.getElementById("pdfInput");
const summary = document.getElementById("summary");

console.log("PDF BUTTON:", pdfButton);
console.log("PDF INPUT:", pdfInput);
console.log("SUMMARY:", summary);


// Open PDF file selector
pdfButton.addEventListener("click", () => {
    pdfInput.click();
});


// When PDF is selected
pdfInput.addEventListener("change", async () => {

    console.log("PDF CHANGE EVENT FIRED");

    const file = pdfInput.files[0];

    if (!file) {
        return;
    }

    console.log("Selected PDF:", file.name);

    summary.innerHTML = `
        <div class="summary-card">
            <p>⏳ Reading and summarizing your PDF...</p>
        </div>
    `;


    const formData = new FormData();

    // IMPORTANT: Flask expects "pdf"
    formData.append("pdf", file);


    try {

        const response = await fetch(
            "http://127.0.0.1:5000/upload",
            {
                method: "POST",
                body: formData
            }
        );


        const result = await response.json();

        console.log("Backend response:", result);


        if (!response.ok) {

            summary.innerHTML = `
                <div class="summary-card">
                    <p>❌ ${result.error || "Unable to summarize PDF."}</p>
                </div>
            `;

            return;
        }


        summary.innerHTML = `
            <div class="summary-card">

                <div class="summary-header">
                    <span class="summary-icon">✨</span>
                    <h2>AI Summary</h2>
                </div>

                <div class="summary-content">

                    <h3>${result.filename}</h3>

                    <p>${result.summary}</p>

                </div>

            </div>
        `;


    } catch (error) {

        console.error("Error uploading PDF:", error);

        summary.innerHTML = `
            <div class="summary-card">

                <h3>❌ Unable to connect</h3>

                <p>
                    Make sure your Flask server is running
                    on port 5000.
                </p>

            </div>
        `;
    }

});