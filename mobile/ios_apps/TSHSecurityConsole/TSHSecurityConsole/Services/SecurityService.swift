import Foundation

actor SecurityService {
    static let shared = SecurityService()

    private init() {}

    func getDashboard() async throws -> DashboardResponse {
        return try await APIClient.shared.request(
            endpoint: "/bff/mobile/security/dashboard"
        )
    }

    func getActiveSessions(
        userId: Int? = nil,
        deviceType: String? = nil,
        page: Int = 1,
        pageSize: Int = 100
    ) async throws -> APIResponse<SessionListResponse> {
        var params = [
            "page": String(page),
            "page_size": String(pageSize)
        ]

        if let userId = userId {
            params["user_id"] = String(userId)
        }
        if let deviceType = deviceType {
            params["device_type"] = deviceType
        }

        return try await APIClient.shared.request(
            endpoint: "/bff/mobile/security/sessions",
            queryParams: params
        )
    }

    func terminateSession(sessionId: String, reason: String) async throws -> APIResponse<[String: AnyCodable]> {
        let params = ["reason": reason]
        return try await APIClient.shared.request(
            endpoint: "/bff/mobile/security/sessions/\(sessionId)/terminate",
            method: .POST,
            queryParams: params
        )
    }

    func terminateAllUserSessions(userId: Int, reason: String) async throws -> APIResponse<[String: AnyCodable]> {
        // Use standard auth terminate all sessions
        return try await APIClient.shared.request(
            endpoint: "/auth/sessions/terminate-all",
            method: .POST
        )
    }

    struct AuditLogResponse: Decodable {
        let entries: [[String: AnyCodable]]
        let total: Int
        let page: Int
        let page_size: Int
    }

    func getAuditLog(
        eventType: String? = nil,
        severity: String? = nil,
        dateFrom: String? = nil,
        dateTo: String? = nil,
        page: Int = 1,
        pageSize: Int = 100
    ) async throws -> APIResponse<AuditLogResponse> {
        var params = [
            "page": String(page),
            "page_size": String(pageSize)
        ]

        if let eventType = eventType {
            params["event_type"] = eventType
        }
        if let severity = severity {
            params["severity"] = severity
        }
        if let dateFrom = dateFrom {
            params["date_from"] = dateFrom
        }
        if let dateTo = dateTo {
            params["date_to"] = dateTo
        }

        // Use standard auth audit log endpoint
        return try await APIClient.shared.request(
            endpoint: "/auth/audit-log",
            queryParams: params
        )
    }

    // Response format from production /users endpoint
    struct ProductionUserListResponse: Decodable {
        let data: [ProductionUser]
        let total: Int
        let page: Int
        let pages: Int
        let per_page: Int
    }

    // User format from production database (different from auth User)
    struct ProductionUser: Decodable {
        let id: DynamicID  // Can be Int or String (UUID)
        let name: String
        let email: String
        let role_id: Int?
        let branch_id: Int?
        let employee_code: String?
        let phone: String?
        let is_salesperson: Bool?
        let is_active: Bool?
        let created_at: String?
        let updated_at: String?
        let last_login: String?
        let role: String
        let branch: String
    }

    // Helper to handle both Int and String IDs
    enum DynamicID: Decodable {
        case int(Int)
        case string(String)

        init(from decoder: Decoder) throws {
            let container = try decoder.singleValueContainer()
            if let intValue = try? container.decode(Int.self) {
                self = .int(intValue)
            } else if let stringValue = try? container.decode(String.self) {
                self = .string(stringValue)
            } else {
                throw DecodingError.typeMismatch(DynamicID.self, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Expected Int or String"))
            }
        }

        var stringValue: String {
            switch self {
            case .int(let value): return String(value)
            case .string(let value): return value
            }
        }
    }

    struct UserListResponse: Decodable {
        let users: [User]
        let total: Int
    }

    func getUsers(search: String? = nil, page: Int = 1, pageSize: Int = 50) async throws -> UserListResponse {
        var params = [
            "skip": String((page - 1) * pageSize),  // Backend uses skip/limit, not page/page_size
            "limit": String(pageSize)
        ]

        // Note: Production API doesn't support search parameter in GET /users
        // if let search = search, !search.isEmpty {
        //     params["search"] = search
        // }

        let response: ProductionUserListResponse = try await APIClient.shared.request(
            endpoint: "/users/",  // Trailing slash required to avoid 307 redirect
            queryParams: params
        )

        // Convert ProductionUser to User model used by the app (with all fields now)
        let users = response.data.map { prodUser in
            User(
                id: prodUser.id.stringValue,
                name: prodUser.name,
                email: prodUser.email,
                role: prodUser.role,
                branch: prodUser.branch,
                permissions: [],  // Not available from list endpoint
                mfaEnabled: nil,
                mobileApp: nil,
                platform: nil,
                roleId: prodUser.role_id,
                branchId: prodUser.branch_id,
                phone: prodUser.phone,
                employeeCode: prodUser.employee_code,
                isSalesperson: prodUser.is_salesperson,
                isActive: prodUser.is_active,
                lastLogin: parseDate(prodUser.last_login),
                createdAt: parseDate(prodUser.created_at),
                updatedAt: parseDate(prodUser.updated_at)
            )
        }

        return UserListResponse(users: users, total: response.total)
    }

    // MARK: - User CRUD Operations

    /// Get single user by ID
    func getUser(id: Int) async throws -> User {
        let response: ProductionUser = try await APIClient.shared.request(
            endpoint: "/users/\(id)/"
        )

        return User(
            id: response.id.stringValue,
            name: response.name,
            email: response.email,
            role: response.role,
            branch: response.branch,
            permissions: [],
            mfaEnabled: nil,
            mobileApp: nil,
            platform: nil,
            roleId: response.role_id,
            branchId: response.branch_id,
            phone: response.phone,
            employeeCode: response.employee_code,
            isSalesperson: response.is_salesperson,
            isActive: response.is_active,
            lastLogin: parseDate(response.last_login),
            createdAt: parseDate(response.created_at),
            updatedAt: parseDate(response.updated_at)
        )
    }

    /// Create new user
    func createUser(_ request: UserCreateRequest) async throws -> User {
        let response: ProductionUser = try await APIClient.shared.request(
            endpoint: "/users/",
            method: .POST,
            body: request
        )

        return User(
            id: response.id.stringValue,
            name: response.name,
            email: response.email,
            role: response.role,
            branch: response.branch,
            permissions: [],
            mfaEnabled: nil,
            mobileApp: nil,
            platform: nil,
            roleId: response.role_id,
            branchId: response.branch_id,
            phone: response.phone,
            employeeCode: response.employee_code,
            isSalesperson: response.is_salesperson,
            isActive: response.is_active,
            lastLogin: nil,
            createdAt: parseDate(response.created_at),
            updatedAt: nil
        )
    }

    /// Update existing user
    func updateUser(id: Int, _ request: UserUpdateRequest) async throws -> User {
        let response: ProductionUser = try await APIClient.shared.request(
            endpoint: "/users/\(id)/",
            method: .PUT,
            body: request
        )

        return User(
            id: response.id.stringValue,
            name: response.name,
            email: response.email,
            role: response.role,
            branch: response.branch,
            permissions: [],
            mfaEnabled: nil,
            mobileApp: nil,
            platform: nil,
            roleId: response.role_id,
            branchId: response.branch_id,
            phone: response.phone,
            employeeCode: response.employee_code,
            isSalesperson: response.is_salesperson,
            isActive: response.is_active,
            lastLogin: parseDate(response.last_login),
            createdAt: parseDate(response.created_at),
            updatedAt: parseDate(response.updated_at)
        )
    }

    /// Delete (deactivate) user
    func deleteUser(id: Int) async throws -> UserActionResponse {
        return try await APIClient.shared.request(
            endpoint: "/users/\(id)",
            method: .DELETE
        )
    }

    /// Activate user
    func activateUser(id: Int) async throws -> UserActionResponse {
        return try await APIClient.shared.request(
            endpoint: "/users/\(id)/activate",
            method: .PUT
        )
    }

    /// Deactivate user
    func deactivateUser(id: Int) async throws -> UserActionResponse {
        return try await APIClient.shared.request(
            endpoint: "/users/\(id)/deactivate",
            method: .PUT
        )
    }

    /// Reset user password
    func resetUserPassword(id: Int, newPassword: String) async throws -> UserActionResponse {
        let request = PasswordResetRequest(newPassword: newPassword)
        return try await APIClient.shared.request(
            endpoint: "/users/\(id)/reset-password",
            method: .POST,
            body: request
        )
    }

    // MARK: - Roles and Branches

    /// Get all available roles
    func getRoles() async throws -> [Role] {
        let response: [RoleData] = try await APIClient.shared.request(
            endpoint: "/users/roles/"
        )
        return response.map { Role(id: $0.id, name: $0.name, description: nil) }
    }

    struct RoleData: Decodable {
        let id: Int
        let name: String
    }

    /// Get all available branches
    func getBranches() async throws -> [Branch] {
        let response: [BranchData] = try await APIClient.shared.request(
            endpoint: "/users/branches/"
        )
        return response.map { Branch(id: $0.id, name: $0.name, code: $0.code) }
    }

    struct BranchData: Decodable {
        let id: Int
        let name: String
        let code: String?
    }

    // MARK: - Helper Methods

    private func parseDate(_ dateString: String?) -> Date? {
        guard let dateString = dateString else { return nil }

        let formatters = [
            ISO8601DateFormatter(),
            {
                let f = DateFormatter()
                f.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
                return f
            }(),
            {
                let f = DateFormatter()
                f.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
                return f
            }()
        ]

        for formatter in formatters {
            if let isoFormatter = formatter as? ISO8601DateFormatter {
                if let date = isoFormatter.date(from: dateString) {
                    return date
                }
            } else if let dateFormatter = formatter as? DateFormatter {
                if let date = dateFormatter.date(from: dateString) {
                    return date
                }
            }
        }
        return nil
    }

    // MARK: - Permission Management

    /// Get all available permissions
    func getAllPermissions() async throws -> [Permission] {
        return try await APIClient.shared.request(
            endpoint: "/permissions/"
        )
    }

    /// Get user's permissions (role + overrides)
    func getUserPermissions(userId: Int) async throws -> UserPermissionsResponse {
        return try await APIClient.shared.request(
            endpoint: "/permissions/users/\(userId)"
        )
    }

    /// Grant permission to user
    func grantPermission(userId: Int, permissionId: Int, expiresAt: Date? = nil) async throws -> PermissionActionResponse {
        let request = GrantPermissionRequest(permissionId: permissionId, expiresAt: expiresAt)
        return try await APIClient.shared.request(
            endpoint: "/permissions/users/\(userId)/grant",
            method: .POST,
            body: request
        )
    }

    /// Revoke permission from user
    func revokePermission(userId: Int, permissionId: Int) async throws -> PermissionActionResponse {
        let request = RevokePermissionRequest(permissionId: permissionId)
        return try await APIClient.shared.request(
            endpoint: "/permissions/users/\(userId)/revoke",
            method: .POST,
            body: request
        )
    }

    /// Remove permission override (revert to role-based)
    func removePermissionOverride(userId: Int, permissionId: Int) async throws -> [String: AnyCodable] {
        return try await APIClient.shared.request(
            endpoint: "/permissions/users/\(userId)/overrides/\(permissionId)",
            method: .DELETE
        )
    }
}
