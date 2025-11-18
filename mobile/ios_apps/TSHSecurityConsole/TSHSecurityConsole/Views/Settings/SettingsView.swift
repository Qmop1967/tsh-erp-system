import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @EnvironmentObject var appState: AppState
    @State private var showingLogoutAlert = false

    var body: some View {
        List {
            // User Info Section
            Section {
                if let user = authViewModel.currentUser {
                    HStack(spacing: 12) {
                        Circle()
                            .fill(Color.blue.opacity(0.2))
                            .frame(width: 60, height: 60)
                            .overlay {
                                Text(user.name.prefix(1).uppercased())
                                    .font(.title)
                                    .foregroundColor(.blue)
                            }

                        VStack(alignment: .leading, spacing: 4) {
                            Text(user.name)
                                .font(.headline)

                            Text(user.email)
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            Text(user.role)
                                .font(.caption)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 2)
                                .background(Color.purple.opacity(0.2))
                                .foregroundColor(.purple)
                                .cornerRadius(4)
                        }
                    }
                    .padding(.vertical, 8)

                    // Token Status Debug
                    HStack {
                        Image(systemName: KeychainService.shared.getAccessToken() != nil ? "checkmark.circle.fill" : "xmark.circle.fill")
                            .foregroundColor(KeychainService.shared.getAccessToken() != nil ? .green : .red)
                        Text(KeychainService.shared.getAccessToken() != nil ? "Token Valid" : "NO TOKEN - Please logout and login again")
                            .font(.caption)
                            .foregroundColor(KeychainService.shared.getAccessToken() != nil ? .green : .red)
                    }
                }
            }

            // App Settings
            Section(header: Text(appState.isArabic ? "التطبيق" : "App Settings")) {
                // Language Toggle
                HStack {
                    Label(
                        appState.isArabic ? "اللغة" : "Language",
                        systemImage: "globe"
                    )

                    Spacer()

                    Button(action: { appState.toggleLanguage() }) {
                        Text(appState.isArabic ? "English" : "العربية")
                            .foregroundColor(.blue)
                    }
                }

                // Biometric Settings
                if BiometricAuth.shared.isBiometricAvailable {
                    HStack {
                        Label(
                            BiometricAuth.shared.biometricName,
                            systemImage: BiometricAuth.shared.biometricIcon
                        )

                        Spacer()

                        Image(systemName: "checkmark")
                            .foregroundColor(.green)
                    }
                }
            }

            // Security Section
            Section(header: Text(appState.isArabic ? "الأمان" : "Security")) {
                NavigationLink {
                    Text("Security Settings - Coming Soon")
                } label: {
                    Label(
                        appState.isArabic ? "إعدادات الأمان" : "Security Settings",
                        systemImage: "shield.checkered"
                    )
                }

                NavigationLink {
                    Text("Notification Settings - Coming Soon")
                } label: {
                    Label(
                        appState.isArabic ? "الإشعارات" : "Notifications",
                        systemImage: "bell"
                    )
                }

                NavigationLink {
                    Text("Audit Log - Coming Soon")
                } label: {
                    Label(
                        appState.isArabic ? "سجل التدقيق" : "Audit Log",
                        systemImage: "list.bullet.rectangle"
                    )
                }
            }

            // System Info
            Section(header: Text(appState.isArabic ? "النظام" : "System")) {
                HStack {
                    Text(appState.isArabic ? "الإصدار" : "Version")
                    Spacer()
                    Text("1.0.0")
                        .foregroundColor(.secondary)
                }

                HStack {
                    Text(appState.isArabic ? "الخادم" : "Server")
                    Spacer()
                    Text("erp.tsh.sale")
                        .foregroundColor(.secondary)
                }

                HStack {
                    Text(appState.isArabic ? "الحالة" : "Status")
                    Spacer()
                    HStack(spacing: 4) {
                        Circle()
                            .fill(appState.isOnline ? Color.green : Color.red)
                            .frame(width: 8, height: 8)
                        Text(appState.isOnline ?
                            (appState.isArabic ? "متصل" : "Online") :
                            (appState.isArabic ? "غير متصل" : "Offline"))
                            .foregroundColor(.secondary)
                    }
                }
            }

            // Logout Section
            Section {
                Button(role: .destructive, action: { showingLogoutAlert = true }) {
                    HStack {
                        Spacer()
                        Label(
                            appState.isArabic ? "تسجيل الخروج" : "Logout",
                            systemImage: "rectangle.portrait.and.arrow.right"
                        )
                        Spacer()
                    }
                }
            }
        }
        .navigationTitle(appState.isArabic ? "الإعدادات" : "Settings")
        .alert(
            appState.isArabic ? "تسجيل الخروج" : "Logout",
            isPresented: $showingLogoutAlert
        ) {
            Button(appState.isArabic ? "إلغاء" : "Cancel", role: .cancel) {}
            Button(appState.isArabic ? "تسجيل الخروج" : "Logout", role: .destructive) {
                authViewModel.logout()
            }
        } message: {
            Text(appState.isArabic ?
                "هل أنت متأكد من تسجيل الخروج؟" :
                "Are you sure you want to logout?")
        }
    }
}

#Preview {
    NavigationStack {
        SettingsView()
            .environmentObject(AuthViewModel())
            .environmentObject(AppState())
    }
}
