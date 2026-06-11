"""Render a static per-subject verification dashboard for the load decoder.

The dashboard is intentionally data-driven: it consumes the prediction table emitted by
``run_control_models.py`` and the subject statistics emitted by
``summarize_subject_statistics.py``. At this stage the mechanism layer has not been run,
so the verdicts are decoding-only and explicitly marked as mechanism pending.

Usage:
    .\\venv\\Scripts\\python.exe scripts\\render_verification_dashboard.py \\
        --predictions outputs\\controls\\control_predictions_logistic_all_all.csv \\
        --subject-statistics outputs\\statistics\\subject_statistics_logistic_all_all.csv \\
        --summary outputs\\statistics\\summary_logistic_all_all.json \\
        --out-dir outputs\\dashboard
"""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path

import pandas as pd


def _derive_tag(path: str) -> str:
    """Derive the run tag from a control_predictions_<tag>.csv filename."""
    name = Path(path).stem
    prefix = "control_predictions_"
    return name[len(prefix):] if name.startswith(prefix) else name


def _fmt(value: float) -> str:
    """Format a floating metric for the dashboard."""
    return f"{float(value):.3f}"


def _trial_strip(rows: pd.DataFrame) -> str:
    """Render compact trial-level correctness cells for one subject."""
    cells = []
    for row in rows.itertuples(index=False):
        correct = int(row.signal_pred) == int(row.load_binary)
        control_correct = (
            int(row.behavioral_pred) == int(row.load_binary)
            or int(row.timing_pred) == int(row.load_binary)
        )
        cls = "hit" if correct else "miss"
        ctrl = "control-hit" if control_correct else "control-miss"
        title = (
            f"{row.trial_id}: true={row.load_binary}, signal={row.signal_pred}, "
            f"behavioral={row.behavioral_pred}, timing={row.timing_pred}, "
            f"set_size={row.set_size}"
        )
        cells.append(f'<span class="trial {cls} {ctrl}" title="{html.escape(title)}"></span>')
    return "\n".join(cells)


