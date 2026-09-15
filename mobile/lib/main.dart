import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/login_screen.dart';

// We will create these screens next!
// import 'screens/login_screen.dart';
// import 'screens/dashboard_screen.dart';

void main() {
  runApp(const PearlApp());
}

class PearlApp extends StatelessWidget {
  const PearlApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'P.E.A.R.L. System',
      debugShowCheckedModeBanner: false,
      
      // 🌊 LIGHT MODE: Ocean Blue Theme
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFE0F2FE), // Soft ocean water
        primaryColor: const Color(0xFF0284C7),
        cardColor: Colors.white,
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

      // 🌌 DARK MODE: Deep Space Theme
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF1A1A2E), // Deep dark purple-blue
        primaryColor: const Color(0xFF8B5CF6), // Neon Purple
        cardColor: const Color(0xFF16213E), // Dark container
        textTheme: GoogleFonts.interTextTheme(Theme.of(context).textTheme).apply(
          bodyColor: const Color(0xFFE2E8F0),
          displayColor: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          iconTheme: IconThemeData(color: Colors.white),
          titleTextStyle: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
        ),
      ),
      
      // Automatically switch based on the user's phone settings
      themeMode: ThemeMode.system, 
      
      // Start at a temporary placeholder until we build the Login Screen
    home: const LoginScreen(),
    );
  }
}