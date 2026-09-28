from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import re
import math


router = APIRouter(prefix="/chat", tags=["Chatbot"])


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str

    # Conversation history from frontend
    history: List[Dict[str, Any]] = Field(default_factory=list)

    # User context
    profile: Dict[str, Any] = Field(default_factory=dict)

    # Application context
    applications: List[Dict[str, Any]] = Field(default_factory=list)

    # Optional scheme data
    schemes: List[Dict[str, Any]] = Field(default_factory=list)

    # Optional documents
    documents: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================
# HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def money(value):
    if value is None or value == "":
        return "Not provided"

    try:
        return f"₹{float(value):,.0f}"
    except Exception:
        return str(value)


def get_value(data, *keys, default=None):
    """
    Safely get the first available value.
    """

    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if value not in [None, "", []]:
            return value

    return default


def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        text.lower().strip()
    )


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(message: str):

    text = normalize(message)

    # Greeting
    if any(x in text for x in [
        "hello",
        "hi",
        "hey",
        "hii",
        "good morning",
        "good afternoon",
        "good evening"
    ]):
        return "greeting"

    # About SchemeSahay
    if any(x in text for x in [
        "what is schemeSahay",
        "what is scheme Sahay",
        "about schemeSahay",
        "about scheme Sahay",
        "what can you do",
        "who are you"
    ]):
        return "about"

    # Profile
    if any(x in text for x in [
        "my profile",
        "profile status",
        "profile details",
        "profile complete",
        "profile completion",
        "what is missing in my profile",
        "profile missing"
    ]):
        return "profile"

    # Application
    if any(x in text for x in [
        "application status",
        "my application",
        "my applications",
        "track application",
        "track my application",
        "application tracking",
        "submitted application",
        "application progress"
    ]):
        return "applications"

    # Documents
    if any(x in text for x in [
        "document",
        "documents",
        "certificate",
        "aadhaar",
        "aadhar",
        "proof",
        "paperwork",
        "what should i upload",
        "what do i need to upload"
    ]):
        return "documents"

    # Eligibility
    if any(x in text for x in [
        "eligible",
        "eligibility",
        "qualify",
        "qualification",
        "criteria",
        "can i apply",
        "am i eligible",
        "do i qualify"
    ]):
        return "eligibility"

    # Scheme discovery
    if any(x in text for x in [
        "scheme",
        "schemes",
        "government scheme",
        "government schemes",
        "which scheme",
        "find scheme",
        "find schemes",
        "scheme for me",
        "scheme can help",
        "loan scheme",
        "subsidy",
        "scholarship",
        "government support"
    ]):
        return "schemes"

    # Business
    if any(x in text for x in [
        "business",
        "startup",
        "start a business",
        "small business",
        "entrepreneur",
        "shop",
        "enterprise"
    ]):
        return "business"

    # Financial
    if any(x in text for x in [
        "emi",
        "loan",
        "repayment",
        "interest",
        "financial",
        "finance",
        "loan amount",
        "calculate loan",
        "monthly payment",
        "monthly emi",
        "interest rate"
    ]):
        return "finance"

    # Partners
    if any(x in text for x in [
        "partner",
        "partners",
        "where can i apply",
        "where should i apply",
        "bank",
        "csc",
        "assistance centre",
        "assistance channel"
    ]):
        return "partners"

    # Simulator
    if any(x in text for x in [
        "simulator",
        "simulate",
        "what if",
        "what-if",
        "scenario"
    ]):
        return "simulator"

    return "general"


# ============================================================
# PROFILE ANALYSIS
# ============================================================

