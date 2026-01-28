import { applyCors, getSupabase, notifyOwner, requireAdminAuth } from "../_shared.js";

export default async function handler(req, res) {
  if (!applyCors(req, res)) return;
  if (req.method !== "POST") {
    res.status(405).json({ error: "Método no permitido." });
    return;
  }

  // Opcional: protege este endpoint con auth admin para uso manual
  const requireAuth = (process.env.NOTIFY_REQUIRE_ADMIN || "false").toLowerCase() === "true";
  if (requireAuth && !requireAdminAuth(req, res)) return;

  const supabase = getSupabase();
  if (!supabase) {
    res.status(500).json({ error: "Servidor no configurado." });
    return;
  }

  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = {}; }
  }

  const conversationId = (body?.conversation_id || "").toString().trim();
  if (!conversationId) {
    res.status(400).json({ error: "conversation_id requerido." });
    return;
  }

  const { data: convo, error } = await supabase
    .from("conversations")
    .select("*")
    .eq("id", conversationId)
    .maybeSingle();

  if (error || !convo) {
    res.status(404).json({ error: "Conversación no encontrada." });
    return;
  }

  await notifyOwner({
    conversationId,
    status: convo.status,
    leadScore: convo.lead_score || 0,
    brief: convo.extracted_brief || {}
  });

  res.status(200).json({ ok: true });
}
