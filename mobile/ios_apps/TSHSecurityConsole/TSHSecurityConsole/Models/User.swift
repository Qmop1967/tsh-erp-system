import Foundation

// MARK: - User Model (Extended for full management)
struct User: Codable, Identifiable {
    let id: String  // UUID string from production database
    let name: String
    let email: String
    let role: String
    let roleId: Int?
    let branch: String?
    let branchId: Int?
    let phone: String?
    let employeeCode: String?
    let isSalesperson: Bool?
    let isActive: Bool?
    let permissions: [String]
    let mfaEnabled: Bool?
    let mobileApp: String?
    let platform: String?
    let lastLogin: Date?
    let createdAt: Date?
    let updatedAt: Date?

    var isOwner: Bool {
        role.lowercased() == "owner" || role.lowercased() == "admin"
    }

    var isAdmin: Bool {
        ["owner", "admin", "manager"].contains(role.lowercased())
    }

    var statusText: String {
        (isActive ?? true) ? "Active" : "Inactive"
    }

    var statusTextArabic: String {
        (isActive ?? true) ? "نشط" : "غير نشط"
    }

    // Custom CodingKeys to map snake_case from API to camelCase in Swift
    enum CodingKeys: String, CodingKey {
        case id, name, email, role, branch, permissions, platform, phone
        case roleId = "role_id"
        case branchId = "branch_id"
        case employeeCode = "employee_code"
        case isSalesperson = "is_salesperson"
        case isActive = "is_active"
        case mfaEnabled = "mfa_enabled"
        case mobileApp = "mobile_app"
        case lastLogin = "last_login"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }

    // Custom initializer for creating User instances
    init(id: String, name: String, email: String, role: String, branch: String?,
         permissions: [String], mfaEnabled: Bool?, mobileApp: String?, platform: String?,
         roleId: Int? = nil, branchId: Int? = nil, phone: String? = nil,
         employeeCode: String? = nil, isSalesperson: Bool? = nil, isActive: Bool? = nil,
         lastLogin: Date? = nil, createdAt: Date? = nil, updatedAt: Date? = nil) {
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.roleId = roleId
        self.branch = branch
        self.branchId = branchId
        self.phone = phone
        self.employeeCode = employeeCode
        self.isSalesperson = isSalesperson
        self.isActive = isActive
        self.permissions = permissions
        self.mfaEnabled = mfaEnabled
        self.mobileApp = mobileApp
        self.platform = platform
        self.lastLogin = lastLogin
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

// MARK: - Role Model
struct Role: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String?

    var localizedName: String {
        // Map English role names to Arabic
        switch name.lowercased() {
        case "owner": return "المالك"
        case "admin": return "المدير"
        case "manager": return "المشرف"
        case "security": return "الأمن"
        case "travel salesperson": return "مندوب المبيعات المتنقل"
        case "partner salesman": return "شريك المبيعات"
        case "retailerman": return "البائع"
        case "accountant": return "المحاسب"
        case "inventory manager": return "مدير المخزون"
        case "viewer": return "المشاهد"
        default: return name
        }
    }
}

// MARK: - Branch Model
struct Branch: Codable, Identifiable {
    let id: Int
    let name: String
    let code: String?

    enum CodingKeys: String, CodingKey {
        case id, name, code
    }
}

// MARK: - Permission Models

struct Permission: Codable, Identifiable {
    let id: Int
    let name: String
    let description: String?
    let category: String?
    let code: String?
    let module: String?
    let action: String?
    let isActive: Bool

    enum CodingKeys: String, CodingKey {
        case id, name, description, category, code, module, action
        case isActive = "is_active"
    }
}

struct UserPermissionInfo: Codable {
    let permissionId: Int
    let permissionCode: String
    let permissionName: String
    let isGranted: Bool
    let source: String  // "role" or "override"
    let grantedBy: Int?
    let grantedAt: Date?
    let expiresAt: Date?

