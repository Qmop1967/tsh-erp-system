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
        #if DEBUG
        print("🚀 [AuthViewModel] Initializing...")
        #endif
        Task {
            await checkAuthStatus()
        }
    }

    func checkAuthStatus() async {
        #if DEBUG
        print("🔍 [AuthViewModel] Checking authentication status...")
        let diagnostics = KeychainService.shared.diagnosticInfo()
        print("   Keychain state: \(diagnostics)")
        #endif

        let isValid = await AuthService.shared.isTokenValid()

        if isValid {
            #if DEBUG
            print("✅ [AuthViewModel] Token exists, validating with server...")
            #endif

            // Try to fetch current user to validate the token actually works
            do {
                currentUser = try await AuthService.shared.getCurrentUser()
                isAuthenticated = true
                #if DEBUG
                print("✅ [AuthViewModel] Token validated, user: \(currentUser?.name ?? "unknown")")
                #endif
            } catch {
                // Token exists but is invalid/expired - clear it
                #if DEBUG
                print("⚠️ [AuthViewModel] Token validation failed: \(error.localizedDescription)")
                #endif
                KeychainService.shared.clearAll()
                isAuthenticated = false
                currentUser = nil
                // Don't set errorMessage here - this is expected behavior for expired tokens
            }
        } else {
            #if DEBUG
            print("⚠️ [AuthViewModel] No valid token found")
            #endif
            isAuthenticated = false
            currentUser = nil
        }
    }

    func login(email: String, password: String) async {
        #if DEBUG
        print("🔐 [AuthViewModel] Starting login process for: \(email)")
        #endif

        isLoading = true
        errorMessage = nil

        do {
            let response = try await AuthService.shared.login(email: email, password: password)

            #if DEBUG
            print("✅ [AuthViewModel] Login API successful")
            print("   User: \(response.user.name)")
            print("   Role: \(response.user.role)")
            print("   Is Owner/Admin: \(response.user.isOwner)")
            #endif

            // Verify token was actually saved (critical check)
            guard KeychainService.shared.hasAccessToken() else {
                #if DEBUG
                print("❌ [AuthViewModel] CRITICAL: Token not found after login!")
                #endif
                errorMessage = "Authentication failed - token not saved. Please try again."
                isAuthenticated = false
                isLoading = false
                return
            }

            // Check if user has owner/admin role
            guard response.user.isOwner else {
                #if DEBUG
                print("🚫 [AuthViewModel] Access denied - user role: \(response.user.role)")
                #endif
                errorMessage = "Access denied. Only Owner/Admin can use this app."
                KeychainService.shared.clearAll()
                isAuthenticated = false
                isLoading = false
                return
            }

            currentUser = response.user
            isAuthenticated = true

            #if DEBUG
            print("✅ [AuthViewModel] Login complete!")
            print("   isAuthenticated: \(isAuthenticated)")
            print("   User ID: \(currentUser?.id ?? "nil")")

            // Final verification
            let finalDiagnostics = KeychainService.shared.diagnosticInfo()
            print("📊 [AuthViewModel] Final Keychain state: \(finalDiagnostics)")
            #endif

            // Register pending APNS token
            await NotificationService.shared.registerPendingToken()

        } catch let error as AuthServiceError {
            #if DEBUG
            print("❌ [AuthViewModel] Auth service error: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            isAuthenticated = false
        } catch let error as APIError {
            #if DEBUG
            print("❌ [AuthViewModel] API error: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            isAuthenticated = false
        } catch {
            #if DEBUG
            print("❌ [AuthViewModel] Unexpected error: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            isAuthenticated = false
        }

        isLoading = false
    }

    func verifyMFA(code: String) async {
        guard let tempToken = tempToken, let userId = mfaUserId else {
            errorMessage = "MFA session expired"
            return
        }

        #if DEBUG
        print("🔐 [AuthViewModel] Verifying MFA code...")
        #endif

        isLoading = true
        errorMessage = nil

        do {
            let response = try await AuthService.shared.verifyMFA(
                code: code,
                tempToken: tempToken,
                userId: userId
            )

            // Verify token was saved
            guard KeychainService.shared.hasAccessToken() else {
                errorMessage = "Authentication failed - token not saved"
                isLoading = false
                return
            }

            currentUser = response.user
            isAuthenticated = true
            requiresMFA = false
            self.tempToken = nil
            self.mfaUserId = nil

            #if DEBUG
            print("✅ [AuthViewModel] MFA verification complete")
            #endif

            await NotificationService.shared.registerPendingToken()
        } catch let error as AuthServiceError {
            errorMessage = error.localizedDescription
        } catch {
            errorMessage = "Invalid MFA code"
        }

        isLoading = false
    }

    func loginWithBiometrics() async {
        #if DEBUG
        print("🔐 [AuthViewModel] Attempting biometric login...")
        #endif

        guard let email = KeychainService.shared.getUserEmail() else {
            #if DEBUG
            print("⚠️ [AuthViewModel] No saved email for biometric login")
            #endif
            errorMessage = "No saved credentials"
            return
        }

        // Check if we have a valid token first
        guard KeychainService.shared.hasAccessToken() else {
            #if DEBUG
            print("⚠️ [AuthViewModel] No token for biometric login")
            #endif
            errorMessage = "Session expired. Please login with email and password."
            return
        }

        do {
            let authenticated = try await BiometricAuth.shared.authenticate(
                reason: "Authenticate to access TSH Security Console"
            )

            if authenticated {
                #if DEBUG
                print("✅ [AuthViewModel] Biometric auth successful, restoring session...")
                #endif

                // Try to restore session with existing token
                await fetchCurrentUser()
                if currentUser != nil {
                    isAuthenticated = true
                    #if DEBUG
                    print("✅ [AuthViewModel] Session restored for: \(currentUser?.name ?? "unknown")")
                    #endif
                } else {
                    // Token is invalid or expired
                    #if DEBUG
                    print("⚠️ [AuthViewModel] Token invalid, session not restored")
                    #endif
                    errorMessage = "Session expired. Please login with email and password."
                }
            }
        } catch {
            #if DEBUG
            print("❌ [AuthViewModel] Biometric auth error: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
        }
    }

    func logout() {
        #if DEBUG
        print("🚪 [AuthViewModel] Logging out...")
        #endif

        Task {
            try? await AuthService.shared.logout()
        }
        KeychainService.shared.clearAll()
        isAuthenticated = false
        currentUser = nil
        requiresMFA = false
        tempToken = nil
        mfaUserId = nil

        #if DEBUG
        print("✅ [AuthViewModel] Logout complete")
        let diagnostics = KeychainService.shared.diagnosticInfo()
        print("   Keychain cleared: \(diagnostics)")
        #endif
    }

    private func fetchCurrentUser() async {
        #if DEBUG
        print("👤 [AuthViewModel] Fetching current user...")
        #endif

        do {
            currentUser = try await AuthService.shared.getCurrentUser()
            #if DEBUG
            print("✅ [AuthViewModel] User fetched: \(currentUser?.name ?? "unknown")")
            #endif
        } catch {
            #if DEBUG
            print("❌ [AuthViewModel] Failed to fetch user: \(error.localizedDescription)")
            #endif
            // Token might be invalid - clear stale tokens
            KeychainService.shared.clearAll()
            isAuthenticated = false
            currentUser = nil
        }
    }

    /// Debug: Get current authentication state summary
    func getAuthStateSummary() -> String {
        let diagnostics = KeychainService.shared.diagnosticInfo()
        return """
        Auth State:
        - isAuthenticated: \(isAuthenticated)
        - currentUser: \(currentUser?.name ?? "nil")
        - hasAccessToken: \(diagnostics["hasAccessToken"] ?? false)
        - hasRefreshToken: \(diagnostics["hasRefreshToken"] ?? false)
        - hasUserId: \(diagnostics["hasUserId"] ?? false)
        - hasUserEmail: \(diagnostics["hasUserEmail"] ?? false)
        """
    }
}
