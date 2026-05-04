import requests

class DrugInteractionEngine:
    OPENFDA_URL = "https://api.fda.gov/drug/event.json"
    
    KNOWN_INTERACTIONS = {
        ("aspirin", "warfarin"): ("CRITICAL", "Major bleeding risk — haemorrhagic stroke"),
        ("ibuprofen", "warfarin"): ("MODERATE", "Increased anticoagulant effect"),
        ("alcohol", "metformin"): ("MODERATE", "Lactic acidosis risk"),
    }
    
    def check(self, active_medications: list, new_drug: str) -> list:
        alerts = []
        new = new_drug.lower().strip()
        for active in active_medications:
            pair = tuple(sorted([active.lower().split()[0], new.split()[0]]))
            if pair in self.KNOWN_INTERACTIONS:
                severity, message = self.KNOWN_INTERACTIONS[pair]
                alerts.append({"severity": severity, "message": message, "pair": pair})
        return alerts
