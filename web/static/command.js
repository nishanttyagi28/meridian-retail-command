/* Meridian Retail Command — dashboard */

const gbp = (n) =>
  new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 0,
  }).format(Number(n) || 0);

const gbpFine = (n) =>
  new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 2,
  }).format(Number(n) || 0);

const pct = (n) => `${Number(n || 0).toFixed(1)}%`;
const num = (n) => new Intl.NumberFormat("en-GB").format(Number(n) || 0);

const chartDefaults = {
  color: "#8b9daf",
  borderColor: "#2a3544",
  plugins: { legend: { labels: { color: "#8b9daf", boxWidth: 12 } } },
  scales: {
    x: {
      ticks: { color: "#8b9daf", maxRotation: 0 },
      grid: { color: "rgba(42,53,68,0.55)" },
    },
    y: {
      ticks: { color: "#8b9daf" },
      grid: { color: "rgba(42,53,68,0.55)" },
    },
  },
};

Chart.defaults.font.family = "Outfit";
Chart.defaults.color = "#8b9daf";

function kpiCard(label, value, sub) {
  return `<div class="kpi"><span class="label">${label}</span><span class="value">${value}</span>${
    sub ? `<span class="sub">${sub}</span>` : ""
  }</div>`;
}

function heatColor(v) {
  if (v == null || Number.isNaN(v)) return "transparent";
  const t = Math.max(0, Math.min(100, v)) / 100;
  const a = 0.12 + t * 0.72;
  return `rgba(14, 124, 123, ${a})`;
}

function wireTabs() {
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabs.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
      document.getElementById(`view-${btn.dataset.view}`).classList.add("active");
    });
  });
}

async function boot() {
  wireTabs();
  const err = document.getElementById("error");
  try {
    const res = await fetch("/api/dashboard");
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data = await res.json();
    renderAll(data);
  } catch (e) {
    err.hidden = false;
    err.textContent =
      "Could not load marts. Run scripts/build_warehouse.py so data/mart exists, then refresh.";
    console.error(e);
  }
}

function renderAll(data) {
  const k = data.kpi || {};
  document.getElementById("citation").textContent =
    (data.meta && data.meta.citation) ||
    "Chen, D. (2019). Online Retail II. UCI Machine Learning Repository.";

  document.getElementById("kpi-row").innerHTML = [
    kpiCard("Gross sales", gbp(k.gross_sales_gbp), `${num(k.invoices)} invoices`),
    kpiCard("Return rate", pct(k.return_rate_pct), gbp(k.returns_abs_value) + " returned"),
    kpiCard("AOV", gbpFine(k.aov), "positive sale invoices"),
    kpiCard("Customers", num(k.customers), "identified IDs"),
    kpiCard("SKUs", num(k.skus), `${num(k.countries)} countries`),
    kpiCard("Guest lines", pct(k.guest_checkout_pct), "no Customer ID"),
  ].join("");

  const uk = (data.country || []).find((c) => c.country === "United Kingdom");
  const ukShare = uk
    ? (100 * Number(uk.sales)) /
      (data.country || []).reduce((s, r) => s + Number(r.sales || 0), 0)
    : 0;
  const champs = (data.segments || []).find((s) => s.rfm_segment === "Champions");
  const ps = data.pareto_stats || {};

  document.getElementById("pulse-insights").innerHTML = `
    <li><strong>UK concentration:</strong> ~${ukShare.toFixed(0)}% of listed top-market sales sit in the home market — international is a thin but higher-AOV layer.</li>
    <li><strong>Returns:</strong> ${pct(k.return_rate_pct)} of gross sales value comes back — Ops pack flags the heaviest lines.</li>
    <li><strong>CRM:</strong> Champions are ${num(champs?.customers || 0)} customers driving ${gbp(champs?.revenue || 0)}.</li>
    <li><strong>Assortment:</strong> ${num(ps.skus_top80)} SKUs (${((100 * ps.skus_top80) / (ps.skus_total || 1)).toFixed(0)}%) cover ~80% of sales.</li>
    <li><strong>Identity gap:</strong> ${pct(k.guest_checkout_pct)} of lines lack Customer ID — RFM understates true loyalty.</li>
  `;

  renderMonthly(data.monthly || []);
  renderCountry(data.country || []);
  renderRfm(data.segments || [], data.at_risk_value || []);
  renderCohort(data.cohort_matrix || []);
  renderPareto(data.pareto_top || [], ps);
  renderReturns(data.returns_country || [], data.returns_top || []);
}

