#!/usr/bin/env python3
"""Dependency-free catalog/HTML validator and best-effort public link checker.
Legacy articles receive compatibility checks; v2 articles receive the full contract.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = 'https://insights.dekrov.com/'
LEGACY_SLUGS = {'agents-md-codex-attack', 'beam-vs-deepseek', 'gemini-4-carbon', 'gpt-6-1-terra', 'kimi-k3-1-pro', 'mercury-3'}
TYPES = {'official', 'independent', 'community', 'unconfirmed'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children, self.text = [], ''
    def has(self, cls):
        return cls in self.attrs.get('class', '').split()
    def content(self):
        return self.text + ''.join(c.content() for c in self.children)
    def below(self, tag=None, cls=None):
        return [c for c in self.walk() if (not tag or c.tag == tag) and (not cls or c.has(cls))]
    def walk(self):
        for c in self.children:
            yield c
            yield from c.walk()
    def ancestor(self, tag):
        p = self.parent
        while p:
            if p.tag == tag:
                return p
            p = p.parent

class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.root = Node('document')
        self.current = self.root
        self.raw = path.read_text(encoding='utf-8')
        self.feed(self.raw)
        self.nodes = list(self.root.walk())
        self.ids = {n.attrs['id']: n for n in self.nodes if n.attrs.get('id')}
    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.current)
        self.current.children.append(n)
        if tag not in VOID:
            self.current = n
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)
    def handle_endtag(self, tag):
        n = self.current
        while n.parent:
            if n.tag == tag:
                self.current = n.parent
                return
            n = n.parent
    def handle_data(self, data):
        self.current.text += data
    def find(self, tag):
        return [n for n in self.nodes if n.tag == tag]


def validate(root=ROOT):
    errors, warnings, external = [], [], set()
    def fail(path, text): errors.append(f'{path.relative_to(root)}: {text}')
    try:
        pages = json.loads((root / 'pages.json').read_text())
    except (OSError, ValueError) as e:
        return [f'pages.json: {e}'], [], set(), 0
    if not isinstance(pages, list) or not pages:
        return ['pages.json must be a nonempty array'], [], set(), 0
    slugs = []
    for i, page in enumerate(pages):
        if not isinstance(page, dict):
            errors.append(f'pages.json entry {i} must be an object'); continue
        slug = page.get('slug')
        if not isinstance(slug, str) or (slug and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug)):
            errors.append(f'pages.json entry {i}: invalid slug'); continue
        if slug in slugs: errors.append(f'pages.json: duplicate slug {slug!r}')
        slugs.append(slug)
        if not isinstance(page.get('title'), str) or not page['title'].strip(): errors.append(f'pages.json {slug}: missing title')
        if not isinstance(page.get('meta'), str): errors.append(f'pages.json {slug}: missing meta')
    if not slugs or slugs[0] != '' or slugs.count('') != 1:
        errors.append('pages.json: Home must appear exactly once, first')
    article_paths = {p.parent.name: p for p in (root / 'pages').glob('*/index.html') if not p.parent.name.startswith('_')}
    for slug in set(slugs) - {''}:
        if slug not in article_paths: errors.append(f'pages.json: missing pages/{slug}/index.html')
    for slug in article_paths:
        if slug not in slugs: errors.append(f'Unregistered article: pages/{slug}/index.html')
    paths = [root / 'index.html', *article_paths.values()]
    docs = {p.resolve(): Document(p) for p in paths if p.exists()}
    for path, doc in docs.items():
        body = next(iter(doc.find('body')), None)
        slug = '' if path == (root / 'index.html').resolve() else path.parent.name
        if not body or body.attrs.get('data-page') != slug: fail(path, 'body data-page must match the catalog slug')
        if not body or body.attrs.get('data-root') != ('./' if slug == '' else '../../'): fail(path, 'incorrect data-root')
        if len(doc.find('h1')) != 1: fail(path, 'expected exactly one h1')
        ids = [n.attrs['id'] for n in doc.nodes if n.attrs.get('id')]
        if len(ids) != len(set(ids)): fail(path, 'duplicate HTML IDs')
        if not any('data-site-nav' in n.attrs for n in doc.nodes): fail(path, 'missing shared navigation')
        scripts = [n.attrs.get('src', '').split('?')[0] for n in doc.find('script')]
        for script in ('site.js', 'theme.js'):
            if not any(s.endswith('/' + script) for s in scripts): fail(path, f'missing {script}')
        if slug:
            if len([n for n in doc.nodes if n.has('article-engagement')]) != 1: fail(path, 'expected one reactions block')
            if len([n for n in doc.nodes if 'data-like-button' in n.attrs]) != 1: fail(path, 'expected one like button')
            for script in ('article-likes.js', 'article.js'):
                if not any(s.endswith('/' + script) for s in scripts): fail(path, f'missing {script}')
        v2 = any(n.attrs.get('data-article-version') == '2' for n in doc.nodes)
        for n in doc.nodes:
            fields = [n.attrs[k] for k in ('href', 'src') if n.attrs.get(k)]
            if n.tag in {'img', 'source'} and n.attrs.get('srcset'):
                fields += [part.strip().split()[0] for part in n.attrs['srcset'].split(',') if part.strip()]
            for value in fields:
                url = urlsplit(value)
                if url.scheme in {'http', 'https'} or url.netloc:
                    if v2 and n.tag in {'a', 'img', 'source'}: external.add(value.split('#')[0])
                    continue
                if url.scheme:
                    if url.scheme not in {'mailto', 'tel', 'data'}: fail(path, f'unsafe URL scheme: {value}')
                    continue
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                if url.path.startswith('/dekrov-insights/'):
                    target = (root / unquote(url.path[len('/dekrov-insights/'):])).resolve()
                if target.is_dir(): target /= 'index.html'
                if not target.is_relative_to(root.resolve()): fail(path, f'local link escapes repository: {value}'); continue
                if not target.exists(): fail(path, f'missing local target: {value}'); continue
                if url.fragment and target.suffix == '.html':
                    other = docs.get(target) or Document(target)
                    if unquote(url.fragment) not in other.ids: fail(path, f'missing fragment: {value}')
        if slug and slug not in LEGACY_SLUGS and not v2: fail(path, "new article requires data-article-version=2")
        if not v2: continue
        if re.search(r'\{\{[^}]+\}\}', doc.raw): fail(path, 'unfilled template tokens')
        for key in ('description', 'og:title', 'og:description', 'og:url'):
            if not any((n.attrs.get('name') == key or n.attrs.get('property') == key) and n.attrs.get('content', '').strip() for n in doc.find('meta')):
                fail(path, f'missing metadata: {key}')
        expected_url = PUBLIC + f'pages/{slug}/'
        if not any(n.attrs.get('rel') == 'canonical' and n.attrs.get('href') == expected_url for n in doc.find('link')): fail(path, 'incorrect canonical URL')
        if not any(n.attrs.get('property') == 'og:url' and n.attrs.get('content') == expected_url for n in doc.find('meta')): fail(path, 'incorrect og:url')
        for section_id in ('overview', 'technical-deep-dive', 'explained-simply', 'conclusion', 'sources'):
            if section_id not in doc.ids: fail(path, f'missing required anchor #{section_id}')
        simple = doc.ids.get('explained-simply')
        if simple and len(simple.content().split()) < 80: warnings.append(f'{path.relative_to(root)}: plain-English explanation is short; review completeness')
        if not any(n.tag == 'a' and n.attrs.get('href') == '#explained-simply' for n in doc.nodes): fail(path, 'missing no-JS plain-English jump')
        meta_times = [t for n in doc.nodes if n.has('article-meta') for t in n.below('time')]
        times = doc.find('time')
        if len(meta_times) < 2: fail(path, 'missing publication/update dates')
        for n in times:
            try: date.fromisoformat(n.attrs.get('datetime', '')[:10])
            except ValueError: fail(path, 'invalid date on time element')
        sources = [n for n in doc.find('li') if n.attrs.get('id', '').startswith('source-')]
        if not sources: fail(path, 'missing numbered bibliography')
        citations = [n for n in doc.find('a') if n.has('citation')]
        if not citations: fail(path, 'missing inline citations')
        for i, n in enumerate(sources, 1):
            if n.attrs.get('id') != f'source-{i}': fail(path, 'source IDs must be contiguous and in bibliography order')
            if not n.parent or not n.parent.has('source-list') or n.parent.tag != 'ol': fail(path, 'sources must be direct children of ol.source-list')
            if n.attrs.get('data-source-type') not in TYPES: fail(path, f'invalid source classification: {n.attrs.get("id")}')
            if not any(urlsplit(a.attrs.get('href', '')).scheme == 'https' for a in n.below('a')): fail(path, f'{n.attrs.get("id")}: source requires a direct HTTPS URL')
            if not n.below('time'): fail(path, f'{n.attrs.get("id")}: missing accessed date')
            if not any(a.attrs.get('href') == '#' + n.attrs['id'] for a in citations): fail(path, f'uncited source {n.attrs["id"]}')
        for n in citations:
            target = n.attrs.get('href', '')
            if not re.fullmatch(r'#source-[1-9][0-9]*', target) or target[1:] not in doc.ids: fail(path, f'invalid citation target: {target}')
            elif n.content().strip() != '[' + target.removeprefix('#source-') + ']': fail(path, f'citation number does not match {target}')
        for figure in [n for n in doc.find('figure') if n.has('article-figure')]:
            if not figure.below('figcaption'): fail(path, 'figure missing caption')
            if not figure.attrs.get('data-rights'): fail(path, 'figure missing rights/permission statement (data-rights)')
            if not figure.attrs.get('data-visual-kind'): fail(path, 'figure must label its visual kind')
            if not any(urlsplit(n.attrs.get('href', '')).scheme == 'https' for n in figure.below('a')): fail(path, 'figure missing original source link')
        for n in doc.find('img'):
            if not n.attrs.get('alt', '').strip(): fail(path, 'image needs meaningful alt text')
            if not all(n.attrs.get(k, '').isdigit() and int(n.attrs[k]) > 0 for k in ('width', 'height')): fail(path, 'image needs positive width and height')
            if n.attrs.get('loading') != 'lazy': fail(path, 'inline article images must use loading=lazy')
            if not n.ancestor('figure'): fail(path, 'evidence image must belong to a credited figure')
        if not page_summary(pages, slug): fail(path, 'v2 article requires catalog summary')
    return errors, warnings, external, len(article_paths)


def page_summary(pages, slug):
    return any(p.get('slug') == slug and isinstance(p.get('summary'), str) and p['summary'].strip() for p in pages if isinstance(p, dict))


def public_url(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password: return False
    if p.hostname == 'localhost' or '.' not in p.hostname: return False
    try:
        if not ipaddress.ip_address(p.hostname).is_global: return False
    except ValueError: pass
    return True

class PublicRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not public_url(newurl): raise URLError('Redirect is not public HTTPS')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check_link(url):
    result = {'url': url, 'checked_at': datetime.now(timezone.utc).isoformat()}
    if not public_url(url): return {**result, 'state': 'unverified', 'detail': 'Only public HTTPS links are probed'}
    opener = build_opener(PublicRedirects())
    for method in ('HEAD', 'GET'):
        try:
            req = Request(url, method=method, headers={'User-Agent': 'DekrovInsights-LinkCheck/1.0'})
            with opener.open(req, timeout=12) as response:
                return {**result, 'state': 'available', 'status': response.status, 'final_url': response.url}
        except HTTPError as e:
            if method == 'HEAD' and e.code in (400, 403, 405, 501): continue
            return {**result, 'state': 'broken' if e.code in (404, 410) else 'unverified', 'status': e.code}
        except (URLError, OSError, ValueError) as e:
            return {**result, 'state': 'unverified', 'detail': str(e)[:200]}
    return {**result, 'state': 'unverified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--links', action='store_true', help='Probe unique external links on v2 articles')
    parser.add_argument('--report', type=Path, help='Write link availability JSON outside published pages')
    args = parser.parse_args()
    errors, warnings, external, count = validate()
    for item in warnings: print('REVIEW:', item)
    results = []
    if args.links:
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(check_link, sorted(external)))
        for result in results:
            print(f'{result["state"].upper()}: {result["url"]} ({result.get("status", result.get("detail", ""))})')
            if result['state'] == 'broken': errors.append(f'Broken external link: {result["url"]}')
    if args.report:
        args.report.write_text(json.dumps({'checked_at': datetime.now(timezone.utc).isoformat(), 'errors': errors, 'warnings': warnings, 'links': results}, indent=2) + '\n')
    for item in errors: print('ERROR:', item, file=sys.stderr)
    print(f'{count} articles checked; {len(errors)} errors; {len(warnings)} editorial review notes.')
    return 1 if errors else 0

if __name__ == '__main__': sys.exit(main())
