from fpdf import FPDF
import os

def create_pdf(filename, text_lines):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for line in text_lines:
        pdf.cell(200, 10, txt=line, ln=1, align='L')
        
    output_path = os.path.join("data", filename)
    pdf.output(output_path)
    print(f"Created {output_path}")

def generate_data():
    os.makedirs("data", exist_ok=True)
    
    # 1. High Income (Eligible)
    # Filename must contain "high_income" to trigger Mock OCR logic
    create_pdf("generated_high_income.pdf", [
        "Salary Slip",
        "Name: Alice Wealthy",
        "Designation: Director",
        "PAN: ABCDE1234F",
        "Total Earnings: Rs. 1,50,000",
        "Deductions: Rs. 10,000",
        "Net Pay: Rs. 1,40,000",
        "Date: 01/01/2023"
    ])
    
    # 2. Fraud / Anomaly (Rejected)
    # Filename must contain "fraud_tax" to trigger Mock OCR logic
    create_pdf("generated_fraud_tax.pdf", [
        "Salary Slip",
        "Name: Charlie Cheat",
        "Designation: Consultant",
        "PAN: ABCDE1234F",
        "Total Earnings: Rs. 2,00,000",
        "Tax: Rs. 0",  # Suspicious: High income but 0 tax
        "Date: 01/01/2023"
    ])

if __name__ == "__main__":
    generate_data()
