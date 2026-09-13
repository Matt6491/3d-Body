
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import RLock
from typing import Any
import uuid

class BodyRepository(ABC):
    @abstractmethod
    def save_body(self, account_ref:str|None, body:dict, profile:dict)->str: ...
    @abstractmethod
    def get_body(self, body_id:str)->dict|None: ...
    @abstractmethod
    def delete_body(self, body_id:str)->bool: ...
    @abstractmethod
    def save_analysis(self, account_ref:str|None, analysis:dict)->str: ...
    @abstractmethod
    def delete_analysis(self, analysis_id:str)->bool: ...
    @abstractmethod
    def delete_account_data(self, account_ref:str)->dict: ...

class InMemoryBodyRepository(BodyRepository):
    """Ephemeral local-development repository.

    Original image bytes are never accepted by this repository. This makes the local
    default privacy behavior safer: only derived measurements and body parameters exist.
    """
    def __init__(self):
        self._lock=RLock(); self.bodies={}; self.analyses={}
    def save_body(self, account_ref, body, profile):
        key=str(uuid.uuid4())
        with self._lock:self.bodies[key]={"accountRef":account_ref,"mesh":body,"profile":profile}
        return key
    def get_body(self,body_id):
        with self._lock:return self.bodies.get(body_id)
    def delete_body(self,body_id):
        with self._lock:return self.bodies.pop(body_id,None) is not None
    def save_analysis(self,account_ref,analysis):
        key=str(uuid.uuid4())
        with self._lock:self.analyses[key]={"accountRef":account_ref,"analysis":analysis}
        return key
    def delete_analysis(self,analysis_id):
        with self._lock:return self.analyses.pop(analysis_id,None) is not None
    def delete_account_data(self,account_ref):
        with self._lock:
            bs=[k for k,v in self.bodies.items() if v["accountRef"]==account_ref]
            an=[k for k,v in self.analyses.items() if v["accountRef"]==account_ref]
            for k in bs:self.bodies.pop(k,None)
            for k in an:self.analyses.pop(k,None)
        return {"bodies":len(bs),"analyses":len(an)}

class SupabaseBodyRepository(BodyRepository):
    """Production adapter boundary.

    Intentionally not activated without credentials. A production implementation should:
    - use a service-role credential only server-side;
    - enforce RLS for end-user access;
    - place photos in a private bucket;
    - issue short-lived signed URLs;
    - split account identity from body-analysis tables;
    - run automatic photo deletion jobs.
    """
    def __init__(self,*_,**__):
        raise RuntimeError("Supabase adapter requires deployment credentials and the supabase client; use InMemoryBodyRepository locally.")
    def save_body(self,*a,**k): raise NotImplementedError
    def get_body(self,*a,**k): raise NotImplementedError
    def delete_body(self,*a,**k): raise NotImplementedError
    def save_analysis(self,*a,**k): raise NotImplementedError
    def delete_analysis(self,*a,**k): raise NotImplementedError
    def delete_account_data(self,*a,**k): raise NotImplementedError
