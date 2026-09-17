
import os
import json
import re
import time
import random
import html
import requests
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageDraw, ImageFont

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
BUFFER_KEY = os.environ["BUFFER_API_KEY"]

DRAFT_COUNT = 4
W, H = 1080, 1350
MARGIN = 90

PALETTE = [
    ("#111111", "#FFE500", "#FFE500"),
    ("#22C4DD", "#0D0D0D", "#0D0D0D"),
    ("#FFFFFF", "#0D0D0D", "#14D6CE"),
    ("#FFE500", "#0D0D0D", "#0D0D0D"),
    ("#FF382D", "#FFFFFF", "#FFFFFF"),
    ("#111111", "#14D6CE", "#14D6CE"),
]

ROOT = Path(__file__).parent
FONT_DIR = ROOT / ".fonts"
FONT_DIR.mkdir(exist_ok=True)
ANTON = FONT_DIR / "Anton-Regular.ttf"
INTER = FONT_DIR / "Inter.ttf"

ANTON_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf"
INTER_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"

STYLE = """
You write LinkedIn posts for Matvei Shakhurdin.

VOICE AND CAPITALIZATION:
- English
- lowercase by default for ordinary words, including "i"
- BUT always use normal capitalization for anything that should be capitalized in English:
  people's names, surnames, cities, countries, companies, products, frameworks,
  official names, acronyms, days/months when used, and branded spellings
- examples that MUST keep their normal capitalization when relevant:
  Matvei Shakhurdin, LinkedIn, OpenAI, Google, GitHub, Jira, Scrum, Agile, Kanban,
  Toyota, Telegram, Tbilisi, AI, PM, API, SQL, CRM, QA
- do not lowercase a proper noun just to preserve the visual style
- do not capitalize an ordinary sentence merely because it starts a paragraph
- no period at the end of paragraphs
- never use an em dash —
- use an en dash – when a dash is actually needed
- natural spoken rhythm, not telegram-style fragments
- occasional emojis are fine as punchlines, not decoration
- dry humor, absurd comparisons and slightly unhinged metaphors are welcome
- smart and practical underneath the joke
- no LinkedIn guru voice
- no corporate bullshit
- no AI slop
- no fake vulnerability, fake experience, fake metrics, fake quotes
- no "in today's fast-paced world", "game changer", "unlock", "leverage"
- no "not only ... but also"
- no hashtags
- do not end with a generic engagement question

The energy can resemble:
"i think a project manager is basically a parent to their projects 👨‍🍼"
"i would like to introduce a new management methodology: LOW CORTISOL MANAGEMENT™ 🧚"
"every project plan should have a backflip built into it 🤸"

The post must contain a real PM idea. Humor is packaging, not the substance.
"""

PROFILE = """
Matvei Shakhurdin is a project / delivery manager with 4+ years of experience.

POSITIONING GOAL:
Every post must primarily demonstrate how Matvei thinks and works as an experienced PM / delivery manager.
The feed is not a random PM magazine and not a trend feed.
It is a public portfolio of judgment.

A strong hiring manager should repeatedly see evidence of:
- turning ambiguity into scope, owners, dependencies and dates
- running several streams at once without losing the economics
- making trade-offs under limited time, people and budget
- managing scope change commercially, not emotionally
- coordinating design, engineering, marketing, legal, finance and vendors
- understanding enough engineering to challenge estimates and discuss scope directly
- understanding design production deeply enough to sequence 2D, identity, UI, motion and 3D work
- managing risks, dependencies, approvals, QA and release discipline
- building lightweight processes and automations instead of adding ceremony
- communicating constraints clearly and de-escalating conflict
- mentoring and helping teams become more autonomous

The post does NOT need to sound like a CV bullet.
It should turn real experience into an observation, argument, useful model, anti-pattern or story.
But its core thesis must be traceable to Matvei's verified experience below.
"""

EXPERIENCE_FACTS = """
VERIFIED MATVEI EXPERIENCE — THE ONLY PERSONAL EXPERIENCE FACTS YOU MAY STATE AS FACT:

A1 — ambiguity into delivery plan
At Whale Studio, Matvei turned one-line business requests into workable delivery plans by running discovery, collecting estimates from discipline leads, building timelines with named risk points and defining decision ownership.

A2 — parallel delivery
He ran 6–7 concurrent projects, each with its own backlog, resource plan, milestones and budget.

A3 — cross-functional coordination
He coordinated teams of up to 15 across design, copy, marketing, legal, finance and external vendors, sequencing dependencies between them.

A4 — multi-market program delivery
He managed three large parallel projects for a global food producer across five GCC markets and Uzbekistan over 18 months, with separate social, influencer, paid and content streams.

A5 — project economics and scope control
He tracked hours against sold sprints weekly, flagged overruns before delivery and converted scope expansion into documented, approved change requests.

A6 — web delivery with engineering
He delivered web-development projects end to end: requirements, estimation with engineering, sprint planning, QA and launch, with enough technical depth to challenge estimates and discuss scope directly with developers.

A7 — design-production dependencies
He worked across 2D and identity, web and UI, motion and 3D, briefing disciplines in their own terms and sequencing dependencies between them.

A8 — complex program dependencies
He ran functional programs made of interlocking streams with separate timelines, owners and approval chains.

A9 — enterprise portfolio
At Pragmatica, he delivered 30+ enterprise projects across banking, cybersecurity, mobility, telecom and media, sometimes running 6–7 in parallel, from short requests to year-long productions.

A10 — long program with many stakeholders
He led a 12-month financial-literacy board-game program for a top-5 Eastern European retail bank with a 15-person team and 25 stakeholders across five client departments, contractors and invited experts, owning process, timeline, budget and delivery.

A11 — WebView games / product-like delivery
He managed three WebView games inside the same bank's mobile app across two delivery organizations as a de facto Product Manager. One game was opened 15M+ times.

A12 — commercial negotiation
He secured additional project funding by documenting scope expansion, preparing the commercial case and running up to five rounds of negotiation with client decision-makers.

A13 — mentoring
He mentored a Junior PM from assisted execution to independently managing and closing client projects.

A14 — customer discovery
In an early-stage B2B distribution startup, he managed a 4-person team and ran structured customer-discovery interviews that fed back into positioning.

A15 — PM automation portfolio
He built seven working n8n automations in seven days for PM work: deadline digests, meeting notes into Jira tickets, workload snapshots, sprint carryover counts, status ping-pong detection, intake brief validation and weekly client-update drafts.

A16 — deterministic automation principle
In those automations, he kept decision logic in code and used the LLM mainly for phrasing, so risk classification stayed rule-based rather than model-guessed.

A17 — automation failure lesson
He tested normal, edge and failure cases and found an LLM could pass a junk task name to a client as fact; after that, filtering moved out of the prompt and into code.

Do not invent another employer, client, metric, result, team size, timeline, quote or personal story.
Do not inflate an anchor beyond the wording above.
"""

