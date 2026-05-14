#!/usr/bin/env python3
"""Convert htmldoku/*.md to 18xx-Doku/*.html — stdlib only, no external dependencies."""

import json
import re
import os
import shutil
import html as _html
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent
OUT_DIR = REPO_ROOT / "docs" / "18xx-Doku"
MD_DIR  = REPO_ROOT / "MD"

SIDEBAR = [
    ("18OE Status", [
        ("Game Rules Summary", "rules-summary.html"),
        ("Map Implementation Status", "18oe-map-status.html"),
        ("Implementation Tracker", "status.html"),
        ("Rulebook Coverage", "rulebook-coverage.html"),
        ("Open for Alpha", "alpha-gaps.html"),
    ]),
    ("Getting Involved", [
        ("Your First Contribution", "first-contribution.html"),
    ]),
    ("Building a New Game", [
        ("Understanding the Engine", "engine-concepts.html"),
        ("Development Setup", "getting-started.html"),
        ("Game Structure", "game-implementation.html"),
        ("Map Configuration", "map.html"),
        ("Corporations & Companies", "entities.html"),
        ("Trains, Phases & Market", "trains-phases.html"),
        ("Rounds & Steps", "round-step-system.html"),
        ("Auction Round", "auction-round.html"),
        ("Revenue & Routing", "revenue-routing.html"),
        ("Abilities", "abilities.html"),
        ("Tile Reference", "tiles.html"),
        ("Common Patterns", "common-patterns.html"),
        ("Testing Your Game", "testing.html"),
        ("Title Checklist", "title-checklist.html"),
        ("Coding Guidelines", "coding-guidelines.html"),
    ]),
    ("Reference", [
        ("Game Engine Reference", "game-engine.html"),
        ("Architecture Decision Records", "adrs.html"),
    ]),
    ("Platform & Testing Setup", [
        ("Architecture Overview", "architecture.html"),
        ("Configuration & Operations", "konfiguration-betrieb.html"),
        ("System Boundaries", "systemgrenzen.html"),
    ]),
    ("Working with Claude", [
        ("Co-developing with Claude", "codevelop.html"),
    ]),
]

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"

# ---------------------------------------------------------------------------
# Step 1 — Extract Mermaid blocks BEFORE any other processing
# ---------------------------------------------------------------------------

MERMAID_FENCE_RE = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)


def extract_mermaid(text):
    blocks = []

    def _replace(m):
        idx = len(blocks)
        blocks.append(m.group(1))
        return f"\n%%MERMAID_{idx}%%\n"

    return MERMAID_FENCE_RE.sub(_replace, text), blocks


def restore_mermaid(html, blocks):
    """Replace %%MERMAID_N%% tokens (possibly wrapped in <p>) with <div class='mermaid'>."""
    for i, block in enumerate(blocks):
        token = f"%%MERMAID_{i}%%"
        inner = block.rstrip()
        div = f'<div class="mermaid">\n{inner}\n</div>'
        # Python markdown-alike converters wrap lone lines in <p>; handle both
        html = html.replace(f"<p>{token}</p>", div)
        html = html.replace(token, div)
    return html


# ---------------------------------------------------------------------------
# Step 2 — Minimal Markdown → HTML converter (stdlib only)
# ---------------------------------------------------------------------------

def md_escape(text):
    """Escape HTML special chars in plain text segments."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def apply_inline(text):
    """Apply inline Markdown: code, bold, italic, links."""
    # Inline code (before bold/italic to protect backtick content)
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{md_escape(m.group(1))}</code>", text)
    # Strikethrough
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)
    # Bold+italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Images ![alt](src) — must come before link rule
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">',
        text,
    )
    # Links [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        text,
    )
    return text


def convert_md(text):
    """Convert Markdown text to HTML. Mermaid blocks must already be tokenised."""
    lines = text.split("\n")
    html_parts = []
    i = 0

    def flush_paragraph(buf):
        if buf:
            content = apply_inline(" ".join(buf))
            html_parts.append(f"<p>{content}</p>")
            buf.clear()

    para_buf = []

    while i < len(lines):
        line = lines[i]

        # ---- Mermaid placeholder (must NOT be wrapped in <p>) ----
        if re.match(r"^%%MERMAID_\d+%%$", line.strip()):
            flush_paragraph(para_buf)
            html_parts.append(line.strip())
            i += 1
            continue

        # ---- Fenced code block (non-mermaid) ----
        if line.startswith("```"):
            flush_paragraph(para_buf)
            lang = line[3:].strip()
            cls = f' class="language-{lang}"' if lang else ""
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(md_escape(lines[i]))
                i += 1
            i += 1  # skip closing ```
            html_parts.append(f"<pre><code{cls}>" + "\n".join(code_lines) + "</code></pre>")
            continue

        # ---- Headings ----
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            flush_paragraph(para_buf)
            level = len(m.group(1))
            content = apply_inline(m.group(2))
            # anchor id from text
            anchor = re.sub(r"[^\w\s-]", "", m.group(2).lower()).strip().replace(" ", "-")
            html_parts.append(f'<h{level} id="{anchor}">{content}</h{level}>')
            i += 1
            continue

        # ---- Horizontal rule ----
        if re.match(r"^-{3,}$", line.strip()) or re.match(r"^\*{3,}$", line.strip()):
            flush_paragraph(para_buf)
            html_parts.append("<hr>")
            i += 1
            continue

        # ---- Table ----
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|?[-:| ]+\|?$", lines[i + 1]):
            flush_paragraph(para_buf)
            header_cells = [c.strip() for c in line.strip("|").split("|")]
            i += 2  # skip separator row
            rows = []
            while i < len(lines) and "|" in lines[i]:
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            th_html = "".join(f"<th>{apply_inline(c)}</th>" for c in header_cells)
            table = f"<table><thead><tr>{th_html}</tr></thead><tbody>"
            for row in rows:
                td_html = "".join(f"<td>{apply_inline(c)}</td>" for c in row)
                table += f"<tr>{td_html}</tr>"
            table += "</tbody></table>"
            html_parts.append(table)
            continue

        # ---- Unordered list ----
        if re.match(r"^[-*]\s+", line):
            flush_paragraph(para_buf)
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append(apply_inline(lines[i][2:].strip()))
                i += 1
            html_parts.append("<ul>" + "".join(f"<li>{it}</li>" for it in items) + "</ul>")
            continue

        # ---- Ordered list ----
        if re.match(r"^\d+\.\s+", line):
            flush_paragraph(para_buf)
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(apply_inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            html_parts.append("<ol>" + "".join(f"<li>{it}</li>" for it in items) + "</ol>")
            continue

        # ---- Blockquote ----
        if line.startswith(">"):
            flush_paragraph(para_buf)
            bq_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                bq_lines.append(lines[i][1:].strip())
                i += 1
            inner = apply_inline(" ".join(bq_lines))
            html_parts.append(f"<blockquote><p>{inner}</p></blockquote>")
            continue

        # ---- Blank line → flush paragraph ----
        if line.strip() == "":
            flush_paragraph(para_buf)
            i += 1
            continue

        # ---- Accumulate paragraph ----
        para_buf.append(md_escape(line).strip())
        i += 1

    flush_paragraph(para_buf)
    return "\n".join(html_parts)


# ---------------------------------------------------------------------------
# Confidence markers
# ---------------------------------------------------------------------------

CONF_BLOCK_RE = re.compile(
    r"<(p|li|td|h[1-6])(\s[^>]*)?>(.*?)</\1>",
    re.DOTALL | re.IGNORECASE,
)
LOW_RE = re.compile(r"\s*\[low\]", re.IGNORECASE)
MED_RE = re.compile(r"\s*\[medium\]", re.IGNORECASE)
HIGH_RE = re.compile(r"\s*\[high\]", re.IGNORECASE)


def _add_class(attrs, cls):
    m = re.search(r'class="([^"]*)"', attrs)
    if m:
        return attrs[: m.start(1)] + m.group(1) + f" {cls}" + attrs[m.end(1) :]
    return attrs + f' class="{cls}"'


def apply_confidence_markers(html):
    def _rep(m):
        tag, attrs, content = m.group(1), m.group(2) or "", m.group(3)
        has_low = LOW_RE.search(content) is not None
        cleaned = HIGH_RE.sub("", MED_RE.sub("", LOW_RE.sub("", content)))
        if has_low:
            attrs = _add_class(attrs, "confidence-low")
        return f"<{tag}{attrs}>{cleaned}</{tag}>"

    html = CONF_BLOCK_RE.sub(_rep, html)
    return HIGH_RE.sub("", MED_RE.sub("", LOW_RE.sub("", html)))


# ---------------------------------------------------------------------------
# Link rewriting and sidebar
# ---------------------------------------------------------------------------

def rewrite_md_links(html):
    return re.sub(r'href="([^"]+)\.md([#"][^"]*)??"',
                  lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', html)


# ---------------------------------------------------------------------------
# Search index
# ---------------------------------------------------------------------------

def _strip_tags(text):
    """Remove HTML tags and decode entities, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = _html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def build_search_index(out_dir):
    """Scrape generated HTML files and write search-index.json."""
    index = []
    for html_file in sorted(out_dir.glob("*.html")):
        if html_file.name == "index.html":
            continue  # alias of readme.html — skip to avoid duplicate
        raw = html_file.read_text(encoding="utf-8")
        art = re.search(r"<article>(.*?)</article>", raw, re.DOTALL)
        if not art:
            continue
        art_html = art.group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", art_html, re.IGNORECASE | re.DOTALL)
        title = _strip_tags(h1.group(1)) if h1 else html_file.stem
        headings = [
            {"text": _strip_tags(m.group(2)), "id": m.group(1)}
            for m in re.finditer(r'<h[23][^>]* id="([^"]+)"[^>]*>(.*?)</h[23]>',
                                 art_html, re.IGNORECASE | re.DOTALL)
        ]
        body = _strip_tags(art_html)
        index.append({"title": title, "url": html_file.name,
                      "headings": headings, "body": body})
    out = out_dir / "search-index.json"
    out.write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print(f"  search-index.json  ({len(index)} pages)")


def parse_kanban_items(md_path):
    """Parse inwork.md or todo.md → list of {title, items[{text, status, layer, beta}]}.

    Beta detection (item.beta = True when any of):
      - H1 section title contains 'Beta' (e.g. '# Beta Backlog' in todo.md)
      - H2 section title is exactly 'Beta' (e.g. '## Beta' in inwork.md)
      - Item text contains the literal token '[BETA]'
    """
    text = md_path.read_text(encoding="utf-8")
    STATUS_MAP = {'x': 'merged', '>': 'needs-pr', 't': 'testing', '~': 'partial', '/': 'started', ' ': 'todo'}
    sections = []
    current = None
    in_beta_h1 = False   # flipped by # Beta … H1 headers
    in_beta_h2 = False   # flipped by ## Beta H2 header
    for line in text.splitlines():
        h1 = re.match(r'^# (.+)', line)
        if h1:
            title = h1.group(1).strip()
            in_beta_h1 = 'beta' in title.lower() and 'alpha' not in title.lower()
            continue
        h2 = re.match(r'^## (.+)', line)
        if h2:
            section_title = h2.group(1).strip()
            in_beta_h2 = section_title.lower() == 'beta'
            current = {'title': section_title, 'items': []}
            sections.append(current)
            continue
        if current is None:
            continue
        m = re.match(r'^- \[([x>t~ /])\] (.*)', line)
        if not m:
            continue
        status_char = m.group(1)
        raw = m.group(2)
        # strip "→ needs PR" suffix before extracting layer
        raw = re.sub(r'\s*→\s*needs PR\s*$', '', raw).strip()
        layer_m = re.search(r'\*\*\[([^\]]+)\]\*\*', raw)
        layer = layer_m.group(1) if layer_m else ''
        # strip trailing layer tag
        clean = re.sub(r'\s*\*\*\[[^\]]+\]\*\*\s*$', '', raw).strip()
        is_beta = in_beta_h1 or in_beta_h2 or '[BETA]' in raw
        current['items'].append({
            'text': clean,
            'status': STATUS_MAP.get(status_char, 'todo'),
            'layer': layer,
            'beta': is_beta,
        })
    return sections


def parse_done(md_path):
    """Parse done.md section summaries → list of {title, summary}."""
    text = md_path.read_text(encoding="utf-8")
    sections = []
    current = None
    for line in text.splitlines():
        h2 = re.match(r'^## (.+)', line)
        if h2:
            current = {'title': h2.group(1).strip(), 'summary': ''}
            sections.append(current)
            continue
        if current is None:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or re.match(r'^-{3,}$', stripped):
            continue
        current['summary'] = (current['summary'] + ' ' + stripped).strip()
    return sections


# ---------------------------------------------------------------------------
# Rulebook coverage data
# status: "done" | "needs-pr" | "partial" | "todo" | "deferred"
# scope:  "alpha" | "beta"   (alpha = needed to ship alpha; beta = sea/OE/Pullman/etc.)
# ---------------------------------------------------------------------------

