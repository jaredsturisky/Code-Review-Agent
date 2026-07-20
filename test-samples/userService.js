const bcrypt = require('bcrypt');
const { User } = require('../models');

async function hashPassword(password) {
  return bcrypt.hash(password, 12);
}

async function getUserForRequest(userId, requestingUserId) {
  return User.findOne({
    where: { id: userId, ownerId: requestingUserId },
    attributes: { exclude: ['passwordHash'] },
    limit: 1,
  });
}

module.exports = { hashPassword, getUserForRequest };
