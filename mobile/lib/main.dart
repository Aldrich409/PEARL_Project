import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const PearlApp());
}

class PearlApp extends StatelessWidget {
  const PearlApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PEARL System',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.system, // Automatically switches based on the device's system theme
      
      // ==========================================
      // 🌊 LIGHT MODE: Soft Pearl Aesthetic
      // ==========================================
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFE8F6F8), 
        primaryColor: const Color(0xFF0284C7),
        
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 2,
          shadowColor: Colors.black.withValues(alpha: 0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20), 
          ),
        ),
        
        listTileTheme: ListTileThemeData(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          selectedTileColor: const Color(0xFF0284C7).withValues(alpha: 0.1),
        ),

        textTheme: GoogleFonts.interTextTheme(Theme.of(context).textTheme).apply(
          bodyColor: const Color(0xFF334155),
          displayColor: const Color(0xFF0369A1),
        ),
        
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          iconTheme: IconThemeData(color: Color(0xFF0369A1)),
          titleTextStyle: TextStyle(color: Color(0xFF0369A1), fontSize: 20, fontWeight: FontWeight.bold),
        ),
      ),

      // ==========================================
      // 🌌 DARK MODE: Deep Space Aesthetic
      // ==========================================
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0F172A), 
        primaryColor: const Color(0xFF38BDF8),
        
        cardTheme: CardThemeData(
          color: const Color(0xFF1E293B),
          elevation: 4,
          shadowColor: Colors.black.withOpacity(0.4),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
        
        listTileTheme: ListTileThemeData(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          selectedTileColor: const Color(0xFF38BDF8).withOpacity(0.15),
        ),

        textTheme: GoogleFonts.interTextTheme(Theme.of(context).textTheme).apply(
          bodyColor: const Color(0xFFCBD5E1),
          displayColor: const Color(0xFFE0F2FE),
        ),
        
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          iconTheme: IconThemeData(color: Color(0xFFE0F2FE)),
          titleTextStyle: TextStyle(color: Color(0xFFE0F2FE), fontSize: 20, fontWeight: FontWeight.bold),
        ),
      ),
      
      // Launch the app on the Login Screen
      home: const LoginScreen(),
    );
  }
}