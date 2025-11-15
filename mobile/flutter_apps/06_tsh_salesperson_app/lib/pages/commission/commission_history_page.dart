import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/commission/commission_service.dart';
import '../../models/commission/commission.dart';

/// Commission History Page
/// View all past commission records
class CommissionHistoryPage extends StatefulWidget {
  final int salespersonId;

  const CommissionHistoryPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<CommissionHistoryPage> createState() => _CommissionHistoryPageState();
}

class _CommissionHistoryPageState extends State<CommissionHistoryPage> {
  final CommissionService _commissionService = CommissionService();
  List<Commission> _commissions = [];
  List<Commission> _filteredCommissions = [];
  bool _isLoading = true;
  String? _filterStatus;

  @override
  void initState() {
    super.initState();
    _loadCommissions();
  }

  Future<void> _loadCommissions() async {
    setState(() => _isLoading = true);

    await _commissionService.initialize();
    _commissions = await _commissionService.getCommissions(widget.salespersonId);
    _applyFilters();

    setState(() => _isLoading = false);
  }

  void _applyFilters() {
    _filteredCommissions = _commissions.where((commission) {
      if (_filterStatus != null && commission.status != _filterStatus) {
        return false;
      }
      return true;
    }).toList();

    setState(() {});
  }

  void _showFilters() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Container(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'تصفية العمولات',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String?>(
                    value: _filterStatus,
                    decoration: const InputDecoration(
                      labelText: 'الحالة',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('الكل')),
                      DropdownMenuItem(value: 'pending', child: Text('قيد الانتظار')),
                      DropdownMenuItem(value: 'approved', child: Text('معتمد')),
                      DropdownMenuItem(value: 'paid', child: Text('مدفوع')),
                      DropdownMenuItem(value: 'disputed', child: Text('متنازع عليه')),
                    ],
                    onChanged: (value) {
                      setModalState(() {
                        _filterStatus = value;
                      });
                    },
                  ),
                  const SizedBox(height: 24),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            setModalState(() {
                              _filterStatus = null;
                            });
                            setState(() {
                              _filterStatus = null;
                            });
                            _applyFilters();
                            Navigator.pop(context);
                          },
                          child: const Text('إعادة تعيين'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            setState(() {
                              _filterStatus = _filterStatus;
                            });
                            _applyFilters();
                            Navigator.pop(context);
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.green,
                            foregroundColor: Colors.white,
                          ),
                          child: const Text('تطبيق'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('سجل العمولات'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilters,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadCommissions,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _filteredCommissions.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.receipt_long,
                        size: 64,
                        color: Colors.grey.shade400,
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'لا توجد عمولات',
                        style: TextStyle(fontSize: 16),
                      ),
                      if (_filterStatus != null)
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _filterStatus = null;
                            });
                            _applyFilters();
                          },
                          child: const Text('إزالة التصفية'),
                        ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadCommissions,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _filteredCommissions.length,
                    itemBuilder: (context, index) {
                      final commission = _filteredCommissions[index];
                      return _buildCommissionCard(commission);
                    },
                  ),
                ),
    );
  }

  Widget _buildCommissionCard(Commission commission) {
    Color statusColor;
    switch (commission.status) {
      case 'pending':
        statusColor = Colors.orange;
        break;
      case 'approved':
        statusColor = Colors.blue;
        break;
      case 'paid':
        statusColor = Colors.green;
        break;
      case 'disputed':
        statusColor = Colors.red;
        break;
      default:
        statusColor = Colors.grey;
    }

    final date = DateTime.parse(commission.createdAt);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showCommissionDetails(commission),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          commission.periodName,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          DateFormat('EEEE، d MMMM yyyy', 'ar').format(date),
                          style: TextStyle(
                            color: Colors.grey.shade600,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        commission.formattedCommissionAmount,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                          color: Colors.green,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: statusColor.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          commission.statusName,
                          style: TextStyle(
                            color: statusColor,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(Icons.shopping_cart, size: 14, color: Colors.grey.shade600),
                      const SizedBox(width: 4),
                      Text(
                        'المبيعات: ${commission.formattedSalesAmount}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      Icon(Icons.percent, size: 14, color: Colors.grey.shade600),
                      const SizedBox(width: 4),
                      Text(
                        '${commission.commissionRate}%',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showCommissionDetails(Commission commission) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تفاصيل العمولة'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildDetailRow('المبلغ', commission.formattedCommissionAmount),
              _buildDetailRow('نسبة العمولة', '${commission.commissionRate}%'),
              _buildDetailRow('المبيعات', commission.formattedSalesAmount),
              _buildDetailRow('الحالة', commission.statusName),
              _buildDetailRow('الفترة', commission.periodName),
              if (commission.ordersCount != null)
                _buildDetailRow('عدد الطلبات', '${commission.ordersCount}'),
              if (commission.notes != null)
                _buildDetailRow('ملاحظات', commission.notes!),
              _buildDetailRow(
                'التاريخ',
                DateFormat('yyyy-MM-dd h:mm a', 'ar')
                    .format(DateTime.parse(commission.createdAt)),
              ),
              if (commission.paidAt != null)
                _buildDetailRow(
                  'تاريخ الدفع',
                  DateFormat('yyyy-MM-dd h:mm a', 'ar')
                      .format(DateTime.parse(commission.paidAt!)),
                ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إغلاق'),
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
