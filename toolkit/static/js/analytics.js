(function () {
  let tokenChart = null;
  let cacheChart = null;

  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function destroyCharts() {
    if (tokenChart) tokenChart.destroy();
    if (cacheChart) cacheChart.destroy();
  }

  function renderCharts() {
    destroyCharts();

    Chart.defaults.color = css("--text");
    Chart.defaults.borderColor = css("--border");
    Chart.defaults.font.family = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

    const calls = window.HERMES_CALLS || [];
    const labels = calls.map((c, i) => "Request " + (i + 1));

    const gridColor = css("--border");
    const accent = css("--accent");
    const good = css("--good");
    const warn = css("--warn");

    tokenChart = new Chart(document.getElementById("tokensChart"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Input Tokens",
            data: calls.map(c => c.in),
            borderColor: accent,
            backgroundColor: "transparent",
            tension: .35,
            pointRadius: 2,
            borderWidth: 2
          },
          {
            label: "Output Tokens",
            data: calls.map(c => c.out),
            borderColor: good,
            backgroundColor: "transparent",
            tension: .35,
            pointRadius: 2,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: { display: true, text: "Token Usage" },
          legend: { labels: { boxWidth: 12, boxHeight: 12 } }
        },
        scales: {
          x: { ticks: { color: css("--muted") }, grid: { color: gridColor } },
          y: { ticks: { color: css("--muted") }, grid: { color: gridColor } }
        }
      }
    });

    cacheChart = new Chart(document.getElementById("cacheChart"), {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Cache Hit %",
            data: calls.map(c => c.pct),
            borderColor: warn,
            backgroundColor: "transparent",
            tension: .35,
            pointRadius: 2,
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: { display: true, text: "Cache Hit Rate" },
          legend: { labels: { boxWidth: 12, boxHeight: 12 } }
        },
        scales: {
          x: { ticks: { color: css("--muted") }, grid: { color: gridColor } },
          y: { min: 0, max: 100, ticks: { color: css("--muted") }, grid: { color: gridColor } }
        }
      }
    });
  }

  window.addEventListener("DOMContentLoaded", renderCharts);
  window.addEventListener("hermes-theme-changed", renderCharts);
})();
