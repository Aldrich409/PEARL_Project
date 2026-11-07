import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AccountManagementScreen extends StatefulWidget {
  final Map<String, dynamic> userData;

  const AccountManagementScreen({super.key, required this.userData});

  @override
  State<AccountManagementScreen> createState() => _AccountManagementScreenState();
}

class _AccountManagementScreenState extends State<AccountManagementScreen> with SingleTickerProviderStateMixin {
  bool _isLoading = true;
  List<dynamic> _accounts = [];
  late TabController _tabController;

  final _newUsernameCtrl = TextEditingController();
  final _newPasswordCtrl = TextEditingController();
  final _newConfirmPwCtrl = TextEditingController();
  String _newRole = 'farmer';
  final _newPondNameCtrl = TextEditingController(text: "My Fish Pond");
  final _newLocationCtrl = TextEditingController(text: "Angono, Rizal");
  final _newLengthCtrl = TextEditingController(text: "25.0");
  final _newWidthCtrl = TextEditingController(text: "20.0");
  final _newDepthCtrl = TextEditingController(text: "1.0");
  final _newFishCountCtrl = TextEditingController(text: "500");
  final _newPhoneCtrl = TextEditingController();

  bool get isAdmin => widget.userData['role'] == 'admin';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: isAdmin ? 2 : 1, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _newUsernameCtrl.dispose();
    _newPasswordCtrl.dispose();
    _newConfirmPwCtrl.dispose();
    _newPondNameCtrl.dispose();
    _newLocationCtrl.dispose();
    _newLengthCtrl.dispose();
    _newWidthCtrl.dispose();
    _newDepthCtrl.dispose();
    _newFishCountCtrl.dispose();
    _newPhoneCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      _accounts = await ApiService.getAllAccounts(); 
    } catch (e) {
      debugPrint("Error loading accounts: $e");
    }
    if (mounted) setState(() => _isLoading = false);
  }

  Future<void> _handleCreateAccount() async {
    if (_newUsernameCtrl.text.isEmpty || _newPasswordCtrl.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("⚠️ Please fill in username and password")));
      return;
    }
    if (_newPasswordCtrl.text != _newConfirmPwCtrl.text) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("❌ Passwords do not match")));
      return;
    }

    final payload = {
      "username": _newUsernameCtrl.text.trim(),
      "password": _newPasswordCtrl.text,
      "role": _newRole,
      "pond_name": _newPondNameCtrl.text.trim(),
      "location": _newLocationCtrl.text.trim(),
      "length": double.tryParse(_newLengthCtrl.text) ?? 25.0,
      "width": double.tryParse(_newWidthCtrl.text) ?? 20.0,
      "depth": double.tryParse(_newDepthCtrl.text) ?? 1.0,
      "fish_count": int.tryParse(_newFishCountCtrl.text) ?? 500,
      "alert_phone": _newPhoneCtrl.text.trim(),
    };

    bool success = await ApiService.adminCreateAccount(payload);
    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("✅ Created account for ${_newUsernameCtrl.text}!")));
      _newUsernameCtrl.clear();
      _newPasswordCtrl.clear();
      _newConfirmPwCtrl.clear();
      _loadData();
      _tabController.animateTo(1); 
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("❌ Failed to create account (Username may already exist)")));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    return Column(
      children: [
        const Padding(
          padding: EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text("👥 Account & Pond Management", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              Text("Pamahalaan ang mga detalye ng account at palaisdaan", style: TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: Colors.grey)),
            ],
          ),
        ),
        if (isAdmin)
          TabBar(
            controller: _tabController,
            labelColor: const Color(0xFF0284C7),
            unselectedLabelColor: Colors.grey,
            indicatorColor: const Color(0xFF0284C7),
            tabs: const [
              Tab(icon: Icon(Icons.person_add), text: "Create Account"),
              Tab(icon: Icon(Icons.manage_accounts), text: "Manage Accounts"),
            ],
          ),
        Expanded(
          child: isAdmin
              ? TabBarView(
                  controller: _tabController,
                  children: [
                    _buildCreateAccountTab(),
                    _buildManageAccountsTab(isDark: Theme.of(context).brightness == Brightness.dark),
                  ],
                )
              : _buildManageAccountsTab(isDark: Theme.of(context).brightness == Brightness.dark),
        ),
      ],
    );
  }

  Widget _buildCreateAccountTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text("📝 New User & Pond Registration", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        TextField(controller: _newUsernameCtrl, decoration: const InputDecoration(labelText: 'Username', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        TextField(controller: _newPasswordCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        TextField(controller: _newConfirmPwCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Confirm Password', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          initialValue: _newRole,
          decoration: const InputDecoration(labelText: 'Account Role', border: OutlineInputBorder()),
          items: ['farmer', 'admin'].map((r) => DropdownMenuItem(value: r, child: Text(r.toUpperCase()))).toList(),
          onChanged: (val) => setState(() => _newRole = val ?? 'farmer'),
        ),
        const SizedBox(height: 24),
        const Divider(),
        const Text("🏡 Pond Specifications", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        TextField(controller: _newPondNameCtrl, decoration: const InputDecoration(labelText: 'Pond Name', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        TextField(controller: _newLocationCtrl, decoration: const InputDecoration(labelText: 'Location', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: TextField(controller: _newLengthCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Length (m)', border: OutlineInputBorder()))),
            const SizedBox(width: 8),
            Expanded(child: TextField(controller: _newWidthCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width (m)', border: OutlineInputBorder()))),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: TextField(controller: _newDepthCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Depth (m)', border: OutlineInputBorder()))),
            const SizedBox(width: 8),
            Expanded(child: TextField(controller: _newFishCountCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Fish Count', border: OutlineInputBorder()))),
          ],
        ),
        const SizedBox(height: 12),
        TextField(controller: _newPhoneCtrl, keyboardType: TextInputType.phone, decoration: const InputDecoration(labelText: 'Alert Phone (+639...)', border: OutlineInputBorder())),
        const SizedBox(height: 24),
        SizedBox(
          height: 50,
          child: ElevatedButton(
            onPressed: _handleCreateAccount,
            style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).primaryColor, foregroundColor: Colors.white),
            child: const Text("Register Account & Pond Profile", style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildManageAccountsTab({required bool isDark}) {
    List targetAccounts = isAdmin 
        ? _accounts 
        : _accounts.where((acc) => acc['id'].toString() == widget.userData['id'].toString()).toList(); 

    if (targetAccounts.isEmpty) {
      return const Center(child: Text("No account details found."));
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(isAdmin ? "🗂️ System Users & Connected Ponds" : "📝 Edit My Profile & Pond Details", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 16),
        ...targetAccounts.map((acc) => AccountEditorCard(acc: acc, isAdmin: isAdmin, onRefresh: _loadData)),
      ],
    );
  }
}

class AccountEditorCard extends StatefulWidget {
  final Map<String, dynamic> acc;
  final bool isAdmin;
  final VoidCallback onRefresh;

  const AccountEditorCard({super.key, required this.acc, required this.isAdmin, required this.onRefresh});

  @override
  State<AccountEditorCard> createState() => _AccountEditorCardState();
}

class _AccountEditorCardState extends State<AccountEditorCard> {
  late TextEditingController _pwCtrl, _cpwCtrl, _nameCtrl, _locCtrl, _lenCtrl, _widCtrl, _depCtrl, _fishCtrl, _phoneCtrl;
  late TextEditingController _fishTypeCtrl, _tMinCtrl, _tMaxCtrl, _pMinCtrl, _pMaxCtrl, _turbMaxCtrl;

  @override
  void initState() {
    super.initState();
    _pwCtrl = TextEditingController();
    _cpwCtrl = TextEditingController();
    _nameCtrl = TextEditingController(text: widget.acc['pond_name'] ?? '');
    _locCtrl = TextEditingController(text: widget.acc['location'] ?? '');
    _lenCtrl = TextEditingController(text: (widget.acc['length'] ?? 25.0).toString());
    _widCtrl = TextEditingController(text: (widget.acc['width'] ?? 20.0).toString());
    _depCtrl = TextEditingController(text: (widget.acc['depth'] ?? 1.0).toString());
    _fishCtrl = TextEditingController(text: (widget.acc['fish_count'] ?? 500).toString());
    _phoneCtrl = TextEditingController(text: widget.acc['alert_phone'] ?? '');

    _fishTypeCtrl = TextEditingController(text: widget.acc['fish_type'] ?? 'Tilapia');
    _tMinCtrl = TextEditingController(text: (widget.acc['temp_norm_min'] ?? 26.0).toString());
    _tMaxCtrl = TextEditingController(text: (widget.acc['temp_norm_max'] ?? 33.0).toString());
    _pMinCtrl = TextEditingController(text: (widget.acc['ph_norm_min'] ?? 7.0).toString());
    _pMaxCtrl = TextEditingController(text: (widget.acc['ph_norm_max'] ?? 8.5).toString());
    _turbMaxCtrl = TextEditingController(text: (widget.acc['turb_norm_max'] ?? 80.0).toString());
  }

  @override
  void dispose() {
    _pwCtrl.dispose(); _cpwCtrl.dispose(); _nameCtrl.dispose(); _locCtrl.dispose();
    _lenCtrl.dispose(); _widCtrl.dispose(); _depCtrl.dispose(); _fishCtrl.dispose(); _phoneCtrl.dispose();
    _fishTypeCtrl.dispose(); _tMinCtrl.dispose(); _tMaxCtrl.dispose();
    _pMinCtrl.dispose(); _pMaxCtrl.dispose(); _turbMaxCtrl.dispose();
    super.dispose();
  }

  Future<void> _saveChanges() async {
    if (_pwCtrl.text.isNotEmpty || _cpwCtrl.text.isNotEmpty) {
      if (_pwCtrl.text != _cpwCtrl.text) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("❌ New passwords do not match!")));
        return;
      }
      await ApiService.adminUpdatePassword(widget.acc['id'], _pwCtrl.text);
    }

    if (widget.acc['device_sn'] != null) {
      final updatedDevice = {
        "device_sn": widget.acc['device_sn'],
        "pond_name": _nameCtrl.text.trim(),
        "location": _locCtrl.text.trim(),
        "length": double.tryParse(_lenCtrl.text) ?? 25.0,
        "width": double.tryParse(_widCtrl.text) ?? 20.0,
        "depth": double.tryParse(_depCtrl.text) ?? 1.0,
        "fish_count": int.tryParse(_fishCtrl.text) ?? 500,
        "alert_phone": _phoneCtrl.text.trim(),
        "fish_type": _fishTypeCtrl.text.trim(),
        "temp_norm_min": double.tryParse(_tMinCtrl.text) ?? 26.0,
        "temp_norm_max": double.tryParse(_tMaxCtrl.text) ?? 33.0,
        "ph_norm_min": double.tryParse(_pMinCtrl.text) ?? 7.0,
        "ph_norm_max": double.tryParse(_pMaxCtrl.text) ?? 8.5,
        "turb_norm_max": double.tryParse(_turbMaxCtrl.text) ?? 80.0,
        "alert_level": "Critical", "sleep_interval": 30, "ph_offset": 0.0, "turb_offset": 0.0
      };
      bool ok = await ApiService.updateDeviceSettings(updatedDevice);
      if (ok && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("✅ Account & Pond details updated!"), backgroundColor: Colors.green));
        widget.onRefresh();
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("✅ Password updated successfully!"), backgroundColor: Colors.green));
      }
    }
  }

  Future<void> _deleteAccount() async {
    bool ok = await ApiService.adminDeleteAccount(widget.acc['id']);
    if (ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("✅ Deleted user ${widget.acc['username']}")));
      widget.onRefresh();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ExpansionTile(
        initiallyExpanded: !widget.isAdmin,
        title: Text("👤 ${widget.acc['username']} (${widget.acc['role'].toString().toUpperCase()})", style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text("Pond: ${widget.acc['pond_name'] ?? 'N/A'}", style: const TextStyle(fontSize: 12)),
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("User ID: ${widget.acc['id']} | Device SN: ${widget.acc['device_sn'] ?? 'None (Admin)'}", style: TextStyle(fontSize: 11, color: isDark ? Colors.grey : Colors.black54)),
                const SizedBox(height: 16),
                const Text("🔐 Update Account Password", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(child: TextField(controller: _pwCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'New Password', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                    const SizedBox(width: 8),
                    Expanded(child: TextField(controller: _cpwCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Confirm Password', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                  ],
                ),
                const SizedBox(height: 16),
                const Text("🏡 Update Pond Details", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 8),
                TextField(controller: _nameCtrl, decoration: const InputDecoration(labelText: 'Pond Name', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8))),
                const SizedBox(height: 8),
                TextField(controller: _locCtrl, decoration: const InputDecoration(labelText: 'Location', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8))),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(child: TextField(controller: _lenCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Length', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                    const SizedBox(width: 6),
                    Expanded(child: TextField(controller: _widCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Width', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                    const SizedBox(width: 6),
                    Expanded(child: TextField(controller: _depCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Depth', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(child: TextField(controller: _fishCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Fish Count', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                    const SizedBox(width: 6),
                    Expanded(child: TextField(controller: _phoneCtrl, keyboardType: TextInputType.phone, decoration: const InputDecoration(labelText: 'Phone', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                  ],
                ),
                const SizedBox(height: 8),
                Theme(
                  data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    tilePadding: EdgeInsets.zero,
                    title: const Text("🐟 Fish Type & Thresholds", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF0284C7))),
                    children: [
                      TextField(controller: _fishTypeCtrl, decoration: const InputDecoration(labelText: 'Active Fish Species', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8))),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(child: TextField(controller: _tMinCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Temp Min (°C)', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                          const SizedBox(width: 6),
                          Expanded(child: TextField(controller: _tMaxCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Temp Max (°C)', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        children: [
                          Expanded(child: TextField(controller: _pMinCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'pH Min', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                          const SizedBox(width: 6),
                          Expanded(child: TextField(controller: _pMaxCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'pH Max', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                          const SizedBox(width: 6),
                          Expanded(child: TextField(controller: _turbMaxCtrl, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Max NTU', border: OutlineInputBorder(), contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8)))),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: ElevatedButton(
                        onPressed: _saveChanges,
                        style: ElevatedButton.styleFrom(backgroundColor: Theme.of(context).primaryColor, foregroundColor: Colors.white),
                        child: const Text("Save Changes"),
                      ),
                    ),
                    if (widget.isAdmin && widget.acc['id'] != 1) ...[
                      const SizedBox(width: 8),
                      Expanded(
                        flex: 1,
                        child: ElevatedButton(
                          onPressed: _deleteAccount,
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
                          child: const Text("Delete"),
                        ),
                      ),
                    ]
                  ],
                )
              ],
            ),
          ),
        ],
      ),
    );
  }
}