PM_FACTS = """
VERIFIED FACT BASE:

Agile Manifesto — https://agilemanifesto.org/
- published in 2001
- four value preferences
- it explicitly says the items on the right still have value

Agile history — https://agilemanifesto.org/history
- seventeen people met at Snowbird, Utah in February 2001
- Scrum was one of several approaches already represented there

Scrum Guide — https://scrumguides.org/scrum-guide.html
- Scrum is a lightweight framework
- developed in the early 1990s
- founded on empiricism and lean thinking
- iterative and incremental
- purposefully incomplete

Toyota Production System —
https://global.toyota/en/company/vision-and-philosophy/production-system/
- Kanban is associated with the Toyota Production System
- Kanban cards support a pull system
- the pull concept was influenced in part by supermarket replenishment

Never invent history, studies, percentages or statistics.
If a claim is not supported by supplied evidence, remove it.
"""

BLOCKED_OR_ALREADY_USED_TOPICS = """
Do NOT create another post whose main topic is any of the following:
- what is Scrum vs what is Agile
- the history of Agile / the Snowbird meeting as the main story
- where Kanban came from / Toyota as the main story
- "a project manager is a parent to projects"
- LOW CORTISOL MANAGEMENT
- every project plan needs a backflip
- Jira deadline alerts sent to Telegram
- automated creative file specification checking

These themes may be mentioned in passing only if they are necessary to a genuinely new idea.
The new post must have a materially different thesis, hook and takeaway.
"""

VALID_ANCHORS = {
    "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9",
    "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17"
}


