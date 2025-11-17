import Foundation
import Security

enum KeychainError: Error, LocalizedError {
    case saveFailed(OSStatus)
    case dataEncodingFailed
    case itemNotFound
    case unexpectedData
    case unhandledError(OSStatus)

    var errorDescription: String? {
        switch self {
        case .saveFailed(let status):
            return "Keychain save failed with status: \(status)"
        case .dataEncodingFailed:
            return "Failed to encode data for Keychain"
        case .itemNotFound:
            return "Item not found in Keychain"
        case .unexpectedData:
            return "Unexpected data format in Keychain"
        case .unhandledError(let status):
            return "Keychain error: \(status)"
        }
    }
}

class KeychainService {
    static let shared = KeychainService()

    private let service = "com.tsh.security.console"

    private enum Keys {
        static let accessToken = "access_token"
        static let refreshToken = "refresh_token"
        static let userId = "user_id"
        static let userEmail = "user_email"
    }

    private init() {}

    // MARK: - Token Management (With Verification)

    /// Save access token with verification - throws on failure
    @discardableResult
    func saveAccessToken(_ token: String) -> Bool {
        let success = save(key: Keys.accessToken, value: token)
        #if DEBUG
        if success {
            print("✅ [Keychain] Access token saved successfully (length: \(token.count))")
        } else {
            print("❌ [Keychain] Failed to save access token")
        }
        #endif
        return success
    }

    /// Save access token and throw error if failed
    func saveAccessTokenVerified(_ token: String) throws {
        guard save(key: Keys.accessToken, value: token) else {
            throw KeychainError.saveFailed(-1)
        }

        // Verify it was actually saved
        guard let savedToken = getAccessToken(), savedToken == token else {
            throw KeychainError.saveFailed(-2)
        }

        #if DEBUG
        print("✅ [Keychain] Access token saved and verified (length: \(token.count))")
        #endif
    }

    func getAccessToken() -> String? {
        let token = get(key: Keys.accessToken)
        #if DEBUG
        if let t = token {
            print("✅ [Keychain] Access token retrieved (length: \(t.count))")
        } else {
            print("⚠️ [Keychain] No access token found")
        }
        #endif
        return token
    }

    @discardableResult
    func saveRefreshToken(_ token: String) -> Bool {
        let success = save(key: Keys.refreshToken, value: token)
        #if DEBUG
        if success {
            print("✅ [Keychain] Refresh token saved successfully")
        } else {
            print("❌ [Keychain] Failed to save refresh token")
        }
        #endif
        return success
    }

    func getRefreshToken() -> String? {
        let token = get(key: Keys.refreshToken)
        #if DEBUG
        if token != nil {
            print("✅ [Keychain] Refresh token retrieved")
        } else {
            print("⚠️ [Keychain] No refresh token found")
        }
        #endif
        return token
    }

    // MARK: - User Info
    @discardableResult
    func saveUserId(_ id: String) -> Bool {
        let success = save(key: Keys.userId, value: id)
        #if DEBUG
        print(success ? "✅ [Keychain] User ID saved: \(id)" : "❌ [Keychain] Failed to save user ID")
        #endif
        return success
    }

    func getUserId() -> String? {
        return get(key: Keys.userId)
    }

    @discardableResult
    func saveUserEmail(_ email: String) -> Bool {
        let success = save(key: Keys.userEmail, value: email)
        #if DEBUG
        print(success ? "✅ [Keychain] User email saved: \(email)" : "❌ [Keychain] Failed to save user email")
        #endif
        return success
    }

    func getUserEmail() -> String? {
        return get(key: Keys.userEmail)
    }

    // MARK: - Clear All
    func clearAll() {
        #if DEBUG
        print("🗑️ [Keychain] Clearing all stored data...")
        #endif
        delete(key: Keys.accessToken)
        delete(key: Keys.refreshToken)
        delete(key: Keys.userId)
        delete(key: Keys.userEmail)
        #if DEBUG
        print("✅ [Keychain] All data cleared")
        #endif
    }

    // MARK: - Diagnostic Methods

    /// Check if access token exists in Keychain
    func hasAccessToken() -> Bool {
        return getAccessToken() != nil
    }

    /// Get diagnostic info about Keychain state
    func diagnosticInfo() -> [String: Any] {
        return [
            "hasAccessToken": hasAccessToken(),
            "hasRefreshToken": getRefreshToken() != nil,
            "hasUserId": getUserId() != nil,
            "hasUserEmail": getUserEmail() != nil
        ]
    }

    // MARK: - Generic Keychain Operations

    /// Save value to Keychain - returns true on success
    private func save(key: String, value: String) -> Bool {
        guard let data = value.data(using: .utf8) else {
            #if DEBUG
            print("❌ [Keychain] Failed to encode value for key: \(key)")
            #endif
            return false
        }

        // Delete existing item first
        delete(key: key)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status != errSecSuccess {
            #if DEBUG
            print("❌ [Keychain] Save failed for key '\(key)' with status: \(status) - \(securityErrorMessage(status))")
            #endif
            return false
        }

        return true
    }

    private func get(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess else {
            #if DEBUG
            if status != errSecItemNotFound {
                print("⚠️ [Keychain] Get failed for key '\(key)' with status: \(status) - \(securityErrorMessage(status))")
            }
            #endif
            return nil
        }

        guard let data = result as? Data else {
            #if DEBUG
            print("⚠️ [Keychain] Unexpected data type for key '\(key)'")
            #endif
            return nil
        }

        guard let string = String(data: data, encoding: .utf8) else {
            #if DEBUG
            print("⚠️ [Keychain] Failed to decode data for key '\(key)'")
            #endif
            return nil
        }

        return string
    }

    private func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        #if DEBUG
        if status != errSecSuccess && status != errSecItemNotFound {
            print("⚠️ [Keychain] Delete failed for key '\(key)' with status: \(status)")
        }
        #endif
    }

    // MARK: - Helper Methods

    private func securityErrorMessage(_ status: OSStatus) -> String {
        switch status {
        case errSecSuccess:
            return "Success"
        case errSecItemNotFound:
            return "Item not found"
        case errSecDuplicateItem:
            return "Duplicate item"
        case errSecAuthFailed:
            return "Authentication failed"
        case errSecParam:
            return "Invalid parameter"
        case errSecAllocate:
            return "Memory allocation error"
        case errSecInteractionNotAllowed:
            return "Interaction not allowed (device locked?)"
        case errSecDecode:
            return "Unable to decode data"
        case errSecMissingEntitlement:
            return "Missing entitlement"
        default:
            return "Unknown error"
        }
    }
}
