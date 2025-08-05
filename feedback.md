Compiled with problems:
×
ERROR in src/pages/admin/AdminDashboard.tsx:745:27
TS2345: Argument of type '(prev: BankAccount[]) => (BankAccount | { id?: string | undefined; createdAt?: string | undefined; lastUpdatedAt?: string | undefined; lastUpdatedBy?: string | undefined; ... 6 more ...; isDefault: boolean; })[]' is not assignable to parameter of type 'SetStateAction<BankAccount[]>'.
  Type '(prev: BankAccount[]) => (BankAccount | { id?: string | undefined; createdAt?: string | undefined; lastUpdatedAt?: string | undefined; lastUpdatedBy?: string | undefined; ... 6 more ...; isDefault: boolean; })[]' is not assignable to type '(prevState: BankAccount[]) => BankAccount[]'.
    Type '(BankAccount | { id?: string | undefined; createdAt?: string | undefined; lastUpdatedAt?: string | undefined; lastUpdatedBy?: string | undefined; active: boolean; accountName: string; ... 4 more ...; isDefault: boolean; })[]' is not assignable to type 'BankAccount[]'.
      Type 'BankAccount | { id?: string | undefined; createdAt?: string | undefined; lastUpdatedAt?: string | undefined; lastUpdatedBy?: string | undefined; active: boolean; accountName: string; ... 4 more ...; isDefault: boolean; }' is not assignable to type 'BankAccount'.
        Type '{ id?: string | undefined; createdAt?: string | undefined; lastUpdatedAt?: string | undefined; lastUpdatedBy?: string | undefined; active: boolean; accountName: string; bankName: string; swiftCode: string; accountCurrency: string; accountNumber: string; isDefault: boolean; }' is not assignable to type 'BankAccount'.
          Types of property 'id' are incompatible.
            Type 'string | undefined' is not assignable to type 'string'.
              Type 'undefined' is not assignable to type 'string'.
    743 |
    744 |         if (response.success) {
  > 745 |           setBankAccounts(prev => prev.map(account => 
        |                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  > 746 |             account.id ? account : { ...response.data! }
        | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  > 747 |           ));
        | ^^^^^^^^^^^^
    748 |         }
    749 |       }
    750 |