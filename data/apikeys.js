/* Online translations — NIV, NKJV, NASB, AMP, MSG (API.Bible) · ESV (Crossway) · NLT (Tyndale)
 *
 * IMPORTANT: this file is published with the website, so EVERY VISITOR CAN READ IT.
 * Never put a real key in it. The keys live on a small Cloudflare Worker instead — see
 * tools/bible-api-proxy/READ ME - how to set up the key proxy.txt
 *
 * 1. API_PROXY  — the address of your Worker. Leave it empty and no online translation appears.
 * 2. API_ENABLED — which of the three the Worker actually holds a key for. A translation only
 *    shows in the version picker when its source is true here.
 *      apibible -> NIV, NKJV, NASB, AMP, MSG      esv -> ESV      nlt -> NLT
 */
window.API_PROXY  = '';
window.API_ENABLED = { apibible:false, esv:false, nlt:false };

/* Testing on the Mac only. If API_PROXY is empty the app will use these instead and talk to the
   Bible publishers directly. Fine on your own machine; NEVER fill these in before a publish. */
window.API_KEYS = { apibible:'', esv:'', nlt:'' };
