# Dekrov Insights

A static research publishing platform for AI and technology investigations by Dekrov.

[Read the site](https://dekrovdev.github.io/dekrov-insights/) · [Authoring guide](ARTICLE_AUTHORING_GUIDE.md) · [Editorial method](https://dekrovdev.github.io/dekrov-insights/pages/research-method/)

Plain HTML, CSS and JavaScript on GitHub Pages. No runtime framework, build step, required backend or tracking. The existing optional shared reactions service is preserved.

New articles start from `pages/_template/index.html`. Register each article once in `pages.json`; the homepage and sidebar update automatically. Read **[ARTICLE_AUTHORING_GUIDE.md](ARTICLE_AUTHORING_GUIDE.md)** for the exact HTML contract, sources, media rights, GitHub API publishing and deployment checks.

```sh
python scripts/validate_articles.py
python scripts/test_validation.py
python scripts/validate_articles.py --links --report /tmp/dekrov-links.json
```

Legacy articles remain readable and gain section navigation without changing their claims or reaction identities. New articles use the v2 contract. Reachability checks do not fact-check articles or establish image rights. GitHub's existing Pages deployment remains separate from the validation workflow.

[Telegram](https://t.me/Dekrov_channel_en) · [X](https://x.com/Dekrov_Dev) · [GitHub](https://github.com/DekrovDev)

© 2026 Dekrov
