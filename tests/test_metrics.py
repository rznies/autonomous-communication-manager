import pytest
from emailmanagement.metrics import MetricsTracker

def test_metrics_tracker_idrr_calculation():
    tracker = MetricsTracker()
    
    tracker.record_incoming_message()
    tracker.record_incoming_message()
    tracker.record_incoming_message()
    tracker.record_incoming_message()
    # 4 incoming messages
    
    tracker.record_automated_decision()
    tracker.record_automated_decision()
    # 2 automated decisions
    
    assert tracker.calculate_idrr() == 0.50 # 50%

def test_metrics_tracker_cr_calculation():
    tracker = MetricsTracker()
    
    for _ in range(100):
        tracker.record_automated_decision()
        
    for _ in range(3):
        tracker.record_correction()
        
    assert tracker.calculate_cr() == 0.03 # 3%

def test_metrics_tracker_alerts_high_cr():
    tracker = MetricsTracker()
    
    for _ in range(100):
        tracker.record_automated_decision()
        
    for _ in range(6): # 6%
        tracker.record_correction()
        
    assert tracker.calculate_cr() == 0.06
    assert tracker.is_cr_alert_active() is True
