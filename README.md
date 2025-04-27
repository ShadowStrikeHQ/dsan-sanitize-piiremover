# dsan-sanitize-PIIRemover
A command-line tool that automatically removes Personal Identifiable Information (PII) from text-based files. It leverages regular expressions and machine learning models (leveraging pre-trained models from transformers library) to identify and redact or replace PII such as phone numbers, email addresses, social security numbers, and credit card numbers. - Focused on Tools for systematically removing or modifying sensitive data from datasets or text, replacing it with realistic or obfuscated substitutes. Useful for creating safe test datasets, anonymizing logs, or securely redacting personal information.

## Install
`git clone https://github.com/ShadowStrikeHQ/dsan-sanitize-piiremover`

## Usage
`./dsan-sanitize-piiremover [params]`

## Parameters
- `-h`: Show help message and exit
- `-i`: Path to the input text file.
- `-o`: Path to the output text file.
- `-r`: No description provided
- `--no-ssn`: Disable SSN removal.
- `--no-phone`: Disable phone number removal.
- `--no-email`: Disable email address removal.
- `--no-credit-card`: Disable credit card number removal.

## License
Copyright (c) ShadowStrikeHQ
