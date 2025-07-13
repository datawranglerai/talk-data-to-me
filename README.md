# 🎙️ Live AI Commentator

## Updates

- Integration of Google's local Gemma3n models via LMStudio & LiteLLM
- Optimised Gemma3n model by community-tuned MLX version for Mac
- Crisis response loop

A sophisticated real-time AI commentary system that provides live sports-style audio commentary on multi-agent AI workflows using Google's Agent Development Kit (ADK) and Gemini Live API.

## 🌟 What Is This?

Imagine having an AI sports commentator providing live, engaging commentary on your AI agents as they work - that's exactly what this project delivers! Our Live AI Commentator watches AI agent activities in real-time and generates dynamic, contextual audio commentary with the energy and insight of a professional sports broadcaster.

## ✨ Key Features

### 🔥 **Real-Time Audio Commentary**
- **Gemini Live Integration**: Utilizes Google's Gemini Live API for low-latency, high-quality audio generation
- **Smooth Audio Playback**: Advanced buffering system using PyAudio for uninterrupted audio streaming
- **Text Transcription**: Simultaneous text output alongside audio for accessibility and debugging

### 🤖 **Advanced Multi-Agent Architecture**
- **Agent Orchestration**: Supervisor coordinates multiple specialized agents (Searcher, Summarizer)
- **Event-Driven Design**: Real-time capture of agent activities via ADK callbacks
- **Parallel Execution**: Commentator runs alongside main workflow without interference

### 🧠 **Intelligent Commentary Generation**
- **Contextual Awareness**: Commentary adapts based on agent activities and workflow progression
- **Memory System**: Avoids repetitive commentary through session state and history tracking
- **Dynamic Styles**: Rotates between different commentary personas (sports announcer, technical analyst, investigative reporter, etc.)
- **Pattern Recognition**: Identifies and comments on agent behavior patterns and efficiency

### 🔧 **Production-Ready Architecture**
- **Asynchronous Processing**: Non-blocking event handling with proper timeout management
- **Resource Management**: Automatic cleanup of audio resources and graceful termination
- **Error Handling**: Robust fallback systems and comprehensive error management
- **Modular Design**: Clean separation of concerns following ADK best practices

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main Runner   │    │   Supervisor    │    │  Live           │
│                 │    │   Agent         │    │  Commentator    │
│                 │    │                 │    │                 │
│  ┌───────────┐  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  │ Parallel  │  │    │  │Sequential │  │    │  │ Event     │  │
│  │ Agent     │  │────▶│  │ Agent     │  │    │  │ Monitor   │  │
│  │           │  │    │  │           │  │    │  │           │  │
│  └───────────┘  │    │  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   Tool Events   │              │
         │              │    Callbacks    │              │
         │              │                 │              │
         │              │ ┌─────────────┐ │              │
         │              │ │fake_search  │ │              │
         │              │ │fake_summarise│ │              │
         │              │ └─────────────┘ │              │
         │              └─────────────────┘              │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         └──────────────▶│ Commentator     │◀─────────────┘
                        │ Queue           │
                        │                 │
                        │ ┌─────────────┐ │
                        │ │asyncio.Queue│ │
                        │ └─────────────┘ │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Gemini Live    │
                        │  Commentary     │
                        │  Generation     │
                        │                 │
                        │ ┌─────────────┐ │
                        │ │Audio Stream │ │
                        │ │Transcription│ │
                        │ └─────────────┘ │
                        └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Audio         │
                        │   Playback      │
                        │                 │
                        │ ┌─────────────┐ │
                        │ │  PyAudio    │ │
                        │ │  Buffering  │ │
                        │ └─────────────┘ │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google API Key (for Gemini Live)
- Audio output device (speakers/headphones)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/live-ai-commentator.git
cd live-ai-commentator

# Install dependencies
pip install -r requirements.txt

# Install audio dependencies
pip install pyaudio pygame  # May require system audio libraries
```

### Environment Setup

```bash
# Set your Google API key
export GOOGLE_API_KEY="your-google-api-key-here"

# Optional: Configure other model providers
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Basic Usage

```bash
# Run the live commentator system
python main.py
```

