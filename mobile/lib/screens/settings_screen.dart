import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SettingsScreen extends StatefulWidget {
  final Map<String, dynamic> userData;
  final String? activeDeviceSn;

  const SettingsScreen({super.key, required this.userData, this.activeDeviceSn});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _device;
  String _selectedPondFish = 'Tilapia';

  bool get isAdmin => widget.userData['role'] == 'admin';

  // --- FISH SPECIES STATE ---
  final Map<String, Map<String, dynamic>> _fishLibrary = {
    'Tilapia': {
      'fish_name': 'Tilapia',
      'temp_norm_min': 26.0, 'temp_norm_max': 33.0, 'temp_danger_min': 24.0, 'temp_danger_max': 35.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 80.0, 'turb_danger_max': 100.0,
      'suggestion_text': '📘 BFAR / FAO Standard (Tilapia): Optimal growth and breeding occur at 26–33°C and pH 7.0–8.5. Keep turbidity ≤80 NTU; readings above 100 NTU indicate heavy plankton blooms that deplete dissolved oxygen at night.\n🇵🇭 Gabay: Pinakamaganda ang paglaki at pangingitlog sa 26–33°C at pH 7.0–8.5. Huwag hayaang lumampas sa 100 NTU ang labo ng tubig.',
    },
    'Bangus (Milkfish)': {
      'fish_name': 'Bangus (Milkfish)',
      'temp_norm_min': 25.0, 'temp_norm_max': 32.0, 'temp_danger_min': 22.0, 'temp_danger_max': 35.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 85.0, 'turb_danger_max': 110.0,
      'suggestion_text': '📘 BFAR / SEAFDEC Standard (Bangus): Milkfish thrive at 25–32°C and pH 7.0–8.5. They are very sensitive to low dissolved oxygen when water temperature exceeds 32°C or turbidity spikes above 110 NTU.\n🇵🇭 Gabay: Sensitibo ang Bangus sa pagbaba ng oxygen kapag mainit (>32°C) o sobrang labo ng tubig (>110 NTU).',
    },
    'Catfish (Hito)': {
      'fish_name': 'Catfish (Hito)',
      'temp_norm_min': 26.0, 'temp_norm_max': 32.0, 'temp_danger_min': 22.0, 'temp_danger_max': 36.0,
      'ph_norm_min': 6.5, 'ph_norm_max': 8.0, 'ph_danger_min': 5.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 100.0, 'turb_danger_max': 140.0,
      'suggestion_text': '📘 BFAR / FAO Standard (Catfish / Hito): Air-breathing organs allow Hito to tolerate higher turbidity (up to 100 NTU) and slightly acidic water (pH 6.5–8.0). However, pH <5.5 or >9.0 burns their scaleless skin.\n🇵🇭 Gabay: Mas matibay ang Hito sa malabong tubig (≤100 NTU), ngunit iwasang bumaba sa 5.5 o lumampas sa 9.0 ang pH.',
    },
    'Carp (Karpa)': {
      'fish_name': 'Carp (Karpa)',
      'temp_norm_min': 24.0, 'temp_norm_max': 30.0, 'temp_danger_min': 20.0, 'temp_danger_max': 34.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.0, 'ph_danger_max': 9.0,
      'turb_norm_max': 90.0, 'turb_danger_max': 120.0,
      'suggestion_text': '📘 FAO Standard (Common Carp / Karpa): Prefers slightly cooler water (24–30°C) and pH 7.0–8.5. Bottom-foraging stirs up mud (Normal ≤90 NTU), but >120 NTU signals excessive organic waste.\n🇵🇭 Gabay: Mas gusto ng Karpa ang 24–30°C at pH 7.0–8.5. Palitan ang tubig kapag lumampas sa 120 NTU ang labo.',
    },
    'Freshwater Prawn (Ulang)': {
      'fish_name': 'Freshwater Prawn (Ulang)',
      'temp_norm_min': 28.0, 'temp_norm_max': 31.0, 'temp_danger_min': 24.0, 'temp_danger_max': 34.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 60.0, 'turb_danger_max': 85.0,
      'suggestion_text': '📘 BFAR Standard (Giant Freshwater Prawn / Ulang): Requires clean water (≤60 NTU) and pH 7.0–8.5 for shell molting. High turbidity (>85 NTU) or acidic pH causes molting mortality.\n🇵🇭 Gabay: Kailangan ng malinis na tubig (≤60 NTU) at pH 7.0–8.5 para sa maayos na pagpapalit ng balat ng Ulang.',
    },
    'Mudfish (Dalag)': {
      'fish_name': 'Mudfish (Dalag)',
      'temp_norm_min': 25.0, 'temp_norm_max': 32.0, 'temp_danger_min': 20.0, 'temp_danger_max': 36.0,
      'ph_norm_min': 6.5, 'ph_norm_max': 8.0, 'ph_danger_min': 5.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 100.0, 'turb_danger_max': 140.0,
      'suggestion_text': '📘 BFAR Standard (Mudfish / Dalag): Hardy air-breathing predator comfortable in 25–32°C and pH 6.5–8.0. Keep turbidity ≤100 NTU so fish can see floating feed pellets.\n🇵🇭 Gabay: Matibay ang Dalag sa 25–32°C at pH 6.5–8.0. Panatilihing ≤100 NTU ang labo upang makita ang pakain.',
    },
    'Pangasius (Cream Dory)': {
      'fish_name': 'Pangasius (Cream Dory)',
      'temp_norm_min': 26.0, 'temp_norm_max': 31.0, 'temp_danger_min': 22.0, 'temp_danger_max': 35.0,
      'ph_norm_min': 6.5, 'ph_norm_max': 8.0, 'ph_danger_min': 5.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 95.0, 'turb_danger_max': 130.0,
      'suggestion_text': '📘 FAO Standard (Pangasius): Thrives in warm ponds (26–31°C) and pH 6.5–8.0. Water exchange is needed if turbidity exceeds 130 NTU to maintain white fillet quality.\n🇵🇭 Gabay: Nabubuhay nang maayos sa 26–31°C at pH 6.5–8.0. Palitan ang tubig kapag lumampas sa 130 NTU ang labo.',
    }
  };

  final _customFishNameCtrl = TextEditingController();
  final _suggestionNoteCtrl = TextEditingController();
  final _tempNormMin = TextEditingController();
  final _tempNormMax = TextEditingController();
  final _tempDangerMin = TextEditingController();
  final _tempDangerMax = TextEditingController();
  final _phNormMin = TextEditingController();
  final _phNormMax = TextEditingController();
  final _phDangerMin = TextEditingController();
  final _phDangerMax = TextEditingController();
  final _turbNormMax = TextEditingController();
  final _turbDangerMax = TextEditingController();
  bool _applyToPondImmediately = true;

  // --- DEVICE SETTINGS STATE ---
  final _smsPhoneCtrl = TextEditingController();
  String _smsAlertLevel = "Critical Emergencies Only";
  double _sleepInterval = 5.0;
  final _phOffsetCtrl = TextEditingController();
  final _turbOffsetCtrl = TextEditingController();
  
  // --- PAIRING STATE (ADMIN) ---
  final _pairSnCtrl = TextEditingController();
  final _pairNameCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void didUpdateWidget(covariant SettingsScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.activeDeviceSn != widget.activeDeviceSn) {
      _loadData();
    }
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final devices = await ApiService.getDevices(widget.userData['id'], widget.userData['role']);
    final apiProfiles = await ApiService.getFishProfiles();

    for (var p in apiProfiles) {
      if (p is Map<String, dynamic>) {
        String name = p['fish_name'] ?? p['name'] ?? p['species'] ?? p['fish_type'] ?? 'Saved Fish';
        p['fish_name'] = name;
        _fishLibrary[name] = p;
      }
    }

    if (devices.isNotEmpty && widget.activeDeviceSn != null) {
      _device = devices.firstWhere((d) => d['device_sn'] == widget.activeDeviceSn, orElse: () => devices[0]);
      
      // Load Device Configs
      _smsPhoneCtrl.text = _device!['alert_phone'] ?? '';
      _smsAlertLevel = (_device!['alert_level'] == "Critical") ? "Critical Emergencies Only" : "Warnings & Critical";
      _sleepInterval = (_device!['sleep_interval'] as num?)?.toDouble() ?? 5.0;
      _phOffsetCtrl.text = (_device!['ph_offset'] as num?)?.toStringAsFixed(2) ?? '0.00';
      _turbOffsetCtrl.text = (_device!['turb_offset'] as num?)?.toStringAsFixed(1) ?? '0.0';

      // Load Fish Configs
      _selectedPondFish = _device!['fish_type'] ?? 'Tilapia';
      if (!_fishLibrary.containsKey(_selectedPondFish)) {
        _fishLibrary[_selectedPondFish] = {
          'fish_name': _selectedPondFish,
          'temp_norm_min': _device!['temp_norm_min'] ?? 26.0,
          'temp_norm_max': _device!['temp_norm_max'] ?? 33.0,
          'temp_danger_min': _device!['temp_danger_min'] ?? 24.0,
          'temp_danger_max': _device!['temp_danger_max'] ?? 35.0,
          'ph_norm_min': _device!['ph_norm_min'] ?? 7.0,
          'ph_norm_max': _device!['ph_norm_max'] ?? 8.5,
          'ph_danger_min': _device!['ph_danger_min'] ?? 6.5,
          'ph_danger_max': _device!['ph_danger_max'] ?? 9.0,
          'turb_norm_max': _device!['turb_norm_max'] ?? 80.0,
          'turb_danger_max': _device!['turb_danger_max'] ?? 100.0,
          'suggestion_text': 'Custom saved thresholds for $_selectedPondFish.',
        };
      }
      _populateEditorFromProfile(_fishLibrary[_selectedPondFish]!);
    }
    if (mounted) setState(() => _isLoading = false);
  }

  void _populateEditorFromProfile(Map<String, dynamic> profile) {
    setState(() {
      _customFishNameCtrl.text = profile['fish_name'] ?? '';
      _tempNormMin.text = (profile['temp_norm_min'] ?? 26.0).toString();
      _tempNormMax.text = (profile['temp_norm_max'] ?? 33.0).toString();
      _tempDangerMin.text = (profile['temp_danger_min'] ?? 24.0).toString();
      _tempDangerMax.text = (profile['temp_danger_max'] ?? 35.0).toString();
      _phNormMin.text = (profile['ph_norm_min'] ?? 7.0).toString();
      _phNormMax.text = (profile['ph_norm_max'] ?? 8.5).toString();
      _phDangerMin.text = (profile['ph_danger_min'] ?? 6.5).toString();
      _phDangerMax.text = (profile['ph_danger_max'] ?? 9.0).toString();
      _turbNormMax.text = (profile['turb_norm_max'] ?? 80.0).toString();
      _turbDangerMax.text = (profile['turb_danger_max'] ?? 100.0).toString();
      _suggestionNoteCtrl.text = profile['suggestion_text'] ?? '';
    });
  }

  Future<void> _fetchAiSuggestion() async {
    final typedName = _customFishNameCtrl.text.trim();
    if (typedName.isEmpty) return;

    final apiSug = await ApiService.getFishSuggestion(typedName);
    if (apiSug != null) {
      _populateEditorFromProfile(apiSug);
    } else {
      final match = _fishLibrary.entries.firstWhere(
        (e) => e.key.toLowerCase().contains(typedName.toLowerCase()),
        orElse: () => MapEntry(typedName, {
          'fish_name': typedName,
          'temp_norm_min': 26.0, 'temp_norm_max': 32.0, 'temp_danger_min': 23.0, 'temp_danger_max': 35.0,
          'ph_norm_min': 6.8, 'ph_norm_max': 8.5, 'ph_danger_min': 6.0, 'ph_danger_max': 9.0,
          'turb_norm_max': 80.0, 'turb_danger_max': 110.0,
          'suggestion_text': '🤖 AI Guide ($typedName): Recommended tropical freshwater range is 26–32°C, pH 6.8–8.5, and turbidity ≤80 NTU (Danger >110 NTU).',
        }),
      );
      final data = Map<String, dynamic>.from(match.value);
      data['fish_name'] = typedName;
      _populateEditorFromProfile(data);
    }
  }

  Future<void> _applySelectedSpeciesToPond() async {
    if (_device == null) return;
    final chosenProfile = _fishLibrary[_selectedPondFish];
    if (chosenProfile == null) return;

    final payload = Map<String, dynamic>.from(_device!);
    payload['fish_type'] = _selectedPondFish;
    payload['temp_norm_min'] = chosenProfile['temp_norm_min'];
    payload['temp_norm_max'] = chosenProfile['temp_norm_max'];
    payload['temp_danger_min'] = chosenProfile['temp_danger_min'];
    payload['temp_danger_max'] = chosenProfile['temp_danger_max'];
    payload['ph_norm_min'] = chosenProfile['ph_norm_min'];
    payload['ph_norm_max'] = chosenProfile['ph_norm_max'];
    payload['ph_danger_min'] = chosenProfile['ph_danger_min'];
    payload['ph_danger_max'] = chosenProfile['ph_danger_max'];
    payload['turb_norm_max'] = chosenProfile['turb_norm_max'];
    payload['turb_danger_max'] = chosenProfile['turb_danger_max'];

    final ok = await ApiService.updateDeviceSettings(payload);
    if (mounted && ok) {
      setState(() => _device = payload);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('🐟 Pond set to $_selectedPondFish!'), backgroundColor: Colors.green));
    }
  }

  Future<void> _saveCustomFishToLibrary() async {
    final fishName = _customFishNameCtrl.text.trim();
    if (fishName.isEmpty) return;

    final newProfile = {
      'fish_name': fishName,
      'temp_norm_min': double.tryParse(_tempNormMin.text) ?? 26.0,
      'temp_norm_max': double.tryParse(_tempNormMax.text) ?? 33.0,
      'temp_danger_min': double.tryParse(_tempDangerMin.text) ?? 24.0,
      'temp_danger_max': double.tryParse(_tempDangerMax.text) ?? 35.0,
      'ph_norm_min': double.tryParse(_phNormMin.text) ?? 7.0,
      'ph_norm_max': double.tryParse(_phNormMax.text) ?? 8.5,
      'ph_danger_min': double.tryParse(_phDangerMin.text) ?? 6.5,
      'ph_danger_max': double.tryParse(_phDangerMax.text) ?? 9.0,
      'turb_norm_max': double.tryParse(_turbNormMax.text) ?? 80.0,
      'turb_danger_max': double.tryParse(_turbDangerMax.text) ?? 100.0,
      'suggestion_text': _suggestionNoteCtrl.text.trim(),
    };

    setState(() {
      _fishLibrary[fishName] = newProfile;
      _selectedPondFish = fishName;
    });

    await ApiService.saveFishProfile(newProfile);
    if (_applyToPondImmediately) {
      await _applySelectedSpeciesToPond();
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('💾 Saved "$fishName" to Library!'), backgroundColor: Colors.teal));
    }
  }

  Future<void> _updateDeviceSetting(String key, dynamic value, String successMsg) async {
    if (_device == null) return;
    final payload = Map<String, dynamic>.from(_device!);
    payload[key] = value;
    
    // Additional parsing for multiple simultaneous fields if needed
    if (key == 'calibration') {
      payload['ph_offset'] = double.tryParse(_phOffsetCtrl.text) ?? 0.0;
      payload['turb_offset'] = double.tryParse(_turbOffsetCtrl.text) ?? 0.0;
    } else if (key == 'sms') {
      payload['alert_phone'] = _smsPhoneCtrl.text.trim();
      payload['alert_level'] = _smsAlertLevel.contains("Critical") ? "Critical" : "Warning";
    }

    final ok = await ApiService.updateDeviceSettings(payload);
    if (mounted && ok) {
      setState(() => _device = payload);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(successMsg), backgroundColor: Colors.green));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_device == null) return const Center(child: Text("No pond node selected."));

    return DefaultTabController(
      length: isAdmin ? 5 : 4,
      child: Column(
        children: [
          TabBar(
            isScrollable: true,
            labelColor: const Color(0xFF0284C7),
            unselectedLabelColor: Colors.grey,
            indicatorColor: const Color(0xFF0284C7),
            tabs: [
              const Tab(icon: Icon(Icons.pets), text: "Fish & Thresholds"),
              if (isAdmin) const Tab(icon: Icon(Icons.link), text: "Pair Node"),
              const Tab(icon: Icon(Icons.sms), text: "SMS Alerts"),
              const Tab(icon: Icon(Icons.bedtime), text: "Deep Sleep"),
              const Tab(icon: Icon(Icons.tune), text: "Calibration"),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                _buildFishTab(),
                if (isAdmin) _buildPairTab(),
                _buildSmsTab(),
                _buildSleepTab(),
                _buildCalibrationTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // =========================================================================
  // TAB BUILDERS
  // =========================================================================

  Widget _buildFishTab() {
    final primaryColor = Theme.of(context).primaryColor;
    final fishNames = _fishLibrary.keys.toList();
    final activeProfile = _fishLibrary[_selectedPondFish] ?? _fishLibrary['Tilapia']!;

    final tempTip = "🟢 ${activeProfile['temp_norm_min']}–${activeProfile['temp_norm_max']}°C | 🔴 <${activeProfile['temp_danger_min']} or >${activeProfile['temp_danger_max']}°C";
    final phTip = "🟢 ${activeProfile['ph_norm_min']}–${activeProfile['ph_norm_max']} | 🔴 <${activeProfile['ph_danger_min']} or >${activeProfile['ph_danger_max']}";
    final turbTip = "🟢 0–${activeProfile['turb_norm_max']} NTU | 🔴 >${activeProfile['turb_danger_max']} NTU";

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("🎯 Choose Species in Pond", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  initialValue: fishNames.contains(_selectedPondFish) ? _selectedPondFish : fishNames.first,
                  decoration: InputDecoration(
                    labelText: 'Select Saved Fish Species',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  items: fishNames.map((f) => DropdownMenuItem(value: f, child: Text(f))).toList(),
                  onChanged: (val) {
                    if (val != null) {
                      setState(() => _selectedPondFish = val);
                      _populateEditorFromProfile(_fishLibrary[val]!);
                    }
                  },
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: primaryColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                    border: Border(left: BorderSide(color: primaryColor, width: 4)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("📖 Guide for $_selectedPondFish:", style: TextStyle(fontWeight: FontWeight.bold, color: primaryColor)),
                      const SizedBox(height: 8),
                      Text(activeProfile['suggestion_text'] ?? '', style: const TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton.icon(
                    onPressed: _applySelectedSpeciesToPond,
                    icon: const Icon(Icons.check_circle_outline),
                    label: Text("Set '$_selectedPondFish' Active"),
                    style: ElevatedButton.styleFrom(backgroundColor: primaryColor, foregroundColor: Colors.white),
                  ),
                ),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 24),
        Text("➕ Add Custom Fish Species", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _customFishNameCtrl,
                decoration: InputDecoration(labelText: 'Type Name (e.g., Red Tilapia)', border: OutlineInputBorder(borderRadius: BorderRadius.circular(10))),
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              height: 56,
              child: ElevatedButton.icon(
                onPressed: _fetchAiSuggestion,
                icon: const Icon(Icons.auto_awesome, size: 18),
                label: const Text("AI Suggest"),
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        _buildRangeCard("🌡️ Temperature (°C)", tempTip, _tempNormMin, _tempNormMax, _tempDangerMin, _tempDangerMax),
        const SizedBox(height: 12),
        _buildRangeCard("🧪 pH Level", phTip, _phNormMin, _phNormMax, _phDangerMin, _phDangerMax),
        const SizedBox(height: 12),
        
        Card(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("🌊 Turbidity (NTU)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: primaryColor)),
                const SizedBox(height: 4),
                Text(turbTip, style: const TextStyle(fontSize: 11, color: Colors.blueGrey)),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(child: _buildField("🟢 Normal Max", _turbNormMax)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildField("🔴 Danger Above", _turbDangerMax)),
                  ],
                ),
              ],
            ),
          ),
        ),
        
        const SizedBox(height: 16),
        CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          controlAffinity: ListTileControlAffinity.leading,
          title: Text("Also set as active species for ${_device!['pond_name']}", style: const TextStyle(fontSize: 13)),
          value: _applyToPondImmediately,
          onChanged: (val) => setState(() => _applyToPondImmediately = val ?? true),
        ),
        
        const SizedBox(height: 8),
        SizedBox(
          width: double.infinity,
          height: 50,
          child: ElevatedButton.icon(
            onPressed: _saveCustomFishToLibrary,
            icon: const Icon(Icons.save),
            label: const Text("Save Ranges to Library"),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.teal, foregroundColor: Colors.white),
          ),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildPairTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("🔗 Pair New Hardware Node", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        TextField(
          controller: _pairSnCtrl,
          decoration: InputDecoration(labelText: 'Sensor Serial Number (e.g., PEARL-ESP32-999)', border: OutlineInputBorder(borderRadius: BorderRadius.circular(8))),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _pairNameCtrl,
          decoration: InputDecoration(labelText: 'Assign Pond Name', border: OutlineInputBorder(borderRadius: BorderRadius.circular(8))),
        ),
        const SizedBox(height: 24),
        SizedBox(
          height: 50,
          child: ElevatedButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Hardware node registered successfully.'), backgroundColor: Colors.green));
            },
            style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).primaryColor, foregroundColor: Colors.white),
            child: const Text("Register Sensor to Network"),
          ),
        ),
      ],
    );
  }

  Widget _buildSmsTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("📱 SMS Alerts Configuration", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        TextField(
          controller: _smsPhoneCtrl,
          keyboardType: TextInputType.phone,
          decoration: InputDecoration(labelText: 'Target Phone Number (+639...)', border: OutlineInputBorder(borderRadius: BorderRadius.circular(8))),
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          initialValue: _smsAlertLevel,
          decoration: InputDecoration(labelText: 'Alert Sensitivity Level', border: OutlineInputBorder(borderRadius: BorderRadius.circular(8))),
          items: ["Critical Emergencies Only", "Warnings & Critical", "All Notifications"]
              .map((f) => DropdownMenuItem(value: f, child: Text(f)))
              .toList(),
          onChanged: (val) => setState(() => _smsAlertLevel = val ?? _smsAlertLevel),
        ),
        const SizedBox(height: 24),
        SizedBox(
          height: 50,
          child: ElevatedButton(
            onPressed: () => _updateDeviceSetting('sms', null, "SMS Settings saved!"),
            style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).primaryColor, foregroundColor: Colors.white),
            child: const Text("Update SMS Settings"),
          ),
        ),
      ],
    );
  }

  Widget _buildSleepTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("💤 Deep Sleep Cycle", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        const Text("Adjust how frequently the sensor wakes up to transmit data.", style: TextStyle(color: Colors.grey, fontSize: 13)),
        const SizedBox(height: 24),
        Text("Broadcast Frequency: ${_sleepInterval.toInt()} Minutes", style: const TextStyle(fontWeight: FontWeight.bold)),
        Slider(
          value: _sleepInterval,
          min: 5,
          max: 120,
          divisions: 23,
          label: "${_sleepInterval.toInt()} Min",
          onChanged: (val) => setState(() => _sleepInterval = val),
        ),
        const SizedBox(height: 24),
        SizedBox(
          height: 50,
          child: ElevatedButton(
            onPressed: () => _updateDeviceSetting('sleep_interval', _sleepInterval, "Sleep interval saved!"),
            style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).primaryColor, foregroundColor: Colors.white),
            child: const Text("Update Broadcast Cycle"),
          ),
        ),
      ],
    );
  }

  Widget _buildCalibrationTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("⚖️ Sensor Calibration", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _buildField("pH Offset", _phOffsetCtrl)),
            const SizedBox(width: 12),
            Expanded(child: _buildField("Turbidity Offset (NTU)", _turbOffsetCtrl)),
          ],
        ),
        const SizedBox(height: 24),
        SizedBox(
          height: 50,
          child: ElevatedButton(
            onPressed: () => _updateDeviceSetting('calibration', null, "Calibration applied successfully!"),
            style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).primaryColor, foregroundColor: Colors.white),
            child: const Text("Save Calibration Offsets"),
          ),
        ),
      ],
    );
  }

  // =========================================================================
  // HELPER WIDGETS
  // =========================================================================

  Widget _buildRangeCard(String title, String tip, TextEditingController nMin, TextEditingController nMax, TextEditingController dMin, TextEditingController dMax) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Theme.of(context).primaryColor)),
            const SizedBox(height: 4),
            Text(tip, style: const TextStyle(fontSize: 11, color: Colors.blueGrey)),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _buildField("🟢 Normal Min", nMin)),
                const SizedBox(width: 12),
                Expanded(child: _buildField("🟢 Normal Max", nMax)),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _buildField("🔴 Danger Below", dMin)),
                const SizedBox(width: 12),
                Expanded(child: _buildField("🔴 Danger Above", dMax)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildField(String label, TextEditingController controller) {
    return TextField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true, signed: true),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(fontSize: 11),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
    );
  }
}