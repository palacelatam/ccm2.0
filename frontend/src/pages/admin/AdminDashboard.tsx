import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import * as XLSX from 'xlsx';
import { useAuth } from '../../components/auth/AuthContext';
import { clientService } from '../../services/api/clientService';
import AlertModal from '../../components/common/AlertModal';
import { getTradeCodeOptions } from '../../constants/tradeCodes';
import './AdminDashboard.css';

interface AlertSettings {
  emailConfirmedTrades: {
    enabled: boolean;
    emails: string[];
  };
  emailDisputedTrades: {
    enabled: boolean;
    emails: string[];
  };
  smsConfirmedTrades: {
    enabled: boolean;
    phones: string[];
  };
  smsDisputedTrades: {
    enabled: boolean;
    phones: string[];
  };
}

interface AutomationSettings {
  dataSharing: boolean;
  autoConfirmMatched: {
    enabled: boolean;
    delayMinutes: number;
  };
  autoCartaInstruccion: boolean;
  autoConfirmDisputed: {
    enabled: boolean;
    delayMinutes: number;
  };
}

interface SettlementRule {
  id: string;
  active: boolean;
  priority: number;
  name: string;
  direction: string;
  counterparty: string;
  product: string;
  modalidad: string;
  settlementCurrency?: string; // For compensación modality
  // Account details - Cargar section
  cargarCurrency?: string;
  cargarBankName?: string;
  cargarSwiftCode?: string;
  cargarAccountNumber?: string;
  // Account details - Abonar section
  abonarCurrency?: string;
  abonarBankName?: string;
  abonarSwiftCode?: string;
  abonarAccountNumber?: string;
  // Central Bank Trade Code
  centralBankTradeCode?: string;
}

interface BankAccount {
  id: string;
  active: boolean;
  accountName: string;
  bankName: string;
  swiftCode: string;
  accountCurrency: string;
  accountNumber: string;
  isDefault: boolean;
}

interface ExpectedField {
  name: string;
  type: 'string' | 'number' | 'date' | 'enum';
  format?: string;
  required: boolean;
  enumValues?: string[];
  description: string;
}

interface FieldMapping {
  sourceField: string;
  targetField: string;
  transformation?: {
    type: 'direct' | 'format' | 'enum' | 'split' | 'combine';
    params?: any;
  };
}

interface DataMapping {
  id: string;
  name: string;
  description: string;
  fileType: 'csv' | 'excel' | 'json';
  createdDate: string;
  fieldMappings: FieldMapping[];
  sampleData?: any[];
}

