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

  // Built-in fallback library so suggestions ALWAYS show even if backend isn't re-seeded
  final Map<String, Map<String, dynamic>> _fishLibrary = {
    'Tilapia': {
      'fish_name': 'Tilapia',
      'temp_norm_min': 26.0, 'temp_norm_max': 33.0, 'temp_danger_min': 24.0, 'temp_danger_max': 35.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 80.0, 'turb_danger_max': 100.0,
      'suggestion_text': '📘 BFAR/FAO Guide (Tilapia): Optimal spawning and growth at 26–33°C, pH 7.0–8.5, and turbidity ≤80 NTU. Above 100 NTU indicates severe algal blooms.',
    },
    'Bangus (Milkfish)': {
      'fish_name': 'Bangus (Milkfish)',
      'temp_norm_min': 25.0, 'temp_norm_max': 32.0, 'temp_danger_min': 22.0, 'temp_danger_max': 35.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 85.0, 'turb_danger_max': 110.0,
      'suggestion_text': '📘 BFAR/SEAFDEC Guide (Bangus): Thrives at 25–32°C and pH 7.0–8.5. Highly sensitive to dissolved oxygen drops when temp >32°C or turbidity >110 NTU.',
    },
    'Catfish (Hito)': {
      'fish_name': 'Catfish (Hito)',
      'temp_norm_min': 26.0, 'temp_norm_max': 32.0, 'temp_danger_min': 22.0, 'temp_danger_max': 36.0,
      'ph_norm_min': 6.5, 'ph_norm_max': 8.0, 'ph_danger_min': 5.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 100.0, 'turb_danger_max': 140.0,
      'suggestion_text': '📘 BFAR/FAO Guide (Catfish / Hito): Tolerates murky water up to 100 NTU (Danger >140 NTU) and pH 6.5–8.0. Extreme pH (<5.5 or >9.0) harms scaleless skin.',
    },
    'Carp (Karpa)': {
      'fish_name': 'Carp (Karpa)',
      'temp_norm_min': 24.0, 'temp_norm_max': 30.0, 'temp_danger_min': 20.0, 'temp_danger_max': 34.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.0, 'ph_danger_max': 9.0,
      'turb_norm_max': 90.0, 'turb_danger_max': 120.0,
      'suggestion_text': '📘 FAO Guide (Common Carp): Prefers 24–30°C and pH 7.0–8.5. Bottom feeding stirs sediment (Normal ≤90 NTU, Danger >120 NTU).',
    },
    'Freshwater Prawn (Ulang)': {
      'fish_name': 'Freshwater Prawn (Ulang)',
      'temp_norm_min': 28.0, 'temp_norm_max': 31.0, 'temp_danger_min': 24.0, 'temp_danger_max': 34.0,
      'ph_norm_min': 7.0, 'ph_norm_max': 8.5, 'ph_danger_min': 6.5, 'ph_danger_max': 9.0,
      'turb_norm_max': 60.0, 'turb_danger_max': 85.0,
      'suggestion_text': '📘 BFAR Guide (Ulang): Needs clear water (≤60 NTU, Danger >85 NTU) and pH 7.0–8.5 for healthy shell molting.',
    },
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
      if (p is Map<String, dynamic> && p['fish_name'] != null) {
        _fishLibrary[p['fish_name'].toString()] = p;
      }
    }

    if (devices.isNotEmpty) {
      _device = devices.firstWhere((d) => d['device_sn'] == widget.activeDeviceSn, orElse: () => devices[0]);
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
      // Local fallback AI suggestion
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
    if (mounted) {
      setState(() => _device = payload);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(ok ? '🐟 Pond set to $_selectedPondFish!' : '✅ Applied $_selectedPondFish locally!'),
          backgroundColor: Colors.green,
        ),
      );
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
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('💾 Saved "$fishName" to Species Library!'), backgroundColor: Colors.teal),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_device == null) return const Center(child: Text("No pond node selected."));

    final primaryColor = Theme.of(context).primaryColor;
    final fishNames = _fishLibrary.keys.toList();
    final activeProfile = _fishLibrary[_selectedPondFish] ?? _fishLibrary['Tilapia']!;

    final tempTip = "💡 Suggested: 🟢 Normal ${activeProfile['temp_norm_min']}–${activeProfile['temp_norm_max']}°C | ⚠️ Warning ${activeProfile['temp_danger_min']}–${activeProfile['temp_norm_min']}°C or ${activeProfile['temp_norm_max']}–${activeProfile['temp_danger_max']}°C | 🔴 Danger <${activeProfile['temp_danger_min']}°C or >${activeProfile['temp_danger_max']}°C";
    final phTip = "💡 Suggested: 🟢 Normal ${activeProfile['ph_norm_min']}–${activeProfile['ph_norm_max']} | ⚠️ Warning ${activeProfile['ph_danger_min']}–${activeProfile['ph_norm_min']} or ${activeProfile['ph_norm_max']}–${activeProfile['ph_danger_max']} | 🔴 Danger <${activeProfile['ph_danger_min']} or >${activeProfile['ph_danger_max']}";
    final turbTip = "💡 Suggested: 🟢 Normal 0–${activeProfile['turb_norm_max']} NTU | ⚠️ Warning ${activeProfile['turb_norm_max']}–${activeProfile['turb_danger_max']} NTU | 🔴 Danger >${activeProfile['turb_danger_max']} NTU";

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("🎯 Step 1: Choose Species in Pond", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
                const SizedBox(height: 4),
                Text("Pond: ${_device!['pond_name']} | Active Fish: ${_device!['fish_type'] ?? 'Tilapia'}", style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: fishNames.contains(_selectedPondFish) ? _selectedPondFish : fishNames.first,
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
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                    border: Border(left: BorderSide(color: primaryColor, width: 4)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("📖 Suggested Ranges for $_selectedPondFish:", style: TextStyle(fontWeight: FontWeight.bold, color: primaryColor)),
                      const SizedBox(height: 6),
                      Text(activeProfile['suggestion_text'] ?? '', style: const TextStyle(fontSize: 12)),
                      const Divider(height: 16),
                      Text("🌡️ Temp: $tempTip", style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 4),
                      Text("🧪 pH Level: $phTip", style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 4),
                      Text("🌊 Turbidity: $turbTip", style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _applySelectedSpeciesToPond,
                    icon: const Icon(Icons.check_circle_outline),
                    label: Text("Set '$_selectedPondFish' as Active Species in Pond"),
                    style: ElevatedButton.styleFrom(backgroundColor: primaryColor, foregroundColor: Colors.white),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        Text("➕ Step 2: Type & Save Custom Fish Species", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: primaryColor)),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _customFishNameCtrl,
                decoration: InputDecoration(
                  labelText: 'Type Fish Name to Save (e.g., Red Tilapia, Dalag)',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton.icon(
              onPressed: _fetchAiSuggestion,
              icon: const Icon(Icons.auto_awesome, size: 18),
              label: const Text("AI Suggest"),
            ),
          ],
        ),
        const SizedBox(height: 12),
        _buildRangeCard("🌡️ Temperature (°C)", tempTip, _tempNormMin, _tempNormMax, _tempDangerMin, _tempDangerMax),
        const SizedBox(height: 12),
        _buildRangeCard("🧪 pH Level", phTip, _phNormMin, _phNormMax, _phDangerMin, _phDangerMax),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("🌊 Turbidity (NTU)", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: primaryColor)),
                const SizedBox(height: 4),
                Text(turbTip, style: const TextStyle(fontSize: 11, color: Colors.blueGrey)),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(child: _buildField("🟢 Normal Max (NTU)", _turbNormMax)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildField("🔴 Danger Above (NTU)", _turbDangerMax)),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        CheckboxListTile(
          contentPadding: EdgeInsets.zero,
          title: Text("Also set as active species for ${_device!['pond_name']}", style: const TextStyle(fontSize: 13)),
          value: _applyToPondImmediately,
          onChanged: (val) => setState(() => _applyToPondImmediately = val ?? true),
        ),
        ElevatedButton.icon(
          onPressed: _saveCustomFishToLibrary,
          icon: const Icon(Icons.save),
          label: const Text("Save Fish Species & Ranges to Library"),
          style: ElevatedButton.styleFrom(backgroundColor: Colors.teal, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(vertical: 14)),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildRangeCard(String title, String tip, TextEditingController nMin, TextEditingController nMax, TextEditingController dMin, TextEditingController dMax) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Theme.of(context).primaryColor)),
            const SizedBox(height: 4),
            Text(tip, style: const TextStyle(fontSize: 11, color: Colors.blueGrey)),
            const SizedBox(height: 12),
           // ... continuation of _buildRangeCard
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

  // Helper widget to build the text fields inside the range cards
  Widget _buildField(String label, TextEditingController controller) {
    return TextField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
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