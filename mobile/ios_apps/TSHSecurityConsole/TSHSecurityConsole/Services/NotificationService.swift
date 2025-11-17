import Foundation

actor NotificationService {
    static let shared = NotificationService()

    private init() {}

    func registerDeviceToken(_ token: String) async {
        guard KeychainService.shared.getAccessToken() != nil else {
            // Not authenticated yet, save for later
            UserDefaults.standard.set(token, forKey: "pending_apns_token")
            return
        }

        do {
            struct TokenRequest: Encodable {
                let device_token: String
                let device_type: String
                let app_id: String
            }

            let request = TokenRequest(
                device_token: token,
                device_type: "ios",
                app_id: "tsh_security_console"
            )

            let _: [String: String] = try await APIClient.shared.request(
                endpoint: "/notifications/device-token",
                method: .POST,
                body: request
            )

            // Clear pending token
            UserDefaults.standard.removeObject(forKey: "pending_apns_token")
        } catch {
            print("Failed to register device token: \(error.localizedDescription)")
        }
    }

    func registerPendingToken() async {
        if let pendingToken = UserDefaults.standard.string(forKey: "pending_apns_token") {
            await registerDeviceToken(pendingToken)
        }
    }
}
