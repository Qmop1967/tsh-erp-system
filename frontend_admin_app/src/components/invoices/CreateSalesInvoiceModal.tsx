import React, { useState, useEffect } from 'react';
import { X, Plus } from 'lucide-react';
import { Customer, Item, InvoiceStatusEnum, InvoiceTypeEnum, PaymentTermsEnum } from '../../types';
import { customersApi, itemsApi, invoiceApi } from '../../lib/api';
import { useNotifications } from '../ui/NotificationProvider';

interface CreateSalesInvoiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CreateSalesInvoiceModal: React.FC<CreateSalesInvoiceModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { addNotification } = useNotifications();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [products, setProducts] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    customer_id: '',
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    payment_terms: PaymentTermsEnum.NET_30,
    notes: '',
    items: [
      {
        product_id: '',
        quantity: 1,
        unit_price: 0,
        description: '',
      },
    ],
  });

  useEffect(() => {
    if (isOpen) {
      fetchCustomers();
      fetchProducts();
    }
  }, [isOpen]);

  const fetchCustomers = async () => {
    try {
      const response = await customersApi.getCustomers();
      setCustomers(response.data.data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await itemsApi.getItems();
      setProducts(response.data.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [
        ...formData.items,
        {
          product_id: '',
          quantity: 1,
          unit_price: 0,
          description: '',
        },
      ],
    });
  };

  const removeItem = (index: number) => {
    setFormData({
      ...formData,
      items: formData.items.filter((_, i) => i !== index),
    });
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updatedItems = [...formData.items];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    
    // If product is selected, auto-fill unit price
    if (field === 'product_id' && value) {
      const selectedProduct = products.find(p => p.id === parseInt(value));
      if (selectedProduct) {
        updatedItems[index].unit_price = selectedProduct.sellingPriceUsd;
      }
    }
    
    setFormData({ ...formData, items: updatedItems });
  };

  const calculateSubtotal = () => {
    return formData.items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.customer_id || formData.items.length === 0) {
      alert('Please select a customer and add at least one item');
      return;
    }

    setLoading(true);
    try {
      const subtotal = calculateSubtotal();
      const invoiceData = {
        customer_id: parseInt(formData.customer_id),
        branch_id: 1, // Default branch
        invoice_date: formData.invoice_date,
        due_date: formData.due_date,
        currency_id: 1, // Default USD
        invoice_type: InvoiceTypeEnum.SALES,
        status: InvoiceStatusEnum.DRAFT,
        payment_terms: formData.payment_terms,
        subtotal,
        total_amount: subtotal, // For simplicity, no tax for now
        notes: formData.notes,
        items: formData.items.map(item => ({
          product_id: parseInt(item.product_id),
          quantity: item.quantity,
          unit_price: item.unit_price,
          line_total: item.quantity * item.unit_price,
          description: item.description,
        })),
      };

      await invoiceApi.createSalesInvoice(invoiceData);
      addNotification({
        type: 'success',
        title: 'Invoice Created',
        message: 'Sales invoice has been created successfully.',
      });
      onSuccess();
      onClose();
      // Reset form
      setFormData({
        customer_id: '',
        invoice_date: new Date().toISOString().split('T')[0],
        due_date: '',
        payment_terms: PaymentTermsEnum.NET_30,
        notes: '',
        items: [
          {
            product_id: '',
            quantity: 1,
            unit_price: 0,
            description: '',
          },
        ],
      });
    } catch (error) {
      console.error('Failed to create invoice:', error);
      addNotification({
        type: 'error',
        title: 'Error Creating Invoice',
        message: 'Failed to create sales invoice. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-gray-900">Create Sales Invoice</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Header Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Customer *
              </label>
              <select
                value={formData.customer_id}
                onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Select Customer</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.nameEn}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Terms
              </label>
              <select
                value={formData.payment_terms}
                onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value as PaymentTermsEnum })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={PaymentTermsEnum.IMMEDIATE}>Immediate</option>
                <option value={PaymentTermsEnum.NET_7}>Net 7 Days</option>
                <option value={PaymentTermsEnum.NET_15}>Net 15 Days</option>
                <option value={PaymentTermsEnum.NET_30}>Net 30 Days</option>
                <option value={PaymentTermsEnum.NET_60}>Net 60 Days</option>
                <option value={PaymentTermsEnum.NET_90}>Net 90 Days</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Invoice Date *
              </label>
              <input
                type="date"
                value={formData.invoice_date}
                onChange={(e) => setFormData({ ...formData, invoice_date: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Items */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Invoice Items</h3>
              <button
                type="button"
                onClick={addItem}
                className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg flex items-center space-x-1 text-sm"
              >
                <Plus className="h-4 w-4" />
                <span>Add Item</span>
              </button>
            </div>

            <div className="space-y-4">
              {formData.items.map((item, index) => (
                <div key={index} className="grid grid-cols-1 md:grid-cols-6 gap-4 p-4 border border-gray-200 rounded-lg">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Product
                    </label>
                    <select
                      value={item.product_id}
                      onChange={(e) => updateItem(index, 'product_id', e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Product</option>
                      {products.map((product) => (
                        <option key={product.id} value={product.id}>
                          {product.nameEn}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Quantity
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Unit Price
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={item.unit_price}
                      onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Total
                    </label>
                    <input
                      type="text"
                      value={`$${(item.quantity * item.unit_price).toFixed(2)}`}
                      readOnly
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50"
                    />
                  </div>

                  <div className="flex items-end">
                    {formData.items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeItem(index)}
                        className="text-red-600 hover:text-red-800 p-2"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter any additional notes..."
            />
          </div>

          {/* Total */}
          <div className="border-t pt-4">
            <div className="flex justify-end">
              <div className="text-right">
                <div className="text-lg font-semibold">
                  Subtotal: ${calculateSubtotal().toFixed(2)}
                </div>
                <div className="text-xl font-bold text-gray-900">
                  Total: ${calculateSubtotal().toFixed(2)}
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Invoice'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateSalesInvoiceModal;
