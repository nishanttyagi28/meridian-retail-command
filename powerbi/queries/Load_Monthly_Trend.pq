let
    FolderPath = "C:\\path\\to\\meridian-retail-command\\data\\mart\\",
    Source = Csv.Document(
        File.Contents(FolderPath & "mart_monthly_trend.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"invoice_month", type text},
            {"sales", type number},
            {"returns_abs", type number},
            {"invoices", Int64.Type},
            {"customers", Int64.Type},
            {"aov", type number}
        }
    )
in
    Typed
