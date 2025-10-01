# 🗑️ TSH ERP System - Legacy Apps Archive

## Purpose
This directory contains archived Flutter apps that have been:
- Replaced by newer versions
- Merged into other apps
- Deprecated due to business requirements changes

## Archived Apps

### tsh_travel_app_merged
**Reason:** Merged with tsh_salesperson_app  
**Date:** September 30, 2025  
**New Location:** `mobile/flutter_apps/05_tsh_salesperson_app`  
**Notes:** Travel salesperson features now integrated into unified salesperson app

### salesperson_old_duplicate
**Reason:** Duplicate of tsh_salesperson_app  
**Date:** September 30, 2025  
**Notes:** Older version, replaced by iOS-configured version

### inventory_app_legacy
**Reason:** Replaced by inventory_app_new  
**Date:** Previous migration  
**New Location:** `mobile/flutter_apps/03_tsh_inventory_app`

### hr_app_legacy
**Reason:** Replaced by current hr_app  
**Date:** Previous migration  
**New Location:** `mobile/flutter_apps/02_tsh_hr_app`

## Restore Procedure

If you need to restore or reference any archived app:

1. **Review the app structure:**
   ```bash
   cd mobile/legacy/[app_name]
   cat README.md  # if exists
   ```

2. **Check for useful code:**
   - Review lib/ directory for reusable components
   - Check for unique features not in current version
   - Review documentation

3. **Extract needed code:**
   - Copy specific files/features to current app
   - Update dependencies if needed
   - Test thoroughly

4. **Full restore (not recommended):**
   ```bash
   cp -R mobile/legacy/[app_name] mobile/flutter_apps/
   cd mobile/flutter_apps/[app_name]
   flutter pub get
   flutter run
   ```

## Important Notes

- **Do NOT delete** without thorough review
- Apps may contain unique features or code
- Useful for historical reference
- Can contain important business logic
- May be needed for data migration

## Archive Policy

Apps are moved to legacy when:
- Replaced by newer version with feature parity
- Merged into another app (features combined)
- No longer needed for business requirements
- Incomplete/broken beyond repair
- Duplicate of existing app

## Retention

- Keep for minimum 1 year after archiving
- Review annually for permanent deletion
- Maintain backup of backup location
- Document any permanent deletions

---

**Archive Created:** September 30, 2025  
**Review Due:** September 30, 2026
