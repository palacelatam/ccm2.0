# Implementation Guide for Client Confirmation Manager 2.0 - Frontend First Approach

## Project Overview
This document serves as the technical implementation guide for Claude Code to build the Client Confirmation Manager 2.0 application, starting with frontend screens and user interfaces.

## Updated Development Strategy

### Phase 1: Frontend Screens & Navigation
**Goal**: Build all main user interfaces with mock data to validate workflows and UX

1. **Authentication & Layout**
   - Login/logout screens with Firebase Auth setup
   - Top banner with Palace logo, language switcher, user menu
   - Dark theme implementation with Manrope font
   - Responsive navigation structure

2. **Client User Screens**
   - Main dashboard with three-panel layout
   - Trade data grids using AG Grid with mock data
   - Admin configuration pages with all toggles/settings
   - Trade verification modal for 3-way comparison
   - Settlement instructions management

3. **Bank User Screens**
   - Bank admin dashboard
   - Template management interface
   - Client segment management
   - Reports overview and trade grids

4. **Shared Components**
   - Reusable AG Grid components with context menus
   - Form components for configuration
   - Modal dialogs for actions
   - Status indicators and alerts

### Phase 2: Frontend State Management & API Integration
**Goal**: Connect frontend to mock/dummy backend services

1. **State Management Setup**
   - React Context for user authentication
   - State management for trade data and configurations
   - Loading states and error handling in UI

2. **Mock API Services**
   - Create service layer with mock responses
   - Implement all API calls with dummy data
   - Error simulation for testing error states

3. **Data Validation**
   - Form validation for user inputs
   - File upload validation (CSV/Excel)
   - Real-time validation feedback

### Phase 3: Backend Foundation
**Goal**: Build real backend services to replace mocks

1. **Core Infrastructure**
   - FastAPI setup with proper structure
   - Firebase Admin SDK integration
   - Firestore database setup
   - Authentication decorators

2. **Basic API Endpoints**
   - User management and authentication
   - Configuration CRUD operations
   - Trade data upload and storage
   - Basic reporting endpoints

### Phase 4: Advanced Backend Features
**Goal**: Implement email processing and trade comparison

1. **Email Processing Pipeline**
   - Gmail API integration
   - LLM parsing with Vertex AI
   - Trade comparison engine

2. **Auto-confirmation System**
   - Email generation and sending
   - Carta de Instrucción templates
   - Notification services

## Validated Project Structure

**Final Approved Directory Structure:**
```
client-confirmation-manager/
├── frontend/                     # React frontend (Firebase hosting)
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/          # Reusable UI components
│   │   │   ├── grids/           # AG Grid components
│   │   │   ├── admin/           # Admin-specific components
│   │   │   └── auth/            # Authentication components
│   │   ├── pages/
│   │   │   ├── client/          # Client user pages
│   │   │   ├── bank/            # Bank user pages
│   │   │   └── admin/           # Admin pages
│   │   ├── services/            # API service calls
│   │   ├── hooks/               # Custom React hooks
│   │   ├── utils/               # Helper functions
│   │   ├── styles/              # CSS/SCSS files (dark theme, Manrope font)
│   │   └── locales/             # i18n files (Spanish, English, Portuguese)
│   ├── public/
│   └── package.json
├── backend/                      # Python backend (Cloud Run)
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/          # API endpoints
│   │   │   ├── middleware/      # Request/response middleware
│   │   │   └── decorators/      # Auth and role decorators
│   │   ├── services/
│   │   │   ├── email/           # Email processing services
│   │   │   ├── parsing/         # LLM parsing services
│   │   │   ├── comparison/      # Trade comparison logic
│   │   │   ├── notification/    # Email/WhatsApp notifications
│   │   │   └── reporting/       # Report generation
│   │   ├── models/              # Data models and schemas
│   │   ├── agents/              # Autonomous agents for workflows
│   │   ├── utils/               # Helper functions
│   │   └── config/              # Configuration management
│   ├── tests/                   # Unit and integration tests
│   ├── Dockerfile               # Container configuration
│   └── requirements.txt         # Python dependencies
├── shared/                       # Shared types and schemas
│   ├── schemas/                 # JSON schemas for data validation
│   └── types/                   # TypeScript type definitions
└── infrastructure/               # Infrastructure as code
    ├── terraform/               # GCP resource definitions
    └── docker-compose.yml       # Local development setup
```

