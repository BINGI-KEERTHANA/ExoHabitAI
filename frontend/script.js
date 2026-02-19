document.getElementById("predictForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const button = document.querySelector(".btn-predict");
    const loading = document.getElementById("loadingBox");
    const resultBox = document.getElementById("resultBox");

    // Show loading
    button.disabled = true;
    loading.style.display = "block";
    resultBox.innerHTML = "";

    const data = {
        radius: parseFloat(document.getElementById("radius").value),
        mass: parseFloat(document.getElementById("mass").value),
        temperature: parseFloat(document.getElementById("temp").value),
        distance: parseFloat(document.getElementById("distance").value)
    };

    fetch("https://exohabitai-1-9zyf.onrender.com/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(result => {

        loading.style.display = "none";
        button.disabled = false;

        if(result.error){
            resultBox.innerHTML = `
                <div class="error-card">
                    <h5>❌ Error</h5>
                    <p>${result.error}</p>
                </div>
            `;
            return;
        }

        resultBox.innerHTML = `
            <div class="success-card">
                <h5>✅ Prediction Result</h5>
                <p><b>Habitability Score:</b> ${result.score}</p>
                <p><b>Status:</b> ${result.status}</p>
            </div>
        `;
    })
    .catch(err => {

        loading.style.display = "none";
        button.disabled = false;

        resultBox.innerHTML = `
            <div class="error-card">
                <h5>❌ Error</h5>
                <p>Backend connection failed.</p>
            </div>
        `;

        console.error(err);
    });
});
