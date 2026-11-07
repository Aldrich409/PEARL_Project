import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
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
  List<dynamic> _history = [];
  List<dynamic> _forecasts = [];
  Map<String, dynamic>? _weatherDaily;

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

  Future<void> _fetch7DayWeather() async {
    const lat = 14.5264;
    const lon = 121.1558;
    final url = Uri.parse(
        "https://api.open-meteo.com/v1/forecast?latitude=$lat&longitude=$lon&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max&timezone=Asia%2FManila");
    try {
      final response = await http.get(url).timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _weatherDaily = data['daily'];
      }
    } catch (e) {
      debugPrint("Weather fetch failed: $e");
    }
  }

  Future<void> _loadData() async {
    if (widget.activeDeviceSn == null) {
      setState(() => _isLoading = false);
      return;
    }

    setState(() => _isLoading = true);

    try {
      // NOTE: Ensure you have getForecast added to your api_service.dart
      final results = await Future.wait([
        ApiService.getHistory(widget.activeDeviceSn!, limit: 120),
        ApiService.getForecast(widget.activeDeviceSn!, days: 7), // Assuming this exists in ApiService
        _fetch7DayWeather(),
      ]);

      _history = results[0] as List<dynamic>? ?? [];
      _forecasts = results[1] as List<dynamic>? ?? [];
    } catch (e) {
      debugPrint("Error loading forecast data: $e");
    }

    if (mounted) setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (widget.activeDeviceSn == null) {
      return const Center(child: Text("Please select a device node from the sidebar."));
    }

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // HEADER
          const Text("🤖 Breeding Forecast", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const Text(
            "Suriin ang nakaraang 1 buwan at asahan ang susunod na 7 araw",
            style: TextStyle(fontSize: 12, color: Colors.grey),
          ),
          const SizedBox(height: 24),

          // 1. PAST 30 DAYS CHART
          Text("📊 Past 30 Days", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          _buildHistoricalChart(isDark),
          const SizedBox(height: 24),

          // 2. FORECAST 7 DAYS CHART
          Text("🔮 Forecast Next 7 Days", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          _buildForecastChart(isDark),
          const SizedBox(height: 24),
          const Divider(),

          // 3. WEATHER INTEGRATION
          if (_weatherDaily != null && _weatherDaily!['time'] != null) ...[
            const SizedBox(height: 12),
            Text("🌤️ 7-Day Weather & Rain", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
            const Text("External weather directly impacts pond water.", style: TextStyle(fontSize: 12, color: Colors.grey)),
            const SizedBox(height: 12),
            _buildWeatherTempChart(isDark),
            const SizedBox(height: 16),
            _buildRainProbabilityChart(isDark),
            const SizedBox(height: 24),
            const Divider(),
          ],

          // 4. ACTION PLAN CARDS
          const SizedBox(height: 12),
          Text("📋 7-Day Action Plan", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 16),
          if (_forecasts.isEmpty)
            const Text("Insufficient telemetry records for Meta Prophet forecasting.", style: TextStyle(fontStyle: FontStyle.italic)),
          ..._forecasts.map((day) => _buildActionCard(day, isDark)),
        ],
      ),
    );
  }

  // =========================================================================
  // CHART BUILDERS
  // =========================================================================

  Widget _buildHistoricalChart(bool isDark) {
    if (_history.isEmpty) return _emptyChartContainer(isDark);

    List<FlSpot> tempSpots = [];
    List<FlSpot> phSpots = [];
    final chronological = _history.reversed.toList();

    for (int i = 0; i < chronological.length; i++) {
      double t = (chronological[i]['temperature'] as num).toDouble();
      double p = (chronological[i]['ph'] as num).toDouble();
      tempSpots.add(FlSpot(i.toDouble(), t));
      phSpots.add(FlSpot(i.toDouble(), p));
    }

    return _buildChartContainer(
      isDark,
      LineChart(
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
            LineChartBarData(spots: phSpots, isCurved: true, color: const Color(0xFF0284C7), barWidth: 2.5, dotData: const FlDotData(show: false)),
          ],
        ),
      ),
      legend: _buildLegendItem("Temp", const Color(0xFFEF4444), "pH", const Color(0xFF0284C7)),
    );
  }

  Widget _buildForecastChart(bool isDark) {
    if (_forecasts.isEmpty) return _emptyChartContainer(isDark);

    List<FlSpot> fTempSpots = [];
    List<FlSpot> fPhSpots = [];

    for (int i = 0; i < _forecasts.length; i++) {
      double t = (_forecasts[i]['predicted_temperature'] as num).toDouble();
      double p = (_forecasts[i]['predicted_ph'] as num).toDouble();
      fTempSpots.add(FlSpot(i.toDouble(), t));
      fPhSpots.add(FlSpot(i.toDouble(), p));
    }

    return _buildChartContainer(
      isDark,
      LineChart(
        LineChartData(
          gridData: const FlGridData(show: true, drawVerticalLine: false),
          titlesData: const FlTitlesData(
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)))),
          lineBarsData: [
            // Using dashArray for dashed lines!
            LineChartBarData(spots: fTempSpots, isCurved: true, color: const Color(0xFFF59E0B), barWidth: 2.5, dashArray: [5, 5], dotData: const FlDotData(show: true)),
            LineChartBarData(spots: fPhSpots, isCurved: true, color: const Color(0xFF0EA5E9), barWidth: 2.5, dashArray: [5, 5], dotData: const FlDotData(show: true)),
          ],
        ),
      ),
      legend: _buildLegendItem("Pred Temp", const Color(0xFFF59E0B), "Pred pH", const Color(0xFF0EA5E9)),
    );
  }

  Widget _buildWeatherTempChart(bool isDark) {
    List<FlSpot> maxSpots = [];
    List<FlSpot> minSpots = [];
    List<dynamic> maxT = _weatherDaily!['temperature_2m_max'];
    List<dynamic> minT = _weatherDaily!['temperature_2m_min'];

    for (int i = 0; i < maxT.length; i++) {
      maxSpots.add(FlSpot(i.toDouble(), (maxT[i] as num).toDouble()));
      minSpots.add(FlSpot(i.toDouble(), (minT[i] as num).toDouble()));
    }

    return _buildChartContainer(
      isDark,
      LineChart(
        LineChartData(
          gridData: const FlGridData(show: true, drawVerticalLine: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)))),
          lineBarsData: [
            LineChartBarData(spots: maxSpots, isCurved: true, color: const Color(0xFFEF4444), barWidth: 2.5),
            LineChartBarData(spots: minSpots, isCurved: true, color: const Color(0xFFF59E0B), barWidth: 2.5),
          ],
        ),
      ),
      title: "Max/Min Air Temp (°C)",
      legend: _buildLegendItem("Max", const Color(0xFFEF4444), "Min", const Color(0xFFF59E0B)),
    );
  }

  Widget _buildRainProbabilityChart(bool isDark) {
    List<FlSpot> probSpots = [];
    List<dynamic> prob = _weatherDaily!['precipitation_probability_max'];

    for (int i = 0; i < prob.length; i++) {
      probSpots.add(FlSpot(i.toDouble(), (prob[i] as num).toDouble()));
    }

    return _buildChartContainer(
      isDark,
      LineChart(
        LineChartData(
          minY: 0, maxY: 100,
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: true, border: Border(bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)))),
          lineBarsData: [
            LineChartBarData(
              spots: probSpots, 
              isCurved: true, 
              color: const Color(0xFF0284C7), 
              barWidth: 2,
              belowBarData: BarAreaData(show: true, color: const Color(0xFF0284C7).withValues(alpha :0.2)),
            ),
          ],
        ),
      ),
      title: "Rain Probability Risk (%)",
    );
  }

  // =========================================================================
  // ACTION PLAN CARD BUILDER
  // =========================================================================

  Widget _buildActionCard(Map<String, dynamic> day, bool isDark) {
    String status = day['status'] ?? '';
    String rawAction = day['action_required'] ?? '';
    List<String> actionParts = rawAction.split("\n");
    String engAction = actionParts.isNotEmpty ? actionParts[0] : "";
    String tagAction = actionParts.length > 1 ? actionParts[1] : "";

    Color cardColor;
    Color accentColor;

    if (status.contains("Optimal") || status.contains("Stable") || status.contains("Magandang")) {
      accentColor = const Color(0xFF10B981);
    } else if (status.contains("Warning") || status.contains("Risk") || status.contains("BABALA")) {
      accentColor = const Color(0xFFF59E0B);
    } else {
      accentColor = const Color(0xFFEF4444);
    }
    cardColor = accentColor.withValues(alpha :0.15);

    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
        boxShadow: isDark ? [] : [BoxShadow(color: Colors.black.withValues(alpha :0.03), blurRadius: 8, offset: const Offset(0, 4))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Date Header
          Padding(
            padding: const EdgeInsets.all(12),
            child: Text("📅 Date: ${day['date']}", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
          
          // Metrics Row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildSmallMetric("Pred Temp", "${day['predicted_temperature']} °C", isDark),
                _buildSmallMetric("Pred pH", "${day['predicted_ph']}", isDark),
                _buildSmallMetric("Turbidity", "${day['predicted_turbidity']} NTU", isDark),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Colored Alert Box
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: cardColor,
              border: Border(left: BorderSide(color: accentColor, width: 4)),
              borderRadius: const BorderRadius.only(bottomLeft: Radius.circular(12), bottomRight: Radius.circular(12)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(status, style: TextStyle(fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87)),
                const SizedBox(height: 8),
                if (engAction.isNotEmpty) Text("🇬🇧 $engAction", style: TextStyle(fontSize: 13, color: isDark ? Colors.white70 : Colors.black87)),
                const SizedBox(height: 4),
                if (tagAction.isNotEmpty) Text("🇵🇭 $tagAction", style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: isDark ? Colors.white70 : Colors.black87)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // =========================================================================
  // HELPER WIDGETS
  // =========================================================================

  Widget _buildChartContainer(bool isDark, Widget chart, {Widget? legend, String? title}) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 10),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: Column(
        children: [
          if (title != null) ...[Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)), const SizedBox(height: 10)],
          SizedBox(height: 200, child: chart),
          if (legend != null) ...[const SizedBox(height: 12), legend],
        ],
      ),
    );
  }

  Widget _emptyChartContainer(bool isDark) {
    return Container(
      height: 220,
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: const Center(child: Text("No data available.")),
    );
  }

  Widget _buildSmallMetric(String label, String value, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 10, color: isDark ? Colors.grey : const Color(0xFF64748B))),
        Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: isDark ? Colors.white : const Color(0xFF0F172A))),
      ],
    );
  }

  Widget _buildLegendItem(String l1, Color c1, String l2, Color c2) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(Icons.circle, color: c1, size: 10), const SizedBox(width: 4), Text(l1, style: const TextStyle(fontSize: 11)),
        const SizedBox(width: 16),
        Icon(Icons.circle, color: c2, size: 10), const SizedBox(width: 4), Text(l2, style: const TextStyle(fontSize: 11)),
      ],
    );
  }
}