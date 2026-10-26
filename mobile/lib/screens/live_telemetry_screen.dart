import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class LiveTelemetryScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String? activeDeviceSn; 
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
  
  List<dynamic> _allDevices = [];
  Map<String, dynamic> _allLatestReadings = {};

  @override
  void initState() {
    super.initState();
    _loadData();
  }

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
      _device = devices.firstWhere((d) => d['device_sn'] == widget.activeDeviceSn, orElse: () => devices[0]);
      _activeDeviceSn = _device!['device_sn'];
      
      final results = await Future.wait([
        ApiService.getLatestTelemetry(_activeDeviceSn!),
        ApiService.getHistory(_activeDeviceSn!, limit: 30),
        ApiService.getCurrentWeather(),
      ]);
      
      _latest = results[0] as Map<String, dynamic>?;
      _history = results[1] as List<dynamic>? ?? [];
      _weather = results[2] as Map<String, dynamic>?;

      if (widget.userData['role'] == 'admin') {
        _allDevices = List.from(devices);
        for (var dev in _allDevices) {
          final reading = await ApiService.getLatestTelemetry(dev['device_sn']);
          if (reading != null) _allLatestReadings[dev['device_sn']] = reading;
        }
        _allDevices.sort((a, b) {
          int scoreA = _getRiskScore(_allLatestReadings[a['device_sn']], a);
          int scoreB = _getRiskScore(_allLatestReadings[b['device_sn']], b);
          return scoreB.compareTo(scoreA);
        });
      }
    }
    if (mounted) setState(() => _isLoading = false);
  }

  int _getRiskScore(Map<String, dynamic>? reading, Map<String, dynamic>? dev) {
    if (reading == null) return -1;
    double temp = (reading['temperature'] as num).toDouble();
    double ph = (reading['ph'] as num).toDouble();
    double turb = (reading['turbidity'] as num).toDouble();

    double tNormMin = (dev?['temp_norm_min'] as num?)?.toDouble() ?? 26.0;
    double tNormMax = (dev?['temp_norm_max'] as num?)?.toDouble() ?? 33.0;
    double tDangMin = (dev?['temp_danger_min'] as num?)?.toDouble() ?? 24.0;
    double tDangMax = (dev?['temp_danger_max'] as num?)?.toDouble() ?? 35.0;

    double pNormMin = (dev?['ph_norm_min'] as num?)?.toDouble() ?? 7.0;
    double pNormMax = (dev?['ph_norm_max'] as num?)?.toDouble() ?? 8.5;
    double pDangMin = (dev?['ph_danger_min'] as num?)?.toDouble() ?? 6.5;
    double pDangMax = (dev?['ph_danger_max'] as num?)?.toDouble() ?? 9.0;

    double tbNormMax = (dev?['turb_norm_max'] as num?)?.toDouble() ?? 80.0;
    double tbDangMax = (dev?['turb_danger_max'] as num?)?.toDouble() ?? 100.0;

    if (turb > tbDangMax || ph < pDangMin || ph > pDangMax || temp < tDangMin || temp > tDangMax) return 3; 
    if (turb > tbNormMax || ph < pNormMin || ph > pNormMax || temp < tNormMin || temp > tNormMax) return 2; 
    return 1; 
  }

  Map<String, dynamic> _getRiskStyling(int score) {
    switch (score) {
      case 3: return {'color': Colors.redAccent};
      case 2: return {'color': Colors.orangeAccent};
      case 1: return {'color': Colors.green};
      default: return {'color': Colors.grey};
    }
  }

  Map<String, dynamic> _evaluateEnvironment(double temp, double ph, double turb, Map<String, dynamic>? dev) {
    String fish = dev?['fish_type'] ?? 'Tilapia';
    double tNormMin = (dev?['temp_norm_min'] as num?)?.toDouble() ?? 26.0;
    double tNormMax = (dev?['temp_norm_max'] as num?)?.toDouble() ?? 33.0;
    double tDangMin = (dev?['temp_danger_min'] as num?)?.toDouble() ?? 24.0;
    double tDangMax = (dev?['temp_danger_max'] as num?)?.toDouble() ?? 35.0;

    double pNormMin = (dev?['ph_norm_min'] as num?)?.toDouble() ?? 7.0;
    double pNormMax = (dev?['ph_norm_max'] as num?)?.toDouble() ?? 8.5;
    double pDangMin = (dev?['ph_danger_min'] as num?)?.toDouble() ?? 6.5;
    double pDangMax = (dev?['ph_danger_max'] as num?)?.toDouble() ?? 9.0;

    double tbNormMax = (dev?['turb_norm_max'] as num?)?.toDouble() ?? 80.0;
    double tbDangMax = (dev?['turb_danger_max'] as num?)?.toDouble() ?? 100.0;

    if (turb > tbDangMax) return {'color': Colors.red, 'icon': '🚨', 'msg': '[$fish] CLASSIFICATION: High Algal Bloom Risk'};
    if (ph < pDangMin || ph > pDangMax) return {'color': Colors.red, 'icon': '🚨', 'msg': '[$fish] CLASSIFICATION: Critical Water Warning'};
    if (temp < tDangMin || temp > tDangMax) return {'color': Colors.red, 'icon': '🚨', 'msg': '[$fish] CLASSIFICATION: Extreme Temperature'};
    if (turb > tbNormMax) return {'color': Colors.orange, 'icon': '⚠️', 'msg': '[$fish] CLASSIFICATION: Approaching High Turbidity'};
    if (ph < pNormMin || ph > pNormMax) return {'color': Colors.orange, 'icon': '⚠️', 'msg': '[$fish] CLASSIFICATION: pH Level Imbalance'};
    if (temp < tNormMin || temp > tNormMax) return {'color': Colors.orange, 'icon': '⚠️', 'msg': '[$fish] CLASSIFICATION: Temperature Stress'};
    if (temp >= tNormMin && temp <= tNormMax && ph >= pNormMin && ph <= pNormMax && turb <= tbNormMax) {
      return {'color': Colors.green, 'icon': '✅', 'msg': '[$fish] CLASSIFICATION: Optimal Environment'};
    }
    return {'color': Colors.blue, 'icon': 'ℹ️', 'msg': '[$fish] CLASSIFICATION: System Stable'};
  }

  Widget _buildMetricCard(String title, String value, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: isDark ? [] : [BoxShadow(color: const Color(0xFF0284C7).withOpacity(0.06), blurRadius: 16, offset: const Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B))),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: isDark ? Colors.white : const Color(0xFF0F172A))),
        ],
      ),
    );
  }

  Widget _buildSpecColumn(String title, String value, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B))),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: isDark ? Colors.white : const Color(0xFF0F172A))),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        Icon(Icons.square, color: color, size: 12),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
      ],
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
    
    double length = (_device?['length'] as num?)?.toDouble() ?? 0.0;
    double width = (_device?['width'] as num?)?.toDouble() ?? 0.0;
    double depth = (_device?['depth'] as num?)?.toDouble() ?? 0.0;
    int fishCount = (_device?['fish_count'] as num?)?.toInt() ?? 0;
    String fishType = _device?['fish_type'] ?? 'Tilapia';
    double volume = length * width * depth;
    
    final aiStatus = _evaluateEnvironment(temp, ph, turb, _device);

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          if (_weather != null) ...[
            Text("🌤️ Local Weather (${_device?['location'] ?? 'Angono, Rizal'})", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
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
          
          Text("📡 Live Readings & AI Engine ($fishType)", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
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

          Text("📏 Pond Specifications", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: isDark ? [] : [BoxShadow(color: const Color(0xFF0284C7).withOpacity(0.06), blurRadius: 16, offset: const Offset(0, 8))],
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildSpecColumn("Species", fishType, isDark),
                _buildSpecColumn("Dimensions", "${length}m x ${width}m x ${depth}m", isDark),
                _buildSpecColumn("Volume", "${volume.toStringAsFixed(1)} m³", isDark),
                _buildSpecColumn("Livestock", "$fishCount Fish", isDark),
              ],
            ),
          ),
          const SizedBox(height: 24),

          Text("📈 Trend Analytics: ${_device!['pond_name']}", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 10),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: isDark ? [] : [BoxShadow(color: const Color(0xFF0284C7).withOpacity(0.06), blurRadius: 16, offset: const Offset(0, 8))],
            ),
            child: _history.isEmpty 
              ? const Center(child: Text("No historical data available."))
              : SizedBox(
                  height: 200,
                  child: LineChart(
                    LineChartData(
                      gridData: const FlGridData(show: false),
                      titlesData: const FlTitlesData(show: false),
                      borderData: FlBorderData(show: false),
                      lineBarsData: [
                        LineChartBarData(
                          spots: _history.reversed.toList().asMap().entries.map((e) => FlSpot(e.key.toDouble(), (e.value['temperature'] as num).toDouble())).toList(),
                          isCurved: true, color: Colors.redAccent, barWidth: 3, dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(show: true, gradient: LinearGradient(colors: [Colors.redAccent.withOpacity(0.4), Colors.transparent], begin: Alignment.topCenter, end: Alignment.bottomCenter)),
                        ),
                        LineChartBarData(
                          spots: _history.reversed.toList().asMap().entries.map((e) => FlSpot(e.key.toDouble(), (e.value['ph'] as num).toDouble())).toList(),
                          isCurved: true, color: Colors.greenAccent, barWidth: 3, dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(show: true, gradient: LinearGradient(colors: [Colors.greenAccent.withOpacity(0.4), Colors.transparent], begin: Alignment.topCenter, end: Alignment.bottomCenter)),
                        ),
                        LineChartBarData(
                          spots: _history.reversed.toList().asMap().entries.map((e) => FlSpot(e.key.toDouble(), (e.value['turbidity'] as num).toDouble())).toList(),
                          isCurved: true, color: Colors.orangeAccent, barWidth: 3, dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(show: true, gradient: LinearGradient(colors: [Colors.orangeAccent.withOpacity(0.4), Colors.transparent], begin: Alignment.topCenter, end: Alignment.bottomCenter)),
                        ),
                        LineChartBarData(
                          spots: _history.reversed.toList().asMap().entries.map((e) => FlSpot(e.key.toDouble(), (e.value['water_level_cm'] as num).toDouble())).toList(),
                          isCurved: true, color: Colors.blueAccent, barWidth: 3, dotData: const FlDotData(show: false),
                          belowBarData: BarAreaData(show: true, gradient: LinearGradient(colors: [Colors.blueAccent.withOpacity(0.4), Colors.transparent], begin: Alignment.topCenter, end: Alignment.bottomCenter)),
                        ),
                      ],
                    ),
                  ),
                ),
          ),
          const SizedBox(height: 10),
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.circle, color: Colors.redAccent, size: 12), SizedBox(width: 4), Text("Temp"),
              SizedBox(width: 12),
              Icon(Icons.circle, color: Colors.greenAccent, size: 12), SizedBox(width: 4), Text("pH"),
              SizedBox(width: 12),
              Icon(Icons.circle, color: Colors.orangeAccent, size: 12), SizedBox(width: 4), Text("Turb"),
              SizedBox(width: 12),
              Icon(Icons.circle, color: Colors.blueAccent, size: 12), SizedBox(width: 4), Text("Lvl"),
            ],
          ),
          const SizedBox(height: 24),

          if (widget.userData['role'] == 'admin' && _allDevices.isNotEmpty) ...[
            Text("🚨 Network Priority (Risk Ranked)", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E293B) : Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: isDark ? [] : [BoxShadow(color: primaryColor.withOpacity(0.06), blurRadius: 16, offset: const Offset(0, 8))],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      _buildLegendItem("Stable", Colors.green),
                      const SizedBox(width: 8),
                      _buildLegendItem("Warning", Colors.orangeAccent),
                      const SizedBox(width: 8),
                      _buildLegendItem("Critical", Colors.redAccent),
                    ],
                  ),
                  const SizedBox(height: 16),
                  
                  ..._allDevices.map((dev) {
                    final sn = dev['device_sn'];
                    final score = _getRiskScore(_allLatestReadings[sn], dev);
                    final style = _getRiskStyling(score);
                    final barColor = style['color'] as Color;
                    
                    double fillPercentage = 0.0;
                    int displayPercent = 0;
                    if (score == 3) { fillPercentage = 1.0; displayPercent = 100; }
                    else if (score == 2) { fillPercentage = 0.66; displayPercent = 66; }
                    else if (score == 1) { fillPercentage = 0.33; displayPercent = 33; }
                    else { fillPercentage = 0.1; displayPercent = 0; }

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: Row(
                        children: [
                          Expanded(
                            flex: 3,
                            child: Text(
                              "Farmer ${dev['owner_id']} (${dev['fish_type'] ?? 'Tilapia'})",
                              style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            flex: 7,
                            child: Stack(
                              children: [
                                Container(height: 18, decoration: BoxDecoration(color: barColor.withOpacity(0.1), borderRadius: BorderRadius.circular(4))),
                                FractionallySizedBox(
                                  widthFactor: fillPercentage,
                                  child: Container(
                                    height: 18,
                                    alignment: Alignment.centerRight,
                                    padding: const EdgeInsets.only(right: 6),
                                    decoration: BoxDecoration(
                                      borderRadius: BorderRadius.circular(8),
                                      gradient: LinearGradient(
                                        begin: Alignment.topCenter,
                                        end: Alignment.bottomCenter,
                                        colors: [barColor.withOpacity(0.6), barColor, barColor.withOpacity(0.9)],
                                      ),
                                      boxShadow: [BoxShadow(color: barColor.withOpacity(0.4), blurRadius: 4, offset: const Offset(0, 3))],
                                    ),
                                    child: Text(
                                      "$displayPercent%",
                                      style: const TextStyle(
                                        fontSize: 10, fontWeight: FontWeight.w900, color: Colors.white,
                                        shadows: [Shadow(color: Colors.black45, blurRadius: 2, offset: Offset(1, 1))]
                                      )
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ],
              ),
            ),
            const SizedBox(height: 24),
          ]
        ],
      ),
    );
  }
}