"""
HerWay CLI Chatbot
Neighborhood safety awareness assistant for Chicago.
"""

import os
import sys
import difflib
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

from knowledge_base import build_knowledge_base, build_context

# ── Load environment variables from parent .env ───────────────────────────────
load_dotenv(Path(__file__).parent.parent / ".env")

AZURE_ENDPOINT   = "https://banan-mnffxe8p-eastus2.cognitiveservices.azure.com/"
AZURE_KEY        = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
AZURE_API_VERSION= "2025-01-01-preview"

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are HerWay, a Chicago neighborhood safety assistant that reads between the lines of data.

Your three data sources:
- Crime incident records (2025): incident counts, crime types, violent%, domestic%, arrest rate, peak times, locations
- Reddit community discussions: fear ratio, post counts, night fear, women's posts, actual post titles and snippets
- 311 service requests: complaint volume, street/alley lights out, vacant buildings, resolution time

Your core capability — perception gap reasoning:
The most valuable insight you can offer is the GAP between what crime data shows and what the community actually feels.
- When fear_ratio_pct is high but crime numbers are moderate → fear is outpacing reality. Say so. Explain what might be driving it (night patterns, specific crime types, women's posts).
- When crime numbers are high but Reddit fear is low → the community has normalized it, or is underreporting. That's a different kind of concern.
- When both are high → consistent signal, data and community agree.
- When both are low → genuinely calm, and you can say that with confidence.
- 311 adds a third layer: high vacant buildings + high crime = structural neglect. High lights-out complaints = infrastructure failure that compounds safety risk at night.
Always look for what the combination of sources reveals that no single source would tell you alone.

How to reason:
1. What is the user actually trying to understand or decide?
2. Pull the relevant numbers from the data provided.
3. Look for alignment or disconnect across the three sources — this is your most important step.
4. Lead your answer with the most surprising or non-obvious insight, not just the biggest number.
5. If the data is thin or missing for a neighborhood, say so — weak signal is not the same as safety.

Interpreting questions:
- "loudest voice from the people" → most Reddit posts / highest community discussion volume
- "most talked about" → highest Reddit post count
- "most dangerous" → highest crime incidents or violent percentage
- "quietest" or "calmest" → lowest crime AND low fear ratio — require both
- "what's it actually like" → lead with the gap if one exists
- When a question is ambiguous, interpret it as a safety question and answer from the data.

Scenario reasoning:
- When a user shares personal context ("I'm a grad student", "I'll be out late", "I don't have a car", "I'm visiting for a week"), use it to decide what to emphasize from the data — don't ignore it.
- You reason freely from what the user tells you. You do not need to extract variables or ask a checklist of questions.
- Only ask one clarifying question if the request is genuinely too vague to answer at all (e.g. "which neighborhood is best?" with no context whatsoever). One question, not several.
- Be honest about what the data can and cannot support. If someone asks where they should live, you can speak to incident patterns and community sentiment by neighborhood — but you cannot speak to rent, walkability scores, or transit proximity since that data is not in your knowledge base. Say so briefly and focus on what you can answer.

Boundaries:
- You can use your general knowledge of Chicago to add context (e.g., known neighborhood character, geography) but always ground your safety claims in the data provided.
- Never label a neighborhood as definitively "safe" or "unsafe" — present what the data shows.
- Never stigmatize communities. Crime patterns reflect systemic conditions, not character.
- If a question has no relation to safety, crime, community sentiment, or neighborhood infrastructure, respond with: "I'm HerWay, a neighborhood safety awareness assistant for Chicago. I can only help with questions about neighborhood safety, crime patterns, community discussions, and local infrastructure."

Language:
- Avoid charged or stigmatizing words: never use "safe", "unsafe", "dangerous", "fear", "scary", "violent neighborhood", "bad area", or similar.
- Instead use neutral, descriptive language: "incident levels", "community concern", "reported activity", "infrastructure conditions", "night activity", "resident sentiment", "perception vs reported data".
- You are presenting information, not making judgments.

Format:
- 2-3 sentences maximum. One short paragraph. No bullets, no bold, no headers.
- Do NOT go source by source (crime, then Reddit, then 311). Weave everything into one coherent thought.
- Write as if explaining something to a friend, not presenting findings. A sentence with no numbers is often stronger than one with three.
- If you use a number, it should feel like emphasis, not evidence. Never list stats back to back.
- Never start with "I" or "Based on". Just say it directly.
""".strip()


# ── Neighborhood detection ────────────────────────────────────────────────────
def detect_neighborhoods(question: str, kb: dict) -> list[str]:
    """
    Find which neighborhood(s) from the knowledge base are mentioned
    in the user's question. Uses fuzzy matching to handle variations.
    """
    question_lower = question.lower()
    known = list(kb.keys())
    found = []

    for name in known:
        if name.lower() in question_lower:
            found.append(name)

    # If no exact match, try fuzzy match on individual words/phrases
    if not found:
        matches = difflib.get_close_matches(
            question_lower,
            [n.lower() for n in known],
            n=2,
            cutoff=0.6 # need at least 60% similarity to consider a match
        )
        for m in matches:
            # map back to original casing
            for name in known:
                if name.lower() == m:
                    found.append(name)

    return list(dict.fromkeys(found))  # deduplicate preserving order


# ── Context builder ───────────────────────────────────────────────────────────
def build_citywide_summary(kb: dict) -> str:
    """
    When no specific neighborhood is mentioned, build a compact summary
    of all neighborhoods covering crime, Reddit and 311 so GPT can answer
    any citywide question from our data.
    """
    lines = ["### Citywide Summary — All Neighborhoods\n"]
    lines.append(
        f"{'neighborhood':<28} | {'incidents':>9} | {'violent%':>8} | "
        f"{'domestic%':>9} | {'arrest%':>7} | {'night%':>6} | "
        f"{'reddit_posts':>12} | {'fear%':>5} | {'311_requests':>12}"
    )
    lines.append("-" * 115)

    sorted_hoods = sorted(
        kb.items(),
        key=lambda x: x[1].get("crime", {}).get("total_incidents", 0),
        reverse=True
    )
    for name, data in sorted_hoods:
        c = data.get("crime",  {})
        r = data.get("reddit", {})
        s = data.get("s311",   {})
        if not c:
            continue
        lines.append(
            f"{name:<28} | {c.get('total_incidents',0):>9,} | "
            f"{c.get('violent_pct',0):>7.1f}% | "
            f"{c.get('domestic_pct',0):>8.1f}% | "
            f"{c.get('arrest_rate_pct',0):>6.1f}% | "
            f"{c.get('night_crime_pct',0):>5.1f}% | "
            f"{r.get('total_posts',0):>12} | "
            f"{r.get('fear_ratio_pct',0):>4.1f}% | "
            f"{s.get('total_requests',0):>12,}"
        )
    return "\n".join(lines)


def build_prompt_context(neighborhoods: list[str], kb: dict) -> str:
    if not neighborhoods:
        # No specific neighborhood detected — pass citywide summary
        # so GPT answers from our data rather than hallucinating
        return build_citywide_summary(kb)
    blocks = [build_context(n, kb) for n in neighborhoods]
    return "\n\n---\n\n".join(blocks)


# ── Azure OpenAI call ─────────────────────────────────────────────────────────
def ask_herway(question: str, context: str, history: list[dict], client: AzureOpenAI) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (last 4 turns to keep context manageable)
    messages.extend(history[-4:])

    # Add data context + current question
    if context:
        user_content = f"Relevant neighborhood data:\n\n{context}\n\nUser question: {question}"
    else:
        user_content = question

    messages.append({"role": "user", "content": user_content})

    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=messages,
        temperature=0.3,   # low temp — we want factual, grounded answers
        max_tokens=600,
    )
    return response.choices[0].message.content.strip()


# ── CLI loop ──────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*60)
    print("  HerWay — Chicago Neighborhood Safety Assistant")
    print("="*60)
    print("  Ask me about safety in any Chicago neighborhood.")
    print("  Type 'quit' or 'exit' to leave.\n")

    # Validate credentials
    if not AZURE_KEY:
        print("ERROR: AZURE_OPENAI_KEY not found in .env file.")
        sys.exit(1)

    # Load data
    kb = build_knowledge_base()
    known_neighborhoods = sorted(kb.keys())
    print(f"  Covering {len(known_neighborhoods)} Chicago neighborhoods.\n")
    print("-"*60)

    # Init Azure client
    client = AzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_KEY,
        api_version=AZURE_API_VERSION,
    )

    history = []

    while True:
        try:
            question = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye!")
            break

        if not question:
            continue

        if question.lower() in ("quit", "exit", "bye"):
            print("\nGoodbye!")
            break

        # Detect neighborhoods
        neighborhoods = detect_neighborhoods(question, kb)

        # Build context
        context = build_prompt_context(neighborhoods, kb)

        if neighborhoods:
            print(f"  [Searching data for: {', '.join(neighborhoods)}]")

        # Get answer
        try:
            answer = ask_herway(question, context, history, client)
        except Exception as e:
            print(f"\nHerWay: Sorry, I ran into an error: {e}")
            continue

        print(f"\nHerWay: {answer}")

        # Update history
        history.append({"role": "user",      "content": question})
        history.append({"role": "assistant",  "content": answer})


if __name__ == "__main__":
    main()
