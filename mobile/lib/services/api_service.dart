import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000';

  // --- AUTHENTICATION ---
  static Future<Map<String, dynamic>?> login(String username, String password) async {
    final url = Uri.parse('$baseUrl/api/login');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final prefs = await SharedPreferences.getInstance();
        await prefs.setInt('user_id', data['id']);
        await prefs.setString('username', data['username']);
        await prefs.setString('role', data['role']);
        return data;
      }
    } catch (e) {
      return null;
    }
    return null;
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // --- DATA FETCHING ---
  static Future<List<dynamic>> getDevices(int userId, String role) async {
    final url = Uri.parse('$baseUrl/api/devices?user_id=$userId&role=$role');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (e) {}
    return [];
  }

  static Future<bool> updateDeviceSettings(Map<String, dynamic> deviceData) async {
    final url = Uri.parse('$baseUrl/api/devices/update');
    try {
      final res = await http.put(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(deviceData),
      );
      return res.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // --- FISH SPECIES LIBRARY & AI SUGGESTIONS ---
  static Future<List<dynamic>> getFishProfiles() async {
    final url = Uri.parse('$baseUrl/api/fish-profiles');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (e) {}
    return [];
  }

  static Future<Map<String, dynamic>?> getFishSuggestion(String fishName) async {
    final url = Uri.parse('$baseUrl/api/fish-profiles/suggest?fish_name=${Uri.encodeComponent(fishName)}');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (e) {}
    return null;
  }

  static Future<bool> saveFishProfile(Map<String, dynamic> profileData) async {
    final url = Uri.parse('$baseUrl/api/fish-profiles');
    try {
      final res = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(profileData),
      );
      return res.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  static Future<Map<String, dynamic>?> getLatestTelemetry(String deviceSn) async {
    final url = Uri.parse('$baseUrl/api/telemetry/latest?device_sn=$deviceSn');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (e) {}
    return null;
  }

  static Future<List<dynamic>> getHistory(String deviceSn, {int limit = 50}) async {
    final url = Uri.parse('$baseUrl/api/telemetry/history?device_sn=$deviceSn&limit=$limit');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body);
    } catch (e) {}
    return [];
  }

  static Future<Map<String, dynamic>?> getCurrentWeather() async {
    final url = Uri.parse('https://api.open-meteo.com/v1/forecast?latitude=14.5264&longitude=121.1558&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=Asia%2FManila');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body)['current'];
    } catch (e) {}
    return null;
  }

  static Future<List<dynamic>> getForecast(String deviceSn, {int days = 7}) async {
    final url = Uri.parse('$baseUrl/api/forecast/breeding?device_sn=$deviceSn&days_ahead=$days');
    try {
      final res = await http.get(url);
      if (res.statusCode == 200) return jsonDecode(res.body)['forecast'];
    } catch (e) {}
    return [];
  }
}