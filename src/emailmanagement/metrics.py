class MetricsTracker:
    def __init__(self, cr_alert_threshold: float = 0.05):
        self.total_incoming_messages = 0
        self.total_automated_decisions = 0
        self.total_corrections = 0
        self.cr_alert_threshold = cr_alert_threshold
        
    def record_incoming_message(self):
        self.total_incoming_messages += 1
        
    def record_automated_decision(self):
        self.total_automated_decisions += 1
        
    def record_correction(self):
        self.total_corrections += 1
        
    def calculate_idrr(self) -> float:
        """Inbox Decision Reduction Rate: automated decisions / total incoming"""
        if self.total_incoming_messages == 0:
            return 0.0
        return self.total_automated_decisions / self.total_incoming_messages
        
    def calculate_cr(self) -> float:
        """Correction Rate: user corrections / automated decisions"""
        if self.total_automated_decisions == 0:
            return 0.0
        return self.total_corrections / self.total_automated_decisions
        
    def is_cr_alert_active(self) -> bool:
        """Alerts if CR is above threshold (default 5%)"""
        return self.calculate_cr() > self.cr_alert_threshold
        
    def get_summary(self) -> str:
        idrr = self.calculate_idrr() * 100
        cr = self.calculate_cr() * 100
        alert = "⚠️ ALERT: High Correction Rate!" if self.is_cr_alert_active() else "✅ Health OK"
        
        return f"Metrics Summary:\n- IDRR: {idrr:.1f}%\n- CR: {cr:.1f}%\n- Status: {alert}"
