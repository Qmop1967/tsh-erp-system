import SwiftUI

struct SessionsListView: View {
    @EnvironmentObject var appState: AppState
    @State private var sessions: [Session] = []
    @State private var isLoading = false
    @State private var errorMessage: String?
    @State private var selectedSession: Session?
    @State private var showingTerminateAlert = false
    @State private var terminateReason = ""

    var body: some View {
        VStack {
            if sessions.isEmpty && !isLoading {
                emptyStateView
            } else {
                List {
                    ForEach(sessions) { session in
                        SessionRowView(session: session)
                            .swipeActions(edge: .trailing) {
                                if session.can_terminate {
                                    Button(role: .destructive) {
                                        selectedSession = session
                                        showingTerminateAlert = true
                                    } label: {
                                        Label(
                                            appState.isArabic ? "إنهاء" : "Terminate",
                                            systemImage: "xmark.circle"
                                        )
                                    }
                                }
                            }
                    }
                }
                .listStyle(.plain)
            }
        }
        .navigationTitle(appState.isArabic ? "الجلسات النشطة" : "Active Sessions")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: loadSessions) {
                    Image(systemName: "arrow.clockwise")
                }
            }
        }
        .refreshable {
            await loadSessionsAsync()
        }
        .onAppear {
            loadSessions()
        }
        .alert(
            appState.isArabic ? "إنهاء الجلسة" : "Terminate Session",
            isPresented: $showingTerminateAlert,
            presenting: selectedSession
        ) { session in
            TextField(
                appState.isArabic ? "سبب الإنهاء" : "Reason",
                text: $terminateReason
            )

            Button(appState.isArabic ? "إنهاء" : "Terminate", role: .destructive) {
                Task {
                    await terminateSession(session)
                }
            }

            Button(appState.isArabic ? "إلغاء" : "Cancel", role: .cancel) {}
        } message: { session in
            Text(appState.isArabic ?
                "هل أنت متأكد من إنهاء جلسة \(session.user_name)؟" :
                "Are you sure you want to terminate the session for \(session.user_name)?")
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
            if isLoading && sessions.isEmpty {
                ProgressView()
            }
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "person.crop.circle.badge.checkmark")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text(appState.isArabic ? "لا توجد جلسات نشطة" : "No Active Sessions")
                .font(.title2)
                .fontWeight(.semibold)

            Button(action: loadSessions) {
                Label(
                    appState.isArabic ? "تحديث" : "Refresh",
                    systemImage: "arrow.clockwise"
                )
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }

    private func loadSessions() {
        Task {
            await loadSessionsAsync()
        }
    }

    private func loadSessionsAsync() async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await SecurityService.shared.getActiveSessions()
            if let data = response.data {
                sessions = data.sessions
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    private func terminateSession(_ session: Session) async {
        do {
            let _ = try await SecurityService.shared.terminateSession(
                sessionId: session.id,
                reason: terminateReason.isEmpty ? "Terminated by admin" : terminateReason
            )

            // Remove from list
            sessions.removeAll { $0.id == session.id }
            terminateReason = ""
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct SessionRowView: View {
    let session: Session
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: session.deviceIcon)
                    .foregroundColor(.blue)

                VStack(alignment: .leading) {
                    Text(session.user_name)
                        .font(.headline)

                    Text(session.user_email)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                riskBadge
            }

            HStack {
                Label(session.ip_address ?? "Unknown", systemImage: "network")
                Spacer()
                Label(session.locationString, systemImage: "location")
            }
            .font(.caption)
            .foregroundColor(.secondary)

            if let lastActivity = session.last_activity {
                Text(appState.isArabic ? "آخر نشاط: \(lastActivity)" : "Last activity: \(lastActivity)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 4)
    }

    private var riskBadge: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(riskColor)
                .frame(width: 8, height: 8)

            Text(String(format: "%.1f", session.risk_score))
                .font(.caption)
                .foregroundColor(riskColor)
        }
    }

    private var riskColor: Color {
        switch session.risk_level.lowercased() {
        case "critical": return .purple
        case "high": return .red
        case "medium": return .orange
        default: return .green
        }
    }
}

#Preview {
    NavigationStack {
        SessionsListView()
            .environmentObject(AppState())
    }
}
