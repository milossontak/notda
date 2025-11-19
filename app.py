from fastapi import FastAPI, Header, HTTPException, Path, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import re
import traceback
import os
import logging
import json
import random
import qrcode
import io
from collections import deque

app = FastAPI(
    title="Event API",
    description="3rd party event API for receiving subscribed events.",
    version="2.0.0"
)

# Nastavení logování
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Middleware pro logování všech příchozích požadavků
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware pro logování všech příchozích požadavků."""
    start_time = datetime.now()
    
    # Zaznamenat požadavek
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Načíst body požadavku (pokud existuje)
    body = None
    body_bytes = None
    
    try:
        # Pro POST/PUT/PATCH požadavky načteme body
        if request.method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()
            if body_bytes:
                try:
                    # Zkusit parsovat jako JSON
                    body = json.loads(body_bytes.decode('utf-8'))
                except:
                    # Pokud to není JSON, uložit jako string
                    body = body_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        body = f"Error reading body: {str(e)}"
    
    # Pokud jsme přečetli body, musíme vytvořit nový request s těmito daty
    # aby FastAPI mohlo také přečíst body
    if body_bytes:
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        request._receive = receive
    
    # Zaznamenat do historie
    request_info = {
        "timestamp": start_time.isoformat(),
        "method": request.method,
        "path": str(request.url.path),
        "query_params": str(request.url.query) if request.url.query else None,
        "client_ip": client_ip,
        "user_agent": user_agent,
        "headers": dict(request.headers),
        "body": body,
        "status_code": None,
        "response_time_ms": None
    }
    
    # Logovat příchozí požadavek
    logger.info(f"📥 INCOMING: {request.method} {request.url.path} from {client_ip}")
    if body:
        logger.info(f"   Body: {json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body}")
    
    try:
        response = await call_next(request)
        
        # Zaznamenat odpověď
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        request_info["status_code"] = response.status_code
        request_info["response_time_ms"] = round(process_time, 2)
        
        # Logovat odpověď
        logger.info(f"📤 RESPONSE: {request.method} {request.url.path} -> {response.status_code} ({process_time:.2f}ms)")
        
        # Uložit do historie
        request_history.append(request_info)
        
        return response
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds() * 1000
        request_info["status_code"] = 500
        request_info["response_time_ms"] = round(process_time, 2)
        request_info["error"] = str(e)
        request_history.append(request_info)
        logger.error(f"❌ ERROR: {request.method} {request.url.path} -> {str(e)}")
        raise

# Ukládání přijatých eventů (v produkci by bylo lepší použít databázi)
events_storage = deque(maxlen=1000)  # Uchovává posledních 1000 eventů

# Ukládání historie všech příchozích požadavků
request_history = deque(maxlen=500)  # Uchovává posledních 500 požadavků

# Ukládání sledovaných plateb (VS -> payment info)
tracked_payments = {}  # {vs: {"iban": "...", "amount": ..., "created": "...", "status": "pending|paid"}}

# API klíč pro autentizaci
# Můžete nastavit buď zde, nebo přes environment variable API_KEY
API_KEY_ENV = os.getenv("API_KEY")
if API_KEY_ENV:
    # Pokud je nastaveno v environment variable, použij to
    VALID_API_KEYS = {API_KEY_ENV}
    print(f"✓ API klíč načten z environment variable")
else:
    # Jinak použij výchozí hodnotu (změňte na svůj API klíč!)
    VALID_API_KEYS = {"123456"}  # ⚠️ ZMĚŇTE NA SVŮJ API KLÍČ!
    print(f"⚠️  Používám výchozí API klíč. Pro produkci nastavte API_KEY environment variable nebo změňte hodnotu zde.")



# Pydantic modely podle specifikace
class CurrencyAmount(BaseModel):
    value: float
    currency: str = Field(..., max_length=3)


# Typy pro jednoduché string hodnoty
IBAN = str
AccountNumber = str
BankCode = str
BankIdentifierCode = str


class TransactionReferences(BaseModel):
    accountServicer: Optional[str] = None
    endToEndIdentification: Optional[str] = None
    variable: Optional[str] = None
    constant: Optional[str] = None
    specific: Optional[str] = None
    receiver: Optional[str] = None
    myDescription: Optional[str] = None


class TransactionCounterparty(BaseModel):
    iban: Optional[str] = None
    name: Optional[str] = None
    accountNo: Optional[str] = None
    bankBic: Optional[str] = None
    bankCode: Optional[str] = None
    bankName: Optional[str] = None


BankTransactionCodeIssuer = str  # "CBA" nebo "OTHER"


class BankTransactionCode(BaseModel):
    code: Optional[str] = Field(None, max_length=35)
    issuer: Optional[str] = Field(None, pattern="^(CBA|OTHER)$")


class GenericTransactionData(BaseModel):
    lastUpdated: str  # ISO 8601 date-time
    accountType: Optional[str] = None
    iban: str
    amount: CurrencyAmount
    creditDebitIndicator: str = Field(..., enum=["CREDIT", "DEBIT"])
    transactionType: Optional[str] = None
    entryReference: Optional[str] = None
    bankTransactionCode: Optional[BankTransactionCode] = None
    valueDate: Optional[str] = None  # ISO date
    instructed: Optional[CurrencyAmount] = None
    reversalIndicator: Optional[bool] = None
    counterParty: Optional[TransactionCounterparty] = None
    references: Optional[TransactionReferences] = None
    additionalTransactionInformation: Optional[str] = Field(None, max_length=500)


class BookingInformation(BaseModel):
    transactionType: Optional[str] = Field(None, enum=["INTEREST", "FEE", "DOMESTIC", "FOREIGN", "SEPA", "CASH", "CARD", "OTHER"])
    bookingDate: Optional[str] = None  # ISO date


class TransactionAdvice(BaseModel):
    transactionType: Optional[str] = None
    bookingDate: Optional[str] = None
    lastUpdated: str
    accountType: Optional[str] = None
    iban: str
    amount: CurrencyAmount
    creditDebitIndicator: str
    entryReference: Optional[str] = None
    bankTransactionCode: Optional[BankTransactionCode] = None
    valueDate: Optional[str] = None
    instructed: Optional[CurrencyAmount] = None
    reversalIndicator: Optional[bool] = None
    counterParty: Optional[TransactionCounterparty] = None
    references: Optional[TransactionReferences] = None
    additionalTransactionInformation: Optional[str] = None


class CardAuthorization(BaseModel):
    holdExpirationDate: Optional[str] = None  # ISO date
    lastUpdated: str
    accountType: Optional[str] = None
    iban: str
    amount: CurrencyAmount
    creditDebitIndicator: str
    transactionType: Optional[str] = None
    entryReference: Optional[str] = None
    bankTransactionCode: Optional[BankTransactionCode] = None
    valueDate: Optional[str] = None
    instructed: Optional[CurrencyAmount] = None
    reversalIndicator: Optional[bool] = None
    counterParty: Optional[TransactionCounterparty] = None
    references: Optional[TransactionReferences] = None
    additionalTransactionInformation: Optional[str] = None


class BookTransaction(BaseModel):
    transactionType: Optional[str] = None
    bookingDate: Optional[str] = None
    lastUpdated: str
    accountType: Optional[str] = None
    iban: str
    amount: CurrencyAmount
    creditDebitIndicator: str
    entryReference: Optional[str] = None
    bankTransactionCode: Optional[BankTransactionCode] = None
    valueDate: Optional[str] = None
    instructed: Optional[CurrencyAmount] = None
    reversalIndicator: Optional[bool] = None
    counterParty: Optional[TransactionCounterparty] = None
    references: Optional[TransactionReferences] = None
    additionalTransactionInformation: Optional[str] = None


class EventPayload(BaseModel):
    eventCount: Optional[int] = None
    transactionAdvices: Optional[List[TransactionAdvice]] = None
    bookTransactions: Optional[List[BookTransaction]] = None
    cardAuthorizations: Optional[List[CardAuthorization]] = None


class VersionResponse(BaseModel):
    version: str = Field(..., min_length=3, max_length=5)


class Error(BaseModel):
    code: Optional[str] = None
    additionalInfo: Optional[dict] = None
    message: str


class ErrorResponse(BaseModel):
    errors: List[Error]


# Validace GUID formátu
def validate_guid(value: str) -> bool:
    pattern = r'^(\{{0,1}([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}\}{0,1})$'
    return bool(re.match(pattern, value))


# Dependency pro Correlation ID
# Poznámka: API klíč není vyžadován - autentizace byla odstraněna
async def verify_correlation_id(x_correlation_id: str = Header(..., alias="x-correlation-id")):
    if not validate_guid(x_correlation_id):
        error_response = ErrorResponse(
            errors=[Error(
                message=f"Invalid correlation ID format: {x_correlation_id}",
                additionalInfo={"parameterName": "x-correlation-id", "rejectedValue": x_correlation_id}
            )]
        )
        raise HTTPException(
            status_code=400,
            detail=error_response.model_dump()
        )
    return x_correlation_id


@app.get("/version", tags=["Diagnostics"])
async def get_api_version(
    x_correlation_id: str = Depends(verify_correlation_id)
):
    """API implementation version. Must return 2.0 for this API definition."""
    return VersionResponse(version="2.0")


@app.head("/version", tags=["Diagnostics"])
async def head_api_version(
    x_correlation_id: str = Depends(verify_correlation_id)
):
    """HEAD request for version endpoint - used for health checks."""
    from fastapi.responses import Response
    return Response(status_code=200)


@app.get("/health", tags=["Diagnostics"])
async def health_check():
    """Simple health check endpoint - no authentication required."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Event API v2.0"
    }


