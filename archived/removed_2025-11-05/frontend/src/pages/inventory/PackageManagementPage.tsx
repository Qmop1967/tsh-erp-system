import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { useDynamicTranslations } from '../../lib/dynamicTranslations';
import { useLanguageStore } from '../../stores/languageStore';
import {
  PackageCheck,
  Search,
  Plus,
  Edit,
  Trash2,
  Eye,
  Package
} from 'lucide-react';

interface PackageItem {
  id: number;
  package_code: string;
  package_name: string;
  description: string;
  total_items: number;
  package_status: 'active' | 'inactive';
  created_date: string;
  last_modified: string;
}

export default function PackageManagementPage() {
  const { language } = useLanguageStore();
  const { t } = useDynamicTranslations(language);
  const [packages, setPackages] = useState<PackageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data for demo
  useEffect(() => {
    setTimeout(() => {
      setPackages([
        {
          id: 1,
          package_code: 'PKG-001',
          package_name: 'حزمة أجهزة الكمبيوتر المحمولة',
          description: 'مجموعة من أجهزة الكمبيوتر المحمولة والإكسسوارات',
          total_items: 15,
          package_status: 'active',
          created_date: '2024-01-15',
          last_modified: '2024-01-20'
        },
        {
          id: 2,
          package_code: 'PKG-002', 
          package_name: 'حزمة الهواتف الذكية',
          description: 'مجموعة من الهواتف الذكية والشواحن',
          total_items: 25,
          package_status: 'active',
          created_date: '2024-01-10',
          last_modified: '2024-01-18'
        },
        {
          id: 3,
          package_code: 'PKG-003',
          package_name: 'حزمة الإكسسوارات',
          description: 'مجموعة متنوعة من الإكسسوارات التقنية',
          total_items: 8,
          package_status: 'inactive',
          created_date: '2024-01-05',
          last_modified: '2024-01-12'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredPackages = packages.filter(pkg =>
    pkg.package_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    pkg.package_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    pkg.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalPackages = packages.length;
  const activePackages = packages.filter(pkg => pkg.package_status === 'active').length;
  const inactivePackages = packages.filter(pkg => pkg.package_status === 'inactive').length;
  const totalItems = packages.reduce((sum, pkg) => sum + pkg.total_items, 0);

  const getStatusBadge = (status: string) => {
    return status === 'active' ? 
      <Badge variant="default">نشط</Badge> : 
      <Badge variant="secondary">غير نشط</Badge>;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <PackageCheck className="w-8 h-8" />
            {t.packageManagement}
          </h1>
          <p className="text-gray-600 mt-1">
            إدارة حزم المنتجات والمجموعات
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            إضافة حزمة جديدة
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">إجمالي الحزم</p>
                <p className="text-2xl font-bold text-gray-900">{totalPackages}</p>
              </div>
              <PackageCheck className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">الحزم النشطة</p>
                <p className="text-2xl font-bold text-green-600">{activePackages}</p>
              </div>
              <Package className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">الحزم غير النشطة</p>
                <p className="text-2xl font-bold text-red-600">{inactivePackages}</p>
              </div>
              <Package className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">إجمالي العناصر</p>
                <p className="text-2xl font-bold text-purple-600">{totalItems}</p>
              </div>
              <PackageCheck className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="البحث في الحزم..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Packages Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PackageCheck className="w-5 h-5" />
            قائمة الحزم
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
                    <th className="text-right py-2">رمز الحزمة</th>
                    <th className="text-right py-2">اسم الحزمة</th>
                    <th className="text-right py-2">الوصف</th>
                    <th className="text-right py-2">عدد العناصر</th>
                    <th className="text-right py-2">الحالة</th>
                    <th className="text-right py-2">تاريخ الإنشاء</th>
                    <th className="text-right py-2">آخر تعديل</th>
                    <th className="text-right py-2">الإجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredPackages.map((pkg) => (
                    <tr key={pkg.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 font-mono text-sm font-medium">
                        {pkg.package_code}
                      </td>
                      <td className="py-3 font-medium">{pkg.package_name}</td>
                      <td className="py-3 text-sm text-gray-600">{pkg.description}</td>
                      <td className="py-3 font-medium">{pkg.total_items}</td>
                      <td className="py-3">
                        {getStatusBadge(pkg.package_status)}
                      </td>
                      <td className="py-3 text-sm">{pkg.created_date}</td>
                      <td className="py-3 text-sm">{pkg.last_modified}</td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm" className="p-2">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="outline" size="sm" className="p-2">
                            <Edit className="w-4 h-4" />
                          </Button>
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