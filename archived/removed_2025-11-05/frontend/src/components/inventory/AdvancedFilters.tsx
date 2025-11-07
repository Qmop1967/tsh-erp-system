import { useState } from 'react';
import { Filter, X, DollarSign, Package, Tag, Calendar } from 'lucide-react';

interface AdvancedFiltersProps {
  isOpen: boolean;
  onClose: () => void;
  onApply: (filters: FilterValues) => void;
  onReset: () => void;
}

export interface FilterValues {
  priceRange: {
    min: string;
    max: string;
  };
  stockRange: {
    min: string;
    max: string;
  };
  categories: string[];
  brands: string[];
  status: 'all' | 'active' | 'inactive';
  stockStatus: 'all' | 'in-stock' | 'low-stock' | 'out-of-stock';
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

const popularBrands = [
  'Apple', 'Samsung', 'Sony', 'HP', 'Dell', 'Lenovo', 'Canon', 'Nikon', 'Microsoft', 'Google'
];

export default function AdvancedFilters({ isOpen, onClose, onApply, onReset }: AdvancedFiltersProps) {
  const [filters, setFilters] = useState<FilterValues>({
    priceRange: { min: '', max: '' },
    stockRange: { min: '', max: '' },
    categories: [],
    brands: [],
    status: 'all',
    stockStatus: 'all'
  });

  const handleInputChange = (field: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNestedInputChange = (parent: string, field: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [parent]: {
        ...(prev as any)[parent],
        [field]: value
      }
    }));
  };

  const handleArrayToggle = (field: 'categories' | 'brands', value: string) => {
    setFilters(prev => ({
      ...prev,
      [field]: prev[field].includes(value)
        ? prev[field].filter(item => item !== value)
        : [...prev[field], value]
    }));
  };

  const handleApply = () => {
    onApply(filters);
    onClose();
  };

  const handleReset = () => {
    const resetFilters: FilterValues = {
      priceRange: { min: '', max: '' },
      stockRange: { min: '', max: '' },
      categories: [],
      brands: [],
      status: 'all',
      stockStatus: 'all'
    };
    setFilters(resetFilters);
    onReset();
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.priceRange.min || filters.priceRange.max) count++;
    if (filters.stockRange.min || filters.stockRange.max) count++;
    if (filters.categories.length > 0) count++;
    if (filters.brands.length > 0) count++;
    if (filters.status !== 'all') count++;
    if (filters.stockStatus !== 'all') count++;
    return count;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-pink-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-600 rounded-lg">
              <Filter className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Advanced Filters</h2>
              <p className="text-sm text-gray-600">
                {getActiveFiltersCount() > 0 
                  ? `${getActiveFiltersCount()} filter${getActiveFiltersCount() !== 1 ? 's' : ''} active`
                  : 'Refine your search with advanced options'
                }
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

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Price Range */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-green-600" />
                Price Range (USD)
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Min Price
                  </label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="number"
                      value={filters.priceRange.min}
                      onChange={(e) => handleNestedInputChange('priceRange', 'min', e.target.value)}
                      step="0.01"
                      min="0"
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="0.00"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Price
                  </label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="number"
                      value={filters.priceRange.max}
                      onChange={(e) => handleNestedInputChange('priceRange', 'max', e.target.value)}
                      step="0.01"
                      min="0"
                      className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="1000.00"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Stock Range */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Package className="w-5 h-5 text-blue-600" />
                Stock Quantity
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Min Stock
                  </label>
                  <input
                    type="number"
                    value={filters.stockRange.min}
                    onChange={(e) => handleNestedInputChange('stockRange', 'min', e.target.value)}
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Stock
                  </label>
                  <input
                    type="number"
                    value={filters.stockRange.max}
                    onChange={(e) => handleNestedInputChange('stockRange', 'max', e.target.value)}
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="1000"
                  />
                </div>
              </div>
            </div>

            {/* Categories */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Tag className="w-5 h-5 text-orange-600" />
                Categories
              </h3>
              <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                {categories.map(category => (
                  <label key={category.id} className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.categories.includes(category.id)}
                      onChange={() => handleArrayToggle('categories', category.id)}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">{category.name}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Brands */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Tag className="w-5 h-5 text-indigo-600" />
                Brands
              </h3>
              <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
                {popularBrands.map(brand => (
                  <label key={brand} className="flex items-center space-x-2 p-2 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.brands.includes(brand)}
                      onChange={() => handleArrayToggle('brands', brand)}
                      className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-700">{brand}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Status Filters */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-gray-600" />
                Item Status
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Active Status
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleInputChange('status', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="all">All Items</option>
                    <option value="active">Active Only</option>
                    <option value="inactive">Inactive Only</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stock Status
                  </label>
                  <select
                    value={filters.stockStatus}
                    onChange={(e) => handleInputChange('stockStatus', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="all">All Stock Levels</option>
                    <option value="in-stock">In Stock (&gt;10)</option>
                    <option value="low-stock">Low Stock (1-10)</option>
                    <option value="out-of-stock">Out of Stock (0)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Quick Presets */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Quick Presets</h3>
              <div className="grid grid-cols-1 gap-2">
                <button
                  onClick={() => setFilters({
                    ...filters,
                    priceRange: { min: '0', max: '100' },
                    stockStatus: 'in-stock'
                  })}
                  className="p-3 text-left bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                >
                  <div className="font-medium text-blue-900">Budget Items</div>
                  <div className="text-sm text-blue-600">Under $100, in stock</div>
                </button>
                <button
                  onClick={() => setFilters({
                    ...filters,
                    stockStatus: 'low-stock'
                  })}
                  className="p-3 text-left bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors"
                >
                  <div className="font-medium text-orange-900">Low Stock Alert</div>
                  <div className="text-sm text-orange-600">Items needing restock</div>
                </button>
                <button
                  onClick={() => setFilters({
                    ...filters,
                    priceRange: { min: '500', max: '' },
                    categories: ['1', '3'] // Electronics & Computers
                  })}
                  className="p-3 text-left bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
                >
                  <div className="font-medium text-green-900">Premium Tech</div>
                  <div className="text-sm text-green-600">High-end electronics & computers</div>
                </button>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-6 border-t border-gray-200 mt-6">
            <button
              onClick={handleReset}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
            >
              Reset All
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleApply}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 transition-all font-medium flex items-center justify-center gap-2"
            >
              <Filter className="w-4 h-4" />
              Apply Filters ({getActiveFiltersCount()})
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
