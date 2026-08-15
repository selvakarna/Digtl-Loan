import os
import json
import math
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Sample Pre-Configured Underwriting Profiles
PROFILES_DB = {
    "ABCDE1234F": {
        "pan": "ABCDE1234F",
        "name": "Selvakumar Panneerselvam",
        "mobile": "9840123456",
        "email": "selvakumar@example.com",
        "applicant_type": "Salaried Senior Executive",
        "company": "Quest Global Engineering Services Pvt Ltd",
        "role": "Senior AI & Computer Vision Tech Lead",
        "monthly_salary": 145000,
        "cibil_score": 792,
        "cibil_grade": "Prime (Excellent)",
        "active_loans_count": 2,
        "active_loans_debt": 5570000,
        "current_monthly_emi": 60000,
        "foir_ratio": 41.3,
        "bureau_overdue": 0,
        "bank_avg_balance": 485000,
        "bank_monthly_inflow": 165000,
        "gst_turnover": 0,
        "max_approved_limit": 2500000,
        "interest_rate": 10.25,
        "risk_category": "Tier-1 Low Risk",
        "speech_ta": "வணக்கம் செல்வகுமார். உங்களின் CIBIL ஸ்கோர் 792 மற்றும் வங்கி வரவு ஆய்வு செய்யப்பட்டு, ₹25,00,000 வரை உடனடி கடன் வரம்பு 10.25% வட்டியில் ஒப்புதல் செய்யப்பட்டுள்ளது.",
        "speech_en": "Hello Selvakumar. Based on your CIBIL score of 792 and banking cashflows, an instant loan limit of ₹25 Lakhs has been pre-approved at 10.25% APR."
    },
    "BKMPR9876K": {
        "pan": "BKMPR9876K",
        "name": "Chola Agri Exports & Coconut Mandi",
        "mobile": "9443211223",
        "email": "chola.agri@example.com",
        "applicant_type": "MSME / Business Enterprise",
        "company": "Chola Agri Exports Pvt Ltd",
        "role": "Managing Director & Promoter",
        "monthly_salary": 250000,
        "cibil_score": 765,
        "cibil_grade": "Very Good (MSME Commercial Prime)",
        "active_loans_count": 2,
        "active_loans_debt": 8500000,
        "current_monthly_emi": 88000,
        "foir_ratio": 35.2,
        "bureau_overdue": 0,
        "bank_avg_balance": 1850000,
        "bank_monthly_inflow": 720000,
        "gst_turnover": 8500000,
        "max_approved_limit": 5000000,
        "interest_rate": 11.50,
        "risk_category": "MSME Commercial Grade A",
        "speech_ta": "வணக்கம். உங்களின் வணிக ஜிஎஸ்டி ஆண்டு வருவாய் ₹85 லட்சம் மற்றும் CIBIL ஸ்கோர் 765 அடிப்படையில், ₹50,00,000 வரை உடனடி வணிகக் கடன் ஒப்புதல் செய்யப்பட்டுள்ளது.",
        "speech_en": "Welcome. Based on your GST turnover of ₹85 Lakhs and CIBIL score of 765, a business loan of ₹50 Lakhs has been pre-approved at 11.50% APR."
    },
    "PQXYZ5432M": {
        "pan": "PQXYZ5432M",
        "name": "Karthik Ramanathan",
        "mobile": "9789055667",
        "email": "karthik.r@example.com",
        "applicant_type": "Salaried IT Professional",
        "company": "Tata Consultancy Services Ltd (TCS)",
        "role": "Senior Software Engineer",
        "monthly_salary": 85000,
        "cibil_score": 780,
        "cibil_grade": "Excellent",
        "active_loans_count": 1,
        "active_loans_debt": 850000,
        "current_monthly_emi": 145000,
        "foir_ratio": 25.8,
        "bureau_overdue": 0,
        "bank_avg_balance": 240000,
        "bank_monthly_inflow": 92000,
        "gst_turnover": 0,
        "max_approved_limit": 1200000,
        "interest_rate": 10.75,
        "risk_category": "Tier-1 Low Risk",
        "speech_ta": "வணக்கம் கார்த்திக். உங்களின் CIBIL ஸ்கோர் 780 அடிப்படையில் ₹12,00,000 தனிநபர் கடன் 10.75% வட்டியில் ஒப்புதல் செய்யப்பட்டுள்ளது.",
        "speech_en": "Hello Karthik. Based on your CIBIL score of 780, an instant personal loan of ₹12 Lakhs has been approved at 10.75% APR."
    }
}

# OTP Storage (Mock memory)
OTP_STORE = {}

def calculate_emi(principal, annual_rate, tenure_months):
    if tenure_months <= 0 or principal <= 0:
        return 0
    monthly_rate = (annual_rate / 12.0) / 100.0
    emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / (math.pow(1 + monthly_rate, tenure_months) - 1)
    return round(emi)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json or {}
    pan = data.get('pan', '').strip().upper()
    mobile = data.get('mobile', '').strip()

    if len(pan) != 10:
        return jsonify({"success": False, "message": "Invalid PAN Number. Must be 10 alphanumeric characters."}), 400
    if len(mobile) < 10:
        return jsonify({"success": False, "message": "Invalid Mobile Number. Must be 10 digits."}), 400

    otp = str(random.randint(100000, 999999))
    OTP_STORE[mobile] = {
        "otp": otp,
        "pan": pan,
        "timestamp": datetime.now().isoformat()
    }

    return jsonify({
        "success": True,
        "message": f"OTP successfully sent to +91-XXXXX-{mobile[-4:]}",
        "otp_code": otp,  # Exposed for automated sandbox demo testing
        "expires_in_seconds": 600
    })

