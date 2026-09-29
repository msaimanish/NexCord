**NexCord** is a **multimodal, human-in-the-loop operations intelligence platform** that helps organizations manage complex real-world operations such as college fests, conferences, weddings, and community events.

NexCord combines **computer vision, machine learning, retrieval-augmented generation, and agentic AI** to understand the current operational state, detect and predict potential incidents, analyze their downstream effects, and generate actionable response plans.

Rather than allowing an AI agent to directly modify operational systems, NexCord follows a controlled **observe → detect → predict → retrieve → analyze → simulate → approve → execute → verify → recover** workflow. When an incident occurs, NexCord evaluates its potential impact and generates multiple resolution plans. The event planner reviews the alternatives and explicitly approves one before any operational changes are made.

Once approved, NexCord executes the selected plan through a **self-hosted MCP (Model Context Protocol) server using Streamable HTTP**, which provides controlled access to operational capabilities such as scheduling, resource allocation, personnel management, and notifications. After execution, NexCord verifies whether the system has reached the intended target state. If verification fails, it performs appropriate **recovery or compensating actions** to restore a valid state.

**PostgreSQL** serves as the authoritative source of operational state, while **pgvector** enables semantic retrieval of event policies, procedures, vendor information, and historical incident records. Machine-learning models provide additional intelligence, including **computer-vision-based occupancy detection, anomaly detection, and operational risk prediction**.

NexCord provides a **voice-first and web-based experience**, allowing users to interact naturally with the system while receiving structured visual information such as incident summaries, impact analyses, and proposed action plans. The platform can therefore serve as a simulated Alexa+ experience while remaining an independent AI/ML systems project and portfolio platform.

### Core workflow

**Observe → Detect → Predict → Retrieve → Analyze Impact → Simulate Plans → Human Approval → MCP Execution → Verify → Recover**

### Example

An organizer can ask:

> “NexCord, the robotics final starts in 30 minutes. Check whether there are any problems.”

NexCord combines the current event state, camera-based occupancy information, machine-learning risk predictions, and relevant operational policies to identify potential issues.

For example, it may determine that the venue is approaching capacity, a judge is unavailable, and required equipment is malfunctioning. It then generates several possible resolutions, such as moving the event, reallocating equipment, assigning backup personnel, or adjusting the schedule.

The organizer selects and approves a plan. NexCord executes the approved actions through its MCP server, verifies that the expected changes occurred, and reports the final state. If execution fails or the desired state is not reached, NexCord initiates recovery or compensating actions.

The platform also includes an **automated evaluation suite** that measures task completion, tool-selection accuracy, planning quality, latency, unsafe actions, verification success, and recovery performance across simulated operational incidents.
