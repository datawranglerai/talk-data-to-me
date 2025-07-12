from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from tools.demo_tools import fake_search, fake_summarise

import litellm

litellm._turn_on_debug()


# Open LMStudio > Load quantized Gemma3n MLX optimised model > start server
# Can use `curl -X GET http://localhost:1234/v1/models` if not sure of model ID
local_model = LiteLlm(
    model="gemma-3n-e2b-it-mlx",  # lmstudio-community/gemma-3n-E2B-it-MLX-4bit optimised for Mac M2
    api_base="http://localhost:1234/v1",  # usually runs on http://localhost:1234 by default
    api_key="not-needed"  # doesn't require real API key
)


search_agent = LlmAgent(
    name="Local_Gemma3n_Search_Agent",
    model=local_model,
    instruction="Use fake_search to look things up.",
    tools=[fake_search]
)