@app.post("/subscriptions/{subscriptionId}/events", tags=["Events"], status_code=204)
async def receive_event(
    subscriptionId: str = Path(..., description="Subscription ID. Format: GUID 128-bit: 8-4-4-4-12"),
    x_correlation_id: str = Depends(verify_correlation_id),
    accept_language: str = Header("CZ", alias="Accept-Language"),
    payload: Optional[EventPayload] = None
):
    """Endpoint for receiving subscribed events."""
    # Validace Subscription ID
    if not validate_guid(subscriptionId):
        error_response = ErrorResponse(
            errors=[Error(
                message=f"Invalid subscription ID format: {subscriptionId}",
                additionalInfo={"parameterName": "subscriptionId", "rejectedValue": subscriptionId}
            )]
        )
        raise HTTPException(
            status_code=400,
            detail=error_response.model_dump()
        )
    
    # Validace Accept-Language
    if accept_language not in ["CZ", "EN"]:
        error_response = ErrorResponse(
            errors=[Error(
                message=f"Invalid Accept-Language value: {accept_language}",
                additionalInfo={"parameterName": "Accept-Language", "rejectedValue": accept_language}
            )]
        )
        raise HTTPException(
            status_code=400,
            detail=error_response.model_dump()
        )
    
    # Uložení eventu do storage
    event_data = {
        "timestamp": datetime.now().isoformat(),
        "subscriptionId": subscriptionId,
        "correlationId": x_correlation_id,
        "acceptLanguage": accept_language,
        "payload": payload.model_dump() if payload else None
    }
    events_storage.append(event_data)
    
    # Kontrola, zda příchozí event obsahuje platbu se sledovaným VS
    if payload:
        transactions = []
        if payload.bookTransactions:
            transactions.extend(payload.bookTransactions)
        if payload.transactionAdvices:
            transactions.extend(payload.transactionAdvices)
        
        for tx in transactions:
            if tx.references and tx.references.variable:
                vs = tx.references.variable
                if vs in tracked_payments:
                    # Aktualizovat status platby
                    tracked_payments[vs]["status"] = "paid"
                    tracked_payments[vs]["paid_at"] = datetime.now().isoformat()
                    tracked_payments[vs]["transaction"] = tx.model_dump() if hasattr(tx, 'model_dump') else tx
    
    return None  # 204 No Content


