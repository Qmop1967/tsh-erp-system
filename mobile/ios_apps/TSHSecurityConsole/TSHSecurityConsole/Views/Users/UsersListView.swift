import SwiftUI

struct UsersListView: View {
    @EnvironmentObject var appState: AppState
    @StateObject private var viewModel = UsersViewModel()
    @State private var showingCreateUser = false
    @State private var showingDeleteConfirmation = false
    @State private var userToDelete: User?
    @State private var selectedUser: User?
    @State private var showingUserDetail = false

    var body: some View {
        VStack {
            if viewModel.users.isEmpty && !viewModel.isLoading {
                emptyStateView
            } else {
                List {
                    ForEach(viewModel.filteredUsers) { user in
                        UserRowView(user: user)
                            .onTapGesture {
                                selectedUser = user
                                showingUserDetail = true
                            }
                            .swipeActions(edge: .trailing, allowsFullSwipe: false) {
                                Button(role: .destructive) {
                                    userToDelete = user
                                    showingDeleteConfirmation = true
                                } label: {
                                    Label(
                                        appState.isArabic ? "حذف" : "Delete",
                                        systemImage: "trash"
                                    )
                                }

                                if user.isActive ?? true {
                                    Button {
                                        Task {
                                            if let userId = Int(user.id) {
                                                _ = await viewModel.deactivateUser(id: userId)
                                            }
                                        }
                                    } label: {
                                        Label(
                                            appState.isArabic ? "تعطيل" : "Deactivate",
                                            systemImage: "person.fill.xmark"
                                        )
                                    }
                                    .tint(.orange)
                                } else {
                                    Button {
                                        Task {
                                            if let userId = Int(user.id) {
                                                _ = await viewModel.activateUser(id: userId)
                                            }
                                        }
                                    } label: {
                                        Label(
                                            appState.isArabic ? "تفعيل" : "Activate",
                                            systemImage: "person.fill.checkmark"
                                        )
                                    }
                                    .tint(.green)
                                }
                            }
                    }
                }
                .listStyle(.plain)
                .searchable(
                    text: $viewModel.searchText,
                    prompt: appState.isArabic ? "بحث..." : "Search..."
                )
            }
        }
        .navigationTitle(appState.isArabic ? "المستخدمون" : "Users")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                HStack {
                    Button(action: {
                        Task { await viewModel.loadUsers() }
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }

                    Button(action: {
                        showingCreateUser = true
                    }) {
                        Image(systemName: "person.badge.plus")
                    }
                }
            }
        }
        .refreshable {
            await viewModel.loadUsers()
        }
        .onAppear {
            Task { await viewModel.loadUsers() }
        }
        .alert(
            appState.isArabic ? "خطأ" : "Error",
            isPresented: Binding<Bool>(
                get: { viewModel.errorMessage != nil },
                set: { if !$0 { viewModel.errorMessage = nil } }
            )
        ) {
            Button("OK") { viewModel.errorMessage = nil }
        } message: {
            Text(viewModel.errorMessage ?? "")
        }
        .alert(
            appState.isArabic ? "تأكيد الحذف" : "Confirm Delete",
            isPresented: $showingDeleteConfirmation
        ) {
            Button(appState.isArabic ? "إلغاء" : "Cancel", role: .cancel) {}
            Button(appState.isArabic ? "حذف" : "Delete", role: .destructive) {
                if let user = userToDelete, let userId = Int(user.id) {
                    Task { await viewModel.deleteUser(id: userId) }
                }
            }
        } message: {
            if let user = userToDelete {
                Text(appState.isArabic
                    ? "هل تريد حذف المستخدم \(user.name)؟"
                    : "Are you sure you want to delete \(user.name)?")
            }
        }
        .overlay {
            if viewModel.isLoading && viewModel.users.isEmpty {
                ProgressView()
            }
        }
        .sheet(isPresented: $showingCreateUser) {
            CreateUserView(viewModel: viewModel)
        }
        .sheet(isPresented: $showingUserDetail) {
            if let user = selectedUser {
                UserDetailView(user: user, viewModel: viewModel)
            }
        }
        // Show success message
        .overlay(alignment: .bottom) {
            if let successMessage = viewModel.successMessage {
                Text(successMessage)
                    .padding()
                    .background(Color.green.opacity(0.9))
                    .foregroundColor(.white)
                    .cornerRadius(10)
                    .padding()
                    .transition(.move(edge: .bottom))
                    .onAppear {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
                            viewModel.successMessage = nil
                        }
                    }
            }
        }
        .animation(.easeInOut, value: viewModel.successMessage)
    }

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "person.3")
                .font(.system(size: 60))
                .foregroundColor(.blue)

            Text(appState.isArabic ? "لا يوجد مستخدمون" : "No Users Found")
                .font(.title2)
                .fontWeight(.semibold)

            Button(action: {
                Task { await viewModel.loadUsers() }
            }) {
                Label(
                    appState.isArabic ? "تحديث" : "Refresh",
                    systemImage: "arrow.clockwise"
                )
            }
            .buttonStyle(.bordered)

            Button(action: {
                showingCreateUser = true
            }) {
                Label(
                    appState.isArabic ? "إضافة مستخدم" : "Add User",
                    systemImage: "person.badge.plus"
                )
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

struct UserRowView: View {
    let user: User
    @EnvironmentObject var appState: AppState

    var body: some View {
        HStack(spacing: 12) {
            // Avatar with status indicator
            ZStack(alignment: .bottomTrailing) {
                Circle()
                    .fill(Color.blue.opacity(0.2))
                    .frame(width: 44, height: 44)
                    .overlay {
                        Text(user.name.prefix(1).uppercased())
                            .font(.headline)
                            .foregroundColor(.blue)
                    }

                // Active/Inactive indicator
                Circle()
                    .fill((user.isActive ?? true) ? Color.green : Color.gray)
                    .frame(width: 12, height: 12)
                    .overlay(
                        Circle()
                            .stroke(Color.white, lineWidth: 2)
                    )
            }

            VStack(alignment: .leading, spacing: 4) {
                HStack {
                    Text(user.name)
                        .font(.headline)

                    if !(user.isActive ?? true) {
                        Text(appState.isArabic ? "غير نشط" : "Inactive")
                            .font(.caption2)
                            .padding(.horizontal, 4)
                            .padding(.vertical, 1)
                            .background(Color.gray.opacity(0.3))
                            .cornerRadius(4)
                    }
                }

                Text(user.email)
                    .font(.caption)
                    .foregroundColor(.secondary)

                if let phone = user.phone, !phone.isEmpty {
                    Text(phone)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 4) {
                Text(user.role)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 2)
                    .background(roleColor.opacity(0.2))
                    .foregroundColor(roleColor)
                    .cornerRadius(4)

                if let branch = user.branch {
                    Text(branch)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }

                if user.isSalesperson ?? false {
                    Image(systemName: "briefcase.fill")
                        .font(.caption)
                        .foregroundColor(.green)
                }
            }

            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 4)
        .contentShape(Rectangle()) // Make entire row tappable
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
}

// Make User conform to Equatable
extension User: Equatable {
    static func == (lhs: User, rhs: User) -> Bool {
        lhs.id == rhs.id
    }
}

#Preview {
    NavigationStack {
        UsersListView()
            .environmentObject(AppState())
    }
}
