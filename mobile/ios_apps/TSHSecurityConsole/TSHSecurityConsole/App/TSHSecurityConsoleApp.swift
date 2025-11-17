import SwiftUI

@main
struct TSHSecurityConsoleApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    @StateObject private var authViewModel = AuthViewModel()
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authViewModel)
                .environmentObject(appState)
                .environment(\.layoutDirection, appState.isArabic ? .rightToLeft : .leftToRight)
        }
    }
}

// MARK: - App State
class AppState: ObservableObject {
    @Published var isArabic: Bool = false
    @Published var isOnline: Bool = true
    @Published var pendingApprovalCount: Int = 0

    init() {
        // Load language preference
        let savedLanguage = UserDefaults.standard.string(forKey: "app_language") ?? "en"
        isArabic = savedLanguage == "ar"

        // Monitor network status
        setupNetworkMonitoring()
    }

    func toggleLanguage() {
        isArabic.toggle()
        UserDefaults.standard.set(isArabic ? "ar" : "en", forKey: "app_language")
    }

    private func setupNetworkMonitoring() {
        // Network monitoring would be implemented here using NWPathMonitor
    }
}
