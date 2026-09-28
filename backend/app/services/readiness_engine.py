def calculate_readiness(profile, evidence, required_docs, uploaded_docs):
    issues = []
    actions = []

    required_evidence = [x for x in evidence if x.get("required")]
    eligibility_score = (
        sum(x["status"] == "SATISFIED" for x in required_evidence) / len(required_evidence) * 100
        if required_evidence else 100
    )

    uploaded_types = {x.get("document_type") for x in uploaded_docs}
    doc_results = []
    for doc in required_docs:
        present = doc["document_type"] in uploaded_types
        doc_results.append({
            "document": doc["document_name"],
            "document_type": doc["document_type"],
            "required": doc.get("required", True),
            "status": "SATISFIED" if present else "MISSING"
        })
        if doc.get("required", True) and not present:
            issues.append(f"Missing {doc['document_name']}")
            actions.append(f"Upload {doc['document_name']}")

    profile_fields = ["age", "state", "district", "category", "income", "occupation", "education"]
    completed = sum(profile.get(x) not in (None, "") for x in profile_fields)
    profile_score = completed / len(profile_fields) * 100

    financial_score = 100
    cost = profile.get("project_cost")
    loan = profile.get("required_loan")
    if loan and cost and loan > cost:
        financial_score = 30
        issues.append("Requested loan is greater than stated project cost")
        actions.append("Verify project cost and requested loan amount")
    elif loan and loan <= 0:
        financial_score = 40
        issues.append("Requested loan amount is invalid")
        actions.append("Enter a valid loan amount")

    readiness = round(
        eligibility_score * 0.45 +
        (sum(x["status"] == "SATISFIED" for x in doc_results) / len(doc_results) * 100 if doc_results else 100) * 0.30 +
        financial_score * 0.15 +
        profile_score * 0.10
    )

    if readiness >= 90:
        label = "Ready with minor checks"
    elif readiness >= 70:
        label = "Ready with corrections"
    else:
        label = "Action required"

    for e in required_evidence:
        if e["status"] == "NOT_SATISFIED":
            issues.append(e["requirement"])
            actions.append(f"Resolve eligibility condition: {e['requirement']}")

    return {
        "score": readiness,
        "label": label,
        "issues": list(dict.fromkeys(issues)),
        "actions": list(dict.fromkeys(actions)),
        "documents": doc_results,
        "components": {
            "eligibility": round(eligibility_score),
            "documents": round(sum(x["status"] == "SATISFIED" for x in doc_results) / len(doc_results) * 100 if doc_results else 100),
            "financial": round(financial_score),
            "profile": round(profile_score),
        }
    }
