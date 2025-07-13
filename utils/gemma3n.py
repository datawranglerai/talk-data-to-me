from google.adk.models.lite_llm import LiteLlm


def setup_local_model() -> LiteLlm:
    # Open LMStudio > Load quantized Gemma3n MLX optimised model > start server
    # Can use `curl -X GET http://localhost:1234/v1/models` if not sure of model ID
    local_model = LiteLlm(
        model="openai/gemma-3n-e2b-it-mlx",  # lmstudio-community/gemma-3n-E2B-it-MLX-4bit optimised for Mac M2
        api_base="http://localhost:1234/v1",  # usually runs on http://localhost:1234 by default
        api_key="not-needed"  # doesn't require real API key
    )

    return local_model