This structure provides:
- **Clear separation** between frontend React app and Python backend
- **User role organization** with dedicated pages for client/bank/admin users
- **Service architecture** that supports the agent-based email processing pipeline
- **Shared resources** for type definitions and validation schemas
- **Infrastructure support** for GCP deployment and local development

## Frontend Screen Specifications

### 1. Client Dashboard Layout
```typescript
// Main three-panel layout for trade management
interface DashboardLayout {
  topLeft: "MatchedTradesGrid";    // Trades identified from client data
  topRight: "ConfirmationsGrid";   // Bank confirmation emails processed
  bottom: "ClientTradesGrid";      // All client trade data uploaded
}

// Panel sizing and responsive behavior
const panelLayout = {
  desktop: {
    topPanels: "50% each horizontally",
    bottomPanel: "full width, 40% height"
  },
  tablet: {
    topPanels: "stacked vertically",
    bottomPanel: "full width below"
  },
  mobile: {
    layout: "tabbed interface switching between views"
  }
};
```

### 2. AG Grid Component Specifications
```typescript
// Standardized AG Grid setup for all trade displays
interface TradeGridProps {
  trades: TradeData[];
  columns: ColumnDef[];
  contextMenuItems: ContextMenuItem[];
  onRowAction: (action: string, rowData: any) => void;
}

// Standard column definitions for trade data
const standardTradeColumns = [
  { field: 'trade_date', headerName: 'Fecha', width: 120, sortable: true },
  { field: 'product', headerName: 'Producto', width: 100, filter: true },
  { field: 'currency_pair', headerName: 'Par', width: 80 },
  { field: 'amount', headerName: 'Monto', width: 120, type: 'numericColumn' },
  { field: 'rate', headerName: 'Tipo de Cambio', width: 120, type: 'numericColumn' },
  { field: 'counterparty', headerName: 'Contraparte', width: 150 },
  { field: 'status', headerName: 'Estado', width: 100, cellRenderer: 'StatusRenderer' }
];

// Context menu actions for each grid
const contextMenuActions = {
  clientTrades: ['Ver Detalles', 'Editar', 'Eliminar'],
  matchedTrades: ['Verificar Trade', 'Ver Confirmación', 'Disputar'],
  confirmations: ['Ver Email Original', 'Marcar como Procesado', 'Rechazar']
};
```

### 3. Client Admin Interface
```typescript
// Configuration toggles and settings
interface ClientAdminConfig {
  // Data sharing
  dataSharing: {
    enabled: boolean;
    description: "Compartir datos anonimizados con bancos";
  };
  
  // Auto-confirmation settings
  autoConfirmMatches: {
    enabled: boolean;
    delaySeconds: number;
    description: "Confirmar automáticamente trades coincidentes";
  };
  
  autoConfirmDisputes: {
    enabled: boolean;
    delaySeconds: number;
    description: "Disputar automáticamente trades con discrepancias";
  };
  
  // Carta de Instrucción
  autoCartaInstruccion: {
    enabled: boolean;
    description: "Generar carta de instrucción automáticamente";
  };
  
  // Alert settings
  alerts: {
    emailConfirmed: { enabled: boolean; addresses: string[] };
    emailDisputed: { enabled: boolean; addresses: string[] };
    whatsappConfirmed: { enabled: boolean; numbers: string[] };
    whatsappDisputed: { enabled: boolean; numbers: string[] };
  };
}
```

### 4. Trade Data Upload Interface
```typescript
// CSV/Excel upload with field mapping
interface TradeUploadInterface {
  // File upload area
  fileUpload: {
    acceptedFormats: ['.csv', '.xlsx', '.xls'];
    maxSize: '10MB';
    dragAndDrop: true;
  };
  
  // Field mapping section (appears after file upload)
  fieldMapping: {
    sourceFields: string[];        // Headers from uploaded file
    targetFields: TradeFieldMap;   // Required application fields
    preview: TradeData[];          // First 5 rows mapped
    validation: ValidationResult[]; // Any mapping issues
  };
  
  // Mapping rule management
  mappingRules: {
    savedMappings: FieldMapping[];
    actions: ['save', 'edit', 'delete', 'copy'];
  };
}
```

### 5. Trade Verification Modal
```typescript
// Three-way comparison interface
interface TradeVerificationModal {
  // Data sources display
  dataSources: {
    clientTrade: TradeData;        // From client system
    bankConfirmation: TradeData;   // From email parsing
    negotiationText: string;       // User-provided context
  };
  
  // Comparison results
  comparison: {
    conflicts: ConflictField[];    // Fields that don't match
    explanations: string[];        // Why each conflict occurred
    recommendations: string[];     // Suggested actions
  };
  
  // Actions
  actions: {
    acceptBank: () => void;        // Accept bank version
    acceptClient: () => void;      // Keep client version
    manualResolve: () => void;     // Custom resolution
    escalate: () => void;          // Flag for manual review
  };
}
```

