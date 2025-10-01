import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

// Events
abstract class CustomersEvent extends Equatable {
  const CustomersEvent();

  @override
  List<Object?> get props => [];
}

class LoadCustomers extends CustomersEvent {}

class SearchCustomers extends CustomersEvent {
  final String query;

  const SearchCustomers(this.query);

  @override
  List<Object?> get props => [query];
}

class FilterCustomers extends CustomersEvent {
  final String? region;
  final String? status;

  const FilterCustomers({this.region, this.status});

  @override
  List<Object?> get props => [region, status];
}

class AddCustomer extends CustomersEvent {
  final Customer customer;

  const AddCustomer(this.customer);

  @override
  List<Object?> get props => [customer];
}

class UpdateCustomer extends CustomersEvent {
  final Customer customer;

  const UpdateCustomer(this.customer);

  @override
  List<Object?> get props => [customer];
}

class DeleteCustomer extends CustomersEvent {
  final String customerId;

  const DeleteCustomer(this.customerId);

  @override
  List<Object?> get props => [customerId];
}

// States
abstract class CustomersState extends Equatable {
  const CustomersState();

  @override
  List<Object?> get props => [];
}

class CustomersInitial extends CustomersState {}

class CustomersLoading extends CustomersState {}

class CustomersLoaded extends CustomersState {
  final List<Customer> customers;
  final List<Customer> filteredCustomers;
  final String searchQuery;
  final String? selectedRegion;
  final String? selectedStatus;

  const CustomersLoaded({
    required this.customers,
    required this.filteredCustomers,
    this.searchQuery = '',
    this.selectedRegion,
    this.selectedStatus,
  });

  @override
  List<Object?> get props => [
        customers,
        filteredCustomers,
        searchQuery,
        selectedRegion,
        selectedStatus,
      ];

  CustomersLoaded copyWith({
    List<Customer>? customers,
    List<Customer>? filteredCustomers,
    String? searchQuery,
    String? selectedRegion,
    String? selectedStatus,
  }) {
    return CustomersLoaded(
      customers: customers ?? this.customers,
      filteredCustomers: filteredCustomers ?? this.filteredCustomers,
      searchQuery: searchQuery ?? this.searchQuery,
      selectedRegion: selectedRegion ?? this.selectedRegion,
      selectedStatus: selectedStatus ?? this.selectedStatus,
    );
  }
}

class CustomersError extends CustomersState {
  final String message;

  const CustomersError(this.message);

  @override
  List<Object?> get props => [message];
}

// Customer Model
class Customer extends Equatable {
  final String id;
  final String name;
  final String email;
  final String phone;
  final String address;
  final String region;
  final String status;
  final double totalPurchases;
  final DateTime lastOrderDate;
  final String? notes;

  const Customer({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.address,
    required this.region,
    required this.status,
    required this.totalPurchases,
    required this.lastOrderDate,
    this.notes,
  });

  @override
  List<Object?> get props => [
        id,
        name,
        email,
        phone,
        address,
        region,
        status,
        totalPurchases,
        lastOrderDate,
        notes,
      ];

  Customer copyWith({
    String? id,
    String? name,
    String? email,
    String? phone,
    String? address,
    String? region,
    String? status,
    double? totalPurchases,
    DateTime? lastOrderDate,
    String? notes,
  }) {
    return Customer(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      address: address ?? this.address,
      region: region ?? this.region,
      status: status ?? this.status,
      totalPurchases: totalPurchases ?? this.totalPurchases,
      lastOrderDate: lastOrderDate ?? this.lastOrderDate,
      notes: notes ?? this.notes,
    );
  }
}

// BLoC
class CustomersBloc extends Bloc<CustomersEvent, CustomersState> {
  CustomersBloc() : super(CustomersInitial()) {
    on<LoadCustomers>(_onLoadCustomers);
    on<SearchCustomers>(_onSearchCustomers);
    on<FilterCustomers>(_onFilterCustomers);
    on<AddCustomer>(_onAddCustomer);
    on<UpdateCustomer>(_onUpdateCustomer);
    on<DeleteCustomer>(_onDeleteCustomer);
  }

  // Mock data
  final List<Customer> _mockCustomers = [
    Customer(
      id: '1',
      name: 'Ahmed Al-Mansouri',
      email: 'ahmed.mansouri@email.com',
      phone: '+971501234567',
      address: 'Dubai Marina, Dubai, UAE',
      region: 'Dubai',
      status: 'Active',
      totalPurchases: 15750.00,
      lastOrderDate: DateTime.now().subtract(const Duration(days: 5)),
      notes: 'Preferred customer, bulk orders',
    ),
    Customer(
      id: '2',
      name: 'Fatima Al-Zahra',
      email: 'fatima.zahra@email.com',
      phone: '+971509876543',
      address: 'Al Ain City, Abu Dhabi, UAE',
      region: 'Abu Dhabi',
      status: 'Active',
      totalPurchases: 8920.50,
      lastOrderDate: DateTime.now().subtract(const Duration(days: 12)),
    ),
    Customer(
      id: '3',
      name: 'Omar Hassan',
      email: 'omar.hassan@email.com',
      phone: '+971551122334',
      address: 'Sharjah City Centre, Sharjah, UAE',
      region: 'Sharjah',
      status: 'Inactive',
      totalPurchases: 3400.00,
      lastOrderDate: DateTime.now().subtract(const Duration(days: 45)),
      notes: 'Payment issues, follow up required',
    ),
    Customer(
      id: '4',
      name: 'Layla Al-Rashid',
      email: 'layla.rashid@email.com',
      phone: '+971504455667',
      address: 'Ras Al Khaimah, UAE',
      region: 'Ras Al Khaimah',
      status: 'Active',
      totalPurchases: 12300.75,
      lastOrderDate: DateTime.now().subtract(const Duration(days: 8)),
    ),
    Customer(
      id: '5',
      name: 'Khalid Al-Maktoum',
      email: 'khalid.maktoum@email.com',
      phone: '+971507788990',
      address: 'Fujairah City, Fujairah, UAE',
      region: 'Fujairah',
      status: 'Active',
      totalPurchases: 6800.25,
      lastOrderDate: DateTime.now().subtract(const Duration(days: 20)),
    ),
  ];

