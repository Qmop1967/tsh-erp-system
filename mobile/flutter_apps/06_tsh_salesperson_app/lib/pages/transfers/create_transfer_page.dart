import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../services/transfers/transfer_service.dart';
import '../../models/transfers/money_transfer.dart';
import 'capture_receipt_page.dart';

/// Create Money Transfer Page
/// Form to record new money transfers (ALTaif, ZAIN Cash, SuperQi, Cash)
class CreateTransferPage extends StatefulWidget {
  final int salespersonId;

  const CreateTransferPage({
    Key? key,
    required this.salespersonId,
  }) : super(key: key);

  @override
  State<CreateTransferPage> createState() => _CreateTransferPageState();
}

class _CreateTransferPageState extends State<CreateTransferPage> {
  final _formKey = GlobalKey<FormState>();
  final TransferService _transferService = TransferService();

  // Form fields
  String _selectedMethod = 'altaif';
  final TextEditingController _amountController = TextEditingController();
  String _selectedCurrency = 'IQD';
  final TextEditingController _referenceController = TextEditingController();
  final TextEditingController _senderNameController = TextEditingController();
  final TextEditingController _senderPhoneController = TextEditingController();
  final TextEditingController _receiverNameController = TextEditingController();
  final TextEditingController _receiverPhoneController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();
  String? _receiptPhotoPath;
  bool _isSubmitting = false;

  final ImagePicker _picker = ImagePicker();

