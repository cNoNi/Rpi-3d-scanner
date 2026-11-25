"use strict";

const $ = (id) => document.getElementById(id);

const buttons = {
    start: $("scan-start"),
    stop: $("scan-stop"),
    photo: $("photo"),
    cw: $("motor-cw"),
    ccw: $("motor-ccw"),
};

function showMessage(text, isError = true) {
    const el = $("message");
    el.textContent = text || "";
    el.hidden = !text;
    el.classList.toggle("error", isError);
}

async function post(url) {
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "X-Requested-With": "fetch" },
        });
        const body = await response.json().catch(() => ({}));
        if (!response.ok) {
            showMessage(body.message || `Request failed (${response.status})`);
        } else {
            showMessage("");
        }
    } catch (err) {
        showMessage(`Network error: ${err.message}`);
    }
}

buttons.start.addEventListener("click", () => post("/scan/start"));
buttons.stop.addEventListener("click", () => post("/scan/stop"));
buttons.photo.addEventListener("click", () => post("/camera/photo"));
buttons.cw.addEventListener("click", () => post("/motor/cw"));
buttons.ccw.addEventListener("click", () => post("/motor/ccw"));

function render(s) {
    const percent = s.total > 0 ? (100 * s.photo) / s.total : 0;
    $("progress-bar").style.width = `${percent}%`;
    $("progress-text").textContent = `${s.photo} / ${s.total}`;

    $("phone").textContent = s.phone_connected ? "connected" : "not connected";

    let state = "idle";
    if (s.stopping) state = "stopping…";
    else if (s.running) state = "scanning";
    else if (s.busy) state = "busy";
    $("state").textContent = state;

    if (s.error) showMessage(`Last scan failed: ${s.error}`);

    buttons.start.disabled = s.busy || !s.phone_connected;
    buttons.stop.disabled = !s.running || s.stopping;
    buttons.photo.disabled = s.busy || !s.phone_connected;
    buttons.cw.disabled = s.busy;
    buttons.ccw.disabled = s.busy;
}

function setConnection(online) {
    const badge = $("connection");
    badge.textContent = online ? "Online" : "Offline";
    badge.classList.toggle("badge-on", online);
    badge.classList.toggle("badge-off", !online);
}

const events = new EventSource("/events");
events.onopen = () => setConnection(true);
events.onerror = () => setConnection(false);
events.onmessage = (event) => {
    try {
        render(JSON.parse(event.data));
    } catch (err) {
        console.error("Bad status message", err);
    }
};