def analyze_profile(profile):

    if not profile:
        return {
            "available": False,
            "missing": [],
            "completion": 0
        }

    important_fields = {
        "age": "Age",
        "state": "State",
        "district": "District",
        "category": "Category",
        "income": "Annual income",
        "occupation": "Occupation",
        "education": "Education",
        "employment_status": "Employment status",
        "business_type": "Business type",
        "project_cost": "Project cost",
        "required_loan": "Required loan"
    }

    missing = []
    filled = 0

    for key, label in important_fields.items():

        value = profile.get(key)

        if value in [None, "", []]:
            missing.append(label)
        else:
            filled += 1

    completion = round(
        (filled / len(important_fields)) * 100
    )

    return {
        "available": True,
        "missing": missing,
        "completion": completion
    }


# ============================================================
# APPLICATION ANALYSIS
# ============================================================

def analyze_applications(applications):

    if not applications:
        return {
            "count": 0,
            "submitted": 0,
            "draft": 0,
            "other": 0
        }

    submitted = 0
    draft = 0
    other = 0

    for app in applications:

        status = normalize(
            str(app.get("status", ""))
        )

        if "submitted" in status:
            submitted += 1

        elif "draft" in status:
            draft += 1

        else:
            other += 1

    return {
        "count": len(applications),
        "submitted": submitted,
        "draft": draft,
        "other": other
    }


# ============================================================
# SCHEME MATCHING
# ============================================================

def score_scheme(scheme, profile, message):

    score = 0

    text = normalize(message)

    scheme_text = " ".join([
        clean(scheme.get("name")),
        clean(scheme.get("description")),
        clean(scheme.get("category")),
        clean(scheme.get("benefit_amount"))
    ]).lower()

    # Keyword relevance
    keywords = [
        "business",
        "loan",
        "startup",
        "scholarship",
        "student",
        "farmer",
        "agriculture",
        "women",
        "education",
        "employment",
        "subsidy",
        "housing",
        "skill",
        "training"
    ]

    for keyword in keywords:

        if keyword in text and keyword in scheme_text:
            score += 3

    # Profile category
    category = clean(
        profile.get("category")
    ).lower()

    if category and category in scheme_text:
        score += 3

    # Occupation
    occupation = clean(
        profile.get("occupation")
    ).lower()

    if occupation and occupation in scheme_text:
        score += 2

    # Business
    business = clean(
        profile.get("business_type")
    ).lower()

    if business and business in scheme_text:
        score += 2

    return score


def find_matching_schemes(
    schemes,
    profile,
    message
):

    if not schemes:
        return []

    scored = []

    for scheme in schemes:

        if not isinstance(scheme, dict):
            continue

        score = score_scheme(
            scheme,
            profile,
            message
        )

        if score > 0:
            scored.append(
                (score, scheme)
            )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        scheme
        for score, scheme in scored[:5]
    ]


# ============================================================
# FINANCIAL CALCULATOR
# ============================================================

def calculate_emi(
    principal,
    annual_rate,
    months
):

    try:

        principal = float(principal)
        annual_rate = float(annual_rate)
        months = int(months)

        if principal <= 0 or months <= 0:
            return None

        monthly_rate = (
            annual_rate / 12 / 100
        )

        if monthly_rate == 0:

            emi = principal / months

        else:

            emi = (
                principal
                * monthly_rate
                * (1 + monthly_rate) ** months
            ) / (
                (1 + monthly_rate) ** months - 1
            )

        total = emi * months

        interest = total - principal

        return {
            "emi": emi,
            "interest": interest,
            "total": total
        }

    except Exception:
        return None


def extract_financial_values(message):

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        message.replace(",", "")
    )

    if not numbers:
        return None

    values = [float(x) for x in numbers]

    return values


# ============================================================
# RESPONSE GENERATORS
# ============================================================

def greeting_response():

    return (
        "Hi! 👋 I'm your SchemeSahay Assistant.\n\n"
        "I can help you with:\n"
        "🔎 Finding relevant government schemes\n"
        "✅ Understanding eligibility\n"
        "📄 Required documents\n"
        "👤 Your SchemeSahay profile\n"
        "📋 Application tracking\n"
        "💰 Loan and EMI calculations\n"
        "📍 Assistance channels\n\n"
        "Try asking me something like:\n"
        "\"Which schemes can help me start a small business?\""
    )


