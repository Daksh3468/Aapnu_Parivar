from typing import List, Optional, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db

router = APIRouter(tags=["AI Welfare Assistant Chatbot"])


class ChatbotQueryPayload(BaseModel):
    query: str = Field(..., min_length=1, description="Citizen or officer prompt")
    family_id: Optional[str] = Field(None, description="Optional active family ID context")


class ActionChip(BaseModel):
    label: str
    action_type: str  # NAVIGATE, QUICK_QUERY
    value: str


class ChatbotQueryResponse(BaseModel):
    reply: str
    suggested_actions: List[ActionChip] = []
    category: str


@router.post("/chatbot/query", response_model=ChatbotQueryResponse)
def handle_chatbot_query(payload: ChatbotQueryPayload, db: Session = Depends(get_db)):
    """
    Demo AI Welfare Assistant ('Aapnu Mitra' / આપણું મિત્ર) query endpoint.
    Provides instant intelligent guidance on schemes, family ID, division splits, login, and documents.
    """
    q = payload.query.strip().lower()

    if any(k in q for k in ["scheme", "eligible", "entitlement", "benefit", "yojana", "યોજના", "પાત્રતા"]):
        reply = (
            "Namaste! 🙏 In **Aapnu Parivar**, scheme eligibility is evaluated automatically based on your household's "
            "verified income band, ration card type, land holdings, social category, and active document certificates. "
            "You can explore all active Gujarat & Central welfare schemes or view your tailored entitlement matches."
        )
        actions = [
            ActionChip(label="Explore Schemes", action_type="NAVIGATE", value="/schemes"),
            ActionChip(label="Check My Entitlements", action_type="NAVIGATE", value="/my-family"),
        ]
        category = "SCHEMES"

    elif any(k in q for k in ["split", "divide", "separate", "division", "વિભાજન", "જુદા"]):
        reply = (
            "You can divide your household into a new nuclear family identity using our 4-Step **Household Split Wizard**. "
            "Select moving members, assign a new Head of Household, and provide address details. "
            "Low-risk splits (Anomaly Score ≤ 50) are instantly auto-approved with a new 12-digit Family ID!"
        )
        actions = [
            ActionChip(label="Open Household Split Wizard", action_type="NAVIGATE", value="/my-family?action=split"),
        ]
        category = "FAMILY_SPLIT"

    elif any(k in q for k in ["family id", "id", "verhoeff", "12 digit", "નંબર", "આઈડી"]):
        fid_context = f" (Your Family ID: **{payload.family_id}**)" if payload.family_id else ""
        reply = (
            f"The **Gujarat Family ID**{fid_context} is a 12-digit structured identity formatted as `GJ-DD-YY-SSSSSSS-C`, "
            "protected by a mathematical Verhoeff check-digit. It links all household members to a single welfare profile."
        )
        actions = [
            ActionChip(label="View Household Profile", action_type="NAVIGATE", value="/my-family"),
        ]
        category = "FAMILY_ID"

    elif any(k in q for k in ["login", "password", "sign in", "register", "પાસવર્ડ", "લોગિન"]):
        reply = (
            "You can log in via our **Unified Common Portal** using your 10-digit Head Mobile Number or Official Email. "
            "Initial passwords can be set during family registration and updated anytime under your Household Profile via 'Change Password'."
        )
        actions = [
            ActionChip(label="Go to Sign In", action_type="NAVIGATE", value="/login"),
            ActionChip(label="Register New Household", action_type="NAVIGATE", value="/register"),
        ]
        category = "AUTH"

    elif any(k in q for k in ["document", "aadhaar", "income", "caste", "vault", "certificate", "પ્રમાણપત્ર"]):
        reply = (
            "Your **Document Vault** securely stores e-KYC verified Aadhaar tokens, Income Certificates, Ration Cards, and Caste Certificates. "
            "Verified documents enable 100% paperless automated scheme approvals."
        )
        actions = [
            ActionChip(label="Open Document Vault", action_type="NAVIGATE", value="/my-family"),
        ]
        category = "DOCUMENTS"

    elif any(k in q for k in ["status", "application", "track", "progress", "અરજી"]):
        reply = (
            "You can track real-time application progression (SUBMITTED → PENDING_OFFICER_REVIEW → APPROVED) "
            "under your Household Applications tab. Officers review pending applications within designated district jurisdictions."
        )
        actions = [
            ActionChip(label="Track Applications", action_type="NAVIGATE", value="/my-family"),
        ]
        category = "APPLICATIONS"

    else:
        reply = (
            "Namaste! 🙏 I am **Aapnu Mitra (આપણું મિત્ર)**, your AI Welfare Assistant for Gujarat State. "
            "I can help you check scheme eligibility, guide household splits, locate your 12-digit Family ID, or manage your document vault. "
            "How can I assist you today?"
        )
        actions = [
            ActionChip(label="What schemes am I eligible for?", action_type="QUICK_QUERY", value="What schemes am I eligible for?"),
            ActionChip(label="How do I split my family?", action_type="QUICK_QUERY", value="How do I split my family?"),
            ActionChip(label="What is Gujarat Family ID?", action_type="QUICK_QUERY", value="What is Gujarat Family ID?"),
        ]
        category = "GENERAL"

    return ChatbotQueryResponse(
        reply=reply,
        suggested_actions=actions,
        category=category,
    )
