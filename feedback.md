Compiled with problems:
×
ERROR in ./src/pages/bank/BankDashboard.tsx
Module build failed (from ./node_modules/babel-loader/lib/index.js):
SyntaxError: C:\Users\bencl\Proyectos\ccm2.0\frontend\src\pages\bank\BankDashboard.tsx: Identifier 'hasUnsavedChanges' has already been declared. (718:8)

  716 |   };
  717 |
> 718 |   const hasUnsavedChanges = Object.keys(pendingChanges).length > 0;
      |         ^
  719 |
  720 |
  721 |   // Filter clients based on search query
    at constructor (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:367:19)
    at TypeScriptParserMixin.raise (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:6627:19)
    at TypeScriptScopeHandler.checkRedeclarationInScope (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:1644:19)
    at TypeScriptScopeHandler.declareName (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:1610:12)
    at TypeScriptScopeHandler.declareName (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:4910:11)
    at TypeScriptParserMixin.declareNameFromIdentifier (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:7591:16)
    at TypeScriptParserMixin.checkIdentifier (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:7587:12)
    at TypeScriptParserMixin.checkLVal (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:7526:12)
    at TypeScriptParserMixin.parseVarId (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13412:10)
    at TypeScriptParserMixin.parseVarId (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9767:11)
    at TypeScriptParserMixin.parseVar (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13383:12)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13230:10)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9493:31)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12851:23)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9527:18)
    at TypeScriptParserMixin.parseStatementLike (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12767:17)
    at TypeScriptParserMixin.parseStatementListItem (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12747:17)
    at TypeScriptParserMixin.parseBlockOrModuleBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13316:61)
    at TypeScriptParserMixin.parseBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13309:10)
    at TypeScriptParserMixin.parseBlock (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13297:10)
    at TypeScriptParserMixin.parseFunctionBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12101:24)
    at TypeScriptParserMixin.parseArrowExpression (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12076:10)
    at TypeScriptParserMixin.parseParenAndDistinguishExpression (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11686:12)
    at TypeScriptParserMixin.parseExprAtom (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11326:23)
    at TypeScriptParserMixin.parseExprAtom (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:4794:20)
    at TypeScriptParserMixin.parseExprSubscripts (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11076:23)
    at TypeScriptParserMixin.parseUpdate (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11061:21)
    at TypeScriptParserMixin.parseMaybeUnary (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11041:23)
    at TypeScriptParserMixin.parseMaybeUnary (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9852:18)
    at TypeScriptParserMixin.parseMaybeUnaryOrPrivate (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10894:61)
    at TypeScriptParserMixin.parseExprOps (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10899:23)
    at TypeScriptParserMixin.parseMaybeConditional (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10876:23)
    at TypeScriptParserMixin.parseMaybeAssign (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10826:21)
    at TypeScriptParserMixin.parseMaybeAssign (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9801:20)
    at C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10795:39
    at TypeScriptParserMixin.allowInAnd (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12422:16)
    at TypeScriptParserMixin.parseMaybeAssignAllowIn (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10795:17)
    at TypeScriptParserMixin.parseVar (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13384:91)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13230:10)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9493:31)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12851:23)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9527:18)
    at TypeScriptParserMixin.parseStatementLike (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12767:17)
    at TypeScriptParserMixin.parseModuleItem (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12744:17)
    at TypeScriptParserMixin.parseBlockOrModuleBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13316:36)
    at TypeScriptParserMixin.parseBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13309:10)
    at TypeScriptParserMixin.parseProgram (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12625:10)
    at TypeScriptParserMixin.parseTopLevel (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12615:25)
    at TypeScriptParserMixin.parse (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:14492:10)
    at TypeScriptParserMixin.parse (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10144:18)
ERROR in ./src/pages/bank/BankDashboard.tsx
Module build failed (from ./node_modules/babel-loader/lib/index.js):
SyntaxError: C:\Users\bencl\Proyectos\ccm2.0\frontend\src\pages\bank\BankDashboard.tsx: Identifier 'hasUnsavedChanges' has already been declared. (718:8)

  716 |   };
  717 |
