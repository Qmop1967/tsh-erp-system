import SwiftUI

@MainActor
class UsersViewModel: ObservableObject {
    // MARK: - Published Properties

    @Published var users: [User] = []
    @Published var roles: [Role] = []
    @Published var branches: [Branch] = []

    @Published var selectedUser: User?
    @Published var totalUsers: Int = 0

    @Published var isLoading = false
    @Published var isLoadingRoles = false
    @Published var isLoadingBranches = false
    @Published var isCreatingUser = false
    @Published var isUpdatingUser = false
    @Published var isDeletingUser = false

    @Published var errorMessage: String?
    @Published var successMessage: String?

    @Published var searchText: String = ""
    @Published var currentPage: Int = 1
    @Published var pageSize: Int = 50

    // MARK: - Computed Properties

    var filteredUsers: [User] {
        if searchText.isEmpty {
            return users
        }
        return users.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.email.localizedCaseInsensitiveContains(searchText) ||
            $0.role.localizedCaseInsensitiveContains(searchText) ||
            ($0.phone ?? "").localizedCaseInsensitiveContains(searchText)
        }
    }

    var activeUsersCount: Int {
        users.filter { $0.isActive ?? true }.count
    }

    var inactiveUsersCount: Int {
        users.filter { !($0.isActive ?? true) }.count
    }

    // MARK: - Initialization

    init() {
        #if DEBUG
        print("👥 [UsersViewModel] Initialized")
        #endif
    }

    // MARK: - User CRUD Operations

    /// Load all users from the server
    func loadUsers() async {
        guard !isLoading else { return }

        #if DEBUG
        print("📥 [UsersViewModel] Loading users...")
        #endif

        isLoading = true
        errorMessage = nil

        do {
            let response = try await SecurityService.shared.getUsers(
                page: currentPage,
                pageSize: pageSize
            )
            users = response.users
            totalUsers = response.total

            #if DEBUG
            print("✅ [UsersViewModel] Loaded \(users.count) users (total: \(totalUsers))")
            #endif
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to load users: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    /// Get a single user by ID
    func loadUser(id: Int) async {
        #if DEBUG
        print("📥 [UsersViewModel] Loading user \(id)...")
        #endif

        isLoading = true
        errorMessage = nil

        do {
            let user = try await SecurityService.shared.getUser(id: id)
            selectedUser = user

            #if DEBUG
            print("✅ [UsersViewModel] Loaded user: \(user.name)")
            #endif
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to load user: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    /// Create a new user
    func createUser(
        name: String,
        email: String,
        password: String,
        roleId: Int,
        branchId: Int,
        phone: String? = nil,
        employeeCode: String? = nil,
        isSalesperson: Bool = false,
        isActive: Bool = true
    ) async -> Bool {
        guard !isCreatingUser else { return false }

        #if DEBUG
        print("➕ [UsersViewModel] Creating user: \(name)...")
        #endif

        isCreatingUser = true
        errorMessage = nil
        successMessage = nil

        do {
            let request = UserCreateRequest(
                name: name,
                email: email,
                password: password,
                roleId: roleId,
                branchId: branchId,
                phone: phone,
                employeeCode: employeeCode,
                isSalesperson: isSalesperson,
                isActive: isActive
            )

            let newUser = try await SecurityService.shared.createUser(request)

            // Add to local list
            users.insert(newUser, at: 0)
            totalUsers += 1

            successMessage = "User \(newUser.name) created successfully"

            #if DEBUG
            print("✅ [UsersViewModel] Created user: \(newUser.name) (ID: \(newUser.id))")
            #endif

            isCreatingUser = false
            return true
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to create user: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            isCreatingUser = false
            return false
        }
    }

    /// Update an existing user
    func updateUser(
        id: Int,
        name: String? = nil,
        email: String? = nil,
        roleId: Int? = nil,
        branchId: Int? = nil,
        phone: String? = nil,
        employeeCode: String? = nil,
        isSalesperson: Bool? = nil,
        isActive: Bool? = nil,
        password: String? = nil
    ) async -> Bool {
        guard !isUpdatingUser else { return false }

        #if DEBUG
        print("✏️ [UsersViewModel] Updating user \(id)...")
        #endif

        isUpdatingUser = true
        errorMessage = nil
        successMessage = nil

        do {
            var request = UserUpdateRequest()
            request.name = name
            request.email = email
            request.roleId = roleId
            request.branchId = branchId
            request.phone = phone
            request.employeeCode = employeeCode
            request.isSalesperson = isSalesperson
            request.isActive = isActive
            request.password = password

            let updatedUser = try await SecurityService.shared.updateUser(id: id, request)

            // Update local list
            if let index = users.firstIndex(where: { $0.id == updatedUser.id }) {
                users[index] = updatedUser
            }

            selectedUser = updatedUser
            successMessage = "User \(updatedUser.name) updated successfully"

            #if DEBUG
            print("✅ [UsersViewModel] Updated user: \(updatedUser.name)")
            #endif

            isUpdatingUser = false
            return true
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to update user: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            isUpdatingUser = false
            return false
        }
    }

    /// Delete (deactivate) a user
    func deleteUser(id: Int) async -> Bool {
        guard !isDeletingUser else { return false }

        #if DEBUG
        print("🗑️ [UsersViewModel] Deleting user \(id)...")
        #endif

        isDeletingUser = true
        errorMessage = nil
        successMessage = nil

        do {
            let response = try await SecurityService.shared.deleteUser(id: id)

            // Update local list (mark as inactive)
            if let index = users.firstIndex(where: { Int($0.id) == id }) {
                // Remove or update the user in the list
                users.remove(at: index)
                totalUsers -= 1
            }

            successMessage = response.message

            #if DEBUG
            print("✅ [UsersViewModel] Deleted user \(id): \(response.message)")
            #endif

            isDeletingUser = false
            return true
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to delete user: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            isDeletingUser = false
            return false
        }
    }

    /// Activate a user
    func activateUser(id: Int) async -> Bool {
        #if DEBUG
        print("✅ [UsersViewModel] Activating user \(id)...")
        #endif

        errorMessage = nil
        successMessage = nil

        do {
            let response = try await SecurityService.shared.activateUser(id: id)

            // Update local list
            if let index = users.firstIndex(where: { Int($0.id) == id }) {
                var updatedUser = users[index]
                updatedUser = User(
                    id: updatedUser.id,
                    name: updatedUser.name,
                    email: updatedUser.email,
                    role: updatedUser.role,
                    branch: updatedUser.branch,
                    permissions: updatedUser.permissions,
                    mfaEnabled: updatedUser.mfaEnabled,
                    mobileApp: updatedUser.mobileApp,
                    platform: updatedUser.platform,
                    roleId: updatedUser.roleId,
                    branchId: updatedUser.branchId,
                    phone: updatedUser.phone,
                    employeeCode: updatedUser.employeeCode,
                    isSalesperson: updatedUser.isSalesperson,
                    isActive: true,
                    lastLogin: updatedUser.lastLogin,
                    createdAt: updatedUser.createdAt,
                    updatedAt: updatedUser.updatedAt
                )
                users[index] = updatedUser
            }

            successMessage = response.message

            #if DEBUG
            print("✅ [UsersViewModel] Activated user \(id)")
            #endif

            return true
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to activate user: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            return false
        }
    }

    /// Deactivate a user
    func deactivateUser(id: Int) async -> Bool {
        #if DEBUG
        print("⛔ [UsersViewModel] Deactivating user \(id)...")
        #endif

        errorMessage = nil
        successMessage = nil

        do {
            let response = try await SecurityService.shared.deactivateUser(id: id)

            // Update local list
            if let index = users.firstIndex(where: { Int($0.id) == id }) {
                var updatedUser = users[index]
                updatedUser = User(
                    id: updatedUser.id,
                    name: updatedUser.name,
                    email: updatedUser.email,
                    role: updatedUser.role,
                    branch: updatedUser.branch,
                    permissions: updatedUser.permissions,
                    mfaEnabled: updatedUser.mfaEnabled,
                    mobileApp: updatedUser.mobileApp,
                    platform: updatedUser.platform,
                    roleId: updatedUser.roleId,
                    branchId: updatedUser.branchId,
                    phone: updatedUser.phone,
                    employeeCode: updatedUser.employeeCode,
                    isSalesperson: updatedUser.isSalesperson,
                    isActive: false,
                    lastLogin: updatedUser.lastLogin,
                    createdAt: updatedUser.createdAt,
                    updatedAt: updatedUser.updatedAt
                )
                users[index] = updatedUser
            }

            successMessage = response.message

            #if DEBUG
            print("✅ [UsersViewModel] Deactivated user \(id)")
            #endif

            return true
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to deactivate user: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            return false
        }
    }

    /// Reset user password
    func resetPassword(userId: Int, newPassword: String) async -> Bool {
        #if DEBUG
        print("🔑 [UsersViewModel] Resetting password for user \(userId)...")
        #endif

        errorMessage = nil
        successMessage = nil

        do {
            let response = try await SecurityService.shared.resetUserPassword(
                id: userId,
                newPassword: newPassword
            )
            successMessage = response.message

            #if DEBUG
            print("✅ [UsersViewModel] Password reset successful")
            #endif

            return true
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to reset password: \(error.localizedDescription)")
            #endif
            errorMessage = error.localizedDescription
            return false
        }
    }

    // MARK: - Supporting Data

    /// Load roles and branches for form pickers
    func loadSupportingData() async {
        await withTaskGroup(of: Void.self) { group in
            group.addTask { await self.loadRoles() }
            group.addTask { await self.loadBranches() }
        }
    }

    /// Load all available roles
    func loadRoles() async {
        guard !isLoadingRoles else { return }

        #if DEBUG
        print("📥 [UsersViewModel] Loading roles...")
        #endif

        isLoadingRoles = true

        do {
            roles = try await SecurityService.shared.getRoles()

            #if DEBUG
            print("✅ [UsersViewModel] Loaded \(roles.count) roles")
            #endif
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to load roles: \(error.localizedDescription)")
            #endif
            // Don't set errorMessage - this is secondary data
        }

        isLoadingRoles = false
    }

    /// Load all available branches
    func loadBranches() async {
        guard !isLoadingBranches else { return }

        #if DEBUG
        print("📥 [UsersViewModel] Loading branches...")
        #endif

        isLoadingBranches = true

        do {
            branches = try await SecurityService.shared.getBranches()

            #if DEBUG
            print("✅ [UsersViewModel] Loaded \(branches.count) branches")
            #endif
        } catch {
            #if DEBUG
            print("❌ [UsersViewModel] Failed to load branches: \(error.localizedDescription)")
            #endif
            // Don't set errorMessage - this is secondary data
        }

        isLoadingBranches = false
    }

    // MARK: - Helper Methods

    func clearMessages() {
        errorMessage = nil
        successMessage = nil
    }

    func getRoleName(for roleId: Int?) -> String {
        guard let roleId = roleId else { return "Unknown" }
        return roles.first(where: { $0.id == roleId })?.name ?? "Unknown"
    }

    func getBranchName(for branchId: Int?) -> String {
        guard let branchId = branchId else { return "Unknown" }
        return branches.first(where: { $0.id == branchId })?.name ?? "Unknown"
    }
}
