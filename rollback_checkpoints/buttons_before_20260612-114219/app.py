import streamlit as st
import streamlit.components.v1 as components

import navigation
from session import initialize_session
from pages.home import show_home
from pages.learning import show_learning
from pages.mock_exam import show_mock_exam
from pages.music import show_music
from pages.review import show_review
from pages.progress import show_progress


st.set_page_config(
    page_title="Leila EST Prep",
    layout="wide",
    initial_sidebar_state="collapsed"
)

initialize_session()

page = navigation.app_navigation()

st.markdown("""
<style>

[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none;
}

.stApp {
    background:
        radial-gradient(circle at 8% 16%, rgba(255, 179, 214, 0.42), transparent 18%),
        radial-gradient(circle at 92% 18%, rgba(222, 184, 255, 0.34), transparent 22%),
        radial-gradient(circle at 88% 82%, rgba(255, 214, 232, 0.66), transparent 25%),
        linear-gradient(135deg, #fff9fc 0%, #fff3f8 46%, #f8ecff 100%);
}

.stApp::before {
    content: "🦋   ✧   ♡";
    position: fixed;
    top: 112px;
    left: 36px;
    z-index: 0;
    color: rgba(220, 117, 173, 0.28);
    font-size: clamp(28px, 5vw, 58px);
    pointer-events: none;
}

.stApp::after {
    content: "♡   ✧   🦋";
    position: fixed;
    right: 36px;
    bottom: 82px;
    z-index: 0;
    color: rgba(184, 104, 210, 0.22);
    font-size: clamp(24px, 4vw, 52px);
    pointer-events: none;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    position: relative;
    z-index: 1;
}

.top-nav-title {
    text-align: center;
    font-size: clamp(22px, 2.8vw, 28px);
    font-weight: 900;
    color: #0f172a;
    margin: 1rem 0 0.65rem;
    letter-spacing: 0.01em;
}

.active-section-banner {
    width: fit-content;
    margin: 0 auto 1.5rem;
    padding: 0.55rem 1.2rem;
    border-radius: 999px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    color: white;
    font-size: clamp(16px, 2vw, 18px);
    font-weight: 900;
    box-shadow: 0 12px 26px rgba(37, 99, 235, 0.28);
}

.stButton button {
    min-height: 50px;
    border-radius: 8px;
    border: 1px solid #dbe3ef;
    background: white;
    color: #1f2937;
    font-size: clamp(14px, 1.4vw, 17px);
    font-weight: 500;
    white-space: normal;
    line-height: 1.15;
}

.stLinkButton a {
    min-height: 50px;
    border-radius: 8px;
    border: 1px solid #dbe3ef;
    background: white;
    color: #1f2937;
    font-size: clamp(14px, 1.4vw, 17px);
    font-weight: 500;
    white-space: normal;
    line-height: 1.15;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
}

.stButton button:hover {
    border-color: #93c5fd;
    background: #eaf3ff;
    color: #0f172a;
}

.stLinkButton a:hover {
    border-color: #93c5fd;
    background: #eaf3ff;
    color: #0f172a;
}

.global-footer {
    margin-top: 1rem;
    padding: 1rem 1.25rem;
    border-radius: 0.5rem;
    background: #e8f2ff;
    color: #0056a8;
    font-size: clamp(15px, 2vw, 18px);
    font-weight: 500;
    overflow-wrap: anywhere;
}

.home-page-tight + .global-footer,
.home-page-tight ~ .global-footer {
    margin-top: 0.75rem;
}

h1 {
    font-size: clamp(30px, 5vw, 50px) !important;
    line-height: 1.15 !important;
}

h2 {
    font-size: clamp(24px, 4vw, 34px) !important;
}

h3 {
    font-size: clamp(20px, 3vw, 28px) !important;
}

p, li, div {
    overflow-wrap: anywhere;
}

iframe {
    max-width: 100%;
    border-radius: 16px;
}

/* Mobile optimization */
@media (max-width: 1100px) {
    div[data-testid="column"] {
        min-width: 140px;
    }
}

@media (max-width: 768px) {

    .block-container {
        max-width: 100%;
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    p, div {
        font-size: 15px !important;
    }

    .stSelectbox {
        width: 100%;
    }
}

@media (max-width: 430px) {
    .global-footer {
        padding: 0.9rem;
    }

    p, div {
        font-size: 14px !important;
    }
}

</style>
""", unsafe_allow_html=True)