COVERAGE_DATA = [
    ("Game Setup", [
        ("Player range & starting cash", "done",     "alpha"),
        ("Bank \u00a354,000",           "done",     "alpha"),
        ("Certificate limits",           "done",     "alpha"),
        ("Three-tier hierarchy",         "done",     "alpha"),
        ("Incremental capitalisation",   "done",     "alpha"),
        ("Regional float condition",     "done",     "alpha"),
        ("Regional dump restriction",    "done",     "alpha"),
        ("Patronage tile setup",         "todo",     "beta"),
    ]),
    ("Map & Components", [
        ("651-hex grid",                      "done",    "alpha"),
        ("19 red off-board hexes",            "done",    "alpha"),
        ("Terrain costs",                     "done",    "alpha"),
        ("255 location names",                "done",    "alpha"),
        ("Station slot revenues",             "done",    "alpha"),
        ("Pre-printed yellow tiles",          "done",    "alpha"),
        ("Pre-printed ferry paths",           "done",    "alpha"),
        ("Sea zones (19)",                    "done",    "alpha"),
        ("Ferry sea hexes (partial)",         "partial", "beta"),
        ("Port icons",                        "partial", "alpha"),
        ("Sea zone borders / ferry distances","todo",    "beta"),
        ("Logo SVGs",                         "todo",    "alpha"),
    ]),
    ("Track Rights", [
        ("8 zones defined",                  "done", "alpha"),
        ("Zone fee on par",                  "done", "alpha"),
        ("Zone token restriction",           "done", "alpha"),
        ("Minor zone assignment",            "done", "alpha"),
        ("Asterisked-zone cap (UK/PHS/FR)",  "done", "alpha"),
        ("Dynamic minor regions",            "done", "alpha"),
        ("Home token filtering",             "done", "alpha"),
        ("20% terrain discount zones",       "needs-pr", "alpha"),
    ]),
    ("Auction Phase", [
        ("Waterfall auction tiered rows",    "done", "alpha"),
        ("Minor card \u2192 float + \u00a3120 par", "done", "alpha"),
        ("All-pass price reduction",         "todo", "alpha"),
    ]),
    ("Concession Phase", [
        ("Concession round",             "deferred", "beta"),
        ("Ordered float actions",        "deferred", "beta"),
        ("Float obligation transfer",    "deferred", "beta"),
        ("Round sequencing",             "deferred", "beta"),
        ("2-player without-concessions", "deferred", "beta"),
    ]),
    ("Stock Market Grid", [
        ("8\u00d717 grid with prices",       "done",     "alpha"),
        ("Par colour bands",                  "done",     "alpha"),
        ("LEFT (zero dividend)",              "needs-pr", "alpha"),
        ("No movement (below par)",           "needs-pr", "alpha"),
        ("RIGHT (at/above par)",              "needs-pr", "alpha"),
        ("Minors/regionals exempt",           "done",     "alpha"),
        ("UP end-of-SR (no OM shares)",       "done",     "alpha"),
        ("Sold-out order (hi→lo price)", "needs-pr", "alpha"),
        ("Post-conversion sell window",       "done",     "alpha"),
        ("Reserved secondary shares",         "todo",     "alpha"),
        (">60% president pool buy at 2×","needs-pr", "alpha"),
        ("+3 RIGHT on OE first run",          "todo",     "beta"),
        ("Voluntary regional removal",        "todo",     "alpha"),
        ("§11.7 issuance DOWN movement", "needs-pr", "alpha"),
    ]),
    ("Train Data & Phases", [
        ("7-level roster",                "done", "alpha"),
        ("Rust triggers (L4/L6/L8)",      "done", "alpha"),
        ("L8 unlock after 4th L7",        "needs-pr", "alpha"),
        ("8 named phases",                "done", "alpha"),
        ("Tile colour by phase",          "done", "alpha"),
        ("Status flags",                  "done", "alpha"),
        ("Consolidation event on L5",     "done", "alpha"),
        ("National corp type",            "done", "alpha"),
        ("Level 3 restriction first OR",  "done", "alpha"),
    ]),
    ("Track Laying", [
        ("OE1\u2013OE3 yellow double-town",      "done", "alpha"),
        ("OE4\u2013OE8 yellow city",             "done", "alpha"),
        ("OE12\u2013OE18 green city",            "done", "alpha"),
        ("OE23\u2013OE33 brown city",            "done", "alpha"),
        ("OE34\u2013OE44 gray city",             "done", "alpha"),
        ("Tile point budgets",                    "done", "alpha"),
        ("Tile point costs",                      "done", "alpha"),
        ("TILE_UPGRADES_MUST_USE_MAX_EXITS",      "done", "alpha"),
        ("Metropolis upgrade labels",             "done", "alpha"),
        ("Nationals pay no terrain",              "todo", "beta"),
        ("OE9\u2013OE11 green double-town",      "todo", "alpha"),
        ("OE20\u2013OE22 brown double-town",     "todo", "alpha"),
        ("OE19 unknown tile",                     "todo", "alpha"),
        ("Tile quantities verify",                "todo", "alpha"),
        ("First-OR green tile exception",         "todo", "alpha"),
        ("Patronage tile payout",                 "todo", "beta"),
    ]),
    ("Token Placement", [
        ("Zone restriction",            "done",    "alpha"),
        ("Connectivity check",          "done",    "alpha"),
        ("Nationals skip token step",   "done",    "alpha"),
        ("Lille White Cliffs position", "partial", "alpha"),
        ("Cross-water token costs",     "todo",    "beta"),
    ]),
    ("Route & Revenue (Cross-Water)", [
        ("Sea zone data",              "done", "alpha"),
        ("Cross-water track costs",    "todo", "beta"),
        ("Cross-water token costs",    "todo", "beta"),
        ("Ferry mechanics / distance", "todo", "beta"),
        ("Port authority purchase",    "todo", "beta"),
        ("Port authority transfer",    "todo", "beta"),
        ("Port types (public/private)","todo", "beta"),
        ("Offshore port mechanics",    "todo", "beta"),
        ("Channel passages",           "todo", "beta"),
        ("Local train town counting",  "todo", "beta"),
        ("Combined train runs",        "todo", "beta"),
    ]),
    ("Orient Express", [
        ("OE route detection",            "todo", "beta"),
        ("First-time bonus by phase",     "todo", "beta"),
        ("+3 RIGHT on first run",         "todo", "beta"),
        ("Train combining for OE",        "todo", "beta"),
        ("Subsequent runs (no bonus)",    "todo", "beta"),
        ("Mandatory OE rule",             "todo", "beta"),
        ("OE blocked for nationals",      "todo", "beta"),
        ("D-train no double on OE bonus", "todo", "beta"),
    ]),
    ("Pullman Cars", [
        ("Pullman asset type",          "todo", "beta"),
        ("Revenue bonus +\u00a310/level","todo","beta"),
        ("Purchase from Minor M",       "todo", "beta"),
        ("Purchase from Open Market",   "todo", "beta"),
        ("Purchase from another RR",    "todo", "beta"),
        ("Minor M free Pullman (Ph4)",  "todo", "beta"),
        ("Discard / return to OM",      "todo", "beta"),
        ("Zero trains + Pullman retain","todo", "beta"),
    ]),
    ("Train Purchase", [
        ("Reserved 2+2 obligation",      "done",     "alpha"),
        ("Phase-status check",           "done",     "alpha"),
        ("Depot level gating",           "done",     "alpha"),
        ("Inter-RR purchase Phase 4+",   "done",     "alpha"),
        ("Train type lock inter-RR",     "todo",     "alpha"),
        ("Nationals claim rusted trains","needs-pr", "beta"),
        ("Forced purchase",              "todo",     "alpha"),
        ("First-round insolvency",       "todo",     "alpha"),
    ]),
    ("OR Steps (Major)", [
        ("Operating order by share price","done", "alpha"),
        ("Lay Track",                    "done", "alpha"),
        ("Place Token",                  "done", "alpha"),
        ("Run Trains / Revenue",         "done", "alpha"),
        ("Pay / Split / Hold",           "done", "alpha"),
        ("Transfer Tokens",              "todo", "alpha"),
        ("Buy Trains",                   "done", "alpha"),
        ("Buy/Sell Own Shares (\u00a711.7)", "done",    "alpha"),
        ("Buy Abandoned Minor (\u00a711.7)", "todo", "alpha"),
    ]),
    ("Stock Rounds", [
        ("Sell-then-buy order",          "done",     "alpha"),
        ("Home token in SR",             "done",     "alpha"),
        ("Regional\u2192major conversion","done",   "alpha"),
        ("Share issuance for majors",    "done",     "alpha"),
        ("Minor SR merge action",        "needs-pr", "beta"),
        ("Change of presidency",         "done",     "alpha"),
        ("Trade with another player",    "todo",     "alpha"),
    ]),
    ("Railroad Formation", [
        ("Floating a minor",             "done", "alpha"),
        ("Floating a regional",          "done", "alpha"),
        ("Floating a major",             "done", "alpha"),
        ("Forming a national (trigger)", "todo", "beta"),
        ("Forming a national (steps)",   "todo", "beta"),
        ("Abandoning a minor",           "todo", "beta"),
    ]),
    ("Nationals", [
        ("National type in train limits", "done", "alpha"),
        ("National region hexes",         "done", "alpha"),
        ("Formation trigger",             "todo", "beta"),
        ("ConvertToNational step",        "todo", "beta"),
        ("National revenue",              "todo", "beta"),
        ("Inherent Pullman",              "todo", "beta"),
        ("No tokens / no terrain",        "todo", "beta"),
        ("Rusted train claim",            "todo", "beta"),
        ("Train exchange/flip/upgrade",   "todo", "beta"),
        ("Merged minors abandoned",       "todo", "beta"),
        ("Track rights removed on form.", "todo", "beta"),
    ]),
    ("Track Rights Chit System", [
        ("MINOR_TRACK_RIGHTS_CHITS", "done", "alpha"),
        ("Asterisked zones cap",     "done", "alpha"),
        ("region_available? / cost", "done", "alpha"),
        ("HomeToken process",        "done", "alpha"),
        ("major_phase?",             "done", "alpha"),
    ]),
    ("Minor Mergers", [
        ("Minor SR merge action",       "needs-pr", "beta"),
        ("Plumbing / can_merge",        "needs-pr", "beta"),
        ("merge_minor!",                "needs-pr", "beta"),
        ("No-stock connection check",   "todo",     "beta"),
        ("Token conflict choice",       "todo",     "beta"),
        ("Side payment UI",             "todo",     "beta"),
        ("Solicit-offers rule",         "todo",     "beta"),
        ("Consolidation forced mergers","todo",     "beta"),
    ]),
    ("Consolidation Phase", [
        ("L5 trigger scaffold",          "done",     "alpha"),
        ("Cannot pass with minors",      "todo",     "beta"),
        ("Conditional merger / abandon", "todo",     "beta"),
    ]),
    ("Token Transfer Between Majors", [
        ("Transfer token between majors","todo", "alpha"),
        ("Transfer cost schedule",       "todo", "alpha"),
        ("Sell token back to charter",   "todo", "alpha"),
        ("Port authority transfer",      "todo", "beta"),
    ]),
    ("End Game", [
        ("Bank break pre-L8 timing",     "needs-pr", "alpha"),
        ("L8 purchase end trigger",      "needs-pr", "alpha"),
        ("Remainder cash injection",     "needs-pr", "alpha"),
        ("Final two OR sequence",        "todo", "beta"),
        ("Second final OR (repeat rev.)","todo", "beta"),
        ("Bankrupt trigger removed",     "needs-pr", "alpha"),
        ("Win condition (scoring)",      "done", "alpha"),
    ]),
    ("Minor Abilities", [
        ("A \u2013 Silver Banner",          "todo",     "alpha"),
        ("B \u2013 Orange Scroll",          "done",     "alpha"),
        ("C \u2013 Golden Bell",            "partial",  "alpha"),
        ("D \u2013 Green Junction",         "partial",  "alpha"),
        ("E \u2013 Blue Coast",             "done",     "alpha"),
        ("F \u2013 White Peak",             "done",     "alpha"),
        ("G \u2013 Indigo Foundry",         "done",     "alpha"),
        ("H \u2013 Great Western Steamship","todo",     "beta"),
        ("J \u2013 Grey Locomotive",        "needs-pr", "alpha"),
        ("K \u2013 Vermilion Seal",         "done",     "alpha"),
        ("L \u2013 Krasnaya Strela",        "partial",  "alpha"),
        ("M \u2013 CIWL Pullmans",          "todo",     "beta"),
        ("Ability transfer on merge",        "todo",     "beta"),
    ]),
    ("Private Abilities", [
        ("Robert Stephenson (none)",   "done",    "alpha"),
        ("Ponts et Chauss\u00e9es (none)", "done", "alpha"),
        ("Wien S\u00fcdbahn hof",     "partial", "beta"),
        ("Barclay, Bevan & Tritton",   "todo",    "alpha"),
        ("Star Harbor",                "partial", "beta"),
        ("Central Circle",             "partial", "alpha"),
        ("White Cliffs Ferry",         "partial", "beta"),
        ("Hochberg Mining",            "partial", "alpha"),
        ("Brandt & Brandau",           "partial", "alpha"),
        ("Swift Metropolitan Line",    "todo",    "alpha"),
    ]),
    ("Patronage Tiles", [
        ("Setup randomisation",          "todo", "beta"),
        ("Payout on track lay",          "todo", "beta"),
        ("Minor float on patronage hex", "todo", "beta"),
    ]),
    ("Variants & Scenarios", [
        ("UK-FR variant entities",    "deferred", "beta"),
        ("UK-FR train rusting",       "deferred", "beta"),
        ("UK-FR map hexes",           "deferred", "beta"),
        ("Medium / short scenarios",  "deferred", "beta"),
    ]),
]

# ---------------------------------------------------------------------------
# Map status overview table  (drives the "Overall Status" section of
# 18oe-map-status.html — edit here, regenerate, done)
# status: "done" | "needs-pr" | "partial" | "todo"
# ---------------------------------------------------------------------------

MAP_STATUS_TABLE = [
    ("Grid coverage",                   "done",    "651 blue hexes"),
    ("Regional home city coordinates",  "done",    "All 24"),
    ("National region hex lists",       "done",    "All 8 (UK, SC, FR, PHS, AH, IT, SP, RU) — "
                                                   "<code>NATIONAL_REGION_HEXES_COMPLETE = true</code>"),
    ("Location names",                  "done",    "All 255"),
    ("Sea zones",                       "done",    "19 named zones with hex lists; borders encoded as "
                                                   "<code>type:province</code>; port stubs on 37 sea tiles"),
    ("Custom tile codes",               "done",    "OE1–OE8, OE12–OE18, OE23–OE44"),
    ("Standard tile quantities",        "done",    "Complete"),
    ("Terrain costs",                   "done",    "UK, FR, SP, SC, Alps, IT, Adriatic, Carpathians, "
                                                   "Balkans, Caucasus, river crossings"),
    ("Station revenues",                "done",    "All 255 named locations have correct starting revenue"),
    ("Pre-printed yellows",             "done",    "Liverpool J25, Manchester J27, Athinai AE72"),
    ("Pre-printed whites (path edges)", "partial", "Several cities missing path edges — see §3"),
    ("Port icons",                      "partial", "Stubs present; public/private classification outstanding"),
    ("Ferry paths / distances",         "todo",    "Outstanding"),
    ("Double-town tile orientations",   "todo",    "OE9–11, OE20–22 outstanding"),
    ("Logo SVGs",                       "todo",    "Company logos not yet added"),
]

