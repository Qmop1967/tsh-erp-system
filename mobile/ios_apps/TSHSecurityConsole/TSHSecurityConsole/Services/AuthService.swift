import Foundation

actor AuthService {
    static let shared = AuthService()

    private init() {}

    func login(email: String, password: String) async throws -> LoginResponse {
        let request = LoginRequest(email: email, password: password)

        let response: LoginResponse = try await APIClient.shared.request(
            endpoint: "/auth/login/mobile",
            method: .POST,
            body: request,
            requiresAuth: false
        )

        // Save tokens
        KeychainService.shared.saveAccessToken(response.access_token)
        if let refreshToken = response.refresh_token {
            KeychainService.shared.saveRefreshToken(refreshToken)
        }
        KeychainService.shared.saveUserId(response.user.id)
        KeychainService.shared.saveUserEmail(response.user.email)

        return response
    }

    func verifyMFA(code: String, tempToken: String, userId: Int) async throws -> LoginResponse {
        let request = MFAVerifyRequest(code: code, temp_token: tempToken, user_id: userId)

        let response: LoginResponse = try await APIClient.shared.request(
            endpoint: "/auth/mfa/verify-login",
            method: .POST,
            body: request,
            requiresAuth: false
        )

        KeychainService.shared.saveAccessToken(response.access_token)
        if let refreshToken = response.refresh_token {
            KeychainService.shared.saveRefreshToken(refreshToken)
        }
        KeychainService.shared.saveUserId(response.user.id)
        KeychainService.shared.saveUserEmail(response.user.email)

        return response
    }

    func logout() async throws {
        // Call logout endpoint
        let _: [String: String] = try await APIClient.shared.request(
            endpoint: "/auth/logout",
            method: .POST
        )

        // Clear local storage
        KeychainService.shared.clearAll()
    }

    func getCurrentUser() async throws -> User {
        struct UserResponse: Decodable {
            let id: Int
            let name: String
            let email: String
            let role: String
            let branch: String
            let permissions: [String]
        }

        let response: UserResponse = try await APIClient.shared.request(
            endpoint: "/auth/me"
        )

        return User(
            id: response.id,
            name: response.name,
            email: response.email,
            role: response.role,
            branch: response.branch,
            permissions: response.permissions,
            mfa_enabled: nil,
            mobile_app: nil,
            platform: nil
        )
    }

    func isTokenValid() -> Bool {
        return KeychainService.shared.getAccessToken() != nil
    }
}
