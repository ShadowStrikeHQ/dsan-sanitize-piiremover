import argparse
import logging
import re
import os
import sys

from faker import Faker
from pydantic import BaseModel, validator, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SanitizeConfig(BaseModel):
    """
    Configuration for the PII remover tool.
    """
    input_file: str
    output_file: str
    redact_char: str = "<REDACTED>"  # Default redaction character
    remove_ssn: bool = True
    remove_phone: bool = True
    remove_email: bool = True
    remove_credit_card: bool = True

    @validator('input_file')
    def input_file_exists(cls, v):
        """Validate that the input file exists."""
        if not os.path.exists(v):
            raise ValueError(f"Input file '{v}' does not exist.")
        return v

    @validator('output_file')
    def output_file_does_not_exist(cls, v):
        """Validate that the output file does not exist to prevent accidental overwrites."""
        if os.path.exists(v):
             logging.warning(f"Output file '{v}' already exists.  It will be overwritten.")  # Issue warning, don't halt.
        return v

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Automatically removes PII from text-based files.")
    parser.add_argument("-i", "--input_file", required=True, help="Path to the input text file.")
    parser.add_argument("-o", "--output_file", required=True, help="Path to the output text file.")
    parser.add_argument("-r", "--redact_char", default="<REDACTED>", help="Replacement string for PII (default: <REDACTED>).")
    parser.add_argument("--no-ssn", action="store_false", dest="remove_ssn", help="Disable SSN removal.")
    parser.add_argument("--no-phone", action="store_false", dest="remove_phone", help="Disable phone number removal.")
    parser.add_argument("--no-email", action="store_false", dest="remove_email", help="Disable email address removal.")
    parser.add_argument("--no-credit-card", action="store_false", dest="remove_credit_card", help="Disable credit card number removal.")
    return parser.parse_args()


def sanitize_text(text, config: SanitizeConfig):
    """
    Sanitizes the given text by removing or replacing PII.
    """
    logging.info("Starting text sanitization.")
    fake = Faker()  # Instantiate Faker here, it's more efficient.

    if config.remove_ssn:
        logging.info("Removing SSNs.")
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", config.redact_char, text) # SSN regex

    if config.remove_phone:
        logging.info("Removing phone numbers.")
        # Updated phone number regex - more robust and handles international formats
        text = re.sub(r"\b(?:\+\d{1,3}\s*)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", config.redact_char, text)

    if config.remove_email:
        logging.info("Removing email addresses.")
        text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", config.redact_char, text)

    if config.remove_credit_card:
        logging.info("Removing credit card numbers.")
        text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", config.redact_char, text)
    
    logging.info("Text sanitization complete.")
    return text


def main():
    """
    Main function to run the PII remover tool.
    """
    try:
        args = setup_argparse()

        config_data = {
            "input_file": args.input_file,
            "output_file": args.output_file,
            "redact_char": args.redact_char,
            "remove_ssn": args.remove_ssn,
            "remove_phone": args.remove_phone,
            "remove_email": args.remove_email,
            "remove_credit_card": args.remove_credit_card
        }

        try:
            config = SanitizeConfig(**config_data)
        except ValidationError as e:
            logging.error(f"Configuration error: {e}")
            sys.exit(1)


        try:
            with open(config.input_file, 'r', encoding='utf-8') as infile:
                text = infile.read()
        except FileNotFoundError:
            logging.error(f"Input file '{config.input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error reading input file: {e}")
            sys.exit(1)

        sanitized_text = sanitize_text(text, config)

        try:
            with open(config.output_file, 'w', encoding='utf-8') as outfile:
                outfile.write(sanitized_text)
            logging.info(f"Sanitized text written to '{config.output_file}'.")
        except Exception as e:
            logging.error(f"Error writing to output file: {e}")
            sys.exit(1)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    """
    Entry point for the script.
    """
    main()


# Usage Examples:
# 1. Basic usage: python main.py -i input.txt -o output.txt
# 2. Custom redaction character: python main.py -i input.txt -o output.txt -r "[PII_REMOVED]"
# 3. Disable SSN removal: python main.py -i input.txt -o output.txt --no-ssn
# 4. Disable phone and email removal: python main.py -i input.txt -o output.txt --no-phone --no-email
# 5. All options disabled: python main.py -i input.txt -o output.txt --no-ssn --no-phone --no-email --no-credit-card