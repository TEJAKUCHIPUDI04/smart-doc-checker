import requests
import json
from datetime import datetime
from config.config import Config

class FlexPriceBilling:
    def __init__(self):
        self.api_key = Config.FLEXPRICE_API_KEY
        self.base_url = "https://api.cloud.flexprice.io/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Pricing configuration
        self.pricing = {
            "document_analysis": 2.00,  # $2.00 per document
            "report_generation": 5.00   # $5.00 per report
        }
    
    def track_usage(self, session_id: str, event_type: str, quantity: int = 1, metadata: dict = None):
        """Track usage event with Flexprice"""
        try:
            event_data = {
                "customer_id": session_id,
                "event_name": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "properties": {
                    "quantity": quantity,
                    "metadata": metadata or {}
                }
            }
            
            response = requests.post(
                f"{self.base_url}/events",
                headers=self.headers,
                json=event_data
            )
            
            if response.status_code == 201:
                print(f"Usage tracked: {event_type} - {quantity}")
                return response.json()
            else:
                print(f"Billing tracking failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Billing error: {e}")
            return None
    
    def calculate_cost(self, documents_analyzed: int, reports_generated: int) -> float:
        """Calculate total cost based on usage"""
        doc_cost = documents_analyzed * self.pricing["document_analysis"]
        report_cost = reports_generated * self.pricing["report_generation"]
        return doc_cost + report_cost
    
    def get_usage_summary(self, session_id: str) -> dict:
        """Get usage summary for a customer"""
        try:
            response = requests.get(
                f"{self.base_url}/customers/{session_id}/usage",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Could not retrieve usage data"}
                
        except Exception as e:
            return {"error": f"Billing API error: {e}"}
    
    def create_invoice(self, session_id: str) -> dict:
        """Generate invoice for customer"""
        try:
            invoice_data = {
                "customer_id": session_id,
                "billing_period_start": datetime.utcnow().replace(day=1).isoformat(),
                "billing_period_end": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/invoices",
                headers=self.headers,
                json=invoice_data
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": "Could not generate invoice"}
                
        except Exception as e:
            return {"error": f"Invoice generation error: {e}"}