@app.get("/", response_class=HTMLResponse)
async def get_events_page():
    """Webová stránka pro zobrazení přijatých eventů."""
    html_content = """
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Demo Event API v.2 - Přijaté platby</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: #f5f5f5;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 28px;
            }
            .stats {
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }
            .stat-card {
                background: white;
                padding: 15px 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                flex: 1;
                min-width: 200px;
            }
            .stat-card h3 {
                font-size: 14px;
                color: #666;
                margin-bottom: 8px;
                font-weight: normal;
            }
            .stat-card .value {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
            .controls {
                margin-bottom: 20px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            button {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            button:hover {
                background-color: #2980b9;
            }
            button:disabled {
                background-color: #bdc3c7;
                cursor: not-allowed;
            }
            .events-list {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .event-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .event-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
                flex-wrap: wrap;
                gap: 10px;
            }
            .event-header h3 {
                color: #2c3e50;
                font-size: 18px;
            }
            .event-meta {
                font-size: 12px;
                color: #666;
            }
            .event-payload {
                margin-top: 15px;
            }
            .event-payload pre {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-size: 13px;
                line-height: 1.5;
            }
            .event-highlights {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            }
            .highlight-card {
                background: #f8f9fa;
                padding: 12px 15px;
                border-radius: 5px;
                border-left: 3px solid #3498db;
            }
            .highlight-card h4 {
                font-size: 11px;
                text-transform: uppercase;
                color: #666;
                margin-bottom: 5px;
                font-weight: 600;
            }
            .highlight-card .value {
                font-size: 16px;
                color: #2c3e50;
                font-weight: 500;
            }
            .highlight-card.amount {
                border-left-color: #27ae60;
            }
            .highlight-card.amount .value {
                color: #27ae60;
                font-weight: 600;
            }
            .highlight-card.counterparty {
                border-left-color: #9b59b6;
            }
            .references-list {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .reference-item {
                font-size: 13px;
                color: #555;
            }
            .reference-item strong {
                color: #333;
                margin-right: 5px;
            }
            .snackbar-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
            }
            .snackbar {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 16px;
                animation: slideIn 0.3s ease-out;
                border-left: 4px solid #3498db;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .snackbar:hover {
                transform: translateX(-5px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.2);
            }
            .snackbar.new-event {
                border-left-color: #27ae60;
            }
            .snackbar-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 10px;
            }
            .snackbar-title {
                font-weight: 600;
                color: #2c3e50;
                font-size: 14px;
            }
            .snackbar-close {
                background: none;
                border: none;
                font-size: 20px;
                color: #999;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background 0.2s;
            }
            .snackbar-close:hover {
                background: #f0f0f0;
                color: #333;
            }
            .snackbar-content {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .snackbar-row {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .snackbar-label {
                font-size: 12px;
                color: #666;
                min-width: 80px;
            }
            .snackbar-value {
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            .snackbar-amount {
                color: #27ae60;
                font-weight: 600;
                font-size: 16px;
            }
            @keyframes slideIn {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
            .snackbar.hiding {
                animation: slideOut 0.3s ease-out forwards;
            }
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #999;
            }
            .empty-state h2 {
                font-size: 24px;
                margin-bottom: 10px;
                color: #666;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Event API v2.0 - Přijaté platby</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>Celkem eventů</h3>
                    <div class="value" id="total-events">0</div>
                </div>
                <div class="stat-card">
                    <h3>Transaction Advices</h3>
                    <div class="value" id="transaction-advices">0</div>
                </div>
                <div class="stat-card">
                    <h3>Book Transactions</h3>
                    <div class="value" id="book-transactions">0</div>
                </div>
                <div class="stat-card">
                    <h3>Card Authorizations</h3>
                    <div class="value" id="card-authorizations">0</div>
                </div>
            </div>
            
            <div class="controls">
                <button onclick="loadEvents()">Obnovit</button>
                <button onclick="clearEvents()">Vymazat vše</button>
                <button onclick="createQRPayment()" style="background-color: #27ae60;">Vytvořit QR platbu</button>
                <label>
                    <input type="checkbox" id="auto-refresh" onchange="toggleAutoRefresh()"> Automatické obnovování
                </label>
            </div>
            
            <div id="qr-payment-section" style="display: none; margin-bottom: 30px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="margin-bottom: 15px; color: #2c3e50;">QR Platba</h2>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: flex-start;">
                    <div>
                        <img id="qr-image" src="" alt="QR kód" style="max-width: 300px; border: 2px solid #ddd; border-radius: 5px; padding: 10px; background: white;">
                    </div>
                    <div style="flex: 1;">
                        <div id="qr-payment-info" style="margin-bottom: 15px;"></div>
                        <div style="margin-top: 15px;">
                            <strong>SPAYD řetězec:</strong>
                            <pre id="qr-spayd" style="background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 12px; word-break: break-all; margin-top: 5px;"></pre>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="tracked-payments" style="margin-bottom: 30px;"></div>
            
            <div id="events-container" class="events-list">
                <div class="loading">Načítání...</div>
            </div>
        </div>
        
        <div id="snackbar-container" class="snackbar-container"></div>
        
        <script>
            let autoRefreshInterval = null;
            let lastEventCount = 0;
            let snackbarCheckInterval = null;
            
            function formatDate(dateString) {
                const date = new Date(dateString);
                return date.toLocaleString('cs-CZ', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            }
            
            function countEvents(events) {
                let transactionAdvices = 0;
                let bookTransactions = 0;
                let cardAuthorizations = 0;
                
                events.forEach(event => {
                    if (event.payload) {
                        transactionAdvices += (event.payload.transactionAdvices || []).length;
                        bookTransactions += (event.payload.bookTransactions || []).length;
                        cardAuthorizations += (event.payload.cardAuthorizations || []).length;
                    }
                });
                
                return {
                    total: events.length,
                    transactionAdvices,
                    bookTransactions,
                    cardAuthorizations
                };
            }
            
            function formatAmount(amount) {
                if (!amount) return 'N/A';
                const value = typeof amount.value === 'number' ? amount.value : parseFloat(amount.value);
                const currency = amount.currency || 'CZK';
                // Formátování čísla s mezerami jako oddělovači tisíců
                const formattedValue = new Intl.NumberFormat('cs-CZ', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }).format(value);
                return `${formattedValue} ${currency}`;
            }
            
            function formatReferences(refs) {
                if (!refs) return null;
                const items = [];
                if (refs.variable) items.push({label: 'VS', value: refs.variable});
                if (refs.constant) items.push({label: 'KS', value: refs.constant});
                if (refs.specific) items.push({label: 'SS', value: refs.specific});
                if (refs.accountServicer) items.push({label: 'Account Servicer', value: refs.accountServicer});
                if (refs.endToEndIdentification) items.push({label: 'End-to-End ID', value: refs.endToEndIdentification});
                if (refs.receiver) items.push({label: 'Zpráva příjemci', value: refs.receiver});
                if (refs.myDescription) items.push({label: 'Moje poznámka', value: refs.myDescription});
                return items.length > 0 ? items : null;
            }
            
            function extractTransactionData(payload) {
                const transactions = [
                    ...(payload?.bookTransactions || []),
                    ...(payload?.transactionAdvices || []),
                    ...(payload?.cardAuthorizations || [])
                ];
                
                if (transactions.length === 0) return null;
                
                // Vezmeme první transakci pro zobrazení hlavních informací
                const tx = transactions[0];
                return {
                    amount: tx.amount,
                    counterparty: tx.counterParty,
                    references: tx.references,
                    transactionType: tx.transactionType || 'N/A',
                    bookingDate: tx.bookingDate || tx.holdExpirationDate,
                    creditDebitIndicator: tx.creditDebitIndicator,
                    totalTransactions: transactions.length
                };
            }
            
            function renderEvents(events) {
                const container = document.getElementById('events-container');
                
                if (events.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <h2>Žádné eventy</h2>
                            <p>Zatím nebyly přijaty žádné eventy.</p>
                        </div>
                    `;
                    return;
                }
                
                const stats = countEvents(events);
                document.getElementById('total-events').textContent = stats.total;
                document.getElementById('transaction-advices').textContent = stats.transactionAdvices;
                document.getElementById('book-transactions').textContent = stats.bookTransactions;
                document.getElementById('card-authorizations').textContent = stats.cardAuthorizations;
                
                container.innerHTML = events.reverse().map((event, index) => {
                    const txData = extractTransactionData(event.payload);
                    const refs = formatReferences(txData?.references);
                    const amount = txData?.amount;
                    const counterparty = txData?.counterparty;
                    
                    return `
                        <div class="event-card">
                            <div class="event-header">
                                <h3>Event #${events.length - index}</h3>
                                <div class="event-meta">
                                    <div><strong>Čas:</strong> ${formatDate(event.timestamp)}</div>
                                    <div><strong>Subscription ID:</strong> ${event.subscriptionId}</div>
                                    <div><strong>Correlation ID:</strong> ${event.correlationId}</div>
                                    <div><strong>Jazyk:</strong> ${event.acceptLanguage}</div>
                                </div>
                            </div>
                            ${txData ? `
                                <div class="event-highlights">
                                    ${amount ? `
                                        <div class="highlight-card amount">
                                            <h4>Částka</h4>
                                            <div class="value">${formatAmount(amount)}</div>
                                            <div style="font-size: 11px; color: #666; margin-top: 3px;">
                                                ${txData.creditDebitIndicator === 'CREDIT' ? '✓ Příjem' : '✗ Výdej'}
                                            </div>
                                        </div>
                                    ` : ''}
                                    ${counterparty?.name ? `
                                        <div class="highlight-card counterparty">
                                            <h4>Protistrana</h4>
                                            <div class="value">${counterparty.name}</div>
                                            ${counterparty.iban ? `<div style="font-size: 11px; color: #666; margin-top: 3px;">${counterparty.iban}</div>` : ''}
                                        </div>
                                    ` : ''}
                                    ${txData.transactionType ? `
                                        <div class="highlight-card">
                                            <h4>Typ transakce</h4>
                                            <div class="value">${txData.transactionType}</div>
                                            ${txData.totalTransactions > 1 ? `<div style="font-size: 11px; color: #666; margin-top: 3px;">${txData.totalTransactions} transakcí</div>` : ''}
                                        </div>
                                    ` : ''}
                                    ${txData.bookingDate ? `
                                        <div class="highlight-card">
                                            <h4>Datum</h4>
                                            <div class="value">${txData.bookingDate}</div>
                                        </div>
                                    ` : ''}
                                </div>
                                ${refs && refs.length > 0 ? `
                                    <div class="highlight-card" style="margin-bottom: 15px;">
                                        <h4>Reference</h4>
                                        <div class="references-list">
                                            ${refs.map(ref => `<div class="reference-item"><strong>${ref.label}:</strong> ${ref.value}</div>`).join('')}
                                        </div>
                                    </div>
                                ` : ''}
                            ` : ''}
                            <div class="event-payload">
                                <details>
                                    <summary style="cursor: pointer; padding: 10px; background: #f0f0f0; border-radius: 5px; margin-bottom: 10px;">
                                        <strong>Kompletní JSON data</strong>
                                    </summary>
                                    <pre>${JSON.stringify(event.payload, null, 2)}</pre>
                                </details>
                            </div>
                        </div>
                    `;
                }).join('');
            }
            
            function showSnackbar(event) {
                const container = document.getElementById('snackbar-container');
                const txData = extractTransactionData(event.payload);
                const refs = formatReferences(txData?.references);
                const amount = txData?.amount;
                const counterparty = txData?.counterparty;
                
                const snackbarId = 'snackbar-' + Date.now();
                const snackbar = document.createElement('div');
                snackbar.id = snackbarId;
                snackbar.className = 'snackbar new-event';
                
                let refsHtml = '';
                if (refs && refs.length > 0) {
                    refsHtml = refs.slice(0, 2).map(ref => 
                        `<div class="snackbar-row"><span class="snackbar-label">${ref.label}:</span><span class="snackbar-value">${ref.value}</span></div>`
                    ).join('');
                }
                
                snackbar.innerHTML = `
                    <div class="snackbar-header">
                        <div class="snackbar-title">💰 Nový event přijat</div>
                        <button class="snackbar-close" onclick="closeSnackbar('${snackbarId}')">×</button>
                    </div>
                    <div class="snackbar-content">
                        ${amount ? `<div class="snackbar-row"><span class="snackbar-label">Částka:</span><span class="snackbar-value snackbar-amount">${formatAmount(amount)}</span></div>` : ''}
                        ${counterparty?.name ? `<div class="snackbar-row"><span class="snackbar-label">Protistrana:</span><span class="snackbar-value">${counterparty.name}</span></div>` : ''}
                        ${refsHtml}
                        <div class="snackbar-row" style="margin-top: 5px; font-size: 11px; color: #999;">
                            ${formatDate(event.timestamp)}
                        </div>
                    </div>
                `;
                
                snackbar.onclick = () => {
                    loadEvents();
                    closeSnackbar(snackbarId);
                };
                
                container.appendChild(snackbar);
                
                // Automatické zavření po 8 sekundách
                setTimeout(() => {
                    closeSnackbar(snackbarId);
                }, 8000);
            }
            
            function closeSnackbar(id) {
                const snackbar = document.getElementById(id);
                if (snackbar) {
                    snackbar.classList.add('hiding');
                    setTimeout(() => {
                        snackbar.remove();
                    }, 300);
                }
            }
            
            async function checkForNewEvents() {
                try {
                    const response = await fetch('/events');
                    const events = await response.json();
                    
                    if (events.length > lastEventCount) {
                        // Nové eventy - zobrazit snackbar pro každý nový
                        const newEvents = events.slice(lastEventCount);
                        newEvents.reverse().forEach(event => {
                            showSnackbar(event);
                        });
                        lastEventCount = events.length;
                        renderEvents(events);
                    }
                } catch (error) {
                    console.error('Chyba při kontrole nových eventů:', error);
                }
            }
            
            async function loadEvents() {
                try {
                    const response = await fetch('/events');
                    const events = await response.json();
                    lastEventCount = events.length;
                    renderEvents(events);
                } catch (error) {
                    console.error('Chyba při načítání eventů:', error);
                    document.getElementById('events-container').innerHTML = 
                        '<div class="empty-state"><h2>Chyba při načítání</h2><p>Zkuste to prosím znovu.</p></div>';
                }
            }
            
            async function clearEvents() {
                if (!confirm('Opravdu chcete vymazat všechny eventy?')) {
                    return;
                }
                
                try {
                    await fetch('/events', { method: 'DELETE' });
                    loadEvents();
                } catch (error) {
                    console.error('Chyba při mazání eventů:', error);
                }
            }
            
            function toggleAutoRefresh() {
                const checkbox = document.getElementById('auto-refresh');
                if (checkbox.checked) {
                    autoRefreshInterval = setInterval(loadEvents, 5000); // Obnovování každých 5 sekund
                    snackbarCheckInterval = setInterval(checkForNewEvents, 2000); // Kontrola nových eventů každé 2 sekundy
                } else {
                    if (autoRefreshInterval) {
                        clearInterval(autoRefreshInterval);
                        autoRefreshInterval = null;
                    }
                    if (snackbarCheckInterval) {
                        clearInterval(snackbarCheckInterval);
                        snackbarCheckInterval = null;
                    }
                }
            }
            
            // Načtení eventů při načtení stránky
            loadEvents();
            
            // Automatická kontrola nových eventů každé 2 sekundy
            snackbarCheckInterval = setInterval(checkForNewEvents, 2000);
            
            // Funkce pro vytvoření QR platby
            async function createQRPayment() {
                const amount = prompt('Zadejte částku (nechte prázdné pro libovolnou částku):');
                const message = prompt('Zadejte zprávu pro příjemce:', 'Platba');
                
                if (message === null) {
                    return; // Uživatel zrušil
                }
                
                try {
                    const params = new URLSearchParams();
                    if (amount && amount.trim()) {
                        params.append('amount', amount.trim());
                    }
                    if (message && message.trim()) {
                        params.append('message', message.trim());
                    }
                    
                    console.log('Vytvářím QR platbu s parametry:', params.toString());
                    
                    const response = await fetch(`/qr-payment?${params.toString()}`);
                    console.log('Response status:', response.status);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error('Chyba odpovědi:', errorText);
                        alert(`Chyba při vytváření QR kódu: ${response.status} ${response.statusText}`);
                        return;
                    }
                    
                    const blob = await response.blob();
                    console.log('Blob vytvořen, velikost:', blob.size, 'typ:', blob.type);
                    
                    if (blob.size === 0) {
                        alert('QR kód je prázdný');
                        return;
                    }
                    
                    const qrImage = document.getElementById('qr-image');
                    const qrSection = document.getElementById('qr-payment-section');
                    
                    if (!qrImage || !qrSection) {
                        console.error('Elementy pro QR kód nebyly nalezeny');
                        alert('Chyba: Elementy pro zobrazení QR kódu nebyly nalezeny');
                        return;
                    }
                    
                    // Použít FileReader pro převod blobu na data URL (spolehlivější)
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        qrImage.src = e.target.result;
                        qrSection.style.display = 'block';
                        console.log('QR kód úspěšně načten jako data URL');
                    };
                    reader.onerror = function() {
                        console.error('Chyba při čtení blobu');
                        // Fallback na ObjectURL
                        const imageUrl = URL.createObjectURL(blob);
                        qrImage.src = imageUrl;
                        qrSection.style.display = 'block';
                    };
                    reader.readAsDataURL(blob);
                    
                    qrImage.onerror = function() {
                        console.error('Chyba při načítání obrázku QR kódu');
                        alert('Chyba při načítání QR kódu. Zkuste obnovit stránku.');
                    };
                    
                    qrImage.onload = function() {
                        console.log('QR kód úspěšně zobrazen');
                    };
                    
                    // Scroll na QR sekci
                    qrSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    
                    // Načíst informace o platbě
                    setTimeout(() => {
                        loadPaymentInfo();
                        loadTrackedPayments();
                    }, 500);
                    
                } catch (error) {
                    console.error('Chyba při vytváření QR platby:', error);
                    alert(`Chyba při vytváření QR kódu: ${error.message}`);
                }
            }
            
            async function loadPaymentInfo() {
                try {
                    const response = await fetch('/qr-payment-info');
                    const data = await response.json();
                    
                    if (data.payments && data.payments.length > 0) {
                        const payment = data.payments[data.payments.length - 1]; // Poslední platba
                        document.getElementById('qr-payment-info').innerHTML = `
                            <div><strong>Variabilní symbol:</strong> ${payment.vs}</div>
                            <div><strong>Částka:</strong> ${payment.amount ? payment.amount + ' CZK' : 'Libovolná'}</div>
                            <div><strong>Status:</strong> <span style="color: ${payment.status === 'paid' ? '#27ae60' : '#e74c3c'}; font-weight: bold;">${payment.status === 'paid' ? '✓ ZAPLACENO' : '⏳ ČEKÁNÍ'}</span></div>
                            ${payment.paid_at ? `<div><strong>Zaplaceno:</strong> ${formatDate(payment.paid_at)}</div>` : ''}
                        `;
                        document.getElementById('qr-spayd').textContent = payment.spayd;
                    }
                } catch (error) {
                    console.error('Chyba při načítání informací o platbě:', error);
                }
            }
            
            async function loadTrackedPayments() {
                try {
                    const response = await fetch('/qr-payment-info');
                    const data = await response.json();
                    const container = document.getElementById('tracked-payments');
                    
                    if (data.payments && data.payments.length > 0) {
                        container.innerHTML = `
                            <h2 style="margin-bottom: 15px; color: #2c3e50;">Sledované platby</h2>
                            <div style="display: grid; gap: 10px;">
                                ${data.payments.reverse().map(payment => `
                                    <div style="padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid ${payment.status === 'paid' ? '#27ae60' : '#e74c3c'};">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div>
                                                <div><strong>VS:</strong> ${payment.vs}</div>
                                                <div><strong>Částka:</strong> ${payment.amount ? payment.amount + ' CZK' : 'Libovolná'}</div>
                                                <div><strong>Vytvořeno:</strong> ${formatDate(payment.created)}</div>
                                                ${payment.paid_at ? `<div><strong>Zaplaceno:</strong> ${formatDate(payment.paid_at)}</div>` : ''}
                                            </div>
                                            <div style="font-size: 24px; font-weight: bold; color: ${payment.status === 'paid' ? '#27ae60' : '#e74c3c'};">
                                                ${payment.status === 'paid' ? '✓' : '⏳'}
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                    } else {
                        container.innerHTML = '';
                    }
                } catch (error) {
                    console.error('Chyba při načítání sledovaných plateb:', error);
                }
            }
            
            // Kontrola plateb při kontrole nových eventů
            const originalCheckForNewEvents = checkForNewEvents;
            checkForNewEvents = async function() {
                await originalCheckForNewEvents();
                loadTrackedPayments();
            };
            
            // Načíst sledované platby při načtení stránky
            loadTrackedPayments();
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/events")
async def get_events():
    """API endpoint pro získání všech uložených eventů."""
    return list(events_storage)


@app.delete("/events")
async def delete_events():
    """API endpoint pro smazání všech eventů."""
    events_storage.clear()
    return {"message": "Všechny eventy byly smazány"}


@app.get("/requests")
async def get_request_history():
    """API endpoint pro získání historie všech příchozích požadavků."""
    return {
        "total": len(request_history),
        "requests": list(request_history)
    }


@app.delete("/requests")
async def clear_request_history():
    """API endpoint pro smazání historie požadavků."""
    request_history.clear()
    return {"message": "Historie požadavků byla smazána"}


def url_encode_spayd(value: str) -> str:
    """
    Zakóduje hodnotu podle SPAYD standardu (URL encoding pro speciální znaky).
    Podle standardu: povolené znaky jsou 0-9, A-Z (velká), mezera, $, %, *, +, -, ., /, :
    Ostatní znaky se kódují pomocí URL encoding.
    """
    import urllib.parse
    # Podle standardu: povolené znaky jsou alfanumerické + některé speciální
    # Pro efektivní uložení do QR kódu použít pouze povolené znaky
    # Ostatní znaky zakódovat pomocí URL encoding
    # Safe znaky: povolené znaky kromě těch, které mají speciální význam v SPAYD (*, :)
    encoded = urllib.parse.quote(value, safe='')
    return encoded


def generate_spayd_string(iban: str, amount: Optional[float] = None, vs: Optional[str] = None, message: Optional[str] = None) -> str:
    """
    Vygeneruje SPAYD řetězec podle standardu QR platby verze 1.2.
    Standard: https://qr-platba.cz/wp-content/uploads/1645-standard-qr-v1-2-cerven-2021.pdf
    
    Pro tuzemský platební styk v CZK:
    - Účet musí být český IBAN (začíná CZ)
    - Měna musí být CZK
    """
    # Verze standardu 1.2 (účinná od 1. ledna 2022)
    # Formát hlavičky: SPD*1.2* (s hvězdičkou na konci verze)
    parts = ["SPD*1.2*"]
    
    # ACC - povinný (IBAN)
    # Formát: ACC:IBAN* nebo ACC:IBAN+BIC*
    # Pro české účty: IBAN začíná CZ
    # Český IBAN: CZ + 2 kontrolní číslice + 10-24 číslic (celkem 14-28 znaků)
    iban_clean = iban.strip().upper().replace(' ', '')
    if not iban_clean.startswith('CZ'):
        raise ValueError(f"Pro tuzemský platební styk v CZK musí být IBAN český (začíná CZ), zadaný: {iban_clean}")
    
    # Validace délky českého IBAN (minimálně 14 znaků, maximálně 28 znaků)
    if len(iban_clean) < 14 or len(iban_clean) > 28:
        raise ValueError(f"Český IBAN musí mít délku 14-28 znaků, zadaný má {len(iban_clean)}: {iban_clean}")
    
    parts.append(f"ACC:{iban_clean}*")
    
    # AM - částka (volitelná)
    # Formát: desetinné číslo, max. 2 desetinné cifry, tečka jako oddělovač
    if amount is not None:
        parts.append(f"AM:{amount:.2f}*")
    
    # CC - měna (volitelná, ale pro CZK doporučeno)
    # Formát: ISO 4217, 3 znaky, velká písmena
    # Pro tuzemský platební styk musí být CZK
    parts.append("CC:CZK*")
    
    # MSG - zpráva pro příjemce (volitelná, max 60 znaků)
    # Speciální znaky se kódují pomocí URL encoding
    if message:
        msg_clean = message[:60]
        # Zakódovat speciální znaky (hvězdička, dvojtečka atd.)
        # Podle standardu: pouze znaky z povolené množiny, ostatní URL encoding
        msg_encoded = url_encode_spayd(msg_clean)
        parts.append(f"MSG:{msg_encoded}*")
    
    # X-VS - variabilní symbol (volitelný, max 10 znaků, celé číslo)
    # Podle standardu verze 1.2 - rozšířené atributy pro ČR
    if vs:
        vs_clean = str(vs)[:10]
        # Ověřit, že je to číslo
        if vs_clean.isdigit():
            parts.append(f"X-VS:{vs_clean}*")
    
    return "".join(parts)


def generate_qr_code_image(spayd_string: str) -> bytes:
    """Vygeneruje QR kód jako PNG obrázek."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(spayd_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Uložit do bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


