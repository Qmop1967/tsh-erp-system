import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'dart:io';
import '../../services/transfers/transfer_service.dart';
import '../../models/transfers/money_transfer.dart';

/// Transfer History Page
/// Browse and filter past money transfers
class TransferHistoryPage extends StatefulWidget {
  final int salespersonId;

  const TransferHistoryPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<TransferHistoryPage> createState() => _TransferHistoryPageState();
}

class _TransferHistoryPageState extends State<TransferHistoryPage> {
  final TransferService _transferService = TransferService();
  List<MoneyTransfer> _allTransfers = [];
  List<MoneyTransfer> _filteredTransfers = [];
  bool _isLoading = true;

  String? _filterStatus;
  String? _filterMethod;
  DateTime? _startDate;
  DateTime? _endDate;

  @override
  void initState() {
    super.initState();
    _loadTransfers();
  }

  Future<void> _loadTransfers() async {
    setState(() => _isLoading = true);

    await _transferService.initialize();
    _allTransfers = await _transferService.getTransfers(widget.salespersonId);
    _applyFilters();

    setState(() => _isLoading = false);
  }

  void _applyFilters() {
    _filteredTransfers = _allTransfers.where((transfer) {
      // Status filter
      if (_filterStatus != null && transfer.status != _filterStatus) {
        return false;
      }

      // Method filter
      if (_filterMethod != null && transfer.transferMethod != _filterMethod) {
        return false;
      }

      // Date range filter
      if (_startDate != null || _endDate != null) {
        final transferDate = DateTime.parse(transfer.date);

        if (_startDate != null &&
            transferDate.isBefore(_startDate!)) {
          return false;
        }

        if (_endDate != null &&
            transferDate.isAfter(_endDate!)) {
          return false;
        }
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
                    'تصفية التحويلات',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Status filter
                  DropdownButtonFormField<String?>(
                    value: _filterStatus,
                    decoration: const InputDecoration(
                      labelText: 'الحالة',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('الكل')),
                      DropdownMenuItem(value: 'pending', child: Text('قيد الانتظار')),
                      DropdownMenuItem(value: 'verified', child: Text('تم التحقق')),
                      DropdownMenuItem(value: 'completed', child: Text('مكتمل')),
                      DropdownMenuItem(value: 'rejected', child: Text('مرفوض')),
                      DropdownMenuItem(value: 'cancelled', child: Text('ملغى')),
                    ],
                    onChanged: (value) {
                      setModalState(() {
                        _filterStatus = value;
                      });
                    },
                  ),
                  const SizedBox(height: 12),

                  // Method filter
                  DropdownButtonFormField<String?>(
                    value: _filterMethod,
                    decoration: const InputDecoration(
                      labelText: 'طريقة التحويل',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: null, child: Text('الكل')),
                      DropdownMenuItem(value: 'altaif', child: Text('الطيف')),
                      DropdownMenuItem(value: 'zainCash', child: Text('زين كاش')),
                      DropdownMenuItem(value: 'superQi', child: Text('سوبر كيو')),
                      DropdownMenuItem(value: 'cash', child: Text('نقدي')),
                    ],
                    onChanged: (value) {
                      setModalState(() {
                        _filterMethod = value;
                      });
                    },
                  ),
                  const SizedBox(height: 24),

                  // Action buttons
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            setModalState(() {
                              _filterStatus = null;
                              _filterMethod = null;
                              _startDate = null;
                              _endDate = null;
                            });
                            setState(() {
                              _filterStatus = null;
                              _filterMethod = null;
                              _startDate = null;
                              _endDate = null;
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
                              _filterMethod = _filterMethod;
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
        title: const Text('سجل التحويلات'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilters,
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTransfers,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _filteredTransfers.isEmpty
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
                        'لا توجد تحويلات',
                        style: TextStyle(fontSize: 16),
                      ),
                      if (_filterStatus != null || _filterMethod != null)
                        TextButton(
                          onPressed: () {
                            setState(() {
                              _filterStatus = null;
                              _filterMethod = null;
                            });
                            _applyFilters();
                          },
                          child: const Text('إزالة التصفية'),
                        ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadTransfers,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _filteredTransfers.length,
                    itemBuilder: (context, index) {
                      final transfer = _filteredTransfers[index];
                      return _buildTransferCard(transfer);
                    },
                  ),
                ),
    );
  }

  Widget _buildTransferCard(MoneyTransfer transfer) {
    IconData methodIcon;
    Color methodColor;

    switch (transfer.transferMethod) {
      case 'altaif':
        methodIcon = MdiIcons.bankTransfer;
        methodColor = Colors.blue;
        break;
      case 'zainCash':
        methodIcon = MdiIcons.cellphone;
        methodColor = Colors.purple;
        break;
      case 'superQi':
        methodIcon = MdiIcons.qrcode;
        methodColor = Colors.orange;
        break;
      case 'cash':
        methodIcon = MdiIcons.cash;
        methodColor = Colors.green;
        break;
      default:
        methodIcon = MdiIcons.help;
        methodColor = Colors.grey;
    }

    Color statusColor;
    switch (transfer.status) {
      case 'pending':
        statusColor = Colors.orange;
        break;
      case 'verified':
        statusColor = Colors.blue;
        break;
      case 'completed':
        statusColor = Colors.green;
        break;
      case 'rejected':
        statusColor = Colors.red;
        break;
      case 'cancelled':
        statusColor = Colors.grey;
        break;
      default:
        statusColor = Colors.grey;
    }

    final date = DateTime.parse(transfer.timestamp);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _showTransferDetails(transfer),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  CircleAvatar(
                    backgroundColor: methodColor.withOpacity(0.2),
                    child: Icon(methodIcon, color: methodColor),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          transfer.transferMethodName,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          DateFormat('EEEE، d MMMM yyyy - h:mm a', 'ar')
                              .format(date),
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
                        transfer.formattedAmount,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
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
                          transfer.statusName,
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
              if (transfer.referenceNumber != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.numbers, size: 14, color: Colors.grey.shade600),
                    const SizedBox(width: 4),
                    Text(
                      'الرقم المرجعي: ${transfer.referenceNumber}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ],
              if (transfer.receiptPhotoPath != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.photo, size: 14, color: Colors.grey.shade600),
                    const SizedBox(width: 4),
                    Text(
                      'يحتوي على صورة إيصال',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showTransferDetails(MoneyTransfer transfer) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تفاصيل التحويل'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (transfer.receiptPhotoPath != null) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.file(
                    File(transfer.receiptPhotoPath!),
                    height: 200,
                    width: double.infinity,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(height: 16),
              ],
              _buildDetailRow('المبلغ', transfer.formattedAmount),
              _buildDetailRow('الطريقة', transfer.transferMethodName),
              _buildDetailRow('الحالة', transfer.statusName),
              if (transfer.referenceNumber != null)
                _buildDetailRow('الرقم المرجعي', transfer.referenceNumber!),
              if (transfer.senderName != null)
                _buildDetailRow('المرسل', transfer.senderName!),
              if (transfer.receiverName != null)
                _buildDetailRow('المستلم', transfer.receiverName!),
              if (transfer.notes != null)
                _buildDetailRow('ملاحظات', transfer.notes!),
              _buildDetailRow(
                'التاريخ',
                DateFormat('yyyy-MM-dd h:mm a', 'ar')
                    .format(DateTime.parse(transfer.timestamp)),
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
