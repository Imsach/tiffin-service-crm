import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  Truck, 
  MapPin, 
  Route,
  Clock,
  CheckCircle,
  AlertCircle,
  Navigation,
  RefreshCw
} from 'lucide-react';
import { deliveriesAPI } from '../lib/api';

const DeliveriesPage = () => {
  const [deliveries, setDeliveries] = useState([]);
  const [todaysDeliveries, setTodaysDeliveries] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRouteDialog, setShowRouteDialog] = useState(false);
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);

  const fetchDeliveries = async () => {
    try {
      setLoading(true);
      const [deliveriesRes, todayRes] = await Promise.all([
        deliveriesAPI.getAll({ limit: 50 }),
        deliveriesAPI.getToday()
      ]);
      
      setDeliveries(deliveriesRes.data.data.deliveries || []);
      setTodaysDeliveries(todayRes.data.data);
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeliveries();
  }, []);

  const handleOptimizeRoute = async () => {
    try {
      setRouteLoading(true);
      const today = new Date().toISOString().split('T')[0];
      const response = await deliveriesAPI.optimizeRoute({
        delivery_date: today,
        start_location: { latitude: 49.1042, longitude: -122.6604 } // Langley, BC
      });
      setOptimizedRoute(response.data.data);
    } catch (error) {
      console.error('Error optimizing route:', error);
    } finally {
      setRouteLoading(false);
    }
  };

  const updateDeliveryStatus = async (deliveryId, newStatus) => {
    try {
      await deliveriesAPI.updateStatus(deliveryId, { delivery_status: newStatus });
      fetchDeliveries();
    } catch (error) {
      console.error('Error updating delivery status:', error);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_transit: 'bg-orange-100 text-orange-800',
      delivered: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    return variants[status] || variants.scheduled;
  };

  const getStatusIcon = (status) => {
    const icons = {
      scheduled: Clock,
      in_transit: Truck,
      delivered: CheckCircle,
      failed: AlertCircle,
      cancelled: AlertCircle
    };
    return icons[status] || Clock;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Deliveries</h1>
          <p className="text-gray-600 mt-1">Track and manage tiffin deliveries</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={fetchDeliveries} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Dialog open={showRouteDialog} onOpenChange={setShowRouteDialog}>
            <DialogTrigger asChild>
              <Button className="bg-orange-600 hover:bg-orange-700">
                <Route className="h-4 w-4 mr-2" />
                Optimize Route
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Route Optimization</DialogTitle>
                <DialogDescription>
                  Optimize delivery routes for today's deliveries
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Button 
                  onClick={handleOptimizeRoute} 
                  disabled={routeLoading}
                  className="w-full"
                >
                  {routeLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Optimizing Route...
                    </>
                  ) : (
                    <>
                      <Navigation className="h-4 w-4 mr-2" />
                      Generate Optimized Route
                    </>
                  )}
                </Button>

                {optimizedRoute && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-4 text-center">
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-600">Total Deliveries</p>
                        <p className="text-xl font-bold text-blue-600">{optimizedRoute.total_deliveries}</p>
                      </div>
                      <div className="p-3 bg-green-50 rounded-lg">
                        <p className="text-sm text-gray-600">Est. Distance</p>
                        <p className="text-xl font-bold text-green-600">{optimizedRoute.total_distance_km} km</p>
                      </div>
                      <div className="p-3 bg-purple-50 rounded-lg">
                        <p className="text-sm text-gray-600">Est. Duration</p>
                        <p className="text-xl font-bold text-purple-600">{optimizedRoute.estimated_duration}</p>
                      </div>
                    </div>

                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium mb-3">Optimized Route</h4>
                      <div className="space-y-2">
                        {optimizedRoute.optimized_route?.map((stop, index) => (
                          <div key={stop.delivery_id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                            <div className="flex items-center">
                              <div className="w-6 h-6 bg-orange-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
                                {stop.sequence}
                              </div>
                              <div>
                                <p className="font-medium">{stop.customer_name}</p>
                                <p className="text-sm text-gray-600">{stop.address}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-medium">{stop.estimated_time}</p>
                              <p className="text-xs text-gray-500">{stop.customer_phone}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Today's Summary */}
      {todaysDeliveries && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Deliveries</p>
                  <p className="text-2xl font-bold">{todaysDeliveries.total_deliveries}</p>
                </div>
                <Truck className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">In Transit</p>
                  <p className="text-2xl font-bold text-orange-600">{todaysDeliveries.summary?.in_transit || 0}</p>
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
                  <p className="text-2xl font-bold text-green-600">{todaysDeliveries.summary?.delivered || 0}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Failed</p>
                  <p className="text-2xl font-bold text-red-600">{todaysDeliveries.summary?.failed || 0}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Delivery Zones */}
      {todaysDeliveries?.deliveries_by_zone && Object.keys(todaysDeliveries.deliveries_by_zone).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <MapPin className="h-5 w-5 mr-2" />
              Delivery Zones
            </CardTitle>
            <CardDescription>
              Today's deliveries grouped by zone
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(todaysDeliveries.deliveries_by_zone).map(([zone, zoneDeliveries]) => (
                <div key={zone} className="p-4 border rounded-lg">
                  <h4 className="font-medium text-lg">{zone}</h4>
                  <p className="text-2xl font-bold text-blue-600">{zoneDeliveries.length}</p>
                  <p className="text-sm text-gray-600">deliveries</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Deliveries Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Truck className="h-5 w-5 mr-2" />
            Recent Deliveries
          </CardTitle>
          <CardDescription>
            Latest deliveries and their current status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading deliveries...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Delivery ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Address</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {deliveries.map((delivery) => {
                  const StatusIcon = getStatusIcon(delivery.delivery_status);
                  return (
                    <TableRow key={delivery.id}>
                      <TableCell className="font-medium">#{delivery.id}</TableCell>
                      <TableCell>
                        <div>
                          <div className="font-medium">{delivery.customer_name}</div>
                          <div className="text-sm text-gray-500">{delivery.customer_phone}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-xs truncate" title={delivery.delivery_address}>
                          {delivery.delivery_address}
                        </div>
                      </TableCell>
                      <TableCell>
                        {new Date(delivery.delivery_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusBadge(delivery.delivery_status)}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {delivery.delivery_status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-1">
                          {delivery.delivery_status === 'scheduled' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateDeliveryStatus(delivery.id, 'in_transit')}
                            >
                              Start Delivery
                            </Button>
                          )}
                          {delivery.delivery_status === 'in_transit' && (
                            <Button 
                              size="sm" 
                              variant="outline"
                              onClick={() => updateDeliveryStatus(delivery.id, 'delivered')}
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

export default DeliveriesPage;

