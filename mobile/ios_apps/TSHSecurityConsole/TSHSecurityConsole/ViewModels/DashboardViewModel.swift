import SwiftUI

@MainActor
class DashboardViewModel: ObservableObject {
    @Published var dashboardData: DashboardData?
    @Published var approvalStats: ApprovalService.ApprovalStats?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var lastUpdated: Date?

    private var refreshTimer: Timer?

    init() {
        startAutoRefresh()
    }

    deinit {
        refreshTimer?.invalidate()
    }

    func loadDashboard() async {
        isLoading = true
        errorMessage = nil

        do {
            async let dashboardTask = SecurityService.shared.getDashboard()
            async let statsTask = ApprovalService.shared.getStats()

            let (dashboardResponse, stats) = try await (dashboardTask, statsTask)

            dashboardData = dashboardResponse.data
            approvalStats = stats
            lastUpdated = Date()
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func startAutoRefresh() {
        refreshTimer = Timer.scheduledTimer(withTimeInterval: 60, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                await self?.loadDashboard()
            }
        }
    }

    var securityScoreColor: Color {
        guard let score = dashboardData?.security_status.security_score else {
            return .gray
        }

        if score >= 85 { return .green }
        if score >= 70 { return .orange }
        return .red
    }

    var threatLevelColor: Color {
        switch dashboardData?.security_status.threat_level ?? "low" {
        case "critical": return .purple
        case "high": return .red
        case "medium": return .orange
        default: return .green
        }
    }

    var overallStatusIcon: String {
        switch dashboardData?.security_status.overall ?? "healthy" {
        case "critical": return "exclamationmark.shield.fill"
        case "warning": return "exclamationmark.triangle.fill"
        case "monitoring": return "eye.fill"
        default: return "checkmark.shield.fill"
        }
    }
}
