import math
import random
from typing import List, Dict, Tuple, Optional
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import networkx as nx
from datetime import datetime, timedelta

class RouteOptimizer:
    def __init__(self):
        self.geocoder = Nominatim(user_agent="tiffin_crm")
        
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to latitude and longitude coordinates.
        In a production environment, you would cache these results.
        """
        try:
            location = self.geocoder.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            print(f"Geocoding error for {address}: {e}")
        return None
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in kilometers."""
        return geodesic(coord1, coord2).kilometers
    
    def create_distance_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[float]]:
        """Create a distance matrix for all coordinates."""
        n = len(coordinates)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self.calculate_distance(coordinates[i], coordinates[j])
        
        return matrix
    
    def nearest_neighbor_tsp(self, distance_matrix: List[List[float]], start_index: int = 0) -> List[int]:
        """
        Solve TSP using nearest neighbor heuristic.
        Returns the order of indices to visit.
        """
        n = len(distance_matrix)
        if n <= 1:
            return list(range(n))
        
        unvisited = set(range(n))
        current = start_index
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
    
    def two_opt_improvement(self, route: List[int], distance_matrix: List[List[float]]) -> List[int]:
        """
        Improve route using 2-opt local search.
        """
        def calculate_route_distance(route_order):
            total = 0
            for i in range(len(route_order) - 1):
                total += distance_matrix[route_order[i]][route_order[i + 1]]
            return total
        
        best_route = route[:]
        best_distance = calculate_route_distance(best_route)
        improved = True
        
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1:
                        continue  # Skip adjacent edges
                    
                    # Create new route by reversing the segment between i and j
                    new_route = route[:i] + route[i:j][::-1] + route[j:]
                    new_distance = calculate_route_distance(new_route)
                    
                    if new_distance < best_distance:
                        best_route = new_route[:]
                        best_distance = new_distance
                        route = new_route[:]
                        improved = True
        
        return best_route
    
    def optimize_delivery_route(self, deliveries: List[Dict], start_location: Dict) -> Dict:
        """
        Optimize delivery route using TSP algorithms.
        
        Args:
            deliveries: List of delivery dictionaries with address information
            start_location: Starting location with latitude and longitude
            
        Returns:
            Optimized route information
        """
        if not deliveries:
            return {
                'optimized_route': [],
                'total_distance_km': 0,
                'estimated_duration_minutes': 0,
                'start_location': start_location
            }
        
        # Prepare coordinates
        start_coord = (start_location['latitude'], start_location['longitude'])
        coordinates = [start_coord]
        delivery_info = []
        
        # Geocode delivery addresses
        for delivery in deliveries:
            address = delivery.get('delivery_address', '')
            coord = self.geocode_address(address)
            
            if coord:
                coordinates.append(coord)
                delivery_info.append(delivery)
            else:
                # Fallback: use approximate coordinates based on city/postal code
                # In production, you'd have a more robust geocoding system
                city = delivery.get('city', 'Langley')
                if 'Surrey' in address or 'Surrey' in city:
                    coord = (49.1913, -122.8490)  # Surrey, BC
                elif 'Vancouver' in address or 'Vancouver' in city:
                    coord = (49.2827, -123.1207)  # Vancouver, BC
                elif 'Burnaby' in address or 'Burnaby' in city:
                    coord = (49.2488, -122.9805)  # Burnaby, BC
                else:
                    coord = (49.1042, -122.6604)  # Default to Langley, BC
                
                coordinates.append(coord)
                delivery_info.append(delivery)
        
        if len(coordinates) <= 1:
            return {
                'optimized_route': [],
                'total_distance_km': 0,
                'estimated_duration_minutes': 0,
                'start_location': start_location
            }
        
        # Create distance matrix
        distance_matrix = self.create_distance_matrix(coordinates)
        
        # Solve TSP
        route_indices = self.nearest_neighbor_tsp(distance_matrix, start_index=0)
        
        # Improve with 2-opt if we have enough points
        if len(route_indices) > 3:
            route_indices = self.two_opt_improvement(route_indices, distance_matrix)
        
        # Calculate total distance
        total_distance = 0
        for i in range(len(route_indices) - 1):
            total_distance += distance_matrix[route_indices[i]][route_indices[i + 1]]
        
        # Build optimized route (excluding start location)
        optimized_route = []
        estimated_time = datetime.strptime('09:00', '%H:%M')  # Start at 9 AM
        
        for i, route_idx in enumerate(route_indices[1:], 1):  # Skip start location
            delivery_idx = route_idx - 1  # Adjust for start location
            delivery = delivery_info[delivery_idx]
            
            # Estimate time (15 minutes per delivery + travel time)
            if i > 1:
                travel_time = max(5, int(distance_matrix[route_indices[i-1]][route_idx] * 3))  # 3 min per km
                estimated_time += timedelta(minutes=travel_time + 15)
            else:
                estimated_time += timedelta(minutes=15)  # First delivery
            
            optimized_route.append({
                'delivery_id': delivery.get('id'),
                'sequence': i,
                'customer_name': delivery.get('customer_name', ''),
                'customer_phone': delivery.get('customer_phone', ''),
                'address': delivery.get('delivery_address', ''),
                'estimated_time': estimated_time.strftime('%H:%M'),
                'delivery_instructions': delivery.get('delivery_instructions', ''),
                'coordinates': coordinates[route_idx]
            })
        
        # Estimate total duration
        estimated_duration_minutes = len(delivery_info) * 15 + int(total_distance * 3)
        
        return {
            'optimized_route': optimized_route,
            'total_distance_km': round(total_distance, 2),
            'estimated_duration_minutes': estimated_duration_minutes,
            'estimated_duration': f"{estimated_duration_minutes // 60}h {estimated_duration_minutes % 60}m",
            'start_location': start_location,
            'algorithm_used': 'Nearest Neighbor + 2-opt',
            'total_deliveries': len(delivery_info)
        }
    
    def optimize_multiple_routes(self, deliveries: List[Dict], start_location: Dict, 
                                max_deliveries_per_route: int = 15) -> List[Dict]:
        """
        Optimize multiple routes when there are too many deliveries for one route.
        """
        if len(deliveries) <= max_deliveries_per_route:
            return [self.optimize_delivery_route(deliveries, start_location)]
        
        # Group deliveries by zone/area for better route efficiency
        zones = self.group_deliveries_by_zone(deliveries)
        routes = []
        
        for zone, zone_deliveries in zones.items():
            if len(zone_deliveries) > max_deliveries_per_route:
                # Further split large zones
                chunks = [zone_deliveries[i:i + max_deliveries_per_route] 
                         for i in range(0, len(zone_deliveries), max_deliveries_per_route)]
                for chunk in chunks:
                    route = self.optimize_delivery_route(chunk, start_location)
                    route['zone'] = f"{zone} (Part {chunks.index(chunk) + 1})"
                    routes.append(route)
            else:
                route = self.optimize_delivery_route(zone_deliveries, start_location)
                route['zone'] = zone
                routes.append(route)
        
        return routes
    
    def group_deliveries_by_zone(self, deliveries: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group deliveries by geographical zone for better route planning.
        """
        zones = {}
        
        for delivery in deliveries:
            address = delivery.get('delivery_address', '').lower()
            city = delivery.get('city', '').lower()
            
            # Simple zone classification based on city/area
            if 'surrey' in address or 'surrey' in city:
                zone = 'Surrey'
            elif 'vancouver' in address or 'vancouver' in city:
                zone = 'Vancouver'
            elif 'burnaby' in address or 'burnaby' in city:
                zone = 'Burnaby'
            elif 'richmond' in address or 'richmond' in city:
                zone = 'Richmond'
            elif 'langley' in address or 'langley' in city:
                zone = 'Langley'
            elif 'coquitlam' in address or 'coquitlam' in city:
                zone = 'Coquitlam'
            else:
                zone = 'Other'
            
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(delivery)
        
        return zones
    
    def calculate_route_efficiency(self, route: List[Dict]) -> Dict:
        """
        Calculate efficiency metrics for a route.
        """
        if not route:
            return {'efficiency_score': 0, 'avg_distance_per_delivery': 0}
        
        total_distance = sum(item.get('distance_to_next', 0) for item in route)
        avg_distance = total_distance / len(route) if route else 0
        
        # Efficiency score (lower is better)
        efficiency_score = avg_distance * len(route)
        
        return {
            'efficiency_score': round(efficiency_score, 2),
            'avg_distance_per_delivery': round(avg_distance, 2),
            'total_stops': len(route),
            'total_distance': round(total_distance, 2)
        }