## Mock Data Strategy

### Sample Trade Data
```typescript
// Mock data for development and testing
const mockClientTrades: ClientTrade[] = [
  {
    id: "trade_001",
    client_id: "client_123",
    trade_date: "2024-01-15T10:30:00Z",
    product: "FX_SPOT",
    currency_pair: "USD/CLP",
    amount: 1000000,
    rate: 890.50,
    settlement_date: "2024-01-17T00:00:00Z",
    counterparty: "Banco Santander",
    direction: "BUY",
    status: "MATCHED"
  },
  // ... more mock trades with various statuses
];

const mockBankConfirmations: BankConfirmation[] = [
  {
    id: "conf_001",
    client_id: "client_123",
    bank_id: "santander",
    email_subject: "Trade Confirmation - USD/CLP Spot",
    extracted_data: { /* parsed trade data */ },
    confidence_score: 0.95,
    status: "PROCESSED",
    matched_trade_id: "trade_001"
  },
  // ... more confirmations with different statuses
];
```

## UI/UX Requirements

### Dark Theme Specifications
```css
/* Color palette for dark theme */
:root {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #3a3a3a;
  --text-primary: #ffffff;
  --text-secondary: #b3b3b3;
  --accent-blue: #4a9eff;
  --accent-green: #00c851;
  --accent-red: #ff4444;
  --accent-yellow: #ffbb33;
  --border-color: #404040;
}

/* Manrope font implementation */
body {
  font-family: 'Manrope', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}
```

### Status Color Coding
```typescript
const statusColors = {
  MATCHED: "#00c851",      // Green
  DISPUTED: "#ff4444",     // Red
  UNRECOGNISED: "#ffbb33", // Yellow
  PENDING: "#4a9eff",      // Blue
  PROCESSED: "#6c757d"     // Gray
};
```

## Language Support Setup
```typescript
// i18n structure for Spanish (default), English, Portuguese
const translations = {
  es: {
    dashboard: {
      title: "Panel de Control",
      matchedTrades: "Trades Coincidentes",
      confirmations: "Confirmaciones",
      clientTrades: "Trades del Cliente"
    },
    // ... complete Spanish translations
  },
  en: {
    dashboard: {
      title: "Dashboard",
      matchedTrades: "Matched Trades",
      confirmations: "Confirmations",
      clientTrades: "Client Trades"
    },
    // ... complete English translations
  },
  pt: {
    // ... Portuguese translations
  }
};
```

## Development Setup Priority

1. **Start with**: Authentication screens and main layout structure
2. **Then build**: Client dashboard with three panels using mock data
3. **Add**: Admin configuration screens with all toggles
4. **Implement**: File upload interface with field mapping
5. **Create**: Bank admin screens and reporting views
6. **Finalize**: All interactive elements, modals, and error states

This frontend-first approach will let you iterate on the user experience quickly and establish the exact data contracts needed for the backend implementation.

---

This updated guide prioritizes frontend development and provides specific screen specifications that Claude Code can use to build a complete UI framework before moving to backend development.

## Implementation Progress Update

### Phase 1 Progress: Frontend Screens & Navigation ✅ **COMPLETED**

#### Authentication & Layout ✅
- **Login/logout screens**: Firebase Auth integration completed with form validation and loading states
- **Top banner navigation**: Implemented with Palace logo, language switcher (ES/EN/PT), and hamburger menu navigation
- **Dark theme**: Complete CSS custom properties implementation with Manrope font integration
- **Responsive navigation**: Mobile-friendly hamburger menu with active state indicators

#### Client User Screens ✅
- **Main dashboard**: Three-panel layout implemented with AG Grid integration
- **Trade data grids**: AG Grid Community with mock data, context menus, and professional status badges
- **Admin configuration**: Comprehensive admin dashboard with tabbed interface including:
  - **Automation Settings**: Data sharing, auto-confirmation toggles with delay settings
  - **Alert Configuration**: Email and WhatsApp alerts with distribution list management
  - **Settlement Rules**: Complete rule management system with add/edit/delete functionality
  - **Data Mapping**: Placeholder for CSV/Excel field mapping (Phase 2)

