from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_CENTER
from figures import LOW

NAVY = colors.HexColor("#1f4e79")
RED = colors.HexColor("#c0392b")
LIGHT = colors.HexColor("#eaf1f8")
IMG = "img/"

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=NAVY, fontSize=22, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=RED, fontSize=14, spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10, leading=14)
SM = ParagraphStyle("SM", parent=B, fontSize=9, leading=12)
BUL = ParagraphStyle("BUL", parent=B, leftIndent=14, bulletIndent=2)
CELL = ParagraphStyle("CELL", parent=B, fontSize=9, leading=11)
CELLB = ParagraphStyle("CELLB", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)


def P(t, s=B):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, BUL, bulletText="•") for i in items]


def table(data, widths, header=True, zebra=True):
    rows = [[Paragraph(str(c), CELLB if (header and r == 0) else CELL) for c in row] for r, row in enumerate(data)]
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c7d9")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for r in range(1 if header else 0, len(rows)):
            if r % 2 == 0:
                st.append(("BACKGROUND", (0, r), (-1, r), LIGHT))
    t.setStyle(TableStyle(st))
    return t


# ---------------- exercise library ----------------
EX = {
    "chair_squat": ("Chair Squat", "Quads, glutes",
                    "Stand in front of a sturdy chair, feet shoulder-width. Push hips back and bend knees until you lightly touch the seat, then press through your heels to stand.",
                    "Chest up; knees track over toes; do not collapse onto the chair.",
                    "Use a higher seat or hold a counter.", "Pause 2 seconds on the seat; hover just above it."),
    "squat": ("Bodyweight Squat", "Quads, glutes, core",
              "Feet shoulder-width, toes slightly out. Sit hips back and down until thighs are about parallel, then drive up through your heels.",
              "Weight in heels and mid-foot; chest proud; knees in line with toes.",
              "Chair squat.", "Lower for 3 seconds, pause 1 second at the bottom, then stand."),
    "incline_pushup": ("Incline Push-Up", "Chest, shoulders, triceps",
                       "Hands on a sturdy counter or table slightly wider than shoulders. Body in one straight line. Lower your chest to the edge, then press away.",
                       "Squeeze glutes and abs; elbows about 45 degrees from the body.",
                       "Use a higher surface (wall or counter).", "Lower surface (stairs, sofa), then floor push-ups."),
    "pushup": ("Push-Up", "Chest, shoulders, triceps, core",
               "Hands under shoulders on the floor, body straight from head to heels. Lower until your chest is a fist from the floor, then press up.",
               "Do not let hips sag or pike; neck neutral.",
               "Incline push-up, or knees on the floor.", "3-second lowering; feet on a low step."),
    "bridge": ("Glute Bridge", "Glutes, hamstrings",
               "Lie on your back, knees bent, feet flat hip-width. Drive through heels to lift hips until shoulders, hips and knees line up. Squeeze, then lower.",
               "Ribs down; do not arch the lower back; squeeze at the top.",
               "Smaller range of motion.", "Hold 2 seconds at the top, or lift one foot (single-leg bridge)."),
    "birddog": ("Bird Dog", "Core, glutes, back",
                "On hands and knees. Reach one arm forward and the opposite leg back until both are level with your torso. Pause, return, switch sides.",
                "Keep hips square; move slowly; do not twist or arch.",
                "Lift only the leg or only the arm.", "Pause 3 seconds; touch elbow to knee under you between reps."),
    "deadbug": ("Dead Bug", "Deep core",
                "Lie on your back, arms to the ceiling, knees above hips. Slowly lower the opposite arm and leg toward the floor without letting your lower back lift. Return and switch.",
                "Press lower back gently into the floor; breathe out as you lower.",
                "Lower only the legs (one heel tap).", "Fully straighten the leg and arm; slow 3-second reps."),
    "plank": ("Plank", "Entire core, shoulders",
              "On forearms and knees (or toes). Elbows under shoulders, body in a straight line. Squeeze glutes and hold.",
              "Do not let the lower back sag; breathe steadily.",
              "Hands on a counter (incline plank) or knees down.", "Full plank on toes; lift one foot a few inches."),
    "lunge": ("Reverse Lunge", "Quads, glutes, balance",
              "Stand tall. Step one foot back and lower until both knees are near 90 degrees. Push through the front heel to return. Alternate legs.",
              "Torso upright; front knee over the ankle; light touch of the back knee at most.",
              "Hold a counter or chair for balance; shorter range.", "Slow 3-second lowering; add a knee-lift at the top."),
    "split": ("Split Squat", "Quads, glutes",
              "Take a long staggered stance, feet hip-width apart. Lower the back knee straight down toward the floor, then press up. Finish all reps, then switch legs.",
              "Weight mostly on the front leg; torso tall.",
              "Hold a chair or counter.", "Elevate the back foot on a couch or step (Bulgarian split squat)."),
    "superman": ("Superman", "Lower back, glutes, upper back",
                 "Lie face down, arms extended overhead. Lift arms, chest and legs a few inches, squeeze your back, hold 1-2 seconds, lower.",
                 "Look at the floor to keep your neck neutral; small, controlled lift.",
                 "Lift only arms or only legs.", "Hold 3 seconds; add a small flutter."),
    "hinge": ("Hip Hinge (Good Morning)", "Hamstrings, glutes, lower back",
              "Soft knees, hands on hips or across chest. Push hips straight back, torso tilts forward with a flat back until you feel a hamstring stretch, then drive hips forward.",
              "Spine long, hips go back (not a squat); stop before your back rounds.",
              "Smaller range; hands on a counter.", "Slow 3-second lowering; single-leg hinge with a light toe tap."),
    "climber": ("Mountain Climber", "Core, shoulders, conditioning",
                "From a high plank (hands under shoulders), drive one knee toward your chest, then switch. Start slow and controlled.",
                "Keep hips level; shoulders stacked over hands.",
                "Hands on a counter or stairs; step feet instead of driving.", "Faster pace; floor-level hands."),
    "tap": ("Plank Shoulder Tap", "Core, shoulders, stability",
            "High plank with feet wider than hips. Lift one hand and tap the opposite shoulder, then switch. Resist rotating your hips.",
            "Wider feet = more stable; squeeze glutes.",
            "Do it from your knees or with hands on a counter.", "Feet closer together; slow taps."),
    "march": ("High-Knee March", "Heart rate, hips, core",
              "Stand tall and march in place, driving knees up to hip height while swinging opposite arms. No jumping - this keeps joints happy.",
              "Tall posture; brisk pace; breathe rhythmically.",
              "Lower knee height.", "Faster pace; add overhead arm reaches."),
}