> 718 |   const hasUnsavedChanges = Object.keys(pendingChanges).length > 0;
      |         ^
  719 |
  720 |
  721 |   // Filter clients based on search query
    at constructor (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:367:19)
    at TypeScriptParserMixin.raise (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:6627:19)
    at TypeScriptScopeHandler.checkRedeclarationInScope (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:1644:19)
    at TypeScriptScopeHandler.declareName (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:1610:12)
    at TypeScriptScopeHandler.declareName (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:4910:11)
    at TypeScriptParserMixin.declareNameFromIdentifier (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:7591:16)
    at TypeScriptParserMixin.checkIdentifier (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:7587:12)
    at TypeScriptParserMixin.checkLVal (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:7526:12)
    at TypeScriptParserMixin.parseVarId (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13412:10)
    at TypeScriptParserMixin.parseVarId (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9767:11)
    at TypeScriptParserMixin.parseVar (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13383:12)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13230:10)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9493:31)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12851:23)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9527:18)
    at TypeScriptParserMixin.parseStatementLike (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12767:17)
    at TypeScriptParserMixin.parseStatementListItem (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12747:17)
    at TypeScriptParserMixin.parseBlockOrModuleBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13316:61)
    at TypeScriptParserMixin.parseBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13309:10)
    at TypeScriptParserMixin.parseBlock (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13297:10)
    at TypeScriptParserMixin.parseFunctionBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12101:24)
    at TypeScriptParserMixin.parseArrowExpression (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12076:10)
    at TypeScriptParserMixin.parseParenAndDistinguishExpression (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11686:12)
    at TypeScriptParserMixin.parseExprAtom (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11326:23)
    at TypeScriptParserMixin.parseExprAtom (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:4794:20)
    at TypeScriptParserMixin.parseExprSubscripts (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11076:23)
    at TypeScriptParserMixin.parseUpdate (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11061:21)
    at TypeScriptParserMixin.parseMaybeUnary (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:11041:23)
    at TypeScriptParserMixin.parseMaybeUnary (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9852:18)
    at TypeScriptParserMixin.parseMaybeUnaryOrPrivate (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10894:61)
    at TypeScriptParserMixin.parseExprOps (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10899:23)
    at TypeScriptParserMixin.parseMaybeConditional (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10876:23)
    at TypeScriptParserMixin.parseMaybeAssign (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10826:21)
    at TypeScriptParserMixin.parseMaybeAssign (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9801:20)
    at C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10795:39
    at TypeScriptParserMixin.allowInAnd (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12422:16)
    at TypeScriptParserMixin.parseMaybeAssignAllowIn (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10795:17)
    at TypeScriptParserMixin.parseVar (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13384:91)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13230:10)
    at TypeScriptParserMixin.parseVarStatement (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9493:31)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12851:23)
    at TypeScriptParserMixin.parseStatementContent (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:9527:18)
    at TypeScriptParserMixin.parseStatementLike (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12767:17)
    at TypeScriptParserMixin.parseModuleItem (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12744:17)
    at TypeScriptParserMixin.parseBlockOrModuleBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13316:36)
    at TypeScriptParserMixin.parseBlockBody (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:13309:10)
    at TypeScriptParserMixin.parseProgram (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12625:10)
    at TypeScriptParserMixin.parseTopLevel (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:12615:25)
    at TypeScriptParserMixin.parse (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:14492:10)
    at TypeScriptParserMixin.parse (C:\Users\bencl\Proyectos\ccm2.0\frontend\node_modules\@babel\parser\lib\index.js:10144:18)
ERROR in src/pages/bank/BankDashboard.tsx:95:10
TS2451: Cannot redeclare block-scoped variable 'hasUnsavedChanges'.
    93 |   
    94 |   // Unsaved changes tracking
  > 95 |   const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
       |          ^^^^^^^^^^^^^^^^^
    96 |   const [pendingTabChange, setPendingTabChange] = useState<string | null>(null);
    97 |   const [showUnsavedChangesModal, setShowUnsavedChangesModal] = useState(false);
    98 |   
ERROR in src/pages/bank/BankDashboard.tsx:718:9
TS2451: Cannot redeclare block-scoped variable 'hasUnsavedChanges'.
    716 |   };
    717 |
  > 718 |   const hasUnsavedChanges = Object.keys(pendingChanges).length > 0;
        |         ^^^^^^^^^^^^^^^^^
    719 |
    720 |
    721 |   // Filter clients based on search query