def _subject_section(subject_id: str, pred: pd.DataFrame, stats_row: pd.Series) -> str:
    """Render one subject's decoding/control panel."""
    rows = pred[pred["subject_id"] == subject_id].sort_values(["session_id", "trial_id"])
    verdict = "weaken" if float(stats_row["improvement"]) > 0.0 else "contradict"
    verdict_text = (
        "beats strongest control; mechanism pending"
        if verdict == "weaken"
        else "does not beat strongest control"
    )
    table_rows = []
    for row in rows.head(12).itertuples(index=False):
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row.trial_id))}</td>"
            f"<td>{int(row.set_size)}</td>"
            f"<td>{int(row.load_binary)}</td>"
            f"<td>{int(row.signal_pred)}</td>"
            f"<td>{int(row.behavioral_pred)}</td>"
            f"<td>{int(row.timing_pred)}</td>"
            "</tr>"
        )
    return f"""
    <section class="subject-panel {verdict}">
      <div class="subject-head">
        <h2>{html.escape(subject_id)}</h2>
        <span class="verdict">{html.escape(verdict_text)}</span>
      </div>
      <div class="metrics">
        <div><span>Signal BA</span><strong>{_fmt(stats_row['signal_ba'])}</strong></div>
        <div><span>Strongest Control</span><strong>{html.escape(str(stats_row['strongest_control']))}</strong></div>
        <div><span>Control BA</span><strong>{_fmt(stats_row['strongest_control_ba'])}</strong></div>
        <div><span>Improvement</span><strong>{_fmt(stats_row['improvement'])}</strong></div>
      </div>
      <div class="strip" aria-label="Trial-level signal correctness for {html.escape(subject_id)}">
        {_trial_strip(rows)}
      </div>
      <table>
        <thead>
          <tr><th>Trial</th><th>Set Size</th><th>True</th><th>Signal</th><th>Behavior</th><th>Timing</th></tr>
        </thead>
        <tbody>
          {''.join(table_rows)}
        </tbody>
      </table>
      <p class="mechanism">Mechanism layer: not run yet for this dashboard render.</p>
    </section>
    """


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--predictions", required=True, help="control_predictions_<tag>.csv.")
    ap.add_argument("--subject-statistics", required=True, help="subject_statistics_<tag>.csv.")
    ap.add_argument("--summary", required=True, help="summary_<tag>.json.")
    ap.add_argument("--out-dir", default="outputs/dashboard", help="Output directory.")
    ap.add_argument("--tag", default=None, help="Optional output tag.")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    tag = args.tag or _derive_tag(args.predictions)
    pred = pd.read_csv(args.predictions)
    stats = pd.read_csv(args.subject_statistics).sort_values("subject_id")
    with open(args.summary, encoding="utf-8") as fh:
        summary = json.load(fh)

    required_pred = {
        "subject_id",
        "session_id",
        "trial_id",
        "set_size",
        "load_binary",
        "signal_pred",
        "behavioral_pred",
        "timing_pred",
    }
    missing = sorted(required_pred - set(pred.columns))
    if missing:
        raise ValueError(f"Prediction file missing required columns: {missing}")

    stats_rows = {row["subject_id"]: row for _, row in stats.iterrows()}
    sections = [
        _subject_section(subject_id, pred, stats_rows[subject_id])
        for subject_id in stats["subject_id"].tolist()
    ]
    summary_rows = []
    for row in stats.itertuples(index=False):
        summary_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row.subject_id))}</td>"
            f"<td>{_fmt(row.signal_ba)}</td>"
            f"<td>{html.escape(str(row.strongest_control))}</td>"
            f"<td>{_fmt(row.strongest_control_ba)}</td>"
            f"<td>{_fmt(row.improvement)}</td>"
            "</tr>"
        )

    success_text = "met" if summary["headline_success"] else "not met"
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EEG to LFP Verification Dashboard - {html.escape(tag)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1c232b;
      --muted: #667381;
      --line: #d8dee6;
      --panel: #ffffff;
      --bg: #f6f7f9;
      --good: #1e8a5a;
      --bad: #b13f3f;
      --warn: #9a6a18;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.45;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    h1, h2 {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: 28px; }}
    h2 {{ font-size: 20px; }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    .summary-grid, .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
    }}
    .summary-grid div, .metrics div {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      min-width: 0;
    }}
    span {{ display: block; color: var(--muted); font-size: 12px; }}
    strong {{ display: block; margin-top: 4px; font-size: 20px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      background: #fff;
      border: 1px solid var(--line);
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 7px 8px;
      text-align: left;
      font-size: 13px;
      white-space: nowrap;
    }}
    th {{ color: var(--muted); font-weight: 700; }}
    .subject-panel {{
      margin-top: 22px;
      padding: 18px;
      border: 1px solid var(--line);
      border-left: 5px solid var(--warn);
      border-radius: 8px;
      background: #fff;
    }}
    .subject-panel.contradict {{ border-left-color: var(--bad); }}
    .subject-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }}
    .verdict {{
      color: var(--ink);
      font-size: 13px;
      font-weight: 700;
      text-align: right;
    }}
    .strip {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(8px, 1fr));
      gap: 2px;
      margin: 14px 0;
      min-height: 28px;
    }}
    .trial {{
      display: block;
      min-width: 8px;
      height: 12px;
      border-radius: 2px;
      border-bottom: 3px solid transparent;
    }}
    .trial.hit {{ background: rgba(30, 138, 90, 0.88); }}
    .trial.miss {{ background: rgba(177, 63, 63, 0.72); }}
    .trial.control-hit {{ border-bottom-color: rgba(28, 35, 43, 0.35); }}
    .mechanism {{
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 700px) {{
      header {{ padding: 20px; }}
      main {{ padding: 16px; }}
      .subject-head {{ align-items: flex-start; flex-direction: column; }}
      th, td {{ font-size: 12px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>EEG to LFP Verification Dashboard</h1>
    <p>{html.escape(tag)} - decoding controls and subject-level statistics</p>
  </header>
  <main>
    <section class="summary-grid">
      <div><span>Headline Criteria</span><strong>{html.escape(success_text)}</strong></div>
      <div><span>Mean Signal BA</span><strong>{_fmt(summary['mean_signal_ba'])}</strong></div>
      <div><span>Mean Strongest Control BA</span><strong>{_fmt(summary['mean_strongest_control_ba'])}</strong></div>
      <div><span>Mean Improvement</span><strong>{_fmt(summary['mean_improvement'])}</strong></div>
      <div><span>Subjects Above Control</span><strong>{summary['subjects_above_strongest_control']}/{summary['n_subjects']}</strong></div>
      <div><span>Min Leave-One-Out Mean</span><strong>{_fmt(summary['min_leave_one_out_mean_improvement'])}</strong></div>
    </section>
    <table>
      <thead>
        <tr><th>Subject</th><th>Signal BA</th><th>Strongest Control</th><th>Control BA</th><th>Improvement</th></tr>
      </thead>
      <tbody>
        {''.join(summary_rows)}
      </tbody>
    </table>
    {''.join(sections)}
  </main>
</body>
</html>
"""

    out_path = os.path.join(args.out_dir, f"verification_dashboard_{tag}.html")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html_doc)
    print(f"Rendered dashboard:\n  {out_path}")


if __name__ == "__main__":
    main()
