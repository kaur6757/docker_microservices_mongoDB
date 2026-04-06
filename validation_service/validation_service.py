import json
import requests
from pymongo import MongoClient

# URL of other services
WELCOME_SERVICE_URL = "http://welcome_service:5001/process"
OFFER_SERVICE_URL = "http://offer_service:5002/process"

# MongoDB connection
client = MongoClient("mongodb://mongodb:27017/")
db = client["bank_db"]
collection = db["validation_logs"]


def validate_record(customer):
    errors = []

    # Check first name
    if not customer.get("FIRST_NAME"):
        errors.append("Missing First Name")

    # Check last name
    if not customer.get("LAST_NAME"):
        errors.append("Missing Last Name")

    # Check account number
    acc_num = str(customer.get("ACCOUNT_NUMBER", ""))
    if not (8 <= len(acc_num) <= 16) or not acc_num.isdigit():
        errors.append(f"Invalid Account Number: {acc_num}")

    # Check address fields
    address_fields = ["STREET_ADDRESS", "CITY", "POSTAL_CODE", "COUNTRY"]
    for field in address_fields:
        if not customer.get(field):
            errors.append(f"Missing {field}")

    # Extra checks for offer letters
    if customer.get("LETTER_TYPE", "").lower() == "offer":
        if not customer.get("OFFER_TYPE"):
            errors.append("Missing OFFER_TYPE")
        if not customer.get("CREDIT_LIMIT"):
            errors.append("Missing CREDIT_LIMIT")

    # If there are errors, record is invalid
    if errors:
        return False, errors

    return True, []


def process_data(file_path):
    valid_records = []
    invalid_records = []

    # Read customers from JSON file
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        customers = data.get("customers", [])

    # Check each customer
    for customer in customers:
        is_valid, error_list = validate_record(customer)

        if is_valid:
            customer["status"] = "valid"
            letter_type = customer.get("LETTER_TYPE", "").lower()

            try:
                # Trigger welcome service
                if letter_type == "welcome":
                    requests.post(WELCOME_SERVICE_URL, json=customer)

                # Trigger offer service
                elif letter_type == "offer":
                    requests.post(OFFER_SERVICE_URL, json=customer)

                valid_records.append(customer)

                # Save valid log into MongoDB
                collection.insert_one({
                    "account_number": customer.get("ACCOUNT_NUMBER"),
                    "first_name": customer.get("FIRST_NAME"),
                    "last_name": customer.get("LAST_NAME"),
                    "status": "valid",
                    "letter_type": letter_type
                })

            except requests.exceptions.ConnectionError:
                print(f"Error: Could not trigger service for {customer.get('LAST_NAME')}")

        else:
            customer["status"] = "invalid"
            customer["errors"] = error_list
            invalid_records.append(customer)

            # Save invalid log into MongoDB
            collection.insert_one({
                "account_number": customer.get("ACCOUNT_NUMBER"),
                "first_name": customer.get("FIRST_NAME"),
                "last_name": customer.get("LAST_NAME"),
                "status": "invalid",
                "errors": error_list
            })

    # Save invalid records into JSON file for review (to show an example)
    with open("invalid_records_log.json", "w", encoding="utf-8") as err_file:
        json.dump(invalid_records, err_file, indent=4)

    # Print summary in terminal
    print(f"Processing complete. Valid: {len(valid_records)}, Invalid: {len(invalid_records)}")

    print("\nValid records:")
    for record in valid_records:
        print(f"{record.get('FIRST_NAME')} {record.get('LAST_NAME')} - {record.get('LETTER_TYPE')}")

    print("\nInvalid records:")
    for record in invalid_records:
        print(f"{record.get('FIRST_NAME')} {record.get('LAST_NAME')} - {record.get('errors')}")


if __name__ == "__main__":
    process_data("customers.json")