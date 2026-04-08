# Support Triage Environment (OpenEnv)

An AI-powered reinforcement learning environment for automating customer support ticket triage and resolution.

## Problem Description

Customer support teams handle thousands of tickets daily, requiring efficient triage, prioritization, and resolution. This project simulates a real-world customer support ticket triage system as an OpenEnv environment, where an AI agent must analyze incoming tickets and take appropriate actions such as classification, assignment, and response generation.

The environment follows the OpenEnv standard API (reset(), step(), state()) and allows training and evaluation of agents on realistic operational workflows.

## Why This is a Real-World Problem

Customer support automation is a critical component of modern businesses. Companies like e-commerce platforms, SaaS providers, and fintech services rely heavily on:

- Ticket prioritization (urgent vs normal)
- Routing to correct departments (billing, technical, etc.)
- Generating accurate responses
- Customer satisfaction metrics

This environment models these real-world processes, making it useful for:

- Training AI support agents
- Evaluating LLM reasoning in multi-step workflows
- Benchmarking decision-making under constraints
- Testing robustness to noisy/imperfect inputs

## Action Space

The agent can perform the following structured actions:

Action Type | Description
----------|----------
classify  | Assign priority level (low, medium, high)
assign    | Route ticket to department (billing, tech, support)
respond   | Generate a response to resolve the issue

Each action is represented as:

```json
{
  "action_type": "string",
  "value": "string"
}
```

Example actions:
- classify: "high" - Mark ticket as high priority
- assign: "billing" - Route to billing department
- respond: "refund processed" - Send response to customer

## Observation Space

At each step, the agent receives:

```json
{
  "ticket_id": "integer",
  "message": "string with potential noise/typos",
  "customer_type": "premium or normal",
  "previous_actions": ["action1:value1", "action2:value2"],
  "last_action_error": false
}
```

Field Descriptions:
- ticket_id: Unique identifier for the ticket
- message: Customer issue description, may contain typos and noise
- customer_type: Either premium (20% reward boost) or normal
- previous_actions: History of actions taken in this episode
- last_action_error: Boolean indicating invalid action

## Ticket Categories and Datasets

The environment includes multiple ticket categories to test agent generalization:

### Billing Category
- Messages: Payment failures, refunds, charge disputes, billing errors
- Base Priority: high
- Correct Assignment: billing
- Dataset Size: 5 unique message templates
- Optimal Actions: classify(high) then assign(billing) then respond(with refund)

### Technical Category
- Messages: App crashes, bugs, API errors, database issues
- Base Priority: high
- Correct Assignment: tech
- Dataset Size: 5 unique message templates
- Optimal Actions: classify(high) then assign(tech) then respond(with escalation)

### General Category
- Messages: Password resets, account issues, feature questions, feedback
- Base Priority: medium
- Correct Assignment: support
- Dataset Size: 5 unique message templates
- Optimal Actions: classify(medium) then assign(support) then respond(with solution)

## Hackathon Bonus Features

### Feature 1: Message Noise (Realism)

Messages are corrupted with realistic variations to test robustness:
- ALL CAPS formatting: "MY PAYMENT FAILED!!!"
- Leetspeak variations: "p@ym3nt f@il3d"
- Mixed case with exclamation marks: "Need refund for order!!!!"
- Random formatting variations with emotional indicators

Noise Injection Rate: 40 percent chance per message

Impact: Agents must be robust to input variations, not memorize exact patterns.

### Feature 2: Multiple Ticket Datasets

The environment includes 15 unique ticket templates across 3 categories:

Billing Messages (5):
- "My payment failed but money deducted"
- "Charged twice for same order"
- "Need refund for subscription"
- "Billing shows wrong amount"
- "Cannot process payment card"

Technical Messages (5):
- "App is crashing on login"
- "Cannot upload files"
- "App keeps freezing"
- "Database connection error"
- "API returning 500 errors"

General Messages (5):
- "How do I reset my password?"
- "Account locked need help"
- "Cannot find feature in app"
- "Need to update account info"
- "Question about pricing plans"

Impact: Agents must learn category-aware strategies and handle diverse ticket types.

### Feature 3: Time Penalty (Speed Optimization)

Each step costs 0.05 in reward value to encourage fast resolution:

- Step 1: minus 0.05 penalty
- Step 2: minus 0.10 penalty (cumulative)
- Step 3: minus 0.15 penalty (cumulative)

Formula: reward = reward minus (0.05 times step_count)

Example Episode Breakdown:
```
Classify (high priority): +0.50 minus 0.05 = plus 0.45
Assign (correct team):    +0.40 minus 0.10 = plus 0.30
Respond (resolved):       +0.50 minus 0.15 = plus 0.35
                         --------------------
Total Episode Reward:                  1.10
```

Impact: Agents learn to resolve tickets quickly in 2-3 steps, not 10 steps.

## Reward Design

The reward function provides dense feedback to guide learning:

### Positive Rewards
- Correct priority classification: plus 0.5
- Correct department assignment: plus 0.3 (billing/tech) or plus 0.2 (general)
- Appropriate response/resolution: plus 0.5
- Premium customer bonus: multiply all rewards by 1.2

