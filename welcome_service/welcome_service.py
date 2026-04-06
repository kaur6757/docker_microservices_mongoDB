from flask import Flask, request
from datetime import datetime
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://mongodb:27017/")
db = client["bank_db"]
collection = db["processed_customers"]

# Create output folder if it does not exist
if not os.path.exists("output_letters"):
    os.makedirs("output_letters")


@app.route("/")
def home():
    return "Welcome Service Running"


@app.route("/process", methods=["POST"])
def process():
    customer = request.get_json()

    # Basic checks
    if not customer:
        return "No data received", 400

    if customer.get("status") != "valid":
        return "Customer is not valid", 400

    if customer.get("LETTER_TYPE", "").lower() != "welcome":
        return "This service only handles welcome letters", 400

    try:
        # Read template
        with open("templates/welcome_template.txt", "r", encoding="utf-8") as file:
            template = file.read()

        # Replace placeholders
        template = template.replace("{{CURRENT_DATE}}", datetime.now().strftime("%B %d, %Y"))
        template = template.replace("{{FIRST_NAME}}", str(customer.get("FIRST_NAME", "")))
        template = template.replace("{{LAST_NAME}}", str(customer.get("LAST_NAME", "")))
        template = template.replace("{{STREET_ADDRESS}}", str(customer.get("STREET_ADDRESS", "")))
        template = template.replace("{{CITY}}", str(customer.get("CITY", "")))
        template = template.replace("{{POSTAL_CODE}}", str(customer.get("POSTAL_CODE", "")))
        template = template.replace("{{COUNTRY}}", str(customer.get("COUNTRY", "")))
        template = template.replace("{{ACCOUNT_NUMBER}}", str(customer.get("ACCOUNT_NUMBER", "")))

        # Create output file name
        first_name = str(customer.get("FIRST_NAME", "Unknown")).strip().replace(" ", "_")
        last_name = str(customer.get("LAST_NAME", "Unknown")).strip().replace(" ", "_")
        filename = f"welcome_{first_name}_{last_name}.txt"
        output_path = os.path.join("output_letters", filename)

        # Save final letter
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write(template)

        # Save status in MongoDB
        customer["generated_letter"] = output_path
        customer["service_processed"] = "welcome_service"
        collection.insert_one(customer)

        print(f"Welcome letter created: {output_path}")
        return f"Welcome letter created: {output_path}", 200

    except FileNotFoundError:
        return "Template file not found", 500
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)