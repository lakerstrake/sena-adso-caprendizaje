/**
 * Cloudflare Pages Edge Function for /cv
 */
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const destination = "https://drive.google.com/file/d/1r89tS4JI4OKwSuzyyfPhGn4ylZTRlrln/view?usp=sharing";

  // Respond with instant 302 redirect
  return Response.redirect(destination, 302);
}
