import crypto from "crypto";
import nodemailer from "nodemailer";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.SUPABASE_URL || "";
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

export const getSupabase = () => {
  if (!supabaseUrl || !supabaseKey) return null;
  if (!globalThis.__supabase) {
    globalThis.__supabase = createClient(supabaseUrl, supabaseKey, {
      auth: { persistSession: false }
    });
  }
  return globalThis.__supabase;
};

export const applyCors = (req, res) => {
  const allowed = (process.env.ALLOWED_ORIGIN || "")
    .split(/[\s,]+/)
    .map(v => v.trim())
    .filter(Boolean);
  const origin = req.headers.origin || "";

  if (allowed.length && origin && !allowed.includes(origin)) {
    res.status(403).json({ error: "Origen no permitido." });
    return false;
  }

  if (origin) res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Vary", "Origin");
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.status(204).end();
    return false;
  }
  return true;
};

export const getClientIp = (req) =>
  (req.headers["x-forwarded-for"] || req.socket?.remoteAddress || "")
    .toString()
    .split(",")[0]
    .trim();

export const hashIp = (ip) => {
  if (!ip) return null;
  const salt = process.env.IP_HASH_SALT || "nova";
  return crypto.createHash("sha256").update(`${salt}:${ip}`).digest("hex");
};

export const sanitizeMessage = (text) => {
  if (!text) return "";
  let clean = text;
  clean = clean.replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[email]");
  clean = clean.replace(/(\+?\d[\d\s().-]{6,}\d)/g, "[telefono]");
  clean = clean.replace(/\b\d{7,}\b/g, "[numero]");
  return clean.slice(0, 2000);
};

export const rateLimit = (req, res) => {
  const ip = getClientIp(req);
  const now = Date.now();
  const windowMs = Number(process.env.RATE_LIMIT_WINDOW_MS || 600000);
  const maxReq = Number(process.env.RATE_LIMIT_MAX || 20);

  globalThis.__rateStore = globalThis.__rateStore || new Map();
  const rateStore = globalThis.__rateStore;

  if (!rateStore.has(ip)) {
    rateStore.set(ip, { count: 0, reset: now + windowMs });
  }

  const rate = rateStore.get(ip);
  if (now > rate.reset) {
    rate.count = 0;
    rate.reset = now + windowMs;
  }

  rate.count += 1;
  if (rate.count > maxReq) {
    res.status(429).json({ error: "Demasiadas solicitudes. Espera un minuto y prueba otra vez." });
    return false;
  }
  return true;
};

export const requireAdminAuth = (req, res) => {
  const allowlist = (process.env.ADMIN_ALLOWLIST || "")
    .split(",")
    .map(v => v.trim())
    .filter(Boolean);
  if (allowlist.length) {
    const ip = getClientIp(req);
    if (!allowlist.includes(ip)) {
      res.status(403).json({ error: "IP no permitida." });
      return false;
    }
  }

  const user = process.env.ADMIN_BASIC_USER || "";
  const pass = process.env.ADMIN_BASIC_PASS || "";
  if (!user || !pass) {
    res.status(500).json({ error: "Admin auth no configurada." });
    return false;
  }

  const auth = req.headers.authorization || "";
  const [scheme, encoded] = auth.split(" ");
  if (scheme !== "Basic" || !encoded) {
    res.setHeader("WWW-Authenticate", 'Basic realm="NovaEstudioWeb Admin"');
    res.status(401).json({ error: "Auth requerida." });
    return false;
  }

  const decoded = Buffer.from(encoded, "base64").toString("utf8");
  const [u, p] = decoded.split(":");
  if (u !== user || p !== pass) {
    res.setHeader("WWW-Authenticate", 'Basic realm="NovaEstudioWeb Admin"');
    res.status(401).json({ error: "Credenciales invalidas." });
    return false;
  }
  return true;
};