# ---------------------------------------------------------------------------
# Weighted progress system
# Each section has a base effort weight (L1≈0.5–1 · L2≈2 · L3≈3).
# Status items carry [L1]/[L2]/[L3] tags that override the section default.
# ---------------------------------------------------------------------------

SECTION_BASE_WEIGHTS = {
    # Mostly data / constants (L1)
    'Game Setup':                     0.5,
    'Map & Components':               0.5,
    'Track Rights Chit System':       1.0,
    'Train Data & Phases':            1.0,
    'Variants & Scenarios':           0.5,
    'Patronage Tiles':                1.0,
    # Light game logic (L1-L2)
    'Concession Phase':               1.5,
    'Auction Phase':                  1.5,
    'Track Laying':                   1.5,
    'Token Placement':                1.5,
    # Medium game logic (L2)
    'Stock Market Grid':              2.0,
    'Stock Rounds':                   2.0,
    'Train Purchase':                 2.0,
    'Minor Abilities':                2.0,
    'Private Abilities':              2.0,
    'Token Transfer Between Majors':  2.0,
    'Pullman Cars':                   2.0,
    # Heavy (L2-L3)
    'End Game':                       2.5,
    'Consolidation Phase':            2.5,
    'OR Steps (Major)':               2.5,
    'Route & Revenue (Cross-Water)':  2.5,
    'Railroad Formation':             2.5,
    'Minor Mergers':                  2.5,
    # Very heavy (L3 full systems)
    'Nationals':                      3.0,
    'Orient Express':                 3.0,
}
_DEFAULT_SECTION_WEIGHT = 1.5

LAYER_WEIGHTS = {
    'L1': 1.0, 'L2': 2.0, 'L3': 3.0,
    'L1/L2': 1.5, 'L2/L3': 2.5, 'L1/L2/L3': 2.0,
    'non-code': 0.5, 'upstream': 0.5,
}
_DEFAULT_LAYER_WEIGHT = 1.5


def coverage_item_weight(section, _name=''):
    return SECTION_BASE_WEIGHTS.get(section, _DEFAULT_SECTION_WEIGHT)


def layer_weight(layer_str):
    return LAYER_WEIGHTS.get(layer_str or '', _DEFAULT_LAYER_WEIGHT)


def weighted_coverage_stats(scope_filter=None):
    """Return (done_w, pr_w, partial_w, todo_w, deferred_w) floats."""
    done = pr = partial = todo = deferred = 0.0
    for section, items in COVERAGE_DATA:
        for item in items:
            name, status, scope = item[:3]
            if scope_filter and scope != scope_filter:
                continue
            w = coverage_item_weight(section, name)
            if   status == 'done':     done     += w
            elif status == 'needs-pr': pr       += w
            elif status == 'partial':  partial  += w * 0.5; todo += w * 0.5
            elif status == 'todo':     todo     += w
            elif status == 'deferred': deferred += w
    return done, pr, partial, todo, deferred


def build_shared_bar(rows, chips):
    """
    Uniform progress bar block used on all three dashboard pages.

    rows  – list of dicts: {label, done, pr, partial, todo, total, right}
    chips – list of dicts: {cls, label, value}
    """
    p = []
    p.append('<div class="bar-rows">')
    for row in rows:
        total = row['total'] or 1.0
        def _pct(k, t=total): return f"{row[k] / t * 100:.1f}%"
        p.append('<div class="bar-row">')
        if row.get('label'):
            p.append(f'<span class="bar-label-left">{row["label"]}</span>')
        p.append('<div class="progress-track">')
        p.append(f'<div class="pb-done"    style="width:{_pct("done")}"></div>')
        p.append(f'<div class="pb-pr"      style="width:{_pct("pr")}"></div>')
        p.append(f'<div class="pb-partial" style="width:{_pct("partial")}"></div>')
        p.append(f'<div class="pb-todo"    style="width:{_pct("todo")}"></div>')
        p.append('</div>')
        if row.get('right'):
            p.append(f'<span class="bar-label-right">{row["right"]}</span>')
        p.append('</div>')  # .bar-row
    p.append('</div>')  # .bar-rows
    if chips:
        p.append('<div class="status-summary" style="margin:0.5rem 0 1.2rem">')
        for chip in chips:
            p.append(
                f'<div class="stat-chip {chip["cls"]}">'
                f'{chip["label"]} <span>{chip["value"]}</span>'
                f'</div>'
            )
        p.append('</div>')
    return '\n'.join(p)


def _layer_grouped_items(sections, valid_statuses):
    """Collect items from sections, grouped by layer tag, sorted L1→L2→L3→compound→other."""
    LAYER_RANK  = {'L1': 0, 'L2': 1, 'L3': 2, 'non-code': 4}
    STATUS_RANK = {'needs-pr': 0, 'partial': 1, 'todo': 2}

    def layer_sort_key(layer):
        if layer in LAYER_RANK:
            return (LAYER_RANK[layer], layer)
        first = re.split(r'[/ ]', layer)[0] if layer else ''
        return (LAYER_RANK.get(first, 3), layer)

    groups = {}
    for sec in sections:
        for it in sec['items']:
            if it['status'] in valid_statuses:
                key = it['layer'] or 'untagged'
                if key not in groups:
                    groups[key] = []
                groups[key].append(it)

    for key in groups:
        groups[key].sort(key=lambda it: STATUS_RANK.get(it['status'], 3))

    return sorted(groups.items(), key=lambda kv: layer_sort_key(kv[0]))


def build_status_html():
    """Generate status.html from MD/inwork.md, MD/todo.md, MD/done.md."""
    inwork_path = MD_DIR / "inwork.md"
    todo_path   = MD_DIR / "todo.md"
    done_path   = MD_DIR / "done.md"
    if not (inwork_path.exists() and todo_path.exists() and done_path.exists()):
        print("  status.html  (skipped — MD/ files not found)")
        return

    inwork_sections = parse_kanban_items(inwork_path)
    todo_sections   = parse_kanban_items(todo_path)
    done_sections   = parse_done(done_path)

    # Raw item counts (for display only)
    count_done    = len(done_sections)
    count_pr      = sum(1 for s in inwork_sections for it in s['items'] if it['status'] == 'needs-pr')
    count_partial = sum(1 for s in inwork_sections for it in s['items'] if it['status'] in ('partial', 'testing'))
    count_started = sum(1 for s in todo_sections   for it in s['items'] if it['status'] == 'started')
    count_todo    = sum(1 for s in todo_sections   for it in s['items'] if it['status'] == 'todo')
    count_inwork  = count_pr + count_partial
    count_beta    = (sum(1 for s in inwork_sections for it in s['items'] if it.get('beta')) +
                     sum(1 for s in todo_sections   for it in s['items'] if it.get('beta')))

    def _is_alpha(it): return not it.get('beta')

    # Weighted sums — each item weighted by its layer tag
    def _w(it): return layer_weight(it.get('layer', ''))

    w_done    = sum(_w(it) for s in done_sections
                    for it in [{'layer': ''}])                                             # done items lack tags → default
    w_done    = count_done * _DEFAULT_LAYER_WEIGHT                                         # approximate done with average
    w_pr      = sum(_w(it) for s in inwork_sections for it in s['items'] if it['status'] == 'needs-pr')
    w_partial = sum(_w(it) * 0.5 for s in inwork_sections for it in s['items']
                    if it['status'] in ('partial', 'testing'))
    w_partial_rem = w_partial                                                               # remaining half of partials
    # started items (todo.md [/]) count as 30% done (wiring exists, completion pending)
    w_started = sum(_w(it) * 0.3 for s in todo_sections for it in s['items'] if it['status'] == 'started')
    w_started_rem = sum(_w(it) * 0.7 for s in todo_sections for it in s['items'] if it['status'] == 'started')
    w_todo    = (sum(_w(it) for s in todo_sections for it in s['items'] if it['status'] == 'todo')
                 + w_partial_rem + w_started_rem)
    w_total   = w_done + w_pr + w_partial + w_started + w_todo or 1.0

    # Alpha-scoped weighted sums
    w_done_a    = w_done  # all done items count for alpha (they were alpha when done)
    w_pr_a      = sum(_w(it) for s in inwork_sections for it in s['items']
                      if it['status'] == 'needs-pr' and _is_alpha(it))
    w_partial_a = sum(_w(it) * 0.5 for s in inwork_sections for it in s['items']
                      if it['status'] in ('partial', 'testing') and _is_alpha(it))
    w_started_a = sum(_w(it) * 0.3 for s in todo_sections for it in s['items']
                      if it['status'] == 'started' and _is_alpha(it))
    w_started_rem_a = sum(_w(it) * 0.7 for s in todo_sections for it in s['items']
                          if it['status'] == 'started' and _is_alpha(it))
    w_todo_a    = (sum(_w(it) for s in todo_sections for it in s['items']
                       if it['status'] == 'todo' and _is_alpha(it))
                   + sum(_w(it) * 0.5 for s in inwork_sections for it in s['items']
                         if it['status'] in ('partial', 'testing') and _is_alpha(it))
                   + w_started_rem_a)
    w_total_a   = w_done_a + w_pr_a + w_partial_a + w_started_a + w_todo_a or 1.0

    alpha_done_pct = round((w_done_a + w_pr_a) / w_total_a * 100)
    alpha_remaining_n = (sum(1 for s in inwork_sections for it in s['items']
                              if it['status'] in ('partial', 'testing') and _is_alpha(it)) +
                         sum(1 for s in todo_sections for it in s['items']
                              if it['status'] in ('todo', 'started') and _is_alpha(it)))

    p = []
    p.append('<h1>18OE — Implementation Tracker</h1>')
    p.append('<p class="page-crosslink">For the full rulebook picture → '
             '<a href="rulebook-coverage.html">Rulebook Coverage</a> · '
             'Alpha gaps → <a href="alpha-gaps.html">Open for Alpha</a></p>')
    p.append('<p class="bar-note">Bar widths reflect implementation effort '
             '(L3 step/round = 3× · L2 override = 2× · L1 constant = 1×), '
             'not item count.</p>')

    bar_html = build_shared_bar(
        rows=[
            {'label': 'Overall', 'done': w_done, 'pr': w_pr, 'partial': w_partial + w_started,
             'todo': w_todo, 'total': w_total,
             'right': f'{count_done + count_pr}&thinsp;/&thinsp;{count_done + count_pr + count_partial + count_started + count_todo} items'},
            {'label': 'Alpha', 'done': w_done_a, 'pr': w_pr_a, 'partial': w_partial_a + w_started_a,
             'todo': w_todo_a, 'total': w_total_a,
             'right': (f'{alpha_done_pct}%'
                       f'<span class="bar-aside"> · {alpha_remaining_n} remaining'
                       + (f' · <span class="bar-beta">{count_beta} beta deferred</span>' if count_beta else '')
                       + '</span>')},
        ],
        chips=[
            {'cls': 'stat-done',    'label': 'Done &amp; merged', 'value': str(count_done)},
            {'cls': 'stat-pr',      'label': 'Needs PR',          'value': str(count_pr)},
            {'cls': 'stat-partial', 'label': 'Partial',           'value': str(count_partial)},
            {'cls': 'stat-partial', 'label': 'Started',           'value': str(count_started)},
            {'cls': 'stat-todo',    'label': 'To do',             'value': str(count_todo)},
        ] + ([{'cls': 'stat-beta', 'label': 'Beta deferred', 'value': str(count_beta)}] if count_beta else []),
    )
    p.append(bar_html)

    # Filter + group bar
    p.append('<div class="status-filters">')
    p.append('<span class="filter-label">Milestone:</span>')
    p.append('<button class="milestone-btn active" data-scope="">All</button>')
    p.append('<button class="milestone-btn" data-scope="alpha">Alpha</button>')
    p.append('<button class="milestone-btn" data-scope="beta">Beta</button>')
    p.append('<span class="filter-sep"></span>')
    p.append('<span class="filter-label">Layer:</span>')
    p.append('<button class="layer-btn active" data-layer="">All</button>')
    p.append('<button class="layer-btn" data-layer="L1">L1</button>')
    p.append('<button class="layer-btn" data-layer="L2">L2</button>')
    p.append('<button class="layer-btn" data-layer="L3">L3</button>')
    p.append('<span class="filter-sep"></span>')
    p.append('<span class="filter-label">Group by:</span>')
    p.append('<button class="group-btn active" data-group="rules">Rules</button>')
    p.append('<button class="group-btn" data-group="layer">Layer</button>')
    p.append('</div>')

    # Board
    p.append('<div class="status-board">')

    # --- Done column ---
    p.append('<div class="sb-col">')
    p.append(f'<div class="sb-col-header done-col">Done &amp; Merged<span class="sb-col-count">{count_done}</span></div>')
    p.append('<div class="sb-col-body">')
    for sec in done_sections:
        p.append('<div class="sb-done-card">')
        p.append(f'<div class="sb-done-title">{_html.escape(sec["title"])}</div>')
        if sec['summary']:
            p.append(f'<div class="sb-done-summary">{_html.escape(sec["summary"])}</div>')
        p.append('</div>')
    p.append('</div></div>')

    # --- In Work column ---
    p.append('<div class="sb-col">')
    p.append(f'<div class="sb-col-header inwork-col">In Work<span class="sb-col-count">{count_inwork}</span></div>')
    # rules view (default)
    p.append('<div class="sb-col-body view-rules">')
    for sec in inwork_sections:
        items = [it for it in sec['items'] if it['status'] in ('needs-pr', 'partial')]
        if not items:
            continue
        p.append('<div class="sb-section">')
        p.append(f'<div class="sb-section-title">{_html.escape(sec["title"])}</div>')
        for it in items:
            layer = _html.escape(it['layer'])
            text  = apply_inline(it['text'])
            cls   = 'sb-needs-pr' if it['status'] == 'needs-pr' else 'sb-partial'
            scope = 'beta' if it.get('beta') else 'alpha'
            p.append(
                f'<div class="sb-item {cls}" data-layer="{layer}" data-scope="{scope}">'
                f'<div class="sb-status-dot"></div>'
                f'<span class="sb-item-text">{text}</span>'
                f'<span class="layer-tag">{layer}</span>'
                f'</div>'
            )
        p.append('</div>')
    p.append('</div>')
    # layer view (hidden until toggled)
    p.append('<div class="sb-col-body view-layer" style="display:none">')
    for layer_name, items in _layer_grouped_items(inwork_sections, ('needs-pr', 'partial')):
        p.append('<div class="sb-section">')
        p.append(f'<div class="sb-section-title">{_html.escape(layer_name)}</div>')
        for it in items:
            layer = _html.escape(it['layer'])
            text  = apply_inline(it['text'])
            cls   = 'sb-needs-pr' if it['status'] == 'needs-pr' else 'sb-partial'
            scope = 'beta' if it.get('beta') else 'alpha'
            p.append(
                f'<div class="sb-item {cls}" data-layer="{layer}" data-scope="{scope}">'
                f'<div class="sb-status-dot"></div>'
                f'<span class="sb-item-text">{text}</span>'
                f'</div>'
            )
        p.append('</div>')
    p.append('</div></div>')

    # --- To Do column ---
    p.append('<div class="sb-col">')
    p.append(f'<div class="sb-col-header todo-col">To Do'
             f'<span class="sb-col-count">{count_started + count_todo}</span></div>')
    # rules view (default)
    p.append('<div class="sb-col-body view-rules">')
    for sec in todo_sections:
        items = [it for it in sec['items'] if it['status'] in ('started', 'todo')]
        if not items:
            continue
        p.append('<div class="sb-section">')
        p.append(f'<div class="sb-section-title">{_html.escape(sec["title"])}</div>')
        for it in items:
            layer = _html.escape(it['layer'])
            text  = apply_inline(it['text'])
            scope = 'beta' if it.get('beta') else 'alpha'
            if it['status'] == 'started':
                p.append(
                    f'<div class="sb-item sb-started" data-layer="{layer}" data-scope="{scope}">'
                    f'<div class="sb-status-dot"></div>'
                    f'<span class="sb-item-text">{text}</span>'
                    f'<span class="layer-tag">{layer}</span>'
                    f'<span class="started-badge">started</span>'
                    f'</div>'
                )
            else:
                p.append(
                    f'<div class="sb-item sb-todo" data-layer="{layer}" data-scope="{scope}">'
                    f'<div class="sb-status-dot"></div>'
                    f'<span class="sb-item-text">{text}</span>'
                    f'<span class="layer-tag">{layer}</span>'
                    f'</div>'
                )
        p.append('</div>')
    p.append('</div>')
    # layer view (hidden until toggled)
    p.append('<div class="sb-col-body view-layer" style="display:none">')
    for layer_name, items in _layer_grouped_items(todo_sections, ('started', 'todo')):
        p.append('<div class="sb-section">')
        p.append(f'<div class="sb-section-title">{_html.escape(layer_name)}</div>')
        for it in items:
            layer = _html.escape(it['layer'])
            text  = apply_inline(it['text'])
            scope = 'beta' if it.get('beta') else 'alpha'
            cls = 'sb-started' if it['status'] == 'started' else 'sb-todo'
            badge = '<span class="started-badge">started</span>' if it['status'] == 'started' else ''
            p.append(
                f'<div class="sb-item {cls}" data-layer="{layer}" data-scope="{scope}">'
                f'<div class="sb-status-dot"></div>'
                f'<span class="sb-item-text">{text}</span>'
                f'{badge}'
                f'</div>'
            )
        p.append('</div>')
    p.append('</div></div>')

    p.append('</div>')  # .status-board

    content = '\n'.join(p)
    sidebar_html = build_sidebar('status.html')
    full_html = HTML_TEMPLATE.format(
        title='Implementation Tracker',
        mermaid_cdn=MERMAID_CDN,
        sidebar=sidebar_html,
        content=content,
    )
    (OUT_DIR / 'status.html').write_text(full_html, encoding='utf-8')
    print(f'  status.html  ({count_done} done \xb7 {count_pr} needs-PR \xb7 {count_partial} partial \xb7 {count_todo} todo)')


