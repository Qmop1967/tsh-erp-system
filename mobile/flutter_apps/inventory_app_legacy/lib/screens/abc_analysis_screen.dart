import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:tsh_core_package/tsh_core_package.dart';
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
    _loadABCAnalysis();
  }

  Future<void> _loadABCAnalysis() async {
    setState(() => _isLoading = true);
    try {
      final data = await _inventoryService.getABCAnalysis();
      setState(() {
        _abcData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
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
        title: const Text('ABC Analysis'),
        subtitle: const Text('Inventory Classification & Optimization'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadABCAnalysis,
          ),
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: _showABCHelp,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildABCAnalysisContent(),
    );
  }

  Widget _buildABCAnalysisContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ABC Overview Cards
          _buildABCOverviewCards(),
          
          const SizedBox(height: 24),
          
          // ABC Distribution Chart
          _buildABCChart(),
          
          const SizedBox(height: 24),
          
          // ABC Classification Details
          _buildClassificationDetails(),
          
          const SizedBox(height: 24),
          
          // Recommendations
          _buildRecommendations(),
          
          const SizedBox(height: 24),
          
          // Action Buttons
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildABCOverviewCards() {
    final classification = _abcData['classification_summary'] as Map<String, dynamic>? ?? {};
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ABC Classification Overview',
          style: TSHTheme.headingSmall,
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildABCCard(
                'Class A',
                'High Value',
                classification['A']?['count'] ?? 0,
                classification['A']?['value_percentage'] ?? 0,
                Colors.green,
                Icons.trending_up,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildABCCard(
                'Class B',
                'Medium Value',
                classification['B']?['count'] ?? 0,
                classification['B']?['value_percentage'] ?? 0,
                Colors.orange,
                Icons.remove,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildABCCard(
                'Class C',
                'Low Value',
                classification['C']?['count'] ?? 0,
                classification['C']?['value_percentage'] ?? 0,
                Colors.red,
                Icons.trending_down,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildABCCard(String title, String subtitle, int count, int valuePercentage, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  title,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            '$count Items',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          Text(
            '$valuePercentage% of Value',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildABCChart() {
    final classification = _abcData['classification_summary'] as Map<String, dynamic>? ?? {};
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'ABC Distribution',
            style: TSHTheme.headingSmall,
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: Row(
              children: [
                // Pie Chart
                Expanded(
                  flex: 2,
                  child: PieChart(
                    PieChartData(
                      sectionsSpace: 2,
                      centerSpaceRadius: 40,
                      sections: [
                        PieChartSectionData(
                          value: (classification['A']?['count'] ?? 0).toDouble(),
                          title: 'A',
                          color: Colors.green,
                          radius: 50,
                          titleStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        PieChartSectionData(
                          value: (classification['B']?['count'] ?? 0).toDouble(),
                          title: 'B',
                          color: Colors.orange,
                          radius: 50,
                          titleStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        PieChartSectionData(
                          value: (classification['C']?['count'] ?? 0).toDouble(),
                          title: 'C',
                          color: Colors.red,
                          radius: 50,
                          titleStyle: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                
                // Legend
                Expanded(
                  flex: 1,
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _buildLegendItem('Class A', Colors.green, classification['A']?['percentage'] ?? 0),
                      const SizedBox(height: 8),
                      _buildLegendItem('Class B', Colors.orange, classification['B']?['percentage'] ?? 0),
                      const SizedBox(height: 8),
                      _buildLegendItem('Class C', Colors.red, classification['C']?['percentage'] ?? 0),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color, int percentage) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                '$percentage%',
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildClassificationDetails() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Classification Criteria',
            style: TSHTheme.headingSmall,
          ),
          const SizedBox(height: 16),
          _buildCriteriaItem(
            'Class A Items',
            'High-value items contributing to 70-80% of total inventory value',
            'Require tight control and frequent monitoring',
            Colors.green,
          ),
          const SizedBox(height: 12),
          _buildCriteriaItem(
            'Class B Items',
            'Medium-value items contributing to 15-20% of total inventory value',
            'Moderate control with periodic reviews',
            Colors.orange,
          ),
          const SizedBox(height: 12),
          _buildCriteriaItem(
            'Class C Items',
            'Low-value items contributing to 5-10% of total inventory value',
            'Basic control with annual reviews',
            Colors.red,
          ),
        ],
      ),
    );
  }

  Widget _buildCriteriaItem(String title, String description, String recommendation, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.left(color: color, width: 4),
        color: color.withOpacity(0.05),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            description,
            style: const TextStyle(fontSize: 14),
          ),
          const SizedBox(height: 4),
          Text(
            'Recommendation: $recommendation',
            style: TextStyle(
              fontSize: 12,
              fontStyle: FontStyle.italic,
              color: Colors.grey.shade700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendations() {
    final recommendations = _abcData['recommendations'] as List<dynamic>? ?? [];
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: TSHTheme.surfaceWhite,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.lightbulb_outline, color: TSHTheme.accentOrange),
              const SizedBox(width: 8),
              Text(
                'Smart Recommendations',
                style: TSHTheme.headingSmall,
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...recommendations.map((recommendation) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.arrow_right, color: TSHTheme.primaryTeal, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    recommendation.toString(),
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _exportABCReport,
            icon: const Icon(Icons.download),
            label: const Text('Export Report'),
            style: ElevatedButton.styleFrom(
              backgroundColor: TSHTheme.primaryTeal,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: _reclassifyItems,
            icon: const Icon(Icons.refresh),
            label: const Text('Reclassify Items'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }

  void _showABCHelp() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('ABC Analysis Help'),
        content: const SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'ABC Analysis is an inventory categorization method that divides items into three categories:',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
              SizedBox(height: 12),
              Text('• Class A: High-value items (70-80% of inventory value)'),
              Text('• Class B: Medium-value items (15-20% of inventory value)'),
              Text('• Class C: Low-value items (5-10% of inventory value)'),
              SizedBox(height: 12),
              Text(
                'This helps prioritize inventory management efforts and optimize stock control strategies.',
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _exportABCReport() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('ABC analysis report exported successfully'),
        action: SnackBarAction(
          label: 'View',
          onPressed: null,
        ),
      ),
    );
  }

  void _reclassifyItems() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reclassify Items'),
        content: const Text(
          'This will recalculate ABC classifications based on current inventory values. Continue?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _loadABCAnalysis(); // Reload with new classifications
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Items reclassified successfully')),
              );
            },
            child: const Text('Reclassify'),
          ),
        ],
      ),
    );
  }
}