@app.route('/api/underwrite', methods=['POST'])
def underwrite_loan():
    data = request.json or {}
    pan = data.get('pan', '').strip().upper()
    mobile = data.get('mobile', '').strip()
    otp = data.get('otp', '').strip()
    gstin = data.get('gstin', '').strip().upper()

    if not otp:
        return jsonify({"success": False, "message": "Please enter the 6-digit consent OTP."}), 400

    # 1. Fetch Profile or Generate Dynamic Financial Underwriting
    if pan in PROFILES_DB:
        profile = dict(PROFILES_DB[pan])
    else:
        # Dynamic deterministic underwriting engine for any custom PAN
        hash_val = abs(hash(pan + mobile))
        cibil = 700 + (hash_val % 180)
        salary = 60000 + (hash_val % 150000)
        bank_bal = 100000 + (hash_val % 800000)
        gst_rev = (1500000 + (hash_val % 7000000)) if gstin else 0

        # AI Multi-Factor Limit Calculation
        approved_limit = int((salary * 18 + (gst_rev * 0.25) + bank_bal * 2) / 10000) * 10000
        approved_limit = min(max(approved_limit, 300000), 5000000)
        rate = 10.25 + (850 - cibil) * 0.015

        profile = {
            "pan": pan,
            "name": "Verified Registered Applicant",
            "mobile": mobile,
            "email": f"applicant.{pan[:5].lower()}@domain.in",
            "applicant_type": "MSME / Salaried Enterprise" if gstin else "Salaried Professional",
            "company": "Verified Enterprise Employer (EPFO / MCA Verified)",
            "role": "Senior Manager / Technical Lead",
            "monthly_salary": salary,
            "cibil_score": cibil,
            "cibil_grade": "Prime (Low Risk)" if cibil >= 750 else "Standard Credit Rating",
            "active_loans_count": (hash_val % 3) + 1,
            "active_loans_debt": approved_limit * 2,
            "current_monthly_emi": int(salary * 0.35),
            "foir_ratio": 35.0,
            "bureau_overdue": 0,
            "bank_avg_balance": bank_bal,
            "bank_monthly_inflow": salary + int(salary * 0.15),
            "gst_turnover": gst_rev,
            "max_approved_limit": approved_limit,
            "interest_rate": round(rate, 2),
            "risk_category": "Tier-1 Low Risk",
            "speech_ta": f"பான் எண் {pan} கடன் ஆய்வு அறிக்கை: CIBIL ஸ்கோர் {cibil}, வங்கி மற்றும் பணி விவரங்கள் ஆய்வு செய்யப்பட்டு ₹{approved_limit:,} வரை கடன் வரம்பு ஒப்புதல் செய்யப்பட்டுள்ளது.",
            "speech_en": f"Underwriting complete for PAN {pan}. Based on CIBIL score {cibil}, pre-approved loan limit is ₹{approved_limit:,} at {round(rate, 2)}% APR."
        }

    # Generate 3 Standard Loan Options
    default_amount = int(profile["max_approved_limit"] * 0.6)
    tenure_options = [
        {"tenure_months": 12, "emi": calculate_emi(default_amount, profile["interest_rate"], 12)},
        {"tenure_months": 24, "emi": calculate_emi(default_amount, profile["interest_rate"], 24)},
        {"tenure_months": 36, "emi": calculate_emi(default_amount, profile["interest_rate"], 36)},
        {"tenure_months": 48, "emi": calculate_emi(default_amount, profile["interest_rate"], 48)},
        {"tenure_months": 60, "emi": calculate_emi(default_amount, profile["interest_rate"], 60)}
    ]

    return jsonify({
        "success": True,
        "profile": profile,
        "tenure_options": tenure_options,
        "default_selected": {
            "amount": default_amount,
            "tenure_months": 36,
            "monthly_emi": calculate_emi(default_amount, profile["interest_rate"], 36)
        },
        "sanction_ref": f"SANCT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
        "timestamp": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    })

@app.route('/api/calculate-emi', methods=['POST'])
def get_custom_emi():
    data = request.json or {}
    amount = float(data.get('amount', 500000))
    rate = float(data.get('rate', 10.5))
    tenure = int(data.get('tenure_months', 36))

    emi = calculate_emi(amount, rate, tenure)
    total_payable = emi * tenure
    total_interest = total_payable - amount

    return jsonify({
        "success": True,
        "monthly_emi": emi,
        "total_payable": total_payable,
        "total_interest": total_interest,
        "principal": amount
    })

@app.route('/api/disburse', methods=['POST'])
def disburse_loan():
    data = request.json or {}
    amount = data.get('amount', 500000)
    pan = data.get('pan', 'ABCDE1234F')
    account_no = data.get('account_no', 'XXXXXXXX4589')
    ifsc = data.get('ifsc', 'HDFC0001234')

    utr_number = f"IMPS{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(100, 999)}"

    return jsonify({
        "success": True,
        "status": "DISBURSED (200 OK)",
        "utr_number": utr_number,
        "disbursed_amount": amount,
        "credited_account": account_no,
        "bank_ifsc": ifsc,
        "disbursal_timestamp": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"),
        "message": f"₹{amount:,} has been credited successfully to your bank account via instant IMPS transfer."
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
