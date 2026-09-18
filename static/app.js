const $ = (id) => document.getElementById(id);
let selectedFiles = [];

// ---- file selection -------------------------------------------------------
const drop = $("drop");
const fileInput = $("files");

$("browse").addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => setFiles([...fileInput.files]));

["dragenter", "dragover"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("over"); })
);
["dragleave", "drop"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("over"); })
);
drop.addEventListener("drop", (ev) => setFiles([...ev.dataTransfer.files]));

function setFiles(files) {
  selectedFiles = files;
  const btn = $("uploadBtn");
  btn.disabled = files.length === 0;
  btn.textContent = files.length ? `Index ${files.length} file(s)` : "Index files";
}

// ---- upload ---------------------------------------------------------------
$("uploadBtn").addEventListener("click", async () => {
  if (!selectedFiles.length) return;
  const status = $("uploadStatus");
  status.className = "status";
  status.textContent = "Indexing… (first run loads the embedding model, ~10–20s)";
  $("uploadBtn").disabled = true;

  const fd = new FormData();
  selectedFiles.forEach((f) => fd.append("files", f));

  try {
    const res = await fetch("/upload", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Upload failed");
    const total = data.indexed.reduce((s, d) => s + d.chunks, 0);
    status.className = "status ok";
    status.textContent =
      `Indexed ${data.indexed.length} file(s), ${total} chunks in ${data.elapsed_ms} ms.` +
      (data.skipped.length ? ` Skipped: ${data.skipped.join(", ")}` : "");
    selectedFiles = [];
    setFiles([]);
    refreshCorpus();
  } catch (err) {
    status.className = "status err";
    status.textContent = err.message;
  } finally {
    $("uploadBtn").disabled = false;
  }
});

// ---- corpus info ----------------------------------------------------------
async function refreshCorpus() {
  const res = await fetch("/documents");
  const data = await res.json();
  const docs = Object.entries(data.documents || {});
  const info = $("corpusInfo");
  const resetBtn = $("resetBtn");
  if (!docs.length) {
    info.textContent = "No documents indexed.";
    resetBtn.hidden = true;
  } else {
    const list = docs.map(([n, c]) => `${n} (${c})`).join(", ");
    info.textContent = `${data.total_chunks} chunks · ${data.embedding_model} · ${list}`;
    resetBtn.hidden = false;
  }
}

$("resetBtn").addEventListener("click", async () => {
  if (!confirm("Remove all indexed documents?")) return;
  await fetch("/reset", { method: "POST" });
  $("results").innerHTML = "";
  $("latency").textContent = "";
  refreshCorpus();
});

// ---- query ----------------------------------------------------------------
async function ask() {
  const question = $("question").value.trim();
  if (!question) return;
  const results = $("results");
  results.innerHTML = `<p class="rank">Searching…</p>`;
  $("latency").textContent = "";

  try {
    const res = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, top_k: Number($("topk").value) || 5 }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Query failed");
    render(data);
  } catch (err) {
    results.innerHTML = `<p class="status err">${err.message}</p>`;
  }
}

$("askBtn").addEventListener("click", ask);
$("question").addEventListener("keydown", (e) => { if (e.key === "Enter") ask(); });

function render(data) {
  $("latency").textContent = `retrieved in ${data.elapsed_ms} ms`;
  const results = $("results");
  if (!data.results.length) {
    results.innerHTML = `<p class="rank">No matches found.</p>`;
    return;
  }
  results.innerHTML = data.results
    .map((r, i) => {
      const badges = r.matched_by
        .map((m) =>
          m === "semantic"
            ? `<span class="badge sem">semantic</span>`
            : `<span class="badge kw">keyword</span>`
        )
        .join("");
      const dense = r.dense_score != null ? `sim ${r.dense_score}` : "";
      const bm25 = r.bm25_score != null ? `bm25 ${r.bm25_score}` : "";
      return `
        <div class="card">
          <div class="meta">
            <span class="rank">#${i + 1}</span>
            <span class="src">${escapeHtml(r.source)}</span>
            <span>p.${r.page}</span>
            ${badges}
            <span>rrf ${r.rrf_score}</span>
            ${dense ? `<span>${dense}</span>` : ""}
            ${bm25 ? `<span>${bm25}</span>` : ""}
          </div>
          <div class="text">${escapeHtml(r.text)}</div>
        </div>`;
    })
    .join("");
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

refreshCorpus();