const AdminDashboard: React.FC = () => {
  const { t } = useTranslation();
  const { user } = useAuth();
  
  // Expected fields for trade data mapping (based on ClientTradesGrid columns, excluding status and source)
  const EXPECTED_FIELDS: ExpectedField[] = [
    { name: 'tradeId', type: 'string', format: 'text', required: true, description: 'Unique identifier for the trade' },
    { name: 'counterparty', type: 'string', format: 'text', required: true, description: 'Bank or financial institution counterparty' },
    { name: 'productType', type: 'enum', format: 'text', required: true, enumValues: ['FX Spot', 'FX Forward'], description: 'Type of financial product' },
    { name: 'tradeDate', type: 'date', format: 'YYYY-MM-DD', required: true, description: 'Date when trade was executed' },
    { name: 'valueDate', type: 'date', format: 'YYYY-MM-DD', required: true, description: 'Settlement/value date for the trade' },
    { name: 'currency1', type: 'enum', format: 'ISO code', required: true, enumValues: ['USD', 'CLP', 'EUR', 'GBP', 'CLF'], description: 'Primary currency (3-letter ISO code)' },
    { name: 'currency2', type: 'enum', format: 'ISO code', required: true, enumValues: ['USD', 'CLP', 'EUR', 'GBP', 'CLF'], description: 'Secondary currency (3-letter ISO code)' },
    { name: 'amount', type: 'number', format: 'decimal', required: true, description: 'Trade amount/notional value' },
    { name: 'price', type: 'number', format: 'decimal(4)', required: true, description: 'Exchange rate or price (4 decimal places)' },
    { name: 'paymentDate', type: 'date', format: 'YYYY-MM-DD', required: true, description: 'Date when payment is due' }
  ];
  
  // Chilean banks list in alphabetical order
  const CHILEAN_BANKS = [
    'Banco BICE',
    'Banco BTG Pactual Chile',
    'Banco Consorcio',
    'Banco de Chile',
    'Banco de Crédito e Inversiones',
    'Banco del Estado de Chile',
    'Banco Falabella',
    'Banco Internacional',
    'Banco Itaú Chile',
    'Banco Ripley',
    'Banco Santander Chile',
    'Banco Security',
    'HSBC Bank Chile',
    'Scotiabank Chile',
    'Tanner Banco Digital'
  ];
  
  const [activeTab, setActiveTab] = useState<'automation' | 'alerts' | 'settlement' | 'accounts' | 'mapping'>('automation');
  
  // Unsaved changes tracking
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [pendingTabChange, setPendingTabChange] = useState<string | null>(null);
  const [showUnsavedChangesModal, setShowUnsavedChangesModal] = useState(false);
  
  // Original values for reset functionality
  const [originalAutomationSettings, setOriginalAutomationSettings] = useState<AutomationSettings | null>(null);
  const [originalAlertSettings, setOriginalAlertSettings] = useState<AlertSettings | null>(null);
  const [originalBankAccounts, setOriginalBankAccounts] = useState<BankAccount[] | null>(null);
  const [originalSettlementRules, setOriginalSettlementRules] = useState<SettlementRule[] | null>(null);
  
  const [automationSettings, setAutomationSettings] = useState<AutomationSettings>({
    dataSharing: true,
    autoConfirmMatched: {
      enabled: true,
      delayMinutes: 30
    },
    autoCartaInstruccion: false,
    autoConfirmDisputed: {
      enabled: false,
      delayMinutes: 60
    }
  });
  
  const [alertSettings, setAlertSettings] = useState<AlertSettings>({
    emailConfirmedTrades: {
      enabled: true,
      emails: ['admin@palace.cl', 'trades@palace.cl']
    },
    emailDisputedTrades: {
      enabled: true,
      emails: ['admin@palace.cl', 'disputes@palace.cl']
    },
    smsConfirmedTrades: {
      enabled: false,
      phones: ['+56912345678']
    },
    smsDisputedTrades: {
      enabled: true,
      phones: ['+56912345678', '+56987654321']
    }
  });
  
  const [newEmailConfirmed, setNewEmailConfirmed] = useState('');
  const [newEmailDisputed, setNewEmailDisputed] = useState('');
  const [newPhoneConfirmed, setNewPhoneConfirmed] = useState('');
  const [newPhoneDisputed, setNewPhoneDisputed] = useState('');
  
  // Bank Accounts state
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);

  // Settlement Rules state
  const [settlementRules, setSettlementRules] = useState<SettlementRule[]>([]);
  
  const [showRuleForm, setShowRuleForm] = useState(false);
  const [editingRule, setEditingRule] = useState<SettlementRule | null>(null);
  const [ruleForm, setRuleForm] = useState<Partial<SettlementRule>>({});
  const [isSavingRule, setIsSavingRule] = useState(false);
  
  // Accounts state
  const [editingAccount, setEditingAccount] = useState<string | null>(null);
  const [accountForm, setAccountForm] = useState<Partial<BankAccount>>({});
  const [accountGrouping, setAccountGrouping] = useState<'none' | 'bank' | 'currency'>('none');
  const [isSavingAccount, setIsSavingAccount] = useState(false);
  
  // Drag and drop state
  const [draggedRule, setDraggedRule] = useState<string | null>(null);
  const [dragOverRule, setDragOverRule] = useState<string | null>(null);
  
  // Modal state
  const [alertModal, setAlertModal] = useState({
    isOpen: false,
    title: '',
    message: '',
    type: 'warning' as 'info' | 'warning' | 'error' | 'success'
  });
  
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Data Mapping state
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedData, setUploadedData] = useState<any[] | null>(null);
  const [sourceFields, setSourceFields] = useState<string[]>([]);
  const [currentMapping, setCurrentMapping] = useState<FieldMapping[]>([]);
  const [mappedData, setMappedData] = useState<any[] | null>(null);
  const [dataMappings, setDataMappings] = useState<DataMapping[]>([]);
  const [showMappingForm, setShowMappingForm] = useState(false);
  const [editingMapping, setEditingMapping] = useState<DataMapping | null>(null);
  const [mappingForm, setMappingForm] = useState<{name: string, description: string}>({name: '', description: ''});
  const [dragOverUpload, setDragOverUpload] = useState(false);
  
  // Load client settings on component mount
  useEffect(() => {
    const loadClientSettings = async () => {
      if (!user?.profile?.organization?.id) {
        setLoadError('No organization ID found');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const response = await clientService.getClientSettings(user.profile.organization.id);
        
        if (response.success && response.data) {
          // Update automation settings
          setAutomationSettings(response.data.automation);
          setOriginalAutomationSettings(response.data.automation);
          
          // Update alert settings
          setAlertSettings(response.data.alerts);
          setOriginalAlertSettings(response.data.alerts);
        }
        
        // Load bank accounts
        const accountsResponse = await clientService.getBankAccounts(user.profile.organization.id);
        let accounts: BankAccount[] = [];
        if (accountsResponse.success && accountsResponse.data) {
          accounts = accountsResponse.data.map(account => ({
            id: account.id || '',
            active: account.active,
            accountName: account.accountName,
            bankName: account.bankName,
            swiftCode: account.swiftCode,
            accountCurrency: account.accountCurrency,
            accountNumber: account.accountNumber,
            isDefault: account.isDefault
          }));
          setBankAccounts(accounts);
          setOriginalBankAccounts([...accounts]);
        }
        
        // Load settlement rules
        const rulesResponse = await clientService.getSettlementRules(user.profile.organization.id);
        if (rulesResponse.success && rulesResponse.data) {
          const rules = rulesResponse.data.map((rule, index) => {
            // If backend doesn't provide ID, generate a consistent one based on rule data
            let finalId = rule.id;
            if (!finalId || finalId === 'undefined' || finalId.trim() === '') {
              // Generate consistent ID based on priority and name (matches backend logic)
              finalId = `rule-${rule.priority}-${rule.name.replace(/\s+/g, '-').toLowerCase()}`;
            }
            
            return {
              id: finalId,
              active: rule.active,
              priority: rule.priority,
              name: rule.name,
              direction: rule.direction || '',
              counterparty: rule.counterparty,
              product: rule.product,
              modalidad: rule.modalidad || '',
              cargarCurrency: rule.cargarCurrency || '',
              cargarBankName: rule.cargarBankName || '',
              cargarSwiftCode: rule.cargarSwiftCode || '',
              cargarAccountNumber: rule.cargarAccountNumber || '',
              abonarCurrency: rule.abonarCurrency || '',
              abonarBankName: rule.abonarBankName || '',
              abonarSwiftCode: rule.abonarSwiftCode || '',
              abonarAccountNumber: rule.abonarAccountNumber || '',
              centralBankTradeCode: rule.centralBankTradeCode || ''
            };
          });
          setSettlementRules(rules);
          setOriginalSettlementRules([...rules]);
        }
        
      } catch (error) {
        console.error('Failed to load client settings:', error);
        setLoadError(error instanceof Error ? error.message : 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    loadClientSettings();
  }, [user?.profile?.organization?.id]);
  
  const handleAutomationChange = (key: keyof AutomationSettings, value: any) => {
    setAutomationSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setHasUnsavedChanges(true);
  };
  
  const handleDelayChange = (setting: 'autoConfirmMatched' | 'autoConfirmDisputed', minutes: number) => {
    setAutomationSettings(prev => ({
      ...prev,
      [setting]: {
        ...prev[setting],
        delayMinutes: minutes
      }
    }));
    setHasUnsavedChanges(true);
  };
  
  const addEmail = (alertType: 'emailConfirmedTrades' | 'emailDisputedTrades') => {
    const email = alertType === 'emailConfirmedTrades' ? newEmailConfirmed : newEmailDisputed;
    const setEmail = alertType === 'emailConfirmedTrades' ? setNewEmailConfirmed : setNewEmailDisputed;
    
    if (email && email.includes('@')) {
      if (alertSettings[alertType].emails.includes(email)) {
        // Show duplicate alert modal
        setAlertModal({
          isOpen: true,
          title: t('admin.modal.duplicateEmail.title'),
          message: t('admin.modal.duplicateEmail.message'),
          type: 'warning'
        });
        return;
      }
      
      setAlertSettings(prev => ({
        ...prev,
        [alertType]: {
          ...prev[alertType],
          emails: [...prev[alertType].emails, email]
        }
      }));
      setEmail('');
      setHasUnsavedChanges(true);
    }
  };
  
  const removeEmail = (alertType: 'emailConfirmedTrades' | 'emailDisputedTrades', email: string) => {
    setAlertSettings(prev => ({
      ...prev,
      [alertType]: {
        ...prev[alertType],
        emails: prev[alertType].emails.filter((e: string) => e !== email)
      }
    }));
    setHasUnsavedChanges(true);
  };
  
  const addPhone = (alertType: 'smsConfirmedTrades' | 'smsDisputedTrades') => {
    const phone = alertType === 'smsConfirmedTrades' ? newPhoneConfirmed : newPhoneDisputed;
    const setPhone = alertType === 'smsConfirmedTrades' ? setNewPhoneConfirmed : setNewPhoneDisputed;
    
    if (phone && phone.startsWith('+')) {
      if (alertSettings[alertType].phones.includes(phone)) {
        // Show duplicate alert modal
        setAlertModal({
          isOpen: true,
          title: t('admin.modal.duplicatePhone.title'),
          message: t('admin.modal.duplicatePhone.message'),
          type: 'warning'
        });
        return;
      }
      
      setAlertSettings(prev => ({
        ...prev,
        [alertType]: {
          ...prev[alertType],
          phones: [...prev[alertType].phones, phone]
        }
      }));
      setPhone('');
      setHasUnsavedChanges(true);
    }
  };
  
  const removePhone = (alertType: 'smsConfirmedTrades' | 'smsDisputedTrades', phone: string) => {
    setAlertSettings(prev => ({
      ...prev,
      [alertType]: {
        ...prev[alertType],
        phones: prev[alertType].phones.filter((p: string) => p !== phone)
      }
    }));
    setHasUnsavedChanges(true);
  };

  const closeModal = () => {
    setAlertModal(prev => ({ ...prev, isOpen: false }));
  };

  // Settlement Rules functions
  const handleAddRule = () => {
    setEditingRule(null);
    setRuleForm({
      active: true,
      priority: settlementRules.length + 1,
      name: '',
      counterparty: '',
      product: '',
      direction: '',
      modalidad: '',
      settlementCurrency: '',
      cargarCurrency: '',
      cargarBankName: '',
      cargarSwiftCode: '',
      cargarAccountNumber: '',
      abonarCurrency: '',
      abonarBankName: '',
      abonarSwiftCode: '',
      abonarAccountNumber: ''
    });
    setShowRuleForm(true);
    setHasUnsavedChanges(true);
  };

  // Check for duplicate settlement rule
  const isDuplicateRule = (rule: Partial<SettlementRule>, excludeId?: string): boolean => {
    return settlementRules.some(existingRule => {
      if (excludeId && existingRule.id === excludeId) return false;
      return (
        existingRule.counterparty === rule.counterparty &&
        existingRule.direction === rule.direction &&
        existingRule.product === rule.product &&
        existingRule.modalidad === rule.modalidad &&
        existingRule.cargarCurrency === rule.cargarCurrency &&
        existingRule.abonarCurrency === rule.abonarCurrency
      );
    });
  };

  const handleEditRule = (rule: SettlementRule) => {
    setEditingRule(rule);
    setRuleForm({ ...rule });
    setShowRuleForm(true);
  };

  const handleDeleteRule = (ruleId: string) => {
    setSettlementRules(prev => prev.filter(rule => rule.id !== ruleId));
    setHasUnsavedChanges(true);
  };

  // Find next available priority
  const getNextAvailablePriority = (excludeId?: string) => {
    const existingPriorities = settlementRules
      .filter(rule => rule.id !== excludeId)
      .map(rule => rule.priority)
      .sort((a, b) => a - b);
    
    for (let i = 1; i <= existingPriorities.length + 1; i++) {
      if (!existingPriorities.includes(i)) {
        return i;
      }
    }
    return existingPriorities.length + 1;
  };

  const handleSaveRule = async () => {
    // Prevent double-clicking
    if (isSavingRule) return;
    
    setIsSavingRule(true);
    
    try {
      // Validate required fields
      if (!ruleForm.name || !ruleForm.direction || !ruleForm.product || !ruleForm.modalidad ||
          !ruleForm.cargarCurrency || !ruleForm.cargarBankName || !ruleForm.cargarAccountNumber ||
          !ruleForm.abonarCurrency || !ruleForm.abonarBankName || !ruleForm.abonarAccountNumber ||
          (ruleForm.modalidad === 'compensacion' && !ruleForm.settlementCurrency)) {
        setAlertModal({
          isOpen: true,
          title: 'Validation Error',
          message: ruleForm.modalidad === 'compensacion' && !ruleForm.settlementCurrency
            ? 'Please fill in all required fields including Settlement Currency for Compensación.'
            : 'Please fill in all required fields (Rule Name, Direction, Product, Modalidad, Cargar Currency/Bank/Account, Abonar Currency/Bank/Account).',
          type: 'warning'
        });
        return;
      }

      // Check for duplicate priority
      const existingPriorities = settlementRules
        .filter(rule => rule.id !== editingRule?.id)
        .map(rule => rule.priority);
      
      if (existingPriorities.includes(ruleForm.priority || 1)) {
        const nextAvailable = getNextAvailablePriority(editingRule?.id);
        setAlertModal({
          isOpen: true,
          title: 'Duplicate Priority',
          message: `Priority ${ruleForm.priority} is already in use. Would you like to use Priority ${nextAvailable} instead?`,
          type: 'warning'
        });
        // Auto-suggest the next available priority
        updateRuleForm('priority', nextAvailable);
        return;
      }

      // Check for duplicate rule
      if (isDuplicateRule(ruleForm, editingRule?.id)) {
        setAlertModal({
          isOpen: true,
          title: 'Duplicate Rule',
          message: 'A rule with the same configuration already exists. Please modify the rule to avoid duplicates.',
          type: 'warning'
        });
        return;
      }

      if (!user?.profile?.organization?.id) {
        setAlertModal({
          isOpen: true,
          title: 'Error',
          message: 'No organization ID found',
          type: 'error'
        });
        return;
      }

      const ruleData = {
        name: ruleForm.name!,
        direction: ruleForm.direction || '',
        counterparty: ruleForm.counterparty || '',
        product: ruleForm.product || '',
        modalidad: ruleForm.modalidad || '',
        settlementCurrency: ruleForm.modalidad === 'entregaFisica' ? undefined : (ruleForm.settlementCurrency || undefined),
        priority: ruleForm.priority || 1,
        cargarCurrency: ruleForm.cargarCurrency || '',
        cargarBankName: ruleForm.cargarBankName || '',
        cargarSwiftCode: ruleForm.cargarSwiftCode || '',
        cargarAccountNumber: ruleForm.cargarAccountNumber || '',
        abonarCurrency: ruleForm.abonarCurrency || '',
        abonarBankName: ruleForm.abonarBankName || '',
        abonarSwiftCode: ruleForm.abonarSwiftCode || '',
        abonarAccountNumber: ruleForm.abonarAccountNumber || '',
        centralBankTradeCode: ruleForm.centralBankTradeCode || undefined
      };

      if (editingRule && editingRule.id) {
        // Update existing rule
        const response = await clientService.updateSettlementRule(user.profile.organization.id, editingRule.id, ruleData);
        if (response.success) {
          setSettlementRules(prev => prev.map(rule => 
            rule.id === editingRule.id ? { ...ruleForm as SettlementRule } : rule
          ));
        }
      } else {
        // Add new rule
        const response = await clientService.createSettlementRule(user.profile.organization.id, ruleData);
        if (response.success && response.data) {
          const newRule: SettlementRule = {
            ...ruleForm as SettlementRule,
            id: response.data.id || Date.now().toString()
          };
          setSettlementRules(prev => [...prev, newRule]);
        }
      }
      setShowRuleForm(false);
      setRuleForm({});
      setEditingRule(null);
    } catch (error) {
      setAlertModal({
        isOpen: true,
        title: 'Save Error',
        message: error instanceof Error ? error.message : 'Failed to save settlement rule',
        type: 'error'
      });
    } finally {
      setIsSavingRule(false);
    }
  };

  const handleCancelRule = () => {
    setShowRuleForm(false);
    setRuleForm({});
    setEditingRule(null);
  };

  const updateRuleForm = (field: keyof SettlementRule, value: any) => {
    setRuleForm(prev => ({ ...prev, [field]: value }));
    setHasUnsavedChanges(true);
  };

  // Account management functions
  const handleAddAccount = () => {
    const newAccount: BankAccount = {
      id: 'NEW_ACCOUNT', // Special marker for new accounts
      active: true,
      accountName: '',
      bankName: '',
      swiftCode: '',
      accountCurrency: '',
      accountNumber: '',
      isDefault: false
    };
    setBankAccounts(prev => [...prev, newAccount]);
    setEditingAccount(newAccount.id);
    setAccountForm({ ...newAccount });
    setHasUnsavedChanges(true);
  };

  const handleEditAccount = (account: BankAccount) => {
    setEditingAccount(account.id);
    setAccountForm({ ...account });
  };

  const handleSaveAccount = async () => {
    // Prevent double-clicking
    if (isSavingAccount) return;
    
    setIsSavingAccount(true);
    
    try {
      if (!accountForm.accountName || !accountForm.bankName || !accountForm.swiftCode || 
          !accountForm.accountCurrency || !accountForm.accountNumber) {
        setAlertModal({
          isOpen: true,
          title: 'Validation Error',
          message: 'Please fill in all required fields.',
          type: 'warning'
        });
        return;
      }

      if (!user?.profile?.organization?.id) {
        setAlertModal({
          isOpen: true,
          title: 'Error',
          message: 'No organization ID found',
          type: 'error'
        });
        return;
      }

      if (editingAccount === 'NEW_ACCOUNT') {
        // Create new account
        const response = await clientService.createBankAccount(user.profile.organization.id, {
          accountName: accountForm.accountName!,
          bankName: accountForm.bankName!,
          swiftCode: accountForm.swiftCode!,
          accountCurrency: accountForm.accountCurrency!,
          accountNumber: accountForm.accountNumber!,
          isDefault: accountForm.isDefault ?? false
        });

        if (response.success && response.data) {
          // Replace the temporary account with the saved account (with server-generated id)
          setBankAccounts(prev => prev.map(account => 
            account.id === 'NEW_ACCOUNT' ? response.data as BankAccount : account
          ));
        }
      } else if (editingAccount) {
        // Update existing account
        const response = await clientService.updateBankAccount(user.profile.organization.id, editingAccount, {
          accountName: accountForm.accountName!,
          bankName: accountForm.bankName!,
          swiftCode: accountForm.swiftCode!,
          accountCurrency: accountForm.accountCurrency!,
          accountNumber: accountForm.accountNumber!,
          active: accountForm.active ?? true,
          isDefault: accountForm.isDefault ?? false
        });

        if (response.success) {
          setBankAccounts(prev => prev.map(account => 
            account.id === editingAccount ? { ...accountForm as BankAccount } : account
          ));
        }
      }

      setEditingAccount(null);
      setAccountForm({});
    } catch (error) {
      setAlertModal({
        isOpen: true,
        title: 'Save Error',
        message: error instanceof Error ? error.message : 'Failed to save bank account',
        type: 'error'
      });
    } finally {
      setIsSavingAccount(false);
    }
  };

  const handleCancelAccount = () => {
    if (editingAccount === 'NEW_ACCOUNT') {
      // Remove new empty account if cancelled
      setBankAccounts(prev => prev.filter(acc => acc.id !== 'NEW_ACCOUNT'));
    }
    setEditingAccount(null);
    setAccountForm({});
  };

  const handleDeleteAccount = (accountId: string) => {
    setBankAccounts(prev => prev.filter(account => account.id !== accountId));
    if (editingAccount === accountId) {
      setEditingAccount(null);
      setAccountForm({});
    }
    setHasUnsavedChanges(true);
  };

  const updateAccountForm = (field: keyof BankAccount, value: any) => {
    setAccountForm(prev => ({ ...prev, [field]: value }));
    setHasUnsavedChanges(true);
  };

  // Get accounts filtered by bank and currency for settlement rule form
  // Only show accounts where account currency matches cashflow currency
  const getAvailableAccounts = (bankName?: string, accountCurrency?: string, cashflowCurrency?: string) => {
    return bankAccounts.filter(account => 
      account.active && 
      (!bankName || account.bankName === bankName) &&
      (!accountCurrency || account.accountCurrency === accountCurrency) &&
      (!cashflowCurrency || account.accountCurrency === cashflowCurrency)
    );
  };

  // Sort and group settlement rules with true global priority
  const getSortedAndGroupedRules = () => {
    // Sort by active status first, then by priority (global priority order)
    const sorted = [...settlementRules].sort((a, b) => {
      // First by active status (active first)
      if (a.active !== b.active) return a.active ? -1 : 1;
      // Then by priority (global across all rules)
      return a.priority - b.priority;
    });

    // Build ordered list maintaining priority sequence but marking counterparty groups
    const orderedRules: Array<{ type: 'rule' | 'header'; data: SettlementRule | string }> = [];
    let currentCounterparty: string | null = null;
    let hasShownGenericHeader = false;

    sorted.forEach(rule => {
      const ruleCounterparty = rule.counterparty && rule.counterparty.trim() !== '' ? rule.counterparty : null;
      
      // Handle generic rules (no counterparty)
      if (!ruleCounterparty) {
        if (!hasShownGenericHeader) {
          orderedRules.push({ type: 'header', data: 'Not Counterparty Specific' });
          hasShownGenericHeader = true;
        }
        orderedRules.push({ type: 'rule', data: rule });
      }
      // Handle counterparty-specific rules
      else {
        if (currentCounterparty !== ruleCounterparty) {
          orderedRules.push({ type: 'header', data: ruleCounterparty });
          currentCounterparty = ruleCounterparty;
        }
        orderedRules.push({ type: 'rule', data: rule });
      }
    });

    return orderedRules;
  };

  // Helper function to group and sort bank accounts
  const getSortedAndGroupedAccounts = () => {
    if (accountGrouping === 'none') {
      // Sort by active status first, then by account name
      const sorted = [...bankAccounts].sort((a, b) => {
        // First by active status (active first)
        if (a.active !== b.active) return a.active ? -1 : 1;
        // Then by account name
        return a.accountName.localeCompare(b.accountName);
      });
      return sorted.map(account => ({ type: 'account' as const, data: account }));
    }

    // Group accounts by the selected criteria
    const groupKey = accountGrouping === 'bank' ? 'bankName' : 'accountCurrency';
    const grouped = bankAccounts.reduce((groups, account) => {
      const key = account[groupKey];
      // Skip accounts with empty/null/undefined group keys
      if (!key || key.trim() === '') {
        return groups;
      }
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(account);
      return groups;
    }, {} as Record<string, BankAccount[]>);

    // Sort accounts within each group
    Object.keys(grouped).forEach(key => {
      grouped[key].sort((a, b) => {
        // First by active status (active first)
        if (a.active !== b.active) return a.active ? -1 : 1;
        // Then by account name
        return a.accountName.localeCompare(b.accountName);
      });
    });

    // Build ordered list with proper grouping
    const orderedAccounts: Array<{ type: 'account' | 'header'; data: BankAccount | string }> = [];
    
    // Sort group keys and filter out empty groups
    const sortedGroupKeys = Object.keys(grouped)
      .filter(key => grouped[key].length > 0) // Only include groups with accounts
      .sort();
    
    sortedGroupKeys.forEach(groupName => {
      // Add header for this group
      orderedAccounts.push({ type: 'header', data: groupName });
      
      // Add all accounts in this group
      grouped[groupName].forEach(account => {
        orderedAccounts.push({ type: 'account', data: account });
      });
    });

    return orderedAccounts;
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, ruleId: string) => {
    setDraggedRule(ruleId);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', ruleId);
    
    // Add visual feedback to the dragged element
    const target = e.target as HTMLElement;
    target.style.opacity = '0.5';
  };

  const handleDragOver = (e: React.DragEvent, ruleId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    
    // Only set drag over if it's different from the dragged rule
    if (draggedRule !== ruleId) {
      setDragOverRule(ruleId);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    // Only clear drag over if we're leaving the entire row, not just a child element
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      setDragOverRule(null);
    }
  };

  const handleDragEnd = (e: React.DragEvent) => {
    // Reset visual feedback
    const target = e.target as HTMLElement;
    target.style.opacity = '1';
    setDraggedRule(null);
    setDragOverRule(null);
  };

  const handleDrop = (e: React.DragEvent, targetRuleId: string) => {
    e.preventDefault();
    
    if (!draggedRule || draggedRule === targetRuleId) {
      setDraggedRule(null);
      setDragOverRule(null);
      return;
    }

    const draggedRuleData = settlementRules.find(r => r.id === draggedRule);
    const targetRuleData = settlementRules.find(r => r.id === targetRuleId);
    
    if (!draggedRuleData || !targetRuleData) {
      setDraggedRule(null);
      setDragOverRule(null);
      return;
    }

    // Calculate new priority order (frontend-only)
    const sortedRules = [...settlementRules].sort((a, b) => a.priority - b.priority);
    const draggedIndex = sortedRules.findIndex(r => r.id === draggedRule);
    const targetIndex = sortedRules.findIndex(r => r.id === targetRuleId);
    
    // If dragging to the same position, no change needed
    if (draggedIndex === targetIndex) {
      setDraggedRule(null);
      setDragOverRule(null);
      return;
    }
    
    // Remove dragged rule from its current position
    const ruleToMove = sortedRules[draggedIndex];
    sortedRules.splice(draggedIndex, 1);
    
    // Insert at target position (adjust target index if we removed an item before it)
    const adjustedTargetIndex = draggedIndex < targetIndex ? targetIndex - 1 : targetIndex;
    sortedRules.splice(adjustedTargetIndex, 0, ruleToMove);
    
    // Reassign priorities based on new order
    const updatedRules = sortedRules.map((rule, index) => ({
      ...rule,
      priority: index + 1
    }));
    
    // Update local state immediately (no backend call)
    setSettlementRules(updatedRules);
    setHasUnsavedChanges(true);
    
    setDraggedRule(null);
    setDragOverRule(null);
  };

  const saveConfiguration = async () => {
    if (!user?.profile?.organization?.id) {
      setAlertModal({
        isOpen: true,
        title: 'Error',
        message: 'No organization ID found',
        type: 'error'
      });
      return;
    }

    setIsSaving(true);
    
    try {
      // Save client settings (automation and alerts)
      await clientService.updateClientSettings(user.profile.organization.id, {
        automation: automationSettings,
        alerts: alertSettings
      });
      
      // Save settlement rule priorities - update ALL rules to ensure correct priorities
      if (settlementRules.length > 0 && user?.profile?.organization?.id) {
        const updatePromises = settlementRules
          .filter(rule => !rule.id.startsWith('temp-rule-')) // Only update rules with real or generated IDs
          .map(rule => {
            // If using a generated ID, we need to find the rule by its properties instead
            if (rule.id.startsWith('rule-') && rule.id.includes('-')) {
              // This is a generated ID, try to update by matching properties
              // For now, let's try using the generated ID - the backend should handle this
              return clientService.updateSettlementRule(
                user.profile!.organization!.id, 
                rule.id, 
                { priority: rule.priority }
              );
            }
            
            return clientService.updateSettlementRule(
              user.profile!.organization!.id, 
              rule.id, 
              { priority: rule.priority }
            );
          });

        if (updatePromises.length > 0) {
          const updateResults = await Promise.all(updatePromises);
          const failedUpdates = updateResults.filter(result => !result.success);
          
          if (failedUpdates.length > 0) {
            // Some settlement rule priority updates failed
          } else {
            // Successfully updated priorities for all settlement rules
          }
        } else {
          // No settlement rules with real IDs found to update
        }
      }
      
      setAlertModal({
        isOpen: true,
        title: t('admin.modal.saveSuccess.title'),
        message: t('admin.modal.saveSuccess.message'),
        type: 'success'
      });
      
      // Reset unsaved changes flag and update original values after successful save
      setHasUnsavedChanges(false);
      setOriginalAutomationSettings({ ...automationSettings });
      setOriginalAlertSettings({ ...alertSettings });
      setOriginalBankAccounts([...bankAccounts]);
      setOriginalSettlementRules([...settlementRules]);
    } catch (error) {
      console.error('Save failed:', error);
      setAlertModal({
        isOpen: true,
        title: t('admin.modal.error.title'),
        message: 'Failed to save configuration. Please try again.',
        type: 'error'
      });
    } finally {
      setIsSaving(false);
    }
  };

  // Unsaved changes handlers
  const handleTabChange = (newTab: 'automation' | 'alerts' | 'settlement' | 'accounts' | 'mapping') => {
    if (hasUnsavedChanges) {
      setPendingTabChange(newTab);
      setShowUnsavedChangesModal(true);
    } else {
      setActiveTab(newTab);
    }
  };

  const handleSaveAndContinue = async () => {
    await saveConfiguration();
    if (pendingTabChange) {
      setActiveTab(pendingTabChange as any);
      setPendingTabChange(null);
    }
    setShowUnsavedChangesModal(false);
    setHasUnsavedChanges(false);
  };

  const handleDiscardAndContinue = () => {
    // Reset all form data to original values
    if (originalAutomationSettings) {
      setAutomationSettings({ ...originalAutomationSettings });
    }
    if (originalAlertSettings) {
      setAlertSettings({ ...originalAlertSettings });
    }
    if (originalBankAccounts) {
      setBankAccounts([...originalBankAccounts]);
      // Reset editing state if user was editing an account
      setEditingAccount(null);
      setAccountForm({});
    }
    if (originalSettlementRules) {
      setSettlementRules([...originalSettlementRules]);
      // Reset editing state if user was editing a rule
      setEditingRule(null);
      setRuleForm({});
      setShowRuleForm(false);
    }
    
    // Navigate to pending tab
    if (pendingTabChange) {
      setActiveTab(pendingTabChange as any);
      setPendingTabChange(null);
    }
    
    // Reset modal state
    setShowUnsavedChangesModal(false);
    setHasUnsavedChanges(false);
  };

  const handleCancelNavigation = () => {
    setPendingTabChange(null);
    setShowUnsavedChangesModal(false);
  };

  // Data Mapping functions
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processUploadedFile(file);
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOverUpload(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      processUploadedFile(file);
    }
  };

  const processUploadedFile = (file: File) => {
    setUploadedFile(file);
    
    let extractedFields: string[] = [];
    let parsedData: any[] = [];
    
    if (file.name.toLowerCase().endsWith('.csv')) {
      // Parse CSV file
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        const lines = text.split('\n').filter(line => line.trim());
        if (lines.length > 0) {
          // Extract headers from first line
          extractedFields = lines[0].split(',').map(field => field.trim().replace(/"/g, ''));
          
          // Parse first few rows for sample data
          for (let i = 1; i < Math.min(lines.length, 4); i++) {
            const values = lines[i].split(',').map(val => val.trim().replace(/"/g, ''));
            const row: any = {};
            extractedFields.forEach((field, index) => {
              row[field] = values[index] || '';
            });
            parsedData.push(row);
          }
        }
        updateFileData(extractedFields, parsedData, file);
      };
      reader.readAsText(file);
      
    } else if (file.name.toLowerCase().endsWith('.json')) {
      // Parse JSON file
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        try {
          const jsonData = JSON.parse(text);
          if (Array.isArray(jsonData) && jsonData.length > 0) {
            extractedFields = Object.keys(jsonData[0]);
            parsedData = jsonData.slice(0, 3);
          }
        } catch (error) {
          console.error('Error parsing JSON:', error);
        }
        updateFileData(extractedFields, parsedData, file);
      };
      reader.readAsText(file);
      
    } else if (file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
      // Parse Excel file using xlsx library
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target?.result;
          const workbook = XLSX.read(data, { type: 'binary' });
          
          // Get the first worksheet
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          
          // Convert to JSON
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          
          // Helper function to convert Excel date serial numbers to readable dates
          const convertExcelValue = (value: any, fieldName: string) => {
            // Only try to convert numbers that are likely to be dates based on field name
            const isLikelyDateField = fieldName && (
              fieldName.toLowerCase().includes('date') ||
              fieldName.toLowerCase().includes('maturity') ||
              fieldName.toLowerCase().includes('payment') ||
              fieldName.toLowerCase().includes('settlement') ||
              fieldName.toLowerCase().includes('fixing') ||
              fieldName.toLowerCase().includes('expiry') ||
              fieldName.toLowerCase().includes('value')
            );
            
            // Check if it's a number that could be an Excel date serial number
            if (isLikelyDateField && typeof value === 'number' && value > 25000 && value < 80000) {
              // Narrower range: 25000 ≈ 1968, 80000 ≈ 2119 (more realistic date range)
              try {
                // Excel stores dates as days since 1900-01-01 (with 1900 leap year bug)
                // Convert Excel serial number to JavaScript Date
                const excelEpoch = new Date(1899, 11, 30); // December 30, 1899 (accounting for Excel's leap year bug)
                const jsDate = new Date(excelEpoch.getTime() + (value * 24 * 60 * 60 * 1000));
                
                // Validate the date and check if it's reasonable
                if (jsDate && !isNaN(jsDate.getTime()) && jsDate.getFullYear() > 1968 && jsDate.getFullYear() < 2119) {
                  // Format as YYYY-MM-DD for consistency
                  return jsDate.toISOString().split('T')[0];
                }
              } catch (error) {
                // Date conversion failed
              }
            }
            // Return original value if not a date serial number or not a date field
            return value || '';
          };
          
          if (jsonData.length > 0) {
            // First row contains headers
            extractedFields = (jsonData[0] as any[]).map(header => String(header || '').trim());
            
            // Convert remaining rows to objects
            for (let i = 1; i < Math.min(jsonData.length, 4); i++) {
              const rowData = jsonData[i] as any[];
              const row: any = {};
              extractedFields.forEach((field, index) => {
                row[field] = convertExcelValue(rowData[index], field);
              });
              parsedData.push(row);
            }
          }
        } catch (error) {
          console.error('Error parsing Excel file:', error);
        }
        updateFileData(extractedFields, parsedData, file);
      };
      reader.readAsBinaryString(file);
      
    } else {
      console.warn('Unsupported file format:', file.name);
      updateFileData([], [], file);
    }
  };

  const updateFileData = (extractedFields: string[], parsedData: any[], file: File) => {
    setSourceFields(extractedFields);
    setUploadedData(parsedData);
    
    // Generate intelligent mapping suggestions based on actual field names
    if (extractedFields.length > 0) {
      const suggestedMapping = generateIntelligentMapping(extractedFields);
      setCurrentMapping(suggestedMapping);
      
      // Apply mapping to generate preview
      if (parsedData.length > 0) {
        const mapped = applyMapping(parsedData, suggestedMapping);
        setMappedData(mapped);
      }
    }
  };

  const generateMockData = (filename: string) => {
    // Mock data based on filename to simulate different client formats with comprehensive field set
    if (filename.toLowerCase().includes('bank')) {
      return [
        { 
          'ID_TRADE': 'T001', 'FECHA_TRADE': '15/01/2025', 'FECHA_VALOR': '17/01/2025', 'CONTRAPARTE': 'BANCO ABC', 
          'PRODUCTO': 'SPOT', 'COMPRA_VENTA': 'C', 'MONEDA1': 'USD', 'MONEDA2': 'CLP', 'MONTO': '100.000,50', 
          'TASA': '920,45', 'FECHA_PAGO': '17/01/2025', 'TIPO_LIQUIDACION': 'DVP', 'REFERENCIA': 'REF001',
          'COMENTARIOS': 'Trade normal', 'ESTADO': 'ACTIVO', 'USUARIO': 'admin', 'SISTEMA': 'CORE'
        },
        { 
          'ID_TRADE': 'T002', 'FECHA_TRADE': '16/01/2025', 'FECHA_VALOR': '18/01/2025', 'CONTRAPARTE': 'BANCO XYZ', 
          'PRODUCTO': 'FORWARD', 'COMPRA_VENTA': 'V', 'MONEDA1': 'EUR', 'MONEDA2': 'USD', 'MONTO': '50.000,00', 
          'TASA': '1,0856', 'FECHA_PAGO': '18/01/2025', 'TIPO_LIQUIDACION': 'NET', 'REFERENCIA': 'REF002',
          'COMENTARIOS': 'Forward EUR/USD', 'ESTADO': 'PENDIENTE', 'USUARIO': 'trader1', 'SISTEMA': 'FRONT'
        }
      ];
    }
    return [
      { 
        'TradeID': 'TR1001', 'TradeDate': '2025-01-15', 'ValueDate': '2025-01-17', 'Counterparty': 'Bank ABC', 
        'Product': 'FX SPOT', 'Ccy1': 'USD', 'Ccy2': 'CLP', 'Amount': '100000.50', 
        'Rate': '920.45', 'PaymentDate': '2025-01-17', 'SettlementType': 'DVP', 'Reference': 'REF001',
        'Comments': 'Standard trade', 'Status': 'ACTIVE', 'User': 'admin', 'Source': 'SYSTEM_A'
      },
      { 
        'TradeID': 'TR1002', 'TradeDate': '2025-01-16', 'ValueDate': '2025-01-18', 'Counterparty': 'Bank XYZ', 
        'Product': 'FX FORWARD', 'Ccy1': 'EUR', 'Ccy2': 'USD', 'Amount': '50000.00', 
        'Rate': '1.0856', 'PaymentDate': '2025-01-18', 'SettlementType': 'NET', 'Reference': 'REF002',
        'Comments': 'Forward EUR/USD', 'Status': 'PENDING', 'User': 'trader1', 'Source': 'SYSTEM_B'
      }
    ];
  };

  const generateIntelligentMapping = (sourceFields: string[]): FieldMapping[] => {
    const mappings: FieldMapping[] = [];
    
    sourceFields.forEach(sourceField => {
      const lowerField = sourceField.toLowerCase();
      
      // Intelligent field matching for ClientTradesGrid fields
      if (lowerField.includes('trade') && lowerField.includes('id') || lowerField === 'id_trade' || lowerField === 'tradeid') {
        mappings.push({ sourceField, targetField: 'tradeId', transformation: { type: 'direct' } });
      }
      else if (lowerField.includes('contraparte') || lowerField === 'counterparty') {
        mappings.push({ sourceField, targetField: 'counterparty', transformation: { type: 'direct' } });
      }
      else if (lowerField.includes('producto') || lowerField.includes('product type') || lowerField === 'producttype' || lowerField === 'product') {
        mappings.push({ sourceField, targetField: 'productType', transformation: { type: 'enum', params: { mapping: { 
          'SPOT': 'FX Spot', 
          'FORWARD': 'FX Forward', 
          'Forward': 'FX Forward',
          'forward': 'FX Forward',
          'FX SPOT': 'FX Spot', 
          'FX FORWARD': 'FX Forward', 
          'SWAP': 'FX Swap', 
          'OPTION': 'FX Option' 
        } } } });
      }
      else if (lowerField.includes('fecha') && lowerField.includes('trade') || lowerField === 'tradedate') {
        mappings.push({ sourceField, targetField: 'tradeDate', transformation: { type: 'format', params: { from: 'auto', to: 'YYYY-MM-DD' } } });
      }
      else if (lowerField.includes('valor') || lowerField.includes('value date') || lowerField === 'valuedate') {
        mappings.push({ sourceField, targetField: 'valueDate', transformation: { type: 'format', params: { from: 'auto', to: 'YYYY-MM-DD' } } });
      }
      else if (lowerField.includes('moneda1') || lowerField === 'ccy1' || lowerField === 'currency1' || lowerField.includes('currency 1')) {
        mappings.push({ sourceField, targetField: 'currency1', transformation: { type: 'enum', params: { mapping: { 
          'US$': 'USD',
          'USD': 'USD',
          '$': 'CLP',
          'CLP': 'CLP',
          'UF': 'CLF',
          'CLF': 'CLF',
          'EUR': 'EUR',
          '€': 'EUR',
          'GBP': 'GBP',
          '£': 'GBP'
        } } } });
      }
      else if (lowerField.includes('moneda2') || lowerField === 'ccy2' || lowerField === 'currency2' || lowerField.includes('currency 2')) {
        mappings.push({ sourceField, targetField: 'currency2', transformation: { type: 'enum', params: { mapping: { 
          'US$': 'USD',
          'USD': 'USD',
          '$': 'CLP',
          'CLP': 'CLP',
          'UF': 'CLF',
          'CLF': 'CLF',
          'EUR': 'EUR',
          '€': 'EUR',
          'GBP': 'GBP',
          '£': 'GBP'
        } } } });
      }
      else if (lowerField.includes('monto') || lowerField === 'amount') {
        mappings.push({ sourceField, targetField: 'amount', transformation: { type: 'format', params: { decimalSeparator: 'auto' } } });
      }
      else if (lowerField.includes('precio') || lowerField.includes('price') || lowerField.includes('tasa') || lowerField.includes('rate')) {
        mappings.push({ sourceField, targetField: 'price', transformation: { type: 'format', params: { decimalSeparator: 'auto', precision: 4 } } });
      }
      else if (lowerField.includes('pago') || lowerField === 'paymentdate' || (lowerField.includes('payment') && lowerField.includes('date'))) {
        mappings.push({ sourceField, targetField: 'paymentDate', transformation: { type: 'format', params: { from: 'auto', to: 'YYYY-MM-DD' } } });
      }
    });
    
    return mappings;
  };

  // Helper function to get suggested source field for each expected field
  const getSuggestedSourceField = (expectedFieldName: string): string => {
    const mapping = currentMapping.find(m => m.targetField === expectedFieldName);
    return mapping ? mapping.sourceField : 'No suggestion';
  };

  const applyMapping = (data: any[], mappings: FieldMapping[]) => {
    return data.map(row => {
      const mappedRow: any = {};
      
      mappings.forEach(mapping => {
        const sourceValue = row[mapping.sourceField];
        let targetValue = sourceValue;
        
        if (mapping.transformation) {
          switch (mapping.transformation.type) {
            case 'format':
              if (mapping.transformation.params?.decimalSeparator) {
                targetValue = sourceValue?.toString().replace(',', '.');
              }
              if (mapping.transformation.params?.from && mapping.transformation.params?.to) {
                // Date format conversion
                if (mapping.transformation.params.from === 'DD/MM/YYYY') {
                  const parts = sourceValue?.split('/');
                  if (parts?.length === 3) {
                    targetValue = `${parts[0]}${parts[1]}${parts[2]}`;
                  }
                }
              }
              break;
            case 'enum':
              const enumMapping = mapping.transformation.params?.mapping;
              if (enumMapping && enumMapping[sourceValue]) {
                targetValue = enumMapping[sourceValue];
              }
              break;
            case 'direct':
            default:
              targetValue = sourceValue;
          }
        }
        
        mappedRow[mapping.targetField] = targetValue;
      });
      
      return mappedRow;
    });
  };

  const updateMapping = (sourceField: string, targetField: string) => {
    setCurrentMapping(prev => {
      const updated = prev.filter(m => m.sourceField !== sourceField);
      if (targetField && targetField !== 'unmapped') {
        updated.push({ sourceField, targetField, transformation: { type: 'direct' } });
      }
      return updated;
    });
    
    // Reapply mapping to update preview
    if (uploadedData) {
      const newMapping = currentMapping.filter(m => m.sourceField !== sourceField);
      if (targetField && targetField !== 'unmapped') {
        newMapping.push({ sourceField, targetField, transformation: { type: 'direct' } });
      }
      const mapped = applyMapping(uploadedData, newMapping);
      setMappedData(mapped);
    }
  };

  const updateMappingByTarget = (targetField: string, sourceField: string) => {
    setCurrentMapping(prev => {
      // Remove any existing mapping for this target field
      const updated = prev.filter(m => m.targetField !== targetField);
      
      if (sourceField && sourceField !== 'unmapped') {
        // Also remove any mapping that was using this source field for a different target
        const finalUpdated = updated.filter(m => m.sourceField !== sourceField);
        
        // Find intelligent transformation for this mapping
        const transformation = getTransformationForField(sourceField, targetField);
        finalUpdated.push({ sourceField, targetField, transformation });
        
        return finalUpdated;
      }
      return updated;
    });
    
    // Reapply mapping to update preview
    if (uploadedData) {
      setTimeout(() => {
        const mapped = applyMapping(uploadedData, currentMapping);
        setMappedData(mapped);
      }, 0);
    }
  };

  const getTransformationForField = (sourceField: string, targetField: string) => {
    const lowerSourceField = sourceField.toLowerCase();
    
    // Date transformation
    if (targetField === 'tradeDate' || targetField === 'valueDate' || targetField === 'maturityDate') {
      const hasSlash = lowerSourceField.includes('/') || (uploadedData?.[0]?.[sourceField] && String(uploadedData[0][sourceField]).includes('/'));
      return { 
        type: 'format' as const, 
        params: hasSlash ? { from: 'DD/MM/YYYY', to: 'DDMMYYYY' } : { from: 'YYYY-MM-DD', to: 'DDMMYYYY' }
      };
    }
    
    // Amount/Rate transformation
    if (targetField === 'amount' || targetField === 'rate') {
      const hasComma = lowerSourceField.includes(',') || (uploadedData?.[0]?.[sourceField] && String(uploadedData[0][sourceField]).includes(','));
      return { 
        type: 'format' as const, 
        params: hasComma ? { decimalSeparator: ',' } : { decimalSeparator: '.' }
      };
    }
    
    // Enum transformations
    if (targetField === 'product') {
      return { type: 'enum' as const, params: { mapping: { 'SPOT': 'FX SPOT', 'FORWARD': 'FX FORWARD', 'SWAP': 'FX SWAP' } } };
    }
    
    if (targetField === 'buySell') {
      return { type: 'enum' as const, params: { mapping: { 'C': 'BUY', 'V': 'SELL', 'BUY': 'BUY', 'SELL': 'SELL' } } };
    }
    
    // Direct mapping for everything else
    return { type: 'direct' as const };
  };

  const saveMapping = () => {
    if (!mappingForm.name || !uploadedFile) return;
    
    const newMapping: DataMapping = {
      id: Date.now().toString(),
      name: mappingForm.name,
      description: mappingForm.description,
      fileType: uploadedFile.name.endsWith('.json') ? 'json' : uploadedFile.name.endsWith('.xlsx') ? 'excel' : 'csv',
      createdDate: new Date().toISOString().split('T')[0],
      fieldMappings: currentMapping,
      sampleData: mappedData?.slice(0, 3)
    };
    
    setDataMappings(prev => [...prev, newMapping]);
    setShowMappingForm(false);
    setMappingForm({name: '', description: ''});
    
    setAlertModal({
      isOpen: true,
      title: t('admin.dataMapping.saveMapping.successTitle'),
      message: t('admin.dataMapping.saveMapping.successMessage').replace('{name}', newMapping.name),
      type: 'success'
    });
  };

  const deleteMapping = (mappingId: string) => {
    setDataMappings(prev => prev.filter(m => m.id !== mappingId));
  };

  const clearUpload = () => {
    setUploadedFile(null);
    setUploadedData(null);
    setSourceFields([]);
    setCurrentMapping([]);
    setMappedData(null);
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-tabs">
        <button 
          className={`tab-button ${activeTab === 'automation' ? 'active' : ''}`}
          onClick={() => handleTabChange('automation')}
        >
          {t('admin.tabs.automation')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => handleTabChange('alerts')}
        >
          {t('admin.tabs.alerts')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'settlement' ? 'active' : ''}`}
          onClick={() => handleTabChange('settlement')}
        >
          {t('admin.tabs.settlement')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'accounts' ? 'active' : ''}`}
          onClick={() => handleTabChange('accounts')}
        >
          {t('admin.tabs.accounts')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'mapping' ? 'active' : ''}`}
          onClick={() => handleTabChange('mapping')}
        >
          {t('admin.tabs.mapping')}
        </button>
        <div className="admin-title">Admin</div>
      </div>
      
      <div className="admin-content">
        {activeTab === 'automation' && (
          <div className="automation-settings">
            <h2>{t('admin.automation.title')}</h2>
            
            <div className="automation-grid">
              <div className="setting-card">
              <div className="setting-header">
                <h3>{t('admin.automation.dataSharing.title')}</h3>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={automationSettings.dataSharing}
                    onChange={(e) => handleAutomationChange('dataSharing', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              <p>{t('admin.automation.dataSharing.description')}</p>
            </div>
            
            <div className="setting-card">
              <div className="setting-header">
                <h3>{t('admin.automation.autoConfirmMatched.title')}</h3>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={automationSettings.autoConfirmMatched.enabled}
                    onChange={(e) => handleAutomationChange('autoConfirmMatched', {
                      ...automationSettings.autoConfirmMatched,
                      enabled: e.target.checked
                    })}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              <p>{t('admin.automation.autoConfirmMatched.description')}</p>
              {automationSettings.autoConfirmMatched.enabled && (
                <div className="delay-setting">
                  <label>{t('admin.automation.autoConfirmMatched.delayLabel')}</label>
                  <input 
                    type="number" 
                    value={automationSettings.autoConfirmMatched.delayMinutes}
                    onChange={(e) => handleDelayChange('autoConfirmMatched', parseInt(e.target.value) || 0)}
                    min="0"
                    max="1440"
                  />
                </div>
              )}
            </div>
            
            <div className="setting-card">
              <div className="setting-header">
                <h3>{t('admin.automation.autoCartaInstruccion.title')}</h3>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={automationSettings.autoCartaInstruccion}
                    onChange={(e) => handleAutomationChange('autoCartaInstruccion', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              <p>{t('admin.automation.autoCartaInstruccion.description')}</p>
            </div>
            
            <div className="setting-card">
              <div className="setting-header">
                <h3>{t('admin.automation.autoConfirmDisputed.title')}</h3>
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={automationSettings.autoConfirmDisputed.enabled}
                    onChange={(e) => handleAutomationChange('autoConfirmDisputed', {
                      ...automationSettings.autoConfirmDisputed,
                      enabled: e.target.checked
                    })}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              <p>{t('admin.automation.autoConfirmDisputed.description')}</p>
              {automationSettings.autoConfirmDisputed.enabled && (
                <div className="delay-setting">
                  <label>{t('admin.automation.autoConfirmDisputed.delayLabel')}</label>
                  <input 
                    type="number" 
                    value={automationSettings.autoConfirmDisputed.delayMinutes}
                    onChange={(e) => handleDelayChange('autoConfirmDisputed', parseInt(e.target.value) || 0)}
                    min="0"
                    max="1440"
                  />
                </div>
              )}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'alerts' && (
          <div className="alerts-settings">
            <h2>{t('admin.alerts.title')}</h2>
            
            <div className="alerts-grid">
              <div className="alert-section">
              <h3>{t('admin.alerts.emailConfirmed')}</h3>
              <div className="alert-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={alertSettings.emailConfirmedTrades.enabled}
                    onChange={(e) => {
                      setAlertSettings(prev => ({
                        ...prev,
                        emailConfirmedTrades: {
                          ...prev.emailConfirmedTrades,
                          enabled: e.target.checked
                        }
                      }));
                      setHasUnsavedChanges(true);
                    }}
                  />
                  <span className="slider"></span>
                </label>
                <span>{t('admin.alerts.enableEmail')}</span>
              </div>
              {alertSettings.emailConfirmedTrades.enabled && (
                <div className="contact-list">
                  <div className="add-contact">
                    <input 
                      type="email" 
                      placeholder={t('admin.alerts.addEmail')}
                      value={newEmailConfirmed}
                      onChange={(e) => setNewEmailConfirmed(e.target.value)}
                    />
                    <button onClick={() => addEmail('emailConfirmedTrades')}>{t('admin.alerts.addButton')}</button>
                  </div>
                  <div className="contact-items">
                    {alertSettings.emailConfirmedTrades.emails.map((email, index) => (
                      <div key={index} className="contact-item">
                        <span>{email}</span>
                        <button onClick={() => removeEmail('emailConfirmedTrades', email)}>×</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="alert-section">
              <h3>{t('admin.alerts.emailDisputed')}</h3>
              <div className="alert-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={alertSettings.emailDisputedTrades.enabled}
                    onChange={(e) => {
                      setAlertSettings(prev => ({
                        ...prev,
                        emailDisputedTrades: {
                          ...prev.emailDisputedTrades,
                          enabled: e.target.checked
                        }
                      }));
                      setHasUnsavedChanges(true);
                    }}
                  />
                  <span className="slider"></span>
                </label>
                <span>{t('admin.alerts.enableEmail')}</span>
              </div>
              {alertSettings.emailDisputedTrades.enabled && (
                <div className="contact-list">
                  <div className="add-contact">
                    <input 
                      type="email" 
                      placeholder={t('admin.alerts.addEmail')}
                      value={newEmailDisputed}
                      onChange={(e) => setNewEmailDisputed(e.target.value)}
                    />
                    <button onClick={() => addEmail('emailDisputedTrades')}>{t('admin.alerts.addButton')}</button>
                  </div>
                  <div className="contact-items">
                    {alertSettings.emailDisputedTrades.emails.map((email, index) => (
                      <div key={index} className="contact-item">
                        <span>{email}</span>
                        <button onClick={() => removeEmail('emailDisputedTrades', email)}>×</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="alert-section">
              <h3>{t('admin.alerts.smsConfirmed')}</h3>
              <div className="alert-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={alertSettings.smsConfirmedTrades.enabled}
                    onChange={(e) => {
                      setAlertSettings(prev => ({
                        ...prev,
                        smsConfirmedTrades: {
                          ...prev.smsConfirmedTrades,
                          enabled: e.target.checked
                        }
                      }));
                      setHasUnsavedChanges(true);
                    }}
                  />
                  <span className="slider"></span>
                </label>
                <span>{t('admin.alerts.enableSms')}</span>
              </div>
              {alertSettings.smsConfirmedTrades.enabled && (
                <div className="contact-list">
                  <div className="add-contact">
                    <input 
                      type="tel" 
                      placeholder={t('admin.alerts.addPhone')}
                      value={newPhoneConfirmed}
                      onChange={(e) => setNewPhoneConfirmed(e.target.value)}
                    />
                    <button onClick={() => addPhone('smsConfirmedTrades')}>{t('admin.alerts.addButton')}</button>
                  </div>
                  <div className="contact-items">
                    {alertSettings.smsConfirmedTrades.phones.map((phone, index) => (
                      <div key={index} className="contact-item">
                        <span>{phone}</span>
                        <button onClick={() => removePhone('smsConfirmedTrades', phone)}>×</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="alert-section">
              <h3>{t('admin.alerts.smsDisputed')}</h3>
              <div className="alert-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={alertSettings.smsDisputedTrades.enabled}
                    onChange={(e) => {
                      setAlertSettings(prev => ({
                        ...prev,
                        smsDisputedTrades: {
                          ...prev.smsDisputedTrades,
                          enabled: e.target.checked
                        }
                      }));
                      setHasUnsavedChanges(true);
                    }}
                  />
                  <span className="slider"></span>
                </label>
                <span>{t('admin.alerts.enableSms')}</span>
              </div>
              {alertSettings.smsDisputedTrades.enabled && (
                <div className="contact-list">
                  <div className="add-contact">
                    <input 
                      type="tel" 
                      placeholder={t('admin.alerts.addPhone')}
                      value={newPhoneDisputed}
                      onChange={(e) => setNewPhoneDisputed(e.target.value)}
                    />
                    <button onClick={() => addPhone('smsDisputedTrades')}>{t('admin.alerts.addButton')}</button>
                  </div>
                  <div className="contact-items">
                    {alertSettings.smsDisputedTrades.phones.map((phone, index) => (
                      <div key={index} className="contact-item">
                        <span>{phone}</span>
                        <button onClick={() => removePhone('smsDisputedTrades', phone)}>×</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            </div>
          </div>
        )}
        
        {activeTab === 'settlement' && (
          <div className="settlement-settings">
            <div className="settlement-header">
              <h2>{t('admin.settlement.title')}</h2>
              <p className="settlement-description">{t('admin.settlement.description')}</p>
              <button className="add-rule-button" onClick={handleAddRule}>
                + {t('admin.settlement.addRule')}
              </button>
            </div>

{!showRuleForm && (
              <div className="rules-table">
                <div className="table-header">
                  <div className="header-cell">{t('admin.settlement.table.active')}</div>
                  <div className="header-cell">{t('admin.settlement.table.priority')}</div>
                  <div className="header-cell">{t('admin.settlement.table.name')}</div>
                  <div className="header-cell">{t('admin.settlement.table.direction')}</div>
                  <div className="header-cell">{t('admin.settlement.table.counterparty')}</div>
                  <div className="header-cell">{t('admin.settlement.table.product')}</div>
                  <div className="header-cell">{t('admin.settlement.table.modalidad')}</div>
                  <div className="header-cell">{t('admin.settlement.table.payCurrency')}</div>
                  <div className="header-cell">{t('admin.settlement.table.receiveCurrency')}</div>
                  <div className="header-cell">{t('admin.settlement.table.actions')}</div>
                </div>
                
{(() => {
                  const orderedRules = getSortedAndGroupedRules();

                  return orderedRules.map((item, index) => {
                    if (item.type === 'header') {
                      const headerText = item.data as string;
                      return (
                        <div key={`header-${headerText}-${index}`} className="counterparty-group-header">
                          <h4>{headerText === 'Not Counterparty Specific' ? t('admin.settlement.table.notCounterpartySpecific') : headerText}</h4>
                        </div>
                      );
                    } else {
                      const rule = item.data as SettlementRule;
                      return (
                        <div 
                          key={`rule-${rule.id || index}`} 
                          className={`table-row ${!rule.active ? 'inactive' : ''} ${dragOverRule === rule.id ? 'drag-over' : ''} ${draggedRule === rule.id ? 'dragging' : ''}`}
                          draggable
                          onDragStart={(e) => handleDragStart(e, rule.id)}
                          onDragOver={(e) => handleDragOver(e, rule.id)}
                          onDragLeave={handleDragLeave}
                          onDragEnd={handleDragEnd}
                          onDrop={(e) => handleDrop(e, rule.id)}
                        >
                          <div className="table-cell center">
                            <input
                              type="checkbox"
                              checked={rule.active}
                              readOnly
                            />
                          </div>
                          <div className="table-cell center">
                            <span className="drag-handle">⋮⋮</span>
                            {rule.priority}
                          </div>
                          <div className="table-cell" title="Name: {rule.name}">{rule.name}</div>
                          <div className="table-cell" title="Direction">
                            {rule.direction ? t(`admin.settlement.directions.${rule.direction}`) : '-'}
                          </div>
                          <div className="table-cell" title="Counterparty">{rule.counterparty || 'No Counterparty'}</div>
                          <div className="table-cell" title="Product">{rule.product || '-'}</div>
                          <div className="table-cell" title="Modalidad">
                            {rule.modalidad ? t(`admin.settlement.modalidad.${rule.modalidad}`) : '-'}
                          </div>
                          <div className="table-cell" title="Pay Currency (Abonar)">{rule.abonarCurrency || '-'}</div>
                          <div className="table-cell" title="Receive Currency (Cargar)">{rule.cargarCurrency || '-'}</div>
                          <div className="table-cell actions">
                            <button className="edit-button" onClick={() => handleEditRule(rule)}>✏️</button>
                            <button className="delete-button" onClick={() => handleDeleteRule(rule.id)}>🗑️</button>
                          </div>
                        </div>
                      );
                    }
                  });
                })()}
                
                {settlementRules.length === 0 && (
                  <div className="empty-state">
                    <p>No settlement rules configured yet. Click "Add New Rule" to create your first rule.</p>
                  </div>
                )}
              </div>
            )}

{showRuleForm && (
              <div className="rule-form">
                <h3>{editingRule ? t('admin.settlement.editRule') : t('admin.settlement.addRule')}</h3>
                
                <div className="form-section">
                  <h4>{t('admin.settlement.form.generalInfo')}</h4>
                  
                  <div className="rule-form-header">
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.name')} *</label>
                      <input
                        type="text"
                        value={ruleForm.name || ''}
                        onChange={(e) => updateRuleForm('name', e.target.value)}
                        placeholder={t('admin.settlement.placeholders.name')}
                      />
                    </div>
                    
                    <div className="form-group priority-field">
                      <label>{t('admin.settlement.rules.priority')} *</label>
                      <input
                        type="number"
                        value={ruleForm.priority || 1}
                        onChange={(e) => updateRuleForm('priority', parseInt(e.target.value) || 1)}
                        min="1"
                        max="999"
                      />
                    </div>
                    
                    <div className="active-checkbox">
                      <label className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={ruleForm.active || false}
                          onChange={(e) => updateRuleForm('active', e.target.checked)}
                        />
                        {t('admin.settlement.rules.active')} *
                      </label>
                    </div>
                  </div>
                  
                  <div className="form-grid">
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.direction')} *</label>
                      <select
                        value={ruleForm.direction || ''}
                        onChange={(e) => updateRuleForm('direction', e.target.value)}
                      >
                        <option value="">{t('admin.settlement.placeholders.direction')}</option>
                        <option value="compra">{t('admin.settlement.directions.compra')}</option>
                        <option value="venta">{t('admin.settlement.directions.venta')}</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="form-grid" style={{ gridTemplateColumns: ruleForm.modalidad === 'compensacion' ? 'repeat(4, 1fr)' : 'repeat(3, 1fr)' }}>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.counterparty')}</label>
                      <select
                        value={ruleForm.counterparty || ''}
                        onChange={(e) => updateRuleForm('counterparty', e.target.value)}
                      >
                        <option value="">{t('admin.settlement.placeholders.counterparty')}</option>
                        {CHILEAN_BANKS.map(bank => (
                          <option key={bank} value={bank}>{bank}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.product')} *</label>
                      <select
                        value={ruleForm.product || ''}
                        onChange={(e) => {
                          const selectedProduct = e.target.value;
                          updateRuleForm('product', selectedProduct);
                          
                          // Implement modalidad logic from specs:
                          // - If Spot: default to "Entrega Física", cannot select "Compensación"
                          // - If Forward: default to "Compensación", can select "Entrega Física"
                          if (selectedProduct === 'Spot') {
                            updateRuleForm('modalidad', 'entregaFisica');
                            updateRuleForm('settlementCurrency', '');
                          } else if (selectedProduct === 'Forward') {
                            updateRuleForm('modalidad', 'compensacion');
                          } else {
                            updateRuleForm('modalidad', '');
                            updateRuleForm('settlementCurrency', '');
                          }
                        }}
                      >
                        <option value="">{t('admin.settlement.placeholders.product')}</option>
                        <option value="Spot">Spot</option>
                        <option value="Forward">Forward</option>                    
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.modalidad')} *</label>
                      <select
                        value={ruleForm.modalidad || ''}
                        onChange={(e) => {
                          const selectedModalidad = e.target.value;
                          updateRuleForm('modalidad', selectedModalidad);
                          // Clear settlement currency if switching to physical delivery
                          if (selectedModalidad === 'entregaFisica') {
                            updateRuleForm('settlementCurrency', undefined);
                          }
                        }}
                      >
                        <option value="">{t('admin.settlement.placeholders.modalidad')}</option>
                        <option value="entregaFisica">
                          {t('admin.settlement.modalidad.entregaFisica')}
                        </option>
                        {ruleForm.product !== 'Spot' && (
                          <option value="compensacion">
                            {t('admin.settlement.modalidad.compensacion')}
                          </option>
                        )}
                      </select>
                    </div>
                    
                    {/* Settlement Currency field - only show for Compensación */}
                    {ruleForm.modalidad === 'compensacion' && (
                      <div className="form-group">
                        <label>{t('admin.settlement.rules.settlementCurrency')} *</label>
                        <select
                          value={ruleForm.settlementCurrency || ''}
                          onChange={(e) => {
                            const currency = e.target.value;
                            updateRuleForm('settlementCurrency', currency);
                            // When settlement currency is set, update both cargar and abonar currencies
                            if (currency) {
                              updateRuleForm('cargarCurrency', currency);
                              updateRuleForm('abonarCurrency', currency);
                            }
                          }}
                        >
                          <option value="">{t('admin.settlement.placeholders.currency')}</option>
                          <option value="USD">USD</option>
                          <option value="EUR">EUR</option>
                          <option value="CLP">CLP</option>
                          <option value="GBP">GBP</option>
                          <option value="JPY">JPY</option>
                        </select>
                      </div>
                    )}
                  </div>
                </div>

{/* Only show Account Details and Central Bank Code sections if required General Information fields are filled */}
                {ruleForm.name && ruleForm.direction && ruleForm.product && ruleForm.modalidad && (
                  <>
                    <div className="form-section">
                      <h4>{t('admin.settlement.form.accountDetails')}</h4>
                      
                      <div className="account-details-grid" style={{ position: 'relative' }}>
                        {/* Cargar column - left */}
                        <div className="account-column">
                          <h5 className="subsection-title">{t('admin.settlement.accountDetails.cargar')}</h5>
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.currency')} *</label>
                            <select
                              value={ruleForm.cargarCurrency || ''}
                              onChange={(e) => updateRuleForm('cargarCurrency', e.target.value)}
                              disabled={ruleForm.modalidad === 'compensacion' && !!ruleForm.settlementCurrency}
                            >
                              <option value="">{t('admin.settlement.placeholders.currency')}</option>
                              {ruleForm.modalidad === 'compensacion' && ruleForm.settlementCurrency ? (
                                <option value={ruleForm.settlementCurrency}>{ruleForm.settlementCurrency}</option>
                              ) : (
                                <>
                                  <option value="USD">USD</option>
                                  <option value="EUR">EUR</option>
                                  <option value="CLP">CLP</option>
                                  <option value="GBP">GBP</option>
                                  <option value="JPY">JPY</option>
                                </>
                              )}
                            </select>
                          </div>
                          
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.bankName')} *</label>
                            <select
                              value={ruleForm.cargarBankName || ''}
                              onChange={(e) => {
                                const selectedBankName = e.target.value;
                                updateRuleForm('cargarBankName', selectedBankName);
                                
                                // Auto-populate SWIFT code if there's only one for this bank/currency combination
                                const availableAccounts = getAvailableAccounts(selectedBankName, undefined, ruleForm.cargarCurrency);
                                const uniqueSwiftCodes = Array.from(new Set(availableAccounts.map(acc => acc.swiftCode)));
                                
                                if (uniqueSwiftCodes.length === 1) {
                                  updateRuleForm('cargarSwiftCode', uniqueSwiftCodes[0]);
                                  
                                  // If there's also only one account, populate account number
                                  const matchingAccounts = availableAccounts.filter(acc => acc.swiftCode === uniqueSwiftCodes[0]);
                                  if (matchingAccounts.length === 1) {
                                    updateRuleForm('cargarAccountNumber', matchingAccounts[0].accountNumber);
                                  } else {
                                    updateRuleForm('cargarAccountNumber', '');
                                  }
                                } else {
                                  updateRuleForm('cargarSwiftCode', '');
                                  updateRuleForm('cargarAccountNumber', '');
                                }
                              }}
                              disabled={!ruleForm.cargarCurrency}
                            >
                              <option value="">{t('admin.settlement.placeholders.bankName')}</option>
                              {ruleForm.cargarCurrency ? (
                                Array.from(new Set(getAvailableAccounts(undefined, undefined, ruleForm.cargarCurrency).map(acc => acc.bankName))).length > 0 ? (
                                  Array.from(new Set(getAvailableAccounts(undefined, undefined, ruleForm.cargarCurrency).map(acc => acc.bankName))).map(bankName => (
                                    <option key={bankName} value={bankName}>{bankName}</option>
                                  ))
                                ) : (
                                  <option value="" disabled>No {ruleForm.cargarCurrency} accounts configured - please add one in Accounts tab</option>
                                )
                              ) : (
                                <option value="" disabled>Please select currency first</option>
                              )}
                            </select>
                          </div>
                          
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.swiftCode')} *</label>
                            <select
                              value={ruleForm.cargarSwiftCode || ''}
                              disabled={true}
                              title="SWIFT code is automatically set based on bank selection"
                            >
                              <option value="">{t('admin.settlement.placeholders.swiftCode')}</option>
                              {getAvailableAccounts(ruleForm.cargarBankName, undefined, ruleForm.cargarCurrency).map(account => (
                                <option key={account.id} value={account.swiftCode}>
                                  {account.swiftCode}
                                </option>
                              ))}
                            </select>
                          </div>
                          
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.accountNumber')} *</label>
                            <select
                              value={ruleForm.cargarAccountNumber || ''}
                              onChange={(e) => updateRuleForm('cargarAccountNumber', e.target.value)}
                              disabled={!ruleForm.cargarBankName || !ruleForm.cargarCurrency}
                            >
                              <option value="">{t('admin.settlement.placeholders.accountNumber')}</option>
                              {getAvailableAccounts(ruleForm.cargarBankName, undefined, ruleForm.cargarCurrency).map(account => (
                                <option key={account.id} value={account.accountNumber}>
                                  {account.accountNumber} ({account.accountName})
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                        
                        {/* Arrow buttons for Compensación - positioned between columns */}
                        {ruleForm.modalidad === 'compensacion' && (
                          <div style={{
                            position: 'absolute',
                            left: '50%',
                            top: '50%',
                            transform: 'translate(-50%, -50%)',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '12px',
                            zIndex: 1
                          }}>
                            <button
                              type="button"
                              className="copy-arrow-button"
                              onClick={() => {
                                // Copy Cargar to Abonar
                                updateRuleForm('abonarCurrency', ruleForm.cargarCurrency);
                                updateRuleForm('abonarBankName', ruleForm.cargarBankName);
                                updateRuleForm('abonarSwiftCode', ruleForm.cargarSwiftCode);
                                updateRuleForm('abonarAccountNumber', ruleForm.cargarAccountNumber);
                              }}
                              disabled={!ruleForm.cargarBankName || !ruleForm.cargarAccountNumber}
                              title={t('admin.settlement.buttons.copyCargarToAbonar')}
                              style={{
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '6px',
                                color: 'var(--text-primary)',
                                padding: '10px 16px',
                                fontSize: '18px',
                                fontWeight: '600',
                                cursor: ruleForm.cargarBankName && ruleForm.cargarAccountNumber ? 'pointer' : 'not-allowed',
                                opacity: ruleForm.cargarBankName && ruleForm.cargarAccountNumber ? 1 : 0.4,
                                transition: 'all 0.2s ease',
                                minWidth: '44px'
                              }}
                              onMouseEnter={(e) => {
                                if (ruleForm.cargarBankName && ruleForm.cargarAccountNumber) {
                                  e.currentTarget.style.background = 'var(--accent-blue)';
                                  e.currentTarget.style.transform = 'scale(1.05)';
                                }
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = 'var(--bg-tertiary)';
                                e.currentTarget.style.transform = 'scale(1)';
                              }}
                            >
                              →
                            </button>
                            <button
                              type="button"
                              className="copy-arrow-button"
                              onClick={() => {
                                // Copy Abonar to Cargar
                                updateRuleForm('cargarCurrency', ruleForm.abonarCurrency);
                                updateRuleForm('cargarBankName', ruleForm.abonarBankName);
                                updateRuleForm('cargarSwiftCode', ruleForm.abonarSwiftCode);
                                updateRuleForm('cargarAccountNumber', ruleForm.abonarAccountNumber);
                              }}
                              disabled={!ruleForm.abonarBankName || !ruleForm.abonarAccountNumber}
                              title={t('admin.settlement.buttons.copyAbonarToCargar')}
                              style={{
                                background: 'var(--bg-tertiary)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '6px',
                                color: 'var(--text-primary)',
                                padding: '10px 16px',
                                fontSize: '18px',
                                fontWeight: '600',
                                cursor: ruleForm.abonarBankName && ruleForm.abonarAccountNumber ? 'pointer' : 'not-allowed',
                                opacity: ruleForm.abonarBankName && ruleForm.abonarAccountNumber ? 1 : 0.4,
                                transition: 'all 0.2s ease',
                                minWidth: '44px'
                              }}
                              onMouseEnter={(e) => {
                                if (ruleForm.abonarBankName && ruleForm.abonarAccountNumber) {
                                  e.currentTarget.style.background = 'var(--accent-blue)';
                                  e.currentTarget.style.transform = 'scale(1.05)';
                                }
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.background = 'var(--bg-tertiary)';
                                e.currentTarget.style.transform = 'scale(1)';
                              }}
                            >
                              ←
                            </button>
                          </div>
                        )}
                        
                        {/* Abonar column - right */}
                        <div className="account-column">
                          <h5 className="subsection-title">{t('admin.settlement.accountDetails.abonar')}</h5>
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.currency')} *</label>
                            <select
                              value={ruleForm.abonarCurrency || ''}
                              onChange={(e) => updateRuleForm('abonarCurrency', e.target.value)}
                              disabled={ruleForm.modalidad === 'compensacion' && !!ruleForm.settlementCurrency}
                            >
                              <option value="">{t('admin.settlement.placeholders.currency')}</option>
                              {ruleForm.modalidad === 'compensacion' && ruleForm.settlementCurrency ? (
                                <option value={ruleForm.settlementCurrency}>{ruleForm.settlementCurrency}</option>
                              ) : (
                                <>
                                  <option value="USD">USD</option>
                                  <option value="EUR">EUR</option>
                                  <option value="CLP">CLP</option>
                                  <option value="GBP">GBP</option>
                                  <option value="JPY">JPY</option>
                                </>
                              )}
                            </select>
                          </div>
                          
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.bankName')} *</label>
                            <select
                              value={ruleForm.abonarBankName || ''}
                              onChange={(e) => {
                                const selectedBankName = e.target.value;
                                updateRuleForm('abonarBankName', selectedBankName);
                                
                                // Auto-populate SWIFT code if there's only one for this bank/currency combination
                                const availableAccounts = getAvailableAccounts(selectedBankName, undefined, ruleForm.abonarCurrency);
                                const uniqueSwiftCodes = Array.from(new Set(availableAccounts.map(acc => acc.swiftCode)));
                                
                                if (uniqueSwiftCodes.length === 1) {
                                  updateRuleForm('abonarSwiftCode', uniqueSwiftCodes[0]);
                                  
                                  // If there's also only one account, populate account number
                                  const matchingAccounts = availableAccounts.filter(acc => acc.swiftCode === uniqueSwiftCodes[0]);
                                  if (matchingAccounts.length === 1) {
                                    updateRuleForm('abonarAccountNumber', matchingAccounts[0].accountNumber);
                                  } else {
                                    updateRuleForm('abonarAccountNumber', '');
                                  }
                                } else {
                                  updateRuleForm('abonarSwiftCode', '');
                                  updateRuleForm('abonarAccountNumber', '');
                                }
                              }}
                              disabled={!ruleForm.abonarCurrency}
                            >
                              <option value="">{t('admin.settlement.placeholders.bankName')}</option>
                              {ruleForm.abonarCurrency ? (
                                Array.from(new Set(getAvailableAccounts(undefined, undefined, ruleForm.abonarCurrency).map(acc => acc.bankName))).length > 0 ? (
                                  Array.from(new Set(getAvailableAccounts(undefined, undefined, ruleForm.abonarCurrency).map(acc => acc.bankName))).map(bankName => (
                                    <option key={bankName} value={bankName}>{bankName}</option>
                                  ))
                                ) : (
                                  <option value="" disabled>No {ruleForm.abonarCurrency} accounts configured - please add one in Accounts tab</option>
                                )
                              ) : (
                                <option value="" disabled>Please select currency first</option>
                              )}
                            </select>
                          </div>
                          
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.swiftCode')} *</label>
                            <select
                              value={ruleForm.abonarSwiftCode || ''}
                              disabled={true}
                              title="SWIFT code is automatically set based on bank selection"
                            >
                              <option value="">{t('admin.settlement.placeholders.swiftCode')}</option>
                              {getAvailableAccounts(ruleForm.abonarBankName, undefined, ruleForm.abonarCurrency).map(account => (
                                <option key={account.id} value={account.swiftCode}>
                                  {account.swiftCode}
                                </option>
                              ))}
                            </select>
                          </div>
                          
                          <div className="form-group">
                            <label>{t('admin.settlement.rules.accountNumber')} *</label>
                            <select
                              value={ruleForm.abonarAccountNumber || ''}
                              onChange={(e) => updateRuleForm('abonarAccountNumber', e.target.value)}
                              disabled={!ruleForm.abonarBankName || !ruleForm.abonarCurrency}
                            >
                              <option value="">{t('admin.settlement.placeholders.accountNumber')}</option>
                              {getAvailableAccounts(ruleForm.abonarBankName, undefined, ruleForm.abonarCurrency).map(account => (
                                <option key={account.id} value={account.accountNumber}>
                                  {account.accountNumber} ({account.accountName})
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="form-section">
                      <h4>{t('admin.settlement.form.centralBankTradeCode')}</h4>
                      <div className="form-grid">
                        <div className="form-group">
                          <select
                            value={ruleForm.centralBankTradeCode || ''}
                            onChange={(e) => updateRuleForm('centralBankTradeCode', e.target.value)}
                          >
                            <option value="">{t('admin.settlement.placeholders.centralBankTradeCode')}</option>
                            {getTradeCodeOptions().map(option => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                <div className="form-actions">
                  <button 
                    className="save-rule-button" 
                    onClick={handleSaveRule}
                    disabled={isSavingRule}
                  >
                    {isSavingRule ? t('admin.settlement.form.saving') : t('admin.settlement.form.save')}
                  </button>
                  <button 
                    className="cancel-rule-button" 
                    onClick={handleCancelRule}
                    disabled={isSavingRule}
                  >
                    {t('admin.settlement.form.cancel')}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'accounts' && (
          <div className="accounts-settings">
            <div className="accounts-header">
              <div className="settlement-header">
                <div>
                  <h2>{t('admin.accounts.title')}</h2>
                  <p className="accounts-description">{t('admin.accounts.description')}</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <label style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                      {t('admin.accounts.groupBy')}:
                    </label>
                    <select
                      value={accountGrouping}
                      onChange={(e) => setAccountGrouping(e.target.value as 'none' | 'bank' | 'currency')}
                      style={{
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '4px',
                        padding: '0.5rem',
                        color: 'var(--text-primary)',
                        fontSize: '0.9rem'
                      }}
                    >
                      <option value="none">{t('admin.accounts.noGrouping')}</option>
                      <option value="bank">{t('admin.accounts.groupByBank')}</option>
                      <option value="currency">{t('admin.accounts.groupByCurrency')}</option>
                    </select>
                  </div>
                  <button className="add-account-button" onClick={handleAddAccount}>
                    + {t('admin.accounts.addAccount')}
                  </button>
                </div>
              </div>
            </div>

            <div className="accounts-table">
              <div className="table-header">
                <div className="header-cell accounts-active-header">{t('admin.accounts.table.active')}</div>
                <div className="header-cell">{t('admin.accounts.table.accountName')}</div>
                <div className="header-cell">{t('admin.accounts.table.bankName')}</div>
                <div className="header-cell">{t('admin.accounts.table.swiftCode')}</div>
                <div className="header-cell">{t('admin.accounts.table.accountCurrency')}</div>
                <div className="header-cell">{t('admin.accounts.table.accountNumber')}</div>
                <div className="header-cell">{t('admin.accounts.table.actions')}</div>
              </div>
              
              {(() => {
                const orderedAccounts = getSortedAndGroupedAccounts();
                
                const renderAccount = (account: BankAccount) => (
                  <div key={account.id} className={`table-row ${!account.active ? 'inactive' : ''}`}>
                    {editingAccount === account.id ? (
                      // Edit mode
                      <>
                        <div className="table-cell center">
                          <input
                            type="checkbox"
                            checked={accountForm.active || false}
                            onChange={(e) => updateAccountForm('active', e.target.checked)}
                          />
                        </div>
                        <div className="table-cell">
                          <input
                            type="text"
                            value={accountForm.accountName || ''}
                            onChange={(e) => updateAccountForm('accountName', e.target.value)}
                            placeholder={t('admin.accounts.placeholders.accountName')}
                          />
                        </div>
                        <div className="table-cell">
                          <select
                            value={accountForm.bankName || ''}
                            onChange={(e) => updateAccountForm('bankName', e.target.value)}
                          >
                            <option value="">{t('admin.accounts.placeholders.bankName')}</option>
                            {CHILEAN_BANKS.map(bank => (
                              <option key={bank} value={bank}>{bank}</option>
                            ))}
                          </select>
                        </div>
                        <div className="table-cell">
                          <input
                            type="text"
                            value={accountForm.swiftCode || ''}
                            onChange={(e) => updateAccountForm('swiftCode', e.target.value)}
                            placeholder={t('admin.accounts.placeholders.swiftCode')}
                          />
                        </div>
                        <div className="table-cell">
                          <select
                            value={accountForm.accountCurrency || ''}
                            onChange={(e) => updateAccountForm('accountCurrency', e.target.value)}
                          >
                            <option value="">{t('admin.accounts.placeholders.accountCurrency')}</option>
                            <option value="USD">USD</option>
                            <option value="EUR">EUR</option>
                            <option value="CLP">CLP</option>
                            <option value="GBP">GBP</option>
                            <option value="JPY">JPY</option>
                          </select>
                        </div>
                        <div className="table-cell">
                          <input
                            type="text"
                            value={accountForm.accountNumber || ''}
                            onChange={(e) => updateAccountForm('accountNumber', e.target.value)}
                            placeholder={t('admin.accounts.placeholders.accountNumber')}
                          />
                        </div>
                        <div className="table-cell actions">
                          <button 
                            className="save-button" 
                            onClick={handleSaveAccount}
                            disabled={isSavingAccount}
                            title={isSavingAccount ? t('admin.accounts.saving') : t('admin.accounts.save')}
                          >
                            {isSavingAccount ? '⏳' : '✓'}
                          </button>
                          <button 
                            className="cancel-button" 
                            onClick={handleCancelAccount}
                            disabled={isSavingAccount}
                          >
                            ✗
                          </button>
                        </div>
                      </>
                    ) : (
                      // View mode
                      <>
                        <div className="table-cell center">
                          <input
                            type="checkbox"
                            checked={account.active}
                            readOnly
                          />
                        </div>
                        <div className="table-cell">{account.accountName}</div>
                        <div className="table-cell">{account.bankName}</div>
                        <div className="table-cell">{account.swiftCode}</div>
                        <div className="table-cell">{account.accountCurrency}</div>
                        <div className="table-cell">{account.accountNumber}</div>
                        <div className="table-cell actions">
                          <button className="edit-button" onClick={() => handleEditAccount(account)}>✏️</button>
                          <button className="delete-button" onClick={() => handleDeleteAccount(account.id)}>🗑️</button>
                        </div>
                      </>
                    )}
                  </div>
                );

                return orderedAccounts.map((item, index) => {
                  if (item.type === 'header') {
                    const headerText = item.data as string;
                    return (
                      <div key={`header-${headerText}-${index}`} className="counterparty-group-header">
                        <h4>{headerText}</h4>
                      </div>
                    );
                  } else {
                    return renderAccount(item.data as BankAccount);
                  }
                });
              })()}
              
              {bankAccounts.length === 0 && (
                <div className="empty-state">
                  <p>No bank accounts configured yet. Click "Add Account" to create your first account.</p>
                </div>
              )}
            </div>
          </div>
        )}
        
        {activeTab === 'mapping' && (
          <div className="mapping-settings">
            <h2>{t('admin.dataMapping.title')}</h2>
            <p className="mapping-description">
              {t('admin.dataMapping.description')}
            </p>
            
            {/* File Upload Section */}
            {!uploadedFile ? (
              <div className="file-upload-section">
                <h3>{t('admin.dataMapping.uploadSampleFile')}</h3>
                <div 
                  className={`file-upload-area ${dragOverUpload ? 'drag-over' : ''}`}
                  onDragOver={(e) => { e.preventDefault(); setDragOverUpload(true); }}
                  onDragLeave={() => setDragOverUpload(false)}
                  onDrop={handleFileDrop}
                >
                  <div className="upload-content">
                    <div className="upload-icon">📁</div>
                    <p>{t('admin.dataMapping.dragDropText')}</p>
                    <label className="upload-button">
                      {t('admin.dataMapping.browseFiles')}
                      <input 
                        type="file" 
                        accept=".csv,.xlsx,.xls,.json" 
                        onChange={handleFileUpload}
                        style={{ display: 'none' }}
                      />
                    </label>
                    <p className="file-types">{t('admin.dataMapping.supportedFormats')}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mapping-interface">
                <div className="uploaded-file-info">
                  <h3>File: {uploadedFile.name}</h3>
                  <button className="clear-upload-button" onClick={clearUpload}>
                    ✗ {t('admin.dataMapping.clearUpload')}
                  </button>
                </div>

                {/* Field Mapping */}
                <div className="field-mapping-section">
                  <h4>{t('admin.dataMapping.fieldMapping')}</h4>
                  <div className="mapping-columns">
                    <div className="mapping-headers">
                      <div className="expected-field-header">{t('admin.dataMapping.headers.expectedField')}</div>
                      <div className="source-field-header">{t('admin.dataMapping.headers.sourceField')}</div>
                      <div className="transformation-header">{t('admin.dataMapping.headers.transformation')}</div>
                      <div className="example-header">{t('admin.dataMapping.headers.example')}</div>
                    </div>
                    {EXPECTED_FIELDS.map(expectedField => (
                      <div key={expectedField.name} className="mapping-row">
                        <div className="expected-field-column">
                          <div className="field-name">{t(`grid.columns.${expectedField.name}`)}</div>
                          <div className="field-format">{expectedField.format}</div>
                          <div className="field-description">{t(`admin.dataMapping.fieldDescriptions.${expectedField.name}`)}</div>
                        </div>
                        <div className="source-field-column">
                          <select 
                            className="source-field-dropdown"
                            value={getSuggestedSourceField(expectedField.name) === 'No suggestion' ? '' : getSuggestedSourceField(expectedField.name)}
                            onChange={(e) => updateMappingByTarget(expectedField.name, e.target.value)}
                          >
                            <option value="">{t('admin.dataMapping.dropdown.selectField')}</option>
                            {(() => {
                              return sourceFields.map(sourceField => (
                                <option key={sourceField} value={sourceField}>
                                  {sourceField}
                                </option>
                              ));
                            })()}
                          </select>
                        </div>
                        <div className="transformation-column">
                          <div className="transformation-info">
                            {(() => {
                              const mapping = currentMapping.find(m => m.targetField === expectedField.name);
                              if (!mapping) return <span className="no-transformation">-</span>;
                              
                              const { type, params } = mapping.transformation || {};
                              switch (type) {
                                case 'direct':
                                  return <span className="transform-direct">{t('admin.dataMapping.transformations.directCopy')}</span>;
                                case 'format':
                                  if (params?.from && params?.to) {
                                    return <span className="transform-format">{t('admin.dataMapping.transformations.date')}: {params.from} → {params.to}</span>;
                                  }
                                  if (params?.decimalSeparator) {
                                    return <span className="transform-format">{t('admin.dataMapping.transformations.decimal')}: {params.decimalSeparator === 'auto' ? t('admin.dataMapping.transformations.autoDetect') : params.decimalSeparator}</span>;
                                  }
                                  if (params?.precision) {
                                    return <span className="transform-format">{t('admin.dataMapping.transformations.precision')}: {params.precision} {t('admin.dataMapping.transformations.decimals')}</span>;
                                  }
                                  return <span className="transform-format">{t('admin.dataMapping.transformations.formatConversion')}</span>;
                                case 'enum':
                                  const mappingCount = params?.mapping ? Object.keys(params.mapping).length : 0;
                                  const mappingPreview = params?.mapping ? Object.entries(params.mapping).slice(0, 2).map(([k, v]) => `${k}→${v}`).join(', ') : '';
                                  return <span className="transform-enum">{t('admin.dataMapping.transformations.enum')}: {mappingPreview}{mappingCount > 2 ? '...' : ''}</span>;
                                default:
                                  return <span className="transform-unknown">{t('admin.dataMapping.transformations.unknown')}</span>;
                              }
                            })()}
                          </div>
                        </div>
                        <div className="example-column">
                          <div className="example-data">
                            {(() => {
                              const mapping = currentMapping.find(m => m.targetField === expectedField.name);
                              if (!mapping || !uploadedData?.[0]) {
                                return <span className="no-example">{t('admin.dataMapping.examples.none')}</span>;
                              }
                              
                              const sourceValue = uploadedData[0][mapping.sourceField];
                              if (!sourceValue) {
                                return <span className="no-example">{t('admin.dataMapping.examples.noData')}</span>;
                              }
                              
                              // Apply the same transformation logic as in applyMapping
                              let transformedValue = sourceValue;
                              const { type, params } = mapping.transformation || {};
                              
                              switch (type) {
                                case 'format':
                                  if (params?.decimalSeparator === ',' || String(sourceValue).includes(',')) {
                                    transformedValue = String(sourceValue).replace(',', '.');
                                  }
                                  if (params?.from === 'DD/MM/YYYY' && String(sourceValue).includes('/')) {
                                    const parts = String(sourceValue).split('/');
                                    if (parts.length === 3) {
                                      transformedValue = `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
                                    }
                                  }
                                  break;
                                case 'enum':
                                  const enumMapping = params?.mapping;
                                  if (enumMapping && enumMapping[sourceValue]) {
                                    transformedValue = enumMapping[sourceValue];
                                  }
                                  break;
                                case 'direct':
                                default:
                                  transformedValue = sourceValue;
                              }
                              
                              return (
                                <div className="example-transformation">
                                  <div className="source-value">{String(sourceValue)}</div>
                                  <div className="arrow">→</div>
                                  <div className="target-value">{String(transformedValue)}</div>
                                </div>
                              );
                            })()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Preview Section */}
                {mappedData && mappedData.length > 0 && (
                  <div className="preview-section">
                    <div className="preview-header-row">
                      <h4>{t('admin.dataMapping.mappingPreview')}</h4>
                      <button 
                        className="refresh-preview-button"
                        onClick={() => {
                          if (uploadedData && uploadedData.length > 0) {
                            const mapped = applyMapping(uploadedData, currentMapping);
                            setMappedData(mapped);
                          }
                        }}
                        title={t('admin.dataMapping.refreshPreview')}
                      >
                        🔄 {t('admin.dataMapping.refresh')}
                      </button>
                    </div>
                    <div className="preview-table-container">
                      <table className="preview-data-table">
                        <thead>
                          <tr>
                            {EXPECTED_FIELDS.map(field => (
                              <th key={field.name} className="preview-th">
                                {t(`grid.columns.${field.name}`)}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {mappedData.slice(0, 3).map((row, index) => (
                            <tr key={index}>
                              {EXPECTED_FIELDS.map(field => (
                                <td key={field.name} className="preview-td">
                                  {row[field.name] || '-'}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Save Mapping Section */}
                <div className="save-mapping-section">
                  {!showMappingForm ? (
                    <button 
                      className="show-save-form-button"
                      onClick={() => setShowMappingForm(true)}
                    >
                      {t('admin.dataMapping.saveMapping.showSaveButton')}
                    </button>
                  ) : (
                    <div className="save-mapping-form">
                      <h4>{t('admin.dataMapping.saveMapping.title')}</h4>
                      <div className="form-grid">
                        <div className="form-group">
                          <label>{t('admin.dataMapping.saveMapping.nameLabel')}</label>
                          <input
                            type="text"
                            value={mappingForm.name}
                            onChange={(e) => setMappingForm(prev => ({ ...prev, name: e.target.value }))}
                            placeholder={t('admin.dataMapping.saveMapping.namePlaceholder')}
                          />
                        </div>
                        <div className="form-group">
                          <label>{t('admin.dataMapping.saveMapping.descriptionLabel')}</label>
                          <input
                            type="text"
                            value={mappingForm.description}
                            onChange={(e) => setMappingForm(prev => ({ ...prev, description: e.target.value }))}
                            placeholder={t('admin.dataMapping.saveMapping.descriptionPlaceholder')}
                          />
                        </div>
                      </div>
                      <div className="form-actions">
                        <button 
                          className="save-mapping-button" 
                          onClick={saveMapping}
                          disabled={!mappingForm.name}
                        >
                          {t('admin.dataMapping.saveMapping.saveButton')}
                        </button>
                        <button 
                          className="cancel-mapping-button"
                          onClick={() => setShowMappingForm(false)}
                        >
                          {t('admin.dataMapping.saveMapping.cancelButton')}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Saved Mappings Section */}
            <div className="saved-mappings-section">
              <h3>{t('admin.dataMapping.savedMappings.title')}</h3>
              {dataMappings.length === 0 ? (
                <div className="empty-state">
                  <p>{t('admin.dataMapping.savedMappings.emptyState')}</p>
                </div>
              ) : (
                <div className="mappings-table">
                  <div className="mappings-header">
                    <div>{t('admin.dataMapping.savedMappings.tableHeaders.name')}</div>
                    <div>{t('admin.dataMapping.savedMappings.tableHeaders.description')}</div>
                    <div>{t('admin.dataMapping.savedMappings.tableHeaders.fileType')}</div>
                    <div>{t('admin.dataMapping.savedMappings.tableHeaders.created')}</div>
                    <div>{t('admin.dataMapping.savedMappings.tableHeaders.fields')}</div>
                    <div>{t('admin.dataMapping.savedMappings.tableHeaders.actions')}</div>
                  </div>
                  {dataMappings.map(mapping => (
                    <div key={mapping.id} className="mapping-row">
                      <div className="mapping-name">{mapping.name}</div>
                      <div className="mapping-description">{mapping.description}</div>
                      <div className="mapping-file-type">
                        <span className={`file-type-badge ${mapping.fileType}`}>
                          {mapping.fileType.toUpperCase()}
                        </span>
                      </div>
                      <div className="mapping-date">{mapping.createdDate}</div>
                      <div className="mapping-fields">
                        {mapping.fieldMappings.length} {t('admin.dataMapping.savedMappings.fieldsCount')}
                      </div>
                      <div className="mapping-actions">
                        <button className="edit-button" title={t('admin.dataMapping.savedMappings.tooltips.edit')}>✏️</button>
                        <button 
                          className="delete-button" 
                          onClick={() => deleteMapping(mapping.id)}
                          title={t('admin.dataMapping.savedMappings.tooltips.delete')}
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {!showRuleForm && (
        <div className="admin-actions">
          <button 
            className="save-button primary" 
            onClick={saveConfiguration}
            disabled={isSaving}
          >
            {isSaving ? t('admin.actions.saving') : t('admin.actions.save')}
          </button>
        </div>
      )}
      
      <AlertModal
        isOpen={alertModal.isOpen}
        onClose={closeModal}
        title={alertModal.title}
        message={alertModal.message}
        type={alertModal.type}
      />

      {/* Unsaved Changes Modal */}
      {showUnsavedChangesModal && (
        <div className="modal-overlay">
          <div className="modal unsaved-changes-modal">
            <h3>{t('admin.unsavedChanges.title')}</h3>
            <p>{t('admin.unsavedChanges.message')}</p>
            <div className="modal-actions">
              <button 
                className="save-button primary"
                onClick={handleSaveAndContinue}
                disabled={isSaving}
              >
                {isSaving ? t('admin.unsavedChanges.saving') : t('admin.unsavedChanges.saveAndContinue')}
              </button>
              <button 
                className="save-button secondary"
                onClick={handleDiscardAndContinue}
                disabled={isSaving}
              >
                {t('admin.unsavedChanges.discardAndContinue')}
              </button>
              <button 
                className="cancel-button"
                onClick={handleCancelNavigation}
                disabled={isSaving}
              >
                {t('admin.unsavedChanges.cancel')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;