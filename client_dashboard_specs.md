# Client Dashboard v2.0 - Implementation Plan

## Executive Summary

This plan outlines the implementation of Client Confirmation Manager v2.0 based on the functional requirements from v1.0, leveraging our existing GCP infrastructure and current frontend foundation. The approach preserves all proven business logic while integrating with our modern Firebase/Firestore architecture and React TypeScript codebase.

## Current State Analysis

### Existing Frontend Foundation
- **Three-Grid Layout**: ClientDashboard.tsx with collapsible bottom panel ✅
- **AG-Grid Integration**: Professional data grids with full feature set ✅
- **TypeScript Architecture**: Type-safe interfaces and components ✅
- **Internationalization**: react-i18next with comprehensive translation support ✅
- **Firebase Auth**: Role-based authentication system ✅
- **Dark Theme**: Professional UI optimized for financial workflows ✅

### Missing v1.0 Functionality (To Implement)
1. **File Upload System**: Drag-and-drop for Excel/CSV trades and .msg/.pdf emails
2. **LLM Integration**: Email processing with Anthropic Claude
3. **Trade Matching Algorithm**: 90-point scoring system with confidence thresholds
4. **Status Management Workflow**: Context menus, mail back, verify functions
5. **Data Persistence**: Firestore integration replacing JSON file storage
6. **Discrepancy Detection**: Visual highlighting of field mismatches

### GCP Architecture Alignment
- **Service Projects**: Deploy to development projects within Development folder
- **Shared VPC**: Leverage existing VPC network architecture  
- **Firestore**: Multi-tenant data storage with organization-based isolation (using emulator for development)
- **Cloud Run**: Serverless backend deployment with auto-scaling (development environment)
- **Security**: CMEK encryption, centralized logging, IAM integration

### Questions & Clarifications

**1. Organization Multi-tenancy**
- Should each client organization have completely isolated data in Firestore?
- Or use shared collections with organization ID filtering?
- **Recommendation**: Organization-isolated collections for security

**2. File Processing Location** 
- Process .msg/.pdf files in Cloud Run backend vs Cloud Functions?
- **Recommendation**: Cloud Run for consistency with existing architecture

**3. Real-time Synchronization**
- Should multiple users see live updates when matches are processed?
- **Recommendation**: Firestore real-time listeners for immediate UI updates

**4. LLM Integration Security**
- How to handle sensitive financial data in LLM requests?
- **Recommendation**: Data anonymization before LLM processing

## Implementation Strategy

### Phase 1: Firestore Data Layer Integration

**Leverage Existing Firebase Setup**
Extend our current Firebase Auth implementation to include organization-based data isolation in Firestore.

```typescript
// Enhanced organization context (extends existing AuthContext)
interface OrganizationContext {
  organizationId: string;
  organizationName: string;
  type: 'client' | 'bank';
}

// Firestore collections structure for multi-tenancy
const COLLECTIONS = {
  trades: (orgId: string) => `organizations/${orgId}/trades`,
  emails: (orgId: string) => `organizations/${orgId}/emails`, 
  matches: (orgId: string) => `organizations/${orgId}/matches`
} as const;
```

**Firestore Data Service Implementation**
```typescript
class FirestoreDataService {
  private db = getFirestore();
  
  constructor(private organizationId: string) {}
  
  async getUnmatchedTrades(): Promise<UnmatchedTrade[]> {
    const tradesRef = collection(this.db, COLLECTIONS.trades(this.organizationId));
    const q = query(tradesRef, where('status', '==', 'unmatched'));
    const snapshot = await getDocs(q);
    return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() } as UnmatchedTrade));
  }
  
  async saveMatch(match: TradeMatch): Promise<void> {
    const matchesRef = collection(this.db, COLLECTIONS.matches(this.organizationId));
    await addDoc(matchesRef, {
      ...match,
      createdAt: serverTimestamp(),
      organizationId: this.organizationId
    });
  }
}
```

**Integration with Current Grid System**
Modify existing ClientTradesGrid to use real data instead of mock data:

