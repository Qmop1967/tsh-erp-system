import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:intl/intl.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

class CreateRemittancePage extends StatefulWidget {
  const CreateRemittancePage({super.key});

  @override
  State<CreateRemittancePage> createState() => _CreateRemittancePageState();
}

class _CreateRemittancePageState extends State<CreateRemittancePage> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _remittanceNumberController = TextEditingController();
  final _feesController = TextEditingController();
  final _notesController = TextEditingController();

  String _selectedChannel = 'Al-Taif Exchange';
  String _selectedCurrency = 'IQD';
  DateTime _selectedDate = DateTime.now();
  File? _proofDocument;

  final List<String> _channels = [
    'Al-Taif Exchange',
    'Al-Taif Bank',
    'Zain Cash',
    'Super Key',
    'Other',
  ];

  final List<String> _currencies = ['IQD', 'USD'];

  @override
  void dispose() {
    _amountController.dispose();
    _remittanceNumberController.dispose();
    _feesController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F8FA),
      appBar: AppBar(
        backgroundColor: const Color(0xFF4FC3F7),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'إنشاء حوالة جديدة',
          style: TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _buildSectionHeader('تفاصيل الحوالة', MdiIcons.informationOutline),
            const SizedBox(height: 16),
            _buildAmountField(),
            const SizedBox(height: 16),
            _buildCurrencySelector(),
            const SizedBox(height: 16),
            _buildRemittanceNumberField(),
            const SizedBox(height: 16),
            _buildChannelDropdown(),
            const SizedBox(height: 16),
            _buildDatePicker(),
            const SizedBox(height: 24),
            _buildSectionHeader('المرفقات', MdiIcons.paperclip),
            const SizedBox(height: 16),
            _buildDocumentUpload(),
            const SizedBox(height: 24),
            _buildSectionHeader('معلومات إضافية', MdiIcons.plus),
            const SizedBox(height: 16),
            _buildFeesField(),
            const SizedBox(height: 16),
            _buildNotesField(),
            const SizedBox(height: 32),
            _buildSubmitButton(),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 22, color: const Color(0xFF0288D1)),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
      ],
    );
  }

  Widget _buildAmountField() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextFormField(
        controller: _amountController,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: 'مبلغ التحويل *',
          hintText: 'أدخل المبلغ',
          prefixIcon: Icon(MdiIcons.cash, color: const Color(0xFF0288D1)),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'يرجى إدخال مبلغ التحويل';
          }
          if (double.tryParse(value) == null) {
            return 'يرجى إدخال رقم صحيح';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildCurrencySelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(MdiIcons.currencyUsd, color: const Color(0xFF0288D1)),
          const SizedBox(width: 12),
          const Text(
            'العملة:',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          ..._currencies.map((currency) {
            return Padding(
              padding: const EdgeInsets.only(left: 12),
              child: ChoiceChip(
                label: Text(currency),
                selected: _selectedCurrency == currency,
                onSelected: (selected) {
                  setState(() {
                    _selectedCurrency = currency;
                  });
                },
                selectedColor: const Color(0xFF4FC3F7),
                labelStyle: TextStyle(
                  color: _selectedCurrency == currency ? Colors.white : Colors.black87,
                  fontWeight: FontWeight.bold,
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildRemittanceNumberField() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextFormField(
        controller: _remittanceNumberController,
        decoration: InputDecoration(
          labelText: 'رقم الحوالة *',
          hintText: 'رقم المرجع من البنك أو الصرافة',
          prefixIcon: Icon(MdiIcons.numeric, color: const Color(0xFF0288D1)),
          suffixIcon: IconButton(
            icon: Icon(MdiIcons.qrcodeScan, color: const Color(0xFF0288D1)),
            onPressed: () {
              // QR Code scan functionality
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('ميزة مسح QR قريباً')),
              );
            },
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'يرجى إدخال رقم الحوالة';
          }
          return null;
        },
      ),
    );
  }

  Widget _buildChannelDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: DropdownButtonFormField<String>(
        value: _selectedChannel,
        decoration: InputDecoration(
          labelText: 'قناة التحويل *',
          prefixIcon: Icon(MdiIcons.bankTransfer, color: const Color(0xFF0288D1)),
          border: InputBorder.none,
        ),
        items: _channels.map((channel) {
          return DropdownMenuItem(
            value: channel,
            child: Text(channel),
          );
        }).toList(),
        onChanged: (value) {
          setState(() {
            _selectedChannel = value!;
          });
        },
      ),
    );
  }

  Widget _buildDatePicker() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListTile(
        leading: Icon(MdiIcons.calendar, color: const Color(0xFF0288D1)),
        title: const Text('تاريخ التحويل'),
        subtitle: Text(
          DateFormat('yyyy-MM-dd').format(_selectedDate),
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: () async {
          final date = await showDatePicker(
            context: context,
            initialDate: _selectedDate,
            firstDate: DateTime(2020),
            lastDate: DateTime.now(),
          );
          if (date != null) {
            setState(() {
              _selectedDate = date;
            });
          }
        },
      ),
    );
  }

  Widget _buildDocumentUpload() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: const Color(0xFF4FC3F7).withOpacity(0.3),
          width: 2,
          style: BorderStyle.solid,
        ),
      ),
      child: Column(
        children: [
          if (_proofDocument != null)
            Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.file(
                    _proofDocument!,
                    height: 200,
                    width: double.infinity,
                    fit: BoxFit.cover,
                  ),
                ),
                Positioned(
                  top: 8,
                  right: 8,
                  child: IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    style: IconButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    onPressed: () {
                      setState(() {
                        _proofDocument = null;
                      });
                    },
                  ),
                ),
              ],
            )
          else
            Column(
              children: [
                Icon(
                  MdiIcons.fileUpload,
                  size: 48,
                  color: const Color(0xFF4FC3F7),
                ),
                const SizedBox(height: 12),
                const Text(
                  'رفع صورة الإيصال',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'صورة واضحة من إيصال التحويل',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ElevatedButton.icon(
                      onPressed: () => _pickImage(ImageSource.camera),
                      icon: Icon(MdiIcons.camera),
                      label: const Text('التقاط'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4FC3F7),
                      ),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      onPressed: () => _pickImage(ImageSource.gallery),
                      icon: Icon(MdiIcons.image),
                      label: const Text('اختيار'),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF4FC3F7)),
                      ),
                    ),
                  ],
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildFeesField() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextFormField(
        controller: _feesController,
        keyboardType: TextInputType.number,
        decoration: InputDecoration(
          labelText: 'رسوم التحويل',
          hintText: 'اختياري',
          prefixIcon: Icon(MdiIcons.cashMinus, color: const Color(0xFFFFA726)),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildNotesField() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: TextFormField(
        controller: _notesController,
        maxLines: 4,
        decoration: InputDecoration(
          labelText: 'ملاحظات',
          hintText: 'أي معلومات إضافية...',
          prefixIcon: Icon(MdiIcons.noteText, color: const Color(0xFF0288D1)),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return Container(
      height: 56,
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF4FC3F7), Color(0xFF0288D1)],
        ),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF4FC3F7).withOpacity(0.3),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: ElevatedButton(
        onPressed: _submitRemittance,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: const Text(
          'إرسال الحوالة',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
      ),
    );
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(
      source: source,
      imageQuality: 85,
    );

    if (pickedFile != null) {
      setState(() {
        _proofDocument = File(pickedFile.path);
      });
    }
  }

  void _submitRemittance() {
    if (_formKey.currentState!.validate()) {
      // TODO: Submit to API
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('تم إنشاء الحوالة بنجاح'),
          backgroundColor: const Color(0xFF66BB6A),
          action: SnackBarAction(
            label: 'عرض',
            textColor: Colors.white,
            onPressed: () {},
          ),
        ),
      );
      Navigator.pop(context);
    }
  }
}
