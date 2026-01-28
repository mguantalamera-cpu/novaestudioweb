const apiOrigin = document.body?.dataset?.apiBase || "";
const apiBase = apiOrigin ? `${apiOrigin}/api/admin/conversations` : "/api/admin/conversations";
let authHeader = "";
let selectedId = "";

const statusEl = document.getElementById("adminStatus");
const listEl = document.getElementById("convoList");
const detailEl = document.getElementById("convoDetail");
const loginForm = document.getElementById("loginForm");
const refreshBtn = document.getElementById("refreshList");

const setStatus = (text) => {
  if (statusEl) statusEl.textContent = text || "";
};

const apiFetch = async (url, options = {}) => {
  if (!authHeader) throw new Error("No auth");
  const headers = Object.assign({ "Content-Type": "application/json", "Authorization": authHeader }, options.headers || {});
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) throw new Error("Auth");
  return res;
};

const renderList = (items = []) => {
  if (!listEl) return;
  listEl.innerHTML = "";
  items.forEach(item => {
    const el = document.createElement("div");
    el.className = "admin-item";
    el.dataset.id = item.id;
    el.innerHTML = `
      <strong>${item.id}</strong>
      <small>Estado: ${item.status} · Lead: ${item.lead_score || 0}</small>
      <small>${item.last_message || ""}</small>
    `;
    el.addEventListener("click", () => loadConversation(item.id));
    listEl.appendChild(el);
  });
};

const renderDetail = (conversation, messages) => {
  if (!detailEl) return;
  if (!conversation) {
    detailEl.innerHTML = "<p>Selecciona una conversación para ver los detalles.</p>";
    return;
  }

  const approved = conversation.status === "APPROVED";
  const briefJson = JSON.stringify(conversation.extracted_brief || {}, null, 2);

  detailEl.innerHTML = `
    <div class="admin-badge">Estado: ${conversation.status}</div>
    <div><strong>Lead score:</strong> ${conversation.lead_score || 0}</div>
    <div class="admin-actions">
      <button class="boton" id="approveBtn" type="button">APROBAR</button>
      <button class="boton boton--ghost" id="rejectBtn" type="button">RECHAZAR</button>
      <button class="boton boton--ghost" id="deleteBtn" type="button">BORRAR</button>
      <button class="boton" id="exportBtn" type="button" ${approved ? "" : "disabled"}>Generar resumen final</button>
    </div>
    <h3>Brief extraído</h3>
    <pre class="admin-json">${briefJson}</pre>
    <h3>Mensajes</h3>
    <div class="admin-messages">
      ${messages.map(m => `<div class="admin-msg ${m.role}">${m.role}: ${m.content}</div>`).join("")}
    </div>
  `;

  document.getElementById("approveBtn").addEventListener("click", () => updateStatus("approve"));
  document.getElementById("rejectBtn").addEventListener("click", () => updateStatus("reject"));
  document.getElementById("deleteBtn").addEventListener("click", () => updateStatus("delete"));
  document.getElementById("exportBtn").addEventListener("click", () => exportBrief());
};

const loadList = async () => {
  try {
    setStatus("Cargando...");
    const res = await apiFetch(apiBase);
    const data = await res.json();
    renderList(data.conversations || []);
    setStatus("OK");
  } catch (err) {
    setStatus(err.message === "Auth" ? "Credenciales inválidas." : "No se pudo cargar la lista.");
  }
};

const loadConversation = async (id) => {
  selectedId = id;
  try {
    setStatus("Cargando conversación...");
    const res = await apiFetch(`${apiBase}?id=${encodeURIComponent(id)}`);
    const data = await res.json();
    renderDetail(data.conversation, data.messages || []);
    setStatus("OK");
  } catch (err) {
    setStatus("No se pudo cargar la conversación.");
  }
};

const updateStatus = async (action) => {
  if (!selectedId) return;
  try {
    const res = await apiFetch(apiBase, {
      method: "POST",
      body: JSON.stringify({ action, conversation_id: selectedId })
    });
    await res.json();
    await loadConversation(selectedId);
    await loadList();
  } catch (err) {
    setStatus("No se pudo actualizar el estado.");
  }
};

const exportBrief = async () => {
  if (!selectedId) return;
  try {
    const res = await apiFetch(apiBase, {
      method: "POST",
      body: JSON.stringify({ action: "export", conversation_id: selectedId })
    });
    const data = await res.json();
    if (!res.ok) {
      setStatus(data.error || "No se pudo exportar.");
      return;
    }
    const jsonBlob = new Blob([JSON.stringify(data.brief || {}, null, 2)], { type: "application/json" });
    const mdBlob = new Blob([data.markdown || ""], { type: "text/markdown" });
    const jsonUrl = URL.createObjectURL(jsonBlob);
    const mdUrl = URL.createObjectURL(mdBlob);

    const jsonLink = document.createElement("a");
    jsonLink.href = jsonUrl;
    jsonLink.download = `brief-${selectedId}.json`;
    jsonLink.click();

    const mdLink = document.createElement("a");
    mdLink.href = mdUrl;
    mdLink.download = `brief-${selectedId}.md`;
    mdLink.click();

    URL.revokeObjectURL(jsonUrl);
    URL.revokeObjectURL(mdUrl);
    setStatus("Exportado.");
  } catch (err) {
    setStatus("No se pudo exportar.");
  }
};

if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const user = document.getElementById("adminUser").value.trim();
    const pass = document.getElementById("adminPass").value.trim();
    if (!user || !pass) return;
    authHeader = `Basic ${btoa(`${user}:${pass}`)}`;
    loadList();
  });
}

if (refreshBtn) {
  refreshBtn.addEventListener("click", () => loadList());
}
