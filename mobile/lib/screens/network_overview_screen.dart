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
    final rawDevices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);

    for (var dev in rawDevices) {
      final reading = await ApiService.getLatestTelemetry(dev['device_sn']);
      if (reading != null) {
        _latestReadings[dev['device_sn']] = reading;
      }
    }
    
    rawDevices.sort((a, b) {
      int scoreA = _getRiskScore(_latestReadings[a['device_sn']], a);
      int scoreB = _getRiskScore(_latestReadings[b['device_sn']], b);
      return scoreB.compareTo(scoreA); 
    });
    
    _devices = rawDevices;
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
      case 3: return {'color': Colors.redAccent, 'label': 'CRITICAL', 'icon': Icons.warning_amber_rounded};
      case 2: return {'color': Colors.orangeAccent, 'label': 'WARNING', 'icon': Icons.priority_high_rounded};
      case 1: return {'color': Colors.green, 'label': 'STABLE', 'icon': Icons.check_circle_outline};
      default: return {'color': Colors.grey, 'label': 'OFFLINE', 'icon': Icons.signal_wifi_off};
    }
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
    final primaryColor = Theme.of(context).primaryColor;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text("🚨 Network Priority (Risk Ranked)", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
        const SizedBox(height: 4),
        Text("Listahan ng mga palaisdaan na nangangailangan ng agarang pansin", style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: isDark ? Colors.white70 : Colors.black54)),
        const SizedBox(height: 16),

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
              
              ..._devices.map((dev) {
                final sn = dev['device_sn'];
                final score = _getRiskScore(_latestReadings[sn], dev);
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
                          "Farmer ${dev['owner_id']}",
                          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        flex: 7,
                        child: Stack(
                          children: [
                            Container(
                              height: 18,
                              decoration: BoxDecoration(color: barColor.withOpacity(0.1), borderRadius: BorderRadius.circular(4)),
                            ),
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
                                  ),
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
        Text("📋 Detailed Node Status", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
        const SizedBox(height: 12),

        ..._devices.map((dev) {
          final sn = dev['device_sn'];
          final reading = _latestReadings[sn];
          final riskScore = _getRiskScore(reading, dev);
          final style = _getRiskStyling(riskScore);
          final statusColor = style['color'] as Color;
          final fishType = dev['fish_type'] ?? 'Tilapia';

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
              side: BorderSide(color: statusColor.withOpacity(0.3), width: 1),
            ),
            color: isDark ? const Color(0xFF1E293B) : Colors.white,
            child: ListTile(
              contentPadding: const EdgeInsets.all(12),
              leading: CircleAvatar(
                backgroundColor: statusColor.withOpacity(0.15),
                child: Icon(style['icon'], color: statusColor),
              ),
              title: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      "Farmer ${dev['owner_id']} - ${dev['pond_name']} ($fishType)",
                      style: TextStyle(fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      style['label'],
                      style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: statusColor),
                    ),
                  ),
                ],
              ),
              subtitle: Padding(
                padding: const EdgeInsets.all(8.0),
                child: reading != null 
                    ? Text("Temp: ${reading['temperature']}°C • pH: ${reading['ph']} • Turb: ${reading['turbidity']} NTU", style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: isDark ? Colors.white70 : Colors.black54))
                    : Text("No recent data broadcasted.", style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: isDark ? Colors.white54 : Colors.black45)),
              ),
            ),
          );
        }),
      ],
    );
  }
}