@app.get("/qr-payment")
async def create_qr_payment(
    amount: Optional[float] = None,
    message: Optional[str] = "Platba",
    iban: str = "CZ5401000001154933990227"
):
    """Vytvoří QR kód pro platbu s náhodným variabilním symbolem."""
    # Generovat náhodný VS (10 číslic)
    vs = str(random.randint(1000000000, 9999999999))
    
    # Vytvořit SPAYD řetězec
    spayd_string = generate_spayd_string(
        iban=iban,
        amount=amount,
        vs=vs,
        message=message
    )
    
    # Uložit do sledovaných plateb
    tracked_payments[vs] = {
        "iban": iban,
        "amount": amount,
        "vs": vs,
        "message": message,
        "spayd": spayd_string,
        "created": datetime.now().isoformat(),
        "status": "pending"
    }
    
    # Vygenerovat QR kód
    qr_image = generate_qr_code_image(spayd_string)
    
    return Response(content=qr_image, media_type="image/png")


@app.get("/qr-payment-info")
async def get_qr_payment_info():
    """Vrátí informace o všech sledovaných platbách."""
    return {
        "total": len(tracked_payments),
        "payments": [
            {
                **info,
                "spayd": info.get("spayd", "")
            }
            for vs, info in tracked_payments.items()
        ]
    }


