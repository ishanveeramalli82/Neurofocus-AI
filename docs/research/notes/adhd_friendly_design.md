# Evidence-Based Design Principles for an ADHD-Friendly Study / Focus App (NeuroFocus AI)

Evidence labels used throughout:
- **[PR]** = peer-reviewed finding (meta-analysis, trial, or peer-reviewed review)
- **[GL]** = authoritative guideline (W3C WCAG/COGA, NICE, AAP, CHADD)
- **[EO]** = expert opinion, popular claim, preprint, press coverage

Method note: Research was done with web search. Direct page fetches to w3.org, link.springer.com and pmc.ncbi.nlm.nih.gov were blocked by this session's network policy, so several findings come from abstracts, search snippets and secondary summaries, not full text. Where that matters it is flagged. Exact WCAG success-criterion numbers below are from the published WCAG 2.2 Recommendation (stable, well-known identifiers), but the W3C page itself could not be re-opened in this session.

---

## 1. Executive-function challenges relevant to studying, and external supports with evidence

### Takeaway
Time-perception problems ("time blindness") and delay aversion have meta-analytic support in ADHD; if-then planning (implementation intentions) has small-sample experimental support in children with ADHD. Guidelines (NICE, AAP) endorse environmental/structural supports as part of care. This supports an app that externalizes time (visible timers), asks for concrete if-then plans, and breaks study into short chunks, but none of these has been tested as a feature of a webcam focus app.

