import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { 
  Package, 
  Plus, 
  Calendar, 
  Clock,
  CheckCircle,
  Truck,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { ordersAPI } from '../lib/api';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [todaysOrders, setTodaysOrders] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showBulkCreateDialog, setShowBulkCreateDialog] = useState(false);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const [ordersRes, todayRes] = await Promise.all([
        ordersAPI.getAll({ limit: 50 }),
        ordersAPI.getToday()
      ]);
      
      setOrders(ordersRes.data.data.orders || []);
      setTodaysOrders(todayRes.data.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleBulkCreateOrders = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      await ordersAPI.bulkCreate({
        order_date: today,
        meal_type: 'lunch'
      });
      setShowBulkCreateDialog(false);
      fetchOrders();
    } catch (error) {
      console.error('Error creating bulk orders:', error);
    }
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await ordersAPI.updateStatus(orderId, { status: newStatus });
      fetchOrders();
    } catch (error) {
      console.error('Error updating order status:', error);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      pending: 'bg-yellow-100 text-yellow-800',
      preparing: 'bg-blue-100 text-blue-800',
      prepared: 'bg-purple-100 text-purple-800',
      packed: 'bg-indigo-100 text-indigo-800',
      out_for_delivery: 'bg-orange-100 text-orange-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return variants[status] || variants.pending;
  };

  const getStatusIcon = (status) => {
    const icons = {
      pending: Clock,
      preparing: RefreshCw,
      prepared: CheckCircle,
      packed: Package,
      out_for_delivery: Truck,
      delivered: CheckCircle,
      cancelled: AlertCircle
    };
    return icons[status] || Clock;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Orders</h1>
          <p className="text-gray-600 mt-1">Manage and track all tiffin orders</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={fetchOrders} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showBulkCreateDialog} onOpenChange={setShowBulkCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-orange-600 hover:bg-orange-700">
                <Plus className="h-4 w-4 mr-2" />
                Create Today's Orders
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Bulk Orders</DialogTitle>
                <DialogDescription>
                  This will create orders for all active subscriptions for today's lunch delivery.
                </DialogDescription>
              </DialogHeader>
              <div className="flex justify-end space-x-2 pt-4">
                <Button variant="outline" onClick={() => setShowBulkCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleBulkCreateOrders} className="bg-orange-600 hover:bg-orange-700">
                  Create Orders
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Today's Summary */}
      {todaysOrders && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Orders</p>
                  <p className="text-2xl font-bold">{todaysOrders.total_orders}</p>
                </div>
                <Package className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pending</p>
                  <p className="text-2xl font-bold text-yellow-600">{todaysOrders.summary?.pending || 0}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Preparing</p>
                  <p className="text-2xl font-bold text-blue-600">{todaysOrders.summary?.preparing || 0}</p>
                </div>
                <RefreshCw className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Out for Delivery</p>
                  <p className="text-2xl font-bold text-orange-600">{todaysOrders.summary?.out_for_delivery || 0}</p>
                </div>
                <Truck className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Delivered</p>
                  <p className="text-2xl font-bold text-green-600">{todaysOrders.summary?.delivered || 0}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Orders Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Package className="h-5 w-5 mr-2" />
            Recent Orders
          </CardTitle>
          <CardDescription>
            Latest orders and their current status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading orders...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Plan</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((order) => {
                  const StatusIcon = getStatusIcon(order.status);
                  return (
                    <TableRow key={order.id}>
                      <TableCell className="font-medium">#{order.id}</TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{order.customer_name}</div>
                          <div className="text-sm text-gray-500">{order.customer_phone}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 mr-1" />
                          {new Date(order.order_date).toLocaleDateString()}
                        </div>
                      </TableCell>
                      <TableCell>{order.plan_name}</TableCell>
                      <TableCell>
                        <Badge className={getStatusBadge(order.status)}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {order.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>${parseFloat(order.total_amount || 0).toFixed(2)}</TableCell>
                      <TableCell>
                        <div className="flex space-x-1">
                          {order.status === 'pending' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateOrderStatus(order.id, 'preparing')}
                            >
                              Start Preparing
                            </Button>
                          )}
                          {order.status === 'preparing' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateOrderStatus(order.id, 'prepared')}
                            >
                              Mark Prepared
                            </Button>
                          )}
                          {order.status === 'prepared' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateOrderStatus(order.id, 'packed')}
                            >
                              Mark Packed
                            </Button>
                          )}
                          {order.status === 'packed' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateOrderStatus(order.id, 'out_for_delivery')}
                            >
                              Out for Delivery
                            </Button>
                          )}
                          {order.status === 'out_for_delivery' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateOrderStatus(order.id, 'delivered')}
                            >
                              Mark Delivered
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default OrdersPage;

