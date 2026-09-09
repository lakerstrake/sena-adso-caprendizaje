/**
 * ================================================================================
 * Cloudflare Edge Worker - SENA ADSO
 * ================================================================================
 * Responsabilidades:
 * 1. Redireccion rastreada de la Hoja de Vida (/cv) con alerta en tiempo real.
 * 2. Cabeceras de seguridad sobre las rutas que no resuelve el capa de assets.
 *
 * La autenticacion se retiro: el directorio es publico y el login solo servia
 * para enmascarar en las cartas unos datos de contacto que la propia pagina ya
 * muestra. Con el se van las credenciales que viajaban en este archivo.
 * Las cabeceras del sitio estatico se declaran en output/_headers, porque
 * Cloudflare sirve los assets existentes sin invocar este Worker.
 * ================================================================================
 */

const CANDIDATE_CV_DESTINATION = "https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing";
const CANDIDATE_CERTS_DESTINATION = "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN?usp=sharing";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Redireccion rastreada de la Hoja de Vida: notifica al abrirse.
    if (url.pathname === "/cv" || url.pathname.startsWith("/cv/") ||
        url.pathname === "/api/track-cv" || url.pathname === "/track/cv") {
      return handleCvTracking(request, url, env, ctx);
    }

    if (url.pathname === "/certificados" || url.pathname.startsWith("/certificados/")) {
      return Response.redirect(CANDIDATE_CERTS_DESTINATION, 302);
    }

    const response = await env.ASSETS.fetch(request);
    const headers = new Headers(response.headers);
    applyEnterpriseSecurityHeaders(headers);
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers
    });
  }
};

async function handleCvTracking(request, url, env, ctx) {
  const empresa = url.searchParams.get("empresa") || url.searchParams.get("e") || "Empresa Reclutadora";
  const contacto = url.searchParams.get("c") || url.searchParams.get("contacto") || "Equipo de Selección";
  const solicitudId = url.searchParams.get("id") || "N/A";
  const source = url.searchParams.get("src") || "Correo Formal";

  const clientIp = request.headers.get("cf-connecting-ip") || request.headers.get("x-forwarded-for") || "IP Oculta";
  const clientCountry = request.headers.get("cf-ipcountry") || "Colombia";
  const clientCity = request.headers.get("cf-ipcity") || "Bogotá D.C.";
  const userAgent = request.headers.get("user-agent") || "Navegador Web";
  
  const nowBogota = new Intl.DateTimeFormat("es-CO", {
    timeZone: "America/Bogota",
    dateStyle: "full",
    timeStyle: "medium"
  }).format(new Date());

  const eventData = {
    id: `cv_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
    empresa,
    contacto,
    solicitudId,
    source,
    ip: clientIp,
    ubicacion: `${clientCity}, ${clientCountry}`,
    dispositivo: parseUserAgent(userAgent),
    fecha: nowBogota,
    timestamp: Date.now()
  };

  if (ctx && ctx.waitUntil) {
    ctx.waitUntil(sendRealtimeNotification(eventData, env));
  } else {
    await sendRealtimeNotification(eventData, env);
  }

  return Response.redirect(CANDIDATE_CV_DESTINATION, 302);
}

/**
 * Cabeceras de seguridad para las respuestas que genera este Worker.
 * Las del sitio estatico viven en output/_headers.
 */
function applyEnterpriseSecurityHeaders(headers) {
  headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("X-Frame-Options", "DENY");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
  headers.set("Cross-Origin-Opener-Policy", "same-origin");
  headers.set("Cross-Origin-Resource-Policy", "same-origin");
  headers.set(
    "Content-Security-Policy",
    "default-src 'self'; " +
    "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; " +
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; " +
    "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; " +
    "img-src 'self' data: https:; " +
    "connect-src 'self' https://api.github.com; " +
    "form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
  );
}

function parseUserAgent(ua) {
  if (!ua) return "Navegador Web";
  let os = "Escritorio";
  let browser = "Navegador";
  if (/windows/i.test(ua)) os = "Windows PC";
  else if (/macintosh|mac os x/i.test(ua)) os = "macOS";
  else if (/android/i.test(ua)) os = "Móvil Android";
  else if (/iphone|ipad/i.test(ua)) os = "iPhone / iPad";
  else if (/linux/i.test(ua)) os = "Linux";

  if (/edg/i.test(ua)) browser = "Microsoft Edge";
  else if (/chrome/i.test(ua)) browser = "Google Chrome";
  else if (/firefox/i.test(ua)) browser = "Mozilla Firefox";
  else if (/safari/i.test(ua)) browser = "Apple Safari";

  return `${browser} en ${os}`;
}

async function sendRealtimeNotification(event, env) {
  const telegramToken = env?.TELEGRAM_BOT_TOKEN;
  const telegramChatId = env?.TELEGRAM_CHAT_ID;
  const discordWebhook = env?.DISCORD_WEBHOOK_URL;

  const msgText = 
`🎯 *¡ALERTA DE RECLUTADOR EN VIVO!*
━━━━━━━━━━━━━━━━━━━━
🏢 *Empresa:* ${escapeMarkdownV1(event.empresa)}
👤 *Contacto:* ${escapeMarkdownV1(event.contacto)}
📍 *Ubicación:* ${escapeMarkdownV1(event.ubicacion)}
💻 *Dispositivo:* ${escapeMarkdownV1(event.dispositivo)}
🔗 *Canal:* ${escapeMarkdownV1(event.source)}
⏱️ *Fecha/Hora:* ${escapeMarkdownV1(event.fecha)}
━━━━━━━━━━━━━━━━━━━━
✨ _El reclutador acaba de abrir tu Hoja de Vida. ¡Prepárate para entrevista!_`;

  if (telegramToken && telegramChatId) {
    try {
      await fetch(`https://api.telegram.org/bot${telegramToken}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: telegramChatId,
          text: msgText,
          parse_mode: "Markdown"
        })
      });
    } catch (err) {
      console.error("Telegram alert error:", err);
    }
  }

  if (discordWebhook && discordWebhook.startsWith("https://discord.com/api/webhooks/")) {
    try {
      await fetch(discordWebhook, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          embeds: [{
            title: "🎯 ¡ALERTA: Un reclutador abrió tu Hoja de Vida!",
            color: 0x10B981,
            fields: [
              { name: "Empresa", value: event.empresa, inline: true },
              { name: "Contacto", value: event.contacto, inline: true },
              { name: "Ubicación", value: event.ubicacion, inline: true },
              { name: "Dispositivo", value: event.dispositivo, inline: true },
              { name: "Canal", value: event.source, inline: true },
              { name: "Hora", value: event.fecha, inline: false }
            ],
            footer: { text: "SENA ADSO · CV Telemetry Engine" }
          }]
        })
      });
    } catch (err) {
      console.error("Discord webhook error:", err);
    }
  }
}

function escapeMarkdownV1(text) {

  if (!text) return "";
  return String(text).replace(/[_*[\]()~`>#+\-=|{}.!]/g, "\\$&");
}
