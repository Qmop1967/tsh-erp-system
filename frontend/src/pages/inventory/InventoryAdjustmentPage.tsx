import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { useDynamicTranslations } from '../../lib/dynamicTranslations';
import { useLanguageStore } from '../../stores/languageStore';
import {
  ClipboardList,
  Search,
  Plus,
  Edit,
  Trash2,
  Eye,
  TrendingUp,
  TrendingDown,
  Calendar
} from 'lucide-react';

interface InventoryAdjustment {
  id: number;
  reference_number: string;
  adjustment_date: string;
  reason: string;
  total_items: number;
  total_adjustment_value: number;
  status: 'draft' | 'posted' | 'cancelled';
  created_by: string;
  warehouse_name: string;
}

export default function InventoryAdjustmentPage() {
  const { language } = useLanguageStore();
  const { t } = useDynamicTranslations(language);
  const [adjustments, setAdjustments] = useState<InventoryAdjustment[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Mock data for demo
  useEffect(() => {
    setTimeout(() => {
      setAdjustments([
        {
          id: 1,
          reference_number: 'ADJ-2024-001',
          adjustment_date: '2024-01-15',
          reason: 'تسوية جرد دوري',
          total_items: 25,
          total_adjustment_value: -1250.50,
          status: 'posted',
          created_by: 'أحمد محمد',
          warehouse_name: 'المستودع الرئيسي'
        },
        {
          id: 2,
          reference_number: 'ADJ-2024-002',
          adjustment_date: '2024-01-20',
          reason: 'تلف بضاعة',
          total_items: 5,
          total_adjustment_value: -890.00,
          status: 'posted',
          created_by: 'فاطمة أحمد',
          warehouse_name: 'مستودع الفرع'
        },
        {
          id: 3,
          reference_number: 'ADJ-2024-003',
          adjustment_date: '2024-01-25',
          reason: 'استلام بضاعة إضافية',
          total_items: 12,
          total_adjustment_value: 2340.75,
          status: 'draft',
          created_by: 'محمد علي',
          warehouse_name: 'المستودع الرئيسي'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredAdjustments = adjustments.filter(adj => {
    const matchesSearch = adj.reference_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         adj.reason.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         adj.created_by.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || adj.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const totalAdjustments = adjustments.length;
  const postedAdjustments = adjustments.filter(adj => adj.status === 'posted').length;
  const draftAdjustments = adjustments.filter(adj => adj.status === 'draft').length;
  const totalValue = adjustments.reduce((sum, adj) => sum + adj.total_adjustment_value, 0);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'posted':
        return <Badge variant="default">مؤكد</Badge>;
      case 'draft':
        return <Badge variant="secondary">مسودة</Badge>;
      case 'cancelled':
        return <Badge variant="destructive">ملغي</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getValueDisplay = (value: number) => {
    const isPositive = value >= 0;
    return (
      <div className={`flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        ${Math.abs(value).toFixed(2)}
      </div>
    );
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <ClipboardList className="w-8 h-8" />
            {t.inventoryAdjustment}
          </h1>
          <p className="text-gray-600 mt-1">
            إدارة تعديلات المخزون والتسويات
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            تعديل جديد
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">إجمالي التعديلات</p>
                <p className="text-2xl font-bold text-gray-900">{totalAdjustments}</p>
              </div>
              <ClipboardList className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">مؤكدة</p>
                <p className="text-2xl font-bold text-green-600">{postedAdjustments}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">مسودات</p>
                <p className="text-2xl font-bold text-orange-600">{draftAdjustments}</p>
              </div>
              <Edit className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">إجمالي القيمة</p>
                <p className={`text-2xl font-bold ${totalValue >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${totalValue.toFixed(2)}
                </p>
              </div>
              {totalValue >= 0 ? 
                <TrendingUp className="w-8 h-8 text-green-600" /> : 
                <TrendingDown className="w-8 h-8 text-red-600" />
              }
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="البحث في التعديلات..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="all">جميع الحالات</option>
                <option value="posted">مؤكدة</option>
                <option value="draft">مسودة</option>
                <option value="cancelled">ملغية</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Adjustments Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ClipboardList className="w-5 h-5" />
            قائمة التعديلات
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-right py-2">رقم المرجع</th>
                    <th className="text-right py-2">التاريخ</th>
                    <th className="text-right py-2">السبب</th>
                    <th className="text-right py-2">المستودع</th>
                    <th className="text-right py-2">عدد العناصر</th>
                    <th className="text-right py-2">القيمة</th>
                    <th className="text-right py-2">المنشئ</th>
                    <th className="text-right py-2">الحالة</th>
                    <th className="text-right py-2">الإجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAdjustments.map((adjustment) => (
                    <tr key={adjustment.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 font-mono text-sm font-medium">
                        {adjustment.reference_number}
                      </td>
                      <td className="py-3 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        {adjustment.adjustment_date}
                      </td>
                      <td className="py-3">{adjustment.reason}</td>
                      <td className="py-3">{adjustment.warehouse_name}</td>
                      <td className="py-3 font-medium">{adjustment.total_items}</td>
                      <td className="py-3">
                        {getValueDisplay(adjustment.total_adjustment_value)}
                      </td>
                      <td className="py-3">{adjustment.created_by}</td>
                      <td className="py-3">
                        {getStatusBadge(adjustment.status)}
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm" className="p-2">
                            <Eye className="w-4 h-4" />
                          </Button>
                          {adjustment.status === 'draft' && (
                            <Button variant="outline" size="sm" className="p-2">
                              <Edit className="w-4 h-4" />
                            </Button>
                          )}
                          <Button variant="outline" size="sm" className="p-2 text-red-600">
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 