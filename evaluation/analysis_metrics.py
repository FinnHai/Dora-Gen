"""
Kleine Auswertung für die Thesis-Evaluations-CSV aus dem Frontend.

Input (CSV aus `thesis_frontend.py` Export):
    inject_id,mode,rating,reason,timestamp
    mode ∈ {"rack"/"baseline rag/llm", "agent"/"agenten-logik"} je nach Export
    rating ∈ {"consistent", "hallucination"}

Nutzung:
    python analysis_metrics.py --file path/to/export.csv
    # optional: --chart schreibt eine einfache Plotly-HTML-Datei
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalisiere Spalten, falls leicht anders benannt
    df.columns = [c.strip().lower() for c in df.columns]
    required = {"inject_id", "mode", "rating"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Fehlende Spalten im CSV: {missing}")
    # Sicherstellen, dass reason vorhanden ist
    if "reason" not in df.columns:
        df["reason"] = ""
    return df


def compute_basic_metrics(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("mode")
    rows = []
    for mode, g in grouped:
        total = len(g)
        halluc = (g["rating"].str.lower() == "hallucination").sum()
        consistent = (g["rating"].str.lower() == "consistent").sum()
        evaluated = halluc + consistent
        rows.append(
            {
                "mode": mode,
                "total": total,
                "evaluated": evaluated,
                "hallucinations": halluc,
                "consistent": consistent,
                "error_rate_pct": round(halluc / evaluated * 100, 2) if evaluated else 0.0,
                "consistency_rate_pct": round(consistent / evaluated * 100, 2)
                if evaluated
                else 0.0,
            }
        )
    return pd.DataFrame(rows)


# Einfache Kategorie-Zuordnung über Schlüsselwörter
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "A_LOGIK": ["inkonsist", "widerspruch", "reihenfolge", "phase", "zeit", "timeline"],
    "B_DORA": ["dora", "article 25", "compliance"],
    "C_KAUSAL": ["mitre", "causal", "sequence", "attack", "ttp"],
    "D_NAMING": ["asset name", "id stimmt", "benennung", "naming"],
    "E_FORMAT": ["schema", "pydantic", "json", "format"],
}


def categorize_reason(reason: str) -> List[str]:
    text = (reason or "").lower()
    hits = []
    for cat, keys in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keys):
            hits.append(cat)
    if not hits:
        hits.append("Z_MISC")
    return hits


def compute_categories(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        if str(row["rating"]).lower() != "hallucination":
            continue
        cats = categorize_reason(row.get("reason", ""))
        for cat in cats:
            records.append({"mode": row["mode"], "category": cat})
    if not records:
        return pd.DataFrame(columns=["mode", "category", "count"])
    cat_df = pd.DataFrame(records)
    return (
        cat_df.groupby(["mode", "category"])
        .size()
        .reset_index(name="count")
        .sort_values(["mode", "count"], ascending=[True, False])
    )


def make_chart(df_metrics: pd.DataFrame, output_html: Path) -> None:
    try:
        import plotly.graph_objects as go
    except ImportError as e:
        raise RuntimeError("Plotly nicht installiert. Bitte 'pip install plotly' ausführen.") from e

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Fehlerrate (%)",
            x=df_metrics["mode"],
            y=df_metrics["error_rate_pct"],
            marker_color="#ef4444",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Konsistenzrate (%)",
            x=df_metrics["mode"],
            y=df_metrics["consistency_rate_pct"],
            marker_color="#10b981",
        )
    )
    fig.update_layout(
        title="Fehler- und Konsistenzraten nach Modus",
        barmode="group",
        yaxis_title="Prozent",
        template="plotly_white",
    )
    fig.write_html(output_html, include_plotlyjs="cdn")


def main():
    parser = argparse.ArgumentParser(description="Thesis-Evaluations-CSV auswerten.")
    parser.add_argument("--file", required=True, help="Pfad zur Export-CSV aus dem Frontend.")
    parser.add_argument("--chart", action="store_true", help="Plotly-Chart als HTML erzeugen.")
    parser.add_argument(
        "--out-json",
        type=str,
        default="",
        help="Optional: Aggregierte Metriken als JSON speichern.",
    )
    args = parser.parse_args()

    csv_path = Path(args.file).expanduser().resolve()
    df = load_data(csv_path)

    df_metrics = compute_basic_metrics(df)
    df_cats = compute_categories(df)

    print("\n=== Basis-Metriken ===")
    print(df_metrics.to_string(index=False))

    if not df_cats.empty:
        print("\n=== Fehlerkategorien (Halluzinationen) ===")
        print(df_cats.to_string(index=False))
    else:
        print("\n=== Fehlerkategorien ===")
        print("Keine Halluzinationen oder keine Gründe erfasst.")

    if args.chart:
        html_path = csv_path.with_suffix(".metrics.html")
        make_chart(df_metrics, html_path)
        print(f"\nPlotly-Chart geschrieben nach: {html_path}")

    if args.out_json:
        out_path = Path(args.out_json).expanduser().resolve()
        payload = {
            "metrics": df_metrics.to_dict(orient="records"),
            "categories": df_cats.to_dict(orient="records") if not df_cats.empty else [],
        }
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Aggregierte Metriken gespeichert in: {out_path}")


if __name__ == "__main__":
    main()
