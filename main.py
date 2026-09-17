
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


PMI Lexicon of Project Management Terms, Version 5.0 —
https://www.pmi.org/-/media/pmi/documents/registered/pdf/pmbok-standards/pmi-lexicon-pm-terms.pdf
- a project life cycle is the series of phases a project passes through from start to completion
- a project charter formally authorizes the existence of a project and provides the PM authority to apply organizational resources
- project governance is the framework, functions and processes that guide project-management activities toward project objectives

PMI article on risks, issues and changes —
https://www.pmi.org/learning/library/risks-issues-changes-forms-logs-1078
- a risk concerns something uncertain in the future
- an issue concerns something happening in the present that needs resolution
- a proposed change should be evaluated for impact on budget, schedule, risk and quality

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

HOOK_STYLES = [
    {"id":"metaphor", "rule":"open with one fresh concrete metaphor or physical image; never reuse parent/baby/backflip/cortisol metaphors"},
    {"id":"direct_claim", "rule":"open with a short confident PM claim, without 'hot take' or 'unpopular opinion'"},
    {"id":"question", "rule":"open with one specific question that creates tension; answer it quickly"},
    {"id":"micro_scene", "rule":"open inside a tiny recognizable project scene or moment, without pretending it literally happened to Matvei"},
    {"id":"reframe", "rule":"open by redefining a familiar PM concept in a surprising but defensible way"},
    {"id":"contrast", "rule":"open with a crisp contrast between two things people often confuse"},
    {"id":"rule_of_thumb", "rule":"open with a practical rule of thumb, then explain where it helps and where it breaks"},
    {"id":"failure_mode", "rule":"open with a specific project failure mode, not a personal anecdote"},
    {"id":"tiny_list", "rule":"open with a compact 2-3 item pattern, then build one thesis from it"},
    {"id":"counterfactual", "rule":"open with a 'what if' or counterfactual project situation"},
    {"id":"object_lesson", "rule":"open with an everyday object or system and connect it to PM without forcing the analogy"},
    {"id":"definition", "rule":"open with a deliberately plain one-line definition in Matvei's voice, then complicate it"},
    {"id":"symptom", "rule":"open with a symptom that tells you a project has a deeper problem"},
    {"id":"decision", "rule":"open with a decision a PM has to make, not with a general observation"},
    {"id":"myth_without_label", "rule":"open by stating a common belief and immediately showing the catch; do not say 'myth'"},
    {"id":"numberless_pattern", "rule":"open with a recurring pattern from project work, with no CV metrics or statistics"},
    {"id":"one_sentence_story", "rule":"open with a one-sentence generic project story, clearly illustrative rather than autobiographical"},
    {"id":"provocative_plain", "rule":"open with a mildly provocative plain sentence, no theatrics, no ragebait"},
    {"id":"cause_effect", "rule":"open with an unexpected cause-and-effect relationship in project work"},
    {"id":"anti_template", "rule":"open in a form that does not resemble any other assigned hook in this batch; keep it natural"},
]

FORBIDDEN_OPENINGS = (
    "we love", "we all", "let's talk", "lets talk", "here's the thing", "heres the thing",
    "hot take", "unpopular opinion", "as a project manager", "as a pm", "i've managed",
    "ive managed", "in my experience", "one thing i've learned", "one thing ive learned"
)