def about_response():

    return (
        "SchemeSahay is an AI-assisted government scheme discovery "
        "and application-readiness platform.\n\n"
        "The platform helps users move through the journey:\n\n"
        "1️⃣ Discover schemes\n"
        "2️⃣ Match schemes to their needs\n"
        "3️⃣ Understand eligibility\n"
        "4️⃣ Verify supporting evidence\n"
        "5️⃣ Identify missing documents\n"
        "6️⃣ Simulate financial scenarios\n"
        "7️⃣ Find assistance channels\n"
        "8️⃣ Prepare an application\n"
        "9️⃣ Track the application\n\n"
        "I'm the assistant layer that helps you navigate this journey."
    )


def profile_response(profile):

    analysis = analyze_profile(profile)

    if not analysis["available"]:

        return (
            "I couldn't access your profile information right now.\n\n"
            "Please open **My Profile** and add your details."
        )

    completion = analysis["completion"]
    missing = analysis["missing"]

    reply = (
        f"👤 **Your SchemeSahay Profile**\n\n"
        f"Profile completeness: **{completion}%**\n\n"
    )

    if missing:

        reply += (
            "Information that may still be useful:\n"
            + "\n".join(
                f"• {item}"
                for item in missing[:7]
            )
            + "\n\n"
            "Adding these details can improve scheme matching."
        )

    else:

        reply += (
            "✅ Your main profile information is filled in.\n\n"
            "You can now use **Schemes** to discover potentially "
            "relevant schemes."
        )

    return reply


def applications_response(applications):

    analysis = analyze_applications(
        applications
    )

    if analysis["count"] == 0:

        return (
            "📋 You don't have any applications available "
            "in your SchemeSahay account yet.\n\n"
            "You can start from **Schemes → View Eligibility → Apply**."
        )

    reply = (
        f"📋 You currently have **{analysis['count']} application(s)**.\n\n"
        f"• Submitted: {analysis['submitted']}\n"
        f"• Draft: {analysis['draft']}\n"
        f"• Other statuses: {analysis['other']}\n\n"
    )

    reply += "Your application details:\n"

    for app in applications[:5]:

        name = get_value(
            app,
            "scheme",
            "scheme_name",
            "name",
            default="Application"
        )

        status = get_value(
            app,
            "status",
            default="Unknown"
        )

        reply += (
            f"• **{name}** — {status}\n"
        )

    return reply


def documents_response(documents, profile):

    if documents:

        completed = 0
        processing = 0

        for doc in documents:

            status = normalize(
                str(doc.get("ocr_status", ""))
            )

            if status == "completed":
                completed += 1
            elif status:
                processing += 1

        return (
            "📄 **Your Documents**\n\n"
            f"Documents available: **{len(documents)}**\n"
            f"Processed: **{completed}**\n"
            f"Processing/other: **{processing}**\n\n"
            "Open **Documents** to review your uploaded records."
        )

    return (
        "📄 SchemeSahay can help organize supporting documents such as:\n\n"
        "• Aadhaar / identity proof\n"
        "• Caste certificate\n"
        "• Income certificate\n"
        "• Address proof\n"
        "• Bank passbook\n"
        "• Project or course documents\n\n"
        "The exact documents depend on the scheme, so always "
        "verify the scheme's official requirements before submission."
    )


