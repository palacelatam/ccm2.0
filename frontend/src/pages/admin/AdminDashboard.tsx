import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as XLSX from 'xlsx';
import AlertModal from '../../components/common/AlertModal';
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
  whatsappConfirmedTrades: {
    enabled: boolean;
    phones: string[];
  };
  whatsappDisputedTrades: {
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
  counterparty: string;
  cashflowCurrency: string;
  direction: 'IN' | 'OUT';
  product: string;
  bankName: string;
  swiftCode: string;
  accountCurrency: string;
  accountNumber: string;
}

interface BankAccount {
  id: string;
  active: boolean;
  accountName: string;
  bankName: string;
  swiftCode: string;
  accountCurrency: string;
  accountNumber: string;
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
  
  // Expected fields for trade data mapping (based on ClientTradesGrid columns, excluding status and source)
  const EXPECTED_FIELDS: ExpectedField[] = [
    { name: 'tradeId', type: 'string', format: 'text', required: true, description: 'Unique identifier for the trade' },
    { name: 'counterparty', type: 'string', format: 'text', required: true, description: 'Bank or financial institution counterparty' },
    { name: 'productType', type: 'enum', format: 'text', required: true, enumValues: ['FX Spot', 'FX Forward'], description: 'Type of financial product' },
    { name: 'tradeDate', type: 'date', format: 'YYYY-MM-DD', required: true, description: 'Date when trade was executed' },
    { name: 'valueDate', type: 'date', format: 'YYYY-MM-DD', required: true, description: 'Settlement/value date for the trade' },
    { name: 'direction', type: 'enum', format: 'text', required: true, enumValues: ['BUY', 'SELL'], description: 'Trade direction (buy or sell)' },
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
    whatsappConfirmedTrades: {
      enabled: false,
      phones: ['+56912345678']
    },
    whatsappDisputedTrades: {
      enabled: true,
      phones: ['+56912345678', '+56987654321']
    }
  });
  
  const [newEmailConfirmed, setNewEmailConfirmed] = useState('');
  const [newEmailDisputed, setNewEmailDisputed] = useState('');
  const [newPhoneConfirmed, setNewPhoneConfirmed] = useState('');
  const [newPhoneDisputed, setNewPhoneDisputed] = useState('');
  
  // Bank Accounts state
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([
    {
      id: '1',
      active: true,
      accountName: 'USD Main Account',
      bankName: 'Banco Santander Chile',
      swiftCode: 'BSCHCLRM',
      accountCurrency: 'USD',
      accountNumber: '12345678901'
    },
    {
      id: '2',
      active: true,
      accountName: 'EUR Operations Account',
      bankName: 'Banco de Crédito e Inversiones',
      swiftCode: 'BCICHCL2',
      accountCurrency: 'EUR',
      accountNumber: '23456789012'
    },
    {
      id: '3',
      active: true,
      accountName: 'CLP Clearing Account',
      bankName: 'Banco del Estado de Chile',
      swiftCode: 'BECHCLRM',
      accountCurrency: 'CLP',
      accountNumber: '34567890123'
    }
  ]);

  // Settlement Rules state
  const [settlementRules, setSettlementRules] = useState<SettlementRule[]>([
    {
      id: '1',
      active: true,
      priority: 1,
      name: 'USD Santander Inbound',
      counterparty: 'Banco Santander Chile',
      cashflowCurrency: 'USD',
      direction: 'IN',
      product: 'FX SPOT',
      bankName: 'Banco Santander Chile',
      swiftCode: 'BSCHCLRM',
      accountCurrency: 'USD',
      accountNumber: '12345678901'
    },
    {
      id: '2',
      active: true,
      priority: 2,
      name: 'EUR BCI Outbound',
      counterparty: 'Banco de Crédito e Inversiones',
      cashflowCurrency: 'EUR',
      direction: 'OUT',
      product: 'FX FORWARD',
      bankName: 'Banco de Crédito e Inversiones',
      swiftCode: 'BCICHCL2',
      accountCurrency: 'EUR',  
      accountNumber: '23456789012'
    }
  ]);
  
  const [showRuleForm, setShowRuleForm] = useState(false);
  const [editingRule, setEditingRule] = useState<SettlementRule | null>(null);
  const [ruleForm, setRuleForm] = useState<Partial<SettlementRule>>({});
  
  // Accounts state
  const [editingAccount, setEditingAccount] = useState<string | null>(null);
  const [accountForm, setAccountForm] = useState<Partial<BankAccount>>({});
  const [accountGrouping, setAccountGrouping] = useState<'none' | 'bank' | 'currency'>('none');
  
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
  
  const handleAutomationChange = (key: keyof AutomationSettings, value: any) => {
    setAutomationSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const handleDelayChange = (setting: 'autoConfirmMatched' | 'autoConfirmDisputed', minutes: number) => {
    setAutomationSettings(prev => ({
      ...prev,
      [setting]: {
        ...prev[setting],
        delayMinutes: minutes
      }
    }));
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
  };
  
  const addPhone = (alertType: 'whatsappConfirmedTrades' | 'whatsappDisputedTrades') => {
    const phone = alertType === 'whatsappConfirmedTrades' ? newPhoneConfirmed : newPhoneDisputed;
    const setPhone = alertType === 'whatsappConfirmedTrades' ? setNewPhoneConfirmed : setNewPhoneDisputed;
    
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
    }
  };
  
  const removePhone = (alertType: 'whatsappConfirmedTrades' | 'whatsappDisputedTrades', phone: string) => {
    setAlertSettings(prev => ({
      ...prev,
      [alertType]: {
        ...prev[alertType],
        phones: prev[alertType].phones.filter((p: string) => p !== phone)
      }
    }));
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
      cashflowCurrency: '',
      direction: 'IN',
      product: '',
      bankName: '',
      swiftCode: '',
      accountCurrency: '',
      accountNumber: ''
    });
    setShowRuleForm(true);
  };

  // Check for duplicate settlement rule
  const isDuplicateRule = (rule: Partial<SettlementRule>, excludeId?: string): boolean => {
    return settlementRules.some(existingRule => {
      if (excludeId && existingRule.id === excludeId) return false;
      return (
        existingRule.counterparty === rule.counterparty &&
        existingRule.cashflowCurrency === rule.cashflowCurrency &&
        existingRule.direction === rule.direction &&
        existingRule.product === rule.product &&
        existingRule.bankName === rule.bankName &&
        existingRule.accountCurrency === rule.accountCurrency
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

  const handleSaveRule = () => {
    // Validate required fields
    if (!ruleForm.name || !ruleForm.cashflowCurrency || !ruleForm.bankName || !ruleForm.swiftCode || 
        !ruleForm.accountCurrency || !ruleForm.accountNumber) {
      setAlertModal({
        isOpen: true,
        title: 'Validation Error',
        message: 'Please fill in all required fields (Active, Priority, Rule Name, Cashflow Currency, Direction, Bank Name, SWIFT Code, Account Currency, Account Number).',
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

    if (editingRule) {
      // Update existing rule
      setSettlementRules(prev => prev.map(rule => 
        rule.id === editingRule.id ? { ...ruleForm as SettlementRule } : rule
      ));
    } else {
      // Add new rule
      const newRule: SettlementRule = {
        ...ruleForm as SettlementRule,
        id: Date.now().toString()
      };
      setSettlementRules(prev => [...prev, newRule]);
    }

    setShowRuleForm(false);
    setRuleForm({});
    setEditingRule(null);
  };

  const handleCancelRule = () => {
    setShowRuleForm(false);
    setRuleForm({});
    setEditingRule(null);
  };

  const updateRuleForm = (field: keyof SettlementRule, value: any) => {
    setRuleForm(prev => ({ ...prev, [field]: value }));
  };

  // Account management functions
  const handleAddAccount = () => {
    const newAccount: BankAccount = {
      id: Date.now().toString(),
      active: true,
      accountName: '',
      bankName: '',
      swiftCode: '',
      accountCurrency: '',
      accountNumber: ''
    };
    setBankAccounts(prev => [...prev, newAccount]);
    setEditingAccount(newAccount.id);
    setAccountForm({ ...newAccount });
  };

  const handleEditAccount = (account: BankAccount) => {
    setEditingAccount(account.id);
    setAccountForm({ ...account });
  };

  const handleSaveAccount = () => {
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

    setBankAccounts(prev => prev.map(account => 
      account.id === editingAccount ? { ...accountForm as BankAccount } : account
    ));
    setEditingAccount(null);
    setAccountForm({});
  };

  const handleCancelAccount = () => {
    if (editingAccount && !bankAccounts.find(acc => acc.id === editingAccount)?.accountName) {
      // Remove new empty account if cancelled
      setBankAccounts(prev => prev.filter(acc => acc.id !== editingAccount));
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
  };

  const updateAccountForm = (field: keyof BankAccount, value: any) => {
    setAccountForm(prev => ({ ...prev, [field]: value }));
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
    // Sort by active status first, then by account name
    const sorted = [...bankAccounts].sort((a, b) => {
      // First by active status (active first)
      if (a.active !== b.active) return a.active ? -1 : 1;
      // Then by account name
      return a.accountName.localeCompare(b.accountName);
    });

    if (accountGrouping === 'none') {
      return sorted.map(account => ({ type: 'account' as const, data: account }));
    }

    // Build ordered list with grouping
    const orderedAccounts: Array<{ type: 'account' | 'header'; data: BankAccount | string }> = [];
    let currentGroup: string | null = null;

    sorted.forEach(account => {
      const groupKey = accountGrouping === 'bank' ? account.bankName : account.accountCurrency;
      
      if (groupKey !== currentGroup) {
        currentGroup = groupKey;
        orderedAccounts.push({ type: 'header', data: groupKey });
      }
      
      orderedAccounts.push({ type: 'account', data: account });
    });

    return orderedAccounts;
  };

  // Drag and drop handlers
  const handleDragStart = (e: React.DragEvent, ruleId: string) => {
    setDraggedRule(ruleId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, ruleId: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverRule(ruleId);
  };

  const handleDragLeave = () => {
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
    
    if (draggedRuleData && targetRuleData) {
      // Swap priorities
      const newRules = settlementRules.map(rule => {
        if (rule.id === draggedRule) {
          return { ...rule, priority: targetRuleData.priority };
        } else if (rule.id === targetRuleId) {
          return { ...rule, priority: draggedRuleData.priority };
        }
        return rule;
      });
      
      setSettlementRules(newRules);
    }
    
    setDraggedRule(null);
    setDragOverRule(null);
  };

  const saveConfiguration = async () => {
    setIsSaving(true);
    
    try {
      // TODO: Implement actual save to backend
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Saving configuration:', { automationSettings, alertSettings });
      
      setAlertModal({
        isOpen: true,
        title: t('admin.modal.saveSuccess.title'),
        message: t('admin.modal.saveSuccess.message'),
        type: 'success'
      });
    } catch (error) {
      console.error('Save failed:', error);
      // TODO: Show error modal
    } finally {
      setIsSaving(false);
    }
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
                console.log('Date conversion failed for value:', value, 'field:', fieldName);
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
        'Product': 'FX SPOT', 'Direction': 'BUY', 'Ccy1': 'USD', 'Ccy2': 'CLP', 'Amount': '100000.50', 
        'Rate': '920.45', 'PaymentDate': '2025-01-17', 'SettlementType': 'DVP', 'Reference': 'REF001',
        'Comments': 'Standard trade', 'Status': 'ACTIVE', 'User': 'admin', 'Source': 'SYSTEM_A'
      },
      { 
        'TradeID': 'TR1002', 'TradeDate': '2025-01-16', 'ValueDate': '2025-01-18', 'Counterparty': 'Bank XYZ', 
        'Product': 'FX FORWARD', 'Direction': 'SELL', 'Ccy1': 'EUR', 'Ccy2': 'USD', 'Amount': '50000.00', 
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
      else if (lowerField.includes('compra') || lowerField.includes('venta') || lowerField === 'direction') {
        mappings.push({ sourceField, targetField: 'direction', transformation: { type: 'enum', params: { mapping: { 'C': 'BUY', 'V': 'SELL', 'BUY': 'BUY', 'SELL': 'SELL' } } } });
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
          onClick={() => setActiveTab('automation')}
        >
          {t('admin.tabs.automation')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'alerts' ? 'active' : ''}`}
          onClick={() => setActiveTab('alerts')}
        >
          {t('admin.tabs.alerts')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'settlement' ? 'active' : ''}`}
          onClick={() => setActiveTab('settlement')}
        >
          {t('admin.tabs.settlement')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'accounts' ? 'active' : ''}`}
          onClick={() => setActiveTab('accounts')}
        >
          {t('admin.tabs.accounts')}
        </button>
        <button 
          className={`tab-button ${activeTab === 'mapping' ? 'active' : ''}`}
          onClick={() => setActiveTab('mapping')}
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
                    onChange={(e) => setAlertSettings(prev => ({
                      ...prev,
                      emailConfirmedTrades: {
                        ...prev.emailConfirmedTrades,
                        enabled: e.target.checked
                      }
                    }))}
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
                    onChange={(e) => setAlertSettings(prev => ({
                      ...prev,
                      emailDisputedTrades: {
                        ...prev.emailDisputedTrades,
                        enabled: e.target.checked
                      }
                    }))}
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
              <h3>{t('admin.alerts.whatsappConfirmed')}</h3>
              <div className="alert-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={alertSettings.whatsappConfirmedTrades.enabled}
                    onChange={(e) => setAlertSettings(prev => ({
                      ...prev,
                      whatsappConfirmedTrades: {
                        ...prev.whatsappConfirmedTrades,
                        enabled: e.target.checked
                      }
                    }))}
                  />
                  <span className="slider"></span>
                </label>
                <span>{t('admin.alerts.enableWhatsapp')}</span>
              </div>
              {alertSettings.whatsappConfirmedTrades.enabled && (
                <div className="contact-list">
                  <div className="add-contact">
                    <input 
                      type="tel" 
                      placeholder={t('admin.alerts.addPhone')}
                      value={newPhoneConfirmed}
                      onChange={(e) => setNewPhoneConfirmed(e.target.value)}
                    />
                    <button onClick={() => addPhone('whatsappConfirmedTrades')}>{t('admin.alerts.addButton')}</button>
                  </div>
                  <div className="contact-items">
                    {alertSettings.whatsappConfirmedTrades.phones.map((phone, index) => (
                      <div key={index} className="contact-item">
                        <span>{phone}</span>
                        <button onClick={() => removePhone('whatsappConfirmedTrades', phone)}>×</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="alert-section">
              <h3>{t('admin.alerts.whatsappDisputed')}</h3>
              <div className="alert-toggle">
                <label className="toggle-switch">
                  <input 
                    type="checkbox" 
                    checked={alertSettings.whatsappDisputedTrades.enabled}
                    onChange={(e) => setAlertSettings(prev => ({
                      ...prev,
                      whatsappDisputedTrades: {
                        ...prev.whatsappDisputedTrades,
                        enabled: e.target.checked
                      }
                    }))}
                  />
                  <span className="slider"></span>
                </label>
                <span>{t('admin.alerts.enableWhatsapp')}</span>
              </div>
              {alertSettings.whatsappDisputedTrades.enabled && (
                <div className="contact-list">
                  <div className="add-contact">
                    <input 
                      type="tel" 
                      placeholder={t('admin.alerts.addPhone')}
                      value={newPhoneDisputed}
                      onChange={(e) => setNewPhoneDisputed(e.target.value)}
                    />
                    <button onClick={() => addPhone('whatsappDisputedTrades')}>{t('admin.alerts.addButton')}</button>
                  </div>
                  <div className="contact-items">
                    {alertSettings.whatsappDisputedTrades.phones.map((phone, index) => (
                      <div key={index} className="contact-item">
                        <span>{phone}</span>
                        <button onClick={() => removePhone('whatsappDisputedTrades', phone)}>×</button>
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
                  <div className="separator-cell"></div>
                  <div className="header-cell">{t('admin.settlement.table.name')}</div>
                  <div className="header-cell">{t('admin.settlement.table.counterparty')}</div>
                  <div className="header-cell">{t('admin.settlement.table.cashflowCurrency')}</div>
                  <div className="header-cell">{t('admin.settlement.table.product')}</div>
                  <div className="header-cell">{t('admin.settlement.table.direction')}</div>
                  <div className="separator-cell"></div>
                  <div className="header-cell">{t('admin.settlement.table.bankSwift')}</div>
                  <div className="header-cell">{t('admin.settlement.table.accountNumber')}</div>
                  <div className="header-cell">{t('admin.settlement.table.actions')}</div>
                </div>
                
{(() => {
                  const orderedRules = getSortedAndGroupedRules();
                  
                  const renderRule = (rule: SettlementRule) => (
                    <div 
                      key={rule.id} 
                      className={`table-row ${!rule.active ? 'inactive' : ''} ${dragOverRule === rule.id ? 'drag-over' : ''}`}
                      draggable
                      onDragStart={(e) => handleDragStart(e, rule.id)}
                      onDragOver={(e) => handleDragOver(e, rule.id)}
                      onDragLeave={handleDragLeave}
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
                      <div className="separator-cell"></div>
                      <div className="table-cell">{rule.name}</div>
                      <div className="table-cell">{rule.counterparty || '-'}</div>
                      <div className="table-cell">{rule.cashflowCurrency}</div>
                      <div className="table-cell">{rule.product || '-'}</div>
                      <div className="table-cell direction-cell">
                        <span className={`direction-badge ${rule.direction.toLowerCase()}`}>
                          {rule.direction}
                        </span>
                      </div>
                      <div className="separator-cell"></div>
                      <div className="table-cell">{rule.swiftCode}</div>
                      <div className="table-cell">{rule.accountNumber}</div>
                      <div className="table-cell actions">
                        <button className="edit-button" onClick={() => handleEditRule(rule)}>✏️</button>
                        <button className="delete-button" onClick={() => handleDeleteRule(rule.id)}>🗑️</button>
                      </div>
                    </div>
                  );

                  return orderedRules.map((item, index) => {
                    if (item.type === 'header') {
                      const headerText = item.data as string;
                      return (
                        <div key={`header-${headerText}`} className="counterparty-group-header">
                          <h4>{headerText === 'Not Counterparty Specific' ? t('admin.settlement.table.notCounterpartySpecific') : headerText}</h4>
                        </div>
                      );
                    } else {
                      return renderRule(item.data as SettlementRule);
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
                      <label>{t('admin.settlement.rules.cashflowCurrency')} *</label>
                      <select
                        value={ruleForm.cashflowCurrency || ''}
                        onChange={(e) => {
                          const selectedCurrency = e.target.value;
                          updateRuleForm('cashflowCurrency', selectedCurrency);
                          // Auto-set account currency to match cashflow currency
                          updateRuleForm('accountCurrency', selectedCurrency);
                          // Clear other account details since they depend on currency
                          updateRuleForm('bankName', '');
                          updateRuleForm('swiftCode', '');
                          updateRuleForm('accountNumber', '');
                        }}
                      >
                        <option value="">{t('admin.settlement.placeholders.cashflowCurrency')}</option>
                        <option value="USD">USD</option>
                        <option value="EUR">EUR</option>
                        <option value="CLP">CLP</option>
                        <option value="GBP">GBP</option>
                        <option value="JPY">JPY</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.direction')} *</label>
                      <select
                        value={ruleForm.direction || 'IN'}
                        onChange={(e) => updateRuleForm('direction', e.target.value as 'IN' | 'OUT')}
                      >
                        <option value="IN">IN</option>
                        <option value="OUT">OUT</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.product')}</label>
                      <select
                        value={ruleForm.product || ''}
                        onChange={(e) => updateRuleForm('product', e.target.value)}
                      >
                        <option value="">{t('admin.settlement.placeholders.product')}</option>
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
                  <h4>{t('admin.settlement.form.accountDetails')}</h4>
                  
                  {/* Show helpful message if no accounts match cashflow currency */}
                  {ruleForm.cashflowCurrency && getAvailableAccounts(undefined, undefined, ruleForm.cashflowCurrency).length === 0 && (
                    <div className="no-accounts-message">
                      <p>
                        <strong>No {ruleForm.cashflowCurrency} accounts found.</strong>
                      </p>
                      <p>
                        Please go to the <strong>Accounts</strong> tab to create a {ruleForm.cashflowCurrency} account before setting up this settlement rule.
                      </p>
                    </div>
                  )}
                  
                  <div className="form-grid two-column">
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.accountCurrency')} * (matches cashflow currency)</label>
                      <input
                        type="text"
                        value={ruleForm.accountCurrency || ''}
                        readOnly
                        disabled
                        placeholder={ruleForm.cashflowCurrency ? ruleForm.cashflowCurrency : t('admin.settlement.placeholders.accountCurrency')}
                        className="auto-populated-field"
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.bankName')} *</label>
                      <select
                        value={ruleForm.bankName || ''}
                        onChange={(e) => {
                          const selectedBankName = e.target.value;
                          updateRuleForm('bankName', selectedBankName);
                          
                          // Auto-populate SWIFT code if there's only one for this bank
                          // Only consider accounts that match the cashflow currency
                          const bankAccounts_filtered = bankAccounts.filter(acc => 
                            acc.active && 
                            acc.bankName === selectedBankName &&
                            (!ruleForm.cashflowCurrency || acc.accountCurrency === ruleForm.cashflowCurrency)
                          );
                          const uniqueSwiftCodes = Array.from(new Set(bankAccounts_filtered.map(acc => acc.swiftCode)));
                          
                          if (uniqueSwiftCodes.length === 1) {
                            updateRuleForm('swiftCode', uniqueSwiftCodes[0]);
                            
                            // If there's also only one account with this bank/swift combination, populate currency and account
                            const matchingAccounts = bankAccounts_filtered.filter(acc => acc.swiftCode === uniqueSwiftCodes[0]);
                            if (matchingAccounts.length === 1) {
                              updateRuleForm('accountCurrency', matchingAccounts[0].accountCurrency);
                              updateRuleForm('accountNumber', matchingAccounts[0].accountNumber);
                            } else {
                              updateRuleForm('accountCurrency', '');
                              updateRuleForm('accountNumber', '');
                            }
                          } else {
                            // Clear account details when bank changes and there are multiple SWIFT codes
                            updateRuleForm('swiftCode', '');
                            updateRuleForm('accountCurrency', '');
                            updateRuleForm('accountNumber', '');
                          }
                        }}
                      >
                        <option value="">{t('admin.settlement.placeholders.bankName')}</option>
                        {Array.from(new Set(getAvailableAccounts(undefined, undefined, ruleForm.cashflowCurrency).map(acc => acc.bankName))).map(bankName => (
                          <option key={bankName} value={bankName}>{bankName}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.swiftCode')} *</label>
                      <select
                        value={ruleForm.swiftCode || ''}
                        onChange={(e) => {
                          updateRuleForm('swiftCode', e.target.value);
                          // Auto-populate account number if there's only one matching account
                          const matchingAccounts = getAvailableAccounts(ruleForm.bankName, ruleForm.accountCurrency, ruleForm.cashflowCurrency)
                            .filter(acc => acc.swiftCode === e.target.value);
                          if (matchingAccounts.length === 1) {
                            updateRuleForm('accountNumber', matchingAccounts[0].accountNumber);
                          } else {
                            updateRuleForm('accountNumber', '');
                          }
                        }}
                        disabled={!ruleForm.bankName || !ruleForm.accountCurrency}
                      >
                        <option value="">{t('admin.settlement.placeholders.swiftCode')}</option>
                        {getAvailableAccounts(ruleForm.bankName, ruleForm.accountCurrency, ruleForm.cashflowCurrency).map(account => (
                          <option key={account.id} value={account.swiftCode}>
                            {account.swiftCode}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    
                    <div className="form-group">
                      <label>{t('admin.settlement.rules.accountNumber')} *</label>
                      <select
                        value={ruleForm.accountNumber || ''}
                        onChange={(e) => updateRuleForm('accountNumber', e.target.value)}
                        disabled={!ruleForm.bankName || !ruleForm.accountCurrency}
                      >
                        <option value="">{t('admin.settlement.placeholders.accountNumber')}</option>
                        {getAvailableAccounts(ruleForm.bankName, ruleForm.accountCurrency, ruleForm.cashflowCurrency).map(account => (
                          <option key={account.id} value={account.accountNumber}>
                            {account.accountNumber} ({account.accountName})
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                <div className="form-actions">
                  <button className="save-rule-button" onClick={handleSaveRule}>
                    {t('admin.settlement.form.save')}
                  </button>
                  <button className="cancel-rule-button" onClick={handleCancelRule}>
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
                          <button className="save-button" onClick={handleSaveAccount}>✓</button>
                          <button className="cancel-button" onClick={handleCancelAccount}>✗</button>
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
                      <div key={`header-${headerText}`} className="counterparty-group-header">
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
                              //console.log('Rendering dropdown for field:', expectedField.name, 'Available sourceFields:', sourceFields);
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
      
      <div className="admin-actions">
        <button 
          className="save-button primary" 
          onClick={saveConfiguration}
          disabled={isSaving}
        >
          {isSaving ? t('admin.actions.saving') : t('admin.actions.save')}
        </button>
      </div>
      
      <AlertModal
        isOpen={alertModal.isOpen}
        onClose={closeModal}
        title={alertModal.title}
        message={alertModal.message}
        type={alertModal.type}
      />
    </div>
  );
};

export default AdminDashboard;