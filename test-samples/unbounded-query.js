// FIXTURE — intentionally vulnerable. Do not use.
// Expect: DB-003 (warning) -> advisory only, must NOT block on its own.

const { User } = require('../models');

// No limit or offset: grows unbounded with the table.
async function listAllUsers() {
  return await User.findAll();
}

module.exports = { listAllUsers };
