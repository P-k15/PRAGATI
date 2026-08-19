import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/complaint_model.dart';

class ApiService {
  final String baseUrl;

  ApiService({String? baseUrl}) : baseUrl = _formatBaseUrl(baseUrl);

  static String _formatBaseUrl(String? inputUrl) {
    final url = inputUrl ?? 'http://127.0.0.1:8000';
    if (!url.contains('/api/v1')) {
      return url.endsWith('/') ? '${url}api/v1' : '$url/api/v1';
    }
    return url;
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Login failed (${response.statusCode})');
    }
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    required String role,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': fullName,
        'role': role,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Registration failed (${response.statusCode})');
    }
  }

  Future<ComplaintModel> submitComplaint(Map<String, dynamic> complaintData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/complaints/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(complaintData),
    );

    if (response.statusCode == 200) {
      return ComplaintModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to submit complaint: ${response.statusCode}');
    }
  }

  Future<ComplaintModel> getComplaint(String complaintId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/complaints/$complaintId'),
    );

    if (response.statusCode == 200) {
      return ComplaintModel.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 404) {
      throw Exception('Complaint not found');
    } else {
      throw Exception('Failed to fetch complaint: ${response.statusCode}');
    }
  }

  Future<List<ComplaintModel>> getComplaints({
    String? citizenId,
    String? status,
    int skip = 0,
    int limit = 100,
  }) async {
    final queryParameters = <String, String>{};
    if (citizenId != null) queryParameters['citizen_id'] = citizenId;
    if (status != null) queryParameters['status'] = status;
    queryParameters['skip'] = skip.toString();
    queryParameters['limit'] = limit.toString();

    final uri = Uri.parse('$baseUrl/complaints/').replace(queryParameters: queryParameters);
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => ComplaintModel.fromJson(json)).toList();
    } else {
      throw Exception('Failed to fetch complaints: ${response.statusCode}');
    }
  }

  Future<ComplaintModel> updateComplaintStatus(String complaintId, String status) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/complaints/$complaintId/status'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'status': status}),
    );

    if (response.statusCode == 200) {
      return ComplaintModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to update complaint status: ${response.statusCode}');
    }
  }

  Future<ComplaintModel> assignComplaintOfficer(String complaintId, String officerId) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/complaints/$complaintId/assign'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'officer_id': officerId}),
    );

    if (response.statusCode == 200) {
      return ComplaintModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to assign complaint officer: ${response.statusCode}');
    }
  }
}