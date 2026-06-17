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
  nav.innerHTML = `<a href="#schedule">Schedule</a><a href="#keynotes">Keynotes</a>`
    + `<a href="#posters">Posters</a><a href="#voting">Voting</a><a href="#sponsors">Sponsors</a>`;
  app.appendChild(nav);

  const main = E("main");
  app.appendChild(main);

  /* welcome */
  const wel = E("section", "welcome"); wel.id = "welcome";
  wel.appendChild(E("h2", "sec", "Welcome"));
  D.welcome.forEach(p => wel.appendChild(E("p", null, esc(p))));
  main.appendChild(wel);

  /* schedule with day tabs */
  const sch = E("section"); sch.id = "schedule";
  sch.appendChild(E("h2", "sec", "Programme"));
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
        if (r.map) vl.innerHTML += ` <a class="vmap" href="${esc(r.map)}" target="_blank" rel="noopener">map</a>`;
        panel.appendChild(vl);
        return;
      }
      const row = E("div", "row");
      row.appendChild(E("div", "time", esc(r.time)));
      const c = E("div");
      if (r.kind === "session") {
        c.appendChild(E("div", "slabel", esc(r.label)));
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
  D.keynotes.forEach(k => {
    const d = E("div", "keynote");
    d.innerHTML = `<div class="klabel">${esc(k.label)}</div><h3>${esc(k.name)}</h3>`
      + (k.affil ? `<div class="aff">${esc(k.affil)}</div>` : "")
      + (k.bio ? `<p>${esc(k.bio)}</p>` : "");
    ks.appendChild(d);
  });
  main.appendChild(ks);

  /* posters */
  const ps = E("section"); ps.id = "posters";
  ps.appendChild(E("h2", "sec", "Poster Presentations"));
  D.abstracts.poster.forEach(a => {
    const d = E("div", "poster");
    d.innerHTML = `<div class="who">${esc(a.name)}${a.uni ? ` <span class="uni">· ${esc(a.uni)}</span>` : ""}</div>`
      + `<div class="tt">${esc(a.title)}</div>`;
    ps.appendChild(d);
  });
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

  /* footer */
  const f = E("footer");
  f.innerHTML = `<strong>TriboUK 2026</strong> · ${esc(D.conf.host)} · <span class="date">${esc(D.conf.date)}</span>`
    + `<div class="dl-foot"><a href="TriboUK-2026-Programme.pdf" download>Download PDF programme</a></div>`;
  app.appendChild(f);
})();
