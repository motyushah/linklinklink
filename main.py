
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

VOICE:
- English
- lowercase by default, including "i"
- proper nouns keep correct capitalization: Jira, Scrum, Agile, Toyota, Telegram, Google, Tbilisi etc
- never capitalize a sentence only because it starts a paragraph
- no period at the end of paragraphs
- never use an em dash —
- use an en dash – when needed
- natural spoken rhythm, not telegram-style fragments
- occasional emojis are fine as punchlines, not decoration
- dry humor, absurd comparisons, slightly unhinged metaphors are welcome
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

def make_prompt(trends):
    trend_text = "\n\n".join(
        f"SOURCE: {x['source']}\nTITLE: {x['title']}\nURL: {x['url']}\nDESCRIPTION: {x['description']}"
        for x in trends
    )

    return f"""
{STYLE}

{PROFILE}

{PM_FACTS}

Create exactly {DRAFT_COUNT} different LinkedIn post candidates.

MIX:
- about half: evergreen PM fundamentals, but with a surprising angle, history,
  analogy, misconception or sharp practical observation
- one practical post: automation, delivery, processes, Jira, workload,
  stakeholders, creative/dev teams, QA or planning
- up to one trend-based post if a fresh trend has a genuinely good PM/work angle

A trend is raw material, not the whole post.
Do not chase trends for the sake of it.

FACT CHECK:
- use only the verified PM facts above or facts explicitly present in the trend evidence
- do not turn a headline into invented detail
- no made-up statistics, research, quotes or company announcements
- when evidence is weak, remove the claim

QUALITY:
- every post needs one real thought
- reject anything that sounds like generic PM influencer content
- interesting > comprehensive
- specific > motivational
- no AI-slop phrases

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
      "category": "pm_basics | practical | trend",
      "topic": "internal topic",
      "text": "finished LinkedIn post",
      "sources": ["actual URLs used"],
      "carousel": {{
        "slides": [
          {{
            "label": "pm basics or another tiny label",
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
    for model in ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]:
        for attempt in range(3):
            print(f"Gemini {model}, attempt {attempt + 1}")
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={
                    "x-goog-api-key": GEMINI_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"responseMimeType": "application/json"}
                },
                timeout=180
            )
            if r.status_code in [429, 500, 502, 503, 504]:
                print("temporary Gemini error:", r.status_code)
                time.sleep(5 * (attempt + 1))
                continue
            r.raise_for_status()
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            data = json.loads(raw)
            posts = data.get("posts", [])
            if posts:
                return posts[:DRAFT_COUNT]
    raise RuntimeError("Gemini failed on all models")

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
    posts = generate_candidates(make_prompt(trends))

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
