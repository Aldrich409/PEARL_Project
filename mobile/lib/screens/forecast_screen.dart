import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math';
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
  String? _activeDeviceSn;
  Map<String, dynamic>? _device;
  List<dynamic> _history = [];
  List<Map<String, dynamic>> _forecastData = [];

  final List<String> _months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  @override
  void initState() {
    super.initState();
    _generateMockForecast();
    _loadData();
  }

  @override
  void didUpdateWidget(covariant ForecastScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.activeDeviceSn != widget.activeDeviceSn) {
      _loadData();
    }
  }

  void _generateMockForecast() {
    final random = Random();
    _forecastData = List.generate(7, (index) => {
      'day': index.toDouble(),
      'temp': 28.0 + random.nextDouble() * 3,     
      'ph': 7.0 + random.nextDouble() * 1.5,      
      'rain_mm': random.nextDouble() * 25,        
      'rain_prob': random.nextDouble() * 100,     
    });
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
    
    if (devices.isNotEmpty) {
      _device = devices.firstWhere((d) => d['device_sn'] == widget.activeDeviceSn, orElse: () => devices[0]);
      _activeDeviceSn = _device!['device_sn'];
      _history = await ApiService.getHistory(_activeDeviceSn!, limit: 30) ?? [];
    }
    if (mounted) setState(() => _isLoading = false);
  }

  // 🚀 NEW: Formats Dates for the X-Axis of the "Past 30 Days" Chart
  SideTitles _getHistoryDateTitles(double interval) {
    return SideTitles(
      showTitles: true,
      reservedSize: 22,
      interval: interval,
      getTitlesWidget: (value, meta) {
        // Value is the index (0 to length-1). Map it backwards from today.
        int daysAgo = (_history.length - 1) - value.toInt();
        if (daysAgo < 0) return const SizedBox.shrink();
        final date = DateTime.now().subtract(Duration(days: daysAgo));
        
        return Padding(
          padding: const EdgeInsets.only(top: 6.0),
          child: Text("${_months[date.month - 1]}\n${date.day}", textAlign: TextAlign.center, style: const TextStyle(fontSize: 8, color: Colors.grey, fontWeight: FontWeight.bold, height: 1.1)),
        );
      },
    );
  }

  // 🚀 NEW: Formats Dates for the X-Axis of the 7-Day Forecast Charts
  SideTitles _getForecastDateTitles(double interval) {
    return SideTitles(
      showTitles: true,
      reservedSize: 22,
      interval: interval,
      getTitlesWidget: (value, meta) {
        final date = DateTime.now().add(Duration(days: value.toInt()));
        return Padding(
          padding: const EdgeInsets.only(top: 6.0),
          child: Text("${_months[date.month - 1]}\n${date.day}", textAlign: TextAlign.center, style: const TextStyle(fontSize: 8, color: Colors.grey, fontWeight: FontWeight.bold, height: 1.1)),
        );
      },
    );
  }

  SideTitles _getLeftTitles(double interval) {
    return SideTitles(
      showTitles: true,
      reservedSize: 26,
      interval: interval,
      getTitlesWidget: (value, meta) => Text(value.toInt().toString(), style: const TextStyle(fontSize: 9, color: Colors.grey, fontWeight: FontWeight.bold)),
    );
  }

  Widget _buildChartContainer(String title, Widget chart, bool isDark, Color primaryColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: primaryColor), maxLines: 1, overflow: TextOverflow.ellipsis),
        const SizedBox(height: 8),
        Container(
          height: 180,
          padding: const EdgeInsets.only(right: 12, left: 4, top: 16, bottom: 8),
          decoration: BoxDecoration(
            color: isDark ? const Color(0xFF1E293B) : Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: isDark ? [] : [BoxShadow(color: primaryColor.withOpacity(0.06), blurRadius: 16, offset: const Offset(0, 8))],
          ),
          child: chart,
        ),
      ],
    );
  }

  String _formatDate(int daysFromNow) {
    final date = DateTime.now().add(Duration(days: daysFromNow));
    return "${_months[date.month - 1]} ${date.day}, ${date.year}";
  }

  Map<String, dynamic> _getForecastAction(double temp, double ph, double rainProb) {
    if (rainProb > 80) return {'color': Colors.blueAccent, 'status': 'Heavy Rain Risk', 'msg': 'High probability of heavy rainfall. Secure pond boundaries, check overflow pipes, and temporarily reduce feeding to prevent water fouling.'};
    if (ph < 6.5 || ph > 9.0) return {'color': Colors.redAccent, 'status': 'Critical pH Warning', 'msg': 'Severe pH shift predicted. Prepare agricultural lime (calcium carbonate) or water buffers immediately.'};
    if (temp < 24 || temp > 35) return {'color': Colors.redAccent, 'status': 'Temperature Stress', 'msg': 'Extreme temperature shift expected. Monitor fish behavior closely and adjust aeration systems.'};
    if (ph < 7.0 || ph > 8.5) return {'color': Colors.orangeAccent, 'status': 'pH Imbalance', 'msg': 'Slight pH imbalance expected. Monitor water quality and prepare for minor adjustments.'};
    if (temp < 26 || temp > 33) return {'color': Colors.orangeAccent, 'status': 'Mild Temp Shift', 'msg': 'Water temperatures are approaching limits. Maintain standard aeration.'};
    return {'color': Colors.green, 'status': 'Optimal Breeding', 'msg': 'Conditions are ideal for spawning. Maintain current feed rate and minimize pond disturbances.'};
  }

  Widget _buildLegendItem(String label, Color color, {bool isDashed = false}) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        isDashed 
          ? Text("---", style: TextStyle(color: color, fontWeight: FontWeight.bold, letterSpacing: -1))
          : Icon(Icons.circle, color: color, size: 8),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 8, fontWeight: FontWeight.bold)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_activeDeviceSn == null) return const Center(child: Text("No assigned pond nodes."));

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;
    final gridData = FlGridData(show: true, drawVerticalLine: false, getDrawingHorizontalLine: (value) => FlLine(color: Colors.grey.withOpacity(0.15), strokeWidth: 1));

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          Text("🤖 AI Breeding Forecast", style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: primaryColor)),
          const SizedBox(height: 4),
          Text("Predictive analytics for ${_device!['pond_name']}", style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: isDark ? Colors.white70 : Colors.black54)),
          const SizedBox(height: 24),

          // ROW 1: HISTORY & FORECAST
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  children: [
                    _buildChartContainer("📅 Past 30 Days", _history.isEmpty ? const Center(child: Text("No data.", style: TextStyle(fontSize: 10)))
                      : LineChart(LineChartData(gridData: gridData, titlesData: FlTitlesData(rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), bottomTitles: AxisTitles(sideTitles: _getHistoryDateTitles(10)), leftTitles: AxisTitles(sideTitles: _getLeftTitles(5))), borderData: FlBorderData(show: false), lineBarsData: [
                          LineChartBarData(spots: _history.reversed.toList().asMap().entries.map((e) => FlSpot(e.key.toDouble(), (e.value['temperature'] as num).toDouble())).toList(), isCurved: true, color: Colors.cyanAccent, barWidth: 2, dotData: const FlDotData(show: false)),
                          LineChartBarData(spots: _history.reversed.toList().asMap().entries.map((e) => FlSpot(e.key.toDouble(), (e.value['ph'] as num).toDouble())).toList(), isCurved: true, color: Colors.greenAccent, barWidth: 2, dotData: const FlDotData(show: false)),
                        ])), isDark, primaryColor),
                    const SizedBox(height: 4),
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [_buildLegendItem("Temp", Colors.cyanAccent), const SizedBox(width: 12), _buildLegendItem("pH", Colors.greenAccent)]),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  children: [
                    _buildChartContainer("🔮 Next 7 Days", LineChart(LineChartData(gridData: gridData, titlesData: FlTitlesData(rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), bottomTitles: AxisTitles(sideTitles: _getForecastDateTitles(2)), leftTitles: AxisTitles(sideTitles: _getLeftTitles(5))), borderData: FlBorderData(show: false), lineBarsData: _forecastData.isEmpty ? [] : [
                          LineChartBarData(spots: _forecastData.map((e) => FlSpot(e['day'], e['temp'])).toList(), isCurved: true, color: Colors.orangeAccent, barWidth: 2, dashArray: [5, 5], dotData: const FlDotData(show: true, getDotPainter: _defaultDot)),
                          LineChartBarData(spots: _forecastData.map((e) => FlSpot(e['day'], e['ph'])).toList(), isCurved: true, color: Colors.blueAccent, barWidth: 2, dashArray: [5, 5], dotData: const FlDotData(show: true, getDotPainter: _defaultDot)),
                        ])), isDark, primaryColor),
                    const SizedBox(height: 4),
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [_buildLegendItem("Pred Temp", Colors.orangeAccent, isDashed: true), const SizedBox(width: 8), _buildLegendItem("Pred pH", Colors.blueAccent, isDashed: true)]),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // ROW 2: WEATHER & PROBABILITY
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  children: [
                    _buildChartContainer("🌧️ Rainfall (mm)", BarChart(BarChartData(gridData: gridData, titlesData: FlTitlesData(rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), bottomTitles: AxisTitles(sideTitles: _getForecastDateTitles(2)), leftTitles: AxisTitles(sideTitles: _getLeftTitles(10))), borderData: FlBorderData(show: false), barGroups: _forecastData.map((e) => BarChartGroupData(x: e['day'].toInt(), barRods: [BarChartRodData(toY: e['rain_mm'], color: Colors.blueAccent, width: 8, borderRadius: const BorderRadius.vertical(top: Radius.circular(4)))])).toList())), isDark, primaryColor),
                    const SizedBox(height: 4),
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [_buildLegendItem("Rainfall", Colors.blueAccent)]),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  children: [
                    _buildChartContainer("☔ Rain Risk (%)", LineChart(LineChartData(minY: 0, maxY: 100, gridData: gridData, titlesData: FlTitlesData(rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)), bottomTitles: AxisTitles(sideTitles: _getForecastDateTitles(2)), leftTitles: AxisTitles(sideTitles: _getLeftTitles(25))), borderData: FlBorderData(show: false), lineBarsData: _forecastData.isEmpty ? [] : [
                          LineChartBarData(spots: _forecastData.map((e) => FlSpot(e['day'], e['rain_prob'])).toList(), isCurved: true, color: Colors.blue, barWidth: 2, dotData: const FlDotData(show: false), belowBarData: BarAreaData(show: true, color: Colors.blue.withOpacity(0.3))),
                        ])), isDark, primaryColor),
                    const SizedBox(height: 4),
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [_buildLegendItem("Probability", Colors.blue)]),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 32),

          // 7-DAY ACTION PLAN
          Text("📋 7-Day Action Plan / Susunod na Linggo", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          
          ..._forecastData.asMap().entries.map((entry) {
            final int index = entry.key;
            final data = entry.value;
            final String dateStr = _formatDate(index); 
            final action = _getForecastAction(data['temp'], data['ph'], data['rain_prob']);
            final Color statusColor = action['color'];

            return Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1E293B) : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border(left: BorderSide(color: statusColor, width: 4)), 
                boxShadow: isDark ? [] : [BoxShadow(color: primaryColor.withOpacity(0.06), blurRadius: 10, offset: const Offset(0, 4))],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(dateStr, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: isDark ? Colors.white : Colors.black87)),
                      Text("${action['status']}", style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: statusColor)),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildMiniMetric("Temp", "${data['temp'].toStringAsFixed(1)}°C", isDark),
                      const SizedBox(width: 12),
                      _buildMiniMetric("pH", data['ph'].toStringAsFixed(1), isDark),
                      const SizedBox(width: 12),
                      _buildMiniMetric("Rain", "${data['rain_prob'].toStringAsFixed(0)}%", isDark),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(action['msg'], style: TextStyle(fontSize: 12, height: 1.4, color: isDark ? Colors.white70 : Colors.black87)),
                ],
              ),
            );
          }),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildMiniMetric(String label, String value, bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: isDark ? Colors.black26 : Colors.grey.shade100, borderRadius: BorderRadius.circular(6)),
      child: Text("$label: $value", style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}

FlDotPainter _defaultDot(FlSpot spot, double xPercentage, LineChartBarData bar, int index) {
  return FlDotCirclePainter(radius: 2, color: bar.color ?? Colors.white, strokeWidth: 1, strokeColor: Colors.white);
}