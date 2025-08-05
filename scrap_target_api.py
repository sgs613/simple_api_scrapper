import sys
import json
import argparse
import requests
import random
import time

# TODO Custom file & path output
# TODO Add automatic response content recognition (adaptative output)
# TODO Add multiple api url support
# TODO Add suffix support to urls
# TODO Change logic from id to general url path variables for flexibility purposes
# TODO What about giving a json template of the expected response ? Allowing graphql kind of behavior
# TODO Rework the scrap method to separate url building from the write-to-file processing


def load_ids_from_file(filepath):
    if filepath:
        # TODO Allow the use of a seperator in file reading for ease of use
        try:
            with open(filepath, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ Error: File not found: {filepath}")
            return []
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return []
    else:
        return []


def get_json_data(url, id, auth_token):
    """
    Fetch data from API endpoint with basic error handling and logging.

    Args:
        url (str): Base URL for the API
        id (str): ID to append to the URL
        auth_token (str): Authorization token

    Returns:
        str: JSON formatted response or error message
    """

    full_url = f"{url}/{id}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "Authorization": f"{auth_token}",  # Given with auth schema
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(full_url, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"✅ Successfully got {id} - Status: {response.status_code}")

            # Try to parse as JSON and format it
            try:
                json_data = response.json()
                return json.dumps(json_data, indent=2)
            except json.JSONDecodeError as e:
                print(f"⚠️ Warning: Invalid JSON for {id} - {str(e)}")
                return json.dumps(
                    {
                        "id": id,
                        "error": "Invalid JSON response",
                        "status": "json_error",
                    },
                    indent=2,
                )

        else:
            print(f"❌ {response.reason} for {id} - Status: {response.status_code}")
            return json.dumps(
                {
                    "id": id,
                    "error": "API request error",
                    "status_code": response.status_code,
                    "status": response.reason,
                },
                indent=2,
            )
    except Exception as e:
        print(f"💥 Unexpected error for {id}: {str(e)}")
        return json.dumps(
            {
                "id": id,
                "error": f"Unexpected error: {str(e)}",
                "status": "unexpected_error",
            },
            indent=2,
        )


def scrap_api_to_file(url, ids, auth_token):
    """
    Scrape data for multiple IDs and save to a JSON file.

    Args:
        url (str): Base URL for the API endpoint
        ids (list): List of IDs to scrape
        auth_token (str): Authorization token
    """

    successful = 0
    failed = 0

    with open("output.json", "w") as f:
        f.write("[\n")  # Start JSON array
        for i, id in enumerate(ids):
            # Only supports JSON for now
            data = get_json_data(url, id, auth_token)

            # Check if it's an error response (simple string check)
            if '"error"' in data:
                failed += 1
            else:
                successful += 1

            # Write data with proper JSON formatting
            if i > 0:
                f.write(",\n")  # Add comma separator (except for first item)
            f.write(data)

            # Progress feedback every 10 requests
            if (i + 1) % 10 == 0:
                print(
                    f"📊 Progress: {i+1}/{len(ids)} - Success: {successful}, Failed: {failed}"
                )
            # Add human-like delays
            time.sleep(random.uniform(0.15, 0.75))  # Random delay between requests
        f.write("\n]")  # Close JSON array
        print(f"✅ Completed! Success: {successful}, Failed: {failed}")
        print(f"📁 Results saved to: {f.name}")


def main():
    # TODO Add single id input option
    # TODO Add error handling for each argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument(
        "--ids-file", type=str, help="Path to file containing IDs (one per line)"
    )
    parser.add_argument("--auth", type=str, help="Authorization token")
    args = parser.parse_args()
    ids = []
    if args.ids_file:
        ids = load_ids_from_file(args.ids_file)

    if len(ids):
        print(f"🚀 Starting scraper for {len(ids)} IDs...")
        scrap_api_to_file(args.url, ids, args.auth)
    else:
        print(f"😫 Nothing to process.")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
