# Intelligent Fake Account Detection and Secure Reporting System

## Overview

A privacy-first system that detects fake and coordinated (sockpuppet network) social media profiles. Unlike most existing fake-profile detectors, this system adds two detection layers that are significantly harder for bad actors to fake:

1. Behavioral rhythm analysis - flags accounts with unnaturally consistent posting/activity timing
2. Cluster/network detection - identifies groups of near-identical profiles operating together as a coordinated fake account network

## Key Features

- ML-based Risk Scoring - RandomForest classifier trained on real Instagram fake/genuine account data (91% test accuracy)
- Behavioral Rhythm Analysis - computes a rhythm score from posting interval variance
- Cluster/Network Detection - compares each new profile against recently checked profiles
- Privacy-Safe Reporting - usernames are SHA-256 hashed before storage
- Data Retention Policy - automatic cleanup endpoint with dry-run mode
- Rate Limiting and API Key Auth - protects reporting endpoints from abuse

## Tech Stack

- Backend: FastAPI (Python)
- Database: PostgreSQL + SQLAlchemy
- ML: scikit-learn (RandomForestClassifier)
- Security: API Key auth, SlowAPI rate limiting, SHA-256 hashing

## API Endpoints

- POST /check-profile - Analyze a profile URL, returns ML risk score, rhythm score, and cluster flag
- POST /api/v1/report - Report a flagged profile (privacy-safe, hashed username)
- GET /api/v1/reports - List all filed reports
- POST /api/v1/upload-image-check - Upload a profile image for checking
- DELETE /api/v1/cleanup-old-data - Apply data retention policy (supports dry_run=true)

## Running Locally

cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

Visit http://127.0.0.1:8000/docs for interactive API documentation.

### Environment Variables

Create a .env file inside backend/:
DATABASE_URL=postgresql://localhost/fakeaccountdb

### Database Setup

createdb fakeaccountdb

Tables are auto-created on server startup.

## Model Training

The ML model is trained on the Instagram Fake Account Detection dataset from Kaggle.

python3 ml_training/train_model.py

This trains a RandomForestClassifier and saves it to backend/ml_models/fake_profile_model.pkl.

## Privacy and Security Design

- Usernames are never stored in plain text - always SHA-256 hashed before persistence
- Uploaded profile images are deleted immediately after processing
- Data retention policy allows automatic purging of records older than a configurable window
- All reporting endpoints require API key authentication and are rate-limited

## Team

Built for Vinhack 25.
