import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../components/auth/AuthContext';
import { bankService, SettlementInstructionLetterCreate, SettlementInstructionLetterUpdate } from '../../services/api';
import AlertModal from '../../components/common/AlertModal';
import './BankDashboard.css';

// Interface for Settlement Instruction Letter
interface SettlementInstructionLetter {
  id: string;
  active: boolean;
  priority: number;
  ruleName: string;
  clientSegment: string; // This will be mapped from clientSegmentId
  clientSegmentId?: string;
  product: string;
  documentUrl?: string;
  documentName?: string;
  templateVariables?: string[];
  conditions?: Record<string, any>;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
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
  clientCount?: number; // This will be calculated client-side
  color?: string;
  createdAt?: string;
  lastUpdatedAt?: string;
  lastUpdatedBy?: string;
}

const BankDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  const [activeTab, setActiveTab] = useState<'letters' | 'segmentation'>('letters');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Settlement Instructions Letters state
  const [settlementLetters, setSettlementLetters] = useState<SettlementInstructionLetter[]>([]);

  // Client Segmentation state
  const [clients, setClients] = useState<Client[]>([]);
  const [clientSegments, setClientSegments] = useState<ClientSegment[]>([]);
  const [clientAssignments, setClientAssignments] = useState<Record<string, string[]>>({});

  // Document preview state
  const [showDocumentPreview, setShowDocumentPreview] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<SettlementInstructionLetter | null>(null);
  const [previewErrorMessage, setPreviewErrorMessage] = useState<string>('');

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
  const [isUploadingDocument, setIsUploadingDocument] = useState(false);

  // Save state for client segmentation
  const [isSavingSegments, setIsSavingSegments] = useState(false);
  
  // Unsaved changes tracking
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [pendingTabChange, setPendingTabChange] = useState<string | null>(null);
  const [showUnsavedChangesModal, setShowUnsavedChangesModal] = useState(false);
  
  // Alert modal state
  const [alertModal, setAlertModal] = useState({
    isOpen: false,
    title: '',
    message: '',
    type: 'warning' as 'info' | 'warning' | 'error' | 'success'
  });

  // Data loading functions
  const loadSettlementLetters = async () => {
    if (!user?.profile?.organization?.id) return;
    
    try {
      const response = await bankService.getSettlementLetters(user.profile.organization.id);
      if (response.success && response.data) {
        // Map API response to component interface
        const mappedLetters = response.data.map((letter: any) => ({
          id: letter.id || `letter-${Date.now()}-${Math.random()}`,
          active: letter.active,
          priority: letter.priority,
          ruleName: letter.rule_name || letter.ruleName, // Handle both formats
          product: letter.product,
          clientSegmentId: letter.client_segment_id || letter.clientSegmentId,
          documentName: letter.document_name || letter.documentName,
          documentUrl: letter.document_url || letter.documentUrl,
          templateVariables: letter.template_variables || letter.templateVariables || [],
          conditions: letter.conditions || {},
          createdAt: letter.createdAt || letter.created_at,
          lastUpdatedAt: letter.lastUpdatedAt || letter.last_updated_at,
          lastUpdatedBy: letter.lastUpdatedBy || letter.last_updated_by,
          clientSegment: getSegmentNameById(letter.client_segment_id || letter.clientSegmentId) || 'No Specific Segment'
        }));
        setSettlementLetters(mappedLetters);
      }
    } catch (error) {
      console.error('Error loading settlement letters:', error);
      setError('Failed to load settlement letters');
    }
  };

  const loadClientSegments = async () => {
    if (!user?.profile?.organization?.id) return;
    
    try {
      const response = await bankService.getClientSegments(user.profile.organization.id);
      if (response.success && response.data) {
        // Ensure IDs exist
        const segmentsWithIds = response.data.map(segment => ({
          ...segment,
          id: segment.id || `segment-${Date.now()}-${Math.random()}`
        }));
        setClientSegments(segmentsWithIds);
      }
    } catch (error) {
      console.error('Error loading client segments:', error);
      setError('Failed to load client segments');
    }
  };

  const loadClientAssignments = async () => {
    if (!user?.profile?.organization?.id) return;
    
    try {
      const response = await bankService.getClientSegmentAssignments(user.profile.organization.id);
      if (response.success && response.data) {
        setClientAssignments(response.data);
      }
    } catch (error) {
      console.error('Error loading client assignments:', error);
      setError('Failed to load client assignments');
    }
  };

  const loadClients = async (assignments?: Record<string, string[]>, segments?: ClientSegment[]) => {
    // Use provided assignments or fall back to state
    const assignmentsToUse = assignments || clientAssignments;
    // Use provided segments or fall back to state
    const segmentsToUse = segments || clientSegments;
    
    try {
      const response = await bankService.getAllClients();
      if (response.success && response.data) {
        // Transform client data from database to match our Client interface
        const clientsWithSegments = response.data.map(client => {
          // Find which segment this client is assigned to
          let assignedSegment: string | undefined;
          for (const [segmentId, clientIds] of Object.entries(assignmentsToUse)) {
            if (clientIds.includes(client.id)) {
              const segment = segmentsToUse.find(s => s.id === segmentId);
              assignedSegment = segment?.name;
              break;
            }
          }
          
          return {
            id: client.id,
            name: client.name,
            rut: client.taxId,
            segment: assignedSegment
          };
        });
        
        setClients(clientsWithSegments);
      }
    } catch (error) {
      console.error('Error loading clients:', error);
      setError('Failed to load clients');
    }
  };

  const loadAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load segments first and store them
      const segmentsResponse = await bankService.getClientSegments(user?.profile?.organization?.id || '');
      let loadedSegments: ClientSegment[] = [];
      if (segmentsResponse.success && segmentsResponse.data) {
        const segmentsWithIds = segmentsResponse.data.map(segment => ({
          ...segment,
          id: segment.id || `segment-${Date.now()}-${Math.random()}`
        }));
        setClientSegments(segmentsWithIds);
        loadedSegments = segmentsWithIds;
      }
      
      // Load assignments and pass both assignments and segments to loadClients
      const assignmentsResponse = await bankService.getClientSegmentAssignments(user?.profile?.organization?.id || '');
      if (assignmentsResponse.success && assignmentsResponse.data) {
        setClientAssignments(assignmentsResponse.data);
        await loadClients(assignmentsResponse.data, loadedSegments);
      }
      
      await loadSettlementLetters();
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Helper functions
  const getSegmentNameById = (segmentId?: string) => {
    if (!segmentId) return null;
    const segment = clientSegments.find(s => s.id === segmentId);
    return segment?.name || null;
  };


  // Load data on component mount and when user changes
  useEffect(() => {
    if (user?.profile?.organization?.id) {
      loadAllData();
    }
  }, [user?.profile?.organization?.id]);

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
  const handleDocumentPreview = async (letter: SettlementInstructionLetter) => {
    // Show preview modal immediately with loading state
    setPreviewDocument({
      ...letter,
      documentUrl: 'loading' // Special value to indicate loading
    });
    setPreviewErrorMessage('');
    setShowDocumentPreview(true);
    
    try {
      // Generate a fresh signed URL for document preview
      const response = await bankService.previewSettlementLetterDocument(user?.profile?.organization?.id || '', letter.id);
      
      if (response.success && response.data.signed_url) {
        // Update with the actual signed URL
        setPreviewDocument({
          ...letter,
          documentUrl: response.data.signed_url
        });
        setPreviewErrorMessage('');
      } else {
        console.error('Failed to generate preview URL:', response.message);
        // Update with error state
        setPreviewDocument({
          ...letter,
          documentUrl: 'error'
        });
        setPreviewErrorMessage(response.message || 'Failed to generate preview URL');
      }
    } catch (error) {
      console.error('Error generating document preview URL:', error);
      // Update with error state
      setPreviewDocument({
        ...letter,
        documentUrl: 'error'
      });
      setPreviewErrorMessage(error instanceof Error ? error.message : 'Failed to generate preview URL');
    }
  };

  const closeDocumentPreview = () => {
    setShowDocumentPreview(false);
    setPreviewDocument(null);
    setPreviewErrorMessage('');
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

  const handleSaveLetter = async () => {
    if (!letterForm.ruleName || !letterForm.product) return;

    setIsSavingSegments(true);
    try {
      if (editingLetter) {
        // Update existing letter
        const updateData: SettlementInstructionLetterUpdate = {
          active: letterForm.active || true,
          priority: letterForm.priority || 1,
          rule_name: letterForm.ruleName,
          product: letterForm.product,
          client_segment_id: letterForm.clientSegmentId,
          document_name: letterForm.documentName || '',
          document_url: letterForm.documentUrl || '',
          template_variables: letterForm.templateVariables || [],
          conditions: letterForm.conditions || {}
        };

        const response = await bankService.updateSettlementLetter(user?.profile?.organization?.id || '', editingLetter.id!, updateData);
        
        if (response.success) {
          // Map API response to local interface
          const apiData: any = response.data;
          const updatedLetter: SettlementInstructionLetter = {
            id: apiData.id || editingLetter.id!,
            active: apiData.active,
            priority: apiData.priority,
            ruleName: apiData.rule_name,
            product: apiData.product,
            clientSegmentId: apiData.client_segment_id,
            documentName: apiData.document_name,
            documentUrl: apiData.document_url,
            templateVariables: apiData.template_variables || [],
            conditions: apiData.conditions || {},
            createdAt: apiData.created_at,
            lastUpdatedAt: apiData.last_updated_at,
            lastUpdatedBy: apiData.last_updated_by,
            clientSegment: getSegmentNameById(apiData.client_segment_id) || 'No Specific Segment'
          };
          
          setSettlementLetters(prev =>
            prev.map(letter =>
              letter.id === editingLetter.id ? updatedLetter : letter
            )
          );
          setAlertModal({
            isOpen: true,
            title: 'Success',
            message: 'Settlement letter template updated successfully',
            type: 'success'
          });
        } else {
          throw new Error(response.message || 'Failed to update settlement letter');
        }
      } else {
        // Create new letter
        let response;
        
        if (uploadedFile) {
          // Use the new endpoint with file upload
          setIsUploadingDocument(true);
          
          const letterData = {
            rule_name: letterForm.ruleName,
            product: letterForm.product,
            client_segment_id: letterForm.clientSegmentId,
            priority: letterForm.priority || 1,
            active: letterForm.active !== false, // Default to true
            template_variables: letterForm.templateVariables || [],
            conditions: letterForm.conditions || {}
          };

          response = await bankService.createSettlementLetterWithDocument(
            user?.profile?.organization?.id || '', 
            letterData, 
            uploadedFile
          );
          
          setIsUploadingDocument(false);
        } else {
          // Use the original endpoint without file upload
          const createData: SettlementInstructionLetterCreate = {
            active: letterForm.active || true,
            priority: letterForm.priority || 1,
            rule_name: letterForm.ruleName,
            product: letterForm.product,
            client_segment_id: letterForm.clientSegmentId,
            document_name: letterForm.documentName || '',
            document_url: letterForm.documentUrl || '',
            template_variables: letterForm.templateVariables || [],
            conditions: letterForm.conditions || {}
          };

          response = await bankService.createSettlementLetter(user?.profile?.organization?.id || '', createData);
        }
        
        if (response.success) {
          // Map API response to local interface
          const apiData: any = response.data;
          const newLetter: SettlementInstructionLetter = {
            id: apiData.id || `letter-${Date.now()}`,
            active: apiData.active,
            priority: apiData.priority,
            ruleName: apiData.rule_name,
            product: apiData.product,
            clientSegmentId: apiData.client_segment_id,
            documentName: apiData.document_name,
            documentUrl: apiData.document_url,
            templateVariables: apiData.template_variables || [],
            conditions: apiData.conditions || {},
            createdAt: apiData.created_at,
            lastUpdatedAt: apiData.last_updated_at,
            lastUpdatedBy: apiData.last_updated_by,
            clientSegment: getSegmentNameById(apiData.client_segment_id) || 'No Specific Segment'
          };
          
          setSettlementLetters(prev => [...prev, newLetter]);
          setAlertModal({
            isOpen: true,
            title: 'Success',
            message: 'Settlement letter template created successfully',
            type: 'success'
          });
        } else {
          throw new Error(response.message || 'Failed to create settlement letter');
        }
      }

      setShowLetterForm(false);
      setEditingLetter(null);
      setLetterForm({});
      
      // Clean up file upload state
      if (filePreviewUrl) {
        URL.revokeObjectURL(filePreviewUrl);
      }
      setUploadedFile(null);
      setFilePreviewUrl(null);
    } catch (error) {
      console.error('Error saving settlement letter:', error);
      setAlertModal({
        isOpen: true,
        title: 'Error',
        message: error instanceof Error ? error.message : 'Failed to save settlement letter',
        type: 'error'
      });
    } finally {
      setIsSavingSegments(false);
      setIsUploadingDocument(false);
    }
  };

  const handleCancelLetter = () => {
    setShowLetterForm(false);
    setEditingLetter(null);
    setLetterForm({});
    
    // Clean up file upload state
    if (filePreviewUrl) {
      URL.revokeObjectURL(filePreviewUrl);
    }
    setUploadedFile(null);
    setFilePreviewUrl(null);
  };

  const handleDeleteLetter = async (letterId: string) => {
    if (!user?.profile?.organization?.id) return;
    
    try {
      const response = await bankService.deleteSettlementLetter(user.profile.organization.id, letterId);
      if (response.success) {
        setSettlementLetters(prev => prev.filter(letter => letter.id !== letterId));
      }
    } catch (error) {
      console.error('Error deleting settlement letter:', error);
      setError('Failed to delete settlement letter');
    }
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
    setHasUnsavedChanges(true);
  };

  const handleSaveChanges = async () => {
    if (!user?.profile?.organization?.id) return;
    
    // Prevent double-clicking
    if (isSavingSegments) return;
    
    setIsSavingSegments(true);
    
    try {
      const assignments: Array<{ clientId: string; segmentId: string }> = [];
      const removals: Array<{ clientId: string; segmentId: string }> = [];

      // Process each pending change
      for (const [clientId, newSegmentName] of Object.entries(pendingChanges)) {
        const client = clients.find(c => c.id === clientId);
        const oldSegmentName = client?.segment;

        // If newSegmentName is null/undefined and there was an old segment, 
        // it means we're removing the client from their segment
        if (!newSegmentName && oldSegmentName) {
          const oldSegment = clientSegments.find(s => s.name === oldSegmentName);
          if (oldSegment?.id) {
            removals.push({ clientId, segmentId: oldSegment.id });
          }
        }
        // If there's a new segment, just assign (backend will handle removal from old segment)
        else if (newSegmentName) {
          const newSegment = clientSegments.find(s => s.name === newSegmentName);
          if (newSegment?.id) {
            assignments.push({ clientId, segmentId: newSegment.id });
          }
        }
      }

      // Execute removals first (only for clients being unassigned completely)
      for (const removal of removals) {
        await bankService.removeClientFromSegment(
          user.profile.organization.id,
          removal.clientId,
          removal.segmentId
        );
      }

      // Then execute assignments (backend handles removal from old segment automatically)
      for (const assignment of assignments) {
        await bankService.assignClientToSegment(user.profile.organization.id, {
          client_id: assignment.clientId,
          segment_id: assignment.segmentId
        });
      }

      // Update local state after successful API calls
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

      // Update client assignments state
      setClientAssignments(prev => {
        const updated = { ...prev };
        
        // Remove from old assignments
        for (const removal of removals) {
          if (updated[removal.segmentId]) {
            updated[removal.segmentId] = updated[removal.segmentId].filter(
              clientId => clientId !== removal.clientId
            );
          }
        }

        // Add to new assignments
        for (const assignment of assignments) {
          if (!updated[assignment.segmentId]) {
            updated[assignment.segmentId] = [];
          }
          if (!updated[assignment.segmentId].includes(assignment.clientId)) {
            updated[assignment.segmentId].push(assignment.clientId);
          }
        }

        return updated;
      });

      updateSegmentCounts();
      setPendingChanges({});
      setHasUnsavedChanges(false);

      // Show success message
      setAlertModal({
        isOpen: true,
        title: t('bank.segmentation.saveSuccess.title'),
        message: t('bank.segmentation.saveSuccess.message'),
        type: 'success'
      });

      // Reload all data to ensure we have the latest state
      await loadAllData();

    } catch (error) {
      console.error('Error saving client segment changes:', error);
      setAlertModal({
        isOpen: true,
        title: t('bank.segmentation.saveError.title'),
        message: t('bank.segmentation.saveError.message'),
        type: 'error'
      });
    } finally {
      setIsSavingSegments(false);
    }
  };

  const handleCancelChanges = () => {
    setPendingChanges({});
    setHasUnsavedChanges(false);
  };

  // Unsaved changes handlers
  const handleTabChange = (newTab: 'letters' | 'segmentation') => {
    const hasSegmentationChanges = hasUnsavedChanges && activeTab === 'segmentation';
    const hasSettlementFormOpen = showLetterForm && activeTab === 'letters';
    
    if (hasSegmentationChanges || hasSettlementFormOpen) {
      setPendingTabChange(newTab);
      setShowUnsavedChangesModal(true);
    } else {
      setActiveTab(newTab);
    }
  };

  const handleSaveAndContinue = async () => {
    if (activeTab === 'segmentation' && hasUnsavedChanges) {
      await handleSaveChanges();
    } else if (activeTab === 'letters' && showLetterForm) {
      await handleSaveLetter();
    }
    
    if (pendingTabChange) {
      setActiveTab(pendingTabChange as 'letters' | 'segmentation');
      setPendingTabChange(null);
    }
    setShowUnsavedChangesModal(false);
  };

  const handleDiscardAndContinue = () => {
    // Reset segmentation changes
    setPendingChanges({});
    setHasUnsavedChanges(false);
    
    // Reset settlement letter form
    if (showLetterForm) {
      setShowLetterForm(false);
      setEditingLetter(null);
      setLetterForm({});
      
      // Clean up file upload state
      if (filePreviewUrl) {
        URL.revokeObjectURL(filePreviewUrl);
      }
      setUploadedFile(null);
      setFilePreviewUrl(null);
    }
    
    // Navigate to pending tab
    if (pendingTabChange) {
      setActiveTab(pendingTabChange as 'letters' | 'segmentation');
      setPendingTabChange(null);
    }
    setShowUnsavedChangesModal(false);
  };

  const handleCancelNavigation = () => {
    setPendingTabChange(null);
    setShowUnsavedChangesModal(false);
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

  const confirmDeleteSegment = async (removeClients: boolean) => {
    if (!showDeleteConfirm || !user?.profile?.organization?.id) return;

    try {
      if (removeClients) {
        // Remove all clients from this segment first
        const clientsInSegment = clientAssignments[showDeleteConfirm.id] || [];
        for (const clientId of clientsInSegment) {
          await bankService.removeClientFromSegment(user.profile.organization.id, clientId, showDeleteConfirm.id);
        }
        
        // Update local state
        setClients(prev =>
          prev.map(client => ({
            ...client,
            segment: client.segment === showDeleteConfirm.name ? undefined : client.segment
          }))
        );
      }

      // Delete the segment
      const response = await bankService.deleteClientSegment(user.profile.organization.id, showDeleteConfirm.id);
      if (response.success) {
        setClientSegments(prev => prev.filter(s => s.id !== showDeleteConfirm.id));
        // Remove from assignments
        setClientAssignments(prev => {
          const updated = { ...prev };
          delete updated[showDeleteConfirm.id];
          return updated;
        });
      }
    } catch (error) {
      console.error('Error deleting segment:', error);
      setError('Failed to delete segment');
    } finally {
      setShowDeleteConfirm(null);
    }
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

    // Only update pending changes (no API call yet)
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

  if (loading) {
    return (
      <div className="bank-dashboard">
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Loading bank data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bank-dashboard">
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p style={{ color: 'var(--color-error)' }}>Error: {error}</p>
          <button onClick={loadAllData} style={{ marginTop: '1rem' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bank-dashboard">
      <div className="bank-tabs">
        <button
          className={`tab-button ${activeTab === 'letters' ? 'active' : ''}`}
          onClick={() => handleTabChange('letters')}
        >
          {t('bank.letters.title')}
        </button>
        <button
          className={`tab-button ${activeTab === 'segmentation' ? 'active' : ''}`}
          onClick={() => handleTabChange('segmentation')}
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
                    <p>{t('bank.letters.emptyState')}</p>
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
                <button className="save-rule-button" onClick={handleSaveLetter} disabled={isSavingSegments || isUploadingDocument}>
                  {isUploadingDocument ? 'Uploading Document...' : (isSavingSegments ? t('bank.segmentation.saving') : 'Save Letter Template')}
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
                    <>
                      <button 
                        className="save-all-button" 
                        onClick={handleSaveChanges}
                        disabled={isSavingSegments}
                      >
                        {isSavingSegments ? t('bank.segmentation.saving') : t('bank.segmentation.saveChanges')}
                      </button>
                      <button 
                        className="cancel-changes-button" 
                        onClick={handleCancelChanges}
                        disabled={isSavingSegments}
                      >
                        {t('bank.segmentation.cancelChanges')}
                      </button>
                    </>
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
                          key={`unassigned-${client.id}`} 
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
                                  key={`expanded-no-segment-${client.id}`} 
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
                                      key={`collapsed-${segment.name}-${client.id}`} 
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
                {previewDocument.documentUrl === 'loading' ? (
                  <div className="document-loading">
                    <div className="loading-spinner"></div>
                    <p>{t('bank.letters.retrievingDocument')}</p>
                  </div>
                ) : previewDocument.documentUrl === 'error' ? (
                  <div className="document-error">
                    <p>❌ {t('bank.letters.failedToLoadDocument')}</p>
                    <p className="error-message">{previewErrorMessage || t('bank.letters.unknownError')}</p>
                  </div>
                ) : previewDocument.documentUrl ? (
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
              <p><strong>{showDeleteConfirm.name}</strong> ({showDeleteConfirm.clientCount ?? 0} clients)</p>
              
              {(showDeleteConfirm.clientCount ?? 0) > 0 && (
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
                  disabled={(showDeleteConfirm.clientCount ?? 0) > 0}
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
      
      {/* Unsaved Changes Modal */}
      {showUnsavedChangesModal && (
        <div className="modal-overlay">
          <div className="modal unsaved-changes-modal">
            <h3>{t('bank.unsavedChanges.title')}</h3>
            <p>{
              activeTab === 'segmentation' && hasUnsavedChanges
                ? t('bank.unsavedChanges.message')
                : activeTab === 'letters' && showLetterForm
                ? 'You have an unsaved settlement letter template. Do you want to save it before continuing?'
                : t('bank.unsavedChanges.message')
            }</p>
            <div className="modal-actions">
              <button 
                className="save-button primary"
                onClick={handleSaveAndContinue}
                disabled={isSavingSegments}
              >
                {isSavingSegments ? t('bank.unsavedChanges.saving') : t('bank.unsavedChanges.saveAndContinue')}
              </button>
              <button 
                className="save-button secondary"
                onClick={handleDiscardAndContinue}
                disabled={isSavingSegments}
              >
                {t('bank.unsavedChanges.discardAndContinue')}
              </button>
              <button 
                className="cancel-button"
                onClick={handleCancelNavigation}
                disabled={isSavingSegments}
              >
                {t('bank.unsavedChanges.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Alert Modal for success/error messages */}
      <AlertModal
        isOpen={alertModal.isOpen}
        onClose={() => setAlertModal({ ...alertModal, isOpen: false })}
        title={alertModal.title}
        message={alertModal.message}
        type={alertModal.type}
      />
    </div>
  );
};

export default BankDashboard;