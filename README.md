# 🎙️ Live AI Commentator

## Recent Updates

- Hooked up Google's local Gemma3n models via LMStudio \& LiteLLM
- Mac optimization with community-tuned MLX version
- Crisis response demo loop (because apparently we needed AI agents to simulate emergencies)

Ever wondered what your AI agents are actually doing? Yeah, me too. Turns out watching AI systems work is like trying to follow a chess match through a telescope - technically impressive, but you have no idea what's happening or why.

So I built an AI commentator that watches other AI agents and explains what they're doing in real-time. Like having a sports announcer for your code, except instead of "He shoots, he scores!" it's more "The search agent is querying the database... and it's found something interesting!"

## What This Actually Does

Picture this: You've got AI agents running around doing important stuff, but you're sitting there like a parent watching their kid's soccer game through thick fog. You know *something* is happening, but good luck explaining it to anyone.

This system gives your AI agents their own play-by-play commentator. It watches what they're doing and translates the technical gibberish into something humans can actually understand. And it does it in real-time with actual audio commentary.

Is it necessary? Probably not. Is it weirdly entertaining? Absolutely.

## What Makes This Work

### Real-Time Audio Commentary

- **Gemini Live Integration**: Uses Google's Gemini Live API because apparently we needed AI to comment on AI
- **Smooth Audio Playback**: PyAudio buffering system that actually works (shocking, I know)
- **Text Transcription**: Also spits out text in case you prefer reading about your AI agents' existential crises


### Multi-Agent Architecture (The Fancy Stuff)

- **Agent Orchestration**: One supervisor agent managing multiple specialist agents (like herding very smart cats)
- **Event-Driven Design**: Captures agent activities in real-time via ADK callbacks
- **Parallel Execution**: Commentary runs alongside your actual workflow without breaking everything


### Commentary Generation (The Fun Part)

- **Contextual Awareness**: Actually understands what the agents are doing instead of just reading log files
- **Memory System**: Remembers what it said before so it doesn't sound like a broken record
- **Dynamic Styles**: Rotates between different commentary personas because variety is the spice of life
- **Pattern Recognition**: Spots when agents are being inefficient (and calls them out on it)


### Production-Ready Architecture (The Boring But Important Stuff)

- **Asynchronous Processing**: Non-blocking event handling with proper timeouts
- **Resource Management**: Cleans up after itself like a well-trained AI system should
- **Error Handling**: Robust fallbacks for when things inevitably go wrong
- **Modular Design**: Clean separation of concerns (following ADK best practices, naturally)


## How This Thing Works

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

Basically, your agents do stuff, the event system catches it, the commentator translates it into human-speak, and you get to listen to AI agents being explained by another AI agent. It's AI all the way down.

## Getting Started (The Easy Part)

### What You Need

