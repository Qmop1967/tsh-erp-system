import SwiftUI

struct EditUserView: View {
    let user: User
    @ObservedObject var viewModel: UsersViewModel
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState

    // Form fields - pre-populated with user data
    @State private var name: String
    @State private var email: String
    @State private var phone: String
    @State private var employeeCode: String
    @State private var selectedRoleId: Int?
    @State private var selectedBranchId: Int?
    @State private var isSalesperson: Bool
    @State private var isActive: Bool

    // Validation
    @State private var showValidationError = false
    @State private var validationErrorMessage = ""

    init(user: User, viewModel: UsersViewModel) {
        self.user = user
        self.viewModel = viewModel

        // Initialize state with user's current values
        _name = State(initialValue: user.name)
        _email = State(initialValue: user.email)
        _phone = State(initialValue: user.phone ?? "")
        _employeeCode = State(initialValue: user.employeeCode ?? "")
        _selectedRoleId = State(initialValue: user.roleId)
        _selectedBranchId = State(initialValue: user.branchId)
        _isSalesperson = State(initialValue: user.isSalesperson ?? false)
        _isActive = State(initialValue: user.isActive ?? true)
    }

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

                // Changes Summary
                if hasChanges {
                    Section(header: Text(appState.isArabic ? "التغييرات" : "Changes")) {
                        ForEach(changedFields, id: \.self) { field in
                            HStack {
                                Image(systemName: "pencil.circle.fill")
                                    .foregroundColor(.orange)
                                Text(field)
                                    .font(.caption)
                            }
                        }
                    }
                }
            }
            .navigationTitle(appState.isArabic ? "تعديل المستخدم" : "Edit User")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(appState.isArabic ? "إلغاء" : "Cancel") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(appState.isArabic ? "حفظ" : "Save") {
                        saveChanges()
                    }
                    .disabled(!isFormValid || !hasChanges || viewModel.isUpdatingUser)
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
                if viewModel.isUpdatingUser {
                    Color.black.opacity(0.3)
                        .ignoresSafeArea()
                    VStack {
                        ProgressView()
                        Text(appState.isArabic ? "جاري حفظ التغييرات..." : "Saving changes...")
                    }
                    .padding()
                    .background(Color.white)
                    .cornerRadius(10)
                }
            }
        }
    }

    private var isFormValid: Bool {
        !name.isEmpty &&
        !email.isEmpty &&
        selectedRoleId != nil &&
        selectedBranchId != nil
    }

    private var hasChanges: Bool {
        name != user.name ||
        email != user.email ||
        phone != (user.phone ?? "") ||
        employeeCode != (user.employeeCode ?? "") ||
        selectedRoleId != user.roleId ||
        selectedBranchId != user.branchId ||
        isSalesperson != (user.isSalesperson ?? false) ||
        isActive != (user.isActive ?? true)
    }

    private var changedFields: [String] {
        var fields: [String] = []

        if name != user.name {
            fields.append(appState.isArabic ? "الاسم" : "Name")
        }
        if email != user.email {
            fields.append(appState.isArabic ? "البريد الإلكتروني" : "Email")
        }
        if phone != (user.phone ?? "") {
            fields.append(appState.isArabic ? "الهاتف" : "Phone")
        }
        if employeeCode != (user.employeeCode ?? "") {
            fields.append(appState.isArabic ? "رمز الموظف" : "Employee Code")
        }
        if selectedRoleId != user.roleId {
            fields.append(appState.isArabic ? "الدور" : "Role")
        }
        if selectedBranchId != user.branchId {
            fields.append(appState.isArabic ? "الفرع" : "Branch")
        }
        if isSalesperson != (user.isSalesperson ?? false) {
            fields.append(appState.isArabic ? "مندوب مبيعات" : "Is Salesperson")
        }
        if isActive != (user.isActive ?? true) {
            fields.append(appState.isArabic ? "الحالة" : "Status")
        }

        return fields
    }

    private func saveChanges() {
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

        guard let userId = Int(user.id) else {
            validationErrorMessage = appState.isArabic ? "معرف المستخدم غير صالح" : "Invalid user ID"
            showValidationError = true
            return
        }

        Task {
            let success = await viewModel.updateUser(
                id: userId,
                name: name != user.name ? name : nil,
                email: email != user.email ? email : nil,
                roleId: selectedRoleId != user.roleId ? roleId : nil,
                branchId: selectedBranchId != user.branchId ? branchId : nil,
                phone: phone != (user.phone ?? "") ? (phone.isEmpty ? nil : phone) : nil,
                employeeCode: employeeCode != (user.employeeCode ?? "") ? (employeeCode.isEmpty ? nil : employeeCode) : nil,
                isSalesperson: isSalesperson != (user.isSalesperson ?? false) ? isSalesperson : nil,
                isActive: isActive != (user.isActive ?? true) ? isActive : nil
            )

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

    return EditUserView(user: sampleUser, viewModel: UsersViewModel())
        .environmentObject(AppState())
}
