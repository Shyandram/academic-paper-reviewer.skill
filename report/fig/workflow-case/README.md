# Figure 1 case files

Figure 1 of the technical report (`../workflow.pdf`, source `../workflow.drawio`) was made with
the `paper-figure` skill (https://github.com/Shyandram/Scribble), Draw.io backend, `paper-clean`
theme, sized for a 162 mm text width.

- `task_packet.json`, `plan.json`, `design.md`, `spec.r01.json`: the task, the typed graph, the
  design note and the layout spec.
- `figure.r01.*`: the delivered revision (native draw.io 32.4.1 export).
- `reviews/G0–G4.r01.json`, `render.manifest.json`, `lint.r01.pdf.json`: gate reviews, hashes and
  lint result. Revision r00 was sized for 170 mm and replaced; a later r02 was rejected and is
  not included.
- `scripts/`: the helper scripts that wrote the plan, spec and reviews. They contain paths from
  the machine they ran on.

`../../img/workflow.svg` on the site is `figure.r01.svg` with `color-scheme: light dark` changed
to `color-scheme: light`.
