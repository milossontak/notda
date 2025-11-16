from fastapi import FastAPI, Header, HTTPException, Path, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
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
        <title>Event API - Přijaté eventy</title>
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
            <h1>Event API - Přijaté eventy</h1>
            
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
                <label>
                    <input type="checkbox" id="auto-refresh" onchange="toggleAutoRefresh()"> Automatické obnovování
                </label>
            </div>
            
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

