"""Step progression schema detailing dashboard target highlights."""

from __future__ import annotations

from typing import Dict, Any, List

STEPS: List[Dict[str, Any]] = [
    {
        "index": 0,
        "title": "Welcome to Sentinel",
        "highlight_class": ".welcome-landing",
        "directive": "Introduce Sentinel as a Crime Intelligence and Decision Support Platform for police command.",
        "narration": "Welcome to Sentinel, an AI decision-support platform designed to convert raw synthetic crime logs and records into structured intelligence."
    },
    {
        "index": 1,
        "title": "Morning Intelligence Brief",
        "highlight_class": ".morning-brief-landing-container",
        "directive": "Explain the Morning Brief summarizing high-risk zones and threat indices in natural language.",
        "narration": "The morning brief aggregates threat levels and highlights active sectors in natural language, helping leadership focus on key areas first."
    },
    {
        "index": 2,
        "title": "Critical Alert Prioritization",
        "highlight_class": ".priority-alerts-section",
        "directive": "Review prioritised alerts (Critical, High) sorted by urgency.",
        "narration": "Priority alerts highlight urgent occurrences, sorting spatial spikes and recurring offender alerts dynamically."
    },
    {
        "index": 3,
        "title": "DBSCAN Spatial Hotspot Map",
        "highlight_class": ".hotspot-map-section",
        "directive": "Interact with map hotspots showing incident density circles.",
        "narration": "Sentinel's DBSCAN algorithm detects active spatial hotspots, automatically mapping emerging crime clusters."
    },
    {
        "index": 4,
        "title": "Explainable AI Risk Forecasts",
        "highlight_class": ".explainability-panel-card",
        "directive": "Analyze Random Forest zone risks using positive and negative SHAP drivers.",
        "narration": "Using SHAP attribution math, Sentinel explains the 'why' behind risk scores, showing positive drivers (like patrol gaps) in red and mitigations in green."
    },
    {
        "index": 5,
        "title": "Unified Investigation Timeline",
        "highlight_class": ".timeline-panel-card",
        "directive": "View unified timelines compiling FIRs, CCTV feeds, and laboratory findings.",
        "narration": "The unified timeline constructs a sequential chronicle of case occurrences, exposing chronological links across data sources."
    },
    {
        "index": 6,
        "title": "Similar Case Recommendation Engine",
        "highlight_class": ".similarity-panel-card",
        "directive": "Analyze historical case matches based on hybrid similarity weights.",
        "narration": "The Similarity Engine uses hybrid scoring to match active files with historical burglary or theft cases above threshold."
    },
    {
        "index": 7,
        "title": "Criminal Network Intelligence",
        "highlight_class": ".network-modal",
        "directive": "Expose relationship links, centralities, and community groupings.",
        "narration": "The Criminal Network Platform maps relationships using NetworkX, identifying central offenders and crime network hubs."
    },
    {
        "index": 8,
        "title": "Unified Case Profile",
        "highlight_class": ".case-profile-panel",
        "directive": "Review consolidated suspect dossiers and resolved communication identifiers.",
        "narration": "Case profiles bring together suspect data, resolved telephone numbers, and vehicle tags to give a complete view of the investigation."
    },
    {
        "index": 9,
        "title": "Patrol Recommendation Dispatch",
        "highlight_class": ".patrol-recommendations-card",
        "directive": "Review recommended shift windows, expected impacts, and approve dispatches.",
        "narration": "The Patrol Engine generates tactical dispatch recommendations. All suggestions are advisories and require manual confirmation."
    },
    {
        "index": 10,
        "title": "Morning Brief Summary",
        "highlight_class": ".brief-summary-container",
        "directive": "Conclude presentation showcasing consolidated briefing narratives.",
        "narration": "This concludes the guided workflow. Sentinel successfully transforms data into a clear tactical action plan."
    }
]


def get_all_steps() -> List[Dict[str, Any]]:
    """Retrieve lists of available walkthrough steps."""
    return STEPS