### Penalties
- Incorrect classification: minus 0.2
- Wrong department assignment: minus 0.1
- Step time penalty: minus 0.05 per step

### Episode Termination
Episode ends when:
- Agent sends valid response (done equals true)
- Maximum 10 steps reached

## Task Difficulty Levels

### Easy Task - Classify and Respond
- **Objective**: Correctly classify and respond to straightforward tickets
- **Expected Actions**: classify → respond  
- **Grader**: Points for correct classification (0.5) + appropriate response (0.5)
- **Typical Reward**: 0.3 to 0.5

### Medium Task - Classify, Assign, and Respond
- **Objective**: Classify ticket priority, route to correct department, send response
- **Expected Actions**: classify → assign → respond
- **Grader**: Classification (0.35) + correct department routing (0.35) + response quality (0.30)
- **Typical Reward**: 0.7 to 1.0
- **Category-Aware Routing**:
  - Billing issues → billing department
  - Technical issues → tech/engineering department
  - General issues → support/customer service

### Hard Task - Multi-step Noisy Input Resolution with Time Pressure
- **Objective**: Handle noisy inputs, classify, route, and resolve efficiently
- **Expected Actions**: classify → assign → respond (within 3 steps for bonus)
- **Grader**: Noisy classification (0.30) + routing (0.30) + resolution quality (0.25) + efficiency bonus (0.15)
- **Typical Reward**: 1.0 to 1.3
- **Efficiency Bonus**: Additional 0.15 for completing in ≤3 steps, scaled down for 4-7 steps

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Virtual environment support

### Step 1: Clone and Navigate
```bash
cd openenv-support-triage
```

### Step 2: Create Python Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

You should see (venv) in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

Dependencies installed:
- fastapi: Web framework for API
- uvicorn: ASGI server
- pydantic: Data validation
- openai: OpenAI API client

### Step 4: Run Environment Locally

Start the API server:
```bash
uvicorn app:app --reload
```

You should see output:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 5: Test API Endpoints

Open in browser: http://127.0.0.1:8000/docs

This opens Swagger UI for interactive testing.

Test Flow:
1. Click /reset endpoint
2. Execute to see initial observation
3. Click /step endpoint
4. Execute with example JSON:

Example 1: Classify priority
```json
{
  "action_type": "classify",
  "value": "high"
}
```

Example 2: Assign to department
```json
{
  "action_type": "assign",
  "value": "billing"
}
```

Example 3: Send response
```json
{
  "action_type": "respond",
  "value": "Your issue has been resolved"
}
```

5. Observe the returned reward and new observation

### Step 6: Run Inference Script

Option A: Mock Mode (No API credentials needed)
```bash
python inference_mock.py
```

Option B: Real OpenAI Mode (Requires API key)
```bash
# Windows
setx OPENAI_API_KEY "sk-your-key"
setx API_BASE_URL "https://api.openai.com/v1"
setx MODEL_NAME "gpt-4o-mini"

# Mac/Linux
export OPENAI_API_KEY="sk-your-key"
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"

# Then run
python inference.py
```

The inference script will:
- Reset the environment
- Run up to 10 steps
- Use mock responses or real API to decide actions
- Display rewards and final metrics
- Show improvement over 0.42 baseline

### Step 7: Run with Docker (Optional)

Build Docker image:
```bash
docker build -t support-triage-env .
```

Run container:
```bash
docker run -p 8000:8000 support-triage-env
```

API will be available at http://localhost:8000

## Baseline Scores

Random Policy Baseline:
- Average Episode Reward: 0.42
- Success Rate: 12 percent
- Average Steps to Resolution: 7-10 steps

Your agent should significantly exceed these baselines.

Performance Benchmarks:

Task Category | Random Baseline | Good Performance | Excellent Performance
-------------|-----------------|-----------------|---------------------
Billing      | 0.30            | 1.00            | 1.30
Technical    | 0.35            | 0.95            | 1.25
General      | 0.40            | 0.80            | 1.10

## Project Structure

```
openenv-support-triage/
  app.py                    FastAPI server with /reset and /step endpoints
  inference.py              Agent inference with mandatory Meta Hackathon format
  inference_mock.py         Mock inference without API (demo mode)
  requirements.txt          Python dependencies
  Dockerfile                Container configuration
  openenv.yaml              Complete environment metadata and task definitions
  README.md                 This file
  validate_code.py          Format validation checker (10/10 compliance checks)
  test_format.py            Runtime validation test suite
  env/
    __init__.py            Package initialization
    environment.py         Core SupportEnv class with noise and penalties
    models.py              Pydantic models (Observation, Action, Reward)
    graders.py             Task graders for easy/medium/hard difficulties
    tasks.py               Task definitions
```

## Environment Configuration

openenv.yaml:
```yaml
name: support-triage-env
version: 1.0
entrypoint: env.environment:SupportEnv
observation_model: env.models:Observation
action_model: env.models:Action
reward_model: env.models:Reward

tasks:
  - easy_ticket
  - medium_ticket
  - hard_ticket
```

