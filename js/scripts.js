(() => {
  const WHATSAPP_NUMBER = "34600063369"; // solo digitos, sin +
  const COOKIE_KEY = "nova_cookie_accepted_v1";

  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  const menu = document.getElementById("menu");
  const hamburger = document.getElementById("hamburger");

  if (hamburger && menu) {
    hamburger.addEventListener("click", () => {
      const open = menu.classList.toggle("open");
      hamburger.setAttribute("aria-expanded", open ? "true" : "false");
    });

    menu.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => {
        if (menu.classList.contains("open")) {
          menu.classList.remove("open");
          hamburger.setAttribute("aria-expanded", "false");
        }
      });
    });
  }

  const toast = document.getElementById("toast");
  const showToast = (msg) => {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("show");
    toast.setAttribute("aria-hidden", "false");
    window.clearTimeout(showToast._t);
    showToast._t = window.setTimeout(() => {
      toast.classList.remove("show");
      toast.setAttribute("aria-hidden", "true");
    }, 2200);
  };

  // FAQ
  document.querySelectorAll(".faq-item .faq-q").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = btn.closest(".faq-item");
      if (!item) return;
      item.classList.toggle("open");
    });
  });

  // Cookies
  const cookieBanner = document.getElementById("cookieBanner");
  const cookieAccept = document.getElementById("cookieAccept");
  const cookieAccepted = () => localStorage.getItem(COOKIE_KEY) === "1";

  if (cookieBanner && !cookieAccepted()) cookieBanner.hidden = false;

  if (cookieAccept) {
    cookieAccept.addEventListener("click", () => {
      localStorage.setItem(COOKIE_KEY, "1");
      if (cookieBanner) cookieBanner.hidden = true;
      showToast("\u2705 Preferencia guardada");
    });
  }

  const openWhatsApp = (text) => {
    if (!WHATSAPP_NUMBER || WHATSAPP_NUMBER.includes("TU_")) {
      showToast("\u26a0\ufe0f Falta configurar el WhatsApp en scripts.js");
      return;
    }
    const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank", "noopener");
  };

  // Contact WhatsApp
  const contactWhatsapp = document.getElementById("contactWhatsapp");
  if (contactWhatsapp) {
    contactWhatsapp.addEventListener("click", (e) => {
      e.preventDefault();
      openWhatsApp("Hola, quiero informaci\u00f3n sobre una web con NovaEstudioWeb.");
    });
  }

  const whatsappFloat = document.getElementById("whatsappFloat");
  if (whatsappFloat) {
    whatsappFloat.addEventListener("click", (e) => {
      e.preventDefault();
      const text = "Hola, quiero informaci\u00f3n sobre una web con NovaEstudioWeb.";
      openWhatsApp(text);
    });
  }

  // Chat IA
  const chatModal = document.getElementById("chatModal");
  const openChatBtn = document.getElementById("openChat");
  const chatLog = document.getElementById("chatLog");
  const chatInput = document.getElementById("chatInput");
  const chatSend = document.getElementById("chatSend");
  const chatNew = document.getElementById("chatNew");
  const chatSummary = document.getElementById("chatSummary");
  const chatTyping = document.getElementById("chatTyping");
  const chatStatus = document.getElementById("chatStatus");
  const chatEndpoint = chatModal?.dataset.chatEndpoint || "";

  let lastFocus = null;
  let conversationId = null;
  let selectedPlan = "";
  let lastSummary = "";
  let history = [];

  const greetMessage = "Hola, \u00bfqu\u00e9 tipo de web quieres crear? (empresa, portfolio, ecommerce\u2026)";

  const addMessage = (role, text) => {
    if (!chatLog) return;
    const msg = document.createElement("div");
    msg.className = `chat-msg ${role}`;
    msg.textContent = text;
    chatLog.appendChild(msg);
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  const resetConversation = () => {
    conversationId = (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`);
    history = [];
    lastSummary = "";
    if (chatLog) chatLog.innerHTML = "";
    if (chatStatus) {
      chatStatus.textContent = "";
      chatStatus.classList.remove("is-visible");
    }
    addMessage("ai", greetMessage);
    if (selectedPlan) {
      addMessage("ai", `He tomado nota del paquete: ${selectedPlan}.`);
    }
  };

  const setChatStatus = (text) => {
    if (!chatStatus) return;
    if (!text) {
      chatStatus.textContent = "";
      chatStatus.classList.remove("is-visible");
      return;
    }
    chatStatus.textContent = text;
    chatStatus.classList.add("is-visible");
  };

  const openChat = () => {
    if (!chatModal) return;
    lastFocus = document.activeElement;
    chatModal.classList.add("is-open");
    chatModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    if (!conversationId) resetConversation();
    if (chatInput) chatInput.focus();
  };

  const closeChat = () => {
    if (!chatModal) return;
    chatModal.classList.remove("is-open");
    chatModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  };

  if (openChatBtn) openChatBtn.addEventListener("click", openChat);

  if (chatModal) {
    chatModal.addEventListener("click", (e) => {
      const target = e.target;
      if (target && target.getAttribute && target.getAttribute("data-close") === "1") closeChat();
    });
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && chatModal?.classList.contains("is-open")) closeChat();
  });

  const sendMessage = async () => {
    if (!chatInput || !chatEndpoint) {
      showToast("\u26a0\ufe0f Falta configurar el endpoint del chat.");
      return;
    }
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage("user", text);
    history.push({ role: "user", content: text });
    chatInput.value = "";

    if (chatTyping) chatTyping.hidden = false;
    if (chatSend) chatSend.disabled = true;

    try {
      const payload = {
        message: text,
        conversation_id: conversationId,
        metadata: {
          plan: selectedPlan,
          page: window.location.pathname,
          referrer: document.referrer || ""
        }
      };

      const res = await fetch(chatEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json().catch(() => ({}));

      if (res.ok && data.reply) {
        addMessage("ai", data.reply);
        history.push({ role: "assistant", content: data.reply });
        conversationId = data.conversation_id || conversationId;
        lastSummary = data.whatsapp_summary || lastSummary;
        if (data.status === "PENDING_OWNER_APPROVAL") {
          setChatStatus("Tu solicitud est\u00e1 en revisi\u00f3n por el equipo.");
        } else {
          setChatStatus("");
        }
      } else {
        showToast("\u274c No se pudo responder. Intenta de nuevo.");
        addMessage("ai", "Ahora mismo tengo un problema t\u00e9cnico. \u00bfQuieres que lo intentemos otra vez?");
      }
    } catch (err) {
      showToast("\u274c Error de conexi\u00f3n.");
      addMessage("ai", "No puedo conectar en este momento. \u00bfQuieres que lo intentemos m\u00e1s tarde?");
    } finally {
      if (chatTyping) chatTyping.hidden = true;
      if (chatSend) chatSend.disabled = false;
    }
  };

  if (chatSend) chatSend.addEventListener("click", sendMessage);
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  if (chatNew) {
    chatNew.addEventListener("click", () => {
      resetConversation();
      showToast("\u2705 Nueva conversaci\u00f3n");
    });
  }

  if (chatSummary) {
    chatSummary.addEventListener("click", async () => {
      const fallbackSummary = history
        .filter((m) => m.role === "user")
        .map((m) => `- ${m.content}`)
        .join("\n");

      const summary = lastSummary || `Resumen de lo hablado:\n${fallbackSummary || "- Sin detalles a\u00fan."}`;
      openWhatsApp(summary);
    });
  }

  document.querySelectorAll(".plan-cta").forEach((cta) => {
    cta.addEventListener("click", (e) => {
      e.preventDefault();
      selectedPlan = cta.dataset.plan || "Paquete";
      showToast(`\u2705 Plan seleccionado: ${selectedPlan}`);
      openChat();
    });
  });
})();
