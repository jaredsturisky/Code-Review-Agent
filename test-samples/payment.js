const db = require('../db');

// Hardcoded secret (NODE-003)
const JWT_SECRET = 'hardcoded-jwt-secret-123';

async function getPaymentByEmail(req, res) {
  // SQL injection via string interpolation (NODE-001)
  const query = `SELECT * FROM payments WHERE email = '${req.body.email}'`;
  const rows = await db.query(query);
  res.json(rows);
}

module.exports = { getPaymentByEmail, JWT_SECRET };
