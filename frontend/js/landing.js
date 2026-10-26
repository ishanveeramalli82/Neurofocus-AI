// If already signed in, swap the landing-page buttons for a dashboard link.
try {
  const r = await fetch("/api/auth/status", { credentials: "same-origin" });
  if ((await r.json()).signed_in) document.getElementById("navActions").innerHTML = '<a class="btn primary" href="/dashboard">Open dashboard</a>';
} catch { /* offline: keep defaults */ }
