"""The small, intentionally strict front-matter contract used by article agents."""
import json
from pathlib import Path
import re

PUBLIC = 'https://insights.dekrov.com/'
SHORT_PATH = re.compile(r'/[a-z0-9]+(?:-[a-z0-9]+)*/')
ALIAS_PATH = re.compile(r'/(?:[a-z0-9]+(?:-[a-z0-9]+)*/)+(?:index\.html)?')
RESERVED = {'pages', 'assets', 'scripts', 'styles', 'theme', 'site', 'article', 'redirect', 'api'}


def front_matter(raw):
    """Read our string/null/string-list subset of YAML, never execute YAML tags.

    Keys are layout, permalink and redirect_from. Lists accept ordinary dash
    notation or a JSON array (which is also valid YAML). Unsupported syntax fails
    closed so source checks cannot disagree silently with Jekyll.
    """
    if not raw.startswith('---\n'):
        return {}, raw
    end = raw.find('\n---\n', 4)
    if end == -1:
        raise ValueError('unterminated front matter')
    data, current = {}, None
    for line in raw[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        item = re.fullmatch(r'  - (.+)', line)
        if item:
            if current != 'redirect_from' or not isinstance(data[current], list):
                raise ValueError('unexpected front-matter list item')
            data[current].append(_string(item.group(1)))
            continue
        entry = re.fullmatch(r'(layout|permalink|redirect_from):\s*(.*)', line)
        if not entry:
            raise ValueError('unsupported front matter: use layout, permalink and redirect_from only')
        key, value = entry.groups()
        if key in data:
            raise ValueError(f'duplicate front-matter key {key}')
        current = key
        if key == 'redirect_from':
            if not value: data[key] = []
            else:
                try: data[key] = json.loads(value)
                except ValueError as e: raise ValueError('redirect_from must be a string list') from e
                if not isinstance(data[key], list) or not all(isinstance(v, str) for v in data[key]):
                    raise ValueError('redirect_from must be a string list')
        elif key == 'layout':
            if value not in ('null', '~'): raise ValueError('article layout must be null')
            data[key] = None
        else: data[key] = _string(value)
    return data, raw[end + 5:]


def _string(value):
    if value.startswith('"'):
        try: parsed = json.loads(value)
        except ValueError as e: raise ValueError('invalid quoted front-matter value') from e
        if not isinstance(parsed, str): raise ValueError('expected string')
        return parsed
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if not value or any(c in value for c in '{}[]&*!|>#'):
        raise ValueError('unsupported front-matter value')
    return value


def output_file(site, route):
    return Path(site) / route.lstrip('/') / 'index.html' if route.endswith('/') else Path(site) / route.lstrip('/')


def collect_routes(root, pages):
    """Return public paths and aliases mapped to sources, plus actionable errors."""
    root = Path(root).resolve()
    routes, canonical, errors = {'/': root / 'index.html'}, {}, []
    pending = []
    for page in pages:
        if not isinstance(page, dict) or not page.get('slug'): continue
        slug = page['slug']
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug): continue
        source = root / 'pages' / slug / 'index.html'
        route = page.get('path')
        if not isinstance(route, str) or not SHORT_PATH.fullmatch(route):
            errors.append(f'pages.json {slug}: path must be a short root-relative /lowercase-name/'); continue
        name = route.strip('/')
        if name in RESERVED or (root / name).exists():
            errors.append(f'pages.json {slug}: reserved or existing root path {route}')
        if route in routes: errors.append(f'pages.json: duplicate public path {route}')
        routes[route] = source
        canonical[slug] = route
        if not source.is_file(): continue
        try: meta, _ = front_matter(source.read_text())
        except ValueError as e: errors.append(f'pages/{slug}/index.html: {e}'); continue
        if 'layout' not in meta or meta['layout'] is not None:
            errors.append(f'pages/{slug}/index.html: front matter must set layout: null')
        if meta.get('permalink') != route:
            errors.append(f'pages/{slug}/index.html: permalink must match catalog path {route}')
        aliases = meta.get('redirect_from', [])
        expected = {f'/pages/{slug}/', f'/pages/{slug}/index.html'}
        if not expected.issubset(set(aliases)):
            errors.append(f'pages/{slug}/index.html: redirect_from must preserve both legacy article URLs')
        for alias in aliases:
            if not ALIAS_PATH.fullmatch(alias) or alias.split('/')[1] in RESERVED - {'pages'}:
                errors.append(f'pages/{slug}/index.html: unsafe or reserved redirect alias {alias}'); continue
            pending.append((alias, source))
    canonical_outputs = {str(output_file('/', route)) for route in canonical.values()}
    occupied_outputs = {str(output_file('/', route)): source for route, source in routes.items()}
    for alias, source in pending:
        slot = str(output_file('/', alias))
        physical = output_file(root, alias)
        if (alias in routes or slot in canonical_outputs or
                (slot in occupied_outputs and occupied_outputs[slot] != source) or
                (physical.exists() and physical.resolve() != source)):
            errors.append(f'redirect alias collision: {alias}')
        occupied_outputs[slot] = source
        routes[alias] = source
    return routes, canonical, errors
