"""Ground-truth vocabulary for the virtual-student experiment.

These definitions belong to the RESEARCH DESIGN, not to the engine. They are
written independently of neurofocus_engine (which must never import this
file) and fixed before any experiment run.

Operational definition of "distracted" used in this study:
  The virtual student is executing an off-task behavior (looking away from the
  screen for >= 3 s, using a phone, eyes closed for >= 2 s, or away from the
  desk). Brief glances (< 1.5 s) and looking down to write notes are treated as
  ON-TASK, because they are normal parts of studying.
"""

# Behaviors the simulator can perform.
ON_TASK = "on_task"          # reading / looking at screen
GLANCE = "glance"            # brief look aside, 0.3-1.5 s   (on-task)
NOTES = "notes"              # looking down to write notes  (on-task, known confound)
AWAY = "away"                # sustained look away          (distracted)
PHONE = "phone"              # using a phone                (distracted)
DROWSY = "drowsy"            # eyes closed                  (distracted)
LEFT_DESK = "left_desk"      # not in front of camera       (distracted)

BEHAVIORS = (ON_TASK, GLANCE, NOTES, AWAY, PHONE, DROWSY, LEFT_DESK)
ON_TASK_BEHAVIORS = (ON_TASK, GLANCE, NOTES)

# Expected attention-state label for each behavior. Strings match the engine's
# output vocabulary so predictions and truth can be compared, but they are
# declared here independently.
EXPECTED_STATE = {
    ON_TASK: "FOCUSED",
    GLANCE: "FOCUSED",
    NOTES: "FOCUSED",
    AWAY: "LOOKING_AWAY",
    PHONE: "LOOKING_DOWN",
    DROWSY: "EYES_CLOSED",
    LEFT_DESK: "ABSENT",
}
STATE_ORDER = ("FOCUSED", "LOOKING_AWAY", "LOOKING_DOWN", "EYES_CLOSED", "ABSENT")
