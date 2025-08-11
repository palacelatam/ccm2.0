# Client Dashboard v2.0 - Revised Implementation Plan

## Executive Summary

This revised implementation plan builds directly on your existing Firebase/Firestore architecture, extending current services and database structures rather than creating parallel systems. The approach preserves your established patterns while implementing v1.0 functionality.

## Current Database Structure Alignment

### Existing Collections (Keep As-Is)
```typescript
// Your current structure - no changes needed
clients/{clientId}/
├── settings/configuration        // ClientSettings
├── bankAccounts/{accountId}     // BankAccount records  
├── settlementRules/{ruleId}     // SettlementRule records
├── dataMappings/{mappingId}     // DataMapping records
└── trades/{tradeId}             // NEW: Add trade collections

banks/{bankId}/
├── clientSegments/{segmentId}
├── settlementInstructionLetters/{letterId}
├── systemSettings/configuration
└── clientSegmentAssignments/assignments

users/{userId}                   // User profiles with organization refs
```

### New Collections to Add
```typescript
// Extend existing client collections
clients/{clientId}/trades/{tradeId}           // Unmatched trades from Excel/CSV
clients/{clientId}/emails/{emailId}           // Email confirmations 
clients/{clientId}/matches/{matchId}          // Matched trade pairs
clients/{clientId}/uploadSessions/{sessionId} // File upload tracking
```

## Phase 1: Extend Existing Services

### Enhance ClientService with Trade Management
```typescript
// Add to existing backend/src/services/client_service.py
class ClientService:
    # ... existing methods ...
    
    # NEW METHODS FOR TRADES
    async def get_unmatched_trades(self, client_id: str) -> List[UnmatchedTrade]:
        """Get all unmatched trades for a client"""
        try:
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            query = trades_ref.where('status', '==', 'unmatched').order_by('trade_date', direction='desc')
            docs = query.stream()
            
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(UnmatchedTrade(**trade_data))
            
            return trades
        except Exception as e:
            logger.error(f"Error getting unmatched trades for client {client_id}: {e}")
            return []
    
    async def save_trade_from_upload(self, client_id: str, trade_data: dict, upload_session_id: str) -> bool:
        """Save trade from Excel/CSV upload"""
        try:
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            
            trade_doc = {
                **trade_data,
                'status': 'unmatched',
                'upload_session_id': upload_session_id,
                'created_at': datetime.now(),
                'organization_id': client_id  # For security rules
            }
            
            trades_ref.add(trade_doc)
            return True
        except Exception as e:
            logger.error(f"Error saving trade for client {client_id}: {e}")
            return False
    
    async def get_email_confirmations(self, client_id: str) -> List[EmailConfirmation]:
        """Get all email confirmations for a client"""
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            docs = emails_ref.order_by('email_date', direction='desc').stream()
            
            emails = []
            for doc in docs:
                email_data = doc.to_dict()
                email_data['id'] = doc.id
                emails.append(EmailConfirmation(**email_data))
            
            return emails
        except Exception as e:
            logger.error(f"Error getting email confirmations for client {client_id}: {e}")
            return []
    
    async def save_email_confirmation(self, client_id: str, email_data: dict, llm_extracted_data: dict) -> str:
        """Save email confirmation with LLM extracted data"""
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            
            email_doc = {
                **email_data,
                'llm_extracted_data': llm_extracted_data,
                'status': 'unmatched',  # Start as unmatched
                'created_at': datetime.now(),
                'organization_id': client_id
            }
            
            doc_ref = emails_ref.add(email_doc)[1]
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error saving email confirmation for client {client_id}: {e}")
            return None
    
    async def get_matches(self, client_id: str) -> List[TradeMatch]:
        """Get all trade matches for a client"""
        try:
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            docs = matches_ref.order_by('created_at', direction='desc').stream()
            
            matches = []
            for doc in docs:
                match_data = doc.to_dict()
                match_data['id'] = doc.id
                matches.append(TradeMatch(**match_data))
            
            return matches
        except Exception as e:
            logger.error(f"Error getting matches for client {client_id}: {e}")
            return []
    
    async def create_match(self, client_id: str, trade_id: str, email_id: str, 
                          confidence_score: int, match_reasons: List[str]) -> bool:
        """Create a trade-email match"""
        try:
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            
            match_doc = {
                'trade_id': trade_id,
                'email_id': email_id,
                'confidence_score': confidence_score,
                'match_reasons': match_reasons,
                'status': 'confirmed' if confidence_score >= 90 else 'review_needed',
                'created_at': datetime.now(),
                'organization_id': client_id
            }
            
            # Create match record
            matches_ref.add(match_doc)
            
            # Update trade and email status
            await self._update_trade_status(client_id, trade_id, 'matched')
            await self._update_email_status(client_id, email_id, 'matched')
            
            return True
        except Exception as e:
            logger.error(f"Error creating match for client {client_id}: {e}")
            return False
    
    async def _update_trade_status(self, client_id: str, trade_id: str, status: str):
        """Update trade status"""
        trade_ref = self.db.collection('clients').document(client_id).collection('trades').document(trade_id)
        trade_ref.update({'status': status, 'updated_at': datetime.now()})
    
    async def _update_email_status(self, client_id: str, email_id: str, status: str):
        """Update email status"""
        email_ref = self.db.collection('clients').document(client_id).collection('emails').document(email_id)
        email_ref.update({'status': status, 'updated_at': datetime.now()})
```

