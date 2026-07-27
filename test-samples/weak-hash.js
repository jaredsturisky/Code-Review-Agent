// FIXTURE — intentionally vulnerable. Do not use.
// Expect: AUTH-003 (critical) -> blocks the merge.

const crypto = require('crypto');

// MD5 is unsalted and fast, so it is trivially brute-forced for passwords.
function hashPassword(password) {
  return crypto.createHash('md5').update(password).digest('hex');
}

function verifyPassword(password, storedHash) {
  return hashPassword(password) === storedHash;
}

module.exports = { hashPassword, verifyPassword };
