import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../services/gps/gps_tracking_service.dart';
import '../../models/gps/gps_location.dart';
import 'gps_tracking_page.dart';
import 'location_history_page.dart';

/// Tracking Dashboard - Daily route overview
/// Shows analytics and summary of GPS tracking
class TrackingDashboardPage extends StatefulWidget {
  final int salespersonId;

  const TrackingDashboardPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<TrackingDashboardPage> createState() => _TrackingDashboardPageState();
}

class _TrackingDashboardPageState extends State<TrackingDashboardPage> {
  final GPSTrackingService _gpsService = GPSTrackingService();
  DailyTrackingSummary? _todaysSummary;
  bool _isLoading = true;
  List<DailyTrackingSummary> _weekSummaries = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    await _gpsService.initialize();

    // Load today's summary
    _todaysSummary = await _gpsService.getTodaysSummary(widget.salespersonId);

    // Load week's data
    await _loadWeekData();

    setState(() => _isLoading = false);
  }

  Future<void> _loadWeekData() async {
    final summaries = <DailyTrackingSummary>[];
    final today = DateTime.now();

    for (int i = 0; i < 7; i++) {
      final date = today.subtract(Duration(days: i));
      final dateStr =
          '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';

      final locations =
          await _gpsService.getLocationsByDate(widget.salespersonId, dateStr);

      if (locations.isNotEmpty) {
        // Calculate summary
        double totalDistance = 0.0;
        for (int j = 1; j < locations.length; j++) {
          totalDistance += _gpsService.calculateDistance(
            locations[j - 1].latitude,
            locations[j - 1].longitude,
            locations[j].latitude,
            locations[j].longitude,
          );
        }

        summaries.add(
          DailyTrackingSummary(
            date: dateStr,
            totalLocations: locations.length,
            totalDistanceKm: totalDistance / 1000,
            startTime: locations.first.timestamp,
            endTime: locations.last.timestamp,
            customerVisits:
                locations.where((l) => l.visitType == 'customer_visit').length,
            totalDuration: _formatDuration(
              DateTime.parse(locations.last.timestamp)
                  .difference(DateTime.parse(locations.first.timestamp)),
            ),
            locations: locations,
          ),
        );
      }
    }

    setState(() {
      _weekSummaries = summaries;
    });
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    return '$hours:${minutes.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('لوحة تحكم التتبع'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      LocationHistoryPage(salespersonId: widget.salespersonId),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Today's Summary Card
                    _buildTodayCard(),
                    const SizedBox(height: 16),

                    // Quick Actions
                    _buildQuickActions(),
                    const SizedBox(height: 16),

                    // Week Chart
                    if (_weekSummaries.isNotEmpty) ...[
                      const Text(
                        'إحصائيات الأسبوع',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildWeekChart(),
                      const SizedBox(height: 16),
                    ],

                    // Week Details
                    if (_weekSummaries.isNotEmpty) ...[
                      const Text(
                        'ملخص الأيام السابقة',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _buildWeekList(),
                    ],
                  ],
                ),
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const GPSTrackingPage(),
            ),
          );
        },
        icon: const Icon(Icons.map),
        label: const Text('عرض الخريطة'),
        backgroundColor: Colors.blue,
      ),
    );
  }

  Widget _buildTodayCard() {
    if (_todaysSummary == null) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(Icons.location_off, size: 48, color: Colors.grey.shade400),
              const SizedBox(height: 8),
              const Text(
                'لا توجد بيانات تتبع لهذا اليوم',
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () async {
                  final success =
                      await _gpsService.startTracking(widget.salespersonId);
                  if (success) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('تم بدء التتبع')),
                    );
                    _loadData();
                  }
                },
                icon: const Icon(Icons.play_arrow),
                label: const Text('بدء التتبع'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      );
    }

    final summary = _todaysSummary!;
    final isActive = summary.endTime == null;

    return Card(
      elevation: 4,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          gradient: LinearGradient(
            colors: isActive
                ? [Colors.green.shade400, Colors.green.shade600]
                : [Colors.blue.shade400, Colors.blue.shade600],
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'اليوم',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        isActive ? Icons.circle : Icons.check_circle,
                        color: Colors.white,
                        size: 16,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        isActive ? 'نشط' : 'مكتمل',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStat(
                  icon: Icons.route,
                  label: 'المسافة',
                  value: '${summary.totalDistanceKm.toStringAsFixed(1)} كم',
                ),
                _buildStat(
                  icon: Icons.people,
                  label: 'الزيارات',
                  value: '${summary.customerVisits}',
                ),
                _buildStat(
                  icon: Icons.access_time,
                  label: 'المدة',
                  value: summary.totalDuration,
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const Icon(Icons.location_on, color: Colors.white70, size: 16),
                const SizedBox(width: 8),
                Text(
                  'نقاط التتبع: ${summary.totalLocations}',
                  style: const TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStat({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, color: Colors.white, size: 32),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const GPSTrackingPage(),
                ),
              );
            },
            icon: const Icon(Icons.map),
            label: const Text('عرض الخريطة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.all(16),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      LocationHistoryPage(salespersonId: widget.salespersonId),
                ),
              );
            },
            icon: const Icon(Icons.history),
            label: const Text('السجل'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey.shade700,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.all(16),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWeekChart() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'المسافة اليومية (كم)',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: _weekSummaries.isEmpty
                      ? 10
                      : _weekSummaries
                              .map((s) => s.totalDistanceKm)
                              .reduce((a, b) => a > b ? a : b) *
                          1.2,
                  barTouchData: BarTouchData(enabled: true),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          if (value.toInt() >= _weekSummaries.length) {
                            return const Text('');
                          }
                          final date =
                              DateTime.parse(_weekSummaries[value.toInt()].date);
                          return Text(
                            DateFormat('EEE', 'ar').format(date),
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: true, reservedSize: 40),
                    ),
                    topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  barGroups: _weekSummaries
                      .asMap()
                      .entries
                      .map(
                        (entry) => BarChartGroupData(
                          x: entry.key,
                          barRods: [
                            BarChartRodData(
                              toY: entry.value.totalDistanceKm,
                              color: Colors.blue,
                              width: 20,
                              borderRadius: const BorderRadius.vertical(
                                top: Radius.circular(6),
                              ),
                            ),
                          ],
                        ),
                      )
                      .toList(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeekList() {
    return Column(
      children: _weekSummaries.map((summary) {
        final date = DateTime.parse(summary.date);
        final isToday = summary.date == DateFormat('yyyy-MM-dd').format(DateTime.now());

        return Card(
          color: isToday ? Colors.blue.shade50 : null,
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: Colors.blue,
              child: Text(
                date.day.toString(),
                style: const TextStyle(color: Colors.white),
              ),
            ),
            title: Text(
              DateFormat('EEEE، d MMMM', 'ar').format(date),
              style: TextStyle(
                fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            subtitle: Text(
              '${summary.totalDistanceKm.toStringAsFixed(1)} كم • ${summary.customerVisits} زيارة • ${summary.totalDuration}',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: Show day details
            },
          ),
        );
      }).toList(),
    );
  }
}
