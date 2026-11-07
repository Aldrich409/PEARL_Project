import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class NetworkOverviewScreen extends StatefulWidget {
  final Map<String, dynamic> userData;

  const NetworkOverviewScreen({super.key, required this.userData});

  @override
  State<NetworkOverviewScreen> createState() => _NetworkOverviewScreenState();
}

class _NetworkOverviewScreenState extends State<NetworkOverviewScreen> {
  bool _isLoading = true;
  final List<Map<String, dynamic>> _networkData = [];
  
  int _activeNodesCount = 0;
  int _totalNodesCount = 0;
  double _totalVolume = 0;
  int _totalFish = 0;
  int _activeAlerts = 0;

  int _stableCount = 0;
  int _warningCount = 0;
  int _dangerCount = 0;
  int _offlineCount = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    try {
      final devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
      _totalNodesCount = devices.length;
      
      _networkData.clear();
      _activeNodesCount = 0;
      _totalVolume = 0;
      _totalFish = 0;
      _activeAlerts = 0;
      _stableCount = 0;
      _warningCount = 0;
      _dangerCount = 0;
      _offlineCount = 0;

      for (var dev in devices) {
        final latest = await ApiService.getLatestTelemetry(dev['device_sn']);
        
        _totalFish += (dev['fish_count'] as num?)?.toInt() ?? 0;
        
        double length = (dev['length'] as num?)?.toDouble() ?? 0;
        double width = (dev['width'] as num?)?.toDouble() ?? 0;
        double depth = (dev['depth'] as num?)?.toDouble() ?? 0;
        _totalVolume += (length * width * depth);

        if (latest != null) {
          _activeNodesCount++;
          double temp = (latest['temperature'] as num).toDouble();
          double ph = (latest['ph'] as num).toDouble();
          double turb = (latest['turbidity'] as num).toDouble();
          
          double risk = _calculateRiskScore(temp, ph, turb, dev);
          
          String status = "Stable";
          Color color = const Color(0xFF10B981); // Green
          
          if (risk >= 50) {
            status = "Danger";
            color = const Color(0xFFEF4444); // Red
            _activeAlerts++;
            _dangerCount++;
          } else if (risk >= 20) {
            status = "Warning";
            color = const Color(0xFFF59E0B); // Orange
            _activeAlerts++;
            _warningCount++;
          } else {
            _stableCount++;
          }

          _networkData.add({
            "Farmer": "Farmer ${dev['owner_id']}",
            "Pond Name": dev['pond_name'],
            "Location": dev['location'] ?? 'N/A',
            "Device SN": dev['device_sn'],
            "Temp": temp,
            "pH": ph,
            "Turbidity": turb,
            "Status": status,
            "Color": color,
          });
        } else {
          _offlineCount++;
          _networkData.add({
            "Farmer": "Farmer ${dev['owner_id']}",
            "Pond Name": dev['pond_name'],
            "Location": dev['location'] ?? 'N/A',
            "Device SN": dev['device_sn'],
            "Temp": null,
            "pH": null,
            "Turbidity": null,
            "Status": "Offline",
            "Color": const Color(0xFF94A3B8), // Grey
          });
        }
      }
    } catch (e) {
      debugPrint("Error loading network data: $e");
    }