# --------------- workouts ----------------
WK = {
    "P1A": ("Workout A - Full Body", ["chair_squat", "incline_pushup", "bridge", "birddog", "march", "deadbug"]),
    "P1B": ("Workout B - Full Body", ["hinge", "incline_pushup", "lunge", "superman", "plank", "march"]),
    "P1C": ("Workout C - Full Body", ["chair_squat", "bridge", "lunge", "birddog", "deadbug", "plank"]),
    "P2A": ("Workout A - Lower + Core", ["squat", "bridge", "lunge", "hinge", "plank", "march"]),
    "P2B": ("Workout B - Upper + Core", ["incline_pushup", "superman", "birddog", "deadbug", "plank", "march"]),
    "P2C": ("Workout C - Full Body", ["squat", "incline_pushup", "split", "bridge", "climber", "deadbug"]),
    "P3A": ("Workout A - Lower Body", ["squat", "split", "bridge", "hinge", "march"]),
    "P3B": ("Workout B - Upper + Core", ["pushup", "superman", "plank", "tap", "deadbug"]),
    "P3C": ("Workout C - Full Body Burn", ["squat", "pushup", "climber", "lunge", "plank"]),
    "P3D": ("Workout D - Lower + Core", ["lunge", "hinge", "bridge", "birddog", "climber"]),
}
WK["P4A"], WK["P4B"], WK["P4C"], WK["P4D"] = (
    ("Workout A - Lower Body", WK["P3A"][1]), ("Workout B - Upper + Core", WK["P3B"][1]),
    ("Workout C - Full Body Burn", WK["P3C"][1]), ("Workout D - Lower + Core", WK["P3D"][1]))

