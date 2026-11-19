from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "motorcycle_accidents_colombia.csv"
OUTPUT_PATH = ROOT / "motorcycle_dashboard.png"

BG = "#F4F7FB"
INK = "#16263D"
MUTED = "#61738A"
BLUE = "#2878B5"
TEAL = "#12A594"
ORANGE = "#E69B37"
GRID = "#DCE4EF"


def main() -> None:
    data = pd.read_csv(DATA_PATH)
    required = {
        "date_of_death",
        "gender",
        "age group",
        "department of residence",
        "municipality_of_residence",
        "condition",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    data["date_of_death"] = pd.to_datetime(data["date_of_death"], errors="coerce", utc=True)
    total = len(data)
    if not total:
        raise ValueError("The dataset has no records to summarize.")

    antioquia_count = data["department of residence"].str.casefold().eq("antioquia").sum()
    medellin_count = data["municipality_of_residence"].str.casefold().eq("medellín").sum()
    age_20_24_count = data["age group"].eq("20-24").sum()
    age_20_34_count = data["age group"].isin(["20-24", "25-29", "30-34"]).sum()
    valid_dates = data["date_of_death"].dropna()
    period = f"{valid_dates.min():%Y-%m-%d} to {valid_dates.max():%Y-%m-%d}"

    cities = data.loc[
        data["municipality_of_residence"].str.casefold().ne("unknown"),
        "municipality_of_residence",
    ].value_counts().head(8).sort_values()
    ages = pd.crosstab(data["age group"], data["gender"])
    age_order = sorted(
        ages.index,
        key=lambda band: int(str(band).split("-")[0]) if str(band).split("-")[0].isdigit() else 999,
    )
    ages = ages.reindex(age_order)
    yearly = valid_dates.dt.year.value_counts().sort_index()

    fig = plt.figure(figsize=(12, 16), facecolor=BG)
    grid = fig.add_gridspec(
        15,
        12,
        left=0.075,
        right=0.94,
        top=0.96,
        bottom=0.055,
        hspace=2.2,
        wspace=1.0,
    )

    title_ax = fig.add_subplot(grid[0:2, :])
    title_ax.set_facecolor(BG)
    title_ax.axis("off")
    title_ax.text(
        0,
        0.88,
        "MOTORCYCLE ROAD SAFETY  /  COLOMBIA",
        color=TEAL,
        fontsize=11,
        fontweight="bold",
        transform=title_ax.transAxes,
    )
    title_ax.text(
        0,
        0.42,
        "Where do the records cluster?",
        color=INK,
        fontsize=27,
        fontweight="bold",
        transform=title_ax.transAxes,
    )
    title_ax.text(
        0,
        0.04,
        "A descriptive look at recorded motorcycle-related deaths and rider characteristics",
        color=MUTED,
        fontsize=12,
        transform=title_ax.transAxes,
    )

    kpi_specs = [
        (f"{total:,}", "PERSON RECORDS", BLUE),
        (f"{medellin_count / total:.1%}", "RESIDENTS IN MEDELLÍN", TEAL),
        (f"{age_20_24_count / total:.1%}", "AGED 20–24", ORANGE),
    ]
    for i, (value, label, color) in enumerate(kpi_specs):
        ax = fig.add_subplot(grid[2:4, i * 4 : (i + 1) * 4])
        ax.set_facecolor(BG)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        card = FancyBboxPatch(
            (0.025, 0.08),
            0.95,
            0.84,
            boxstyle="round,pad=0.015,rounding_size=0.035",
            transform=ax.transAxes,
            facecolor="white",
            edgecolor=GRID,
            linewidth=1,
        )
        ax.add_patch(card)
        ax.text(0.10, 0.54, value, transform=ax.transAxes, fontsize=25, color=color, fontweight="bold")
        ax.text(0.10, 0.25, label, transform=ax.transAxes, fontsize=9, color=MUTED, fontweight="bold")

    insight_ax = fig.add_subplot(grid[4:6, :])
    insight_ax.set_facecolor(BG)
    insight_ax.axis("off")
    insight = (
        f"INSIGHT  •  Ages 20–34 make up {age_20_34_count:,} of {total:,} records "
        f"({age_20_34_count / total:.1%}); ages 20–24 are the largest single band. "
        f"{antioquia_count:,} records ({antioquia_count / total:.1%}) list Antioquia as residence."
    )
    insight_ax.text(
        0.02,
        0.68,
        insight,
        transform=insight_ax.transAxes,
        fontsize=13,
        color=INK,
        fontweight="medium",
        wrap=True,
        bbox={"boxstyle": "round,pad=0.8", "facecolor": "#E8F3F4", "edgecolor": "none"},
    )
    insight_ax.text(
        0.02,
        0.12,
        "Residence geography is not crash location; these counts do not measure exposure or risk.",
        transform=insight_ax.transAxes,
        fontsize=10,
        color=MUTED,
        style="italic",
    )

    city_ax = fig.add_subplot(grid[6:10, 0:6])
    city_ax.set_facecolor("white")
    city_ax.barh(cities.index, cities.values, color=BLUE, height=0.66)
    city_ax.set_title("Residence municipality", loc="left", color=INK, fontsize=14, fontweight="bold", pad=14)
    city_ax.set_xlabel("Person records", color=MUTED, labelpad=4)
    city_ax.grid(axis="x", color=GRID, linewidth=0.8)
    city_ax.set_axisbelow(True)
    city_ax.spines[["top", "right", "left"]].set_visible(False)
    city_ax.spines["bottom"].set_color(GRID)
    city_ax.tick_params(axis="y", length=0, colors=INK, labelsize=9)
    city_ax.tick_params(axis="x", colors=MUTED, labelsize=9)
    city_ax.set_xlim(0, max(cities.values) * 1.18)
    for position, count in enumerate(cities.values):
        city_ax.text(count + max(cities.values) * 0.015, position, f"{count:,}", va="center", color=INK, fontsize=9)

    age_ax = fig.add_subplot(grid[6:10, 7:12])
    age_ax.set_facecolor("white")
    colors = {"female": ORANGE, "male": BLUE}
    ages.plot(kind="bar", stacked=True, ax=age_ax, color=[colors.get(str(col).casefold(), TEAL) for col in ages.columns], width=0.72)
    age_ax.set_title("Records by age and gender", loc="left", color=INK, fontsize=14, fontweight="bold", pad=14)
    age_ax.set_xlabel("Age band", color=MUTED, labelpad=4)
    age_ax.set_ylabel("Person records", color=MUTED)
    age_ax.grid(axis="y", color=GRID, linewidth=0.8)
    age_ax.set_axisbelow(True)
    age_ax.spines[["top", "right"]].set_visible(False)
    age_ax.spines["left"].set_color(GRID)
    age_ax.spines["bottom"].set_color(GRID)
    age_ax.tick_params(axis="x", rotation=45, labelsize=8, colors=INK)
    age_ax.tick_params(axis="y", labelsize=8, colors=MUTED)
    age_ax.legend(title="Gender", frameon=False, fontsize=8, title_fontsize=8, loc="upper right")

    year_ax = fig.add_subplot(grid[10:13, :])
    year_ax.set_facecolor("white")
    year_ax.bar(yearly.index.astype(str), yearly.values, color=TEAL, width=0.55)
    year_ax.set_title("Records by year of death", loc="left", color=INK, fontsize=14, fontweight="bold", pad=14)
    year_ax.set_ylabel("Person records", color=MUTED)
    year_ax.grid(axis="y", color=GRID, linewidth=0.8)
    year_ax.set_axisbelow(True)
    year_ax.spines[["top", "right"]].set_visible(False)
    year_ax.spines["left"].set_color(GRID)
    year_ax.spines["bottom"].set_color(GRID)
    year_ax.tick_params(axis="x", colors=INK, labelsize=10)
    year_ax.tick_params(axis="y", colors=MUTED, labelsize=9)
    for year, count in zip(yearly.index.astype(str), yearly.values, strict=True):
        year_ax.text(year, count + max(yearly.values) * 0.025, f"{count}", ha="center", color=INK, fontsize=10)

    footer_ax = fig.add_subplot(grid[13:15, :])
    footer_ax.set_facecolor(BG)
    footer_ax.axis("off")
    footer_ax.text(
        0,
        0.82,
        "CAUTION",
        color=ORANGE,
        fontsize=10,
        fontweight="bold",
        transform=footer_ax.transAxes,
    )
    footer_ax.text(
        0,
        0.58,
        "The supplied file has date of death and residence fields, but no crash site or injury-severity field. "
        "It contains person records, not a count of all crashes; no risk comparison is possible.",
        color=INK,
        fontsize=10,
        wrap=True,
        transform=footer_ax.transAxes,
    )
    footer_ax.text(
        0,
        0.20,
        f"Tool: Python · pandas · Matplotlib     |     Period: {period} (date of death)     |     "
        "Source: supplied motorcycle_accidents_colombia.csv; upstream attribution not provided",
        color=MUTED,
        fontsize=8,
        wrap=True,
        transform=footer_ax.transAxes,
    )

    fig.savefig(OUTPUT_PATH, dpi=200, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"Dashboard saved to {OUTPUT_PATH}")
    print(
        f"Verified: {total} records; Antioquia residence {antioquia_count}; "
        f"Medellín residence {medellin_count}; ages 20–24 {age_20_24_count}; "
        f"ages 20–34 {age_20_34_count}; date range {period}."
    )


if __name__ == "__main__":
    main()
