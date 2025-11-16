import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../services/commission/commission_service.dart';
import '../../models/commission/commission.dart';

/// Sales Target Page
/// Set and track monthly/weekly sales goals
class SalesTargetPage extends StatefulWidget {
  final int salespersonId;

  const SalesTargetPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<SalesTargetPage> createState() => _SalesTargetPageState();
}

class _SalesTargetPageState extends State<SalesTargetPage> {
  final CommissionService _commissionService = CommissionService();
  final TextEditingController _targetController = TextEditingController();
  SalesTarget? _currentTarget;
  bool _isLoading = true;
  String _selectedPeriod = 'monthly';

  @override
  void initState() {
    super.initState();
    _loadCurrentTarget();
  }

  @override
  void dispose() {
    _targetController.dispose();
    super.dispose();
  }

  Future<void> _loadCurrentTarget() async {
    setState(() => _isLoading = true);

    await _commissionService.initialize();
    _currentTarget = await _commissionService.getCurrentTarget(widget.salespersonId);

    setState(() => _isLoading = false);
  }

  Future<void> _setNewTarget() async {
    if (_targetController.text.isEmpty) return;

    final targetAmount = double.tryParse(_targetController.text);
    if (targetAmount == null || targetAmount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('يرجى إدخال مبلغ صحيح')),
      );
      return;
    }

    await _commissionService.setTarget(
      salespersonId: widget.salespersonId,
      targetAmount: targetAmount,
      period: _selectedPeriod,
    );

    _targetController.clear();
    _loadCurrentTarget();

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم تحديد الهدف بنجاح')),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('هدف المبيعات'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showSetTargetDialog(),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (_currentTarget != null) ...[
                    _buildCurrentTargetCard(),
                    const SizedBox(height: 24),
                    _buildProgressDetails(),
                  ] else ...[
                    _buildNoTargetCard(),
                  ],
                ],
              ),
            ),
    );
  }

  Widget _buildCurrentTargetCard() {
    if (_currentTarget == null) return const SizedBox();

    final progress = _currentTarget!.progressPercentage;
    final isAchieved = _currentTarget!.isAchieved;

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isAchieved ? Icons.check_circle : Icons.flag,
                  color: isAchieved ? Colors.green : Colors.blue,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Text(
                  _currentTarget!.periodName,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: LinearProgressIndicator(
                value: progress / 100,
                minHeight: 20,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation<Color>(
                  isAchieved ? Colors.green : Colors.blue,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Center(
              child: Text(
                '${progress.toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: isAchieved ? Colors.green : Colors.blue,
                ),
              ),
            ),
            const SizedBox(height: 24),
            _buildProgressRow('الهدف', _currentTarget!.formattedTargetAmount),
            const SizedBox(height: 12),
            _buildProgressRow('المحقق', _currentTarget!.formattedCurrentAmount),
            const SizedBox(height: 12),
            _buildProgressRow(
              'المتبقي',
              _currentTarget!.formattedRemainingAmount,
              color: isAchieved ? Colors.green : Colors.orange,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressRow(String label, String value, {Color? color}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 16,
            color: Colors.grey,
          ),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildProgressDetails() {
    if (_currentTarget == null) return const SizedBox();

    final isAchieved = _currentTarget!.isAchieved;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'التفاصيل',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                if (isAchieved) ...[
                  const Icon(
                    Icons.celebration,
                    color: Colors.green,
                    size: 48,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'تهانينا! لقد حققت هدفك',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.green,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'تجاوزت الهدف بمبلغ: ${_currentTarget!.formattedRemainingAmount}',
                    style: const TextStyle(color: Colors.grey),
                  ),
                ] else ...[
                  const Icon(
                    Icons.trending_up,
                    color: Colors.blue,
                    size: 48,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'استمر في التقدم!',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'تحتاج إلى: ${_currentTarget!.formattedRemainingAmount}',
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildNoTargetCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            Icon(
              Icons.flag_outlined,
              size: 64,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: 16),
            const Text(
              'لم يتم تحديد هدف',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'حدد هدفاً شهرياً أو أسبوعياً لتتبع تقدمك',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => _showSetTargetDialog(),
              icon: const Icon(Icons.add),
              label: const Text('تحديد هدف جديد'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showSetTargetDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تحديد هدف جديد'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            DropdownButtonFormField<String>(
              value: _selectedPeriod,
              decoration: const InputDecoration(
                labelText: 'الفترة',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(value: 'weekly', child: Text('أسبوعي')),
                DropdownMenuItem(value: 'monthly', child: Text('شهري')),
                DropdownMenuItem(value: 'quarterly', child: Text('ربع سنوي')),
              ],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedPeriod = value;
                  });
                }
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _targetController,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              inputFormatters: [
                FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,2}')),
              ],
              decoration: const InputDecoration(
                labelText: 'المبلغ المستهدف',
                hintText: '0.00',
                suffixText: 'د.ع',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: _setNewTarget,
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
            ),
            child: const Text('تحديد'),
          ),
        ],
      ),
    );
  }
}
