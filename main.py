
import os
import json
import re
import time
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
His real background includes design and creative production, web development,
marketing, fintech, designers, developers, stakeholder communication,
team workload, limited resources, process setup and automation.

CONTENT POSITIONING GOAL:
The feed should make an experienced hiring manager think:
"this person understands how delivery actually works"
without Matvei sounding like he is begging for a job.

Good expertise signals include:
- turning vague stakeholder asks into workable scope
- prioritization and trade-offs under limited time / people / budget
- resource and workload planning
- delivery risk, dependencies, escalation and expectation management
- QA and release discipline
- cross-functional work between design, development, marketing and business
- process design that removes friction instead of adding ceremony
- practical AI / automation for PM work
- retrospectives, failure modes and what a PM would change next time
- product thinking from an agency / delivery background
- communicating difficult constraints clearly without creating drama

Prefer specific operational insights, trade-offs and anti-patterns over textbook definitions.
Never invent employers, numbers, results, team sizes or personal stories.
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

def make_prompt(trends, previous_posts):
    trend_text = "\n\n".join(
        f"SOURCE: {x['source']}\nTITLE: {x['title']}\nURL: {x['url']}\nDESCRIPTION: {x['description']}"
        for x in trends
    )

    history_text = "\n\n--- PREVIOUS POST ---\n".join(previous_posts[:40])

    return f"""
{STYLE}

{PROFILE}

{PM_FACTS}

{BLOCKED_OR_ALREADY_USED_TOPICS}

Create exactly {DRAFT_COUNT} different LinkedIn post candidates.

CONTENT MIX:
- 2 candidates: genuinely interesting project-management topics that demonstrate senior delivery judgment
- 1 candidate: practical operations / automation / AI / process design
- 1 candidate: trend-aware, but only if the trend creates a real PM/work insight; otherwise make another strong PM post

TOPIC RULES:
- do NOT repeat the thesis, hook, metaphor or conclusion of any recent Buffer post shown below
- do NOT revisit blocked topics above as the main idea
- avoid textbook explainers unless there is a surprising misconception, historical twist or practical contradiction
- prioritize topics that reveal judgment: trade-offs, prioritization, scope, risk, resources, stakeholder dynamics,
  QA, dependencies, decision-making, process design, delivery systems, product thinking, AI-assisted PM work
- a hiring manager should learn something about how Matvei thinks and works from the post
- the post should still be enjoyable even for someone who is not hiring

FACT-CHECK RULES — MANDATORY:
- every factual claim must be supported by the VERIFIED FACT BASE or by the TREND EVIDENCE supplied below
- a title/headline alone does not justify inventing details behind it
- if a claim cannot be supported from the supplied evidence, remove it or rewrite it as clearly subjective opinion
- never invent studies, statistics, dates, quotes, company announcements, product capabilities or historical details
- never create a source URL that was not supplied
- when using a trend, source URLs must point to the evidence actually used
- when using only personal reasoning / PM opinion with no factual external claim, sources may be an empty list
- separate facts from interpretations: factual language must be supportable; opinions can be framed as opinions

CAPITALIZATION CHECK BEFORE RETURNING:
- ordinary prose stays lowercase by default
- proper nouns and official names keep standard capitalization
- examples: LinkedIn, OpenAI, GitHub, Jira, Scrum, Agile, Kanban, Toyota, Telegram, Tbilisi, Matvei Shakhurdin
- acronyms stay uppercase: AI, PM, API, SQL, CRM, QA
- never output "linkedin", "jira", "scrum", "agile", "toyota", "tbilisi" etc when they refer to the proper noun

QUALITY:
- every post needs one real thought
- reject anything that sounds like generic PM influencer content
- interesting > comprehensive
- specific > motivational
- useful tension / contradiction / trade-off is better than a generic lesson
- no AI-slop phrases

RECENT BUFFER POSTS — DO NOT REPEAT:
{history_text if history_text else "No readable Buffer history available. Use the blocked list above."}

CAROUSEL:
For every post create 5–8 slides.
The carousel should feel like Matvei's existing visual identity:
- 1080×1350
- Anton-style huge condensed uppercase headline
- thin sans-serif supporting copy
- huge margins
- black / white / vivid yellow / cyan / vivid red
- flat colors, no gradients
- minimal editorial composition
- one idea per slide
- headlines short, preferably under 8 words
- body ideally under 35 words
- proper nouns and acronyms must still be correctly capitalized in body copy
- do not invent screenshots or fake interfaces
- if a real screenshot would be required, explain the idea with typography instead

The first slide must be a strong cover.
The final slide should land the conclusion, not beg for engagement.

TREND EVIDENCE:
{trend_text}

Return VALID JSON ONLY:
{{
  "posts": [
    {{
      "category": "pm_expertise | practical | trend",
      "topic": "internal topic",
      "text": "finished LinkedIn post",
      "sources": ["actual URLs used"],
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

def generate_candidates(prompt):
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
                            "responseMimeType": "application/json"
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
                print(f"SUCCESS with {model}: {len(posts)} posts generated")
                return posts[:DRAFT_COUNT]

            last_error = RuntimeError(f"{model} returned no posts")
            print("Gemini returned no posts, trying again")

    raise RuntimeError(f"Gemini failed on all free models. Last error: {last_error}")


def fact_check_candidate(candidate, trends):
    """Second-pass verifier. It may correct or reject unsupported claims before anything reaches Buffer."""
    trend_text = "\n\n".join(
        f"SOURCE: {x['source']}\nTITLE: {x['title']}\nURL: {x['url']}\nDESCRIPTION: {x['description']}"
        for x in trends
    )

    prompt = f"""
