#!/usr/bin/env python3
"""
Simple format validation test - no external dependencies
Tests that inference.py code structure is correct
"""

import re
import sys
from pathlib import Path

def validate_inference_code():
    """Check inference.py code for mandatory format compliance"""
    
    inference_file = Path(__file__).parent / "inference.py"
    
    if not inference_file.exists():
        print("[ERROR] inference.py not found")
        return False
    
    code = inference_file.read_text()
    checks = []
    
    # Check for mandatory format strings
    print("Validation Results:")
    print("=" * 70)
    
    # 1. Check for [START] line format
    if '[START] task=' in code and 'env=' in code and 'model=' in code:
        print("✓ [START] format line found")
        checks.append(True)
    else:
        print("✗ [START] format line missing")
        checks.append(False)
    
    # 2. Check for [STEP] format
    if '[STEP] step=' in code and 'action=' in code and 'reward=' in code and 'done=' in code:
        print("✓ [STEP] format line found")
        checks.append(True)
    else:
        print("✗ [STEP] format line missing")
        checks.append(False)
    
    # 3. Check for [END] format
    if '[END] success=' in code and 'steps=' in code and 'rewards=' in code:
        print("✓ [END] format line found")
        checks.append(True)
    else:
        print("✗ [END] format line missing")
        checks.append(False)
    
    # 4. Check for sys.stdout.flush() calls
    flush_count = code.count('sys.stdout.flush()')
    if flush_count >= 3:
        print(f"✓ sys.stdout.flush() calls found ({flush_count})")
        checks.append(True)
    else:
        print(f"✗ Not enough sys.stdout.flush() calls ({flush_count}, need >= 3)")
        checks.append(False)
    
    # 5. Check for reward formatting (.2f)
    if '{reward:.2f}' in code:
        print("✓ Reward formatting to 2 decimal places")
        checks.append(True)
    else:
        print("✗ Reward formatting not found")
        checks.append(False)
    
    # 6. Check for .lower() on boolean strings
    if 'str(done).lower()' in code and 'str(success).lower()' in code:
        print("✓ Boolean lowercasing (.lower()) implemented")
        checks.append(True)
    else:
        print("✗ Boolean lowercasing not found")
        checks.append(False)
    
    # 7. Check for no emojis
    emojis = [' [:alnum:] ', '[:alnum:]', '✓', '✗', '📋', '🎯', '💎', '⚠️', '🔄']
    emoji_found = False
    for emoji in emojis:
        if emoji in code:
            emoji_found = True
            print(f"✗ Found emoji/symbol in code: {emoji}")
            checks.append(False)
            break
    
    if not emoji_found:
        print("✓ No emojis or forbidden symbols found")
        checks.append(True)
    
    # 8. Check env.step() integration
    if 'env.step(action)' in code:
        print("✓ Environment step method called")
        checks.append(True)
    else:
        print("✗ Environment step method not found")
        checks.append(False)
    
    # 9. Check for main() function
    if 'def main():' in code:
        print("✓ main() function defined")
        checks.append(True)
    else:
        print("✗ main() function not found")
        checks.append(False)
    
    # 10. Check for exit code handling
    if 'sys.exit(exit_code)' in code or 'return 0 if success else 1' in code:
        print("✓ Exit code handling implemented")
        checks.append(True)
    else:
        print("✗ Exit code handling not found")
        checks.append(False)
    
    print("=" * 70)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"\nResult: PASSED ({passed}/{total} checks)")
        return True
    else:
        print(f"\nResult: FAILED ({passed}/{total} checks)")
        return False

if __name__ == "__main__":
    success = validate_inference_code()
    sys.exit(0 if success else 1)
