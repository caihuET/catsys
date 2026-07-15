# -*- coding: utf-8 -*-
import subprocess, os
st = os.stat(r".git")
print(f".git writable: {os.access(r'.git', os.W_OK)}")
try:
    result = subprocess.run(["git", "add", "deploy/k3s/secrets.yaml"], capture_output=True, text=True, check=True)
    print("git add succeeded:", result.stdout)
except subprocess.CalledProcessError as e:
    print(f"git add failed: {e.stderr}")
except Exception as e:
    print(f"Error: {e}")
