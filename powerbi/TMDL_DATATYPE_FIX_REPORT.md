# TMDL datatype fix report

Total replacements: **43**

| File | Line | Old | New |
|------|------|-----|-----|
| `powerbi/Meridian.SemanticModel/definition/tables/Cohort.tmdl` | 28 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Cohort.tmdl` | 55 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Country.tmdl` | 46 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Country.tmdl` | 55 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Country.tmdl` | 64 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Country.tmdl` | 73 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/KPI.tmdl` | 64 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/KPI.tmdl` | 73 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/KPI.tmdl` | 82 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/KPI.tmdl` | 91 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/KPI.tmdl` | 100 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Monthly.tmdl` | 28 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Monthly.tmdl` | 37 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Monthly.tmdl` | 64 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Pareto.tmdl` | 37 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Pareto.tmdl` | 55 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Pareto.tmdl` | 64 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/RFM.tmdl` | 55 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/RFM.tmdl` | 64 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Returns.tmdl` | 82 | `dataType: doublePrecision` | `dataType: double` |
| `powerbi/Meridian.SemanticModel/definition/tables/Returns.tmdl` | 91 | `dataType: doublePrecision` | `dataType: double` |
| `scripts/generate_pbip.py` | 344 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 415 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 416 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 417 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 418 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 419 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 437 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 438 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 441 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 456 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 457 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 458 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 459 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 475 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 476 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 494 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 497 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 510 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 512 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 513 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 532 | `doublePrecision` | `double` |
| `scripts/generate_pbip.py` | 533 | `doublePrecision` | `double` |

## Mapping applied
- `doublePrecision` → `double` (TOM `DataType.Double`; TMDL keyword `double`)

## Post-fix validation
- All `dataType:` values are in the TMDL set: string, int64, double, decimal, dateTime, boolean, binary, unknown, variant.
- All `summarizeBy:` values are valid.

