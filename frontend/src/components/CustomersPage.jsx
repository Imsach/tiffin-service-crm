import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  Users, 
  Plus, 
  Search, 
  Phone, 
  Mail, 
  MapPin,
  DollarSign,
  Edit,
  Eye
} from 'lucide-react';
import { customersAPI } from '../lib/api';

const CustomersPage = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    address_line1: '',
    address_line2: '',
    city: '',
    province: '',
    postal_code: '',
    dietary_restrictions: '',
    delivery_instructions: ''
  });

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      const response = await customersAPI.getAll();
      setCustomers(response.data.data.customers || []);
    } catch (error) {
      console.error('Error fetching customers:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  const handleAddCustomer = async (e) => {
    e.preventDefault();
    try {
      await customersAPI.create(newCustomer);
      setShowAddDialog(false);
      setNewCustomer({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        address_line1: '',
        address_line2: '',
        city: '',
        province: '',
        postal_code: '',
        dietary_restrictions: '',
        delivery_instructions: ''
      });
      fetchCustomers();
    } catch (error) {
      console.error('Error adding customer:', error);
    }
  };

  const filteredCustomers = customers.filter(customer =>
    `${customer.first_name} ${customer.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone_number?.includes(searchTerm)
  );

  const getStatusBadge = (status) => {
    const variants = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800',
      suspended: 'bg-red-100 text-red-800'
    };
    return variants[status] || variants.active;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-600 mt-1">Manage your tiffin service customers</p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button className="bg-orange-600 hover:bg-orange-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Customer
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Add New Customer</DialogTitle>
              <DialogDescription>
                Enter customer details to create a new account
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleAddCustomer} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="first_name">First Name</Label>
                  <Input
                    id="first_name"
                    value={newCustomer.first_name}
                    onChange={(e) => setNewCustomer({...newCustomer, first_name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="last_name">Last Name</Label>
                  <Input
                    id="last_name"
                    value={newCustomer.last_name}
                    onChange={(e) => setNewCustomer({...newCustomer, last_name: e.target.value})}
                    required
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newCustomer.email}
                    onChange={(e) => setNewCustomer({...newCustomer, email: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="phone_number">Phone Number</Label>
                  <Input
                    id="phone_number"
                    value={newCustomer.phone_number}
                    onChange={(e) => setNewCustomer({...newCustomer, phone_number: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="address_line1">Address Line 1</Label>
                <Input
                  id="address_line1"
                  value={newCustomer.address_line1}
                  onChange={(e) => setNewCustomer({...newCustomer, address_line1: e.target.value})}
                  required
                />
              </div>

              <div>
                <Label htmlFor="address_line2">Address Line 2 (Optional)</Label>
                <Input
                  id="address_line2"
                  value={newCustomer.address_line2}
                  onChange={(e) => setNewCustomer({...newCustomer, address_line2: e.target.value})}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={newCustomer.city}
                    onChange={(e) => setNewCustomer({...newCustomer, city: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="province">Province</Label>
                  <Input
                    id="province"
                    value={newCustomer.province}
                    onChange={(e) => setNewCustomer({...newCustomer, province: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="postal_code">Postal Code</Label>
                  <Input
                    id="postal_code"
                    value={newCustomer.postal_code}
                    onChange={(e) => setNewCustomer({...newCustomer, postal_code: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="dietary_restrictions">Dietary Restrictions</Label>
                <Input
                  id="dietary_restrictions"
                  value={newCustomer.dietary_restrictions}
                  onChange={(e) => setNewCustomer({...newCustomer, dietary_restrictions: e.target.value})}
                  placeholder="e.g., Vegetarian, No nuts, etc."
                />
              </div>

              <div>
                <Label htmlFor="delivery_instructions">Delivery Instructions</Label>
                <Input
                  id="delivery_instructions"
                  value={newCustomer.delivery_instructions}
                  onChange={(e) => setNewCustomer({...newCustomer, delivery_instructions: e.target.value})}
                  placeholder="e.g., Leave at door, Ring bell, etc."
                />
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
                <Button type="submit" className="bg-orange-600 hover:bg-orange-700">
                  Add Customer
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search and Stats */}
      <div className="flex items-center justify-between">
        <div className="relative w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search customers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>Total: {customers.length}</span>
          <span>Active: {customers.filter(c => c.status === 'active').length}</span>
        </div>
      </div>

      {/* Customers Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="h-5 w-5 mr-2" />
            Customer List
          </CardTitle>
          <CardDescription>
            Manage and view all your customers
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading customers...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Contact</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Balance</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCustomers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">
                          {customer.first_name} {customer.last_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {customer.id}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center text-sm">
                          <Phone className="h-3 w-3 mr-1" />
                          {customer.phone_number}
                        </div>
                        <div className="flex items-center text-sm text-gray-500">
                          <Mail className="h-3 w-3 mr-1" />
                          {customer.email}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center text-sm">
                        <MapPin className="h-3 w-3 mr-1" />
                        {customer.city}, {customer.province}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <DollarSign className="h-3 w-3 mr-1" />
                        <span className={customer.account_balance >= 0 ? 'text-green-600' : 'text-red-600'}>
                          ${parseFloat(customer.account_balance || 0).toFixed(2)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(customer.status)}>
                        {customer.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomersPage;

