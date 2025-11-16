#!/usr/bin/env python3
"""
Jednoduchý testovací skript pro Event API.
"""

import requests
import uuid
import json

# Konfigurace
BASE_URL = "http://localhost:8000"
API_KEY = "your-api-key-here"  # Změňte na skutečný API klíč

def generate_guid():
    """Vygeneruje GUID."""
    return str(uuid.uuid4())

def test_version():
    """Test endpointu /version"""
    print("Testování /version endpointu...")
    headers = {
        "x-api-key": API_KEY,
        "x-correlation-id": generate_guid()
    }
    
    try:
        response = requests.get(f"{BASE_URL}/version", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Chyba: {e}")
        return False

def test_receive_event():
    """Test endpointu pro přijímání eventů"""
    print("\nTestování /subscriptions/{subscriptionId}/events endpointu...")
    
    subscription_id = generate_guid()
    correlation_id = generate_guid()
    
    headers = {
        "x-api-key": API_KEY,
        "x-correlation-id": correlation_id,
        "Accept-Language": "CZ",
        "Content-Type": "application/json"
    }
    
    payload = {
        "eventCount": 1,
        "bookTransactions": [
            {
                "transactionType": "DOMESTIC",
                "bookingDate": "2024-01-15",
                "lastUpdated": "2024-01-15T10:30:00Z",
                "iban": "CZ6508000000192000145399",
                "amount": {
                    "value": 1000.50,
                    "currency": "CZK"
                },
                "creditDebitIndicator": "CREDIT",
                "entryReference": "KB-1234567890",
                "counterParty": {
                    "name": "Test Company s.r.o.",
                    "iban": "CZ6508000000192000145399"
                },
                "references": {
                    "variable": "123456",
                    "receiver": "Test platba"
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/subscriptions/{subscription_id}/events",
            headers=headers,
            json=payload
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 204:
            print("✓ Event úspěšně přijat")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 204
    except Exception as e:
        print(f"Chyba: {e}")
        return False

def main():
    print("="*60)
    print("Testování Event API")
    print("="*60)
    
    # Test version endpointu
    version_ok = test_version()
    
    # Test receive event endpointu
    event_ok = test_receive_event()
    
    print("\n" + "="*60)
    print("Výsledky:")
    print(f"Version endpoint: {'✓ OK' if version_ok else '✗ CHYBA'}")
    print(f"Receive event endpoint: {'✓ OK' if event_ok else '✗ CHYBA'}")
    print("="*60)
    
    if version_ok and event_ok:
        print("\nVšechny testy prošly! Otevřete http://localhost:8000 pro zobrazení eventů.")
    else:
        print("\nNěkteré testy selhaly. Zkontrolujte konfiguraci API klíče v app.py")

if __name__ == "__main__":
    main()

