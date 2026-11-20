# Gentle Refocus Cues and Fatigue-Based Break Prompts (NeuroFocus AI)

Scope note: research done quickly (about 15 tool calls). Two primary documents could not be fetched because their hosts are blocked in this session's network: the W3C WCAG Understanding page (www.w3.org) and Patterson's 1982 CAA guidelines PDF (www.pdn.cam.ac.uk). Facts drawn from those come from search-result abstracts and secondary citations, and are marked. Numbers in "Inferences" and the final parameter list are engineering choices built from the cited findings, not values any one paper prescribes, unless a source is given.

## A1. What sound properties trigger the acoustic startle reflex, and what onset ramps and levels avoid it?

### Takeaway
Startle is driven mainly by a fast rise time combined with high intensity, especially broadband noise. Slowing the onset reduces startle in a graded way. Most startle studies use intense noise (about 95 to 105 dB) with near-instant onsets. A quiet tonal cue with an onset of 50 ms or more sits far outside the conditions that cause startle.

### Cited Findings
- Blumenthal, Cuthbert, Filion, Hackley, Lipp & Van Boxtel (2005), "Committee report: Guidelines for human startle eyeblink electromyographic studies," *Psychophysiology* 42(1), 1-15, DOI 10.1111/j.1469-8986.2005.00271.x. This is the standard methods paper for eliciting and measuring human startle blink. Its exact rise-time recommendations were not visible in what I could access, so check the full text. — [Scilit record](https://www.scilit.net/publications/1cf3a7bb59abaa293b92df62a19c520a)
- Earlier rise-time work cited in this literature: Blumenthal & Berg (1986), on rise-time effects, and Blumenthal (1988), on stimulus rise and fall time. I saw titles only, not results. — [Scilit record of the 2005 report and related search](https://www.scilit.net/publications/1cf3a7bb59abaa293b92df62a19c520a)
- A review chapter states that "even the most intense sound will fail to generate a body jerk or even an eyeblink if the rise time is slow enough." It reports similar rise-time effects in adult humans and a possible "critical duration" of at least about 30 ms (Berg, 1973). — [Taylor & Francis chapter](https://www.taylorfrancis.com/books/9781317783299/chapters/10.4324/9781315807355-6)
- Lipp & Vila (Castellar): in humans, 105 dB white noise with rise times from 0 to 240 ms. Rise time changed the blink startle response but did not selectively change the short-latency heart-rate acceleration. — [Springer, Psychonomic journal PDF](https://link.springer.com/content/pdf/10.3758/BF03205275.pdf) (attribution from search snippet; verify)
- In rats, a short rise time is "a crucial factor" for eliciting the acoustic startle response, and changing rise time causes "pronounced changes in ASR amplitude." — [Acta Neurobiologiae Experimentalis](https://ane.pl/index.php/ane/article/download/1451/1451)
- In bottlenose dolphins (Götz & Janik lab, *J. Exp. Biol.*), startle to broadband noise decreased as rise time increased from 2 to 100 ms. Models estimated that about 141 to 220 ms would eliminate startle. These figures are from another species and are modelled, not measured. — [JEB PDF](https://cob.silverchair.com/jeb/article-pdf/1982528/jeb208470.pdf)
- Patterson (1989/1990), in a follow-up to his guidelines, suggests that a slower onset of about 50 ms is less startling. This is secondhand, from a search summary; I could not fetch the original. — [Patterson, Auditory warnings at work (Royal Society 1990) PDF](https://www.pdn.cam.ac.uk/system/files/documents/AuditoryWarningsAtWork_RSoc1990.pdf)

### Inferences
- In a quiet bedroom or study, a cue at normal conversational loudness with an onset ramp of 50 ms or more, and preferably 100 to 300 ms for the softest tier, should be far from startle-eliciting conditions. The data above suggest longer rise times keep reducing startle.
- Avoid white or broadband noise bursts and instant (0 ms) onsets, which also cause audible clicks in Web Audio. Use pure or softly harmonic tones.

### Gaps
- I did not verify the exact rise-time values in the Blumenthal 2005 guidelines (full text not accessed).
- I found no human study giving a dB threshold for startle from tonal (non-noise) sounds at everyday listening levels.

## A2. Auditory warning design: urgency versus annoyance, earcons versus speech, and escalation and repetition

### Takeaway
Perceived urgency is predictably controlled by fundamental frequency, harmonic content, amplitude envelope, and pulse speed and repetition (Edworthy et al. 1991). For a gentle cue, set these toward the "low urgency" end. Patterson's guidelines recommend pulses shaped with onset and offset ramps, played at a moderate level above the background rather than at maximum level.

### Cited Findings
- Edworthy, Loxley & Dennis (1991), "Improving auditory warning design: Relationship between warning sound parameters and perceived urgency," *Human Factors* 33(2), 205-231. Fundamental frequency, harmonic series, amplitude envelope shape and delayed harmonics "all have clear and consistent effects on perceived urgency," and an urgency ranking predicted from these parameters correlated highly with listeners' actual ratings. — [Plymouth research portal](https://researchportal.plymouth.ac.uk/en/publications/improving-auditory-warning-design-relationship-between-warning-so/)
- Hellier, Edworthy & Dennis (1993), "Improving auditory warning design: Quantifying and predicting the effects of different warning parameters on perceived urgency," *Human Factors* 35(4), 693-706, DOI 10.1177/001872089303500408. Even when parameters are equalized psychophysically, some contribute more to urgency than others. The search tool flagged minor citation-detail discrepancies, so verify via the DOI. — [Plymouth research portal](https://researchportal.plymouth.ac.uk/en/publications/improving-auditory-warning-design-quantifying-and-predicting-the-/)
- Patterson, R. D. (1982), *Guidelines for auditory warning systems on civil aircraft*, CAA Paper 82017, UK Civil Aviation Authority (NTIS PB83248625). Warning components should be about 15 to 25 dB above the masked threshold set by background noise, not at maximum level. Source: secondary citation in a later Patterson paper (OCR read "2SdB", interpreted as 25 dB). The guidelines contain sections on rise and fall times and onset and offset form, but I could not fetch their exact millisecond values. — [Cambridge PDN copy](https://www.pdn.cam.ac.uk/system/files/documents/AuditoryWarningSystems_CAA82017.pdf); [CAA copy](https://www.caa.co.uk/Documents/Download/10717/96a1f546-c431-426f-9574-0495147cf0ea/19); [IOA Patterson guidelines PDF](https://www.ioa.org.uk/system/files/publications/RD%20PATTERSON%20GUIDELINES%20FOR%20THE%20DESIGN%20OF%20AUDITORY%20WARNING%20SOUNDS.pdf)
- Unverified (from memory; the primary was not fetchable): Patterson's guidelines are widely summarised as recommending pulse onset and offset ramps of about 20 to 30 ms and a pulse duration of about 100 to 150 ms. This was **not confirmed** here. Treat it as a lead to check in section 2 of CAA 82017.

### Inferences
- Low-urgency settings, based on the direction of the effects in Edworthy et al. 1991: a lower fundamental frequency (about 300 to 600 Hz rather than 1 to 3 kHz), few or soft harmonics (sine or triangle wave), a slow, falling or "rounded" envelope, slow or no repetition, and a falling pitch contour (two notes, high then low). Each of these lowers perceived urgency. These are directional inferences; the paper does not give exact Hz values for "gentle."
- Earcon versus speech: a short earcon (under 1 s) is less intrusive and language-free. Speech synthesis (e.g., "Hey, ready to jump back in?") carries meaning but takes longer and may be more intrusive. Offer it as an opt-in second tier. I found no head-to-head study for study-focus prompts (gap).
- Alarm fatigue and habituation: use few cues, spaced widely, with escalation capped at a mild level. Startle and orienting responses habituate with repetition (general startle literature), so a constantly repeating cue loses effect and adds annoyance.

### Gaps
- I did not fetch a primary source on alarm fatigue or habituation rates for repeated non-critical notification sounds. Clinical alarm-fatigue literature exists but was not reviewed.
- I found no study comparing earcons with TTS for refocusing students.

## A3. Sound sensitivity in ADHD and autism, and WCAG 2.2 SC 1.4.2

### Takeaway
Decreased sound tolerance (hyperacusis) is common in autism (roughly 27 to 41 percent, depending on the method) and is poorly studied but reported in ADHD. Audio must be optional, quiet by default, adjustable, and never long or looping. WCAG SC 1.4.2 requires a pause or stop control or independent volume control for any audio that plays automatically for more than 3 seconds.

### Cited Findings
- A 2021 meta-analysis (Williams et al.) estimated hyperacusis prevalence in autism at 41.42 percent when measured by interview or questionnaire and 27.3 percent with observational or objective measures. A 2026 narrative review gives 38 to 45 percent for decreased sound tolerance in autism and lists ADHD as a comorbidity. These figures come from a search summary of the review sources; verify the original (Williams, Suzman & Woynaroski 2021, *Ear and Hearing*) before quoting. — [ENT & Audiology News: Hyperacusis and autism](https://entandaudiologynews.com/features/audiology-features/post/hyperacusis-and-autism-spectrum-disorder); [PMC review](https://pmc.ncbi.nlm.nih.gov/articles/PMC7855558)
- Terminology overlaps: hyperacusis, misophonia, phonophobia, noxacusis and auditory hypersensitivity all describe forms of sound intolerance. — [ENT & Audiology News](https://entandaudiologynews.com/media/37240/entja24-danesh-final.pdf)
- Hyperacusis in ADHD is under-studied. A preliminary study compared 30 normal-hearing children with ADHD and 30 matched controls ("Hyperacusis in Children with Attention Deficit Hyperactivity Disorder: A Preliminary Study," *IJERPH* 2020, 17(9), 3045). I did not see its results. — [MDPI](https://mdpi.com/1660-4601/17/9/3045)
- WCAG SC 1.4.2 Audio Control (Level A, the same in WCAG 2.0, 2.1 and 2.2): "If any audio on a Web page plays automatically for more than 3 seconds, either a mechanism is available to pause or stop the audio, or a mechanism is available to control audio volume independently from the overall system volume level." Sufficient techniques include G60 (sound turns off within 3 s), G170 (a control near the start of the page) and G171 (sound plays only on user request). Looping audio counts toward the 3 s total. — [W3C Understanding 1.4.2 (WCAG 2.1)](https://www.w3.org/WAI/WCAG21/Understanding/audio-control.html); [Deque axe rule](https://dequeuniversity.com/rules/axe/4.8/no-autoplay-audio)

### Inferences
- Design cues lasting well under 3 s each, and also provide an in-app mute and volume slider independent of system volume. This satisfies 1.4.2 two ways.
- Offer a "visual only" mode, a "gentle chime" mode and an optional "voice" mode. Default to visual or very quiet audio. Avoid high frequencies (above about 2 to 3 kHz), sharp transients, buzzy square or sawtooth waves, and repetitive clicks or mouth-like sounds (common misophonia triggers; this last point is general clinical knowledge, not verified here).

### Gaps
- No ADHD-specific prevalence figure for sound sensitivity was found.
- I found no evidence-based "safe" frequency or level for hyperacusic users. Rely on user control.

## A4. Evidence that auditory or tactile prompts help on-task behaviour

### Takeaway
Periodic prompts that trigger self-monitoring ("Am I on task?") raised on-task behaviour in small single-case studies of students with ADHD or attention problems, including high-school students. The evidence base is small, mostly uses tactile (vibrating) prompts, and lacks randomized trials.

### Cited Findings
- Amato-Zech, Hoff & Doepke (2006), "Increasing on-task behavior in the classroom: Extension of self-monitoring strategies," *Psychology in the Schools* 43(2), 211-221. Three elementary students in special education used the MotivAider (a vibrating interval prompt) in an ABAB design. On-task behaviour rose from a mean of 55 percent to over 90 percent of observed intervals, and students and teachers rated the method highly acceptable. — [UTB catalogue record](https://vufind-test.katalog.k.utb.cz/SummonRecord/FETCH-LOGICAL-c4287-c19fb45625e5a546257c9895b4872a3c255de4ff8f4adbc7a153311d3269863c3)
- Morrison et al. (2014), *Journal of College Teaching & Learning*. High-school students with ADHD in a general-education biology class (multiple-baseline design) completed more independent work after tactile-cued self-monitoring, and students and co-teachers approved of the procedure. — [Clute Journals](https://clutejournals.com/index.php/TLC/article/view/8856)
- Unpublished ETSU theses (Almutairi 2017; Summey 2018) found that student-operated MotivAider use produced more time on task than teacher-operated use. — [ETSU 3343](https://dc.etsu.edu/etd/3343); [ETSU 3450](https://dc.etsu.edu/etd/3450)

### Inferences
- Present the cue as a prompt for the student's own self-check, not as a reprimand. Let students configure it themselves, which matches the finding that student control helped.
- These studies used fixed-interval prompts. NeuroFocus uses distraction-triggered prompts, which is an untested extension; frame it that way in the ISEF write-up.

### Gaps
- No RCTs. All tested prompts were tactile or fixed-interval, not webcam-triggered audio.

## B1. Webcam-measurable signs of drowsiness: thresholds, windows, reliability

### Takeaway
PERCLOS (the proportion of time the eyes are at least 80 percent closed, usually per minute) is the best-validated ocular drowsiness measure, from driving and lab research. Blink duration and slow eyelid reopening are also strong indicators (Schleicher et al. 2008). Webcam versions approximate these with the eye aspect ratio (EAR). Thresholds vary a lot between people, so per-user calibration is needed. Blink rate is an unreliable sign at a desk.

### Cited Findings
- FHWA Tech Brief FHWA-MCRT-98-006 (Oct 1998), "PERCLOS: A Valid Psychophysiological Measure of Alertness As Assessed by Psychomotor Vigilance." It found PERCLOS the most reliable and valid of the drowsiness measures tested. It defines PERCLOS as the proportion of time in a minute that the eyes are at least 80 percent closed, and tested the P70, P80 and EYEMEAS variants. — [ROSA P (USDOT)](https://rosap.ntl.bts.gov/view/dot/113); [archived PDF](https://webarchive.library.unt.edu/web/20130220154848/http://@fmcsa.dot.gov/documents/tb98-006.pdf)
- The underlying report is Dinges, Mallis, Maislin & Powell (1998), *Evaluation of techniques for ocular measurement as an index of fatigue and as the basis for alertness management*, NHTSA DOT HS 808 762. Note: "Dinges & Grace 1998" as a pairing appears to conflate this report with Grace's related work, so cite the tech brief and DOT HS 808 762. — [TRID](https://trid.trb.org/View/647942); [ROSA P](https://rosap.ntl.bts.gov/view/dot/2518/dot_2518_DS1.pdf)
- A 2023 review (Abe, "PERCLOS-based technologies for detecting drowsiness: current evidence and future directions," *SLEEP Advances*): PERCLOS definitions vary across studies, and simplified versions treat the eye as "closed" when EAR falls below a threshold. The review warns that PERCLOS alone may not be sensitive enough in real-world settings and is best combined with other measures. — [PMC10108649](https://pmc.ncbi.nlm.nih.gov/articles/PMC10108649/)
- Schleicher, Galley, Briest & Galley (2008), "Blinks and saccades as indicators of fatigue in sleepiness warnings: looking tired?", *Ergonomics* 51(7), 982-1010, DOI 10.1080/00140130701817062. Blink duration, delay of lid reopening, blink interval and standardised lid closure speed were the best oculomotor indicators of sleepiness, with large differences between individuals. A secondhand figure says overlong blinks averaged about 269 ms versus about 190 to 204 ms otherwise; this is unverified. — [Ingenta](https://www.ingentaconnect.com/content/10.1080/00140130701817062)
- Soukupová & Čech (2016), "Real-Time Eye Blink Detection using Facial Landmarks," 21st Computer Vision Winter Workshop. EAR is roughly constant while the eye is open and falls toward zero during a blink. The paper uses an EAR threshold of 0.2 as a baseline, with an SVM over EAR sequences as its main method. — [CVWW 2016 paper](https://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf)
- Fixed EAR and MAR (mouth aspect ratio) thresholds often fail to generalise across individuals. A 2026 arXiv preprint reports that personalised thresholds improve accuracy by about 2 to 3 percent. One webcam system counts a yawn when MAR stays high for more than 15 consecutive frames (to exclude speech). — [PeerJ CS 2022 adjusted EAR](https://peerj.com/articles/cs-943); [arXiv 2604.22479](https://arxiv.org/pdf/2604.22479)
- Blink rate on screens is contested. Earlier studies (e.g., Patel et al. 1991, *Optom Vis Sci*; Tsubota & Nakamori 1993) reported lower blink rates during VDU work. A 2014 controlled study (*Optom Vis Sci*) found no difference between screen and hard copy (14.9 vs 13.6 blinks/min, p = 0.58) but more incomplete blinks on screens. — [PubMed 24413278](https://pubmed.ncbi.nlm.nih.gov/24413278/); [PubMed 1766652](https://pubmed.ncbi.nlm.nih.gov/1766652/)

### Inferences
- Do not use low blink rate as a fatigue sign. Concentration and screen reading change it, so it would cause false positives in exactly the focused state the app wants to protect. Prefer long blink duration, PERCLOS and yawns.
- Desk-specific false positives: looking down at notes, a keyboard or a phone lowers EAR without the eyes closing. Gate eye-closure measures on head pitch (exclude frames with large downward pitch) or treat them as "looking away" rather than "eyes closed." Glasses, lighting, camera angle and eye shape all shift EAR, so calibrate per user.
- Talking, laughing and eating raise MAR. Require a sustained wide-open mouth (yawns typically last several seconds) rather than brief peaks.

### Gaps
- I found no validated PERCLOS cut-off for "tired" in desk or study settings; the driving thresholds may not transfer. No validated webcam yawn or head-nod thresholds were found in primary sources.
- MediaPipe-specific EAR baselines were not researched.

## B2. Time-on-task, vigilance decrement, break timing and break-prompt wording

### Takeaway
Sustained attention is effortful and declines with time on task (Warm et al. 2008). Micro-breaks of 10 minutes or less give small but reliable boosts to vigour and reductions in fatigue (Albulescu et al. 2022). In students, scheduled breaks (e.g., 24 min of work plus 6 min of break) improved mood and efficiency compared with self-chosen breaks (Biwer et al. 2023).

### Cited Findings
- Warm, Parasuraman & Matthews (2008), "Vigilance requires hard mental work and is stressful," *Human Factors* 50(3), 433-441, DOI 10.1518/001872008X312152. Behavioural, neural (transcranial Doppler) and subjective evidence shows vigilance is demanding and stressful, and the performance decrement is linked to resource depletion. — [Crossref](https://api.crossref.org/works/10.1518%2F001872008X312152)
- Albulescu, Macsinga, Rusu, Sulea, Bodnaru & Tulbure (2022), "'Give me a break!' A systematic review and meta-analysis on the efficacy of micro-breaks for increasing well-being and performance," *PLOS ONE* 17(8): e0272460, DOI 10.1371/journal.pone.0272460. 22 samples, N = 2335. Micro-breaks (10 minutes or less) increased vigour (d = 0.36) and reduced fatigue (d = 0.35). The performance effect overall was not significant (d = 0.16, p = .116) and was significant only for less demanding tasks. Longer breaks gave larger performance gains, and highly depleting tasks may need breaks longer than 10 minutes. — [PMC9432722](https://pmc.ncbi.nlm.nih.gov/articles/PMC9432722/)
- Biwer, de Bruin & Persoon (2023), "Understanding effort regulation: Comparing 'Pomodoro' breaks and self-regulated breaks," *British Journal of Educational Psychology* 93(S2), 353-367. In real study sessions, 6 min of break after every 24 min (n = 25) and 3 min after every 12 min (n = 27) were compared with self-regulated breaks (n = 35). Self-regulators took longer sessions and longer breaks. Systematic breaks gave mood benefits and similar task completion in less time. Secondary sources disagree on the effects on concentration and motivation, so check the original. — [PubMed 36859717](https://pubmed.ncbi.nlm.nih.gov/36859717/)
- Smits, Wenzel & de Bruin (2025), *Behavioral Sciences* 15(7): 861. Flowtime breaks led to a slower increase in fatigue. A Pomodoro-type condition showed a faster increase in fatigue than self-regulated breaks. This complicates a simple "Pomodoro is best" message. — [PMC12292963](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/)

### Inferences
- Combine a soft time-based suggestion (about every 25 to 30 min of continuous focus) with a fatigue-sign-based suggestion. Recommend a 3 to 6 min micro-break, and a longer break (over 10 min) after about 90 to 120 min of work. The 90 to 120 min figure is an inference from the meta-regression's direction, not a cited value.
- Wording: autonomy-supportive, non-judgemental and optional, for example "You've been working for 30 minutes. A short break might help you feel fresher. Take 5 minutes?" with buttons [Take a break] [Not now] [Snooze 10 min]. Avoid "You are tired" or "You lost focus."

### Gaps
- I found no primary study on the wording of break prompts for students with ADHD. The wording advice comes from general autonomy-support principles and was not verified here.

## B3. Ethics: suggest, don't diagnose; user control

### Takeaway
Ocular measures differ greatly between individuals (Schleicher et al. 2008; Abe 2023), and validation comes from driving and lab tasks. Any output should therefore be framed as "signs you might be tired," never as a measurement or diagnosis of fatigue, attention problems or ADHD.

### Cited Findings
- PERCLOS alone may not be sensitive enough in real-world settings, and definitions vary. — [Abe 2023, PMC10108649](https://pmc.ncbi.nlm.nih.gov/articles/PMC10108649/)
- There are large inter-individual differences in oculomotor fatigue indicators. — [Schleicher et al. 2008](https://www.ingentaconnect.com/content/10.1080/00140130701817062)
- Fixed thresholds generalise poorly; personalisation helps. — [arXiv 2604.22479](https://arxiv.org/pdf/2604.22479)

### Inferences
- Required controls: opt-in camera; all processing on the device (no video leaves the browser); visible "camera on" status; a one-click pause; adjustable sensitivity; and a way to dismiss or snooze any prompt. Show the reason for a prompt ("your eyes were closed often in the last minute") so users can judge it. Log nothing identifiable by default.
- Never use clinical terms (ADHD, disorder, symptom) in user-facing text.

### Gaps
- No formal ethics guideline specific to webcam attention tools for minors was reviewed. ISEF human-participant rules (IRB and informed consent for minors) apply if the project tests on people; these were not researched here.

---

### Implementable parameter recommendations (engineering defaults; tune with users)
These are reasoned defaults derived from the findings above. Items marked [cited] map directly to a source; everything else is an inference to validate in user testing.

**Audio cue (Web Audio API)**
- Waveform: `sine` (optionally a quiet 2nd harmonic at -12 dB). No noise, square or sawtooth waves (fewer harmonics means lower urgency [Edworthy 1991, direction]).
- Pitch: tier 1 is a two-note falling chime, about 660 Hz then 523 Hz (E5 to C5), staying in 300 to 1000 Hz.
- Envelope: attack 80 to 150 ms with `linearRampToValueAtTime` (or `setTargetAtTime`, timeConstant about 0.04 s), never 0 ms. Release or exponential decay 300 to 600 ms. Note length about 250 to 400 ms; whole cue under 1.2 s, well below the 3 s WCAG limit [cited]. (50 ms or more is less startling [Patterson, secondhand]. Startle falls as rise time increases [rise-time literature].)
- Level: default gain about 0.05 to 0.15 (about -26 to -16 dBFS peak) via a master `GainNode`; an in-app volume slider and mute independent of system volume [WCAG 1.4.2]. Never auto-increase the volume above the user's setting.
- Escalation (maximum 3 tiers, then stop): tier 0 is visual only (a soft screen-edge glow) after about 20 to 30 s of detected distraction; tier 1 is the soft chime if distraction continues about 30 s more; tier 2 (opt-in) is a quiet TTS line (`speechSynthesis`, rate about 0.9, pitch about 1.0, volume about 0.6) after about 60 s more. Escalate by meaning (visual, then chime, then words), not by loudness or speed.
- Cooldown: at least 2 to 3 min between audio cues; at most about 6 to 10 audio cues per hour. Back off further (double the cooldown) if the user dismisses 2 cues in a row. Respect "snooze 15 min" and "visual-only" modes.
- Default mode for first run: visual only, with audio opt-in during onboarding (sound-sensitive users [A3]).

**Fatigue detection (MediaPipe Face Mesh / Face Landmarker)**
- Calibration: 30 to 60 s at session start (eyes open, looking at screen) to get each user's open-eye EAR baseline. Closed threshold = baseline x about 0.5 to 0.6, or use the blendshape `eyeBlinkLeft/Right` > about 0.5 if using Face Landmarker. The fixed fallback is EAR < 0.2 [Soukupová & Čech 2016, cited].
- PERCLOS: fraction of frames that count as closed (about 80 percent closure, approximated by the closed threshold) over a rolling 60 s window [FHWA 1998 per-minute definition, cited]. Flag "possible tiredness" when PERCLOS stays above about 0.15 for 2 or more consecutive minutes. This cut-off is from driving-study practice and is uncertain at a desk; tune it.
- Long blinks: closure lasting 0.4 s or more but under 2 s counts as a long blink. Flag if 3 or more occur per minute, or if the median blink duration rises 30 percent or more above the user's own baseline [Schleicher 2008, direction; numbers are inference]. Closure of 2 s or more counts as a microsleep or eyes-closed event.
- Ignore blink rate as a fatigue sign [2014 screen versus paper study]. Exclude frames where head pitch is more than about 20 degrees downward (reading notes) from eye-closure statistics.
- Yawn: MAR above baseline x about 2 (or jawOpen blendshape > about 0.6) sustained for 1.5 s or more (more than 15 frames at about 10 fps or higher [cited system used >15 frames]). Flag at 2 or more yawns in 10 min.
- Head nod: downward pitch change of more than about 15 degrees within less than 1 s, followed by a recovery, while the eyes are closing. Count as supporting evidence only.
- Decision rule: suggest a break only when 2 or more independent signs agree within a 5 min window (e.g., PERCLOS plus yawns), OR after about 30 min of continuous work (a time-based nudge). Fatigue break cooldown: at least 15 min after any break prompt. A dismissal snoozes it for 20 min.
- Break prompt: suggest 5 min (range 3 to 10) [Albulescu 2022; Biwer 2023]. After about 90 or more min of total work, suggest a longer break of 10 to 15 min (inference).
- Copy: "Looks like you might be getting tired (more long blinks than usual). Want a 5-minute break?" Buttons: [Take a break] [Not now] [Snooze]. Never "You are tired," "fatigue detected," or any clinical wording.
