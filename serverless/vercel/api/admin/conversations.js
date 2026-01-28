import { applyCors, getSupabase, requireAdminAuth } from "../_shared.js";

const buildMarkdown = (brief = {}, messages = []) => {
  const lines = [
    "# Brief NovaEstudioWeb",
    "",
    `- Tipo de web: ${brief.site_type || "sin definir"}`,
    `- Objetivo: ${brief.goal || "sin definir"}`,
    `- Secciones: ${Array.isArray(brief.sections) ? brief.sections.join(", ") : "sin definir"}`,
    `- Referencias: ${brief.references || "sin definir"}`,
    `- Contenidos: ${brief.contents || "sin definir"}`,
    `- Idiomas: ${brief.languages || "sin definir"}`,
    `- Integraciones: ${brief.integrations || "sin definir"}`,
    `- Plazo: ${brief.timeline || "sin definir"}`,
    `- Presupuesto: ${brief.budget || "sin definir"}`,
    "",
    "## Conversación (resumen)",
    ...messages.slice(-10).map(m => `- ${m.role}: ${m.content}`)
  ];
  return lines.join("\n");
};

export default async function handler(req, res) {
  if (!applyCors(req, res)) return;
  if (!requireAdminAuth(req, res)) return;

  const supabase = getSupabase();
  if (!supabase) {
    res.status(500).json({ error: "Servidor no configurado." });
    return;
  }

  const id = (req.query?.id || "").toString().trim();

  if (req.method === "GET") {
    if (id) {
      const { data: convo, error: convoErr } = await supabase
        .from("conversations")
        .select("*")
        .eq("id", id)
        .maybeSingle();
      if (convoErr || !convo) {
        res.status(404).json({ error: "Conversación no encontrada." });
        return;
      }
      const { data: msgs } = await supabase
        .from("messages")
        .select("role, content, created_at")
        .eq("conversation_id", id)
        .order("created_at", { ascending: true });
      res.status(200).json({ conversation: convo, messages: msgs || [] });
      return;
    }

    const { data, error } = await supabase
      .from("conversations")
      .select("id, status, lead_score, last_message, last_message_at, updated_at, created_at")
      .order("updated_at", { ascending: false })
      .limit(200);
    if (error) {
      res.status(500).json({ error: "Error listando conversaciones." });
      return;
    }
    res.status(200).json({ conversations: data || [] });
    return;
  }

  if (req.method === "POST") {
    let body = req.body;
    if (typeof body === "string") {
      try { body = JSON.parse(body); } catch { body = {}; }
    }
    const action = (body?.action || "").toString().trim();
    const convoId = (body?.conversation_id || id || "").toString().trim();
    if (!convoId) {
      res.status(400).json({ error: "conversation_id requerido." });
      return;
    }

    if (action === "approve" || action === "reject") {
      const status = action === "approve" ? "APPROVED" : "REJECTED";
      await supabase.from("conversations").update({ status, updated_at: new Date().toISOString() }).eq("id", convoId);
      res.status(200).json({ ok: true, status });
      return;
    }

    if (action === "delete") {
      await supabase.from("messages").delete().eq("conversation_id", convoId);
      await supabase.from("conversations").delete().eq("id", convoId);
      res.status(200).json({ ok: true });
      return;
    }

    if (action === "export") {
      const { data: convo } = await supabase
        .from("conversations")
        .select("*")
        .eq("id", convoId)
        .maybeSingle();
      if (!convo) {
        res.status(404).json({ error: "Conversación no encontrada." });
        return;
      }
      if (convo.status !== "APPROVED") {
        res.status(403).json({ error: "Solo disponible si está APPROVED." });
        return;
      }
      const { data: msgs } = await supabase
        .from("messages")
        .select("role, content, created_at")
        .eq("conversation_id", convoId)
        .order("created_at", { ascending: true });
      const markdown = buildMarkdown(convo.extracted_brief || {}, msgs || []);
      res.status(200).json({
        ok: true,
        brief: convo.extracted_brief || {},
        markdown
      });
      return;
    }

    res.status(400).json({ error: "Acción no válida." });
    return;
  }

  res.status(405).json({ error: "Método no permitido." });
}
