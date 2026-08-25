/**
 * Cloudflare Edge Worker - Enterprise Security & Asset Router
 * Standards: ISO/IEC 27001 (Information Security) & OWASP Top 10
 */

export default {
  async fetch(request, env) {
    // 1. Fetch static assets from Cloudflare Edge Cache
    const response = await env.ASSETS.fetch(request);

    // 2. Clone response to append security headers
    const newHeaders = new Headers(response.headers);

    // Strict Transport Security (HSTS)
    newHeaders.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");

    // MIME Type Sniffing Protection
    newHeaders.set("X-Content-Type-Options", "nosniff");

    // Clickjacking Defense
    newHeaders.set("X-Frame-Options", "DENY");

    // Referrer Policy
    newHeaders.set("Referrer-Policy", "strict-origin-when-cross-origin");

    // Permissions Policy
    newHeaders.set("Permissions-Policy", "geolocation=(), microphone=(), camera=(), payment=()");

    // Content Security Policy (CSP)
    newHeaders.set(
      "Content-Security-Policy",
      "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; " +
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; " +
      "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; " +
      "img-src 'self' data: https:; " +
      "connect-src 'self'; " +
      "frame-ancestors 'none';"
    );

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders
    });
  }
};
