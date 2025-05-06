import functions_framework
from google.cloud import bigquery, secretmanager
import google.generativeai as genai
import pandas as pd
import logging
from pandas_gbq import to_gbq

PROJECT_ID = "reference-tide-458016-b3"  # replace this
SOURCE_QUERY = "SELECT * FROM reference-tide-458016-b3.logs.reply_logs"  # full table
DEST_TABLE = "logs.24hr_responses"  # destination table

# Access Gemini API key from Secret Manager
def api_key_secret_manager_accessor():
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{PROJECT_ID}/secrets/gemini-api-key/versions/latest"
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.exception("Failed to access Gemini API Key from Secret Manager")
        raise

# Gemini follow-up generation
def follow_ups_gemini(row):
    prompt = (
        f"You are a marketer following up with a nurse in Germany who has not replied to an earlier recruitment message.\n"
        f"--- Previous Message ---\n{row['Message']}\n"
        f"--- Nurse Info ---\n"
        f"Name: {row['name']}\nAge: {row['age']}\nInterest: {row['interest']}\n\n"
        "Craft a personalized follow-up. Emphasize better pay and quality of life in Germany. Limit to 6 lines or 55 words.\n"
        "Return ONLY the message text.\n\n"
        "Example: Hey Gary Newman, we just wanted to ensure if you're still dreaming of Germany! Better pay, better life awaits. "
        "You're an experienced pediatric nurse — exactly what they need!"
    )

    try:
        genai.configure(api_key=api_key_secret_manager_accessor())
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.exception("Gemini generation failed")
        print(e)
        return "ERROR_GENERATING_MESSAGE"

@functions_framework.http
def read_reply_status(request):
    try:
        bq_client = bigquery.Client(project=PROJECT_ID)
        query_job = bq_client.query(SOURCE_QUERY)
        df = query_job.result().to_dataframe()
    except Exception as e:
        logging.exception("BigQuery query failed")
        print(e)
        return {"error": "BigQuery query failed", "details": str(e)}, 500

    # Filter out already replied rows
    df = df[df['reply_status'] == False]

    if df.empty:
        return {"message": "No rows with reply_status=False"}, 200

    # Limit to 15 rows
    df = df.head(15)

    # Generate messages one by one
    df['follow_up_message'] = df.apply(follow_ups_gemini, axis=1)

    # Upload to BigQuery
    try:
        to_gbq(df, DEST_TABLE, project_id=PROJECT_ID, if_exists='append')
        return {"message": "Follow-up messages generated and saved to BigQuery."}, 200
    except Exception as bq_error:
        logging.exception("Failed to write to BigQuery")
        print(e)
        return {"error": f"BigQuery upload failed: {str(bq_error)}"}, 500
