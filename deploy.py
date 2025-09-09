#!/usr/bin/env python3
"""
Simple deployment script for RHOAI AI Feature Sizing
"""

import asyncio
from pathlib import Path
import yaml

import subprocess
import sys


def main():
    """Deploy the services using llama-deploy CLI"""

    # Load the deployment configuration
    config_path = Path("deployment.yml")
    if not config_path.exists():
        print("❌ deployment.yml not found!")
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    print("🚀 Starting LlamaDeploy services...")
    print(f"📋 Deployment: {config['name']}")
    print(f"🎯 Services: {', '.join(config['services'].keys())}")

    # Start the API server directly with correct binding
    import os
    try:
        print("🌐 Starting API server...")
        # Set environment variables to force correct binding
        env = os.environ.copy()
        env["LLAMA_DEPLOY_HOST"] = "0.0.0.0"
        env["LLAMA_DEPLOY_PORT"] = "8000"
        subprocess.run([sys.executable, "-m", "llama_deploy.apiserver"], check=True, env=env)
    except KeyboardInterrupt:
        print("\n⏹️  Deployment stopped by user")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")


if __name__ == "__main__":
    print("🚀 RHOAI AI Feature Sizing - LlamaDeploy")
    print("=" * 50)
    main()
