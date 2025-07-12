from google.adk.agents import SequentialAgent, LlmAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm

from agents.supervisor import broadcast_tool_event

from tools.crisis_tools import (
    emergency_alert_scan, resource_availability_check,
    evacuation_route_analysis, communication_broadcast
)

LLM_MODEL = "openai/gpt-4o"

# Crisis Response Team Structure
alert_monitor = LlmAgent(
    name="AlertMonitor",
    model=LiteLlm(model=LLM_MODEL),
    instruction="Monitor emergency situations and scan for alerts. Prioritize by severity.",
    tools=[emergency_alert_scan],
    before_tool_callback=broadcast_tool_event
)

resource_coordinator = LlmAgent(
    name="ResourceCoordinator",
    model=LiteLlm(model=LLM_MODEL),
    instruction="Check and coordinate emergency resources. Focus on availability and response times.",
    tools=[resource_availability_check],
    before_tool_callback=broadcast_tool_event
)

evacuation_planner = LlmAgent(
    name="EvacuationPlanner",
    model=LiteLlm(model=LLM_MODEL),
    instruction="Analyze evacuation routes and plan optimal paths for civilians.",
    tools=[evacuation_route_analysis],
    before_tool_callback=broadcast_tool_event
)

communications_hub = LlmAgent(
    name="CommunicationsHub",
    model=LiteLlm(model=LLM_MODEL),
    instruction="Broadcast critical information to the public and coordinate messaging.",
    tools=[communication_broadcast],
    before_tool_callback=broadcast_tool_event
)

crisis_supervisor = ParallelAgent(
    name="CrisisResponseTeam",
    sub_agents=[alert_monitor, resource_coordinator, evacuation_planner, communications_hub]
)
