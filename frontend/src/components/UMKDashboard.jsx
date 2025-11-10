import React, { useState, useEffect } from 'react';
import {
  Search, Filter, Plus, Edit, Trash2, Upload, Download,
  RefreshCw, Save, X, ChevronDown, ChevronUp,
  MapPin, Calendar, TrendingUp, Users, AlertCircle,
  CheckSquare, Square
} from 'lucide-react';

const UMKDashboard = () => {
  const [umkData, setUMKData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedProvince, setSelectedProvince] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [stats, setStats] = useState(null);
  const [provinces, setProvinces] = useState([]);
  const [years, setYears] = useState([]);

  // Form states
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    kabupaten_kota: '',
    provinsi: '',
    umk: '',
    tahun: new Date().getFullYear(),
    region: '',
    is_active: true,
    source: 'Manual Entry',
    notes: ''
  });

  // Filter states
  const [showFilters, setShowFilters] = useState(false);

  const pageSize = 20;

  useEffect(() => {
    fetchData();
    fetchStats();
    fetchFilters();
  }, [search, selectedProvince, selectedYear, selectedStatus, currentPage]);

  useEffect(() => {
    if (selectedItems.size > 0) {
      setShowBulkActions(true);
    } else {
      setShowBulkActions(false);
    }
  }, [selectedItems]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      });

      if (search) params.append('search', search);
      if (selectedProvince) params.append('provinsi', selectedProvince);
      if (selectedYear) params.append('tahun', selectedYear);
      if (selectedStatus) params.append('is_active', selectedStatus === 'active');

      const response = await fetch(`/api/admin/umk?${params}`);
      const data = await response.json();

      setUMKData(data.data || []);
      setTotalPages(Math.ceil(data.total / pageSize));
    } catch (error) {
      console.error('Error fetching UMK data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/admin/umk/stats/overview');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchFilters = async () => {
    try {
      const [provincesRes, yearsRes] = await Promise.all([
        fetch('/api/admin/umk/filters/provinces'),
        fetch('/api/admin/umk/filters/years')
      ]);

      const provincesData = await provincesRes.json();
      const yearsData = await yearsRes.json();

      setProvinces(provincesData.provinces || []);
      setYears(yearsData.years || []);
    } catch (error) {
      console.error('Error fetching filters:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingItem
        ? `/api/admin/umk/${editingItem.id}`
        : '/api/admin/umk';

      const method = editingItem ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        fetchData();
        fetchStats();
        resetForm();
        alert(editingItem ? 'UMK updated successfully!' : 'UMK created successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error saving UMK:', error);
      alert('Error saving UMK');
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData({
      kabupaten_kota: item.kabupaten_kota,
      provinsi: item.provinsi,
      umk: item.umk,
      tahun: item.tahun,
      region: item.region || '',
      is_active: item.is_active,
      source: item.source || 'Manual Entry',
      notes: item.notes || ''
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this UMK data?')) return;

    try {
      const response = await fetch(`/api/admin/umk/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchData();
        fetchStats();
        alert('UMK deleted successfully!');
      } else {
        alert('Error deleting UMK');
      }
    } catch (error) {
      console.error('Error deleting UMK:', error);
      alert('Error deleting UMK');
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Are you sure you want to delete ${selectedItems.size} items?`)) return;

    try {
      const response = await fetch('/api/admin/umk/bulk-delete', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ umk_ids: Array.from(selectedItems) }),
      });

      if (response.ok) {
        setSelectedItems(new Set());
        fetchData();
        fetchStats();
        alert('Bulk delete completed successfully!');
      } else {
        alert('Error during bulk delete');
      }
    } catch (error) {
      console.error('Error during bulk delete:', error);
      alert('Error during bulk delete');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('created_by', 'admin');

    try {
      console.log('Uploading file:', file.name);
      const response = await fetch('/api/admin/umk/import-csv', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      console.log('Upload response:', result);

      if (response.ok) {
        if (result.success) {
          alert(`✅ Import completed: ${result.success_count} successful, ${result.error_count} errors`);
          fetchData();
          fetchStats();

          // Reset file input
          event.target.value = '';
        } else {
          alert(`❌ Import failed: ${result.errors?.join(', ') || 'Unknown error'}`);
        }
      } else {
        console.error('Server response error:', response.status, result);
        alert(`❌ Import failed: ${result.detail || 'Server error'}`);
      }
    } catch (error) {
      console.error('Error importing CSV:', error);
      alert(`❌ Network error: ${error.message}`);
    }
  };

  const handleExport = async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (selectedProvince) params.append('provinsi', selectedProvince);
      if (selectedYear) params.append('tahun', selectedYear);
      if (selectedStatus) params.append('is_active', selectedStatus === 'active');

      const response = await fetch(`/api/admin/umk/export/csv?${params}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'umk_data_export.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Error exporting data');
    }
  };

  const resetForm = () => {
    setFormData({
      kabupaten_kota: '',
      provinsi: '',
      umk: '',
      tahun: new Date().getFullYear(),
      region: '',
      is_active: true,
      source: 'Manual Entry',
      notes: ''
    });
    setEditingItem(null);
    setShowForm(false);
  };

  const toggleItemSelection = (id) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedItems(newSelected);
  };

  const toggleAllSelection = () => {
    if (selectedItems.size === umkData.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(umkData.map(item => item.id)));
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount || 0);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">UMK Management Dashboard</h1>
          <p className="text-gray-600 mt-2">Manage Indonesian Minimum Wage (UMK/UMP) Data</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowForm(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add UMK</span>
          </button>
          <button
            onClick={fetchData}
            className="btn btn-outline flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Total Records</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total_records}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckSquare className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.active_records}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <X className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Inactive</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.inactive_records}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg border">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <MapPin className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Provinces</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.top_provinces?.length || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white p-6 rounded-lg border mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by city, province, or region..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn btn-outline flex items-center space-x-2"
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            <label className="btn btn-outline flex items-center space-x-2 cursor-pointer">
              <Upload className="w-4 h-4" />
              <span>Import CSV</span>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>

            <button
              onClick={handleExport}
              className="btn btn-outline flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>

        {/* Expandable Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-4 gap-4">
            <select
              value={selectedProvince}
              onChange={(e) => setSelectedProvince(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Provinces</option>
              {provinces.map(province => (
                <option key={province} value={province}>{province}</option>
              ))}
            </select>

            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Years</option>
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>

            <button
              onClick={() => {
                setSearch('');
                setSelectedProvince('');
                setSelectedYear('');
                setSelectedStatus('');
              }}
              className="btn btn-outline"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>

      {/* Bulk Actions */}
      {showBulkActions && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-blue-800 font-medium">
              {selectedItems.size} item{selectedItems.size > 1 ? 's' : ''} selected
            </span>
            <button
              onClick={handleBulkDelete}
              className="btn btn-danger text-sm"
            >
              Delete Selected
            </button>
          </div>
          <button
            onClick={() => setSelectedItems(new Set())}
            className="text-blue-600 hover:text-blue-800"
          >
            Clear Selection
          </button>
        </div>
      )}

      {/* Data Table */}
      <div className="bg-white rounded-lg border overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading UMK data...</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedItems.size === umkData.length && umkData.length > 0}
                        onChange={toggleAllSelection}
                        className="rounded border-gray-300"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      City/Regency
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Province
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      UMK (Monthly)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Year
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {umkData.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedItems.has(item.id)}
                          onChange={() => toggleItemSelection(item.id)}
                          className="rounded border-gray-300"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{item.kabupaten_kota}</div>
                        {item.region && (
                          <div className="text-xs text-gray-500">{item.region}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.provinsi}</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {formatCurrency(item.umk)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">{item.tahun}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          item.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {item.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEdit(item)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(item.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-white px-6 py-3 border-t flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, umkData.length)} of {totalPages * pageSize} results
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="btn btn-outline disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <span className="px-3 py-1 text-sm text-gray-700">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="btn btn-outline disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Add/Edit Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                {editingItem ? 'Edit UMK Data' : 'Add New UMK Data'}
              </h2>
              <button
                onClick={resetForm}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City/Regency *
                </label>
                <input
                  type="text"
                  required
                  value={formData.kabupaten_kota}
                  onChange={(e) => setFormData({...formData, kabupaten_kota: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Jakarta, Bandung, Surabaya"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Province *
                </label>
                <input
                  type="text"
                  required
                  value={formData.provinsi}
                  onChange={(e) => setFormData({...formData, provinsi: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., DKI Jakarta, Jawa Barat"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  UMK Amount (Monthly) *
                </label>
                <input
                  type="number"
                  required
                  value={formData.umk}
                  onChange={(e) => setFormData({...formData, umk: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., 5000000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Year *
                </label>
                <input
                  type="number"
                  required
                  value={formData.tahun}
                  onChange={(e) => setFormData({...formData, tahun: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="2020"
                  max="2030"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Region
                </label>
                <input
                  type="text"
                  value={formData.region}
                  onChange={(e) => setFormData({...formData, region: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., jabodetabek, jawa_barat"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.value === 'true'})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Source
                </label>
                <input
                  type="text"
                  value={formData.source}
                  onChange={(e) => setFormData({...formData, source: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Kemenaker RI"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Additional notes..."
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={resetForm}
                  className="btn btn-outline"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <Save className="w-4 h-4" />
                  <span>{editingItem ? 'Update' : 'Save'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UMKDashboard;