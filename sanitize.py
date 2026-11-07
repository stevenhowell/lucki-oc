"""Strip personal names and emails from Surplus Land Act notice contacts (keep agency and phone) in every data file."""
import json, re
from pathlib import Path
B = Path(__file__).parent
PHONE = re.compile(r"\(?\d{3}\)?[-. ]?\d{3}[-. ]\d{4}")
def clean(contact):
    if not contact: return contact
    parts = [p.strip() for p in str(contact).split(",")]
    agency = next((p for p in parts if re.search(r"city of|county|district|authority|agency|department|state of|caltrans|university", p, re.I)), "")
    phone = (PHONE.search(str(contact)) or [None])[0] if PHONE.search(str(contact)) else ""
    return ", ".join(x for x in (agency, phone) if x) or "see the notice"
def scrub_candidates(path):
    d = json.load(open(path)); n = 0
    for c in d["candidates"]:
        if c.get("noa_contact"): c["noa_contact"] = clean(c["noa_contact"]); n += 1
    json.dump(d, open(path, "w"), separators=(",", ":")); print(path.name, "contacts cleaned", n)
def scrub_rows(path):
    rows = json.load(open(path)); n = 0
    for r in rows:
        k = "Notice Contact Information- Concatenated"
        if r.get(k): r[k] = clean(r[k]); n += 1
    json.dump(rows, open(path, "w"), indent=0); print(path.name, "contacts cleaned", n)
for p in (B/"site"/"candidates.json", B/"cache"/"candidates_v1_backup.json"): scrub_candidates(p)
for p in (B/"cache"/"oc_noa.json", B/"cache"/"noa_santa_ana.json"): scrub_rows(p)
left = [p.name for p in (B/"site"/"candidates.json", B/"cache"/"oc_noa.json", B/"cache"/"noa_santa_ana.json", B/"cache"/"candidates_v1_backup.json")
        if re.search(r"[\w.+-]+@[\w-]+\.(?:org|gov|com|net|us)", open(p).read())]
print("files still holding an email:", left)
