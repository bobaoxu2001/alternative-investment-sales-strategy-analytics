const moduleData = {
  funnel: {
    question: "Where does the pipeline drop off?",
    output: "sales_funnel_summary.csv",
    metric: "10.87% overall conversion rate",
    why: "Helps sales leadership focus on the stages and segments with the largest conversion gaps.",
  },
  rm: {
    question: "Which RMs convert engagement into committed capital?",
    output: "rm_productivity_summary.csv",
    metric: "3 coaching-opportunity RMs",
    why: "Separates activity volume from actual conversion and follow-up discipline.",
  },
  product: {
    question: "Which products and asset classes generate demand and capital?",
    output: "product_demand_summary.csv",
    metric: "Private Equity and Infrastructure show stronger modeled conversion.",
    why: "Helps align RM time and product focus with higher-quality demand.",
  },
  campaign: {
    question: "Which campaigns show strongest modeled efficiency?",
    output: "campaign_roi_summary.csv",
    metric: "Email campaigns show highest modeled committed-capital-to-cost multiple.",
    why: "Supports campaign allocation decisions while keeping synthetic ROI magnitudes directional.",
  },
  advisor: {
    question: "Which advisors should RMs prioritize next?",
    output: "advisor_priority_scores.csv",
    metric: "132 high-priority advisors",
    why: "Turns engagement, AUM, product fit, conversion probability, and recency into next-best-action guidance.",
  },
};

const menuToggle = document.querySelector(".menu-toggle");
const primaryNav = document.querySelector("#primary-nav");

function setMenuOpen(isOpen) {
  if (!menuToggle || !primaryNav) return;
  menuToggle.setAttribute("aria-expanded", String(isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
  primaryNav.classList.toggle("open", isOpen);
}

if (menuToggle && primaryNav) {
  menuToggle.addEventListener("click", () => {
    setMenuOpen(menuToggle.getAttribute("aria-expanded") !== "true");
  });

  primaryNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setMenuOpen(false));
  });
}

function showMetricsFallbackNotice() {
  const fallbackNote = document.querySelector("#metrics-fallback-note");
  if (fallbackNote) {
    fallbackNote.hidden = false;
  }
}

async function hydrateSummaryMetrics() {
  try {
    const response = await fetch("data/summary_metrics.json", { cache: "no-store" });
    if (!response.ok) {
      showMetricsFallbackNotice();
      return;
    }

    const summary = await response.json();

    document.querySelectorAll("[data-summary-metric]").forEach((node) => {
      const key = node.dataset.summaryMetric;
      if (summary[key]?.display) {
        node.textContent = summary[key].display;
        node.setAttribute("title", summary[key].source || "Generated summary metric");
        node.setAttribute("aria-label", `${node.textContent}. ${summary[key].source || "Generated summary metric"}`);
      }
    });

    const sourceNote = document.querySelector("#summary-source-note");
    if (sourceNote && summary.synthetic_data_disclaimer) {
      sourceNote.textContent = `${summary.synthetic_data_disclaimer} Source: site/data/summary_metrics.json.`;
    }

    const snapshot = summary.validation_snapshot || {};
    document.querySelectorAll("[data-validation-metric]").forEach((node) => {
      const key = node.dataset.validationMetric;
      if (snapshot[key] !== undefined) {
        node.textContent = snapshot[key].toLocaleString();
      }
    });

    const validationDisclaimer = document.querySelector("#validation-disclaimer");
    if (validationDisclaimer && summary.synthetic_data_disclaimer) {
      validationDisclaimer.textContent = `Synthetic data disclosure: ${summary.synthetic_data_disclaimer}`;
    }

    const tierPreview = document.querySelector("#priority-tier-preview");
    if (tierPreview && Array.isArray(summary.priority_tier_preview)) {
      tierPreview.innerHTML = summary.priority_tier_preview
        .map(
          (row) => `<tr><td>${row.tier}</td><td>${row.advisor_count.toLocaleString()}</td></tr>`
        )
        .join("");
    }
  } catch (error) {
    showMetricsFallbackNotice();
    console.warn("Using static KPI fallbacks because summary metrics could not load.", error);
  }
}

hydrateSummaryMetrics();

const moduleTabs = document.querySelectorAll(".module-tab");
const moduleQuestion = document.querySelector("#module-question");
const moduleOutput = document.querySelector("#module-output");
const moduleMetric = document.querySelector("#module-metric");
const moduleWhy = document.querySelector("#module-why");

moduleTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    const selected = tab.dataset.module;
    const detail = moduleData[selected];
    if (!detail) return;

    moduleTabs.forEach((item) => {
      const isActive = item === tab;
      item.classList.toggle("active", isActive);
      item.setAttribute("aria-pressed", String(isActive));
    });

    moduleQuestion.textContent = detail.question;
    moduleOutput.textContent = detail.output;
    moduleMetric.textContent = detail.metric;
    moduleWhy.textContent = detail.why;
  });
});

const modal = document.querySelector("#chart-modal");
const modalImage = document.querySelector("#modal-image");
const modalTitle = document.querySelector("#modal-title");
const modalClose = document.querySelector(".modal-close");
let activeChartTrigger = null;
let lastFocusedElement = null;

function openModal(src, title, trigger) {
  lastFocusedElement = document.activeElement;
  activeChartTrigger = trigger || document.querySelector(`.chart-trigger[data-src="${src}"]`);
  if (activeChartTrigger) {
    activeChartTrigger.setAttribute("aria-expanded", "true");
  }
  modalImage.src = src;
  modalImage.alt = `${title} enlarged chart`;
  modalTitle.textContent = title;
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  modalClose.focus();
}

function closeModal() {
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  modalImage.src = "";
  document.querySelectorAll(".chart-trigger[aria-expanded='true']").forEach((trigger) => {
    trigger.setAttribute("aria-expanded", "false");
  });
  if (activeChartTrigger) {
    activeChartTrigger.setAttribute("aria-expanded", "false");
  }
  if (lastFocusedElement) {
    lastFocusedElement.focus();
  }
  activeChartTrigger = null;
}

document.querySelectorAll(".chart-trigger").forEach((trigger) => {
  trigger.addEventListener("click", () => {
    openModal(trigger.dataset.src, trigger.dataset.title, trigger);
  });
});

modalClose.addEventListener("click", closeModal);
modal.addEventListener("click", (event) => {
  if (event.target === modal) {
    closeModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && modal.classList.contains("open")) {
    closeModal();
  } else if (event.key === "Escape" && menuToggle?.getAttribute("aria-expanded") === "true") {
    setMenuOpen(false);
    menuToggle.focus();
  }
});

const navLinks = Array.from(document.querySelectorAll(".nav-link"));
const observedSections = navLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;

      navLinks.forEach((link) => {
        const isActive = link.getAttribute("href") === `#${visible.target.id}`;
        link.classList.toggle("active", isActive);
      });
    },
    {
      rootMargin: "-25% 0px -55% 0px",
      threshold: [0.1, 0.25, 0.5],
    }
  );

  observedSections.forEach((section) => observer.observe(section));
}