### Cited Findings
- [PR] Time perception: Marx et al. (2021) meta-analysis of 55 studies found "a broad range of timing deficits in persons with ADHD"; time reproduction (26 studies, n = 2,364) showed a significant pooled effect; time estimation (8 studies, n = 1,024) showed a small-to-medium increase in absolute errors. Authors linked reproduction deficits to attentional and motivational factors. DOI 10.1016/j.jaac.2021.12.004 — [Southampton ePrints record](https://eprints.soton.ac.uk/456003); [ADHD Evidence blog summary](https://adhdevidence.org/blog/time-blindness-found-to-be-a-consistent-feature-of-adhd)
- [PR] A separate child/adolescent meta-analysis (Zheng et al., 27 studies after 2000) also reported timing problems but noted inconsistent earlier results — [Scientific Reports, s41598-022-05425-2](https://link.springer.com/10.1038/s41598-022-05425-2)
- [PR] Caveat: an adult-ADHD review (2023) found the time-perception literature "very scarce" and mixed (some studies find reproduction deficits, others do not) — [Time Perception in Adult ADHD: Findings from a Decade—A Review (PMC9962130)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9962130/)
- [PR] Delay aversion: Marx, Hacker, Yu, Cortese & Sonuga-Barke, meta-analysis in *Journal of Attention Disorders* (2021, vol. 25), 37 group comparisons, 3,763 participants: people with ADHD chose small immediate over larger delayed rewards more often than controls (small-to-medium effects); real rewards roughly doubled the odds ratio vs hypothetical rewards — [Southampton ePrints](https://eprints.soton.ac.uk/420008)
- [PR] Yu, Sonuga-Barke & Liu (2015): delay duration, not paradigm type, drove the ADHD difference (group differences appeared only in the long-delay condition) — [Southampton ePrints](https://eprints.soton.ac.uk/376602)
- [PR] Implementation intentions (if-then plans): Gawrilow & Gollwitzer (2008, *Cognitive Therapy and Research*): children with ADHD who formed if-then plans improved Go/No-Go inhibition to the level of non-ADHD children; plans + stimulant medication gave best performance — [Univ. Konstanz PDF](https://www.socmot.uni-konstanz.de/sites/default/files/08_Gawrilow_Gollwitzer_Implementation_intentions_facilit.pdf)
- [PR] Gawrilow, Gollwitzer & Oettingen (2011, *Journal of Social and Clinical Psychology*): if-then plans reduced perseverative errors on a shifting task and helped children with ADHD solve math problems requiring working memory and inhibition of distractions — [PDF](https://www.socmot.uni-konstanz.de/sites/default/files/Gawrilow_Gollwitzer_Oettingen_Executive_Function_JSCP_2011.pdf)
- [PR] Gawrilow, Gollwitzer & Oettingen (2011, *Cognitive Therapy and Research*): 45 inpatient children with ADHD improved delay of gratification after forming implementation intentions; replicated in an outpatient sample — [PDF](https://www.socmot.uni-konstanz.de/sites/default/files/Gawrilow_Gollwitzer_Oettingen_Delay_2011-2.pdf)
- [GL] NICE NG87 (2018, updated 2019): environmental modifications should be applied systematically to limit the impact of ADHD symptoms, and their effect reviewed before/alongside other treatment — [NICE NG87](https://www.nice.org.uk/guidance/ng87); [Rationale and impact](https://www.nice.org.uk/guidance/ng87/chapter/Rationale-and-impact)
- [GL] AAP 2019 clinical practice guideline: for adolescents 12–18, medication with assent plus evidence-based training/behavioral interventions; educational interventions and individualized supports (often via IEP/504) are "a necessary part of any treatment plan" — [AAP EQIPP Key Action Statements](https://eqipp.aap.org/courses/adhd/mn/clinical-guide/popups/key-action-statements); [AAP evidence-based behavioral interventions](https://eqipp.aap.org/courses/adhd/mn/my-improvement-project/popups/evidence)

### Inferences
- Externalize time: show an always-visible remaining-time display (e.g., a shrinking bar or ring) rather than only digits, and show clock time for the session end. Supported indirectly by timing-deficit meta-analyses; no trial tests visual timers in apps.
- Short, concrete, near-term goals fit delay aversion better than long sessions with a reward only at the end. Delay effects appear mainly at long delays, so keep feedback loops short (minutes, not hours).
- Add an optional "if-then plan" prompt at session start (e.g., "If I notice I picked up my phone, then I will put it face-down and reread the last line"). This is a cheap feature with experimental support in ADHD, though from small samples by one research group, in children, on lab tasks.
- Frame the app as an "environmental support / study aid", matching NICE/AAP language, never as treatment.

### Gaps
- No direct trials found of visual timers, task-chunking UIs, or digital reminders for students with ADHD. Chunking and visual timers are widely recommended but I found no meta-analytic evidence specific to them.
- Implementation-intention studies were not found in adolescents/college students with ADHD; independent replication not checked.
- CHADD guidance pages were not retrieved (could not search/fetch them within budget).

---

## 2. Feedback, rewards/gamification, streaks and progress visualization

### Takeaway
Immediate, frequent, consequence-based feedback has the strongest classroom evidence for ADHD, consistent with delay-aversion research. Game elements, however, have weak and inconsistent evidence, and I found no evidence on streaks at all. Popular "gamify everything" advice is largely expert opinion.

### Cited Findings
- [PR] Gaastra, Groen, Tucha & Tucha (2016), *PLoS ONE* meta-analysis of classroom interventions for children with ADHD symptoms: interventions reduced off-task/disruptive behavior (within-subjects designs MSMD = 0.92; single-subject designs MSMD = 3.08); consequence-based interventions had the largest within-subject effects (MSMD = 1.82) vs antecedent-based (MSMD = 0.31); self-regulation largest in single-subject designs (MSMD = 3.61). DOI 10.1371/journal.pone.0148841 — [PMC4757442](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4757442/)
- [PR] Daily Behavior Report Cards for children with ADHD (meta-analysis, *Journal of Attention Disorders*): large effect (Hedges' g = 1.05) when outcomes were measured by systematic direct observation, smaller on teacher ratings — [PubMed 29135352](https://pubmed.ncbi.nlm.nih.gov/29135352/) (author list not verified in this session)
- [PR] Delay aversion meta-analysis (see Section 1): ADHD shows a stronger preference for smaller immediate rewards; real rewards increase this — [Southampton ePrints](https://eprints.soton.ac.uk/420008)
- [PR] Systematic review of 22 ADHD games / 37 studies (Frontiers in Psychiatry, 2025): 55% target cognitive training; parent-rated symptom changes range from d = -0.55 to 1.26 "without an obvious pattern of advantage for any game element"; largest far-transfer effects come from studies at highest risk of bias — [Frontiers in Psychiatry 10.3389/fpsyt.2025.1605744](https://www.frontiersin.org/journals/psychiatry/articles/10.3389/fpsyt.2025.1605744/full)
- [PR] Scoping review of 19 mobile-game studies (2022): children improved within the games, but "evidence for the effectiveness of these modalities remains scarce and mixed"; long-term engagement of children with ADHD may be difficult — [Frontiers in Psychiatry 10.3389/fpsyt.2022.792402](https://frontiersin.org/articles/10.3389/fpsyt.2022.792402/full)
- [PR] Briesch & Briesch (2016) single-case meta-analysis of self-management (47 studies, 1971–2011): stronger effects in studies that assessed rating accuracy, asked students to reflect on behavior over time, and **did not** use evaluation or rewards; effects lower for students with ADHD/learning disabilities than other groups — [School Psychology Review 45(1), DOI 10.17105/SPR45-1.3-18](https://informahealthcare.com/doi/abs/10.17105/SPR45-1.3-18) (from search snippet; full text not read)

### Inferences
- Give feedback immediately and frequently during a session (e.g., a calm live indicator), plus a short end-of-session summary, rather than only weekly reports.
- Keep rewards informational ("You refocused 6 times; that is the skill") rather than points/badges by default; Briesch & Briesch suggest reflection over time can matter more than rewards.
- Streaks: no evidence found either way for ADHD. Design risk (inference, not evidence): a broken streak is a delayed, all-or-nothing loss signal, which may feel like failure. If used, make them forgiving (e.g., "4 of the last 7 days" rather than consecutive days).
- Progress visualization should emphasize improvement and effort over absolute scores; avoid red/fail colors for low Focus Scores.

### Gaps
- No peer-reviewed evidence found on streaks, badges, or leaderboards specifically for ADHD; no study found on anxiety/shame from gamified focus metrics in ADHD (the harm question is open).
- HCI venues (CHI/ASSETS) were only partly covered: Spiel et al. (2022) located (Section 5) but not read in full.

---

## 3. Self-monitoring interventions for students with ADHD (core mechanism of the app)

### Takeaway
Self-monitoring/self-regulation is one of the best-supported school interventions for ADHD, with large effects (often >1.0) on on-task behavior, but nearly all evidence is from small single-case studies of younger children with teacher/mentor support, and effects may be smaller for students with ADHD than other groups. Evidence for high-school, app-delivered self-monitoring is limited to tiny pilots. Importantly, classic self-monitoring has the *student* judge their own attention; the app's automated webcam judgment is a different mechanism that has not been tested.

### Cited Findings
- [PR] Reid, Trout & Schartz (2005), "Self-Regulation Interventions for Children With Attention Deficit/Hyperactivity Disorder," *Exceptional Children* 71(4):361–377 (foundational, pre-2010): meta-analysis of 16 studies (1974–2003) of self-monitoring, self-monitoring + reinforcement, self-management, and self-reinforcement; combined effect sizes > 1.0 for on-task behavior, inappropriate behavior, and academic accuracy and productivity — [ERIC EJ697216 record](https://searchworks.jioinstitute.edu.in/articles/eric__EJ697216); [ProQuest](https://www.proquest.com/docview/201228664)
- [PR] Gaastra et al. (2016): self-regulation interventions had the largest effect in single-subject designs (MSMD = 3.61) — [PMC4757442](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4757442/)
- [PR] Briesch & Briesch (2016), *School Psychology Review*: across 47 single-case studies, self-management effects were lower for students with ADHD and learning disabilities; larger where accuracy of self-ratings was checked and students reflected on behavior over time — [DOI 10.17105/SPR45-1.3-18](https://informahealthcare.com/doi/abs/10.17105/SPR45-1.3-18)
- [PR] Bruhn, McDaniel & Kreigh (2015), *Behavioral Disorders* 40(2):102–121: systematic review of 41 self-monitoring studies (2000–2012) in K-12 students with persistent behavior problems, focusing on reinforcement, feedback, function and technology; feedback was provided in 25 of 41 studies — [Univ. of Iowa record](https://iro.uiowa.edu/esploro/outputs/journalArticle/Self-Monitoring-Interventions-for-Students-with-Behavior/9984371113102771)
- [PR] Briesch & Chafouleas (2009), *School Psychology Quarterly* 24(2):106–118: review (not meta-analysis) of self-management (1988–2008) identifying 16 different characterizations varying in components and student involvement — [Ovid](https://www.ovid.com/journals/spsy/pdf/10.1037/a0016159~review-and-analysis-of-literature-on-self-management)
- [PR] Age gap: one review notes none of 51 participants across 16 self-monitoring/ADHD studies were high-school age — [search summary of review; see PMC4662407](https://pmc.ncbi.nlm.nih.gov/articles/PMC4662407) (exact source of this statement not verified; treat as unconfirmed)
- [PR] Technology-delivered self-monitoring, adolescents: I-Connect (Wills & Mason) high-school pilot, withdrawal design, n = 2, app plus weekly mentor review — [PMC4662407](https://pmc.ncbi.nlm.nih.gov/articles/PMC4662407); Cook & Sayeski (2022): 4 high schoolers with high-incidence disabilities, smartphone prompts; at least 2 of 4 showed moderate increases in on-task behavior — [Frontiers / related search result](https://ifp.nyu.edu/2023/journal-article-abstracts/s40817-023-00152-6/) (venue details not verified)
- [PR] App-based self-monitoring with students with learning difficulties (Melzer & Herwix, 2024, single-case designs, three apps incl. I-Connect): interventions "were successful"; interval prompts asked students whether they were on task — [Frontiers in Education 10.3389/feduc.2024.1270484](https://www.frontiersin.org/articles/10.3389/feduc.2024.1270484/pdf)
- [PR] iSelfControl iPad app feasibility/pilot studies for children with ADHD — [PMC5065230](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5065230/) (details not read)
- [GL] Self-monitoring/self-regulation sits within the "behavioral/classroom supports" that AAP 2019 calls a necessary part of a treatment plan — [AAP EQIPP](https://eqipp.aap.org/courses/adhd/mn/clinical-guide/popups/key-action-statements)

### Inferences
- The strongest design move: keep the student as the self-monitor. E.g., periodic gentle check-ins ("Were you on task just now? yes / mostly / no") and then show the student's self-rating next to the webcam estimate. This mirrors "accuracy matching", which Briesch & Briesch associate with larger effects, and keeps the webcam as a mirror, not a judge.
- Add an end-of-session reflection ("What pulled you away? What helped?") and multi-session trend views ("reflect over time").
- Expect smaller effects for students with ADHD than older single-case studies suggest; for an ISEF claim, measure your own outcomes and do not cite >1.0 effect sizes as the app's expected effect.
- Most successful tech self-monitoring paired the app with a human (mentor/teacher review). Consider an optional "share summary with a parent/teacher/coach" export, controlled by the student.

### Gaps
- Could not obtain a pooled effect size for self-monitoring alone in adolescents or college students with ADHD; full texts of Bruhn et al. (2015) and Briesch & Briesch (2016) not read.
- No study found that tests automated (sensor/webcam) attention feedback as a substitute for student self-monitoring in ADHD.

---

## 4. Digital / app-based interventions for ADHD in adolescents: efficacy limits, engagement, dropout

### Takeaway
Digital ADHD interventions show small effects on inattention, inconsistent results, and low-quality evidence, with adolescents underrepresented. Engagement is a recognized problem. This supports modest framing ("study aid") and against efficacy claims.

### Cited Findings
- [PR] He et al. (2023), *Frontiers in Psychiatry*, meta-analysis of 31 studies (n = 2,169, ages 4–17): digital interventions improved inattention with effect −0.20 (95% CI −0.36 to −0.04); hyperactivity/impulsivity −0.07 (95% CI −0.23 to 0.09, not significant); executive function 0.71 (95% CI 0.37–1.04); authors note inconsistent findings due to intervention variety and small samples. PROSPERO CRD42022350349, PMID 37260755 — [Frontiers 10.3389/fpsyt.2023.1054831](https://www.frontiersin.org/articles/10.3389/fpsyt.2023.1054831); [PMC10228751](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10228751/)
- [PR] 2024 *European Child & Adolescent Psychiatry* meta-analysis of game-based digital therapeutics: small inattention benefits vs control on assessor ratings (SMD 0.28 and 0.21), but medication outperformed game-based DTx on teacher-rated inattention (SMD −0.62) — [search summary; Springer s00787 record](https://link.springer.com/10.1007/s00787-025-02676-y) (exact citation for this 2024 paper not verified; may be a different Springer article)
- [PR] BMC Psychiatry (April 2025) review of reviews, 26 systematic reviews of digital ADHD interventions: effectiveness "remains inconclusive due to low evidence quality" — [DOAJ record](https://doaj.org/article/789ef3c13fd143468097858bb49f61e5)
- [PR] 2026 JMIR meta-analysis in children: digital interventions "may relieve core symptoms", with highly variable efficacy depending on type, age, dose and assessment; notes an earlier meta-analysis was limited to ages 6–12, leaving adolescents (13–18) unexplored — [JMIR 2026;e95043](https://www.jmir.org/2026/1/e95043)
- [PR] Oxford mixed-methods review of digital health interventions for young people 16–25 with ADHD: limited evidence for this age group — [Oxford ORA](https://ora.ox.ac.uk/objects/uuid:fe5c55cb-4e47-4676-9ab3-45c89ab049f7)
- [PR] Game reviews (2022, 2025) note engagement of children with ADHD may be hard to sustain and evidence remains scarce/mixed; clinicians in an earlier review of popular ADHD apps raised concerns about lack of research support for app elements — [Frontiers 2022](https://frontiersin.org/articles/10.3389/fpsyt.2022.792402/full); [Frontiers 2025](https://www.frontiersin.org/journals/psychiatry/articles/10.3389/fpsyt.2025.1605744/full)

### Inferences
- Do not claim the app reduces ADHD symptoms; even purpose-built digital therapeutics show small (~0.2) inattention effects. Claim only what you measure (e.g., usability, self-reported usefulness, Focus Score agreement with self-report).
- Design for low-friction return: assume users will drop off; make it easy to resume (one-click "start a session", no re-setup), and avoid punishing gaps.

### Gaps
- No specific dropout/attrition percentages for adolescent ADHD apps were retrieved (full texts blocked). This is a known gap to fill before citing numbers.

---

## 5. Interface guidance: clutter, consistency, one primary action, clear language, animation, hiding non-essentials, notifications

### Takeaway
W3C's COGA guidance and WCAG 2.2 give concrete, authoritative rules that map directly to ADHD-friendly design: help users focus, limit interruptions, keep critical paths short, use clear words, keep layout consistent, allow pausing/hiding moving content and animations, and do not rely on memory. These are guidelines for cognitive and learning disabilities generally, not ADHD-specific trials.

### Cited Findings
- [GL] W3C "Making Content Usable for People with Cognitive and Learning Disabilities" (COGA, W3C Working Group Note, 2021) has a design objective "Help Users Focus" (earlier drafts: "Help Users to Maintain Focus"), with the user story "Distractions" and patterns including "Limit Interruptions" and "Make Short Critical Paths" — [W3C TR coga-usable](https://www.w3.org/tr/coga-usable); [2020 draft, multi-page](https://www.w3.org/TR/2020/WD-coga-usable-20201211/Overview-mutiple-pages.html)
- [GL] COGA rationale: people "who have issues with keeping or regaining focus may have difficulty completing a simple task if there are a lot of distractions and interruptions" — [W3C 2020 draft](https://www.w3.org/TR/2020/WD-coga-usable-20200717/Overview-mutiple-pages.html)
- [GL] COGA's other objectives (from the published Note; names recalled, not re-fetched this session): help users understand what things are and how to use them; help users find what they need; use clear and understandable content; help users avoid mistakes and know how to correct them; help users focus; ensure processes do not rely on memory; provide help and support; support adaptation and personalization — [W3C TR coga-usable](https://www.w3.org/tr/coga-usable); summarized by [UK DfE cognitive accessibility guidelines](https://accessibility.education.gov.uk/guidelines/coga)
- [GL] COGA card-sorting research grouped "Limit interruptions" under "Help users focus" with 91.3% agreement ("Make short critical paths" 34.8%) — [COGA TPAC 2021 slides](https://lists.w3.org/Archives/Public/www-archive/2021Oct/att-0007/COGA_Content_Usable_for_TPAC_2021.pdf)
- [GL] WCAG 2.2 success criteria relevant here (W3C Recommendation, Oct 2023) — [WCAG 2.2](https://www.w3.org/TR/WCAG22/):
  - 2.2.1 Timing Adjustable (A): users can turn off, adjust, or extend time limits.
  - 2.2.2 Pause, Stop, Hide (A): moving, blinking, scrolling or auto-updating content that starts automatically and lasts >5 s must be pausable/stoppable/hideable.
  - 2.2.4 Interruptions (AAA): interruptions can be postponed or suppressed by the user.
  - 2.3.3 Animation from Interactions (AAA): motion animation triggered by interaction can be disabled (pairs with CSS `prefers-reduced-motion`).
  - 3.2.3 Consistent Navigation (AA) and 3.2.4 Consistent Identification (AA): repeated navigation and components stay in the same order and naming.
  - 3.2.6 Consistent Help (A, new in 2.2): help mechanisms appear in the same relative place.
  - 3.3.2 Labels or Instructions (A); 3.3.7 Redundant Entry (A, new in 2.2): do not make users re-enter information already given; 3.3.8 Accessible Authentication (Minimum) (AA, new in 2.2): no cognitive function test (e.g., memorizing) to log in.
  - 2.4.6 Headings and Labels (AA); 3.1.5 Reading Level (AAA).
- [EO] UK government design guidance explicitly frames cognitive overload as a design risk (minimize choices and content per page) — [Kirklees Council: cognitive overload](https://www.kirklees.gov.uk/beta/website-standards/cognitive-overload.aspx)

### Inferences (concrete UI rules for NeuroFocus AI)
- One primary action per screen (big "Start focus session"); secondary items in a collapsed "More" area. (COGA: Make Short Critical Paths.)
- A "Focus mode" during sessions that hides nav, stats and everything except the timer, task name and a stop/pause button. (COGA: Help Users Focus / Limit Interruptions.)
- Nudges: user-controlled frequency, quiet tone, never modal pop-ups that block work; allow "snooze nudges" and "mute for this session" (WCAG 2.2.4). No sound by default.
- Respect `prefers-reduced-motion`; no auto-playing animation, confetti, or pulsing elements; any live Focus Score indicator must be hideable (WCAG 2.2.2, 2.3.3).
- Same layout and button positions on every page; help link always in the same spot (WCAG 3.2.3, 3.2.6).
- Plain language at roughly middle-school reading level; short sentences; no jargon like "gaze vector" in the UI.
- Do not rely on memory: show the current task and the user's if-then plan on the session screen; remember last settings (WCAG 3.3.7).
- Let users adjust session length and turn time limits off (WCAG 2.2.1).

### Gaps
- Could not verify current COGA pattern numbering/wording (w3.org fetch blocked). Re-check before quoting pattern numbers.
- No ADHD-specific RCTs of these interface rules were found; evidence is guideline-level.

---

## 6. Pomodoro-style fixed intervals and break scheduling

### Takeaway
I found no randomized trial of the Pomodoro Technique in people with ADHD or in students. Popular claims that it is "great for ADHD" are expert opinion. Adjacent evidence: micro-breaks have small benefits for vigor and fatigue but not clearly for cognitively demanding performance.

### Cited Findings
- [PR] Albulescu et al. (2022), "'Give me a break!' A systematic review and meta-analysis on the efficacy of micro-breaks for increasing well-being and performance," *PLoS ONE* 17(8): e0272460; 22 samples, N = 2,335: micro-breaks (≤10 min) increased vigor (d = .36) and reduced fatigue (d = .35); overall performance effect not significant (d = .16, p = .116); longer breaks associated with larger performance gains; significant performance effects only for less cognitively demanding tasks — [PubMed 36044424](https://pubmed.ncbi.nlm.nih.gov/36044424/); [BPS Research Digest summary](https://bps.org.uk/research-digest/gimme-microbreak)
- [EO] Popular/clinician claims that Pomodoro helps ADHD (breaks make long tasks less overwhelming; 25 minutes is not "scientifically sacred" and is often adjusted) — [Business Insider](https://www.businessinsider.in/science/health/news/what-is-the-pomodoro-technique-the-productivity-method-great-for-students-and-people-with-adhd/articleshow/87190953.cms); [TextExpander blog](https://textexpander.com/blog/pomodoro-technique-adhd)
- [EO] A secondary source states the Pomodoro Technique itself has never been tested in clinical trials (unverified) — [Acibadem blog](https://acibademinternational.com/blog/the-pomodoro-technique-why-25-minutes-keeps-beating-willpower/)

### Inferences
- Offer Pomodoro as a preset, not a rule: let users pick interval length (e.g., 10/15/25 min) and break length; a short default (10–15 min) suits delay aversion (inference).
- Present breaks as planned, guilt-free, and timed (visible break countdown), with a gentle "ready to start again?" cue to address task re-initiation.
- Label Pomodoro in the app as "a popular method", not "proven for ADHD".

### Gaps
- No ADHD- or student-specific controlled study of fixed work/break intervals found. The "University of Illinois brief-breaks vigilance study" often cited in blogs was not verified against the original paper.

---

## 7. Privacy, stigma and surveillance concerns with webcam/attention monitoring

### Takeaway
Students react negatively to camera-based attention monitoring, especially when it is visible to others or used to judge them; commercial classroom "engagement detection" and webcam proctoring drew public backlash and legal findings. Neurodivergent HCI researchers criticize ADHD technology that frames users as deficient and excludes them from design. On-device processing, student control and no sharing by default are the key mitigations.

### Cited Findings
- [EO, preprint] Han, McKay, Buchanan & Smith (2026, arXiv:2602.11074): survey of 132 students at Australian universities shown scenarios of AI attention/emotion sensing; consistently negative reception to the monitoring element; gaze-based attention tracking received about as negative a reaction as facial emotion recognition; students worried about being identified as struggling; anxiety/discomfort rose and perceived benefit fell — [arXiv 2602.11074](https://www.arxiv.org/pdf/2602.11074); [press summary](https://www.devdiscourse.com/article/technology/3802721-students-push-back-against-gaze-tracking-and-emotion-ai-in-universities) (peer-review status not confirmed)
- [EO] Intel/Classroom Technologies classroom engagement-detection software using student webcams drew criticism that students could be wrongly penalized, plus petitions on privacy and discrimination grounds — [Gizmodo](https://gizmodo.com/remote-learning-spyware-tracks-student-emotions-1848806568)
- [EO] Cleveland State University was found (2022) to have violated a student's privacy by requiring a webcam room scan before a remote test — [Inside Higher Ed](https://www.insidehighered.com/index%2Ephp/node/142111)
- [EO] Virginia Tech Tech4Humanity occasional paper: gaze-tracking measures "have been scrutinized for issues with ethics, privacy, and legality" — [Tech4Humanity Lab PDF](https://tech4humanitylab.clahs.vt.edu/wp-content/uploads/2025/03/Occasional-Paper-2-Gaze-Tracking.pdf)
- [PR/EO] An attention-tracking tool for online classes that alerts teachers below a threshold surveyed 31 students on privacy/ethics — [arXiv 2210.07286](https://arxiv.org/pdf/2210.07286)
- [PR] Spiel, Hornecker, Williams & Good (2022), "ADHD and Technology Research – Investigated by Neurodivergent Readers," CHI '22, DOI 10.1145/3491102.3517592: critical review from neurodivergent researchers of how ADHD tech frames ADHD, its aims, and the (often excluded) role of people with ADHD in the research — [UvA DARE](https://dare.uva.nl/id/b5158a6b-ee52-48a7-b4be-772d430bad4a); [author PDF](https://researchgate.net/profile/Katta-Spiel/publication/360330913_ADHD_and_Technology_Research_-_Investigated_by_Neurodivergent_Readers/links/6282c0e27a08f263d551e17c/ADHD-and-Technology-Research-Investigated-by-Neurodivergent-Readers.pdf) (specific recommendations not read in full)
- [PR] Webcam eye-tracking is promoted as cheaper/scalable, but accuracy and false positives are recognized challenges — [Univ. NOVA Lisbon review](https://run.unl.pt/bitstreams/0e03dd03-5be2-4ec9-94cd-9d1f1beff708/download); [CEUR-WS paper](https://ceur-ws.org/Vol-4036/Paper10.pdf)

### Inferences
- Process video on-device only; never store or upload frames; say so plainly on the camera-permission screen and in a privacy page. Provide a clear camera-on indicator and a one-click "camera off" that still lets the timer run.
- The student owns the data: no teacher/parent dashboards by default; sharing is opt-in, per report.
- Language: "Looking-at-screen estimate", not "attention" or "focus" as a fact; acknowledge false positives (reading paper notes, thinking while looking away) and let users correct a session ("I was reading my textbook").
- Avoid deficit framing (no "ADHD score", no diagnosis-like wording); involve students with ADHD in testing (Spiel et al. critique).

### Gaps
- No peer-reviewed study found specifically on adolescents with ADHD using self-directed (not teacher-facing) webcam focus tools; the 132-student study is a preprint about university students.
- No validation evidence found that webcam gaze-on-screen correlates with learning or genuine attention.