# A deliberately broad editorial map. Python picks the lanes BEFORE Gemini writes,
# so the model cannot keep falling back to the same stakeholder/automation themes.
# Each lane is tied to verified experience anchors above.
TOPIC_LANES = [{'id': 'why_project_exists',
  'domain': 'initiation',
  'bucket': 'core',
  'title': 'before planning, define why the project exists',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'how a PM turns an incoming request into a reasoned project rather than a task list'},
 {'id': 'project_charter_lite',
  'domain': 'initiation',
  'bucket': 'core',
  'title': 'most projects need a one-page charter before they need a giant plan',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'minimum useful alignment: objective, owner, scope, constraints, success, major risks'},
 {'id': 'kickoff_is_not_start',
  'domain': 'initiation',
  'bucket': 'core',
  'title': 'a kickoff meeting is not the same thing as project initiation',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'the work that must be settled before the calendar invite'},
 {'id': 'sponsor_before_schedule',
  'domain': 'initiation',
  'bucket': 'core',
  'title': 'a project without a real sponsor has a hidden governance problem',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'why authority and backing matter before dates become meaningful'},
 {'id': 'output_vs_outcome',
  'domain': 'objectives_success',
  'bucket': 'core',
  'title': 'deliverables are not the same as success',
  'anchors': ['A1', 'A6', 'A10'],
  'angle': 'a project can ship everything and still miss the reason it existed'},
 {'id': 'success_criteria_early',
  'domain': 'objectives_success',
  'bucket': 'core',
  'title': 'success criteria are easiest to define before everyone is emotionally attached to the solution',
  'anchors': ['A1', 'A6', 'A10'],
  'angle': 'why measurable acceptance should precede execution'},
 {'id': 'one_sentence_goal',
  'domain': 'objectives_success',
  'bucket': 'core',
  'title': 'if the project goal needs a paragraph, the team will probably execute four different projects',
  'anchors': ['A1', 'A6', 'A10'],
  'angle': 'using a simple objective as a filter for trade-offs'},
 {'id': 'done_means_what',
  'domain': 'objectives_success',
  'bucket': 'core',
  'title': '"done" needs a definition at project level, not only task level',
  'anchors': ['A1', 'A6', 'A10'],
  'angle': 'how teams discover too late that delivery and acceptance are different things'},
 {'id': 'scope_is_boundary',
  'domain': 'scope',
  'bucket': 'core',
  'title': 'scope is a boundary, not a shopping list',
  'anchors': ['A1', 'A5', 'A12'],
  'angle': 'the useful part of scope is what it prevents from silently entering'},
 {'id': 'out_of_scope',
  'domain': 'scope',
  'bucket': 'core',
  'title': 'out-of-scope is one of the most underrated project documents',
  'anchors': ['A1', 'A5', 'A12'],
  'angle': 'negative space makes later change conversations less emotional'},
 {'id': 'scope_before_solution',
  'domain': 'scope',
  'bucket': 'core',
  'title': 'define the problem boundary before falling in love with the solution',
  'anchors': ['A1', 'A5', 'A12'],
  'angle': 'keeping intent stable while execution can still change'},
 {'id': 'scope_drift_small',
  'domain': 'scope',
  'bucket': 'core',
  'title': 'scope rarely explodes in one dramatic moment',
  'anchors': ['A1', 'A5', 'A12'],
  'angle': 'how tiny reasonable additions accumulate into a different project'},
 {'id': 'scope_owner',
  'domain': 'scope',
  'bucket': 'core',
  'title': 'somebody has to own the decision that changes scope',
  'anchors': ['A1', 'A5', 'A12'],
  'angle': 'change without decision ownership becomes invisible work'},
 {'id': 'assumptions_visible',
  'domain': 'assumptions_constraints',
  'bucket': 'core',
  'title': 'assumptions are future arguments unless they are written down',
  'anchors': ['A1', 'A2', 'A5', 'A10'],
  'angle': 'turning invisible beliefs into things the team can test'},
 {'id': 'constraint_not_excuse',
  'domain': 'assumptions_constraints',
  'bucket': 'core',
  'title': 'a constraint is useful when it changes the plan',
  'anchors': ['A1', 'A2', 'A5', 'A10'],
  'angle': 'budget, time and people should shape choices rather than appear as excuses later'},
 {'id': 'unknowns_register',
  'domain': 'assumptions_constraints',
  'bucket': 'core',
  'title': 'unknowns deserve a place next to tasks',
  'anchors': ['A1', 'A2', 'A5', 'A10'],
  'angle': 'planning the discovery of information, not pretending it already exists'},
 {'id': 'constraint_priority',
  'domain': 'assumptions_constraints',
  'bucket': 'core',
  'title': 'when everything is fixed, something is actually not fixed',
  'anchors': ['A1', 'A2', 'A5', 'A10'],
  'angle': 'surfacing which constraint will move when reality arrives'},
 {'id': 'requirement_test',
  'domain': 'requirements',
  'bucket': 'core',
  'title': 'a requirement should survive the question: how will we know this is met?',
  'anchors': ['A1', 'A6', 'A7'],
  'angle': 'acceptance logic as a cure for vague requests'},
 {'id': 'requirements_are_decisions',
  'domain': 'requirements',
  'bucket': 'core',
  'title': 'requirements are accumulated decisions, not notes from a meeting',
  'anchors': ['A1', 'A6', 'A7'],
  'angle': 'keeping rationale and ownership with the requirement'},
 {'id': 'must_should_could',
  'domain': 'requirements',
  'bucket': 'core',
  'title': 'priority words only work if people accept that some things will not ship',
  'anchors': ['A1', 'A6', 'A7'],
  'angle': 'forcing real trade-offs instead of decorative labels'},
 {'id': 'brief_vs_requirements',
  'domain': 'requirements',
  'bucket': 'core',
  'title': 'a brief explains intent; requirements make delivery testable',
  'anchors': ['A1', 'A6', 'A7'],
  'angle': 'why both can be necessary without becoming bureaucracy'},
 {'id': 'estimate_is_not_promise',
  'domain': 'estimation',
  'bucket': 'core',
  'title': 'an estimate is information, not a blood oath',
  'anchors': ['A1', 'A5', 'A6', 'A7'],
  'angle': 'how to keep uncertainty visible without making the plan useless'},
 {'id': 'estimate_inputs',
  'domain': 'estimation',
  'bucket': 'core',
  'title': 'bad estimates often start with bad inputs, not bad specialists',
  'anchors': ['A1', 'A5', 'A6', 'A7'],
  'angle': 'what a PM should clarify before asking for a number'},
 {'id': 'estimate_range',
  'domain': 'estimation',
  'bucket': 'core',
  'title': 'a range can be more honest than a precise number early on',
  'anchors': ['A1', 'A5', 'A6', 'A7'],
  'angle': 'communicating uncertainty without giving up accountability'},
 {'id': 'estimate_review',
  'domain': 'estimation',
  'bucket': 'core',
  'title': 'an estimate should change when the work becomes better understood',
  'anchors': ['A1', 'A5', 'A6', 'A7'],
  'angle': 'why re-estimation is not automatically failure'},
 {'id': 'pm_owns_estimation_process',
  'domain': 'estimation',
  'bucket': 'core',
  'title': 'the PM owns the estimation process, not every estimate',
  'anchors': ['A1', 'A5', 'A6', 'A7'],
  'angle': 'getting the right people, assumptions and dependencies into the number'},
 {'id': 'plan_is_model',
  'domain': 'planning',
  'bucket': 'core',
  'title': 'a project plan is a model of reality, not reality',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'why a plan is useful precisely because it can be updated'},
 {'id': 'plan_decisions_first',
  'domain': 'planning',
  'bucket': 'core',
  'title': 'plans should capture decisions before decoration',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'owners, sequence and constraints matter more than pretty Gantt bars'},
 {'id': 'planning_horizon',
  'domain': 'planning',
  'bucket': 'core',
  'title': 'not every part of a project deserves the same level of detail today',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'rolling detail as uncertainty falls'},
 {'id': 'plan_for_replan',
  'domain': 'planning',
  'bucket': 'core',
  'title': 'replanning is part of planning',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'building a plan that can absorb changed priorities without becoming fiction'},
 {'id': 'plan_owner',
  'domain': 'planning',
  'bucket': 'core',
  'title': 'if nobody knows who maintains the plan, there is no plan',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'the update path is part of the system'},
 {'id': 'dates_need_logic',
  'domain': 'scheduling',
  'bucket': 'core',
  'title': 'a date without scheduling logic is just a wish with formatting',
  'anchors': ['A2', 'A3', 'A8', 'A9'],
  'angle': 'sequence, effort, availability and dependencies behind a deadline'},
 {'id': 'calendar_vs_effort',
  'domain': 'scheduling',
  'bucket': 'core',
  'title': 'three days of effort can take three weeks of calendar',
  'anchors': ['A2', 'A3', 'A8', 'A9'],
  'angle': 'availability, queues and approvals change elapsed time'},
 {'id': 'buffer_visibility',
  'domain': 'scheduling',
  'bucket': 'core',
  'title': 'buffers work better when everyone knows what they protect',
  'anchors': ['A2', 'A3', 'A8', 'A9'],
  'angle': 'using contingency intentionally instead of hiding padding'},
 {'id': 'schedule_compression',
  'domain': 'scheduling',
  'bucket': 'core',
  'title': 'making the date earlier does not make the work shorter',
  'anchors': ['A2', 'A3', 'A8', 'A9'],
  'angle': 'what actually has to change when a deadline is pulled in'},
 {'id': 'late_start_early_finish',
  'domain': 'scheduling',
  'bucket': 'core',
  'title': 'starting everything immediately can make everything later',
  'anchors': ['A2', 'A3', 'A8', 'A9'],
  'angle': 'queues and WIP as a scheduling problem'},
 {'id': 'milestone_is_evidence',
  'domain': 'milestones',
  'bucket': 'core',
  'title': 'a milestone should prove something changed',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'using observable outcomes instead of arbitrary calendar markers'},
 {'id': 'milestone_owner',
  'domain': 'milestones',
  'bucket': 'core',
  'title': 'a milestone without an owner is a future status question',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'ownership attached to the evidence of completion'},
 {'id': 'milestone_decision',
  'domain': 'milestones',
  'bucket': 'core',
  'title': 'some milestones should be decisions, not deliverables',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'decision gates as real schedule events'},
 {'id': 'milestone_health',
  'domain': 'milestones',
  'bucket': 'core',
  'title': 'green milestones can hide a red project',
  'anchors': ['A1', 'A8', 'A10'],
  'angle': 'why local completion does not equal overall health'},
 {'id': 'dependency_is_commitment',
  'domain': 'dependencies',
  'bucket': 'core',
  'title': 'a dependency is a commitment between two pieces of work',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'making handoffs explicit instead of hoping they happen'},
 {'id': 'dependency_owner',
  'domain': 'dependencies',
  'bucket': 'core',
  'title': 'every dependency needs someone watching both sides',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'why task ownership alone misses cross-team risk'},
 {'id': 'dependency_date',
  'domain': 'dependencies',
  'bucket': 'core',
  'title': 'dependencies need dates, not just arrows',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'turning architecture diagrams into delivery logic'},
 {'id': 'hidden_dependencies',
  'domain': 'dependencies',
  'bucket': 'core',
  'title': 'the most expensive dependencies are often approvals, access and decisions',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'non-production dependencies can dominate the schedule'},
 {'id': 'dependency_recheck',
  'domain': 'dependencies',
  'bucket': 'core',
  'title': 'dependencies change when scope and sequence change',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'why the map has to move with the plan'},
 {'id': 'critical_path_not_biggest',
  'domain': 'critical_path',
  'bucket': 'core',
  'title': 'the biggest task is not necessarily the task that controls the finish date',
  'anchors': ['A3', 'A8', 'A10'],
  'angle': 'sequence and dependency can matter more than effort'},
 {'id': 'critical_path_changes',
  'domain': 'critical_path',
  'bucket': 'core',
  'title': 'the path controlling the date can change mid-project',
  'anchors': ['A3', 'A8', 'A10'],
  'angle': 'why schedule attention has to move as work moves'},
 {'id': 'critical_waiting',
  'domain': 'critical_path',
  'bucket': 'core',
  'title': 'waiting can sit on the critical path too',
  'anchors': ['A3', 'A8', 'A10'],
  'angle': 'approvals and decisions count as project time'},
 {'id': 'critical_path_focus',
  'domain': 'critical_path',
  'bucket': 'core',
  'title': 'not every late task threatens the project date',
  'anchors': ['A3', 'A8', 'A10'],
  'angle': 'separating noise from schedule impact'},
 {'id': 'risk_is_future',
  'domain': 'risk',
  'bucket': 'core',
  'title': 'a risk is useful before it becomes a problem',
  'anchors': ['A1', 'A5', 'A8', 'A10'],
  'angle': 'turning uncertainty into an owner, trigger and response'},
 {'id': 'risk_trigger',
  'domain': 'risk',
  'bucket': 'core',
  'title': 'a risk without a trigger is hard to manage',
  'anchors': ['A1', 'A5', 'A8', 'A10'],
  'angle': 'what observable sign tells you the contingency should start'},
 {'id': 'risk_owner',
  'domain': 'risk',
  'bucket': 'core',
  'title': 'putting a risk in a register is not assigning responsibility',
  'anchors': ['A1', 'A5', 'A8', 'A10'],
  'angle': 'ownership means monitoring and acting, not merely naming'},
 {'id': 'risk_response',
  'domain': 'risk',
  'bucket': 'core',
  'title': '"watch closely" is not a risk response',
  'anchors': ['A1', 'A5', 'A8', 'A10'],
  'angle': 'what mitigation, avoidance, transfer or acceptance looks like in practical delivery'},
 {'id': 'risk_budget',
  'domain': 'risk',
  'bucket': 'core',
  'title': 'risk consumes schedule and budget even before it happens',
  'anchors': ['A1', 'A5', 'A8', 'A10'],
  'angle': 'why contingency is part of planning rather than pessimism'},
 {'id': 'risk_retire',
  'domain': 'risk',
  'bucket': 'core',
  'title': 'risks should die when the uncertainty dies',
  'anchors': ['A1', 'A5', 'A8', 'A10'],
  'angle': 'keeping risk lists useful instead of accumulating museum exhibits'},
 {'id': 'risk_vs_issue',
  'domain': 'issues_escalation',
  'bucket': 'core',
  'title': 'once the thing happened, stop calling it a risk',
  'anchors': ['A1', 'A5', 'A8', 'A10', 'A12'],
  'angle': 'switching from probability management to resolution'},
 {'id': 'issue_owner',
  'domain': 'issues_escalation',
  'bucket': 'core',
  'title': 'an issue needs an owner and a next decision',
  'anchors': ['A1', 'A5', 'A8', 'A10', 'A12'],
  'angle': 'status descriptions do not resolve anything'},
 {'id': 'escalate_early',
  'domain': 'issues_escalation',
  'bucket': 'core',
  'title': 'escalation is cheaper before everyone is angry',
  'anchors': ['A1', 'A5', 'A8', 'A10', 'A12'],
  'angle': 'raising a constraint while options still exist'},
 {'id': 'escalation_packet',
  'domain': 'issues_escalation',
  'bucket': 'core',
  'title': 'a useful escalation contains context, options and a decision request',
  'anchors': ['A1', 'A5', 'A8', 'A10', 'A12'],
  'angle': 'making it easy for the right person to unblock the project'},
 {'id': 'red_status',
  'domain': 'issues_escalation',
  'bucket': 'core',
  'title': 'red is a management signal, not a confession of failure',
  'anchors': ['A1', 'A5', 'A8', 'A10', 'A12'],
  'angle': 'using status to create action instead of protect appearances'},
 {'id': 'decision_log',
  'domain': 'decisions',
  'bucket': 'core',
  'title': 'projects forget decisions faster than they forget tasks',
  'anchors': ['A1', 'A8', 'A10', 'A12'],
  'angle': 'why rationale and owner matter months later'},
 {'id': 'decision_deadline',
  'domain': 'decisions',
  'bucket': 'core',
  'title': 'decisions need due dates too',
  'anchors': ['A1', 'A8', 'A10', 'A12'],
  'angle': 'a pending decision can be a schedule dependency'},
 {'id': 'reversible_decisions',
  'domain': 'decisions',
  'bucket': 'core',
  'title': 'not every decision deserves the same ceremony',
  'anchors': ['A1', 'A8', 'A10', 'A12'],
  'angle': 'matching decision process to reversibility and impact'},
 {'id': 'decision_owner_vs_consensus',
  'domain': 'decisions',
  'bucket': 'core',
  'title': 'consensus is not always a decision mechanism',
  'anchors': ['A1', 'A8', 'A10', 'A12'],
  'angle': 'clear decision rights prevent endless alignment loops'},
 {'id': 'decision_quality',
  'domain': 'decisions',
  'bucket': 'core',
  'title': 'a fast bad decision and a slow perfect decision can both kill a project',
  'anchors': ['A1', 'A8', 'A10', 'A12'],
  'angle': 'timeliness as part of decision quality'},
 {'id': 'change_is_not_bad',
  'domain': 'change_control',
  'bucket': 'core',
  'title': 'change is normal; invisible change is expensive',
  'anchors': ['A5', 'A8', 'A12'],
  'angle': 'the point of change control is visibility, not punishment'},
 {'id': 'change_impact',
  'domain': 'change_control',
  'bucket': 'core',
  'title': 'every change should answer what moves with it',
  'anchors': ['A5', 'A8', 'A12'],
  'angle': 'schedule, cost, risk, quality and other deliverables as connected consequences'},
 {'id': 'change_small',
  'domain': 'change_control',
  'bucket': 'core',
  'title': 'small changes need proportionate control',
  'anchors': ['A5', 'A8', 'A12'],
  'angle': 'avoiding both chaos and bureaucracy'},
 {'id': 'change_log',
  'domain': 'change_control',
  'bucket': 'core',
  'title': 'a change log is memory for the project contract with reality',
  'anchors': ['A5', 'A8', 'A12'],
  'angle': 'keeping cumulative drift visible'},
 {'id': 'change_decision',
  'domain': 'change_control',
  'bucket': 'core',
  'title': 'a change request is a decision package, not a form',
  'anchors': ['A5', 'A8', 'A12'],
  'angle': 'framing options and impacts so somebody can choose'},
 {'id': 'role_clarity',
  'domain': 'roles_governance',
  'bucket': 'core',
  'title': 'roles become important exactly where work crosses boundaries',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'who recommends, decides, executes and approves'},
 {'id': 'governance_light',
  'domain': 'roles_governance',
  'bucket': 'core',
  'title': 'governance should get heavier only when risk and complexity justify it',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'minimum viable control for the project at hand'},
 {'id': 'sponsor_role',
  'domain': 'roles_governance',
  'bucket': 'core',
  'title': 'the sponsor is not just the person invited to the kickoff',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'what the project needs from authority above the PM'},
 {'id': 'raci_limits',
  'domain': 'roles_governance',
  'bucket': 'core',
  'title': 'a matrix cannot rescue a team that avoids decisions',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'roles tools help only when behavior matches them'},
 {'id': 'stakeholder_interest_power',
  'domain': 'stakeholders',
  'bucket': 'core',
  'title': 'not every stakeholder needs the same communication',
  'anchors': ['A3', 'A10', 'A12'],
  'angle': 'attention based on influence, impact and decision role'},
 {'id': 'stakeholder_expectation',
  'domain': 'stakeholders',
  'bucket': 'core',
  'title': 'expectation gaps become delivery problems',
  'anchors': ['A3', 'A10', 'A12'],
  'angle': 'alignment as ongoing work, not a kickoff artifact'},
 {'id': 'stakeholder_conflict',
  'domain': 'stakeholders',
  'bucket': 'core',
  'title': 'two valid stakeholder goals can still conflict',
  'anchors': ['A3', 'A10', 'A12'],
  'angle': 'making the trade-off explicit instead of promising both'},
 {'id': 'stakeholder_change',
  'domain': 'stakeholders',
  'bucket': 'core',
  'title': 'stakeholder maps are not static',
  'anchors': ['A3', 'A10', 'A12'],
  'angle': 'new people, changed influence and changed incentives over long programs'},
 {'id': 'communication_action',
  'domain': 'communication',
  'bucket': 'core',
  'title': "project communication should change somebody's next action",
  'anchors': ['A1', 'A3', 'A8', 'A10', 'A12'],
  'angle': 'information without consequence is often noise'},
 {'id': 'audience_format',
  'domain': 'communication',
  'bucket': 'core',
  'title': 'the same project truth needs different formats for different audiences',
  'anchors': ['A1', 'A3', 'A8', 'A10', 'A12'],
  'angle': 'detail for the team, decisions for leaders, evidence for clients'},
 {'id': 'bad_news_speed',
  'domain': 'communication',
  'bucket': 'core',
  'title': 'bad news ages badly',
  'anchors': ['A1', 'A3', 'A8', 'A10', 'A12'],
  'angle': 'why delay usually reduces options and trust'},
 {'id': 'written_vs_sync',
  'domain': 'communication',
  'bucket': 'core',
  'title': 'some conversations should be meetings; some should become durable text',
  'anchors': ['A1', 'A3', 'A8', 'A10', 'A12'],
  'angle': 'choosing medium based on ambiguity, speed and future memory'},
 {'id': 'communication_contract',
  'domain': 'communication',
  'bucket': 'core',
  'title': 'teams benefit from knowing where decisions, updates and urgent issues live',
  'anchors': ['A1', 'A3', 'A8', 'A10', 'A12'],
  'angle': 'reducing search and duplicate communication'},
 {'id': 'meeting_output',
  'domain': 'meetings',
  'bucket': 'core',
  'title': 'a meeting without an output is a social event with a calendar invite',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'decisions, owners and next actions as the minimum result'},
 {'id': 'meeting_attendees',
  'domain': 'meetings',
  'bucket': 'core',
  'title': 'inviting everyone is often a sign the decision structure is unclear',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'attendance by role in the conversation'},
 {'id': 'meeting_vs_async',
  'domain': 'meetings',
  'bucket': 'core',
  'title': 'meetings are expensive bandwidth',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'when ambiguity deserves sync and when status does not'},
 {'id': 'meeting_followup',
  'domain': 'meetings',
  'bucket': 'core',
  'title': 'the real meeting ends when the actions are captured',
  'anchors': ['A1', 'A3', 'A8', 'A10'],
  'angle': 'preventing verbal alignment from evaporating'},
 {'id': 'docs_as_memory',
  'domain': 'documentation',
  'bucket': 'core',
  'title': 'documentation is external project memory',
  'anchors': ['A1', 'A8', 'A9', 'A10'],
  'angle': 'writing down what the team should not have to rediscover'},
 {'id': 'decision_docs',
  'domain': 'documentation',
  'bucket': 'core',
  'title': 'document decisions, not every breath the project takes',
  'anchors': ['A1', 'A8', 'A9', 'A10'],
  'angle': 'high-value records over transcript culture'},
 {'id': 'doc_owner',
  'domain': 'documentation',
  'bucket': 'core',
  'title': 'every living document needs an update path',
  'anchors': ['A1', 'A8', 'A9', 'A10'],
  'angle': 'a source of truth dies when nobody owns freshness'},
 {'id': 'documentation_level',
  'domain': 'documentation',
  'bucket': 'core',
  'title': 'documentation should scale with consequence and handoff count',
  'anchors': ['A1', 'A8', 'A9', 'A10'],
  'angle': 'how to avoid both tribal knowledge and paperwork theatre'},
 {'id': 'status_report_decision',
  'domain': 'reporting',
  'bucket': 'core',
  'title': 'a status report should help somebody decide or act',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'moving from activity lists to project health'},
 {'id': 'percent_complete',
  'domain': 'reporting',
  'bucket': 'core',
  'title': 'percent complete can hide the hardest 10 percent',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'using evidence and milestones instead of comforting arithmetic'},
 {'id': 'status_color',
  'domain': 'reporting',
  'bucket': 'core',
  'title': 'green needs a definition',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'making status criteria consistent enough to trust'},
 {'id': 'forecast_not_history',
  'domain': 'reporting',
  'bucket': 'core',
  'title': 'good reporting is partly a forecast',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'what is likely to happen next matters more than what happened last week'},
 {'id': 'report_exception',
  'domain': 'reporting',
  'bucket': 'core',
  'title': 'leaders often need exceptions, not the entire task list',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'surfacing deviations, decisions and risks'},
 {'id': 'acceptance_before_build',
  'domain': 'quality_acceptance',
  'bucket': 'core',
  'title': 'acceptance criteria belong near the beginning',
  'anchors': ['A6', 'A7', 'A8', 'A10'],
  'angle': 'quality gets easier when everyone knows what pass means'},
 {'id': 'quality_owner',
  'domain': 'quality_acceptance',
  'bucket': 'core',
  'title': 'quality cannot be thrown over the wall to QA',
  'anchors': ['A6', 'A7', 'A8', 'A10'],
  'angle': 'the whole delivery system creates the result'},
 {'id': 'review_budget',
  'domain': 'quality_acceptance',
  'bucket': 'core',
  'title': 'reviews consume time and should be planned',
  'anchors': ['A6', 'A7', 'A8', 'A10'],
  'angle': 'feedback cycles are schedule events, not free space'},
 {'id': 'definition_done_project',
  'domain': 'quality_acceptance',
  'bucket': 'core',
  'title': 'project-level done includes acceptance and handover',
  'anchors': ['A6', 'A7', 'A8', 'A10'],
  'angle': 'completion beyond internal task closure'},
 {'id': 'quality_tradeoff',
  'domain': 'quality_acceptance',
  'bucket': 'core',
  'title': 'quality trade-offs should be explicit decisions',
  'anchors': ['A6', 'A7', 'A8', 'A10'],
  'angle': 'when time or budget pressure changes the bar, name the consequence'},
 {'id': 'handover_design',
  'domain': 'handover_closure',
  'bucket': 'core',
  'title': 'handover should be designed from the start',
  'anchors': ['A6', 'A9', 'A10', 'A13'],
  'angle': 'the future owner needs context, assets, decisions and known limitations'},
 {'id': 'closure_is_work',
  'domain': 'handover_closure',
  'bucket': 'core',
  'title': 'project closure is actual project work',
  'anchors': ['A6', 'A9', 'A10', 'A13'],
  'angle': 'acceptance, loose ends, economics, access and documentation do not close themselves'},
 {'id': 'unfinished_tail',
  'domain': 'handover_closure',
  'bucket': 'core',
  'title': 'the last 5 percent can be the most operationally expensive',
  'anchors': ['A6', 'A9', 'A10', 'A13'],
  'angle': 'small unresolved items after launch create long tails'},
 {'id': 'close_decisions',
  'domain': 'handover_closure',
  'bucket': 'core',
  'title': 'closure should record what remains intentionally unresolved',
  'anchors': ['A6', 'A9', 'A10', 'A13'],
  'angle': 'known debt is different from forgotten debt'},
 {'id': 'celebrate_close',
  'domain': 'handover_closure',
  'bucket': 'core',
  'title': 'closing well includes recognizing the team',
  'anchors': ['A6', 'A9', 'A10', 'A13'],
  'angle': 'why psychological closure matters after sustained delivery'},
 {'id': 'retro_to_change',
  'domain': 'retrospectives',
  'bucket': 'core',
  'title': 'a retro is useless if nothing changes afterward',
  'anchors': ['A9', 'A13', 'A17'],
  'angle': 'turning reflection into one or two operating experiments'},
 {'id': 'retro_specific',
  'domain': 'retrospectives',
  'bucket': 'core',
  'title': '"communication could be better" is not a retro insight',
  'anchors': ['A9', 'A13', 'A17'],
  'angle': 'finding a concrete failure mechanism instead of vague sentiment'},
 {'id': 'retro_system',
  'domain': 'retrospectives',
  'bucket': 'core',
  'title': 'retrospectives should inspect the system, not hunt for a guilty person',
  'anchors': ['A9', 'A13', 'A17'],
  'angle': 'process, incentives and constraints behind failure'},
 {'id': 'lessons_reuse',
  'domain': 'retrospectives',
  'bucket': 'core',
  'title': 'lessons learned should change the next project template',
  'anchors': ['A9', 'A13', 'A17'],
  'angle': 'institutional learning rather than archive storage'},
 {'id': 'budget_is_plan',
  'domain': 'budget_economics',
  'bucket': 'core',
  'title': 'a budget is another version of the project plan',
  'anchors': ['A5', 'A9', 'A10', 'A12'],
  'angle': 'money encodes assumptions about effort, scope and timing'},
 {'id': 'forecast_budget',
  'domain': 'budget_economics',
  'bucket': 'core',
  'title': 'budget control is forecasting, not just recording spend',
  'anchors': ['A5', 'A9', 'A10', 'A12'],
  'angle': 'seeing the overrun while options still exist'},
 {'id': 'cost_of_delay',
  'domain': 'budget_economics',
  'bucket': 'core',
  'title': 'delay has a cost even when nobody sends an invoice for it',
  'anchors': ['A5', 'A9', 'A10', 'A12'],
  'angle': 'capacity, opportunity and downstream impact'},
 {'id': 'tradeoff_triangle',
  'domain': 'budget_economics',
  'bucket': 'core',
  'title': 'when scope, time and cost all refuse to move, quality or people usually pay',
  'anchors': ['A5', 'A9', 'A10', 'A12'],
  'angle': 'making the hidden variable explicit'},
 {'id': 'contingency_money',
  'domain': 'budget_economics',
  'bucket': 'core',
  'title': 'contingency is not spare money',
  'anchors': ['A5', 'A9', 'A10', 'A12'],
  'angle': 'protecting uncertainty rather than treating reserve as available scope'},
 {'id': 'capacity_not_headcount',
  'domain': 'resource_capacity',
  'bucket': 'core',
  'title': 'headcount is not capacity',
  'anchors': ['A2', 'A3', 'A7', 'A9', 'A10'],
  'angle': 'availability, skills, context and competing commitments change what a team can actually do'},
 {'id': 'resource_loading',
  'domain': 'resource_capacity',
  'bucket': 'core',
  'title': 'resource plans should show overload before people feel it',
  'anchors': ['A2', 'A3', 'A7', 'A9', 'A10'],
  'angle': 'capacity as an early-warning system'},
 {'id': 'shared_resource',
  'domain': 'resource_capacity',
  'bucket': 'core',
  'title': 'shared specialists create portfolio dependencies',
  'anchors': ['A2', 'A3', 'A7', 'A9', 'A10'],
  'angle': 'one person can become the critical path of several projects'},
 {'id': 'resource_substitution',
  'domain': 'resource_capacity',
  'bucket': 'core',
  'title': 'people are not interchangeable cells in a spreadsheet',
  'anchors': ['A2', 'A3', 'A7', 'A9', 'A10'],
  'angle': 'skill shape and project context matter'},
 {'id': 'capacity_buffer',
  'domain': 'resource_capacity',
  'bucket': 'core',
  'title': '100 percent planned utilization leaves no room for reality',
  'anchors': ['A2', 'A3', 'A7', 'A9', 'A10'],
  'angle': 'interruptions, support and uncertainty need somewhere to go'},
 {'id': 'priority_means_no',
  'domain': 'prioritization',
  'bucket': 'core',
  'title': 'priority only exists when something else loses',
  'anchors': ['A2', 'A3', 'A9', 'A10'],
  'angle': 'why ranking without consequence is theatre'},
 {'id': 'priority_levels',
  'domain': 'prioritization',
  'bucket': 'core',
  'title': 'P1 through P5 mean nothing if all five start today',
  'anchors': ['A2', 'A3', 'A9', 'A10'],
  'angle': 'connecting priority to resource and sequence decisions'},
 {'id': 'urgent_important_project',
  'domain': 'prioritization',
  'bucket': 'core',
  'title': 'urgency can hijack the project portfolio',
  'anchors': ['A2', 'A3', 'A9', 'A10'],
  'angle': 'protecting important work from constant local emergencies'},
 {'id': 'repriority_cost',
  'domain': 'prioritization',
  'bucket': 'core',
  'title': 'changing priority has a switching cost',
  'anchors': ['A2', 'A3', 'A9', 'A10'],
  'angle': 'replanning, rebriefing and lost context as real project work'},
 {'id': 'priority_owner',
  'domain': 'prioritization',
  'bucket': 'core',
  'title': 'someone must be allowed to resolve competing priorities',
  'anchors': ['A2', 'A3', 'A9', 'A10'],
  'angle': 'avoiding escalation loops between equally loud requests'},
 {'id': 'portfolio_vs_project',
  'domain': 'portfolio',
  'bucket': 'core',
  'title': 'a healthy project can live inside an unhealthy portfolio',
  'anchors': ['A2', 'A8', 'A9'],
  'angle': 'local green status can hide organization-level overload'},
 {'id': 'portfolio_dependencies',
  'domain': 'portfolio',
  'bucket': 'core',
  'title': 'projects compete and depend on each other even when their plans do not show it',
  'anchors': ['A2', 'A8', 'A9'],
  'angle': 'shared people, systems and decision-makers'},
 {'id': 'stop_start_continue',
  'domain': 'portfolio',
  'bucket': 'core',
  'title': 'portfolio management includes stopping work',
  'anchors': ['A2', 'A8', 'A9'],
  'angle': 'why killing or pausing initiatives can be a delivery skill'},
 {'id': 'portfolio_balance',
  'domain': 'portfolio',
  'bucket': 'core',
  'title': 'a portfolio needs different kinds of risk and horizon',
  'anchors': ['A2', 'A8', 'A9'],
  'angle': 'why every initiative cannot be the urgent flagship'},
 {'id': 'team_clarity',
  'domain': 'team_dynamics',
  'bucket': 'core',
  'title': 'teams often need clarity more than motivation',
  'anchors': ['A2', 'A3', 'A10', 'A13'],
  'angle': 'unclear goals and ownership can look like low engagement'},
 {'id': 'psychological_load',
  'domain': 'team_dynamics',
  'bucket': 'core',
  'title': 'project uncertainty creates cognitive load',
  'anchors': ['A2', 'A3', 'A10', 'A13'],
  'angle': 'structure as a way to free attention for actual work'},
 {'id': 'team_autonomy',
  'domain': 'team_dynamics',
  'bucket': 'core',
  'title': 'autonomy needs boundaries',
  'anchors': ['A2', 'A3', 'A10', 'A13'],
  'angle': 'people can move faster when decisions they own are explicit'},
 {'id': 'team_visibility',
  'domain': 'team_dynamics',
  'bucket': 'core',
  'title': 'invisible work creates invisible overload',
  'anchors': ['A2', 'A3', 'A10', 'A13'],
  'angle': 'making coordination and review work visible in the plan'},
 {'id': 'team_trust',
  'domain': 'team_dynamics',
  'bucket': 'core',
  'title': 'trust grows when commitments and constraints are explicit',
  'anchors': ['A2', 'A3', 'A10', 'A13'],
  'angle': 'reliability as a project-management behavior'},
 {'id': 'conflict_is_data',
  'domain': 'conflict',
  'bucket': 'core',
  'title': 'conflict can be information about a hidden trade-off',
  'anchors': ['A3', 'A10', 'A12', 'A13'],
  'angle': 'finding the structural disagreement before solving the interpersonal one'},
 {'id': 'conflict_early',
  'domain': 'conflict',
  'bucket': 'core',
  'title': 'small disagreements are cheaper to resolve before they become positions',
  'anchors': ['A3', 'A10', 'A12', 'A13'],
  'angle': 'surfacing tension while options are still open'},
 {'id': 'conflict_constraints',
  'domain': 'conflict',
  'bucket': 'core',
  'title': 'many team conflicts are actually constraint conflicts',
  'anchors': ['A3', 'A10', 'A12', 'A13'],
  'angle': 'time, quality, scope and ownership pulling people in different directions'},
 {'id': 'deescalation',
  'domain': 'conflict',
  'bucket': 'core',
  'title': 'de-escalation starts with separating facts, constraints and preferences',
  'anchors': ['A3', 'A10', 'A12', 'A13'],
  'angle': 'making the problem discussable again'},
 {'id': 'delegation_outcome',
  'domain': 'delegation',
  'bucket': 'core',
  'title': 'delegate outcomes and boundaries, not just tasks',
  'anchors': ['A13'],
  'angle': 'giving autonomy without abandoning accountability'},
 {'id': 'delegation_checkpoints',
  'domain': 'delegation',
  'bucket': 'core',
  'title': 'good delegation includes agreed checkpoints',
  'anchors': ['A13'],
  'angle': 'avoiding both micromanagement and surprise failure'},
 {'id': 'mentor_decisions',
  'domain': 'delegation',
  'bucket': 'core',
  'title': 'teach the decision logic, not only the checklist',
  'anchors': ['A13'],
  'angle': 'how junior PMs build judgment'},
 {'id': 'take_work_back',
  'domain': 'delegation',
  'bucket': 'core',
  'title': 'taking work back is the fastest way to teach dependence',
  'anchors': ['A13'],
  'angle': 'reviewing without quietly becoming the owner again'},
 {'id': 'vendor_is_dependency',
  'domain': 'vendor_external',
  'bucket': 'core',
  'title': 'a vendor is an external dependency with a contract attached',
  'anchors': ['A3', 'A8', 'A9', 'A10'],
  'angle': 'planning inputs, approvals and acceptance around external teams'},
 {'id': 'vendor_brief',
  'domain': 'vendor_external',
  'bucket': 'core',
  'title': 'vendor quality starts with the brief and acceptance model',
  'anchors': ['A3', 'A8', 'A9', 'A10'],
  'angle': 'outsourcing execution does not outsource clarity'},
 {'id': 'vendor_lead_time',
  'domain': 'vendor_external',
  'bucket': 'core',
  'title': 'external partners have queues too',
  'anchors': ['A3', 'A8', 'A9', 'A10'],
  'angle': 'lead time and availability should enter the project schedule'},
 {'id': 'vendor_handover',
  'domain': 'vendor_external',
  'bucket': 'core',
  'title': 'vendor handover needs operational ownership',
  'anchors': ['A3', 'A8', 'A9', 'A10'],
  'angle': 'making sure knowledge survives the commercial relationship'},
 {'id': 'client_yes',
  'domain': 'client_commercial',
  'bucket': 'core',
  'title': 'saying yes to a client can be a project risk',
  'anchors': ['A5', 'A9', 'A12'],
  'angle': 'service quality sometimes means showing the consequence of the request'},
 {'id': 'commercial_pm',
  'domain': 'client_commercial',
  'bucket': 'core',
  'title': 'commercial awareness is part of delivery judgment',
  'anchors': ['A5', 'A9', 'A12'],
  'angle': 'scope, budget and relationship are connected systems'},
 {'id': 'proposal_assumptions',
  'domain': 'client_commercial',
  'bucket': 'core',
  'title': 'a proposal contains delivery assumptions whether written or not',
  'anchors': ['A5', 'A9', 'A12'],
  'angle': 'making them explicit before they become disputes'},
 {'id': 'negotiation_options',
  'domain': 'client_commercial',
  'bucket': 'core',
  'title': 'good negotiation gives options, not ultimatums',
  'anchors': ['A5', 'A9', 'A12'],
  'angle': 'changing scope, timing, cost or sequence to preserve the goal'},
 {'id': 'certainty_theatre',
  'domain': 'uncertainty',
  'bucket': 'core',
  'title': 'false certainty is more dangerous than visible uncertainty',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'using confidence and assumptions instead of decorative precision'},
 {'id': 'progressive_detail',
  'domain': 'uncertainty',
  'bucket': 'core',
  'title': 'detail should increase as uncertainty falls',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'planning at the right resolution for the current stage'},
 {'id': 'unknown_unknowns',
  'domain': 'uncertainty',
  'bucket': 'core',
  'title': 'you cannot list every risk, but you can design for surprises',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'contingency, decision speed and spare capacity'},
 {'id': 'uncertainty_owner',
  'domain': 'uncertainty',
  'bucket': 'core',
  'title': 'uncertainty still needs an owner',
  'anchors': ['A1', 'A2', 'A8', 'A10'],
  'angle': 'somebody has to discover the answer by a date'},
 {'id': 'health_not_status',
  'domain': 'project_health',
  'bucket': 'core',
  'title': 'project health is more than red amber green',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'schedule, scope, economics, risks and decision flow together'},
 {'id': 'leading_indicators',
  'domain': 'project_health',
  'bucket': 'core',
  'title': 'the most useful project signals often appear before a missed deadline',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'approval delay, rework, burn rate and unresolved decisions as warnings'},
 {'id': 'forecast_confidence',
  'domain': 'project_health',
  'bucket': 'core',
  'title': 'a forecast should include confidence',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'distinguishing the date from how sure the team is about the date'},
 {'id': 'health_trend',
  'domain': 'project_health',
  'bucket': 'core',
  'title': 'direction matters as much as current status',
  'anchors': ['A2', 'A5', 'A8', 'A9', 'A10'],
  'angle': 'a green project getting worse deserves attention'},
 {'id': 'different_clocks',
  'domain': 'cross_functional',
  'bucket': 'core',
  'title': 'different disciplines run on different clocks',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'planning cross-functional work without pretending every team behaves the same'},
 {'id': 'translation_loss',
  'domain': 'cross_functional',
  'bucket': 'core',
  'title': 'every functional boundary risks translation loss',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'keeping intent intact as work moves between business and specialists'},
 {'id': 'cross_functional_sequence',
  'domain': 'cross_functional',
  'bucket': 'core',
  'title': 'cross-functional delivery is mostly sequencing commitments',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'coordination as more than status meetings'},
 {'id': 'shared_definition',
  'domain': 'cross_functional',
  'bucket': 'core',
  'title': 'teams need shared definitions for ready, review and done',
  'anchors': ['A3', 'A7', 'A8', 'A10'],
  'angle': 'reducing friction at handoffs without imposing one universal workflow'},
 {'id': 'creative_dependency',
  'domain': 'design',
  'bucket': 'adjacent',
  'title': 'creative work has dependencies even when the board looks flat',
  'anchors': ['A7', 'A8'],
  'angle': 'identity, UI, motion and 3D do not become ready in the same order'},
 {'id': 'creative_feedback',
  'domain': 'design',
  'bucket': 'adjacent',
  'title': 'feedback is production input and needs a schedule',
  'anchors': ['A7', 'A8'],
  'angle': 'review cycles as real work rather than free iteration'},
 {'id': 'creative_briefing',
  'domain': 'design',
  'bucket': 'adjacent',
  'title': 'specialists need different kinds of clarity',
  'anchors': ['A7', 'A8'],
  'angle': 'briefing by discipline without losing the common objective'},
 {'id': 'project_product_boundary',
  'domain': 'product',
  'bucket': 'adjacent',
  'title': 'projects end; products keep accumulating consequences',
  'anchors': ['A11', 'A14'],
  'angle': 'what delivery ownership can and cannot solve after launch'},
 {'id': 'product_feedback_loop',
  'domain': 'product',
  'bucket': 'adjacent',
  'title': 'shipping is the start of the feedback loop, not the end of the story',
  'anchors': ['A11', 'A14'],
  'angle': 'what project managers can learn from product thinking'},
 {'id': 'feature_vs_goal',
  'domain': 'product',
  'bucket': 'adjacent',
  'title': 'a requested feature is not automatically the project goal',
  'anchors': ['A11', 'A14'],
  'angle': 'keeping the outcome visible when solution ideas arrive early'},
 {'id': 'campaign_parallelism',
  'domain': 'marketing_delivery',
  'bucket': 'adjacent',
  'title': 'campaign work is a portfolio inside a project',
  'anchors': ['A4', 'A8'],
  'angle': 'social, paid, influencer and content streams with different dependencies'},
 {'id': 'multi_market',
  'domain': 'marketing_delivery',
  'bucket': 'adjacent',
  'title': 'multi-market delivery multiplies constraints faster than deliverables',
  'anchors': ['A4', 'A8'],
  'angle': 'shared framework with local approvals and realities'},
 {'id': 'calendar_dependency',
  'domain': 'marketing_delivery',
  'bucket': 'adjacent',
  'title': 'a content calendar is also a dependency schedule',
  'anchors': ['A4', 'A8'],
  'angle': 'approvals, assets and channels behind each publication date'},
 {'id': 'technical_pm_boundary',
  'domain': 'engineering',
  'bucket': 'adjacent',
  'title': 'technical literacy for a PM is mainly about better questions',
  'anchors': ['A6'],
  'angle': 'enough depth to discuss estimates and scope without pretending to code'},
 {'id': 'qa_early',
  'domain': 'engineering',
  'bucket': 'adjacent',
  'title': 'QA begins when acceptance becomes explicit',
  'anchors': ['A6'],
  'angle': 'quality thinking before the final test cycle'},
 {'id': 'automation_judgment',
  'domain': 'automation',
  'bucket': 'adjacent',
  'title': 'automate repetition before judgment',
  'anchors': ['A15', 'A16', 'A17'],
  'angle': 'where deterministic rules are safer than model guesses'},
 {'id': 'automation_failure_mode',
  'domain': 'automation',
  'bucket': 'adjacent',
  'title': 'an automation is only useful after you understand how it fails',
  'anchors': ['A15', 'A16', 'A17'],
  'angle': 'testing edge cases as part of PM tooling'},
 {'id': 'discovery_decision',
  'domain': 'discovery',
  'bucket': 'adjacent',
  'title': 'research matters when it changes a decision',
  'anchors': ['A14'],
  'angle': 'turning interviews into choices rather than a slide deck'},
 {'id': 'discovery_bias',
  'domain': 'discovery',
  'bucket': 'adjacent',
  'title': 'good discovery tries to disprove the convenient story',
  'anchors': ['A14'],
  'angle': 'questions designed to find surprise rather than agreement'}]

