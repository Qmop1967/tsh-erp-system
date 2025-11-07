import { useState } from 'react';
import { CheckSquare, X, Edit, Trash2, Package, DollarSign, Tag, AlertTriangle } from 'lucide-react';
import type { Item } from '../../types';

interface BulkOperationsProps {
  selectedItems: Item[];
  onClose: () => void;
  onApply: (operation: string, data?: any) => void;
}

export default function BulkOperations({ selectedItems, onClose, onApply }: BulkOperationsProps) {
  const [activeTab, setActiveTab] = useState<'edit' | 'delete' | 'pricing'>('edit');
  const [bulkData, setBulkData] = useState({
    category_id: '',
    brand: '',
    is_active: true,
    price_adjustment: {
      type: 'percentage', // 'percentage' or 'fixed'
      value: '',
      operation: 'increase' // 'increase' or 'decrease'
    }
  });

  const handleBulkEdit = () => {
    const updateData: any = {};
    if (bulkData.category_id) updateData.category_id = parseInt(bulkData.category_id);
    if (bulkData.brand) updateData.brand = bulkData.brand;
    updateData.is_active = bulkData.is_active;

    onApply('bulk_edit', updateData);
  };

  const handleBulkPricing = () => {
    onApply('bulk_pricing', bulkData.price_adjustment);
  };

  const handleBulkDelete = () => {
    if (window.confirm(`Are you sure you want to delete ${selectedItems.length} items? This action cannot be undone.`)) {
      onApply('bulk_delete');
    }
  };

  const categories = [
    { id: '1', name: 'Electronics' },
    { id: '2', name: 'Accessories' },
    { id: '3', name: 'Computers' },
    { id: '4', name: 'Mobile Phones' },
    { id: '5', name: 'Tablets' },
    { id: '6', name: 'Gaming' },
    { id: '7', name: 'Audio' },
    { id: '8', name: 'Cables' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-blue-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <CheckSquare className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Bulk Operations</h2>
              <p className="text-sm text-gray-600">
                Apply changes to {selectedItems.length} selected item{selectedItems.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('edit')}
            className={`flex-1 px-6 py-4 font-medium text-sm flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'edit'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Edit className="w-4 h-4" />
            Bulk Edit
          </button>
          <button
            onClick={() => setActiveTab('pricing')}
            className={`flex-1 px-6 py-4 font-medium text-sm flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'pricing'
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <DollarSign className="w-4 h-4" />
            Price Update
          </button>
          <button
            onClick={() => setActiveTab('delete')}
            className={`flex-1 px-6 py-4 font-medium text-sm flex items-center justify-center gap-2 transition-colors ${
              activeTab === 'delete'
                ? 'text-red-600 border-b-2 border-red-600 bg-red-50'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
        </div>

        <div className="p-6">
          {/* Selected Items Preview */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Selected Items ({selectedItems.length})</h3>
            <div className="max-h-32 overflow-y-auto space-y-1">
              {selectedItems.slice(0, 5).map(item => (
                <div key={item.id} className="text-sm text-gray-600 flex items-center gap-2">
                  <Package className="w-3 h-3" />
                  {(item as any).name_en || 'Unnamed Item'} ({item.code})
                </div>
              ))}
              {selectedItems.length > 5 && (
                <div className="text-sm text-gray-500">
                  ... and {selectedItems.length - 5} more items
                </div>
              )}
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'edit' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Tag className="w-5 h-5 text-blue-600" />
                Bulk Edit Properties
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={bulkData.category_id}
                    onChange={(e) => setBulkData(prev => ({ ...prev, category_id: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Keep existing categories</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Brand
                  </label>
                  <input
                    type="text"
                    value={bulkData.brand}
                    onChange={(e) => setBulkData(prev => ({ ...prev, brand: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Leave empty to keep existing brands"
                  />
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={bulkData.is_active}
                  onChange={(e) => setBulkData(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Set all items as active
                </label>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={onClose}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBulkEdit}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium flex items-center justify-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Apply Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'pricing' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-green-600" />
                Bulk Price Update
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adjustment Type
                  </label>
                  <select
                    value={bulkData.price_adjustment.type}
                    onChange={(e) => setBulkData(prev => ({
                      ...prev,
                      price_adjustment: { ...prev.price_adjustment, type: e.target.value as 'percentage' | 'fixed' }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="percentage">Percentage</option>
                    <option value="fixed">Fixed Amount</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Operation
                  </label>
                  <select
                    value={bulkData.price_adjustment.operation}
                    onChange={(e) => setBulkData(prev => ({
                      ...prev,
                      price_adjustment: { ...prev.price_adjustment, operation: e.target.value as 'increase' | 'decrease' }
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="increase">Increase</option>
                    <option value="decrease">Decrease</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Value {bulkData.price_adjustment.type === 'percentage' ? '(%)' : '($)'}
                  </label>
                  <input
                    type="number"
                    value={bulkData.price_adjustment.value}
                    onChange={(e) => setBulkData(prev => ({
                      ...prev,
                      price_adjustment: { ...prev.price_adjustment, value: e.target.value }
                    }))}
                    step={bulkData.price_adjustment.type === 'percentage' ? '1' : '0.01'}
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={bulkData.price_adjustment.type === 'percentage' ? '10' : '5.00'}
                  />
                </div>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Preview</h4>
                <p className="text-sm text-blue-800">
                  {bulkData.price_adjustment.value ? (
                    <>
                      {bulkData.price_adjustment.operation === 'increase' ? 'Increase' : 'Decrease'} all prices by{' '}
                      {bulkData.price_adjustment.type === 'percentage' 
                        ? `${bulkData.price_adjustment.value}%`
                        : `$${bulkData.price_adjustment.value}`
                      }
                    </>
                  ) : (
                    'Enter a value to see preview'
                  )}
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={onClose}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBulkPricing}
                  disabled={!bulkData.price_adjustment.value}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 transition-all font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <DollarSign className="w-4 h-4" />
                  Update Prices
                </button>
              </div>
            </div>
          )}

          {activeTab === 'delete' && (
            <div className="space-y-6">
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-600" />
                <div>
                  <h3 className="text-lg font-semibold text-red-900">Danger Zone</h3>
                  <p className="text-sm text-red-700">
                    This action will permanently delete {selectedItems.length} items and cannot be undone.
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-gray-900">Items to be deleted:</h4>
                <div className="max-h-40 overflow-y-auto space-y-2 border border-gray-200 rounded-lg p-4">
                  {selectedItems.map(item => (
                    <div key={item.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center gap-2">
                        <Package className="w-4 h-4 text-gray-400" />
                        <span className="font-medium">{(item as any).name_en || 'Unnamed Item'}</span>
                        <span className="text-sm text-gray-500">({item.code})</span>
                      </div>
                      <span className="text-sm text-red-600 font-medium">
                        ${parseFloat((item as any).selling_price_usd || '0').toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={onClose}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 transition-all font-medium flex items-center justify-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete {selectedItems.length} Items
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