```typescript
// Update ClientTradesGrid.tsx to use Firestore
const ClientTradesGrid: React.FC = () => {
  const { organizationId } = useOrganization();
  const [trades, setTrades] = useState<ClientTrade[]>([]);
  const dataService = new FirestoreDataService(organizationId);
  
  useEffect(() => {
    // Real-time Firestore listener
    const tradesRef = collection(db, COLLECTIONS.trades(organizationId));
    const unsubscribe = onSnapshot(tradesRef, (snapshot) => {
      const updatedTrades = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      } as ClientTrade));
      setTrades(updatedTrades);
    });
    
    return () => unsubscribe();
  }, [organizationId]);
}
```

### Phase 2: File Upload & Processing System

**Build on Existing Upload Infrastructure**
Add drag-and-drop capability to the current ClientDashboard layout. Create upload zones for both trade files (Excel/CSV) and email confirmations (.msg/.pdf).

```typescript
// New component: FileUploadZone.tsx
interface FileUploadZoneProps {
  acceptedFileTypes: string[];
  onFileDrop: (files: File[]) => Promise<void>;
  uploadType: 'trades' | 'emails';
  className?: string;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({ 
  acceptedFileTypes, 
  onFileDrop, 
  uploadType,
  className 
}) => {
  const { t } = useTranslation();
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState<Map<string, number>>(new Map());

  const handleDrop = async (e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer?.files || []);
    const validFiles = files.filter(file => 
      acceptedFileTypes.some(type => file.name.toLowerCase().endsWith(type))
    );
    
    if (validFiles.length > 0) {
      await onFileDrop(validFiles);
    }
  };

  return (
    <div 
      className={`file-upload-zone ${isDragOver ? 'drag-over' : ''} ${className}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
    >
      <div className="upload-content">
        <div className="upload-icon">📁</div>
        <p className="upload-text">
          {t(`upload.${uploadType}.dragPrompt`)}
        </p>
        <p className="upload-types">
          {acceptedFileTypes.join(', ')}
        </p>
      </div>
    </div>
  );
};
```

**Integration with Current Dashboard Layout**
```typescript
// Enhanced ClientDashboard.tsx with upload zones
const ClientDashboard: React.FC = () => {
  const { t } = useTranslation();
  const [isBottomPanelExpanded, setIsBottomPanelExpanded] = useState(true);
  
  const handleTradeFileDrop = async (files: File[]) => {
    // Process Excel/CSV trade files
    for (const file of files) {
      await tradeUploadService.processTradeFile(file);
    }
  };
  
  const handleEmailFileDrop = async (files: File[]) => {
    // Process .msg/.pdf email files
    for (const file of files) {
      await emailProcessingService.processEmailFile(file);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Upload zones at top */}
      <div className="upload-zones">
        <FileUploadZone
          acceptedFileTypes={['.xlsx', '.csv']}
          onFileDrop={handleTradeFileDrop}
          uploadType="trades"
          className="trades-upload"
        />
        <FileUploadZone
          acceptedFileTypes={['.msg', '.pdf']}
          onFileDrop={handleEmailFileDrop}
          uploadType="emails"  
          className="emails-upload"
        />
      </div>
      
      {/* Existing three-panel layout */}
      <div className={`top-panels ${isBottomPanelExpanded ? '' : 'expanded'}`}>
        {/* ... existing panel code ... */}
      </div>
    </div>
  );
};
```

**Backend Processing Service**
Align with existing FastAPI backend structure and deploy to Cloud Run:

```python
# backend/services/file_processor.py (enhance existing)
from typing import List, Union
import pandas as pd
from fastapi import UploadFile

class FileProcessorService:
    def __init__(self, organization_id: str):
        self.organization_id = organization_id
        self.firestore_service = FirestoreService(organization_id)
    
    async def process_trade_file(self, file: UploadFile) -> ProcessingResult:
        """Process Excel/CSV trade files"""
        try:
            # Validate file
            await self._validate_file(file, allowed_types=['.xlsx', '.csv'])
            
            # Parse data
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file.file)
            else:
                df = pd.read_csv(file.file)
            
            # Transform to standard format
            trades = self._standardize_trade_data(df)
            
            # Save to Firestore
            await self.firestore_service.save_unmatched_trades(trades)
            
            return ProcessingResult(
                success=True,
                message=f"Processed {len(trades)} trades",
                data=trades
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False, 
                message=f"Error processing file: {str(e)}"
            )
