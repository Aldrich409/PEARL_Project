import 'package:flutter/material.dart';
import '../services/api_service.dart';

class RecordsScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String? activeDeviceSn;
  const RecordsScreen({super.key, required this.userData, this.activeDeviceSn});

  @override
  State<RecordsScreen> createState() => _RecordsScreenState();
}

class _RecordsScreenState extends State<RecordsScreen> {
  bool _isLoading = true;
  List<dynamic> _history = [];
  String _pondName = "";

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void didUpdateWidget(covariant RecordsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.activeDeviceSn != widget.activeDeviceSn) {
      _loadData();
    }
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
    
    if (devices.isNotEmpty) {
      final device = devices.firstWhere((d) => d['device_sn'] == widget.activeDeviceSn, orElse: () => devices[0]);
      _pondName = device['pond_name'];
      _history = await ApiService.getHistory(device['device_sn'], limit: 100); 
    }
    if (mounted) setState(() => _isLoading = false);
  }

  Widget _buildMiniMetric(String label, String value, bool isDark) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 11, color: isDark ? Colors.white54 : Colors.black54, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: isDark ? Colors.white : Colors.black87)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_history.isEmpty) return const Center(child: Text("No telemetry records found."));

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          color: isDark ? const Color(0xFF16213E) : Colors.white,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("📋 Data Logs for $_pondName", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
              const SizedBox(height: 4),
              Text("Showing the latest ${_history.length} records", style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
            ],
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: _history.length,
            itemBuilder: (context, index) {
              final record = _history[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.access_time, size: 16, color: primaryColor),
                          const SizedBox(width: 8),
                          Text(record['timestamp'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildMiniMetric("Temp", "${record['temperature']}°C", isDark),
                          _buildMiniMetric("pH", "${record['ph']}", isDark),
                          _buildMiniMetric("Turb", "${record['turbidity']}", isDark),
                          _buildMiniMetric("Lvl", "${record['water_level_cm']}cm", isDark),
                        ],
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}