PHASES = [
    dict(n=1, name="Foundation", weeks="Weeks 1-4", days=3, order=["P1A", "P1B", "P1C"],
         goal="Learn the movements, build the habit and tolerance. Slow, clean reps; easy-to-moderate effort (RPE 5-6 of 10).",
         timing=[("Weeks 1-2", "30 sec work / 30 sec rest", "3 rounds"), ("Weeks 3-4", "40 sec work / 20 sec rest", "3 rounds")],
         total="3 min warm-up + 18 min circuit + 3 min cool-down = about 24 min",
         schedule="Mon / Wed / Fri (or any 3 non-consecutive days). Walk 20-30 min on 1-2 other days.",
         progress="Use the easier option of any exercise you cannot hold form on. Optional: add a 20-minute easy walk on a non-workout day."),
    dict(n=2, name="Build", weeks="Weeks 5-8", days=3, order=["P2A", "P2B", "P2C"],
         goal="Add range and difficulty. Start feeling muscles work (RPE 6-7). Optional 4th day: 20-25 min brisk walk or Workout A repeated.",
         timing=[("Weeks 5-6", "40 sec work / 20 sec rest", "3 rounds"), ("Weeks 7-8", "45 sec work / 15 sec rest", "3 rounds")],
         total="3 min warm-up + 18 min circuit + 3 min cool-down = about 24 min",
         schedule="Mon / Wed / Fri plus optional Sat brisk walk or repeat of a favorite workout (4 sessions).",
         progress="Lower the incline for push-ups, move from chair to full bodyweight squats, and move from knee plank to full plank."),
    dict(n=3, name="Strengthen", weeks="Weeks 9-12", days=4, order=["P3A", "P3B", "P3C", "P3D"],
         goal="Four sessions per week with an upper/lower focus to build muscle and burn more calories (RPE 7-8).",
         timing=[("Weeks 9-10", "45 sec work / 15 sec rest", "4 rounds"), ("Weeks 11-12", "45 sec work / 15 sec rest", "4 rounds, use harder variations")],
         total="2 min warm-up + 20 min circuit + 2 min cool-down = about 24 min",
         schedule="Mon (A) / Tue (B) / Thu (C) / Sat (D). Never do A and D on back-to-back days.",
         progress="Slow the lowering phase to 3 seconds on every rep. Move to full push-ups when you can do 12 clean incline reps."),
    dict(n=4, name="Transform", weeks="Weeks 13-16", days=4, order=["P4A", "P4B", "P4C", "P4D"],
         goal="Peak intensity. Use your harder variations and tempo to keep progressing (RPE 8). Week 16 is a test week.",
         timing=[("Weeks 13-14", "50 sec work / 10 sec rest", "4 rounds"), ("Weeks 15-16", "50 sec work / 10 sec rest", "4 rounds, hardest variation you can do with clean form")],
         total="2 min warm-up + 20 min circuit + 2 min cool-down = about 24 min",
         schedule="Mon (A) / Tue (B) / Thu (C) / Sat (D).",
         progress="Test week (16): max clean push-ups, chair-free squats in 60 seconds, plank hold time. Compare with Week 1."),
]


def footer(c, d):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(letter[0] / 2, 0.45 * inch, f"16-Week Bodyweight Program   |   Page {d.page}")
    c.restoreState()


def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    c.setFillColor(RED)
    c.rect(0, 4.2 * inch, letter[0], 0.12 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 38)
    c.drawString(0.8 * inch, 7.2 * inch, "THE 16-WEEK")
    c.drawString(0.8 * inch, 6.5 * inch, "BODYWEIGHT")
    c.drawString(0.8 * inch, 5.8 * inch, "TRANSFORMATION")
    c.setFont("Helvetica", 15)
    c.drawString(0.8 * inch, 5.1 * inch, "Lose fat. Build muscle. 20-25 minutes, 3-4 days a week.")
    c.drawString(0.8 * inch, 3.6 * inch, "No gym. No equipment. Just a chair, a counter and a floor.")
    c.setFont("Helvetica", 11)
    c.drawString(0.8 * inch, 1.0 * inch, "Beginner program - 4 phases - 15 illustrated exercises - progress tracker")
    c.restoreState()


