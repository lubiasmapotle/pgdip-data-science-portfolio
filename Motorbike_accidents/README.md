# Colombia motorcycle road-safety analysis

## Dashboard deliverable

- [motorcycle_dashboard.png](./motorcycle_dashboard.png) is the high-resolution, one-page dashboard export.
- [build_dashboard.py](./build_dashboard.py) regenerates the dashboard from the CSV.
- [Motorcycle_accidents.ipynb](./Motorcycle_accidents.ipynb) contains the detailed exploratory analysis.

From this directory, install the project dependencies and regenerate the dashboard with:

```bash
uv sync
uv run python build_dashboard.py
```

## Scope note

The supplied file is `motorcycle_accidents_colombia.csv`; an upstream publisher or source URL was not included with it. Its 416 records have dates of death and residence geography, but no crash-site, incident, or injury-severity fields. The dashboard therefore summarizes people in this file by residence, rider characteristics, and date of death; it cannot identify where crashes occurred or compare severity. Counts are not population-adjusted risk estimates. The displayed reporting period is derived from the minimum and maximum valid `date_of_death` values.

The official challenge hashtag was not provided; add it consistently when publishing.