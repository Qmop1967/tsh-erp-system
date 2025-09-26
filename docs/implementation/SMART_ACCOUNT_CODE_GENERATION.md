# Smart Account Code Auto-Generation Feature

## Overview
The Chart of Accounts now includes intelligent automatic generation of account codes based on account type and parent account hierarchy, following standard accounting practices.

## Features Implemented

### 🔢 **Account Type Base Codes**
- **Assets (الأصول)**: 1000-1999
- **Liabilities (الخصوم)**: 2000-2999
- **Equity (حقوق الملكية)**: 3000-3999
- **Revenue (الإيرادات)**: 4000-4999
- **Expenses (المصروفات)**: 5000-5999

### 🎯 **Smart Generation Logic**

#### **Top-Level Accounts**
- First account of each type starts at base code (1000, 2000, etc.)
- Subsequent accounts increment by 100 (1100, 1200, 1300...)
- Ensures proper spacing for sub-accounts

#### **Sub-Accounts (Child Accounts)**
- Automatically appends sequential numbers to parent code
- Parent "1100" generates children: "11001", "11002", "11003"...
- Finds next available number in sequence
- Prevents duplicate codes

### ✨ **User Experience Features**

#### **Auto-Generation Triggers**
1. **When Modal Opens**: New account gets initial code based on default type
2. **Account Type Change**: Code updates automatically to match new type
3. **Parent Selection**: Code regenerates based on parent hierarchy
4. **Manual Refresh**: Click refresh icon (🔄) to regenerate

#### **User Control**
- Auto-generated codes can be manually edited
- Helpful tooltip explains the generation logic
- Visual indicators show what influences code generation

## How It Works

### **Example Scenarios**

#### **Creating Top-Level Assets**
1. Select "Assets - الأصول" → Auto-generates: **1000**
2. Create another Asset → Auto-generates: **1100**
3. Create third Asset → Auto-generates: **1200**

#### **Creating Sub-Accounts**
1. Create Asset parent: **1500** "Fixed Assets"
2. Add child with parent 1500 → Auto-generates: **15001**
3. Add another child → Auto-generates: **15002**

#### **Mixed Hierarchy Example**
```
1000 - Current Assets (Top-level)
  10001 - Cash on Hand (Child)
  10002 - Bank Account (Child)
1100 - Inventory (Top-level)
  11001 - Raw Materials (Child)
  11002 - Finished Goods (Child)
    110021 - Product A (Grandchild)
    110022 - Product B (Grandchild)
```

## Technical Implementation

### **Core Functions**
- `generateAccountCode()`: Main logic for code generation
- `handleAccountTypeChange()`: Updates code when type changes
- `handleParentAccountChange()`: Updates code when parent changes

### **Algorithm**
1. Check if parent account is selected
2. If parent exists:
   - Find all existing child accounts
   - Generate next sequential sub-code
3. If no parent (top-level):
   - Find existing accounts of same type
   - Generate next available code (increments of 100)

### **Validation**
- Ensures no duplicate codes
- Handles edge cases (non-numeric codes)
- Maintains proper hierarchy relationships

## Benefits

### 🚀 **For Users**
- **Time Saving**: No manual code calculation needed
- **Error Prevention**: Eliminates duplicate or invalid codes
- **Consistency**: Follows standard accounting practices
- **Flexibility**: Can override auto-generated codes if needed

### 📊 **For Accounting**
- **Standard Compliance**: Follows international chart of accounts structure
- **Scalability**: Supports unlimited account levels
- **Organization**: Clear hierarchical numbering system
- **Reporting**: Simplified account grouping and filtering

## Usage Instructions

### **Creating New Accounts**
1. Click "Add Account" button
2. Select Account Type → Code auto-generates
3. (Optional) Select Parent Account → Code updates
4. Fill in account names and details
5. Review/edit code if needed
6. Click "Create Account"

### **Manual Code Override**
- Edit the auto-generated code directly in the input field
- Click refresh icon (🔄) to regenerate if needed
- System prevents duplicate codes during save

## Future Enhancements

### **Planned Features**
- [ ] Company-specific numbering schemes
- [ ] Import/export account templates
- [ ] Bulk account creation with auto-numbering
- [ ] Custom numbering rules per account type
- [ ] Account code format validation

### **Advanced Options** (Future)
- Custom increment values (50, 10, 1)
- Department-based prefixes
- Integration with external accounting standards
- Multi-company account code isolation

---

## Status: ✅ FULLY IMPLEMENTED

**Last Updated**: January 2025  
**Version**: 1.0  
**Compatibility**: TSH ERP System v1.0+

*This feature is now live and ready for production use. Users can immediately benefit from intelligent account code generation when creating new accounts in the Chart of Accounts.* 