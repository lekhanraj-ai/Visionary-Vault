import json
from datetime import datetime

def generate_esg_report(company_name: str, co2_emission_kg: float, renewable_share: float, esg_score: float):
    """
    Generates a simple ESG (Environmental, Social, Governance) report for a company.
    """

    sustainability_status = "Strong" if esg_score >= 70 else "Moderate" if esg_score >= 40 else "Weak"
    category = (
        "🌍 Environmentally Sustainable" if renewable_share > 50 and co2_emission_kg < 1000
        else "⚠️ Needs Improvement"
    )

    report = {
        "company": company_name,
        "report_generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": f"ESG performance for {company_name} indicates a {sustainability_status} sustainability profile.",
        "details": {
            "CO2 Emission (kg)": co2_emission_kg,
            "Renewable Energy Usage (%)": renewable_share,
            "ESG Score": esg_score,
            "Sustainability Status": sustainability_status,
            "Environmental Category": category
        },
        "recommendations": [
            "Increase renewable energy adoption to reduce CO2 impact.",
            "Implement automated energy efficiency monitoring systems.",
            "Focus on transparent carbon disclosure following CSRD/ESRS guidelines."
        ],
    }

    # Save a copy locally (optional)
    filename = f"../reports/{company_name.replace(' ', '_')}_ESG_Report.json"
    try:
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)
    except Exception as e:
        print(f"⚠️ Could not save report file: {e}")

    return report
