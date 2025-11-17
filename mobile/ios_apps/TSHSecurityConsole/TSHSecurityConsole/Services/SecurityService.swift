import Foundation

actor SecurityService {
    static let shared = SecurityService()

    private init() {}

    func getDashboard() async throws -> DashboardResponse {
        return try await APIClient.shared.request(
            endpoint: "/bff/security/dashboard"
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
            endpoint: "/bff/security/sessions",
            queryParams: params
        )
    }

    func terminateSession(sessionId: String, reason: String) async throws -> APIResponse<[String: AnyCodable]> {
        let params = ["reason": reason]

        return try await APIClient.shared.request(
            endpoint: "/bff/security/sessions/\(sessionId)/terminate",
            method: .POST,
            queryParams: params
        )
    }

    func terminateAllUserSessions(userId: Int, reason: String) async throws -> APIResponse<[String: AnyCodable]> {
        let params = ["reason": reason]

        return try await APIClient.shared.request(
            endpoint: "/bff/security/users/\(userId)/terminate-all-sessions",
            method: .POST,
            queryParams: params
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

        return try await APIClient.shared.request(
            endpoint: "/bff/security/audit-log",
            queryParams: params
        )
    }

    struct UserListResponse: Decodable {
        let users: [User]
        let total: Int
    }

    func getUsers(search: String? = nil, page: Int = 1, pageSize: Int = 50) async throws -> UserListResponse {
        var params = [
            "page": String(page),
            "page_size": String(pageSize)
        ]

        if let search = search, !search.isEmpty {
            params["search"] = search
        }

        return try await APIClient.shared.request(
            endpoint: "/users",
            queryParams: params
        )
    }
}