def ex_block(key):
    n, m, how, cues, easy, hard = EX[key]
    inner = [P(f"<b>{n}</b>  <font color='#666666'>- {m}</font>", ParagraphStyle("t", parent=B, fontSize=12, textColor=NAVY)),
             Image(IMG + key + ".png", width=5.6 * inch, height=5.6 * inch * (1.5 if key in LOW else 2.15) / 7.2),
             P(f"<b>How:</b> {how}", SM), P(f"<b>Cues:</b> {cues}", SM),
             P(f"<b>Easier:</b> {easy} &nbsp; <b>Harder:</b> {hard}", SM), Spacer(1, 10)]
    return KeepTogether(inner)


def workout_table(code, ph):
    title, ex = WK[code]
    data = [["#", "Exercise", "Focus", "Notes"]]
    for i, k in enumerate(ex, 1):
        data.append([i, EX[k][0], EX[k][1], EX[k][4].split(";")[0] if ph["n"] <= 2 else EX[k][5]])
    return [KeepTogether([P(f"<b>{title}</b>", ParagraphStyle("w", parent=B, fontSize=11, textColor=NAVY, spaceBefore=4, spaceAfter=2)),
                          table(data, [0.3 * inch, 1.7 * inch, 1.9 * inch, 3.1 * inch])])]


