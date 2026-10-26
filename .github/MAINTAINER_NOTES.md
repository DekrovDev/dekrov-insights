# Dekrov Insights — Maintainer Notes

> Development workflow reference. This file is still publicly accessible in the source repository; it is simply not shown as the repository landing-page README.
## Creating a new research article

Use `pages/_template/index.html` as the starting point. The template already includes the shared reaction button and its script.

1. Copy the template to `pages/<unique-slug>/index.html`. Pick a stable lowercase hyphenated slug; do not reuse slugs across articles.
2. In the new HTML file, fill in the page title, description, Open Graph metadata, canonical URL, and `<body data-page="<unique-slug>" data-root="../../">`.
3. Write the article between the `ARTICLE CONTENT START` and `ARTICLE CONTENT END` comments. **Keep the reaction block and the `article-likes.js` script.**
4. Register the slug, title, and meta label in `pages.json` so the navigation includes the page.
5. Add a homepage article row to `index.html`, with a link to `./pages/<unique-slug>/`.

### Reactions / likes

The shared button at the end of the template uses `article-likes.js` and the site-wide rules in `styles.css`. The counter ID is derived automatically from `body[data-page]`: no copy/pasting API URLs, special account, API keys or database setup for each new article.

Counts are publicly stored through the free Abacus counter service (`abacus.jasoncameron.dev`) and shared across visitors. A browser `localStorage` marker prevents accidental repeat votes in that browser; **this is not anti-fraud protection** or a reversible like. A service outage disables voting with a clear message but doesn't affect the article itself.

Do not change a published article's `data-page` slug casually: that would create a different counter and leave the previous count behind. Do not insert a second reaction block on new pages.