def build_coverage_html():
    """Generate rulebook-coverage.html from COVERAGE_DATA."""
    STATUS_LABEL = {
        'done':     'Done & merged',
        'needs-pr': 'Needs PR',
        'partial':  'Partial',
        'todo':     'To do',
        'deferred': 'Deferred',
    }
    SWATCH_COLOR = {
        'done':     '#2d7a2d',
        'needs-pr': '#2a4ab0',
        'partial':  '#b87800',
        'todo':     'rgba(13,31,56,0.12)',
        'deferred': 'repeating-linear-gradient(45deg,rgba(100,80,60,0.15) 0px,rgba(100,80,60,0.15) 3px,transparent 3px,transparent 6px)',
    }

    # Raw item counts (for chips display)
    counts = {s: 0 for s in STATUS_LABEL}
    for _, items in COVERAGE_DATA:
        for item in items:
            _name, status, _scope = item[:3]
            counts[status] = counts.get(status, 0) + 1
    total_items = sum(counts.values())

    # Weighted stats — overall and alpha-only
    wd, wpr, wpa, wto, wde = weighted_coverage_stats()
    w_total = wd + wpr + wpa + wto or 1.0
    done_pct = round((wd + wpr) / w_total * 100)

    wd_a, wpr_a, wpa_a, wto_a, _ = weighted_coverage_stats(scope_filter='alpha')
    w_total_a = wd_a + wpr_a + wpa_a + wto_a or 1.0
    alpha_pct = round((wd_a + wpr_a) / w_total_a * 100)

    p = []
    p.append('<h1>18OE — Rulebook Coverage</h1>')
    p.append('<p class="page-crosslink">For current sprint state → '
             '<a href="status.html">Implementation Tracker</a> · '
             'Alpha gaps → <a href="alpha-gaps.html">Open for Alpha</a></p>')
    p.append(f'<p style="color:#5a4a38;font-size:0.9rem;margin-bottom:0.5rem">'
             f'{total_items} mechanics tracked across {len(COVERAGE_DATA)} rulebook chapters.</p>')
    p.append('<p class="bar-note">Bar widths weighted by section effort (L3 systems = 3× · '
             'L2 overrides = 2× · L1 data = 1×).</p>')

    bar_html = build_shared_bar(
        rows=[
            {'label': 'Overall', 'done': wd, 'pr': wpr, 'partial': wpa, 'todo': wto,
             'total': w_total,
             'right': f'<strong>{done_pct}%</strong> implemented or in review'},
            {'label': 'Alpha',   'done': wd_a, 'pr': wpr_a, 'partial': wpa_a, 'todo': wto_a,
             'total': w_total_a,
             'right': f'<strong>{alpha_pct}%</strong> alpha scope done'},
        ],
        chips=[
            {'cls': 'stat-done',    'label': 'Done &amp; merged', 'value': str(counts['done'])},
            {'cls': 'stat-pr',      'label': 'Needs PR',          'value': str(counts['needs-pr'])},
            {'cls': 'stat-partial', 'label': 'Partial',           'value': str(counts['partial'])},
            {'cls': 'stat-todo',    'label': 'To do',             'value': str(counts['todo'])},
            {'cls': 'stat-todo',    'label': 'Deferred',          'value': str(counts['deferred'])},
        ],
    )
    p.append(bar_html)

    # milestone filter
    p.append('<div class="status-filters" style="margin-bottom:1rem">')
    p.append('<span class="filter-label">Milestone:</span>')
    p.append('<button class="milestone-btn active" data-scope="">All</button>')
    p.append('<button class="milestone-btn" data-scope="alpha">Alpha</button>')
    p.append('<button class="milestone-btn" data-scope="beta">Beta</button>')
    p.append('</div>')

    # legend
    p.append('<div class="cov-legend">')
    for s, label in STATUS_LABEL.items():
        color = SWATCH_COLOR[s]
        if 'gradient' in color:
            bg = f'background:{color};border:1px solid rgba(120,100,70,0.25)'
        else:
            bg = f'background:{color}'
        p.append(
            f'<div class="cov-legend-item">'
            f'<div class="cov-legend-swatch" style="{bg}"></div>'
            f'{_html.escape(label)}'
            f'</div>'
        )
    p.append('</div>')

    # heatmap grid
    p.append('<div class="coverage-map">')
    for chapter, items in COVERAGE_DATA:
        anchor = re.sub(r'[^\w\s-]', '', chapter.lower()).strip().replace(' ', '-')
        # chapter scope: "alpha" if any alpha item; "beta" if all beta/deferred
        all_scopes = [scope for _, _, scope in items]
        chapter_scope = 'beta' if all(s == 'beta' for s in all_scopes) else 'mixed'
        p.append(f'<div class="cov-chapter" data-chapter-scope="{chapter_scope}">')
        p.append(f'<div class="cov-chapter-title" id="{anchor}">{_html.escape(chapter)}</div>')
        p.append('<div class="cov-items">')
        for label, status, scope in items:
            p.append(
                f'<div class="cov-item cov-{status}" data-scope="{scope}" title="{_html.escape(label)}">'
                f'{_html.escape(label)}'
                f'</div>'
            )
        p.append('</div></div>')
    p.append('</div>')

    content = '\n'.join(p)
    sidebar_html = build_sidebar('rulebook-coverage.html')
    full_html = HTML_TEMPLATE.format(
        title='Rulebook Coverage',
        mermaid_cdn=MERMAID_CDN,
        sidebar=sidebar_html,
        content=content,
    )
    (OUT_DIR / 'rulebook-coverage.html').write_text(full_html, encoding='utf-8')
    done_n = counts['done'] + counts['needs-pr']
    print(f'  rulebook-coverage.html  ({done_n}/{total_items} implemented or in review, {done_pct}%)')


def build_sidebar(active_file):
    lines = ['<nav id="sidebar" aria-label="Navigation">']
    lines.append('<input id="nav-search" type="search" placeholder="Search…" aria-label="Search documentation" autocomplete="off">')
    # Results panel — hidden until a query is entered
    lines.append('<div id="search-results" style="display:none">')
    lines.append('<p id="search-no-results" style="display:none">No results found.</p>')
    lines.append('<ul id="search-results-list"></ul>')
    lines.append('</div>')
    for track_name, pages in SIDEBAR:
        lines.append(f'<div class="track"><h3>{track_name}</h3><ul>')
        for label, filename in pages:
            if filename == active_file:
                lines.append(
                    f'<li><a href="{filename}" aria-current="page"><strong>{label}</strong></a></li>'
                )
            else:
                lines.append(f'<li><a href="{filename}">{label}</a></li>')
        lines.append("</ul></div>")
    lines.append("</nav>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — 18OE Dev Docs</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script src="{mermaid_cdn}"></script>
<script>mermaid.initialize({{ startOnLoad: true, theme: 'base', themeVariables: {{
  primaryColor: '#0d1f38', primaryTextColor: '#faf6ec',
  primaryBorderColor: '#c9a843', lineColor: '#c9a843',
  secondaryColor: '#1a3a6a', tertiaryColor: '#2a4a80',
  actorBkg: '#0d1f38', actorTextColor: '#faf6ec',
  actorBorder: '#c9a843', actorLineColor: '#c9a843',
  activationBkgColor: '#2a4ab0', activationBorderColor: '#c9a843',
  signalColor: '#c9a843', signalTextColor: '#2a1a0a',
  labelBoxBkgColor: '#0d1f38', labelBoxBorderColor: '#c9a843', labelTextColor: '#faf6ec',
  loopTextColor: '#2a1a0a',
  edgeLabelBackground: '#f0ead8',
  noteBkgColor: '#f0e8d4', noteTextColor: '#2a1a0a', noteBorderColor: '#c9a843',
  titleColor: '#2a1a0a',
  clusterBkg: '#1a3a6a', clusterBorder: '#c9a843', clusterTextColor: '#faf6ec',
  fillType0: '#0d1f38', fillType1: '#1a3a6a', fillType2: '#2a4a80',
  fillType3: '#1a3a6a', fillType4: '#0d1f38', fillType5: '#2a4a80',
  fillType6: '#1a3a6a', fillType7: '#0d1f38'
}} }});</script>
</head>
<body>
<header id="site-header">
  <a href="index.html">18OE</a> &mdash; Developer Documentation
</header>
<div id="layout">
{sidebar}
<main>
<article>
{content}
</article>
</main>
</div>
<script src="search.js"></script>
<script src="ui.js"></script>
</body>
</html>
"""


def extract_title(html):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return "18xx.games"


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """\
/* ============================================================
   Orient Express — Documentation Theme
   Midnight navy · Brass gold · Ivory · Art Deco
   ============================================================ */

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  font-family: 'EB Garamond', Georgia, 'Times New Roman', serif;
  font-size: 17px;
  line-height: 1.78;
  background: #0a1628;
  color: #1a0f08;
}

/* --- Header — double gold rule --- */
#site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #060e1c;
  color: #c9a843;
  padding: 0.55rem 1.5rem;
  font-family: 'Cinzel', 'Playfair Display', Georgia, serif;
  font-size: 0.82rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  border-bottom: 1px solid #c9a843;
  box-shadow: 0 3px 0 rgba(201,168,67,0.28);
}
#site-header a { color: #c9a843; text-decoration: none; }
#site-header a:hover { color: #e0c060; }

/* --- Layout --- */
#layout { display: flex; min-height: calc(100vh - 44px); }

