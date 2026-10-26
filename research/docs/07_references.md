# 7. References

**Verify every reference yourself before citing it.** These were compiled
from memory by an AI assistant while writing the code. Look each one up
(Google Scholar, arXiv, the publisher's site), confirm authors, year, title
and page numbers, and read at least the abstract and relevant section
before you cite it. Delete any you cannot verify. Add sources you find
yourself, especially on webcam-based attention estimation and gaze/head-pose
accuracy.

## Methods used in the engine

1. Soukupová, T., & Čech, J. (2016). Real-time eye blink detection using
   facial landmarks. *21st Computer Vision Winter Workshop (CVWW)*.
   Used for: eye aspect ratio (EAR) definition.
2. Kartynnik, Y., Ablavatski, A., Grishchenko, I., & Grundmann, M. (2019).
   Real-time facial surface geometry from monocular video on mobile GPUs.
   *arXiv:1907.06724*. Used for: the face-mesh model behind MediaPipe Face
   Landmarker.
3. Ablavatski, A., Vakunov, A., Grishchenko, I., Raveendran, K., &
   Zhdanovich, M. (2020). Real-time pupil tracking from monocular video for
   digital puppetry. *arXiv:2006.11341*. Used for: iris landmarks.
4. Lugaresi, C., et al. (2019). MediaPipe: A framework for building
   perception pipelines. *arXiv:1906.08172*. Used for: the MediaPipe framework.
5. Google. MediaPipe Face Landmarker documentation and model card (online;
   cite with the access date). Used for: model inputs/outputs, the facial
   transformation matrix, and the model's own evaluation and fairness notes.
6. Dinges, D. F., & Grace, R. (1998). PERCLOS: A valid psychophysiological
   measure of alertness as assessed by psychomotor vigilance. *Federal
   Highway Administration Tech Brief FHWA-MCRT-98-006*. Background for
   eye-closure-based drowsiness measures.

## Evaluation and statistics

7. Sokolova, M., & Lapalme, G. (2009). A systematic analysis of performance
   measures for classification tasks. *Information Processing & Management,
   45*(4), 427-437. Used for: precision, recall, F1 definitions.
8. Powers, D. M. W. (2011). Evaluation: From precision, recall and F-measure
   to ROC, informedness, markedness and correlation. *Journal of Machine
   Learning Technologies, 2*(1), 37-63. Used for: limitations of accuracy/F1.
9. Cohen, J. (1960). A coefficient of agreement for nominal scales.
   *Educational and Psychological Measurement, 20*(1), 37-46. Used for:
   Cohen's kappa.
10. Wilcoxon, F. (1945). Individual comparisons by ranking methods.
    *Biometrics Bulletin, 1*(6), 80-83. Used for: signed-rank test.
11. Holm, S. (1979). A simple sequentially rejective multiple test
    procedure. *Scandinavian Journal of Statistics, 6*(2), 65-70. Used for:
    multiple-comparison correction.
12. Friedman, M. (1937). The use of ranks to avoid the assumption of
    normality implicit in the analysis of variance. *Journal of the American
    Statistical Association, 32*(200), 675-701. Used for: noise-level effect.
13. Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the
    Bootstrap*. Chapman & Hall/CRC. Used for: bootstrap confidence intervals.
14. Kerby, D. S. (2014). The simple difference formula: An approach to
    teaching nonparametric correlation. *Comprehensive Psychology, 3*.
    Used for: matched-pairs rank-biserial correlation.

## Rules

15. Society for Science. *International Rules for Precollege Science
    Research: Guidelines for Science and Engineering Fairs* (use the edition
    for your competition year). Used for: human-participant rules, project
    categories, required forms.

## Software

16. Python, NumPy, SciPy, Matplotlib, Flask: cite the versions recorded in
    each run's `manifest.json`.
17. MediaPipe Tasks Vision 0.10.14 (npm `@mediapipe/tasks-vision`), Apache-2.0.

## Gaps to fill with your own literature search

* Prior webcam- or eye-tracking-based attention/engagement detection in
  learning settings, and how it was validated.
* Accuracy of webcam head-pose and gaze estimation versus lab eye trackers.
* Mind-wandering research showing that gaze direction is an imperfect
  proxy for attention (useful for your limitations section).
