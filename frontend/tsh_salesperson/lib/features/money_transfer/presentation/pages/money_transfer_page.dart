import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';

import '../../../../core/models/money_transfer.dart';
import '../../../../localization/app_localizations.dart';
import '../../../gps_tracking/services/gps_service.dart';
import '../../../gps_tracking/models/location_data.dart';
import '../blocs/money_transfer_bloc.dart';

class MoneyTransferPage extends StatefulWidget {
  const MoneyTransferPage({super.key});

  @override
  State<MoneyTransferPage> createState() => _MoneyTransferPageState();
}

class _MoneyTransferPageState extends State<MoneyTransferPage> {
  final _formKey = GlobalKey<FormState>();
  final _amountUsdController = TextEditingController();
  final _amountIqdController = TextEditingController();
  final _exchangeRateController = TextEditingController();
  final _grossSalesController = TextEditingController();
  final _claimedCommissionController = TextEditingController();
  final _platformReferenceController = TextEditingController();
  final _transferFeeController = TextEditingController(text: '0.0');

  TransferPlatform _selectedPlatform = TransferPlatform.zainCash;
  File? _receiptPhoto;
  LocationData? _currentLocation;
  bool _isLocationVerified = false;
  bool _isSubmitting = false;

  final ImagePicker _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    // Auto-verify location when page loads
    _verifyLocation();
  }

  @override
  void dispose() {
    _amountUsdController.dispose();
    _amountIqdController.dispose();
    _exchangeRateController.dispose();
    _grossSalesController.dispose();
    _claimedCommissionController.dispose();
    _platformReferenceController.dispose();
    _transferFeeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(localizations.submitTransfer),
          backgroundColor: const Color(0xFF1565C0),
          foregroundColor: Colors.white,
          elevation: 0,
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _verifyLocation,
              tooltip: localizations.refresh,
            ),
          ],
        ),
        body: BlocListener<MoneyTransferBloc, MoneyTransferState>(
          listener: (context, state) {
            if (state is LocationVerificationSuccess) {
              setState(() {
                _currentLocation = state.location;
                _isLocationVerified = true;
              });
              
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    isArabic 
                        ? state.verificationMessageArabic 
                        : state.verificationMessage,
                  ),
                  backgroundColor: Colors.green,
                  duration: const Duration(seconds: 2),
                ),
              );
            } else if (state is MoneyTransferSubmissionSuccess) {
              setState(() {
                _isSubmitting = false;
              });
              
              // Show success dialog
              _showSuccessDialog(context, state, isArabic);
              
              // Clear form
              _clearForm();
            } else if (state is MoneyTransferSubmissionLoading) {
              setState(() {
                _isSubmitting = true;
              });
            } else if (state is MoneyTransferError) {
              setState(() {
                _isSubmitting = false;
              });
              
              _showErrorDialog(context, state, isArabic);
            }
          },
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 🚨 CRITICAL: GPS Verification Section
                  _buildGPSVerificationCard(localizations, isArabic),
                  
                  const SizedBox(height: 20),
                  
                  // 💰 Money Transfer Details
                  _buildMoneyTransferCard(localizations, isArabic),
                  
                  const SizedBox(height: 20),
                  
                  // 📋 Commission Details
                  _buildCommissionCard(localizations, isArabic),
                  
                  const SizedBox(height: 20),
                  
                  // 💳 Platform Selection
                  _buildPlatformCard(localizations, isArabic),
                  
                  const SizedBox(height: 20),
                  
                  // 📷 Receipt Photo
                  _buildReceiptPhotoCard(localizations, isArabic),
                  
                  const SizedBox(height: 30),
                  
                  // 🚀 Submit Button
                  _buildSubmitButton(localizations, isArabic),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  // ==============================================
  // 📍 GPS VERIFICATION CARD
  // ==============================================
  
  Widget _buildGPSVerificationCard(AppLocalizations localizations, bool isArabic) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _isLocationVerified ? Icons.location_on : Icons.location_off,
                  color: _isLocationVerified ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  localizations.locationVerification,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (!_isLocationVerified)
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: _verifyLocation,
                    tooltip: localizations.refresh,
                  ),
              ],
            ),
            const SizedBox(height: 12),
            if (_currentLocation != null) ...[
              _buildLocationInfo(localizations, isArabic),
            ] else ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  border: Border.all(color: Colors.orange),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning, color: Colors.orange),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        localizations.locationVerificationRequired,
                        style: const TextStyle(color: Colors.orange),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLocationInfo(AppLocalizations localizations, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.green.shade50,
        border: Border.all(color: Colors.green),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.green),
              const SizedBox(width: 8),
              Text(
                localizations.locationVerifiedSuccessfully,
                style: const TextStyle(
                  color: Colors.green,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '${localizations.gpsCoordinates}: ${_currentLocation!.coordinatesString}',
            style: const TextStyle(fontSize: 12),
          ),
          if (_currentLocation!.address != null) ...[
            const SizedBox(height: 4),
            Text(
              '${localizations.locationAddress}: ${_currentLocation!.address}',
              style: const TextStyle(fontSize: 12),
            ),
          ],
          const SizedBox(height: 4),
          Text(
            '${localizations.locationAccuracy}: ${_currentLocation!.accuracyText}',
            style: const TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }

  // ==============================================
  // 💰 MONEY TRANSFER DETAILS CARD
  // ==============================================
  
  Widget _buildMoneyTransferCard(AppLocalizations localizations, bool isArabic) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.transferAmount,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            // Amount in USD
            TextFormField(
              controller: _amountUsdController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: localizations.amountInUSD,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.attach_money),
                suffix: Text(localizations.usd),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '${localizations.amountInUSD} ${localizations.required}';
                }
                if (double.tryParse(value) == null) {
                  return isArabic ? 'قيمة غير صحيحة' : 'Invalid amount';
                }
                return null;
              },
              onChanged: _calculateIQDAmount,
            ),
            
            const SizedBox(height: 16),
            
            // Exchange Rate
            TextFormField(
              controller: _exchangeRateController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: localizations.exchangeRate,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.currency_exchange),
                helperText: isArabic ? 'دينار عراقي لكل دولار' : 'IQD per USD',
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '${localizations.exchangeRate} ${localizations.required}';
                }
                if (double.tryParse(value) == null) {
                  return isArabic ? 'قيمة غير صحيحة' : 'Invalid rate';
                }
                return null;
              },
              onChanged: (value) => _calculateIQDAmount(value),
            ),
            
            const SizedBox(height: 16),
            
            // Amount in IQD (Auto-calculated)
            TextFormField(
              controller: _amountIqdController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: localizations.amountInIQD,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.money),
                suffix: Text(localizations.iqd),
                helperText: isArabic ? 'محسوب تلقائياً' : 'Auto-calculated',
              ),
              readOnly: true,
            ),
          ],
        ),
      ),
    );
  }

  // ==============================================
  // 📋 COMMISSION DETAILS CARD
  // ==============================================
  
  Widget _buildCommissionCard(AppLocalizations localizations, bool isArabic) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.commission,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            // Gross Sales
            TextFormField(
              controller: _grossSalesController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: localizations.grossSales,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.point_of_sale),
                suffix: Text(localizations.usd),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '${localizations.grossSales} ${localizations.required}';
                }
                if (double.tryParse(value) == null) {
                  return isArabic ? 'قيمة غير صحيحة' : 'Invalid amount';
                }
                return null;
              },
              onChanged: _calculateCommission,
            ),
            
            const SizedBox(height: 16),
            
            // Claimed Commission
            TextFormField(
              controller: _claimedCommissionController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: localizations.claimedCommission,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.paid),
                suffix: Text(localizations.usd),
                helperText: isArabic 
                    ? 'العمولة التي تطالب بها (2.25%)' 
                    : 'Commission you are claiming (2.25%)',
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return '${localizations.claimedCommission} ${localizations.required}';
                }
                if (double.tryParse(value) == null) {
                  return isArabic ? 'قيمة غير صحيحة' : 'Invalid amount';
                }
                return null;
              },
            ),
            
            // Commission warning if discrepancy
            if (_getCommissionDiscrepancy() > 0.01)
              Container(
                margin: const EdgeInsets.only(top: 12),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  border: Border.all(color: Colors.orange),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.warning, color: Colors.orange),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        isArabic 
                            ? 'تضارب في العمولة: \$${_getCommissionDiscrepancy().toStringAsFixed(2)}'
                            : 'Commission discrepancy: \$${_getCommissionDiscrepancy().toStringAsFixed(2)}',
                        style: const TextStyle(color: Colors.orange),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  // ==============================================
  // 💳 PLATFORM SELECTION CARD
  // ==============================================
  
  Widget _buildPlatformCard(AppLocalizations localizations, bool isArabic) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.transferPlatform,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            // Platform Selection
            DropdownButtonFormField<TransferPlatform>(
              value: _selectedPlatform,
              decoration: InputDecoration(
                labelText: localizations.selectPlatform,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.payment),
              ),
              items: TransferPlatform.values.map((platform) {
                return DropdownMenuItem(
                  value: platform,
                  child: Text(
                    isArabic ? platform.displayNameArabic : platform.displayName,
                  ),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  _selectedPlatform = value!;
                });
              },
            ),
            
            const SizedBox(height: 16),
            
            // Platform Reference (Optional)
            TextFormField(
              controller: _platformReferenceController,
              decoration: InputDecoration(
                labelText: '${localizations.platformReference} (${localizations.optional})',
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.receipt_long),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // Transfer Fee
            TextFormField(
              controller: _transferFeeController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: localizations.transferFee,
                border: const OutlineInputBorder(),
                prefixIcon: const Icon(Icons.money_off),
                suffix: Text(localizations.usd),
              ),
              validator: (value) {
                if (value != null && value.isNotEmpty) {
                  if (double.tryParse(value) == null) {
                    return isArabic ? 'قيمة غير صحيحة' : 'Invalid amount';
                  }
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  // ==============================================
  // 📷 RECEIPT PHOTO CARD
  // ==============================================
  
  Widget _buildReceiptPhotoCard(AppLocalizations localizations, bool isArabic) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              localizations.receiptPhoto,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            
            if (_receiptPhoto != null) ...[
              // Show captured photo
              Container(
                height: 200,
                width: double.infinity,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.file(
                    _receiptPhoto!,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _captureReceiptPhoto,
                      icon: const Icon(Icons.camera_alt),
                      label: Text(isArabic ? 'التقط صورة جديدة' : 'Retake Photo'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {
                        setState(() {
                          _receiptPhoto = null;
                        });
                      },
                      icon: const Icon(Icons.delete),
                      label: Text(localizations.delete),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ] else ...[
              // Photo capture buttons
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _captureReceiptPhoto,
                      icon: const Icon(Icons.camera_alt),
                      label: Text(localizations.takeReceiptPhoto),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _selectReceiptPhoto,
                      icon: const Icon(Icons.photo_library),
                      label: Text(localizations.uploadReceiptPhoto),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  // ==============================================
  // 🚀 SUBMIT BUTTON
  // ==============================================
  
  Widget _buildSubmitButton(AppLocalizations localizations, bool isArabic) {
    final canSubmit = _isLocationVerified && !_isSubmitting;
    
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: canSubmit ? _submitTransfer : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF1565C0),
          foregroundColor: Colors.white,
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isSubmitting
            ? Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      color: Colors.white,
                      strokeWidth: 2,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    localizations.pleaseWait,
                    style: const TextStyle(fontSize: 16),
                  ),
                ],
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.security, size: 24),
                  const SizedBox(width: 12),
                  Text(
                    localizations.submitTransfer,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
      ),
    );
  }

  // ==============================================
  // 🔧 HELPER METHODS
  // ==============================================

  void _verifyLocation() {
    context.read<MoneyTransferBloc>().add(VerifyCurrentLocation());
  }

  void _calculateIQDAmount(String? value) {
    final usdAmount = double.tryParse(_amountUsdController.text);
    final exchangeRate = double.tryParse(_exchangeRateController.text);
    
    if (usdAmount != null && exchangeRate != null) {
      final iqdAmount = usdAmount * exchangeRate;
      _amountIqdController.text = iqdAmount.toStringAsFixed(2);
    }
  }

  void _calculateCommission(String? value) {
    final grossSales = double.tryParse(_grossSalesController.text);
    
    if (grossSales != null) {
      final commission = grossSales * 0.0225; // 2.25%
      _claimedCommissionController.text = commission.toStringAsFixed(2);
    }
  }

  double _getCommissionDiscrepancy() {
    final grossSales = double.tryParse(_grossSalesController.text) ?? 0;
    final claimedCommission = double.tryParse(_claimedCommissionController.text) ?? 0;
    final calculatedCommission = grossSales * 0.0225;
    
    return (claimedCommission - calculatedCommission).abs();
  }

  Future<void> _captureReceiptPhoto() async {
    final XFile? photo = await _imagePicker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
      maxWidth: 1920,
      maxHeight: 1080,
    );
    
    if (photo != null) {
      setState(() {
        _receiptPhoto = File(photo.path);
      });
    }
  }

  Future<void> _selectReceiptPhoto() async {
    final XFile? photo = await _imagePicker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 85,
      maxWidth: 1920,
      maxHeight: 1080,
    );
    
    if (photo != null) {
      setState(() {
        _receiptPhoto = File(photo.path);
      });
    }
  }

  void _submitTransfer() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (!_isLocationVerified || _currentLocation == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            Localizations.localeOf(context).languageCode == 'ar'
                ? 'التحقق من الموقع مطلوب قبل الإرسال'
                : 'Location verification required before submission',
          ),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final request = MoneyTransferCreateRequest(
      amountUsd: double.parse(_amountUsdController.text),
      amountIqd: double.parse(_amountIqdController.text),
      exchangeRate: double.parse(_exchangeRateController.text),
      grossSales: double.parse(_grossSalesController.text),
      claimedCommission: double.parse(_claimedCommissionController.text),
      transferPlatform: _selectedPlatform.value,
      platformReference: _platformReferenceController.text.isNotEmpty 
          ? _platformReferenceController.text 
          : null,
      transferFee: double.tryParse(_transferFeeController.text) ?? 0.0,
      gpsLatitude: _currentLocation!.latitude,
      gpsLongitude: _currentLocation!.longitude,
      locationName: _currentLocation!.address,
      receiptPhotoUrl: null, // Will be uploaded separately
    );

    context.read<MoneyTransferBloc>().add(SubmitMoneyTransfer(request));
  }

  void _clearForm() {
    _amountUsdController.clear();
    _amountIqdController.clear();
    _exchangeRateController.clear();
    _grossSalesController.clear();
    _claimedCommissionController.clear();
    _platformReferenceController.clear();
    _transferFeeController.text = '0.0';
    
    setState(() {
      _receiptPhoto = null;
      _selectedPlatform = TransferPlatform.zainCash;
    });
  }

  void _showSuccessDialog(BuildContext context, MoneyTransferSubmissionSuccess state, bool isArabic) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.check_circle, color: Colors.green),
            const SizedBox(width: 8),
            Text(
              isArabic ? 'تم بنجاح' : 'Success',
            ),
          ],
        ),
        content: Text(
          isArabic ? state.messageArabic : state.message,
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // Return to previous screen
            },
            child: Text(
              isArabic ? 'موافق' : 'OK',
            ),
          ),
        ],
      ),
    );
  }

  void _showErrorDialog(BuildContext context, MoneyTransferError state, bool isArabic) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              state.isCritical ? Icons.error : Icons.warning,
              color: state.isCritical ? Colors.red : Colors.orange,
            ),
            const SizedBox(width: 8),
            Text(
              isArabic ? (state.isCritical ? 'خطأ حرج' : 'تحذير') : (state.isCritical ? 'Critical Error' : 'Warning'),
            ),
          ],
        ),
        content: Text(
          isArabic ? state.messageArabic : state.message,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(
              isArabic ? 'موافق' : 'OK',
            ),
          ),
          if (state.errorCode == 'LOCATION_VERIFICATION_FAILED' || state.errorCode.contains('GPS'))
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _verifyLocation();
              },
              child: Text(
                isArabic ? 'إعادة المحاولة' : 'Retry',
              ),
            ),
        ],
      ),
    );
  }
} 