def scheme_response(
    message,
    schemes,
    profile
):

    matches = find_matching_schemes(
        schemes,
        profile,
        message
    )

    if not matches:

        return (
            "🔎 I can help you find a suitable scheme.\n\n"
            "Tell me what you're trying to do, for example:\n\n"
            "• Start a small business\n"
            "• Get a business loan\n"
            "• Pay for education\n"
            "• Get a scholarship\n"
            "• Improve agricultural income\n"
            "• Get training or employment support\n\n"
            "For a more precise match, also tell me your "
            "state, occupation and approximate income."
        )

    reply = (
        "🔎 **Potentially Relevant Schemes**\n\n"
        "Based on the information available to SchemeSahay, "
        "these records may be relevant:\n\n"
    )

    for index, scheme in enumerate(matches, 1):

        name = get_value(
            scheme,
            "name",
            "scheme_name",
            default="Scheme"
        )

        description = get_value(
            scheme,
            "description",
            default=""
        )

        benefit = get_value(
            scheme,
            "benefit_amount",
            default=""
        )

        reply += f"**{index}. {name}**\n"

        if description:
            reply += f"{description}\n"

        if benefit:
            reply += f"Benefit: {benefit}\n"

        reply += "\n"

    reply += (
        "⚠️ These are potential matches, not a final eligibility "
        "decision. Open the scheme and use **Check Eligibility** "
        "and **Readiness Check** before applying."
    )

    return reply


def eligibility_response(profile):

    analysis = analyze_profile(profile)

    if not analysis["available"]:

        return (
            "✅ To assess eligibility, SchemeSahay needs your profile "
            "information such as age, state, category, income and occupation.\n\n"
            "Please complete **My Profile** first."
        )

    if analysis["missing"]:

        return (
            "✅ SchemeSahay can perform evidence-based eligibility checks "
            "for individual schemes.\n\n"
            f"Your profile is currently about **{analysis['completion']}%** "
            "complete.\n\n"
            "Some useful information is still missing:\n"
            + "\n".join(
                f"• {item}"
                for item in analysis["missing"][:6]
            )
            + "\n\n"
            "Open a specific scheme and select **Check Eligibility** "
            "for the actual rule-based result."
        )

    return (
        "✅ Your main profile information is available.\n\n"
        "For a reliable result, open the specific scheme and select "
        "**Check Eligibility**. SchemeSahay compares your profile "
        "against the scheme's structured rules and evidence.\n\n"
        "I can help explain the result once you have it."
    )


def business_response(
    message,
    schemes,
    profile
):

    matches = find_matching_schemes(
        schemes,
        profile,
        message
    )

    if matches:

        return scheme_response(
            message,
            matches,
            profile
        )

    return (
        "🏪 Starting a small business usually involves looking at "
        "financing, subsidies, training and application requirements.\n\n"
        "SchemeSahay can help you:\n"
        "1. Find potentially relevant schemes\n"
        "2. Compare their requirements\n"
        "3. Check your profile against eligibility rules\n"
        "4. Identify supporting documents\n"
        "5. Simulate loan repayment\n"
        "6. Find assistance channels\n\n"
        "Tell me your business type and approximate project cost "
        "and I can narrow the search."
    )


def finance_response(message, profile):

    values = extract_financial_values(message)

    # Try to infer a simple EMI request:
    # Example: EMI for 200000 at 10% for 3 years
    if values and len(values) >= 3:

        principal = values[0]
        rate = values[1]
        years = values[2]

        months = int(years * 12)

        result = calculate_emi(
            principal,
            rate,
            months
        )

        if result:

            return (
                "💰 **Estimated Loan Scenario**\n\n"
                f"Loan amount: **{money(principal)}**\n"
                f"Annual interest: **{rate}%**\n"
                f"Tenure: **{years:g} years**\n\n"
                f"Estimated EMI: **{money(result['emi'])}/month**\n"
                f"Estimated interest: **{money(result['interest'])}**\n"
                f"Estimated repayment: **{money(result['total'])}**\n\n"
                "This is an estimate for planning purposes. "
                "Actual loan terms depend on the lender."
            )

    loan = profile.get("required_loan")
    project_cost = profile.get("project_cost")

    if loan:

        reply = (
            "💰 I found a required loan amount in your profile.\n\n"
            f"Required loan: **{money(loan)}**\n"
        )

        if project_cost:
            reply += (
                f"Project cost: **{money(project_cost)}**\n"
            )

        reply += (
            "\nFor an EMI estimate, ask something like:\n"
            "**Calculate EMI for ₹200000 at 10% for 3 years.**"
        )

        return reply

    return (
        "💰 I can help with financial what-if scenarios.\n\n"
        "For example, ask:\n"
        "**Calculate EMI for ₹200000 at 10% for 3 years.**\n\n"
        "I can estimate:\n"
        "• Monthly EMI\n"
        "• Total interest\n"
        "• Total repayment\n\n"
        "You can also use the **Simulator** section."
    )


