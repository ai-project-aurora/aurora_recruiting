CANDIDATE_NOTIFICATION_PROMPT = """
You have selected candidates for an interview. Your task is to write a personal email notification to each candidate, inviting them to the interview and providing details about the position and the interview process.
Your email should include the following information:
1. **Candidate's Name**: Address the candidate by their name. (candidate.name)
2. **Position**: Clearly state the position for which the candidate is being considered.
3. **Interview Details**: Include the date, time, and location of the interview, or specify if it will be conducted online.
4. **Interview Process**: Briefly outline what the candidate can expect during the interview, such as the format (e.g., technical interview, behavioral interview) and any specific topics that will be covered.
5. **Contact Information**: Provide your contact information in case the candidate has any questions or needs to reschedule.
6. **Encouragement**: End the email with a positive note, encouraging the candidate to prepare and expressing enthusiasm about the interview.
Please ensure that the email is professional, friendly, and tailored to each candidate. Use the information provided by the previous agents to personalize the email as much as possible.
Store the email content in a file named `candidate_notification_{candidate.name}.txt` in the output directory. The file should contain the complete email text, ready to be sent to the candidate.
"""
