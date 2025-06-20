import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Users, 
  Package, 
  Truck, 
  DollarSign, 
  TrendingUp, 
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { reportsAPI, ordersAPI, deliveriesAPI } from '../lib/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    dailySummary: null,
    todaysOrders: null,
    todaysDeliveries: null,
    loading: true
  });

  const fetchDashboardData = async () => {
    try {
      setDashboardData(prev => ({ ...prev, loading: true }));
      
      const today = new Date().toISOString().split('T')[0];
      
      const [dailySummaryRes, ordersRes, deliveriesRes] = await Promise.all([
        reportsAPI.getDailySummary({ date: today }),
        ordersAPI.getToday(),
        deliveriesAPI.getToday()
      ]);

      setDashboardData({
        dailySummary: dailySummaryRes.data.data,
        todaysOrders: ordersRes.data.data,
        todaysDeliveries: deliveriesRes.data.data,
        loading: false
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData(prev => ({ ...prev, loading: false }));
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const { dailySummary, todaysOrders, todaysDeliveries, loading } = dashboardData;

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Orders',
      value: dailySummary?.summary?.total_orders || 0,
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Completed Deliveries',
      value: dailySummary?.summary?.completed_deliveries || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Revenue Today',
      value: `$${dailySummary?.summary?.total_revenue?.toFixed(2) || '0.00'}`,
      icon: DollarSign,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-100'
    },
    {
      title: 'Active Customers',
      value: dailySummary?.summary?.active_customers || 0,
      icon: Users,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    }
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's what's happening with your tiffin service today.
          </p>
        </div>
        <Button onClick={fetchDashboardData} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Today's Orders */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Package className="h-5 w-5 mr-2" />
              Today's Orders
            </CardTitle>
            <CardDescription>
              Order status breakdown for {new Date().toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {todaysOrders?.summary ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Pending</span>
                  <Badge variant="secondary">{todaysOrders.summary.pending}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Preparing</span>
                  <Badge variant="outline">{todaysOrders.summary.preparing}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Prepared</span>
                  <Badge variant="outline">{todaysOrders.summary.prepared}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Out for Delivery</span>
                  <Badge className="bg-blue-100 text-blue-800">{todaysOrders.summary.out_for_delivery}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Delivered</span>
                  <Badge className="bg-green-100 text-green-800">{todaysOrders.summary.delivered}</Badge>
                </div>
                <div className="pt-3 border-t">
                  <div className="flex justify-between items-center font-medium">
                    <span>Total Revenue</span>
                    <span className="text-green-600">${todaysOrders.total_revenue?.toFixed(2) || '0.00'}</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No orders data available</p>
            )}
          </CardContent>
        </Card>

        {/* Today's Deliveries */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Truck className="h-5 w-5 mr-2" />
              Today's Deliveries
            </CardTitle>
            <CardDescription>
              Delivery status and zones for {new Date().toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {todaysDeliveries?.summary ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Scheduled</span>
                  <Badge variant="secondary">{todaysDeliveries.summary.scheduled}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">In Transit</span>
                  <Badge className="bg-blue-100 text-blue-800">{todaysDeliveries.summary.in_transit}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Delivered</span>
                  <Badge className="bg-green-100 text-green-800">{todaysDeliveries.summary.delivered}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Failed</span>
                  <Badge variant="destructive">{todaysDeliveries.summary.failed}</Badge>
                </div>
                
                {/* Delivery Zones */}
                {todaysDeliveries.deliveries_by_zone && Object.keys(todaysDeliveries.deliveries_by_zone).length > 0 && (
                  <div className="pt-3 border-t">
                    <h4 className="font-medium text-sm mb-2">Delivery Zones</h4>
                    {Object.entries(todaysDeliveries.deliveries_by_zone).map(([zone, deliveries]) => (
                      <div key={zone} className="flex justify-between items-center text-sm">
                        <span className="text-gray-600">{zone}</span>
                        <span className="font-medium">{deliveries.length}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No deliveries data available</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks to manage your tiffin service
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-auto p-4 flex flex-col items-center space-y-2" variant="outline">
              <Package className="h-6 w-6" />
              <span>Create Orders</span>
              <span className="text-xs text-gray-500">Bulk create today's orders</span>
            </Button>
            <Button className="h-auto p-4 flex flex-col items-center space-y-2" variant="outline">
              <Truck className="h-6 w-6" />
              <span>Optimize Routes</span>
              <span className="text-xs text-gray-500">Plan delivery routes</span>
            </Button>
            <Button className="h-auto p-4 flex flex-col items-center space-y-2" variant="outline">
              <Users className="h-6 w-6" />
              <span>Add Customer</span>
              <span className="text-xs text-gray-500">Register new customer</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

