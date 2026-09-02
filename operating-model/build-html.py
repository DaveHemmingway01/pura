import re, html, pathlib

SRC = pathlib.Path("/home/user/pura/operating-model/dave-operating-model-v1.md")
OUT = pathlib.Path("/home/user/pura/operating-model/dave-operating-model-v1.html")

BADGE = re.compile(r"\[(Established|Hypothesis|Unknown)([^\]]*)\]")

def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    def b(m):
        kind = m.group(1)
        extra = m.group(2).strip()
        cls = kind.lower()
        label = kind + (" " + extra.lstrip(", ") if extra else "")
        return f'<span class="tag tag-{cls}">{label}</span>'
    t = BADGE.sub(b, t)
    return t

lines = SRC.read_text().split("\n")
out = []
i = 0
n = len(lines)
sec = 0

def flush_list(buf, tag):
    if buf:
        out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in buf) + f"</{tag}>")
    return []

ul, ol = [], []
while i < n:
    line = lines[i]
    s = line.strip()

    if not s:
        ul = flush_list(ul, "ul"); ol = flush_list(ol, "ol"); i += 1; continue

    if s.startswith("|") and i + 1 < n and set(lines[i+1].strip()) <= set("|-: "):
        ul = flush_list(ul, "ul"); ol = flush_list(ol, "ol")
        head = [c.strip() for c in s.strip("|").split("|")]
        i += 2
        rows = []
        while i < n and lines[i].strip().startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
            i += 1
        th = "".join(f"<th>{inline(c)}</th>" for c in head)
        tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
        out.append(f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
        continue

    if s == "---":
        ul = flush_list(ul, "ul"); ol = flush_list(ol, "ol")
        out.append('<hr />'); i += 1; continue

    m = re.match(r"^(#{1,4})\s+(.*)$", s)
    if m:
        ul = flush_list(ul, "ul"); ol = flush_list(ol, "ol")
        lvl, txt = len(m.group(1)), m.group(2)
        if lvl == 1:
            out.append(f"<h1>{inline(txt)}</h1>")
        elif lvl == 2:
            eyebrow = ""
            em = re.match(r"^([A-H])\.\s+(.*)$", txt)
            if em:
                eyebrow = f'<span class="eyebrow">Deel {em.group(1)}</span>'
                txt = em.group(2)
            out.append(f'<h2>{eyebrow}<span>{inline(txt)}</span></h2>')
        else:
            out.append(f"<h{lvl}>{inline(txt)}</h{lvl}>")
        i += 1; continue

    m = re.match(r"^-\s+(.*)$", s)
    if m:
        ol = flush_list(ol, "ol"); ul.append(m.group(1)); i += 1; continue

    m = re.match(r"^\d+\.\s+(.*)$", s)
    if m:
        ul = flush_list(ul, "ul"); ol.append(m.group(1)); i += 1; continue

    ul = flush_list(ul, "ul"); ol = flush_list(ol, "ol")
    para = [s]
    i += 1
    while i < n and lines[i].strip() and not re.match(r"^(#|-\s|\d+\.\s|\||---$)", lines[i].strip()):
        para.append(lines[i].strip()); i += 1
    out.append(f"<p>{inline(' '.join(para))}</p>")

flush_list(ul, "ul"); flush_list(ol, "ol")
out = out[2:]  # drop the markdown h1 and version line; the masthead replaces them
body = "\n".join(out)

CSS = """
<title>Dave's Operating Model</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>
:root{
  --paper:#F5F6F3; --surface:#FFFFFF; --ink:#141D1A; --ink-soft:#4C5852;
  --rule:#DCE0DA; --rule-soft:#E9ECE6;
  --accent:#0E5A50; --accent-soft:#E2EEEA;
  --amber:#7E5310; --amber-soft:#F4EBDA;
  --clay:#8B3A30; --clay-soft:#F6E5E2;
  --sans:"IBM Plex Sans",system-ui,-apple-system,Segoe UI,sans-serif;
  --serif:"Newsreader",Georgia,"Times New Roman",serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0F1412; --surface:#161D1A; --ink:#E4E9E5; --ink-soft:#9AA8A2;
    --rule:#2A342F; --rule-soft:#212A26;
    --accent:#6DC3B2; --accent-soft:#17322D;
    --amber:#D8A64A; --amber-soft:#2E2718;
    --clay:#E38A7C; --clay-soft:#33201D;
  }
}
:root[data-theme="dark"]{
  --paper:#0F1412; --surface:#161D1A; --ink:#E4E9E5; --ink-soft:#9AA8A2;
  --rule:#2A342F; --rule-soft:#212A26;
  --accent:#6DC3B2; --accent-soft:#17322D;
  --amber:#D8A64A; --amber-soft:#2E2718;
  --clay:#E38A7C; --clay-soft:#33201D;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16.5px;line-height:1.62;-webkit-font-smoothing:antialiased}
.wrap{max-width:830px;margin:0 auto;padding:56px 28px 120px}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(2.3rem,5.2vw,3.4rem);line-height:1.05;letter-spacing:-.02em;margin:0 0 18px;text-wrap:balance}
h2{display:flex;flex-direction:column;gap:10px;font-family:var(--serif);font-weight:600;font-size:clamp(1.55rem,3.2vw,2.05rem);line-height:1.15;letter-spacing:-.015em;margin:72px 0 20px;padding-top:26px;border-top:2px solid var(--ink);text-wrap:balance}
h3{font-family:var(--sans);font-weight:600;font-size:1.12rem;letter-spacing:-.005em;margin:38px 0 12px}
h4{font-family:var(--mono);font-weight:500;font-size:.82rem;text-transform:uppercase;letter-spacing:.1em;color:var(--ink-soft);margin:30px 0 10px}
.eyebrow{font-family:var(--mono);font-size:.72rem;font-weight:500;text-transform:uppercase;letter-spacing:.18em;color:var(--accent)}
p{margin:0 0 16px;max-width:68ch}
ul,ol{margin:0 0 18px;padding-left:22px;max-width:68ch}
li{margin:0 0 7px}
li::marker{color:var(--ink-soft)}
strong{font-weight:600}
hr{border:0;height:1px;background:var(--rule);margin:52px 0}
h2+hr,hr+h2{display:none}
.tag{display:inline-block;font-family:var(--mono);font-size:.68rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;padding:2px 7px;border-radius:2px;margin-right:7px;vertical-align:1px;white-space:nowrap}
.tag-established{background:var(--accent-soft);color:var(--accent)}
.tag-hypothesis{background:var(--amber-soft);color:var(--amber);white-space:normal}
.tag-unknown{background:var(--clay-soft);color:var(--clay)}
.tw{overflow-x:auto;margin:0 0 26px;border-top:1.5px solid var(--ink);border-bottom:1px solid var(--rule)}
table{border-collapse:collapse;width:100%;font-size:.9rem;line-height:1.5}
th{font-family:var(--mono);font-weight:500;font-size:.7rem;text-transform:uppercase;letter-spacing:.09em;color:var(--ink-soft);text-align:left;padding:11px 14px 11px 0;border-bottom:1px solid var(--rule);vertical-align:bottom}
td{padding:12px 14px 12px 0;border-bottom:1px solid var(--rule-soft);vertical-align:top}
tr:last-child td{border-bottom:0}
th:last-child,td:last-child{padding-right:0}
.masthead{border-top:3px solid var(--ink);padding-top:20px}
.meta{display:flex;flex-wrap:wrap;gap:8px 26px;font-family:var(--mono);font-size:.74rem;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-soft);margin:0 0 34px}
.meta b{font-weight:500;color:var(--accent)}
.lede{font-family:var(--serif);font-size:1.16rem;line-height:1.5;color:var(--ink-soft)}
.key{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);margin:0 0 46px}
.key div{padding:14px 18px 14px 0}
.key p{margin:6px 0 0;font-size:.86rem;color:var(--ink-soft);max-width:none}
@media(max-width:620px){
  .wrap{padding:36px 20px 80px}
  body{font-size:16px}
}
@media(prefers-reduced-motion:no-preference){
  a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
}
</style>
"""



masthead = """
<div class="masthead">
  <h1>Dave&rsquo;s Operating Model</h1>
  <div class="meta">
    <span>Versie <b>1.0</b></span><span>Concept ter goedkeuring</span><span>2 september 2026</span>
  </div>
</div>
<div class="key">
  <div><span class="tag tag-established">Established</span><p>Voldoende onderbouwd door discovery of door bewijs uit agenda en mail.</p></div>
  <div><span class="tag tag-hypothesis">Hypothesis</span><p>Aannemelijk, maar nog in de praktijk te toetsen. Toetsen staan in deel G.</p></div>
  <div><span class="tag tag-unknown">Unknown</span><p>Nog geen verantwoorde werkhypothese. Eén stuk in dit document.</p></div>
</div>
"""

OUT.write_text(CSS + '<div class="wrap">' + masthead + body + "</div>\n")
print("wrote", OUT, OUT.stat().st_size, "bytes")
