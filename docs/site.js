/* Website version of the programme — shares data.js with the print build. */
(function () {
  const D = window.DATA;
  const E = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
  const esc = (s) => (s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const app = document.getElementById("app");

  /* hero */
  const hero = E("header", "hero");
  hero.innerHTML = `
    <img class="logo" src="img/Logo_TriboUK_full.png" alt="TriboUK 2026">
    <div class="sub">${esc(D.conf.sub)}</div>
    <div class="rule"></div>
    <div class="date">${esc(D.conf.date)}</div>
    <div class="host"><img src="img/UoSheffield-logo.png" alt="${esc(D.conf.host)}"></div>
    <a class="dl" href="TriboUK-2026-Programme.pdf" download>⬇&nbsp; Download PDF programme</a>`;
  app.appendChild(hero);

  /* sticky nav */
  const nav = E("nav", "topnav");
  let navHtml = `<a href="#schedule">Schedule</a><a href="#keynotes">Keynotes</a>`
    + `<a href="#presentations">Presentations</a><a href="#posters">Posters</a>`
    + `<a href="#voting">Voting</a><a href="#sponsors">Sponsors</a>`;
  if (D.committee && D.committee.length) navHtml += `<a href="#committee">Committee</a>`;
  nav.innerHTML = navHtml;
  app.appendChild(nav);

  const main = E("main");
  app.appendChild(main);

  /* welcome (only if text has been supplied) */
  if (D.welcome && D.welcome.length) {
    const wel = E("section", "welcome"); wel.id = "welcome";
    wel.appendChild(E("h2", "sec", "Welcome"));
    D.welcome.forEach(p => wel.appendChild(E("p", null, esc(p))));
    main.appendChild(wel);
  }

  /* schedule with day tabs */
  const sch = E("section"); sch.id = "schedule";
  sch.appendChild(E("h2", "sec", "Schedule"));
  const tabs = E("div", "tabs");
  const panels = [];
  D.days.forEach((day, i) => {
    const btn = E("button", "tab", esc(day.label.split("—")[0].trim()));
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", i === 0 ? "true" : "false");
    btn.onclick = () => panels.forEach((p, j) => {
      p.hidden = j !== i;
      tabs.children[j].setAttribute("aria-selected", j === i ? "true" : "false");
    });
    tabs.appendChild(btn);
  });
  sch.appendChild(tabs);
  D.days.forEach((day, i) => {
    const panel = E("div", "panel"); panel.hidden = i !== 0;
    day.rows.forEach(r => {
      if (r.kind === "venue") {
        const vl = E("div", "venue", esc(r.label));
        if (r.map) vl.innerHTML += ` <a class="vmap" href="${esc(r.map)}" target="_blank" rel="noopener" title="Open in Google Maps"><svg viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg></a>`;
        panel.appendChild(vl);
        return;
      }
      const row = E("div", "row");
      row.appendChild(E("div", "time", esc(r.time)));
      const c = E("div");
      if (r.kind === "session") {
        c.appendChild(E("div", "slabel", esc(r.label)));
        if (r.chair) c.appendChild(E("div", "schair", "Chair: " + esc(r.chair)));
        r.talks.forEach(tk => {
          const t = E("div", "talk");
          t.innerHTML = `<div class="who">${esc(tk.name)}${tk.uni ? ` <span class="uni">· ${esc(tk.uni)}</span>` : ""}</div>`
            + `<div class="tt">${esc(tk.title)}</div>`;
          c.appendChild(t);
        });
      } else {
        const ev = E("div", "ev" + (r.kind === "keynote" || r.bold ? " key" : ""));
        ev.innerHTML = (r.kind === "keynote" && r.who) ? `${esc(r.label)} — ${esc(r.who)}`
          : esc(r.label);
        if (r.sponsor) ev.innerHTML += `<span class="spon">${esc(r.sponsor)}</span>`;
        c.appendChild(ev);
      }
      row.appendChild(c);
      panel.appendChild(row);
    });
    panels.push(panel);
    sch.appendChild(panel);
  });
  main.appendChild(sch);

  /* keynotes */
  const ks = E("section"); ks.id = "keynotes";
  ks.appendChild(E("h2", "sec", "Keynote Speakers"));
  const initials = (n) => { const p = (n || "").trim().split(/\s+/); return ((p[0] || "")[0] || "") + ((p[p.length - 1] || "")[0] || ""); };
  D.keynotes.forEach(k => {
    const d = E("div", "keynote");
    const photo = k.photo
      ? `<img class="kphoto" src="${esc(k.photo)}" alt="${esc(k.name)}">`
      : `<div class="kphoto kphoto-ph">${esc(initials(k.name))}</div>`;
    d.innerHTML = photo + `<div class="kbody"><div class="klabel">${esc(k.label)}</div><h3>${esc(k.name)}</h3>`
      + (k.affil ? `<div class="aff">${esc(k.affil)}</div>` : "")
      + (k.bio ? `<p>${esc(k.bio)}</p>` : "") + `</div>`;
    ks.appendChild(d);
  });
  main.appendChild(ks);

  /* shared abstract card: a collapsible <details> — title + author always shown,
     abstract expands on click */
  const absParas = (txt) => (txt || "").split(/\n{2,}/).map(p => p.replace(/\n/g, " ").trim()).filter(Boolean);
  const absCard = (a) => {
    const d = E("details", "abs");
    const sum = document.createElement("summary");
    sum.innerHTML = `<span class="atitle">${esc(a.title)}</span>`
      + `<span class="ameta"><b>${esc(a.name)}</b>${a.uni ? ` · ${esc(a.uni)}` : ""}</span>`;
    d.appendChild(sum);
    const paras = absParas(a.abstract);
    const body = E("div", "abody");
    if (paras.length) paras.forEach(p => body.appendChild(E("p", "apar", esc(p))));
    else body.appendChild(E("p", "apar muted", "Abstract to follow."));
    d.appendChild(body);
    return d;
  };

  /* oral presentation abstracts */
  const pr = E("section"); pr.id = "presentations";
  pr.appendChild(E("h2", "sec", "Oral Presentations"));
  D.abstracts.oral.forEach(a => pr.appendChild(absCard(a)));
  main.appendChild(pr);

  /* posters (title + abstract) */
  const ps = E("section"); ps.id = "posters";
  ps.appendChild(E("h2", "sec", "Poster Presentations"));
  D.abstracts.poster.forEach(a => ps.appendChild(absCard(a)));
  main.appendChild(ps);

  /* voting */
  const vt = E("section"); vt.id = "voting";
  vt.appendChild(E("h2", "sec", "Voting"));
  if (D.voting.intro) vt.appendChild(E("p", null, esc(D.voting.intro)));
  const vgrid = E("div", "votes");
  D.voting.items.forEach(v => {
    const card = E("div", "vote");
    const qr = `<img src="${v.img}" alt="${esc(v.label)} voting QR code">`;
    card.innerHTML = (v.url ? `<a href="${esc(v.url)}" target="_blank" rel="noopener">${qr}</a>` : qr)
      + `<div class="vlabel">${esc(v.label)}</div>`
      + (v.url ? `<a class="vbtn" href="${esc(v.url)}" target="_blank" rel="noopener">Vote</a>` : "");
    vgrid.appendChild(card);
  });
  vt.appendChild(vgrid);
  main.appendChild(vt);

  /* sponsors */
  const sp = E("section"); sp.id = "sponsors";
  sp.appendChild(E("h2", "sec", "Sponsors & Partners"));
  const grid = E("div", "sponsors");
  D.sponsors.forEach(s => {
    const img = `<img src="${s.img}" alt="${esc(s.name)}">`;
    grid.appendChild(E("div", "card", s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${img}</a>` : img));
  });
  sp.appendChild(grid);
  if (D.sponsorNote) sp.appendChild(E("div", "spon-note", esc(D.sponsorNote)));
  main.appendChild(sp);

  /* organising committee (only if populated) */
  if (D.committee && D.committee.length) {
    const cm = E("section"); cm.id = "committee";
    cm.appendChild(E("h2", "sec", "Organising Committee"));
    cm.appendChild(E("p", null, "TriboUK 2026 is organised by the following team — feel free to approach any of us during the event."));
    D.committee.forEach(m => {
      const d = E("div", "keynote");
      const ph = m.photo
        ? `<img class="kphoto" src="${esc(m.photo)}" alt="${esc(m.name)}">`
        : `<div class="kphoto kphoto-ph">${esc(initials(m.name))}</div>`;
      d.innerHTML = ph + `<div class="kbody"><h3>${esc(m.name)}</h3>`
        + (m.role ? `<div class="aff">${esc(m.role)}</div>` : "")
        + (m.bio ? `<p>${esc(m.bio)}</p>` : "") + `</div>`;
      cm.appendChild(d);
    });
    main.appendChild(cm);
  }

  /* footer */
  const f = E("footer");
  f.innerHTML = `<strong>TriboUK 2026</strong> · ${esc(D.conf.host)} · <span class="date">${esc(D.conf.date)}</span>`
    + `<div class="dl-foot"><a href="TriboUK-2026-Programme.pdf" download>Download PDF programme</a></div>`;
  app.appendChild(f);
})();
