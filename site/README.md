# Project Showcase Website

This folder contains a lightweight static website that presents the analytics project as a recruiter-friendly portfolio case study.

## How to run locally

Open `site/index.html` directly in a browser.

From the repository root on macOS:

```bash
open site/index.html
```

You can also serve it with any static file server if preferred.

## How to build

No build step is required. The site uses plain HTML and CSS.

## How to deploy

### Vercel

1. Import the GitHub repository into Vercel.
2. Set the project root or output directory to `site`.
3. Use no build command.
4. Deploy as a static site.

### GitHub Pages

1. In repository settings, enable GitHub Pages.
2. Use a GitHub Pages workflow or configure the source to publish the `site` folder.
3. The entry point is `site/index.html`.

## Chart assets

The chart PNGs in `site/assets/` are copied from the main analytics project:

- `reports/charts/sales_funnel_conversion.png`
- `reports/charts/rm_productivity.png`
- `reports/charts/campaign_roi.png`
- `reports/charts/product_demand.png`

## Relationship to the main project

This website is a companion to the main analytics repository. The full project includes synthetic data generation, SQL analysis, Python analytics, dashboard-ready outputs, executive reporting, documentation, and validation checks.

All data shown on the site is synthetic and is used to demonstrate the analytical framework.