```

### Phase 3: LLM Integration & Matching Algorithm

**Anthropic Claude Integration**
Build email processing service using the proven v1.0 LLM prompts with enhanced security:

```python
# backend/services/llm_service.py  
import anthropic
from typing import Dict, Optional

class LLMService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-3-5-sonnet-20241022"
    
    async def extract_trade_data(self, email_content: Dict, formatted_data: str) -> Dict:
        """Extract structured trade data from email using v1.0 proven prompt"""
        
        prompt = f"""You are receiving an email from a bank. This email is likely to be about a trade confirmation.
        
                Tell me if this email is requesting the confirmation of a trade(s) or not. It could feasibly be about something else.

                {formatted_data}

                If there is a reference to a trade confirmation, set the Confirmation field to Yes.
                If there is no reference to a trade confirmation, set the Confirmation field to No.

                The most likely type of emails that we will process are those that request the confirmation of a trade, and they come from banks.
                
                Typically (but not always), the subject line of an email about a trade confirmation will include the words "Confirmación" or "Confirmation" and the body will also probably refer to a confirmation.

                If this email is indeed about a trade confirmation, you need to extract the data as per the following instructions:
                
                Look for the trade number in the subject of the email and in the body. This is usually a number, e.g. "1234567890"). Can also be named as a reference and is one of the most important fields. It will always be present on a confirmation email.

                I also need you to extract some data from the email body. Data in the email body should also override data in the email subject, as it is possible that the conversation
                has moved on from the initial subject line.

                Remember that this email is written from the Bank's perspective, not you, the Client's. Therefore, the details of the trade are reversed. Specific consequences of this can include the following:
                - Counterparty: the bank could refer to you as the counterparty. However, from your perspective, the bank is the counterparty.
                - Currency 1: the bank could refer to the currency you pay as Currency 1. However, from your perspective, the currency you pay is Currency 2.
                - Currency 2: the bank could refer to the currency you receive as Currency 2. However, from your perspective, the currency you receive is Currency 1.
                - Direction: the bank could refer to the direction of the trade as "Buy" or "Sell". However, from your perspective, the direction of the trade is the opposite.
                - Counterparty Payment Method: the bank will refer to the payment method they use as "Forma de Pago Nuestra" or something similar. This should be saved in the field "Counterparty Payment Method".
                - Our Payment Method: the bank will refer to the payment method you use as "Forma de Pago Contraparte" or something similar. This should be saved in the field "Our Payment Method".
                
                The specific data you need to find is as follows:
                 
                - Trade Number, a number indicating the ID of the trade, can also be named as a reference. This is usually a number, e.g. "1234567890").
                - Counterparty ID, typically the bank's ID. It may not be present in the email, in which case you should leave it blank.
                - Counterparty Name, the bank's name
                - Product Type, if this says "Spot", save as "Spot". If it says "Seguro de Cambio", "Seguro de Inflación", "Arbitraje", "Forward", "NDF", save as "Forward".
                - Direction, from your perspective as the client, are you buying from the bank or selling to the bank? Save as "Buy" or "Sell".
                - Currency 1, an ISO 4217 currency code, the currency you are buying or selling according to the Direction field. Remember if the bank says "Buy", you are selling to the bank (and you should store it as "Sell"), and if the bank says "Sell", you are buying from the bank (and you should store it as "Buy").
                - Amount of Currency 1, a number, the amount of currency 1 you are buying or selling according to the Direction field.
                - Currency 2, an ISO 4217 currency code, the other currency of the trade.
                - Settlement Type, if it says "Compensación" or "Non-Deliverable", save as "Compensación". If it says "Entrega Física" or "Deliverable", save as "Entrega Física".
                - Settlement Currency, an ISO 4217 currency code. If the Settlement Type is "Entrega Física", this field is unlikely to exist or have a value, in which case set as "N/A".
                - Trade Date, a date, which can be in different formats
                - Value Date, a date, which can be in different formats
                - Maturity Date, a date, which can be in different formats
                - Payment Date, a date, which can be in different formats
                - Duration, an integer number, indicating the number of days between the value date and the maturity date
                - Forward Price, a number usually with decimal places
                - Fixing Reference, If you see anything such as "USD Obs", "Dolar Observado", "CLP10", "Dólar Observado", "CLP Obs", save as "USD Obs".
                - Counterparty Payment Method, look in fields labelled "Forma de Pago". Usually one of the following values: "Trans Alto Valor", "ComBanc", "SWIFT", "Cuenta Corriente".
                - Our Payment Method, look in fields labelled "Forma de Pago". Usually one of the following values: "Trans Alto Valor", "ComBanc", "SWIFT", "Cuenta Corriente"

                Return this in a JSON format, but do not include any markdown formatting such as ```json or ```. This causes errors so I really need you to return it without any markdown formatting.
                DO NOT return any other text than the JSON, as this causes errors.

                The required structured of the JSON file is as follows:

                {{
                    "Email": {{
                        "Email_subject": string,
                        "Email_sender": string,
                        "Email_date": date (dd-mm-yyyy),
                        "Email_time": time (hh:mm:ss),
                        "Confirmation": string (Yes or No)
                        "Num_trades": integer (the number of trades referred to in the email),
                    }},
                    "Trades": [
                        {{
                            "TradeNumber": string,
                            "CounterpartyName": string,
                            "ProductType": string,
                            "Direction": string ("Buy" or "Sell"),
                            "Currency1": string (ISO 4217 currency code),
                            "QuantityCurrency1": number to a minimum of two decimal places,
                            "Currency2": string (ISO 4217 currency code),
                            "SettlementType": string, ("Compensación" or "Entrega Física"),
                            "SettlementCurrency": string (ISO 4217 currency code),
                            "TradeDate": date in format dd-mm-yyyy,
                            "ValueDate": date in format dd-mm-yyyy,
                            "MaturityDate": date in format dd-mm-yyyy,
                            "PaymentDate": date in format dd-mm-yyyy,
                            "ForwardPrice": number to a minimum of two decimal places,
                            "FixingReference": string,
                            "CounterpartyPaymentMethod": string,
                            "OurPaymentMethod": string
                        }}
                        // Repeat as many times as there are trades in the email
                    ]
                }}

                Now STOP for a minute, before you return the JSON. I need you to compare the data you have extracted into the Trades array in the JSON with the data in the email. If there is any difference on a specific field, overwrite the data in the JSON with the data you think is correct in the email.
                
                I repeat, the email body is the best source of truth.

                If the Direction field is "Buy", then QuantityCurrency1 is the amount of currency 1 you are buying from the bank. If the Direction field is "Sell", then QuantityCurrency1 is the amount of currency 1 you are selling to the bank.

                DO NOT return any other text than the JSON, as this causes errors. NO MARKDOWN.
            """
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        try:
            return json.loads(message.content[0].text)
        except json.JSONDecodeError:
            return {"Confirmation": "No", "error": "Invalid response format"}
