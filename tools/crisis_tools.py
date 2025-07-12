from google.adk.tools import ToolContext
from typing import Dict
import random
import time


def emergency_alert_scan(location: str, alert_type: str, tool_context: ToolContext):
    """Scan for emergency alerts in a specific location."""
    # Simulate realistic crisis data
    alerts = [
        f"SEVERE: Wildfire spotted {random.randint(1,5)} miles from {location}",
        f"MODERATE: Evacuation route congestion detected near {location}",
        f"HIGH: Emergency services responding to {alert_type} in {location}",
        f"CRITICAL: Infrastructure damage reported in {location} area"
    ]
    return {"alerts": random.choice(alerts), "timestamp": time.time()}


def resource_availability_check(resource_type: str, radius_miles: int, tool_context: ToolContext):
    """Check availability of emergency resources."""
    resources = {
        "ambulances": random.randint(2, 8),
        "fire_trucks": random.randint(1, 4),
        "helicopters": random.randint(0, 2),
        "shelters": random.randint(3, 12)
    }
    return {
        "available": resources.get(resource_type, 0),
        "location_radius": f"{radius_miles} miles",
        "response_time": f"{random.randint(5, 25)} minutes"
    }


def evacuation_route_analysis(start_location: str, destination: str, tool_context: ToolContext):
    """Analyze optimal evacuation routes."""
    return {
        "primary_route": f"Highway 101 from {start_location} to {destination}",
        "traffic_status": random.choice(["Clear", "Moderate", "Heavy", "Blocked"]),
        "estimated_time": f"{random.randint(15, 90)} minutes",
        "alternative_routes": 2
    }


def communication_broadcast(message: str, urgency_level: str, tool_context: ToolContext):
    """Broadcast emergency communications."""
    return {
        "broadcast_sent": True,
        "channels": ["Emergency Alert System", "Social Media", "Local Radio"],
        "estimated_reach": f"{random.randint(10000, 100000)} people",
        "urgency": urgency_level
    }
