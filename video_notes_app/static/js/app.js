const apiBaseUrl = "http://127.0.0.1:5000/api";

document.getElementById("videoForm").addEventListener("submit", async function (event) {
    event.preventDefault();
    const videoUrl = document.getElementById("videoUrl").value;

    const response = await fetch(`${apiBaseUrl}/videos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: videoUrl }),
    });

    if (response.ok) {
        loadVideos();
        document.getElementById("videoUrl").value = "";
    } else {
        alert("Failed to add video.");
    }
});

async function loadVideos() {
    const response = await fetch(`${apiBaseUrl}/videos`);
    const videos = await response.json();

    const videoList = document.getElementById("videoList");
    videoList.innerHTML = ""; // Clear previous list

    videos.forEach((video) => {
        const videoDiv = document.createElement("div");
        videoDiv.className = "bg-white p-6 rounded-lg shadow-lg";
        videoDiv.innerHTML = `
            <iframe class="w-full h-[600px] rounded-md" id="video-${video.id}" src="${video.url}" frameborder="0" allowfullscreen></iframe>
            <button onclick="deleteVideo(${video.id})" class="bg-red-500 text-white p-2 rounded mt-2">Delete Video</button>
            <form onsubmit="addNoteToVideo(event, ${video.id})" class="mt-4">
                <input type="text" name="note" placeholder="Add a note" class="block w-full p-2 border rounded">
                <input type="text" name="time" placeholder="Timestamp (HH:MM:SS)" class="block w-full p-2 border rounded mt-2">
                <button type="submit" class="w-full bg-green-500 text-white p-2 rounded mt-2">Add Note</button>
            </form>
            <ul class="mt-4 space-y-2">
                ${video.notes
                    .map(
                        (note) => `
                    <li class="flex justify-between items-center">
                        <span class="cursor-pointer text-blue-500" onclick="seekToTime(${video.id}, '${note.time}')">${note.text} (at ${note.time})</span>
                        <button class="text-red-500" onclick="deleteNoteFromVideo(${video.id}, ${note.id})">Delete</button>
                    </li>
                `
                    )
                    .join("")}
            </ul>
        `;
        videoList.appendChild(videoDiv);
    });
}

async function deleteVideo(videoId) {
    await fetch(`${apiBaseUrl}/videos/${videoId}`, { method: "DELETE" });
    loadVideos();
}

async function addNoteToVideo(event, videoId) {
    event.preventDefault();
    const form = event.target;
    const note = form.note.value;
    const time = form.time.value;

    await fetch(`${apiBaseUrl}/videos/${videoId}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ note, time }),
    });

    loadVideos();
}

async function deleteNoteFromVideo(videoId, noteId) {
    await fetch(`${apiBaseUrl}/videos/${videoId}/notes/${noteId}`, { method: "DELETE" });
    loadVideos();
}

function seekToTime(videoId, time) {
    const iframe = document.getElementById(`video-${videoId}`);
    const [hours, minutes, seconds] = time.split(":").map(Number);
    const totalSeconds = hours * 3600 + minutes * 60 + seconds;

    iframe.src = `${iframe.src.split("?")[0]}?start=${totalSeconds}&autoplay=1`;
}

// Initial load
loadVideos();