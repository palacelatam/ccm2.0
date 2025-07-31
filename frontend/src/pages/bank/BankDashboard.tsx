import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './BankDashboard.css';

// Interface for Settlement Instruction Letter
interface SettlementInstructionLetter {
  id: string;
  active: boolean;
  priority: number;
  ruleName: string;
  clientSegment: string;
  product: string;
  documentUrl?: string;
  documentName?: string;
}

// Interface for Client
interface Client {
  id: string;
  name: string;
  rut: string;
  segment?: string;
}

// Interface for Client Segment
interface ClientSegment {
  id: string;
  name: string;
  description: string;  
  clientCount: number;
}

const BankDashboard: React.FC = () => {
  const { t } = useTranslation();
  
  const [activeTab, setActiveTab] = useState<'letters' | 'segmentation'>('letters');
  
  // Settlement Instructions Letters state
  const [settlementLetters, setSettlementLetters] = useState<SettlementInstructionLetter[]>([
    {
      id: '1',
      active: true,
      priority: 1,
      ruleName: 'USD FX Spot Standard Letter',
      clientSegment: 'Premium Clients',
      product: 'FX SPOT',
      documentUrl: 'sample-usd-fx-spot.docx',
      documentName: 'USD_FX_Spot_Template.docx'
    },
    {
      id: '2', 
      active: true,
      priority: 2,
      ruleName: 'EUR Forward Generic Letter',
      clientSegment: 'No Specific Segment',
      product: 'FX FORWARD',
      documentUrl: 'sample-eur-forward.docx',
      documentName: 'EUR_Forward_Template.docx'
    },
    {
      id: '3',
      active: false,
      priority: 3,
      ruleName: 'CLP Corporate Client Letter',
      clientSegment: 'Corporate Clients',
      product: 'FX SWAP',
      documentUrl: 'sample-clp-corporate.docx',
      documentName: 'CLP_Corporate_Template.docx'
    }
  ]);

  // Client Segmentation state
  const [clients, setClients] = useState<Client[]>([
    { id: '1', name: 'Empresa Minera Los Andes S.A.', rut: '76.123.456-7', segment: 'Corporate Clients' },
    { id: '2', name: 'Inversiones del Pacífico Ltda.', rut: '77.234.567-8', segment: 'Premium Clients' },
    { id: '3', name: 'Constructora Valle Verde S.A.', rut: '78.345.678-9', segment: 'Corporate Clients' },
    { id: '4', name: 'Comercial Santiago Norte Ltda.', rut: '79.456.789-0', segment: undefined },
    { id: '5', name: 'Exportadora Frutas del Sur S.A.', rut: '76.567.890-1', segment: 'Premium Clients' },
    { id: '6', name: 'Tecnología Innovadora Chile Ltda.', rut: '77.678.901-K', segment: undefined },
    { id: '7', name: 'Servicios Financieros Andinos S.A.', rut: '78.789.012-3', segment: 'Corporate Clients' },
    { id: '8', name: 'Importadora Textil Metropolitana Ltda.', rut: '79.890.123-4', segment: undefined },
    { id: '9', name: 'Compañía Naviera del Sur S.A.', rut: '80.123.456-7', segment: 'Premium Clients' },
    { id: '10', name: 'Industrias Químicas del Norte Ltda.', rut: '81.234.567-8', segment: 'Corporate Clients' },
    { id: '11', name: 'Servicios Logísticos Integrados S.A.', rut: '82.345.678-9', segment: undefined },
    { id: '12', name: 'Desarrollos Inmobiliarios Central Ltda.', rut: '83.456.789-0', segment: 'Premium Clients' },
    { id: '13', name: 'Consultora Estratégica Empresarial S.A.', rut: '84.567.890-1', segment: 'Corporate Clients' },
    { id: '14', name: 'Manufacturas Textiles Avanzadas Ltda.', rut: '85.678.901-K', segment: undefined },
    { id: '15', name: 'Grupo Financiero Metropolitano S.A.', rut: '86.789.012-3', segment: 'Premium Clients' },
    { id: '16', name: 'Transportes y Distribución Nacional Ltda.', rut: '87.890.123-4', segment: 'Corporate Clients' },
    { id: '17', name: 'Energías Renovables del Pacífico S.A.', rut: '88.123.456-7', segment: undefined },
    { id: '18', name: 'Comercializadora de Productos Agrícolas Ltda.', rut: '89.234.567-8', segment: 'Premium Clients' },
    { id: '19', name: 'Soluciones Tecnológicas Empresariales S.A.', rut: '90.345.678-9', segment: 'Corporate Clients' },
    { id: '20', name: 'Inversiones y Desarrollo Urbano Ltda.', rut: '91.456.789-0', segment: undefined }
  ]);

  const [clientSegments, setClientSegments] = useState<ClientSegment[]>([
    { id: '1', name: 'Premium Clients', description: 'High-value clients with preferential treatment', clientCount: 2 },
    { id: '2', name: 'Corporate Clients', description: 'Large corporate entities and institutions', clientCount: 3 },
    { id: '3', name: 'SME Clients', description: 'Small and medium enterprise clients', clientCount: 0 }
  ]);

  // Document preview state
  const [showDocumentPreview, setShowDocumentPreview] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<SettlementInstructionLetter | null>(null);

  // Form states
  const [showLetterForm, setShowLetterForm] = useState(false);
  const [editingLetter, setEditingLetter] = useState<SettlementInstructionLetter | null>(null);
  const [letterForm, setLetterForm] = useState<Partial<SettlementInstructionLetter>>({});

  // Drag and drop states
  const [draggedLetter, setDraggedLetter] = useState<string | null>(null);

  // Client segmentation states
  const [selectedClients, setSelectedClients] = useState<string[]>([]);
  const [bulkMode, setBulkMode] = useState(false);
  const [pendingChanges, setPendingChanges] = useState<{[clientId: string]: string | null | undefined}>({});
  const [showSegmentForm, setShowSegmentForm] = useState(false);
  const [editingSegment, setEditingSegment] = useState<ClientSegment | null>(null);
  const [segmentForm, setSegmentForm] = useState<{name: string, description: string}>({name: '', description: ''});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<ClientSegment | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [draggedClient, setDraggedClient] = useState<Client | null>(null);
  const [dragOverSegment, setDragOverSegment] = useState<string | null>(null);
  const [expandedSegments, setExpandedSegments] = useState<{[segmentName: string]: boolean}>({});
  const [dragOverLetter, setDragOverLetter] = useState<string | null>(null);
  const [contextMenu, setContextMenu] = useState<{client: Client, x: number, y: number} | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [filePreviewUrl, setFilePreviewUrl] = useState<string | null>(null);

  // Helper function to get sorted and grouped letters
  const getSortedAndGroupedLetters = () => {
    // Sort by active status first, then by priority
    const sorted = [...settlementLetters].sort((a, b) => {
      if (a.active !== b.active) return a.active ? -1 : 1;
      return a.priority - b.priority;
    });

    // Build ordered list with segment grouping
    const orderedLetters: Array<{ type: 'letter' | 'header'; data: SettlementInstructionLetter | string }> = [];
    let currentSegment: string | null = null;

    sorted.forEach(letter => {
      const letterSegment = letter.clientSegment || 'No Specific Segment';
      
      if (letterSegment !== currentSegment) {
        currentSegment = letterSegment;
        orderedLetters.push({ type: 'header', data: letterSegment });
      }
      
      orderedLetters.push({ type: 'letter', data: letter });
    });

    return orderedLetters;
  };

  // Document preview handlers
  const handleDocumentPreview = (letter: SettlementInstructionLetter) => {
    setPreviewDocument(letter);
    setShowDocumentPreview(true);
  };

  const closeDocumentPreview = () => {
    setShowDocumentPreview(false);
    setPreviewDocument(null);
  };

  // Form handlers
  const handleAddLetter = () => {
    setEditingLetter(null);
    setLetterForm({
      active: true,
      priority: Math.max(...settlementLetters.map(r => r.priority), 0) + 1,
      clientSegment: '',
      product: '',
      ruleName: ''
    });
    setShowLetterForm(true);
  };

  const handleEditLetter = (letter: SettlementInstructionLetter) => {
    setEditingLetter(letter);
    setLetterForm({ ...letter });
    setShowLetterForm(true);
  };

  const updateLetterForm = (field: keyof SettlementInstructionLetter, value: any) => {
    setLetterForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveLetter = () => {
    if (!letterForm.ruleName || !letterForm.product) return;

    if (editingLetter) {
      // Update existing letter
      setSettlementLetters(prev =>
        prev.map(letter =>
          letter.id === editingLetter.id
            ? { ...letter, ...letterForm } as SettlementInstructionLetter
            : letter
        )
      );
    } else {
      // Add new letter
      const newLetter: SettlementInstructionLetter = {
        id: Date.now().toString(),
        active: letterForm.active || true,
        priority: letterForm.priority || 1,
        ruleName: letterForm.ruleName || '',
        clientSegment: letterForm.clientSegment || 'No Specific Segment',
        product: letterForm.product || '',
        documentUrl: letterForm.documentUrl,
        documentName: letterForm.documentName
      };
      setSettlementLetters(prev => [...prev, newLetter]);
    }

    setShowLetterForm(false);
    setEditingLetter(null);
    setLetterForm({});
  };

  const handleCancelLetter = () => {
    setShowLetterForm(false);
    setEditingLetter(null);
    setLetterForm({});
  };

  const handleDeleteLetter = (letterId: string) => {
    setSettlementLetters(prev => prev.filter(letter => letter.id !== letterId));
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, letterId: string) => {
    setDraggedLetter(letterId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, letterId: string) => {
    e.preventDefault();
    setDragOverLetter(letterId);
  };

  const handleDragLeave = () => {
    setDragOverLetter(null);
  };

  const handleDrop = (e: React.DragEvent, targetLetterId: string) => {
    e.preventDefault();
    
    if (!draggedLetter || draggedLetter === targetLetterId) {
      setDraggedLetter(null);
      setDragOverLetter(null);
      return;
    }

    const draggedLetterObj = settlementLetters.find(l => l.id === draggedLetter);
    const targetLetterObj = settlementLetters.find(l => l.id === targetLetterId);

    if (!draggedLetterObj || !targetLetterObj) return;

    // Swap priorities
    const updatedLetters = settlementLetters.map(letter => {
      if (letter.id === draggedLetter) {
        return { ...letter, priority: targetLetterObj.priority };
      }
      if (letter.id === targetLetterId) {
        return { ...letter, priority: draggedLetterObj.priority };
      }
      return letter;
    });

    setSettlementLetters(updatedLetters);
    setDraggedLetter(null);
    setDragOverLetter(null);
  };

  // Client segmentation handlers
  const handleClientSegmentChange = (clientId: string, newSegment: string | null | undefined) => {
    setPendingChanges(prev => ({ ...prev, [clientId]: newSegment }));
  };

  const handleSaveChanges = () => {
    setClients(prev => 
      prev.map(client => {
        const hasPendingChange = client.id in pendingChanges;
        const newSegment = hasPendingChange ? pendingChanges[client.id] : client.segment;
        return {
          ...client,
          segment: newSegment || undefined
        };
      })
    );
    updateSegmentCounts();
    setPendingChanges({});
  };

  const handleCancelChanges = () => {
    setPendingChanges({});
  };

  const updateSegmentCounts = () => {
    setClientSegments(prev =>
      prev.map(segment => ({
        ...segment,
        clientCount: clients.filter(c => c.segment === segment.name).length
      }))
    );
  };

  const handleClientSelection = (clientId: string, selected: boolean) => {
    if (selected) {
      setSelectedClients(prev => [...prev, clientId]);
    } else {
      setSelectedClients(prev => prev.filter(id => id !== clientId));
    }
  };

  const handleBulkAssignment = (segmentName: string | undefined) => {
    const updates: {[clientId: string]: string | undefined} = {};
    selectedClients.forEach(clientId => {
      updates[clientId] = segmentName;
    });
    setPendingChanges(prev => ({ ...prev, ...updates }));
    setSelectedClients([]);
  };

  const handleAddSegment = () => {
    setEditingSegment(null);
    setSegmentForm({ name: '', description: '' });
    setShowSegmentForm(true);
  };

  const handleEditSegment = (segment: ClientSegment) => {
    setEditingSegment(segment);
    setSegmentForm({ name: segment.name, description: segment.description });
    setShowSegmentForm(true);
  };

  const handleSaveSegment = () => {
    if (!segmentForm.name.trim()) return;

    if (editingSegment) {
      // Update existing segment
      const oldName = editingSegment.name;
      const newName = segmentForm.name;
      
      setClientSegments(prev =>
        prev.map(segment =>
          segment.id === editingSegment.id
            ? { ...segment, name: newName, description: segmentForm.description }
            : segment
        )
      );
      
      // Update client assignments if segment name changed
      if (oldName !== newName) {
        setClients(prev =>
          prev.map(client => ({
            ...client,
            segment: client.segment === oldName ? newName : client.segment
          }))
        );
      }
    } else {
      // Add new segment
      const newSegment: ClientSegment = {
        id: Date.now().toString(),
        name: segmentForm.name,
        description: segmentForm.description,
        clientCount: 0
      };
      setClientSegments(prev => [...prev, newSegment]);
    }

    setShowSegmentForm(false);
    setEditingSegment(null);
    setSegmentForm({ name: '', description: '' });
  };

  const handleDeleteSegment = (segment: ClientSegment) => {
    setShowDeleteConfirm(segment);
  };

  const confirmDeleteSegment = (removeClients: boolean) => {
    if (!showDeleteConfirm) return;

    if (removeClients) {
      // Remove clients from segment
      setClients(prev =>
        prev.map(client => ({
          ...client,
          segment: client.segment === showDeleteConfirm.name ? undefined : client.segment
        }))
      );
    }

    // Remove segment
    setClientSegments(prev => prev.filter(s => s.id !== showDeleteConfirm.id));
    setShowDeleteConfirm(null);
  };

  const getClientsBySegment = () => {
    const clientsBySegment: {[segmentName: string]: Client[]} = {};
    
    // Initialize with all segments
    clientSegments.forEach(segment => {
      clientsBySegment[segment.name] = [];
    });
    clientsBySegment['No Segment'] = [];

    // Group clients by segment using current + pending changes
    clients.forEach(client => {
      const hasPendingChange = client.id in pendingChanges;
      const currentSegment = hasPendingChange ? pendingChanges[client.id] : client.segment;
      const segmentName = currentSegment || 'No Segment';
      if (!clientsBySegment[segmentName]) {
        clientsBySegment[segmentName] = [];
      }
      clientsBySegment[segmentName].push(client);
    });

    // Sort clients alphabetically within each segment
    Object.keys(clientsBySegment).forEach(segmentName => {
      clientsBySegment[segmentName].sort((a, b) => a.name.localeCompare(b.name));
    });

    return clientsBySegment;
  };

  const hasUnsavedChanges = Object.keys(pendingChanges).length > 0;


  // Filter clients based on search query
  const filteredClients = clients.filter(client => 
    searchQuery === '' || 
    client.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    client.rut.includes(searchQuery)
  );

  // Drag and drop handlers for clients
  const handleClientDragStart = (e: React.DragEvent, client: Client) => {
    setDraggedClient(client);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleClientDragEnd = () => {
    // Clear all drag states
    setDraggedClient(null);
    setDragOverSegment(null);
  };

  const clearAllDragStates = () => {
    setDraggedClient(null);
    setDragOverSegment(null);
  };

  const handleSegmentDragOver = (e: React.DragEvent, segmentName: string | null) => {
    e.preventDefault();
    setDragOverSegment(segmentName);
  };

  const handleSegmentDragLeave = () => {
    setDragOverSegment(null);
  };

  const handleSegmentDrop = (e: React.DragEvent, targetSegment: string | null) => {
    e.preventDefault();
    
    if (!draggedClient) {
      clearAllDragStates();
      return;
    }

    // Update client segment through pending changes
    handleClientSegmentChange(draggedClient.id, targetSegment);
    
    // Clear all drag states
    clearAllDragStates();
  };

  const toggleSegmentExpansion = (segmentName: string) => {
    setExpandedSegments(prev => ({
      ...prev,
      [segmentName]: !prev[segmentName]
    }));
  };

  const handleClientPreviewDragStart = (e: React.DragEvent, client: Client) => {
    setDraggedClient(client);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleContextMenu = (e: React.MouseEvent, client: Client) => {
    e.preventDefault();
    setContextMenu({
      client,
      x: e.clientX,
      y: e.clientY
    });
  };

  const handleContextMenuAssign = (client: Client, segmentName: string | null) => {
    handleClientSegmentChange(client.id, segmentName);
    setContextMenu(null);
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  // Close context menu on clicks outside
  React.useEffect(() => {
    const handleClickOutside = () => {
      if (contextMenu) {
        setContextMenu(null);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [contextMenu]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setUploadedFile(file);
      setLetterForm(prev => ({ 
        ...prev, 
        documentName: file.name,
        documentUrl: URL.createObjectURL(file)
      }));
      
      // Create preview URL for PDF
      setFilePreviewUrl(URL.createObjectURL(file));
    }
  };

  const removeUploadedFile = () => {
    if (filePreviewUrl) {
      URL.revokeObjectURL(filePreviewUrl);
    }
    setUploadedFile(null);
    setFilePreviewUrl(null);
    setLetterForm(prev => ({ 
      ...prev, 
      documentName: undefined,
      documentUrl: undefined
    }));
  };

  return (
    <div className="bank-dashboard">
      <div className="bank-tabs">
        <button
          className={`tab-button ${activeTab === 'letters' ? 'active' : ''}`}
          onClick={() => setActiveTab('letters')}
        >
          {t('bank.letters.title')}
        </button>
        <button
          className={`tab-button ${activeTab === 'segmentation' ? 'active' : ''}`}
          onClick={() => setActiveTab('segmentation')}
        >
          {t('bank.segmentation.title')}
        </button>
        <div className="admin-title">Admin</div>
      </div>

      <div className={`bank-content ${showDocumentPreview ? 'with-preview' : ''}`}>
        <div className="main-content">
          {activeTab === 'letters' && !showLetterForm && (
            <div className="letters-settings">
              <div className="letters-header">
                <div className="settlement-header">
                  <div>
                    <h2>{t('bank.letters.title')}</h2>
                    <p className="letters-description">
                      {t('bank.letters.description')}
                    </p>
                  </div>
                  <button className="add-letter-button" onClick={handleAddLetter}>
                    + {t('bank.letters.addTemplate')}
                  </button>
                </div>
              </div>

              <div className="letters-table">
                <div className="table-header">
                  <div className="header-cell">{t('bank.table.active')}</div>
                  <div className="header-cell">{t('bank.table.priority')}</div>
                  <div className="header-cell">{t('bank.table.ruleName')}</div>
                  <div className="header-cell">{t('bank.table.clientSegment')}</div>
                  <div className="header-cell">{t('bank.table.product')}</div>
                  <div className="header-cell">{t('bank.table.document')}</div>
                  <div className="header-cell">{t('bank.table.actions')}</div>
                </div>
                
                {(() => {
                  const orderedLetters = getSortedAndGroupedLetters();
                  
                  const renderLetter = (letter: SettlementInstructionLetter) => (
                    <div 
                      key={letter.id} 
                      className={`table-row ${!letter.active ? 'inactive' : ''} ${dragOverLetter === letter.id ? 'drag-over' : ''}`}
                      draggable
                      onDragStart={(e) => handleDragStart(e, letter.id)}
                      onDragOver={(e) => handleDragOver(e, letter.id)}
                      onDragLeave={handleDragLeave}
                      onDrop={(e) => handleDrop(e, letter.id)}
                    >
                      <div className="table-cell center">
                        <input
                          type="checkbox"
                          checked={letter.active}
                          readOnly
                        />
                      </div>
                      <div className="table-cell center">
                        <span className="drag-handle">⋮⋮</span>
                        {letter.priority}
                      </div>
                      <div className="table-cell">{letter.ruleName}</div>
                      <div className="table-cell">{letter.clientSegment}</div>
                      <div className="table-cell">{letter.product}</div>
                      <div className="table-cell center">
                        {letter.documentUrl && (
                          <button 
                            className="document-preview-button"
                            onClick={() => handleDocumentPreview(letter)}
                            title="Preview document template"
                          >
                            📄
                          </button>
                        )}
                      </div>
                      <div className="table-cell actions">
                        <button className="edit-button" onClick={() => handleEditLetter(letter)}>✏️</button>
                        <button className="delete-button" onClick={() => handleDeleteLetter(letter.id)}>🗑️</button>
                      </div>
                    </div>
                  );

                  return orderedLetters.map((item, index) => {
                    if (item.type === 'header') {
                      const headerText = item.data as string;
                      return (
                        <div key={`header-${headerText}`} className="counterparty-group-header">
                          <h4>{headerText}</h4>
                        </div>
                      );
                    } else {
                      return renderLetter(item.data as SettlementInstructionLetter);
                    }
                  });
                })()}
                
                {settlementLetters.length === 0 && (
                  <div className="empty-state">
                    <p>No settlement instruction letters configured yet. Click "Add New Letter Template" to create your first template.</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'letters' && showLetterForm && (
            <div className="letter-form">
              <h3>{editingLetter ? t('bank.letters.editTemplate') : t('bank.letters.addTemplate')}</h3>
              
              <div className="form-section">
                <h4>Template Information</h4>
                
                <div className="rule-form-header">
                  <div className="form-group">
                    <label>Settlement Instruction Rule Name *</label>
                    <input
                      type="text"
                      value={letterForm.ruleName || ''}
                      onChange={(e) => updateLetterForm('ruleName', e.target.value)}
                      placeholder="Ex: USD FX Spot Premium Client Letter"
                    />
                  </div>
                  
                  <div className="form-group priority-field">
                    <label>Priority *</label>
                    <input
                      type="number"
                      value={letterForm.priority || 1}
                      onChange={(e) => updateLetterForm('priority', parseInt(e.target.value) || 1)}
                      min="1"
                      max="999"
                    />
                  </div>
                  
                  <div className="active-checkbox">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={letterForm.active || false}
                        onChange={(e) => updateLetterForm('active', e.target.checked)}
                      />
                      Active *
                    </label>
                  </div>
                </div>
                
                <div className="form-grid">
                  <div className="form-group">
                    <label>Client Segment</label>
                    <select
                      value={letterForm.clientSegment || ''}
                      onChange={(e) => updateLetterForm('clientSegment', e.target.value)}
                    >
                      <option value="">No Specific Segment</option>
                      {clientSegments.map(segment => (
                        <option key={segment.id} value={segment.name}>{segment.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label>Product *</label>
                    <select
                      value={letterForm.product || ''}
                      onChange={(e) => updateLetterForm('product', e.target.value)}
                    >
                      <option value="">Select product...</option>
                      <option value="FX SPOT">FX SPOT</option>
                      <option value="FX FORWARD">FX FORWARD</option>
                      <option value="FX SWAP">FX SWAP</option>
                      <option value="NDF">NDF</option>
                      <option value="OPTION">OPTION</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="form-section">
                <h4>{t('bank.letters.documentTemplate')}</h4>
                <div className="form-group full-width">
                  <label>{t('bank.letters.documentLabel')}</label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileUpload}
                  />
                  {(uploadedFile || letterForm.documentName) && (
                    <div className="uploaded-document">
                      <span>📄 {uploadedFile?.name || letterForm.documentName}</span>
                      <button 
                        type="button"
                        className="remove-document"
                        onClick={removeUploadedFile}
                      >
                        ✗
                      </button>
                    </div>
                  )}
                  {filePreviewUrl && (
                    <div className="file-preview">
                      <h5>{t('bank.letters.documentPreview')}</h5>
                      <iframe
                        src={filePreviewUrl}
                        width="100%"
                        height="400px"
                        title="PDF Document Preview"
                      />
                    </div>
                  )}
                </div>
              </div>

              <div className="form-actions">
                <button className="save-rule-button" onClick={handleSaveLetter}>
                  Save Letter Template
                </button>
                <button className="cancel-rule-button" onClick={handleCancelLetter}>
                  Cancel
                </button>
              </div>
            </div>
          )}

          {activeTab === 'segmentation' && (
            <div className="segmentation-settings">
              <div className="segmentation-header">
                <div>
                  <h2>{t('bank.segmentation.title')}</h2>
                  <p className="segmentation-description">
                    {t('bank.segmentation.description')}
                  </p>
                </div>
                <div className="segmentation-actions">
                  <button className="add-segment-button" onClick={handleAddSegment}>
                    + {t('bank.segmentation.addSegment')}
                  </button>
                  {hasUnsavedChanges && (
                    <button className="save-all-button" onClick={handleSaveChanges}>
                      {t('bank.segmentation.saveChanges')}
                    </button>
                  )}
                </div>
              </div>

              {/* Inline add segment form - below the buttons */}
              {showSegmentForm && !editingSegment && (
                <div className="add-segment-form">
                  <input
                    type="text"
                    value={segmentForm.name}
                    onChange={(e) => setSegmentForm(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Segment name"
                    autoFocus
                  />
                  <input
                    type="text"
                    value={segmentForm.description}
                    onChange={(e) => setSegmentForm(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Description"
                  />
                  <div className="add-form-actions">
                    <button className="save-segment-button" onClick={handleSaveSegment} disabled={!segmentForm.name.trim()}>
                      ✓ Add
                    </button>
                    <button className="cancel-segment-button" onClick={() => setShowSegmentForm(false)}>
                      ✗ Cancel
                    </button>
                  </div>
                </div>
              )}

              <div className="segmentation-drag-layout">
                {/* Left side: All clients with search */}
                <div className="clients-panel">
                  <div className="clients-panel-header">
                    <h3>Client List</h3>
                    <div className="search-box">
                      <input
                        type="text"
                        placeholder="Search clients..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div className="clients-list">
                    {filteredClients.map(client => {
                      const hasPendingChange = client.id in pendingChanges;
                      const currentSegment = hasPendingChange ? pendingChanges[client.id] : client.segment;
                      const hasChange = hasPendingChange;
                      
                      return (
                        <div 
                          key={client.id} 
                          className={`draggable-client ${hasChange ? 'has-change' : ''}`}
                          draggable
                          onDragStart={(e) => handleClientDragStart(e, client)}
                          onDragEnd={handleClientDragEnd}
                        >
                          <div className="client-info">
                            <h4>{client.name} <span className="client-rut">({client.rut})</span></h4>
                          </div>
                          <div className="client-current-segment">
                            {currentSegment || t('bank.segmentation.noSegment')}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Right side: Segments as drop zones */}
                <div className="segments-panel">
                  <div className="segments-panel-header">
                    <h3>{t('bank.segmentation.availableSegments')}</h3>
                  </div>
                  
                  <div className="segments-drop-zones">
                    {/* No Segment drop zone */}
                    <div 
                      className={`segment-drop-zone no-segment ${dragOverSegment === null ? 'drag-over' : ''}`}
                      onDragOver={(e) => handleSegmentDragOver(e, null)}
                      onDragLeave={handleSegmentDragLeave}
                      onDrop={(e) => handleSegmentDrop(e, null)}
                    >
                      <div className="segment-drop-header">
                        <h4>{t('bank.segmentation.noSegment')}</h4>
                        <div className="segment-header-right">
                          <span className="segment-client-count">
                            ({(getClientsBySegment()['No Segment'] || []).length} {t('bank.segmentation.clientsCount')})
                          </span>
                        </div>
                      </div>
                      <div className="segment-clients-preview">
                        {(() => {
                          const allClientsBySegment = getClientsBySegment();
                          const segmentClients = allClientsBySegment['No Segment'] || [];
                          const isExpanded = expandedSegments['No Segment'];
                          const displayClients = isExpanded ? segmentClients : segmentClients.slice(0, 5);
                          
                          return (
                            <>
                              {displayClients.map(client => (
                                <div 
                                  key={client.id} 
                                  className="client-preview draggable"
                                    draggable
                                    onDragStart={(e) => handleClientPreviewDragStart(e, client)}
                                    onDragEnd={handleClientDragEnd}
                                    onContextMenu={(e) => handleContextMenu(e, client)}
                                >
                                  {client.name} <span className="client-rut-preview">({client.rut})</span>
                                </div>
                              ))}
                              {segmentClients.length > 5 && (
                                <button 
                                  className="expand-clients-button"
                                  onClick={() => toggleSegmentExpansion('No Segment')}
                                >
                                  {isExpanded 
                                    ? `- Show less` 
                                    : `+ ${segmentClients.length - 5} more`
                                  }
                                </button>
                              )}
                            </>
                          );
                        })()}
                      </div>
                    </div>

                    {/* Segment drop zones */}
                    {clientSegments.map(segment => {
                      const segmentClients = getClientsBySegment()[segment.name];
                      return (
                        <div 
                          key={segment.id}
                          className={`segment-drop-zone ${dragOverSegment === segment.name ? 'drag-over' : ''}`}
                          onDragOver={(e) => handleSegmentDragOver(e, segment.name)}
                          onDragLeave={handleSegmentDragLeave}
                          onDrop={(e) => handleSegmentDrop(e, segment.name)}
                        >
                          <div className="segment-drop-header">
                            <h4>{segment.name}</h4>
                            <div className="segment-header-right">
                              <span className="segment-client-count">
                                ({segmentClients.length} {t('bank.segmentation.clientsCount')})
                              </span>
                              <div className="segment-actions">
                                <button 
                                  className="edit-segment-button"
                                  onClick={() => handleEditSegment(segment)}
                                >
                                  ✏️
                                </button>
                                <button 
                                  className="delete-segment-button"
                                  onClick={() => handleDeleteSegment(segment)}
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                          </div>
                          
                          {/* Inline edit segment form - within the card */}
                          {showSegmentForm && editingSegment?.id === segment.id && (
                            <div className="edit-segment-form">
                              <input
                                type="text"
                                value={segmentForm.name}
                                onChange={(e) => setSegmentForm(prev => ({ ...prev, name: e.target.value }))}
                                placeholder="Segment name"
                                autoFocus
                              />
                              <input
                                type="text"
                                value={segmentForm.description}
                                onChange={(e) => setSegmentForm(prev => ({ ...prev, description: e.target.value }))}
                                placeholder="Description"
                              />
                              <div className="edit-form-actions">
                                <button className="save-segment-button" onClick={handleSaveSegment} disabled={!segmentForm.name.trim()}>
                                  ✓
                                </button>
                                <button className="cancel-segment-button" onClick={() => setShowSegmentForm(false)}>
                                  ✗
                                </button>
                              </div>
                            </div>
                          )}
                          
                          <div className="segment-clients-preview">
                            {(() => {
                              const isExpanded = expandedSegments[segment.name];
                              const displayClients = isExpanded ? segmentClients : segmentClients.slice(0, 5);
                              
                              return (
                                <>
                                  {displayClients.map(client => (
                                    <div 
                                      key={client.id} 
                                      className="client-preview draggable"
                                        draggable
                                        onDragStart={(e) => handleClientPreviewDragStart(e, client)}
                                        onDragEnd={handleClientDragEnd}
                                        onContextMenu={(e) => handleContextMenu(e, client)}
                                    >
                                      {client.name} <span className="client-rut-preview">({client.rut})</span>
                                    </div>
                                  ))}
                                  {segmentClients.length > 5 && (
                                    <button 
                                      className="expand-clients-button"
                                      onClick={() => toggleSegmentExpansion(segment.name)}
                                    >
                                      {isExpanded 
                                        ? `- Show less` 
                                        : `+ ${segmentClients.length - 5} more`
                                      }
                                    </button>
                                  )}
                                </>
                              );
                            })()}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

        {showDocumentPreview && previewDocument && (
          <div className="document-preview-sidebar">
            <div className="preview-header">
              <h3>{t('bank.letters.documentPreview')}</h3>
              <button className="close-preview" onClick={closeDocumentPreview}>✗</button>
            </div>
            <div className="preview-content">
              <div className="document-info">
                <h4>{previewDocument.documentName}</h4>
                <p><strong>Rule:</strong> {previewDocument.ruleName}</p>
                <p><strong>Segment:</strong> {previewDocument.clientSegment}</p>
                <p><strong>Product:</strong> {previewDocument.product}</p>
              </div>
              <div className="document-preview-area">
                {previewDocument.documentUrl ? (
                  <iframe
                    src={previewDocument.documentUrl}
                    width="100%"
                    height="600px"
                    title="PDF Document Preview"
                  />
                ) : (
                  <div className="no-document">
                    <p>No PDF document uploaded for this template.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {showDeleteConfirm && (
          <div className="modal-overlay">
            <div className="modal-content">
              <h3>{t('bank.segmentation.deleteSegment')}</h3>
              <p>{t('bank.segmentation.confirmDelete')}</p>
              <p><strong>{showDeleteConfirm.name}</strong> ({showDeleteConfirm.clientCount} clients)</p>
              
              {showDeleteConfirm.clientCount > 0 && (
                <div className="reassignment-options">
                  <p>{t('bank.segmentation.reassignClients')}</p>
                  <button 
                    className="reassign-button"
                    onClick={() => confirmDeleteSegment(true)}
                  >
                    {t('bank.segmentation.removeFromSegment')}
                  </button>
                </div>
              )}

              <div className="modal-actions">
                <button 
                  className="delete-confirm-button"
                  onClick={() => confirmDeleteSegment(false)}
                  disabled={showDeleteConfirm.clientCount > 0}
                >
                  {t('bank.segmentation.deleteSegment')}
                </button>
                <button 
                  className="cancel-button"
                  onClick={() => setShowDeleteConfirm(null)}
                >
                  {t('bank.segmentation.cancel')}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Context Menu */}
        {contextMenu && (
          <div 
            className="context-menu"
            style={{ 
              position: 'fixed', 
              left: contextMenu.x, 
              top: contextMenu.y,
              zIndex: 1000
            }}
          >
            <div className="context-menu-header">
              <strong>{contextMenu.client.name}</strong>
              <span className="client-rut-context">({contextMenu.client.rut})</span>
            </div>
            <div className="context-menu-divider"></div>
            <div className="context-menu-item" onClick={() => handleContextMenuAssign(contextMenu.client, null)}>
              📋 {t('bank.segmentation.noSegment')}
            </div>
            {clientSegments.map(segment => (
              <div 
                key={segment.id}
                className="context-menu-item" 
                onClick={() => handleContextMenuAssign(contextMenu.client, segment.name)}
              >
                📁 {segment.name}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BankDashboard;