    enum CodingKeys: String, CodingKey {
        case permissionId = "permission_id"
        case permissionCode = "permission_code"
        case permissionName = "permission_name"
        case isGranted = "is_granted"
        case source
        case grantedBy = "granted_by"
        case grantedAt = "granted_at"
        case expiresAt = "expires_at"
    }
}

struct UserPermissionsResponse: Codable {
    let userId: Int
    let userName: String
    let roleName: String
    let rolePermissions: [Permission]
    let permissionOverrides: [UserPermissionInfo]
    let effectivePermissions: [String]

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case userName = "user_name"
        case roleName = "role_name"
        case rolePermissions = "role_permissions"
        case permissionOverrides = "permission_overrides"
        case effectivePermissions = "effective_permissions"
    }
}

struct GrantPermissionRequest: Encodable {
    let permissionId: Int
    let expiresAt: Date?

    enum CodingKeys: String, CodingKey {
        case permissionId = "permission_id"
        case expiresAt = "expires_at"
    }
}

struct RevokePermissionRequest: Encodable {
    let permissionId: Int

    enum CodingKeys: String, CodingKey {
        case permissionId = "permission_id"
    }
}

struct PermissionActionResponse: Codable {
    let message: String
    let permissionId: Int
    let permissionCode: String
    let userId: Int
    let expiresAt: Date?

    enum CodingKeys: String, CodingKey {
        case message
        case permissionId = "permission_id"
        case permissionCode = "permission_code"
        case userId = "user_id"
        case expiresAt = "expires_at"
    }
}

// MARK: - User CRUD Request/Response Models

struct UserCreateRequest: Encodable {
    let name: String
    let email: String
    let password: String
    let roleId: Int
    let branchId: Int
    let phone: String?
    let employeeCode: String?
    let isSalesperson: Bool
    let isActive: Bool

    enum CodingKeys: String, CodingKey {
        case name, email, password, phone
        case roleId = "role_id"
        case branchId = "branch_id"
        case employeeCode = "employee_code"
        case isSalesperson = "is_salesperson"
        case isActive = "is_active"
    }
}

struct UserUpdateRequest: Encodable {
    var name: String?
    var email: String?
    var roleId: Int?
    var branchId: Int?
    var phone: String?
    var employeeCode: String?
    var isSalesperson: Bool?
    var isActive: Bool?
    var password: String?

    enum CodingKeys: String, CodingKey {
        case name, email, phone, password
        case roleId = "role_id"
        case branchId = "branch_id"
        case employeeCode = "employee_code"
        case isSalesperson = "is_salesperson"
        case isActive = "is_active"
    }

    // Only include non-nil values in the JSON
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        if let name = name { try container.encode(name, forKey: .name) }
        if let email = email { try container.encode(email, forKey: .email) }
        if let roleId = roleId { try container.encode(roleId, forKey: .roleId) }
        if let branchId = branchId { try container.encode(branchId, forKey: .branchId) }
        if let phone = phone { try container.encode(phone, forKey: .phone) }
        if let employeeCode = employeeCode { try container.encode(employeeCode, forKey: .employeeCode) }
        if let isSalesperson = isSalesperson { try container.encode(isSalesperson, forKey: .isSalesperson) }
        if let isActive = isActive { try container.encode(isActive, forKey: .isActive) }
        if let password = password { try container.encode(password, forKey: .password) }
    }
}

struct PasswordResetRequest: Encodable {
    let newPassword: String

    enum CodingKeys: String, CodingKey {
        case newPassword = "new_password"
    }
}

// MARK: - API Response Wrappers

struct UserActionResponse: Decodable {
    let message: String
    let userId: Int?
    let isActive: Bool?
    let deactivated: Bool?

    enum CodingKeys: String, CodingKey {
        case message
        case userId = "user_id"
        case isActive = "is_active"
        case deactivated
    }
}

struct RolesResponse: Decodable {
    let roles: [Role]
}

struct BranchesResponse: Decodable {
    let branches: [Branch]
}

// MARK: - Authentication Models

struct LoginRequest: Encodable {
    let email: String
    let password: String
}

struct LoginResponse: Decodable {
    let access_token: String
    let token_type: String
    let refresh_token: String?
    let user: User
}

struct MFAVerifyRequest: Encodable {
    let code: String
    let temp_token: String
    let user_id: Int
}