  @override
  void dispose() {
    _amountController.dispose();
    _referenceController.dispose();
    _senderNameController.dispose();
    _senderPhoneController.dispose();
    _receiverNameController.dispose();
    _receiverPhoneController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _captureReceipt() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const CaptureReceiptPage(),
      ),
    );

    if (result != null && result is String) {
      setState(() {
        _receiptPhotoPath = result;
      });
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          _receiptPhotoPath = image.path;
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطأ في اختيار الصورة: $e')),
      );
    }
  }

  Future<void> _submitTransfer() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      await _transferService.initialize();

      final transfer = await _transferService.recordTransfer(
        salespersonId: widget.salespersonId,
        transferMethod: _selectedMethod,
        amount: double.parse(_amountController.text),
        currency: _selectedCurrency,
        referenceNumber: _referenceController.text.isEmpty
            ? null
            : _referenceController.text,
        senderName: _senderNameController.text.isEmpty
            ? null
            : _senderNameController.text,
        senderPhone: _senderPhoneController.text.isEmpty
            ? null
            : _senderPhoneController.text,
        receiverName: _receiverNameController.text.isEmpty
            ? null
            : _receiverNameController.text,
        receiverPhone: _receiverPhoneController.text.isEmpty
            ? null
            : _receiverPhoneController.text,
        notes: _notesController.text.isEmpty ? null : _notesController.text,
        receiptPhotoPath: _receiptPhotoPath,
      );

      if (!mounted) return;

      // Show success dialog
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green, size: 32),
              SizedBox(width: 12),
              Text('تم التسجيل بنجاح'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('تم تسجيل التحويل بنجاح'),
              const SizedBox(height: 8),
              Text('المبلغ: ${transfer.formattedAmount}'),
              Text('الطريقة: ${transfer.transferMethodName}'),
              if (transfer.referenceNumber != null)
                Text('الرقم المرجعي: ${transfer.referenceNumber}'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
                Navigator.pop(context, true); // Return to dashboard
              },
              child: const Text('حسناً'),
            ),
            if (_receiptPhotoPath != null)
              ElevatedButton.icon(
                onPressed: () {
                  // TODO: Send to WhatsApp
                  Navigator.pop(context);
                  Navigator.pop(context, true);
                },
                icon: const Icon(Icons.send),
                label: const Text('إرسال عبر واتساب'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
          ],
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('خطأ في تسجيل التحويل: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تحويل مالي جديد'),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Transfer Method Selection
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'طريقة التحويل',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 12,
                        runSpacing: 12,
                        children: [
                          _buildMethodChip(
                            'altaif',
                            'الطيف',
                            MdiIcons.bankTransfer,
                            Colors.blue,
                          ),
                          _buildMethodChip(
                            'zainCash',
                            'زين كاش',
                            MdiIcons.cellphone,
                            Colors.purple,
                          ),
                          _buildMethodChip(
                            'superQi',
                            'سوبر كيو',
                            MdiIcons.qrcode,
                            Colors.orange,
                          ),
                          _buildMethodChip(
                            'cash',
                            'نقدي',
                            MdiIcons.cash,
                            Colors.green,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Amount and Currency
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'المبلغ',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            flex: 2,
                            child: TextFormField(
                              controller: _amountController,
                              keyboardType: const TextInputType.numberWithOptions(
                                decimal: true,
                              ),
                              inputFormatters: [
                                FilteringTextInputFormatter.allow(
                                  RegExp(r'^\d+\.?\d{0,2}'),
                                ),
                              ],
                              decoration: const InputDecoration(
                                labelText: 'المبلغ',
                                hintText: '0.00',
                                prefixIcon: Icon(Icons.attach_money),
                                border: OutlineInputBorder(),
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return 'يرجى إدخال المبلغ';
                                }
                                final amount = double.tryParse(value);
                                if (amount == null || amount <= 0) {
                                  return 'المبلغ غير صحيح';
                                }
                                return null;
                              },
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: DropdownButtonFormField<String>(
                              value: _selectedCurrency,
                              decoration: const InputDecoration(
                                labelText: 'العملة',
                                border: OutlineInputBorder(),
                              ),
                              items: const [
                                DropdownMenuItem(
                                  value: 'IQD',
                                  child: Text('د.ع'),
                                ),
                                DropdownMenuItem(
                                  value: 'USD',
                                  child: Text('USD'),
                                ),
                              ],
                              onChanged: (value) {
                                setState(() {
                                  _selectedCurrency = value!;
                                });
                              },
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Reference Number
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: TextFormField(
                    controller: _referenceController,
                    decoration: const InputDecoration(
                      labelText: 'الرقم المرجعي (اختياري)',
                      hintText: 'رقم المعاملة أو التحويل',
                      prefixIcon: Icon(Icons.numbers),
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Sender Details
              if (_selectedMethod != 'cash') ...[
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'معلومات المرسل',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _senderNameController,
                          decoration: const InputDecoration(
                            labelText: 'اسم المرسل',
                            prefixIcon: Icon(Icons.person),
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _senderPhoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                            labelText: 'رقم هاتف المرسل',
                            prefixIcon: Icon(Icons.phone),
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // Receiver Details
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'معلومات المستلم',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _receiverNameController,
                          decoration: const InputDecoration(
                            labelText: 'اسم المستلم',
                            prefixIcon: Icon(Icons.person_outline),
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _receiverPhoneController,
                          keyboardType: TextInputType.phone,
                          decoration: const InputDecoration(
                            labelText: 'رقم هاتف المستلم',
                            prefixIcon: Icon(Icons.phone_outlined),
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Receipt Photo
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'صورة الإيصال (مطلوب للتحقق)',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      if (_receiptPhotoPath != null) ...[
                        ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.file(
                            File(_receiptPhotoPath!),
                            height: 200,
                            width: double.infinity,
                            fit: BoxFit.cover,
                          ),
                        ),
                        const SizedBox(height: 12),
                      ],
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: _captureReceipt,
                              icon: const Icon(Icons.camera_alt),
                              label: const Text('التقاط صورة'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: _pickFromGallery,
                              icon: const Icon(Icons.photo_library),
                              label: const Text('من المعرض'),
                            ),
                          ),
                        ],
                      ),
                      if (_receiptPhotoPath != null)
                        TextButton.icon(
                          onPressed: () {
                            setState(() {
                              _receiptPhotoPath = null;
                            });
                          },
                          icon: const Icon(Icons.delete, color: Colors.red),
                          label: const Text(
                            'حذف الصورة',
                            style: TextStyle(color: Colors.red),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Notes
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: TextFormField(
                    controller: _notesController,
                    maxLines: 3,
                    decoration: const InputDecoration(
                      labelText: 'ملاحظات (اختياري)',
                      hintText: 'أي معلومات إضافية...',
                      prefixIcon: Icon(Icons.note),
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Submit Button
              ElevatedButton(
                onPressed: _isSubmitting ? null : _submitTransfer,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.all(16),
                  textStyle: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Text('تسجيل التحويل'),
              ),
              const SizedBox(height: 100),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMethodChip(
    String value,
    String label,
    IconData icon,
    Color color,
  ) {
    final isSelected = _selectedMethod == value;

    return ChoiceChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 20,
            color: isSelected ? Colors.white : color,
          ),
          const SizedBox(width: 8),
          Text(label),
        ],
      ),
      selectedColor: color,
      backgroundColor: color.withOpacity(0.1),
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : color,
        fontWeight: FontWeight.bold,
      ),
      onSelected: (selected) {
        setState(() {
          _selectedMethod = value;
        });
      },
    );
  }
}
