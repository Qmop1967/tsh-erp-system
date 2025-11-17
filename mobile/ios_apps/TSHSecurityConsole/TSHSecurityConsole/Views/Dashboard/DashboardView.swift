import SwiftUI

struct DashboardView: View {
    @StateObject private var viewModel = DashboardViewModel()
    @EnvironmentObject var appState: AppState

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Security Score Card
                securityScoreCard

                // Alerts Summary
                alertsGrid

                // Active Sessions
                activeSessionsCard

                // Failed Logins
                failedLoginsCard

                // Pending Approvals
                pendingApprovalsCard

                // Recent Events
                recentEventsCard
            }
            .padding()
        }
        .navigationTitle(appState.isArabic ? "لوحة المراقبة" : "Security Dashboard")
        .refreshable {
            await viewModel.loadDashboard()
        }
        .onAppear {
            Task {
                await viewModel.loadDashboard()
            }
        }
        .overlay {
            if viewModel.isLoading && viewModel.dashboardData == nil {
                ProgressView()
            }
        }
    }

    // MARK: - Security Score Card
    private var securityScoreCard: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: viewModel.overallStatusIcon)
                    .font(.title)
                    .foregroundColor(viewModel.securityScoreColor)

                VStack(alignment: .leading) {
                    Text(appState.isArabic ? "درجة الأمان" : "Security Score")
                        .font(.headline)

                    Text(viewModel.dashboardData?.security_status.overall.uppercased() ?? "LOADING")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Text("\(viewModel.dashboardData?.security_status.security_score ?? 0)")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(viewModel.securityScoreColor)
            }

            // Progress bar
            ProgressView(value: Double(viewModel.dashboardData?.security_status.security_score ?? 0), total: 100)
                .tint(viewModel.securityScoreColor)

            HStack {
                Label(
                    appState.isArabic ? "مستوى التهديد" : "Threat Level",
                    systemImage: "exclamationmark.triangle"
                )

                Spacer()

                Text((viewModel.dashboardData?.security_status.threat_level ?? "low").uppercased())
                    .fontWeight(.semibold)
                    .foregroundColor(viewModel.threatLevelColor)
            }
            .font(.subheadline)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }

    // MARK: - Alerts Grid
    private var alertsGrid: some View {
        VStack(alignment: .leading) {
            Text(appState.isArabic ? "التنبيهات" : "Alerts")
                .font(.headline)

            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                alertTile(
                    title: appState.isArabic ? "حرج" : "Critical",
                    count: viewModel.dashboardData?.alerts.critical ?? 0,
                    color: .purple
                )

                alertTile(
                    title: appState.isArabic ? "عالي" : "High",
                    count: viewModel.dashboardData?.alerts.high ?? 0,
                    color: .red
                )

                alertTile(
                    title: appState.isArabic ? "متوسط" : "Medium",
                    count: viewModel.dashboardData?.alerts.medium ?? 0,
                    color: .orange
                )

                alertTile(
                    title: appState.isArabic ? "منخفض" : "Low",
                    count: viewModel.dashboardData?.alerts.low ?? 0,
                    color: .green
                )
            }
        }
    }

    private func alertTile(title: String, count: Int, color: Color) -> some View {
        VStack {
            Text("\(count)")
                .font(.title)
                .fontWeight(.bold)
                .foregroundColor(count > 0 ? color : .gray)

            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(8)
    }

    // MARK: - Active Sessions Card
    private var activeSessionsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Label(
                    appState.isArabic ? "الجلسات النشطة" : "Active Sessions",
                    systemImage: "person.2.wave.2"
                )
                .font(.headline)

                Spacer()

                Text("\(viewModel.dashboardData?.active_sessions.total ?? 0)")
                    .font(.title2)
                    .fontWeight(.bold)
            }

            HStack {
                sessionDevice(
                    icon: "iphone",
                    label: appState.isArabic ? "جوال" : "Mobile",
                    count: viewModel.dashboardData?.active_sessions.by_device["mobile"] ?? 0
                )

                Spacer()

                sessionDevice(
                    icon: "desktopcomputer",
                    label: appState.isArabic ? "سطح المكتب" : "Desktop",
                    count: viewModel.dashboardData?.active_sessions.by_device["desktop"] ?? 0
                )

                Spacer()

                sessionDevice(
                    icon: "ipad",
                    label: appState.isArabic ? "تابلت" : "Tablet",
                    count: viewModel.dashboardData?.active_sessions.by_device["tablet"] ?? 0
                )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }

    private func sessionDevice(icon: String, label: String, count: Int) -> some View {
        VStack {
            Image(systemName: icon)
                .font(.title2)
            Text("\(count)")
                .font(.headline)
            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }

    // MARK: - Failed Logins Card
    private var failedLoginsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(
                appState.isArabic ? "محاولات تسجيل الدخول الفاشلة" : "Failed Login Attempts",
                systemImage: "xmark.shield"
            )
            .font(.headline)

            HStack {
                VStack {
                    Text("\(viewModel.dashboardData?.failed_logins.last_hour ?? 0)")
                        .font(.title)
                        .foregroundColor(.red)
                    Text(appState.isArabic ? "آخر ساعة" : "Last Hour")
                        .font(.caption)
                }

                Spacer()

                VStack {
                    Text("\(viewModel.dashboardData?.failed_logins.last_24h ?? 0)")
                        .font(.title)
                        .foregroundColor(.orange)
                    Text(appState.isArabic ? "آخر 24 ساعة" : "Last 24h")
                        .font(.caption)
                }

                Spacer()

                VStack {
                    Text("\(viewModel.dashboardData?.failed_logins.blocked_ips.count ?? 0)")
                        .font(.title)
                        .foregroundColor(.purple)
                    Text(appState.isArabic ? "عناوين محظورة" : "Blocked IPs")
                        .font(.caption)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }

    // MARK: - Pending Approvals Card
    private var pendingApprovalsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Label(
                    appState.isArabic ? "الموافقات المعلقة" : "Pending Approvals",
                    systemImage: "clock.badge.checkmark"
                )
                .font(.headline)

                Spacer()

                Text("\(viewModel.approvalStats?.pending ?? 0)")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.blue)
            }

            if let stats = viewModel.approvalStats {
                HStack {
                    Text(appState.isArabic ? "تمت الموافقة اليوم: \(stats.approved_today)" : "Approved Today: \(stats.approved_today)")
                    Spacer()
                    Text(appState.isArabic ? "مرفوض: \(stats.denied_today)" : "Denied: \(stats.denied_today)")
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }

    // MARK: - Recent Events Card
    private var recentEventsCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(
                appState.isArabic ? "الأحداث الأخيرة" : "Recent Events",
                systemImage: "list.bullet.rectangle"
            )
            .font(.headline)

            if viewModel.dashboardData?.recent_events.isEmpty == true {
                Text(appState.isArabic ? "لا توجد أحداث" : "No recent events")
                    .foregroundColor(.secondary)
                    .padding()
            } else {
                ForEach(0..<min(3, viewModel.dashboardData?.recent_events.count ?? 0), id: \.self) { index in
                    if let event = viewModel.dashboardData?.recent_events[index] {
                        HStack {
                            Circle()
                                .fill(eventColor(event))
                                .frame(width: 8, height: 8)

                            Text(event["type"]?.value as? String ?? "Unknown")
                                .font(.subheadline)

                            Spacer()

                            Text(event["severity"]?.value as? String ?? "")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        .padding(.vertical, 4)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }

    private func eventColor(_ event: [String: AnyCodable]) -> Color {
        let severity = event["severity"]?.value as? String ?? "low"
        switch severity {
        case "critical": return .purple
        case "high": return .red
        case "medium": return .orange
        default: return .green
        }
    }
}

#Preview {
    NavigationStack {
        DashboardView()
            .environmentObject(AppState())
    }
}