- Python 3.9+ (because life's too short for older versions)
- Google API Key (for Gemini Live)
- Something to hear audio with (speakers, headphones, whatever)


### Installation

```bash
# Get the code
git clone https://github.com/your-username/live-ai-commentator.git
cd live-ai-commentator

# Install the dependencies
pip install -r requirements.txt

# Install audio stuff (this might be annoying on some systems)
pip install pyaudio pygame
```


### Environment Setup

```bash
# Set your Google API key
export GOOGLE_API_KEY="your-google-api-key-here"

# Optional: Other AI providers if you're feeling adventurous
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```


### Running the Thing

```bash
# Fire it up
python main.py
```

Now you'll hear an AI commentator explaining what your AI agents are doing. Welcome to the future, I guess.

## The Technical Bits (For the Curious)

### Event-Driven Commentary

The system hooks into ADK's callback mechanism to catch agent activities:

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


### Asynchronous Queue Communication

Events flow from agents to commentator via asyncio queue (because threading is for people who like debugging race conditions):

```python
# Global queue for cross-agent communication
commentator_queue = Queue()

# Commentator consumes events
async for event in commentator_queue.get():
    await generate_commentary(event)
```


### Dynamic Commentary Styles

The system rotates between different personas to keep things interesting:

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


### Memory Management

The commentator remembers what it said before (unlike most AI systems):

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


### Audio Streaming

Smooth audio playback through callback-based audio player:

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


## Configuration (Making It Yours)

### Commentary Styles

Want different personalities? Edit `agents/commentator.py`:

```python
def _get_commentary_style(self) -> str:
    styles = [
        "sarcastic developer who's seen too many standup meetings",
        "overly enthusiastic startup founder",
        "tired sys admin who just wants to go home",
        # ... add whatever personality disorders you prefer
    ]
    return styles[self._event_count % len(styles)]
```


### Audio Settings

Tweak audio parameters in `utils/audio_player.py`:

```python
self.stream = self.p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=24000,  # Gemini Live sample rate
    output=True,
    frames_per_buffer=1024,  # Smaller = lower latency, higher CPU usage
    stream_callback=self._audio_callback
)
```


### Model Configuration

Mix and match AI models because why not:

```python
# Use different models for different jobs
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


## Advanced Features (For the Overachievers)

### Custom Workflow Integration

Hook this into your existing ADK workflows:

```python
# Your existing workflow
your_workflow = SequentialAgent(
    name="YourWorkflow", 
    sub_agents=[
        # ... your agents with callbacks
    ]
)

# Add commentator to the mix
main_system = ParallelAgent(
    name="MainSystem",
    sub_agents=[
        your_workflow,
        LiveCommentator(name="Commentator")
    ]
)
```


### Event Filtering

Only comment on the interesting stuff:

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
    
    Focus on:
    - {self.focus_area_1}
    - {self.focus_area_2}
    - Why this matters
    
    Keep it under 30 words and make it interesting!"""
```


## File Structure

- **`main.py`**: Entry point and main orchestration
- **`agents/supervisor.py`**: Main workflow coordinator with callbacks
- **`agents/commentator.py`**: Live commentary generation and audio streaming
- **`utils/audio_player.py`**: Audio buffering and playback management
- **`tools/`**: Mock tools for demo purposes (replace with your actual tools)


## Dependencies

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


## Performance Notes

- **Memory Usage**: Commentary history is bounded (adjustable)
- **Audio Latency**: ~200-500ms from event to audio (not bad for real-time AI)
- **CPU Usage**: Moderate due to audio processing
- **Network**: Depends on how chatty Gemini Live gets


## Future Ideas (The Wishlist)

### Audio Enhancements

- Multiple commentary tracks for different audiences
- Audio effects and background music (because why not make it even more extra)
- Voice cloning for personalized commentators


### Analytics

- Performance metrics dashboard
- Commentary quality analysis
- Agent efficiency reporting (so you can judge your AI agents)


### Integration Options

- Web dashboard with live visualization
- Slack/Discord bot integration
- REST API for remote commentary triggering


### Multi-Agent Fun

- Commentator debates (let AI argue about AI)
- Specialized domain commentators
- Interactive Q\&A with commentators


## Contributing

Want to make this better? Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-amazing-idea`
3. Make your changes (and try not to break everything)
4. Add tests (yes, really)
5. Update docs as needed
6. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/live-ai-commentator.git

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting (because code style matters)
flake8 src/
black src/
```


### Code Style

- Follow PEP 8 (it's not optional)
- Use type hints throughout
- Write docstrings that humans can understand
- Add tests for new features
- Follow ADK best practices


## License

MIT License - see the [LICENSE](LICENSE) file for details. Do whatever you want with this code, just don't blame me if it achieves sentience.

## Credits

- **Google ADK Team** for building the framework that makes this possible
- **Google AI** for the Gemini Live API
- **OpenAI \& Anthropic** for additional LLM support via LiteLLM
- **ADK Community** for patterns and best practices
- **Everyone who's ever wished AI would just explain itself** - this one's for you


## Further Reading

- [Google ADK Documentation](https://developers.google.com/agent-development-kit)
- [Gemini Live API Guide](https://developers.google.com/gemini/docs/live)
- [Multi-Agent Systems with ADK](https://developers.google.com/agent-development-kit/docs/multi-agent)
- [ADK Custom Agents Tutorial](https://developers.google.com/agent-development-kit/docs/custom-agents)

**Built with Google's Agent Development Kit** (and a healthy dose of curiosity about what AI agents actually do all day)

*Making AI workflows less mysterious, one commentary at a time.*

