from typing import Dict, Any, List

class BillingCompiler:
    """
    Computes litigation appearance billing totals including the traditional 10% Munshiana (clerkage) surcharge
    and compiles invoices with RCM (Reverse Charge Mechanism) compliance flags.
    """

    def __init__(self, clerkage_rate: float = 0.10):
        self.clerkage_rate = clerkage_rate

    def calculate_invoice_total(self, billing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates total litigation fees:
        T = (1 + mu) * ( Sum(Fe_i * E_i + Fne_i * NE_i) + Sum(D_j) + Sum(C_p) ) + E_actual
        """
        # Appearance counts and rates
        effective_hearings = billing_data.get("effective_hearings", 0)
        effective_rate = billing_data.get("effective_rate", 0.0)
        
        non_effective_hearings = billing_data.get("non_effective_hearings", 0)
        non_effective_rate = billing_data.get("non_effective_rate", 0.0)

        # Base drafting & conference charges
        drafting_fees = sum(billing_data.get("drafting_charges", []))
        conference_fees = sum(billing_data.get("conference_charges", []))
        
        # Out-of-pocket expenses
        actual_expenses = billing_data.get("actual_expenses", 0.0)

        # Calculations
        hearings_subtotal = (effective_hearings * effective_rate) + (non_effective_hearings * non_effective_rate)
        subtotal_before_clerkage = hearings_subtotal + drafting_fees + conference_fees
        
        clerkage_amount = subtotal_before_clerkage * self.clerkage_rate
        total_before_expenses = subtotal_before_clerkage + clerkage_amount
        grand_total = total_before_expenses + actual_expenses

        return {
            "subtotal_before_clerkage": round(subtotal_before_clerkage, 2),
            "clerkage_amount": round(clerkage_amount, 2),
            "total_before_expenses": round(total_before_expenses, 2),
            "actual_expenses": round(actual_expenses, 2),
            "grand_total": round(grand_total, 2)
        }

    def determine_gst_rcm_status(self, client_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Applies GST RCM (Reverse Charge Mechanism) rules based on turnover threshold.
        RCM (18% tax paid by client) applies if client is a registered business with turnover >= INR 20 Lakhs.
        Otherwise, legal services are exempt.
        """
        is_registered_business = client_profile.get("is_registered_business", False)
        turnover_inr_lakhs = client_profile.get("turnover_inr_lakhs", 0.0)

        if is_registered_business and turnover_inr_lakhs >= 20.0:
            return {
                "gst_rate": 18.0,
                "rcm_applicable": True,
                "invoice_notation": "GST payable by recipient under RCM",
                "payment_by": "Recipient (Client)"
            }
        else:
            return {
                "gst_rate": 0.0,
                "rcm_applicable": False,
                "invoice_notation": "Legal Service Exempt under GST Notification",
                "payment_by": "Not Applicable"
            }
