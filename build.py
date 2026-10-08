"""Build index.html from cv.toml.   Usage: python3 build.py

Only the Python standard library is needed. Every fact on the page comes from cv.toml,
which is kept in step with the CV, so the website and the CV never disagree.
"""
import html
import re
import tomllib
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
ICONS = {
    "github": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.56-.29-5.25-1.28-5.25-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.47.11-3.06 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.77.11 3.06.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.27 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05a3.74 3.74 0 0 1 3.37-1.85c3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45ZM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "download": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 3v12m0 0-4-4m4 4 4-4M4 19h16"/></svg>',
    "theme": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>',
}


def e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def chips(items) -> str:
    return '<ul class="chips">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"


def points(items, limit=None) -> str:
    items = [i for i in items if i.strip()][:limit]
    return '<ul class="points">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>" if items else ""


def split_name(name: str) -> tuple[str, str]:
    """'Classifier (university group project, team of 3)' -> ('Classifier', 'University group project, team of 3')."""
    m = re.match(r"^(.*?)\s*\((.+)\)\s*$", name)
    return (m[1], m[2][:1].upper() + m[2][1:]) if m else (name, "")


def build(cv: dict) -> str:
    p = cv["profile"]
    gh = f"https://github.com/{p['github_user']}"
    year = date.today().year

    stats = "".join(f'<div class="stat"><b>{e(h["value"])}</b><span>{e(h["label"])}</span></div>'
                    for h in p.get("highlights", []))

    jobs = "".join(f"""
      <li class="card job reveal"><header><div><h3>{e(j['title'])}</h3>
        <div class="org">{e(j['company'])} &middot; {e(j['location'])}</div></div>
        <div class="when">{e(j['dates'])}</div></header>{points(j['bullets'], 4)}</li>"""
                   for j in cv.get("experience", []))

    cards = []
    for pr in cv.get("projects", []):
        title, tag = split_name(pr["name"])
        repo = cv.get("repos", {}).get(pr["id"], {})
        if repo.get("published"):
            link = f'<a href="{gh}/{e(repo["name"])}">View code &rarr;</a>'
        else:
            link = '<span class="soon">Code: coming soon</span>'
        cards.append(f"""
      <article class="card project reveal"><h3>{e(title)}</h3>
        <div class="meta">{f'<span class="tag" style="margin:0 6px 0 0">{e(tag)}</span>' if tag else ''}{e(pr.get('dates') or 'Personal project')}</div>{points(pr['bullets'], 3)}
        {chips(pr.get('tech', []))}<div class="links">{link}</div></article>""")

    skills = "".join(f'<div class="card reveal"><h3>{e(group)}</h3>{chips(items)}</div>'
                     for group, items in cv.get("skills", {}).items())

    edu = "".join(f"""
      <div class="card job reveal"><header><div><h3>{e(ed['degree'])}</h3>
        <div class="org">{e(ed['institution'])} &middot; {e(ed['location'])}</div></div>
        <div class="when">{e(ed['dates'])}</div></header>{points(ed.get('details', []))}</div>"""
                  for ed in cv.get("education", []))
    certs = cv.get("certifications", []) + cv.get("achievements", [])
    if certs:
        edu += f'<div class="card reveal"><h3>Certifications &amp; achievements</h3>{points(certs)}</div>'

    dissertation = next((d.split(":", 1)[1].strip() for ed in cv.get("education", [])
                         for d in ed.get("details", []) if d.lower().startswith("dissertation")), "")
    title = f"{p['name']} - {p['role']}"
    desc = p["tagline"]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav"><div class="wrap">
  <a class="brand" href="#top">{e(p['name'])}</a>
  <nav aria-label="Sections"><a href="#about">About</a><a href="#experience">Experience</a><a href="#projects">Projects</a><a href="#skills">Skills</a><a href="#education">Education</a><a href="#contact">Contact</a></nav>
  <button class="theme" type="button" aria-label="Switch light or dark theme">{ICONS['theme']}</button>
</div></header>

<main id="main" class="wrap">
  <section class="hero" id="top">
    <span class="badge"><span class="dot"></span>Open to: {e(p['open_to'])}</span>
    <h1>{e(p['name'])}</h1>
    <p class="role">{e(p['role'])} &middot; {e(p['location'])}</p>
    <p class="tagline">{e(p['tagline'])}</p>
    <div class="actions">
      <a class="btn primary" href="{e(p['cv_file'])}" download>{ICONS['download']}Download CV</a>
      <a class="btn" href="{gh}">{ICONS['github']}GitHub</a>
      <a class="btn" href="{e(p['linkedin'])}">{ICONS['linkedin']}LinkedIn</a>
      <a class="btn" href="mailto:{e(p['email'])}">{ICONS['mail']}Email</a>
    </div>
    <div class="stats">{stats}</div>
  </section>

  <section id="about">
    <h2>About</h2>
    <div class="grid2">
      <div class="card reveal"><p style="margin:0">{e(cv['summary'].strip())}</p></div>
      <dl class="card now reveal">
        <dt>Now</dt><dd>Final year, {e(cv['education'][0]['degree'])}, {e(cv['education'][0]['institution'])}</dd>
        {f'<dt>Dissertation</dt><dd>{e(dissertation)}</dd>' if dissertation else ''}
        <dt>Looking for</dt><dd>{e(p['open_to'])}</dd>
        <dt>Based in</dt><dd>{e(p['location'])}</dd>
      </dl>
    </div>
  </section>

  <section id="experience">
    <h2>Experience</h2>
    <p class="lead">Professional work in full-stack development and data analysis.</p>
    <ol class="timeline">{jobs}
    </ol>
  </section>

  <section id="projects">
    <h2>Projects</h2>
    <p class="lead">Machine learning, data engineering and automation, with the code on GitHub.</p>
    <div class="projects">{''.join(cards)}
    </div>
  </section>

  <section id="skills">
    <h2>Skills</h2>
    <p class="lead">Tools I have used in real work and projects.</p>
    <div class="skills">{skills}</div>
  </section>

  <section id="education">
    <h2>Education</h2>
    <div style="display:grid;gap:16px">{edu}</div>
  </section>

  <section id="contact">
    <div class="card contact reveal">
      <h2>Let's talk</h2>
      <p>I'm looking for {e(p['open_to'][0].lower() + p['open_to'][1:])}. The quickest way to reach me is email.</p>
      <div class="actions">
        <a class="btn primary" href="mailto:{e(p['email'])}">{ICONS['mail']}{e(p['email'])}</a>
        <a class="btn" href="{e(p['linkedin'])}">{ICONS['linkedin']}LinkedIn</a>
        <a class="btn" href="{gh}">{ICONS['github']}GitHub</a>
      </div>
    </div>
  </section>
</main>
<footer>&copy; {year} {e(p['name'])} &middot; Built with Python and plain HTML/CSS &middot; <a href="{gh}/{e(p['github_user'])}.github.io">Source</a></footer>
<script src="script.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    data = tomllib.loads((HERE / "cv.toml").read_text(encoding="utf-8"))
    (HERE / "index.html").write_text(build(data), encoding="utf-8")
    print("Wrote index.html")