export const sendEmail = async ({ subject, text }) => {
  const provider = (process.env.EMAIL_PROVIDER || "smtp").toLowerCase();
  const to = process.env.ADMIN_EMAIL || "";
  const from = process.env.EMAIL_FROM || process.env.SMTP_USER || to;
  if (!to) throw new Error("ADMIN_EMAIL missing");

  if (provider === "resend") {
    const apiKey = process.env.EMAIL_API_KEY || "";
    if (!apiKey) throw new Error("EMAIL_API_KEY missing");
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ from, to, subject, text })
    });
    if (!res.ok) throw new Error("Resend failed");
    return;
  }

  if (provider === "sendgrid") {
    const apiKey = process.env.EMAIL_API_KEY || "";
    if (!apiKey) throw new Error("EMAIL_API_KEY missing");
    const res = await fetch("https://api.sendgrid.com/v3/mail/send", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        personalizations: [{ to: [{ email: to }] }],
        from: { email: from },
        subject,
        content: [{ type: "text/plain", value: text }]
      })
    });
    if (!res.ok) throw new Error("SendGrid failed");
    return;
  }

  const host = process.env.SMTP_HOST || "";
  const port = Number(process.env.SMTP_PORT || 587);
  const user = process.env.SMTP_USER || "";
  const pass = process.env.SMTP_PASS || "";
  const secure = (process.env.SMTP_SECURE || "").toLowerCase() === "true" || port === 465;
  if (!host || !user || !pass) throw new Error("SMTP missing");

  const transporter = nodemailer.createTransport({
    host,
    port,
    secure,
    auth: { user, pass }
  });

  await transporter.sendMail({ from, to, subject, text });
};

export const sendWhatsApp = async ({ text }) => {
  const provider = (process.env.WHATSAPP_PROVIDER || "").toLowerCase();
  const to = process.env.ADMIN_WHATSAPP || "";
  if (!provider || !to) throw new Error("WhatsApp config missing");

  if (provider === "meta") {
    const token = process.env.WHATSAPP_TOKEN || "";
    const senderId = process.env.WHATSAPP_SENDER_ID || "";
    if (!token || !senderId) throw new Error("Meta WhatsApp missing");
    const res = await fetch(`https://graph.facebook.com/v19.0/${senderId}/messages`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        messaging_product: "whatsapp",
        to,
        type: "text",
        text: { body: text }
      })
    });
    if (!res.ok) throw new Error("Meta WhatsApp failed");
    return;
  }

  if (provider === "twilio") {
    const accountSid = process.env.TWILIO_ACCOUNT_SID || "";
    const authToken = process.env.TWILIO_AUTH_TOKEN || "";
    const from = process.env.WHATSAPP_SENDER_ID || "";
    if (!accountSid || !authToken || !from) throw new Error("Twilio WhatsApp missing");
    const auth = Buffer.from(`${accountSid}:${authToken}`).toString("base64");
    const body = new URLSearchParams({
      From: `whatsapp:${from}`,
      To: `whatsapp:${to}`,
      Body: text
    });
    const res = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`, {
      method: "POST",
      headers: {
        "Authorization": `Basic ${auth}`,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body
    });
    if (!res.ok) throw new Error("Twilio WhatsApp failed");
  }
};

export const buildOwnerSummary = ({ conversationId, status, leadScore, brief }) => {
  const type = brief?.site_type || "sin definir";
  const goal = brief?.goal || "sin definir";
  const sections = Array.isArray(brief?.sections) ? brief.sections.join(", ") : "sin definir";
  return [
    `Nuevo posible cliente`,
    `ID: ${conversationId}`,
    `Estado: ${status}`,
    `Lead score: ${leadScore}`,
    `Tipo web: ${type}`,
    `Objetivo: ${goal}`,
    `Secciones: ${sections}`
  ].join("\n");
};

export const notifyOwner = async ({ conversationId, status, leadScore, brief }) => {
  const summary = buildOwnerSummary({ conversationId, status, leadScore, brief });
  const panelUrl = process.env.ADMIN_PANEL_URL || "";
  const link = panelUrl ? `${panelUrl}?id=${conversationId}` : "";
  const text = link ? `${summary}\n\nPanel: ${link}` : summary;
  const channels = (process.env.NOTIFY_CHANNELS || "whatsapp,email").split(",").map(v => v.trim());

  const tasks = [];
  if (channels.includes("email")) {
    tasks.push(sendEmail({
      subject: "[NovaEstudioWeb] Nuevo posible cliente",
      text
    }));
  }
  if (channels.includes("whatsapp")) {
    tasks.push(sendWhatsApp({ text }));
  }
  await Promise.allSettled(tasks);
};
