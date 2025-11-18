import SwiftUI

struct CreateUserView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState
    @ObservedObject var viewModel: UsersViewModel

    // Form fields
    @State private var name = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var phone = ""
    @State private var employeeCode = ""
    @State private var selectedRoleId: Int?
    @State private var selectedBranchId: Int?
    @State private var isSalesperson = false
    @State private var isActive = true

    // Validation
    @State private var showPasswordMismatch = false
    @State private var showValidationError = false
    @State private var validationErrorMessage = ""

    var body: some View {
        NavigationStack {
            Form {
                // Basic Information
                Section(header: Text(appState.isArabic ? "المعلومات الأساسية" : "Basic Information")) {
                    TextField(appState.isArabic ? "الاسم الكامل" : "Full Name", text: $name)
                        .textContentType(.name)

                    TextField(appState.isArabic ? "البريد الإلكتروني" : "Email", text: $email)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)

                    TextField(appState.isArabic ? "رقم الهاتف" : "Phone Number", text: $phone)
                        .textContentType(.telephoneNumber)
                        .keyboardType(.phonePad)

                    TextField(appState.isArabic ? "رمز الموظف" : "Employee Code", text: $employeeCode)
                }

                // Password
                Section(header: Text(appState.isArabic ? "كلمة المرور" : "Password")) {
                    SecureField(appState.isArabic ? "كلمة المرور" : "Password", text: $password)
                        .textContentType(.newPassword)

                    SecureField(appState.isArabic ? "تأكيد كلمة المرور" : "Confirm Password", text: $confirmPassword)
                        .textContentType(.newPassword)

                    if !password.isEmpty {
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

                // Role and Branch
                Section(header: Text(appState.isArabic ? "الدور والفرع" : "Role & Branch")) {
                    if viewModel.isLoadingRoles {
                        HStack {
                            ProgressView()
                            Text(appState.isArabic ? "جاري تحميل الأدوار..." : "Loading roles...")
                        }
                    } else {
                        Picker(appState.isArabic ? "الدور" : "Role", selection: $selectedRoleId) {
                            Text(appState.isArabic ? "اختر الدور" : "Select Role")
                                .tag(nil as Int?)

                            ForEach(viewModel.roles) { role in
                                Text(appState.isArabic ? role.localizedName : role.name)
                                    .tag(role.id as Int?)
                            }
                        }
                    }

                    if viewModel.isLoadingBranches {
                        HStack {
                            ProgressView()
                            Text(appState.isArabic ? "جاري تحميل الفروع..." : "Loading branches...")
                        }
                    } else {
                        Picker(appState.isArabic ? "الفرع" : "Branch", selection: $selectedBranchId) {
                            Text(appState.isArabic ? "اختر الفرع" : "Select Branch")
                                .tag(nil as Int?)

                            ForEach(viewModel.branches) { branch in
                                Text(branch.name)
                                    .tag(branch.id as Int?)
                            }
                        }
                    }
                }

                // Additional Options
                Section(header: Text(appState.isArabic ? "خيارات إضافية" : "Additional Options")) {
                    Toggle(
                        appState.isArabic ? "مندوب مبيعات" : "Is Salesperson",
                        isOn: $isSalesperson
                    )

                    Toggle(
                        appState.isArabic ? "الحساب نشط" : "Account Active",
                        isOn: $isActive
                    )
                }
            }
            .navigationTitle(appState.isArabic ? "إضافة مستخدم" : "Create User")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(appState.isArabic ? "إلغاء" : "Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(appState.isArabic ? "إنشاء" : "Create") {
                        createUser()
                    }
                    .disabled(!isFormValid || viewModel.isCreatingUser)
                }
            }
            .onAppear {
                Task {
                    await viewModel.loadSupportingData()
                }
            }
            .alert(
                appState.isArabic ? "خطأ في التحقق" : "Validation Error",
                isPresented: $showValidationError
            ) {
                Button("OK") {}
            } message: {
                Text(validationErrorMessage)
            }
            .overlay {
                if viewModel.isCreatingUser {
                    Color.black.opacity(0.3)
                        .ignoresSafeArea()
                    VStack {
                        ProgressView()
                        Text(appState.isArabic ? "جاري إنشاء المستخدم..." : "Creating user...")
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(10)
                }
            }
        }
        .onChange(of: confirmPassword) { _ in
            showPasswordMismatch = !confirmPassword.isEmpty && password != confirmPassword
        }
    }

    private var isFormValid: Bool {
        !name.isEmpty &&
        !email.isEmpty &&
        !password.isEmpty &&
        password == confirmPassword &&
        password.count >= 8 &&
        selectedRoleId != nil &&
        selectedBranchId != nil
    }

    private var passwordStrength: String {
        if password.count < 8 {
            return appState.isArabic ? "ضعيفة" : "Weak"
        } else if password.count < 12 {
            return appState.isArabic ? "متوسطة" : "Medium"
        } else {
            return appState.isArabic ? "قوية" : "Strong"
        }
    }

    private var passwordStrengthColor: Color {
        if password.count < 8 {
            return .red
        } else if password.count < 12 {
            return .orange
        } else {
            return .green
        }
    }

    private func createUser() {
        // Validate
        guard let roleId = selectedRoleId else {
            validationErrorMessage = appState.isArabic ? "يرجى اختيار الدور" : "Please select a role"
            showValidationError = true
            return
        }

        guard let branchId = selectedBranchId else {
            validationErrorMessage = appState.isArabic ? "يرجى اختيار الفرع" : "Please select a branch"
            showValidationError = true
            return
        }

        if password != confirmPassword {
            validationErrorMessage = appState.isArabic ? "كلمات المرور غير متطابقة" : "Passwords do not match"
            showValidationError = true
            return
        }

        Task {
            let success = await viewModel.createUser(
                name: name,
                email: email,
                password: password,
                roleId: roleId,
                branchId: branchId,
                phone: phone.isEmpty ? nil : phone,
                employeeCode: employeeCode.isEmpty ? nil : employeeCode,
                isSalesperson: isSalesperson,
                isActive: isActive
            )

            if success {
                dismiss()
            }
        }
    }
}
