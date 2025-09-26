# Enhanced Security and Backup Management
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
import aiofiles
import hashlib
import json
import subprocess
import shutil
import os
from pathlib import Path
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.models.permissions import AuditLog
from app.services.permission_service import PermissionService

class SecurityService:
    """Enhanced security service with encryption and monitoring"""
    
    def __init__(self, db: Session, encryption_key: Optional[bytes] = None):
        self.db = db
        self.permission_service = PermissionService(db)
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # Load from environment or generate
            key_file = Path("config/encryption.key")
            if key_file.exists():
                with open(key_file, "rb") as f:
                    self.cipher = Fernet(f.read())
            else:
                key = Fernet.generate_key()
                with open(key_file, "wb") as f:
                    f.write(key)
                self.cipher = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt"""
        if not salt:
            salt = os.urandom(32).hex()
        
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          password.encode('utf-8'), 
                                          salt.encode('utf-8'), 
                                          100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """Verify password against hash"""
        password_hash, _ = self.hash_password(password, salt)
        return password_hash == hash_value
    
    def detect_suspicious_activity(self, user_id: int, action: str, 
                                 ip_address: str) -> Dict[str, Any]:
        """Detect suspicious activities"""
        # Check for rapid successive logins
        recent_logins = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login",
            AuditLog.timestamp > datetime.utcnow() - timedelta(minutes=5)
        ).count()
        
        # Check for login from multiple IPs
        unique_ips = self.db.query(AuditLog.ip_address).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login",
            AuditLog.timestamp > datetime.utcnow() - timedelta(hours=1)
        ).distinct().count()
        
        # Check for failed login attempts
        failed_attempts = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == "login_failed",
            AuditLog.timestamp > datetime.utcnow() - timedelta(minutes=15)
        ).count()
        
        risk_score = 0
        alerts = []
        
        if recent_logins > 5:
            risk_score += 30
            alerts.append("Multiple rapid login attempts")
        
        if unique_ips > 3:
            risk_score += 40
            alerts.append("Login from multiple IP addresses")
        
        if failed_attempts > 3:
            risk_score += 50
            alerts.append("Multiple failed login attempts")
        
        return {
            "risk_score": risk_score,
            "alerts": alerts,
            "action_required": risk_score > 50
        }

class EnhancedBackupService:
    """Enhanced backup service with encryption, scheduling, and verification"""
    
    def __init__(self, db: Session, backup_dir: str = "backups"):
        self.db = db
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.permission_service = PermissionService(db)
        self.security_service = SecurityService(db)
    
    async def create_encrypted_backup(self, user_id: int, backup_type: str = "full",
                                    include_files: bool = True) -> Dict[str, Any]:
        """Create encrypted backup with verification"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"tsh_erp_{backup_type}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        try:
            # Database backup
            db_backup_file = backup_path / "database.sql"
            await self._backup_database(db_backup_file)
            
            # Configuration backup
            config_backup = backup_path / "config"
            config_backup.mkdir(exist_ok=True)
            await self._backup_configuration(config_backup)
            
            # File system backup (if requested)
            if include_files:
                files_backup = backup_path / "files"
                files_backup.mkdir(exist_ok=True)
                await self._backup_files(files_backup)
            
            # Create manifest
            manifest = await self._create_backup_manifest(backup_path)
            
            # Encrypt backup
            encrypted_file = await self._encrypt_backup(backup_path, backup_name)
            
            # Verify backup integrity
            verification_result = await self._verify_backup(encrypted_file)
            
            # Clean up unencrypted files
            shutil.rmtree(backup_path)
            
            # Log backup creation
            self.permission_service.log_action(
                user_id=user_id,
                action="create_backup",
                resource_type="backup",
                resource_id=backup_name,
                new_values=manifest
            )
            
            return {
                "backup_name": backup_name,
                "backup_file": str(encrypted_file),
                "size": encrypted_file.stat().st_size,
                "manifest": manifest,
                "verification": verification_result,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Clean up on failure
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise e
    
    async def _backup_database(self, output_file: Path):
        """Backup database to SQL file"""
        # Assuming PostgreSQL
        cmd = [
            "pg_dump",
            "-h", os.getenv("DB_HOST", "localhost"),
            "-p", os.getenv("DB_PORT", "5432"),
            "-U", os.getenv("DB_USER", "postgres"),
            "-d", os.getenv("DB_NAME", "tsh_erp"),
            "-f", str(output_file),
            "--no-password"
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = os.getenv("DB_PASSWORD", "")
        
        process = await asyncio.create_subprocess_exec(
            *cmd, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Database backup failed: {stderr.decode()}")
    
    async def _backup_configuration(self, config_dir: Path):
        """Backup configuration files"""
        config_files = [
            "config/requirements.txt",
            ".env",
            "app/config/zoho_config.py"
        ]
        
        for config_file in config_files:
            src = Path(config_file)
            if src.exists():
                dst = config_dir / src.name
                shutil.copy2(src, dst)
    
    async def _backup_files(self, files_dir: Path):
        """Backup important files and uploads"""
        # Backup uploaded files, documents, etc.
        upload_dirs = ["uploads", "documents", "exports"]
        
        for upload_dir in upload_dirs:
            src_dir = Path(upload_dir)
            if src_dir.exists():
                dst_dir = files_dir / upload_dir
                shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns("*.tmp"))
    
    async def _create_backup_manifest(self, backup_path: Path) -> Dict[str, Any]:
        """Create backup manifest with checksums"""
        manifest = {
            "version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "files": {}
        }
        
        for file_path in backup_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(backup_path)
                file_hash = await self._calculate_file_hash(file_path)
                manifest["files"][str(relative_path)] = {
                    "size": file_path.stat().st_size,
                    "checksum": file_hash,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
        
        # Save manifest
        manifest_file = backup_path / "manifest.json"
        async with aiofiles.open(manifest_file, "w") as f:
            await f.write(json.dumps(manifest, indent=2))
        
        return manifest
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            async for chunk in self._file_chunks(f):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _file_chunks(self, file_obj, chunk_size: int = 8192):
        """Generate file chunks for hashing"""
        while True:
            chunk = await file_obj.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    async def _encrypt_backup(self, backup_path: Path, backup_name: str) -> Path:
        """Encrypt backup directory into single file"""
        # Create tar.gz first
        archive_path = self.backup_dir / f"{backup_name}.tar.gz"
        
        process = await asyncio.create_subprocess_exec(
            "tar", "-czf", str(archive_path), "-C", str(backup_path.parent), backup_path.name,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if process.returncode != 0:
            raise Exception("Failed to create backup archive")
        
        # Encrypt the archive
        encrypted_path = self.backup_dir / f"{backup_name}.tar.gz.enc"
        
        async with aiofiles.open(archive_path, "rb") as src:
            encrypted_data = self.security_service.cipher.encrypt(await src.read())
            
        async with aiofiles.open(encrypted_path, "wb") as dst:
            await dst.write(encrypted_data)
        
        # Remove unencrypted archive
        archive_path.unlink()
        
        return encrypted_path
    
    async def _verify_backup(self, backup_file: Path) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            # Check if file exists and is readable
            if not backup_file.exists():
                return {"valid": False, "error": "Backup file not found"}
            
            # Try to decrypt and read manifest
            async with aiofiles.open(backup_file, "rb") as f:
                encrypted_data = await f.read()
            
            decrypted_data = self.security_service.cipher.decrypt(encrypted_data)
            
            # Basic validation - check if it's a valid tar.gz
            if not decrypted_data.startswith(b'\x1f\x8b'):  # gzip magic number
                return {"valid": False, "error": "Invalid backup format"}
            
            return {
                "valid": True,
                "size": len(decrypted_data),
                "checksum": hashlib.sha256(decrypted_data).hexdigest()
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def schedule_backup(self, user_id: int, schedule: Dict[str, Any]) -> bool:
        """Schedule automatic backups"""
        # This would integrate with a task scheduler like Celery
        # For now, just log the schedule request
        self.permission_service.log_action(
            user_id=user_id,
            action="schedule_backup",
            resource_type="backup",
            resource_id="scheduler",
            new_values=schedule
        )
        return True
    
    async def restore_backup(self, user_id: int, backup_file: str, 
                           approver_ids: List[int]) -> Dict[str, Any]:
        """Restore from encrypted backup with multi-person approval"""
        # Check if user has restore permission
        if not self.permission_service.check_permission(user_id, "restore_backup"):
            raise Exception("Insufficient permissions for backup restoration")
        
        # Verify approvers have appropriate permissions
        for approver_id in approver_ids:
            if not self.permission_service.check_permission(approver_id, "approve_restore"):
                raise Exception(f"Approver {approver_id} lacks restore approval permission")
        
        backup_path = self.backup_dir / backup_file
        if not backup_path.exists():
            raise Exception("Backup file not found")
        
        # Log restore initiation
        self.permission_service.log_action(
            user_id=user_id,
            action="initiate_restore",
            resource_type="backup",
            resource_id=backup_file,
            new_values={"approvers": approver_ids}
        )
        
        # In a real implementation, this would:
        # 1. Create restore request requiring approvals
        # 2. Wait for all approvals
        # 3. Perform actual restore
        # 4. Verify restore success
        
        return {
            "restore_id": f"restore_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "pending_approval",
            "required_approvers": len(approver_ids),
            "approved_by": []
        }
