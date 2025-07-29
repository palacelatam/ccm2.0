import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
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

const AdminDashboard: React.FC = () => {
  const { t } = useTranslation();
  
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

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>{t('admin.title')}</h1>
        <p className="admin-subtitle">{t('admin.subtitle')}</p>
      </div>
      
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
            <h2>{t('admin.mapping.title')}</h2>
            <div className="coming-soon">
              <h3>{t('admin.mapping.title')}</h3>
              <p>{t('admin.mapping.description')}</p>
              <div className="feature-list">
                <ul>
                  <li>{t('admin.mapping.features.columns')}</li>
                  <li>{t('admin.mapping.features.validation')}</li>
                  <li>{t('admin.mapping.features.transformation')}</li>
                  <li>{t('admin.mapping.features.templates')}</li>
                </ul>
              </div>
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