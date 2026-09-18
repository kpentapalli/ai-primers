"""Convert the four published primer artifacts into a standalone static site."""
import re, html, pathlib

SRC = pathlib.Path('artifact-files')
OUT = pathlib.Path('site')
MODULES = [  # (artifact id, download dir, slug, favicon)
    ('F9V7xgiTeUqUhfz4UHDaAe', '728f3891-41cd-4c41-97ab-93b1465ce1d3', 'ai-foundations', '🧠'),
    ('UfRJCuqW1j2VZV8jaHWpDg', 'e003fafc-b7fa-42c9-8693-fd74c81241a3', 'ml-fundamentals', '📈'),
    ('Hq9CZQhpjkQU93jyULjaAk', '884af8f6-7ffd-4645-bba2-20eb34733b79', 'spec-driven-development', '📐'),
    ('Xm1JUB7qXXKVHnv3bxBRGh', 'f9171240-04aa-43e6-8e0f-2d8db045382e', 'agentic-ai', '🤖'),
]
URL = {aid: f'{slug}.html' for aid, _, slug, _ in MODULES}

def favicon(emoji):
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>{emoji}</text></svg>"
    return '<link rel="icon" href="data:image/svg+xml,' + svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23') + '">'

cards, tokens, fonts = [], None, None
for n, (aid, d, slug, emoji) in enumerate(MODULES, 1):
    s = (SRC / d / 'index.html').read_text()
    inner = s[s.index('<body>') + 6 : s.rindex('</body>')].strip()   # drop the artifact runtime shell
    cut = inner.index('</style>') + 8                                 # title + fonts + css belong in <head>
    head, body = inner[:cut], inner[cut:].strip()
    for a, target in URL.items():
        body = body.replace(f'https://claude.ai/artifact/{a}', target)
    assert 'claude.ai/artifact' not in body
    title = re.search(r'<title>(.*?)</title>', head).group(1)
    lede = re.search(r'<p class="lede">(.*?)</p>', body, re.S).group(1)
    body = body.replace('<div class="modlinks">', '<div class="modlinks"><a href="./">← All modules</a>', 1)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            f'<meta name="description" content="{html.escape(re.sub("<.*?>", "", lede), quote=True)}">\n'
            f'{favicon(emoji)}\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n')
    (OUT / f'{slug}.html').write_text(page)
    cards.append((n, slug, emoji, title, lede, len(re.findall(r'<section', body))))
    if tokens is None:
        css = head[head.index('<style>') + 7:]
        tokens = css[:css.index('*{box-sizing')]
        fonts = head[head.index('<link'):head.index('<style>')]

card_html = '\n'.join(
    f'<a class="card" href="{slug}.html"><div class="num">Module {n} of 4</div>'
    f'<h2><span aria-hidden="true">{emoji}</span> {title}</h2><p>{lede}</p><span class="go">Open module →</span></a>'
    for n, slug, emoji, title, lede, secs in cards)

index = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="Four visual primers for product leaders: AI Foundations, ML Fundamentals, Spec-Driven Development, Agentic AI.">
{favicon('🧭')}
<title>Visual Primers for Product Leaders</title>
{fonts}<style>
{tokens}*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}}
.shell{{max-width:1180px;margin:0 auto;padding-block:0 48px;padding-inline:16px}}
a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
h1,h2{{font-family:var(--display);text-wrap:balance;margin:0}}
h1{{font-size:clamp(34px,5vw,54px);font-weight:800;line-height:1.02;letter-spacing:-.02em}}
h2{{font-size:clamp(22px,2.6vw,28px);font-weight:700;line-height:1.15}}
p{{margin:0}}
.masthead{{padding-block:36px 24px;border-bottom:1px solid var(--line);display:grid;gap:14px}}
.series{{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}}
.lede{{font-size:18px;color:var(--ink-2);max-width:62ch}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:16px;margin-top:28px}}
.card{{display:grid;gap:10px;align-content:start;padding:22px;background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow);text-decoration:none;color:inherit;transition:border-color .15s,transform .15s}}
.card:hover{{border-color:var(--accent);transform:translateY(-2px)}}
@media (prefers-reduced-motion:reduce){{.card{{transition:none}}.card:hover{{transform:none}}}}
.card p{{color:var(--ink-2);font-size:15px}}
.num{{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
.go{{font-size:14px;font-weight:600;color:var(--accent);margin-top:4px}}
.legend{{display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:28px;font-size:13px;color:var(--ink-2)}}
.legend span{{display:inline-flex;align-items:center;gap:6px}}
.legend i{{width:12px;height:12px;border-radius:3px;display:inline-block}}
</style>
</head>
<body>
<div class="shell">
<header class="masthead">
  <div class="series">Visual primers for product leaders</div>
  <h1>AI, ML, specs and agents, as pictures</h1>
  <p class="lede">Four modules sharing one visual language. Every idea is a diagram first; open the panels inside each module for why it matters, the mechanics, or a basics refresher.</p>
</header>
<main class="grid">
{card_html}
</main>
<div class="legend" aria-label="Colour code used in every diagram">
  <span><i style="background:var(--data)"></i>Data</span>
  <span><i style="background:var(--model)"></i>Model / compute</span>
  <span><i style="background:var(--human)"></i>People</span>
  <span><i style="background:var(--tool)"></i>Tools / systems</span>
  <span><i style="background:var(--risk)"></i>Risk</span>
</div>
</div>
</body>
</html>
'''
(OUT / 'index.html').write_text(index)
(OUT / '.nojekyll').write_text('')
for p in sorted(OUT.iterdir()): print(p.name, p.stat().st_size)
print(cards)