#### Status Badge System ✅
- **Professional styling**: Pill-shaped badges with gradients and appropriate sizing
- **Internationalization**: Status text properly localized across all three languages
- **Color coding**: Consistent status colors (Green: Matched, Red: Disputed, Yellow: Unrecognised, Blue: Pending, Gray: Processed)

#### Complete Internationalization ✅
- **Spanish (Primary)**: Complete translation coverage
- **English**: Full translation implementation
- **Portuguese**: Complete translation support
- **Dynamic switching**: Real-time language switching without page refresh
- **Comprehensive coverage**: All UI elements, form labels, status messages, and alerts translated

#### Advanced UI Components ✅
- **AlertModal**: Reusable modal system with four types (info, warning, error, success)
- **Form validation**: Elegant duplicate detection with modal alerts
- **Save notifications**: Success feedback with internationalized messages
- **Responsive design**: Mobile-optimized layouts with CSS Grid and Flexbox

### Settlement Rules Management System ✅

#### Rule Table Interface
- **Responsive table**: Professional grid layout with sortable columns
- **Status indicators**: Active/Inactive badges with appropriate styling
- **Action buttons**: Edit and delete functionality with hover effects
- **Empty state**: User-friendly message when no rules exist

#### Rule Form System
- **Three-section form**:
  1. **General Information**: Name, counterparty, product, currency, settlement type, payment method
  2. **Account Details**: Account numbers, bank codes, SWIFT codes, cutoff times
  3. **Additional Information**: Special instructions, active status, priority
- **Form validation**: Required field validation with internationalized error messages
- **Dropdown selections**: Pre-populated options for counterparties, products, currencies, settlement types
- **Professional styling**: Consistent with admin dashboard theme

#### Data Management
- **Sample data**: Pre-populated with realistic settlement rules for demonstration
- **CRUD operations**: Complete Create, Read, Update, Delete functionality
- **State management**: React hooks for form state and rule management
- **Form persistence**: Proper form data handling and validation

### Technical Improvements ✅

#### Code Quality
- **TypeScript interfaces**: Comprehensive type definitions for settlement rules
- **Component organization**: Clean separation of concerns with proper state management
- **CSS organization**: Modular styling with responsive design patterns
- **Error handling**: Graceful error states and user feedback

#### User Experience
- **Intuitive navigation**: Clear visual hierarchy and logical flow
- **Professional appearance**: Consistent styling and branding
- **Accessibility**: Proper form labels and keyboard navigation
- **Performance**: Optimized rendering and state updates

### Phase 2 Preparation: Frontend State Management & API Integration

#### Ready for Implementation
- **State management structure**: React Context patterns established
- **API service layer**: Service interfaces defined for backend integration
- **Mock data integration**: Sample data structure established for realistic testing
- **Error handling patterns**: Modal-based error communication system implemented

#### Next Steps for Phase 2
1. **API Service Layer**: Implement actual API calls to replace mock data
2. **State Management**: Implement React Context for global state management
3. **File Upload System**: Complete CSV/Excel upload with field mapping interface
4. **Real-time Updates**: WebSocket integration for live trade status updates
5. **Advanced Validation**: Server-side validation integration

### Updated Color Specifications
```css
/* Enhanced status badge colors with gradients */
.status-badge.matched {
  background: linear-gradient(135deg, #00c851 0%, #007e32 100%);
  color: white;
}

.status-badge.disputed {
  background: linear-gradient(135deg, #ff4444 0%, #cc1f1f 100%);
  color: white;
}

.status-badge.processed {
  background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
  color: white;
}
```

### File Structure Updates
```
frontend/src/
├── components/
│   ├── common/
│   │   ├── AlertModal.tsx ✅    # Reusable modal system
│   │   └── StatusCellRenderer.tsx ✅ # AG Grid status renderer
│   └── grids/ ✅                # AG Grid components
├── pages/
│   ├── admin/
│   │   ├── AdminDashboard.tsx ✅ # Complete admin interface
│   │   └── AdminDashboard.css ✅ # Professional styling
│   └── auth/ ✅                 # Authentication pages
├── locales/ ✅                  # Complete i18n support
│   ├── es.json ✅              # Spanish (primary)
│   ├── en.json ✅              # English
│   └── pt.json ✅              # Portuguese
└── styles/ ✅                   # Dark theme implementation
```

This comprehensive frontend implementation provides a solid foundation for Phase 2 backend integration and establishes all the UI patterns and data structures needed for the complete trade confirmation system.