import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:excel/excel.dart';
import 'package:csv/csv.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class ExportService {
  static Future<String> _getExportPath(String fileName) async {
    final directory = await getApplicationDocumentsDirectory();
    return '${directory.path}/$fileName';
  }

  static Future<void> exportToPDF({
    required String reportTitle,
    required String reportType,
    required Map<String, dynamic> data,
    required BuildContext context,
  }) async {
    try {
      final pdf = pw.Document();
      
      pdf.addPage(
        pw.MultiPage(
          pageFormat: PdfPageFormat.a4,
          build: (pw.Context context) {
            return [
              // Header
              pw.Header(
                level: 0,
                child: pw.Text(
                  'TSH ERP System - $reportTitle',
                  style: pw.TextStyle(
                    fontSize: 20,
                    fontWeight: pw.FontWeight.bold,
                  ),
                ),
              ),
              pw.SizedBox(height: 20),
              
              // Report Info
              pw.Container(
                padding: const pw.EdgeInsets.all(10),
                decoration: pw.BoxDecoration(
                  border: pw.Border.all(color: PdfColors.grey300),
                ),
                child: pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    pw.Text('Report Type: $reportType', style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
                    pw.Text('Generated: ${DateTime.now().toString().split('.')[0]}'),
                    pw.Text('TSH Inventory Management System'),
                  ],
                ),
              ),
              pw.SizedBox(height: 20),
              
              // Data sections based on report type
              ...(_buildPDFContent(reportType, data)),
            ];
          },
        ),
      );

      final fileName = 'TSH_${reportType}_${DateTime.now().millisecondsSinceEpoch}.pdf';
      final filePath = await _getExportPath(fileName);
      final file = File(filePath);
      await file.writeAsBytes(await pdf.save());

      // Share the file
      await Share.shareXFiles([XFile(filePath)], text: 'TSH $reportTitle Report');
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ PDF exported and shared successfully!')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ Error exporting PDF: $e')),
        );
      }
    }
  }

  static List<pw.Widget> _buildPDFContent(String reportType, Map<String, dynamic> data) {
    switch (reportType) {
      case 'stock_levels':
        return [
          pw.Text('Stock Levels Summary', style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 10),
          _buildStockLevelsPDFTable(data),
        ];
      case 'low_stock_alerts':
        return [
          pw.Text('Low Stock Alerts', style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 10),
          _buildLowStockPDFTable(data),
        ];
      case 'packaging_summary':
        return [
          pw.Text('Packaging Summary', style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 10),
          _buildPackagingSummaryPDF(data),
        ];
      case 'shipment_tracking':
        return [
          pw.Text('Shipment Tracking', style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 10),
          _buildShipmentTrackingPDF(data),
        ];
      case 'warehouse_utilization':
        return [
          pw.Text('Warehouse Utilization', style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 10),
          _buildWarehouseUtilizationPDF(data),
        ];
      default:
        return [
          pw.Text('General Report Data', style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
          pw.SizedBox(height: 10),
          pw.Text('Total Inventory Value: \$${data['totalInventoryValue']?.toString() ?? 'N/A'}'),
          pw.Text('Stock Turnover Ratio: ${data['stockTurnoverRatio']?.toString() ?? 'N/A'}'),
          pw.Text('Low Stock Items: ${data['lowStockItemsCount']?.toString() ?? '0'}'),
          pw.Text('Zero Stock Items: ${data['zeroStockItemsCount']?.toString() ?? '0'}'),
        ];
    }
  }

  static pw.Widget _buildStockLevelsPDFTable(Map<String, dynamic> data) {
    return pw.Table(
      border: pw.TableBorder.all(color: PdfColors.grey300),
      children: [
        pw.TableRow(
          decoration: pw.BoxDecoration(color: PdfColors.grey100),
          children: [
            pw.Padding(padding: const pw.EdgeInsets.all(8), child: pw.Text('Item', style: pw.TextStyle(fontWeight: pw.FontWeight.bold))),
            pw.Padding(padding: const pw.EdgeInsets.all(8), child: pw.Text('Current Stock', style: pw.TextStyle(fontWeight: pw.FontWeight.bold))),
            pw.Padding(padding: const pw.EdgeInsets.all(8), child: pw.Text('Min Stock', style: pw.TextStyle(fontWeight: pw.FontWeight.bold))),
            pw.Padding(padding: const pw.EdgeInsets.all(8), child: pw.Text('Status', style: pw.TextStyle(fontWeight: pw.FontWeight.bold))),
          ],
        ),
        // Sample data rows
        ..._generateSampleStockRows(),
      ],
    );
  }

  static List<pw.TableRow> _generateSampleStockRows() {
    final sampleItems = [
      ['Phone Charger USB-C', '150', '50', 'Normal'],
      ['Bluetooth Headphones', '25', '30', 'Low Stock'],
      ['Phone Cases iPhone 14', '200', '100', 'Normal'],
      ['Screen Protectors', '15', '25', 'Low Stock'],
      ['Power Banks 10000mAh', '80', '40', 'Normal'],
    ];
    
    return sampleItems.map((item) => pw.TableRow(
      children: item.map((cell) => pw.Padding(
        padding: const pw.EdgeInsets.all(8),
        child: pw.Text(cell),
      )).toList(),
    )).toList();
  }

  static pw.Widget _buildLowStockPDFTable(Map<String, dynamic> data) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text('Low Stock Items Count: ${data['lowStockItemsCount'] ?? 0}'),
        pw.SizedBox(height: 10),
        pw.Text('Zero Stock Items Count: ${data['zeroStockItemsCount'] ?? 0}'),
        pw.SizedBox(height: 10),
        pw.Text('Recommended Actions:'),
        pw.Bullet(text: 'Reorder low stock items immediately'),
        pw.Bullet(text: 'Contact suppliers for urgent items'),
        pw.Bullet(text: 'Consider increasing minimum stock levels'),
      ],
    );
  }

  static pw.Widget _buildPackagingSummaryPDF(Map<String, dynamic> data) {
    final packageData = data['packageVariants'] as Map<String, dynamic>? ?? {};
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text('Packaging Summary:'),
        pw.SizedBox(height: 10),
        pw.Text('Boxes: ${packageData['boxes'] ?? 0}'),
        pw.Text('Bundles: ${packageData['bundles'] ?? 0}'),
        pw.Text('Bags: ${packageData['bags'] ?? 0}'),
        pw.SizedBox(height: 10),
        pw.Text('Total Completed Packaging: ${data['completedPackaging'] ?? 0}'),
      ],
    );
  }

  static pw.Widget _buildShipmentTrackingPDF(Map<String, dynamic> data) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text('Shipment Status:'),
        pw.SizedBox(height: 10),
        pw.Text('Pending Shipments: ${data['pendingShipments'] ?? 0}'),
        pw.Text('Warehouse Utilization: ${data['warehouseUtilization'] ?? 0}%'),
        pw.SizedBox(height: 10),
        pw.Text('Recent Shipment Activities:'),
        pw.Bullet(text: 'Shipment #SH001 - In Transit'),
        pw.Bullet(text: 'Shipment #SH002 - Delivered'),
        pw.Bullet(text: 'Shipment #SH003 - Preparing'),
      ],
    );
  }

  static pw.Widget _buildWarehouseUtilizationPDF(Map<String, dynamic> data) {
    return pw.Column(
      crossAxisAlignment: pw.CrossAxisAlignment.start,
      children: [
        pw.Text('Warehouse Utilization: ${data['warehouseUtilization'] ?? 0}%'),
        pw.SizedBox(height: 10),
        pw.Text('Capacity Analysis:'),
        pw.Bullet(text: 'Main Warehouse: 78% utilized'),
        pw.Bullet(text: 'Retail Shop: 45% utilized'),
        pw.Bullet(text: 'Available Space: 2,200 sq ft'),
        pw.SizedBox(height: 10),
        pw.Text('Recommendations:'),
        pw.Bullet(text: 'Optimize storage layout'),
        pw.Bullet(text: 'Consider expansion if >85% utilization'),
      ],
    );
  }

  static Future<void> exportToExcel({
    required String reportTitle,
    required String reportType,
    required Map<String, dynamic> data,
    required BuildContext context,
  }) async {
    try {
      final excel = Excel.createExcel();
      final sheet = excel['TSH_Report'];
      
      // Add header
      sheet.cell(CellIndex.indexByString('A1')).value = 'TSH ERP System - $reportTitle';
      sheet.cell(CellIndex.indexByString('A2')).value = 'Generated: ${DateTime.now().toString().split('.')[0]}';
      sheet.cell(CellIndex.indexByString('A3')).value = 'Report Type: $reportType';
      
      // Add data based on report type
      _addExcelData(sheet, reportType, data);
      
      final fileName = 'TSH_${reportType}_${DateTime.now().millisecondsSinceEpoch}.xlsx';
      final filePath = await _getExportPath(fileName);
      final file = File(filePath);
      await file.writeAsBytes(excel.encode()!);
      
      // Share the file
      await Share.shareXFiles([XFile(filePath)], text: 'TSH $reportTitle Report');
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ Excel exported and shared successfully!')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ Error exporting Excel: $e')),
        );
      }
    }
  }

  static void _addExcelData(Sheet sheet, String reportType, Map<String, dynamic> data) {
    int currentRow = 5;
    
    switch (reportType) {
      case 'stock_levels':
        // Headers
        sheet.cell(CellIndex.indexByString('A$currentRow')).value = 'Item Name';
        sheet.cell(CellIndex.indexByString('B$currentRow')).value = 'Current Stock';
        sheet.cell(CellIndex.indexByString('C$currentRow')).value = 'Min Stock';
        sheet.cell(CellIndex.indexByString('D$currentRow')).value = 'Status';
        currentRow++;
        
        // Sample data
        final sampleItems = [
          ['Phone Charger USB-C', '150', '50', 'Normal'],
          ['Bluetooth Headphones', '25', '30', 'Low Stock'],
          ['Phone Cases iPhone 14', '200', '100', 'Normal'],
          ['Screen Protectors', '15', '25', 'Low Stock'],
          ['Power Banks 10000mAh', '80', '40', 'Normal'],
        ];
        
        for (final item in sampleItems) {
          sheet.cell(CellIndex.indexByString('A$currentRow')).value = item[0];
          sheet.cell(CellIndex.indexByString('B$currentRow')).value = item[1];
          sheet.cell(CellIndex.indexByString('C$currentRow')).value = item[2];
          sheet.cell(CellIndex.indexByString('D$currentRow')).value = item[3];
          currentRow++;
        }
        break;
        
      case 'low_stock_alerts':
        sheet.cell(CellIndex.indexByString('A$currentRow')).value = 'Low Stock Items Count';
        sheet.cell(CellIndex.indexByString('B$currentRow')).value = data['lowStockItemsCount'] ?? 0;
        currentRow++;
        sheet.cell(CellIndex.indexByString('A$currentRow')).value = 'Zero Stock Items Count';
        sheet.cell(CellIndex.indexByString('B$currentRow')).value = data['zeroStockItemsCount'] ?? 0;
        break;
        
      default:
        sheet.cell(CellIndex.indexByString('A$currentRow')).value = 'Total Inventory Value';
        sheet.cell(CellIndex.indexByString('B$currentRow')).value = data['totalInventoryValue'] ?? 0;
        currentRow++;
        sheet.cell(CellIndex.indexByString('A$currentRow')).value = 'Stock Turnover Ratio';
        sheet.cell(CellIndex.indexByString('B$currentRow')).value = data['stockTurnoverRatio'] ?? 0;
        currentRow++;
        sheet.cell(CellIndex.indexByString('A$currentRow')).value = 'Low Stock Items';
        sheet.cell(CellIndex.indexByString('B$currentRow')).value = data['lowStockItemsCount'] ?? 0;
    }
  }

  static Future<void> exportToCSV({
    required String reportTitle,
    required String reportType,
    required Map<String, dynamic> data,
    required BuildContext context,
  }) async {
    try {
      final List<List<dynamic>> csvData = [];
      
      // Add header rows
      csvData.add(['TSH ERP System - $reportTitle']);
      csvData.add(['Generated: ${DateTime.now().toString().split('.')[0]}']);
      csvData.add(['Report Type: $reportType']);
      csvData.add([]); // Empty row
      
      // Add data based on report type
      _addCSVData(csvData, reportType, data);
      
      final csvString = const ListToCsvConverter().convert(csvData);
      
      final fileName = 'TSH_${reportType}_${DateTime.now().millisecondsSinceEpoch}.csv';
      final filePath = await _getExportPath(fileName);
      final file = File(filePath);
      await file.writeAsString(csvString);
      
      // Share the file
      await Share.shareXFiles([XFile(filePath)], text: 'TSH $reportTitle Report');
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ CSV exported and shared successfully!')),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ Error exporting CSV: $e')),
        );
      }
    }
  }

  static void _addCSVData(List<List<dynamic>> csvData, String reportType, Map<String, dynamic> data) {
    switch (reportType) {
      case 'stock_levels':
        csvData.add(['Item Name', 'Current Stock', 'Min Stock', 'Status']);
        csvData.add(['Phone Charger USB-C', '150', '50', 'Normal']);
        csvData.add(['Bluetooth Headphones', '25', '30', 'Low Stock']);
        csvData.add(['Phone Cases iPhone 14', '200', '100', 'Normal']);
        csvData.add(['Screen Protectors', '15', '25', 'Low Stock']);
        csvData.add(['Power Banks 10000mAh', '80', '40', 'Normal']);
        break;
        
      case 'low_stock_alerts':
        csvData.add(['Metric', 'Value']);
        csvData.add(['Low Stock Items Count', data['lowStockItemsCount'] ?? 0]);
        csvData.add(['Zero Stock Items Count', data['zeroStockItemsCount'] ?? 0]);
        break;
        
      case 'packaging_summary':
        csvData.add(['Package Type', 'Count']);
        final packageData = data['packageVariants'] as Map<String, dynamic>? ?? {};
        csvData.add(['Boxes', packageData['boxes'] ?? 0]);
        csvData.add(['Bundles', packageData['bundles'] ?? 0]);
        csvData.add(['Bags', packageData['bags'] ?? 0]);
        csvData.add(['Total Completed', data['completedPackaging'] ?? 0]);
        break;
        
      default:
        csvData.add(['Metric', 'Value']);
        csvData.add(['Total Inventory Value', data['totalInventoryValue'] ?? 0]);
        csvData.add(['Stock Turnover Ratio', data['stockTurnoverRatio'] ?? 0]);
        csvData.add(['Low Stock Items', data['lowStockItemsCount'] ?? 0]);
        csvData.add(['Zero Stock Items', data['zeroStockItemsCount'] ?? 0]);
        csvData.add(['Warehouse Utilization %', data['warehouseUtilization'] ?? 0]);
    }
  }
}
