import SwiftUI

struct UsersListView: View {
    @EnvironmentObject var appState: AppState
    @State private var users: [User] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var searchText = ""

    var body: some View {
        VStack {
            if users.isEmpty && !isLoading && searchText.isEmpty {
                emptyStateView
            } else {
                List {
                    ForEach(filteredUsers) { user in
                        UserRowView(user: user)
                    }
                }
                .listStyle(.plain)
                .searchable(
                    text: $searchText,
                    prompt: appState.isArabic ? "بحث..." : "Search..."
                )
            }
        }
        .navigationTitle(appState.isArabic ? "المستخدمون" : "Users")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: loadUsers) {
                    Image(systemName: "arrow.clockwise")
                }
            }
        }
        .refreshable {
            await loadUsersAsync()
        }
        .onAppear {
            loadUsers()
        }
        .alert(
            appState.isArabic ? "خطأ" : "Error",
            isPresented: Binding<Bool>(
                get: { errorMessage != nil },
                set: { if !$0 { errorMessage = nil } }
            )
        ) {
            Button("OK") { errorMessage = nil }
        } message: {
            Text(errorMessage ?? "")
        }
        .overlay {
            if isLoading && users.isEmpty {
                ProgressView()
            }
        }
    }

    private var filteredUsers: [User] {
        if searchText.isEmpty {
            return users
        }
        return users.filter {
            $0.name.localizedCaseInsensitiveContains(searchText) ||
            $0.email.localizedCaseInsensitiveContains(searchText) ||
            $0.role.localizedCaseInsensitiveContains(searchText)
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "person.3")
                .font(.system(size: 60))
                .foregroundColor(.blue)

            Text(appState.isArabic ? "لا يوجد مستخدمون" : "No Users Found")
                .font(.title2)
                .fontWeight(.semibold)

            Button(action: loadUsers) {
                Label(
                    appState.isArabic ? "تحديث" : "Refresh",
                    systemImage: "arrow.clockwise"
                )
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }

    private func loadUsers() {
        Task {
            await loadUsersAsync()
        }
    }

    private func loadUsersAsync() async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await SecurityService.shared.getUsers()
            users = response.users
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

struct UserRowView: View {
    let user: User
    @EnvironmentObject var appState: AppState

    var body: some View {
        HStack(spacing: 12) {
            // Avatar
            Circle()
                .fill(Color.blue.opacity(0.2))
                .frame(width: 44, height: 44)
                .overlay {
                    Text(user.name.prefix(1).uppercased())
                        .font(.headline)
                        .foregroundColor(.blue)
                }

            VStack(alignment: .leading, spacing: 4) {
                Text(user.name)
                    .font(.headline)

                Text(user.email)
                    .font(.caption)
                    .foregroundColor(.secondary)
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
            }
        }
        .padding(.vertical, 4)
    }

    private var roleColor: Color {
        switch user.role.lowercased() {
        case "owner", "admin": return .purple
        case "manager": return .blue
        case "salesperson": return .green
        case "accountant": return .orange
        default: return .gray
        }
    }
}

// Make User conform to Identifiable
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
