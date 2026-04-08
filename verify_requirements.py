#!/usr/bin/env python3
"""
Verify both requirements are met before resubmission
"""

import yaml
from env.environment import SupportEnv
from env.models import Action

print("\n" + "="*70)
print("REQUIREMENT 1: At least 3 tasks with graders")
print("="*70)

with open('openenv.yaml') as f:
    config = yaml.safe_load(f)

tasks = config.get('tasks', [])
print(f'\nFound {len(tasks)} tasks:\n')

for task in tasks:
    name = task['name']
    grader = task.get('grader', 'NO GRADER')
    print(f"  ✓ {name:20s} -> {grader}")

req1 = len(tasks) >= 3
print(f"\n{'✓ PASS' if req1 else '✗ FAIL'}: {len(tasks)} tasks with graders (need 3+)\n")

print("="*70)
print("REQUIREMENT 2: Scores strictly between 0 and 1")
print("="*70)

# Test all combinations
print("\nTesting score ranges:\n")

all_scores = []
for task_type in ['easy_task', 'medium_task', 'hard_task']:
    env = SupportEnv()
    env.reset()
    
    # Run some actions
    actions = [
        Action(action_type='classify', value='high'),
        Action(action_type='assign', value=env.state_data.get('correct_agent', 'support')),
        Action(action_type='respond', value='resolved')
    ]
    
    for action in actions:
        result = env.step(action)
        if result['done']:
            break
    
    score = env.grade(task_type)
    all_scores.append(score)
    
    # Check constraints
    valid_low = score > 0.0
    valid_high = score < 1.0
    valid = valid_low and valid_high
    
    status = "✓" if valid else "✗"
    print(f"  {status} {task_type:20s} score={score:.4f} (0 < {score:.4f} < 1)")

print()

# Check no scores are exactly 0 or 1
has_zero = any(s == 0.0 for s in all_scores)
has_one = any(s == 1.0 for s in all_scores)
all_valid = all(0 < s < 1 for s in all_scores)

print(f"  ✓ No scores = 0.0: {not has_zero}")
print(f"  ✓ No scores = 1.0: {not has_one}")
print(f"  ✓ All in (0, 1): {all_valid}")

req2 = all_valid

print(f"\n{'✓ PASS' if req2 else '✗ FAIL'}: All scores strictly between 0 and 1\n")

print("="*70)
print("FINAL RESULT")
print("="*70)
print(f"\n  Requirement 1 (3+ graders):     {'✓ PASS' if req1 else '✗ FAIL'}")
print(f"  Requirement 2 (0 < score < 1): {'✓ PASS' if req2 else '✗ FAIL'}")

if req1 and req2:
    print("\n✓ ALL REQUIREMENTS MET - Ready to resubmit to HuggingFace\n")
else:
    print("\n✗ REQUIREMENTS NOT MET - Fix before resubmission\n")
