"""
Shared pipeline status writer for MTIC agents.

Each agent calls update_status(agent, vc_id, payload) at the end of its run.
Reads and writes data/pipeline_status.json — a single file that the dashboard
Pipeline tab fetches at runtime to show the current state of the pipeline.

Schema:
{
  "updated_at": "ISO-8601",
  "chains": {
    "VC01": {
      "name": "Iron & Steel",
      "ingest":    { ... agent-specific payload ... },
      "synthesise": { ... },
      "review":    { ... }
    }
  }
}
"""

import json, datetime
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent
STATUS_FILE = ROOT / 'data' / 'pipeline_status.json'

VC_NAMES = {
    'VC01': 'Iron & Steel',
    'VC02': 'Copper & Allied Metals',
    'VC03': 'Automotive',
    'VC04': 'Textiles & Garments',
    'VC05': 'Pharmaceuticals',
    'VC06': 'Petrochemicals & Fertilizers',
    'VC07': 'Sugar & Confectionery',
    'VC08': 'Plastics & Packaging',
    'VC09': 'Cement & Building Materials',
}


def update_status(agent: str, vc_id: str, payload: dict):
    """
    agent   — 'ingest' | 'synthesise' | 'review'
    vc_id   — e.g. 'VC01'
    payload — dict of agent-specific status fields (no timestamp needed)
    """
    status = _load()

    chain = status['chains'].setdefault(vc_id, {'name': VC_NAMES.get(vc_id, vc_id)})
    chain[agent] = {
        'timestamp': datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        **payload,
    }
    status['updated_at'] = datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z'

    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding='utf-8')


def _load() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text('utf-8'))
        except json.JSONDecodeError:
            pass
    return {'updated_at': '', 'chains': {}}
