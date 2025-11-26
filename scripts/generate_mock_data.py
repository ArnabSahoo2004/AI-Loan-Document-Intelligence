import os
import random
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = "ai_loan_document_intelligence/data"
os.makedirs(DATA_DIR, exist_ok=True)

def generate_salary_slip(filename, name, employer, month, basic, hra, special, pf, tax):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Salary Slip - {month}", ln=1, align="C")
    pdf.cell(200, 10, txt=employer, ln=1, align="C")
    pdf.ln(10)
    
    pdf.cell(100, 10, txt=f"Employee Name: {name}", ln=0)
    pdf.cell(100, 10, txt=f"Designation: Software Engineer", ln=1)
    
    pdf.ln(10)
    pdf.cell(100, 10, txt="Earnings", border=1)
    pdf.cell(90, 10, txt="Amount (INR)", border=1, ln=1)
    
    pdf.cell(100, 10, txt="Basic Salary", border=1)
    pdf.cell(90, 10, txt=str(basic), border=1, ln=1)
    
    pdf.cell(100, 10, txt="HRA", border=1)
    pdf.cell(90, 10, txt=str(hra), border=1, ln=1)
    
    pdf.cell(100, 10, txt="Special Allowance", border=1)
    pdf.cell(90, 10, txt=str(special), border=1, ln=1)
    
    total_earnings = basic + hra + special
    pdf.cell(100, 10, txt="Total Earnings", border=1)
    pdf.cell(90, 10, txt=str(total_earnings), border=1, ln=1)
    
    pdf.ln(10)
    pdf.cell(100, 10, txt="Deductions", border=1)
    pdf.cell(90, 10, txt="Amount (INR)", border=1, ln=1)
    
    pdf.cell(100, 10, txt="Provident Fund", border=1)
    pdf.cell(90, 10, txt=str(pf), border=1, ln=1)
    
    pdf.cell(100, 10, txt="Professional Tax", border=1)
    pdf.cell(90, 10, txt=str(tax), border=1, ln=1)
    
    total_deductions = pf + tax
    pdf.cell(100, 10, txt="Total Deductions", border=1)
    pdf.cell(90, 10, txt=str(total_deductions), border=1, ln=1)
    
    pdf.ln(10)
    net_pay = total_earnings - total_deductions
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Net Pay: INR {net_pay}", ln=1, align="R")
    
    pdf.output(os.path.join(DATA_DIR, filename))
    print(f"Generated {filename}")

def generate_kyc_image(filename, name, pan, dob):
    img = Image.new('RGB', (600, 400), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Try to load a default font, otherwise use default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        header_font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        
    d.text((200, 30), "INCOME TAX DEPARTMENT", fill=(0,0,0), font=header_font)
    d.text((250, 70), "GOVT OF INDIA", fill=(0,0,0), font=font)
    
    d.text((50, 150), "Name:", fill=(0,0,0), font=font)
    d.text((150, 150), name, fill=(0,0,0), font=font)
    
    d.text((50, 200), "Date of Birth:", fill=(0,0,0), font=font)
    d.text((200, 200), dob, fill=(0,0,0), font=font)
    
    d.text((50, 250), "Permanent Account Number:", fill=(0,0,0), font=font)
    d.text((50, 280), pan, fill=(0,0,0), font=header_font)
    
    img.save(os.path.join(DATA_DIR, filename))
    print(f"Generated {filename}")

if __name__ == "__main__":
    # Generate Salary Slips
    generate_salary_slip("salary_slip_john.pdf", "John Doe", "Tech Corp Inc", "October 2023", 
                         basic=50000, hra=20000, special=15000, pf=1800, tax=200)
    
    generate_salary_slip("salary_slip_jane.pdf", "Jane Smith", "Finance Solutions Ltd", "September 2023", 
                         basic=80000, hra=32000, special=25000, pf=3600, tax=500)

    # 1. Standard High Income
    generate_salary_slip("salary_slip_high_income.pdf", "Alice High", "Big Tech Corp", "October 2023", 
                         basic=150000, hra=60000, special=40000, pf=5000, tax=15000)

    # 2. Standard Low Income (Should trigger risk warning)
    generate_salary_slip("salary_slip_low_income.pdf", "Bob Low", "Small Biz Inc", "October 2023", 
                         basic=8000, hra=2000, special=1000, pf=500, tax=0)

    # 3. Fraud Case: High Salary but suspiciously low tax (Anomaly)
    generate_salary_slip("salary_slip_fraud_tax.pdf", "Charlie Fraud", "Shell Corp", "October 2023", 
                         basic=200000, hra=80000, special=50000, pf=100, tax=0)

    # 4. Missing Fields Case (Empty Name/Employer - handled by passing empty strings)
    generate_salary_slip("salary_slip_missing_fields.pdf", "", "", "October 2023", 
                         basic=50000, hra=20000, special=15000, pf=1800, tax=200)

    # Generate KYC Images
    generate_kyc_image("pan_card_john.jpg", "JOHN DOE", "ABCDE1234F", "01/01/1990")
    generate_kyc_image("pan_card_jane.jpg", "JANE SMITH", "FGHIJ5678K", "15/08/1995")
