/// Dashboard Metrics Model
class DashboardMetrics {
  final int totalUsers;
  final int activeUsers;
  final int onlineUsers;
  final int totalDevices;
  final int failedLogins;
  final int securityAlerts;
  final int activeSessions;
  final int pendingApprovals;

  DashboardMetrics({
    required this.totalUsers,
    required this.activeUsers,
    required this.onlineUsers,
    required this.totalDevices,
    required this.failedLogins,
    required this.securityAlerts,
    required this.activeSessions,
    required this.pendingApprovals,
  });

  factory DashboardMetrics.fromJson(Map<String, dynamic> json) {
    return DashboardMetrics(
      totalUsers: json['total_users'] as int? ?? 0,
      activeUsers: json['active_users'] as int? ?? 0,
      onlineUsers: json['online_users'] as int? ?? 0,
      totalDevices: json['total_devices'] as int? ?? 0,
      failedLogins: json['failed_logins'] as int? ?? 0,
      securityAlerts: json['security_alerts'] as int? ?? 0,
      activeSessions: json['active_sessions'] as int? ?? 0,
      pendingApprovals: json['pending_approvals'] as int? ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_users': totalUsers,
      'active_users': activeUsers,
      'online_users': onlineUsers,
      'total_devices': totalDevices,
      'failed_logins': failedLogins,
      'security_alerts': securityAlerts,
      'active_sessions': activeSessions,
      'pending_approvals': pendingApprovals,
    };
  }
}
