"""
Simple CLI interface for Python Parking System
"""

import asyncio
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from main import system_manager

app = typer.Typer(help="Python Parking System CLI")
console = Console()


@app.command()
def start():
    """Start the parking system"""
    console.print(Panel.fit("🚀 Starting Python Parking System", style="bold green"))
    asyncio.run(system_manager.initialize())
    asyncio.run(system_manager.start())


@app.command()
def status():
    """Show system status"""
    try:
        asyncio.run(system_manager.initialize())
        status = system_manager.get_system_status()
        
        table = Table(title="System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="magenta")
        
        table.add_row("System", "Running" if status["running"] else "Stopped")
        table.add_row("Database", "Connected" if status["database"]["connected"] else "Disconnected")
        table.add_row("ALPR", "Ready" if status["alpr"]["ready"] else "Error")
        
        for gate_id, gate_status in status["gates"].items():
            if "error" in gate_status:
                table.add_row(f"Gate {gate_id}", f"Error: {gate_status['error']}")
            else:
                table.add_row(f"Gate {gate_id}", gate_status.get("gate_status", "Unknown"))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error getting status: {e}", style="bold red")


@app.command()
def test_gate(gate_id: str):
    """Test a specific gate"""
    try:
        asyncio.run(system_manager.initialize())
        gate = system_manager.get_gate(gate_id)
        
        if not gate:
            console.print(f"❌ Gate {gate_id} not found", style="bold red")
            return
        
        status = gate.get_status()
        
        console.print(Panel.fit(
            f"Gate: {gate_id}\n"
            f"Type: {status.gate_type}\n"
            f"Mode: {status.gate_mode}\n"
            f"Status: {status.gate_status}\n"
            f"ALPR: {status.alpr_status}\n"
            f"Transactions: {status.transaction_count}",
            title=f"Gate {gate_id} Status"
        ))
        
    except Exception as e:
        console.print(f"❌ Error testing gate: {e}", style="bold red")


@app.command()
def list_gates():
    """List all available gates"""
    gates = [
        {"ID": "entry_manual", "Type": "Entry", "Mode": "Manual"},
        {"ID": "entry_manless", "Type": "Entry", "Mode": "Manless"},
        {"ID": "exit_manual", "Type": "Exit", "Mode": "Manual"},
        {"ID": "exit_manless", "Type": "Exit", "Mode": "Manless"}
    ]
    
    table = Table(title="Available Gates")
    table.add_column("Gate ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Mode", style="yellow")
    
    for gate in gates:
        table.add_row(gate["ID"], gate["Type"], gate["Mode"])
    
    console.print(table)


@app.command()
def init_db():
    """Initialize database"""
    console.print("🔄 Initializing database...", style="bold blue")
    try:
        asyncio.run(system_manager.initialize())
        console.print("✅ Database initialized successfully", style="bold green")
    except Exception as e:
        console.print(f"❌ Error initializing database: {e}", style="bold red")


if __name__ == "__main__":
    app()
