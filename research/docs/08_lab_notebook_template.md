# 8. Lab notebook template

Keep a dated entry for every working session. Copy this block each time.
(ISEF projects are expected to have a research notebook; a handwritten or
dated digital notebook both work. Check your fair's preference.)

---

**Date:**
**Time spent:**
**Git commit (run `git rev-parse --short HEAD`):**

**Goal for today:**

**What I did:**

**Commands run / run IDs:**

**Observations (raw, before interpretation):**

**Problems and how I solved them:**

**Decisions made and why (especially any change to code, parameters,
simulator or analysis; note whether it happened before or after seeing
official results):**

**Next steps:**

---

## Required entries before the official run

- [ ] Hypotheses (H1, H2) written in my own words, dated
- [ ] Any numeric success targets written, dated
- [ ] `python -m pytest` result recorded
- [ ] All code committed; commit hash recorded
- [ ] Config file used: `research/config/experiment_v1.json`, SHA-256 recorded
      (from `manifest.json` after the run)

## Required entries after the official run

- [ ] Run ID
- [ ] Reproducibility check: second run with a new run ID gives identical metrics
- [ ] Primary result table copied from `statistics_report.md`
- [ ] Whether H1 / H2 were supported, in plain language
- [ ] Surprises, and what the confusion matrices say about the error sources
- [ ] Raw data backed up (where)