function renderMonthly(rows) {
  const labels = rows.map((r) => r.invoice_month);
  new Chart(document.getElementById("chart-monthly"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          type: "line",
          label: "Sales",
          data: rows.map((r) => Number(r.sales)),
          borderColor: "#1fb6a6",
          backgroundColor: "rgba(31,182,166,0.15)",
          tension: 0.25,
          yAxisID: "y",
          order: 0,
        },
        {
          label: "Returns",
          data: rows.map((r) => Number(r.returns_abs)),
          backgroundColor: "rgba(184,92,56,0.55)",
          yAxisID: "y",
          order: 1,
        },
      ],
    },
    options: {
      ...chartDefaults,
      responsive: true,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: "#8b9daf" } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${gbp(ctx.raw)}`,
          },
        },
      },
    },
  });
}

function renderCountry(rows) {
  const top = rows.slice(0, 12);
  new Chart(document.getElementById("chart-country"), {
    type: "bar",
    data: {
      labels: top.map((r) => r.country),
      datasets: [
        {
          label: "Sales GBP",
          data: top.map((r) => Number(r.sales)),
          backgroundColor: top.map((_, i) =>
            i === 0 ? "#0e7c7b" : "rgba(58,124,165,0.7)"
          ),
        },
      ],
    },
    options: {
      ...chartDefaults,
      indexAxis: "y",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => gbp(c.raw) } },
      },
    },
  });

  const tb = document.querySelector("#table-country tbody");
  tb.innerHTML = rows
    .slice(0, 15)
    .map(
      (r) => `<tr>
      <td>${r.country}</td>
      <td class="num">${gbp(r.sales)}</td>
      <td class="num">${pct(r.return_rate_pct)}</td>
      <td class="num">${gbpFine(r.aov)}</td>
      <td class="num">${num(r.customers)}</td>
    </tr>`
    )
    .join("");
}

function renderRfm(segments, atRisk) {
  new Chart(document.getElementById("chart-rfm"), {
    type: "doughnut",
    data: {
      labels: segments.map((s) => s.rfm_segment),
      datasets: [
        {
          data: segments.map((s) => s.revenue),
          backgroundColor: [
            "#0e7c7b",
            "#1c2541",
            "#d97706",
            "#3a7ca5",
            "#b85c38",
            "#5c6b73",
            "#2a9d8f",
          ],
          borderWidth: 0,
        },
      ],
    },
    options: {
      plugins: {
        legend: { position: "right", labels: { color: "#8b9daf", boxWidth: 10 } },
        tooltip: { callbacks: { label: (c) => gbp(c.raw) } },
      },
    },
  });

  document.querySelector("#table-rfm tbody").innerHTML = segments
    .map(
      (s) => `<tr>
      <td>${s.rfm_segment}</td>
      <td class="num">${num(s.customers)}</td>
      <td class="num">${gbp(s.revenue)}</td>
      <td class="num">${gbp(s.returns)}</td>
    </tr>`
    )
    .join("");

  document.querySelector("#table-atrisk tbody").innerHTML = atRisk
    .map(
      (r) => `<tr>
      <td>${r.customer_id}</td>
      <td>${r.rfm_segment}</td>
      <td>${String(r.last_purchase).slice(0, 10)}</td>
      <td class="num">${r.recency_days}d</td>
      <td class="num">${r.frequency}</td>
      <td class="num">${gbpFine(r.monetary)}</td>
    </tr>`
    )
    .join("");
}

function renderCohort(matrix) {
  const thead = document.querySelector("#table-cohort thead");
  const tbody = document.querySelector("#table-cohort tbody");
  thead.innerHTML = `<tr><th>Cohort</th><th>Size</th>${Array.from(
    { length: 13 },
    (_, i) => `<th>M${i}</th>`
  ).join("")}</tr>`;
  tbody.innerHTML = matrix
    .map((row) => {
      const cells = Array.from({ length: 13 }, (_, i) => {
        const v = row[`m${i}`];
        const show = v == null ? "—" : Number(v).toFixed(0);
        return `<td style="background:${heatColor(v)}">${show}</td>`;
      }).join("");
      return `<tr><td>${row.cohort_month}</td><td class="num">${num(
        row.cohort_customers
      )}</td>${cells}</tr>`;
    })
    .join("");
}

function renderPareto(rows, stats) {
  document.getElementById("pareto-kpis").innerHTML = [
    kpiCard("SKUs in top 80%", num(stats.skus_top80), `of ${num(stats.skus_total)} with sales`),
    kpiCard("Sales in top 80%", gbp(stats.sales_top80), "Pareto band"),
  ].join("");

  new Chart(document.getElementById("chart-pareto"), {
    type: "line",
    data: {
      labels: rows.map((_, i) => i + 1),
      datasets: [
        {
          label: "Cumulative %",
          data: rows.map((r) => Number(r.cumulative_pct)),
          borderColor: "#d97706",
          backgroundColor: "rgba(217,119,6,0.12)",
          fill: true,
          tension: 0.2,
          pointRadius: 0,
        },
      ],
    },
    options: {
      ...chartDefaults,
      plugins: {
        legend: { display: false },
        annotation: undefined,
      },
      scales: {
        ...chartDefaults.scales,
        y: {
          ...chartDefaults.scales.y,
          max: 100,
          title: { display: true, text: "% of sales", color: "#8b9daf" },
        },
        x: {
          ...chartDefaults.scales.x,
          title: { display: true, text: "SKU rank", color: "#8b9daf" },
        },
      },
    },
  });

  document.querySelector("#table-pareto tbody").innerHTML = rows
    .slice(0, 25)
    .map(
      (r) => `<tr>
      <td>${r.stock_code}</td>
      <td title="${r.description}">${String(r.description || "").slice(0, 36)}</td>
      <td class="num">${gbp(r.sales)}</td>
      <td class="num">${Number(r.cumulative_pct).toFixed(1)}%</td>
    </tr>`
    )
    .join("");
}

function renderReturns(byCountry, top) {
  new Chart(document.getElementById("chart-returns"), {
    type: "bar",
    data: {
      labels: byCountry.map((r) => r.country),
      datasets: [
        {
          label: "Return value",
          data: byCountry.map((r) => r.return_value),
          backgroundColor: "rgba(184,92,56,0.7)",
        },
      ],
    },
    options: {
      ...chartDefaults,
      indexAxis: "y",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => gbp(c.raw) } },
      },
    },
  });

  document.querySelector("#table-returns tbody").innerHTML = top
    .slice(0, 20)
    .map(
      (r) => `<tr>
      <td>${String(r.invoice_date || "").slice(0, 10)}</td>
      <td>${r.stock_code}</td>
      <td>${r.country}</td>
      <td class="num">${r.qty}</td>
      <td class="num">${gbpFine(r.return_value)}</td>
    </tr>`
    )
    .join("");
}

boot();
