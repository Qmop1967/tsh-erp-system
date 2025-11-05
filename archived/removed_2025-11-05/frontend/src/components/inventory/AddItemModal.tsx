import React, { useState, useEffect } from 'react';
import { X, Package, Tag, DollarSign, Hash, FileText } from 'lucide-react';
import { migrationItemsApi } from '../../lib/api';
import type { Item } from '../../types';

interface AddItemModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (item: Item) => void;
}

interface ItemFormData {
  name_en: string;
  name_ar: string;
  code: string;
  brand: string;
  category_id: string;
  selling_price_usd: string;
  cost_price_usd: string;
  stock_quantity: string;
  description: string;
  is_active: boolean;
}

const categories = [
  { id: '1', name: 'Electronics', name_ar: 'الكترونيات' },
  { id: '2', name: 'Accessories', name_ar: 'إكسسوارات' },
  { id: '3', name: 'Computers', name_ar: 'حاسوب' },
  { id: '4', name: 'Mobile Phones', name_ar: 'هواتف محمولة' },
  { id: '5', name: 'Tablets', name_ar: 'أجهزة لوحية' },
  { id: '6', name: 'Gaming', name_ar: 'ألعاب' },
  { id: '7', name: 'Audio', name_ar: 'صوتيات' },
  { id: '8', name: 'Cables', name_ar: 'كوابل' }
];

export default function AddItemModal({ isOpen, onClose, onSuccess }: AddItemModalProps) {
  const [formData, setFormData] = useState<ItemFormData>({
    name_en: '',
    name_ar: '',
    code: '',
    brand: '',
    category_id: '',
    selling_price_usd: '',
    cost_price_usd: '',
    stock_quantity: '',
    description: '',
    is_active: true
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      // Generate a unique SKU when modal opens
      const timestamp = Date.now();
      const randomNum = Math.floor(Math.random() * 1000);
      setFormData(prev => ({
        ...prev,
        code: `ITM-${timestamp}-${randomNum}`
      }));
    }
  }, [isOpen]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name_en.trim()) newErrors.name_en = 'English name is required';
    if (!formData.code.trim()) newErrors.code = 'Item code is required';
    if (!formData.category_id) newErrors.category_id = 'Category is required';
    if (!formData.selling_price_usd || parseFloat(formData.selling_price_usd) <= 0) {
      newErrors.selling_price_usd = 'Valid selling price is required';
    }
    if (!formData.cost_price_usd || parseFloat(formData.cost_price_usd) <= 0) {
      newErrors.cost_price_usd = 'Valid cost price is required';
    }
    if (!formData.stock_quantity || parseInt(formData.stock_quantity) < 0) {
      newErrors.stock_quantity = 'Valid stock quantity is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      const itemData = {
        ...formData,
        selling_price_usd: parseFloat(formData.selling_price_usd),
        cost_price_usd: parseFloat(formData.cost_price_usd),
        stock_quantity: parseInt(formData.stock_quantity),
        category_id: parseInt(formData.category_id)
      };

      const response = await migrationItemsApi.createItem(itemData);
      onSuccess(response.data);
      handleClose();
    } catch (error) {
      console.error('Error creating item:', error);
      alert('Failed to create item. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name_en: '',
      name_ar: '',
      code: '',
      brand: '',
      category_id: '',
      selling_price_usd: '',
      cost_price_usd: '',
      stock_quantity: '',
      description: '',
      is_active: true
    });
    setErrors({});
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Package className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900" data-testid="modal-title">Add New Inventory Item</h2>
              <p className="text-sm text-gray-600">Create a new item in your inventory</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            data-testid="close-modal"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Tag className="w-5 h-5 text-blue-600" />
              Basic Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Item Name (English) *
                </label>
                <input
                  type="text"
                  name="name_en"
                  value={formData.name_en}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                    errors.name_en ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Enter item name in English"
                  data-testid="item-name-input"
                />
                {errors.name_en && <p className="text-red-500 text-sm mt-1">{errors.name_en}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Item Name (Arabic)
                </label>
                <input
                  type="text"
                  name="name_ar"
                  value={formData.name_ar}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="أدخل اسم العنصر بالعربية"
                  dir="rtl"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Item Code/SKU *
                </label>
                <div className="relative">
                  <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    name="code"
                    value={formData.code}
                    onChange={handleInputChange}
                    className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      errors.code ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="ITM-123456"
                    data-testid="item-sku-input"
                  />
                </div>
                {errors.code && <p className="text-red-500 text-sm mt-1">{errors.code}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brand
                </label>
                <input
                  type="text"
                  name="brand"
                  value={formData.brand}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter brand name"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleInputChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                  errors.category_id ? 'border-red-300' : 'border-gray-300'
                }`}
                data-testid="item-category-select"
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category.id} value={category.id}>
                    {category.name} - {category.name_ar}
                  </option>
                ))}
              </select>
              {errors.category_id && <p className="text-red-500 text-sm mt-1">{errors.category_id}</p>}
            </div>
          </div>

          {/* Pricing Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-green-600" />
              Pricing Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selling Price (USD) *
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="number"
                    name="selling_price_usd"
                    value={formData.selling_price_usd}
                    onChange={handleInputChange}
                    step="0.01"
                    min="0"
                    className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      errors.selling_price_usd ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="0.00"
                    data-testid="item-price-input"
                  />
                </div>
                {errors.selling_price_usd && <p className="text-red-500 text-sm mt-1">{errors.selling_price_usd}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cost Price (USD) *
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="number"
                    name="cost_price_usd"
                    value={formData.cost_price_usd}
                    onChange={handleInputChange}
                    step="0.01"
                    min="0"
                    className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      errors.cost_price_usd ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="0.00"
                  />
                </div>
                {errors.cost_price_usd && <p className="text-red-500 text-sm mt-1">{errors.cost_price_usd}</p>}
              </div>
            </div>
          </div>

          {/* Stock Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Package className="w-5 h-5 text-purple-600" />
              Stock Information
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Initial Stock Quantity *
              </label>
              <input
                type="number"
                name="stock_quantity"
                value={formData.stock_quantity}
                onChange={handleInputChange}
                min="0"
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                  errors.stock_quantity ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="0"
                data-testid="item-quantity-input"
              />
              {errors.stock_quantity && <p className="text-red-500 text-sm mt-1">{errors.stock_quantity}</p>}
            </div>
          </div>

          {/* Description */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-orange-600" />
              Additional Information
            </h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                placeholder="Enter item description..."
                data-testid="item-description-input"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-700">
                Item is active and available for sale
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
              data-testid="cancel-add-item"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              data-testid="save-add-item"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Package className="w-4 h-4" />
                  Create Item
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