# A deliberately broad editorial map. Python picks the lanes BEFORE Gemini writes,
# so the model cannot keep falling back to the same stakeholder/automation themes.
# Each lane is tied to verified experience anchors above.
TOPIC_LANES = [
    # ambiguity / scoping
    {"id":"brief_to_plan", "domain":"scoping", "title":"turning a one-line request into a delivery plan", "anchors":["A1"], "angle":"what has to become explicit before work can actually start"},
    {"id":"decision_rights", "domain":"scoping", "title":"decision ownership is part of scope", "anchors":["A1","A8"], "angle":"a timeline is weak when nobody knows who can make which decision"},
    {"id":"brief_quality", "domain":"scoping", "title":"a brief is not a requirement set", "anchors":["A1","A6"], "angle":"how discovery converts intent into something specialists can estimate"},
    {"id":"scope_boundary", "domain":"scoping", "title":"good scope is partly a list of what is not included", "anchors":["A1","A5"], "angle":"negative space in scope prevents expensive ambiguity"},
    {"id":"unknowns_before_dates", "domain":"scoping", "title":"name the unknowns before promising the date", "anchors":["A1","A6"], "angle":"risk points are more useful than decorative certainty"},

    # estimation / planning
    {"id":"estimate_with_specialists", "domain":"estimation", "title":"PMs should not estimate specialist work for specialists", "anchors":["A1","A6","A7"], "angle":"the PM owns the estimation process, not every number"},
    {"id":"challenge_estimates", "domain":"estimation", "title":"challenging an estimate is not the same as cutting it", "anchors":["A6"], "angle":"technical literacy lets a PM ask better questions without pretending to be an engineer"},
    {"id":"confidence_ranges", "domain":"estimation", "title":"early estimates should expose confidence, not fake precision", "anchors":["A1","A6"], "angle":"what to do when the work is still partially unknown"},
    {"id":"timeline_risk_points", "domain":"estimation", "title":"a timeline should show where it can break", "anchors":["A1","A8"], "angle":"named risk points make a plan operational rather than decorative"},

    # project economics / commercial
    {"id":"sold_hours", "domain":"commercial", "title":"sold hours are a delivery constraint, not an accounting detail", "anchors":["A5"], "angle":"why economics needs to be visible during delivery, not after it"},
    {"id":"overrun_early", "domain":"commercial", "title":"an overrun discovered at delivery is already old news", "anchors":["A5"], "angle":"why weekly project economics creates options while there is still time"},
    {"id":"change_request_evidence", "domain":"commercial", "title":"a change request is an evidence problem before it is a negotiation problem", "anchors":["A5","A12"], "angle":"documenting how scope changed before asking for more budget"},
    {"id":"scope_vs_goodwill", "domain":"commercial", "title":"good client service does not mean absorbing unlimited scope", "anchors":["A5","A12"], "angle":"protecting the relationship and the economics at the same time"},
    {"id":"negotiation_rounds", "domain":"commercial", "title":"commercial negotiation is part of delivery", "anchors":["A12"], "angle":"why PM judgment continues after the estimate is approved"},
    {"id":"budget_is_design_constraint", "domain":"commercial", "title":"budget behaves like a design constraint", "anchors":["A5","A7"], "angle":"constraints can improve prioritization if they are visible early"},

    # portfolio / capacity
    {"id":"parallel_projects", "domain":"portfolio", "title":"six projects cannot all be priority one", "anchors":["A2","A9"], "angle":"portfolio triage when several projects compete for the same people"},
    {"id":"shared_specialists", "domain":"portfolio", "title":"the real bottleneck is often a shared specialist", "anchors":["A2","A7","A9"], "angle":"resource planning across projects is dependency management between projects"},
    {"id":"portfolio_visibility", "domain":"portfolio", "title":"a perfect project plan can fail inside a bad portfolio", "anchors":["A2","A9"], "angle":"local optimization breaks when the same team is booked elsewhere"},
    {"id":"wip_at_portfolio", "domain":"portfolio", "title":"WIP limits matter above the task board too", "anchors":["A2","A9"], "angle":"too many active initiatives create hidden queues between teams"},
    {"id":"context_switch_cost", "domain":"portfolio", "title":"context switching is a scheduling problem, not a personal discipline problem", "anchors":["A2","A3","A9"], "angle":"how fragmented staffing damages delivery"},

    # dependencies / programs
    {"id":"dependency_map", "domain":"dependencies", "title":"dependencies deserve their own map", "anchors":["A3","A8"], "angle":"a task list hides the handoffs that actually determine the schedule"},
    {"id":"approval_chain", "domain":"dependencies", "title":"approval chains are part of the critical path", "anchors":["A8","A10"], "angle":"waiting for a decision is still project time"},
    {"id":"interlocking_streams", "domain":"dependencies", "title":"program management starts where timelines stop being independent", "anchors":["A8","A10"], "angle":"how separate streams create system-level risk"},
    {"id":"handoff_debt", "domain":"dependencies", "title":"every handoff creates delivery debt", "anchors":["A3","A7","A8"], "angle":"what gets lost between disciplines and how to reduce it"},
    {"id":"sequence_before_speed", "domain":"dependencies", "title":"sequencing can matter more than making every team faster", "anchors":["A7","A8"], "angle":"speed in the wrong order creates rework"},

    # design production
    {"id":"design_disciplines", "domain":"design", "title":"design is not one production queue", "anchors":["A7"], "angle":"2D, identity, UI, motion and 3D have different inputs and dependency patterns"},
    {"id":"brief_by_discipline", "domain":"design", "title":"one brief format does not fit every creative discipline", "anchors":["A7"], "angle":"briefing specialists in their own working language"},
    {"id":"creative_review_order", "domain":"design", "title":"review order can create or remove rework", "anchors":["A7","A8"], "angle":"why approvals need to follow production dependencies"},
    {"id":"creative_pm_quality", "domain":"design", "title":"a PM does not need to design, but needs to understand production", "anchors":["A7"], "angle":"enough craft literacy to sequence work and spot impossible handoffs"},
    {"id":"motion_depends_on_static", "domain":"design", "title":"downstream creative work should not start on unstable upstream decisions", "anchors":["A7"], "angle":"why freezing the right things at the right moment matters"},

    # engineering / web
    {"id":"pm_technical_depth", "domain":"engineering", "title":"technical depth for a PM is mostly about asking non-stupid questions", "anchors":["A6"], "angle":"how to discuss scope and estimates directly with developers without cosplay engineering"},
    {"id":"qa_ownership", "domain":"engineering", "title":"QA is not the last stage of a project", "anchors":["A6"], "angle":"release quality begins when requirements and acceptance logic are defined"},
    {"id":"requirements_vs_solution", "domain":"engineering", "title":"requirements and implementation are different conversations", "anchors":["A6"], "angle":"keeping the problem stable while allowing engineering choices to evolve"},
    {"id":"launch_is_not_handover", "domain":"engineering", "title":"launch is a delivery event, not the disappearance of the PM", "anchors":["A6"], "angle":"what end-to-end ownership changes around release"},
    {"id":"engineering_scope_talk", "domain":"engineering", "title":"scope conversations get better when PMs can talk directly to engineering", "anchors":["A6"], "angle":"reducing translation loss between business request and technical reality"},

    # multi-market / marketing delivery
    {"id":"multi_market_localization", "domain":"multimarket", "title":"multi-market delivery is not copy-paste with different flags", "anchors":["A4"], "angle":"shared system, local constraints and many parallel content streams"},
    {"id":"stream_sync", "domain":"multimarket", "title":"social, influencer, paid and content streams do not share one clock", "anchors":["A4"], "angle":"how parallel marketing streams create coordination risk"},
    {"id":"global_local_tradeoff", "domain":"multimarket", "title":"consistency and local relevance pull in opposite directions", "anchors":["A4"], "angle":"a delivery problem hidden inside a brand problem"},
    {"id":"campaign_dependency", "domain":"multimarket", "title":"campaign calendars are dependency maps in disguise", "anchors":["A4","A8"], "angle":"how one late approval can move several downstream streams"},

    # stakeholder / governance — deliberately only a few lanes
    {"id":"stakeholder_count_not_decisions", "domain":"governance", "title":"25 stakeholders do not mean 25 decision-makers", "anchors":["A10"], "angle":"separating participation from decision rights"},
    {"id":"governance_design", "domain":"governance", "title":"governance is a delivery design problem", "anchors":["A10"], "angle":"who reviews, who decides and when feedback stops"},
    {"id":"feedback_consolidation", "domain":"governance", "title":"unconsolidated feedback is hidden scope", "anchors":["A10"], "angle":"multiple departments can create conflicting work without changing the brief on paper"},

    # product-like delivery
    {"id":"agency_product_thinking", "domain":"product", "title":"product thinking can exist inside project delivery", "anchors":["A11"], "angle":"shipping inside a live app changes what good delivery means"},
    {"id":"two_delivery_orgs", "domain":"product", "title":"one product can have two delivery organizations", "anchors":["A11"], "angle":"coordination when ownership is split across organizational boundaries"},
    {"id":"usage_after_launch", "domain":"product", "title":"delivery changes when people actually keep using what you ship", "anchors":["A11"], "angle":"what a high-usage WebView project teaches a delivery PM about product consequences"},
    {"id":"project_to_product_gap", "domain":"product", "title":"the project ends before the product does", "anchors":["A11"], "angle":"where project delivery and product ownership diverge after launch"},

    # long programs / resilience
    {"id":"year_long_delivery", "domain":"long_programs", "title":"a 12-month plan should be designed to be rewritten", "anchors":["A10"], "angle":"long programs need stable goals and flexible execution"},
    {"id":"program_memory", "domain":"long_programs", "title":"long projects need institutional memory", "anchors":["A10"], "angle":"keeping decisions and context alive across months and many participants"},
    {"id":"stakeholder_turnover", "domain":"long_programs", "title":"a long program must survive people changing around it", "anchors":["A10"], "angle":"process as continuity, not bureaucracy"},

    # mentoring / team autonomy
    {"id":"delegation_ladder", "domain":"mentoring", "title":"delegation should have levels, not a binary switch", "anchors":["A13"], "angle":"moving a Junior PM from assisted execution to independent ownership"},
    {"id":"pm_autonomy", "domain":"mentoring", "title":"the goal of mentoring is to become unnecessary in the loop", "anchors":["A13"], "angle":"how autonomy changes what the mentor should keep and give away"},
    {"id":"review_without_takeover", "domain":"mentoring", "title":"reviewing work without taking the work back", "anchors":["A13"], "angle":"the management trap that blocks junior growth"},
    {"id":"teach_judgment", "domain":"mentoring", "title":"checklists teach process; edge cases teach judgment", "anchors":["A13","A17"], "angle":"why developing a PM means exposing decision logic, not just procedures"},

    # customer discovery
    {"id":"customer_interviews", "domain":"discovery", "title":"customer discovery is project management before there is a project", "anchors":["A14"], "angle":"structured interviews turning uncertainty into positioning choices"},
    {"id":"interview_synthesis", "domain":"discovery", "title":"ten interviews are useless if they never change a decision", "anchors":["A14"], "angle":"research only matters when evidence feeds back into positioning"},
    {"id":"discovery_vs_validation", "domain":"discovery", "title":"customer interviews should be designed to surprise you", "anchors":["A14"], "angle":"avoiding questions that merely validate an existing story"},

    # process / operations
    {"id":"process_theatre", "domain":"process", "title":"process is only useful when it removes a recurring decision or failure", "anchors":["A1","A8","A15"], "angle":"distinguishing operational structure from ceremony"},
    {"id":"single_source_truth", "domain":"process", "title":"a source of truth is useless if nobody trusts the update path", "anchors":["A2","A8"], "angle":"information architecture is part of delivery"},
    {"id":"rituals_have_cost", "domain":"process", "title":"every project ritual should earn its calendar slot", "anchors":["A2","A8"], "angle":"ceremony has a cost and should solve a concrete coordination problem"},
    {"id":"handover_quality", "domain":"process", "title":"handover quality is a test of whether the project was actually structured", "anchors":["A6","A9"], "angle":"clean closure reveals the quality of decisions and documentation upstream"},

    # automation / AI — capped by selector to max one per batch
    {"id":"rules_vs_llm", "domain":"automation", "title":"rules should decide; LLMs should phrase", "anchors":["A16"], "angle":"why deterministic business logic is safer than model judgment for operational automation"},
    {"id":"automation_failure", "domain":"automation", "title":"the useful part of AI automation starts when it fails", "anchors":["A17"], "angle":"moving validation out of the prompt after a junk task name reached client-facing output"},
    {"id":"automation_test_cases", "domain":"automation", "title":"automations need QA like products do", "anchors":["A15","A17"], "angle":"normal, edge and failure cases for PM workflows"},
    {"id":"automate_checks_not_judgment", "domain":"automation", "title":"automate repeated checks before automating judgment", "anchors":["A15","A16"], "angle":"a practical boundary for safe PM automation"},
    {"id":"intake_validation", "domain":"automation", "title":"bad input should fail early", "anchors":["A15","A17"], "angle":"why intake validation is more valuable than polishing bad downstream output"},
]

