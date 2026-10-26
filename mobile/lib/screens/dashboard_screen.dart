import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import 'live_telemetry_screen.dart';
import 'forecast_screen.dart';
import 'network_overview_screen.dart';
import 'records_screen.dart';
import 'settings_screen.dart';

class DashboardScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  const DashboardScreen({super.key, required this.userData});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String _currentPage = 'Live Telemetry';
  List<dynamic> _devices = [];
  String? _selectedDeviceSn;

  @override
  void initState() {
    super.initState();
    _fetchDevices();
  }

  // Fetch the devices so the Admin dropdown has options
  Future<void> _fetchDevices() async {
    final devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
    if (mounted) {
      setState(() {
        _devices = devices;
        if (_devices.isNotEmpty) {
          _selectedDeviceSn = _devices[0]['device_sn'];
        }
      });
    }
  }

  void _logout() async {
    await ApiService.logout();
    if (mounted) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const LoginScreen()),
      );
    }
  }

  Widget _buildBody() {
    switch (_currentPage) {
      case 'Live Telemetry':
        return LiveTelemetryScreen(userData: widget.userData, activeDeviceSn: _selectedDeviceSn);
      case 'Breeding Forecast':
        return ForecastScreen(userData: widget.userData, activeDeviceSn: _selectedDeviceSn);
      case 'Network Overview':
        return NetworkOverviewScreen(userData: widget.userData);
      case 'Telemetry Records':
        return RecordsScreen(userData: widget.userData, activeDeviceSn: _selectedDeviceSn);
      case 'System Settings':
        return SettingsScreen(userData: widget.userData, activeDeviceSn: _selectedDeviceSn);
      default:
        return const Center(child: Text('Page Not Found'));
    }
  }

  @override
  Widget build(BuildContext context) {
    final role = widget.userData['role'] ?? 'farmer';
    final username = widget.userData['username'] ?? 'User';
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return Scaffold(
      appBar: AppBar(
        title: Text(_currentPage),
        centerTitle: true,
        actions: [
          // 🚀 ADMIN ONLY: Active Node Selector Dropdown
          if (role == 'admin' && _devices.isNotEmpty)
            PopupMenuButton<String>(
              icon: const Icon(Icons.sensors),
              tooltip: 'Select Active Node',
              onSelected: (String newValue) {
                setState(() => _selectedDeviceSn = newValue);
              },
              itemBuilder: (BuildContext context) {
                return _devices.map<PopupMenuItem<String>>((dynamic dev) {
                  return PopupMenuItem<String>(
                    value: dev['device_sn'],
                    child: Text(
                      "Farmer ${dev['owner_id']} (${dev['pond_name']} - ${dev['fish_type'] ?? 'Tilapia'})",
                      style: TextStyle(
                        fontWeight: _selectedDeviceSn == dev['device_sn'] ? FontWeight.bold : FontWeight.normal,
                        color: _selectedDeviceSn == dev['device_sn'] ? primaryColor : null,
                      ),
                    ),
                  );
                }).toList();
              },
            ),
        ],
      ),
      drawer: Drawer(
        backgroundColor: isDark ? const Color(0xFF16213E) : const Color(0xFFF0F9FF),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1A1A2E) : const Color(0xFFE0F2FE),
                border: Border(bottom: BorderSide(color: isDark ? const Color(0xFF2A2A4A) : const Color(0xFFBAE6FD))),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('🐟 PEARL System', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text('User: $username', style: const TextStyle(fontSize: 16)),
                  Text('Role: ${role.toString().toUpperCase()}', style: TextStyle(fontSize: 12, color: primaryColor, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.analytics_outlined),
              title: const Text('Live Telemetry'),
              selected: _currentPage == 'Live Telemetry',
              selectedColor: primaryColor,
              onTap: () {
                setState(() => _currentPage = 'Live Telemetry');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.online_prediction),
              title: const Text('Breeding Forecast'),
              selected: _currentPage == 'Breeding Forecast',
              selectedColor: primaryColor,
              onTap: () {
                setState(() => _currentPage = 'Breeding Forecast');
                Navigator.pop(context);
              },
            ),
            if (role == 'admin')
              ListTile(
                leading: const Icon(Icons.public),
                title: const Text('Network Overview'),
                selected: _currentPage == 'Network Overview',
                selectedColor: primaryColor,
                onTap: () {
                  setState(() => _currentPage = 'Network Overview');
                  Navigator.pop(context);
                },
              ),
            ListTile(
              leading: const Icon(Icons.folder_open),
              title: const Text('Telemetry Records'),
              selected: _currentPage == 'Telemetry Records',
              selectedColor: primaryColor,
              onTap: () {
                setState(() => _currentPage = 'Telemetry Records');
                Navigator.pop(context);
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('System Settings'),
              selected: _currentPage == 'System Settings',
              selectedColor: primaryColor,
              onTap: () {
                setState(() => _currentPage = 'System Settings');
                Navigator.pop(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.redAccent),
              title: const Text('Logout', style: TextStyle(color: Colors.redAccent)),
              onTap: _logout,
            ),
          ],
        ),
      ),
      body: _buildBody(),
    );
  }
}