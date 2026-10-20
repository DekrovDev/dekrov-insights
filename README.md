# Dekrov Insights

A minimal, mobile-friendly archive of charts, AI benchmarks, and research by Dekrov.

## Pages

- Home: `https://dekrovdev.github.io/dekrov-insights/`
- Beam vs DeepSeek: `https://dekrovdev.github.io/dekrov-insights/beam-vs-deepseek/`

The Pages URLs start working once GitHub Pages is enabled.

**Enable GitHub Pages (once):** GitHub repository → Settings → Pages → Build and deployment → Deploy from a branch → Branch `main`, folder `/ (root)` → Save.

## How it works

The site is static HTML and CSS, with no build tools, dependencies, JavaScript, database, or paid hosting.

- `index.html`: home page and article list.
- `styles.css`: shared light theme, responsive cards and charts.
- `beam-vs-deepseek/index.html`: independent comparison page (a direct link opens it immediately).

To publish a new article, add `topic-name/index.html` and link it from the list on `index.html`. Use relative paths so both pages and links work under the `/dekrov-insights/` GitHub Pages project path.

Charts and benchmark data should include links to original sources and identify the evaluation version/date. Posts in X do not need a matching site page unless extra information is useful.

## Notes

This public repository should never contain account credentials, private project data, API keys, or unpublished personal information.

© 2026 Dekrov
