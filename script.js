const API_BASE = "http://localhost:8000";

// ---- Tabs ----
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");

    if (btn.dataset.tab === "users") loadUsers();
  });
});

// ---- Camera setup ----
async function startCamera(videoEl) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    videoEl.srcObject = stream;
  } catch (err) {
    console.error("Camera access failed:", err);
  }
}

const videoRegister = document.getElementById("video-register");
const videoPay = document.getElementById("video-pay");
startCamera(videoRegister);
startCamera(videoPay);

function captureFrame(videoEl, canvasEl) {
  canvasEl.width = videoEl.videoWidth;
  canvasEl.height = videoEl.videoHeight;
  const ctx = canvasEl.getContext("2d");
  ctx.drawImage(videoEl, 0, 0);
  return canvasEl.toDataURL("image/jpeg", 0.85);
}

// ---- Register ----
document.getElementById("capture-register-btn").addEventListener("click", async () => {
  const name = document.getElementById("name").value.trim();
  const balance = parseFloat(document.getElementById("balance").value) || 0;
  const resultEl = document.getElementById("register-result");

  if (!name) {
    resultEl.textContent = "Please enter your name.";
    resultEl.className = "result-msg error";
    return;
  }

  const imageData = captureFrame(videoRegister, document.getElementById("canvas-register"));

  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, image_base64: imageData, starting_balance: balance }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed");

    resultEl.textContent = `Registered! ${data.name} (ID: ${data.user_id}) — balance $${data.balance}`;
    resultEl.className = "result-msg success";
  } catch (err) {
    resultEl.textContent = `Error: ${err.message}`;
    resultEl.className = "result-msg error";
  }
});

// ---- Pay ----
document.getElementById("capture-pay-btn").addEventListener("click", async () => {
  const amount = parseFloat(document.getElementById("amount").value) || 0;
  const merchant = document.getElementById("merchant").value.trim() || "Demo Store";
  const resultEl = document.getElementById("pay-result");

  const imageData = captureFrame(videoPay, document.getElementById("canvas-pay"));

  try {
    const res = await fetch(`${API_BASE}/pay`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_base64: imageData, amount, merchant }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Payment failed");

    resultEl.textContent = `✅ Paid $${amount} to ${merchant}\nUser: ${data.user}\nMatch confidence: ${data.match_confidence}\nNew balance: $${data.transaction.balance_after}`;
    resultEl.className = "result-msg success";
  } catch (err) {
    resultEl.textContent = `Error: ${err.message}`;
    resultEl.className = "result-msg error";
  }
});

// ---- Users list ----
async function loadUsers() {
  const listEl = document.getElementById("users-list");
  listEl.innerHTML = "<li>Loading...</li>";
  try {
    const res = await fetch(`${API_BASE}/users`);
    const data = await res.json();
    listEl.innerHTML = "";
    if (data.users.length === 0) {
      listEl.innerHTML = "<li>No users registered yet.</li>";
      return;
    }
    data.users.forEach((u) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>${u.name}</span><span>$${u.balance.toFixed(2)}</span>`;
      listEl.appendChild(li);
    });
  } catch (err) {
    listEl.innerHTML = `<li>Couldn't reach API: ${err.message}</li>`;
  }
}

document.getElementById("refresh-users-btn").addEventListener("click", loadUsers);