@app.get("/qr-payment/{vs}")
async def get_payment_status(vs: str):
    """Vrátí status konkrétní platby podle VS."""
    if vs not in tracked_payments:
        raise HTTPException(status_code=404, detail=f"Platba s VS {vs} nebyla nalezena")
    
    return tracked_payments[vs]


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handler pro 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={
            "timestamp": datetime.now().isoformat(),
            "status": 404,
            "error": "Not Found",
            "message": f"Endpoint {request.url.path} nebyl nalezen.",
            "path": request.url.path,
            "available_endpoints": [
                "GET /version",
                "POST /subscriptions/{subscriptionId}/events",
                "GET /",
                "GET /events",
                "DELETE /events"
            ]
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handler pro 500 Internal Server Error."""
    error_detail = str(exc) if exc else "Internal Server Error"
    return JSONResponse(
        status_code=500,
        content={
            "timestamp": datetime.now().isoformat(),
            "status": 500,
            "error": "Internal Server Error",
            "message": error_detail,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler pro validační chyby."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error.get("loc", [])),
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "validation_error")
        })
    
    return JSONResponse(
        status_code=400,
        content={
            "timestamp": datetime.now().isoformat(),
            "status": 400,
            "error": "Bad Request",
            "message": "Validation error - missing required headers",
            "path": request.url.path,
            "errors": errors,
            "required_headers": {
                "x-correlation-id": "GUID correlation ID (format: 8-4-4-4-12)"
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


# Catch-all handler pro všechny ostatní cesty (musí být na konci, aby neinterferoval s ostatními routami)
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def catch_all_handler(request: Request, full_path: str):
    """Handler pro všechny neexistující endpointy."""
    # Speciální případ pro health check endpointy
    if full_path == "health" or full_path.startswith("health/"):
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "Event API v2.0"
        }
    
    # Vrátit 404 s informací o dostupných endpointech
    return JSONResponse(
        status_code=404,
        content={
            "timestamp": datetime.now().isoformat(),
            "status": 404,
            "error": "Not Found",
            "message": f"Endpoint /{full_path} nebyl nalezen. Tento endpoint není součástí Event API specifikace v2.0.",
            "path": f"/{full_path}",
            "available_endpoints": [
                "GET /version",
                "HEAD /version",
                "POST /subscriptions/{subscriptionId}/events",
                "GET /",
                "GET /events",
                "DELETE /events",
                "GET /health"
            ],
            "note": "Tato API implementuje pouze Event API v2.0 specifikaci pro přijímání eventů."
        }
    )


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Port lze změnit přes environment variable PORT
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Spouštím server na {host}:{port}")
    print(f"Webové rozhraní: http://localhost:{port}")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\n❌ Chyba: Port {port} je již obsazený!")
            print(f"Zkuste:")
            print(f"  1. Ukončit proces na portu {port}: lsof -ti :{port} | xargs kill")
            print(f"  2. Nebo použít jiný port: PORT=8001 python3 app.py")
        else:
            print(f"\n❌ Chyba při spuštění serveru: {e}")
        raise