def show_floating_explanation_pad():
    components.html(
        """
        <script>
        (() => {
            const doc = window.parent.document;
            const oldPad = doc.getElementById("leila-floating-pad");
            if (oldPad) oldPad.remove();

            const styleId = "leila-floating-pad-style";
            if (!doc.getElementById(styleId)) {
                const style = doc.createElement("style");
                style.id = styleId;
                style.textContent = `
                    #leila-floating-pad {
                        position: fixed;
                        right: 24px;
                        bottom: 24px;
                        width: 560px;
                        height: 420px;
                        min-width: 300px;
                        min-height: 230px;
                        max-width: calc(100vw - 32px);
                        max-height: calc(100vh - 32px);
                        z-index: 999999;
                        background: #ffffff;
                        border: 1px solid #cbd5e1;
                        border-radius: 16px;
                        box-shadow: 0 22px 70px rgba(15, 23, 42, 0.22);
                        overflow: hidden;
                        resize: both;
                        font-family: Arial, sans-serif;
                    }
                    #leila-floating-pad.minimized {
                        width: 260px !important;
                        height: 54px !important;
                        min-height: 54px;
                        resize: none;
                    }
                    #leila-floating-pad.minimized .pad-body {
                        display: none;
                    }
                    #leila-floating-pad .pad-header {
                        height: 48px;
                        cursor: move;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        gap: 8px;
                        padding: 0 10px 0 14px;
                        background: linear-gradient(135deg, #2563eb, #7c3aed);
                        color: white;
                        font-weight: 800;
                        user-select: none;
                    }
                    #leila-floating-pad .pad-header button,
                    #leila-floating-pad .pad-tools button {
                        border: 0;
                        border-radius: 8px;
                        padding: 7px 9px;
                        cursor: pointer;
                        font-weight: 700;
                    }
                    #leila-floating-pad .pad-header button {
                        background: rgba(255, 255, 255, 0.18);
                        color: white;
                    }
                    #leila-floating-pad .pad-body {
                        height: calc(100% - 48px);
                        display: flex;
                        flex-direction: column;
                    }
                    #leila-floating-pad .pad-tools {
                        display: flex;
                        flex-wrap: wrap;
                        align-items: center;
                        gap: 8px;
                        padding: 8px;
                        background: #f8fafc;
                        border-bottom: 1px solid #e2e8f0;
                    }
                    #leila-floating-pad .pad-tools button {
                        background: #e2e8f0;
                        color: #0f172a;
                    }
                    #leila-floating-pad .pad-tools button.active {
                        background: #2563eb;
                        color: white;
                    }
                    #leila-floating-pad input[type="color"] {
                        width: 38px;
                        height: 34px;
                        border: 0;
                        background: transparent;
                        cursor: pointer;
                    }
                    #leila-floating-pad input[type="range"] {
                        width: 92px;
                    }
                    #leila-floating-pad input[type="text"] {
                        height: 34px;
                        width: 180px;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        padding: 0 9px;
                        font-size: 14px;
                        color: #0f172a;
                    }
                    #leila-floating-pad .pad-status {
                        padding: 0 10px 7px;
                        font-size: 12px;
                        color: #475569;
                        background: #f8fafc;
                    }
                    #leila-floating-pad .pad-canvas-wrap {
                        position: relative;
                        flex: 1;
                        min-height: 0;
                        background-size: 32px 32px;
                        background-image:
                            linear-gradient(to right, rgba(148,163,184,.22) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(148,163,184,.22) 1px, transparent 1px);
                    }
                    #leila-floating-pad canvas {
                        width: 100%;
                        height: 100%;
                        display: block;
                        cursor: crosshair;
                        touch-action: none;
                    }
                    @media (max-width: 768px) {
                        #leila-floating-pad {
                            left: 10px;
                            right: auto;
                            bottom: 10px;
                            width: calc(100vw - 20px);
                            height: 48vh;
                        }
                        #leila-floating-pad .pad-tools {
                            gap: 5px;
                        }
                        #leila-floating-pad .pad-tools button {
                            padding: 6px 7px;
                            font-size: 12px;
                        }
                        #leila-floating-pad input[type="text"] {
                            width: 128px;
                        }
                    }
                `;
                doc.head.appendChild(style);
            }

            const pad = doc.createElement("div");
            pad.id = "leila-floating-pad";
            pad.innerHTML = `
                <div class="pad-header">
                    <span>Explanation Pad</span>
                    <span>
                        <button type="button" data-action="minimize">_</button>
                        <button type="button" data-action="hide">Hide</button>
                    </span>
                </div>
                <div class="pad-body">
                    <div class="pad-tools">
                        <button type="button" data-tool="pen" class="active">Pen</button>
                        <button type="button" data-tool="autoText">Auto Text</button>
                        <button type="button" data-tool="text">Text</button>
                        <button type="button" data-tool="eraser">Eraser</button>
                        <input type="text" data-action="typedText" placeholder="Type text..." />
                        <input type="color" data-action="color" value="#111827" title="Pen color" />
                        <label>Size <input type="range" data-action="size" min="2" max="32" value="5" /></label>
                        <button type="button" data-action="undo">Undo</button>
                        <button type="button" data-action="clear">Clear</button>
                        <button type="button" data-action="grid">Grid</button>
                        <button type="button" data-action="download">Download</button>
                    </div>
                    <div class="pad-status" data-role="pad-status">Pen mode: write freely on any page.</div>
                    <div class="pad-canvas-wrap">
                        <canvas></canvas>
                    </div>
                </div>
            `;

            const reopen = doc.createElement("button");
            reopen.id = "leila-floating-pad-reopen";
            reopen.textContent = "Open Pad";
            reopen.style.cssText = `
                position: fixed;
                right: 24px;
                bottom: 24px;
                z-index: 999998;
                display: none;
                border: 0;
                border-radius: 999px;
                padding: 12px 18px;
                background: #2563eb;
                color: white;
                font-weight: 800;
                box-shadow: 0 12px 30px rgba(37,99,235,.28);
                cursor: pointer;
            `;

            doc.body.appendChild(pad);
            doc.body.appendChild(reopen);
            pad.style.display = "none";
            reopen.style.display = "block";

            const canvas = pad.querySelector("canvas");
            const ctx = canvas.getContext("2d");
            const wrap = pad.querySelector(".pad-canvas-wrap");
            const colorInput = pad.querySelector('[data-action="color"]');
            const sizeInput = pad.querySelector('[data-action="size"]');
            const textInput = pad.querySelector('[data-action="typedText"]');
            const statusLine = pad.querySelector('[data-role="pad-status"]');
            let drawing = false;
            let tool = "pen";
            let history = [];
            let gridOn = true;
            let strokePoints = [];

            function resizeCanvas() {
                const saved = canvas.toDataURL("image/png");
                const rect = canvas.getBoundingClientRect();
                const scale = window.parent.devicePixelRatio || 1;
                canvas.width = Math.max(1, Math.floor(rect.width * scale));
                canvas.height = Math.max(1, Math.floor(rect.height * scale));
                ctx.setTransform(scale, 0, 0, scale, 0, 0);
                ctx.lineCap = "round";
                ctx.lineJoin = "round";
                if (saved && saved.length > 100) {
                    const img = new Image();
                    img.onload = () => ctx.drawImage(img, 0, 0, rect.width, rect.height);
                    img.src = saved;
                }
            }

            function saveBoard() {
                try {
                    window.parent.localStorage.setItem("leila-pad-image", canvas.toDataURL("image/png"));
                } catch (_) {}
            }

            function loadBoard() {
                const saved = window.parent.localStorage.getItem("leila-pad-image");
                if (!saved) return;
                const img = new Image();
                img.onload = () => {
                    const rect = canvas.getBoundingClientRect();
                    ctx.drawImage(img, 0, 0, rect.width, rect.height);
                };
                img.src = saved;
            }

            function pushHistory() {
                try {
                    history.push(canvas.toDataURL("image/png"));
                    if (history.length > 25) history.shift();
                } catch (_) {}
            }

            function pointerPosition(event) {
                const rect = canvas.getBoundingClientRect();
                return {
                    x: event.clientX - rect.left,
                    y: event.clientY - rect.top
                };
            }

            function setStatus(message) {
                statusLine.textContent = message;
            }

            function restoreImage(dataUrl, afterRestore) {
                if (!dataUrl) return;
                const img = new Image();
                img.onload = () => {
                    const rect = canvas.getBoundingClientRect();
                    ctx.clearRect(0, 0, rect.width, rect.height);
                    ctx.drawImage(img, 0, 0, rect.width, rect.height);
                    if (afterRestore) afterRestore();
                    saveBoard();
                };
                img.src = dataUrl;
            }

            function drawCleanText(text, x, y) {
                if (!text) return;
                ctx.save();
                ctx.globalCompositeOperation = "source-over";
                ctx.font = "24px Arial, sans-serif";
                ctx.fillStyle = colorInput.value;
                ctx.textBaseline = "middle";
                ctx.fillText(text, x, y);
                ctx.restore();
            }

            function eraseAt(pos) {
                const eraserSize = Math.max(18, Number(sizeInput.value) * 3);
                ctx.save();
                ctx.globalCompositeOperation = "destination-out";
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, eraserSize / 2, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }

            function strokeBounds(points) {
                const xs = points.map((point) => point.x);
                const ys = points.map((point) => point.y);
                return {
                    left: Math.min(...xs),
                    right: Math.max(...xs),
                    top: Math.min(...ys),
                    bottom: Math.max(...ys)
                };
            }

            async function convertStrokeToText() {
                const previous = history[history.length - 1];
                const typedFallback = textInput.value.trim();
                const bounds = strokeBounds(strokePoints);
                const x = bounds.left;
                const y = bounds.top + Math.max(24, (bounds.bottom - bounds.top) / 2);

                if (typedFallback) {
                    restoreImage(previous, () => drawCleanText(typedFallback, x, y));
                    setStatus("Auto Text placed clean medium text from the text box.");
                    return;
                }

                const handwritingFactory = window.parent.navigator.createHandwritingRecognizer;
                if (!handwritingFactory) {
                    setStatus("Auto Text needs browser handwriting recognition. Type in the box, then write/tap where it should appear.");
                    saveBoard();
                    return;
                }

                try {
                    const recognizer = await handwritingFactory.call(window.parent.navigator, { languages: ["en"] });
                    if (!recognizer || typeof recognizer.startDrawing !== "function") {
                        setStatus("This browser exposes handwriting recognition but cannot read this canvas stroke. Use Text mode.");
                        saveBoard();
                        return;
                    }
                    setStatus("Handwriting recognition is available, but this browser API cannot convert the existing canvas stroke directly. Use the text box for clean placement.");
                    saveBoard();
                } catch (_) {
                    setStatus("Auto Text recognition is unavailable in this browser. Use Text mode.");
                    saveBoard();
                }
            }

            function startDraw(event) {
                event.preventDefault();
                const pos = pointerPosition(event);

                if (tool === "text") {
                    const text = textInput.value.trim();
                    if (!text) {
                        textInput.focus();
                        setStatus("Text mode: type in the box, then tap the pad to place clean medium text.");
                        return;
                    }
                    pushHistory();
                    drawCleanText(text, pos.x, pos.y);
                    saveBoard();
                    setStatus("Text placed. Change the box text and tap again to add more.");
                    return;
                }

                pushHistory();
                drawing = true;
                strokePoints = [pos];
                ctx.beginPath();
                ctx.moveTo(pos.x, pos.y);
                if (tool === "eraser") {
                    eraseAt(pos);
                    setStatus("Eraser mode: larger eraser is active.");
                }
            }

            function draw(event) {
                if (!drawing) return;
                event.preventDefault();
                const pos = pointerPosition(event);
                strokePoints.push(pos);
                if (tool === "eraser") {
                    eraseAt(pos);
                    return;
                }
                ctx.globalCompositeOperation = "source-over";
                ctx.strokeStyle = colorInput.value;
                ctx.lineWidth = Number(sizeInput.value);
                ctx.lineTo(pos.x, pos.y);
                ctx.stroke();
            }

            function endDraw() {
                if (!drawing) return;
                drawing = false;
                ctx.closePath();
                if (tool === "autoText") {
                    convertStrokeToText();
                } else {
                    saveBoard();
                }
            }

            canvas.addEventListener("pointerdown", startDraw);
            canvas.addEventListener("pointermove", draw);
            canvas.addEventListener("pointerup", endDraw);
            canvas.addEventListener("pointercancel", endDraw);
            canvas.addEventListener("pointerleave", endDraw);

            pad.querySelectorAll("[data-tool]").forEach((button) => {
                button.addEventListener("click", () => {
                    tool = button.dataset.tool;
                    pad.querySelectorAll("[data-tool]").forEach((item) => item.classList.remove("active"));
                    button.classList.add("active");
                    if (tool === "pen") setStatus("Pen mode: write freely on any page.");
                    if (tool === "autoText") setStatus("Auto Text: write with the pen. If the browser cannot recognize it, type in the box and write/tap to place clean text.");
                    if (tool === "text") setStatus("Text mode: type in the box, then tap the pad to place clean medium text.");
                    if (tool === "eraser") setStatus("Eraser mode: larger eraser is active.");
                });
            });

            pad.querySelector('[data-action="undo"]').addEventListener("click", () => {
                const previous = history.pop();
                if (!previous) return;
                const img = new Image();
                img.onload = () => {
                    const rect = canvas.getBoundingClientRect();
                    ctx.clearRect(0, 0, rect.width, rect.height);
                    ctx.drawImage(img, 0, 0, rect.width, rect.height);
                    saveBoard();
                };
                img.src = previous;
            });

            pad.querySelector('[data-action="clear"]').addEventListener("click", () => {
                pushHistory();
                const rect = canvas.getBoundingClientRect();
                ctx.clearRect(0, 0, rect.width, rect.height);
                saveBoard();
            });

            pad.querySelector('[data-action="grid"]').addEventListener("click", () => {
                gridOn = !gridOn;
                wrap.style.backgroundImage = gridOn
                    ? "linear-gradient(to right, rgba(148,163,184,.22) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,.22) 1px, transparent 1px)"
                    : "none";
            });

            pad.querySelector('[data-action="download"]').addEventListener("click", () => {
                const link = doc.createElement("a");
                link.download = "leila-explanation-pad.png";
                link.href = canvas.toDataURL("image/png");
                link.click();
            });

            pad.querySelector('[data-action="minimize"]').addEventListener("click", () => {
                pad.classList.toggle("minimized");
                setTimeout(resizeCanvas, 120);
            });

            pad.querySelector('[data-action="hide"]').addEventListener("click", () => {
                pad.style.display = "none";
                reopen.style.display = "block";
            });

            reopen.addEventListener("click", () => {
                pad.style.display = "block";
                reopen.style.display = "none";
                setTimeout(resizeCanvas, 120);
            });

            const header = pad.querySelector(".pad-header");
            let dragging = false;
            let dragOffsetX = 0;
            let dragOffsetY = 0;

            header.addEventListener("pointerdown", (event) => {
                if (event.target.tagName === "BUTTON") return;
                dragging = true;
                const rect = pad.getBoundingClientRect();
                dragOffsetX = event.clientX - rect.left;
                dragOffsetY = event.clientY - rect.top;
                header.setPointerCapture(event.pointerId);
            });

            header.addEventListener("pointermove", (event) => {
                if (!dragging) return;
                const maxX = window.parent.innerWidth - pad.offsetWidth;
                const maxY = window.parent.innerHeight - pad.offsetHeight;
                const nextX = Math.max(0, Math.min(maxX, event.clientX - dragOffsetX));
                const nextY = Math.max(0, Math.min(maxY, event.clientY - dragOffsetY));
                pad.style.left = `${nextX}px`;
                pad.style.top = `${nextY}px`;
                pad.style.right = "auto";
                pad.style.bottom = "auto";
            });

            header.addEventListener("pointerup", () => {
                dragging = false;
            });

            new window.parent.ResizeObserver(() => {
                resizeCanvas();
                loadBoard();
            }).observe(pad);

            setTimeout(() => {
                resizeCanvas();
                loadBoard();
            }, 200);
        })();
        </script>
        """,
        height=0,
    )


show_floating_explanation_pad()


def show_global_footer():
    st.markdown(
        '<div class="global-footer">Developed by BEBA | Ahmed Labib | 2026 Ⓡ ™</div>',
        unsafe_allow_html=True,
    )


# ---------------- HOME ----------------

if page == "Home":

    show_home()

# ---------------- LEARNING ----------------

elif page == "Learning Mode":

    show_learning()

# ---------------- MOCK EXAM ----------------

elif page == "Mock Exam":

    show_mock_exam()

# ---------------- STUDY MUSIC ----------------

elif page == "Study Music":

    show_music()

# ---------------- REVIEW ----------------

elif page == "Review Mistakes":

    show_review()

# ---------------- PROGRESS ----------------

elif page == "Progress":

    show_progress()

show_global_footer()
