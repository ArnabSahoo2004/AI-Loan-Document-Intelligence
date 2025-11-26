import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    logger.warning("Spacy model not found. Using regex-only extraction.")
    nlp = None
    SPACY_AVAILABLE = False

class DataExtractor:
    def __init__(self):
        self.patterns = {
            "pan": r"[A-Z]{5}[0-9]{4}[A-Z]{1}",
            "aadhaar": r"\d{4}\s\d{4}\s\d{4}",
            "email": r"[\w\.-]+@[\w\.-]+",
            "phone": r"(\+91[\-\s]?)?[0]?(91)?[789]\d{9}",
            "date": r"\d{2}[/-]\d{2}[/-]\d{4}",
            # Fixed: Use non-capturing group (?:\.\d{2})? so findall returns the whole match
            "amount": r"Rs\.?\s?[\d,]+(?:\.\d{2})?",
            "ifsc": r"[A-Z]{4}0[A-Z0-9]{6}",
            # Fixed: Strict regex to not match across lines (e.g. avoiding 'Designation' from next line)
            "name_regex": r"Name:[ \t]*([A-Za-z ]+)(?:\n|$)"
        }

    def extract_entities(self, text):
        """
        Extract structured data from raw text.
        """
        data = {
            "pan": self._extract_regex(text, "pan"),
            "aadhaar": self._extract_regex(text, "aadhaar"),
            "email": self._extract_regex(text, "email"),
            "phone": self._extract_regex(text, "phone"),
            "dates": self._extract_all_regex(text, "date"),
            "amounts": self._extract_all_regex(text, "amount"),
            "ifsc": self._extract_regex(text, "ifsc"),
            "names": self._extract_names(text),
            "orgs": self._extract_orgs(text)
        }
        
        # Robust Extraction for Salary Components
        data["basic_salary"] = self._extract_key_value(text, ["Basic", "Basic Salary", "Basic Pay", "Basic & DA"])
        data["hra"] = self._extract_key_value(text, ["HRA", "House Rent Allowance"])
        data["net_pay"] = self._extract_key_value(text, ["Net Pay", "Net Salary", "Take Home", "NET Salary"])
        data["total_earnings"] = self._extract_key_value(text, ["Total Earnings", "Gross Salary", "Total Pay", "Total Addition", "Total Earning"])
        data["total_deductions"] = self._extract_key_value(text, ["Total Deductions", "Total Deduction"])
        
        # Post-processing: Infer final salary
        data["salary"] = self._infer_salary(data)
        
        return data

    def _extract_key_value(self, text, keywords):
        """
        Find a line containing one of the keywords and extract the number from it.
        Also checks the NEXT line if no number is found on the same line (common in tables).
        """
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    # 1. Try finding number on the SAME line
                    match = re.search(r"[\d,]+(?:\.\d{2})?", line)
                    if match:
                        val_str = match.group(0).replace(',', '')
                        try:
                            return float(val_str)
                        except ValueError:
                            pass
                    
                    # 2. Try finding number on the NEXT line (if it exists)
                    if i + 1 < len(lines):
                        next_line = lines[i+1]
                        # Ensure next line isn't another keyword (heuristic)
                        if not any(k.lower() in next_line.lower() for k in ["Name", "Designation", "Month"]):
                            match_next = re.search(r"[\d,]+(?:\.\d{2})?", next_line)
                            if match_next:
                                val_str = match_next.group(0).replace(',', '')
                                try:
                                    return float(val_str)
                                except ValueError:
                                    pass
        return 0.0

    def _extract_regex(self, text, key):
        match = re.search(self.patterns[key], text)
        return match.group(0) if match else None

    def _extract_all_regex(self, text, key):
        return re.findall(self.patterns[key], text)

    def _extract_names(self, text):
        names = []
        # 1. Try Spacy
        if nlp:
            doc = nlp(text)
            names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        
        # 2. Fallback to Regex if empty (useful for mock data)
        if not names:
            # Try "Name: ..." pattern
            match = re.search(self.patterns["name_regex"], text)
            if match:
                raw_name = match.group(1).strip().split('\n')[0]
                names.append(raw_name)
            
            # Try "Employee Name: ..." pattern
            match = re.search(r"(?:Employee Name|Name of Employee)[\s:]+([A-Za-z ]+)", text, re.IGNORECASE)
            if match:
                names.append(match.group(1).strip())
        
        return names

    def _extract_orgs(self, text):
        if not nlp: return []
        doc = nlp(text)
        return [ent.text for ent in doc.ents if ent.label_ == "ORG"]

    def _infer_salary(self, data):
        """
        Determine the final salary value to use.
        Priority: Net Pay > Total Earnings > Max Amount Found
        """
        if data.get("net_pay", 0) > 0:
            return data["net_pay"]
        
        if data.get("total_earnings", 0) > 0:
            return data["total_earnings"]
            
        # Fallback to finding max amount from regex
        amounts = data.get("amounts", [])
        if not amounts: return 0.0
        
        clean_amounts = []
        for amt in amounts:
            clean = re.sub(r"Rs\.?", "", amt, flags=re.IGNORECASE)
            clean = re.sub(r"[^\d.]", "", clean)
            try:
                val = float(clean)
                clean_amounts.append(val)
            except ValueError:
                continue
        
        if clean_amounts:
            return max(clean_amounts)
        return 0.0

if __name__ == "__main__":
    extractor = DataExtractor()
    sample_text = "Name: John Doe, PAN: ABCDE1234F, Salary: Rs. 50,000"
    print(extractor.extract_entities(sample_text))
