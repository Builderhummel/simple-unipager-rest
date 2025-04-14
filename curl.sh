curl -X POST http://192.168.188.21:5000/send \
  -H "Content-Type: application/json" \
  -d '{
    "RIC": 2022658,
    "MSG": "Distribute2",
    "m_type": "AlphaNum",
    "m_func": "Func3"
  }'
