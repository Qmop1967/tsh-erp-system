import Foundation

enum AuthServiceError: Error, LocalizedError {
    case tokenSaveFailed
    case userDataSaveFailed
    case invalidResponse

    var errorDescription: String? {
        switch self {
        case .tokenSaveFailed:
            return "Failed to save authentication token securely"
        case .userDataSaveFailed:
            return "Failed to save user data"
        case .invalidResponse:
            return "Invalid response from server"
        }
    }
}

actor AuthService {
    static let shared = AuthService()

    private init() {}

    func login(email: String, password: String) async throws -> LoginResponse {
        #if DEBUG
        print("🔐 [AuthService] Starting login for: \(email)")
        #endif

        let request = LoginRequest(email: email, password: password)

        let response: LoginResponse = try await APIClient.shared.request(
            endpoint: "/auth/login/mobile",
            method: .POST,
            body: request,
            requiresAuth: false
        )

        #if DEBUG
        print("✅ [AuthService] Login successful, saving credentials...")
        print("   Token length: \(response.access_token.count)")
        print("   Has refresh token: \(response.refresh_token != nil)")
        print("   User ID: \(response.user.id)")
        print("   User role: \(response.user.role)")
        #endif

        // Save tokens with verification
        try saveCredentials(response)

        #if DEBUG
        print("✅ [AuthService] All credentials saved successfully")

        // Verify token is accessible
        let diagnostics = KeychainService.shared.diagnosticInfo()
        print("📊 [AuthService] Keychain diagnostics: \(diagnostics)")
        #endif

        return response
    }

    func verifyMFA(code: String, tempToken: String, userId: Int) async throws -> LoginResponse {
        #if DEBUG
        print("🔐 [AuthService] Verifying MFA...")
        #endif

        let request = MFAVerifyRequest(code: code, temp_token: tempToken, user_id: userId)

        let response: LoginResponse = try await APIClient.shared.request(
            endpoint: "/auth/mfa/verify-login",
            method: .POST,
            body: request,
            requiresAuth: false
        )

        // Save tokens with verification
        try saveCredentials(response)

        #if DEBUG
        print("✅ [AuthService] MFA verification complete, credentials saved")
        #endif

        return response
    }

    /// Save all credentials from login response with verification
    private func saveCredentials(_ response: LoginResponse) throws {
        // Save access token (CRITICAL - must succeed)
        guard KeychainService.shared.saveAccessToken(response.access_token) else {
            #if DEBUG
            print("❌ [AuthService] CRITICAL: Failed to save access token!")
            #endif
            throw AuthServiceError.tokenSaveFailed
        }

        // Verify token was actually saved by reading it back
        guard let savedToken = KeychainService.shared.getAccessToken(),
              savedToken == response.access_token else {
            #if DEBUG
            print("❌ [AuthService] CRITICAL: Token verification failed - saved token doesn't match!")
            #endif
            throw AuthServiceError.tokenSaveFailed
        }

        // Save refresh token if available
        if let refreshToken = response.refresh_token {
            if !KeychainService.shared.saveRefreshToken(refreshToken) {
                #if DEBUG
                print("⚠️ [AuthService] Warning: Failed to save refresh token")
                #endif
                // Not critical, continue anyway
            }
        } else {
            #if DEBUG
            print("⚠️ [AuthService] No refresh token provided by server")
            #endif
        }

        // Save user info
        let userIdSaved = KeychainService.shared.saveUserId(response.user.id)
        let emailSaved = KeychainService.shared.saveUserEmail(response.user.email)

        if !userIdSaved || !emailSaved {
            #if DEBUG
            print("⚠️ [AuthService] Warning: Failed to save some user data (ID: \(userIdSaved), Email: \(emailSaved))")
            #endif
            // Not critical, continue anyway
        }
    }

    func logout() async throws {
        #if DEBUG
        print("🚪 [AuthService] Logging out...")
        #endif

        // Call logout endpoint
        let _: [String: String] = try await APIClient.shared.request(
            endpoint: "/auth/logout",
            method: .POST
        )

        // Clear local storage
        KeychainService.shared.clearAll()

        #if DEBUG
        print("✅ [AuthService] Logout complete")
        #endif
    }

    func getCurrentUser() async throws -> User {
        #if DEBUG
        print("👤 [AuthService] Fetching current user...")
        #endif

        struct UserResponse: Decodable {
            let id: String  // UUID string from production
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
            mfaEnabled: nil,
            mobileApp: nil,
            platform: nil
        )
    }

    func isTokenValid() -> Bool {
        let hasToken = KeychainService.shared.hasAccessToken()
        #if DEBUG
        print("🔍 [AuthService] Token valid check: \(hasToken)")
        #endif
        return hasToken
    }

    /// Verify current authentication state
    func verifyAuthenticationState() -> Bool {
        let diagnostics = KeychainService.shared.diagnosticInfo()
        let hasToken = diagnostics["hasAccessToken"] as? Bool ?? false

        #if DEBUG
        print("🔍 [AuthService] Auth state verification:")
        print("   - Has access token: \(hasToken)")
        print("   - Has refresh token: \(diagnostics["hasRefreshToken"] ?? false)")
        print("   - Has user ID: \(diagnostics["hasUserId"] ?? false)")
        print("   - Has user email: \(diagnostics["hasUserEmail"] ?? false)")
        #endif

        return hasToken
    }
}
