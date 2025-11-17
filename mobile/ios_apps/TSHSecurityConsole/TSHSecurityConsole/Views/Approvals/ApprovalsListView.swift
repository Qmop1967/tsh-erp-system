import SwiftUI

struct ApprovalsListView: View {
    @StateObject private var viewModel = ApprovalsViewModel()
    @EnvironmentObject var appState: AppState
    @State private var showingScanner = false
    @State private var showingApproveSheet = false
    @State private var selectedApprovalForAction: Approval?
    @State private var approvalCode = ""
    @State private var denyReason = ""
    @State private var showingDenySheet = false

    var navigateToId: String?

    var body: some View {
        VStack {
            if viewModel.pendingApprovals.isEmpty && !viewModel.isLoading {
                emptyStateView
            } else {
                List {
                    ForEach(viewModel.pendingApprovals) { approval in
                        ApprovalRowView(approval: approval)
                            .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                                Button(role: .destructive) {
                                    selectedApprovalForAction = approval
                                    showingDenySheet = true
                                } label: {
                                    Label(appState.isArabic ? "رفض" : "Deny", systemImage: "xmark.circle")
                                }

                                Button {
                                    selectedApprovalForAction = approval
                                    approvalCode = approval.approval_code
                                    showingApproveSheet = true
                                } label: {
                                    Label(appState.isArabic ? "موافقة" : "Approve", systemImage: "checkmark.circle")
                                }
                                .tint(.green)
                            }
                            .onAppear {
                                if approval.id == viewModel.pendingApprovals.last?.id {
                                    Task {
                                        await viewModel.loadMorePending()
                                    }
                                }
                            }
                    }
                }
                .listStyle(.plain)
            }
        }
        .navigationTitle(appState.isArabic ? "الموافقات المعلقة" : "Pending Approvals")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: { showingScanner = true }) {
                    Image(systemName: "qrcode.viewfinder")
                }
            }

            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: {
                    Task { await viewModel.loadPendingApprovals() }
                }) {
                    Image(systemName: "arrow.clockwise")
                }
            }
        }
        .refreshable {
            await viewModel.loadPendingApprovals()
        }
        .onAppear {
            Task {
                await viewModel.loadPendingApprovals()
            }
        }
        .sheet(isPresented: $showingScanner) {
            QRScannerView { payload in
                Task {
                    let success = await viewModel.scanQRApprove(payload: payload)
                    if success {
                        showingScanner = false
                    }
                }
            }
        }
        .sheet(isPresented: $showingApproveSheet) {
            approveSheet
        }
        .sheet(isPresented: $showingDenySheet) {
            denySheet
        }
        .alert(
            appState.isArabic ? "تم بنجاح" : "Success",
            isPresented: Binding<Bool>(
                get: { viewModel.successMessage != nil },
                set: { if !$0 { viewModel.clearMessages() } }
            )
        ) {
            Button("OK") { viewModel.clearMessages() }
        } message: {
            Text(viewModel.successMessage ?? "")
        }
        .alert(
            appState.isArabic ? "خطأ" : "Error",
            isPresented: Binding<Bool>(
                get: { viewModel.errorMessage != nil },
                set: { if !$0 { viewModel.clearMessages() } }
            )
        ) {
            Button("OK") { viewModel.clearMessages() }
        } message: {
            Text(viewModel.errorMessage ?? "")
        }
        .overlay {
            if viewModel.isLoading && viewModel.pendingApprovals.isEmpty {
                ProgressView()
            }
        }
    }

    private var emptyStateView: some View {
        VStack(spacing: 16) {
            Image(systemName: "checkmark.shield.fill")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text(appState.isArabic ? "لا توجد موافقات معلقة" : "No Pending Approvals")
                .font(.title2)
                .fontWeight(.semibold)

            Text(appState.isArabic ? "جميع الطلبات تمت معالجتها" : "All requests have been processed")
                .foregroundColor(.secondary)

            Button(action: {
                Task { await viewModel.loadPendingApprovals() }
            }) {
                Label(
                    appState.isArabic ? "تحديث" : "Refresh",
                    systemImage: "arrow.clockwise"
                )
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }

    private var approveSheet: some View {
        NavigationStack {
            VStack(spacing: 20) {
                if let approval = selectedApprovalForAction {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(appState.isArabic ? "تفاصيل الطلب" : "Request Details")
                            .font(.headline)

                        Text(approval.request_description)
                            .foregroundColor(.secondary)

                        if let ar = approval.request_description_ar {
                            Text(ar)
                                .foregroundColor(.secondary)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                }

                TextField(
                    appState.isArabic ? "رمز الموافقة" : "Approval Code",
                    text: $approvalCode
                )
                .keyboardType(.numberPad)
                .textFieldStyle(.roundedBorder)
                .font(.title)
                .multilineTextAlignment(.center)

                if viewModel.isLoading {
                    ProgressView()
                }

                Spacer()
            }
            .padding()
            .navigationTitle(appState.isArabic ? "الموافقة على الطلب" : "Approve Request")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(appState.isArabic ? "إلغاء" : "Cancel") {
                        showingApproveSheet = false
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button(appState.isArabic ? "موافقة" : "Approve") {
                        Task {
                            let success = await viewModel.approveRequest(code: approvalCode)
                            if success {
                                showingApproveSheet = false
                                approvalCode = ""
                            }
                        }
                    }
                    .disabled(approvalCode.count != 6)
                }
            }
        }
    }

    private var denySheet: some View {
        NavigationStack {
            VStack(spacing: 20) {
                if let approval = selectedApprovalForAction {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(appState.isArabic ? "رفض الطلب" : "Deny Request")
                            .font(.headline)

                        Text(approval.request_description)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(8)
                }

                TextField(
                    appState.isArabic ? "سبب الرفض" : "Reason for denial",
                    text: $denyReason,
                    axis: .vertical
                )
                .textFieldStyle(.roundedBorder)
                .lineLimit(3...6)

                Spacer()
            }
            .padding()
            .navigationTitle(appState.isArabic ? "رفض الطلب" : "Deny Request")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(appState.isArabic ? "إلغاء" : "Cancel") {
                        showingDenySheet = false
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button(appState.isArabic ? "رفض" : "Deny") {
                        Task {
                            if let approval = selectedApprovalForAction {
                                let success = await viewModel.denyRequest(id: approval.id, reason: denyReason)
                                if success {
                                    showingDenySheet = false
                                    denyReason = ""
                                }
                            }
                        }
                    }
                    .disabled(denyReason.count < 10)
                    .foregroundColor(.red)
                }
            }
        }
    }
}

struct ApprovalRowView: View {
    let approval: Approval
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                riskBadge

                Text(approval.approval_type.displayName)
                    .font(.headline)

                Spacer()

                Text(approval.timeRemaining)
                    .font(.caption)
                    .foregroundColor(approval.is_expired ? .red : .secondary)
            }

            Text(appState.isArabic ? (approval.request_description_ar ?? approval.request_description) : approval.request_description)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .lineLimit(2)

            HStack {
                Label(approval.requester.name, systemImage: "person")
                Spacer()
                Label(approval.ip_address ?? "Unknown", systemImage: "network")
            }
            .font(.caption)
            .foregroundColor(.secondary)
        }
        .padding(.vertical, 4)
    }

    private var riskBadge: some View {
        Text(approval.risk_level.rawValue.uppercased())
            .font(.caption2)
            .fontWeight(.bold)
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(riskColor.opacity(0.2))
            .foregroundColor(riskColor)
            .cornerRadius(4)
    }

    private var riskColor: Color {
        switch approval.risk_level {
        case .low: return .green
        case .medium: return .orange
        case .high: return .red
        case .critical: return .purple
        }
    }
}

#Preview {
    NavigationStack {
        ApprovalsListView()
            .environmentObject(AppState())
    }
}