TOPIC_HISTORY_PATH = ROOT / "generated" / "topic_history.json"
TOPIC_COOLDOWN = 120  # individual topic lanes stay out for a long time
FAMILY_LOOKBACK = 80  # rotate topic families based on recent generation history


def load_topic_history():
    try:
        if TOPIC_HISTORY_PATH.exists():
            data = json.loads(TOPIC_HISTORY_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except Exception as e:
        print("Could not read persistent topic history:", e)
    return []


def choose_topic_lanes(history):
    """Pick mostly core PM fundamentals, rotating families and avoiding recent lanes."""
    rng = random.SystemRandom()

    recent_ids = [x.get("lane_id") for x in history[-TOPIC_COOLDOWN:] if x.get("lane_id")]
    blocked_ids = set(recent_ids)

    # Track how often each family appeared recently. Newer history matters most simply
    # because the window is bounded. Families with the lowest use are preferred.
    family_use = {}
    for item in history[-FAMILY_LOOKBACK:]:
        fam = item.get("domain")
        if fam:
            family_use[fam] = family_use.get(fam, 0) + 1

    available = [x for x in TOPIC_LANES if x["id"] not in blocked_ids]
    if len(available) < DRAFT_COUNT:
        # Keep only the newest 40 lane IDs blocked if the giant catalog is somehow exhausted.
        blocked_ids = set(recent_ids[-40:])
        available = [x for x in TOPIC_LANES if x["id"] not in blocked_ids]

    core = [x for x in available if x.get("bucket", "core") == "core"]
    adjacent = [x for x in available if x.get("bucket") == "adjacent"]

    def pick_from(pool, count, used_domains):
        chosen = []
        while len(chosen) < count:
            candidates = [x for x in pool if x["domain"] not in used_domains and x not in chosen]
            if not candidates:
                break
            min_use = min(family_use.get(x["domain"], 0) for x in candidates)
            # Allow a small random pool around the least-used families so output is not deterministic.
            low_use = [x for x in candidates if family_use.get(x["domain"], 0) <= min_use + 1]
            lane = rng.choice(low_use)
            chosen.append(lane)
            used_domains.add(lane["domain"])
        return chosen

    selected = []
    used_domains = set()

    # Core PM is the default: 4 core topics on two runs out of three.
    # Every third run, allow exactly one adjacent/specialized topic.
    completed_runs = len(history) // DRAFT_COUNT
    adjacent_allowed = (completed_runs % 3 == 2) and bool(adjacent)
    core_needed = 3 if adjacent_allowed else 4

    selected.extend(pick_from(core, core_needed, used_domains))
    if adjacent_allowed:
        selected.extend(pick_from(adjacent, 1, used_domains))

    if len(selected) < DRAFT_COUNT:
        selected.extend(pick_from(core, DRAFT_COUNT - len(selected), used_domains))
    if len(selected) < DRAFT_COUNT:
        selected.extend(pick_from(adjacent, DRAFT_COUNT - len(selected), used_domains))

    if len(selected) != DRAFT_COUNT:
        raise RuntimeError("Not enough diverse unused topic lanes available")

    # Randomize slot order so provocative posts are not always tied to the same kind of topic.
    rng.shuffle(selected)

    print("SELECTED TOPIC LANES:")
    for i, lane in enumerate(selected, 1):
        print(f"  {i}. [{lane['bucket']}/{lane['domain']}] {lane['id']} — {lane['title']}")
    return selected


def choose_hook_styles(history):
    """Pick four structurally different openings and avoid recent hook templates."""
    recent = [x.get("hook_style") for x in history[-32:] if x.get("hook_style")]
    blocked = set(recent[-16:])
    available = [x for x in HOOK_STYLES if x["id"] not in blocked]
    if len(available) < DRAFT_COUNT:
        available = HOOK_STYLES[:]  # long-run fallback; still unique inside this batch
    rng = random.SystemRandom()
    selected = rng.sample(available, DRAFT_COUNT)
    print("SELECTED HOOK STYLES:")
    for i, hook in enumerate(selected, 1):
        print(f"  {i}. {hook['id']} — {hook['rule']}")
    return selected


def _opening(text, limit=180):
    text = (text or "").strip()
    first = re.split(r"\n\s*\n|\n", text, maxsplit=1)[0]
    return re.sub(r"\s+", " ", first).strip()[:limit]


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
            "domain": post.get("topic_domain", ""),
            "bucket": post.get("topic_bucket", ""),
            "anchors": post.get("experience_anchor", []),
            "provocative": bool(post.get("provocative")),
            "hook_style": post.get("hook_style", ""),
            "opening": _opening(post.get("text", "")),
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

def make_prompt(trends, previous_posts, selected_lanes, selected_hooks, topic_history):
    trend_text = "\n\n".join(
        f"SOURCE: {x['source']}\nTITLE: {x['title']}\nURL: {x['url']}\nDESCRIPTION: {x['description']}"
        for x in trends
    )

    history_text = "\n\n--- PREVIOUS POST ---\n".join(previous_posts[:40])
    lane_text = "\n".join(
        f"POST {i}: lane_id={lane['id']} | bucket={lane['bucket']} | domain={lane['domain']} | title={lane['title']} | angle={lane['angle']} | HOOK_STYLE={selected_hooks[i-1]['id']} | HOOK_RULE={selected_hooks[i-1]['rule']}"
        for i, lane in enumerate(selected_lanes, start=1)
    )
    persistent_history_text = "\n".join(
        f"- lane={x.get('lane_id','')} | hook={x.get('hook_style','')} | topic={x.get('topic','')} | opening={x.get('opening','')}"
        for x in topic_history[-80:]
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
- return the exact lane_id in "topic_lane", exact domain in "topic_domain", and exact bucket in "topic_bucket"
- the selected lane is the main subject; do not drag it back to stakeholders, automation, development or scope unless that is the selected lane
- each post must feel materially different from the other three in subject, problem, hook and takeaway
- CORE PM fundamentals are the default
- specialized development / AI / automation / design / product / marketing topics appear only when code explicitly selected an adjacent lane
- NEVER turn a core PM topic into a software-development post just because Matvei has web experience

THIS IS THE MOST IMPORTANT RULE:
The SELECTED PM TOPIC comes first. Matvei's CV is PRIVATE GROUNDING, not copy material.
The experience_anchor field exists only so the system knows the opinion is compatible with something Matvei has actually done.
DEFAULT BEHAVIOR: do NOT mention the anchor, employer, client, project, team size, number of stakeholders, number of projects, 15M figure, timelines or other CV metrics in the public post.
Write the post as expert operational judgment: what tends to work, what breaks, what a PM should notice, what trade-off exists.
Across the four posts, AT MOST ONE may explicitly refer to Matvei's personal experience, and only when the selected topic genuinely becomes better because of it.
Never use a CV number or impressive metric as the hook.
Never use the 25-stakeholder story, 15-person team, 6–7 parallel projects, 15M opens, 30+ projects or seven-automations-in-seven-days as recurring proof points. Treat them as internal evidence, not recurring content.
Do not start from a random trend and force Matvei into it.
Do not invent personal experience.

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

POST 3 — PRACTICAL PM FUNDAMENTAL
- provocative = false
- explain the selected project-management concept through a concrete operating principle, trade-off, failure mode or decision pattern
- basic PM topics are GOOD: planning, risk, issues, milestones, estimates, changes, reporting, quality, handover, priorities, capacity, documentation, roles, project health, closure and similar fundamentals
- practical does not mean software-specific

POST 4 — EXPERT PM FUNDAMENTAL
- provocative = false
- make the selected topic useful to an experienced PM, not a textbook definition
- if code selected an adjacent topic, use it; otherwise stay firmly in core project management
- trend evidence is optional seasoning only and must never replace the selected PM topic

PROVOCATION RULES:
- EXACTLY 2 of the 4 posts must have "provocative": true
- the other 2 must have "provocative": false
- provocation should come from a strong thesis, not swearing, insults or fake certainty
- good examples of structure: "X is often treated as Y. in practice, I think the real problem is Z"
- do not attack PMs, clients, developers, designers or companies as groups
- no cheap contrarianism

EXPERIENCE RULES:
- every post must output "experience_anchor" using one or more IDs from A1–A17, but this metadata is INTERNAL and does not need to appear in the copy
- every personal factual statement must be supported by those anchors
- prefer ZERO explicit CV examples in a post; use operational reasoning instead
- at most ONE of the four posts may include a concrete first-person work example
- do not use "i've managed X", "in my experience", employer names, client descriptions or CV metrics as default credibility devices
- do not turn the feed into four rewrites of the same case study
- across the four candidates, use at least 3 different anchor IDs internally

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

EDITORIAL DIRECTION:
The feed should feel like a very broad, intelligent exploration of project management — not a feed about software delivery, stakeholders or automation.

Core PM territory includes, among many others:
- project initiation and charters
- objectives and success criteria
- scope and out-of-scope
- assumptions, constraints and unknowns
- requirements and acceptance
- estimation and uncertainty
- planning and replanning
- scheduling, milestones and critical path
- dependencies and handoffs
- risks, issues and escalation
- decisions and decision rights
- change control
- roles, governance and sponsorship
- communication and meetings
- documentation and project memory
- status reporting, forecasting and project health
- quality and acceptance
- handover and closure
- retrospectives and lessons learned
- budget, project economics and contingency
- resources, capacity and workload
- prioritization and portfolio thinking
- team dynamics, conflict, delegation and mentoring
- vendors and external dependencies
- client / commercial judgment
- uncertainty and contingency

Do not keep returning to the same five "safe" themes. Variety is a hard requirement.

DO NOT DEFAULT TO:
- generic productivity advice
- generic leadership quotes
- "communication is important"
- "AI is changing everything"
- generic Scrum / Agile / Kanban explainers
- generic remote-work takes
- generic meeting advice
unless there is a specific, experience-led thesis that could only plausibly come from this background

HOOK DIVERSITY — HARD REQUIREMENT:
- each post MUST use its assigned HOOK_STYLE from the selected topic line above and return that exact id in "hook_style"
- the first paragraph must have a visibly different sentence shape from the other three posts
- NEVER start with: "we love", "we all", "let's talk", "here's the thing", "hot take", "unpopular opinion", "as a project manager", "in my experience", "one thing i've learned"
- do not start more than one post in a batch with "i"
- do not use the same rhetorical skeleton across runs, even with different nouns
- no repeated opening formulas such as "X is not Y", "we love X", or "the problem with X is Y" in multiple posts in the same batch
- recent persistent openings below are examples to AVOID structurally, not templates to imitate

DEDUPLICATION:
- do NOT repeat the thesis, hook, metaphor or conclusion of recent Buffer posts below
- do NOT revisit blocked topics as the main idea
- if a candidate feels semantically similar to a previous post, discard it and generate another
- different wording is NOT enough; the underlying idea must be different
- avoid using the same topic family repeatedly across runs even when lane IDs differ
- if recent history contains several posts from one family, prefer a genuinely different PM area
- development, automation and stakeholder topics must not become fallback themes

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
- the reasoning should sound like someone who has actually delivered projects, without repeatedly proving it with CV anecdotes
- concrete trade-off > abstract advice
- operating principle > inspirational lesson
- specific failure mode > generic best practice
- tension > listicle
- practical judgment > autobiography
- if a random PM influencer could write the same generic advice, reject it
- if the only thing making the post specific is a recycled CV number, reject it

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
      "topic_domain": "exact selected domain",
      "topic_bucket": "exact selected bucket",
      "hook_style": "exact assigned HOOK_STYLE id",
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

def generate_candidates(prompt, selected_lanes, selected_hooks):
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

                expected_domains = [x["domain"] for x in selected_lanes]
                returned_domains = [p.get("topic_domain") for p in posts]
                expected_buckets = [x["bucket"] for x in selected_lanes]
                returned_buckets = [p.get("topic_bucket") for p in posts]
                if returned_domains != expected_domains or returned_buckets != expected_buckets:
                    last_error = RuntimeError(
                        f"Model ignored required topic domain/bucket. Expected {list(zip(expected_domains, expected_buckets))}, got {list(zip(returned_domains, returned_buckets))}"
                    )
                    print(last_error)
                    continue

                expected_hooks = [x["id"] for x in selected_hooks]
                returned_hooks = [p.get("hook_style") for p in posts]
                if returned_hooks != expected_hooks:
                    last_error = RuntimeError(
                        f"Model ignored required hook styles. Expected {expected_hooks}, got {returned_hooks}"
                    )
                    print(last_error)
                    continue

                openings = [_opening(p.get("text", "")).lower() for p in posts]
                if any(any(op.startswith(bad) for bad in FORBIDDEN_OPENINGS) for op in openings):
                    last_error = RuntimeError(f"Model used a forbidden/repetitive opening: {openings}")
                    print(last_error)
                    continue
                first_words = [" ".join(re.findall(r"[a-zA-Z']+", op)[:3]) for op in openings]
                if len(set(first_words)) < len(first_words):
                    last_error = RuntimeError(f"Opening structures are too similar inside the batch: {first_words}")
                    print(last_error)
                    continue
                if sum(1 for op in openings if op.startswith("i ") or op == "i") > 1:
                    last_error = RuntimeError("More than one post starts with 'i'")
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
1. The experience_anchor IDs are INTERNAL grounding metadata. The public copy does NOT need to mention them or retell the CV case.
2. If the copy does make a factual claim about Matvei's work, it must be directly supported by VERIFIED MATVEI EXPERIENCE.
3. Do not inject a CV anecdote, employer, client, metric, team size or impressive number during fact-checking if the draft did not need one. Prefer operational judgment without autobiography.
4. External factual claims are allowed only if supported by VERIFIED FACT BASE or supplied TREND EVIDENCE.
5. If an unsupported detail is nonessential, remove it or rewrite it as clearly subjective judgment.
6. If the main thesis depends on invented or unsupported experience, set approved=false rather than fabricating a replacement story.
7. Keep the core PM thesis and Matvei's voice. Do not make the post more autobiographical.
8. Correct every proper noun / official name / acronym.
9. Keep lowercase ordinary prose and no period at the end of paragraphs.
10. Carousel copy must match the corrected post and the same factual standard.
11. The carousel MUST contain 5 to 8 slides. Never return fewer than 5 slides.
12. Provocative posts may challenge assumptions, but must not become ragebait or universal claims unsupported by experience.
13. Preserve "provocative", "topic_lane", "topic_domain", "topic_bucket", "hook_style" and "experience_anchor" fields exactly.
14. Do not change the subject into stakeholder management, automation or another familiar PM fallback.

Return VALID JSON ONLY:
{{
  "approved": true,
  "issues": ["short description of anything corrected"],
  "candidate": {{
    "provocative": true,
    "topic_lane": "exact original lane_id",
    "hook_style": "exact original hook_style",
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
                    corrected["hook_style"] = candidate.get("hook_style", corrected.get("hook_style", ""))
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
    selected_hooks = choose_hook_styles(topic_history)
    posts = generate_candidates(
        make_prompt(trends, previous_posts, selected_lanes, selected_hooks, topic_history),
        selected_lanes,
        selected_hooks
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
