/* Build the programme DOM from window.DATA. Edit data.js, not this file. */
(function () {
  const D = window.DATA;
  const E = (tag, cls, html) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (html != null) el.innerHTML = html;
    return el;
  };
  const esc = (s) => (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const app = document.getElementById("app");
  const add = (node) => app.appendChild(node);

  // screen-only preview chrome — shows the running band/footer in the browser;
  // hidden in print, where build.py stamps the real band + page numbers.
  const chrome = (section, title) => {
    const h = E("div", "screen-head");
    h.innerHTML = `<span class="sh-title">${esc(title)}</span>` +
                  `<img class="sh-logo" src="img/Logo_TriboUK_full_white.png" alt="">`;
    section.insertBefore(h, section.firstChild);
    section.appendChild(E("div", "screen-foot", "TriboUK 2026 · University of Sheffield"));
  };

  /* ---------- COVER ---------- */
  const cover = E("section", "sheet cover");
  cover.innerHTML = `
    <div class="topbar"></div><div class="topbar sky"></div>
    <img class="hero" src="img/Logo_TriboUK_full.png" alt="${esc(D.conf.name)}">
    <div class="sub">${esc(D.conf.sub)}</div>
    <div class="rule"></div>
    <div class="date">${esc(D.conf.date)}</div>
    <div class="hosted">
      <img src="img/UoSheffield-logo.png" alt="${esc(D.conf.host)}">
    </div>
    <div class="botbar lilac"></div><div class="botbar"></div>`;
  add(cover);

  /* ---------- WELCOME ---------- */
  const wel = E("section", "sheet page-break");
  wel.appendChild(E("h1", "title", "Welcome to " + esc(D.conf.name)));
  D.welcome.forEach((p, i) =>
    wel.appendChild(E("p", i === 0 ? "lead" : "copy", esc(p))));
  chrome(wel, "Welcome");
  add(wel);

  /* ---------- SCHEDULE ---------- */
  D.days.forEach(day => {
    const s = E("section", "sheet day");
    s.appendChild(E("div", "dayhead", esc(day.label.toUpperCase())));
    day.rows.forEach(r => {
      if (r.kind === "venue") {
        s.appendChild(E("div", "venue-label", esc(r.label)));
        return;
      }
      const row = E("div", "row " + (r.kind === "keynote" ? "key" : r.kind === "break" ? "brk" : r.kind === "session" ? "sess" : "item"));
      const t = E("div", "t", esc(r.time));
      const c = E("div", "c");
      if (r.kind === "session") {
        c.appendChild(E("div", "slabel", esc(r.label)));
        r.talks.forEach(tk => {
          const tdiv = E("div", "talk");
          tdiv.innerHTML = `<div class="th">${esc(tk.name)}${tk.uni ? ` <span class="uni">· ${esc(tk.uni)}</span>` : ""}</div>
            <div class="tt">${esc(tk.title)}</div>`;
          c.appendChild(tdiv);
        });
      } else {
        const lead = E("div", "lead-row");
        lead.innerHTML = (r.kind === "keynote" && r.who)
          ? `${esc(r.label)} — <b>${esc(r.who)}</b>` : esc(r.label);
        if (r.sponsor) lead.innerHTML += `<span class="spon">${esc(r.sponsor)}</span>`;
        c.appendChild(lead);
      }
      row.appendChild(t); row.appendChild(c);
      s.appendChild(row);
    });
    chrome(s, "Programme");
    add(s);
  });

  /* ---------- KEYNOTE SPEAKERS ---------- */
  const ks = E("section", "sheet page-break");
  ks.appendChild(E("h1", "title", "Keynote Speakers"));
  D.keynotes.forEach(k => {
    const d = E("div", "keynote");
    d.innerHTML = `<div class="klabel">${esc(k.label)}</div>
      <h3>${esc(k.name)}</h3>
      ${k.affil ? `<div class="kaffil">${esc(k.affil)}</div>` : ""}
      ${k.bio ? `<p class="kbio">${esc(k.bio)}</p>` : ""}`;
    ks.appendChild(d);
  });
  chrome(ks, "Keynote Speakers");
  add(ks);

  /* ---------- POSTER PRESENTATIONS (list) ---------- */
  const ps = E("section", "sheet page-break");
  ps.appendChild(E("h1", "title", "Poster Presentations"));
  const ol = E("ul", "poster-list");
  D.abstracts.poster.forEach(a => {
    const li = document.createElement("li");
    li.innerHTML = `<div class="pwho"><b>${esc(a.name)}</b>${a.uni ? ` <span class="uni">· ${esc(a.uni)}</span>` : ""}</div>
      <div class="ptitle">${esc(a.title)}</div>`;
    ol.appendChild(li);
  });
  ps.appendChild(ol);
  chrome(ps, "Poster Presentations");
  add(ps);

  /* ---------- SPONSORS (3 bands per page) ---------- */
  const band = (s) => {
    const b = E("div", "sponsor-band");
    const img = `<img src="${s.img}" alt="${esc(s.name)}">`;
    b.innerHTML = s.url ? `<a href="${esc(s.url)}">${img}</a>` : img;
    return b;
  };
  const groups = [];
  for (let i = 0; i < D.sponsors.length; i += 3) groups.push(D.sponsors.slice(i, i + 3));
  groups.forEach((group, gi) => {
    const sp = E("section", "sheet page-break");
    if (gi === 0) {
      sp.appendChild(E("h1", "title", "Our Sponsors &amp; Partners"));
      sp.appendChild(E("p", "copy",
        "TriboUK 2026 is made possible through the generous support of our sponsors and partners. "
        + "We are grateful for their commitment to the tribology community and to early-career researchers."));
    }
    group.forEach(s => sp.appendChild(band(s)));
    if (gi === groups.length - 1) sp.appendChild(E("div", "sponsor-note", esc(D.sponsorNote)));
    chrome(sp, "Sponsors & Partners");
    add(sp);
  });
})();
