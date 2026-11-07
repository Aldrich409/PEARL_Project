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
  final Map<String, dynamic> _allLatestReadings = {};

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
          double scoreA = _calculateContinuousRiskScore(_allLatestReadings[a['device_sn']]);
          double scoreB = _calculateContinuousRiskScore(_allLatestReadings[b['device_sn']]);
          return scoreB.compareTo(scoreA);
        });
      }
    }
    if (mounted) setState(() => _isLoading = false);
  }

  double _calculateContinuousRiskScore(Map<String, dynamic>? reading) {
    if (reading == null) return 0;
    double temp = (reading['temperature'] as num).toDouble();
    double ph = (reading['ph'] as num).toDouble();
    double turb = (reading['turbidity'] as num).toDouble();

    double score = 0;
    if (temp < 26 || temp > 33) {
      score += 40;
    }
    else if (temp < 28 || temp > 31) {
      score += 20;
    }
    
    if (ph < 6.5 || ph > 9.0) {
      score += 50;
    } else if (ph < 7.0 || ph > 8.5) {
      score += 20;
    }
    
    if (turb > 100) {
      score += 40;
    } else if (turb > 80) {
      score += 20;
    }
    
    return score > 100 ? 100 : score;
  }

  Map<String, dynamic> _getRiskStyling(double score) {
    if (score >= 50) return {'color': Colors.redAccent, 'label': 'Danger'};
    if (score >= 20) return {'color': Colors.orangeAccent, 'label': 'Warning'};
    return {'color': Colors.green, 'label': 'Stable'};
  }

  Map<String, dynamic> _evaluateEnvironment(double temp, double ph, double turb) {
    if (turb > 100) return {'color': Colors.red, 'icon': '🚨', 'msg': 'High Algal Bloom Risk (PANGANIB)'};
    if (ph < 6.5 || ph > 9.0) return {'color': Colors.red, 'icon': '🚨', 'msg': 'Critical Water Warning (PANGANIB)'};
    if (temp < 24 || temp > 35) return {'color': Colors.red, 'icon': '🚨', 'msg': 'Extreme Temperature (PANGANIB)'};
    if (turb > 80) return {'color': Colors.orange, 'icon': '⚠️', 'msg': 'Approaching High Turbidity (BABALA)'};
    if (ph < 7.0 || ph > 8.5) return {'color': Colors.orange, 'icon': '⚠️', 'msg': 'pH Level Imbalance (BABALA)'};
    if (temp < 26 || temp > 33) return {'color': Colors.orange, 'icon': '⚠️', 'msg': 'Temperature Stress (BABALA)'};
    if (temp >= 28 && temp <= 31 && ph >= 7.0 && ph <= 8.5 && turb <= 80) {
      return {'color': Colors.green, 'icon': '✅', 'msg': 'Optimal Breeding Environment'};
    }
    return {'color': Colors.blue, 'icon': 'ℹ️', 'msg': 'System Stable'};
  }

  Widget _buildMetricCard(String title, String value, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
        boxShadow: isDark ? [] : [BoxShadow(color: Colors.black.withValues(alpha: 0.02), blurRadius: 4, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B))),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: isDark ? Colors.white : const Color(0xFF0F172A))),
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
    
    final aiStatus = _evaluateEnvironment(temp, ph, turb);

    List<FlSpot> tempSpots = [];
    List<FlSpot> phSpots = [];
    List<FlSpot> riskSpots = [];
    List<BarChartGroupData> turbBars = [];

    if (_history.isNotEmpty) {
      final chronologicalHistory = _history.reversed.toList();
      for (int i = 0; i < chronologicalHistory.length; i++) {
        var item = chronologicalHistory[i];
        double t = (item['temperature'] as num).toDouble();
        double p = (item['ph'] as num).toDouble();
        double tb = (item['turbidity'] as num).toDouble();
        double r = _calculateContinuousRiskScore(item);
        
        tempSpots.add(FlSpot(i.toDouble(), t));
        phSpots.add(FlSpot(i.toDouble(), p));
        riskSpots.add(FlSpot(i.toDouble(), r));
        turbBars.add(BarChartGroupData(
          x: i,
          barRods: [BarChartRodData(toY: tb, color: tb > 80 ? Colors.orange : const Color(0xFF93C5FD), width: 8, borderRadius: BorderRadius.circular(3))]
        ));
      }
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // =========================================================
          // 0. LOCAL WEATHER BANNER (RESTORED)
          // =========================================================
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
          
          Text("📡 Live Readings & AI Engine", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: (aiStatus['color'] as Color).withValues(alpha: 0.15),
              border: Border(left: BorderSide(color: aiStatus['color'], width: 4)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Text(aiStatus['icon'], style: const TextStyle(fontSize: 24)),
                const SizedBox(width: 12),
                Expanded(child: Text(aiStatus['msg'], style: TextStyle(fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87))),
              ],
            ),
          ),
          const SizedBox(height: 16),
          
          // 2x2 LIVE METRICS GRID
          Row(
            children: [
              Expanded(child: _buildMetricCard("WATER TEMP (°C)", "$temp", isDark)),
              const SizedBox(width: 8),
              Expanded(child: _buildMetricCard("pH LEVEL", "$ph", isDark)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _buildMetricCard("TURBIDITY (NTU)", "$turb", isDark)),
              const SizedBox(width: 8),
              Expanded(child: _buildMetricCard("WATER LEVEL (cm)", "$lvl", isDark)),
            ],
          ),
          const SizedBox(height: 24),

          // =========================================================
          // 1. HISTORICAL CONDITIONS CHART (Separated Card)
          // =========================================================
          Text("📈 Historical conditions", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          Text("Temperature and pH trends • dual-axis", style: TextStyle(fontSize: 12, color: isDark ? Colors.grey : const Color(0xFF64748B))),
          const SizedBox(height: 12),
          Container(
            height: 220,
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 10),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
            ),
            child: tempSpots.isEmpty ? const Center(child: Text("No data")) : LineChart(
              LineChartData(
                gridData: const FlGridData(show: true, drawVerticalLine: false),
                titlesData: const FlTitlesData(
                  topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)))),
                lineBarsData: [
                  LineChartBarData(spots: tempSpots, isCurved: true, color: const Color(0xFFEF4444), barWidth: 2.5, dotData: const FlDotData(show: false)),
                  LineChartBarData(spots: phSpots, isCurved: true, color: const Color(0xFF0EA5E9), barWidth: 2.5, dotData: const FlDotData(show: false)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          const Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.circle, color: Color(0xFFEF4444), size: 10), SizedBox(width: 4), Text("Temp", style: TextStyle(fontSize: 11)),
              SizedBox(width: 16),
              Icon(Icons.circle, color: Color(0xFF0EA5E9), size: 10), SizedBox(width: 4), Text("pH", style: TextStyle(fontSize: 11)),
            ],
          ),
          const SizedBox(height: 24),

          // =========================================================
          // 2. WATER QUALITY RISK TREND CHART (Separated Card)
          // =========================================================
          Text("📊 Water quality risk trend", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          Container(
            height: 240,
            padding: const EdgeInsets.only(top: 20, bottom: 10, left: 10, right: 10),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
            ),
            child: riskSpots.isEmpty ? const Center(child: Text("No data")) : LineChart(
              LineChartData(
                minY: 0, maxY: 100,
                gridData: const FlGridData(show: false),
                titlesData: const FlTitlesData(
                  topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)))),
                extraLinesData: ExtraLinesData(
                  horizontalLines: [
                    HorizontalLine(y: 10, color: const Color(0xFF10B981).withValues(alpha: 0.15), strokeWidth: 20, label: HorizontalLineLabel(show: true, alignment: Alignment.topLeft, padding: const EdgeInsets.only(left: 4, bottom: 4), labelResolver: (_) => 'Optimal', style: const TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold))),
                    HorizontalLine(y: 35, color: const Color(0xFFF59E0B).withValues(alpha: 0.15), strokeWidth: 30, label: HorizontalLineLabel(show: true, alignment: Alignment.topLeft, padding: const EdgeInsets.only(left: 4, bottom: 4), labelResolver: (_) => 'Warning', style: const TextStyle(color: Color(0xFFF59E0B), fontSize: 10, fontWeight: FontWeight.bold))),
                    HorizontalLine(y: 75, color: const Color(0xFFEF4444).withValues(alpha: 0.15), strokeWidth: 50, label: HorizontalLineLabel(show: true, alignment: Alignment.topLeft, padding: const EdgeInsets.only(left: 4, bottom: 4), labelResolver: (_) => 'Critical', style: const TextStyle(color: Color(0xFFEF4444), fontSize: 10, fontWeight: FontWeight.bold))),
                  ],
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: riskSpots, isCurved: true, 
                    color: isDark ? Colors.white : const Color(0xFF1E293B), 
                    barWidth: 2.5, dotData: const FlDotData(show: false)
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // =========================================================
          // 3. TURBIDITY BY DAY CHART (Separated Card)
          // =========================================================
          Text("🌊 Turbidity by day", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          Container(
            height: 220,
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 10),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
            ),
            child: turbBars.isEmpty ? const Center(child: Text("No data")) : BarChart(
              BarChartData(
                gridData: const FlGridData(show: true, drawVerticalLine: false),
                titlesData: const FlTitlesData(
                  topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)))),
                barGroups: turbBars,
              ),
            ),
          ),
          const SizedBox(height: 24),

          // POND SPECIFICATIONS
          Text("📏 Pond Specifications", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF1E293B) : Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildSpecColumn("Species", fishType, isDark),
                    _buildSpecColumn("Dimensions", "${length}x${width}x${depth}m", isDark),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildSpecColumn("Volume", "${volume.toStringAsFixed(1)} m³", isDark),
                    _buildSpecColumn("Livestock", "$fishCount Fish", isDark),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ADMIN NETWORK PRIORITY
          if (widget.userData['role'] == 'admin' && _allDevices.isNotEmpty) ...[
            Text("🚨 Network Risk Rankings", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E293B) : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: _allDevices.map((dev) {
                  final sn = dev['device_sn'];
                  final score = _calculateContinuousRiskScore(_allLatestReadings[sn]);
                  final style = _getRiskStyling(score);
                  final barColor = style['color'] as Color;
                  
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: Row(
                      children: [
                        Expanded(
                          flex: 3,
                          child: Text(
                            "F${dev['owner_id']} (${dev['pond_name']})",
                            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          flex: 7,
                          child: Stack(
                            children: [
                              Container(height: 18, decoration: BoxDecoration(color: barColor.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(4))),
                              FractionallySizedBox(
                                widthFactor: (score / 100).clamp(0.05, 1.0),
                                child: Container(
                                  height: 18,
                                  alignment: Alignment.centerRight,
                                  padding: const EdgeInsets.only(right: 6),
                                  decoration: BoxDecoration(
                                    borderRadius: BorderRadius.circular(4),
                                    color: barColor,
                                  ),
                                  child: Text(
                                    "${score.toInt()}",
                                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: Colors.white),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 24),
          ]
        ],
      ),
    );
  }
}