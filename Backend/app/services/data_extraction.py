import spacy
import re
from werkzeug.exceptions import BadRequest
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_structured_data(raw_text: str) -> dict:
    """Extract structured data from raw text using spaCy and regex."""
    if not raw_text or not isinstance(raw_text, str):
        raise BadRequest("Invalid or empty text provided")

    try:
        # Process text with spaCy
        doc = nlp(raw_text)
        
        # Initialize result
        extracted_data = {
            'claim_amount': None,
            'claim_date': None,
            'claimant_name': None,
            'claim_type': None
        }

        # Extract entities with spaCy
        for ent in doc.ents:
            if ent.label_ == 'MONEY':
                extracted_data['claim_amount'] = ent.text
            elif ent.label_ == 'DATE':
                extracted_data['claim_date'] = ent.text
            elif ent.label_ == 'PERSON':
                extracted_data['claimant_name'] = ent.text

        # Use regex for specific patterns (e.g., claim type)
        claim_type_pattern = r'\b(auto|health|home|life)\b'
        match = re.search(claim_type_pattern, raw_text, re.IGNORECASE)
        if match:
            extracted_data['claim_type'] = match.group(1).lower()

        # Log extracted data
        logger.info("Extracted data: %s", extracted_data)
        return extracted_data
    except Exception as e:
        logger.error("Error extracting data: %s", str(e))
        raise BadRequest(f"Failed to extract data: {str(e)}")