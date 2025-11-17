import UIKit
import UserNotifications

class AppDelegate: NSObject, UIApplicationDelegate, UNUserNotificationCenterDelegate {

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        // Setup push notifications
        setupPushNotifications(application)
        return true
    }

    // MARK: - Push Notifications Setup
    private func setupPushNotifications(_ application: UIApplication) {
        UNUserNotificationCenter.current().delegate = self

        // Request authorization
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    application.registerForRemoteNotifications()
                }
            }
        }
    }

    // MARK: - APNS Token Registration
    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        let tokenString = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        print("APNS Token: \(tokenString)")

        // Store token for sending to backend
        UserDefaults.standard.set(tokenString, forKey: "apns_token")

        // Send to backend if authenticated
        Task {
            await NotificationService.shared.registerDeviceToken(tokenString)
        }
    }

    func application(_ application: UIApplication,
                     didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("Failed to register for remote notifications: \(error.localizedDescription)")
    }

    // MARK: - Handle Push Notifications
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        // Show notification even when app is in foreground
        completionHandler([.banner, .badge, .sound])
    }

    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        let userInfo = response.notification.request.content.userInfo

        // Handle deep linking for approval requests
        if let type = userInfo["type"] as? String, type == "owner_approval_request" {
            if let approvalId = userInfo["approval_id"] as? String {
                // Navigate to approval detail
                NotificationCenter.default.post(
                    name: .navigateToApproval,
                    object: nil,
                    userInfo: ["approvalId": approvalId]
                )
            }
        }

        completionHandler()
    }
}

// MARK: - Notification Names
extension Notification.Name {
    static let navigateToApproval = Notification.Name("navigateToApproval")
    static let tokenExpired = Notification.Name("tokenExpired")
    static let sessionTerminated = Notification.Name("sessionTerminated")
}
