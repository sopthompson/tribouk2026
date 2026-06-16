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
    """Keep the abstract exactly as submitted: full text, paragraph breaks preserved."""
    if s is None: return ""
    s = str(s).replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    s = re.sub(r"[ ]{2,}", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()
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
title_by_name = {norm(a["name"]): a["title"] for a in abstracts}
uni_by_name   = {norm(a["name"]): a["uni"]   for a in abstracts}
def ttl(n): return title_by_name.get(norm(n), "")
def uni(n): return uni_by_name.get(norm(n), "")

# ---- presentation sessions (running order) ----
SESSIONS = {
 "S1": [("10:15","Yun Zhao"),("10:35","Zhifeng Hu"),("10:55","Michael Bartram")],
 "S2": [("11:30","Sofia Mushtaq"),("11:50","Zhen Dong"),("12:10","Osian Thomas")],
 "S3": [("10:00","Song Yang"),("10:20","Oluwatamilore Adenipekun"),("10:40","Siyu Wang")],
 "S4": [("11:15","Ziyuan Ren"),("11:35","Seona Mauchline"),("11:55","Charlotte Currie"),("12:15","Paula Sebastian Asenjo")],
 "S5": [("14:30","Musab Rizwan Kazi"),("14:50","Uresha Madhuwanthi Herath Mudiyanselage"),("15:10","Faraz Shaikh")],
}
def session(code):
    return [dict(time=t, name=n, uni=uni(n), title=ttl(n)) for (t, n) in SESSIONS[code]]

def row(kind, time, label, who=None, sponsor=None, code=None):
    r = dict(kind=kind, time=time, label=label)
    if who: r["who"] = who
    if sponsor: r["sponsor"] = sponsor
    if code: r["talks"] = session(code)
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
   row("venue", "", "AMRC"),
   row("break", "13:10–13:50", "Lunch"),
   row("item",  "13:50–14:00", "Introduction to AMRC"),
   row("keynote","14:00–14:30","Keynote 2", who="Leon Proud"),
   row("item",  "14:30–15:30", "Lab tours"),
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

# ---- order abstracts: oral by running order, posters alphabetical ----
roster = [norm(n) for s in ("S1","S2","S3","S4","S5") for (_, n) in SESSIONS[s]]
def oidx(a):
    k = norm(a["name"]); return roster.index(k) if k in roster else 999
def absrec(a): return dict(name=a["name"], uni=a["uni"], title=a["title"])
oral   = [absrec(a) for a in sorted([x for x in abstracts if "oral"   in x["pref"].lower()], key=lambda a:(oidx(a), a["name"]))]
poster = [absrec(a) for a in sorted([x for x in abstracts if "poster" in x["pref"].lower()], key=lambda a:a["name"])]

DATA = {
 "conf": {"name":"TriboUK 2026", "sub":"Postgraduate Tribology Conference",
          "host":"University of Sheffield", "date":"1–2 July 2026"},
 "welcome": [
   "[Placeholder — the welcome address from the TriboUK 2026 organising committee will be added here.]",
 ],
 "keynotes": [
   {"label":"Keynote 1", "name":"Eladio Hurtado Molina",
    "affil":"Lead Engineer, Blade Bearings — Vestas",
    "bio":"Eladio Hurtado Molina is a leading expert in wind turbine component reliability, currently serving as Lead Engineer for Blade Bearings at Vestas. After earning his PhD from the University of Sheffield in 2022, he successfully transitioned from small-scale wear research to validating components for the world's largest multi-MW wind turbines. Today, he continues to bridge the gap between industry and academia by managing a strategic collaboration between Vestas and the University of Sheffield."},
   {"label":"Keynote 2", "name":"Leon Proud",
    "affil":"Advanced Manufacturing Research Centre (AMRC)", "bio":""},
   {"label":"Keynote 3", "name":"Roger Lewis",
    "affil":"Professor of Mechanical Engineering, University of Sheffield",
    "bio":"Professor Roger Lewis is a Royal Academy of Engineering Research Chair in the Department of Mechanical Engineering at the University of Sheffield, where he has been an academic since 2002. His research spans industrial wear problems, the development of novel ultrasonic techniques for machine element contact analysis, and the design of engineering components and machines. His work covers wheel/rail contact tribology, friction management, condition monitoring, and the tribology of human interactions including skin friction, hand/object contact, and pedestrian slips. He has been recognised by the Tribology Trust Bronze Medal (2001), a Royal Society Brian Mercer Award for Innovation (2003), the Institute of Physics Innovation in Tribology Prize (2008), and the Donald Julius Groen Prize in Tribology (2020)."},
   {"label":"Keynote 4", "name":"Klaus-Dieter Meck",
    "affil":"Innovation Director, Core Technology & Simulation — John Crane",
    "bio":"Klaus-Dieter Meck is the Innovation Director for Core Technology & Simulation at John Crane. Mr Meck has over 32 years of experience in sealing technology and rotating equipment. He is also a named inventor on patents related to mechanical seals, power transmission couplings, and condition monitoring. Mr Meck has recently been appointed as a Visiting Professor to the School of Mechanical, Aerospace & Civil Engineering at the University of Sheffield."},
 ],
 "days": days,
 "abstracts": {"oral": oral, "poster": poster},
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
 "sponsorNote": "In partnership with the Royal Society of Chemistry journals: Materials Advances, Materials Horizons & Lubrication Frontiers.",
}

with open(os.path.join(HERE, "docs", "data.js"), "w") as f:
    f.write("// Auto-generated by generate_data.py — safe to hand-edit afterwards.\n")
    f.write("window.DATA = ")
    json.dump(DATA, f, ensure_ascii=False, indent=2)
    f.write(";\n")
print("wrote docs/data.js  (oral=%d poster=%d)" % (len(oral), len(poster)))
