/**
 * Cloudflare Pages Edge Function for /cv
 */
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);
  const destination = "https://drive.google.com/drive/folders/1BZ-qBNdPeYsxW84zIq_ls97UkPlQcHyN";

  // Respond with instant 302 redirect
  return Response.redirect(destination, 302);
}
