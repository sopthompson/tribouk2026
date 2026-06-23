#!/usr/bin/env python3
"""Generate web/data.js (the edit-me data file) from the abstract spreadsheet
plus the schedule structure. Run once to (re)populate; after that data.js can be
hand-edited and is the single source for both the web page and the PDF."""
import os, re, json
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))

def clean(s):
    if s is None: return ""
    return re.sub(r"\s+", " ", str(s).replace("\t", " ")).strip()
def clean_abs(s):
    """Keep the abstract text as submitted (no rewording/shortening), but tidy two
    things people sometimes include: a stray 'Abstract' heading at the very start,
    and a trailing references / bibliography list."""
    if s is None: return ""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    # drop a standalone "Abstract" / "Abstract:" heading line at the start
    # (only when it's its own line — leaves e.g. "Abstract pending approval…" intact)
    s = re.sub(r"^\s*abstract\s*:?\s*\n+", "", s, flags=re.IGNORECASE)
    # cut a trailing references / bibliography section (header on its own line)
    s = re.split(r"\n\s*(?:references|bibliography|reference list)\s*:?\s*\n",
                 s, maxsplit=1, flags=re.IGNORECASE)[0]
    s = re.sub(r"[ ]{2,}", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.strip()
    # blank obvious placeholders (e.g. "Abstract pending approval from funder")
    if re.search(r"pending approval", s, re.IGNORECASE) and len(s) < 120:
        return ""
    return s
def norm(s): return re.sub(r"[^a-z]", "", s.lower())

# canonical institution names (only the inconsistent ones need mapping)
UNI_CANON = {
    "the university of sheffield": "University of Sheffield",
    "university of huddersfield":  "University of Huddersfield",
}
def fix_uni(s):
    u = clean(s)
    return UNI_CANON.get(u.lower(), u)

# fix names submitted with inconsistent capitalisation
NAME_CANON = {"yuyang yuan": "Yuyang Yuan"}
def fix_name(n):
    return NAME_CANON.get(n.lower(), n)

# presentation titles standardised to sentence case (acronyms / proper nouns kept);
# key = exact submitted title. Titles already in sentence case are left untouched.
TITLE_CANON = {
 "Condition Monitoring of Lubricant Degradation in Journal Bearing System based on Wireless On-Rotor Sensing Method":
   "Condition monitoring of lubricant degradation in journal bearing system based on wireless on-rotor sensing method",
 "Laser Surface Texturing of Surgical Blades":
   "Laser surface texturing of surgical blades",
 "Investigation into the Tribological differences between plant and animal proteins using a novel test methodology":
   "Investigation into the tribological differences between plant and animal proteins using a novel test methodology",
 "Advanced Acoustic Testing to Lubricated Contacts":
   "Advanced acoustic testing to lubricated contacts",
 "Tribological Characterization of Oil Lubricated EV Bearing under an Electric Field":
   "Tribological characterization of oil lubricated EV bearing under an electric field",
 "Research on the Influence of Nonlinear Friction on Transmission Error and Torsional Stiffness in Harmonic Reducers":
   "The influence of nonlinear friction on transmission error and torsional stiffness in harmonic reducers",
 "Interfacial Mesh Asymmetry Governs Lubrication and Frictional Transition in Cartilage Biomimetic Hydrogels":
   "Interfacial mesh asymmetry governs lubrication and frictional transition in cartilage biomimetic hydrogels",
 "Understanding the Wear of Ceramic Abradable Liners in Jet Engine Turbine Seals":
   "Understanding the wear of ceramic abradable liners in jet engine turbine seals",
 "Optimising Radial Air Foil Bearing Performance: Balancing Clearance and Stiffness for Enhanced Lift-Off":
   "Optimising radial air foil bearing performance: balancing clearance and stiffness for enhanced lift-off",
 "Additive Friction Stir Deposition (AFSD) for Light Weight Alloys":
   "Additive friction stir deposition (AFSD) for light weight alloys",
 "Slurry erosion and erosion-corrosion response of Niobium as an alternative cladding material for neutron-producing targets at ISIS":
   "Slurry erosion and erosion-corrosion response of niobium as an alternative cladding material for neutron-producing targets at ISIS",
 "Investigation of Friction, Wear and Particle Emissions from Coated and Uncoated Commercial Vehicle Brake Rotors Using a Small-Scale Tribological Approach":
   "Investigation of friction, wear and particle emissions from coated and uncoated commercial vehicle brake rotors using a small-scale tribological approach",
 "Microstructure-controlled mixed lubrication by WPI-stabilised Water-in-Water emulsions":
   "Microstructure-controlled mixed lubrication by WPI-stabilised water-in-water emulsions",
 "The Effect of Lubricant Contamination On Fretting wear of Engine Piston Rings and Cylinder Liners in PHEVs":
   "The effect of lubricant contamination on fretting wear of engine piston rings and cylinder liners in PHEVs",
 "Fabrication of Photoluminescent Thin Films via Tribochemical Deposition of Upconversion Nanoparticles":
   "Fabrication of photoluminescent thin films via tribochemical deposition of upconversion nanoparticles",
 "Evaluating the Friction Recovery and Damage Behaviour of Sand Alternatives in the Wheel-Rail Contact":
   "Evaluating the friction recovery and damage behaviour of sand alternatives in the wheel-rail contact",
 "The Future Of Dry Gas Seal Materials":
   "The future of dry gas seal materials",
 "Probabilistic Distribution of Ball-Raceway Contact Force and Contact Pressure in the Blade Pitch Bearing of the IWT7.5 Reference Wind Turbine":
   "Probabilistic distribution of ball-raceway contact force and contact pressure in the blade pitch bearing of the IWT7.5 reference wind turbine",
 "Development of PFAS-Free Ionic Liquid Greases for Tribological Applications":
   "Development of PFAS-free ionic liquid greases for tribological applications",
 "How to replenish lubricant in an oscillating wind turbine blade bearing raceway?":
   "How to replenish lubricant in an oscillating wind turbine blade bearing raceway",
}
def fix_title(s):
    t = clean(s)
    return TITLE_CANON.get(t, t)

# ---- abstracts from the Google Form responses ----
wb = openpyxl.load_workbook(os.path.join(HERE, "TriboUK26 - Abstract Submission form (Responses).xlsx"), data_only=True)
ws = wb["Form responses 1"]
abstracts = []
for r in list(ws.iter_rows(values_only=True))[1:]:
    if clean(r[14]).lower() != "accepted": continue
    name = (clean(r[2]) + " " + clean(r[3])).strip()
    p = name.split()
    if len(p) >= 2 and p[-1].lower() == p[-2].lower(): p = p[:-1]
    name = " ".join(p)
    abstracts.append(dict(name=fix_name(name), uni=fix_uni(r[4]), title=fix_title(r[8]),
                          keywords=clean(r[9]), abstract=clean_abs(r[10]), pref=clean(r[12])))
# presenters withdrawn from the programme — removed from schedule and abstracts
WITHDRAWN = {norm("Michael Bartram")}
abstracts = [a for a in abstracts if norm(a["name"]) not in WITHDRAWN]
title_by_name = {norm(a["name"]): a["title"] for a in abstracts}
uni_by_name   = {norm(a["name"]): a["uni"]   for a in abstracts}
def ttl(n): return title_by_name.get(norm(n), "")
def uni(n): return uni_by_name.get(norm(n), "")

# ---- presentation sessions (running order) ----
SESSIONS = {
 "S1": [("10:15","Yun Zhao"),("10:35","Zhifeng Hu")],
 "S2": [("11:30","Sofia Mushtaq"),("11:50","Zhen Dong"),("12:10","Osian Thomas")],
 "S3": [("10:00","Song Yang"),("10:20","Oluwatamilore Adenipekun"),("10:40","Siyu Wang")],
 "S4": [("11:15","Ziyuan Ren"),("11:35","Seona Mauchline"),("11:55","Charlotte Currie"),("12:15","Paula Sebastian Asenjo")],
 "S5": [("14:30","Musab Rizwan Kazi"),("14:50","Uresha Madhuwanthi Herath Mudiyanselage"),("15:10","Faraz Shaikh")],
}
def session(code):
    return [dict(time=t, name=n, uni=uni(n), title=ttl(n)) for (t, n) in SESSIONS[code]]

# Session chairs — fill in the display name for each session and re-run; the
# chair appears under the session title on the schedule (blank = nothing shown).
CHAIRS = {  # from Schedule Plan v2 (full names)
 "S1": "Alvaro Barrueto",
 "S2": "Mustafa Faisal",
 "S3": "Charlotte Currie & Jaden Davies",
 "S4": "Spike Thompson",
 "S5": "Damien Dooley",
}

VENUE_MAPS = {
 "Mappin Hall": "https://maps.app.goo.gl/CkdEHVfv9mitN4pJ7",
 "AMRC":        "https://maps.app.goo.gl/WBT7CQsHMQJfFZ846",
 "Guyshi":      "https://maps.app.goo.gl/sjytt6beGNBByQDw6",
}
def row(kind, time, label, who=None, sponsor=None, code=None, bold=False, chair=None):
    r = dict(kind=kind, time=time, label=label)
    if who: r["who"] = who
    if sponsor: r["sponsor"] = sponsor
    if code: r["talks"] = session(code)
    if code and CHAIRS.get(code): r["chair"] = CHAIRS[code]
    if chair: r["chair"] = chair            # explicit chair (e.g. on a venue block)
    if bold: r["bold"] = True
    if kind == "venue" and label in VENUE_MAPS: r["map"] = VENUE_MAPS[label]
    return r

days = [
 {"label": "Day 1 — Wednesday 1 July", "rows": [
   row("venue", "", "Mappin Hall"),
   row("break", "09:00–09:30", "Registration"),
   row("item",  "09:30–09:45", "Welcome"),
   row("keynote","09:45–10:15","Keynote 1", who="Eladio Hurtado Molina"),
   row("session","10:15–11:15","Presentation Session 1", code="S1"),
   row("break", "11:15–11:30", "Coffee break", sponsor="Sponsored by Phoenix Tribology"),
   row("session","11:30–12:30","Presentation Session 2", code="S2"),
   row("break", "12:30–13:10", "Travel to AMRC"),
   row("venue", "", "AMRC", chair="Forbes Gusha"),
   row("break", "13:10–13:50", "Lunch"),
   row("item",  "13:50–14:00", "Introduction to AMRC"),
   row("keynote","14:00–14:30","Keynote 2", who="Leon Proud"),
   row("item",  "14:30–15:30", "Guided laboratory tours", bold=True),
   row("item",  "15:30–15:55", "Networking & closing remarks"),
   row("break", "15:55–16:40", "Travel to University"),
   row("venue", "", "Mappin Hall"),
   row("break", "16:40–17:50", "Drinks reception", sponsor="Sponsored by PCS Instruments"),
   row("venue", "", "Guyshi"),
   row("break", "19:00–23:00", "Conference dinner"),
 ]},
 {"label": "Day 2 — Thursday 2 July", "rows": [
   row("venue", "", "Mappin Hall"),
   row("break", "09:00–09:30", "Arrival & refreshments"),
   row("keynote","09:30–10:00","Keynote 3", who="Roger Lewis"),
   row("session","10:00–11:00","Presentation Session 3", code="S3"),
   row("break", "11:00–11:15", "Coffee break", sponsor="Sponsored by Phoenix Tribology"),
   row("session","11:15–12:35","Presentation Session 4", code="S4"),
   row("item",  "12:35–13:00", "Poster flash talks"),
   row("break", "13:00–14:00", "Lunch & poster session"),
   row("keynote","14:00–14:30","Keynote 4", who="Klaus-Dieter Meck"),
   row("session","14:30–15:30","Presentation Session 5", code="S5"),
   row("item",  "15:30–15:35", "Voting"),
   row("break", "15:35–16:00", "Coffee break", sponsor="Sponsored by Phoenix Tribology"),
   row("item",  "16:00–16:30", "Awards & close"),
 ]},
]

# ---- manual additions (presenters not yet in the accepted form responses) ----
# Each is {name, uni, title, abstract, keywords}; leave abstract="" if not supplied
# yet. Deduplicated by name, so these vanish automatically once they appear in the
# form. (Never store submitter emails / personal data here.)
EXTRA_ORAL = []
EXTRA_POSTERS = [
 dict(name="Jaden Davies", uni="University of Sheffield",
      title="Ultrasonic measurement of lubricant film thickness in ball-raceway contacts of rolling element bearings",
      abstract="", keywords="Lubrication, Rolling Element Bearings, Ultrasound"),
]

# ---- order abstracts: oral by running order, posters alphabetical ----
roster = [norm(n) for s in ("S1","S2","S3","S4","S5") for (_, n) in SESSIONS[s]]
def oidx(a):
    k = norm(a["name"]); return roster.index(k) if k in roster else 999
def absrec(a): return dict(name=a["name"], uni=a["uni"], title=a["title"],
                           abstract=a["abstract"], keywords=a["keywords"])
def add_extra(lst, extra):
    have = {norm(a["name"]) for a in lst}
    return lst + [e for e in extra if norm(e["name"]) not in have]
oral   = [absrec(a) for a in sorted([x for x in abstracts if "oral"   in x["pref"].lower()], key=lambda a:(oidx(a), a["name"]))]
oral   = add_extra(oral, EXTRA_ORAL)
poster = [absrec(a) for a in sorted([x for x in abstracts if "poster" in x["pref"].lower()], key=lambda a:a["name"])]
poster = sorted(add_extra(poster, EXTRA_POSTERS), key=lambda a:a["name"])

DATA = {
 "conf": {"name":"TriboUK 2026", "sub":"Postgraduate Tribology Conference",
          "host":"University of Sheffield", "date":"1–2 July 2026"},
 # Welcome address — add the organising committee's text here (one string per
 # paragraph) and it will reappear automatically on the site and in the PDF.
 "welcome": [],
 "keynotes": [
   {"label":"Keynote 1", "name":"Eladio Hurtado Molina",
    "affil":"Lead Engineer, Blade Bearings — Vestas",
    "photo":"img/keynote_eladio.jpg",
    "bio":"Eladio Hurtado Molina is a leading expert in wind turbine component reliability, currently serving as Lead Engineer for Blade Bearings at Vestas. After earning his PhD from the University of Sheffield in 2022, he successfully transitioned from small-scale wear research to validating components for the world's largest multi-MW wind turbines. Today, he continues to bridge the gap between industry and academia by managing a strategic collaboration between Vestas and the University of Sheffield."},
   {"label":"Keynote 2", "name":"Leon Proud",
    "affil":"Advanced Manufacturing Research Centre (AMRC)", "photo":"", "bio":""},
   {"label":"Keynote 3", "name":"Roger Lewis",
    "affil":"Professor of Mechanical Engineering, University of Sheffield",
    "photo":"img/keynote_lewis.jpg",
    "bio":"Professor Roger Lewis is a Royal Academy of Engineering Research Chair in the Department of Mechanical Engineering at the University of Sheffield, where he has been an academic since 2002. His research spans industrial wear problems, the development of novel ultrasonic techniques for machine element contact analysis, and the design of engineering components and machines. His work covers wheel/rail contact tribology, friction management, condition monitoring, and the tribology of human interactions including skin friction, hand/object contact, and pedestrian slips. He has been recognised by the Tribology Trust Bronze Medal (2001), a Royal Society Brian Mercer Award for Innovation (2003), the Institute of Physics Innovation in Tribology Prize (2008), and the Donald Julius Groen Prize in Tribology (2020)."},
   {"label":"Keynote 4", "name":"Klaus-Dieter Meck",
    "affil":"Innovation Director, Core Technology & Simulation — John Crane",
    "photo":"img/keynote_meck.jpg",
    "bio":"Klaus-D. Meck is the Innovation Director — Core Technology & Simulation at John Crane, a division of Smiths Group plc, a global manufacturer and service provider for mechanical seals and supporting equipment. Mr Meck has over 30 years of experience in sealing technology and rotating equipment, with roles in R&D and Application Engineering. He received his master's degree from the University of Stuttgart, Germany and is the author of several papers related to rotating equipment and critical components. He is named inventor on several patents related to mechanical seals, power transmission couplings, and condition monitoring. Mr Meck has recently been appointed as Visiting Professor to the School of Mechanical, Aerospace & Civil Engineering at the University of Sheffield."},
 ],
 "days": days,
 "abstracts": {"oral": oral, "poster": poster},
 # Organising committee — add members as {"name","role","bio"} (and an optional
 # "photo":"img/..."); the section appears automatically once populated.
 "committee": [],
 "voting": {
   "intro": "Scan the QR codes or tap the link below to choose your favourites. Voting closes during the final coffee break on Day 2.",
   "items": [
     {"label": "Best Oral Presentation", "img": "img/QR_oral_vote.png", "url": "https://app.sli.do/event/eBHkSJe7jNZ1QErF9TcL4G"},
     {"label": "Best Poster", "img": "img/QR_poster_vote.png", "url": "https://app.sli.do/event/rLLnTMWEwXeBK1ZPvdBh9s"},
   ],
 },
 "sponsors": [
   {"img":"img/PCS_Logo_with_strap_line.png", "name":"PCS Instruments", "url":"https://pcs-instruments.com"},
   {"img":"img/Rtec-High-Res-Rtec-Instruments-Logo-M-01A.png", "name":"Rtec Instruments", "url":"https://rtec-instruments.com"},
   {"img":"img/CN_Tech_-_MAIN_CN_Tech_Logo.png", "name":"CN Tech", "url":"https://www.cntech.co.uk"},
   {"img":"img/Surface_Ventures_logo.png", "name":"Surface Ventures", "url":"https://surfaceventures.org"},
   {"img":"img/Tribonet_logo.png", "name":"Tribonet", "url":"https://www.tribonet.org"},
   {"img":"img/Mechanical-Engineers-Logo-HR.png", "name":"Institution of Mechanical Engineers", "url":"https://www.imeche.org"},
   {"img":"img/IOP_logo.png", "name":"Institute of Physics", "url":"https://www.iop.org"},
   {"img":"img/RSC-brand-guidelines-2019_tcm18-246471.png", "name":"Royal Society of Chemistry", "url":"https://www.rsc.org"},
   {"img":"img/Jost_Foundation_only_for_brochure.png", "name":"The Jost Foundation", "url":"https://jostfoundation.org.uk"},
 ],
 "sponsorNote": "",
}

with open(os.path.join(HERE, "docs", "data.js"), "w") as f:
    f.write("// Auto-generated by generate_data.py — safe to hand-edit afterwards.\n")
    f.write("window.DATA = ")
    json.dump(DATA, f, ensure_ascii=False, indent=2)
    f.write(";\n")
print("wrote docs/data.js  (oral=%d poster=%d)" % (len(oral), len(poster)))
