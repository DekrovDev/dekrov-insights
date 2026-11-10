#!/usr/bin/env python3
"""Contract regression tests: invalid publications must be detected before a push."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from validate_articles import ROOT, validate, public_url

class PublicationContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ('pages', 'pages.json', 'index.html', 'site.js', 'article.js', 'styles.css', 'theme.js', 'article-likes.js', '_config.yml', '_layouts', 'redirect.js'):
            src, dst = ROOT / name, self.root / name
            if src.is_dir(): shutil.copytree(src, dst)
            else: shutil.copy2(src, dst)
        self.article = self.root / 'pages/research-method/index.html'
    def tearDown(self): self.tmp.cleanup()
    def edit(self, old, new): self.article.write_text(self.article.read_text().replace(old, new))
    def assert_error(self, fragment):
        errors = validate(self.root)[0]
        self.assertTrue(any(fragment in e for e in errors), errors)
    def test_existing_and_v2_articles(self): self.assertEqual(validate(self.root)[0], [])
    def test_nested_paragraph(self):
        self.edit('<p class="intro">', '<p><p class="intro">')
        self.assert_error('block <p> inside <p>')
    def test_heading_inside_paragraph(self):
        self.edit('<p class="intro">', '<p><h3 id="invalid-heading">Heading</h3></p><p class="intro">')
        self.assert_error('block <h3> inside <p>')
    def test_stray_paragraph_close(self):
        self.edit('<p class="intro">', '</p><p class="intro">')
        self.assert_error('closing </p> without an open paragraph')
    def test_duplicate_catalog_slug(self):
        p = self.root / 'pages.json'; entries = json.loads(p.read_text()); entries.append(entries[1]); p.write_text(json.dumps(entries))
        self.assert_error('duplicate slug')
    def test_missing_catalog_page(self):
        p = self.root / 'pages.json'; entries = json.loads(p.read_text()); entries.append({'slug': 'missing', 'title': 'Missing', 'meta': 'Test'}); p.write_text(json.dumps(entries))
        self.assert_error('missing pages/missing')
    def test_duplicate_reactions(self):
        self.edit('<!-- ARTICLE CONTENT START -->', '<section class="article-engagement"></section>')
        self.assert_error('expected one reactions block')
    def test_broken_citation(self):
        self.edit('href="#source-1"', 'href="#source-99"'); self.assert_error('invalid citation target')
    def test_missing_local_image(self):
        (self.root / 'pages/research-method/assets/claim-only.svg').unlink(); self.assert_error('missing local target')
    def test_missing_rights(self):
        self.edit('data-rights="Original work by Dekrov; reproduced by its publisher"', ''); self.assert_error('missing rights')
    def test_unfilled_template(self):
        self.edit('Evidence before confidence', '{{TITLE}}'); self.assert_error('unfilled template tokens')
    def test_simple_explanation_anchor(self):
        self.edit('id="explained-simply"', 'id="missing-simple"'); self.assert_error('missing required anchor #explained-simply')
    def test_source_type(self):
        self.edit('data-source-type="official"', 'data-source-type="verified"'); self.assert_error('invalid source classification')
    def test_canonical_slug(self):
        self.edit('rel="canonical" href="https://insights.dekrov.com/research-method/"', 'rel="canonical" href="https://example.org/"'); self.assert_error('incorrect canonical')
    def catalog_edit(self, operation):
        path = self.root / 'pages.json'
        pages = json.loads(path.read_text())
        operation(pages)
        path.write_text(json.dumps(pages))
    def test_duplicate_public_path(self):
        self.catalog_edit(lambda pages: pages[1].update(path=pages[2]['path']))
        self.assert_error('duplicate public path')
    def test_reserved_public_path(self):
        self.catalog_edit(lambda pages: pages[1].update(path='/pages/'))
        self.assert_error('reserved or existing root path')
    def test_root_directory_collision(self):
        (self.root / 'occupied').mkdir()
        self.catalog_edit(lambda pages: pages[1].update(path='/occupied/'))
        self.assert_error('reserved or existing root path')
    def test_unsafe_public_path(self):
        self.catalog_edit(lambda pages: pages[1].update(path='https://example.org/'))
        self.assert_error('path must be a short root-relative')
    def test_permalink_must_match_catalog(self):
        self.edit('permalink: /research-method/', 'permalink: /wrong/')
        self.assert_error('permalink must match catalog')
    def test_legacy_alias_required(self):
        self.edit('  - /pages/research-method/index.html', '')
        self.assert_error('preserve both legacy article URLs')
    def test_alias_cannot_shadow_article(self):
        self.edit('redirect_from:', 'redirect_from:\n  - /paperclip/')
        self.assert_error('redirect alias collision')
    def test_alias_index_file_cannot_shadow_article(self):
        self.edit('redirect_from:', 'redirect_from:\n  - /paperclip/index.html')
        self.assert_error('redirect alias collision')
    def test_alias_cannot_shadow_static_file(self):
        (self.root / 'manual').mkdir()
        (self.root / 'manual/index.html').write_text('<p>Existing static page</p>')
        self.edit('redirect_from:', 'redirect_from:\n  - /manual/')
        self.assert_error('redirect alias collision')
    def test_unsupported_yaml_fails_closed(self):
        self.edit('layout: null', 'layout: !!python/object:invalid')
        self.assert_error('article layout must be null')
    def test_relative_assets_resolve_at_public_url(self):
        self.edit('src="/pages/research-method/assets/claim-only.svg"', 'src="./assets/claim-only.svg"')
        self.assert_error('missing local target')
    def test_source_path_and_public_url_are_independent(self):
        self.edit('<!-- ARTICLE CONTENT START -->', '<!-- ARTICLE CONTENT START --><p><a href="/paperclip/#overview">Related article</a></p>')
        self.assertEqual(validate(self.root)[0], [])
    def test_no_front_matter_rejected(self):
        text = self.article.read_text()
        self.article.write_text(text.split('---\n', 2)[2])
        self.assert_error('permalink must match catalog')
    def test_link_probe_scope(self):
        self.assertFalse(public_url('http://example.org/'))
        self.assertFalse(public_url('https://127.0.0.1/'))
        self.assertFalse(public_url('https://user:password@example.org/'))
        self.assertTrue(public_url('https://github.com/DekrovDev/dekrov-insights'))

if __name__ == '__main__': unittest.main()
