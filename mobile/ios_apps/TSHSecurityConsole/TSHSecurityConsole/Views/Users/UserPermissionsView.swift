import SwiftUI

struct UserPermissionsView: View {
    let user: User
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState

    @State private var userPermissions: UserPermissionsResponse?
    @State private var allPermissions: [Permission] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var successMessage: String?
    @State private var showingGrantPermission = false
    @State private var selectedPermissionToGrant: Permission?
    @State private var searchText = ""

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    ProgressView()
                } else if let error = errorMessage {
                    VStack(spacing: 16) {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.largeTitle)
                            .foregroundColor(.orange)
                        Text(error)
                            .multilineTextAlignment(.center)
                        Button(appState.isArabic ? "إعادة المحاولة" : "Retry") {
                            Task { await loadData() }
                        }
                        .buttonStyle(.bordered)
                    }
                    .padding()
                } else if let perms = userPermissions {
                    List {
                        // Summary Section
                        Section(header: Text(appState.isArabic ? "الملخص" : "Summary")) {
                            HStack {
                                Label(
                                    appState.isArabic ? "الدور" : "Role",
                                    systemImage: "person.badge.shield.checkmark"
                                )
                                Spacer()
                                Text(perms.roleName)
                                    .foregroundColor(.secondary)
                            }

                            HStack {
                                Label(
                                    appState.isArabic ? "صلاحيات الدور" : "Role Permissions",
                                    systemImage: "lock.shield"
                                )
                                Spacer()
                                Text("\(perms.rolePermissions.count)")
                                    .foregroundColor(.secondary)
                            }

                            HStack {
                                Label(
                                    appState.isArabic ? "التجاوزات" : "Overrides",
                                    systemImage: "arrow.triangle.branch"
                                )
                                Spacer()
                                Text("\(perms.permissionOverrides.count)")
                                    .foregroundColor(.secondary)
                            }

                            HStack {
                                Label(
                                    appState.isArabic ? "الصلاحيات الفعالة" : "Effective Permissions",
                                    systemImage: "checkmark.shield"
                                )
                                Spacer()
                                Text("\(perms.effectivePermissions.count)")
                                    .foregroundColor(.blue)
                                    .fontWeight(.semibold)
                            }
                        }

                        // Permission Overrides Section
                        if !perms.permissionOverrides.isEmpty {
                            Section(header: Text(appState.isArabic ? "تجاوزات الصلاحيات" : "Permission Overrides")) {
                                ForEach(perms.permissionOverrides, id: \.permissionId) { override in
                                    PermissionOverrideRow(
                                        override: override,
                                        onRemove: {
                                            Task { await removeOverride(permissionId: override.permissionId) }
                                        }
                                    )
                                }
                            }
                        }

                        // Role Permissions Section
                        Section(header: Text(appState.isArabic ? "صلاحيات الدور" : "Role Permissions")) {
                            if perms.rolePermissions.isEmpty {
                                Text(appState.isArabic ? "لا توجد صلاحيات للدور" : "No role permissions")
                                    .foregroundColor(.secondary)
                                    .italic()
                            } else {
                                ForEach(perms.rolePermissions) { permission in
                                    PermissionRow(permission: permission, isGranted: true, source: "role")
                                }
                            }
                        }

                        // Available Permissions to Grant
                        Section(header: Text(appState.isArabic ? "منح صلاحية جديدة" : "Grant New Permission")) {
                            if availablePermissionsToGrant.isEmpty {
                                Text(appState.isArabic ? "جميع الصلاحيات ممنوحة" : "All permissions granted")
                                    .foregroundColor(.secondary)
                                    .italic()
                            } else {
                                ForEach(filteredAvailablePermissions) { permission in
                                    Button {
                                        selectedPermissionToGrant = permission
                                        showingGrantPermission = true
                                    } label: {
                                        HStack {
                                            VStack(alignment: .leading) {
                                                Text(permission.name)
                                                    .font(.body)
                                                if let code = permission.code {
                                                    Text(code)
                                                        .font(.caption)
                                                        .foregroundColor(.secondary)
                                                }
                                            }
                                            Spacer()
                                            Image(systemName: "plus.circle.fill")
                                                .foregroundColor(.green)
                                        }
                                    }
                                    .buttonStyle(.plain)
                                }
                            }
                        }
                    }
                    .listStyle(.insetGrouped)
                    .searchable(
                        text: $searchText,
                        prompt: appState.isArabic ? "بحث عن صلاحية..." : "Search permissions..."
                    )
                }
            }
            .navigationTitle(appState.isArabic ? "إدارة الصلاحيات" : "Manage Permissions")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(appState.isArabic ? "إغلاق" : "Close") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        Task { await loadData() }
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
            .onAppear {
                Task { await loadData() }
            }
            .alert(
                appState.isArabic ? "منح صلاحية" : "Grant Permission",
                isPresented: $showingGrantPermission
            ) {
                Button(appState.isArabic ? "إلغاء" : "Cancel", role: .cancel) {}
                Button(appState.isArabic ? "منح" : "Grant") {
                    if let perm = selectedPermissionToGrant {
                        Task { await grantPermission(permissionId: perm.id) }
                    }
                }
            } message: {
                if let perm = selectedPermissionToGrant {
                    Text(appState.isArabic
                        ? "هل تريد منح صلاحية '\(perm.name)' للمستخدم \(user.name)؟"
                        : "Grant permission '\(perm.name)' to \(user.name)?")
                }
            }
            .overlay(alignment: .bottom) {
                if let success = successMessage {
                    Text(success)
                        .padding()
                        .background(Color.green.opacity(0.9))
                        .foregroundColor(.white)
                        .cornerRadius(10)
                        .padding()
                        .transition(.move(edge: .bottom))
                        .onAppear {
                            DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                                successMessage = nil
                            }
                        }
                }
            }
            .animation(.easeInOut, value: successMessage)
        }
    }

    private var availablePermissionsToGrant: [Permission] {
        guard let perms = userPermissions else { return [] }
        let effectiveCodes = Set(perms.effectivePermissions)
        return allPermissions.filter { permission in
            let code = permission.code ?? "\(permission.module ?? "").\(permission.action ?? "")"
            return !effectiveCodes.contains(code)
        }
    }

    private var filteredAvailablePermissions: [Permission] {
        if searchText.isEmpty {
            return availablePermissionsToGrant
        }
        return availablePermissionsToGrant.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            ($0.code ?? "").localizedCaseInsensitiveContains(searchText) ||
            ($0.category ?? "").localizedCaseInsensitiveContains(searchText)
        }
    }

    private func loadData() async {
        isLoading = true
        errorMessage = nil

        do {
            guard let userId = Int(user.id) else {
                errorMessage = "Invalid user ID"
                isLoading = false
                return
            }

            async let permsTask = SecurityService.shared.getUserPermissions(userId: userId)
            async let allPermsTask = SecurityService.shared.getAllPermissions()

            let (perms, allPerms) = try await (permsTask, allPermsTask)
            userPermissions = perms
            allPermissions = allPerms
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    private func grantPermission(permissionId: Int) async {
        guard let userId = Int(user.id) else { return }

        do {
            let response = try await SecurityService.shared.grantPermission(
                userId: userId,
                permissionId: permissionId
            )
            successMessage = response.message
            await loadData()  // Reload to show updated permissions
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func removeOverride(permissionId: Int) async {
        guard let userId = Int(user.id) else { return }

        do {
            _ = try await SecurityService.shared.removePermissionOverride(
                userId: userId,
                permissionId: permissionId
            )
            successMessage = appState.isArabic
                ? "تم إزالة التجاوز بنجاح"
                : "Override removed successfully"
            await loadData()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// MARK: - Permission Row

struct PermissionRow: View {
    let permission: Permission
    let isGranted: Bool
    let source: String

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(permission.name)
                    .font(.body)

                if let code = permission.code {
                    Text(code)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                if let category = permission.category {
                    Text(category)
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(4)
                }
            }

            Spacer()

            Image(systemName: isGranted ? "checkmark.circle.fill" : "xmark.circle.fill")
                .foregroundColor(isGranted ? .green : .red)
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Permission Override Row

struct PermissionOverrideRow: View {
    let override: UserPermissionInfo
    let onRemove: () -> Void
    @EnvironmentObject var appState: AppState

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(override.permissionName)
                    .font(.body)

                Text(override.permissionCode)
                    .font(.caption)
                    .foregroundColor(.secondary)

                HStack {
                    Image(systemName: override.isGranted ? "plus.circle.fill" : "minus.circle.fill")
                        .foregroundColor(override.isGranted ? .green : .red)
                        .font(.caption)

                    Text(override.isGranted
                        ? (appState.isArabic ? "ممنوح" : "Granted")
                        : (appState.isArabic ? "ملغى" : "Revoked"))
                        .font(.caption)
                        .foregroundColor(override.isGranted ? .green : .red)
                }

                if let expiresAt = override.expiresAt {
                    Text(appState.isArabic ? "ينتهي: \(formatDate(expiresAt))" : "Expires: \(formatDate(expiresAt))")
                        .font(.caption2)
                        .foregroundColor(.orange)
                }
            }

            Spacer()

            Button {
                onRemove()
            } label: {
                Image(systemName: "arrow.uturn.backward.circle")
                    .foregroundColor(.orange)
            }
            .buttonStyle(.plain)
        }
        .padding(.vertical, 4)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

#Preview {
    let sampleUser = User(
        id: "1",
        name: "John Doe",
        email: "john@example.com",
        role: "Admin",
        branch: "Main Branch",
        permissions: [],
        mfaEnabled: nil,
        mobileApp: nil,
        platform: nil
    )

    return UserPermissionsView(user: sampleUser)
        .environmentObject(AppState())
}
