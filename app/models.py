from sqlalchemy import Column, Integer, String
from .db import Base

class SheetData(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String)
    email_address = Column(String)
    queue_name = Column(String)
    extension_id = Column(String)
    extension_title = Column(String)
    extension_functionality = Column(String)
    revision_id = Column(String)
    dcr_link = Column(String)
    change_in_verdict = Column(String)
    score_logs_triggered  = Column(String)
    sensitive_permissions_requested  = Column(String)
    external_calls_unsafe_eval = Column(String)
    content_scripts = Column(String)
    web_sockets = Column(String)
    action_taken = Column(String)
    escalation_approved_by = Column(String)
    reason_for_escalation = Column(String)
    l0_verdict = Column(String)
    verdict = Column(String)
    teamlead= Column(String)
    code_comparison = Column(String)
    web_APIs = Column(String)
    Escalation_Approved_by_L1 = Column(String)
    Escalation_Reason_Sub_category = Column(String)


