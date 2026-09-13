import uuid
from dataclasses import dataclass
from typing import Dict, Optional, Any

@dataclass
class StoredBody:
    account_ref: Optional[str]
    mesh: Dict[str, Any]
    profile: Dict[str, Any]

@dataclass
class StoredAnalysis:
    account_ref: Optional[str]
    analysis: Dict[str, Any]

class InMemoryBodyRepository:
    def __init__(self):
        self._bodies: Dict[str, StoredBody] = {}
        self._analyses: Dict[str, StoredAnalysis] = {}

    def save_body(self, account_ref: Optional[str], body: Dict[str, Any], profile: Dict[str, Any]) -> str:
        key = str(uuid.uuid4())
        self._bodies[key] = StoredBody(account_ref=account_ref, mesh=body, profile=profile)
        return key

    def get_body(self, body_id: str) -> Optional[StoredBody]:
        return self._bodies.get(body_id)

    def delete_body(self, body_id: str) -> bool:
        return self._bodies.pop(body_id, None) is not None

    def save_analysis(self, account_ref: Optional[str], analysis: Dict[str, Any]) -> str:
        key = str(uuid.uuid4())
        self._analyses[key] = StoredAnalysis(account_ref=account_ref, analysis=analysis)
        return key

    def delete_analysis(self, analysis_id: str) -> bool:
        return self._analyses.pop(analysis_id, None) is not None

    def delete_account_data(self, account_ref: str) -> Dict[str, int]:
        b = [k for k, v in self._bodies.items() if v.account_ref == account_ref]
        a = [k for k, v in self._analyses.items() if v.account_ref == account_ref]
        for k in b: del self._bodies[k]
        for k in a: del self._analyses[k]
        return {"bodies": len(b), "analyses": len(a)}