    if (mounted) setState(() => _isLoading = false);
  }

  double _calculateRiskScore(double temp, double ph, double turb, Map<String, dynamic> dev) {
    double tNormMin = (dev['temp_norm_min'] as num?)?.toDouble() ?? 26.0;
    double tNormMax = (dev['temp_norm_max'] as num?)?.toDouble() ?? 33.0;
    double tDangMin = (dev['temp_danger_min'] as num?)?.toDouble() ?? 24.0;
    double tDangMax = (dev['temp_danger_max'] as num?)?.toDouble() ?? 35.0;

    double pNormMin = (dev['ph_norm_min'] as num?)?.toDouble() ?? 7.0;
    double pNormMax = (dev['ph_norm_max'] as num?)?.toDouble() ?? 8.5;
    double pDangMin = (dev['ph_danger_min'] as num?)?.toDouble() ?? 6.5;
    double pDangMax = (dev['ph_danger_max'] as num?)?.toDouble() ?? 9.0;

    double tbNormMax = (dev['turb_norm_max'] as num?)?.toDouble() ?? 80.0;
    double tbDangMax = (dev['turb_danger_max'] as num?)?.toDouble() ?? 100.0;

    double score = 0;
    if (temp < tDangMin || temp > tDangMax) {
      score += 50;
    } else if (temp < tNormMin || temp > tNormMax) {
      score += 25;
    }

    if (ph < pDangMin || ph > pDangMax) {
      score += 50;
    } else if (ph < pNormMin || ph > pNormMax) {
      score += 25;
    }

    if (turb > tbDangMax) {
      score += 50;
    } else if (turb > tbNormMax) {
      score += 25;
    }

    return score > 100 ? 100 : score;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_totalNodesCount == 0) return const Center(child: Text("No devices found on the network."));

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          const Text("🌐 Network Command", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const Text("Bird's-eye view of all registered nodes.", style: TextStyle(fontSize: 12, color: Colors.grey)),
          const SizedBox(height: 24),

          // 1. TOP LEVEL METRICS (2x2 Grid)
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            childAspectRatio: 1.8,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            children: [
              _buildMetricCard("Active Nodes", "$_activeNodesCount / $_totalNodesCount", isDark, Colors.blue),
              _buildMetricCard("Total Volume", "${_totalVolume.toStringAsFixed(1)} m³", isDark, Colors.teal),
              _buildMetricCard("Monitored Fish", _totalFish.toString(), isDark, Colors.green),
              _buildMetricCard("Active Alerts", _activeAlerts.toString(), isDark, _activeAlerts > 0 ? Colors.red : Colors.grey),
            ],
          ),
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 12),

          // 2. PIE CHART (Network Health)
          Text("📊 Network Health Status", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          _buildPieChartCard(isDark),
          const SizedBox(height: 24),

          // 3. SCATTER PLOT (Temp vs pH)
          Text("🌡️ Temp vs pH Scatter", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          _buildScatterChartCard(isDark),
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 12),

          // 4. DATA MATRIX (Converted to Mobile Cards)
          Text("🗃️ Active Nodes Data", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
          const SizedBox(height: 12),
          ..._networkData.map((node) => _buildNodeCard(node, isDark)),
        ],
      ),
    );
  }

  // =========================================================================
  // UI WIDGET BUILDERS
  // =========================================================================

  Widget _buildMetricCard(String title, String value, bool isDark, Color accentColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
        boxShadow: isDark ? [] : [BoxShadow(color: Colors.black.withValues(alpha: .02), blurRadius: 4, offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(title, style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B))),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: accentColor)),
        ],
      ),
    );
  }

  Widget _buildPieChartCard(bool isDark) {
    List<PieChartSectionData> sections = [];
    if (_stableCount > 0) sections.add(PieChartSectionData(value: _stableCount.toDouble(), color: const Color(0xFF10B981), title: 'Stable\n$_stableCount', radius: 50, titleStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white)));
    if (_warningCount > 0) sections.add(PieChartSectionData(value: _warningCount.toDouble(), color: const Color(0xFFF59E0B), title: 'Warn\n$_warningCount', radius: 50, titleStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white)));
    if (_dangerCount > 0) sections.add(PieChartSectionData(value: _dangerCount.toDouble(), color: const Color(0xFFEF4444), title: 'Danger\n$_dangerCount', radius: 50, titleStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white)));
    if (_offlineCount > 0) sections.add(PieChartSectionData(value: _offlineCount.toDouble(), color: const Color(0xFF94A3B8), title: 'Offline\n$_offlineCount', radius: 50, titleStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white)));

    return Container(
      height: 220,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: sections.isEmpty 
        ? const Center(child: Text("No Data"))
        : PieChart(
            PieChartData(
              sectionsSpace: 2,
              centerSpaceRadius: 40,
              sections: sections,
            ),
          ),
    );
  }

 Widget _buildScatterChartCard(bool isDark) {
    List<ScatterSpot> spots = [];
    for (var node in _networkData) {
      if (node['Status'] != 'Offline' && node['Temp'] != null && node['pH'] != null) {
        
        // 1. Explicitly cast the dynamic map values to proper types to prevent errors
        double tempVal = (node['Temp'] as num).toDouble();
        double phVal = (node['pH'] as num).toDouble();
        Color dotColor = node['Color'] as Color;

       spots.add(ScatterSpot(
          tempVal,
          phVal,
          color: dotColor, 
          radius: 6,
        ));
      }
    }

    return Container(
      height: 240,
      padding: const EdgeInsets.only(top: 20, right: 20, left: 10, bottom: 10),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: spots.isEmpty 
        ? const Center(child: Text("No active data"))
        : ScatterChart(
            ScatterChartData(
              scatterSpots: spots,
              minX: 20, maxX: 40,
              minY: 5, maxY: 10,
      gridData: const FlGridData(show: true),
        titlesData: const FlTitlesData( // <-- Added const here
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: true, reservedSize: 30), 
            axisNameWidget: Text("Temperature (°C)", style: TextStyle(fontSize: 10))
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: true, reservedSize: 30), 
            axisNameWidget: Text("pH Level", style: TextStyle(fontSize: 10))
          ),
        ),
        // Note: borderData CANNOT be const because it uses the dynamic 'isDark' variable
        borderData: FlBorderData(
          show: true, 
          border: Border(
            bottom: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0)), 
            left: BorderSide(color: isDark ? Colors.grey.shade800 : const Color(0xFFE2E8F0))
          )
        ),
          ),
        ),
    );
  }

  Widget _buildNodeCard(Map<String, dynamic> node, bool isDark) {
    bool isOffline = node['Status'] == 'Offline';
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          // Color Indicator Strip
          Container(
            width: 8,
            height: 90,
            decoration: BoxDecoration(
              color: node['Color'],
              borderRadius: const BorderRadius.only(topLeft: Radius.circular(12), bottomLeft: Radius.circular(12)),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(node['Pond Name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(color: (node['Color'] as Color).withValues(alpha: 0.15), borderRadius: BorderRadius.circular(12)),
                        child: Text(node['Status'], style: TextStyle(color: node['Color'], fontSize: 10, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  Text("${node['Farmer']} • ${node['Device SN']}", style: TextStyle(fontSize: 11, color: isDark ? Colors.grey : const Color(0xFF64748B))),
                  const SizedBox(height: 8),
                  isOffline 
                    ? const Text("No recent telemetry data available.", style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic))
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildSmallData("Temp", "${node['Temp']} °C", isDark),
                          _buildSmallData("pH", "${node['pH']}", isDark),
                          _buildSmallData("Turb", "${node['Turbidity']} NTU", isDark),
                        ],
                      ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSmallData(String label, String value, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: TextStyle(fontSize: 10, color: isDark ? Colors.grey : const Color(0xFF64748B))),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: isDark ? Colors.white : const Color(0xFF0F172A))),
      ],
    );
  }
}