import os
import requests

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
BUFFER_KEY = os.environ["BUFFER_API_KEY"]

PROMPT = """
Write one LinkedIn post for Matvei Shakhurdin.

He is a senior project/delivery manager with an agency background,
strong in design, web development, fintech, processes and AI automation.

Style:
- human, conversational English
- no AI slop
- no "not only... but also"
- no corporate bullshit
- practical PM topic
- 800-1300 characters
- strong opening
- no hashtags
- no emojis
- no final full stop

Return only the finished post.
"""

# 1. Gemini writes the post
r = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
    headers={
        "x-goog-api-key": GEMINI_KEY,
        "Content-Type": "application/json"
    },
    json={
        "contents": [{"parts": [{"text": PROMPT}]}]
    }
)
r.raise_for_status()
post = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

# Buffer helper
headers = {
    "Authorization": f"Bearer {BUFFER_KEY}",
    "Content-Type": "application/json"
}

def buffer(query):
    r = requests.post(
        "https://api.buffer.com",
        headers=headers,
        json={"query": query}
    )
    r.raise_for_status()
    return r.json()

# 2. Find Buffer organization
data = buffer("""
query {
  account {
    organizations {
      id
      name
    }
  }
}
""")

org_id = data["data"]["account"]["organizations"][0]["id"]

# 3. Find LinkedIn
data = buffer(f"""
query {{
  channels(input: {{organizationId: "{org_id}"}}) {{
    id
    Name
    service
  }}
}}
""")

linkedin = next(
    x for x in data["data"]["channels"]
    if "linkedin" in x["service"].lower()
)

# 4. Escape post for GraphQL
safe_post = (
    post.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
)

# 5. Put it into Buffer as DRAFT
result = buffer(f"""
mutation {{
  createPost(input: {{
    text: "{safe_post}",
    channelId: "{linkedin['id']}",
    schedulingType: automatic,
    mode: addToQueue,
    saveToDraft: true
  }}) {{
    ... on PostActionSuccess {{
      post {{ id text }}
    }}
    ... on MutationError {{
      message
    }}
  }}
}}
""")

print(result)
