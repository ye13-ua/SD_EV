let regions = [];
let canvas, ctx;
let minLat, maxLat, minLon, maxLon;

async function loadRegions() {
    let res = await fetch("/api/regions");
    regions = await res.json();

    if (regions.length === 0) {
        console.log("No regions.");
        return;
    }

    computeBounds();
    drawMap();
}

function computeBounds() {
    minLat = Math.min(...regions.map(r => r.lat));
    maxLat = Math.max(...regions.map(r => r.lat));
    minLon = Math.min(...regions.map(r => r.lon));
    maxLon = Math.max(...regions.map(r => r.lon));
}

function drawMap() {
    canvas = document.getElementById("map");
    ctx = canvas.getContext("2d");

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    regions.forEach((region, index) => {
        let x = (region.lon - minLon) / (maxLon - minLon + 0.0001) * canvas.width;
        let y = canvas.height - (region.lat - minLat) / (maxLat - minLat + 0.0001) * canvas.height;

        region.x = x;
        region.y = y;

        ctx.beginPath();
        ctx.arc(x, y, 7, 0, 2 * Math.PI);
        ctx.fillStyle = region.alert ? "red" : "green";
        ctx.fill();
        ctx.strokeStyle = "#000";
        ctx.stroke();
    });
}

document.addEventListener("click", function (e) {
    if (!regions.length) return;

    let rect = canvas.getBoundingClientRect();
    let x = e.clientX - rect.left;
    let y = e.clientY - rect.top;

    let clickedRegion = regions.find(r => Math.abs(r.x - x) < 10 && Math.abs(r.y - y) < 10);

    if (clickedRegion) showRegion(clickedRegion);
});

function showRegion(region) {
    let info = document.getElementById("info");

    let html = `
        <h3>Region at (${region.lat.toFixed(2)}, ${region.lon.toFixed(2)})</h3>
        <p><b>Temperature:</b> ${region.last_temp ?? "N/A"}°C</p>
        <p><b>Status:</b> <span class="${region.alert ? "alert" : ""}">
            ${region.alert ? "ALERT" : "NORMAL"}
        </span></p>
        <p><b>Assigned CPs (${region.cps.length}):</b></p>
        <ul>
    `;

    region.cps.forEach(cp => {
        html += `<li>${cp}</li>`;
    });

    html += "</ul>";

    info.innerHTML = html;
}

async function refreshCPs() {
    let res = await fetch("/api/refresh");
    let out = await res.json();
    alert("Refreshed. Total regions: " + out.regions);
    loadRegions();
}

window.onload = loadRegions;