You'll hear real-time audio commentary as the AI agents execute their workflow, along with text output in the console.

## 💡 Key Concepts

### 🎯 **Event-Driven Commentary**

The system uses ADK's callback mechanism to capture agent activities in real-time:

```python
def broadcast_tool_event(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext
) -> Optional[Dict]:
    """Capture tool calls and send to commentator."""
    event_data = {
        "agent": tool_context.agent_name,
        "tool": tool.name,
        "args": args,
        "timestamp": "now"
    }
    commentator_queue.put_nowait(event_data)
    return None

# Attach to agents
searcher = LlmAgent(
    name="Searcher",
    before_tool_callback=broadcast_tool_event,
    # ... other config
)
```

### 🧵 **Asynchronous Queue Communication**

Events flow from the supervisor agents to the commentator via an asyncio queue:

```python
# Global queue for cross-agent communication
commentator_queue = Queue()

# Commentator consumes events
async for event in commentator_queue.get():
    await generate_commentary(event)
```

### 🎨 **Dynamic Commentary Styles**

The system rotates between different commentary personas to keep output engaging:

```python
def _get_commentary_style(self) -> str:
    styles = [
        "sports announcer with high energy and play-by-play details",
        "technical analyst focusing on efficiency and patterns", 
        "strategic commentator analyzing decision-making",
        "investigative reporter uncovering the story behind the actions",
        "data scientist explaining the technical implications"
    ]
    return styles[self._event_count % len(styles)]
```

### 🧠 **Memory and Context Management**

The commentator maintains memory to avoid repetitive commentary:

```python
class LiveCommentator(BaseAgent):
    _commentary_history: Deque[str] = PrivateAttr(default_factory=lambda: deque(maxlen=10))
    
    def _generate_commentary_prompt(self, narration: str) -> str:
        recent_commentary = list(self._commentary_history)[-3:]
        
        prompt = f"""Previous Commentary (avoid repeating):
        {chr(10).join(recent_commentary) if recent_commentary else "None"}
        
        Current Activities: {narration}
        
        Provide fresh, varied commentary..."""
        
        return prompt
```

### 🔊 **Audio Streaming Architecture**

Smooth audio playback is achieved through a callback-based audio player:

```python
class CallbackAudioPlayer:
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Continuous audio playback callback."""
        try:
            data = self.audio_queue.get_nowait()
            return (data, pyaudio.paContinue)
        except queue.Empty:
            silence = b'\x00' * (frame_count * 2)
            return (silence, pyaudio.paContinue)
```

## 🔧 Configuration

### Commentary Styles

Customize commentary personas in `agents/commentator.py`:

```python
def _get_commentary_style(self) -> str:
    styles = [
        "your custom style here",
        # ... add more styles
    ]
    return styles[self._event_count % len(styles)]
```

### Audio Settings

Adjust audio parameters in `utils/audio_player.py`:

```python
self.stream = self.p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=24000,  # Gemini Live sample rate
    output=True,
    frames_per_buffer=1024,  # Adjust for latency/quality trade-off
    stream_callback=self._audio_callback
)
```

### Models and Providers

Configure different AI models in your agent definitions:

```python
# Use different models for different agents
supervisor = SequentialAgent(
    sub_agents=[
        LlmAgent(model="gemini-2.0-flash-live-001"),      # Fast for tools
        LlmAgent(model=LiteLlm(model="openai/gpt-4o")),   # Powerful for analysis
    ]
)

commentator = LiveCommentator(
    model="gemini-2.0-flash-live-001"  # Optimized for real-time
)
```

## 🎯 Advanced Features

### Custom Workflow Integration

Integrate the commentator with your own ADK workflows:

```python
# Your existing workflow
your_workflow = SequentialAgent(
    name="YourWorkflow", 
    sub_agents=[
        # ... your agents with callbacks
    ]
)

# Create parallel system with commentator
main_system = ParallelAgent(
    name="MainSystem",
    sub_agents=[
        your_workflow,
        LiveCommentator(name="Commentator")
    ]
)
```

### Event Filtering

Filter which events trigger commentary:

