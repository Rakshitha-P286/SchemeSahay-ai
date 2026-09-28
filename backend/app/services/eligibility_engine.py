from typing import Any

def normalize(v: Any):
    if isinstance(v, str):
        return v.strip().lower()
    return v

def compare(user_value, operator, expected):
    if user_value is None or user_value == "":
        return "NEEDS_VERIFICATION", "User value is missing"

    try:
        if operator in ("gte", "lte", "gt", "lt"):
            a, b = float(user_value), float(expected)
            ok = {"gte": a >= b, "lte": a <= b, "gt": a > b, "lt": a < b}[operator]
        elif operator == "eq":
            ok = normalize(user_value) == normalize(expected)
        elif operator == "neq":
            ok = normalize(user_value) != normalize(expected)
        elif operator == "in":
            options = [normalize(x) for x in str(expected).split(",")]
            ok = normalize(user_value) in options
        else:
            return "NEEDS_VERIFICATION", f"Unsupported rule operator: {operator}"
    except Exception:
        return "NEEDS_VERIFICATION", "Value could not be evaluated safely"

    return ("SATISFIED" if ok else "NOT_SATISFIED",
            "Condition satisfied" if ok else "Condition not satisfied")

def check_rules(profile: dict, rules: list[dict]):
    evidence = []
    for rule in rules:
        field = rule["field"]
        user_value = profile.get(field)
        status, explanation = compare(user_value, rule["operator"], rule["value"])
        evidence.append({
            "field": field,
            "requirement": rule["rule_description"],
            "operator": rule["operator"],
            "required_value": rule["value"],
            "user_value": user_value,
            "status": status,
            "source": "Structured scheme rule",
            "required": rule.get("required", True),
            "explanation": explanation
        })
    required = [x for x in evidence if x["required"]]
    satisfied = sum(x["status"] == "SATISFIED" for x in required)
    score = round((satisfied / len(required)) * 100) if required else 0
    return evidence, score
