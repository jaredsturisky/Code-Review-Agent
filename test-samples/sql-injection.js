// FIXTURE — intentionally vulnerable. Do not use.
// Expect: NODE-001 (critical) -> blocks the merge.

const { pool } = require('../db');

// req.params.id is attacker-controlled and interpolated straight into SQL.
async function getUserById(req, res) {
  const query = `SELECT id, email, role FROM users WHERE id = ${req.params.id}`;
  const { rows } = await pool.query(query);
  res.json(rows[0]);
}

// Same defect via concatenation rather than a template literal.
async function searchUsers(req, res) {
  const { rows } = await pool.query(
    "SELECT id, email FROM users WHERE email LIKE '%" + req.query.q + "%'"
  );
  res.json(rows);
}

module.exports = { getUserById, searchUsers };
