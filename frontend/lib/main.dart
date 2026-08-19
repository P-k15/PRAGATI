import 'package:flutter/material.dart';
import 'screens/submit_complaint_screen.dart';
import 'screens/ai_analysis_screen.dart';
import 'screens/my_complaints_screen.dart';
import 'screens/complaint_tracking_screen.dart';
import 'screens/officer_dashboard_screen.dart';
import 'screens/complaint_details_screen.dart';
import 'models/complaint_model.dart';
import 'services/api_service.dart';

void main() {
  runApp(const PragatiApp());
}

class PragatiApp extends StatelessWidget {
  const PragatiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PRAGATI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E88E5),
          primary: const Color(0xFF1E88E5),
          secondary: const Color(0xFF26A69A),
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: const LoginScreen(),
      onGenerateRoute: (RouteSettings settings) {
        switch (settings.name) {
          case '/citizen-home':
            return MaterialPageRoute(
              builder: (_) => const CitizenHomeScreen(),
            );
          case '/submit-complaint':
            return MaterialPageRoute(
              builder: (_) => const SubmitComplaintScreen(),
            );
          case '/ai-analysis':
            final complaint = settings.arguments as ComplaintModel;
            return MaterialPageRoute(
              builder: (_) => AIAnalysisScreen(complaint: complaint),
            );
          case '/my-complaints':
            return MaterialPageRoute(
              builder: (_) => const MyComplaintsScreen(),
            );
          case '/complaint-tracking':
            final complaintId = settings.arguments as String;
            return MaterialPageRoute(
              builder: (_) => ComplaintTrackingScreen(complaintId: complaintId),
            );
          case '/officer-dashboard':
            return MaterialPageRoute(
              builder: (_) => const OfficerDashboardScreen(),
            );
          case '/complaint-details':
            final complaintId = settings.arguments as String;
            return MaterialPageRoute(
              builder: (_) => ComplaintDetailsScreen(complaintId: complaintId),
            );
          default:
            return null;
        }
      },
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _formKey = GlobalKey<FormState>();

  // Form Controllers
  final _emailController = TextEditingController(text: 'citizen@example.com');
  final _passwordController = TextEditingController(text: 'citizenpass');
  final _nameController = TextEditingController();

  bool _isSignUp = false;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() {
      setState(() {
        _errorMessage = null;
        if (_tabController.index == 1) {
          // Officer default credentials
          _emailController.text = 'officer@example.com';
          _passwordController.text = 'officerpass';
        } else {
          // Citizen default credentials
          _emailController.text = 'citizen@example.com';
          _passwordController.text = 'citizenpass';
        }
      });
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _handleCitizenAuth() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiService = ApiService();

    try {
      if (_isSignUp) {
        // Register Citizen
        await apiService.register(
          email: _emailController.text.trim(),
          password: _passwordController.text.trim(),
          fullName: _nameController.text.trim(),
          role: 'citizen',
        );
      } else {
        // Login Citizen
        await apiService.login(
          _emailController.text.trim(),
          _passwordController.text.trim(),
        );
      }

      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/citizen-home');
      }
    } catch (e) {
      // Backend error or offline mode fallback for demo/testing
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Auth Note: ${e.toString().replaceAll('Exception: ', '')}. Logging in demo mode.'),
            duration: const Duration(seconds: 3),
          ),
        );
        Navigator.of(context).pushReplacementNamed('/citizen-home');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleOfficerAuth() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final apiService = ApiService();

    try {
      await apiService.login(
        _emailController.text.trim(),
        _passwordController.text.trim(),
      );

      if (mounted) {
        Navigator.of(context).pushReplacementNamed('/officer-dashboard');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Logging in to Officer Dashboard (Demo mode)'),
            duration: const Duration(seconds: 2),
          ),
        );
        Navigator.of(context).pushReplacementNamed('/officer-dashboard');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: Colors.grey.shade50,
      appBar: AppBar(
        title: const Text('PRAGATI - Grievance Portal'),
        elevation: 0,
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: theme.colorScheme.primary,
          indicatorWeight: 3,
          labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          tabs: const [
            Tab(icon: Icon(Icons.person), text: 'Citizen Portal'),
            Tab(icon: Icon(Icons.security), text: 'Officer Portal'),
          ],
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              const SizedBox(height: 12),
              // App Logo / Title Banner
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.primaryContainer.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: theme.colorScheme.primary.withOpacity(0.2)),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.primary,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.account_balance, color: Colors.white, size: 28),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'PRAGATI',
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: theme.colorScheme.primary,
                            ),
                          ),
                          const Text(
                            'Public Redressal & AI Grievance Tracking',
                            style: TextStyle(fontSize: 12, color: Colors.black54),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Form Card
              Card(
                elevation: 2,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Toggle between Sign In / Sign Up for Citizen Tab
                        if (_tabController.index == 0) ...[
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              ChoiceChip(
                                label: const Text('Sign In'),
                                selected: !_isSignUp,
                                onSelected: (selected) {
                                  if (selected) setState(() => _isSignUp = false);
                                },
                              ),
                              const SizedBox(width: 12),
                              ChoiceChip(
                                label: const Text('Register (Sign Up)'),
                                selected: _isSignUp,
                                onSelected: (selected) {
                                  if (selected) setState(() => _isSignUp = true);
                                },
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                        ],

                        Text(
                          _tabController.index == 0
                              ? (_isSignUp ? 'Create Citizen Account' : 'Citizen Sign In')
                              : 'Officer Sign In',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),

                        // Full Name (Only for Register)
                        if (_tabController.index == 0 && _isSignUp) ...[
                          TextFormField(
                            controller: _nameController,
                            decoration: const InputDecoration(
                              labelText: 'Full Name',
                              prefixIcon: Icon(Icons.badge_outlined),
                              border: OutlineInputBorder(),
                            ),
                            validator: (v) => (v == null || v.trim().isEmpty) ? 'Please enter your name' : null,
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Email Field
                        TextFormField(
                          controller: _emailController,
                          keyboardType: TextInputType.emailAddress,
                          decoration: const InputDecoration(
                            labelText: 'Email or Phone',
                            prefixIcon: Icon(Icons.email_outlined),
                            border: OutlineInputBorder(),
                          ),
                          validator: (v) => (v == null || v.trim().isEmpty) ? 'Please enter email or phone' : null,
                        ),
                        const SizedBox(height: 16),

                        // Password Field
                        TextFormField(
                          controller: _passwordController,
                          obscureText: true,
                          decoration: const InputDecoration(
                            labelText: 'Password',
                            prefixIcon: Icon(Icons.lock_outline),
                            border: OutlineInputBorder(),
                          ),
                          validator: (v) => (v == null || v.length < 4) ? 'Password must be at least 4 chars' : null,
                        ),
                        if (_errorMessage != null) ...[
                          const SizedBox(height: 12),
                          Text(
                            _errorMessage!,
                            style: const TextStyle(color: Colors.red, fontSize: 13),
                            textAlign: TextAlign.center,
                          ),
                        ],
                        const SizedBox(height: 24),

                        // Action Button
                        ElevatedButton(
                          onPressed: _isLoading
                              ? null
                              : (_tabController.index == 0 ? _handleCitizenAuth : _handleOfficerAuth),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: theme.colorScheme.primary,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 22,
                                  height: 22,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                                )
                              : Text(
                                  _tabController.index == 0
                                      ? (_isSignUp ? 'Register as Citizen' : 'Login as Citizen')
                                      : 'Login as Officer',
                                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Demo Credentials Quick Fill Helper
              Card(
                color: Colors.blue.shade50,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.info_outline, size: 18, color: Colors.blue),
                          SizedBox(width: 8),
                          Text('Demo Credentials Quick Fill', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Wrap(
                        spacing: 8,
                        children: [
                          ActionChip(
                            avatar: const Icon(Icons.person, size: 14),
                            label: const Text('Citizen Demo'),
                            onPressed: () {
                              setState(() {
                                _tabController.animateTo(0);
                                _isSignUp = false;
                                _emailController.text = 'citizen@example.com';
                                _passwordController.text = 'citizenpass';
                              });
                            },
                          ),
                          ActionChip(
                            avatar: const Icon(Icons.admin_panel_settings, size: 14),
                            label: const Text('Officer Demo'),
                            onPressed: () {
                              setState(() {
                                _tabController.animateTo(1);
                                _emailController.text = 'officer@example.com';
                                _passwordController.text = 'officerpass';
                              });
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Citizen Home Dashboard
class CitizenHomeScreen extends StatefulWidget {
  const CitizenHomeScreen({super.key});

  @override
  State<CitizenHomeScreen> createState() => _CitizenHomeScreenState();
}

class _CitizenHomeScreenState extends State<CitizenHomeScreen> {
  int _currentIndex = 0;

  void _showTrackDialog() {
    final trackController = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Track Complaint'),
        content: TextField(
          controller: trackController,
          decoration: const InputDecoration(
            labelText: 'Enter Complaint ID',
            hintText: 'e.g. comp_12345',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final id = trackController.text.trim();
              if (id.isNotEmpty) {
                Navigator.pop(ctx);
                Navigator.of(context).pushNamed(
                  '/complaint-tracking',
                  arguments: id,
                );
              }
            },
            child: const Text('Track'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final List<Widget> pages = [
      // Home Tab
      SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [theme.colorScheme.primary, theme.colorScheme.primary.withOpacity(0.8)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: theme.colorScheme.primary.withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Welcome Citizen! 👋',
                        style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white24,
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: const Text('Verified', style: TextStyle(color: Colors.white, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Report public issues directly to local authorities with instant AI analysis & automated tracking.',
                    style: TextStyle(color: Colors.white70, fontSize: 13),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Quick Actions Title
            const Text(
              'Quick Actions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            // Grid of Action Buttons
            Row(
              children: [
                Expanded(
                  child: _buildActionCard(
                    context,
                    title: 'Submit New\nGrievance',
                    icon: Icons.add_comment_rounded,
                    color: Colors.blue.shade700,
                    onTap: () {
                      Navigator.of(context).pushNamed('/submit-complaint');
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionCard(
                    context,
                    title: 'View My\nComplaints',
                    icon: Icons.list_alt_rounded,
                    color: Colors.teal.shade700,
                    onTap: () {
                      Navigator.of(context).pushNamed('/my-complaints');
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildActionCard(
                    context,
                    title: 'Track\nComplaint Status',
                    icon: Icons.search_rounded,
                    color: Colors.indigo.shade700,
                    onTap: _showTrackDialog,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionCard(
                    context,
                    title: 'AI Smart\nCategorization',
                    icon: Icons.auto_awesome,
                    color: Colors.amber.shade900,
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('AI auto-categorization is active when submitting complaints!')),
                      );
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Information Banner
            Card(
              elevation: 1,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Icon(Icons.psychology, size: 36, color: theme.colorScheme.primary),
                    const SizedBox(width: 16),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Powered by NVIDIA Nemotron AI', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          SizedBox(height: 4),
                          Text('Complaints are automatically summarized, prioritized, and assigned SLA response times.', style: TextStyle(fontSize: 12, color: Colors.black54)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),

      // Submit Complaint Tab
      const SubmitComplaintScreen(),

      // My Complaints Tab
      const MyComplaintsScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(_currentIndex == 0 ? 'PRAGATI Citizen Dashboard' : (_currentIndex == 1 ? 'Submit Complaint' : 'My Complaints')),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () {
              Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentIndex,
        children: pages,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        selectedItemColor: theme.colorScheme.primary,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_rounded), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.add_circle_outline_rounded), label: 'Submit'),
          BottomNavigationBarItem(icon: Icon(Icons.receipt_long_rounded), label: 'My Complaints'),
        ],
      ),
    );
  }

  Widget _buildActionCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(8)),
              child: Icon(icon, color: Colors.white, size: 24),
            ),
            const SizedBox(height: 12),
            Text(
              title,
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: color.withOpacity(0.9)),
            ),
          ],
        ),
      ),
    );
  }
}
