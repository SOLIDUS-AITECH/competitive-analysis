def finalize_summary(industry: str, overview: str, findings: dict, sources: list) -> str:
    competitor_sections = "\n\n".join(
        f"## {competitor}\n\n" +
        "\n".join([
            f"* **Key Insights:** {', '.join(data.get('key_insights', []))}",
            f"* **Unique Capabilities:** {', '.join(data.get('unique_capabilities', []))}",
            f"* **Unique Selling Points & Target Market:** {', '.join(data.get('unique_selling_points', []))}",
            f"* **Recent Innovations, Strengths & Weaknesses:** {', '.join(data.get('recent_innovations', []))}",
            f"* **Market Positioning:** {', '.join(data.get('market_positioning', []))}",
            f"* **Challenges:** {', '.join(data.get('challenges', []))}",
            f"* **Future Vision:** {', '.join(data.get('future_vision', []))}"
        ])
        for competitor, data in findings.items()
    )
    
    summary = f"""✅ Final Competitive Analysis Summary:

# Competitive Analysis: {industry}

{overview or "Comprehensive Competitive Landscape Overview"}

{competitor_sections}

### Sources
{chr(10).join(sources) if sources else "No sources available."}
"""
    return summary
