curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "RIC": 123456,
    "MSG": "Test message",
    "m_type": "B",
    "m_func": "4"
  }'

