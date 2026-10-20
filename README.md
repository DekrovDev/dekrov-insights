# Dekrov Insights

A minimal, mobile-friendly archive of charts, AI benchmarks, and research by Dekrov.

## Pages

- Home: `https://dekrovdev.github.io/dekrov-insights/`
- Beam vs DeepSeek: `https://dekrovdev.github.io/dekrov-insights/beam-vs-deepseek/`

GitHub Pages serves the site from the `main` branch, `/ (root)` folder.

## How it works

The site is static HTML and CSS with small shared scripts. There are no build tools, package dependencies, database, or paid hosting.

- `index.html`: welcome page, a short explanation of the site, and the article list.
- `styles.css`: shared light and dark themes, responsive layout, sidebar, and charts.
- `theme.js`: reads the saved theme (or the system preference), switches it, and stores the choice in `localStorage`.
- `pages.json`: the single list of pages used to build the sidebar.
- `site.js`: fetches `pages.json` and renders the sidebar on every page.
- `_template/index.html`: bare page shell for a new article (header, sidebar, footer, empty article body).
- `NEW_PAGE.md`: step-by-step instructions and a ready-to-use ChatGPT prompt.
- `beam-vs-deepseek/index.html`: independent comparison page (a direct link opens it immediately).

To publish a new article, copy `_template/index.html` to `<slug>/index.html`, fill the title/meta tags, set `data-page` to the slug, add the article content using `beam-vs-deepseek/index.html` as the reference, add the page to `pages.json`, and add a row to the `Pages` list in `index.html`. See `NEW_PAGE.md` for the exact steps. Existing articles do not need their sidebars edited: `site.js` builds the navigation from `pages.json`.

Use relative paths so both pages and links work under the `/dekrov-insights/` GitHub Pages project path. The sidebar is generated in the browser from `pages.json` (fetched with `cache: "no-store"`), but the site itself remains fully static and works on GitHub Pages without a backend or build step. The `_template` folder starts with an underscore, so GitHub Pages' Jekyll build does not publish it.

Charts and benchmark data should include links to original sources and identify the evaluation version/date. Posts in X do not need a matching site page unless extra information is useful.

## Notes

This public repository should never contain account credentials, private project data, API keys, or unpublished personal information.

© 2026 Dekrov