TOPIC_HISTORY_PATH = ROOT / "generated" / "topic_history.json"
TOPIC_COOLDOWN = 44  # last 44 generated lanes cannot be selected again


def load_topic_history():
    try:
        if TOPIC_HISTORY_PATH.exists():
            data = json.loads(TOPIC_HISTORY_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception as e:
        print("Could not read persistent topic history:", e)
    return []


def choose_topic_lanes(history):
    """Choose four lanes with hard diversity before the model sees the prompt."""
    recent_ids = [x.get("lane_id") for x in history[-TOPIC_COOLDOWN:] if x.get("lane_id")]
    blocked = set(recent_ids)
    available = [x for x in TOPIC_LANES if x["id"] not in blocked]

    # If the catalog is eventually exhausted, release only the oldest cooldown entries.
    if len(available) < DRAFT_COUNT:
        blocked = set(recent_ids[-24:])
        available = [x for x in TOPIC_LANES if x["id"] not in blocked]

    rng = random.SystemRandom()
    rng.shuffle(available)

    selected = []
    used_domains = set()
    automation_count = 0

    # First pass: one lane per domain, max one automation topic.
    for lane in available:
        if lane["domain"] in used_domains:
            continue
        if lane["domain"] == "automation" and automation_count >= 1:
            continue
        selected.append(lane)
        used_domains.add(lane["domain"])
        automation_count += int(lane["domain"] == "automation")
        if len(selected) == DRAFT_COUNT:
            break

    # Emergency fill, still never duplicate a lane.
    if len(selected) < DRAFT_COUNT:
        for lane in available:
            if lane in selected:
                continue
            if lane["domain"] == "automation" and automation_count >= 1:
                continue
            selected.append(lane)
            automation_count += int(lane["domain"] == "automation")
            if len(selected) == DRAFT_COUNT:
                break

    if len(selected) != DRAFT_COUNT:
        raise RuntimeError("Not enough unused topic lanes available")

    print("SELECTED TOPIC LANES:")
    for i, lane in enumerate(selected, 1):
        print(f"  {i}. [{lane['domain']}] {lane['id']} — {lane['title']}")
    return selected


def save_topic_history(posts):
    """Persist generated themes in the repo, so deleting a Buffer draft does not erase memory."""
    TOPIC_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = load_topic_history()
    run_id = os.getenv("GITHUB_RUN_ID", str(int(time.time())))
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    for post in posts:
        history.append({
            "run_id": run_id,
            "created_at": stamp,
            "lane_id": post.get("topic_lane", ""),
            "topic": post.get("topic", ""),
            "anchors": post.get("experience_anchor", []),
            "provocative": bool(post.get("provocative")),
        })
    # Enough history for a long cooldown, without growing forever.
    TOPIC_HISTORY_PATH.write_text(
        json.dumps(history[-240:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def download(url, path):
    if path.exists():
        return
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    path.write_bytes(r.content)

def load_anton(size):
    return ImageFont.truetype(str(ANTON), size)

def load_inter(size, weight=300):
    f = ImageFont.truetype(str(INTER), size)
    try:
        f.set_variation_by_axes([24, weight])
    except Exception:
        pass
    return f

def wrap(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]
    lines, line = [], words[0]
    for word in words[1:]:
        test = line + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines

def fit_text(draw, text, loader, max_width, max_height, start, minimum, spacing=8):
    for size in range(start, minimum - 1, -2):
        font = loader(size)
        lines = wrap(draw, text, font, max_width)
        heights = []
        for ln in lines:
            box = draw.textbbox((0, 0), ln or "A", font=font)
            heights.append(box[3] - box[1])
        total = sum(heights) + spacing * max(0, len(lines) - 1)
        if total <= max_height:
            return font, lines, total
    font = loader(minimum)
    lines = wrap(draw, text, font, max_width)
    return font, lines, max_height

def draw_lines(draw, xy, lines, font, fill, spacing):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        box = draw.textbbox((x, y), line or "A", font=font)
        y += (box[3] - box[1]) + spacing
    return y

def render_slide(slide, index, out_path):
    bg, fg, accent = PALETTE[index % len(PALETTE)]
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    label = slide.get("label", "pm notes")
    headline = slide.get("headline", "").strip().upper()
    body = slide.get("body", "").strip()

    label_font = load_inter(32, 300)
    draw.text((MARGIN, 78), label, font=label_font, fill=accent)

    headline_y = 275 if index == 0 else 255
    max_head_h = 600 if index == 0 else 470
    head_font, head_lines, _ = fit_text(
        draw, headline, load_anton,
        W - 2 * MARGIN, max_head_h,
        148 if index == 0 else 126, 72, spacing=2
    )
    y = draw_lines(draw, (MARGIN, headline_y), head_lines, head_font, fg, 2)

    if body:
        y += 58
        body_loader = lambda s: load_inter(s, 300)
        body_font, body_lines, _ = fit_text(
            draw, body, body_loader,
            W - 2 * MARGIN, H - y - 140,
            48, 30, spacing=16
        )
        draw_lines(draw, (MARGIN, y), body_lines, body_font, fg, 16)

    # tiny signature on final slide only
    if slide.get("signature"):
        sig_font = load_inter(26, 300)
        draw.text((MARGIN, H - 85), "Matvei Shakhurdin · motyushah.com",
                  font=sig_font, fill=accent)

    img.save(out_path, "PNG", optimize=True)

def strip_html(value):
    if not value:
        return ""
    value = html.unescape(value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def hacker_news():
    result = []
    try:
        ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=20
        ).json()[:25]
        for item_id in ids:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                timeout=10
            ).json()
            if item and item.get("type") == "story":
                result.append({
                    "source": "Hacker News",
                    "title": item.get("title", ""),
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                    "description": ""
                })
    except Exception as e:
        print("HN failed:", e)
    return result

def product_hunt():
    result = []
    try:
        r = requests.get(
            "https://www.producthunt.com/feed",
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        r.raise_for_status()
        root = ET.fromstring(r.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns)[:15]:
            link_el = entry.find("atom:link", ns)
            result.append({
                "source": "Product Hunt",
                "title": strip_html(entry.findtext("atom:title", default="", namespaces=ns)),
                "url": link_el.attrib.get("href", "") if link_el is not None else "",
                "description": strip_html(entry.findtext("atom:content", default="", namespaces=ns))[:500]
            })
    except Exception as e:
        print("Product Hunt failed:", e)
    return result

def google_news():
    result = []
    for search in [
        "AI project management",
        "AI automation work",
        "future of work AI",
        "design AI tools",
        "software project management"
    ]:
        try:
            url = (
                "https://news.google.com/rss/search?"
                f"q={quote(search)}&hl=en-US&gl=US&ceid=US:en"
            )
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:5]:
                result.append({
                    "source": "Google News",
                    "title": strip_html(item.findtext("title", "")),
                    "url": item.findtext("link", ""),
                    "description": strip_html(item.findtext("description", ""))[:500]
                })
        except Exception as e:
            print("Google News failed:", e)
    return result

def collect_trends():
    items = hacker_news() + product_hunt() + google_news()
    unique, seen = [], set()
    for item in items:
        key = item["title"].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:50]

def buffer_request(query, variables=None):
    r = requests.post(
        "https://api.buffer.com",
        headers={
            "Authorization": f"Bearer {BUFFER_KEY}",
            "Content-Type": "application/json",
        },
        json={"query": query, "variables": variables or {}},
        timeout=60,
    )
    r.raise_for_status()
    result = r.json()
    if result.get("errors"):
        raise RuntimeError(str(result["errors"]))
    return result["data"]

def get_linkedin():
    data = buffer_request("""
    query {
      account {
        organizations { id name }
      }
    }
    """)
    org = data["account"]["organizations"][0]
    data = buffer_request(
        """
        query GetChannels($organizationId: OrganizationId!) {
          channels(input: {organizationId: $organizationId}) {
            id name service
          }
        }
        """,
        {"organizationId": org["id"]},
    )
    linkedin = next(
        c for c in data["channels"]
        if str(c["service"]).lower() == "linkedin"
    )
    return linkedin["id"]


def get_recent_buffer_posts(limit=50):
    """Best-effort semantic history for topic deduplication. Never break the workflow if Buffer changes this query."""
    try:
        data = buffer_request("""
        query {
          account {
            organizations { id name }
          }
        }
        """)
        org = data["account"]["organizations"][0]

        channels_data = buffer_request(
            """
            query GetChannels($organizationId: OrganizationId!) {
              channels(input: {organizationId: $organizationId}) {
                id name service
              }
            }
            """,
            {"organizationId": org["id"]},
        )
        linkedin = next(
            c for c in channels_data["channels"]
            if str(c["service"]).lower() == "linkedin"
        )

        posts_data = buffer_request(
            """
            query RecentPosts($organizationId: OrganizationId!, $channelId: ChannelId!) {
              posts(
                first: 50
                input: {
                  organizationId: $organizationId
                  filter: {
                    status: [draft, scheduled, sent]
                    channelIds: [$channelId]
                  }
                  sort: [{field: createdAt, direction: desc}]
                }
              ) {
                edges { node { text } }
              }
            }
            """,
            {"organizationId": org["id"], "channelId": linkedin["id"]},
        )
        texts = [
            edge["node"].get("text", "").strip()
            for edge in posts_data.get("posts", {}).get("edges", [])
            if edge.get("node", {}).get("text")
        ]
        return texts[:limit]
    except Exception as e:
        print("Could not read recent Buffer posts for dedupe:", e)
        return []

def make_prompt(trends, previous_posts, selected_lanes, topic_history):
    trend_text = "\n\n".join(
        f"SOURCE: {x['source']}\nTITLE: {x['title']}\nURL: {x['url']}\nDESCRIPTION: {x['description']}"
        for x in trends
    )

    history_text = "\n\n--- PREVIOUS POST ---\n".join(previous_posts[:40])
    lane_text = "\n".join(
        f"POST {i}: lane_id={lane['id']} | domain={lane['domain']} | title={lane['title']} | verified anchors={','.join(lane['anchors'])} | angle={lane['angle']}"
        for i, lane in enumerate(selected_lanes, start=1)
    )
    persistent_history_text = "\n".join(
        f"- {x.get('lane_id','')}: {x.get('topic','')}"
        for x in topic_history[-60:]
    )

    return f"""
{STYLE}

{PROFILE}

{EXPERIENCE_FACTS}

{PM_FACTS}

{BLOCKED_OR_ALREADY_USED_TOPICS}

Create exactly {DRAFT_COUNT} different LinkedIn post candidates.

THE FOUR TOPICS HAVE ALREADY BEEN CHOSEN BY CODE. YOU MUST USE THEM EXACTLY:
{lane_text}

HARD TOPIC RULES:
- Post 1 must use POST 1 lane above, Post 2 must use POST 2 lane, etc
- return the exact lane_id in a field called "topic_lane"
- do not replace a selected lane with stakeholder management, automation, scope control or another familiar fallback
- the selected lane is the main subject; other PM concepts may appear only as supporting context
- each post must feel materially different from the other three in subject, problem, hook and takeaway
- at most ONE post in the batch may be primarily about AI or automation
- at most ONE post in the batch may be primarily about stakeholders/governance

THIS IS THE MOST IMPORTANT RULE:
Every candidate must start from ONE OR MORE verified Matvei experience anchors A1–A17 above.
Do not start from a random trend and then force Matvei into it.
Do not start from a generic PM topic and pretend Matvei experienced it.
First choose a real experience anchor. Then extract a useful, interesting thesis from it.

EXACT EDITORIAL MIX — FOLLOW THIS, DO NOT RANDOMIZE:

POST 1 — PROVOCATIVE EXPERT TAKE
- provocative = true
- grounded in one verified experience anchor
- challenge a common PM assumption or comfortable convention
- provocative means defensible tension, not ragebait
- make the reader think "huh, that's uncomfortable but fair"

POST 2 — PROVOCATIVE EXPERT TAKE
- provocative = true
- use a DIFFERENT experience anchor from Post 1
- challenge another conventional PM belief, ritual, habit or management instinct
- still practical, evidence-led and professional

POST 3 — PRACTICAL EXPERIENCE-LED POST
- provocative = false
- unpack a real delivery lesson, trade-off, failure mode, operating principle or decision pattern from Matvei's experience
- preferably use a concrete situation type: scope, resources, dependencies, QA, stakeholder management, estimation, project economics, design/dev coordination, mentoring or delivery under parallel load

POST 4 — EXPERTISE / SYSTEMS POST
- provocative = false
- choose either:
  a) AI / automation / process design grounded in A15–A17, OR
  b) another strong delivery topic grounded in a DIFFERENT anchor, OR
  c) a current trend ONLY when it directly intersects with a verified Matvei experience anchor
- if the trend connection is weak, ignore the trend completely

PROVOCATION RULES:
- EXACTLY 2 of the 4 posts must have "provocative": true
- the other 2 must have "provocative": false
- provocation should come from a strong thesis, not swearing, insults or fake certainty
- good examples of structure: "X is often treated as Y. in practice, I think the real problem is Z"
- do not attack PMs, clients, developers, designers or companies as groups
- no cheap contrarianism

EXPERIENCE RULES:
- every post must output "experience_anchor" using one or more IDs from A1–A17
- every personal factual statement must be supported by those anchors
- the post may be inspired by an anchor without literally repeating the CV bullet
- first-person language is welcome when natural: "i've found", "i learned", "the projects where..."
- do not turn every post into "at my previous company..."
- the experience should give the idea credibility, not make the post read like a resume
- across the four candidates, use at least 3 different anchor IDs

JOB-SEARCH POSITIONING:
Without explicitly saying "hire me", the four-post batch should collectively signal:
- senior delivery judgment
- commercial awareness
- cross-functional leadership
- comfort with design and engineering
- ability to structure ambiguity
- risk / scope / resource thinking
- process and automation literacy
- ability to learn from failures rather than hide them

TOPIC PRIORITY:
Prefer these areas because they map directly to Matvei's actual work:
1. scope and change control
2. project economics, sold hours, overruns and trade-offs
3. running 6–7 projects without pretending all are equally important
4. dependency management across design / engineering / marketing
5. turning one-line asks into decision-ready plans
6. estimating with specialists rather than "estimating for them"
7. stakeholder complexity and decision ownership
8. QA and release responsibility
9. what product thinking looks like from a delivery background
10. what agency PMs learn about constraints that product teams can use
11. AI automation where deterministic rules beat model judgment
12. failure modes in AI-assisted PM workflows
13. mentoring and building PM autonomy
14. multi-market / multi-stream coordination
15. when process reduces friction vs when process becomes theatre

DO NOT DEFAULT TO:
- generic productivity advice
- generic leadership quotes
- "communication is important"
- "AI is changing everything"
- generic Scrum / Agile / Kanban explainers
- generic remote-work takes
- generic meeting advice
unless there is a specific, experience-led thesis that could only plausibly come from this background

DEDUPLICATION:
- do NOT repeat the thesis, hook, metaphor or conclusion of recent Buffer posts below
- do NOT revisit blocked topics as the main idea
- if a candidate feels semantically similar to a previous post, discard it and generate another
- different wording is NOT enough; the underlying idea must be different

FACT-CHECK RULES — MANDATORY:
- personal-experience facts must be supported by VERIFIED MATVEI EXPERIENCE
- external factual claims must be supported by VERIFIED FACT BASE or TREND EVIDENCE below
- if support is missing, remove the claim or frame it explicitly as opinion
- never invent studies, statistics, dates, quotes, company announcements, product capabilities or history
- never create a source URL that was not supplied
- opinion and operational judgment do not need a source, but must be phrased as judgment rather than universal fact

CAPITALIZATION CHECK BEFORE RETURNING:
- ordinary prose stays lowercase by default, including "i"
- proper nouns, names, brands, frameworks and acronyms use correct capitalization
- examples: LinkedIn, OpenAI, GitHub, Jira, Scrum, Agile, Kanban, Toyota, Telegram, Tbilisi, Matvei Shakhurdin, AI, PM, API, SQL, CRM, QA
- never lowercase a proper noun for style

QUALITY BAR:
- each post must have ONE precise thesis
- the thesis should be traceable to real experience
- concrete trade-off > abstract advice
- operating principle > inspirational lesson
- specific failure mode > generic best practice
- tension > listicle
- if a random PM influencer with no delivery experience could write the same thing, reject it
- if the post sounds impressive but reveals nothing about how Matvei actually works, reject it

RECENT BUFFER POSTS — DO NOT REPEAT:
{history_text if history_text else "No readable Buffer history available. Use the blocked list above."}

PERSISTENT GENERATED-TOPIC HISTORY — THIS SURVIVES DELETING BUFFER DRAFTS:
{persistent_history_text if persistent_history_text else "No persistent topic history yet."}

If a selected topic lane could accidentally recreate a thesis from this history, choose a NEW thesis inside the selected lane. Do not switch lanes.

CAROUSEL:
For every post create 5–8 slides.
Visual identity:
- 1080×1350
- Anton-style huge condensed uppercase headlines
- thin sans-serif supporting copy
- huge margins
- black / white / vivid yellow / cyan / vivid red
- flat colors, no gradients
- minimal editorial composition
- one idea per slide
- headline preferably under 8 words
- body ideally under 35 words
- proper nouns and acronyms correctly capitalized
- no fake screenshots or fake interfaces
- first slide = strong thesis / hook
- middle slides = reasoning / example / model
- final slide = conclusion, no begging for engagement

CURRENT TREND EVIDENCE — OPTIONAL RAW MATERIAL ONLY:
{trend_text}

Return VALID JSON ONLY:
{{
  "posts": [
    {{
      "provocative": true,
      "topic_lane": "exact selected lane_id",
      "experience_anchor": ["A5"],
      "category": "pm_expertise | practical | systems | trend",
      "topic": "internal topic",
      "text": "finished LinkedIn post",
      "sources": ["only actual supplied URLs used for external factual claims"],
      "carousel": {{
        "slides": [
          {{
            "label": "pm notes or another tiny label",
            "headline": "SHORT HEADLINE",
            "body": "optional supporting copy"
          }}
        ]
      }}
    }}
  ]
}}
"""

def generate_candidates(prompt, selected_lanes):
    # Free-tier first. If one model is temporarily overloaded (503/429),
    # the script waits and automatically tries the next one.
    models = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
    ]

    last_error = None

    for model in models:
        for attempt in range(3):
            print(f"Gemini {model}, attempt {attempt + 1}")

            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    headers={
                        "x-goog-api-key": GEMINI_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.75
                        },
                    },
                    timeout=180,
                )
            except requests.RequestException as e:
                last_error = e
                wait = 15 * (attempt + 1)
                print(f"Gemini network error: {e}. waiting {wait}s")
                time.sleep(wait)
                continue

            if r.status_code in [429, 500, 502, 503, 504]:
                last_error = RuntimeError(
                    f"{model} returned {r.status_code}: {r.text[:300]}"
                )
                wait = 15 * (attempt + 1)
                print(f"temporary Gemini error: {r.status_code}. waiting {wait}s")
                time.sleep(wait)
                continue

            if r.status_code in [401, 403]:
                raise RuntimeError(
                    "Gemini rejected GEMINI_API_KEY. Create a new key in Google AI Studio "
                    "and replace the GEMINI_API_KEY secret in GitHub."
                )

            if r.status_code == 404:
                last_error = RuntimeError(
                    f"Model {model} is unavailable for this API key/project"
                )
                print(f"{model} unavailable (404), trying next model")
                break

            r.raise_for_status()

            try:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(raw)
                posts = data.get("posts", [])
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                last_error = e
                print("Gemini returned an unexpected response, trying again")
                wait = 10 * (attempt + 1)
                time.sleep(wait)
                continue

            if posts:
                posts = posts[:DRAFT_COUNT]
                provocative_count = sum(1 for p in posts if p.get("provocative") is True)
                anchors = []
                invalid_anchor = False
                for p in posts:
                    p_anchors = p.get("experience_anchor", [])
                    if isinstance(p_anchors, str):
                        p_anchors = [p_anchors]
                        p["experience_anchor"] = p_anchors
                    if not p_anchors or any(a not in VALID_ANCHORS for a in p_anchors):
                        invalid_anchor = True
                    anchors.extend(p_anchors)

                if len(posts) != DRAFT_COUNT:
                    last_error = RuntimeError(f"Expected {DRAFT_COUNT} posts, got {len(posts)}")
                    print(last_error)
                    continue
                if provocative_count != 2:
                    last_error = RuntimeError(f"Expected exactly 2 provocative posts, got {provocative_count}")
                    print(last_error)
                    continue
                if invalid_anchor or len(set(anchors)) < 3:
                    last_error = RuntimeError("Experience anchors are invalid or insufficiently diverse")
                    print(last_error)
                    continue

                expected_lanes = [x["id"] for x in selected_lanes]
                returned_lanes = [p.get("topic_lane") for p in posts]
                if returned_lanes != expected_lanes:
                    last_error = RuntimeError(
                        f"Model ignored required topic lanes. Expected {expected_lanes}, got {returned_lanes}"
                    )
                    print(last_error)
                    continue

                # Also enforce that each selected lane uses only verified compatible anchors.
                lane_map = {x["id"]: set(x["anchors"]) for x in selected_lanes}
                bad_lane_anchor = False
                for p in posts:
                    used = set(p.get("experience_anchor", []))
                    allowed = lane_map.get(p.get("topic_lane"), set())
                    if not used.intersection(allowed):
                        bad_lane_anchor = True
                        break
                if bad_lane_anchor:
                    last_error = RuntimeError("A post is not grounded in an anchor compatible with its required topic lane")
                    print(last_error)
                    continue

                print(f"SUCCESS with {model}: {len(posts)} experience-led posts generated")
                return posts

            last_error = RuntimeError(f"{model} returned no posts")
            print("Gemini returned no posts, trying again")

    raise RuntimeError(f"Gemini failed on all free models. Last error: {last_error}")