```python
def broadcast_tool_event(tool, args, tool_context):
    # Only comment on certain tools
    if tool.name in ['important_tool', 'critical_operation']:
        event_data = {
            "agent": tool_context.agent_name,
            "tool": tool.name,
            "args": args,
            "priority": "high"
        }
        commentator_queue.put_nowait(event_data)
```

### Custom Commentary Prompts

Create domain-specific commentary:

```python
def _generate_commentary_prompt(self, narration: str) -> str:
    return f"""You are an expert {self.domain} commentator.
    
    Current system activities: {narration}
    
    Provide insightful commentary focusing on:
    - {self.focus_area_1}
    - {self.focus_area_2}
    - Performance implications
    
    Keep it under 30 words, high energy!"""
```

## 🛠️ Technical Implementation

### Core Components

- **`main.py`**: Entry point and main orchestration
- **`agents/supervisor.py`**: Main workflow coordinator with tool callbacks
- **`agents/commentator.py`**: Live commentary generation and audio streaming
- **`utils/audio_player.py`**: Audio buffering and playback management
- **`tools/`**: Mock tools for demonstration (replace with real tools)

### Dependencies

```txt
google-adk>=1.1.1
google-genai>=0.8.0
litellm>=1.0.0
pyaudio>=0.2.11
pygame>=2.0.0
pydantic>=2.0.0
loguru>=0.7.0
asyncio-queue>=0.1.0
```

### Performance Considerations

- **Memory Usage**: Commentary history is bounded (configurable)
- **Audio Latency**: ~200-500ms from event to audio output
- **CPU Usage**: Moderate due to real-time audio processing
- **Network**: Depends on Gemini Live API usage

## 🔮 Future Possibilities

### 🎵 **Enhanced Audio Features**
- Multiple commentary tracks (different languages/styles)
- Audio effects and background music
- Voice cloning for personalized commentators

### 📊 **Advanced Analytics**
- Performance metrics dashboard
- Commentary quality analysis
- Agent efficiency reporting

### 🌐 **Integration Opportunities**
- Web dashboard with live visualization
- Slack/Discord bot integration
- REST API for remote commentary triggering

### 🤝 **Multi-Agent Enhancements**
- Commentator debates (multiple perspectives)
- Specialized domain commentators
- Interactive Q&A with commentators

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the existing code style
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/live-ai-commentator.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 src/
black src/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Add comprehensive docstrings
- Include unit tests for new features
- Follow ADK best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google ADK Team** for the powerful Agent Development Kit framework
- **Google AI** for the Gemini Live API enabling real-time audio generation
- **OpenAI & Anthropic** for additional LLM capabilities via LiteLLM
- **ADK Community** for patterns and best practices

## 📚 Further Reading

- [Google ADK Documentation](https://developers.google.com/agent-development-kit)
- [Gemini Live API Guide](https://developers.google.com/gemini/docs/live)
- [Multi-Agent Systems with ADK](https://developers.google.com/agent-development-kit/docs/multi-agent)
- [ADK Custom Agents Tutorial](https://developers.google.com/agent-development-kit/docs/custom-agents)

---

**Built with ❤️ using Google's Agent Development Kit**

*Transform your AI workflows into engaging, commentated experiences!*

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/fd6bcff4-c597-41cc-a9a7-b9acbfc1941a/Google-ADK-Custom-Agent.pdf
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/23f7e58a-0084-41b8-9685-fa133850cff4/Google-ADK-Multi-Agent-Systems.pdf
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/45bf34e0-12c8-49dc-b9f8-b5bd2eecda48/Google-ADK-LLM-Agents.pdf
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/faf04a22-707a-4809-883d-1567dd56a3b5/Google-Agent-Development-Kit-ADK-Tutorials.pdf
[5] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/e91c54b6-e532-4825-a3eb-ea1edcdaa536/Google-ADK-Using-Different-Models.pdf
[6] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/c931bcf4-649e-451e-a1fa-5d9e123ec85f/Google-Agent-Development-Kit-ADK-Core-Concepts.pdf
[7] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_590ac644-406a-4bf2-92dd-ba24c95aef71/ce3ca1fd-15c1-4076-a767-0aa92d7bd642/Google-ADK-Workflow-Agents.pdf