from datetime import date
from app.database.connection import get_db

db = get_db()
db.schemes.delete_many({})
db.eligibility_rules.delete_many({})
db.scheme_documents.delete_many({})
db.assistance_channels.delete_many({})

schemes = [
    {
        "name":"Demo Micro Enterprise Loan","ministry":"Demo / Replace with official authority",
        "description":"Illustrative small-business finance record for development and testing.",
        "benefit":"Business loan assistance","benefit_amount":"Up to ₹5,00,000",
        "category":"Entrepreneurship","state":"All India","application_channel":"Authorized bank/channel partner",
        "application_mode":"Assisted or online","source_url":"REPLACE_WITH_OFFICIAL_SOURCE",
        "last_verified":"2026-09-28","status":"active","is_demo":True,
        "business_keywords":"tailoring shop artisan self employment micro enterprise small business"
    },
    {
        "name":"Demo SC Entrepreneur Support","ministry":"Demo / Replace with official authority",
        "description":"Illustrative category-focused entrepreneurship scheme record for testing.",
        "benefit":"Entrepreneurship finance support","benefit_amount":"Scheme-specific",
        "category":"SC Entrepreneurship","state":"All India","application_channel":"Authorized channel partner",
        "application_mode":"Assisted","source_url":"REPLACE_WITH_OFFICIAL_SOURCE",
        "last_verified":"2026-09-28","status":"active","is_demo":True,
        "business_keywords":"SC entrepreneur business self employment"
    },
    {
        "name":"Demo Educational Loan Support","ministry":"Demo / Replace with official authority",
        "description":"Illustrative education finance record for testing educational-loan flows.",
        "benefit":"Education finance support","benefit_amount":"Scheme-specific",
        "category":"Education","state":"All India","application_channel":"Authorized bank/channel partner",
        "application_mode":"Online or bank assisted","source_url":"REPLACE_WITH_OFFICIAL_SOURCE",
        "last_verified":"2026-09-28","status":"active","is_demo":True,
        "business_keywords":"education college course student educational loan"
    },
    {
        "name":"Demo Skill & Self Employment Support","ministry":"Demo / Replace with official authority",
        "description":"Illustrative skill and self-employment record for testing.",
        "benefit":"Training/self-employment support","benefit_amount":"Scheme-specific",
        "category":"Skill & Employment","state":"All India","application_channel":"Authorized agency",
        "application_mode":"Assisted","source_url":"REPLACE_WITH_OFFICIAL_SOURCE",
        "last_verified":"2026-09-28","status":"active","is_demo":True,
        "business_keywords":"skill training employment artisan self employment"
    }
]
result = db.schemes.insert_many(schemes)
ids = result.inserted_ids

rule_sets = [
    [
        ("age","gte","18","Applicant must be at least 18 years old",True),
        ("income","lte","500000","Illustrative income ceiling for the demo record",True),
        ("bank_account","eq","true","Bank account required",True)
    ],
    [
        ("age","gte","18","Applicant must be at least 18 years old",True),
        ("category","eq","SC","Applicant must belong to SC category",True),
        ("income","lte","500000","Illustrative income ceiling for the demo record",True)
    ],
    [
        ("age","gte","18","Applicant must be at least 18 years old",True),
        ("education","in","Diploma,Graduate,Post Graduate","Applicant should have the specified education level",True)
    ],
    [
        ("age","gte","18","Applicant must be at least 18 years old",True),
        ("employment_status","in","Unemployed,Self-employed","Applicant should match the supported employment condition",True)
    ]
]
for sid, rules in zip(ids, rule_sets):
    db.eligibility_rules.insert_many([
        {"scheme_id":sid,"field":f,"operator":op,"value":v,"rule_description":d,"required":req}
        for f,op,v,d,req in rules
    ])
    db.scheme_documents.insert_many([
        {"scheme_id":sid,"document_name":"Aadhaar / Identity Proof","document_type":"aadhaar","required":True},
        {"scheme_id":sid,"document_name":"Income Certificate","document_type":"income_certificate","required":True},
        {"scheme_id":sid,"document_name":"Project / Course Document","document_type":"project_document","required":True},
    ])

channels = [
    {"name":"Authorized Bank Partner - Demo A","type":"Public Sector Bank","state":"Karnataka","district":"Bengaluru Rural","address":"Demo address","contact":"Official contact to be verified","services":["Entrepreneurship loans"],"distance_km":2.1,"is_demo":True},
    {"name":"Authorized Agency - Demo B","type":"Channelizing Agency","state":"Karnataka","district":"Bengaluru Rural","address":"Demo address","contact":"Official contact to be verified","services":["Scheme applications"],"distance_km":4.8,"is_demo":True},
    {"name":"CSC Assisted Centre - Demo C","type":"CSC","state":"Karnataka","district":"Bengaluru Rural","address":"Demo address","contact":"Official contact to be verified","services":["Document scanning","Application assistance"],"distance_km":6.2,"is_demo":True},
]
db.assistance_channels.insert_many(channels)
print("SchemeMate demo data seeded.")