### Add Trade-Related Data Models
```python
# Add to backend/src/models/client.py (extend existing)

@dataclass
class UnmatchedTrade:
    """Unmatched trade from Excel/CSV upload"""
    id: Optional[str] = None
    trade_number: str = ""
    counterparty_name: str = ""
    product_type: str = ""
    trade_date: str = ""
    value_date: str = ""
    direction: str = ""  # Buy/Sell
    currency1: str = ""
    quantity_currency1: float = 0.0
    currency2: str = ""
    forward_price: float = 0.0
    maturity_date: str = ""
    fixing_reference: str = ""
    settlement_type: str = ""
    settlement_currency: str = ""
    payment_date: str = ""
    counterparty_payment_method: str = ""
    our_payment_method: str = ""
    status: str = "unmatched"
    upload_session_id: Optional[str] = None
    created_at: Optional[datetime] = None
    organization_id: Optional[str] = None

@dataclass 
class EmailConfirmation:
    """Email confirmation from bank"""
    id: Optional[str] = None
    email_sender: str = ""
    email_date: str = ""
    email_time: str = ""
    email_subject: str = ""
    email_body: str = ""
    bank_trade_number: str = ""
    llm_extracted_data: Optional[Dict] = None
    status: str = "unmatched"
    created_at: Optional[datetime] = None
    organization_id: Optional[str] = None

@dataclass
class TradeMatch:
    """Matched trade-email pair"""
    id: Optional[str] = None
    trade_id: str = ""
    email_id: str = ""
    confidence_score: int = 0
    match_reasons: List[str] = field(default_factory=list)
    discrepancies: List[Dict] = field(default_factory=list)
    status: str = "review_needed"  # confirmed, review_needed, rejected
    created_at: Optional[datetime] = None
    organization_id: Optional[str] = None
```

### Add New API Endpoints
```python
# Add to backend/src/api/routes/clients.py (extend existing router)

@router.post("/{client_id}/upload-trades")
async def upload_trades(
    client_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload Excel/CSV file with trade data"""
    client_service = ClientService()
    
    # Check client access
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Process file
    file_processor = FileProcessorService(client_id)
    result = await file_processor.process_trade_file(file)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    
    return {
        "message": result.message,
        "trades_processed": len(result.data),
        "upload_session_id": result.upload_session_id
    }

@router.post("/{client_id}/upload-emails") 
async def upload_emails(
    client_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload .msg/.pdf email files"""
    client_service = ClientService()
    
    # Check client access
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Process email file
    email_processor = EmailProcessorService(client_id)
    result = await email_processor.process_email_file(file)
    
    return {
        "message": "Email processed successfully",
        "email_id": result.email_id,
        "llm_extracted_trades": len(result.extracted_trades)
    }

@router.get("/{client_id}/unmatched-trades")
async def get_unmatched_trades(
    client_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all unmatched trades for client"""
    client_service = ClientService()
    trades = await client_service.get_unmatched_trades(client_id)
    return {"trades": trades}

@router.get("/{client_id}/email-confirmations")
async def get_email_confirmations(
    client_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all email confirmations for client"""
    client_service = ClientService()
    emails = await client_service.get_email_confirmations(client_id)
    return {"emails": emails}

@router.get("/{client_id}/matches")
async def get_matches(
    client_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all trade matches for client"""
    client_service = ClientService()
    matches = await client_service.get_matches(client_id)
    return {"matches": matches}

@router.post("/{client_id}/process-matches")
async def process_matches(
    client_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Run matching algorithm on unmatched trades and emails"""
    matching_service = MatchingService(client_id)
    results = await matching_service.find_all_matches()
    
    return {
        "matches_found": len(results.matches),
        "confidence_scores": [m.confidence_score for m in results.matches]
    }
```

