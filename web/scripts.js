
async function loadJSON(url) {
  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return await r.json();
}

function fmtPct(x) { return (x*100).toFixed(1) + "%"; }

function renderMeta(selection) {
  const div = document.getElementById("meta");
  const sel = selection || {};
  const changed = (sel.changed_files||[]).map(f => `<code>${f}</code>`).join(", ") || "<em>(none)</em>";
  div.innerHTML = `
    <p><strong>Base:</strong> ${sel.base || "-"} &nbsp; <strong>Head:</strong> ${sel.head || "-"}</p>
    <p><strong>Budget:</strong> ${sel.budget_tests||"-"} tests, ${sel.budget_time_seconds||"-"} seconds</p>
    <p><strong>Changed files:</strong> ${changed}</p>
    <p><strong>Selected ${ (sel.selected||[]).length } test(s)</strong></p>
  `;
}

function renderExplanations(explanations, selection) {
  const container = document.getElementById("expl");
  const entries = Object.entries(explanations||{});
  if (!entries.length) {
    container.textContent = "No explanations yet — run a selection.";
    return;
  }
  entries.sort((a,b) => (b[1].score||0) - (a[1].score||0));
  const rows = entries.map(([nodeid, e]) => `
    <tr>
      <td><code>${nodeid}</code></td>
      <td>${e.affected ? '<span class="badge yes">affected</span>' : '<span class="badge no">not affected</span>'}</td>
      <td>${fmtPct(e.fail_rate||0)}</td>
      <td>${fmtPct(e.flaky_rate||0)}</td>
      <td>${(e.runtime_norm||0).toFixed(2)}</td>
      <td>${(e.score||0).toFixed(3)}</td>
      <td>${e.included ? '<span class="badge yes">included</span>' : '<span class="badge no">excluded</span>'}</td>
      <td>${e.reason || ""}</td>
    </tr>
  `).join("");

  container.innerHTML = `
    <table class="table">
      <thead>
        <tr>
          <th>Test</th>
          <th>Affected?</th>
          <th>Fail rate</th>
          <th>Flaky rate</th>
          <th>Runtime norm</th>
          <th>Score</th>
          <th>Decision</th>
          <th>Reason</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderHistory(hist) {
  const container = document.getElementById("history");
  const runs = (hist.runs||[]);
  if (!runs.length) { container.textContent = "No history yet."; return; }
  const rows = runs.map(r => `
    <tr>
      <td>${new Date((r.time||0)*1000).toLocaleString()}</td>
      <td>${r.project}</td>
      <td>${r.count}</td>
      <td>${r.failed}</td>
    </tr>
  `).join("");
  container.innerHTML = `
    <table class="table">
      <thead><tr><th>Time</th><th>Project</th><th># Tests</th><th># Failed</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

async function render() {
  try {
    const data = await loadJSON("./data/latest.json");
    renderMeta(data.selection || {});
    renderExplanations(data.explanations || {}, data.selection || {});
    renderHistory(data.history || {});
  } catch (e) {
    document.getElementById("meta").textContent = "Run the CLI to generate web/data/latest.json";
  }
}

document.getElementById("reload").addEventListener("click", render);
render();
