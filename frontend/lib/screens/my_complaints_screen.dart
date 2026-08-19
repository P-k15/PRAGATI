import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/complaint_model.dart';
import 'package:intl/intl.dart';

class MyComplaintsScreen extends StatefulWidget {
  final String? baseUrl;

  const MyComplaintsScreen({Key? key, this.baseUrl}) : super(key: key);

  @override
  State<MyComplaintsScreen> createState() => _MyComplaintsScreenState();
}

class _MyComplaintsScreenState extends State<MyComplaintsScreen> {
  late final ApiService _apiService;
  List<ComplaintModel> _complaints = [];
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _apiService = ApiService(baseUrl: widget.baseUrl);
    _loadComplaints();
  }

  Future<void> _loadComplaints() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      // In a real app, we would get the citizen ID from login
      final complaints = await _apiService.getComplaints(citizenId: 'citizen_001');
      setState(() {
        _complaints = complaints;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
      });
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // Helper method to get SLA status color
  Color _getSlaStatusColor(String? status) {
    switch (status) {
      case 'ON_TRACK':
        return Colors.green;
      case 'DUE_SOON':
        return Colors.orange;
      case 'OVERDUE':
        return Colors.red;
      case 'RESOLVED':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Complaints'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadComplaints,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('Error: $_errorMessage'),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _loadComplaints,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  )
                : _complaints.isEmpty
                    ? const Center(
                        child: Text('No complaints found'),
                      )
                    : ListView.builder(
                        itemCount: _complaints.length,
                        itemBuilder: (context, index) {
                          final complaint = _complaints[index];
                          return ListTile(
                            leading: Container(
                              width: 12,
                              height: 12,
                              decoration: BoxDecoration(
                                color: _getSlaStatusColor(complaint.slaStatus),
                                shape: BoxShape.circle,
                              ),
                            ),
                            title: Text(complaint.description),
                            subtitle: Text(
                                'Submitted: ${DateFormat.yMMMd().format(complaint.createdAt)} • Status: ${complaint.status ?? 'N/A'} • SLA: ${complaint.slaStatus ?? 'NOT_SET'}'),
                            trailing: const Icon(Icons.chevron_right),
                            onTap: () {
                              Navigator.of(context).pushNamed(
                                '/complaint-details',
                                arguments: complaint.id,
                              );
                            },
                          );
                        },
                      ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.of(context).pushNamed('/submit-complaint');
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}