def fact_check_candidate(candidate, trends):
    """Strict second pass: verify both Matvei-experience claims and external facts before Buffer."""
    trend_text = "\n\n".join(
        f"SOURCE: {x['source']}\nTITLE: {x['title']}\nURL: {x['url']}\nDESCRIPTION: {x['description']}"
        for x in trends
    )

    prompt = f"""
You are a strict fact-checker, experience-grounding editor and copy editor.

{EXPERIENCE_FACTS}

{PM_FACTS}

CAPITALIZATION POLICY:
- ordinary prose may begin lowercase and "i" stays lowercase
- proper nouns, official names, brands, frameworks and acronyms MUST use standard capitalization
- examples: LinkedIn, OpenAI, GitHub, Jira, Scrum, Agile, Kanban, Toyota, Telegram, Tbilisi, Matvei Shakhurdin, AI, PM, API, SQL, CRM, QA

TREND EVIDENCE:
{trend_text}

CANDIDATE JSON:
{json.dumps(candidate, ensure_ascii=False)}

Check every claim and the underlying thesis.

MANDATORY RULES:
1. The candidate MUST be genuinely grounded in the listed experience_anchor IDs.
2. Every factual claim about Matvei's work must be directly supported by VERIFIED MATVEI EXPERIENCE.
3. Do not infer extra client details, results, motives, team sizes, timelines or outcomes from an anchor.
4. External factual claims are allowed only if supported by VERIFIED FACT BASE or supplied TREND EVIDENCE.
5. If an unsupported detail is nonessential, remove it or rewrite it as clearly subjective judgment.
6. If the main thesis depends on invented or unsupported experience, set approved=false rather than fabricating a replacement story.
7. Keep the core experience-led thesis and Matvei's voice.
8. Correct every proper noun / official name / acronym.
9. Keep lowercase ordinary prose and no period at the end of paragraphs.
10. Carousel copy must match the corrected post and the same factual standard.
11. The carousel MUST contain 5 to 8 slides. Never return fewer than 5 slides.
12. Provocative posts may challenge assumptions, but must not become ragebait or universal claims unsupported by experience.
13. Preserve "provocative", "topic_lane" and "experience_anchor" fields exactly.
14. Do not change the subject into stakeholder management, automation or another familiar PM fallback.

Return VALID JSON ONLY:
{{
  "approved": true,
  "issues": ["short description of anything corrected"],
  "candidate": {{
    "provocative": true,
    "topic_lane": "exact original lane_id",
    "experience_anchor": ["A5"],
    "category": "...",
    "topic": "...",
    "text": "corrected final post",
    "sources": ["only supplied URLs actually used"],
    "carousel": {{"slides": [{{"label":"...","headline":"...","body":"..."}}]}}
  }}
}}
"""

    models = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
    ]

    last_error = None
    for model in models:
        for attempt in range(2):
            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    headers={
                        "x-goog-api-key": GEMINI_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.2
                        },
                    },
                    timeout=180,
                )
            except requests.RequestException as e:
                last_error = e
                time.sleep(10 * (attempt + 1))
                continue

            if r.status_code in [429, 500, 502, 503, 504]:
                last_error = RuntimeError(f"fact-check {model} returned {r.status_code}")
                time.sleep(10 * (attempt + 1))
                continue
            if r.status_code == 404:
                break
            r.raise_for_status()

            try:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                checked = json.loads(raw)
                corrected = checked.get("candidate")
                if checked.get("approved") is not True:
                    last_error = RuntimeError("Candidate failed experience/fact grounding")
                    print("FACT-CHECK REJECTED:", checked.get("issues"))
                    continue
                if corrected and corrected.get("text"):
                    corrected["topic_lane"] = candidate.get("topic_lane", corrected.get("topic_lane", ""))
                    anchors = corrected.get("experience_anchor", [])
                    if isinstance(anchors, str):
                        anchors = [anchors]
                        corrected["experience_anchor"] = anchors
                    if not anchors or any(a not in VALID_ANCHORS for a in anchors):
                        last_error = RuntimeError("Fact-check returned invalid experience anchor")
                        continue
                    if checked.get("issues"):
                        print("FACT-CHECK CORRECTIONS:", checked.get("issues"))
                    return corrected
            except Exception as e:
                last_error = e
                time.sleep(5)
                continue

    raise RuntimeError(f"Fact-check failed; draft was not sent to Buffer. Last error: {last_error}")