  Future<void> _onLoadCustomers(
    LoadCustomers event,
    Emitter<CustomersState> emit,
  ) async {
    emit(CustomersLoading());
    
    try {
      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 500));
      
      emit(CustomersLoaded(
        customers: _mockCustomers,
        filteredCustomers: _mockCustomers,
      ));
    } catch (e) {
      emit(CustomersError('Failed to load customers: ${e.toString()}'));
    }
  }

  Future<void> _onSearchCustomers(
    SearchCustomers event,
    Emitter<CustomersState> emit,
  ) async {
    if (state is CustomersLoaded) {
      final currentState = state as CustomersLoaded;
      final filteredCustomers = _filterCustomers(
        currentState.customers,
        searchQuery: event.query,
        region: currentState.selectedRegion,
        status: currentState.selectedStatus,
      );

      emit(currentState.copyWith(
        filteredCustomers: filteredCustomers,
        searchQuery: event.query,
      ));
    }
  }

  Future<void> _onFilterCustomers(
    FilterCustomers event,
    Emitter<CustomersState> emit,
  ) async {
    if (state is CustomersLoaded) {
      final currentState = state as CustomersLoaded;
      final filteredCustomers = _filterCustomers(
        currentState.customers,
        searchQuery: currentState.searchQuery,
        region: event.region,
        status: event.status,
      );

      emit(currentState.copyWith(
        filteredCustomers: filteredCustomers,
        selectedRegion: event.region,
        selectedStatus: event.status,
      ));
    }
  }

  Future<void> _onAddCustomer(
    AddCustomer event,
    Emitter<CustomersState> emit,
  ) async {
    if (state is CustomersLoaded) {
      final currentState = state as CustomersLoaded;
      final updatedCustomers = [...currentState.customers, event.customer];
      final filteredCustomers = _filterCustomers(
        updatedCustomers,
        searchQuery: currentState.searchQuery,
        region: currentState.selectedRegion,
        status: currentState.selectedStatus,
      );

      emit(currentState.copyWith(
        customers: updatedCustomers,
        filteredCustomers: filteredCustomers,
      ));
    }
  }

  Future<void> _onUpdateCustomer(
    UpdateCustomer event,
    Emitter<CustomersState> emit,
  ) async {
    if (state is CustomersLoaded) {
      final currentState = state as CustomersLoaded;
      final updatedCustomers = currentState.customers
          .map((customer) => customer.id == event.customer.id ? event.customer : customer)
          .toList();
      final filteredCustomers = _filterCustomers(
        updatedCustomers,
        searchQuery: currentState.searchQuery,
        region: currentState.selectedRegion,
        status: currentState.selectedStatus,
      );

      emit(currentState.copyWith(
        customers: updatedCustomers,
        filteredCustomers: filteredCustomers,
      ));
    }
  }

  Future<void> _onDeleteCustomer(
    DeleteCustomer event,
    Emitter<CustomersState> emit,
  ) async {
    if (state is CustomersLoaded) {
      final currentState = state as CustomersLoaded;
      final updatedCustomers = currentState.customers
          .where((customer) => customer.id != event.customerId)
          .toList();
      final filteredCustomers = _filterCustomers(
        updatedCustomers,
        searchQuery: currentState.searchQuery,
        region: currentState.selectedRegion,
        status: currentState.selectedStatus,
      );

      emit(currentState.copyWith(
        customers: updatedCustomers,
        filteredCustomers: filteredCustomers,
      ));
    }
  }

  List<Customer> _filterCustomers(
    List<Customer> customers, {
    String? searchQuery,
    String? region,
    String? status,
  }) {
    var filtered = customers;

    if (searchQuery != null && searchQuery.isNotEmpty) {
      filtered = filtered
          .where((customer) =>
              customer.name.toLowerCase().contains(searchQuery.toLowerCase()) ||
              customer.email.toLowerCase().contains(searchQuery.toLowerCase()) ||
              customer.phone.contains(searchQuery))
          .toList();
    }

    if (region != null && region.isNotEmpty && region != 'All') {
      filtered = filtered.where((customer) => customer.region == region).toList();
    }

    if (status != null && status.isNotEmpty && status != 'All') {
      filtered = filtered.where((customer) => customer.status == status).toList();
    }

    return filtered;
  }
}
