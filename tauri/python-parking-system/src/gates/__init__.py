"""
Gate Module Initialization
Exports all gate implementations for easy importing
"""

from .entry.manual import ManualEntryGate
from .entry.manless import ManlessEntryGate
from .exit.manual import ManualExitGate
from .exit.manless import ManlessExitGate

__all__ = [
    "ManualEntryGate",
    "ManlessEntryGate", 
    "ManualExitGate",
    "ManlessExitGate"
]


def create_gate(gate_type: str, gate_mode: str, gate_id: str = None):
    """
    Factory function to create gate instances
    
    Args:
        gate_type: "entry" or "exit"
        gate_mode: "manual" or "manless"
        gate_id: Optional custom gate ID
    
    Returns:
        Gate instance
    """
    if gate_type == "entry":
        if gate_mode == "manual":
            return ManualEntryGate(gate_id or "entry_manual")
        elif gate_mode == "manless":
            return ManlessEntryGate(gate_id or "entry_manless")
        else:
            raise ValueError(f"Invalid gate mode for entry: {gate_mode}")
    
    elif gate_type == "exit":
        if gate_mode == "manual":
            return ManualExitGate(gate_id or "exit_manual")
        elif gate_mode == "manless":
            return ManlessExitGate(gate_id or "exit_manless")
        else:
            raise ValueError(f"Invalid gate mode for exit: {gate_mode}")
    
    else:
        raise ValueError(f"Invalid gate type: {gate_type}")


def get_available_gate_types():
    """Get list of available gate configurations"""
    return [
        {"type": "entry", "mode": "manual", "class": "ManualEntryGate"},
        {"type": "entry", "mode": "manless", "class": "ManlessEntryGate"},
        {"type": "exit", "mode": "manual", "class": "ManualExitGate"},
        {"type": "exit", "mode": "manless", "class": "ManlessExitGate"}
    ]
