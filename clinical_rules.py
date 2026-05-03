class DrugInteractionEngine:
    """
    Clinical Decision Support (CDS) - Phase 8
    Scans patient medication history and flags dangerous drug-drug interactions (DDI).
    Essential for preventing medical errors in a unified health record system.
    """
    
    def __init__(self):
        # Sample DDI Knowledge Base
        # In a production-grade system, this would link to external APIs like RxNorm or DrugBank.
        self.interaction_rules = [
            {
                "drugs": ["Aspirin", "Warfarin"],
                "severity": "CRITICAL",
                "message": "High risk of internal bleeding. Both medications inhibit clotting through different pathways."
            },
            {
                "drugs": ["Amlodipine", "Simvastatin"],
                "severity": "MODERATE",
                "message": "Increased risk of myopathy (muscle damage). Limit Simvastatin dose to 20mg daily."
            },
            {
                "drugs": ["Metformin", "Iodinated Contrast"],
                "severity": "CRITICAL",
                "message": "Risk of lactic acidosis. Metformin must be withheld 48 hours before and after radiologic procedures."
            },
            {
                "drugs": ["Sildenafil", "Nitroglycerin"],
                "severity": "FATAL",
                "message": "Severe hypotension (dangerous drop in blood pressure). Do not combine."
            }
        ]

    def check_interactions(self, history_meds, new_med_text):
        """
        Compares a new medication against a list of existing medications in the FHIR record.
        """
        alerts = []
        new_med_clean = str(new_med_text).lower().strip()
        
        for rule in self.interaction_rules:
            rule_drugs = [d.lower() for d in rule["drugs"]]
            
            # Check if the new drug being prescribed is mentioned in this interaction rule
            new_drug_in_rule = None
            for d in rule_drugs:
                if d in new_med_clean:
                    new_drug_in_rule = d
                    break
            
            if new_drug_in_rule:
                # Now check if ANY of the other drugs in the rule exist in the patient's history
                other_drugs_in_rule = [d for d in rule_drugs if d != new_drug_in_rule]
                
                for existing_med in history_meds:
                    existing_med_clean = str(existing_med).lower().strip()
                    
                    for other_drug in other_drugs_in_rule:
                        if other_drug in existing_med_clean:
                            alerts.append({
                                "severity": rule["severity"],
                                "interacting_drugs": rule["drugs"],
                                "message": rule["message"],
                                "detected_history_med": existing_med
                            })
                            
        return alerts

if __name__ == "__main__":
    # Simulation
    engine = DrugInteractionEngine()
    
    # Let's say Rahul is already taking Warfarin (prescribed at Apollo)
    rahul_history = ["Warfarin 5mg (Apollo)", "Metformin 500mg"]
    
    # A new doctor at Fortis tries to prescribe Aspirin
    new_rx = "Aspirin 75mg"
    
    print(f"Checking interactions for: {new_rx}")
    alerts = engine.check_interactions(rahul_history, new_rx)
    
    if alerts:
        for alert in alerts:
            print(f"\n⚠️ [{alert['severity']} INTERACTION DETECTED]")
            print(f"Reason: {alert['message']}")
            print(f"Conflicts with history med: {alert['detected_history_med']}")
    else:
        print("No clinical interactions found.")
