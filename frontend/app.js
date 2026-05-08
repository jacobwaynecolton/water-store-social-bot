// Refresh interval in ms — fast enough to see a new post appear after "Post Now"
const REFRESH_MS = 15_000;

async function fetchJSON(url, opts = {}) {
  const resp = await fetch(url, opts);
  if (!resp.ok) throw new Error(`${url} → ${resp.status}`);
  return resp.json();
}

function fmt(isoStr) {
  if (!isoStr) return "—";
  return new Date(isoStr).toLocaleString("en-CA", {
    month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function statusPill(status) {
  const cls = { posted: "pill-posted", pending: "pill-pending", failed: "pill-failed" }[status] ?? "";
  return `<span class="pill ${cls}">${status}</span>`;
}

// --- Status & jobs ---
async function loadStatus() {
  try {
    const data = await fetchJSON("/api/status");
    const badge = document.getElementById("status-badge");
    badge.textContent = data.running ? "running" : "paused";
    badge.className = `badge ${data.running ? "badge-running" : "badge-paused"}`;

    const rows = data.jobs.map(j => `
      <tr>
        <td>${j.id}</td>
        <td>${fmt(j.next_run)}</td>
      </tr>
    `).join("");
    document.getElementById("jobs-body").innerHTML = rows || `<tr><td colspan="2" class="empty">No jobs found</td></tr>`;
  } catch (e) {
    console.error("Status load failed:", e);
  }
}

// --- Modal ---
let _posts = [];

function openModal(post) {
  document.getElementById("modal-img").src = post.image_url ?? "";
  document.getElementById("modal-img").style.display = post.image_url ? "block" : "none";
  document.getElementById("modal-theme").textContent = post.theme ?? "unknown theme";
  document.getElementById("modal-status").className = `pill ${
    { posted: "pill-posted", pending: "pill-pending", failed: "pill-failed" }[post.status] ?? ""
  }`;
  document.getElementById("modal-status").textContent = post.status;
  document.getElementById("modal-date").textContent = fmt(post.posted_at);
  document.getElementById("modal-caption").textContent = post.caption ?? "No caption";
  document.getElementById("modal-overlay").classList.remove("hidden");
}

document.getElementById("modal-close").addEventListener("click", () => {
  document.getElementById("modal-overlay").classList.add("hidden");
});
document.getElementById("modal-overlay").addEventListener("click", (e) => {
  if (e.target === document.getElementById("modal-overlay")) {
    document.getElementById("modal-overlay").classList.add("hidden");
  }
});

// --- Posts ---
async function loadPosts() {
  try {
    const posts = await fetchJSON("/api/posts");
    _posts = posts;
    if (!posts.length) {
      document.getElementById("posts-body").innerHTML = `<tr><td colspan="6" class="empty">No posts yet</td></tr>`;
      return;
    }
    const rows = posts.map((p, i) => {
      const fbLink = p.facebook_post_id && p.facebook_post_id !== "dry-run"
        ? `<a href="https://facebook.com/${p.facebook_post_id}" target="_blank"><span class="pill pill-fb">FB</span></a>`
        : `<span style="color:#94a3b8;font-size:12px">${p.facebook_post_id === "dry-run" ? "dry-run" : "—"}</span>`;
      const igLink = p.instagram_post_id && p.instagram_post_id !== "dry-run"
        ? `<a href="https://instagram.com/p/${p.instagram_post_id}" target="_blank"><span class="pill pill-ig">IG</span></a>`
        : `<span style="color:#94a3b8;font-size:12px">${p.instagram_post_id === "dry-run" ? "dry-run" : "—"}</span>`;
      const caption = p.caption ? p.caption.slice(0, 80) + (p.caption.length > 80 ? "…" : "") : "—";
      return `
        <tr class="clickable" data-idx="${i}" title="Click to view full post">
          <td>${p.theme ?? "—"}</td>
          <td>${statusPill(p.status)}${p.error ? `<br><small style="color:#ef4444">${p.error.slice(0, 60)}</small>` : ""}</td>
          <td>${fmt(p.posted_at)}</td>
          <td class="caption-cell" style="white-space:normal;max-width:260px">${caption}</td>
          <td>${fbLink}</td>
          <td>${igLink}</td>
        </tr>
      `;
    }).join("");
    document.getElementById("posts-body").innerHTML = rows;

    // Attach click handlers to each row
    document.querySelectorAll("#posts-body tr.clickable").forEach(row => {
      row.addEventListener("click", () => openModal(_posts[+row.dataset.idx]));
    });

  } catch (e) {
    console.error("Posts load failed:", e);
  }
}

// --- Comments ---
async function loadComments() {
  try {
    const comments = await fetchJSON("/api/comments");
    if (!comments.length) {
      document.getElementById("comments-body").innerHTML = `<tr><td colspan="5" class="empty">No comments yet</td></tr>`;
      return;
    }
    const rows = comments.map(c => `
      <tr>
        <td><span class="pill ${c.platform === "facebook" ? "pill-fb" : "pill-ig"}">${c.platform}</span></td>
        <td>${c.commenter}</td>
        <td style="white-space:normal;max-width:200px">${c.comment}</td>
        <td style="white-space:normal;max-width:200px;color:#475569">${c.reply ?? '<em>not replied</em>'}</td>
        <td>${fmt(c.replied_at)}</td>
      </tr>
    `).join("");
    document.getElementById("comments-body").innerHTML = rows;
  } catch (e) {
    console.error("Comments load failed:", e);
  }
}

function refreshAll() {
  loadStatus();
  loadPosts();
  loadComments();
}

// --- Controls ---
document.getElementById("btn-post-now").addEventListener("click", async () => {
  const btn = document.getElementById("btn-post-now");
  btn.disabled = true;
  btn.textContent = "Starting...";
  try {
    await fetchJSON("/api/post-now", { method: "POST" });
    btn.textContent = "Job started!";
    // Give the job a few seconds then refresh
    setTimeout(refreshAll, 4000);
  } catch (e) {
    btn.textContent = "Error";
  }
  setTimeout(() => { btn.disabled = false; btn.textContent = "Post Now"; }, 5000);
});

document.getElementById("btn-pause").addEventListener("click", async () => {
  await fetchJSON("/api/pause", { method: "POST" });
  loadStatus();
});

document.getElementById("btn-resume").addEventListener("click", async () => {
  await fetchJSON("/api/resume", { method: "POST" });
  loadStatus();
});

// Initial load + polling
refreshAll();
setInterval(refreshAll, REFRESH_MS);
