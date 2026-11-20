# Evidence-Based Personalized Weekly Study Plans and Transparent Small-Data Personalization (NeuroFocus AI)

Verification note: Items marked **[verified]** were checked against a search result or abstract during this session. Items marked **[background, not re-verified]** are standard references cited from prior knowledge. Their bibliographic details are well known, but the developer should open the DOI before quoting any number. journals.plos.org and pmc.ncbi.nlm.nih.gov could not be fetched from this session, so for the PLOS papers only the abstracts and secondary summaries were seen.

## 1. Learning-science rules for scheduling (spacing, retrieval practice, interleaving)

### Takeaway
Two techniques have the strongest evidence and should drive the plan's structure: spreading study of each topic over several days (distributed practice) and self-testing (retrieval practice). Mixing related problem types (interleaving) has moderate support and should be used selectively. Spacing becomes a concrete rule if the gap between reviews is set as a fraction of the time remaining until the test: about 20–40% for a test 1 week away, falling to about 5–10% for a test 1 year away.

### Cited Findings
- Dunlosky, Rawson, Marsh, Nathan & Willingham (2013), "Improving Students' Learning With Effective Learning Techniques: Promising Directions From Cognitive and Educational Psychology," *Psychological Science in the Public Interest* 14(1), 4–58, DOI 10.1177/1529100612453266. They rated 10 techniques. **Practice testing** and **distributed practice** received "high utility." **Interleaved practice**, elaborative interrogation and self-explanation received "moderate." Summarization, highlighting, the keyword mnemonic, imagery for text and **rereading** received "low." — [Dunlosky et al. 2013](https://doi.org/10.1177/1529100612453266) [background, not re-verified]
- Cepeda, Pashler, Vul, Wixted & Rohrer (2006), "Distributed practice in verbal recall tasks: A review and quantitative synthesis," *Psychological Bulletin* 132(3), 354–380, DOI 10.1037/0033-2909.132.3.354. Spaced study beat massed study across hundreds of comparisons. The best gap between study sessions grew longer as the retention interval grew longer. — [Cepeda et al. 2006](https://doi.org/10.1037/0033-2909.132.3.354) [background, not re-verified]
- Cepeda, Vul, Rohrer, Wixted & Pashler (2008), "Spacing Effects in Learning: A Temporal Ridgeline of Optimal Retention," *Psychological Science* 19(11), 1095–1102, DOI 10.1111/j.1467-9280.2008.02209.x. More than 1,350 participants were tested, with study gaps up to 3.5 months and test delays up to 1 year. As the gap increased, retention first rose and then fell. **The optimal gap fell from about 20–40% of a 1-week test delay to about 5–10% of a 1-year test delay.** A gap that is too long costs less than a gap that is too short. — [PubMed 19076480](https://pubmed.ncbi.nlm.nih.gov/19076480/); [PDF](https://www.evullab.org/pdf/CepedaVulRohrerWixtedPashler-PS-2008.pdf) [verified, abstract]
- Latimier, Peyre & Ramus (2021), "A Meta-Analytic Review of the Benefit of Spacing out Retrieval Practice Episodes on Retention," *Educational Psychology Review* 33, 959–987, DOI 10.1007/s10648-020-09572-8. In 29 studies, spaced retrieval beat massed retrieval with **g = 0.74**. **Expanding and uniform spacing schedules did not differ reliably (g = 0.034)**, although expanding schedules may help more when items are tested many times. — [Springer](https://link.springer.com/10.1007/s10648-020-09572-8) [verified, abstract via search]
- Rowland (2014), "The effect of testing versus restudy on retention: A meta-analytic review of the testing effect," *Psychological Bulletin* 140(6), 1432–1463, DOI 10.1037/a0037559. Testing beat restudying with **g ≈ 0.50**. Secondary summaries report a larger effect when the retention interval is longer than 1 day (g ≈ 0.69). — [PDF copy](https://courseware.epfl.ch/assets/courseware/v1/fdde2f0aa590bf3b1324077a6bf1540c/asset-v1%3AEPFL%2BDEMO%2B2020%2Btype%40asset%2Bblock/Rowland2014-meta-analysis.pdf) [g value from secondary sources, verify in paper]
- Adesope, Trevisan & Sundararajan (2017), "Rethinking the Use of Tests: A Meta-Analysis of Practice Testing," *Review of Educational Research* 87(3), 659–701, DOI 10.3102/0034654316689306. The analysis covered 118 articles, 272 effect sizes and 15,472 participants. Practice tests beat restudying and all other comparison conditions. The overall effect is reported as **g ≈ 0.61** (my recollection), while a later review cites 0.70. Check the paper before quoting either number. — [WSU PDF](https://education.wsu.edu/documents/2018/01/rethinking-use-tests.pdf/) [scope verified, g needs check]
- Brunmair & Richter (2019), "Similarity matters: A meta-analysis of interleaved learning and its moderators," *Psychological Bulletin* 145(11), 1029–1052, DOI 10.1037/bul0000209. The analysis covered 59 studies and 238 effect sizes. The overall effect was **g = 0.42**, with high heterogeneity (I² = 77%). Interleaving helped more when categories were similar to each other and when material was complex. It was not beneficial, and sometimes harmful, for expository texts and word lists (one subgroup estimate was g = −0.39). — [PubMed 31556629](https://pubmed.ncbi.nlm.nih.gov/31556629/) [verified, abstract]

### Inferences (scheduling rules an algorithm can implement)
- **Review-gap rule.** Let D be the number of days until a deadline or exam. After a topic's first study block, schedule the first review about 0.2–0.4 × D later when D ≤ 7–14 days. For longer horizons, use smaller fractions (about 0.1 × D for 1–3 months, following the ridgeline trend). Enforce a minimum gap of 1 day, because the benefit of spacing depends on sleep and time passing. Example: an exam in 10 days gives learn on day 0, review on day 3, review on day 6–7, and a final retrieval check on day 9. When the available time windows cannot fit the ideal gap, choose the longer option, since Cepeda 2008 found a too-long gap costs less than a too-short one.
- **Fixed or equal gaps are acceptable.** Latimier et al. found no reliable advantage for expanding schedules, so the algorithm does not need SM-2-style expanding intervals to be defensible. Equal gaps that fit the student's available days are easier to explain.
- **Make each review a retrieval session.** A review block should be labeled "self-test / practice questions / blurt-recall," not "reread." Rereading has low utility (Dunlosky).
- **Interleave related material only.** Interleave inside one subject when it has similar problem types (for example math problem types or science categories). Do not mix unrelated subjects in the name of interleaving. For reading-heavy subjects, use blocked study. Brunmair & Richter's moderators support this.
- **Spread out new material.** Prefer fewer minutes on a topic per day across more days over one long block. Cap new material for any one topic at about one block per day when the deadline allows it.

### Gaps
- The ridgeline percentages come from learning facts and trivia-type verbal material. Whether they hold for complex high-school problem solving is extrapolation.
- No source gives an exact optimal number of reviews. Three or four retrieval sessions before an exam is a reasonable heuristic, not an empirically derived optimum.
- I could not verify the exact Adesope et al. overall g in this session.

## 2. Block length and breaks (vigilance, Pomodoro, micro-breaks)

### Takeaway
No study fixes one "correct" study block length. The often-quoted "10–15 minute attention span" is not well supported. Systematic breaks (for example 24 minutes of study and a 6-minute break) gave mood and efficiency benefits over self-regulated breaks in one controlled study. Micro-breaks reliably raise vigor and lower fatigue but have only a small, non-significant average effect on performance. A default of about 25 minutes of work and 5 minutes of break is defensible, as long as the app labels it a default and adapts it.

### Cited Findings
- Biwer, Wiradhany, oude Egbrink & de Bruin (2023), "Understanding effort regulation: Comparing 'Pomodoro' breaks and self-regulated breaks," *British Journal of Educational Psychology* 93(S2), 353–367, DOI 10.1111/bjep.12593. University students had real study sessions in one of three conditions:
  - self-regulated breaks (n = 35)
  - a 6-minute break after each 24-minute block (n = 25)
  - a 3-minute break after each 12-minute block (n = 27)

  Systematic breaks produced better mood and similar task completion in less time. Self-regulators studied longer stretches and took longer breaks. — [PubMed 36859717](https://pubmed.ncbi.nlm.nih.gov/36859717/) [verified, abstract via search]
- A later paper from the same Maastricht group compared Pomodoro, Flowtime and self-regulated breaks. It reportedly found that fatigue rose faster with Pomodoro breaks, and motivation fell faster with Pomodoro and Flowtime breaks, than with self-regulated breaks. The evidence on systematic breaks is therefore mixed. — [PMC12292963](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/) [seen only as a search summary, not fetched; confirm authors and year before citing]
- Albulescu, Macsinga, Rusu, Sulea, Bodnaru & Tulbure (2022), "'Give me a break!' A systematic review and meta-analysis on the efficacy of micro-breaks for increasing well-being and performance," *PLOS ONE* 17(8), e0272460, DOI 10.1371/journal.pone.0272460. The review covered 22 samples (N = 2,335) with breaks of 10 minutes or less. Results:
  - Vigor improved, d = 0.36.
  - Fatigue decreased, d = 0.35.
  - Overall performance changed by d = 0.16, which was not significant (p = .116). The effect was significant only for tasks with lower cognitive demand.
  - Longer breaks produced larger performance gains. The authors suggest that recovering from highly depleting tasks may need breaks longer than 10 minutes.

  — [PubMed 36044424](https://pubmed.ncbi.nlm.nih.gov/36044424/) [verified, abstract]
- Wilson & Korn (2007), "Attention during lectures: Beyond ten minutes," *Teaching of Psychology* 34(2), 85–89, DOI 10.1080/00986280701291291. This literature review found weak empirical support for the common claim that attention declines 10–15 minutes into a lecture. — [SAGE](https://journals.sagepub.com/doi/10.1080/00986280701291291) [verified]
- Warm, Parasuraman & Matthews (2008), "Vigilance requires hard mental work and is stressful," *Human Factors* 50(3), 433–441, DOI 10.1518/001872008X312152. The vigilance decrement in monitoring tasks is linked to resource depletion and workload, not just boredom. Note that this comes from detecting rare signals, not studying. — [Warm et al. 2008](https://doi.org/10.1518/001872008X312152) [background, not re-verified]
- Ariga & Lleras (2011), "Brief and rare mental 'breaks' keep you focused: Deactivation and reactivation of task goals preempt vigilance decrements," *Cognition* 118(3), 439–443, DOI 10.1016/j.cognition.2010.12.007. Brief switches away from the task prevented the vigilance decrement in a roughly 50-minute task. — [Ariga & Lleras 2011](https://doi.org/10.1016/j.cognition.2010.12.007) [background, not re-verified]

### Inferences (defaults and individual adaptation)
- **Default block:** 25 minutes of study and 5 minutes of break, closely matching the 24 + 6 condition in Biwer 2023. After 3–4 blocks, add a longer break of 15–20 minutes, since Albulescu's meta-regression suggests longer breaks help with depleting work. Allowed range: about 10–50 minutes. A 12 + 3 option suits students with low measured streaks or self-reported ADHD-type difficulties. That is a design choice based on the 12 + 3 condition, not tested on ADHD samples.
- **Individual adaptation from the app's own data:** set the planned block length near the student's typical uninterrupted focus streak, for example the median streak or the 60th–75th percentile, rounded to 5 minutes and clamped to the 10–50 minute range. Combine it with the population default using shrinkage (see section 5). Justify breaks with mood and fatigue benefits. Do not claim proven performance gains, because the performance effect in Albulescu 2022 was not significant.
- **Honesty:** the app should say "a default supported by one controlled study and a micro-break meta-analysis." It should not say "science proves 25 minutes is optimal."

### Gaps
- I found no meta-analysis of the Pomodoro technique for high-school students, and no controlled study of it in ADHD populations.
- Gaze-on-screen "focus streaks" are not the same as validated vigilance measures. Mapping streak length to block length is an engineering heuristic.

## 3. Time of day and chronotype

### Takeaway
Adolescents shift toward later sleep and wake times ("eveningness"), and some evidence shows people perform better at their preferred time of day (the "synchrony effect"). The synchrony evidence is mixed, comes mainly from individual studies, and has small effects. Time of day should be a soft preference in the plan, not a hard rule.

### Cited Findings
- Roenneberg et al. (2004), "A marker for the end of adolescence," *Current Biology* 14(24), R1038–R1039, DOI 10.1016/j.cub.2004.11.039. In a large population sample, chronotype grows progressively later through adolescence and peaks around age 20. — [Roenneberg et al. 2004](https://doi.org/10.1016/j.cub.2004.11.039) [background, not re-verified]
- May, Hasher & Stoltzfus (1993), "Optimal time of day and the magnitude of age differences in memory," *Psychological Science* 4(5), 326–330. This is a foundational study of the synchrony effect: performance was better at the participant's preferred time of day. — [May et al. 1993](https://doi.org/10.1111/j.1467-9280.1993.tb00473.x) [background, not re-verified]
- Goldstein, Hahn, Hasher, Wiprzycka & Zelazo (2007), "Time of day, intellectual performance, and behavioral problems in Morning versus Evening type adolescents: Is there a synchrony effect?" *Personality and Individual Differences* 42(3), 431–440. Adolescents showed a synchrony effect on fluid-intelligence measures. — [UMN record](https://experts.umn.edu/en/publications/time-of-day-intellectual-performance-and-behavioral-problems-in-m/) [verified exists; effect description from secondary summary]
- Preckel, Lipnevich, Schneider & Roberts (2011), "Chronotype, cognitive abilities, and academic achievement: A meta-analytic investigation," *Learning and Individual Differences* 21(5), 483–492. Morningness is associated with somewhat higher school achievement, while eveningness has a small positive relation to cognitive ability. — [DOI 10.1016/j.lindif.2011.07.003](https://doi.org/10.1016/j.lindif.2011.07.003) [effect sizes not verified this session]
- Goldin, Hahn and others (2020), *Nature Human Behaviour*: in a large sample of secondary-school students who attended school in the morning, early chronotypes outperformed late chronotypes, most strongly in math. The effect disappeared for students with afternoon schedules. — [Nature Hum Behav](https://www.nature.com/articles/s41562-020-0820-2) [verified via search summary; confirm author list]
- Counter-evidence: a 2024 study of children found better performance on some tasks at a non-preferred time of day. — [Behav Sci 2024](https://www.mdpi.com/2076-328X/14/4/310) [search summary only]

### Inferences
- Use time of day as a soft weight. Rank the student's chosen time slots by (a) the time of day they report as best in the onboarding survey (a reduced Morningness–Eveningness-type question) and (b) their measured focus by time of day, shrunk toward "no difference" (see section 5). Place the hardest or newest material in the highest-ranked slots, and reviews or easier tasks in lower-ranked ones.
- With 3–4 sessions, often only 1–2 per time band, the measured time-of-day difference is mostly noise. The app should not claim "you focus best in the evening" until each compared time band has at least about 3 sessions and the difference survives shrinkage.

### Gaps
- I found no meta-analysis focused on the synchrony effect in adolescents.

## 4. Planning interventions (implementation intentions, time management, planning fallacy)

### Takeaway
Concrete "if-then / when-where" plans have a medium-to-large average effect on reaching goals (d = 0.65). Time management relates moderately to academic achievement and more strongly to wellbeing. People routinely underestimate how long tasks take, so plans need built-in slack.

### Cited Findings
- Gollwitzer & Sheeran (2006), "Implementation intentions and goal achievement: A meta-analysis of effects and processes," *Advances in Experimental Social Psychology* 38, 69–119, DOI 10.1016/S0065-2601(06)38002-1. Across 94 independent tests (more than 8,000 participants), implementation intentions had **d = 0.65** on goal attainment. — [Konstanz record](https://kops.uni-konstanz.de/entities/publication/2e749bfb-8533-437c-8203-7e788c910c5f) [verified]
- Aeon, Faber & Panaccio (2021), "Does time management work? A meta-analysis," *PLOS ONE* 16(1), e0245066, DOI 10.1371/journal.pone.0245066. The analysis covered 158 studies and more than 53,000 respondents. Findings:
  - Moderate positive relations with job performance, academic achievement and wellbeing, and a moderate negative relation with distress.
  - Stronger effects on wellbeing, especially life satisfaction, than on performance.
  - Conscientiousness was the strongest correlate.
  - The university press release reports no discernible link with standardized test results.
  - Most data are correlational, and I could not confirm the exact pooled r values in this session.

  — [EconPapers abstract](https://econpapers.repec.org/RePEc:plo:pone00:0245066); [EurekAlert release](https://www.eurekalert.org/news-releases/878307) [verified abstract-level]
- Buehler, Griffin & Ross (1994), "Exploring the 'planning fallacy': Why people underestimate their task completion times," *Journal of Personality and Social Psychology* 67(3), 366–381, DOI 10.1037/0022-3514.67.3.366. Students' predictions of when they would finish academic projects were systematically optimistic. In a well-known result, students took far longer than their "best guess" to finish their theses, and only a minority finished by their own predicted date. — [Buehler et al. 1994](https://doi.org/10.1037/0022-3514.67.3.366) [background, not re-verified; check exact figures before quoting]

### Inferences
- **Turn every block into an implementation intention:** "On Tuesday at 17:00, at my desk, I will do 2 × 25-minute blocks of Chemistry: practice questions on stoichiometry." Add an optional if-then line for the student's most common distraction, for example: "If I reach for my phone, then I put it in the other room."
- **Planning-fallacy buffer:** fill only about 70–80% of the student's declared available time with planned blocks, leaving 20–30% as catch-up slack. Plan to finish new material 1–2 days before the deadline, leaving the final days for retrieval. These percentages are design heuristics based on Buehler et al.'s qualitative finding, not values estimated in the literature.
- **Frame benefits honestly:** the strongest evidence is for reduced stress and better follow-through, not guaranteed higher grades (Aeon 2021).

### Gaps
- Exact pooled correlations in Aeon et al. 2021 are not confirmed here, because journals.plos.org was unreachable.
- I found no quantitative "optimal buffer percentage" in the literature.

## 5. Transparent personalization with 3–4 sessions

### Takeaway
Three or four sessions are far too few to train a machine-learning model, and enough only for crude, heavily regularized estimates. The defensible method is to start from population defaults (section 2), then update toward the student's own summary statistics in proportion to how much data exists (shrinkage, also called Bayesian or empirical-Bayes updating). The app should show the student the formula and the confidence level, and should keep adapting from later sessions, for example with a simple bandit or rule-based adjustment.

### Cited Findings
- Efron & Morris (1975), "Data analysis using Stein's estimator and its generalizations," *JASA* 70(350), 311–319, DOI 10.1080/01621459.1975.10479864. Their classic baseball example showed that shrinking each player's early-season batting average toward the overall mean predicted the rest of the season better than the raw averages. This is a close analogy to estimating a student's focus from a few sessions. — [Efron & Morris 1975](https://doi.org/10.1080/01621459.1975.10479864) [background, not re-verified]
- Gelman, Carlin, Stern, Dunson, Vehtari & Rubin (2013), *Bayesian Data Analysis* (3rd ed.), CRC Press. Hierarchical and normal–normal models give a posterior mean that is a precision-weighted average of the prior mean and the data mean. The free PDF is on the authors' site. — [BDA3](http://www.stat.columbia.edu/~gelman/book/) [background, not re-verified]
- Barnett, van der Pols & Dobson (2005), "Regression to the mean: what it is and how to deal with it," *International Journal of Epidemiology* 34(1), 215–220, DOI 10.1093/ije/dyh299. Extreme first measurements tend to be followed by values closer to the mean, so an apparent "improvement" or "decline" after a very good or bad session can be pure artifact. — [Barnett et al. 2005](https://doi.org/10.1093/ije/dyh299) [background, not re-verified]
- Russo, Van Roy, Kazerouni, Osband & Wen (2018), "A Tutorial on Thompson Sampling," *Foundations and Trends in Machine Learning* 11(1), 1–96, DOI 10.1561/2200000070. Thompson sampling handles the explore/exploit trade-off by sampling from the posterior of each option. — [arXiv 1707.02038](https://arxiv.org/abs/1707.02038) [background, not re-verified]
- Spaced-repetition systems personalized from data exist, but they rely on large datasets, for example millions of Duolingo review traces. Settles & Meeder (2016), "A Trainable Spaced Repetition Model for Language Learning," *ACL* 2016, DOI 10.18653/v1/P16-1174. Tabibian et al. (2019), "Enhancing human learning via spaced repetition optimization," *PNAS* 116(10), 3988–3993, DOI 10.1073/pnas.1815156116. — [Settles & Meeder](https://doi.org/10.18653/v1/P16-1174); [Tabibian et al.](https://doi.org/10.1073/pnas.1815156116) [background, not re-verified]

### Inferences (concrete, explainable algorithm)
- **Why not train an ML model:** with 3–4 sessions there are 3–4 independent observations per student. That is fewer data points than parameters for almost any model, and train/test validation is impossible. The data-driven systems cited above needed population-scale data. The defensible label is "rule-based personalization with statistical shrinkage," not "AI that learned you."
- **Shrinkage formula for block length:**
  - personal estimate = w × (student's median focus streak) + (1 − w) × (default of 25 minutes)
  - w = n / (n + k), where n is the number of sessions and k is a prior strength of about 4–5 sessions (a design choice)
  - With n = 3 and k = 4, w ≈ 0.43, so the estimate stays close to the default. With n = 12, w = 0.75.
  - Round to 5 minutes and clamp to 10–50 minutes.

  Use the median, not the mean, because streaks are right-skewed. The app can show this calculation verbatim.
- **Same pattern for time of day:**
  - adjusted score for a time band = (n_b × band mean + k × overall mean) / (n_b + k)
  - Only rank a band as "better" when the adjusted difference is above a set threshold (for example 5 percentage points of Focus Score) and n_b ≥ 3.
- **Minimum-data rules (heuristic, to be stated as such):**
  - Under 3 sessions: defaults only.
  - 3–4 sessions: adjust block length only, and only partially through shrinkage.
  - At least 3 sessions per time band: allow time-of-day ranking.
  - About 8 or more sessions: allow subject-specific adjustments.
  - Always show "confidence: low / medium / high" based on n.
- **Ongoing adaptation:** after the plan starts, each session contributes another observation. An option is a simple bandit over 3–4 block-length "arms," for example 15, 20, 25 and 35 minutes. The reward could be completion of the planned block or the block's Focus Score. Use Thompson sampling with Beta or Normal priors centered on the default. A simpler alternative is a rule: if at least 2 of the last 3 blocks were completed with focus above the threshold, lengthen by 5 minutes; if at least 2 were abandoned, shorten by 5 minutes.
  - Caveat: a bandit needs many pulls per arm to converge, likely dozens of sessions. Over a few weeks it acts mostly as structured exploration.
- **Regression-to-the-mean guard:** do not report "your focus improved X%" based on comparing the first session with later ones. Compare like with like (same subject and time band), and describe changes cautiously.
- **Construct-validity caveat:** Focus Score (looking at the screen) is a proxy. Off-screen work such as paper notes or textbooks will look like "distraction." The plan should allow off-screen study modes, or let the student mark them.

### Gaps
- No published source gives a validated minimum number of sessions for personalizing study block length. The thresholds above are reasoned heuristics.
- The reliability across sessions (test–retest) of gaze-based focus streaks is unknown. Measuring it, for example with an intraclass correlation (ICC) across sessions from pilot data or the developer's own use, would justify the shrinkage weight k.

## 6. Evaluating the plan without human participants

### Takeaway
Without participants, the project can rigorously show that the planner correctly applies its stated rules, and how robust its personalization is to noisy data. It cannot show that students learn more. The evaluation should consist of deterministic constraint tests and simulation studies, with the limitations stated explicitly.

### Cited Findings
- The rules being tested come from the sources above: review-gap fractions (Cepeda et al. 2008), retrieval-based reviews (Dunlosky 2013; Rowland 2014), and break defaults (Biwer 2023; Albulescu 2022). — see sections 1–2
- Shrinkage estimators reduce total squared prediction error relative to raw per-unit means when there are many units with few observations each. Efron & Morris (1975) is the standard demonstration. — [Efron & Morris 1975](https://doi.org/10.1080/01621459.1975.10479864) [background, not re-verified]

### Inferences (concrete evaluation plan)
1. **Unit and property tests for constraint satisfaction.** Generate random inputs: availability windows, subjects, deadlines and session histories. Check that every plan:
   - places no block outside the available windows
   - has no overlapping blocks
   - schedules every topic's first study before its deadline
   - puts at least 2 retrieval reviews for each topic before its deadline when time allows
   - keeps review gaps within the target fraction of the time remaining, or uses the nearest feasible longer gap
   - keeps total planned time at or below 80% of available time (the buffer)
   - keeps block lengths within 10–50 minutes
   - includes a long break after N blocks
   - produces identical output for identical input (deterministic)

   Report the pass rate over, for example, 10,000 randomized cases. Property-based testing (Hypothesis for Python, fast-check for JavaScript) suits this.
2. **Simulation of personalization accuracy.** Create synthetic students with known true median streaks drawn from a plausible distribution, for example 10–45 minutes, and session-to-session noise. Generate 3, 4, 8 and 12 sessions for each. Compare the mean absolute error of three estimators: (a) the population default, (b) the raw personal median, and (c) the shrinkage estimate. Expected result: (c) beats (b) at small n and converges toward it as n grows. Show this as a graph. Also vary k and the noise level as a sensitivity analysis.
3. **Optional learning-outcome simulation.** Plug the schedules into a published memory model to compare spaced and massed variants, for example the exponential-forgetting or half-life model of Settles & Meeder (2016). Present this only as a model-based illustration, not as evidence of real learning gains.
4. **Comparison baselines.** Compare against (i) a naive plan that crams each subject just before its deadline and (ii) a fixed plan with 25-minute blocks and no personalization. Report metrics such as mean review gap divided by time to deadline, the number of reviews per topic, and slack.
5. **Transparency audit.** For each generated plan, check that every decision (block length, slot choice, review date) has a human-readable reason string that cites its rule and source.
6. **State the limitation explicitly.** Effects on grades or retention require a future study with human participants, ethics review and informed consent (for minors, parental consent). ISEF requires IRB or SRC approval for human-participant research.

### Gaps
- I found no published standard benchmark for evaluating study-planning apps without users. The simulation design above is my proposal.
- I did not verify the specific ISEF rule numbers for human-participant research in this session. Check them in the current ISEF International Rules.
