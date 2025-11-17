import Foundation

actor ApprovalService {
    static let shared = ApprovalService()

    private init() {}

    func getPendingApprovals(page: Int = 1, pageSize: Int = 20) async throws -> ApprovalListResponse {
        let params = [
            "page": String(page),
            "page_size": String(pageSize)
        ]

        return try await APIClient.shared.request(
            endpoint: "/auth/owner/pending",
            queryParams: params
        )
    }

    func getAllApprovals(
        status: String? = nil,
        riskLevel: String? = nil,
        page: Int = 1,
        pageSize: Int = 20
    ) async throws -> ApprovalListResponse {
        var params = [
            "page": String(page),
            "page_size": String(pageSize)
        ]

        if let status = status {
            params["status_filter"] = status
        }
        if let riskLevel = riskLevel {
            params["risk_level"] = riskLevel
        }

        return try await APIClient.shared.request(
            endpoint: "/auth/owner/all",
            queryParams: params
        )
    }

    func getApprovalDetails(id: String) async throws -> Approval {
        return try await APIClient.shared.request(
            endpoint: "/auth/owner/\(id)"
        )
    }

    func approveRequest(code: String, reason: String? = nil, biometricVerified: Bool = false) async throws -> ApprovalActionResponse {
        let request = ApproveRequest(
            approval_code: code,
            resolution_reason: reason,
            resolution_reason_ar: nil,
            biometric_verified: biometricVerified
        )

        return try await APIClient.shared.request(
            endpoint: "/auth/owner/approve",
            method: .POST,
            body: request
        )
    }

    func denyRequest(id: String, reason: String) async throws -> ApprovalActionResponse {
        let request = DenyRequest(
            resolution_reason: reason,
            resolution_reason_ar: nil
        )

        return try await APIClient.shared.request(
            endpoint: "/auth/owner/\(id)/deny",
            method: .POST,
            body: request
        )
    }

    func scanQRApprove(payload: String, biometricVerified: Bool = false) async throws -> ApprovalActionResponse {
        let request = QRScanRequest(
            qr_payload: payload,
            biometric_verified: biometricVerified
        )

        return try await APIClient.shared.request(
            endpoint: "/auth/owner/qr/scan",
            method: .POST,
            body: request
        )
    }

    struct ApprovalStats: Decodable {
        let pending: Int
        let approved_today: Int
        let denied_today: Int
        let expired_today: Int
        let average_resolution_time_seconds: Double?
        let by_risk_level: [String: Int]
        let by_type: [String: Int]
    }

    func getStats() async throws -> ApprovalStats {
        return try await APIClient.shared.request(
            endpoint: "/auth/owner/stats/summary"
        )
    }
}
