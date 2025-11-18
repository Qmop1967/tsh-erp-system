import SwiftUI

struct UserDetailView: View {
    let user: User
    @ObservedObject var viewModel: UsersViewModel
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState

    @State private var showingEditUser = false
    @State private var showingResetPassword = false
    @State private var showingDeactivateConfirm = false
    @State private var showingActivateConfirm = false
    @State private var showingPermissions = false

    var body: some View {
        NavigationStack {
            List {
                // User Header
                Section {
                    HStack(spacing: 16) {
                        // Avatar
                        ZStack(alignment: .bottomTrailing) {
                            Circle()
                                .fill(Color.blue.opacity(0.2))
                                .frame(width: 80, height: 80)
                                .overlay {
                                    Text(user.name.prefix(1).uppercased())
                                        .font(.largeTitle)
                                        .foregroundColor(.blue)
                                }

                            Circle()
                                .fill((user.isActive ?? true) ? Color.green : Color.gray)
                                .frame(width: 20, height: 20)
                                .overlay(
                                    Circle().stroke(Color.white, lineWidth: 3)
                                )
                        }

                        VStack(alignment: .leading, spacing: 4) {
                            Text(user.name)
                                .font(.title2)
                                .fontWeight(.bold)

                            Text(user.email)
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            HStack {
                                Text(user.role)
                                    .font(.caption)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(roleColor.opacity(0.2))
                                    .foregroundColor(roleColor)
                                    .cornerRadius(6)

                                if !(user.isActive ?? true) {
                                    Text(appState.isArabic ? "غير نشط" : "Inactive")
                                        .font(.caption)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(Color.gray.opacity(0.2))
                                        .foregroundColor(.gray)
                                        .cornerRadius(6)
                                }
                            }
                        }

                        Spacer()
                    }
                    .padding(.vertical, 8)
                }

                // Contact Information
                Section(header: Text(appState.isArabic ? "معلومات الاتصال" : "Contact Information")) {
                    if let phone = user.phone, !phone.isEmpty {
                        DetailRow(
                            icon: "phone.fill",
                            title: appState.isArabic ? "الهاتف" : "Phone",
                            value: phone,
                            iconColor: .green
                        )
                    } else {
                        DetailRow(
                            icon: "phone",
                            title: appState.isArabic ? "الهاتف" : "Phone",
                            value: appState.isArabic ? "غير محدد" : "Not set",
                            iconColor: .gray
                        )
                    }

                    DetailRow(
                        icon: "envelope.fill",
                        title: appState.isArabic ? "البريد الإلكتروني" : "Email",
                        value: user.email,
                        iconColor: .blue
                    )
                }

                // Work Information
                Section(header: Text(appState.isArabic ? "معلومات العمل" : "Work Information")) {
                    DetailRow(
                        icon: "building.2.fill",
                        title: appState.isArabic ? "الفرع" : "Branch",
                        value: user.branch ?? (appState.isArabic ? "غير محدد" : "Not set"),
                        iconColor: .purple
                    )

                    if let employeeCode = user.employeeCode, !employeeCode.isEmpty {
                        DetailRow(
                            icon: "person.badge.shield.checkmark.fill",
                            title: appState.isArabic ? "رمز الموظف" : "Employee Code",
                            value: employeeCode,
                            iconColor: .orange
                        )
                    }

                    DetailRow(
                        icon: "briefcase.fill",
                        title: appState.isArabic ? "مندوب مبيعات" : "Is Salesperson",
                        value: (user.isSalesperson ?? false)
                            ? (appState.isArabic ? "نعم" : "Yes")
                            : (appState.isArabic ? "لا" : "No"),
                        iconColor: .teal
                    )
                }

                // Account Status
                Section(header: Text(appState.isArabic ? "حالة الحساب" : "Account Status")) {
                    DetailRow(
                        icon: (user.isActive ?? true) ? "checkmark.circle.fill" : "xmark.circle.fill",
                        title: appState.isArabic ? "الحالة" : "Status",
                        value: (user.isActive ?? true)
                            ? (appState.isArabic ? "نشط" : "Active")
                            : (appState.isArabic ? "غير نشط" : "Inactive"),
                        iconColor: (user.isActive ?? true) ? .green : .red
                    )

                    if let lastLogin = user.lastLogin {
                        DetailRow(
                            icon: "clock.arrow.circlepath",
                            title: appState.isArabic ? "آخر تسجيل دخول" : "Last Login",
                            value: formatDate(lastLogin),
                            iconColor: .blue
                        )
                    }

                    if let createdAt = user.createdAt {
                        DetailRow(
                            icon: "calendar.badge.plus",
                            title: appState.isArabic ? "تاريخ الإنشاء" : "Created",
                            value: formatDate(createdAt),
                            iconColor: .green
                        )
                    }

                    if let updatedAt = user.updatedAt {
                        DetailRow(
                            icon: "pencil.circle.fill",
                            title: appState.isArabic ? "آخر تحديث" : "Last Updated",
                            value: formatDate(updatedAt),
                            iconColor: .orange
                        )
                    }
                }

                // Security Information
                Section(header: Text(appState.isArabic ? "الأمان" : "Security")) {
                    DetailRow(
                        icon: "shield.fill",
                        title: appState.isArabic ? "المصادقة الثنائية" : "MFA Enabled",
                        value: (user.mfaEnabled ?? false)
                            ? (appState.isArabic ? "مفعّل" : "Enabled")
                            : (appState.isArabic ? "غير مفعّل" : "Disabled"),
                        iconColor: (user.mfaEnabled ?? false) ? .green : .orange
                    )

                    if let platform = user.platform, !platform.isEmpty {
                        DetailRow(
                            icon: "iphone",
                            title: appState.isArabic ? "المنصة" : "Platform",
                            value: platform,
                            iconColor: .blue
                        )
                    }

                    if let mobileApp = user.mobileApp, !mobileApp.isEmpty {
                        DetailRow(
                            icon: "app.fill",
                            title: appState.isArabic ? "التطبيق" : "Mobile App",
                            value: mobileApp,
                            iconColor: .purple
                        )
                    }
                }

                // Actions
                Section(header: Text(appState.isArabic ? "الإجراءات" : "Actions")) {
                    Button {
                        showingPermissions = true
                    } label: {
                        Label(
                            appState.isArabic ? "إدارة الصلاحيات" : "Manage Permissions",
                            systemImage: "lock.shield"
                        )
                        .foregroundColor(.blue)
                    }

                    Button {
                        showingResetPassword = true
                    } label: {
                        Label(
                            appState.isArabic ? "إعادة تعيين كلمة المرور" : "Reset Password",
                            systemImage: "key.fill"
                        )
                        .foregroundColor(.orange)
                    }

                    if user.isActive ?? true {
                        Button {
                            showingDeactivateConfirm = true
                        } label: {
                            Label(
                                appState.isArabic ? "تعطيل الحساب" : "Deactivate Account",
                                systemImage: "person.fill.xmark"
                            )
                            .foregroundColor(.red)
                        }
                    } else {
                        Button {
                            showingActivateConfirm = true
                        } label: {
                            Label(
                                appState.isArabic ? "تفعيل الحساب" : "Activate Account",
                                systemImage: "person.fill.checkmark"
                            )
                            .foregroundColor(.green)
                        }
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle(appState.isArabic ? "تفاصيل المستخدم" : "User Details")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(appState.isArabic ? "إغلاق" : "Close") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(appState.isArabic ? "تعديل" : "Edit") {
                        showingEditUser = true
                    }
                }
            }
            .sheet(isPresented: $showingEditUser) {
                EditUserView(user: user, viewModel: viewModel)
            }
            .sheet(isPresented: $showingResetPassword) {
                ResetPasswordView(user: user, viewModel: viewModel)
            }
            .sheet(isPresented: $showingPermissions) {
                UserPermissionsView(user: user)
            }
            .alert(
                appState.isArabic ? "تعطيل الحساب" : "Deactivate Account",
                isPresented: $showingDeactivateConfirm
            ) {
                Button(appState.isArabic ? "إلغاء" : "Cancel", role: .cancel) {}
                Button(appState.isArabic ? "تعطيل" : "Deactivate", role: .destructive) {
                    deactivateUser()
                }
            } message: {
                Text(appState.isArabic
                    ? "هل تريد تعطيل حساب \(user.name)؟"
                    : "Are you sure you want to deactivate \(user.name)'s account?")
            }
            .alert(
                appState.isArabic ? "تفعيل الحساب" : "Activate Account",
                isPresented: $showingActivateConfirm
            ) {
                Button(appState.isArabic ? "إلغاء" : "Cancel", role: .cancel) {}
                Button(appState.isArabic ? "تفعيل" : "Activate") {
                    activateUser()
                }
            } message: {
                Text(appState.isArabic
                    ? "هل تريد تفعيل حساب \(user.name)؟"
                    : "Are you sure you want to activate \(user.name)'s account?")
            }
            .overlay {
                if viewModel.isUpdatingUser {
                    Color.black.opacity(0.3)
                        .ignoresSafeArea()
                    VStack {
                        ProgressView()
                        Text(appState.isArabic ? "جاري التحديث..." : "Updating...")
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(10)
                }
            }
        }
    }

    private var roleColor: Color {
        switch user.role.lowercased() {
        case "owner": return .purple
        case "admin": return .pink
        case "manager": return .blue
        case "salesperson", "travel salesperson", "partner salesman": return .green
        case "accountant": return .orange
        case "inventory manager": return .teal
        case "security": return .red
        default: return .gray
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        if appState.isArabic {
            formatter.locale = Locale(identifier: "ar")
        }
        return formatter.string(from: date)
    }

    private func deactivateUser() {
        guard let userId = Int(user.id) else { return }
        Task {
            let success = await viewModel.deactivateUser(id: userId)
            if success {
                dismiss()
            }
        }
    }

    private func activateUser() {
        guard let userId = Int(user.id) else { return }
        Task {
            let success = await viewModel.activateUser(id: userId)
            if success {
                dismiss()
            }
        }
    }
}

// MARK: - Detail Row Component

struct DetailRow: View {
    let icon: String
    let title: String
    let value: String
    var iconColor: Color = .blue

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .foregroundColor(iconColor)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(value)
                    .font(.body)
            }

            Spacer()
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Reset Password View

struct ResetPasswordView: View {
    let user: User
    @ObservedObject var viewModel: UsersViewModel
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState

    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var showPasswordMismatch = false

    var body: some View {
        NavigationStack {
            Form {
                Section(header: Text(appState.isArabic ? "كلمة المرور الجديدة" : "New Password")) {
                    SecureField(
                        appState.isArabic ? "كلمة المرور الجديدة" : "New Password",
                        text: $newPassword
                    )
                    .textContentType(.newPassword)

                    SecureField(
                        appState.isArabic ? "تأكيد كلمة المرور" : "Confirm Password",
                        text: $confirmPassword
                    )
                    .textContentType(.newPassword)

                    if !newPassword.isEmpty {
                        HStack {
                            Text(appState.isArabic ? "قوة كلمة المرور:" : "Password Strength:")
                                .font(.caption)
                            Text(passwordStrength)
                                .font(.caption)
                                .foregroundColor(passwordStrengthColor)
                        }
                    }

                    if showPasswordMismatch {
                        Text(appState.isArabic ? "كلمات المرور غير متطابقة" : "Passwords do not match")
                            .foregroundColor(.red)
                            .font(.caption)
                    }
                }

                Section {
                    Text(appState.isArabic
                        ? "سيتم إعادة تعيين كلمة مرور المستخدم \(user.name). تأكد من إبلاغه بكلمة المرور الجديدة."
                        : "This will reset the password for \(user.name). Make sure to inform them of the new password.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .navigationTitle(appState.isArabic ? "إعادة تعيين كلمة المرور" : "Reset Password")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(appState.isArabic ? "إلغاء" : "Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(appState.isArabic ? "إعادة تعيين" : "Reset") {
                        resetPassword()
                    }
                    .disabled(!isFormValid)
                }
            }
            .onChange(of: confirmPassword) { _ in
                showPasswordMismatch = !confirmPassword.isEmpty && newPassword != confirmPassword
            }
        }
    }

    private var isFormValid: Bool {
        !newPassword.isEmpty &&
        newPassword == confirmPassword &&
        newPassword.count >= 8
    }

    private var passwordStrength: String {
        if newPassword.count < 8 {
            return appState.isArabic ? "ضعيفة" : "Weak"
        } else if newPassword.count < 12 {
            return appState.isArabic ? "متوسطة" : "Medium"
        } else {
            return appState.isArabic ? "قوية" : "Strong"
        }
    }

    private var passwordStrengthColor: Color {
        if newPassword.count < 8 {
            return .red
        } else if newPassword.count < 12 {
            return .orange
        } else {
            return .green
        }
    }

    private func resetPassword() {
        guard let userId = Int(user.id) else { return }

        Task {
            let success = await viewModel.resetPassword(userId: userId, newPassword: newPassword)
            if success {
                dismiss()
            }
        }
    }
}

#Preview {
    let sampleUser = User(
        id: "1",
        name: "John Doe",
        email: "john@example.com",
        role: "Admin",
        branch: "Main Branch",
        permissions: ["read", "write"],
        mfaEnabled: true,
        mobileApp: "TSHSecurityConsole",
        platform: "iOS",
        roleId: 2,
        branchId: 1,
        phone: "+964 750 123 4567",
        employeeCode: "EMP001",
        isSalesperson: false,
        isActive: true,
        lastLogin: Date(),
        createdAt: Date().addingTimeInterval(-86400 * 30),
        updatedAt: Date().addingTimeInterval(-3600)
    )

    return UserDetailView(user: sampleUser, viewModel: UsersViewModel())
        .environmentObject(AppState())
}
