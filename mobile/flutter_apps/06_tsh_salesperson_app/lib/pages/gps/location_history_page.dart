import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/gps/gps_tracking_service.dart';
import '../../models/gps/gps_location.dart';

/// Location History Page - View historical GPS tracking data
class LocationHistoryPage extends StatefulWidget {
  final int salespersonId;

  const LocationHistoryPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<LocationHistoryPage> createState() => _LocationHistoryPageState();
}

class _LocationHistoryPageState extends State<LocationHistoryPage> {
  final GPSTrackingService _gpsService = GPSTrackingService();
  List<GPSLocation> _locations = [];
  bool _isLoading = true;
  DateTime _selectedDate = DateTime.now();

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);

    await _gpsService.initialize();

    final dateStr =
        '${_selectedDate.year}-${_selectedDate.month.toString().padLeft(2, '0')}-${_selectedDate.day.toString().padLeft(2, '0')}';

    _locations = await _gpsService.getLocationsByDate(
      widget.salespersonId,
      dateStr,
    );

    setState(() => _isLoading = false);
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now().subtract(const Duration(days: 90)),
      lastDate: DateTime.now(),
      locale: const Locale('ar'),
    );

    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
      });
      _loadHistory();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('سجل المواقع'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today),
            onPressed: _selectDate,
          ),
        ],
      ),
      body: Column(
        children: [
          // Date Selector
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.blue.shade50,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  DateFormat('EEEE، d MMMM yyyy', 'ar').format(_selectedDate),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _selectDate,
                  icon: const Icon(Icons.calendar_today, size: 16),
                  label: const Text('اختر تاريخ'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ),
          ),

          // Locations List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _locations.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.location_off,
                              size: 64,
                              color: Colors.grey.shade400,
                            ),
                            const SizedBox(height: 16),
                            const Text(
                              'لا توجد سجلات لهذا اليوم',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey,
                              ),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        itemCount: _locations.length,
                        padding: const EdgeInsets.all(16),
                        itemBuilder: (context, index) {
                          final location = _locations[index];
                          final time =
                              DateTime.parse(location.timestamp).toLocal();

                          return _buildLocationCard(location, time, index);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildLocationCard(GPSLocation location, DateTime time, int index) {
    IconData icon;
    Color iconColor;
    String typeLabel;

    switch (location.visitType) {
      case 'start_day':
        icon = Icons.play_circle;
        iconColor = Colors.green;
        typeLabel = 'بداية اليوم';
        break;
      case 'end_day':
        icon = Icons.stop_circle;
        iconColor = Colors.red;
        typeLabel = 'نهاية اليوم';
        break;
      case 'customer_visit':
        icon = Icons.person_pin_circle;
        iconColor = Colors.blue;
        typeLabel = 'زيارة عميل';
        break;
      default:
        icon = Icons.location_on;
        iconColor = Colors.grey;
        typeLabel = 'في الطريق';
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: iconColor.withOpacity(0.2),
          child: Icon(icon, color: iconColor),
        ),
        title: Text(
          typeLabel,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.access_time, size: 14, color: Colors.grey),
                const SizedBox(width: 4),
                Text(DateFormat('h:mm a', 'ar').format(time)),
              ],
            ),
            if (location.address != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.place, size: 14, color: Colors.grey),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      location.address!,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ],
            if (location.accuracy != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.gps_fixed, size: 14, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    'دقة: ${location.accuracy!.toStringAsFixed(0)}م',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ],
            if (location.notes != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.note, size: 14, color: Colors.grey),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      location.notes!,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              location.isSynced ? Icons.cloud_done : Icons.cloud_upload,
              color: location.isSynced ? Colors.green : Colors.orange,
              size: 20,
            ),
            const SizedBox(height: 4),
            Text(
              location.isSynced ? 'مزامن' : 'قيد المزامنة',
              style: TextStyle(
                fontSize: 10,
                color: location.isSynced ? Colors.green : Colors.orange,
              ),
            ),
          ],
        ),
        onTap: () {
          _showLocationDetails(location);
        },
      ),
    );
  }

  void _showLocationDetails(GPSLocation location) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تفاصيل الموقع'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('الوقت', DateFormat('h:mm:ss a', 'ar').format(
                DateTime.parse(location.timestamp).toLocal(),
              )),
              _buildDetailRow(
                'الإحداثيات',
                '${location.latitude.toStringAsFixed(6)}, ${location.longitude.toStringAsFixed(6)}',
              ),
              if (location.address != null)
                _buildDetailRow('العنوان', location.address!),
              if (location.accuracy != null)
                _buildDetailRow('الدقة', '${location.accuracy!.toStringAsFixed(1)} متر'),
              if (location.altitude != null)
                _buildDetailRow('الارتفاع', '${location.altitude!.toStringAsFixed(1)} متر'),
              if (location.speed != null)
                _buildDetailRow('السرعة', '${(location.speed! * 3.6).toStringAsFixed(1)} كم/س'),
              if (location.visitType != null)
                _buildDetailRow('النوع', location.visitType!),
              if (location.customerId != null)
                _buildDetailRow('معرف العميل', location.customerId.toString()),
              if (location.notes != null)
                _buildDetailRow('ملاحظات', location.notes!),
              _buildDetailRow('حالة المزامنة', location.isSynced ? 'مزامن' : 'قيد المزامنة'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إغلاق'),
          ),
          ElevatedButton.icon(
            onPressed: () {
              // TODO: Open in maps app
              Navigator.pop(context);
            },
            icon: const Icon(Icons.map),
            label: const Text('عرض في الخرائط'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }
}
