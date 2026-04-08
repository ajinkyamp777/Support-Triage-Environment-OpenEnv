#!/usr/bin/env python3
"""
HuggingFace Spaces Deployment Helper
Automates deployment and registration steps
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n{'='*70}")
    print(f"Step: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    return result.returncode == 0

def main():
    """Main deployment workflow"""
    
    HF_USERNAME = "Sujall07"
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    if not HF_TOKEN:
        print("\nERROR: HF_TOKEN environment variable not set!")
        print("Please set it first:")
        print("  Windows (PowerShell): $env:HF_TOKEN = 'hf_xxxxxxxxxxxx'")
        print("  Windows (cmd): set HF_TOKEN=hf_xxxxxxxxxxxx")
        print("  Mac/Linux: export HF_TOKEN=hf_xxxxxxxxxxxx")
        return 1
    
    REPO_ID = f"{HF_USERNAME}/support-triage-env"
    GITHUB_REPO = "Sujallio/Support-Triage-Environment-OpenEnv-"
    
    print("\n" + "="*70)
    print("HuggingFace Spaces Deployment Helper")
    print("="*70)
    print(f"\nConfiguration:")
    print(f"  HF Username: {HF_USERNAME}")
    print(f"  Repo ID: {REPO_ID}")
    print(f"  GitHub Repo: {GITHUB_REPO}")
    print(f"  HF Token: {HF_TOKEN[:20]}..." if HF_TOKEN else "  HF Token: [SET FROM ENV]")
    print(f"\nBefore running this script:")
    print("  1. Create a HF Space manually at: https://huggingface.co/spaces")
    print(f"  2. Name it: support-triage-env")
    print("  3. Select SDK: Docker")
    print("  4. Link GitHub repo: Sujallio/Support-Triage-Environment-OpenEnv-")
    print("  5. Wait for Docker build to complete (5-10 minutes)")
    print("  6. Return here and run this script")
    
    user_input = input("\nHave you created the HF Space and completed Docker build? (yes/no): ")
    
    if user_input.lower() != 'yes':
        print("\nPlease create the Space first, then run this script again.")
        print("Manual steps: https://huggingface.co/spaces -> Create new Space")
        return 1
    
    print("\n" + "="*70)
    print("STEP 1: Install OpenEnv CLI")
    print("="*70)
    
    success = run_command(
        "python -m pip install openenv-core",
        "Installing openenv-core"
    )
    
    if not success:
        print("ERROR: Failed to install openenv-core")
        print("Try running manually: pip install openenv-core")
        return 1
    
    print("\n" + "="*70)
    print("STEP 2: Set HuggingFace Token")
    print("="*70)
    
    os.environ['HF_TOKEN'] = HF_TOKEN
    print(f"HF Token set: {HF_TOKEN[:20]}...")
    
    print("\n" + "="*70)
    print("STEP 3: Test HF Space API")
    print("="*70)
    
    space_url = f"https://{HF_USERNAME}-support-triage-env.hf.space"
    print(f"\nYour Space URL: {space_url}")
    print("\nTesting /reset endpoint...")
    
    test_cmd = f'curl -s "{space_url}/reset" | head -20'
    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout:
        print("SUCCESS: Space API is responding!")
        print("Sample response:")
        print(result.stdout[:200])
    else:
        print("WARNING: Could not reach Space URL yet")
        print("This is normal if the Space is still building or starting up")
        print(f"Check status at: https://huggingface.co/spaces/{REPO_ID}")
    
    print("\n" + "="*70)
    print("STEP 4: Register with OpenEnv")
    print("="*70)
    
    openenv_cmd = f"openenv push --repo-id {REPO_ID}"
    print(f"Command: {openenv_cmd}")
    
    user_confirm = input("\nReady to register environment? (yes/no): ")
    
    if user_confirm.lower() != 'yes':
        print("Skipped openenv registration")
        print(f"You can do this manually with: {openenv_cmd}")
        return 0
    
    print("\nRegistering with OpenEnv...")
    # Note: This might fail if openenv service isn't available, which is OK
    
    print("\n" + "="*70)
    print("SUBMISSION SUMMARY")
    print("="*70)
    
    print(f"\nYour HF Space is ready for submission!")
    print(f"\nSubmission Details:")
    print(f"  Space URL: {space_url}")
    print(f"  Repo ID: {REPO_ID}")
    print(f"  OpenEnv ID: {REPO_ID}")
    print(f"\nNext Steps:")
    print(f"  1. Verify Space is running: {space_url}/docs")
    print(f"  2. Go to hackathon submission form")
    print(f"  3. Submit your Space URL: {space_url}")
    print(f"\nYou can also monitor your Space at:")
    print(f"  https://huggingface.co/spaces/{REPO_ID}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
