// FIXTURE — intentionally vulnerable. Do not use.
// Expect: NODE-005 (warning) -> advisory only, must NOT block on its own.

// Returning err.stack leaks internal paths and library versions to the client.
function errorHandler(err, req, res, next) {
  res.status(500).json({
    error: err.stack,
    query: err.sql,
  });
}

module.exports = { errorHandler };
