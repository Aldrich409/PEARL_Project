import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NetworkOverviewScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  const NetworkOverviewScreen({super.key, required this.userData});

  @override
  State<NetworkOverviewScreen> createState() => _NetworkOverviewScreenState();
}

class _NetworkOverviewScreenState extends State<NetworkOverviewScreen> {
  bool _isLoading = true;
  List<dynamic> _devices = [];
  Map<String, dynamic> _latestReadings = {};

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    _devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);

    // Fetch the latest reading for every pond
    for (var dev in _devices) {
      final reading = await ApiService.getLatestTelemetry(dev['device_sn']);
      if (reading != null) {
        _latestReadings[dev['device_sn']] = reading;
      }
    }
    if (mounted) setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: _devices.length,
      itemBuilder: (context, index) {
        final dev = _devices[index];
        final sn = dev['device_sn'];
        final reading = _latestReadings[sn];
        final isOnline = reading != null;

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isOnline ? Colors.green.withOpacity(0.2) : Colors.grey.withOpacity(0.2),
              child: Icon(Icons.water, color: isOnline ? Colors.green : Colors.grey),
            ),
            title: Text("${dev['pond_name']} (Farmer ${dev['owner_id']})", style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(
              isOnline 
                  ? "Temp: ${reading['temperature']}°C | pH: ${reading['ph']} | Turb: ${reading['turbidity']}" 
                  : "🔴 Offline - No recent data",
              style: TextStyle(fontSize: 12, color: isOnline ? null : Colors.redAccent),
            ),
          ),
        );
      },
    );
  }
}