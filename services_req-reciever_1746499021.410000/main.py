import functions_framework
from flask import jsonify, request, make_response
import pandas as pd
from google.cloud import bigquery
from pandas_gbq import to_gbq


PROJECT_ID = 'reference-tide-458016-b3'    
DATASET_ID = 'logs'     
TABLE_ID = 'nurse_messages'        
timestamp = pd.Timestamp.now()
@functions_framework.http
def send_email(request):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    try:
        request_json = request.get_json(silent=True)
        headers = request_json.get("headers")
        rows = request_json.get("rows")

        if not headers or not rows:
            return _build_response({"error": "Missing headers or rows"}, 400)

        for col in ["Status", "timestamp"]:
            if col not in headers:
                headers.append(col)

        updated_rows = []
        for row in rows:
            padded_row = row + [""] * (len(headers) - 3 - len(row))
            padded_row += ["Success",timestamp]
            updated_rows.append(padded_row)

        
        df = pd.DataFrame(updated_rows, columns=headers)

        
        try:
            full_table_id = f"{DATASET_ID}.{TABLE_ID}"
            to_gbq(df, full_table_id, project_id=PROJECT_ID, if_exists='append')

        except Exception as bq_error:
            return _build_response({"error": f"BigQuery upload failed: {str(bq_error)}"}, 500)

        return _build_response({
            "headers": headers,
            "rows": updated_rows,
            "message": "Statuses updated and uploaded to BigQuery successfully."
        })

    except Exception as e:
        return _build_response({"error": str(e)}, 500)



def _build_cors_preflight_response():
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

def _build_response(data, status_code=200):
    response = jsonify(data)
    response.status_code = status_code
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