def _fallback_carousel(candidate):
    """Last-resort carousel built only from the already fact-checked post text."""
    text = (candidate.get("text") or "").strip()
    topic = (candidate.get("topic") or "project management note").strip()

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paragraphs) < 4:
        sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text)) if x.strip()]
        if len(sentences) > len(paragraphs):
            paragraphs = sentences

    chunks = []
    for p in paragraphs:
        if len(p) <= 420:
            chunks.append(p)
        else:
            words = p.split()
            current = []
            for w in words:
                current.append(w)
                if len(" ".join(current)) >= 300:
                    chunks.append(" ".join(current))
                    current = []
            if current:
                chunks.append(" ".join(current))

    if not chunks:
        chunks = [text or topic]

    def short_headline(value, fallback):
        words = re.sub(r"\s+", " ", value).strip().split()
        if not words:
            return fallback
        return " ".join(words[:8]).upper()

    slides = [{
        "label": "pm notes",
        "headline": short_headline(topic, "PM NOTES"),
        "body": chunks[0][:360],
    }]

    for chunk in chunks[1:6]:
        slides.append({
            "label": "pm notes",
            "headline": short_headline(chunk, "THE POINT"),
            "body": chunk[:420],
        })

    while len(slides) < 5:
        idx = len(slides) % len(chunks)
        chunk = chunks[idx]
        slides.append({
            "label": "pm notes",
            "headline": short_headline(chunk, "THE POINT"),
            "body": chunk[:420],
        })

    return slides[:8]


