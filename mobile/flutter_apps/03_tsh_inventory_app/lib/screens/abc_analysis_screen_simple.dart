import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/inventory_service.dart';

class ABCAnalysisScreen extends StatefulWidget {
  const ABCAnalysisScreen({super.key});

  @override
  State<ABCAnalysisScreen> createState() => _ABCAnalysisScreenState();
}

class _ABCAnalysisScreenState extends State<ABCAnalysisScreen> {
  final InventoryService _inventoryService = InventoryService();
  Map<String, dynamic> _abcData = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadABCData();
  }

  Future<void> _loadABCData() async {
    setState(() => _isLoading = true);
    try {
      final data = await _inventoryService.getABCAnalysis();
      if (mounted) {
        setState(() {
          _abcData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading ABC analysis: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('ABC Analysis'),
            Text(
              'Inventory Classification & Insights',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadABCData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _abcData.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.analytics, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'No ABC Analysis Data',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      SizedBox(height: 8),
                      Text(
                        'Generate analysis from inventory data',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _buildSummaryCards(),
                      const SizedBox(height: 20),
                      _buildChart(),
                      const SizedBox(height: 20),
                      _buildRecommendations(),
                    ],
                  ),
                ),
    );
  }

  Widget _buildSummaryCards() {
    return Row(
      children: [
        Expanded(child: _buildClassCard('A', Colors.red, _abcData['classA'] ?? {})),
        const SizedBox(width: 12),
        Expanded(child: _buildClassCard('B', Colors.orange, _abcData['classB'] ?? {})),
        const SizedBox(width: 12),
        Expanded(child: _buildClassCard('C', Colors.green, _abcData['classC'] ?? {})),
      ],
    );
  }

  Widget _buildClassCard(String className, Color color, Map<String, dynamic> data) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              'Class $className',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${data['count'] ?? 0} Items',
              style: const TextStyle(fontSize: 16),
            ),
            Text(
              '${data['valuePercentage'] ?? 0}% Value',
              style: const TextStyle(fontSize: 14, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChart() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Value Distribution',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: PieChart(
                PieChartData(
                  sections: [
                    PieChartSectionData(
                      value: (_abcData['classA']?['valuePercentage'] ?? 0).toDouble(),
                      title: 'A',
                      color: Colors.red,
                      radius: 60,
                    ),
                    PieChartSectionData(
                      value: (_abcData['classB']?['valuePercentage'] ?? 0).toDouble(),
                      title: 'B',
                      color: Colors.orange,
                      radius: 60,
                    ),
                    PieChartSectionData(
                      value: (_abcData['classC']?['valuePercentage'] ?? 0).toDouble(),
                      title: 'C',
                      color: Colors.green,
                      radius: 60,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendations() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.lightbulb_outline, color: Colors.orange),
                SizedBox(width: 8),
                Text(
                  'Recommendations',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text('• Class A: Focus on tight inventory control and frequent monitoring'),
            const SizedBox(height: 8),
            const Text('• Class B: Maintain balanced stock levels with periodic reviews'),
            const SizedBox(height: 8),
            const Text('• Class C: Use simple controls and bulk purchasing strategies'),
          ],
        ),
      ),
    );
  }
}
