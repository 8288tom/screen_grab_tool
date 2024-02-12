const form = document.getElementById("captureForm");
const link = document.getElementById("videoLink");
const times = document.getElementById("times");
const submitButton = document.getElementById("submitButton");
const sendUrl = "http://127.0.0.1:5174/screen_grab_tool/capture_and_download";

form.addEventListener("submit", (e) => {
    e.preventDefault();
    postData(link.value, times.value)
});


const toggleLoader = (isLoading) => {
    const loaderExists = document.getElementById("loader");

    if (isLoading) {
        if (!loaderExists) {
            const loader = document.createElement("div");
            const progress = document.createElement("div")
            progress.className = "indeterminate"
            loader.className = "progress";
            loader.id = "loader";
            document.body.appendChild(loader).appendChild(progress).classList.add("indigo");
        }
        submitButton.disabled = true;

    } else {
        // Remove the loader from the document
        if (loaderExists) {
            document.body.removeChild(loaderExists);
        }
        submitButton.disabled = false;
    }
};


const postData = async (videoLink, timesString) => {
    // Validations:
    const sanitizedTimes = timesString.split(',').map(time => time.trim()).filter(Boolean);
    // Check if the videoLink ends with .mp4
    if (!(videoLink.endsWith('.mp4') || videoLink.endsWith(".m3u8"))) {
        M.toast({ html: 'Invalid video link. The link must end with .mp4 or .m3u8' });
        return;
    }
    toggleLoader(true);
    try {
        const response = await fetch(sendUrl, {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json"
            },
            referrerPolicy: "no-referrer",
            body: JSON.stringify({ videoLink, times: sanitizedTimes }),
        });
        if (!response.ok) {
            console.error("Failed to send video to server:", response);
            M.toast({ html: 'Failed to send video to server' })
        }
        // Handling the ZIP file download
        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = "screenshots.zip";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);

    }
    catch (error) {
        M.toast({ html: 'Request Failed!' })
        console.error(`Failed sending data to backend:`, error);
    }
    finally {
        toggleLoader(false);
    }
};

