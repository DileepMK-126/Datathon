"""Date and document formatters for morning brief templates."""

from __future__ import annotations

from typing import Dict, Any, List
from datetime import datetime


def format_brief_date(dt: datetime) -> str:
    """Format brief datetime to readable command brief format."""
    return dt.strftime("%d %B %Y")


def format_to_markdown(brief: Dict[str, Any]) -> str:
    """Compile brief data into a printable Markdown report layout."""
    markdown = []
    markdown.append(f"# Executive Crime Intelligence Brief")
    markdown.append(f"**Date:** {brief['date']}  ")
    markdown.append(f"**Overall Threat Level:** {brief['threat_level']} (Score: {brief['threat_score']}/100)  ")
    markdown.append(f"**Highest Risk Sector:** {brief['highest_risk_sector']}  ")
    markdown.append("\n---")
    markdown.append(f"\n## Tactical Intelligence Summary")
    markdown.append(f"\"{brief['summary']}\"")
    markdown.append("\n## Key Operational Highlights")
    for highlight in brief["highlights"]:
        markdown.append(f"* {highlight}")
    markdown.append("\n---")
    markdown.append(f"\n*Sentinel Command Brief — Human Verification Required before Operational Dispatch.*")
    
    return "\n".join(markdown)
