# Dekrov Insights

A static research publishing platform for AI and technology investigations by Dekrov.

[Read the site](https://insights.dekrov.com/) · [Authoring guide](ARTICLE_AUTHORING_GUIDE.md) · [Editorial method](https://insights.dekrov.com/research-method/)

Plain HTML, CSS and JavaScript on GitHub Pages. No runtime framework, required backend or tracking. GitHub Pages’ built-in Jekyll build publishes short article URLs. The existing optional shared reactions service is preserved.

New articles start from `pages/_template/index.html`. Keep article sources under `pages/<slug>/index.html`, set their `permalink` in YAML front matter, and register the same public `path` once in `pages.json`; the homepage and sidebar update automatically. Read **[ARTICLE_AUTHORING_GUIDE.md](ARTICLE_AUTHORING_GUIDE.md)** for the exact HTML contract, sources, media rights, GitHub API publishing and deployment checks.

```sh
python scripts/validate_articles.py
python scripts/test_validation.py
# CI runs the real Jekyll build, then:
python scripts/validate_articles.py --site _site
python scripts/validate_articles.py --links --report /tmp/dekrov-links.json
```

Generated redirects preserve old `/pages/<slug>/` links, with query strings and fragments retained when JavaScript is available. Legacy articles remain readable and gain section navigation without changing their claims or reaction identities. New articles use the v2 contract. Reachability checks do not fact-check articles or establish image rights. GitHub's existing Pages deployment remains separate from the validation workflow.

[Telegram](https://t.me/Dekrov_channel_en) · [X](https://x.com/Dekrov_Dev) · [GitHub](https://github.com/DekrovDev)

© 2026 Dekrov
