import random
from env.environment import SupportEnv
from env.models import Action

# Mock LLM responses optimized for categories
MOCK_RESPONSES = {
    "billing": {
        1: "classify: high",
        2: "assign: billing",
        3: "respond: refund processed - apologize for inconvenience"
    },
    "technical": {
        1: "classify: high",
        2: "assign: tech",
        3: "respond: escalating to engineering team for investigation"
    },
    "general": {
        1: "classify: medium",
        2: "assign: support",
        3: "respond: password reset link sent to your email"
    }
}

def get_mock_action(step_num, category):
    """Get intelligent mock action based on category and step"""
    category_responses = MOCK_RESPONSES.get(category, MOCK_RESPONSES["general"])
    return category_responses.get(step_num, category_responses[3])

def main():
    print("🤖 Support Triage Agent (MOCK MODE - Hackathon Edition)")
    print("=" * 70)

    env = SupportEnv()
    obs = env.reset()
    
    total_reward = 0.0
    episode_data = env.state()

    for step in range(1, 11):
        print(f"\n📋 Step {step}")
        print(f"   Category: {episode_data['category'].upper()}")
        print(f"   Ticket ID: {obs.ticket_id}")
        print(f"   Customer: {obs.customer_type.title()}")
        print(f"   Message: {obs.message}")

        # Get category-aware mock action
        action_text = get_mock_action(step, episode_data['category'])
        action_type, action_value = action_text.split(": ", 1)
        
        print(f"   🎯 Action: {action_type.title()} → {action_value}")

        action = Action(action_type=action_type.strip().lower(), value=action_value.strip())

        result = env.step(action)
        obs = result["observation"]
        reward = result["reward"]
        total_reward += reward
        info = result.get("info", {})
        
        # Show detailed reward breakdown
        time_penalty = info.get("time_penalty", 0)
        print(f"   💎 Reward: {reward:+.3f}")
        if time_penalty > 0:
            print(f"      ⏱️  Time penalty: -{time_penalty:.3f} (step {step})")
        
        print(f"   📊 Total: {total_reward:.3f}")

        if result["done"]:
            print(f"\n✅ Episode RESOLVED at step {step}")
            break

    print("\n" + "=" * 70)
    print("📊 FINAL METRICS")
    print("=" * 70)
    state = env.state()
    print(f"Category: {state['category'].upper()}")
    print(f"Customer Type: {state['customer_type'].title()}")
    print(f"Steps Taken: {len(state['history'])}")
    print(f"Actions: {' → '.join([h.split(':')[0].upper() for h in state['history']])}")
    print(f"\n🏆 Episode Reward: {total_reward:.3f}")
    print(f"📈 Baseline (random): 0.42")
    print(f"📈 Your agent: {total_reward:.3f}")
    
    if total_reward > 0.42:
        improvement = ((total_reward - 0.42) / 0.42) * 100
        print(f"🎉 {improvement:.1f}% better than baseline!")
    else:
        print("🚀 Train your agent to beat the baseline!")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
