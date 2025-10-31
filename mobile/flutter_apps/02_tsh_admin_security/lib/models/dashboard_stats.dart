/// Dashboard Statistics Model
class DashboardStats {
  final int totalUsers;
  final int activeSessions;
  final int securityAlerts;
  final int failedLogins;

  DashboardStats({
    required this.totalUsers,
    required this.activeSessions,
    required this.securityAlerts,
    required this.failedLogins,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalUsers: json['total_users'] ?? 0,
      activeSessions: json['active_sessions'] ?? 0,
      securityAlerts: json['security_alerts'] ?? 0,
      failedLogins: json['failed_logins'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'total_users': totalUsers,
      'active_sessions': activeSessions,
      'security_alerts': securityAlerts,
      'failed_logins': failedLogins,
    };
  }

  factory DashboardStats.empty() {
    return DashboardStats(
      totalUsers: 0,
      activeSessions: 0,
      securityAlerts: 0,
      failedLogins: 0,
    );
  }
}
