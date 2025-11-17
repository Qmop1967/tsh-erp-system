import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @EnvironmentObject var appState: AppState
    @State private var selectedTab: Tab = .dashboard
    @State private var navigateToApprovalId: String?

    enum Tab {
        case dashboard, approvals, sessions, users, settings
    }

    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                mainTabView
            } else {
                LoginView()
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .navigateToApproval)) { notification in
            if let approvalId = notification.userInfo?["approvalId"] as? String {
                navigateToApprovalId = approvalId
                selectedTab = .approvals
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: .tokenExpired)) { _ in
            authViewModel.logout()
        }
    }

    private var mainTabView: some View {
        TabView(selection: $selectedTab) {
            NavigationStack {
                DashboardView()
            }
            .tabItem {
                Label(
                    appState.isArabic ? "الرئيسية" : "Dashboard",
                    systemImage: "shield.checkered"
                )
            }
            .tag(Tab.dashboard)

            NavigationStack {
                ApprovalsListView(navigateToId: navigateToApprovalId)
            }
            .tabItem {
                Label(
                    appState.isArabic ? "الموافقات" : "Approvals",
                    systemImage: "checkmark.shield"
                )
            }
            .badge(appState.pendingApprovalCount)
            .tag(Tab.approvals)

            NavigationStack {
                SessionsListView()
            }
            .tabItem {
                Label(
                    appState.isArabic ? "الجلسات" : "Sessions",
                    systemImage: "person.2.wave.2"
                )
            }
            .tag(Tab.sessions)

            NavigationStack {
                UsersListView()
            }
            .tabItem {
                Label(
                    appState.isArabic ? "المستخدمون" : "Users",
                    systemImage: "person.3"
                )
            }
            .tag(Tab.users)

            NavigationStack {
                SettingsView()
            }
            .tabItem {
                Label(
                    appState.isArabic ? "الإعدادات" : "Settings",
                    systemImage: "gearshape"
                )
            }
            .tag(Tab.settings)
        }
        .accentColor(.blue)
    }
}

#Preview {
    ContentView()
        .environmentObject(AuthViewModel())
        .environmentObject(AppState())
}