def ensure_carousel(candidate):
    """Repair an incomplete carousel instead of failing the entire workflow."""
    slides = candidate.get("carousel", {}).get("slides", [])
    if 5 <= len(slides) <= 8:
        return candidate

    print(f"Carousel incomplete ({len(slides)} slide(s)). Repairing it...")

    prompt = f"""
You are repairing ONLY the carousel for an already fact-checked LinkedIn post.

POST:
{candidate.get('text', '')}

TOPIC:
{candidate.get('topic', '')}

EXPERIENCE ANCHORS:
{json.dumps(candidate.get('experience_anchor', []), ensure_ascii=False)}

STRICT RULES:
- return 5 to 8 slides, never fewer than 5
- do not add any new facts, numbers, dates, names, claims or outcomes that are not already present in the post
- the carousel must simply explain or sharpen the existing post
- use normal capitalization for proper nouns and acronyms: Jira, LinkedIn, AI, PM, API, SQL, CRM, QA, names, companies and products
- ordinary supporting copy may begin lowercase
- no em dash —; use en dash – if needed
- no periods at the end of slide body copy
- visual identity: editorial, minimal, huge Anton-style uppercase headline, thin sans-serif body, bright flat colors
- slide 1 must work as a strong cover
- final slide should land the idea, not add a generic CTA

Return VALID JSON ONLY:
{{
  "slides": [
    {{"label":"pm notes","headline":"SHORT HEADLINE","body":"supporting copy"}}
  ]
}}
"""

    models = [
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash",
    ]

    for model in models:
        for attempt in range(2):
            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    headers={
                        "x-goog-api-key": GEMINI_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.3,
                        },
                    },
                    timeout=180,
                )
            except requests.RequestException as e:
                print(f"Carousel repair network error with {model}: {e}")
                time.sleep(5 * (attempt + 1))
                continue

            if r.status_code in [429, 500, 502, 503, 504]:
                print(f"Carousel repair temporary error {r.status_code} with {model}")
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code == 404:
                break
            r.raise_for_status()

            try:
                raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(raw)
                repaired = data.get("slides", [])[:8]
                if len(repaired) >= 5:
                    candidate.setdefault("carousel", {})["slides"] = repaired
                    print(f"Carousel repaired with {model}: {len(repaired)} slides")
                    return candidate
            except Exception as e:
                print(f"Carousel repair parse error with {model}: {e}")
                time.sleep(3)

    # Never kill the whole run just because the carousel model misbehaved.
    fallback = _fallback_carousel(candidate)
    candidate.setdefault("carousel", {})["slides"] = fallback
    print(f"Carousel repair fell back to deterministic layout: {len(fallback)} slides")
    return candidate


