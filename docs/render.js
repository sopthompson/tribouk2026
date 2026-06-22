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

  /* ---------- WELCOME (only if text has been supplied) ---------- */
  if (D.welcome && D.welcome.length) {
    const wel = E("section", "sheet page-break");
    wel.appendChild(E("h1", "title", "Welcome to " + esc(D.conf.name)));
    D.welcome.forEach((p, i) =>
      wel.appendChild(E("p", i === 0 ? "lead" : "copy", esc(p))));
    chrome(wel, "Welcome");
    add(wel);
  }

  /* ---------- SCHEDULE ---------- */
  D.days.forEach(day => {
    const s = E("section", "sheet day");
    s.appendChild(E("div", "dayhead", esc(day.label.toUpperCase())));
    day.rows.forEach(r => {
      if (r.kind === "venue") {
        const vl = E("div", "venue-label", esc(r.label));
        if (r.map) vl.innerHTML += ` <a class="vmap" href="${esc(r.map)}" title="Open in Google Maps"><svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg></a>`;
        s.appendChild(vl);
        return;
      }
      const row = E("div", "row " + (r.kind === "keynote" ? "key" : r.kind === "break" ? "brk" : r.kind === "session" ? "sess" : "item"));
      const t = E("div", "t", esc(r.time));
      const c = E("div", "c");
      if (r.kind === "session") {
        c.appendChild(E("div", "slabel", esc(r.label)));
        if (r.chair) c.appendChild(E("div", "schair", "Chair: " + esc(r.chair)));
        r.talks.forEach(tk => {
          const tdiv = E("div", "talk");
          tdiv.innerHTML = `<div class="th">${esc(tk.name)}${tk.uni ? ` <span class="uni">· ${esc(tk.uni)}</span>` : ""}</div>
            <div class="tt">${esc(tk.title)}</div>`;
          c.appendChild(tdiv);
        });
      } else {
        const lead = E("div", "lead-row");
        lead.innerHTML = (r.kind === "keynote" && r.who)
          ? `${esc(r.label)} — <b>${esc(r.who)}</b>`
          : (r.bold ? `<b>${esc(r.label)}</b>` : esc(r.label));
        if (r.sponsor) lead.innerHTML += `<span class="spon">${esc(r.sponsor)}</span>`;
        c.appendChild(lead);
      }
      row.appendChild(t); row.appendChild(c);
      s.appendChild(row);
    });
    chrome(s, "Schedule");
    add(s);
  });

  // shared abstract block: title, author · institution, then paragraphs
  const absParas = (txt) => (txt || "").split(/\n{2,}/).map(p => p.replace(/\n/g, " ").trim()).filter(Boolean);
  const absBlock = (a) => {
    const d = E("div", "abs-item");
    d.innerHTML = `<h3>${esc(a.title)}</h3>`
      + `<div class="ameta"><b>${esc(a.name)}</b>${a.uni ? ` · ${esc(a.uni)}` : ""}</div>`;
    absParas(a.abstract).forEach(p => d.appendChild(E("p", "apar", esc(p))));
    return d;
  };

  /* ---------- KEYNOTE SPEAKERS ---------- */
  const ks = E("section", "sheet page-break");
  ks.appendChild(E("h1", "title", "Keynote Speakers"));
  const initials = (n) => { const p = (n || "").trim().split(/\s+/); return ((p[0] || "")[0] || "") + ((p[p.length - 1] || "")[0] || ""); };
  D.keynotes.forEach(k => {
    const d = E("div", "keynote");
    const photo = k.photo
      ? `<img class="kphoto" src="${esc(k.photo)}" alt="${esc(k.name)}">`
      : `<div class="kphoto kphoto-ph">${esc(initials(k.name))}</div>`;
    d.innerHTML = photo + `<div class="kbody">
      <div class="klabel">${esc(k.label)}</div>
      <h3>${esc(k.name)}</h3>
      ${k.affil ? `<div class="kaffil">${esc(k.affil)}</div>` : ""}
      ${k.bio ? `<p class="kbio">${esc(k.bio)}</p>` : ""}</div>`;
    ks.appendChild(d);
  });
  chrome(ks, "Keynote Speakers");
  add(ks);

  /* ---------- ORAL PRESENTATION ABSTRACTS ---------- */
  const op = E("section", "sheet page-break");
  op.appendChild(E("h1", "title", "Oral Presentations"));
  op.appendChild(E("p", "copy", "Abstracts for the oral presentations, listed in running order."));
  D.abstracts.oral.forEach(a => op.appendChild(absBlock(a)));
  chrome(op, "Oral Presentations");
  add(op);

  /* ---------- POSTER PRESENTATION ABSTRACTS ---------- */
  const ps = E("section", "sheet page-break");
  ps.appendChild(E("h1", "title", "Poster Presentations"));
  ps.appendChild(E("p", "copy", "Abstracts for the poster presentations."));
  D.abstracts.poster.forEach(a => ps.appendChild(absBlock(a)));
  chrome(ps, "Poster Presentations");
  add(ps);

  /* ---------- VOTING ---------- */
  const vt = E("section", "sheet page-break");
  vt.appendChild(E("h1", "title", "Voting"));
  if (D.voting.intro) vt.appendChild(E("p", "copy", esc(D.voting.intro)));
  const vgrid = E("div", "votes");
  D.voting.items.forEach(v => {
    const card = E("div", "vote");
    const qr = `<img src="${v.img}" alt="">`;
    card.innerHTML = (v.url ? `<a href="${esc(v.url)}">${qr}</a>` : qr)
      + `<div class="vlabel">${esc(v.label)}</div>`
      + (v.url ? `<a class="vbtn" href="${esc(v.url)}">Vote</a>` : "");
    vgrid.appendChild(card);
  });
  vt.appendChild(vgrid);
  chrome(vt, "Voting");
  add(vt);

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
        "TriboUK 2026 is made possible through the generous support of our sponsors and partners."));
    }
    group.forEach(s => sp.appendChild(band(s)));
    if (gi === groups.length - 1 && D.sponsorNote) sp.appendChild(E("div", "sponsor-note", esc(D.sponsorNote)));
    chrome(sp, "Sponsors & Partners");
    add(sp);
  });

  /* ---------- ORGANISING COMMITTEE (only if populated) ---------- */
  if (D.committee && D.committee.length) {
    const cm = E("section", "sheet page-break");
    cm.appendChild(E("h1", "title", "Organising Committee"));
    cm.appendChild(E("p", "copy",
      "TriboUK 2026 is organised by the following team — please feel free to approach any of us during the event."));
    D.committee.forEach(m => {
      const d = E("div", "committee");
      const ph = m.photo
        ? `<img class="cphoto" src="${esc(m.photo)}" alt="${esc(m.name)}">`
        : `<div class="cphoto cphoto-ph">${esc(initials(m.name))}</div>`;
      d.innerHTML = ph + `<div class="cbody"><h3>${esc(m.name)}</h3>`
        + (m.role ? `<div class="crole">${esc(m.role)}</div>` : "")
        + (m.bio ? `<p class="cbio">${esc(m.bio)}</p>` : "") + `</div>`;
      cm.appendChild(d);
    });
    chrome(cm, "Organising Committee");
    add(cm);
  }
})();
