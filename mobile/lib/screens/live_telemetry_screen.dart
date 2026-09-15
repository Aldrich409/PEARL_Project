import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class LiveTelemetryScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String? activeDeviceSn; // Receives the selected node from the dashboard!
  const LiveTelemetryScreen({super.key, required this.userData, this.activeDeviceSn});

  @override
  State<LiveTelemetryScreen> createState() => _LiveTelemetryScreenState();
}

class _LiveTelemetryScreenState extends State<LiveTelemetryScreen> {
  bool _isLoading = true;
  String? _activeDeviceSn;
  Map<String, dynamic>? _device;
  Map<String, dynamic>? _latest;
  List<dynamic> _history = [];
  Map<String, dynamic>? _weather;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  // 🚀 This forces the screen to reload instantly if the Admin selects a new node!
  @override
  void didUpdateWidget(covariant LiveTelemetryScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.activeDeviceSn != widget.activeDeviceSn) {
      _loadData();
    }
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
    
    if (devices.isNotEmpty) {
      // Find the specific pond the admin clicked, or default to the first one
      _device = devices.firstWhere(
        (d) => d['device_sn'] == widget.activeDeviceSn,
        orElse: () => devices[0],
      );
      _activeDeviceSn = _device!['device_sn'];
      
      final results = await Future.wait([
        ApiService.getLatestTelemetry(_activeDeviceSn!),
        ApiService.getHistory(_activeDeviceSn!, limit: 30),
        ApiService.getCurrentWeather(),
      ]);
      
      _latest = results[0] as Map<String, dynamic>?;
      _history = results[1] as List<dynamic>? ?? [];
      _weather = results[2] as Map<String, dynamic>?;
    }
    if (mounted) setState(() => _isLoading = false);
  }

  Map<String, dynamic> _evaluateEnvironment(double temp, double ph, double turb) {
    if (turb > 100) return {'color': Colors.red, 'icon': '🚨', 'msg': 'CLASSIFICATION: High Algal Bloom Risk'};
    if (ph < 6.5 || ph > 9.0) return {'color': Colors.red, 'icon': '🚨', 'msg': 'CLASSIFICATION: Critical Water Warning'};
    if (temp < 24 || temp > 35) return {'color': Colors.red, 'icon': '🚨', 'msg': 'CLASSIFICATION: Extreme Temperature'};
    
    if (turb > 80) return {'color': Colors.orange, 'icon': '⚠️', 'msg': 'CLASSIFICATION: Approaching High Turbidity'};
    if (ph < 7.0 || ph > 8.5) return {'color': Colors.orange, 'icon': '⚠️', 'msg': 'CLASSIFICATION: pH Level Imbalance'};
    if (temp < 26 || temp > 33) return {'color': Colors.orange, 'icon': '⚠️', 'msg': 'CLASSIFICATION: Temperature Stress'};
    
    if (temp >= 28 && temp <= 31 && ph >= 7.0 && ph <= 8.5 && turb <= 80) {
      return {'color': Colors.green, 'icon': '✅', 'msg': 'CLASSIFICATION: Optimal Breeding'};
    }
    return {'color': Colors.blue, 'icon': 'ℹ️', 'msg': 'CLASSIFICATION: System Stable'};
  }

  Widget _buildMetricCard(String title, String value, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF16213E) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? const Color(0xFF2A2A4A) : const Color(0xFF7DD3FC)),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 4, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF0284C7))),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
        ],
      ),
    );
  }

  Widget _buildChart() {
    if (_history.isEmpty) return const Center(child: Text("No historical data available."));
    final data = _history.reversed.toList();
    List<FlSpot> tempSpots = [];
    List<FlSpot> phSpots = [];
    for (int i = 0; i < data.length; i++) {
      tempSpots.add(FlSpot(i.toDouble(), (data[i]['temperature'] as num).toDouble()));
      phSpots.add(FlSpot(i.toDouble(), (data[i]['ph'] as num).toDouble()));
    }
    return SizedBox(
      height: 200,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(spots: tempSpots, isCurved: true, color: Colors.redAccent, barWidth: 3, dotData: FlDotData(show: false)),
            LineChartBarData(spots: phSpots, isCurved: true, color: Colors.greenAccent, barWidth: 3, dotData: FlDotData(show: false)),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_activeDeviceSn == null) return const Center(child: Text("No assigned pond nodes."));

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    double temp = (_latest?['temperature'] as num?)?.toDouble() ?? 0.0;
    double ph = (_latest?['ph'] as num?)?.toDouble() ?? 0.0;
    double turb = (_latest?['turbidity'] as num?)?.toDouble() ?? 0.0;
    double lvl = (_latest?['water_level_cm'] as num?)?.toDouble() ?? 0.0;
    
    final aiStatus = _evaluateEnvironment(temp, ph, turb);

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          if (_weather != null) ...[
            Text("🌤️ Local Weather (Angono, Rizal)", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _buildMetricCard("AIR TEMP", "${_weather!['temperature_2m']} °C", isDark)),
                const SizedBox(width: 8),
                Expanded(child: _buildMetricCard("HUMIDITY", "${_weather!['relative_humidity_2m']} %", isDark)),
                const SizedBox(width: 8),
                Expanded(child: _buildMetricCard("WIND", "${_weather!['wind_speed_10m']} km/h", isDark)),
              ],
            ),
            const SizedBox(height: 24),
          ],
          Text("📡 Live Readings & AI Engine", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: (aiStatus['color'] as Color).withOpacity(0.15),
              border: Border(left: BorderSide(color: aiStatus['color'], width: 4)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Text(aiStatus['icon'], style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 12),
                Expanded(child: Text(aiStatus['msg'], style: const TextStyle(fontWeight: FontWeight.bold))),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: _buildMetricCard("WATER TEMP", "$temp °C", isDark)),
              const SizedBox(width: 8),
              Expanded(child: _buildMetricCard("pH LEVEL", "$ph", isDark)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _buildMetricCard("TURBIDITY", "$turb NTU", isDark)),
              const SizedBox(width: 8),
              Expanded(child: _buildMetricCard("WATER LEVEL", "$lvl cm", isDark)),
            ],
          ),
          const SizedBox(height: 24),
          Text("📈 Trend Analytics: ${_device!['pond_name']}", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 10),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF16213E) : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isDark ? const Color(0xFF2A2A4A) : const Color(0xFF7DD3FC)),
            ),
            child: _buildChart(),
          ),
          const SizedBox(height: 10),
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.circle, color: Colors.redAccent, size: 12), SizedBox(width: 4), Text("Temp"),
              SizedBox(width: 16),
              Icon(Icons.circle, color: Colors.greenAccent, size: 12), SizedBox(width: 4), Text("pH"),
            ],
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}