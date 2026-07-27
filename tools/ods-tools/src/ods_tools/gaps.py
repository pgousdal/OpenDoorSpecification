from __future__ import annotations

import json
from pathlib import Path

from .semantic import load_operations


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def build_adapter_gap_report(root: Path) -> dict:
    operations_doc = load_operations(root)
    operations = [item['id'] for item in operations_doc['operations']]

    historical = []
    for path in sorted((root / 'catalog' / 'mappings').glob('*.json')):
        data = _load_json(path)
        mapping_by_operation = {item['operation']: item for item in data['mappings']}
        rows = []
        for operation in operations:
            mapping = mapping_by_operation.get(operation)
            if mapping is None:
                status = 'missing'
                symbols = []
            else:
                status = 'supported' if mapping['status'] == 'verified' else 'partial'
                symbols = mapping['symbols']
            rows.append({'operation': operation, 'status': status, 'symbols': symbols})
        historical.append({
            'id': data['api'],
            'kind': 'historical-api',
            'rows': rows,
            'summary': _summarize(rows),
        })

    adapters = []
    for path in sorted((root / 'catalog' / 'adapters').glob('*.json')):
        data = _load_json(path)
        adapter_id = data.get('id', data.get('adapter'))
        supported = set(data['operations'])
        rows = [
            {'operation': operation, 'status': 'supported' if operation in supported else 'missing'}
            for operation in operations
        ]
        adapters.append({
            'id': adapter_id,
            'kind': data.get('kind', 'historical-adapter'),
            'implementation': data['implementation'],
            'conformance': data.get('conformance', 'unspecified'),
            'rows': rows,
            'summary': _summarize(rows),
        })

    all_targets = [*historical, *adapters]
    return {
        'schema_version': 1,
        'spec_version': operations_doc['spec_version'],
        'operations': operations,
        'historical_apis': historical,
        'adapters': adapters,
        'summary': {
            'operation_count': len(operations),
            'historical_api_count': len(historical),
            'adapter_count': len(adapters),
            'complete_targets': sum(item['summary']['missing'] == 0 and item['summary']['partial'] == 0 for item in all_targets),
        },
    }


def _summarize(rows: list[dict]) -> dict:
    return {
        'supported': sum(row['status'] == 'supported' for row in rows),
        'partial': sum(row['status'] == 'partial' for row in rows),
        'missing': sum(row['status'] == 'missing' for row in rows),
    }


def write_adapter_gap_report(root: Path, destination: Path | None = None) -> dict:
    report = build_adapter_gap_report(root)
    target = destination or root / 'catalog' / 'knowledge' / 'adapter-gap-report.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report
