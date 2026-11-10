import json, hashlib, sys, subprocess, datetime
from pathlib import Path
D = Path("/home/user/figcase/out"); W, H = 1400, 730
rev = sys.argv[1] if len(sys.argv) > 1 else "r00"
plan = json.loads((D / "plan.json").read_text())
psha = hashlib.sha256((D / "plan.json").read_bytes()).hexdigest()
R = {"paper": (20, 282, 150, 64), "scan": (230, 120, 180, 64), "packet": (230, 282, 180, 64), "field": (230, 444, 180, 64),
     "r1": (490, 100, 210, 60), "r2": (490, 192, 210, 60), "r3": (490, 284, 210, 60), "r4": (490, 376, 210, 60), "da": (490, 468, 210, 60),
     "lit": (780, 200, 190, 64), "chk": (780, 360, 190, 64), "eic": (1020, 280, 200, 72), "agg": (1020, 444, 200, 64),
     "dec": (1250, 186, 130, 76), "venue": (1250, 444, 130, 64), "gap": (190, 566, 170, 60), "gapout": (400, 566, 180, 60)}
R.update(json.loads(Path("/home/user/figcase/rects.json").read_text()) if Path("/home/user/figcase/rects.json").exists() else {})
G = {"g_rev": (470, 40, 250, 520), "band": (170, 528, 430, 118)}
G.update(json.loads(Path("/home/user/figcase/grects.json").read_text()) if Path("/home/user/figcase/grects.json").exists() else {})
def rect(t): x, y, w, h = t; return {"x": x / W, "y": y / H, "w": w / W, "h": h / H}
els = []
for nd in plan["graph"]["nodes"]:
    el = {"id": "el_" + nd["id"], "plan_ids": [nd["id"]], "label": nd["label"], "role": nd["role"], "visual_kind": "native_shape",
          "scope": "both", "evidence_ids": nd["evidence_ids"], "rect": rect(R[nd["id"]]), "shape": "block",
          "emphasis": "hero" if nd["id"] == "eic" else ("muted" if nd["role"] == "optional" else "normal")}
    els.append(el)
els.append({"id": "el_g_rev", "plan_ids": ["g_rev"], "label": "Five reviewers", "role": "container", "visual_kind": "native_shape",
            "scope": "both", "evidence_ids": ["src_skill"], "rect": rect(G["g_rev"]), "shape": "container"})
els.append({"id": "el_band", "plan_ids": [], "label": "Optional", "role": "container", "visual_kind": "decoration",
            "scope": "both", "evidence_ids": [], "rect": rect(G["band"]), "shape": "container"})
P = {"e_pf": {"exit": "right", "entry": "left"}, "e_ps": {"exit": "right", "entry": "left"},
     "e_fp": {"exit": "top", "entry": "bottom"}, "e_sp": {"exit": "bottom", "entry": "top"},
     "e_lc": {"exit": "bottom", "entry": "top"}, "e_ce": {"exit": "right", "entry": "left"},
     "e_se": {"exit": "top", "entry": "top"}, "e_ed": {"exit": "right", "entry": "left"},
     "e_ea": {"exit": "bottom", "entry": "top"}, "e_av": {"exit": "right", "entry": "left"},
     "e_pg": {"exit": "bottom", "entry": "left"}, "e_gg": {"exit": "right", "entry": "left"}}
for r in ("r1", "r2", "r3", "r4", "da"):
    P["e_p" + r] = {"exit": "right", "entry": "left"}; P["e_" + r + "l"] = {"exit": "right", "entry": "left"}
P.update(json.loads(Path("/home/user/figcase/ports.json").read_text()) if Path("/home/user/figcase/ports.json").exists() else {})
first = ["e_se"]
order = first + [e["id"] for e in plan["graph"]["edges"] if e["id"] not in first]
byid = {e["id"]: e for e in plan["graph"]["edges"]}
rels = []
for i in order:
    e = byid[i]; r = {k: e[k] for k in ("id", "from", "to", "type", "scope", "evidence_ids")}
    r["ports"] = P[i]
    if "label" in e: r["label"] = e["label"]
    rels.append(r)
roles = {"input": {}, "prep": {"fill": "#E3F2FB", "stroke": "#56B4E9"}, "reviewer": {"fill": "#D9F2EA", "stroke": "#009E73"},
         "check": {"fill": "#FCEBD0", "stroke": "#E69F00"}, "editor": {"fill": "#FBE3D6", "stroke": "#D55E00"},
         "script": {"fill": "#FFFFFF", "stroke": "#333333"}, "output": {}, "optional": {"fill": "#F2F2F2", "stroke": "#7F7F7F"},
         "container": {}}
spec = {"schema": "FigureSpec@2", "figure_id": "apr_workflow", "plan_sha256": psha, "backends": ["drawio"], "theme": "paper-clean",
        "elements": els, "relations": rels, "style_roles": roles, "page": {"width": W, "height": H, "unit": "px"},
        "drawio": {"cell_map": {}, "edge_map": {}, "encoding": "uncompressed_utf8_xml", "output_uri": "figure.%s.drawio" % rev},
        "provenance": {"status": "ordinary", "excluded_from_clean_aggregate": False, "input_hashes": {}, "parent_artifact_hashes": {"plan.json": psha},
                       "source_coverage": [], "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}}
sp = D / ("spec.%s.json" % rev)
sp.write_text(json.dumps(spec, indent=1, ensure_ascii=False))
m = subprocess.run([sys.executable, "/home/user/scribble/paper-figure/scripts/compile_drawio.py", str(sp), "--plan", str(D / "plan.json"), "--emit-maps"], capture_output=True, text=True)
if m.returncode: print(m.stdout, m.stderr); sys.exit(1)
spec["drawio"].update(json.loads(m.stdout)) if m.stdout.strip().startswith("{") else print("MAPS:", m.stdout[:500])
sp.write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
print("spec", sp)
