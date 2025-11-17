import SwiftUI

@MainActor
class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var requiresMFA = false
    @Published var tempToken: String?
    @Published var mfaUserId: Int?

    init() {
        checkAuthStatus()
    }

    func checkAuthStatus() {
        if AuthService.shared.isTokenValid() {
            isAuthenticated = true
            Task {
                await fetchCurrentUser()
            }
        }
    }

    func login(email: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await AuthService.shared.login(email: email, password: password)

            // Check if user has owner/admin role
            guard response.user.isOwner else {
                errorMessage = "Access denied. Only Owner/Admin can use this app."
                KeychainService.shared.clearAll()
                isLoading = false
                return
            }

            currentUser = response.user
            isAuthenticated = true

            // Register pending APNS token
            await NotificationService.shared.registerPendingToken()
        } catch let error as APIError {
            errorMessage = error.localizedDescription
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func verifyMFA(code: String) async {
        guard let tempToken = tempToken, let userId = mfaUserId else {
            errorMessage = "MFA session expired"
            return
        }

        isLoading = true
        errorMessage = nil

        do {
            let response = try await AuthService.shared.verifyMFA(
                code: code,
                tempToken: tempToken,
                userId: userId
            )

            currentUser = response.user
            isAuthenticated = true
            requiresMFA = false
            self.tempToken = nil
            self.mfaUserId = nil

            await NotificationService.shared.registerPendingToken()
        } catch {
            errorMessage = "Invalid MFA code"
        }

        isLoading = false
    }

    func loginWithBiometrics() async {
        guard let email = KeychainService.shared.getUserEmail() else {
            errorMessage = "No saved credentials"
            return
        }

        do {
            let authenticated = try await BiometricAuth.shared.authenticate(
                reason: "Authenticate to access TSH Security Console"
            )

            if authenticated {
                // Try to restore session
                await fetchCurrentUser()
                if currentUser != nil {
                    isAuthenticated = true
                }
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func logout() {
        Task {
            try? await AuthService.shared.logout()
        }
        KeychainService.shared.clearAll()
        isAuthenticated = false
        currentUser = nil
        requiresMFA = false
        tempToken = nil
        mfaUserId = nil
    }

    private func fetchCurrentUser() async {
        do {
            currentUser = try await AuthService.shared.getCurrentUser()
        } catch {
            // Token might be invalid
            isAuthenticated = false
        }
    }
}
