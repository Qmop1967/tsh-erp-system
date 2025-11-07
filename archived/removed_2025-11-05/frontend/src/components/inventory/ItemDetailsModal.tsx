import React, { useState, useEffect } from 'react';
import { X, Package, Edit, Save, Tag, DollarSign, Hash, Calendar, BarChart } from 'lucide-react';
import { migrationItemsApi } from '../../lib/api';
import type { Item } from '../../types';

interface ItemDetailsModalProps {
  item: Item | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (item: Item) => void;
  mode?: 'view' | 'edit';
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

export default function ItemDetailsModal({ item, isOpen, onClose, onUpdate, mode = 'view' }: ItemDetailsModalProps) {
  const [editMode, setEditMode] = useState(mode === 'edit');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    if (item) {
      setFormData({
        name_en: (item as any).name_en || '',
        name_ar: (item as any).name_ar || '',
        code: item.code || '',
        brand: item.brand || '',
        category_id: String((item as any).category_id || ''),
        selling_price_usd: String((item as any).selling_price_usd || ''),
        cost_price_usd: String((item as any).cost_price_usd || ''),
        stock_quantity: String((item as any).stock_quantity || 0),
        description: (item as any).description || '',
        is_active: (item as any).is_active || false
      });
    }
  }, [item]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev: any) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSave = async () => {
    if (!item) return;

    setLoading(true);
    try {
      const updatedData = {
        ...formData,
        selling_price_usd: parseFloat(formData.selling_price_usd),
        cost_price_usd: parseFloat(formData.cost_price_usd),
        stock_quantity: parseInt(formData.stock_quantity),
        category_id: parseInt(formData.category_id)
      };

      const response = await migrationItemsApi.updateItem(item.id, updatedData);
      onUpdate(response.data);
      setEditMode(false);
    } catch (error) {
      console.error('Error updating item:', error);
      alert('Failed to update item. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryName = (categoryId: string) => {
    const category = categories.find(c => c.id === categoryId);
    return category ? `${category.name} - ${category.name_ar}` : 'Unknown Category';
  };

  if (!isOpen || !item) return null;

  const profit = parseFloat(formData.selling_price_usd || '0') - parseFloat(formData.cost_price_usd || '0');
  const profitMargin = parseFloat(formData.selling_price_usd || '0') > 0 
    ? ((profit / parseFloat(formData.selling_price_usd || '0')) * 100).toFixed(1)
    : '0';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <Package className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                {editMode ? 'Edit Item' : 'Item Details'}
              </h2>
              <p className="text-sm text-gray-600">
                {editMode ? 'Modify item information' : 'View item information and statistics'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {!editMode && (
              <button
                onClick={() => setEditMode(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all flex items-center gap-2"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Information */}
            <div className="lg:col-span-2 space-y-6">
              {/* Basic Information */}
              <div className="bg-gray-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Tag className="w-5 h-5 text-blue-600" />
                  Basic Information
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Item Name (English)
                    </label>
                    {editMode ? (
                      <input
                        type="text"
                        name="name_en"
                        value={formData.name_en}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900 font-medium">
                        {formData.name_en || 'Not set'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Item Name (Arabic)
                    </label>
                    {editMode ? (
                      <input
                        type="text"
                        name="name_ar"
                        value={formData.name_ar}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        dir="rtl"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900 font-medium" dir="rtl">
                        {formData.name_ar || 'غير محدد'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Item Code/SKU
                    </label>
                    {editMode ? (
                      <div className="relative">
                        <Hash className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                          type="text"
                          name="code"
                          value={formData.code}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono"
                        />
                      </div>
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900 font-mono">
                        {formData.code || 'Not set'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Brand
                    </label>
                    {editMode ? (
                      <input
                        type="text"
                        name="brand"
                        value={formData.brand}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900">
                        {formData.brand || 'Not specified'}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    {editMode ? (
                      <select
                        name="category_id"
                        value={formData.category_id}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Select a category</option>
                        {categories.map(category => (
                          <option key={category.id} value={category.id}>
                            {category.name} - {category.name_ar}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900">
                        {getCategoryName(formData.category_id)}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Stock Quantity
                    </label>
                    {editMode ? (
                      <input
                        type="number"
                        name="stock_quantity"
                        value={formData.stock_quantity}
                        onChange={handleInputChange}
                        min="0"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900 font-medium">
                        {parseInt(formData.stock_quantity || '0').toLocaleString()} units
                      </p>
                    )}
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  {editMode ? (
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    />
                  ) : (
                    <div className="px-3 py-2 bg-white border rounded-lg text-gray-900 min-h-[80px]">
                      {formData.description || 'No description provided'}
                    </div>
                  )}
                </div>

                {editMode && (
                  <div className="mt-4 flex items-center">
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
                )}
              </div>

              {/* Pricing Information */}
              <div className="bg-green-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  Pricing & Profitability
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Selling Price (USD)
                    </label>
                    {editMode ? (
                      <div className="relative">
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                          type="number"
                          name="selling_price_usd"
                          value={formData.selling_price_usd}
                          onChange={handleInputChange}
                          step="0.01"
                          min="0"
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900 font-bold text-lg text-green-600">
                        ${parseFloat(formData.selling_price_usd || '0').toFixed(2)}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Cost Price (USD)
                    </label>
                    {editMode ? (
                      <div className="relative">
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                          type="number"
                          name="cost_price_usd"
                          value={formData.cost_price_usd}
                          onChange={handleInputChange}
                          step="0.01"
                          min="0"
                          className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                    ) : (
                      <p className="px-3 py-2 bg-white border rounded-lg text-gray-900 font-bold text-lg text-red-600">
                        ${parseFloat(formData.cost_price_usd || '0').toFixed(2)}
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Profit per Unit
                    </label>
                    <p className={`px-3 py-2 bg-white border rounded-lg font-bold text-lg ${
                      profit >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      ${profit.toFixed(2)}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Profit Margin
                    </label>
                    <p className={`px-3 py-2 bg-white border rounded-lg font-bold text-lg ${
                      parseFloat(profitMargin) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {profitMargin}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Status */}
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BarChart className="w-5 h-5 text-purple-600" />
                  Status & Metrics
                </h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Status:</span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      formData.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      <span className={`w-2 h-2 rounded-full mr-1 ${
                        formData.is_active ? 'bg-green-400' : 'bg-red-400'
                      }`}></span>
                      {formData.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Item ID:</span>
                    <span className="text-sm font-mono text-gray-900">#{item.id}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total Value:</span>
                    <span className="text-sm font-bold text-blue-600">
                      ${(parseFloat(formData.selling_price_usd || '0') * parseInt(formData.stock_quantity || '0')).toFixed(2)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total Cost:</span>
                    <span className="text-sm font-bold text-red-600">
                      ${(parseFloat(formData.cost_price_usd || '0') * parseInt(formData.stock_quantity || '0')).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Creation Info */}
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-gray-600" />
                  Item Information
                </h3>
                
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="text-gray-600">Created:</span>
                    <p className="text-gray-900 font-medium">
                      {(item as any).created_at ? new Date((item as any).created_at).toLocaleDateString() : 'Unknown'}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600">Last Updated:</span>
                    <p className="text-gray-900 font-medium">
                      {(item as any).updated_at ? new Date((item as any).updated_at).toLocaleDateString() : 'Unknown'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          {editMode && (
            <div className="flex gap-3 pt-6 border-t border-gray-200 mt-6">
              <button
                onClick={() => {
                  setEditMode(false);
                  // Reset form data to original values
                  if (item) {
                    setFormData({
                      name_en: (item as any).name_en || '',
                      name_ar: (item as any).name_ar || '',
                      code: item.code || '',
                      brand: item.brand || '',
                      category_id: String((item as any).category_id || ''),
                      selling_price_usd: String((item as any).selling_price_usd || ''),
                      cost_price_usd: String((item as any).cost_price_usd || ''),
                      stock_quantity: String((item as any).stock_quantity || 0),
                      description: (item as any).description || '',
                      is_active: (item as any).is_active || false
                    });
                  }
                }}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={loading}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