/* --- Sidebar — dark sleeping-car panelling --- */
#sidebar {
  width: 272px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #0d1f38 0%, #091828 100%);
  border-right: 1px solid rgba(201,168,67,0.45);
  padding: 0.75rem 0 1.5rem;
  overflow-y: auto;
  position: sticky;
  top: 44px;
  height: calc(100vh - 44px);
}
#sidebar .track { margin-bottom: 1.25rem; }
#sidebar h3 {
  font-family: 'Cinzel', 'Playfair Display', Georgia, serif;
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.24em;
  color: #c9a843;
  margin: 1rem 1rem 0.4rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid rgba(201,168,67,0.22);
}
#sidebar ul { list-style: none; margin: 0; padding: 0; }
#sidebar li a {
  display: block;
  padding: 0.3rem 1rem;
  text-decoration: none;
  color: #9a8868;
  font-size: 0.875rem;
  font-family: 'EB Garamond', Georgia, serif;
  transition: background 0.15s, color 0.15s;
}
#sidebar li a:hover { background: rgba(201,168,67,0.09); color: #d4b860; }
#sidebar li a[aria-current="page"] {
  background: rgba(201,168,67,0.14);
  color: #c9a843;
  font-weight: 600;
  border-left: 2px solid #c9a843;
  padding-left: calc(1rem - 2px);
}

