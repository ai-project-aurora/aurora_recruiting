# Recruiting agents for Aurora Recruiting
# Aurora Recruiting
Aurora Recruiting is a platform for recruiting, matching, and managing candidates to specific job roles.
It is designed to streamline the hiring process by providing tools for both recruiters and candidates. 
The bunch of agents in this repository are designed to automate various aspects of the recruiting process, from job posting to candidate matching and interview scheduling.
# Agent Overview
This repository contains a set of agents that work together to facilitate the recruiting process:
- **Candidate Agent**: Takes requirements from the recruiter and searches for candidates that match the job description.
- **Interview Agent**: Manages the scheduling of interviews between candidates and recruiters.
- **Recruiter Agent**: Handles job postings, manages applications, and communicates with candidates.
- **Analytics Agent**: Provides insights and analytics on job postings, candidate applications, and interview outcomes.
- **Calendar Agent**: Integrates with calendar services to manage interview schedules and reminders.
- **Salaries Agent**: Provides insights into salary expectations based on market data and candidate profiles.
- **Notification Agent**: Sends notifications to candidates and recruiters about application status, interview schedules, etc.
# Features
- **Job Posting**: Recruiters can post job openings with detailed descriptions.
- **Candidate Matching**: The system matches candidates to job roles based on their skills and experience.
- **Application Management**: Recruiters can manage applications, schedule interviews, and communicate with candidates.
- **Candidate Profiles**: Candidates can create profiles showcasing their skills, experience, and education.
- **Interview Scheduling**: Integrated tools for scheduling interviews with candidates.
- **Analytics Dashboard**: Recruiters can view analytics on job postings, candidate applications, and interview outcomes.
- **Notifications**: Automated notifications for candidates and recruiters about application status, interview schedules, etc.

# Installation
0. Use a virtual environment to avoid conflicts with other projects:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the adk server:
   ```bash
   adk web
   ```