You are a strict fact-checker and copy editor.

{PM_FACTS}

CAPITALIZATION POLICY:
- ordinary prose may begin lowercase
- proper nouns, official names and acronyms MUST use standard capitalization
- examples: LinkedIn, OpenAI, GitHub, Jira, Scrum, Agile, Kanban, Toyota, Telegram, Tbilisi, Matvei Shakhurdin, AI, PM, API, SQL, CRM, QA

TREND EVIDENCE:
{trend_text}

CANDIDATE JSON:
{json.dumps(candidate, ensure_ascii=False)}

Do a claim-by-claim check.
Rules:
1. A factual claim is allowed only if supported by the verified PM facts above or by the supplied trend evidence.
2. If unsupported, remove it, soften it into clearly subjective opinion, or rewrite around it.
3. Do not invent replacement facts.
4. Keep Matvei's tone of voice and lowercase ordinary prose.
5. Correct capitalization of every proper noun / official name / acronym.
6. Do not reintroduce a period at the end of paragraphs.
7. Keep the same general topic unless the entire topic depends on unsupported facts.
8. Carousel copy must match the corrected post and follow the same factual standard.

Return VALID JSON ONLY in this shape:
{{
  "approved": true,
  "issues": ["short description of anything corrected"],
  "candidate": {{
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
                        "generationConfig": {"responseMimeType": "application/json"},
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
                if corrected and corrected.get("text"):
                    if checked.get("issues"):
                        print("FACT-CHECK CORRECTIONS:", checked.get("issues"))
                    return corrected
            except Exception as e:
                last_error = e
                time.sleep(5)
                continue

    # Safer failure mode: do not publish an unverified candidate.
    raise RuntimeError(f"Fact-check failed; draft was not sent to Buffer. Last error: {last_error}")

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
    posts = generate_candidates(make_prompt(trends, previous_posts))

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
        post_dir = run_dir / f"post_{p_idx:02d}"
        post_dir.mkdir(parents=True, exist_ok=True)
        slides = post.get("carousel", {}).get("slides", [])[:8]
        if len(slides) < 2:
            raise RuntimeError("carousel needs at least 2 slides")
        slides[-1]["signature"] = True

        paths = []
        for s_idx, slide in enumerate(slides):
            out = post_dir / f"slide_{s_idx + 1:02d}.png"
            render_slide(slide, s_idx, out)
            paths.append(out)
        rendered.append((post, paths))

    # Buffer needs public URLs, so publish the generated PNG files first.
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