## Phase 2: Enhance Frontend with Real Data

### Update Existing Grid Components
```typescript
// Modify frontend/src/components/grids/ClientTradesGrid.tsx
import { useAuth } from '../../contexts/AuthContext';
import { clientService } from '../../services/clientService';

const ClientTradesGrid: React.FC = () => {
  const { user } = useAuth();  // Get current user
  const [trades, setTrades] = useState<UnmatchedTrade[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Get client ID from user context (assuming user.organization.id exists)
  const clientId = user?.organization?.id;

  useEffect(() => {
    if (!clientId) return;
    
    const loadTrades = async () => {
      try {
        const response = await clientService.getUnmatchedTrades(clientId);
        setTrades(response.trades);
      } catch (error) {
        console.error('Error loading trades:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTrades();
  }, [clientId]);

  const columnDefs = [
    {
      field: 'trade_number',
      headerName: t('grid.tradeNumber'),
      filter: true,
      sortable: true
    },
    {
      field: 'counterparty_name', 
      headerName: t('grid.counterparty'),
      filter: true
    },
    {
      field: 'product_type',
      headerName: t('grid.productType'),
      filter: true
    },
    {
      field: 'direction',
      headerName: t('grid.direction'),
      cellRenderer: (params: any) => (
        <span className={`direction-${params.value.toLowerCase()}`}>
          {params.value}
        </span>
      )
    },
    {
      field: 'currency1',
      headerName: t('grid.currency'),
      width: 100
    },
    {
      field: 'quantity_currency1',
      headerName: t('grid.amount'),
      cellRenderer: (params: any) => 
        new Intl.NumberFormat('es-CL').format(params.value),
      cellClass: 'number-cell'
    },
    {
      field: 'trade_date',
      headerName: t('grid.tradeDate'),
      cellRenderer: (params: any) => 
        new Date(params.value).toLocaleDateString('es-CL')
    },
    {
      field: 'status',
      headerName: t('grid.status'),
      cellRenderer: 'statusCellRenderer',
      cellClassRules: {
        'status-unmatched': params => params.value === 'unmatched',
        'status-matched': params => params.value === 'matched'
      }
    }
  ];

  if (loading) {
    return <div className="grid-loading">Loading trades...</div>;
  }

  return (
    <div className="client-trades-grid">
      <AgGridReact
        rowData={trades}
        columnDefs={columnDefs}
        defaultColDef={{
          resizable: true,
          sortable: true,
          filter: true
        }}
        components={{
          statusCellRenderer: StatusCellRenderer
        }}
        onGridReady={() => console.log('Client trades grid ready')}
      />
    </div>
  );
};
```

### Add Client Service Frontend
```typescript
// Create frontend/src/services/clientService.ts
class ClientService {
  private baseURL = '/api/v1/clients';

  async getUnmatchedTrades(clientId: string) {
    const response = await fetch(`${this.baseURL}/${clientId}/unmatched-trades`, {
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch unmatched trades');
    }
    
    return await response.json();
  }

  async getEmailConfirmations(clientId: string) {
    const response = await fetch(`${this.baseURL}/${clientId}/email-confirmations`, {
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`
      }
    });
    
    return await response.json();
  }

  async uploadTradeFile(clientId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/${clientId}/upload-trades`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`
      },
      body: formData
    });
    
    return await response.json();
  }

  async uploadEmailFile(clientId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/${clientId}/upload-emails`, {
      method: 'POST', 
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`
      },
      body: formData
    });
    
    return await response.json();
  }

  async processMatches(clientId: string) {
    const response = await fetch(`${this.baseURL}/${clientId}/process-matches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await this.getAuthToken()}`
      }
    });
    
    return await response.json();
  }

  private async getAuthToken(): Promise<string> {
    // Get Firebase auth token
    const user = auth.currentUser;
    return user ? await user.getIdToken() : '';
  }
}