```

**90-Point Matching Algorithm Implementation**
Use the exact v1.0 scoring system with Firestore integration:

```typescript
// frontend/src/services/MatchingService.ts
class MatchingService {
  private readonly SCORING_WEIGHTS = {
    tradeNumber: 50,    // v1.0 proven weights
    amount: 20,
    currency: 10,
    date: 10
  };
  
  private readonly MIN_CONFIDENCE = 60; // v1.0 threshold
  
  constructor(private firestoreService: FirestoreService) {}

  async findMatches(extractedData: ExtractedTrade): Promise<MatchResult[]> {
    const unmatchedTrades = await this.firestoreService.getUnmatchedTrades();
    
    const matches = unmatchedTrades.map(trade => {
      const score = this.calculateScore(extractedData, trade);
      const confidence = Math.round((score / 90) * 100); // v1.0 calculation
      
      return {
        trade,
        score,
        confidence,
        reasons: this.getMatchReasons(extractedData, trade),
        discrepancies: this.identifyDiscrepancies(extractedData, trade)
      };
    });

    return matches
      .filter(match => match.confidence >= this.MIN_CONFIDENCE)
      .sort((a, b) => b.score - a.score);
  }
  
  private calculateScore(email: ExtractedTrade, trade: UnmatchedTrade): number {
    let totalScore = 0;
    
    // Trade number (50 points - most important)
    if (this.compareValues(email.TradeNumber, trade.TradeNumber)) {
      totalScore += 50;
    }
    
    // Amount (20 points with tolerance)
    if (this.compareAmounts(email.Amount, trade.QuantityCurrency1)) {
      totalScore += 20;
    }
    
    // Currency (10 points)
    if (email.Currency === trade.Currency1) {
      totalScore += 10;
    }
    
    // Date (10 points with business day tolerance)
    if (this.compareDates(email.TradeDate, trade.TradeDate)) {
      totalScore += 10;
    }
    
    return totalScore;
  }
}
```

### Phase 4: Enhanced Grid Functionality

**Add v1.0 Context Menu & Status Management**
Enhance existing grids with v1.0 proven workflow features:

```typescript
// Enhanced ConfirmationsGrid with v1.0 context menu
const ConfirmationsGrid: React.FC = () => {
  const { t } = useTranslation();
  const [selectedEmailRow, setSelectedEmailRow] = useState<any>(null);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const [showContextMenu, setShowContextMenu] = useState(false);

  const handleCellRightClick = (params: any) => {
    if (params.column.getColId() === 'status') {
      setSelectedEmailRow(params.node);
      setContextMenuPosition({
        x: params.event.clientX,
        y: params.event.clientY
      });
      setShowContextMenu(true);
    }
  };

  const contextMenuItems = [
    {
      name: t('contextMenu.resolved'),
      action: () => handleStatusChange('resolved')
    },
    {
      name: t('contextMenu.tagged'), 
      action: () => handleStatusChange('tagged')
    },
    {
      name: t('contextMenu.mailBack'),
      action: () => generateMailBack()
    },
    {
      name: t('contextMenu.verify'),
      action: () => openVerifyModal()
    }
  ];

  // Column definitions with discrepancy highlighting
  const columnDefs = [
    {
      field: 'status',
      headerName: t('grid.status'),
      cellRenderer: 'statusCellRenderer',
      cellClassRules: {
        'status-confirmed': params => params.value === 'confirmed',
        'status-difference': params => params.value === 'difference',
        'status-resolved': params => params.value === 'resolved'
      }
    },
    {
      field: 'bankTradeNumber',
      headerName: t('grid.bankTradeNumber'),
      cellClassRules: {
        'mismatch-cell': params => hasMismatch(params, 'tradeNumber')
      }
    },
    // ... other columns with mismatch detection
  ];

  return (
    <>
      <AgGridReact
        rowData={emailConfirmations}
        columnDefs={columnDefs}
        onCellContextMenu={handleCellRightClick}
        components={{
          statusCellRenderer: StatusCellRenderer
        }}
      />
      
      {showContextMenu && (
        <ContextMenu
          position={contextMenuPosition}
          items={contextMenuItems}
          onClose={() => setShowContextMenu(false)}
        />
      )}
    </>
  );
};
```

**Discrepancy Visual Highlighting**
Implement v1.0 red highlighting for mismatched fields:

```typescript
// Mismatch detection service
class MismatchDetectionService {
  detectDiscrepancies(bankData: EmailMatch, clientData: MatchedTrade): Discrepancy[] {
    const discrepancies: Discrepancy[] = [];
    const fieldsToCompare = ['amount', 'currency', 'tradeDate', 'counterparty', 'forwardPrice'];
    
    fieldsToCompare.forEach(field => {
      const bankValue = this.normalizeValue(bankData[field]);
      const clientValue = this.normalizeValue(clientData[field]);
      
      if (bankValue !== clientValue) {
        discrepancies.push({
          field,
          bankValue: bankData[field],
          clientValue: clientData[field],
          status: 'mismatch'
        });
      }
    });
    
    return discrepancies;
  }
  
