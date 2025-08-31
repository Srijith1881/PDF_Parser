from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd

from .schema import METADATA_SCHEMA, SECTION_SCHEMA, TOC_SCHEMA, validate_item


@dataclass
class Validator:
    def validate(
        self, toc: List[Dict], sections: List[Dict], metadata: List[Dict] | None = None
    ) -> Dict:
        toc_ids = [t["section_id"] for t in toc]
        sec_ids = [s["section_id"] for s in sections]

        toc_fail = self._collect_schema_failures(toc, TOC_SCHEMA, id_key="section_id")
        sec_fail = self._collect_schema_failures(sections, SECTION_SCHEMA, id_key="section_id")
        meta_fail: List[Dict] = []
        if metadata:
            meta_fail = self._collect_schema_failures(metadata, METADATA_SCHEMA, id_key="id")

        missing = sorted(list(set(toc_ids) - set(sec_ids)), key=self._sort_key)
        extra = sorted(list(set(sec_ids) - set(toc_ids)), key=self._sort_key)
        ordering_mismatch = self._ordering_mismatch(toc_ids, sec_ids)

        toc_table_count = sum(1 for t in toc if "table" in t["title"].lower())
        metadata_table_count = sum(1 for m in (metadata or []) if m.get("type") == "table")

        return {
            "summary": {
                "toc_count": len(toc),
                "sections_count": len(sections),
                "metadata_count": len(metadata or []),
                "missing_sections_count": len(missing),
                "extra_sections_count": len(extra),
                "ordering_mismatch": ordering_mismatch,
                "toc_table_count": toc_table_count,
                "metadata_table_count": metadata_table_count,
            },
            "missing_sections": missing,
            "extra_sections": extra,
            "toc_schema_failures": toc_fail,
            "section_schema_failures": sec_fail,
            "metadata_schema_failures": meta_fail,
        }

    def write_excel_report(self, results: Dict, output_path: str) -> None:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            pd.DataFrame([results.get("summary", {})]).to_excel(
                writer, sheet_name="Summary", index=False
            )
            pd.DataFrame(results.get("missing_sections", []), columns=["missing_section_id"]).to_excel(
                writer, sheet_name="MissingSections", index=False
            )
            pd.DataFrame(results.get("extra_sections", []), columns=["extra_section_id"]).to_excel(
                writer, sheet_name="ExtraSections", index=False
            )

            def failures_to_df(fails: List[Dict]) -> pd.DataFrame:
                rows: List[Dict] = []
                for f in fails:
                    item = f.get("item")
                    err = f.get("error")
                    rows.append(
                        {
                            "item_id": (item or {}).get("section_id")
                            or (item or {}).get("id"),
                            "error": err,
                            "item_preview": str(item)[:400],
                        }
                    )
                return pd.DataFrame(rows)

            failures_to_df(results.get("toc_schema_failures", [])).to_excel(
                writer, sheet_name="ToC_Schema_Failures", index=False
            )
            failures_to_df(results.get("section_schema_failures", [])).to_excel(
                writer, sheet_name="Section_Schema_Failures", index=False
            )
            failures_to_df(results.get("metadata_schema_failures", [])).to_excel(
                writer, sheet_name="Metadata_Schema_Failures", index=False
            )

    # ---------- helpers ----------
    @staticmethod
    def _collect_schema_failures(items: List[Dict], schema: Dict, id_key: str) -> List[Dict]:
        fails: List[Dict] = []
        for it in items:
            ok, err = validate_item(it, schema)
            if not ok:
                fails.append({"item": it, "error": err, "id": it.get(id_key)})
        return fails

    @staticmethod
    def _ordering_mismatch(toc_ids: List[str], sec_ids: List[str]) -> bool:
        def parse(s: str) -> Tuple[int, ...]:
            return tuple(int(x) for x in s.split("."))

        return sorted(toc_ids, key=parse) != sorted(sec_ids, key=parse)

    @staticmethod
    def _sort_key(s: str) -> Tuple[int, ...]:
        return tuple(int(x) for x in s.split("."))
