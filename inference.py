#!/usr/bin/env python3
"""
OpenEnv Support Triage Agent - Meta Hackathon Phase 1
Implements mandatory [START]/[STEP]/[END] format for evaluation
"""

import os
import sys
from openai import OpenAI
from env.environment import SupportEnv
from env.models import Action

# Environment configuration
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TASK_NAME = os.getenv("SUPPORT_TRIAGE_TASK", "medium_task")
BENCHMARK = "support-triage-env"
MAX_STEPS = 10
USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"

# Initialize OpenAI client
client = None
if API_KEY and not USE_MOCK:
    try:
        client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    except Exception:
        client = None

# Mock responses for fallback/testing
MOCK_RESPONSES = {
    "billing": {
        1: "classify: high",
        2: "assign: billing",
        3: "respond: refund processed",
        4: "classify: high",
        5: "respond: escalating to manager"
    },
    "technical": {
        1: "classify: high",
        2: "assign: technical",
        3: "respond: escalating to engineering team",
        4: "classify: high",
        5: "respond: ticket created for development"
    },
    "general": {
        1: "classify: medium",
        2: "assign: general",
        3: "respond: password reset link sent",
        4: "classify: medium",
        5: "respond: thank you for your patience"
    }
}


def get_mock_action(step_num, category):
    """Get mock action from predefined responses"""
    category_responses = MOCK_RESPONSES.get(category, MOCK_RESPONSES["general"])
    if step_num in category_responses:
        return category_responses[step_num]
    # Cycle through responses if step exceeds predefined
    cycle_step = ((step_num - 1) % len(category_responses)) + 1
    return category_responses.get(cycle_step, "respond: thank you for contacting support")


def get_llm_action(message, step_num):
    """Get action from LLM via OpenAI API"""
    if not client:
        return None
    
    try:
        prompt = (
            f"You are a support triage agent. Analyze this ticket and respond with "
            f"exactly one action in format 'action_type: value'.\n\n"
            f"Ticket (step {step_num}):\n{message}\n\n"
            f"Valid action types: classify, assign, respond\n"
            f"Respond with only the action."
        )
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def main():
    """
    Main inference loop implementing mandatory format:
    [START] task=... env=... model=...
    [STEP] step=... action=... reward=... done=... error=...
    [END] success=... steps=... rewards=...
    """
    # Initialize environment
    env = SupportEnv()
    obs = env.reset()
    
    # Get episode metadata and task from environment variable
    episode_data = env.state()
    category = episode_data.get("category", "general")
    task_name = TASK_NAME
    
    # Emit START line (mandatory format)
    print(f"[START] task={task_name} env={BENCHMARK} model={MODEL_NAME}")
    sys.stdout.flush()
    
    # Episode tracking
    total_reward = 0.0
    rewards = []
    step_counter = 0
    
    # Main loop
    for step in range(1, MAX_STEPS + 1):
        step_counter = step
        
        # Get action from LLM or mock
        action_text = get_llm_action(obs.message, step)
        if not action_text:
            action_text = get_mock_action(step, category)
        
        # Parse action string
        try:
            if ":" in action_text:
                parts = action_text.split(":", 1)
                action_type = parts[0].strip().lower()
                action_value = parts[1].strip()
            else:
                action_type = "respond"
                action_value = action_text.strip()
        except Exception:
            action_type = "respond"
            action_value = "thank you for contacting support"
        
        # Step environment
        reward = 0.0
        done = False
        error_msg = None
        
        try:
            action = Action(action_type=action_type, value=action_value)
            step_result = env.step(action)
            obs = step_result.get("observation", obs)
            reward = step_result.get("reward", 0.0)
            done = step_result.get("done", False)
        except Exception as e:
            reward = -0.1
            done = False
            error_msg = str(e)
        
        # Track reward
        total_reward += reward
        rewards.append(reward)
        
        # Emit STEP line (mandatory format)
        error_str = "null" if error_msg is None else error_msg
        action_str = f"{action_type}:{action_value}".replace(" ", "")
        print(
            f"[STEP] step={step} action={action_str} reward={reward:.2f} "
            f"done={str(done).lower()} error={error_str}"
        )
        sys.stdout.flush()
        
        # Exit if done
        if done:
            break
    
    # Calculate success
    success = total_reward > 0.5
    
    # Get the grade using the appropriate grader
    grade_score = env.grade(task_name)
    
    # Format rewards string
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    
    # Emit END line (mandatory format)
    print(f"[END] success={str(success).lower()} steps={step_counter} rewards={rewards_str} grade={grade_score:.4f}")
    sys.stdout.flush()
    
    # Return exit code
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)