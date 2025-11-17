import Foundation
import Security

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

    // MARK: - Token Management
    func saveAccessToken(_ token: String) {
        save(key: Keys.accessToken, value: token)
    }

    func getAccessToken() -> String? {
        return get(key: Keys.accessToken)
    }

    func saveRefreshToken(_ token: String) {
        save(key: Keys.refreshToken, value: token)
    }

    func getRefreshToken() -> String? {
        return get(key: Keys.refreshToken)
    }

    // MARK: - User Info
    func saveUserId(_ id: Int) {
        save(key: Keys.userId, value: String(id))
    }

    func getUserId() -> Int? {
        guard let idString = get(key: Keys.userId) else { return nil }
        return Int(idString)
    }

    func saveUserEmail(_ email: String) {
        save(key: Keys.userEmail, value: email)
    }

    func getUserEmail() -> String? {
        return get(key: Keys.userEmail)
    }

    // MARK: - Clear All
    func clearAll() {
        delete(key: Keys.accessToken)
        delete(key: Keys.refreshToken)
        delete(key: Keys.userId)
        delete(key: Keys.userEmail)
    }

    // MARK: - Generic Keychain Operations
    private func save(key: String, value: String) {
        guard let data = value.data(using: .utf8) else { return }

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
            print("Keychain save error: \(status)")
        }
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

        guard status == errSecSuccess,
              let data = result as? Data,
              let string = String(data: data, encoding: .utf8) else {
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

        SecItemDelete(query as CFDictionary)
    }
}
