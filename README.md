# Personalized Automated Reach Outs and Follow Ups

## Project Context

Enabling personalized automated emails with Gemini Driven Content.

## Tech Stack

Python, GCP Cloud Run Functions, BigQuery, Gemini, HTML, CSS, JavaScript  

---

## Walkthrough

### Front End : Folder Link

The front was written in HTML and Javascript and hosted on cloud functions using a python script that sends the index.html file and css file through flask’s send file when the browser invokes the URL

---

### CSV Upload : Folder Link

This Cloud  function takes in the front request when the upload button is hit handles the file and sends it back for it to be displayed.

---

### Content Generation : Folder Link

This Cloud function is invoked when the user hits the generate message button. The function takes in the selected rows and uses the defined prompt and gemini api key sourced from secret manager to call the Gemini API for each row and appends the Messages and sends it back to the front end

---

### Req-Reciever (Mock Gmail API) : Folder Link

Another Cloud function that takes the call when user hits send the email button on UI. The function then writes the whole data to a bigquery table with statuses and timestamp for logging and then returns the statuses and timestamp to front end as well.

---

### Follow Up Generator (Driven By Cron Job from Cloud Scheduler) : Folder Link

This function checks the table created by the scheduled query that updates reply status for 24hr window. It sources the recipients that did not reply and then calls gemini to draft a follow up message.  
Which is for now written into a BigQuery table.

---

## WHAT WOULD I HAVE DONE NEXT
---
### CUSTOMER JOURNEY TRACKING AND LEAD PRIORITIZATION

Implement a UTM embedded Link in the email messages with an image so that whenever the user clicks the event is fired and received by a Web analytics tool  
When the user lands on the website we can resolve his pseudo id(If GA4) with the email and track his movements across the website and assess amount to spend basis his lead propensity  
Use the pseudo id and lead propensity to upload the audience and re-target them through Google Ads with appropriate budgets

---

### RESPONSE MANAGEMENT

Automated handling through Gemini of first response basis the customer reply that will also tag a human  
If any information requested  
Enable a information retrieval system that mines information from FAQ collaterals Borderplus has and works in tandem with the response generator to provide first response on the question  

---

### EXPAND TO OTHER CHANNELS

Expand to whatsapp, sms, insta ads etc.