  private normalizeValue(value: any): string {
    if (typeof value === 'number') return value.toFixed(2);
    if (typeof value === 'string') return value.trim().toLowerCase();
    return String(value || '').trim().toLowerCase();
  }
}

// CSS for discrepancy highlighting
.mismatch-cell {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-weight: bold;
  border-left: 3px solid #ef4444;
}
```

### Phase 5: Communication & Verification Tools

**Mail Back Generation (v1.0 Proven Templates)**
Use exact v1.0 email templates that clients already know:

```typescript
// services/MailGenerationService.ts
class MailGenerationService {
  generateMailBack(emailData: EmailMatch, tradeData: MatchedTrade, discrepancies: Discrepancy[]): string {
    const { counterpartyName, bankTradeNumber } = emailData;
    
    if (emailData.status === 'confirmed') {
      return `mailto:${emailData.emailSender}?subject=Confirmación operación ${bankTradeNumber}&body=Hola ${counterpartyName},%0D%0A%0D%0AConfirmamos los datos de la operación ${bankTradeNumber}.%0D%0A%0D%0ASaludos,%0D%0APalace`;
    }
    
    if (emailData.status === 'difference') {
      let discrepancyList = '';
      discrepancies.forEach(disc => {
        discrepancyList += `- ${disc.field}: Ustedes ${disc.bankValue} vs Nosotros ${disc.clientValue}%0D%0A`;
      });
      
      return `mailto:${emailData.emailSender}?subject=Discrepancias en operación ${bankTradeNumber}&body=Hola ${counterpartyName},%0D%0A%0D%0AIdentificamos las siguientes discrepancias en la confirmación de la operación ${bankTradeNumber}:%0D%0A%0D%0A${discrepancyList}%0D%0APor favor revisar y confirmar los datos correctos.%0D%0A%0D%0ASaludos,%0D%0APalace`;
    }
    
    // Default template
    return `mailto:${emailData.emailSender}?subject=Referente operación ${bankTradeNumber}&body=Hola ${counterpartyName},%0D%0A%0D%0AReferente a la operación ${bankTradeNumber}.%0D%0A%0D%0ASaludos,%0D%0APalace`;
  }
}
```

**Verification Modal (v1.0 Three-Way Comparison)**
Implement the exact v1.0 verify functionality for cross-referencing chat conversations:

```typescript
// components/VerifyModal.tsx
const VerifyModal: React.FC<VerifyModalProps> = ({ 
  selectedTrade, 
  selectedEmail,
  isOpen, 
  onClose 
}) => {
  const [verifyText, setVerifyText] = useState('');
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    if (!verifyText.trim()) return;
    
    setLoading(true);
    try {
      const result = await verificationService.verifyTrade({
        tradeId: selectedTrade.id,
        emailId: selectedEmail.id,
        verifyText: verifyText
      });
      
      if (result.extractedData.IsTradeText === 'No') {
        alert('El texto ingresado no parece contener información de una operación.');
        return;
      }
      
      setVerificationResult(result);
    } catch (error) {
      console.error('Verification error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Verificar Operación">
      <div className="verify-modal-content">
        <div className="input-section">
          <label htmlFor="verify-text">
            Pegar texto de chat o conversación de negociación:
          </label>
          <textarea
            id="verify-text"
            value={verifyText}
            onChange={(e) => setVerifyText(e.target.value)}
            placeholder="Pegar aquí el texto del chat, email o conversación donde se negoció esta operación..."
            rows={8}
            className="verify-textarea"
          />
          <button 
            onClick={handleVerify} 
            disabled={!verifyText.trim() || loading}
            className="verify-button"
          >
            {loading ? 'Verificando...' : 'Verificar'}
          </button>
        </div>
        
        {verificationResult && (
          <div className="verification-results">
            <h3>Resultados de Verificación</h3>
            <div className="three-way-comparison">
              <div className="source-column">
                <h4>Nuestro Registro</h4>
                <TradeDataDisplay data={verificationResult.sources.client} />
              </div>
              <div className="source-column">
                <h4>Confirmación del Banco</h4>
                <TradeDataDisplay data={verificationResult.sources.bank} />
              </div>
              <div className="source-column">
                <h4>Texto de Verificación</h4>
                <TradeDataDisplay data={verificationResult.sources.verification} />
              </div>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
```

**Leverage Existing Palace.cl GCP Organization**

Deploy to established `palace.cl` organization infrastructure, utilizing the Development folder and projects for initial deployment.

### Development Deployment
```yaml
# Cloud Run service deployment to development project
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ccm-backend-dev
  namespace: development
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/vpc-access-connector: projects/vpc-host-nonprod/locations/southamerica-west1/connectors/vpc-connector
        run.googleapis.com/vpc-access-egress: private-ranges-only
    spec:
      containers:
      - image: gcr.io/development/ccm-backend
        ports:
        - containerPort: 8080
        env:
        - name: FIRESTORE_PROJECT_ID
          value: development
        - name: USE_FIREBASE_EMULATOR
          value: "true"
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: anthropic-secrets
              key: api-key
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

**Firestore Security Rules (Multi-tenant)**
```javascript
// Firestore rules for organization-based isolation
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Organization-isolated collections
    match /organizations/{orgId}/{collection}/{docId} {
      allow read, write: if request.auth != null 
        && request.auth.token.organization_id == orgId;
    }
    
    // User access to their organization's data only
    match /organizations/{orgId}/trades/{tradeId} {
      allow read, write: if request.auth != null 
        && request.auth.token.organization_id == orgId
        && request.auth.token.role in ['client_admin', 'client_user'];
    }
  }
}
```

**Frontend Development (Firebase Hosting & Emulator)**
```json
{
  "hosting": {
    "public": "build",
    "site": "ccm-frontend-dev",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [{
      "source": "**",
      "destination": "/index.html"
    }]
  },
  "emulators": {
    "auth": {
      "port": 9099
    },
    "firestore": {
      "port": 8080
    },
    "hosting": {
      "port": 5000
    },
    "ui": {
      "enabled": true,
      "port": 4000
    }
  }
```

## Security Implementation

**Customer-Managed Encryption Keys (CMEK)**
Leverage existing KMS Autokey setup for all data at rest (when moving to production):

```python
# backend/config/firestore.py
from google.cloud import firestore
import os

def get_firestore_client():
    # For development, use emulator or development project
    if os.getenv('USE_FIREBASE_EMULATOR', 'false').lower() == 'true':
        # Connect to Firestore emulator
        os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8080'
    
    project_id = os.getenv('PROJECT_ID', 'development')
    
    # CMEK will be automatically used when deployed to production projects
    return firestore.Client(project=project_id)
```

**Data Anonymization for LLM Processing (Future Enhancement)**
```python
# PLACEHOLDER: To be implemented in future phase for enhanced security
# This service will anonymize sensitive data before sending to LLM providers
# Currently, we process data as-is in development environment
# 
# Future implementation will include:
# - Client name anonymization
# - Amount obfuscation  
# - Account number masking
# - Personal information removal
```

## Performance & Monitoring

**Cloud Monitoring Integration**
Utilize existing central-logging-monitoring project:

```python
# backend/middleware/monitoring.py
from google.cloud import monitoring_v3
import time

class PerformanceMonitor:
    def __init__(self):
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/central-logging-monitoring"
    
    def record_matching_time(self, duration_ms: float):
        """Track matching algorithm performance"""
        series = monitoring_v3.TimeSeries()
        series.metric.type = 'custom.googleapis.com/ccm/matching_duration'
        series.resource.type = 'cloud_run_revision'
        
        point = monitoring_v3.Point()
        point.value.double_value = duration_ms
        point.interval.end_time.seconds = int(time.time())
        
        series.points = [point]
        self.client.create_time_series(name=self.project_name, time_series=[series])
```

## Migration & Rollout Strategy

**Progressive Feature Rollout**
Build incrementally on the existing dashboard foundation:

1. **Phase 1**: Replace mock data with Firestore (no UI changes)
2. **Phase 2**: Add file upload zones to existing layout
3. **Phase 3**: Implement LLM processing and matching
4. **Phase 4**: Add context menus and status management
5. **Phase 5**: Enable mail back and verification features

## Data Structures and Storage

### Unmatched Trades (Client Trade Records)
```json
{
  "TradeNumber": "32010",
  "CounterpartyName": "Bci",
  "ProductType": "Forward",
  "TradeDate": "01-10-2025",
  "ValueDate": "01-10-2025",
  "Direction": "Buy",
  "Currency1": "USD",
  "QuantityCurrency1": 330000.0,
  "ForwardPrice": 932.33,
  "Currency2": "CLP",
  "MaturityDate": "01-10-2026",
  "FixingReference": "USD Obs",
  "SettlementType": "Compensación",
  "SettlementCurrency": "CLP",
  "PaymentDate": "03-10-2026",
  "CounterpartyPaymentMethod": "SWIFT",
  "OurPaymentMethod": "SWIFT"
}
```

### Matched Trades (Successfully Matched Records)
```json
{
  "TradeNumber": "32013",
  "CounterpartyName": "Banco ABC",
  "ProductType": "Forward",
  "TradeDate": "29-09-2025",
  "ValueDate": "01-10-2025",
  "Direction": "Buy",
  "Currency1": "USD",
  "QuantityCurrency1": 1000000.0,
  "ForwardPrice": 932.88,
  "Currency2": "CLP",
  "MaturityDate": "30-10-2025",
  "FixingReference": "USD Obs",
  "SettlementType": "Compensación",
  "SettlementCurrency": "CLP",
  "PaymentDate": "01-11-2025",
  "CounterpartyPaymentMethod": "LBTR",
  "OurPaymentMethod": "LBTR",
  "identified_at": "2025-08-08T16:14:37.216324+00:00",
  "match_id": "608d18e1-98cf-4230-b8a0-e20a5c1f153e",
  "match_confidence": "89%",
  "match_reasons": ["Trade number match", "Amount match", "Currency match"],
  "status": "confirmed"
}
```

### Email Matches (Bank Confirmation Emails)
```json
{
  "EmailSender": "confirmacionesderivados@bancoabc.cl",
  "EmailDate": "2025-04-04",
  "EmailTime": "11:39:04",
  "EmailSubject": "Confirmación operación 9239834",
  "BankTradeNumber": "9239834",
  "match_id": "608d18e1-98cf-4230-b8a0-e20a5c1f153e",
  "CounterpartyID": "",
  "CounterpartyName": "Banco ABC",
  "ProductType": "Forward",
  "Direction": "Buy",
  "Trader": null,
  "Currency1": "USD",
  "QuantityCurrency1": 1000000.0,
  "Currency2": "CLP",
  "SettlementType": "Compensación",
  "SettlementCurrency": "CLP",
  "TradeDate": "29-09-2025",
  "ValueDate": "01-10-2025",
  "MaturityDate": "30-10-2025",
  "PaymentDate": "01-11-2025",
  "Duration": 0,
  "ForwardPrice": 932.98,
  "FixingReference": "USD Obs",
  "CounterpartyPaymentMethod": "SWIFT",
  "OurPaymentMethod": "SWIFT",
  "EmailBody": "Estimados señores,\nSe ha negociado entre Banco ABC y Empresas ABC Limitada la siguiente operación...",
  "previous_status": "",
  "status": ""
}
```

This implementation plan provides a clear roadmap for building Client Dashboard v2.0 by leveraging your existing GCP infrastructure and frontend foundation while preserving all the proven business logic from v1.0. The approach eliminates technical debt while maintaining feature parity and user familiarity.

## Summary

### Implementation Approach
- **Build on Existing Foundation**: Extend current three-grid React/TypeScript dashboard
- **Preserve v1.0 Business Logic**: 90-point matching algorithm, context menus, verification workflow
- **Leverage GCP Infrastructure**: Deploy to existing `palace.cl` organization with Shared VPC
- **Maintain Security**: CMEK encryption, organization-based data isolation, LLM data anonymization
- **Enable Progressive Rollout**: Incremental feature delivery without breaking existing functionality

### Key Benefits
1. **Immediate Value**: Transform current mock dashboard into fully functional v1.0 equivalent
2. **Modern Architecture**: TypeScript, Firestore, Cloud Run deployment with Firebase Auth
3. **Enhanced Security**: Multi-tenant isolation, data encryption, secure LLM processing
4. **Performance Optimization**: Real-time updates, efficient data handling, monitoring integration
5. **Future-Ready**: Scalable architecture supporting both Pool and Silo tenancy models

### Next Steps
1. **Review and Iterate**: Validate approach and clarify any outstanding questions
2. **Phase 1 Kickoff**: Begin Firestore integration with existing grid components
3. **Progressive Implementation**: Build features incrementally while maintaining working dashboard
4. **Testing Integration**: Validate v1.0 business logic preservation throughout development
5. **Deployment Preparation**: Configure GCP services and security policies for production readiness