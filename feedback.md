Compiled with problems:
×
ERROR in src/pages/bank/BankDashboard.tsx:309:11
TS2345: Argument of type '{ documentUrl: string; errorMessage: string; id: string; active: boolean; priority: number; ruleName: string; clientSegment: string; clientSegmentId?: string | undefined; product: string; documentName?: string | undefined; ... 4 more ...; lastUpdatedBy?: string | undefined; }' is not assignable to parameter of type 'SetStateAction<SettlementInstructionLetter | null>'.
  Object literal may only specify known properties, and 'errorMessage' does not exist in type 'SettlementInstructionLetter | ((prevState: SettlementInstructionLetter | null) => SettlementInstructionLetter | null)'.
    307 |           ...letter,
    308 |           documentUrl: 'error',
  > 309 |           errorMessage: response.message || 'Failed to generate preview URL'
        |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    310 |         });
    311 |       }
    312 |     } catch (error) {
ERROR in src/pages/bank/BankDashboard.tsx:318:9
TS2345: Argument of type '{ documentUrl: string; errorMessage: string; id: string; active: boolean; priority: number; ruleName: string; clientSegment: string; clientSegmentId?: string | undefined; product: string; documentName?: string | undefined; ... 4 more ...; lastUpdatedBy?: string | undefined; }' is not assignable to parameter of type 'SetStateAction<SettlementInstructionLetter | null>'.
  Object literal may only specify known properties, and 'errorMessage' does not exist in type 'SettlementInstructionLetter | ((prevState: SettlementInstructionLetter | null) => SettlementInstructionLetter | null)'.
    316 |         ...letter,
    317 |         documentUrl: 'error',
  > 318 |         errorMessage: error instanceof Error ? error.message : 'Failed to generate preview URL'
        |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    319 |       });
    320 |     }
    321 |   };