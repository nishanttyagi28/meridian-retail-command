// Power Query (M) — load Meridian mart CSVs into Power BI Desktop
// Home → Get data → Blank query → Advanced Editor → paste one query per mart.
// Point FolderPath to your local clone's data/mart folder.

let
    FolderPath = "C:\\path\\to\\meridian-retail-command\\data\\mart\\",
    Source = Csv.Document(
        File.Contents(FolderPath & "mart_kpi_snapshot.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"line_rows", Int64.Type},
            {"invoices", Int64.Type},
            {"customers", Int64.Type},
            {"skus", Int64.Type},
            {"countries", Int64.Type},
            {"gross_sales_gbp", type number},
            {"returns_abs_value", type number},
            {"return_rate_pct", type number},
            {"aov", type number},
            {"guest_checkout_pct", type number}
        }
    )
in
    Typed
