#!/usr/bin/env python3
"""Generate Meridian.pbip — openable in Power BI Desktop (Windows/Mac)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi" / "Meridian.pbip"
REPORT = ROOT / "powerbi" / "Meridian.Report"
MODEL = ROOT / "powerbi" / "Meridian.SemanticModel"
THEME_SRC = ROOT / "powerbi" / "theme" / "MeridianRetailTheme.json"

SCHEMA_VISUAL = (
    "https://developer.microsoft.com/json-schemas/fabric/item/"
    "report/definition/visualContainer/2.7.0/schema.json"
)
SCHEMA_PAGE = (
    "https://developer.microsoft.com/json-schemas/fabric/item/"
    "report/definition/page/2.0.0/schema.json"
)


def uid(n: int = 20) -> str:
    return uuid.uuid4().hex[:n]


def lineage() -> str:
    return str(uuid.uuid4())


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8", newline="\n")


def measure_proj(entity: str, prop: str) -> dict:
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop,
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }


def column_proj(entity: str, prop: str, active: bool | None = None) -> dict:
    p: dict = {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": entity}},
                "Property": prop,
            }
        },
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }
    if active is not None:
        p["active"] = active
    return p


def card(name: str, x: float, y: float, z: int, w: float, h: float, entity: str, measure: str, title: str) -> dict:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": [measure_proj(entity, measure)]}}},
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def line_chart(
    name: str,
    x: float,
    y: float,
    z: int,
    w: float,
    h: float,
    cat_entity: str,
    cat_col: str,
    measures: list[tuple[str, str]],
    title: str,
) -> dict:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [column_proj(cat_entity, cat_col, True)]},
                    "Y": {"projections": [measure_proj(e, m) for e, m in measures]},
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def bar_chart(
    name: str,
    x: float,
    y: float,
    z: int,
    w: float,
    h: float,
    cat_entity: str,
    cat_col: str,
    measures: list[tuple[str, str]],
    title: str,
) -> dict:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "barChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [column_proj(cat_entity, cat_col, True)]},
                    "Y": {"projections": [measure_proj(e, m) for e, m in measures]},
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def donut(
    name: str,
    x: float,
    y: float,
    z: int,
    w: float,
    h: float,
    cat_entity: str,
    cat_col: str,
    measure_entity: str,
    measure: str,
    title: str,
) -> dict:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "donutChart",
            "query": {
                "queryState": {
                    "Category": {"projections": [column_proj(cat_entity, cat_col, True)]},
                    "Y": {"projections": [measure_proj(measure_entity, measure)]},
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def table_ex(
    name: str,
    x: float,
    y: float,
    z: int,
    w: float,
    h: float,
    fields: list[tuple[str, str, str]],
    title: str,
) -> dict:
    """fields: list of (kind, entity, prop) where kind is Column|Measure."""
    projs = []
    for kind, entity, prop in fields:
        if kind == "Measure":
            projs.append(measure_proj(entity, prop))
        else:
            projs.append(column_proj(entity, prop))
    return {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": projs}}},
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def matrix_cohort(
    name: str,
    x: float,
    y: float,
    z: int,
    w: float,
    h: float,
) -> dict:
    return {
        "$schema": SCHEMA_VISUAL,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": "pivotTable",
            "query": {
                "queryState": {
                    "Rows": {"projections": [column_proj("Cohort", "cohort_month", True)]},
                    "Columns": {"projections": [column_proj("Cohort", "month_number", True)]},
                    "Values": {"projections": [measure_proj("Cohort", "Retention %")]},
                }
            },
            "visualContainerObjects": {
                "title": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "text": {"expr": {"Literal": {"Value": "'Cohort retention %'"}}},
                        }
                    }
                ]
            },
            "drillFilterOtherVisuals": True,
        },
    }


def page_json(name: str, display: str) -> dict:
    return {
        "$schema": SCHEMA_PAGE,
        "name": name,
        "displayName": display,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
    }


def csv_partition(table: str, filename: str, columns: list[tuple[str, str]]) -> str:
    """columns: (name, m_type) e.g. ('sales', 'type number')."""
    n = len(columns)
    type_pairs = ", ".join(f'{{"{c}", {t}}}' for c, t in columns)
    # M uses backslash paths on Windows; MartFolder parameter supplies folder.
    return f"""
	partition '{table}' = m
		mode: import
		source =
			let
				Source = Csv.Document(
					File.Contents(MartFolder & "\\\\{filename}"),
					[Delimiter=",", Columns={n}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
				),
				#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
				#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{type_pairs}}})
			in
				#"Changed Type"
"""


def column_block(name: str, dtype: str, summarize: str = "none") -> str:
    return f"""
	column '{name}'
		dataType: {dtype}
		lineageTag: {lineage()}
		summarizeBy: {summarize}
		sourceColumn: {name}

		annotation SummarizationSetBy = Automatic
"""


def render_table(
    name: str,
    filename: str,
    columns: list[tuple[str, str, str]],
    measures: list[tuple[str, str, str]] | None = None,
) -> str:
    """columns: (name, tmdl_dtype, m_type). measures: (name, dax, format)."""
    parts = [f"table '{name}'", f"\tlineageTag: {lineage()}"]
    m_cols = [(c[0], c[2]) for c in columns]
    parts.append(csv_partition(name, filename, m_cols))
    for cname, dtype, _ in columns:
        summarize = "sum" if dtype == "doublePrecision" else "none"
        if cname in ("customers", "invoices", "frequency", "units", "active_customers", "cohort_customers", "skus", "line_rows", "countries"):
            summarize = "sum"
        parts.append(column_block(cname, dtype, summarize))
    for mname, dax, fmt in measures or []:
        parts.append(
            f"""
	measure '{mname}' = {dax}
		formatString: {fmt}
		lineageTag: {lineage()}
"""
        )
    return "\n".join(parts) + "\n"


def build_model() -> None:
    if MODEL.exists():
        import shutil

        shutil.rmtree(MODEL)
    (MODEL / "definition" / "tables").mkdir(parents=True)
    (MODEL / "definition" / "roles").mkdir(parents=True)
    (MODEL / ".pbi").mkdir(parents=True)

    write_json(
        MODEL / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.0",
            "settings": {},
        },
    )
    write_json(
        MODEL / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {
                "type": "SemanticModel",
                "displayName": "Meridian",
            },
            "config": {"version": "2.0", "logicalId": uid(32)},
        },
    )
    write(
        MODEL / "definition" / "database.tmdl",
        "database Meridian\n\tcompatibilityLevel: 1567\n",
    )
    write(
        MODEL / "definition" / "expressions.tmdl",
        """expression MartFolder = "C:\\\\Repos\\\\meridian-retail-command\\\\data\\\\mart" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
	lineageTag: """
        + lineage()
        + """
	queryGroup: Parameters

	annotation PBI_NavigationStepName = Navigation

	annotation PBI_ResultType = Text
""",
    )

    tables = {
        "KPI": render_table(
            "KPI",
            "mart_kpi_snapshot.csv",
            [
                ("line_rows", "int64", "Int64.Type"),
                ("invoices", "int64", "Int64.Type"),
                ("customers", "int64", "Int64.Type"),
                ("skus", "int64", "Int64.Type"),
                ("countries", "int64", "Int64.Type"),
                ("gross_sales_gbp", "doublePrecision", "type number"),
                ("returns_abs_value", "doublePrecision", "type number"),
                ("return_rate_pct", "doublePrecision", "type number"),
                ("aov", "doublePrecision", "type number"),
                ("guest_checkout_pct", "doublePrecision", "type number"),
            ],
            [
                ("Gross Sales GBP", "MAX ( 'KPI'[gross_sales_gbp] )", "£#,##0"),
                ("Returns GBP", "MAX ( 'KPI'[returns_abs_value] )", "£#,##0"),
                ("Return Rate %", "MAX ( 'KPI'[return_rate_pct] ) / 100", "0.0%"),
                ("AOV GBP", "MAX ( 'KPI'[aov] )", "£#,##0.00"),
                ("Customers", "MAX ( 'KPI'[customers] )", "#,##0"),
                ("SKUs", "MAX ( 'KPI'[skus] )", "#,##0"),
                ("Guest Checkout %", "MAX ( 'KPI'[guest_checkout_pct] ) / 100", "0.0%"),
                ("Invoices", "MAX ( 'KPI'[invoices] )", "#,##0"),
            ],
        ),
        "Monthly": render_table(
            "Monthly",
            "mart_monthly_trend.csv",
            [
                ("invoice_month", "string", "type text"),
                ("sales", "doublePrecision", "type number"),
                ("returns_abs", "doublePrecision", "type number"),
                ("invoices", "int64", "Int64.Type"),
                ("customers", "int64", "Int64.Type"),
                ("aov", "doublePrecision", "type number"),
            ],
            [
                ("Monthly Sales", "SUM ( 'Monthly'[sales] )", "£#,##0"),
                ("Monthly Returns", "SUM ( 'Monthly'[returns_abs] )", "£#,##0"),
                ("Monthly Invoices", "SUM ( 'Monthly'[invoices] )", "#,##0"),
            ],
        ),
        "Country": render_table(
            "Country",
            "mart_country_performance.csv",
            [
                ("country", "string", "type text"),
                ("customers", "int64", "Int64.Type"),
                ("invoices", "int64", "Int64.Type"),
                ("sales", "doublePrecision", "type number"),
                ("returns_abs", "doublePrecision", "type number"),
                ("return_rate_pct", "doublePrecision", "type number"),
                ("aov", "doublePrecision", "type number"),
            ],
            [
                ("Country Sales", "SUM ( 'Country'[sales] )", "£#,##0"),
                ("Country Return Rate", "DIVIDE ( SUM ( 'Country'[returns_abs] ), SUM ( 'Country'[sales] ), 0 )", "0.0%"),
                ("Country AOV", "AVERAGE ( 'Country'[aov] )", "£#,##0.00"),
            ],
        ),
        "RFM": render_table(
            "RFM",
            "mart_customer_rfm.csv",
            [
                ("customer_id", "string", "type text"),
                ("last_purchase", "string", "type text"),
                ("recency_days", "int64", "Int64.Type"),
                ("frequency", "int64", "Int64.Type"),
                ("monetary", "doublePrecision", "type number"),
                ("returns_abs", "doublePrecision", "type number"),
                ("r_score", "int64", "Int64.Type"),
                ("f_score", "int64", "Int64.Type"),
                ("m_score", "int64", "Int64.Type"),
                ("rfm_sum", "int64", "Int64.Type"),
                ("rfm_segment", "string", "type text"),
            ],
            [
                ("RFM Customers", "DISTINCTCOUNT ( 'RFM'[customer_id] )", "#,##0"),
                ("RFM Revenue", "SUM ( 'RFM'[monetary] )", "£#,##0"),
                ("Champions Revenue", "CALCULATE ( SUM ( 'RFM'[monetary] ), 'RFM'[rfm_segment] = \"Champions\" )", "£#,##0"),
            ],
        ),
        "Cohort": render_table(
            "Cohort",
            "mart_cohort_retention.csv",
            [
                ("cohort_month", "string", "type text"),
                ("month_number", "doublePrecision", "type number"),
                ("active_customers", "int64", "Int64.Type"),
                ("cohort_customers", "int64", "Int64.Type"),
                ("retention_pct", "doublePrecision", "type number"),
            ],
            [
                ("Retention %", "AVERAGE ( 'Cohort'[retention_pct] ) / 100", "0.0%"),
                ("Active in Cohort Month", "SUM ( 'Cohort'[active_customers] )", "#,##0"),
            ],
        ),
        "Pareto": render_table(
            "Pareto",
            "mart_product_pareto.csv",
            [
                ("stock_code", "string", "type text"),
                ("description", "string", "type text"),
                ("sales", "doublePrecision", "type number"),
                ("units", "int64", "Int64.Type"),
                ("pct_of_sales", "doublePrecision", "type number"),
                ("cumulative_pct", "doublePrecision", "type number"),
                ("is_top80_pct", "int64", "Int64.Type"),
            ],
            [
                ("SKU Sales", "SUM ( 'Pareto'[sales] )", "£#,##0"),
                ("Top 80 SKU Count", "CALCULATE ( DISTINCTCOUNT ( 'Pareto'[stock_code] ), 'Pareto'[is_top80_pct] = 1 )", "#,##0"),
            ],
        ),
        "Returns": render_table(
            "Returns",
            "mart_returns_leakage.csv",
            [
                ("invoice_id", "string", "type text"),
                ("invoice_date", "string", "type text"),
                ("stock_code", "string", "type text"),
                ("description", "string", "type text"),
                ("customer_id", "string", "type text"),
                ("country", "string", "type text"),
                ("qty", "int64", "Int64.Type"),
                ("unit_price", "doublePrecision", "type number"),
                ("return_value", "doublePrecision", "type number"),
                ("is_cancellation", "int64", "Int64.Type"),
                ("is_return_qty", "int64", "Int64.Type"),
            ],
            [
                ("Return Value", "SUM ( 'Returns'[return_value] )", "£#,##0.00"),
                ("Return Lines", "COUNTROWS ( 'Returns' )", "#,##0"),
            ],
        ),
    }

    for tname, body in tables.items():
        write(MODEL / "definition" / "tables" / f"{tname}.tmdl", body)

    refs = "\n".join(f"ref table '{t}'" for t in tables)
    write(
        MODEL / "definition" / "model.tmdl",
        f"""model Model
	culture: en-US
	defaultPowerBIDataSourceVersion: powerBI_V3
	sourceQueryCulture: en-US
	dataAccessOptions
		legacyRedirects
		returnErrorValuesAsNull

queryGroup Parameters

	annotation PBI_QueryGroupOrder = 0

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_QueryOrder = ["MartFolder","KPI","Monthly","Country","RFM","Cohort","Pareto","Returns"]

{refs}
""",
    )
    write(MODEL / "definition" / "relationships.tmdl", "")

    # RLS on Country + Returns country column
    write(
        MODEL / "definition" / "roles" / "UK_Market.tmdl",
        """role 'UK_Market'
	modelPermission: read

	tablePermission Country
		filterExpression: 'Country'[country] = "United Kingdom"

	tablePermission Returns
		filterExpression: 'Returns'[country] = "United Kingdom"
""",
    )
    write(
        MODEL / "definition" / "roles" / "Executive_All.tmdl",
        """role 'Executive_All'
	modelPermission: read
""",
    )


def add_visuals(page_dir: Path, visuals: list[dict]) -> None:
    for v in visuals:
        name = v["name"]
        write_json(page_dir / "visuals" / name / "visual.json", v)


def build_report() -> None:
    if REPORT.exists():
        import shutil

        shutil.rmtree(REPORT)
    pages_root = REPORT / "definition" / "pages"
    pages_root.mkdir(parents=True)
    (REPORT / "StaticResources" / "RegisteredResources").mkdir(parents=True)
    (REPORT / "StaticResources" / "SharedResources" / "BaseThemes").mkdir(parents=True)
    (REPORT / ".pbi").mkdir(parents=True)

    theme = json.loads(THEME_SRC.read_text(encoding="utf-8"))
    write_json(
        REPORT / "StaticResources" / "RegisteredResources" / "MeridianRetailTheme.json",
        theme,
    )

    write_json(
        REPORT / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../Meridian.SemanticModel"}},
        },
    )
    write_json(
        REPORT / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "Report", "displayName": "Meridian"},
            "config": {"version": "2.0", "logicalId": uid(32)},
        },
    )
    write_json(
        REPORT / "definition" / "version.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "2.0.0",
        },
    )
    write_json(
        REPORT / "definition" / "report.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.0.0/schema.json",
            "themeCollection": {
                "customTheme": {
                    "name": "MeridianRetailTheme.json",
                    "reportVersionAtImport": {
                        "visual": "2.1.0",
                        "report": "2.1.0",
                        "page": "2.0.0",
                    },
                    "type": "RegisteredResources",
                }
            },
            "objects": {
                "section": [{"properties": {"verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}}}]
            },
            "resourcePackages": [
                {
                    "name": "RegisteredResources",
                    "type": "RegisteredResources",
                    "items": [
                        {
                            "name": "MeridianRetailTheme.json",
                            "path": "MeridianRetailTheme.json",
                            "type": "CustomTheme",
                        }
                    ],
                }
            ],
            "settings": {
                "useStylableLimit": True,
                "exportDataMode": "AllowSummarized",
            },
        },
    )

    page_ids = {
        "pulse": uid(),
        "markets": uid(),
        "crm": uid(),
        "cohort": uid(),
        "assortment": uid(),
        "returns": uid(),
    }

    # Pulse
    p = pages_root / page_ids["pulse"]
    write_json(p / "page.json", page_json(page_ids["pulse"], "01 Pulse"))
    add_visuals(
        p,
        [
            card(uid(), 24, 24, 0, 190, 110, "KPI", "Gross Sales GBP", "Gross sales"),
            card(uid(), 230, 24, 1, 190, 110, "KPI", "Return Rate %", "Return rate"),
            card(uid(), 436, 24, 2, 190, 110, "KPI", "AOV GBP", "AOV"),
            card(uid(), 642, 24, 3, 190, 110, "KPI", "Customers", "Customers"),
            card(uid(), 848, 24, 4, 190, 110, "KPI", "SKUs", "SKUs"),
            card(uid(), 1054, 24, 5, 200, 110, "KPI", "Guest Checkout %", "Guest lines"),
            line_chart(
                uid(),
                24,
                160,
                6,
                820,
                520,
                "Monthly",
                "invoice_month",
                [("Monthly", "Monthly Sales"), ("Monthly", "Monthly Returns")],
                "Monthly sales vs returns",
            ),
            table_ex(
                uid(),
                860,
                160,
                7,
                396,
                520,
                [
                    ("Column", "Monthly", "invoice_month"),
                    ("Measure", "Monthly", "Monthly Sales"),
                    ("Measure", "Monthly", "Monthly Returns"),
                    ("Measure", "Monthly", "Monthly Invoices"),
                ],
                "Month detail",
            ),
        ],
    )

    # Markets
    p = pages_root / page_ids["markets"]
    write_json(p / "page.json", page_json(page_ids["markets"], "02 Markets"))
    add_visuals(
        p,
        [
            bar_chart(
                uid(),
                24,
                24,
                0,
                640,
                660,
                "Country",
                "country",
                [("Country", "Country Sales")],
                "Sales by country",
            ),
            table_ex(
                uid(),
                680,
                24,
                1,
                576,
                660,
                [
                    ("Column", "Country", "country"),
                    ("Measure", "Country", "Country Sales"),
                    ("Column", "Country", "return_rate_pct"),
                    ("Column", "Country", "aov"),
                    ("Column", "Country", "customers"),
                ],
                "Market scorecard",
            ),
        ],
    )

    # RFM / CRM
    p = pages_root / page_ids["crm"]
    write_json(p / "page.json", page_json(page_ids["crm"], "03 RFM CRM"))
    add_visuals(
        p,
        [
            card(uid(), 24, 24, 0, 280, 110, "RFM", "Champions Revenue", "Champions revenue"),
            card(uid(), 320, 24, 1, 280, 110, "RFM", "RFM Customers", "Identified customers"),
            card(uid(), 616, 24, 2, 280, 110, "RFM", "RFM Revenue", "RFM revenue"),
            donut(
                uid(),
                24,
                160,
                3,
                520,
                520,
                "RFM",
                "rfm_segment",
                "RFM",
                "RFM Revenue",
                "Revenue by segment",
            ),
            table_ex(
                uid(),
                560,
                160,
                4,
                696,
                520,
                [
                    ("Column", "RFM", "rfm_segment"),
                    ("Column", "RFM", "customer_id"),
                    ("Column", "RFM", "recency_days"),
                    ("Column", "RFM", "frequency"),
                    ("Column", "RFM", "monetary"),
                ],
                "Customer RFM",
            ),
        ],
    )

    # Cohort
    p = pages_root / page_ids["cohort"]
    write_json(p / "page.json", page_json(page_ids["cohort"], "04 Cohorts"))
    add_visuals(
        p,
        [
            card(uid(), 24, 24, 0, 300, 110, "Cohort", "Retention %", "Avg retention %"),
            matrix_cohort(uid(), 24, 160, 1, 1232, 520),
        ],
    )

    # Assortment
    p = pages_root / page_ids["assortment"]
    write_json(p / "page.json", page_json(page_ids["assortment"], "05 Assortment"))
    add_visuals(
        p,
        [
            card(uid(), 24, 24, 0, 300, 110, "Pareto", "Top 80 SKU Count", "SKUs in top 80%"),
            card(uid(), 340, 24, 1, 300, 110, "Pareto", "SKU Sales", "SKU sales"),
            line_chart(
                uid(),
                24,
                160,
                2,
                640,
                520,
                "Pareto",
                "stock_code",
                [("Pareto", "SKU Sales")],
                "SKU sales (Pareto view)",
            ),
            table_ex(
                uid(),
                680,
                160,
                3,
                576,
                520,
                [
                    ("Column", "Pareto", "stock_code"),
                    ("Column", "Pareto", "description"),
                    ("Measure", "Pareto", "SKU Sales"),
                    ("Column", "Pareto", "cumulative_pct"),
                    ("Column", "Pareto", "is_top80_pct"),
                ],
                "Top SKUs",
            ),
        ],
    )

    # Returns
    p = pages_root / page_ids["returns"]
    write_json(p / "page.json", page_json(page_ids["returns"], "06 Returns"))
    add_visuals(
        p,
        [
            card(uid(), 24, 24, 0, 300, 110, "Returns", "Return Value", "Return value"),
            card(uid(), 340, 24, 1, 300, 110, "Returns", "Return Lines", "Return lines"),
            bar_chart(
                uid(),
                24,
                160,
                2,
                560,
                520,
                "Returns",
                "country",
                [("Returns", "Return Value")],
                "Returns by country",
            ),
            table_ex(
                uid(),
                600,
                160,
                3,
                656,
                520,
                [
                    ("Column", "Returns", "invoice_date"),
                    ("Column", "Returns", "stock_code"),
                    ("Column", "Returns", "country"),
                    ("Column", "Returns", "qty"),
                    ("Measure", "Returns", "Return Value"),
                ],
                "Largest return lines",
            ),
        ],
    )

    write_json(
        pages_root / "pages.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": list(page_ids.values()),
            "activePageName": page_ids["pulse"],
        },
    )


def build_pbip() -> None:
    write_json(
        OUT,
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
            "version": "1.0",
            "artifacts": [
                {
                    "report": {
                        "path": "Meridian.Report",
                    }
                }
            ],
        },
    )
    write(
        ROOT / "powerbi" / ".gitignore",
        "**/.pbi/localSettings.json\n**/.pbi/cache.abf\n**/.pbi/desktop.ini.json\n",
    )


def main() -> None:
    build_model()
    build_report()
    build_pbip()
    print(f"Wrote {OUT}")
    print(f"Report: {REPORT}")
    print(f"Model:  {MODEL}")


if __name__ == "__main__":
    main()
