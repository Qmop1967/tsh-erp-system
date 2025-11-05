import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { SalesInvoice, PurchaseInvoice, PaymentMethodEnum, InvoiceTypeEnum } from '../../types';
import { invoiceApi, getAllSalesInvoices, getAllPurchaseInvoices } from '../../lib/api';
import { useNotifications } from '../ui/NotificationProvider';

interface CreatePaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreatePaymentModal: React.FC<CreatePaymentModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { addNotification } = useNotifications();
  const [salesInvoices, setSalesInvoices] = useState<SalesInvoice[]>([]);
  const [purchaseInvoices, setPurchaseInvoices] = useState<PurchaseInvoice[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    payment_number: '',
    amount: 0,
    payment_date: new Date().toISOString().split('T')[0],
    payment_method: PaymentMethodEnum.CASH,
    reference_number: '',
    notes: '',
    invoice_type: InvoiceTypeEnum.SALES,
    sales_invoice_id: '',
    purchase_invoice_id: '',
  });

  useEffect(() => {
    if (isOpen) {
      fetchInvoices();
    }
  }, [isOpen]);

  const fetchInvoices = async () => {
    try {
      const [salesResponse, purchaseResponse] = await Promise.all([
        getAllSalesInvoices({ page: 1, size: 100 }),
        getAllPurchaseInvoices({ page: 1, size: 100 }),
      ]);
      setSalesInvoices(salesResponse.data);
      setPurchaseInvoices(purchaseResponse.data);
    } catch (error) {
      console.error('Failed to fetch invoices:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const paymentData = {
        ...formData,
        amount: Number(formData.amount),
        sales_invoice_id: formData.invoice_type === InvoiceTypeEnum.SALES ? Number(formData.sales_invoice_id) : undefined,
        purchase_invoice_id: formData.invoice_type === InvoiceTypeEnum.PURCHASE ? Number(formData.purchase_invoice_id) : undefined,
      };

      await invoiceApi.createPayment(paymentData);
      addNotification({
        type: 'success',
        title: 'Payment Recorded',
        message: 'Payment has been recorded successfully.',
      });
      onSuccess();
    } catch (error) {
      console.error('Failed to create payment:', error);
      addNotification({
        type: 'error',
        title: 'Error Recording Payment',
        message: 'Failed to record payment. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  if (!isOpen) return null;

  const availableInvoices = formData.invoice_type === InvoiceTypeEnum.SALES ? salesInvoices : purchaseInvoices;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Record Payment</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Payment Number
            </label>
            <input
              type="text"
              name="payment_number"
              value={formData.payment_number}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Auto-generated if left empty"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Invoice Type *
            </label>
            <select
              name="invoice_type"
              value={formData.invoice_type}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={InvoiceTypeEnum.SALES}>Sales Invoice</option>
              <option value={InvoiceTypeEnum.PURCHASE}>Purchase Invoice</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select Invoice *
            </label>
            <select
              name={formData.invoice_type === InvoiceTypeEnum.SALES ? 'sales_invoice_id' : 'purchase_invoice_id'}
              value={formData.invoice_type === InvoiceTypeEnum.SALES ? formData.sales_invoice_id : formData.purchase_invoice_id}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select an invoice</option>
              {availableInvoices.map((invoice) => (
                <option key={invoice.id} value={invoice.id}>
                  {invoice.invoice_number} - {new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: invoice.currency?.code || 'USD',
                  }).format(invoice.total_amount || 0)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Amount *
            </label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              step="0.01"
              min="0"
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Payment Date *
            </label>
            <input
              type="date"
              name="payment_date"
              value={formData.payment_date}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Payment Method *
            </label>
            <select
              name="payment_method"
              value={formData.payment_method}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={PaymentMethodEnum.CASH}>Cash</option>
              <option value={PaymentMethodEnum.BANK_TRANSFER}>Bank Transfer</option>
              <option value={PaymentMethodEnum.CHECK}>Check</option>
              <option value={PaymentMethodEnum.CREDIT_CARD}>Credit Card</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reference Number
            </label>
            <input
              type="text"
              name="reference_number"
              value={formData.reference_number}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Check number, transaction ID, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Additional notes..."
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md disabled:opacity-50"
            >
              {loading ? 'Recording...' : 'Record Payment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePaymentModal;
