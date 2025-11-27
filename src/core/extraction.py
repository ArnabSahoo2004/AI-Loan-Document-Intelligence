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
            "name_regex": r"(?:Name|Employee Name|Emp Name)[\s:]+([A-Za-z ]+)(?:\n|$)"
        }
        
        # Load Custom NER Model
        self.ner_model = None
        try:
            import os
            model_path = os.path.join("models", "ner_model")
            if os.path.exists(model_path):
                import spacy
                self.ner_model = spacy.load(model_path)
                logger.info("Loaded custom NER model.")
        except Exception as e:
            logger.warning(f"Could not load custom NER model: {e}")

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
        data["net_pay"] = self._extract_key_value(text, ["Net Pay", "Net Salary", "Take Home", "NET Salary", "NETPAY", "Net Payable"])
        data["total_earnings"] = self._extract_key_value(text, ["Total Earnings", "Gross Salary", "Total Pay", "Total Addition", "Total Earning", "Total"])
        data["total_deductions"] = self._extract_key_value(text, ["Total Deductions", "Total Deduction"])
        
        # OVERRIDE with Custom NER if available
        if self.ner_model:
            doc = self.ner_model(text)
            for ent in doc.ents:
                if ent.label_ == "SALARY":
                    val = self._parse_float(ent.text)
                    if val: data["total_earnings"] = val # Map SALARY to Total Earnings
                elif ent.label_ == "NET_PAY":
                    val = self._parse_float(ent.text)
                    if val: data["net_pay"] = val
                elif ent.label_ == "EMPLOYEE_NAME":
                    # Prepend to names list so it's prioritized
                    if ent.text.strip():
                        data["names"].insert(0, ent.text.strip())
        
        # Post-processing: Infer final salary
        data["salary"] = self._infer_salary(data)
        
        # Smart Math: Reconcile Data
        data = self._reconcile_data(data)
        
        print(f"DEBUG: Net Pay: {data['net_pay']}, Total Earnings: {data['total_earnings']}, Deductions: {data['total_deductions']}")
        
        return data

    def _reconcile_data(self, data):
        """
        Use math to fill in missing fields.
        Equation: Net Pay = Total Earnings - Total Deductions
        """
        net = data.get("net_pay", 0) or 0
        earnings = data.get("total_earnings", 0) or 0
        deductions = data.get("total_deductions", 0) or 0
        
        # Case 1: Missing Deductions
        if deductions == 0 and earnings > 0 and net > 0:
            if earnings >= net:
                data["total_deductions"] = earnings - net
                
        # Case 2: Missing Net Pay (less likely but possible)
        elif net == 0 and earnings > 0 and deductions > 0:
            if earnings >= deductions:
                data["net_pay"] = earnings - deductions
                
        # Case 3: Missing Earnings
        elif earnings == 0 and net > 0 and deductions > 0:
            data["total_earnings"] = net + deductions
            
        return data

    def _extract_key_value(self, text, keywords):
        """
        Find a number associated with a keyword, handling both structured lines and single-line streams.
        """
        # 1. Try Line-Based Logic (for structured docs)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    # Same line
                    match = re.search(r"[\d,]+(?:\.\d{2})?", line)
                    if match:
                        val = self._parse_float(match.group(0))
                        if val: return val
                    
                    # Next line
                    if i + 1 < len(lines):
                        next_line = lines[i+1]
                        if not any(k.lower() in next_line.lower() for k in ["Name", "Designation", "Month"]):
                            match_next = re.search(r"[\d,]+(?:\.\d{2})?", next_line)
                            if match_next:
                                val = self._parse_float(match_next.group(0))
                                if val: return val

        # 2. Fallback: Stream-Based Logic (for single-line OCR)
        # Look for Keyword followed by some chars (non-greedy) then a number
        # We limit the gap to ~100 chars to avoid matching across too much text
        for keyword in keywords:
            # Pattern: Keyword ... (junk) ... Number
            # Case insensitive search
            pattern = re.compile(re.escape(keyword) + r".{0,100}?([\d,]+(?:\.\d{2})?)", re.IGNORECASE | re.DOTALL)
            match = pattern.search(text)
            if match:
                val = self._parse_float(match.group(1))
                if val: return val
                
        return 0.0

    def _parse_float(self, val_str):
        try:
            val_str = val_str.replace(',', '')
            val = float(val_str)
            if 1990 <= val <= 2100: # Ignore years
                return None
            return val
        except ValueError:
            return None

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
        
        # 2. Fallback to Regex
        if not names:
            # Try "Name: ..." pattern
            # Updated to stop at common next-field keywords
            match = re.search(r"(?:Name|Employee Name|Emp Name)[\s:_]+([A-Za-z ]+?)(?=\s+(?:Total|Designation|Id|Pan|Bank|Date|\d))", text, re.IGNORECASE)
            if match:
                names.append(match.group(1).strip())
            
            # Fallback for simple "Name: Value" at end of line or string
            if not names:
                 match = re.search(r"(?:Name|Employee Name|Emp Name)[\s:_]+([A-Za-z ]+)(?:\n|$)", text, re.IGNORECASE)
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
        # 1. Trust explicit fields first
        if data.get("net_pay", 0) > 0:
            return data["net_pay"]
        
        if data.get("total_earnings", 0) > 0:
            return data["total_earnings"]
            
        # 2. Fallback to finding max amount from regex, but filter out years
        amounts = data.get("amounts", [])
        if not amounts: return 0.0
        
        clean_amounts = []
        for amt in amounts:
            clean = re.sub(r"Rs\.?", "", amt, flags=re.IGNORECASE)
            clean = re.sub(r"[^\d.]", "", clean)
            try:
                val = float(clean)
                # Filter out likely years (2000-2100) if they are the only match, 
                # but keep them if they are part of a larger set (unlikely to be salary anyway if < 3000)
                if 1990 <= val <= 2100:
                    continue
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
