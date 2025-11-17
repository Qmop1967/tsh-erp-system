import Foundation

struct Session: Codable, Identifiable {
    let id: String
    let user_id: Int
    let user_name: String
    let user_email: String
    let device_type: String
    let ip_address: String?
    let location: [String: AnyCodable]?
    let risk_score: Double
    let risk_level: String
    let created_at: String?
    let last_activity: String?
    let expires_at: String?
    let can_terminate: Bool

    var riskColor: String {
        switch risk_level.lowercased() {
        case "low": return "green"
        case "medium": return "orange"
        case "high": return "red"
        case "critical": return "purple"
        default: return "gray"
        }
    }

    var deviceIcon: String {
        switch device_type.lowercased() {
        case "mobile": return "iphone"
        case "tablet": return "ipad"
        default: return "desktopcomputer"
        }
    }

    var locationString: String {
        guard let loc = location else { return "Unknown" }
        let city = loc["city"]?.value as? String ?? "Unknown"
        return city
    }
}

struct SessionListResponse: Decodable {
    let sessions: [Session]
    let total: Int
    let by_device: [String: Int]
    let by_location: [String: Int]
    let page: Int
    let page_size: Int
}

struct DashboardData: Decodable {
    let security_status: SecurityStatus
    let alerts: AlertCounts
    let failed_logins: FailedLoginData
    let active_sessions: ActiveSessionData
    let recent_events: [[String: AnyCodable]]
    let suspicious_activities: [[String: AnyCodable]]
    let access_violations: [[String: AnyCodable]]
}

struct SecurityStatus: Decodable {
    let overall: String
    let threat_level: String
    let active_threats: Int
    let security_score: Int
}

struct AlertCounts: Decodable {
    let critical: Int
    let high: Int
    let medium: Int
    let low: Int
}

struct FailedLoginData: Decodable {
    let last_hour: Int
    let last_24h: Int
    let blocked_ips: [String]
}

struct ActiveSessionData: Decodable {
    let total: Int
    let by_device: [String: Int]
}

struct DashboardResponse: Decodable {
    let success: Bool
    let data: DashboardData
    let metadata: DashboardMetadata
}

struct DashboardMetadata: Decodable {
    let cached: Bool
    let response_time_ms: Double
}
