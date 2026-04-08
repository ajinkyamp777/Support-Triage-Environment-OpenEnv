#!/usr/bin/env python3
"""
Test script to validate inference.py output format compliance
with Meta Hackathon Phase 1 mandatory format requirements
"""

import subprocess
import sys
import re
from pathlib import Path


def validate_output(output: str) -> tuple[bool, list[str]]:
    """
    Validates inference.py output against mandatory format
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    lines = output.strip().split('\n')
    
    # Validate [START] line
    start_lines = [l for l in lines if l.startswith('[START]')]
    if not start_lines:
        errors.append("ERROR: No [START] line found")
    else:
        start_line = start_lines[0]
        # Pattern: [START] task={task_name} env={benchmark} model={model_name}
        if not re.match(r'\[START\] task=\w+ env=\w+ model=[\w\-\.]+', start_line):
            errors.append(f"ERROR: [START] format incorrect: {start_line}")
    
    # Validate [STEP] lines
    step_lines = [l for l in lines if l.startswith('[STEP]')]
    if not step_lines:
        errors.append("WARNING: No [STEP] lines found (might be normal if env resets immediately)")
    else:
        step_pattern = r'\[STEP\] step=\d+ action=\w+\:\w+ reward=-?\d+\.\d{2} done=(true|false) error=(null|.+)'
        for i, step_line in enumerate(step_lines):
            if not re.match(step_pattern, step_line):
                errors.append(f"ERROR: [STEP] format incorrect at line {i+1}: {step_line}")
                errors.append(f"  Expected pattern: [STEP] step=<int> action=<type>:<value> reward=<float> done=<bool> error=<null|msg>")
    
    # Validate [END] line
    end_lines = [l for l in lines if l.startswith('[END]')]
    if not end_lines:
        errors.append("ERROR: No [END] line found")
    else:
        end_line = end_lines[0]
        # Pattern: [END] success={true|false} steps={n} rewards={r1,r2,...}
        if not re.match(r'\[END\] success=(true|false) steps=\d+ rewards=[\d\.,\-]+', end_line):
            errors.append(f"ERROR: [END] format incorrect: {end_line}")
    
    # Check for forbidden patterns (emojis, old formats)
    forbidden = ['😊', '✓', '✗', '⏱️', '🎯', '💰', '❌', '✅']
    for i, line in enumerate(lines):
        for emoji in forbidden:
            if emoji in line:
                errors.append(f"ERROR: Line {i+1} contains forbidden emoji: {emoji}")
    
    # Check decimal formatting in [STEP] lines
    for step_line in step_lines:
        rewards = re.findall(r'reward=(-?\d+\.\d{2})', step_line)
        for reward in rewards:
            # Verify exactly 2 decimal places
            if not re.match(r'^-?\d+\.\d{2}$', reward):
                errors.append(f"ERROR: Reward not formatted to 2 decimal places: {reward}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def run_test():
    """Run inference.py and validate output"""
    print("=" * 70)
    print("Meta Hackathon Format Validation Test")
    print("=" * 70)
    print()
    
    project_path = Path(__file__).parent
    
    # Set environment to use mock inference (no API key needed)
    env = {
        'USE_MOCK': 'true',
        'PYTHONUNBUFFERED': '1'
    }
    
    print("[1] Running inference.py with mock inference...")
    print("    Command: python inference.py")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, str(project_path / "inference.py")],
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=30,
            env={**dict(os.environ), **env} if 'os' in dir() else env
        )
        
        output = result.stdout + result.stderr
        
        print("[2] Validating output format...")
        print()
        
        is_valid, errors = validate_output(output)
        
        if is_valid:
            print("✓ Format validation PASSED")
            print()
            print("[3] Output sample:")
            print("-" * 70)
            for line in output.split('\n')[:20]:  # First 20 lines
                if line.strip():
                    print(line)
            print("-" * 70)
        else:
            print("✗ Format validation FAILED")
            print()
            print("Errors found:")
            for error in errors:
                print(f"  {error}")
            print()
            print("Full output:")
            print("-" * 70)
            print(output)
            print("-" * 70)
        
        print()
        print("[4] Exit code check:")
        if result.returncode in (0, 1):
            print(f"✓ Valid exit code: {result.returncode}")
        else:
            print(f"✗ Invalid exit code: {result.returncode} (expected 0 or 1)")
            is_valid = False
        
        print()
        print("=" * 70)
        if is_valid:
            print("RESULT: ✓ Inference.py is compliant with Meta Hackathon format")
        else:
            print("RESULT: ✗ Inference.py has format compliance issues")
        print("=" * 70)
        
        return 0 if is_valid else 1
        
    except subprocess.TimeoutExpired:
        print("✗ Timeout: inference.py took longer than 30 seconds")
        return 1
    except Exception as e:
        print(f"✗ Error running test: {e}")
        return 1


if __name__ == "__main__":
    import os
    sys.exit(run_test())
