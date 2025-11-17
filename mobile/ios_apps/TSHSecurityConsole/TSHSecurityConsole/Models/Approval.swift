import Foundation

struct Approval: Codable, Identifiable {
    let id: String
    let requester: RequesterInfo
    let approval_type: ApprovalType
    let risk_level: RiskLevel
    let status: ApprovalStatus
    let method: ApprovalMethod
    let request_description: String
    let request_description_ar: String?
    let app_id: String?
    let device_info: [String: AnyCodable]?
    let ip_address: String?
    let geolocation: [String: AnyCodable]?
    let created_at: String
    let expires_at: String
    let resolved_at: String?
    let resolved_by: Int?
    let resolution_reason: String?
    let resolution_reason_ar: String?
    let is_expired: Bool
    let time_remaining_seconds: Int?

    var timeRemaining: String {
        guard let seconds = time_remaining_seconds, seconds > 0 else {
            return "Expired"
        }
        let minutes = seconds / 60
        let secs = seconds % 60
        return String(format: "%d:%02d", minutes, secs)
    }

    var riskColor: String {
        switch risk_level {
        case .low: return "green"
        case .medium: return "orange"
        case .high: return "red"
        case .critical: return "purple"
        }
    }
}

struct RequesterInfo: Codable {
    let id: Int
    let name: String
    let email: String
    let role: String?
}

enum ApprovalType: String, Codable {
    case login_suspicious
    case high_value_transaction
    case sensitive_data_access
    case user_role_change
    case system_config_change
    case bulk_operation
    case device_trust
    case emergency_access
    case financial_report
    case data_export

    var displayName: String {
        switch self {
        case .login_suspicious: return "Suspicious Login"
        case .high_value_transaction: return "High Value Transaction"
        case .sensitive_data_access: return "Sensitive Data Access"
        case .user_role_change: return "User Role Change"
        case .system_config_change: return "System Config Change"
        case .bulk_operation: return "Bulk Operation"
        case .device_trust: return "Device Trust"
        case .emergency_access: return "Emergency Access"
        case .financial_report: return "Financial Report"
        case .data_export: return "Data Export"
        }
    }
}

enum RiskLevel: String, Codable {
    case low, medium, high, critical
}

enum ApprovalStatus: String, Codable {
    case pending, approved, denied, expired, cancelled
}

enum ApprovalMethod: String, Codable {
    case push, qr, sms, manual, biometric
}

struct ApprovalListResponse: Decodable {
    let approvals: [Approval]
    let total: Int
    let page: Int
    let page_size: Int
    let has_more: Bool
}

struct ApproveRequest: Encodable {
    let approval_code: String
    let resolution_reason: String?
    let resolution_reason_ar: String?
    let biometric_verified: Bool
}

struct DenyRequest: Encodable {
    let resolution_reason: String
    let resolution_reason_ar: String?
}

struct ApprovalActionResponse: Decodable {
    let success: Bool
    let message: String
    let message_ar: String
    let approval_id: String
    let new_status: String
    let resolved_at: String
}

struct QRScanRequest: Encodable {
    let qr_payload: String
    let biometric_verified: Bool
}

// Helper for dynamic JSON
struct AnyCodable: Codable {
    let value: Any

    init(_ value: Any) {
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else {
            value = ""
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        if let intValue = value as? Int {
            try container.encode(intValue)
        } else if let doubleValue = value as? Double {
            try container.encode(doubleValue)
        } else if let stringValue = value as? String {
            try container.encode(stringValue)
        } else if let boolValue = value as? Bool {
            try container.encode(boolValue)
        }
    }
}
