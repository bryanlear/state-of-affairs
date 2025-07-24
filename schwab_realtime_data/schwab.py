import os
import base64
import requests
import webbrowser
import json
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def construct_init_auth_url() -> tuple[str, str, str]:
    """Construct the initial authentication URL using environment variables."""

    app_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    callback_url = os.getenv("CALLBACK_URL", "https://127.0.0.1")

    if not app_key or not app_secret:
        raise ValueError("APP_KEY and APP_SECRET must be set in environment variables")

    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri={callback_url}"

    logger.info("Click to authenticate:")
    logger.info(auth_url)

    return app_key, app_secret, auth_url


def construct_headers_and_payload(returned_url, app_key, app_secret):
    """Extract authorization code from returned URL and construct headers/payload for token request."""
    try:
        # Extract the authorization code from the returned URL
        if 'code=' not in returned_url:
            raise ValueError("Authorization code not found in returned URL")

        code_start = returned_url.index('code=') + 5
        if '%40' in returned_url:
            code_end = returned_url.index('%40')
            response_code = f"{returned_url[code_start:code_end]}@"
        else:
            # Handle case where %40 might not be present
            code_end = returned_url.find('&', code_start)
            if code_end == -1:
                response_code = returned_url[code_start:]
            else:
                response_code = returned_url[code_start:code_end]

        credentials = f"{app_key}:{app_secret}"
        base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        headers = {
            "Authorization": f"Basic {base64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        callback_url = os.getenv("CALLBACK_URL", "https://127.0.0.1")
        payload = {
            "grant_type": "authorization_code",
            "code": response_code,
            "redirect_uri": callback_url,
        }

        return headers, payload

    except Exception as e:
        logger.error(f"Error constructing headers and payload: {e}")
        raise


def retrieve_tokens(headers, payload) -> dict:
    """Retrieve access and refresh tokens from Schwab API."""
    try:
        logger.info("Requesting tokens from Schwab API...")
        init_token_response = requests.post(
            url="https://api.schwabapi.com/v1/oauth/token",
            headers=headers,
            data=payload,
        )

        if init_token_response.status_code != 200:
            logger.error(f"Token request failed with status {init_token_response.status_code}")
            logger.error(f"Response: {init_token_response.text}")
            raise requests.exceptions.HTTPError(f"HTTP {init_token_response.status_code}: {init_token_response.text}")

        init_tokens_dict = init_token_response.json()
        logger.info("Successfully retrieved tokens")

        return init_tokens_dict

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during token retrieval: {e}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving tokens: {e}")
        raise


def save_tokens(tokens_dict: dict, token_path: str | None = None) -> None:
    """Save tokens to a JSON file for future use."""
    if token_path is None:
        token_path = os.getenv("TOKEN_PATH", "tokens.json")

    try:
        with open(token_path, 'w') as f:
            json.dump(tokens_dict, f, indent=2)
        logger.info(f"Tokens saved to {token_path}")
    except Exception as e:
        logger.error(f"Error saving tokens: {e}")
        raise


def load_tokens(token_path: str | None = None) -> dict:
    """Load tokens from a JSON file."""
    if token_path is None:
        token_path = os.getenv("TOKEN_PATH", "tokens.json")

    try:
        if not Path(token_path).exists():
            logger.warning(f"Token file {token_path} does not exist")
            return {}

        with open(token_path, 'r') as f:
            tokens = json.load(f)
        logger.info(f"Tokens loaded from {token_path}")
        return tokens
    except Exception as e:
        logger.error(f"Error loading tokens: {e}")
        return {}


def main():
    """Main function to handle Schwab API authentication and token retrieval."""
    try:
        # Check if tokens already exist
        existing_tokens = load_tokens()
        if existing_tokens and 'access_token' in existing_tokens:
            logger.info("Existing tokens found. You may want to refresh them if they're expired.")
            logger.info("Current tokens:")
            for key, value in existing_tokens.items():
                if key != 'refresh_token':  # Don't log the full refresh token for security
                    logger.info(f"{key}: {value}")
                else:
                    logger.info(f"{key}: {'*' * 20}")

            choice = input("Do you want to get new tokens? (y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                logger.info("Using existing tokens.")
                return existing_tokens

        # Get new tokens
        app_key, app_secret, cs_auth_url = construct_init_auth_url()

        logger.info("Opening browser for authentication...")
        webbrowser.open(cs_auth_url)

        logger.info("\nAfter authenticating, you'll be redirected to a URL that starts with your callback URL.")
        logger.info("Copy and paste the ENTIRE redirected URL here:")
        returned_url = input().strip()

        if not returned_url:
            raise ValueError("No URL provided")

        init_token_headers, init_token_payload = construct_headers_and_payload(
            returned_url, app_key, app_secret
        )

        init_tokens_dict = retrieve_tokens(
            headers=init_token_headers, payload=init_token_payload
        )

        # Save tokens for future use
        save_tokens(init_tokens_dict)

        logger.info("Authentication successful!")
        logger.info("Token details:")
        for key, value in init_tokens_dict.items():
            if key not in ['access_token', 'refresh_token']:
                logger.info(f"{key}: {value}")
            else:
                logger.info(f"{key}: {'*' * 20}")

        return init_tokens_dict

    except KeyboardInterrupt:
        logger.info("\nAuthentication cancelled by user.")
        return None
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise


if __name__ == "__main__":
    result = main()
    if result:
        logger.info("Authentication completed successfully!")
    else:
        logger.error("Authentication failed or was cancelled.")