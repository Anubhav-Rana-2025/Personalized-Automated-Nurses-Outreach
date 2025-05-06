import functions_framework
from flask import request, make_response
from google.cloud import secretmanager
import google.generativeai as genai
import pandas as pd
import io
import logging


def api_key_secret_manager_accessor():
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = "reference-tide-458016-b3"
        secret_name = "gemini-api-key"
        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.exception("Failed to access Secret Manager")
        raise


def generate_content_for_row(row):
    prompt = (
        f"Draft a personalized message for the following nurse:\n"
        f"Name: {row.get('name','?')}\n"
        f"Age: {row.get('age','?')}\n"
        f"Degree: {row.get('degree','?')}\n"
        f"Interest: {row.get('interest','?')}\n"
        f"City: {row.get('city','Not specified')}\n\n"
        "Pitch a recruitment opportunity in Germany for a medical nurse. "
        "Do not include a subject line. Do not include any placeholders. Only return the body. Personalize the message basis age, interest, degree and experience which you can assume from their age and degree. Keep it marketing friendly and call to action oriented and not more than 5 lines or 40 words."
        "Example {name: John Doe, age : 28 , degree: bsc in nursing , interest: pediatrician.}"
        "Response : Hey John Doe, did you know that Germany Offers amazing opportunities for nurses who are good with kids and have 3-5 years of experience like you? Do you want to know more? Drop us a message!!"
    )
    try:
        genai.configure(api_key=api_key_secret_manager_accessor())
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.exception("Gemini generation failed for row: %s", row)
        return "Error generating message"


@functions_framework.http
def generate(request):
    try:
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.set('Access-Control-Allow-Origin', '*')
            response.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS')
            response.headers.set('Access-Control-Allow-Headers', 'Content-Type')
            return response

        data = request.get_json()
        if not data or 'headers' not in data or 'rows' not in data:
            return make_response("Invalid input: expecting JSON with 'headers' and 'rows'", 400)

        df = pd.DataFrame(data['rows'], columns=data['headers'])

        messages = []
        for _, row in df.iterrows():
            msg = generate_content_for_row(row)
            messages.append(msg)

        df['Message'] = messages

        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)

        response = make_response(output.read())
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Content-Type', 'text/csv')
        return response

    except Exception as e:
        logging.exception("Server-side error occurred.")
        return make_response(f"Server Error: {str(e)}", 500)
