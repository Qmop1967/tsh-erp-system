#!/usr/bin/env python3
"""
Apply Async Context Fix to All Remaining Handlers

This script automatically fixes all remaining entity handlers by:
1. Replacing "await self.db.execute" with "await self.execute_with_context"
2. Removing "await self.db.commit()" statements
3. Removing "await self.db.rollback()" in exception handlers

Run: python3 scripts/apply_async_context_fix.py
"""

import re

file_path = "app/background/zoho_entity_handlers.py"

print("🔧 Applying async context fixes to remaining handlers...")
print("=" * 80)

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

original_content = content

# Track changes
changes = []

# Fix Pattern 1: Direct execute with result assignment and commit
# Example: result = await self.db.execute(...) followed by await self.db.commit()
pattern1 = re.compile(
    r'(\s+)(result = await self\.db\.execute\()',
    re.MULTILINE
)

def fix_execute_calls(content):
    """Replace all self.db.execute with self.execute_with_context (except in BaseEntityHandler)"""
    lines = content.split('\n')
    fixed_lines = []
    in_base_handler = False

    for i, line in enumerate(lines):
        # Track if we're in BaseEntityHandler (skip those)
        if 'class BaseEntityHandler' in line:
            in_base_handler = True
        elif re.match(r'class \w+Handler\(BaseEntityHandler\):', line):
            in_base_handler = False

        # Fix execute calls outside BaseEntityHandler
        if not in_base_handler and 'await self.db.execute(' in line:
            if 'self.execute_with_context(' not in line:  # Don't fix if already fixed
                # Add comment before the line if not already there
                if i > 0 and '# ✅ FIX:' not in lines[i-1]:
                    indent = len(line) - len(line.lstrip())
                    comment = ' ' * indent + '# ✅ FIX: Use execute_with_context for proper async transaction handling'
                    fixed_lines.append(comment)

                # Replace the execute call
                fixed_line = line.replace('await self.db.execute(', 'await self.execute_with_context(')
                fixed_lines.append(fixed_line)
                changes.append(f"Line {i+1}: Replaced self.db.execute with self.execute_with_context")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)

# Apply the fix
content = fix_execute_calls(content)

# Fix Pattern 2: Remove all "await self.db.commit()" lines (except in BaseEntityHandler)
lines = content.split('\n')
fixed_lines = []
in_base_handler = False
i = 0

while i < len(lines):
    line = lines[i]

    # Track BaseEntityHandler
    if 'class BaseEntityHandler' in line:
        in_base_handler = True
    elif re.match(r'class \w+Handler\(BaseEntityHandler\):', line):
        in_base_handler = False

    # Remove commit statements outside BaseEntityHandler
    if not in_base_handler and 'await self.db.commit()' in line and line.strip() == 'await self.db.commit()':
        # Add comment instead
        indent = len(line) - len(line.lstrip())
        comment = ' ' * indent + '# ✅ No manual commit needed - auto-commits on context exit'
        fixed_lines.append(comment)
        changes.append(f"Line {i+1}: Removed await self.db.commit()")
        i += 1
        continue

    fixed_lines.append(line)
    i += 1

content = '\n'.join(fixed_lines)

# Fix Pattern 3: Remove "await self.db.rollback()" in exception handlers
lines = content.split('\n')
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]

    # Remove rollback statements
    if 'await self.db.rollback()' in line and line.strip() == 'await self.db.rollback()':
        # Check if previous line was "except Exception as e:"
        if i > 0 and 'except Exception as e:' in lines[i-1]:
            # Add comment instead
            indent = len(line) - len(line.lstrip())
            comment = ' ' * indent + '# ✅ No manual rollback needed - context manager handles it automatically'
            fixed_lines.append(comment)
            changes.append(f"Line {i+1}: Removed await self.db.rollback()")
            i += 1
            continue

    fixed_lines.append(line)
    i += 1

content = '\n'.join(fixed_lines)

# Write back if changes were made
if content != original_content:
    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✅ Applied {len(changes)} changes to {file_path}")
    print("\n📝 Changes made:")
    for change in changes[:10]:  # Show first 10 changes
        print(f"   - {change}")
    if len(changes) > 10:
        print(f"   ... and {len(changes) - 10} more changes")
else:
    print("ℹ️  No changes needed - all handlers already fixed!")

print("\n" + "=" * 80)
print("✅ Async context fix complete!")
print("\n🎯 Next step: Test webhook processing")
print("   Run: python3 scripts/test_webhook_fix.py")
