import 'package:http/http.dart' as http;
import 'dart:convert';

const String baseUrl = 'http://127.0.0.1:8000/api/v1';

void main() async {
  print('Debugging AI Source issue...');

  final complaintData = {
    'citizen_id': 'citizen_001',
    'description': 'The street lights near our college have not been working for five days.',
    'location': 'Main Street, Near College',
  };

  final response = await http.post(
    Uri.parse('$baseUrl/complaints/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(complaintData),
  );

  print('Status Code: ${response.statusCode}');
  print('Response Body: ${response.body}');

  if (response.statusCode == 200) {
    final Map<String, dynamic> jsonData = jsonDecode(response.body);
    print('\\nParsed JSON:');
    jsonData.forEach((key, value) {
      print('  $key: $value (${value.runtimeType})');
    });

    print('\\nChecking ai_source specifically:');
    print('  jsonData[\"ai_source\"]: ${jsonData['ai_source']}');
    print('  jsonData[\"aiSource\"]: ${jsonData['aiSource']}'); // This will likely be null

    // Test the model
    // Import the model - for now let's just manually check
  }
}