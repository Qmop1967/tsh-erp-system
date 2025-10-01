import { useState, useEffect } from 'react';
import { 
  Package, Plus, Search, Download, Upload, RefreshCw, Grid, List, 
  Eye, Edit, ChevronLeft, ChevronRight, Filter, CheckSquare, MoreHorizontal,
  TrendingUp, AlertTriangle, Star, Zap
} from 'lucide-react';
import { migrationItemsApi } from '../../lib/api';
import type { Item } from '../../types';
import AddItemModal from '../../components/inventory/AddItemModal';
import ItemDetailsModal from '../../components/inventory/ItemDetailsModal';
import AdvancedFilters, { FilterValues } from '../../components/inventory/AdvancedFilters';
import BulkOperations from '../../components/inventory/BulkOperations';

export default function ItemsPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(50);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'price' | 'code'>('name');
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showBulkOperations, setShowBulkOperations] = useState(false);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [selectedItems, setSelectedItems] = useState<Item[]>([]);
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  
  // Advanced filters
  const [advancedFilters, setAdvancedFilters] = useState<FilterValues>({
    priceRange: { min: '', max: '' },
    stockRange: { min: '', max: '' },
    categories: [],
    brands: [],
    status: 'all',
    stockStatus: 'all'
  });

  // Fetch items using public migration endpoint
  const fetchItems = async () => {
    try {
      setLoading(true);
      console.log('🔄 Fetching items from API...');
      // Fetch items with max allowed limit of 1000
      const response = await migrationItemsApi.getItems({ limit: 1000 });
      console.log('📦 API Response:', response);
      console.log('📦 Response data type:', typeof response.data, Array.isArray(response.data));
      const itemsData = Array.isArray(response.data) ? response.data : [];
      console.log('✅ Fetched items:', itemsData.length, 'items');
      if (itemsData.length > 0) {
        console.log('📄 First item sample:', itemsData[0]);
      }
      setItems(itemsData);
    } catch (error) {
      console.error('❌ Error fetching items:', error);
      setItems([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  // Handler functions
  const handleAddItem = (newItem: Item) => {
    setItems(prev => [newItem, ...prev]);
    setShowAddModal(false);
  };

  const handleUpdateItem = (updatedItem: Item) => {
    setItems(prev => prev.map(item => item.id === updatedItem.id ? updatedItem : item));
    setSelectedItem(updatedItem);
  };

  const handleViewItem = (item: Item) => {
    setSelectedItem(item);
    setShowDetailsModal(true);
  };

  const handleEditItem = (item: Item) => {
    setSelectedItem(item);
    setShowDetailsModal(true);
  };

  const handleSelectItem = (item: Item) => {
    if (selectedItems.find(selected => selected.id === item.id)) {
      setSelectedItems(prev => prev.filter(selected => selected.id !== item.id));
    } else {
      setSelectedItems(prev => [...prev, item]);
    }
  };

  const handleSelectAll = () => {
    if (selectedItems.length === currentItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems([...currentItems]);
    }
  };

  const handleBulkOperation = (operation: string, data?: any) => {
    console.log('Bulk operation:', operation, data, 'on', selectedItems.length, 'items');
    // Here you would implement the actual bulk operations
    // For now, just close the modal and clear selection
    setShowBulkOperations(false);
    setSelectedItems([]);
    setIsSelectionMode(false);
  };

  const handleApplyAdvancedFilters = (filters: FilterValues) => {
    setAdvancedFilters(filters);
    setCurrentPage(1); // Reset to first page when filters change
  };

  const handleResetAdvancedFilters = () => {
    setAdvancedFilters({
      priceRange: { min: '', max: '' },
      stockRange: { min: '', max: '' },
      categories: [],
      brands: [],
      status: 'all',
      stockStatus: 'all'
    });
    setCurrentPage(1);
  };

  const handleExport = () => {
    // Export filtered items to CSV
    const csvContent = [
      ['Code', 'Name (EN)', 'Name (AR)', 'Brand', 'Category', 'Cost Price (USD)', 'Selling Price (USD)', 'Status'],
      ...filteredItems.map(item => [
        item.code,
        (item as any).name_en || '',
        (item as any).name_ar || '',
        item.brand || '',
        (item as any).category_id || '',
        (item as any).cost_price_usd || '0',
        (item as any).selling_price_usd || '0',
        (item as any).is_active ? 'Active' : 'Inactive'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `inventory_items_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  const handleImport = () => {
    alert('Import functionality: Upload CSV file to bulk import items. This feature will be implemented soon.');
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const filteredItems = items.filter(item => {
    // Basic search
    const matchesSearch =
      (item as any).name_en?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item as any).name_ar?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.brand?.toLowerCase().includes(searchTerm.toLowerCase());

    // Basic category filter
    const matchesCategory = selectedCategory === 'all' || (item as any).category_id?.toString() === selectedCategory;

    // Advanced filters
    const price = parseFloat((item as any).selling_price_usd || '0');
    const stock = parseInt((item as any).stock_quantity || '0');
    
    const matchesPriceRange = 
      (!advancedFilters.priceRange.min || price >= parseFloat(advancedFilters.priceRange.min)) &&
      (!advancedFilters.priceRange.max || price <= parseFloat(advancedFilters.priceRange.max));
    
    const matchesStockRange = 
      (!advancedFilters.stockRange.min || stock >= parseInt(advancedFilters.stockRange.min)) &&
      (!advancedFilters.stockRange.max || stock <= parseInt(advancedFilters.stockRange.max));
    
    const matchesCategories = 
      advancedFilters.categories.length === 0 || 
      advancedFilters.categories.includes((item as any).category_id?.toString());
    
    const matchesBrands = 
      advancedFilters.brands.length === 0 || 
      advancedFilters.brands.includes(item.brand || '');
    
    const matchesStatus = 
      advancedFilters.status === 'all' ||
      (advancedFilters.status === 'active' && (item as any).is_active) ||
      (advancedFilters.status === 'inactive' && !(item as any).is_active);
    
    const matchesStockStatus = 
      advancedFilters.stockStatus === 'all' ||
      (advancedFilters.stockStatus === 'in-stock' && stock > 10) ||
      (advancedFilters.stockStatus === 'low-stock' && stock >= 1 && stock <= 10) ||
      (advancedFilters.stockStatus === 'out-of-stock' && stock === 0);

    return matchesSearch && matchesCategory && matchesPriceRange && matchesStockRange && 
           matchesCategories && matchesBrands && matchesStatus && matchesStockStatus;
  });

  // Sort items
  const sortedItems = [...filteredItems].sort((a, b) => {
    if (sortBy === 'name') {
      return ((a as any).name_en || '').localeCompare((b as any).name_en || '');
    } else if (sortBy === 'price') {
      return parseFloat((b as any).selling_price_usd || '0') - parseFloat((a as any).selling_price_usd || '0');
    } else {
      return (a.code || '').localeCompare(b.code || '');
    }
  });

  // Pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentItems = sortedItems.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(sortedItems.length / itemsPerPage);

  const totalItems = items.length;
  const activeItems = items.filter(item => (item as any).is_active).length;
  const totalValue = items.reduce((sum, item) => sum + parseFloat((item as any).selling_price_usd || '0'), 0);
  const lowStockItems = 3; // This would come from actual stock data

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading inventory items...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <div className="p-3 bg-blue-600 rounded-xl shadow-lg">
                  <Package className="w-8 h-8 text-white" />
                </div>
                Inventory Items
              </h1>
              <p className="text-gray-600 mt-2">Manage your product catalog and inventory</p>
            </div>
            <div className="flex gap-3">
              {/* Selection Mode Toggle */}
              {filteredItems.length > 0 && (
                <button 
                  onClick={() => {
                    setIsSelectionMode(!isSelectionMode);
                    setSelectedItems([]);
                  }}
                  className={`px-4 py-2 border rounded-lg transition-all flex items-center gap-2 shadow-sm ${
                    isSelectionMode 
                      ? 'bg-blue-600 text-white border-blue-600' 
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <CheckSquare className="w-4 h-4" />
                  {isSelectionMode ? 'Exit Selection' : 'Select Items'}
                </button>
              )}
              
              {/* Bulk Operations Button */}
              {selectedItems.length > 0 && (
                <button 
                  onClick={() => setShowBulkOperations(true)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all flex items-center gap-2 shadow-sm"
                >
                  <Edit className="w-4 h-4" />
                  Bulk Actions ({selectedItems.length})
                </button>
              )}
              
              <button 
                onClick={handleExport}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all flex items-center gap-2 shadow-sm"
                title="Export filtered items to CSV"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
              <button 
                onClick={handleImport}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all flex items-center gap-2 shadow-sm"
                title="Import items from CSV"
              >
                <Upload className="w-4 h-4" />
                Import
              </button>
              <button 
                onClick={() => setShowAddModal(true)}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all flex items-center gap-2 shadow-lg"
              >
                <Plus className="w-5 h-5" />
                Add New Item
              </button>
            </div>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total Items</p>
                  <p className="text-3xl font-bold text-gray-900">{totalItems}</p>
                  <p className="text-xs text-green-600 mt-1">↑ 12% from last month</p>
                </div>
                <div className="p-4 bg-blue-100 rounded-lg">
                  <Package className="w-8 h-8 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Active Items</p>
                  <p className="text-3xl font-bold text-gray-900">{activeItems}</p>
                  <p className="text-xs text-gray-500 mt-1">{((activeItems/totalItems)*100).toFixed(1)}% of total</p>
                </div>
                <div className="p-4 bg-green-100 rounded-lg">
                  <Package className="w-8 h-8 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total Value</p>
                  <p className="text-3xl font-bold text-gray-900">${totalValue.toFixed(2)}</p>
                  <p className="text-xs text-green-600 mt-1">↑ 8.5% this week</p>
                </div>
                <div className="p-4 bg-purple-100 rounded-lg">
                  <Package className="w-8 h-8 text-purple-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Low Stock</p>
                  <p className="text-3xl font-bold text-gray-900">{lowStockItems}</p>
                  <p className="text-xs text-orange-600 mt-1">Needs attention</p>
                </div>
                <div className="p-4 bg-orange-100 rounded-lg">
                  <Package className="w-8 h-8 text-orange-600" />
                </div>
              </div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by name, code, brand, or description..."
                  className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <select
                className="px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="all">All Categories</option>
                <option value="1">Electronics</option>
                <option value="2">Accessories</option>
                <option value="3">Computers</option>
                <option value="4">Mobile Phones</option>
                <option value="5">Tablets</option>
              </select>

              <select
                className="px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="name">Sort by Name</option>
                <option value="price">Sort by Price</option>
                <option value="code">Sort by Code</option>
              </select>

              {/* Advanced Filters Button */}
              <button
                onClick={() => setShowAdvancedFilters(true)}
                className={`px-4 py-3 rounded-lg border transition-all flex items-center gap-2 ${
                  Object.values(advancedFilters).some(v => 
                    Array.isArray(v) ? v.length > 0 : (typeof v === 'object' ? Object.values(v).some(val => val) : v !== 'all')
                  )
                    ? 'bg-purple-600 text-white border-purple-600'
                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Filter className="w-4 h-4" />
                Filters
                {Object.values(advancedFilters).some(v => 
                  Array.isArray(v) ? v.length > 0 : (typeof v === 'object' ? Object.values(v).some(val => val) : v !== 'all')
                ) && (
                  <span className="bg-white text-purple-600 text-xs px-2 py-1 rounded-full font-medium">
                    Active
                  </span>
                )}
              </button>

              <div className="flex gap-2">
                {/* Select All in Selection Mode */}
                {isSelectionMode && (
                  <button
                    onClick={handleSelectAll}
                    className={`p-3 rounded-lg border transition-all ${
                      selectedItems.length === currentItems.length && currentItems.length > 0
                        ? 'bg-green-600 text-white border-green-600'
                        : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                    }`}
                    title={selectedItems.length === currentItems.length ? 'Deselect All' : 'Select All'}
                  >
                    <CheckSquare className="w-5 h-5" />
                  </button>
                )}
                
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-3 rounded-lg border transition-all ${
                    viewMode === 'list'
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <List className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-3 rounded-lg border transition-all ${
                    viewMode === 'grid'
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <Grid className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Info */}
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            Debug: Total items: {items.length} | Filtered: {filteredItems.length} | Current page items: {currentItems.length} | View mode: {viewMode}
          </p>
        </div>

        {/* Items Display - Zoho-style Grid */}
        {filteredItems.length === 0 ? (
          <div className="bg-white rounded-xl shadow-md p-12 text-center border border-gray-100">
            <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No items found</h3>
            <p className="text-gray-600 mb-6">
              {items.length === 0 ? 'Start by adding your first item.' : 'Try adjusting your search or filters.'}
            </p>
            <button 
              onClick={() => setShowAddModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all inline-flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              Add Your First Item
            </button>
          </div>
        ) : (
          /* Zoho-style Product Cards Grid */
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-6">
            {currentItems.map((item) => (
              <div
                key={item.id}
                className="relative bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-200 cursor-pointer group overflow-hidden"
              >
                {/* Product Image Area */}
                <div className="aspect-square bg-gray-50 flex items-center justify-center border-b border-gray-100 group-hover:bg-gray-100 transition-colors">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center shadow-md">
                    <Package className="w-10 h-10 text-white" />
                  </div>
                </div>

                {/* Product Info */}
                <div className="p-3">
                  {/* Product Name */}
                  <h3 className="text-sm font-medium text-gray-900 mb-2 h-10 overflow-hidden leading-tight" style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {(item as any).name_en || 'Unnamed Product'}
                  </h3>
                  
                  {/* SKU */}
                  <p className="text-xs text-gray-500 mb-3 font-mono">
                    SKU: {item.code}
                  </p>

                  {/* Pricing */}
                  <div className="space-y-1 mb-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">Selling Price:</span>
                      <span className="text-sm font-bold text-gray-900">
                        ${parseFloat((item as any).selling_price_usd || '0').toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-gray-500">Cost Price:</span>
                      <span className="text-xs text-gray-600">
                        ${parseFloat((item as any).cost_price_usd || '0').toFixed(2)}
                      </span>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div className="flex justify-center">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      (item as any).is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      <span className={`w-2 h-2 rounded-full mr-1 ${
                        (item as any).is_active ? 'bg-green-400' : 'bg-red-400'
                      }`}></span>
                      {(item as any).is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                {/* Hover Actions Overlay */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => handleViewItem(item)}
                      className="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-110"
                      title="View Details"
                    >
                      <Eye className="w-4 h-4 text-blue-600" />
                    </button>
                    <button 
                      onClick={() => handleEditItem(item)}
                      className="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-110"
                      title="Edit Item"
                    >
                      <Edit className="w-4 h-4 text-green-600" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex items-center justify-between bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
            <div className="text-sm text-gray-700">
              Showing <span className="font-semibold">{indexOfFirstItem + 1}</span> to{' '}
              <span className="font-semibold">{Math.min(indexOfLastItem, sortedItems.length)}</span> of{' '}
              <span className="font-semibold">{sortedItems.length}</span> items
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </button>
              <div className="flex gap-1">
                {[...Array(totalPages)].map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                      currentPage === i + 1
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
              >
                Next
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showAddModal && (
        <AddItemModal
          onClose={() => setShowAddModal(false)}
          onSuccess={handleAddItem}
        />
      )}

      {showDetailsModal && selectedItem && (
        <ItemDetailsModal
          item={selectedItem}
          onClose={() => {
            setShowDetailsModal(false);
            setSelectedItem(null);
          }}
          onUpdate={handleUpdateItem}
        />
      )}

      {showAdvancedFilters && (
        <AdvancedFilters
          onClose={() => setShowAdvancedFilters(false)}
          onApply={handleApplyAdvancedFilters}
          onReset={handleResetAdvancedFilters}
          currentFilters={advancedFilters}
        />
      )}

      {showBulkOperations && (
        <BulkOperations
          selectedItems={selectedItems}
          onClose={() => setShowBulkOperations(false)}
          onComplete={handleBulkOperation}
        />
      )}

      {/* Modals */}
      <AddItemModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={handleAddItem}
      />

      <ItemDetailsModal
        item={selectedItem}
        isOpen={showDetailsModal}
        onClose={() => {
          setShowDetailsModal(false);
          setSelectedItem(null);
        }}
        onUpdate={handleUpdateItem}
        mode="view"
      />

      <AdvancedFilters
        isOpen={showAdvancedFilters}
        onClose={() => setShowAdvancedFilters(false)}
        onApply={handleApplyAdvancedFilters}
        onReset={handleResetAdvancedFilters}
      />

      {selectedItems.length > 0 && (
        <BulkOperations
          selectedItems={selectedItems}
          onClose={() => setShowBulkOperations(false)}
          onApply={handleBulkOperation}
        />
      )}
    </div>
  );
}