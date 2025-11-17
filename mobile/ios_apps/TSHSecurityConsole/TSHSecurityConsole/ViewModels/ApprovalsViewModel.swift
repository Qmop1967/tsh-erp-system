import SwiftUI

@MainActor
class ApprovalsViewModel: ObservableObject {
    @Published var pendingApprovals: [Approval] = []
    @Published var allApprovals: [Approval] = []
    @Published var selectedApproval: Approval?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var successMessage: String?
    @Published var total = 0
    @Published var hasMore = false

    private var currentPage = 1

    func loadPendingApprovals() async {
        isLoading = true
        errorMessage = nil
        currentPage = 1

        do {
            let response = try await ApprovalService.shared.getPendingApprovals(page: 1)
            pendingApprovals = response.approvals
            total = response.total
            hasMore = response.has_more
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func loadMorePending() async {
        guard hasMore, !isLoading else { return }

        currentPage += 1

        do {
            let response = try await ApprovalService.shared.getPendingApprovals(page: currentPage)
            pendingApprovals.append(contentsOf: response.approvals)
            hasMore = response.has_more
        } catch {
            currentPage -= 1
            errorMessage = error.localizedDescription
        }
    }

    func loadAllApprovals(status: String? = nil, riskLevel: String? = nil) async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await ApprovalService.shared.getAllApprovals(
                status: status,
                riskLevel: riskLevel,
                page: 1
            )
            allApprovals = response.approvals
            total = response.total
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func approveRequest(code: String, reason: String? = nil) async -> Bool {
        isLoading = true
        errorMessage = nil
        successMessage = nil

        // Try biometric verification first
        var biometricVerified = false
        if BiometricAuth.shared.isBiometricAvailable {
            do {
                biometricVerified = try await BiometricAuth.shared.authenticate(
                    reason: "Verify your identity to approve this request"
                )
            } catch {
                // Continue without biometric
            }
        }

        do {
            let response = try await ApprovalService.shared.approveRequest(
                code: code,
                reason: reason,
                biometricVerified: biometricVerified
            )

            successMessage = response.message

            // Remove from pending list
            pendingApprovals.removeAll { $0.approval_code == code }

            isLoading = false
            return true
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }

    func denyRequest(id: String, reason: String) async -> Bool {
        isLoading = true
        errorMessage = nil
        successMessage = nil

        do {
            let response = try await ApprovalService.shared.denyRequest(
                id: id,
                reason: reason
            )

            successMessage = response.message

            // Remove from pending list
            pendingApprovals.removeAll { $0.id == id }

            isLoading = false
            return true
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }

    func scanQRApprove(payload: String) async -> Bool {
        isLoading = true
        errorMessage = nil
        successMessage = nil

        var biometricVerified = false
        if BiometricAuth.shared.isBiometricAvailable {
            do {
                biometricVerified = try await BiometricAuth.shared.authenticate(
                    reason: "Verify your identity for QR approval"
                )
            } catch {
                // Continue without biometric
            }
        }

        do {
            let response = try await ApprovalService.shared.scanQRApprove(
                payload: payload,
                biometricVerified: biometricVerified
            )

            successMessage = response.message

            // Reload pending list
            await loadPendingApprovals()

            isLoading = false
            return true
        } catch {
            errorMessage = error.localizedDescription
            isLoading = false
            return false
        }
    }

    func clearMessages() {
        errorMessage = nil
        successMessage = nil
    }
}