def build(path):
    doc = BaseDocTemplate(path, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                          topMargin=0.7 * inch, bottomMargin=0.8 * inch, title="16-Week Bodyweight Transformation",
                          author="Personal Program")
    fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate("cover", [Frame(0, 0, 1, 1)], onPage=cover),
                          PageTemplate("body", [fr], onPage=footer)])
    from reportlab.platypus import NextPageTemplate
    s = [NextPageTemplate("body"), PageBreak()]

    s += [P("Welcome", H1),
          P("This program is built for a 40-year-old beginner at about 255 lb who wants to lose body fat and add some "
            "muscle without a gym. Every session is 20-25 minutes, three to four days a week, over 16 weeks "
            "(about 4 months). All movements are low-impact (no jumping), so they are friendly to your joints "
            "while still raising your heart rate and building strength."),
          P("How it works", H2),
          *bullets(["<b>Circuit format:</b> you do each exercise for a set number of seconds, rest briefly, move to the next, and repeat for 3-4 rounds.",
                    "<b>Four phases</b> of four weeks. Each phase makes the work a little harder so your body keeps adapting.",
                    "<b>Quality over speed:</b> the first goal is clean form. If form breaks down, use the Easier option.",
                    "<b>Equipment:</b> a sturdy chair, a sturdy kitchen counter or table, a yoga mat or towel, a timer (phone), and water."]),
          P("The 16-week roadmap", H2),
          table([["Phase", "Weeks", "Days / week", "Focus", "Session"],
                 ["1 Foundation", "1-4", "3", "Learn form, build habit", "~24 min"],
                 ["2 Build", "5-8", "3 (+ optional walk)", "More range, harder variations", "~24 min"],
                 ["3 Strengthen", "9-12", "4", "Upper / lower split, muscle building", "~24 min"],
                 ["4 Transform", "13-16", "4", "Peak intensity, test week", "~24 min"]],
                [1.2 * inch, 0.8 * inch, 1.5 * inch, 2.4 * inch, 1.1 * inch]),
          P("Safety first", H2),
          *bullets(["Because you are new to exercise and over 40, get a quick check-up from your doctor before starting.",
                    "Stop any exercise that causes sharp pain, dizziness or chest discomfort. Muscle burn and fatigue are normal; joint pain is not.",
                    "Effort scale (RPE): 1 = very easy, 10 = maximum. Work at 5-6 early on and build gradually. You should be able to say a short sentence.",
                    "Take at least one rest day between sessions in Phases 1-2. Sore muscles in the first 2 weeks are normal."]),
          PageBreak()]

    s += [P("Every Session: Warm-Up and Cool-Down", H1),
          P("Warm-Up (2-3 minutes)", H2),
          table([["Move", "Time"],
                 ["March in place with arm swings", "45 sec"], ["Arm circles (forward and back)", "30 sec"],
                 ["Hip circles and gentle torso twists", "30 sec"], ["Bodyweight half squats (slow)", "30 sec"],
                 ["Cat-cow on hands and knees", "30 sec"]], [4.5 * inch, 1.5 * inch]),
          P("Cool-Down (2-3 minutes)", H2),
          table([["Stretch", "Time"],
                 ["Standing quad stretch (each leg)", "20 sec"], ["Seated or standing hamstring stretch", "30 sec"],
                 ["Doorway chest stretch", "30 sec"], ["Child's pose", "40 sec"], ["Slow deep breaths", "30 sec"]],
                [4.5 * inch, 1.5 * inch]),
          P("Fat Loss and Muscle: The Non-Workout 80%", H2),
          *bullets(["<b>Calories:</b> aim for a modest deficit of about 300-500 calories a day below maintenance. A realistic loss is 1-2 lb per week; you may lose 15-30 lb over 16 weeks.",
                    "<b>Protein:</b> about 0.7-1 g per lb of your goal body weight (roughly 140-180 g a day) preserves and builds muscle. Include protein at every meal.",
                    "<b>Food basics:</b> mostly whole foods, vegetables at two meals, limit sugary drinks and alcohol, and drink plenty of water.",
                    "<b>Steps:</b> build toward 7,000-10,000 steps per day. Walking is the easiest fat-loss tool.",
                    "<b>Sleep:</b> 7-9 hours. Poor sleep increases hunger and slows recovery.",
                    "<b>Track:</b> weigh yourself 1-2 times a week at the same time, take waist/hip/chest measurements every 4 weeks, and snap photos monthly. The scale will fluctuate; the trend matters."]),
          PageBreak()]

    s += [P("Exercise Library", H1),
          P("Each illustration shows the start and finish positions. The dark red line is the torso, blue is the "
            "working limb, and light blue is the opposite limb.", B), Spacer(1, 8)]
    for k in EX:
        s.append(ex_block(k))
    s.append(PageBreak())

    for ph in PHASES:
        s += [P(f"Phase {ph['n']}: {ph['name']} ({ph['weeks']})", H1), P(ph["goal"]),
              P("Format", H2),
              table([["When", "Timing", "Rounds"]] + [list(t) for t in ph["timing"]], [1.4 * inch, 3.0 * inch, 2.6 * inch]),
              Spacer(1, 4), P(f"<b>Session length:</b> {ph['total']}", SM), P(f"<b>Schedule:</b> {ph['schedule']}", SM),
              P(f"<b>Progression:</b> {ph['progress']}", SM)]
        for code in ph["order"]:
            s += workout_table(code, ph)
        if ph["n"] >= 3:
            s += [Spacer(1, 6), P("Phase 4 notes: use the Harder column as your target. Keep each rep controlled." if ph["n"] == 4 else
                                  "Use the Harder column as your goal for each exercise once the standard version feels comfortable.", SM)]
        s.append(PageBreak())

    wk = [["Week", "Phase", "Sessions", "Timing", "Rounds"]]
    for ph in PHASES:
        a, b = [int(x) for x in ph["weeks"].replace("Weeks ", "").split("-")]
        for w in range(a, b + 1):
            idx = 0 if w <= a + 1 else 1
            wk.append([w, ph["name"], ph["days"], ph["timing"][idx][1], ph["timing"][idx][2].split(",")[0]])
    s += [P("Week-by-Week Overview", H1), table(wk, [0.7 * inch, 1.3 * inch, 0.9 * inch, 2.7 * inch, 1.4 * inch]), PageBreak()]

    log = [["Week", "Date", "Weight (lb)", "Waist (in)", "Sessions done", "Energy (1-10)", "Notes"]]
    log += [[w, "", "", "", "", "", ""] for w in range(1, 17)]
    t = table(log, [0.5 * inch, 0.8 * inch, 0.9 * inch, 0.8 * inch, 1.0 * inch, 1.0 * inch, 2.0 * inch])
    t._argH = [None] + [0.28 * inch] * 16
    s += [P("Progress Tracker", H1), t, Spacer(1, 10),
          P("<b>Test week benchmarks (Week 1 vs Week 16)</b>", B),
          table([["Test", "Week 1", "Week 16"], ["Max clean push-ups (incline or floor)", "", ""],
                 ["Bodyweight squats in 60 seconds", "", ""], ["Plank hold (seconds)", "", ""],
                 ["Waist / hips / chest (in)", "", ""]], [3.6 * inch, 1.7 * inch, 1.7 * inch]),
          Spacer(1, 12),
          P("<i>This program is general fitness guidance, not medical advice. Consult your physician before beginning any exercise program.</i>", SM)]

    doc.build(s)


if __name__ == "__main__":
    build("./Bodyweight_Program_16_Weeks.pdf")
