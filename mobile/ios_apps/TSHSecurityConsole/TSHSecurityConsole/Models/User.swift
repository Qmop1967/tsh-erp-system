import Foundation

struct User: Codable, Identifiable {
    let id: Int
    let name: String
    let email: String
    let role: String
    let branch: String?
    let permissions: [String]
    let mfa_enabled: Bool?
    let mobile_app: String?
    let platform: String?

    var isOwner: Bool {
        role.lowercased() == "owner" || role.lowercased() == "admin"
    }
}

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