/* --- Search --- */
#nav-search {
  display: block;
  width: calc(100% - 2rem);
  margin: 0.7rem 1rem 0.9rem;
  padding: 0.35rem 0.65rem;
  border: 1px solid rgba(201,168,67,0.3);
  border-radius: 1px;
  font-size: 0.85rem;
  font-family: 'EB Garamond', Georgia, serif;
  background: rgba(255,255,255,0.04);
  color: #c8b48a;
}
#nav-search::placeholder { color: rgba(200,180,138,0.38); }
#nav-search:focus { outline: 1px solid #c9a843; border-color: #c9a843; background: rgba(255,255,255,0.07); }
#search-results ul { list-style: none; margin: 0; padding: 0; }
#search-no-results { padding: 0.4rem 1rem; color: #6a5a3a; font-size: 0.85rem; margin: 0; }
.search-result a { display: block; padding: 0.5rem 1rem; text-decoration: none; border-bottom: 1px solid rgba(201,168,67,0.1); }
.search-result a:hover, .result-focused a { background: rgba(201,168,67,0.1); }
.result-focused a { outline: 1px solid #c9a843; outline-offset: -1px; }
.result-title { display: block; font-weight: 600; font-size: 0.88rem; color: #d4b860; font-family: 'Playfair Display', Georgia, serif; }
.result-heading { display: block; font-size: 0.75rem; color: #c9a843; margin-top: 0.1rem; }
.result-excerpt { display: block; font-size: 0.78rem; color: #7a6a4a; margin-top: 0.15rem; line-height: 1.4; }
mark { background: rgba(201,168,67,0.3); color: inherit; padding: 0 2px; border-radius: 1px; font-style: normal; }

/* --- Main — cartographic map grid --- */
main {
  flex: 1;
  padding: 2.5rem 3rem;
  background: #e4d8c0;
  background-image:
    linear-gradient(rgba(140,110,60,0.14) 1px, transparent 1px),
    linear-gradient(90deg, rgba(140,110,60,0.14) 1px, transparent 1px);
  background-size: 32px 32px;
}

/* --- Article — ivory card with Art Deco corner brackets --- */
article {
  max-width: 820px;
  margin: 0 auto;
  padding: 2.75rem 3rem;
  background:
    linear-gradient(to right,  #c9a843 28px, transparent 28px) top    left  / 46px 2px  no-repeat,
    linear-gradient(to bottom, #c9a843 28px, transparent 28px) top    left  / 2px  46px no-repeat,
    linear-gradient(to left,   #c9a843 28px, transparent 28px) top    right / 46px 2px  no-repeat,
    linear-gradient(to bottom, #c9a843 28px, transparent 28px) top    right / 2px  46px no-repeat,
    linear-gradient(to right,  #c9a843 28px, transparent 28px) bottom left  / 46px 2px  no-repeat,
    linear-gradient(to top,    #c9a843 28px, transparent 28px) bottom left  / 2px  46px no-repeat,
    linear-gradient(to left,   #c9a843 28px, transparent 28px) bottom right / 46px 2px  no-repeat,
    linear-gradient(to top,    #c9a843 28px, transparent 28px) bottom right / 2px  46px no-repeat,
    #faf6ec;
  box-shadow: 0 8px 40px rgba(6,14,28,0.32);
}

/* --- Headings --- */
h1, h2, h3, h4 { font-family: 'Playfair Display', Georgia, serif; color: #0d1f38; line-height: 1.3; }

h1 {
  font-size: 2.1rem;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 1.5rem;
  letter-spacing: 0.01em;
}
h1::after {
  content: '';
  display: block;
  margin-top: 0.5rem;
  height: 2px;
  background: linear-gradient(to right, #c9a843 0%, #c9a843 42%, transparent 100%);
}

h2 {
  font-size: 1.45rem;
  margin-top: 2.25rem;
  margin-bottom: 0.75rem;
}
h2::after {
  content: '';
  display: block;
  margin-top: 0.3rem;
  height: 1px;
  background: linear-gradient(to right, rgba(201,168,67,0.7) 0%, rgba(201,168,67,0.1) 55%, transparent 100%);
}

h3 { font-size: 1.1rem; color: #1a3560; margin-top: 1.75rem; margin-bottom: 0.5rem; }
h4 { font-size: 0.95rem; color: #2a4570; margin-top: 1.25rem; }

p { margin: 0 0 1rem; color: #1a0f08; }

a { color: #7c1c2e; text-decoration: underline; text-decoration-color: rgba(124,28,46,0.3); }
a:hover { color: #a02030; text-decoration-color: rgba(160,32,48,0.6); }

/* --- HR — gold rule with hexagon ornament (18xx tile nod) --- */
hr {
  border: none;
  height: 18px;
  margin: 2rem 0;
  position: relative;
  text-align: center;
}
hr::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0; right: 0;
  height: 1px;
  background: linear-gradient(to right, transparent 0%, #c9a843 12%, #c9a843 88%, transparent 100%);
}
hr::after {
  content: '\\2B21';
  position: relative;
  z-index: 1;
  background: #faf6ec;
  padding: 0 0.75rem;
  color: #c9a843;
  font-size: 0.72rem;
  line-height: 18px;
}

/* --- Code --- */
pre, code { font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace; }
pre {
  background: #060e1c;
  color: #e0d0a0;
  border-left: 2px solid #c9a843;
  border-radius: 0 2px 2px 0;
  padding: 1rem 1.2rem;
  overflow-x: auto;
  font-size: 0.84rem;
  line-height: 1.6;
  margin: 1.25rem 0;
}
code {
  background: rgba(10,22,40,0.08);
  color: #0d1f38;
  padding: 0.1em 0.35em;
  border-radius: 2px;
  font-size: 0.86em;
}
pre code { background: none; padding: 0; color: inherit; font-size: inherit; }

/* --- Tables --- */
table { border-collapse: collapse; width: 100%; margin: 1.25rem 0; font-size: 0.9rem; }
th {
  background: #0d1f38;
  color: #c9a843;
  text-align: left;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 600;
  letter-spacing: 0.05em;
  font-size: 0.87rem;
}
th, td { padding: 0.45rem 0.85rem; border: 1px solid rgba(201,168,67,0.28); }
td { color: #1a0f08; }
tr:nth-child(even) td { background: rgba(201,168,67,0.04); }
tr:hover td { background: rgba(201,168,67,0.09); }

/* --- Images --- */
img {
  max-width: 100%;
  border: 1px solid rgba(201,168,67,0.45);
  border-radius: 1px;
  box-shadow: 2px 4px 12px rgba(6,14,28,0.24);
  display: block;
  margin: 0.75rem 0;
}

/* --- Blockquote --- */
blockquote {
  border-left: 2px solid #c9a843;
  margin: 1.25rem 0;
  padding: 0.5rem 1rem;
  background: rgba(201,168,67,0.06);
  color: #4a3a22;
  font-style: italic;
}

/* --- Lists --- */
ul, ol { padding-left: 1.5rem; margin: 0.5rem 0 1rem; }
li { margin-bottom: 0.25rem; }

/* --- Mermaid --- */
.mermaid { margin: 1.5rem 0; }

/* --- Confidence markers --- */
.confidence-low { color: #8a7a5a; }
.confidence-low code { color: #7a6a4a; }

/* --- Responsive --- */
@media (max-width: 960px) {
  #layout { flex-direction: column; }
  #sidebar { width: 100%; height: auto; position: static; border-right: none; border-bottom: 1px solid rgba(201,168,67,0.45); }
  main { padding: 1.25rem; }
  article { padding: 1.5rem 1.25rem; background: #faf6ec; }
}

/* --- Copy buttons --- */
.pre-wrap { position: relative; }
.copy-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: rgba(201,168,67,0.1);
  color: #c9a843;
  border: 1px solid rgba(201,168,67,0.28);
  border-radius: 2px;
  padding: 0.18rem 0.55rem;
  font-size: 0.7rem;
  font-family: 'EB Garamond', Georgia, serif;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  line-height: 1.6;
}
.copy-btn:hover { background: rgba(201,168,67,0.22); color: #e0c060; border-color: rgba(201,168,67,0.5); }
.copy-btn.copied { background: rgba(60,140,60,0.2); color: #7ec87e; border-color: rgba(80,160,80,0.35); }

/* --- Anchor links --- */
.anchor-link {
  margin-left: 0.45rem;
  color: transparent;
  text-decoration: none;
  font-size: 0.72em;
  font-weight: 400;
  font-family: 'EB Garamond', Georgia, serif;
  vertical-align: middle;
  cursor: pointer;
  transition: color 0.15s;
  user-select: none;
}
h2:hover .anchor-link, h3:hover .anchor-link, h4:hover .anchor-link { color: rgba(201,168,67,0.55); }
.anchor-link:hover { color: #c9a843 !important; text-decoration: none; }
.anchor-link.anchor-copied { color: #7ec87e !important; }

/* --- Floating TOC --- */
#toc {
  position: fixed;
  right: 0.75rem;
  top: 52px;
  width: 188px;
  max-height: calc(100vh - 68px);
  overflow-y: auto;
  background: #0d1f38;
  border: 1px solid rgba(201,168,67,0.28);
  border-radius: 2px;
  padding: 0.6rem 0 0.75rem;
  z-index: 50;
  display: none;
}
#toc::-webkit-scrollbar { width: 4px; }
#toc::-webkit-scrollbar-track { background: transparent; }
#toc::-webkit-scrollbar-thumb { background: rgba(201,168,67,0.25); border-radius: 2px; }
.toc-header {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.58rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: #c9a843;
  padding: 0 0.75rem 0.45rem;
  border-bottom: 1px solid rgba(201,168,67,0.18);
  margin-bottom: 0.35rem;
}
#toc ul { list-style: none; margin: 0; padding: 0; }
#toc li a {
  display: block;
  padding: 0.22rem 0.75rem;
  color: #8a7858;
  text-decoration: none;
  font-size: 0.78rem;
  line-height: 1.4;
  font-family: 'EB Garamond', Georgia, serif;
  transition: color 0.15s, background 0.15s;
}
#toc li.toc-h3 a { padding-left: 1.2rem; color: #6a5840; font-size: 0.74rem; }
#toc li a:hover { color: #d4b860; background: rgba(201,168,67,0.07); }
#toc li a.toc-active { color: #c9a843; border-left: 2px solid #c9a843; padding-left: calc(0.75rem - 2px); }
#toc li.toc-h3 a.toc-active { padding-left: calc(1.2rem - 2px); }

#toc-toggle {
  position: fixed;
  right: 0.75rem;
  top: 52px;
  background: #0d1f38;
  color: #c9a843;
  border: 1px solid rgba(201,168,67,0.28);
  border-radius: 2px;
  width: 30px;
  height: 30px;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
  z-index: 51;
  display: none;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
#toc-toggle:hover { background: rgba(201,168,67,0.14); }

@media (min-width: 1320px) {
  #toc { display: block; }
  #toc-toggle { display: none !important; }
}
@media (min-width: 769px) and (max-width: 1319px) {
  #toc-toggle { display: flex; }
  #toc.toc-visible { display: block; }
}

/* --- Status Board (status.html) --- */
article:has(.status-board) { max-width: 1400px; }

/* progress bar */
/* dual progress bars */
.bar-rows { margin: 0 0 1.1rem; }
.bar-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.35rem;
}
.bar-label-left {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.6rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #8a7a62;
  min-width: 3.6rem;
  text-align: right;
  flex-shrink: 0;
}
.bar-label-right {
  font-size: 0.72rem;
  color: #6a5c48;
  white-space: nowrap;
  flex-shrink: 0;
}
.bar-aside { color: #9a8a72; }
.bar-beta  { color: #7a6850; font-style: italic; }
.bar-row .progress-track { flex: 1; margin: 0; }

.progress-track {
  height: 5px;
  border-radius: 3px;
  overflow: hidden;
  margin: 0 0 1.1rem;
  display: flex;
  background: rgba(13,31,56,0.08);
}
.bar-note {
  font-size: 0.78rem; color: rgba(90,74,56,0.7); margin: -0.4rem 0 0.9rem;
  font-style: italic;
}
.pb-done     { background: #2d7a2d; }
.pb-pr       { background: #2a4ab0; }
.pb-partial  { background: #b87800; }
.pb-todo     { background: rgba(13,31,56,0.12); }
.pb-deferred { background: rgba(120,100,70,0.18); }

.page-crosslink {
  font-size: 0.82rem;
  color: #7a6a52;
  margin: -0.5rem 0 1.5rem;
}

/* summary chips */
.status-summary {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin: 0 0 1rem;
}
.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.28rem 0.85rem 0.28rem 0.65rem;
  border-radius: 2px;
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.65rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.stat-chip span { font-family: 'Playfair Display', Georgia, serif; font-size: 1.1rem; font-weight: 700; line-height: 1; }
.stat-chip::before {
  content: '';
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.stat-done    { background: rgba(45,122,45,0.1);  color: #2d7a2d; border: 1px solid rgba(45,122,45,0.25); }
.stat-done::before    { background: #2d7a2d; }
.stat-pr      { background: rgba(42,74,176,0.1);  color: #2a4ab0; border: 1px solid rgba(42,74,176,0.25); }
.stat-pr::before      { background: #2a4ab0; }
.stat-partial { background: rgba(184,120,0,0.1);  color: #8a5800; border: 1px solid rgba(184,120,0,0.25); }
.stat-partial::before { background: #b87800; }
.stat-todo    { background: rgba(100,80,60,0.07); color: #5a4a38; border: 1px solid rgba(120,100,70,0.18); }
.stat-todo::before    { background: rgba(13,31,56,0.22); border: 1px solid rgba(13,31,56,0.15); }
.stat-beta    { background: rgba(100,80,50,0.07); color: #7a6040; border: 1px dashed rgba(120,90,50,0.3); font-style: italic; }
.stat-beta::before    { background: repeating-linear-gradient(45deg,rgba(100,80,50,0.4) 0px,rgba(100,80,50,0.4) 2px,transparent 2px,transparent 4px); }

/* milestone filter buttons */
.milestone-btn {
  padding: 0.2rem 0.7rem;
  border: 1px solid rgba(120,100,70,0.35);
  border-radius: 2px;
  background: transparent;
  color: #5a4a38;
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.62rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.milestone-btn:hover { background: rgba(201,168,67,0.12); color: #0d1f38; }
.milestone-btn.active { background: #0d1f38; color: #c9a843; border-color: rgba(201,168,67,0.7); }

/* scope dimming for alpha/beta filter */
.scope-dimmed {
  opacity: 0.18;
  filter: grayscale(1);
  pointer-events: none;
  transition: opacity 0.2s, filter 0.2s;
}
.cov-item, .sb-item { transition: opacity 0.2s, filter 0.2s; }

/* filters */
.status-filters { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.filter-label {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #4a3a22;
}
.layer-btn {
  padding: 0.22rem 0.7rem;
  border: 1px solid rgba(201,168,67,0.35);
  border-radius: 2px;
  background: transparent;
  color: #6a5638;
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.layer-btn:hover { background: rgba(201,168,67,0.12); color: #0d1f38; }
.layer-btn.active { background: #0d1f38; color: #c9a843; border-color: rgba(201,168,67,0.7); }

.filter-sep { width: 1px; height: 1.1rem; background: rgba(201,168,67,0.22); margin: 0 0.2rem; align-self: center; flex-shrink: 0; }
.group-btn {
  padding: 0.22rem 0.7rem;
  border: 1px solid rgba(201,168,67,0.35);
  border-radius: 2px;
  background: transparent;
  color: #6a5638;
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.group-btn:hover { background: rgba(201,168,67,0.12); color: #0d1f38; }
.group-btn.active { background: #1a3a24; color: #7ec87e; border-color: rgba(80,160,80,0.4); }

/* board */
.status-board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; align-items: start; }

.sb-col {
  border: 1px solid rgba(201,168,67,0.22);
  border-radius: 2px;
  overflow: hidden;
  min-width: 0;
  display: flex;
  flex-direction: column;
  max-height: 74vh;
}
.sb-col-body {
  overflow-y: auto;
  flex: 1;
}
.sb-col-body::-webkit-scrollbar { width: 4px; }
.sb-col-body::-webkit-scrollbar-track { background: transparent; }
.sb-col-body::-webkit-scrollbar-thumb { background: rgba(201,168,67,0.2); border-radius: 2px; }

.sb-col-header {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: #faf6ec;
  padding: 0.65rem 1rem;
  border-bottom: 1px solid rgba(201,168,67,0.25);
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sb-col-count {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 0.92rem;
  font-weight: 700;
  letter-spacing: 0;
  opacity: 0.75;
}
.done-col   { background: #1a3a1a; }
.inwork-col { background: #0d2040; }
.todo-col   { background: #2a1e0e; }

/* sections */
.sb-section { border-bottom: 1px solid rgba(201,168,67,0.1); padding: 0.5rem 0 0.3rem; }
.sb-section:last-child { border-bottom: none; }
.sb-section-title {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.57rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #8a7050;
  padding: 0 0.85rem 0.3rem;
}

/* done cards */
.sb-done-card { padding: 0.6rem 0.85rem; border-bottom: 1px solid rgba(201,168,67,0.08); }
.sb-done-card:last-child { border-bottom: none; }
.sb-done-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 0.82rem;
  font-weight: 600;
  color: #1a3a1a;
  margin-bottom: 0.15rem;
}
.sb-done-summary {
  font-size: 0.73rem;
  color: #4a5840;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* items */
.sb-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.3rem 0.85rem;
  font-size: 0.8rem;
  line-height: 1.42;
  transition: background 0.1s;
}
.sb-item:hover { background: rgba(201,168,67,0.07); }
.sb-item[data-hidden] { display: none; }

.sb-status-dot {
  flex-shrink: 0;
  width: 7px; height: 7px;
  border-radius: 50%;
  margin-top: 0.42em;
}
.sb-needs-pr .sb-status-dot { background: #2a4ab0; box-shadow: 0 0 0 2px rgba(42,74,176,0.15); }
.sb-partial   .sb-status-dot { background: #b87800; box-shadow: 0 0 0 2px rgba(184,120,0,0.15); }
.sb-started   .sb-status-dot { background: #7a5200; box-shadow: 0 0 0 2px rgba(122,82,0,0.12); }
.sb-todo      .sb-status-dot { background: transparent; border: 1.5px solid rgba(13,31,56,0.28); }

.sb-item-text { flex: 1; min-width: 0; color: #1a0f08; }
.layer-tag {
  flex-shrink: 0;
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.56rem;
  letter-spacing: 0.07em;
  padding: 0.1rem 0.35rem;
  border-radius: 2px;
  background: rgba(13,31,56,0.06);
  color: #5a4a32;
  border: 1px solid rgba(201,168,67,0.16);
  white-space: nowrap;
  margin-top: 0.15em;
}
.started-badge {
  flex-shrink: 0;
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.5rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 0.1rem 0.4rem;
  border-radius: 2px;
  background: rgba(122,82,0,0.12);
  color: #7a5200;
  border: 1px solid rgba(122,82,0,0.25);
  white-space: nowrap;
  margin-top: 0.15em;
}

.sb-section:not(:has(.sb-item:not([data-hidden]))) { display: none; }

@media (max-width: 1100px) {
  article:has(.status-board) { max-width: 820px; }
  .status-board { grid-template-columns: 1fr; }
  .sb-col { max-height: none; }
}

/* --- Rulebook Coverage Heatmap --- */
article:has(.coverage-map) { max-width: 1200px; }

.coverage-summary {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
  margin: 0 0 1.5rem;
}

.coverage-map {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cov-chapter { }
.cov-chapter-title {
  font-family: 'Cinzel', Georgia, serif;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #0d1f38;
  margin: 0 0 0.45rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid rgba(201,168,67,0.3);
}

.cov-items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.cov-item {
  padding: 0.22rem 0.6rem;
  border-radius: 2px;
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 0.75rem;
  line-height: 1.5;
  white-space: nowrap;
  cursor: default;
}

.cov-done     { background: #2d7a2d; color: #dff0df; }
.cov-needs-pr { background: #2a4ab0; color: #dde5f8; }
.cov-partial  { background: #b87800; color: #fff3d8; }
.cov-todo     { background: rgba(13,31,56,0.07); color: #5a4a38; border: 1px solid rgba(201,168,67,0.2); }
.cov-deferred {
  background: repeating-linear-gradient(
    45deg,
    rgba(100,80,60,0.08) 0px, rgba(100,80,60,0.08) 3px,
    transparent 3px, transparent 6px
  );
  color: #8a7a62;
  border: 1px solid rgba(120,100,70,0.2);
}

.cov-legend {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  padding: 0.75rem 1rem;
  background: rgba(13,31,56,0.04);
  border: 1px solid rgba(201,168,67,0.15);
  border-radius: 2px;
}
.cov-legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 0.8rem;
  color: #4a3a22;
}
.cov-legend-swatch {
  width: 14px; height: 14px;
  border-radius: 2px;
  flex-shrink: 0;
}

/* ── Alpha Gaps page ─────────────────────────────────────────────────── */
.gap-stats {
  display: flex; flex-wrap: wrap; gap: 0.6rem;
  margin: 1.4rem 0 2rem;
}
.gap-stat {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.45rem 1rem; border-radius: 4px;
  font-size: 0.82rem; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase; color: #faf6ec;
}
.gap-stat span {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.2rem; font-weight: 700;
}
.gap-stat-high    { background: #7a1a1a; border: 1px solid #c03030; }
.gap-stat-med     { background: #5a3a00; border: 1px solid #c9a843; }
.gap-stat-low     { background: #1a3a1a; border: 1px solid #3a7a3a; }
.gap-stat-feat    { background: #0d1f38; border: 1px solid #2a4ab0; }
.gap-stat-partial { background: #2a1f00; border: 1px solid #b87800; }

.gap-section-h {
  margin: 2.2rem 0 0.7rem;
  font-size: 1rem; letter-spacing: 0.06em; text-transform: uppercase;
  color: #c9a843; border-bottom: 1px solid rgba(201,168,67,0.25);
  padding-bottom: 0.3rem;
}

.gap-table {
  width: 100%; border-collapse: collapse;
  font-size: 0.875rem; margin-bottom: 1rem;
}
.gap-table thead th {
  text-align: left; padding: 0.4rem 0.7rem;
  background: rgba(13,31,56,0.7);
  color: #c9a843; font-size: 0.75rem;
  letter-spacing: 0.08em; text-transform: uppercase;
  border-bottom: 1px solid rgba(201,168,67,0.3);
}
.gap-table td { padding: 0.35rem 0.7rem; vertical-align: top; }
.gap-table tr + tr td { border-top: 1px solid rgba(201,168,67,0.07); }

.gap-section-row td.gap-section-label {
  background: rgba(13,31,56,0.5);
  color: #c9a843; font-size: 0.78rem;
  letter-spacing: 0.06em; text-transform: uppercase;
  padding: 0.3rem 0.7rem; font-weight: 600;
  border-top: 1px solid rgba(201,168,67,0.15) !important;
}

.gap-id    { font-family: monospace; font-size: 0.8rem; white-space: nowrap; width: 6.5rem; color: #8ab4d8; }
.gap-title { font-weight: 600; width: 35%; }
.gap-sym   { color: rgba(26,15,8,0.72); font-size: 0.83rem; }
.gap-feat  { padding-left: 1.2rem; }
.gap-area  { width: 0.5rem; }

.gap-row-high   { background: rgba(122,26,26,0.08); }
.gap-row-high:hover { background: rgba(122,26,26,0.15); }
.gap-row-med    { background: rgba(90,58,0,0.06); }
.gap-row-med:hover { background: rgba(90,58,0,0.12); }
.gap-row-low    { }
.gap-row-feat   { }
.gap-row-partial { background: rgba(42,31,0,0.06); }

.gap-none { color: #2d7a2d; font-style: italic; margin: 0.3rem 0 1rem; }

/* ---- Map Status Table ---- */
.map-status-table { width: 100%; border-collapse: collapse; margin: 0.8rem 0 1.4rem; }
.map-status-table thead th {
  background: rgba(13,31,56,0.55); color: #c9a843;
  font-family: 'Cinzel', serif; font-size: 0.68rem; letter-spacing: 0.12em;
  text-transform: uppercase; padding: 0.45rem 0.7rem; text-align: left;
}
.map-status-table td { padding: 0.35rem 0.7rem; vertical-align: top; }
.map-status-table tr + tr td { border-top: 1px solid rgba(201,168,67,0.07); }
.ms-area  { font-weight: 500; white-space: nowrap; width: 22%; }
.ms-status { width: 2.5rem; text-align: center; }
.ms-sym { display: inline-block; width: 1.4rem; text-align: center;
  font-weight: 700; font-size: 1rem; border-radius: 2px; }
.ms-sym-done    { color: #2d7a2d; }
.ms-sym-needs-pr{ color: #2a4ab0; }
.ms-sym-partial { color: #b87800; }
.ms-sym-todo    { color: rgba(13,31,56,0.35); }
.ms-row-done    { background: rgba(45,122,45,0.04); }
.ms-row-partial { background: rgba(184,120,0,0.05); }
.ms-row-todo    { }
.ms-row-needs-pr{ background: rgba(42,74,176,0.05); }
.ms-desc code   { font-size: 0.82em; }
"""

# ---------------------------------------------------------------------------
# Search JS (written to search.js in OUT_DIR)
# ---------------------------------------------------------------------------

SEARCH_JS = """\
(function () {
  'use strict';

  var input  = document.getElementById('nav-search');
  if (!input) return;

  var panel  = document.getElementById('search-results');
  var list   = document.getElementById('search-results-list');
  var noRes  = document.getElementById('search-no-results');
  var tracks = document.querySelectorAll('#sidebar .track');

  var index      = null;
  var pending    = null;
  var focusIndex = -1;

  // ---- index loading (lazy, once) ----

  function loadIndex() {
    if (index)   return Promise.resolve();
    if (pending) return pending;
    pending = fetch('search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; pending = null; });
    return pending;
  }

  // ---- utilities ----

  function escapeRe(s) {
    return s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  }

  function highlight(text, words) {
    if (!words.length) return text;
    var re = new RegExp('(' + words.map(escapeRe).join('|') + ')', 'gi');
    return text.replace(re, '<mark>$1</mark>');
  }

  function excerpt(body, words) {
    var idx = -1;
    for (var i = 0; i < words.length; i++) {
      var p = body.toLowerCase().indexOf(words[i].toLowerCase());
      if (p !== -1) { idx = p; break; }
    }
    var start = Math.max(0, idx === -1 ? 0 : idx - 60);
    var end   = Math.min(body.length, start + 160);
    return (start > 0 ? '\\u2026' : '') +
           highlight(body.slice(start, end), words) +
           (end < body.length ? '\\u2026' : '');
  }

  function scoreItem(item, words) {
    var s  = 0;
    var tl = item.title.toLowerCase();
    var hl = item.headings.map(function (h) { return h.text; }).join(' ').toLowerCase();
    var bl = item.body.toLowerCase();
    words.forEach(function (w) {
      var wl = w.toLowerCase();
      if (tl.includes(wl)) s += 10;
      if (hl.includes(wl)) s +=  5;
      if (bl.includes(wl)) s +=  1;
    });
    return s;
  }

  // ---- keyboard focus ----

  function setFocus(idx) {
    var items = list.querySelectorAll('.search-result');
    if (focusIndex >= 0 && focusIndex < items.length)
      items[focusIndex].classList.remove('result-focused');
    focusIndex = Math.max(0, Math.min(idx, items.length - 1));
    if (items.length) {
      items[focusIndex].classList.add('result-focused');
      items[focusIndex].scrollIntoView({ block: 'nearest' });
    }
  }

  input.addEventListener('keydown', function (e) {
    var items = list.querySelectorAll('.search-result');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setFocus(focusIndex < 0 ? 0 : focusIndex + 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setFocus(focusIndex <= 0 ? 0 : focusIndex - 1);
    } else if (e.key === 'Enter' && focusIndex >= 0) {
      e.preventDefault();
      var link = items[focusIndex].querySelector('a');
      if (link) window.location.href = link.href;
    } else if (e.key === 'Escape') {
      input.value = '';
      showPanel(false);
    }
  });

  // ---- render ----

  function showPanel(show) {
    panel.style.display = show ? '' : 'none';
    tracks.forEach(function (t) { t.style.display = show ? 'none' : ''; });
    if (!show) focusIndex = -1;
  }

  function renderResults(results, words) {
    list.innerHTML = '';
    focusIndex = -1;
    if (!results.length) { noRes.style.display = ''; return; }
    noRes.style.display = 'none';
    results.forEach(function (item) {
      var matchHeading = null;
      item.headings.forEach(function (h) {
        if (!matchHeading &&
            words.some(function (w) { return h.text.toLowerCase().includes(w.toLowerCase()); })) {
          matchHeading = h;
        }
      });
      var href = matchHeading ? item.url + '#' + matchHeading.id : item.url;
      var li   = document.createElement('li');
      li.className = 'search-result';
      li.innerHTML =
        '<a href="' + href + '">' +
        '<span class="result-title">'   + highlight(item.title, words) + '</span>' +
        (matchHeading
          ? '<span class="result-heading">\\u00a7\\u00a0' + highlight(matchHeading.text, words) + '</span>'
          : '') +
        '<span class="result-excerpt">' + excerpt(item.body, words) + '</span>' +
        '</a>';
      list.appendChild(li);
    });
  }

  // ---- input event ----

  input.addEventListener('input', function () {
    var q = input.value.trim();
    if (!q) { showPanel(false); return; }
    var words = q.split(/\\s+/).filter(Boolean);
    loadIndex().then(function () {
      var results = index
        .map(function (item) { return { item: item, s: scoreItem(item, words) }; })
        .filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 12)
        .map(function (r) { return r.item; });
      renderResults(results, words);
      showPanel(true);
    });
  });
}());
"""


UI_JS = """\
(function () {
  'use strict';

  /* ---- helpers ---- */

  function headingText(h) {
    // text nodes only — excludes injected anchor-link elements
    return Array.from(h.childNodes)
      .filter(function (n) { return n.nodeType === 3; })
      .map(function (n) { return n.textContent; })
      .join('').trim();
  }

  function flashClass(el, cls, ms) {
    el.classList.add(cls);
    setTimeout(function () { el.classList.remove(cls); }, ms || 1500);
  }

  function copyText(text, onDone) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(onDone).catch(function () {});
    } else {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); onDone(); } catch (e) {}
      document.body.removeChild(ta);
    }
  }

  /* ---- 1. Copy buttons ---- */

  function initCopyButtons() {
    document.querySelectorAll('pre').forEach(function (pre) {
      var wrap = document.createElement('div');
      wrap.className = 'pre-wrap';
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(pre);

      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.setAttribute('aria-label', 'Copy code');
      btn.textContent = 'Copy';
      wrap.appendChild(btn);

      btn.addEventListener('click', function () {
        var code = pre.querySelector('code');
        copyText((code || pre).textContent, function () {
          btn.textContent = 'Copied!';
          flashClass(btn, 'copied', 2000);
          setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
        });
      });
    });
  }

  /* ---- 2. Heading anchor links ---- */

  function initAnchorLinks() {
    var article = document.querySelector('article');
    if (!article) return;
    article.querySelectorAll('h2[id], h3[id], h4[id]').forEach(function (h) {
      var a = document.createElement('a');
      a.className = 'anchor-link';
      a.href = '#' + h.id;
      a.setAttribute('aria-label', 'Link to this section');
      a.textContent = '\\u00a7';
      h.appendChild(a);
      a.addEventListener('click', function (e) {
        e.preventDefault();
        history.pushState(null, '', '#' + h.id);
        copyText(location.href, function () { flashClass(a, 'anchor-copied'); });
      });
    });
  }

  /* ---- 3. Floating TOC ---- */

  function initTOC() {
    var article = document.querySelector('article');
    if (!article) return;
    var headings = Array.from(article.querySelectorAll('h2[id], h3[id]'));
    if (headings.length < 3) return;

    /* build panel */
    var nav = document.createElement('nav');
    nav.id = 'toc';
    nav.setAttribute('aria-label', 'Page contents');

    var hdr = document.createElement('div');
    hdr.className = 'toc-header';
    hdr.textContent = 'Contents';
    nav.appendChild(hdr);

    var ul = document.createElement('ul');
    headings.forEach(function (h) {
      var li = document.createElement('li');
      li.className = h.tagName === 'H3' ? 'toc-h3' : 'toc-h2';
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = headingText(h);
      a.dataset.id = h.id;
      li.appendChild(a);
      ul.appendChild(li);
    });
    nav.appendChild(ul);

    /* toggle button for medium viewports */
    var btn = document.createElement('button');
    btn.id = 'toc-toggle';
    btn.setAttribute('aria-label', 'Table of contents');
    btn.textContent = '\\u2630';
    document.body.appendChild(btn);
    document.body.appendChild(nav);

    btn.addEventListener('click', function () { nav.classList.toggle('toc-visible'); });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') nav.classList.remove('toc-visible');
    });

    /* scroll spy */
    var active = null;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          if (active) active.classList.remove('toc-active');
          active = ul.querySelector('a[data-id="' + entry.target.id + '"]');
          if (active) active.classList.add('toc-active');
        }
      });
    }, { rootMargin: '-10% 0px -80% 0px', threshold: 0 });
    headings.forEach(function (h) { observer.observe(h); });
  }

  /* ---- 4. Status board: layer filter + group-by toggle ---- */

  /* shared milestone filter — works on both status board and coverage heatmap */
  function initMilestoneFilter() {
    var milestoneBtns = document.querySelectorAll('.milestone-btn');
    if (!milestoneBtns.length) return;

    milestoneBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        milestoneBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var scope = btn.dataset.scope || '';

        /* coverage heatmap cells */
        document.querySelectorAll('.cov-item[data-scope]').forEach(function (el) {
          el.classList.toggle('scope-dimmed', !!(scope && el.dataset.scope !== scope));
        });
        /* chapter headers: dim entirely-beta chapters when alpha selected */
        document.querySelectorAll('.cov-chapter[data-chapter-scope]').forEach(function (el) {
          var allBeta = el.dataset.chapterScope === 'beta';
          el.classList.toggle('scope-dimmed', !!(scope === 'alpha' && allBeta));
        });

        /* status board items */
        document.querySelectorAll('.sb-item[data-scope]').forEach(function (el) {
          el.classList.toggle('scope-dimmed', !!(scope && el.dataset.scope !== scope));
        });
      });
    });
  }

  function initStatusBoard() {
    var board = document.querySelector('.status-board');
    if (!board) return;

    /* layer filter */
    var layerBtns = document.querySelectorAll('.layer-btn');
    layerBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        layerBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var filter = btn.dataset.layer || '';
        board.querySelectorAll('.sb-item').forEach(function (item) {
          var layer = item.dataset.layer || '';
          if (!filter || layer.indexOf(filter) !== -1) {
            item.removeAttribute('data-hidden');
          } else {
            item.setAttribute('data-hidden', '');
          }
        });
      });
    });

    /* group-by toggle */
    var groupBtns = document.querySelectorAll('.group-btn');
    var viewBodies = board.querySelectorAll('.view-rules, .view-layer');
    groupBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        groupBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        var group = btn.dataset.group;
        viewBodies.forEach(function (body) {
          body.style.display = body.classList.contains('view-' + group) ? '' : 'none';
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTOC();           // before anchor links so headingText() reads clean nodes
    initAnchorLinks();
    initCopyButtons();
    initMilestoneFilter();
    initStatusBoard();
  });
}());
"""


# ---------------------------------------------------------------------------
# Alpha Gaps page
# ---------------------------------------------------------------------------

# Section priority for "what to tackle first" ordering in the gaps page.
# Lower number = higher impact on alpha playability.
_SECTION_PRIORITY = {
    "End Game":                     0,
    "Stock Market Grid":            1,
    "Train Purchase":               2,
    "OR Steps (Major)":             3,
    "Stock Rounds":                 4,
    "Railroad Formation":           90,
    "Nationals":                    91,
    "Minor Mergers":                92,
    "Track Laying":                 8,
    "Track Rights":                 9,
    "Auction Phase":                10,
    "Token Placement":              11,
    "Map & Components":             12,
    "Minor Abilities":              13,
    "Private Abilities":            14,
    "Route & Revenue (Cross-Water)":15,
    "Token Transfer Between Majors":16,
    "Consolidation Phase":          17,
    "Track Rights Chit System":     18,
    "Game Setup":                   99,
}


def parse_bugs_md(path):
    """Parse MD/bugs.md and return list of dicts for OPEN bugs.

    Each dict: { id, title, severity, summary }
    """
    if not path.exists():
        return []
    text = path.read_text(encoding='utf-8')
    bugs = []
    # Match each ### BUG-NNN block
    blocks = re.split(r'\n(?=### BUG-)', text)
    for block in blocks:
        id_m = re.match(r'### (BUG-\d+) — (.+)', block)
        if not id_m:
            continue
        bug_id    = id_m.group(1)
        title     = id_m.group(2).strip()
        status_m  = re.search(r'\*\*Status:\*\*\s*([A-Z]+)', block)
        sev_m     = re.search(r'\*\*Severity:\*\*\s*(HIGH|MEDIUM|LOW)', block)
        sym_m     = re.search(r'\*\*Symptom\.\*\*\s*(.+?)(?=\n\n|\*\*|$)', block, re.DOTALL)
        if not status_m:
            continue
        status = status_m.group(1)
        if status not in ('OPEN', 'INVESTIGATING'):
            continue
        severity = sev_m.group(1) if sev_m else 'MEDIUM'
        # Collapse symptom to one line
        symptom = ''
        if sym_m:
            symptom = re.sub(r'\s+', ' ', sym_m.group(1)).strip()[:160]
        bugs.append({'id': bug_id, 'title': title, 'severity': severity, 'symptom': symptom})
    return bugs


def build_alpha_gaps_html():
    """Generate alpha-gaps.html — prioritised list of what's missing for alpha."""
    bugs_path = MD_DIR / "bugs.md"
    open_bugs = parse_bugs_md(bugs_path)

    # Partition bugs by severity
    high_bugs   = [b for b in open_bugs if b['severity'] == 'HIGH']
    medium_bugs = [b for b in open_bugs if b['severity'] == 'MEDIUM']
    low_bugs    = [b for b in open_bugs if b['severity'] == 'LOW']

    # Collect todo/partial alpha items from COVERAGE_DATA, grouped by section
    alpha_todo    = []   # (section, item_name, status)
    alpha_partial = []
    for section, items in COVERAGE_DATA:
        prio = _SECTION_PRIORITY.get(section, 50)
        for name, status, scope in items:
            if scope != 'alpha':
                continue
            if status == 'todo':
                alpha_todo.append((prio, section, name))
            elif status == 'partial':
                alpha_partial.append((prio, section, name))

    alpha_todo.sort(key=lambda t: (t[0], t[2]))
    alpha_partial.sort(key=lambda t: (t[0], t[2]))

    # Stats
    n_high   = len(high_bugs)
    n_medium = len(medium_bugs)
    n_low    = len(low_bugs)
    n_todo   = len(alpha_todo)
    n_partial= len(alpha_partial)
    total_open = len(open_bugs)

    def sev_cls(sev):
        return {'HIGH': 'sev-high', 'MEDIUM': 'sev-med', 'LOW': 'sev-low'}.get(sev, 'sev-med')

    p = []
    p.append('<h1>18OE — Open for Alpha</h1>')
    p.append('<p class="page-crosslink">Fast triage view · bugs and missing features sorted by impact. '
             'For full rulebook picture → <a href="rulebook-coverage.html">Rulebook Coverage</a> · '
             'For in-flight work → <a href="status.html">Implementation Tracker</a></p>')
    p.append('<p class="bar-note">Bar weights: L3 step/round = 3× · L2 override = 2× · L1 data = 1×</p>')

    # Weighted alpha-scope progress bar (coverage items only, alpha scope)
    wd_a, wpr_a, wpa_a, wto_a, _ = weighted_coverage_stats(scope_filter='alpha')
    w_total_a = wd_a + wpr_a + wpa_a + wto_a or 1.0
    alpha_pct = round((wd_a + wpr_a) / w_total_a * 100)
    p.append(build_shared_bar(
        rows=[{'label': 'Alpha scope', 'done': wd_a, 'pr': wpr_a, 'partial': wpa_a,
               'todo': wto_a, 'total': w_total_a,
               'right': f'<strong>{alpha_pct}%</strong> complete (effort-weighted)'}],
        chips=[],
    ))

    # Stats bar
    p.append('<div class="gap-stats">')
    p.append(f'<div class="gap-stat gap-stat-high">HIGH bugs <span>{n_high}</span></div>')
    p.append(f'<div class="gap-stat gap-stat-med">MEDIUM bugs <span>{n_medium}</span></div>')
    p.append(f'<div class="gap-stat gap-stat-low">LOW bugs <span>{n_low}</span></div>')
    p.append(f'<div class="gap-stat gap-stat-feat">Missing features <span>{n_todo}</span></div>')
    p.append(f'<div class="gap-stat gap-stat-partial">Partial impl. <span>{n_partial}</span></div>')
    p.append('</div>')

    # ── Section 1: HIGH bugs ────────────────────────────────────────────────
    p.append('<h2 class="gap-section-h">Critical Bugs — fix before any playtesting</h2>')
    if high_bugs:
        p.append('<table class="gap-table">')
        p.append('<thead><tr><th>ID</th><th>Rule violated</th><th>Symptom</th></tr></thead><tbody>')
        for b in high_bugs:
            p.append(
                f'<tr class="gap-row-high">'
                f'<td class="gap-id">{_html.escape(b["id"])}</td>'
                f'<td class="gap-title">{_html.escape(b["title"])}</td>'
                f'<td class="gap-sym">{_html.escape(b["symptom"])}</td>'
                f'</tr>'
            )
        p.append('</tbody></table>')
    else:
        p.append('<p class="gap-none">No HIGH bugs open.</p>')

    # ── Section 2: Missing alpha features ───────────────────────────────────
    p.append('<h2 class="gap-section-h">Missing Alpha Features — not yet implemented</h2>')
    if alpha_todo:
        # Group by section for readability
        from itertools import groupby
        p.append('<table class="gap-table">')
        p.append('<thead><tr><th>Area</th><th>Feature</th></tr></thead><tbody>')
        cur_section = None
        for prio, section, name in alpha_todo:
            if section != cur_section:
                cur_section = section
                p.append(
                    f'<tr class="gap-section-row">'
                    f'<td colspan="2" class="gap-section-label">{_html.escape(section)}</td>'
                    f'</tr>'
                )
            p.append(
                f'<tr class="gap-row-feat">'
                f'<td class="gap-area"></td>'
                f'<td class="gap-feat">{_html.escape(name)}</td>'
                f'</tr>'
            )
        p.append('</tbody></table>')
    else:
        p.append('<p class="gap-none">All alpha features implemented.</p>')

    # ── Section 3: Partial implementations ──────────────────────────────────
    p.append('<h2 class="gap-section-h">Partial Implementations — need completion</h2>')
    if alpha_partial:
        p.append('<table class="gap-table">')
        p.append('<thead><tr><th>Area</th><th>Feature</th></tr></thead><tbody>')
        cur_section = None
        for prio, section, name in alpha_partial:
            if section != cur_section:
                cur_section = section
                p.append(
                    f'<tr class="gap-section-row">'
                    f'<td colspan="2" class="gap-section-label">{_html.escape(section)}</td>'
                    f'</tr>'
                )
            p.append(
                f'<tr class="gap-row-partial">'
                f'<td class="gap-area"></td>'
                f'<td class="gap-feat">{_html.escape(name)}</td>'
                f'</tr>'
            )
        p.append('</tbody></table>')
    else:
        p.append('<p class="gap-none">No partial alpha items.</p>')

    # ── Section 4: MEDIUM bugs ───────────────────────────────────────────────
    p.append('<h2 class="gap-section-h">Medium Bugs — rule violations in specific cases</h2>')
    if medium_bugs:
        p.append('<table class="gap-table">')
        p.append('<thead><tr><th>ID</th><th>Rule violated</th><th>Symptom</th></tr></thead><tbody>')
        for b in medium_bugs:
            p.append(
                f'<tr class="gap-row-med">'
                f'<td class="gap-id">{_html.escape(b["id"])}</td>'
                f'<td class="gap-title">{_html.escape(b["title"])}</td>'
                f'<td class="gap-sym">{_html.escape(b["symptom"])}</td>'
                f'</tr>'
            )
        p.append('</tbody></table>')
    else:
        p.append('<p class="gap-none">No MEDIUM bugs open.</p>')

    # ── Section 5: LOW bugs ──────────────────────────────────────────────────
    p.append('<h2 class="gap-section-h">Low Bugs — cosmetic / edge-case</h2>')
    if low_bugs:
        p.append('<table class="gap-table">')
        p.append('<thead><tr><th>ID</th><th>Issue</th><th>Symptom</th></tr></thead><tbody>')
        for b in low_bugs:
            p.append(
                f'<tr class="gap-row-low">'
                f'<td class="gap-id">{_html.escape(b["id"])}</td>'
                f'<td class="gap-title">{_html.escape(b["title"])}</td>'
                f'<td class="gap-sym">{_html.escape(b["symptom"])}</td>'
                f'</tr>'
            )
        p.append('</tbody></table>')
    else:
        p.append('<p class="gap-none">No LOW bugs open.</p>')

    content = '\n'.join(p)
    sidebar_html = build_sidebar('alpha-gaps.html')
    full_html = HTML_TEMPLATE.format(
        title='Open for Alpha',
        mermaid_cdn=MERMAID_CDN,
        sidebar=sidebar_html,
        content=content,
    )
    (OUT_DIR / 'alpha-gaps.html').write_text(full_html, encoding='utf-8')
    print(f'  alpha-gaps.html  ({n_high} HIGH · {n_medium} MED · {n_low} LOW bugs · {n_todo} missing · {n_partial} partial)')


def build_map_status_html():
    """Generate 18oe-map-status.html: dynamic progress bar + coverage grid + static reference content."""
    md_path = SRC_DIR / "18oe-map-status.md"
    if not md_path.exists():
        print("  18oe-map-status.html  (skipped — 18oe-map-status.md not found)")
        return

    MAP_COV_SECTIONS = {'Map & Components', 'Track Laying', 'Token Placement'}

    # Weighted progress stats from Map & Components (primary bar)
    done_w = pr_w = part_w = todo_w = 0.0
    for section, items in COVERAGE_DATA:
        if section != 'Map & Components':
            continue
        w = coverage_item_weight(section)
        for _name, status, _scope in items:
            if   status == 'done':     done_w += w
            elif status == 'needs-pr': pr_w   += w
            elif status == 'partial':  part_w += w * 0.5; todo_w += w * 0.5
            elif status == 'todo':     todo_w += w
    total_w = done_w + pr_w + part_w + todo_w or 1.0

    # Raw counts across all map-relevant sections (for chips)
    n = {'done': 0, 'needs-pr': 0, 'partial': 0, 'todo': 0}
    for section, items in COVERAGE_DATA:
        if section not in MAP_COV_SECTIONS:
            continue
        for _name, status, _scope in items:
            if status in n:
                n[status] += 1

    pct = round((done_w + pr_w) / total_w * 100)

    bar_html = build_shared_bar(
        rows=[{
            'label': 'Map & Components', 'done': done_w, 'pr': pr_w,
            'partial': part_w, 'todo': todo_w, 'total': total_w,
            'right': f'<strong>{pct}%</strong> · {n["done"] + n["needs-pr"]} / {sum(n.values())} items across map sections',
        }],
        chips=[
            {'cls': 'stat-done',    'label': 'Done',     'value': str(n['done'])},
            {'cls': 'stat-pr',      'label': 'Needs PR', 'value': str(n['needs-pr'])},
            {'cls': 'stat-partial', 'label': 'Partial',  'value': str(n['partial'])},
            {'cls': 'stat-todo',    'label': 'To do',    'value': str(n['todo'])},
        ],
    )

    # Coverage grid for all map-relevant sections
    cov_lines = ['<div class="coverage-map" style="margin-bottom:1.5rem">']
    for section, items in COVERAGE_DATA:
        if section not in MAP_COV_SECTIONS:
            continue
        anchor = re.sub(r'[^\w\s-]', '', section.lower()).strip().replace(' ', '-')
        all_beta = all(scope == 'beta' for _, _, scope in items)
        chapter_scope = 'beta' if all_beta else 'mixed'
        cov_lines.append(f'<div class="cov-chapter" data-chapter-scope="{chapter_scope}">')
        cov_lines.append(f'<div class="cov-chapter-title" id="cov-{anchor}">{_html.escape(section)}</div>')
        cov_lines.append('<div class="cov-items">')
        for label, status, scope in items:
            cov_lines.append(
                f'<div class="cov-item cov-{status}" data-scope="{scope}" title="{_html.escape(label)}">'
                f'{_html.escape(label)}</div>'
            )
        cov_lines.append('</div></div>')
    cov_lines.append('</div>')

    # Convert static .md, stripping the "## Overall Status" section (replaced above)
    raw = md_path.read_text(encoding='utf-8')
    lines_in = raw.splitlines(keepends=True)
    skip = False
    cleaned_lines = []
    for line in lines_in:
        if re.match(r'^## Overall Status\s*$', line):
            skip = True
            continue
        if skip and re.match(r'^## \w', line):
            skip = False
        if not skip:
            cleaned_lines.append(line)
    raw_cleaned = ''.join(cleaned_lines)

    tokenised, mermaid_blocks = extract_mermaid(raw_cleaned)
    body_html = convert_md(tokenised)
    body_html = rewrite_md_links(body_html)
    body_html = apply_confidence_markers(body_html)
    body_html = restore_mermaid(body_html, mermaid_blocks)
    # Drop the H1 (we emit it explicitly below)
    body_html = re.sub(r'<h1[^>]*>.*?</h1>\n?', '', body_html, count=1, flags=re.DOTALL)

    # Overall Status table from MAP_STATUS_TABLE
    STATUS_SYMBOL = {'done': '✓', 'needs-pr': '→', 'partial': '~', 'todo': '?'}
    table_lines = [
        '<h2 id="overall-status">Overall Status</h2>',
        '<table class="map-status-table">',
        '<thead><tr><th>Area</th><th>Status</th><th>Notes</th></tr></thead>',
        '<tbody>',
    ]
    for area, status, desc in MAP_STATUS_TABLE:
        sym = STATUS_SYMBOL.get(status, '?')
        table_lines.append(
            f'<tr class="ms-row ms-{status}">'
            f'<td class="ms-area">{_html.escape(area)}</td>'
            f'<td class="ms-status"><span class="ms-sym ms-sym-{status}">{sym}</span></td>'
            f'<td class="ms-desc">{desc}</td>'  # desc may contain <code> tags — no escaping
            f'</tr>'
        )
    table_lines += ['</tbody></table>']

    p = []
    p.append('<h1>18OE — Map Implementation Status</h1>')
    p.append('<p class="page-crosslink">For full rulebook picture → '
             '<a href="rulebook-coverage.html">Rulebook Coverage</a> · '
             'All open gaps → <a href="alpha-gaps.html">Open for Alpha</a></p>')
    p.append('<p class="bar-note">Bar weighted by section effort (L1 data = 1×).</p>')
    p.append(bar_html)
    p.append('\n'.join(table_lines))
    p.append('\n'.join(cov_lines))
    p.append('<hr>')
    p.append(body_html)

    content = '\n'.join(p)
    sidebar_html = build_sidebar('18oe-map-status.html')
    full_html = HTML_TEMPLATE.format(
        title='Map Implementation Status',
        mermaid_cdn=MERMAID_CDN,
        sidebar=sidebar_html,
        content=content,
    )
    (OUT_DIR / '18oe-map-status.html').write_text(full_html, encoding='utf-8')
    n_done = n['done'] + n['needs-pr']
    n_total = sum(n.values())
    print(f'  18oe-map-status.html  ({n_done}/{n_total} map items done or in review, {pct}%)')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def convert_file(md_path, out_dir):
    raw = md_path.read_text(encoding="utf-8")

    # Step 1: extract Mermaid blocks first
    tokenised, mermaid_blocks = extract_mermaid(raw)

    # Step 2: Markdown → HTML (Mermaid placeholders treated as plain text lines)
    body_html = convert_md(tokenised)

    # Step 3: rewrite .md → .html links
    body_html = rewrite_md_links(body_html)

    # Step 4: confidence markers
    body_html = apply_confidence_markers(body_html)

    # Step 5: restore Mermaid divs (after all other transforms)
    body_html = restore_mermaid(body_html, mermaid_blocks)

    out_filename = md_path.stem + ".html"
    title = extract_title(body_html)
    sidebar_html = build_sidebar(out_filename)

    full_html = HTML_TEMPLATE.format(
        title=title,
        mermaid_cdn=MERMAID_CDN,
        sidebar=sidebar_html,
        content=body_html,
    )

    (out_dir / out_filename).write_text(full_html, encoding="utf-8")
    print(f"  {md_path.name} → {out_filename}")
    return out_filename


def main():
    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "style.css").write_text(CSS, encoding="utf-8")

    # Files generated programmatically (not converted from .md directly)
    PROGRAMMATIC_MD = {'18oe-map-status.md'}

    converted = []
    for md_file in sorted(SRC_DIR.glob("*.md")):
        if md_file.name in PROGRAMMATIC_MD:
            continue
        converted.append(convert_file(md_file, OUT_DIR))

    readme_src = OUT_DIR / "readme.html"
    if readme_src.exists():
        shutil.copy(readme_src, OUT_DIR / "index.html")
        print("  readme.html → index.html (copy)")

    for img in SRC_DIR.glob("*.png"):
        shutil.copy(img, OUT_DIR / img.name)
        print(f"  {img.name} (copied)")

    images_src = SRC_DIR / "images"
    if images_src.is_dir():
        images_dst = OUT_DIR / "images"
        if images_dst.exists():
            shutil.rmtree(images_dst)
        shutil.copytree(images_src, images_dst)
        count = len(list(images_src.iterdir()))
        print(f"  images/ ({count} files copied)")

    (OUT_DIR / "search.js").write_text(SEARCH_JS, encoding="utf-8")
    (OUT_DIR / "ui.js").write_text(UI_JS, encoding="utf-8")
    build_status_html()
    build_coverage_html()
    build_alpha_gaps_html()
    build_map_status_html()
    build_search_index(OUT_DIR)

    print(f"\nDone. {len(converted)} pages → {OUT_DIR}/index.html")


if __name__ == "__main__":
    main()
