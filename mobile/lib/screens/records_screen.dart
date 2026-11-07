import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
// Note: To enable CSV export sharing, add 'share_plus: ^7.0.0' to pubspec.yaml
// import 'package:share_plus/share_plus.dart'; 

class RecordsScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String? activeDeviceSn;

  const RecordsScreen({super.key, required this.userData, this.activeDeviceSn});

  @override
  State<RecordsScreen> createState() => _RecordsScreenState();
}

class _RecordsScreenState extends State<RecordsScreen> {
  bool _isLoading = true;
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 7));
  DateTime _endDate = DateTime.now();

  List<dynamic> _devices = [];
  final List<Map<String, dynamic>> _farmerRisks = [];
  List<dynamic> _masterlist = []; // Holds all records
  List<dynamic> _filteredMasterlist = []; // Holds date-filtered records
  
  final List<dynamic> _isoLogs = [];
  final double _avgOverall = 0;
  final double _avgDash = 0;
  final double _avgIot = 0;
  final double _avgAi = 0;

  bool get isAdmin => widget.userData['role'] == 'admin';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    try {
      if (isAdmin) {
        _devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
        
        // 1. Calculate Farmer Risks
        _farmerRisks.clear();
        _masterlist.clear();

        for (var dev in _devices) {
          final latest = await ApiService.getLatestTelemetry(dev['device_sn']);
          if (latest != null) {
            double risk = _calculateRiskScore(
              (latest['temperature'] as num).toDouble(), 
              (latest['ph'] as num).toDouble(), 
              (latest['turbidity'] as num).toDouble()
            );
            
            _farmerRisks.add({
              "Farmer": "Farmer ${dev['owner_id']} (${dev['pond_name']})",
              "Risk Score": risk,
              "Status": risk >= 50 ? "Danger" : risk >= 20 ? "Warning" : "Normal",
              "Color": risk >= 50 ? const Color(0xFFEF4444) : risk >= 20 ? const Color(0xFFF59E0B) : const Color(0xFF10B981)
            });
          }

          // 2. Compile Masterlist
          final history = await ApiService.getHistory(dev['device_sn'], limit: 500);
          for (var record in history) {
            record['Owner'] = "Farmer ${dev['owner_id']}";
            record['Pond Name'] = dev['pond_name'];
            _masterlist.add(record);
          }
        }
        
        _farmerRisks.sort((a, b) => (b['Risk Score'] as num).compareTo(a['Risk Score'] as num));
        
        // 3. Fetch ISO Logs (Assuming ApiService has this method)
        // _isoLogs = await ApiService.getIsoPerformanceLogs(limit: 300);
        // _calculateIsoMetrics();

      } else {
        // Farmer View
        if (widget.activeDeviceSn != null) {
          _masterlist = await ApiService.getHistory(widget.activeDeviceSn!, limit: 500);
        }
      }
      
      _applyDateFilter();

    } catch (e) {
      debugPrint("Error loading records: $e");
    }

    if (mounted) setState(() => _isLoading = false);
  }

  void _applyDateFilter() {
    // Set end date to the very end of the selected day for accurate filtering
    DateTime endOfDay = DateTime(_endDate.year, _endDate.month, _endDate.day, 23, 59, 59);
    DateTime startOfDay = DateTime(_startDate.year, _startDate.month, _startDate.day, 0, 0, 0);

    _filteredMasterlist = _masterlist.where((record) {
      DateTime ts = DateTime.parse(record['timestamp']);
      return ts.isAfter(startOfDay) && ts.isBefore(endOfDay);
    }).toList();
    
    // Sort newest first
    _filteredMasterlist.sort((a, b) => DateTime.parse(b['timestamp']).compareTo(DateTime.parse(a['timestamp'])));
  }

  Future<void> _selectDate(BuildContext context, bool isStart) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: isStart ? _startDate : _endDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
    setState(() {
      // Add the curly braces here:
      if (isStart) {
        _startDate = picked;
      } else {
        _endDate = picked;
      }
      _applyDateFilter();
    });
    }
  } 
  void _exportCsv(bool isIso) {
    // To implement real export on mobile:
    // 1. Add share_plus to pubspec.yaml
    // 2. Generate CSV string looping through _filteredMasterlist or _isoLogs
    // 3. Share.share(csvString, subject: 'PEARL Export');
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("CSV Export triggered! (Requires share_plus package implementation)")),
    );
  }

  double _calculateRiskScore(double temp, double ph, double turb) {
    double score = 0;
    if (temp < 26 || temp > 33) {
      score += 40;
    } else if (temp < 28 || temp > 31) {
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

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    if (isAdmin) {
      return DefaultTabController(
        length: 2,
        child: Column(
          children: [
            const TabBar(
              labelColor: Color(0xFF0284C7),
              unselectedLabelColor: Colors.grey,
              indicatorColor: Color(0xFF0284C7),
              tabs: [
                Tab(icon: Icon(Icons.analytics), text: "Masterlist"),
                Tab(icon: Icon(Icons.speed), text: "ISO/IEC 25010"),
              ],
            ),
            Expanded(
              child: TabBarView(
                children: [
                  _buildTelemetryTab(),
                  _buildIsoTab(),
                ],
              ),
            ),
          ],
        ),
      );
    } else {
      return _buildTelemetryTab();
    }
  }

  // =========================================================================
  // TAB 1: TELEMETRY MASTERLIST
  // =========================================================================
  Widget _buildTelemetryTab() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("📂 Telemetry Records", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),

        // Date Filter Row
        Text("📅 Filter Data by Date", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: primaryColor)),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: InkWell(
                onTap: () => _selectDate(context, true),
                child: _buildDateBox("Start Date", _startDate, isDark),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: InkWell(
                onTap: () => _selectDate(context, false),
                child: _buildDateBox("End Date", _endDate, isDark),
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        const Divider(),

        // Admin Risk Ranking Chart
        if (isAdmin && _farmerRisks.isNotEmpty) ...[
          const SizedBox(height: 12),
          Text("🚨 Farmer Risk Ranking", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
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
              children: _farmerRisks.map((risk) {
                final double score = risk['Risk Score'] as double;
                final Color barColor = risk['Color'] as Color;
                
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16.0),
                  child: Row(
                    children: [
                      Expanded(
                        flex: 4,
                        child: Text(
                          risk['Farmer'],
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        flex: 6,
                        child: Stack(
                          children: [
                            Container(height: 18, decoration: BoxDecoration(color: barColor.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(4))),
                            FractionallySizedBox(
                              widthFactor: (score / 100).clamp(0.05, 1.0),
                              child: Container(
                                height: 18,
                                alignment: Alignment.centerRight,
                                padding: const EdgeInsets.only(right: 6),
                                decoration: BoxDecoration(color: barColor, borderRadius: BorderRadius.circular(4)),
                                child: Text("${score.toInt()}", style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: Colors.white)),
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
          const Divider(),
        ],

        // Masterlist Export & Records
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(isAdmin ? "📋 Raw Masterlist" : "📋 Your Records", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
            ElevatedButton.icon(
              onPressed: () => _exportCsv(false), 
              icon: const Icon(Icons.download, size: 16), 
              label: const Text("Export"),
              style: ElevatedButton.styleFrom(backgroundColor: primaryColor, foregroundColor: Colors.white),
            )
          ],
        ),
        const SizedBox(height: 12),
        
        if (_filteredMasterlist.isEmpty)
          const Padding(padding: EdgeInsets.all(20.0), child: Center(child: Text("No records found in this date range.")))
        else
          ..._filteredMasterlist.map((record) => _buildRecordCard(record, isDark, isAdmin)),
      ],
    );
  }

  // =========================================================================
  // TAB 2: ISO/IEC 25010 (ADMIN ONLY)
  // =========================================================================
  Widget _buildIsoTab() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = Theme.of(context).primaryColor;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(child: Text("⚡ Performance Logs", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: primaryColor))),
            ElevatedButton.icon(
              onPressed: () => _exportCsv(true), 
              icon: const Icon(Icons.download, size: 16), 
              label: const Text("CSV"),
              style: ElevatedButton.styleFrom(backgroundColor: primaryColor, foregroundColor: Colors.white),
            )
          ],
        ),
        const SizedBox(height: 8),
        const Text("Real-time millisecond (ms) response latency metrics for Chapter 4 statistical evaluation.", style: TextStyle(fontSize: 12, color: Colors.grey)),
        const SizedBox(height: 24),

        // 2x2 Metric Grid
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          childAspectRatio: 1.8,
          mainAxisSpacing: 10,
          crossAxisSpacing: 10,
          children: [
            _buildMetricCard("Overall Mean", "${_avgOverall.toStringAsFixed(2)} ms", isDark, Colors.purple),
            _buildMetricCard("Dashboard Query", "${_avgDash.toStringAsFixed(2)} ms", isDark, Colors.blue),
            _buildMetricCard("IoT Ingestion", "${_avgIot.toStringAsFixed(2)} ms", isDark, Colors.teal),
            _buildMetricCard("AI Forecast", "${_avgAi.toStringAsFixed(2)} ms", isDark, Colors.orange),
          ],
        ),
        const SizedBox(height: 24),

        // Logs list (placeholder representation)
        if (_isoLogs.isEmpty)
          const Padding(padding: EdgeInsets.all(20.0), child: Center(child: Text("Performance logs will populate automatically.")))
        else
          ..._isoLogs.map((log) => _buildIsoLogCard(log, isDark)),
      ],
    );
  }

  // =========================================================================
  // UI HELPERS
  // =========================================================================

  Widget _buildDateBox(String label, DateTime date, bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF0284C7).withValues (alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
          const SizedBox(height: 4),
          Text(DateFormat('MMM dd, yyyy').format(date), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildRecordCard(Map<String, dynamic> record, bool isDark, bool showOwner) {
    DateTime ts = DateTime.parse(record['timestamp']);
    String formattedTime = DateFormat('MMM dd • hh:mm a').format(ts);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(formattedTime, style: TextStyle(fontWeight: FontWeight.bold, color: Theme.of(context).primaryColor)),
              if (showOwner) Text("${record['Owner']} (${record['Pond Name']})", style: const TextStyle(fontSize: 10, color: Colors.grey)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildMiniStat("Temp", "${record['temperature']}°C", isDark),
              _buildMiniStat("pH", "${record['ph']}", isDark),
              _buildMiniStat("Turbidity", "${record['turbidity']} NTU", isDark),
              _buildMiniStat("Level", "${record['water_level_cm']} cm", isDark),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildIsoLogCard(Map<String, dynamic> log, bool isDark) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(child: Text(log['operation_category'] ?? 'Query', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13))),
          Text("${log['execution_time_ms']} ms", style: TextStyle(fontWeight: FontWeight.w900, color: Theme.of(context).primaryColor)),
        ],
      ),
    );
  }

  Widget _buildMiniStat(String label, String value, bool isDark) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87)),
      ],
    );
  }

  Widget _buildMetricCard(String title, String value, bool isDark, Color accentColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF1E293B) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B))),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900, color: accentColor)),
        ],
      ),
    );
  }
}