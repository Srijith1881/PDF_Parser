# validate.py
from typing import List, Dict
import pandas as pd
from schema import validate_item, TOC_SCHEMA, SECTION_SCHEMA, METADATA_SCHEMA
import logging

logger = logging.getLogger(__name__)

def validate_toc_vs_sections(toc_data: List[Dict], sections_data: List[Dict], metadata_data: List[Dict] = None) -> Dict:
    """
    Compares ToC data with actual parsed sections.
    Returns mismatch counts, missing sections, and ordering issues.
    """
    results = {}
    toc_ids = [t['section_id'] for t in toc_data]
    sec_ids = [s['section_id'] for s in sections_data]

    # Schema validation counts
    toc_schema_failures = []
    for t in toc_data:
        ok, err = validate_item(t, TOC_SCHEMA)
        if not ok:
            toc_schema_failures.append({"item": t, "error": err})
    sec_schema_failures = []
    for s in sections_data:
        ok, err = validate_item(s, SECTION_SCHEMA)
        if not ok:
            sec_schema_failures.append({"item": s, "error": err})
    metadata_schema_failures = []
    if metadata_data:
        for m in metadata_data:
            ok, err = validate_item(m, METADATA_SCHEMA)
            if not ok:
                metadata_schema_failures.append({"item": m, "error": err})

    # Missing sections: in ToC but not extracted
    missing_sections = sorted(list(set(toc_ids) - set(sec_ids)))

    # Extra sections: present in parsed but not in ToC
    extra_sections = sorted(list(set(sec_ids) - set(toc_ids)))

    # Order check: compare sorted order by section_id
    def sort_key(ids):
        def to_tuple(s):
            return tuple(int(x) for x in s.split('.'))
        return sorted(ids, key=to_tuple)

    toc_sorted = sort_key(toc_ids)
    sec_sorted = sort_key(sec_ids)

    ordering_mismatch = toc_sorted != sec_sorted

    # Table count match (if metadata data contains type 'table' and ToC has references—this is heuristic)
    toc_table_count = 0
    for t in toc_data:
        if t['title'].lower().startswith('table') or 'table' in t['title'].lower():
            toc_table_count += 1
    metadata_table_count = 0
    if metadata_data:
        metadata_table_count = sum(1 for m in metadata_data if m.get('type') == 'table')

    results['summary'] = {
        "toc_count": len(toc_data),
        "sections_count": len(sections_data),
        "metadata_count": len(metadata_data) if metadata_data is not None else 0,
        "missing_sections_count": len(missing_sections),
        "extra_sections_count": len(extra_sections),
        "ordering_mismatch": ordering_mismatch,
        "toc_table_count": toc_table_count,
        "metadata_table_count": metadata_table_count
    }
    results['missing_sections'] = missing_sections
    results['extra_sections'] = extra_sections
    results['toc_schema_failures'] = toc_schema_failures
    results['section_schema_failures'] = sec_schema_failures
    results['metadata_schema_failures'] = metadata_schema_failures
    return results

def generate_excel_report(validation_results: Dict, output_path: str) -> None:
    """
    Writes validation results into an Excel file with multiple sheets.
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary
        summary = validation_results.get('summary', {})
        pd.DataFrame([summary]).to_excel(writer, sheet_name='Summary', index=False)

        # Missing/Extra
        pd.DataFrame(validation_results.get('missing_sections', []), columns=['missing_section_id']).to_excel(
            writer, sheet_name='MissingSections', index=False
        )
        pd.DataFrame(validation_results.get('extra_sections', []), columns=['extra_section_id']).to_excel(
            writer, sheet_name='ExtraSections', index=False
        )

        # Failures
        def failures_to_df(fails):
            rows = []
            for f in fails:
                item = f.get('item')
                err = f.get('error')
                rows.append({
                    "item_id": (item or {}).get('section_id') if item else None,
                    "error": err,
                    "item_preview": str(item)[:400]
                })
            return pd.DataFrame(rows)

        failures_to_df(validation_results.get('toc_schema_failures', [])).to_excel(
            writer, sheet_name='ToC_Schema_Failures', index=False
        )
        failures_to_df(validation_results.get('section_schema_failures', [])).to_excel(
            writer, sheet_name='Section_Schema_Failures', index=False
        )
        failures_to_df(validation_results.get('metadata_schema_failures', [])).to_excel(
            writer, sheet_name='Metadata_Schema_Failures', index=False
        )

    logger.info("Validation report saved to %s", output_path)