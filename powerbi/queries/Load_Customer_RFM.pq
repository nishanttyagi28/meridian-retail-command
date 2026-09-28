let
    FolderPath = "C:\\path\\to\\meridian-retail-command\\data\\mart\\",
    Source = Csv.Document(
        File.Contents(FolderPath & "mart_customer_rfm.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"customer_id", type text},
            {"last_purchase", type date},
            {"recency_days", Int64.Type},
            {"frequency", Int64.Type},
            {"monetary", type number},
            {"returns_abs", type number},
            {"r_score", Int64.Type},
            {"f_score", Int64.Type},
            {"m_score", Int64.Type},
            {"rfm_sum", Int64.Type},
            {"rfm_segment", type text}
        }
    )
in
    Typed