def partners_response():

    return (
        "📍 SchemeSahay can help you identify suitable assistance channels "
        "such as banks, agencies and CSC-assisted channels.\n\n"
        "Open **Partners** to see the available assistance channels "
        "and their services."
    )


def simulator_response():

    return (
        "🧮 **Financial What-If Simulator**\n\n"
        "You can explore scenarios using:\n"
        "• Project cost\n"
        "• Loan amount\n"
        "• Annual interest rate\n"
        "• Tenure\n"
        "• Own contribution\n"
        "• Moratorium\n\n"
        "The simulator estimates EMI, interest and total repayment.\n\n"
        "You can also ask me directly:\n"
        "**Calculate EMI for ₹200000 at 10% for 3 years.**"
    )


def general_response():

    return (
        "I can help you with your SchemeSahay journey. 😊\n\n"
        "Try asking me about:\n\n"
        "🔎 **Schemes** — Find potentially relevant schemes\n"
        "✅ **Eligibility** — Understand eligibility checks\n"
        "📄 **Documents** — Understand supporting documents\n"
        "👤 **Profile** — Check profile completeness\n"
        "📋 **Applications** — Track application information\n"
        "💰 **Finance** — Calculate EMI and repayment\n"
        "📍 **Partners** — Find assistance channels\n\n"
        "Example:\n"
        "\"I want to start a small business and need ₹2 lakh.\""
    )


# ============================================================
# MAIN RESPONSE ENGINE
# ============================================================

def generate_response(request: ChatRequest):

    message = request.message.strip()

    intent = detect_intent(message)

    profile = request.profile or {}

    applications = request.applications or []

    schemes = request.schemes or []

    documents = request.documents or []

    if intent == "greeting":
        reply = greeting_response()

    elif intent == "about":
        reply = about_response()

    elif intent == "profile":
        reply = profile_response(profile)

    elif intent == "schemes":
        reply = scheme_response(
            message,
            schemes,
            profile
        )

    elif intent == "business":
        reply = business_response(
            message,
            schemes,
            profile
        )

    elif intent == "documents":
        reply = documents_response(
            documents,
            profile
        )

    elif intent == "applications":
        reply = applications_response(
            applications
        )

    elif intent == "eligibility":
        reply = eligibility_response(
            profile
        )

    elif intent == "finance":
        reply = finance_response(
            message,
            profile
        )

    elif intent == "partners":
        reply = partners_response()

    elif intent == "simulator":
        reply = simulator_response()

    else:
        reply = general_response()

    return reply, intent


# ============================================================
# API ENDPOINT
# ============================================================

@router.post("")
async def chat(request: ChatRequest):

    try:

        message = request.message.strip()

        if not message:

            return {
                "reply": "Please type a question and I'll help you.",
                "intent": "empty"
            }

        reply, intent = generate_response(
            request
        )

        return {
            "reply": reply,
            "intent": intent,
            "assistant": "SchemeSahay Assistant"
        }

    except Exception as e:

        print(
            "CHATBOT ERROR:",
            repr(e)
        )

        return {
            "reply": (
                "I ran into a temporary problem while processing "
                "that request. Please try again."
            ),
            "intent": "error"
        }