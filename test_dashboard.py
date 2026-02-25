#!/usr/bin/env python3
"""Test script to verify dashboard functionality."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend import auth as auth_service

# Initialize DB
auth_service.init_db()

# Create a test user
test_email = "test@example.com"
test_user = auth_service.create_user(test_email, "Test User", "password123")
print(f"✓ Created test user: {test_user}")

# Save an ATS score
auth_service.save_ats_score(test_email, 85, "Sample resume text", "Sample JD")
print(f"✓ Saved ATS score: 85")

# Save an interview session
auth_service.save_interview_session(test_email, 5, 8.5)
print(f"✓ Saved interview session: 5 questions, 8.5 avg score")

# Get last ATS score
last_score = auth_service.get_last_ats_score(test_email)
print(f"✓ Retrieved last ATS score: {last_score}")

# Get interview stats
sessions_count, avg_score = auth_service.get_interview_stats(test_email)
print(f"✓ Retrieved interview stats: {sessions_count} sessions, {avg_score} avg score")

# Verify
if last_score == 85 and sessions_count == 1 and avg_score == 8.5:
    print("\n✓ All tests passed!")
else:
    print(f"\n✗ Test failed!")
    print(f"  Expected: ATS=85, Sessions=1, Avg=8.5")
    print(f"  Got: ATS={last_score}, Sessions={sessions_count}, Avg={avg_score}")
