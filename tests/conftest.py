# -*- coding: utf-8 -*-
"""??????"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ????? SQLite ?????
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PASSWORD"] = "test"
os.environ["MYSQL_DATABASE"] = ":memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["ENV_MODE"] = "test"
os.environ["LOG_LEVEL"] = "DEBUG"