## Additional Configuration Features

### Enable Mock Mode Only
```bash
setx USE_MOCK "true"
python inference.py
```

### Use Local LLM (Ollama)
```bash
# Install Ollama: https://ollama.ai
# Run local model
ollama run mistral

# Set environment
setx API_BASE_URL "http://localhost:11434/v1"
setx MODEL_NAME "mistral"
python inference.py
```

## API Endpoints

### /reset (GET)
Reset environment and get initial observation
Response: Observation object

### /step (POST)
Take action in environment
Request body:
```json
{
  "action_type": "classify|assign|respond",
  "value": "string"
}
```
Response: {observation, reward, done, info}

## Training Your Agent

This environment is compatible with:
- Stable Baselines3 (PPO, DQN, A2C)
- RLlib (TensorFlow, PyTorch)
- Custom RL implementations
- Imitation learning approaches

## Validation with OpenEnv CLI

After setup, validate with openenv-core (optional):
```bash
pip install openenv-core
openenv validate
```

## Key Features Summary

- Real-world customer support simulation
- Multiple ticket categories and datasets
- Message noise for robustness testing
- Time penalty for speed optimization
- Premium customer prioritization
- OpenEnv compliant API
- FastAPI for easy local testing
- Docker containerization
- Comprehensive reward shaping
- Dense feedback for agent learning

## Meta Hackathon Phase 1 Compliance

This environment is fully compliant with Meta Hackathon Phase 1 mandatory requirements:

### Mandatory Output Format
The inference.py script implements the required stdout format:

```
[START] task=<task_name> env=<benchmark_name> model=<model_name>
[STEP] step=<n> action=<type>:<value> reward=<x.xx> done=<true|false> error=<null|message>
[STEP] step=<n+1> action=<type>:<value> reward=<x.xx> done=<true|false> error=<null|message>
...
[END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
```

### Format Validation
Run format compliance check:
```bash
python validate_code.py
```

This validates:
- [START] format with task, env, model fields
- [STEP] format with all required fields (step, action, reward, done, error)
- [END] format with success, steps, rewards
- 2-decimal reward formatting
- Boolean lowercasing (true/false not True/False)
- No emojis or forbidden symbols
- Proper stdout buffering and exit codes

All 10 compliance checks PASS.

### Environment Variables Supported
- `OPENAI_API_KEY`: Your OpenAI API key
- `HF_TOKEN`: HuggingFace token (preferred over OPENAI_API_KEY)
- `API_BASE_URL`: Custom API endpoint (default: https://api.openai.com/v1)
- `MODEL_NAME`: Model to use (default: gpt-4o-mini)
- `USE_MOCK`: Set to 'true' for mock mode without API

## HuggingFace Spaces Deployment

This environment is deployed and live on HuggingFace Spaces!

### Live API Access
**URL**: https://Sujall07-support-triage-env.hf.space

### Accessing the Deployed Environment

1. **Interactive API Testing**
   - Open: https://Sujall07-support-triage-env.hf.space/docs
   - Uses Swagger UI to test /reset and /step endpoints
   - No authentication required

2. **Test with /reset Endpoint**
   ```bash
   curl https://Sujall07-support-triage-env.hf.space/reset
   ```
   Returns initial observation with ticket info

3. **Test with /step Endpoint**
   ```bash
   curl -X POST https://Sujall07-support-triage-env.hf.space/step \
     -H "Content-Type: application/json" \
     -d '{"action_type": "classify", "value": "high"}'
   ```
   Returns observation, reward, done flag, and info

### Environment Variables for Deployment
- `HF_TOKEN`: HuggingFace API token (for authentication)
- `OPENAI_API_KEY`: OpenAI API key for inference script (optional)
- `API_BASE_URL`: Custom API endpoint (default: https://api.openai.com/v1)
- `MODEL_NAME`: Model selection (default: gpt-4o-mini)
- `USE_MOCK`: Set to 'true' for mock mode without API calls

### Deployment Logs
Check Space logs at: https://huggingface.co/spaces/Sujall07/support-triage-env/logs

### Docker Configuration
The Space uses the included Dockerfile for containerization:
- Base Image: python:3.10-slim
- Port: 7860 (HuggingFace Spaces standard)
- Server: Uvicorn with hot-reload disabled

### Status
- ✅ Deployed on HF Spaces
- ✅ API endpoints tested and working
- ✅ Docker build successful
- ✅ Ready for hackathon evaluation

## Next Steps

1. Run local API Server
   ```bash
   uvicorn app:app --reload
   ```

2. Test endpoints at http://127.0.0.1:8000/docs

3. Run inference script
   ```bash
   python inference_mock.py
   ```

4. Train agent using RL framework of choice

5. Evaluate on all ticket categories

6. Submit to OpenEnv hackathon

## License

MIT License - Use freely for educational and commercial purposes.

## Support and Resources

For questions or issues:
- Check OpenEnv documentation
- Review example inference scripts
- Examine environment.py for implementation details
- Test with mock mode before using real APIs

---

Project Status: Production Ready for Hackathon Submission
Last Updated: April 2026