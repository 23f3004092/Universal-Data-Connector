
from typing import List, Dict, Any


def identify_data_type(data: List[Dict[str, Any]]) -> str:
    if not data:
        return "unknown"

    sample = data[0]

    # Detect hierarchical / nested structures
    if any(isinstance(v, (dict, list)) for v in sample.values()):
        return "hierarchical"

    # Detect time-series / analytics
    if "date" in sample and ("metric" in sample or "value" in sample):
        return "time_series"

    # Detect connector-specific tabular schemas
    if "email" in sample and ("customer_id" in sample or "name" in sample):
        return "tabular_crm"
    if "ticket_id" in sample and ("priority" in sample or "subject" in sample):
        return "tabular_support"

    return "generic"
