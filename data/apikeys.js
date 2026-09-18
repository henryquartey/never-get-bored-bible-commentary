/* Online translations.
 *
 * IMPORTANT: this file is published with the website, so EVERY VISITOR CAN READ IT.
 * No real key ever goes in it. The keys live on a small Cloudflare Worker — see
 * tools/bible-api-proxy/READ ME - how to set up the key proxy.txt
 *
 * API_PROXY   — the Worker's address.
 * API_ENABLED — the starting guess at which keys it holds. The app asks the Worker itself
 *               on every open (/enabled), so adding a key on Cloudflare is enough; this file
 *               does not have to change.
 *      apibible -> NIV, NLT, AMP and the public-domain Bibles      esv -> ESV      nlt -> unused
 */
window.API_PROXY  = 'https://bible-api.quarteyjnr.workers.dev';
window.API_ENABLED = { apibible:true, esv:true, nlt:false };

/* Testing on the Mac only. If API_PROXY is empty the app talks to the publishers directly with
   these. Fine on your own machine; NEVER fill these in before a publish. */
window.API_KEYS = { apibible:'', esv:'', nlt:'' };