def git_publish_generated():
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(
        ["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"],
        check=True
    )
    subprocess.run(["git", "add", "generated"], check=True)
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True, capture_output=True, text=True
    ).stdout.strip()
    if not status:
        return
    subprocess.run(
        ["git", "commit", "-m", f"add generated LinkedIn carousels {os.getenv('GITHUB_RUN_ID', '')}"],
        check=True
    )
    subprocess.run(["git", "push"], check=True)

def public_url(path):
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    rel = path.relative_to(ROOT).as_posix()
    return f"https://raw.githubusercontent.com/{repo}/{branch}/{rel}"

def wait_until_public(url):
    for _ in range(12):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and r.content:
                return
        except Exception:
            pass
        time.sleep(5)
    raise RuntimeError(f"generated image did not become public: {url}")

def create_buffer_draft(channel_id, text, urls):
    assets = [{"image": {"url": u}} for u in urls]
    data = buffer_request(
        """
        mutation CreateDraft($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post { id text }
            }
            ... on MutationError {
              message
            }
          }
        }
        """,
        {
            "input": {
                "text": text,
                "channelId": channel_id,
                "schedulingType": "automatic",
                "mode": "addToQueue",
                "saveToDraft": True,
                "aiAssisted": True,
                "assets": assets,
            }
        },
    )
    result = data["createPost"]
    if result.get("message"):
        raise RuntimeError(result["message"])
    return result["post"]

def main():
    download(ANTON_URL, ANTON)
    download(INTER_URL, INTER)

    channel_id = get_linkedin()
    trends = collect_trends()
    previous_posts = get_recent_buffer_posts()
    topic_history = load_topic_history()
    selected_lanes = choose_topic_lanes(topic_history)
    posts = generate_candidates(
        make_prompt(trends, previous_posts, selected_lanes, topic_history),
        selected_lanes
    )

    print("Running mandatory fact-check + capitalization pass...")
    checked_posts = []
    for idx, post in enumerate(posts, start=1):
        print(f"Fact-checking candidate {idx}/{len(posts)}")
        checked_posts.append(fact_check_candidate(post, trends))
    posts = checked_posts

    run_id = os.getenv("GITHUB_RUN_ID", str(int(time.time())))
    run_dir = ROOT / "generated" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rendered = []
    for p_idx, post in enumerate(posts, start=1):
        post = ensure_carousel(post)
        post_dir = run_dir / f"post_{p_idx:02d}"
        post_dir.mkdir(parents=True, exist_ok=True)
        slides = post.get("carousel", {}).get("slides", [])[:8]
        slides[-1]["signature"] = True

        paths = []
        for s_idx, slide in enumerate(slides):
            out = post_dir / f"slide_{s_idx + 1:02d}.png"
            render_slide(slide, s_idx, out)
            paths.append(out)
        rendered.append((post, paths))

    # Persist themes independently of Buffer. Deleted drafts must not erase topic memory.
    save_topic_history([post for post, _ in rendered])

    # Buffer needs public URLs, so publish the generated PNG files + topic history first.
    git_publish_generated()

    for post, paths in rendered:
        urls = [public_url(p) for p in paths]
        wait_until_public(urls[0])
        created = create_buffer_draft(channel_id, post["text"].strip(), urls)
        print("BUFFER DRAFT:", created["id"])
        print("MEDIA:", len(urls))

    print(f"DONE: {len(rendered)} drafts with carousels created")

if __name__ == "__main__":
    main()
