import { access, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const siteDir = join(root, "site");
const docsDir = join(root, "docs");
const requiredFiles = [
  "site/index.html",
  "site/styles.css",
  "site/script.js",
  "site/data/summary_metrics.json",
  "site/assets/sales_funnel_conversion.png",
  "site/assets/rm_productivity.png",
  "site/assets/campaign_roi.png",
  "site/assets/product_demand.png",
  "docs/portfolio_case_study.md",
  "docs/website_copy.md",
  "docs/interview_talking_points.md",
  "docs/future_improvements.md",
];

const errors = [];

async function exists(relativePath) {
  try {
    await access(join(root, relativePath));
    return true;
  } catch {
    return false;
  }
}

for (const file of requiredFiles) {
  if (!(await exists(file))) {
    errors.push(`Missing required file: ${file}`);
  }
}

const html = await readFile(join(siteDir, "index.html"), "utf8");
const css = await readFile(join(siteDir, "styles.css"), "utf8");
const script = await readFile(join(siteDir, "script.js"), "utf8");
const summaryMetrics = JSON.parse(await readFile(join(siteDir, "data", "summary_metrics.json"), "utf8"));

for (const asset of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
  const value = asset[1];
  if (value.startsWith("http") || value.startsWith("#") || value.startsWith("mailto:")) {
    continue;
  }

  const target = value.endsWith(".md") ? join(root, value) : join(siteDir, value);
  if (!(await exists(target.replace(`${root}/`, "")))) {
    errors.push(`Broken local reference in site/index.html: ${value}`);
  }
}

for (const requiredText of [
  "deterministic synthetic data",
  "advisor coverage",
  "campaign roi",
  "priority scoring",
  "validation snapshot",
]) {
  if (!html.toLowerCase().includes(requiredText)) {
    errors.push(`Missing dashboard positioning phrase: ${requiredText}`);
  }
}

if (!css.includes("@media (max-width: 720px)")) {
  errors.push("Missing mobile responsive breakpoint in site/styles.css");
}

if (!script.includes("moduleData")) {
  errors.push("Missing module interaction data in site/script.js");
}

if (!script.includes("summary_metrics.json")) {
  errors.push("Static site does not load generated summary metrics JSON");
}

for (const key of [
  "expected_pipeline",
  "committed_capital",
  "conversion_rate",
  "advisor_count",
  "relationship_manager_count",
  "high_priority_advisor_count",
  "campaign_spend",
  "avg_days_to_close",
  "generated_from",
  "synthetic_data_disclaimer",
]) {
  if (!(key in summaryMetrics)) {
    errors.push(`summary_metrics.json missing key: ${key}`);
  }
}

for (const doc of [
  "portfolio_case_study.md",
  "website_copy.md",
  "interview_talking_points.md",
  "future_improvements.md",
]) {
  const body = await readFile(join(docsDir, doc), "utf8");
  if (!body.toLowerCase().includes("synthetic")) {
    errors.push(`${doc} must disclose synthetic/demo data`);
  }
}

if (errors.length) {
  console.error(errors.map((error) => `FAIL: ${error}`).join("\n"));
  process.exit(1);
}

console.log("Static site lint passed.");
