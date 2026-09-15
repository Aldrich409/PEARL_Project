import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ForecastScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String? activeDeviceSn;
  const ForecastScreen({super.key, required this.userData, this.activeDeviceSn});

  @override
  State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
  bool _isLoading = true;
  List<dynamic> _forecasts = [];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void didUpdateWidget(covariant ForecastScreen oldWidget) {
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
      _forecasts = await ApiService.getForecast(device['device_sn'], days: 7);
    }
    if (mounted) setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_forecasts.isEmpty) return const Center(child: Text("Not enough telemetry data for Meta Prophet AI."));

    final isDark = Theme.of(context).brightness == Brightness.dark;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _forecasts.length,
      itemBuilder: (context, index) {
        final day = _forecasts[index];
        final status = day['status'] as String;
        
        final isSuccess = status.contains('Optimal') || status.contains('Stable');
        final isWarning = status.contains('Warning') || status.contains('Approaching');
        final color = isSuccess ? const Color(0xFF10B981) : isWarning ? const Color(0xFFF59E0B) : const Color(0xFFEF4444);

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border(left: BorderSide(color: color, width: 5)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("📅 Date: ${day['date']}", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: isDark ? Colors.white : Colors.black87)),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text("Temp: ${day['predicted_temperature']}°C"),
                  Text("pH: ${day['predicted_ph']}"),
                  Text("Turb: ${day['predicted_turbidity']}"),
                ],
              ),
              const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Divider()),
              Text(status, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 6),
              Text(day['action_required'], style: TextStyle(fontStyle: FontStyle.italic, fontSize: 12, color: isDark ? Colors.white70 : Colors.black54)),
            ],
          ),
        );
      },
    );
  }
}