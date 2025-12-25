const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const startBtn = document.getElementById("startBtn");
const snapBtn = document.getElementById("snapBtn");
const statusBox = document.getElementById("status");

let stream = null;

/* START CAMERA --------------------------------------------------- */
startBtn.addEventListener("click", async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        statusBox.innerText = "Camera started.";
    } catch (error) {
        statusBox.innerText = "Camera error: " + error.message;
    }
});

/* CAPTURE & VERIFY ------------------------------------------------ */
snapBtn.addEventListener("click", async () => {

    if (!stream) {
        statusBox.innerText = "Start camera first!";
        return;
    }

    statusBox.innerText = "Capturing image...";

    /* Draw video frame into canvas */
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    /* Convert to Base64 */
    const base64Image = canvas.toDataURL("image/jpeg", 0.9);

    statusBox.innerText = "Verifying... Please wait.";

    /* Send image to Django backend */
    const formData = new FormData();
    formData.append("image", base64Image);

    try {
        const response = await fetch("/verify/", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.error) {
            statusBox.innerText = "Error: " + result.error;
            return;
        }

        if (result.authorized) {
            statusBox.innerText = `✔ AUTHORIZED: ${result.name} (distance=${result.distance})`;
            statusBox.style.color = "#5eead4";
        } else {
            statusBox.innerText = "❌ UNAUTHORIZED PERSON DETECTED!";
            statusBox.style.color = "#ff7676";
        }

    } catch (err) {
        statusBox.innerText = "Request failed: " + err.message;
    }
});
