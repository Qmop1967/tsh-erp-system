import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:provider/provider.dart';
import '../../services/gps/gps_tracking_service.dart';
import '../../models/gps/gps_location.dart';
import '../../providers/auth_provider.dart';

/// Real-time GPS tracking page with Google Maps
/// Critical for fraud prevention in $35K USD weekly money tracking
class GPSTrackingPage extends StatefulWidget {
  const GPSTrackingPage({Key? key}) : super(key: key);

  @override
  State<GPSTrackingPage> createState() => _GPSTrackingPageState();
}

class _GPSTrackingPageState extends State<GPSTrackingPage> {
  GoogleMapController? _mapController;
  final GPSTrackingService _gpsService = GPSTrackingService();
  Position? _currentPosition;
  DailyTrackingSummary? _todaysSummary;
  bool _isLoading = true;
  Set<Marker> _markers = {};
  Set<Polyline> _polylines = {};

  @override
  void initState() {
    super.initState();
    _initializeTracking();
  }

  Future<void> _initializeTracking() async {
    setState(() => _isLoading = true);

    await _gpsService.initialize();

    // Get current position
    _currentPosition = await _gpsService.getCurrentPosition();

    // Load today's summary
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final userId = authProvider.user?.id ?? 1; // TODO: Get from auth

    _todaysSummary = await _gpsService.getTodaysSummary(userId);

    // Build markers and polylines
    if (_todaysSummary != null) {
      _buildMapElements(_todaysSummary!);
    }

    setState(() => _isLoading = false);
  }

  void _buildMapElements(DailyTrackingSummary summary) {
    final markers = <Marker>{};
    final List<LatLng> routePoints = [];

    // Add markers for each location
    for (int i = 0; i < summary.locations.length; i++) {
      final location = summary.locations[i];
      routePoints.add(LatLng(location.latitude, location.longitude));

      BitmapDescriptor icon = BitmapDescriptor.defaultMarker;
      String title = 'موقع $i';

      if (location.visitType == 'start_day') {
        icon = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen);
        title = 'بداية اليوم';
      } else if (location.visitType == 'end_day') {
        icon = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed);
        title = 'نهاية اليوم';
      } else if (location.visitType == 'customer_visit') {
        icon = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue);
        title = 'زيارة عميل';
      }

      markers.add(
        Marker(
          markerId: MarkerId('location_$i'),
          position: LatLng(location.latitude, location.longitude),
          icon: icon,
          infoWindow: InfoWindow(
            title: title,
            snippet: location.address ?? '',
          ),
        ),
      );
    }

    // Add current position marker
    if (_currentPosition != null) {
      markers.add(
        Marker(
          markerId: const MarkerId('current'),
          position: LatLng(
            _currentPosition!.latitude,
            _currentPosition!.longitude,
          ),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure),
          infoWindow: const InfoWindow(
            title: 'موقعك الحالي',
          ),
        ),
      );
    }

    // Create polyline for route
    final polylines = <Polyline>{};
    if (routePoints.isNotEmpty) {
      polylines.add(
        Polyline(
          polylineId: const PolylineId('route'),
          points: routePoints,
          color: Colors.blue,
          width: 3,
          geodesic: true,
        ),
      );
    }

    setState(() {
      _markers = markers;
      _polylines = polylines;
    });
  }

  Future<void> _toggleTracking() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final userId = authProvider.user?.id ?? 1;

    if (_gpsService.isTracking) {
      await _gpsService.stopTracking(userId);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم إيقاف التتبع')),
      );
    } else {
      final success = await _gpsService.startTracking(userId);
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم بدء التتبع')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('فشل بدء التتبع. يرجى التحقق من أذونات الموقع'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }

    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تتبع GPS'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: Icon(_gpsService.isTracking ? Icons.pause : Icons.play_arrow),
            onPressed: _toggleTracking,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _initializeTracking,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Statistics Card
                _buildStatisticsCard(),

                // Map
                Expanded(
                  child: _currentPosition == null
                      ? const Center(child: Text('لا يمكن الحصول على الموقع'))
                      : GoogleMap(
                          initialCameraPosition: CameraPosition(
                            target: LatLng(
                              _currentPosition!.latitude,
                              _currentPosition!.longitude,
                            ),
                            zoom: 14,
                          ),
                          markers: _markers,
                          polylines: _polylines,
                          myLocationEnabled: true,
                          myLocationButtonEnabled: true,
                          onMapCreated: (controller) {
                            _mapController = controller;
                          },
                        ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _toggleTracking,
        icon: Icon(_gpsService.isTracking ? Icons.stop : Icons.location_on),
        label: Text(_gpsService.isTracking ? 'إيقاف التتبع' : 'بدء التتبع'),
        backgroundColor: _gpsService.isTracking ? Colors.red : Colors.green,
      ),
    );
  }

  Widget _buildStatisticsCard() {
    if (_todaysSummary == null) {
      return Container(
        padding: const EdgeInsets.all(16),
        color: Colors.blue.shade50,
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.info_outline, color: Colors.blue),
            SizedBox(width: 8),
            Text('لا توجد بيانات تتبع لهذا اليوم'),
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade400, Colors.blue.shade600],
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem(
                icon: Icons.route,
                label: 'المسافة',
                value: '${_todaysSummary!.totalDistanceKm.toStringAsFixed(1)} كم',
              ),
              _buildStatItem(
                icon: Icons.people,
                label: 'الزيارات',
                value: '${_todaysSummary!.customerVisits}',
              ),
              _buildStatItem(
                icon: Icons.access_time,
                label: 'المدة',
                value: _todaysSummary!.totalDuration,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                _gpsService.isTracking ? Icons.circle : Icons.circle_outlined,
                color: _gpsService.isTracking ? Colors.green : Colors.white,
                size: 12,
              ),
              const SizedBox(width: 8),
              Text(
                _gpsService.isTracking ? 'التتبع نشط' : 'التتبع متوقف',
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, color: Colors.white, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
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

  @override
  void dispose() {
    _mapController?.dispose();
    super.dispose();
  }
}