export const clientService = new ClientService();
```

## Phase 3: Add File Upload Functionality

### File Upload Component (Reusable)
```typescript
// Create frontend/src/components/FileUpload/FileUploadZone.tsx
interface FileUploadZoneProps {
  acceptedTypes: string[];
  onFileDrop: (files: File[]) => Promise<void>;
  title: string;
  description: string;
  className?: string;
}

const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  acceptedTypes,
  onFileDrop,
  title,
  description,
  className
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(file => 
      acceptedTypes.some(type => file.name.toLowerCase().endsWith(type.replace('*', '')))
    );
    
    if (validFiles.length > 0) {
      setUploading(true);
      try {
        await onFileDrop(validFiles);
      } finally {
        setUploading(false);
      }
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      setUploading(true);
      try {
        await onFileDrop(files);
      } finally {
        setUploading(false);
      }
    }
  };

  return (
    <div 
      className={`file-upload-zone ${isDragOver ? 'drag-over' : ''} ${className}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes.join(',')}
        onChange={handleFileSelect}
        style={{ display: 'none' }}
        multiple
      />
      
      <div className="upload-content">
        {uploading ? (
          <div className="upload-spinner">
            <span className="spinner"></span>
            <p>Uploading...</p>
          </div>
        ) : (
          <>
            <div className="upload-icon">📁</div>
            <h3>{title}</h3>
            <p>{description}</p>
            <p className="file-types">{acceptedTypes.join(', ')}</p>
          </>
        )}
      </div>
    </div>
  );
};
```

### Integrate with ClientDashboard
```typescript
// Modify frontend/src/pages/ClientDashboard.tsx
const ClientDashboard: React.FC = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [isBottomPanelExpanded, setIsBottomPanelExpanded] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const clientId = user?.organization?.id;

  const handleTradeFileUpload = async (files: File[]) => {
    if (!clientId) return;
    
    for (const file of files) {
      try {
        const result = await clientService.uploadTradeFile(clientId, file);
        console.log(`Uploaded ${file.name}:`, result);
        
        // Trigger grid refresh
        setRefreshTrigger(prev => prev + 1);
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
      }
    }
  };

  const handleEmailFileUpload = async (files: File[]) => {
    if (!clientId) return;
    
    for (const file of files) {
      try {
        const result = await clientService.uploadEmailFile(clientId, file);
        console.log(`Uploaded ${file.name}:`, result);
        
        // Trigger grid refresh
        setRefreshTrigger(prev => prev + 1);
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
      }
    }
  };

  const handleProcessMatches = async () => {
    if (!clientId) return;
    
    try {
      const result = await clientService.processMatches(clientId);
      console.log('Matching results:', result);
      
      // Trigger grid refresh
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
      console.error('Error processing matches:', error);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Add upload zones at top */}
      <div className="upload-section">
        <div className="upload-zones">
          <FileUploadZone
            acceptedTypes={['*.xlsx', '*.csv']}
            onFileDrop={handleTradeFileUpload}
            title={t('upload.trades.title')}
            description={t('upload.trades.description')}
            className="trades-upload"
          />
          <FileUploadZone
            acceptedTypes={['*.msg', '*.pdf']}
            onFileDrop={handleEmailFileUpload}
            title={t('upload.emails.title')} 
            description={t('upload.emails.description')}
            className="emails-upload"
          />
        </div>
        <div className="process-section">
          <button 
            onClick={handleProcessMatches}
            className="process-matches-btn"
          >
            {t('dashboard.processMatches')}
          </button>
        </div>
      </div>

      {/* Existing three-panel layout */}
      <div className={`dashboard-content ${isBottomPanelExpanded ? '' : 'expanded'}`}>
        <div className="top-panels">
          <div className="left-panel">
            <ClientTradesGrid key={`trades-${refreshTrigger}`} />
          </div>
          <div className="right-panel">
            <ConfirmationsGrid key={`emails-${refreshTrigger}`} />
          </div>
        </div>
        
        <div className="bottom-panel">
          <div className="panel-header">
            <h3>{t('dashboard.matchesPanel')}</h3>
            <button 
              onClick={() => setIsBottomPanelExpanded(!isBottomPanelExpanded)}
              className="panel-toggle"
            >
              {isBottomPanelExpanded ? '▼' : '▲'}
            </button>
          </div>
          {isBottomPanelExpanded && (
            <MatchesGrid key={`matches-${refreshTrigger}`} />
          )}
        </div>
      </div>
    </div>
  );
};
```

## Phase 4: Security & Access Control

### Update Firestore Security Rules
```javascript
// Firestore rules aligned with current structure
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can access their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Client data access - users can access their organization's data
    match /clients/{clientId}/{document=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.organization_id == clientId
        && request.auth.token.organization_type == 'client';
    }
    
    // Bank data access - bank users can access their bank's data  
    match /banks/{bankId}/{document=**} {
      allow read, write: if request.auth != null
        && request.auth.token.organization_id == bankId 
        && request.auth.token.organization_type == 'bank';
    }
    
    // Specific trade access with additional validation
    match /clients/{clientId}/trades/{tradeId} {
      allow read, write: if request.auth != null 
        && request.auth.token.organization_id == clientId
        && resource.data.organization_id == clientId;
    }
  }
}
```

### Enhance AuthContext with Organization Data
```typescript
// Modify frontend/src/contexts/AuthContext.tsx
interface AuthContextType {
  user: UserProfile | null;
  organization: OrganizationInfo | null;  // ADD THIS
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

interface OrganizationInfo {
  id: string;
  name: string;
  type: 'client' | 'bank';
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [organization, setOrganization] = useState<OrganizationInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          // Get user profile from backend
          const userProfile = await userService.getMyProfile();
          setUser(userProfile);
          
          // Extract organization info from user profile
          if (userProfile.organization) {
            setOrganization({
              id: userProfile.organization.id,
              name: userProfile.organization.name,
              type: userProfile.organization.type
            });
          }
          
        } catch (error) {
          console.error('Failed to load user profile:', error);
          setUser(null);
          setOrganization(null);
        }
      } else {
        setUser(null);
        setOrganization(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
      // User state will be set by the auth state listener
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      setUser(null);
      setOrganization(null);
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      organization,  // ADD THIS
      login, 
      logout, 
      loading 
    }}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Implementation Phases

### Phase 1: Database & Backend Extensions
- [ ] Add new collections to Firestore
- [ ] Extend ClientService with trade methods
- [ ] Add new API endpoints
- [ ] Create data models for trades/emails/matches

### Phase 2: Frontend Data Integration  
- [ ] Update grids to use real data instead of mocks
- [ ] Add ClientService frontend integration
- [ ] Enhance AuthContext with organization data
- [ ] Test data flow end-to-end

### Phase 3: File Upload System
- [ ] Create FileUploadZone component
- [ ] Add file processing services (Excel/CSV/MSG/PDF)
- [ ] Integrate upload zones with ClientDashboard
- [ ] Test file upload and processing

### Phase 4: Matching & LLM Integration
- [ ] Implement matching algorithm service
- [ ] Add LLM service for email processing  
- [ ] Create matching workflow
- [ ] Test complete upload-to-match cycle

## Key Advantages of This Approach

1. **Builds on Existing Architecture** - No database restructuring needed
2. **Incremental Implementation** - Can test each phase independently  
3. **Preserves Current Functionality** - Admin dashboard continues working
4. **Security Alignment** - Uses your existing auth patterns
5. **Performance Optimized** - Leverages existing CMEK client caching
6. **Rollback Friendly** - Each phase is additive, not destructive

This revised plan should integrate much more smoothly with your existing codebase while delivering the same v1.0 functionality described in the original specs.